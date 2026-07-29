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

logma = Logma(__name__)

# Referral code format: NB-X7K2-PQ or NBABCD12 (10-12 chars uppercase alphanumeric)
_ALPHABET = string.ascii_uppercase + string.digits
_CODE_RE = re.compile(r"^[A-Z0-9]{10,12}$")
_FORMAT_RE = re.compile(r"^([A-Z0-9]{2,4})-([A-Z0-9]{3,4})-([A-Z0-9]{2,4})$")

# Default API base (nchantdoffice.com — see nchantdoffice_com/app/apis/affiliate_api.py)
DEFAULT_API_BASE = os.environ.get(
    "NCHANT_API_BASE",
    "https://nchantdoffice.com/api/affiliate",
)

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
        seed = f"{user_id}:{salt or os.environ.get('NCHANT_REFERRAL_SALT', 'default-salt')}"
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
    """REST client for the affiliate/referral endpoints on nchantdoffice_com.

    Endpoints consumed (see nchantdoffice_com/app/apis/affiliate_api.py):

        GET    /api/affiliate/referrals        -> ReferralCode + tier + counts
        GET    /api/affiliate/earnings        -> EarningsDashboard JSON
        POST   /api/affiliate/payouts/request  -> request a payout
        POST   /api/affiliate/track/click/<id> -> record an outbound click

    All calls are best-effort: any network failure returns ``None`` /
    empty result rather than raising, so the in-app panel degrades
    gracefully when offline.
    """

    def __init__(self, base_url: str = DEFAULT_API_BASE,
                 api_key: Optional[str] = None,
                 timeout: float = 5.0):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._session = requests.Session()
        if api_key:
            self._session.headers["Authorization"] = f"Bearer {api_key}"

    def _request(self, method: str, path: str, *,
                 json: Optional[dict] = None,
                 params: Optional[dict] = None) -> Optional[Any]:
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

    # ---- Reads ----

    def fetch_referrals(self) -> Optional[Dict[str, Any]]:
        """Fetch the user's referral-code + tier + count summary."""
        return self._request("GET", "referrals")

    def fetch_earnings(self) -> Optional[Dict[str, Any]]:
        """Fetch the full earnings dashboard JSON."""
        return self._request("GET", "earnings")

    def fetch_offers(self, category: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        """Fetch active offers (Service Quick Links catalog)."""
        params = {"category": category} if category else None
        result = self._request("GET", "offers", params=params)
        if isinstance(result, list):
            return result
        if isinstance(result, dict):
            return result.get("offers", [])
        return None

    def fetch_banners(self) -> Optional[List[Dict[str, Any]]]:
        """Fetch ad-tab banner feed."""
        result = self._request("GET", "banners")
        if isinstance(result, list):
            return result
        if isinstance(result, dict):
            return result.get("banners", [])
        return None

    # ---- Writes ----

    def request_payout(self, amount_cents: int) -> Optional[Dict[str, Any]]:
        """Request a payout (must be >= min threshold)."""
        return self._request(
            "POST", "payouts/request", json={"amount_cents": amount_cents},
        )

    def track_click(self, offer_id: int, *, service_slug: Optional[str] = None,
                    session_id: Optional[str] = None,
                    tier: Optional[str] = None) -> bool:
        """Record an outbound quicklink click (ATNRG spec §1 analytics)."""
        payload = {"offer_id": offer_id}
        if service_slug:
            payload["service_slug"] = service_slug
        if session_id:
            payload["session_id"] = session_id
        if tier:
            payload["tier"] = tier
        result = self._request(
            "POST", f"track/click/{offer_id}", json=payload,
        )
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
