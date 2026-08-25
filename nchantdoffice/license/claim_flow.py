"""nchantdoffice.license — desktop-side glue for the account-claim flow.

DESK T-NEW-049 lives here. :class:`ClaimFlow` is the bridge between
the desktop install and the user's account — the magic-link flow
that binds an anonymous install to a user's email.

The flow (server-side endpoints are in the sister ``nchantdoffice_com``
repo — COM T-NEW-049b ships ``POST /api/account/claim`` and the
browser-side ``GET /account/claim``)::

    1. User opens the desktop's "Claim this install" dialog, types
       their email, clicks Send.  -> ClaimFlow.request_magic_link(email)
    2. POST /api/account/claim {email, install_id} -- server emails
       a magic-link to the user's address. The server returns 200
       even for unknown emails (enumeration-safe).
    3. User clicks the link in their email. The OS opens it in the
       default browser, which lands on
         https://nchantdoffice.com/account/claim?token=…&install_id=…
       The browser-side consumes the token (out of scope for this
       module). That endpoint mints a fresh entitlement token at
       the user's tier and binds the install.
    4. User returns to the desktop. Either the desktop's "Refresh
       entitlement" button or the auto-refresh on timer drives
       :meth:`ClaimFlow.complete_from_browser` (called with the
       deep-link URL the OS handed back via the custom URL scheme)
       or :meth:`ClaimFlow.complete_from_url_params` (called with
       the parsed params directly).
       On 200, the entitlement token + envelope are persisted via
       :meth:`EntitlementCache.store` and the tier-getter is
       re-installed so :func:`tier_gate.current_tier` immediately
       returns the user's tier.
       On 401 / 410, :class:`ClaimError` is raised so the caller
       can show the appropriate "token expired / invalid" UI.

Async model
===========

Like :class:`LicenseRemote`, :class:`ClaimFlow` is **async-first**.
The two ``complete_*`` flows and ``request_magic_link`` are
coroutines that build a single HTTP request, await the response,
and persist the result on the local disk.

For callers that can't ``await`` -- notably PySide6 widget
constructors on the GUI thread -- the class exposes a thin sync
wrapper (:meth:`sync_request_magic_link`) that drives the
coroutine via ``asyncio.run()``. Same semantics as LicenseRemote:
safe from a sync context with NO existing event loop; raises
``RuntimeError`` if called from inside an async handler.

HTTP layer
==========

All HTTP goes through :meth:`ClaimFlow._http_post` /
:meth:`ClaimFlow._http_get`. Both are ``async def`` methods
returning ``(status_code, parsed_body)``. The default
implementation uses ``aiohttp``; tests override with
:class:`unittest.mock.AsyncMock` so the suite never opens a real
socket.

Enumeration safety
==================

``request_magic_link`` returns ``None`` on BOTH a successful 200
AND on a server-side 4xx/5xx that signals "the email isn't
registered". The two responses are indistinguishable to the
caller -- that's the point. The only failures that propagate as
exceptions are network errors (``ConnectionError``,
``asyncio.TimeoutError``, etc.), which the caller surfaces as
"unable to reach server, please try again".

The complete_* flows deliberately DO raise :class:`ClaimError`
on 401 / 410 -- those are real, recoverable-from-the-user's-side
errors (the token expired or was already consumed) and the
desktop UI needs to know which message to show.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict, Optional, Tuple
from urllib.parse import parse_qs, urlparse

import aiohttp

from nchantdoffice.license import tier_gate
from nchantdoffice.license.entitlement_cache import EntitlementCache
from nchantdoffice.license.install_store import InstallStore


__all__ = ["ClaimFlow", "ClaimError"]


# Module-level logger so caplog can pick up warnings in tests.
_logger = logging.getLogger("nchantdoffice.license.claim_flow")
if not _logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(name)s %(levelname)s %(message)s"))
    _logger.addHandler(_handler)
    _logger.setLevel(logging.INFO)


# -----------------------------------------------------------------------------
# Exceptions
# -----------------------------------------------------------------------------


class ClaimError(Exception):
    """Raised on claim consumption failure (401 / 410).

    Attributes
    ----------
    status : int
        The HTTP status code that triggered the failure (401 or
        410 are the only ones the desktop cares about; other
        4xx/5xx pass through as :class:`ClaimError` too, with
        the actual code preserved for telemetry).
    body : Any
        The parsed response body (or the raw text if the body
        wasn't JSON) so the caller can drive a more specific UI
        message.
    """

    def __init__(self, status: int, body: Any, message: str = "") -> None:
        self.status = status
        self.body = body
        self._message = message or (
            f"claim failed: HTTP {status}: {body!r}"
        )
        super().__init__(self._message)


# -----------------------------------------------------------------------------
# ClaimFlow
# -----------------------------------------------------------------------------


class ClaimFlow:
    """Desktop-side glue for the account-claim magic-link flow.

    See module docstring for the full architecture overview.

    Constructor
    -----------
    :param install_store: The :class:`InstallStore` whose
        ``install_id`` is sent to the server as part of the
        magic-link request.
    :param entitlement_cache: The :class:`EntitlementCache`
        where the server-issued ``entitlement_token`` is
        persisted after a successful claim.
    :param license_remote: The :class:`LicenseRemote` whose
        ``refresh`` is called after a successful claim so the
        desktop picks up the user's tier via the existing
        refresh path. (We could call ``refresh`` directly here,
        but going through LicenseRemote keeps the persistence
        logic in one place.)
    :param server_base_url: The server's base URL -- e.g.
        ``"https://api.nchantdoffice.com"``. The claim endpoint
        is appended by the methods themselves.
    :param http_timeout_seconds: Per-request timeout (default 30s).
    """

    # Path constants -- single source of truth for the two endpoints.
    _CLAIM_ISSUE_PATH = "/api/account/claim"
    _CLAIM_COMPLETE_PATH = "/api/account/claim"

    def __init__(
        self,
        install_store: InstallStore,
        entitlement_cache: EntitlementCache,
        license_remote: Any,  # LicenseRemote; kept untyped to avoid import cycle
        server_base_url: str,
        http_timeout_seconds: float = 30.0,
    ) -> None:
        self._install_store = install_store
        self._entitlement_cache = entitlement_cache
        self._license_remote = license_remote
        # Trim a trailing slash so URL concatenation is predictable.
        self._server_base_url = server_base_url.rstrip("/")
        self._http_timeout_seconds = http_timeout_seconds

    # ---------- public flows -------------------------------------------------

    async def request_magic_link(self, email: str) -> None:
        """POST /api/account/claim {email, install_id}.

        Always returns ``None`` on success-or-known-failure. The
        server returns 200 for both "email is registered" and
        "email isn't registered" -- enumeration-safe -- so we
        don't try to distinguish them here.

        Raises on network errors (the caller can show "unable
        to reach server, please try again"). HTTP errors
        (4xx/5xx) from the server are intentionally swallowed
        for the same enumeration-safety reason: if the server
        ever returns 4xx for an unknown email, returning the
        status code would leak the same information.
        """
        record = self._install_store.get_or_create()
        payload = {
            "email": email,
            "install_id": record["install_id"],
        }
        # We do NOT inspect the return status -- 200 vs 4xx are
        # both "OK" from the desktop's perspective. The only
        # failures that propagate are network errors.
        await self._http_post(self._CLAIM_ISSUE_PATH, payload)
        return None

    async def complete_from_browser(self, deep_link_url: str) -> Dict[str, Any]:
        """Parse a magic-link deep-link URL and consume the token.

        ``deep_link_url`` is typically a URL the OS handed back
        via the custom URL scheme registered in the application
        bundle (e.g. ``nchantdoffice://claim?token=…&install_id=…``
        or ``https://nchantdoffice.com/account/claim?token=…``
        -- both forms work; the URL parser only cares about the
        query string).

        Calls :meth:`complete_from_url_params` with the parsed
        ``token`` and ``install_id`` query params.

        Returns the 200 response body on success. Raises
        :class:`ClaimError` on 401 / 410 so the caller can show
        the appropriate "token expired / invalid" UI.
        """
        parsed = urlparse(deep_link_url)
        query = parse_qs(parsed.query)
        # parse_qs returns lists (to support repeated keys); we
        # only ever have one token / one install_id, so take the
        # first element.
        token_values = query.get("token")
        if not token_values:
            raise ClaimError(
                status=0,
                body={"error": "deep_link_missing_token"},
                message=f"deep-link URL has no token param: {deep_link_url!r}",
            )
        token = token_values[0]
        install_id_values = query.get("install_id")
        install_id = install_id_values[0] if install_id_values else None

        return await self.complete_from_url_params(
            token=token, install_id=install_id
        )

    async def complete_from_url_params(
        self,
        token: str,
        install_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """GET /api/account/claim?token=…&install_id=….

        On 200:
          - persist the returned ``entitlement_token`` via
            :meth:`EntitlementCache.store`;
          - re-install the tier-getter on ``tier_gate`` so
            widgets immediately pick up the new tier;
          - return the response dict.

        On 401 / 410:
          - raise :class:`ClaimError` with the status preserved
            for telemetry. No cache mutation -- the token has
            either expired or was consumed already; nothing to
            persist.

        Any other non-200 status code is also treated as
        :class:`ClaimError` -- the desktop UI wants to know
        about every failure mode for telemetry, even if the
        user-visible UX is the same "please try the link
        again".
        """
        params: Dict[str, str] = {"token": token}
        if install_id is not None:
            params["install_id"] = install_id

        status, body = await self._http_get(self._CLAIM_COMPLETE_PATH, params)

        if status == 200:
            if not isinstance(body, dict):
                raise ClaimError(
                    status=200,
                    body=body,
                    message="account/claim returned non-dict body",
                )
            # Persist the entitlement token + envelope. The
            # server's response shape is:
            #   {ok, user_id, install_bound, desktop_uuid,
            #    email, entitlement_token, entitlements}
            # We only need ``entitlement_token`` and
            # ``entitlements`` (the envelope dict). If
            # ``entitlements`` is missing, fall back to a
            # minimal envelope derived from the top-level tier
            # field, so the cache always stores something
            # usable.
            ent_token = body.get("entitlement_token")
            envelope = body.get("entitlements")
            if not isinstance(envelope, dict):
                # Fallback: synthesise a minimal envelope from
                # the top-level fields the server returned.
                # The server is supposed to include
                # ``entitlements``; this branch is only hit
                # for older / non-conforming server builds.
                tier = body.get("tier")
                envelope = {
                    "tier": tier if isinstance(tier, str) else "free",
                    "feat": [],
                }
            if not isinstance(ent_token, str):
                raise ClaimError(
                    status=200,
                    body=body,
                    message=(
                        "account/claim response missing entitlement_token"
                    ),
                )
            self._entitlement_cache.store(token=ent_token, envelope=envelope)
            # Re-install the tier-getter so widgets immediately
            # pick up the new tier. Idempotent.
            self._install_tier_getter()
            return body

        # Non-200 → ClaimError. Caller drives the appropriate UI.
        raise ClaimError(
            status=status,
            body=body,
            message=f"account/claim returned HTTP {status}: {body!r}",
        )

    # ---------- sync wrapper -------------------------------------------------

    def sync_request_magic_link(self, email: str) -> None:
        """``asyncio.run`` wrapper around :meth:`request_magic_link`.

        Use from synchronous call sites (PySide6 widget
        constructors, ``__main__`` blocks, etc.) where awaiting
        is not an option. Raises ``RuntimeError`` if called
        from inside an existing event loop -- that's a
        programmer error and we want it to fail loudly.
        """
        return asyncio.run(self.request_magic_link(email))

    # ---------- HTTP seam ----------------------------------------------------

    async def _http_post(
        self,
        path: str,
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
    ) -> Tuple[int, Any]:
        """POST ``payload`` to ``{server_base_url}{path}``.

        Returns ``(status_code, parsed_body)``. ``parsed_body``
        is a dict for JSON responses and the raw text otherwise
        (so error-handling code can surface it without a second
        parse round-trip).

        Tests override this with an
        :class:`unittest.mock.AsyncMock` so the test suite never
        opens a real socket. The signature is intentionally
        narrow (status + body) -- any auth-token handling or
        retry logic should live in the caller.
        """
        url = f"{self._server_base_url}{path}"
        request_headers = {"Content-Type": "application/json"}
        if headers:
            request_headers.update(headers)

        timeout = aiohttp.ClientTimeout(total=self._http_timeout_seconds)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                url, json=payload, headers=request_headers
            ) as response:
                text = await response.text()
                try:
                    parsed: Any = json.loads(text) if text else None
                except json.JSONDecodeError:
                    parsed = text
                return response.status, parsed

    async def _http_get(
        self,
        path: str,
        params: Dict[str, str],
        headers: Optional[Dict[str, str]] = None,
    ) -> Tuple[int, Any]:
        """GET ``{server_base_url}{path}?{params}``.

        Returns ``(status_code, parsed_body)``. Same shape
        contract as :meth:`_http_post` -- tests override with
        ``AsyncMock``.
        """
        url = f"{self._server_base_url}{path}"
        request_headers: Dict[str, str] = {}
        if headers:
            request_headers.update(headers)

        timeout = aiohttp.ClientTimeout(total=self._http_timeout_seconds)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(
                url, params=params, headers=request_headers
            ) as response:
                text = await response.text()
                try:
                    parsed: Any = json.loads(text) if text else None
                except json.JSONDecodeError:
                    parsed = text
                return response.status, parsed

    # ---------- tier-getter wiring -------------------------------------------

    def _install_tier_getter(self) -> None:
        """Install the cache's ``load`` as the tier-getter on tier_gate.

        Same pattern as :meth:`LicenseRemote._install_tier_getter`
        -- kept independent (not shared) so a change to one
        doesn't ripple to the other.

        Idempotent -- safe to call multiple times. Tests verify
        the getter is wired and that
        ``tier_gate.current_tier()`` returns the new tier.
        """
        cache = self._entitlement_cache

        def _getter() -> Optional[Dict[str, Any]]:
            record = cache.load()
            if record is None:
                return None
            return record.get("envelope")

        tier_gate.set_tier_getter(_getter)
