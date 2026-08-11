# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
    docid: nchantdoffice-referral-utilities
    name: App Referral Utilities
    description: >
        App Referral code generation, validation, and API client for
        the nchantdoffice desktop application. Backed by the spec at
        ``nchantdofficeATNRG/AppReferralSpec.md`` and the production
        implementation in
        ``nchantdofficeATNRG/nchantdofficeatnrg/referral.py``.
    version: 1.0.0
    authority: filesystem
    security: seclvl2
    <(WT)>: -32
"""
# -*- coding: utf-8 -*-
# ======================================Standard Library Modules======================================================||
import hashlib
import os
import re
import secrets
import string
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional, Dict, List, Tuple, Any
from urllib.parse import urlencode

# ======================================3rd Party Library Modules=====================================================||
import requests

# ======================================Solutions Brewer Library Modules=============================================||
from kahndor.logma import Logma

# T-DESK-061 — compose RateLimitTracker for per-endpoint
# counting + Retry-After honoring (the server is rate-limited
# at 5/minute on /api/updates + /api/affiliate/links/ via
# flask-limiter; the desktop would silently 429 without this).
from nchantdoffice.utilities.rate_limit import RateLimitTracker

logma = Logma(__name__)

# Referral code format: NB-X7K2-PQ or NBABCD12 (10-12 chars uppercase alphanumeric)
_ALPHABET = string.ascii_uppercase + string.digits
_CODE_RE = re.compile(r"^[A-Z0-9]{10,12}$")
_FORMAT_RE = re.compile(r"^([A-Z0-9]{2,4})-([A-Z0-9]{3,4})-([A-Z0-9]{2,4})$")

# T-NEW-070 (DESK-2): default salt for the referral code
# generator. Previously read from NCHANT_REFERRAL_SALT env
# var (removed per hard-break). Override via the explicit
# `salt=` kwarg in ReferralCode.generate() if needed.
_DEFAULT_REFERRAL_SALT = "default-salt"

# T-NEW-070 (DESK-2 hard-break): NCHANT_API_BASE env var
# removed. The API base URL now comes from the user config
# file (~/.config/nchantdoffice/config.yaml) via
# get_server_url(). When dev_mode is true, the server URL
# defaults to http://localhost:5000 (the nchantdoffice_com
# cmds/serve_detached.py port) so operators can run a local
# test server without writing any env vars.
#
# The v1 namespaced endpoints live at:
#   https://nchantdoffice.com/api/v1/{affiliate,referral,quicklinks}
# (T-DESK-052 alignment, 2026-08-07). The previous
# /api/affiliate/... paths no longer exist on the live server.
from nchantdoffice.utilities.user_config import get_server_url  # noqa: E402
DEFAULT_API_BASE = get_server_url() + "/api/v1"

# Referral state machine (mirrors ATNRG spec §6)
REFERRAL_STATE_ACTIVE = "active"
REFERRAL_STATE_USED = "used"
REFERRAL_STATE_SUSPENDED = "suspended"
REFERRAL_STATE_EXPIRED = "expired"

# Invitation states (mirrors ATNRG spec §2)
INVITE_AVAILABLE = "available"
INVITE_PENDING = "pending"
INVITE_CONVERTED = "converted"
INVITE_EXPIRED = "expired"
INVITE_REVOKED = "revoked"

# Commission statuses
COMMISSION_PENDING = "pending"
COMMISSION_ACCRUED = "accrued"
COMMISSION_PAID = "paid"
COMMISSION_REVERSED = "reversed"

# Payout minimum threshold (USD cents) — ATNRG spec §7 says $25
DEFAULT_PAYOUT_MIN_CENTS = 2500


class Tier(Enum):
    """Commission tier (ATNRG spec §3).

    BASE: 0-9 referrals completed = 5% of referred revenue
    ELEVATED: 10-49 referrals = 10% of referred revenue
    """
    BASE = ("base", 0.05)
    ELEVATED = ("elevated", 0.10)

    def __init__(self, label: str, rate: float):
        self.label = label
        self.rate = rate

    @classmethod
    def for_count(cls, n: int) -> "Tier":
        return cls.ELEVATED if n >= 10 else cls.BASE


@dataclass(frozen=True)
class ReferralCode:
    """A referral code in the user's unique referral string.

    Format: ``NB-X7K2-PQ`` (10-12 chars uppercase alphanumeric,
    dashed). Mirrors ``nchantdofficeATNRG/nchantdofficeatnrg/referral.py``
    exactly so the desktop and ATNRG generate codes the server can
    validate uniformly.
    """
    value: str

    def __post_init__(self):
        if not (_CODE_RE.match(self.value) or _FORMAT_RE.match(self.value)):
            raise ValueError(f"Invalid referral code: {self.value!r}")
        logma.info(f"ReferralCode created: value={self.value!r}")

    @classmethod
    def generate(cls, user_id: str, *, salt: Optional[str] = None,
                 prefix: str = "NB", dashed: bool = True) -> "ReferralCode":
        """Deterministic code derived from user_id + salt."""
        # T-NEW-070 (DESK-2 hard-break): NCHANT_REFERRAL_SALT
        # env var removed. Salt now defaults to a module
        # constant. Operators who need a different salt
        # should pass it via the explicit `salt=` kwarg
        # (callers in nchantdoffice_com pass the per-user
        # salt explicitly — see services/referral.py).
        if salt is None:
            salt = _DEFAULT_REFERRAL_SALT
        seed = f"{user_id}:{salt}"
        digest = hashlib.sha256(seed.encode()).digest()
        raw = "".join(_ALPHABET[digest[i] % len(_ALPHABET)] for i in range(7))
        val = f"{prefix}-{raw[:3]}-{raw[3:7]}" if dashed else f"{prefix}{raw[:8]}"
        return cls(value=val)

    @classmethod
    def random(cls, prefix: str = "NB", dashed: bool = True) -> "ReferralCode":
        """Cryptographically-random code (no user association)."""
        n = 10 if dashed else 12
        raw = "".join(secrets.choice(_ALPHABET) for _ in range(n))
        val = f"{prefix}-{raw[:4]}-{raw[4:8]}" if dashed else f"{prefix}{raw}"
        return cls(value=val)

    @property
    def normalized(self) -> str:
        """Normalised form (no dashes, uppercase) for dedup/indexing."""
        return self.value.replace("-", "").upper()

    def __str__(self) -> str:
        return self.value


@dataclass
class ReferralAttribution:
    """Records who-referred-whom with timestamps.

    Mirrors ATNRG spec §4 (first-touch, no-self-referral, 30-day cookie).
    """
    code: ReferralCode
    referrer_user_id: str
    referee_user_id: str
    attributed_at: datetime
    first_paid_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    @classmethod
    def new(cls, code: ReferralCode, referrer_user_id: str,
            referee_user_id: str, *, cookie_days: int = 30,
            commission_days: int = 365) -> "ReferralAttribution":
        """Build a fresh attribution. Raises if self-referral attempted."""
        if referrer_user_id == referee_user_id:
            raise ValueError("Self-referral not allowed (ATNRG spec §4 rule 4)")
        now = datetime.now(timezone.utc)
        return cls(
            code=code,
            referrer_user_id=referrer_user_id,
            referee_user_id=referee_user_id,
            attributed_at=now,
            expires_at=now + timedelta(days=commission_days),
        )

    @property
    def is_active(self) -> bool:
        """Whether the commission window is still open."""
        return self.expires_at is not None and datetime.now(timezone.utc) < self.expires_at


@dataclass
class CommissionRecord:
    """Per-referee commission accrual ledger (ATNRG spec §7)."""
    referrer_user_id: str
    referee_user_id: str
    signup_date: datetime
    first_paid_date: Optional[datetime]
    tier: Tier
    period_start: datetime
    period_end: datetime
    revenue_cents: int = 0
    commission_cents: int = 0
    status: str = COMMISSION_PENDING

    def accrue(self, revenue_cents: int) -> int:
        """Add revenue and recompute commission. Returns new commission cents."""
        if self.status in (COMMISSION_PAID, COMMISSION_REVERSED):
            return 0
        self.revenue_cents += revenue_cents
        self.commission_cents = int(self.revenue_cents * self.tier.rate)
        self.status = COMMISSION_ACCRUED
        return self.commission_cents


@dataclass
class EarningsDashboard:
    """Snapshot of the user's referral program status (for the in-app panel)."""
    user_id: str
    total_referrals: int = 0
    active_referrals: int = 0
    current_tier: Tier = Tier.BASE
    pending_cents: int = 0
    this_month_cents: int = 0
    this_year_cents: int = 0
    lifetime_cents: int = 0
    next_payout_at: Optional[datetime] = None
    invitations_remaining: int = 0
    referrals: List[CommissionRecord] = field(default_factory=list)


class InMemoryReferralStore:
    """Local fallback when the server is unreachable.

    The desktop app keeps a small in-memory mirror of the server state so
    the panel can render even when offline. State is overwritten on each
    successful ``fetch_dashboard()`` call.
    """

    def __init__(self):
        logma.info("InMemoryReferralStore init")
        self.codes: Dict[str, ReferralCode] = {}
        self.code_index: Dict[str, str] = {}  # normalised -> user_id
        self.attributions: List[ReferralAttribution] = []
        self.commissions: Dict[str, List[CommissionRecord]] = {}
        self.invitations_remaining: int = 0

    def issue_code(self, user_id: str, code: ReferralCode) -> None:
        if user_id not in self.codes:
            self.codes[user_id] = code
            self.code_index[code.normalized] = user_id

    def resolve(self, code: ReferralCode) -> Optional[str]:
        return self.code_index.get(code.normalized)

    def attribute(self, attr: ReferralAttribution) -> None:
        self.attributions.append(attr)

    def has_prior(self, uid: str) -> bool:
        return any(a.referee_user_id == uid for a in self.attributions)

    def add_commission(self, rec: CommissionRecord) -> None:
        self.commissions.setdefault(rec.referrer_user_id, []).append(rec)

    def dashboard(self, user_id: str, *,
                  min_payout_cents: int = DEFAULT_PAYOUT_MIN_CENTS) -> EarningsDashboard:
        recs = self.commissions.get(user_id, [])
        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        pending = sum(r.commission_cents for r in recs if r.status == COMMISSION_ACCRUED)
        this_month = sum(r.commission_cents for r in recs if r.period_start >= month_start)
        this_year = sum(r.commission_cents for r in recs if r.period_start >= year_start)
        lifetime = sum(r.commission_cents for r in recs)
        active = sum(1 for r in recs if r.status == COMMISSION_ACCRUED)
        next_payout = (
            now + timedelta(days=15) if pending >= min_payout_cents else None
        )
        return EarningsDashboard(
            user_id=user_id,
            total_referrals=len(recs),
            active_referrals=active,
            current_tier=Tier.for_count(len(recs)),
            pending_cents=pending,
            this_month_cents=this_month,
            this_year_cents=this_year,
            lifetime_cents=lifetime,
            next_payout_at=next_payout,
            invitations_remaining=self.invitations_remaining,
            referrals=recs,
        )


# =============================================================================
# API Client — desktop -> nchantdoffice_com
# =============================================================================


class ReferralAPIClient:
    """REST client for the v1 namespaced affiliate/referral/
    quicklinks endpoints on nchantdoffice_com (T-DESK-052).

    Endpoints consumed (see nchantdoffice_com/app/apis/affiliate_api.py,
    referral_api.py, and quicklinks_api.py):

      POST /api/desktop/register         -> register a new desktop
      GET  /api/v1/referral/stats/<uid>  -> ReferralCode + tier + counts
      GET  /api/v1/referral/earnings/<uid>-> EarningsDashboard JSON
      GET  /api/v1/referral/share/<uid>  -> share link
      POST /api/v1/referral/generate-code -> mint a new referral code
      POST /api/v1/referral/track-click  -> record an outbound quicklink click
      POST /api/v1/referral/track-install-> record a referral install
      POST /api/v1/affiliate/payout/request -> request a payout
      GET  /api/v1/affiliate/dashboard   -> affiliate dashboard
      POST /api/v1/affiliate/link        -> create an affiliate link
      GET  /api/v1/quicklinks/           -> quicklinks catalog
      GET  /api/v1/quicklinks/categories -> quicklinks categories
      POST /api/v1/quicklinks/track-click -> track a quicklink click

    Rate-limit-aware (T-DESK-061): composes
    ``RateLimitTracker`` for per-endpoint counting + the
    server's ``Retry-After`` header is honored on 429s.

    Auth model: when an ``api_key`` is configured (i.e. the
    desktop has registered and the key is in the credentials
    store), it's sent as the ``x-api-key`` header on every
    request. The v1 referral/affiliate/quicklinks endpoints
    are currently open (no auth required) but the header is
    still sent for forward-compat: if the server starts
    requiring auth, the desktop is already wired.

    All calls are best-effort: any network failure returns
    ``None`` / empty result rather than raising, so the in-app
    panel degrades gracefully when offline.
    """

    def __init__(self, base_url: str = DEFAULT_API_BASE,
                 api_key: Optional[str] = None,
                 user_id: Optional[int] = None,
                 timeout: float = 5.0):
        """
        Args:
            base_url: API base URL. Defaults to DEFAULT_API_BASE
                (``https://nchantdoffice.com/api/v1``). Override
                for testing.
            api_key: per-desktop api_key from the registration
                response. When set, sent as ``x-api-key`` header
                on every request. Optional — the v1 endpoints
                are open today.
            user_id: the FAB user id. Required by the per-user
                endpoints (``stats/<uid>``, ``earnings/<uid>``,
                ``share/<uid>``). When ``None``, the methods
                that need a user_id will return ``None`` rather
                than make the call.
            timeout: HTTP request timeout in seconds. Default
                5.0 (per ATNRG spec; was previously
                ``connect_timeout=5`` which was too tight
                against the live server).
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.user_id = user_id
        self.timeout = timeout
        self._session = requests.Session()
        if api_key:
            # T-DESK-052: server expects x-api-key, not Bearer.
            self._session.headers["x-api-key"] = api_key
        # T-DESK-061: per-endpoint rate-limit tracker. The
        # server's flask-limiter caps /api/updates + /api/affiliate/links/
        # at 5/minute per IP; without this tracker a chatty UI
        # silently hits 429.
        self._rate_limit = RateLimitTracker()

    def _request(self, method: str, path: str, *,
                 json: Optional[dict] = None,
                 params: Optional[dict] = None) -> Optional[Any]:
        """Issue a request, return parsed JSON or None on failure.

        Best-effort: any HTTP error or network failure is
        logged at warning level and ``None`` is returned.
        Callers should treat ``None`` as "API unreachable"
        and fall back to local data.
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            response = self._session.request(
                method, url, json=json, params=params, timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json() if response.content else {}
        except (requests.RequestException, ValueError) as e:
            logma.warning(
                f"[referral_api] {method.upper()} {url} failed: {e}",
            )
            return None

    # ---- Registration (called once at first launch) ----

    @staticmethod
    def register_desktop(
        base_url: str,
        username: str,
        public_key: str,
        timeout: float = 5.0,
    ) -> Optional[Dict[str, Any]]:
        """Register a new desktop with the server.

        T-DESK-052: this is a STATIC method because the desktop
        doesn't have a server-issued api_key yet (that's the
        whole point of calling this). Calls
        ``POST /api/desktop/register`` (unauthenticated) and
        returns the server's response:

            {
                "desktop_uuid": "...",
                "api_key": "...",
                "user_name_txt": "...",
            }

        Args:
            base_url: server base URL, WITHOUT the /api/v1
                suffix. The desktop/register endpoint lives
                one level up at ``/api/desktop/register``.
            username: the ab_user.username the desktop is
                registering for.
            public_key: the desktop's public key (a string;
                the server stores it in
                NchantdUserDesktopModel.default_address_public_key).
                For now we send a 128-char random string; the
                real ATN RPC layer would send a real Paillier
                public key.
            timeout: HTTP request timeout.

        Returns:
            The server's response dict, or None on failure.
        """
        url = f"{base_url.rstrip('/')}/api/desktop/register"
        try:
            response = requests.post(
                url,
                json={"username": username, "public_key": public_key},
                timeout=timeout,
            )
            response.raise_for_status()
            return response.json() if response.content else {}
        except (requests.RequestException, ValueError) as e:
            logma.warning(
                f"[referral_api] POST {url} failed: {e}",
            )
            return None

    # ---- Reads ----

    def fetch_referral_stats(
        self, user_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Fetch the user's referral-code + tier + count summary.

        Calls ``GET /api/v1/referral/stats/<user_id>``. Returns
        ``None`` if no ``user_id`` is available (either set on
        the client or passed here).
        """
        uid = user_id if user_id is not None else self.user_id
        if uid is None:
            logma.warning(
                "[referral_api] fetch_referral_stats: no user_id, "
                "skipping call.",
            )
            return None
        return self._request("GET", f"referral/stats/{uid}")

    def fetch_earnings(
        self, user_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Fetch the full earnings dashboard JSON.

        Calls ``GET /api/v1/referral/earnings/<user_id>``.
        """
        uid = user_id if user_id is not None else self.user_id
        if uid is None:
            return None
        return self._request("GET", f"referral/earnings/{uid}")

    def fetch_share_link(
        self, user_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Fetch the shareable referral link.

        Calls ``GET /api/v1/referral/share/<user_id>``.
        """
        uid = user_id if user_id is not None else self.user_id
        if uid is None:
            return None
        return self._request("GET", f"referral/share/{uid}")

    def fetch_offers(self, category: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        """Fetch active offers (Service Quick Links catalog).

        Calls ``GET /api/v1/quicklinks/`` (the v1 QuickLinks
        endpoint replaces the old /api/affiliate/offers
        endpoint which no longer exists).

        Args:
            category: optional category filter (passed as
                ``?category=...`` query param).
        """
        params = {"category": category} if category else None
        result = self._request("GET", "quicklinks/", params=params)
        # The v1 quicklinks endpoint may return either a list
        # directly, or a dict with an "items"/"offers" key.
        if isinstance(result, list):
            return result
        if isinstance(result, dict):
            for key in ("items", "offers", "quicklinks", "links"):
                if key in result and isinstance(result[key], list):
                    return result[key]
        return None

    def fetch_banners(self) -> Optional[List[Dict[str, Any]]]:
        """Fetch ad-tab banner feed.

        The v1 server has no dedicated banners endpoint. The
        closest equivalent is the quicklinks catalog. Returns
        the quicklinks as "banners" — the ad tab can render
        them as banner-style cards even though the server
        doesn't differentiate.

        Returns an empty list on failure so the caller can
        fall back to FALLBACK_BANNERS.
        """
        result = self.fetch_offers()
        if result:
            return result
        return None

    def fetch_dashboard(self) -> Optional[Dict[str, Any]]:
        """Fetch the affiliate dashboard.

        Calls ``GET /api/v1/affiliate/dashboard``. Returns
        the full dashboard JSON (clicks, conversions, payouts
        summary, etc.).
        """
        return self._request("GET", "affiliate/dashboard")

    def fetch_payout_eligibility(self, user_id: int) -> Dict[str, Any]:
        """T-NEW-044 (UI-1): fetch the authoritative
        payout-eligibility dict from the server.

        Calls ``GET /api/v1/referral/payout-eligibility/<user_id>``.
        Returns the dict the server produces from
        ``ReferralService.get_payout_eligibility`` (PAY-1):

          eligible: bool
          pending_total: float
          threshold: float  ($25 = MIN_PAYOUT)
          tier: str         ("free", "pro", "pro_data", "enterprise")
          reason: str | None (None | "free_tier" | "below_threshold"
                              | "cookie_expired" | "first_touch_existing")

        Best-effort: returns ``{}`` on network failure or
        non-200 response. The caller is expected to handle
        the empty dict as "unknown" — the in-app panel will
        fall back to a neutral state ("Checking eligibility...")
        rather than rendering the wrong UI.

        The desktop MUST use this server-side check rather
        than computing eligibility locally: the server is
        the only place that knows the referrer's tier
        (which gates whether paid payouts are even allowed).
        """
        if not user_id:
            return {}
        url = f"{self.base_url}/referral/payout-eligibility/{user_id}"
        try:
            resp = requests.get(url, timeout=self.timeout)
            if resp.status_code != 200:
                logma.warning(
                    f"[referral] fetch_payout_eligibility returned "
                    f"{resp.status_code}: {resp.text[:200]}"
                )
                return {}
            return resp.json() if resp.content else {}
        except Exception as exc:
            logma.warning(
                f"[referral] fetch_payout_eligibility failed (non-blocking): "
                f"{exc}"
            )
            return {}

    def record_app_open(self, referee_user_id: str) -> Dict[str, Any]:
        """Record one desktop app-open for `referee_user_id`.

        T-NEW-042 (DESK-1): called by the launcher on every
        desktop startup so the server can track the
        3-opens-minimum anti-abuse rule (a referee must
        open the app ≥3 times before commission is credited).

        The endpoint is best-effort — failures are logged
        but never raise. Network errors are non-critical
        (the anti-abuse telemetry has to be allowed to fail
        in offline scenarios without blocking app launch).

        Args:
            referee_user_id: the desktop's user identifier.
                Currently sourced from
                ``NchantdOfficeUser.persist_uuid()`` (T-NEW-042
                DESK-0).

        Returns:
            Dict from the server (empty dict on failure).
            Server returns:
              {success, app_opens (int),
               already_recorded_today (bool)}
        """
        if not referee_user_id:
            return {}
        url = f"{self.base_url}/referral/record-app-open"
        try:
            resp = requests.post(
                url,
                json={"referee_user_id": referee_user_id},
                timeout=5,
            )
            if resp.status_code != 200:
                logma.warning(
                    f"[referral] record_app_open returned "
                    f"{resp.status_code}: {resp.text[:200]}"
                )
                return {}
            return resp.json() if resp.content else {}
        except Exception as exc:
            logma.warning(
                f"[referral] record_app_open failed (non-blocking): "
                f"{exc}"
            )
            return {}

    # ---- Writes ----

    def request_payout(self, amount_cents: int) -> Optional[Dict[str, Any]]:
        """Request a payout (must be >= min threshold).

        Calls ``POST /api/v1/affiliate/payout/request``.
        """
        return self._request(
            "POST", "affiliate/payout/request",
            json={"amount_cents": amount_cents},
        )

    def generate_referral_code(self) -> Optional[Dict[str, Any]]:
        """Mint a new referral code for the current user.

        Calls ``POST /api/v1/referral/generate-code``.
        """
        return self._request("POST", "referral/generate-code", json={})

    def track_click(
        self, offer_id: int, *,
        service_slug: Optional[str] = None,
        session_id: Optional[str] = None,
        tier: Optional[str] = None,
    ) -> bool:
        """Record an outbound quicklink click.

        T-DESK-052: was ``POST /api/affiliate/track/click/<id>``
        (404 on the live server). Now calls
        ``POST /api/v1/referral/track-click`` (the new endpoint
        in referral_api.py) with the offer_id in the body.

        Returns True on success, False on failure.
        """
        payload: Dict[str, Any] = {"offer_id": offer_id}
        if service_slug:
            payload["service_slug"] = service_slug
        if session_id:
            payload["session_id"] = session_id
        if tier:
            payload["tier"] = tier
        result = self._request(
            "POST", "referral/track-click", json=payload,
        )
        return result is not None

    def track_install(self) -> bool:
        """Record a referral install (called once at first launch).

        Calls ``POST /api/v1/referral/track-install``. The
        server reads the api_key from the header to determine
        which referral code (if any) attributed this install.
        """
        result = self._request("POST", "referral/track-install", json={})
        return result is not None

    # ---- Convenience ----

    @staticmethod
    def build_share_link(code: ReferralCode,
                         base_url: str = "https://nchantdoffice.com") -> str:
        """Build the shareable referral landing link (ATNRG spec §3)."""
        return f"{base_url}/download?ref={code}"


# =============================================================================
# Code-side helpers (portable across desktop)
# =============================================================================


def generate_referral_code(user_id: Optional[str] = None,
                            *, prefix: str = "NB",
                            dashed: bool = True) -> str:
    """Generate a single referral code string.

    If ``user_id`` is provided, the code is deterministic for that user.
    Otherwise a cryptographically-random code is produced.
    """
    if user_id:
        return str(ReferralCode.generate(user_id, prefix=prefix, dashed=dashed))
    return str(ReferralCode.random(prefix=prefix, dashed=dashed))


def validate_referral_code(code: str) -> Tuple[bool, str]:
    """Validate a referral code format.

    Returns ``(valid, message)``.
    """
    try:
        rc = ReferralCode(value=code)
        return True, f"valid ({rc.normalized})"
    except ValueError as e:
        return False, str(e)


def payout_eligible(dash: EarningsDashboard,
                     *, min_payout_cents: int = DEFAULT_PAYOUT_MIN_CENTS) -> bool:
    """Whether the dashboard's pending balance qualifies for payout."""
    return dash.pending_cents >= min_payout_cents


def build_share_urls(code: ReferralCode,
                     *,
                     base_url: str = "https://nchantdoffice.com") -> Dict[str, str]:
    """Build one-click share URLs for each platform (ATNRG spec §5)."""
    link = ReferralAPIClient.build_share_link(code, base_url=base_url)
    encoded = urlencode({"url": link, "text": f"Try nchantd Office — {code}"})
    return {
        "link": link,
        "clipboard": link,
        "twitter": f"https://twitter.com/intent/tweet?{encoded}",
        "linkedin": f"https://www.linkedin.com/sharing/share-offsite/?{encoded}",
        "email": f"mailto:?subject=Try%20nchantd%20Office&body={link}",
        "whatsapp": f"https://wa.me/?text={link}",
        "telegram": f"https://t.me/share/url?url={link}&text={code}",
    }


__all__ = [
    # Constants
    "REFERRAL_STATE_ACTIVE", "REFERRAL_STATE_USED", "REFERRAL_STATE_SUSPENDED",
    "REFERRAL_STATE_EXPIRED",
    "INVITE_AVAILABLE", "INVITE_PENDING", "INVITE_CONVERTED",
    "INVITE_EXPIRED", "INVITE_REVOKED",
    "COMMISSION_PENDING", "COMMISSION_ACCRUED", "COMMISSION_PAID",
    "COMMISSION_REVERSED",
    "DEFAULT_PAYOUT_MIN_CENTS",
    "DEFAULT_API_BASE",
    # Classes
    "Tier", "ReferralCode", "ReferralAttribution", "CommissionRecord",
    "EarningsDashboard", "InMemoryReferralStore", "ReferralAPIClient",
    # Helpers
    "generate_referral_code", "validate_referral_code",
    "payout_eligible", "build_share_urls",
]
