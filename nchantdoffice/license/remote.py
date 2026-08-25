"""nchantdoffice.license — async client wrapping the server-side license API.

DESK T-NEW-048 lives here. The :class:`LicenseRemote` is the only
class in the desktop that talks to ``https://<server>/api/desktop/...``.
It is responsible for:

  1. **Bootstrap** — first-launch registration. Called once when the
     :class:`EntitlementCache` is empty. Persists the server-issued
     ``api_key`` + ``desktop_uuid`` into :class:`InstallStore` and
     the ``entitlement_token`` + envelope into
     :class:`EntitlementCache`.

  2. **Refresh** — token rotation. Called on app start when the
     cached envelope is expired-or-close, or when the last refresh
     flagged ``entitlement_stale=True``.

The claim flow (magic-link to a desktop install) is DESK T-NEW-049
and lives in :mod:`nchantdoffice.widgets.config.accounts` — NOT
here.

Async model
===========

:class:`LicenseRemote` is **async-first**. ``bootstrap`` and
``refresh`` are coroutines that build a single HTTP request, await
the response, and persist the result on the local disk.

For callers that can't ``await`` — notably PySide6 widget
constructors on the GUI thread — the class exposes two thin
sync wrappers (:meth:`sync_bootstrap`, :meth:`sync_refresh`) that
drive the coroutine via ``asyncio.run()``. ``asyncio.run()`` is
safe to call from a sync context with NO existing event loop; it
will raise ``RuntimeError`` if a loop is already running, which is
exactly the right behaviour for a widget that should never be
called from inside an async handler. The widget code that runs
inside Qt's event loop is expected to use the async surface
directly (via a worker thread or ``qasync``); the sync wrappers
are for the bootstrap-and-die flow at app start.

HTTP layer
==========

All HTTP goes through :meth:`LicenseRemote._http_post`, which is
an ``async def`` method returning ``(status_code, parsed_body)``.
The default implementation uses ``aiohttp``; tests override it
with an :class:`unittest.mock.AsyncMock` so the test suite never
touches a real socket. Swapping the implementation out is also
the natural place to plug in a fake-license server for
integration tests later.

Server response shapes (from the sister nchantdoffice_com repo)
================================================================

``POST /api/desktop/install-bootstrap`` → 201::

    {
        "desktop_uuid":  "<uuid>",
        "api_key":       "<nk_...>",
        "install_id":    "<uuid>",
        "user_fk":       <int>,
        "entitlements":  {<dict>},
        "entitlement_token": "<fernet-string>"
    }

``POST /api/desktop/entitlement/refresh`` → 200::

    {
        "tier":              "<free|pro|...>",
        "features":          ["..."],
        "expires_at":        <epoch-seconds>,
        "entitlements":      {<dict>},
        "entitlement_token": "<fernet-string>"
    }

Errors come back as ``{"ok": false, "error": "<message>"}`` with
HTTP status matching the failure mode:

  - 400 — bad request body / shape mismatch;
  - 403 — hardware_key mismatch (server has a record, but the
    caller's hardware_key doesn't hash to the stored hash);
  - 401 — api_key unknown / revoked (the server can't tell the
    difference, so the desktop must re-bootstrap to recover);
  - 410 — install revoked (the api_key is gone because the
    server-side install row was marked ``revoked_at``);
  - 429 — rate-limited by flask-limiter.

The 401+revoked disambiguation
==============================

When the server responds with 401 it could mean either:

  (a) ``api_key`` is genuinely unknown (typo / disk corruption /
      a key rotated by the server after a revoke-and-rebind); or
  (b) the install row was revoked and the server can no longer
      map the api_key to anything.

The server's error envelope for (b) carries ``"install revoked"``
as the ``error`` field; for (a) it's ``"invalid api_key"``. The
:class:`LicenseRemote` treats any 401 with a revoked marker in
the body as :class:`RefreshRevokedError` so the caller can decide
to re-bootstrap; a plain 401 with no revoked marker is treated
as :class:`RefreshError` (caller will surface "license lost,
please reinstall").

Error hierarchy
===============

  - :class:`BootstrapError` — raised by ``bootstrap`` on 4xx/5xx
    that isn't a transient network failure. Carries the HTTP
    status and the parsed body so the caller can show a useful
    UI message.
  - :class:`RefreshError` — raised by ``refresh`` on transient
    failures (network errors, non-revoked 5xx).
  - :class:`RefreshRevokedError` — subclass of :class:`RefreshError`,
    raised by ``refresh`` on 410 or on 401 with a revoked marker.
    The caller can catch it specifically to drive a re-bootstrap
    flow.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Awaitable, Callable, Dict, Optional, Tuple

import aiohttp

from nchantdoffice.license.entitlement_cache import EntitlementCache
from nchantdoffice.license.install_store import InstallStore
from nchantdoffice.license import tier_gate


__all__ = [
    "LicenseRemote",
    "BootstrapError",
    "RefreshError",
    "RefreshRevokedError",
]


# Module-level logger so caplog can pick up warnings in tests.
_logger = logging.getLogger("nchantdoffice.license.remote")
if not _logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(name)s %(levelname)s %(message)s"))
    _logger.addHandler(_handler)
    _logger.setLevel(logging.INFO)


# Markers the server includes in the ``error`` field of a 401/410
# response when the install row was revoked. The desktop treats
# these as a re-bootstrap signal — the same machine + hardware_key
# may re-register.
_REVOKED_MARKERS = ("install revoked", "revoked")


def _body_indicates_revoked(body: Any) -> bool:
    """Return True if the parsed response body carries a revoked
    marker in its ``error`` field.

    The server's error envelope is ``{"ok": false, "error": "..."}``.
    A revoked install shows up as either a 401 with body
    ``{"error": "install revoked"}`` (the server can't tell apart
    "unknown api_key" from "api_key for a revoked row" because
    both lookups return None) or as a 410 with the same body.
    A genuine "unknown api_key" carries ``{"error": "invalid
    api_key"}`` which we treat as non-revoked — the caller decides
    whether to re-bootstrap or surface a "license lost" error.
    """
    if not isinstance(body, dict):
        return False
    err = body.get("error")
    if not isinstance(err, str):
        return False
    lower = err.lower()
    return any(marker in lower for marker in _REVOKED_MARKERS)


# -----------------------------------------------------------------------------
# Exceptions
# -----------------------------------------------------------------------------


class BootstrapError(Exception):
    """Raised by :meth:`LicenseRemote.bootstrap` on a 4xx/5xx response.

    Carries the HTTP status code and the parsed body (or raw text
    if the body wasn't JSON) so the caller can drive an
    appropriate UI flow.

    Network errors (DNS failure, refused connection, etc.) do NOT
    raise BootstrapError — they propagate as :class:`aiohttp.ClientError`
    or :class:`asyncio.TimeoutError` so the caller can treat them
    as "offline, try again later" rather than a license failure.
    """

    def __init__(self, status: int, body: Any, message: str = "") -> None:
        self.status = status
        self.body = body
        self._message = message or (
            f"bootstrap failed: HTTP {status}: {body!r}"
        )
        super().__init__(self._message)


class RefreshError(Exception):
    """Raised by :meth:`LicenseRemote.refresh` on transient failures.

    Transient = 5xx, network error, or 401 without a revoked
    marker. The caller should NOT automatically re-bootstrap —
    the user may simply be offline.
    """

    def __init__(self, status: int = 0, body: Any = None, message: str = "") -> None:
        self.status = status
        self.body = body
        self._message = message or (
            f"refresh failed: HTTP {status}: {body!r}"
        )
        super().__init__(self._message)


class RefreshRevokedError(RefreshError):
    """Raised by :meth:`LicenseRemote.refresh` when the install row
    is no longer reachable on the server.

    Triggered by:

      - a 410 response (server saw the api_key but the install
        row is revoked);
      - a 401 response whose body carries a revoked marker (see
        :func:`_body_indicates_revoked`).

    The caller may attempt :meth:`LicenseRemote.bootstrap` again
    with the same ``install_id`` + ``hardware_key`` — if the
    hardware_key still hashes to the server's value, the server
    will re-issue a fresh ``api_key`` + ``desktop_uuid`` pair.
    """


# -----------------------------------------------------------------------------
# LicenseRemote
# -----------------------------------------------------------------------------


class LicenseRemote:
    """Async aiohttp client wrapping the server-side license API.

    See the module docstring for the full architecture overview.

    Constructor
    -----------
    :param install_store: The :class:`InstallStore` whose
        ``save_api_credentials`` is called after a successful
        bootstrap.
    :param entitlement_cache: The :class:`EntitlementCache` where
        the bootstrap and refresh tokens are persisted.
    :param server_base_url: The server's base URL — e.g.
        ``"https://api.nchantdoffice.com"``. The bootstrap and
        refresh endpoints are appended by the methods themselves.
    :param http_timeout_seconds: Per-request timeout (default 30s).
        Long enough for the first bootstrap on a slow network;
        short enough to fail fast on a hung connection.

    Lifecycle
    ---------
    LicenseRemote holds no resources that need explicit cleanup
    (aiohttp.ClientSession is created on demand inside
    :meth:`_http_post` and closed in the same coroutine). Tests
    reuse a single instance freely.

    Failure isolation
    -----------------
    The two public flows (``bootstrap``, ``refresh``) catch
    aiohttp network errors and re-raise them as the relevant
    :class:`BootstrapError` / :class:`RefreshError` subclass so the
    caller doesn't have to import aiohttp to handle them. JSON
    parse failures on the response body raise the same.
    """

    # Path constants — single source of truth for the two endpoints.
    _BOOTSTRAP_PATH = "/api/desktop/install-bootstrap"
    _REFRESH_PATH = "/api/desktop/entitlement/refresh"

    def __init__(
        self,
        install_store: InstallStore,
        entitlement_cache: EntitlementCache,
        server_base_url: str,
        http_timeout_seconds: float = 30.0,
    ) -> None:
        self._install_store = install_store
        self._entitlement_cache = entitlement_cache
        # Trim a trailing slash so URL concatenation is predictable.
        self._server_base_url = server_base_url.rstrip("/")
        self._http_timeout_seconds = http_timeout_seconds

    # ---------- public flows -------------------------------------------------

    async def bootstrap(
        self,
        install_id: str,
        hardware_key: str,
        public_key: str,
        os: str,
        app_version: str,
    ) -> Dict[str, Any]:
        """POST ``/api/desktop/install-bootstrap``.

        Parameters
        ----------
        install_id : str
            UUID4 minted by :meth:`InstallStore.get_or_create`.
        hardware_key : str
            64-hex-char PBKDF2-derived key (see
            :meth:`InstallStore._derive_hardware_key`).
        public_key : str
            The desktop's age-verification public key (PEM-encoded
            RSA / Ed25519, server stores the fingerprint). This
            module passes it through opaquely — it doesn't parse
            the key, the server does.
        os : str
            One of ``"linux"`` / ``"macos"`` / ``"windows"`` — the
            server validates against an allow-list and 400s on
            anything else.
        app_version : str
            Desktop version string (informational; not validated
            by the server).

        Returns
        -------
        dict
            The 201 response body. The relevant keys
            (``api_key``, ``desktop_uuid``, ``entitlement_token``,
            ``entitlements``) are also persisted as side-effects
            before the method returns.

        Raises
        ------
        BootstrapError
            On 400 / 403 / 429 / 5xx. Network errors propagate as
            :class:`aiohttp.ClientError` or
            :class:`asyncio.TimeoutError`.
        """
        payload = {
            "install_id": install_id,
            "hardware_key": hardware_key,
            "public_key": public_key,
            "os": os,
            "app_version": app_version,
        }
        status, body = await self._http_post(self._BOOTSTRAP_PATH, payload)

        if status != 201:
            raise BootstrapError(
                status=status,
                body=body,
                message=(
                    f"install-bootstrap returned HTTP {status}: "
                    f"{body!r}"
                ),
            )

        # Validate the response shape — server-side bugs (a missing
        # api_key, etc.) should fail loudly rather than silently
        # persist a half-populated record.
        if not isinstance(body, dict):
            raise BootstrapError(
                status=201,
                body=body,
                message="install-bootstrap returned non-dict body",
            )
        api_key = body.get("api_key")
        desktop_uuid = body.get("desktop_uuid")
        token = body.get("entitlement_token")
        envelope = body.get("entitlements")
        if not isinstance(api_key, str) or not isinstance(desktop_uuid, str):
            raise BootstrapError(
                status=201,
                body=body,
                message=(
                    "install-bootstrap response missing api_key or "
                    "desktop_uuid"
                ),
            )
        if not isinstance(token, str) or not isinstance(envelope, dict):
            raise BootstrapError(
                status=201,
                body=body,
                message=(
                    "install-bootstrap response missing entitlement_token "
                    "or entitlements envelope"
                ),
            )

        # Persist in this order: install store first (credentials
        # are the hard thing to lose — if we crash after this
        # point the cache will be repopulated by the next refresh),
        # then entitlement cache.
        self._install_store.save_api_credentials(
            api_key=api_key, desktop_uuid=desktop_uuid
        )
        self._entitlement_cache.store(token=token, envelope=envelope)

        # Wire the tier-getter so widgets immediately pick up the
        # bootstrapped tier. Idempotent — safe to call again on
        # every bootstrap.
        self._install_tier_getter()

        return body

    async def refresh(
        self,
        api_key: str,
        install_id: str,
        hardware_key: str,
    ) -> Dict[str, Any]:
        """POST ``/api/desktop/entitlement/refresh``.

        Parameters
        ----------
        api_key : str
            The server-issued api_key returned by a previous
            bootstrap. Pass ``install_store.get_or_create()['api_key']``.
        install_id : str
            UUID4 from the InstallStore. Sent in the body for
            server-side correlation (the header is the
            ``x-install-hardware-key``; the body has ``install_id``).
        hardware_key : str
            Same value used at bootstrap time.

        Returns
        -------
        dict
            The 200 response body. ``entitlement_token`` and
            ``entitlements`` are persisted as side-effects.

        Raises
        ------
        RefreshRevokedError
            On 410 (revoked) or on 401 with a revoked marker.
            The caller may attempt a fresh bootstrap; if the
            hardware_key still matches, the server will re-issue.
        RefreshError
            On 5xx, network errors, or 401 without a revoked
            marker. The caller should treat as "offline, retry
            later" rather than driving a re-bootstrap.

        Auto-retry policy
        -----------------
        This method does NOT auto-retry on 401. Per the plan,
        the caller owns the retry decision — it may want to ask
        the user before re-bootstrapping, or skip the bootstrap
        if the install is being deliberately rotated by the
        server (e.g. after a billing plan change).
        """
        payload = {"install_id": install_id}
        headers = {
            "x-api-key": api_key,
            "x-install-hardware-key": hardware_key,
        }
        status, body = await self._http_post(
            self._REFRESH_PATH, payload, headers=headers
        )

        if status == 200:
            if not isinstance(body, dict):
                raise RefreshError(
                    status=200,
                    body=body,
                    message="entitlement/refresh returned non-dict body",
                )
            token = body.get("entitlement_token")
            envelope = body.get("entitlements")
            if not isinstance(token, str) or not isinstance(envelope, dict):
                raise RefreshError(
                    status=200,
                    body=body,
                    message=(
                        "entitlement/refresh response missing "
                        "entitlement_token or entitlements envelope"
                    ),
                )
            self._entitlement_cache.store(token=token, envelope=envelope)
            # Re-install the tier-getter in case the cache was
            # cleared between bootstrap and now.
            self._install_tier_getter()
            return body

        if status == 410:
            # Hard revoke — mark the cache stale so the gate stops
            # granting pro features, then raise.
            self._entitlement_cache.mark_stale()
            raise RefreshRevokedError(
                status=status,
                body=body,
                message=(
                    f"entitlement/refresh returned HTTP 410 (revoked): "
                    f"{body!r}"
                ),
            )

        if status == 401 and _body_indicates_revoked(body):
            # Server saw the api_key but the install row is gone.
            # Same semantics as a 410 — mark stale and raise.
            self._entitlement_cache.mark_stale()
            raise RefreshRevokedError(
                status=status,
                body=body,
                message=(
                    f"entitlement/refresh returned HTTP 401 with revoked "
                    f"marker: {body!r}"
                ),
            )

        # Everything else (5xx, network errors that didn't raise,
        # plain 401, 403) → RefreshError. Caller decides retry.
        raise RefreshError(
            status=status,
            body=body,
            message=(
                f"entitlement/refresh returned HTTP {status}: {body!r}"
            ),
        )

    # ---------- sync wrappers ------------------------------------------------

    def sync_bootstrap(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """``asyncio.run`` wrapper around :meth:`bootstrap`.

        Use from synchronous call sites (PySide6 widget
        constructors, ``__main__`` blocks, etc.) where awaiting
        is not an option. Raises ``RuntimeError`` if called from
        inside an existing event loop — that's a programmer
        error and we want it to fail loudly.
        """
        return asyncio.run(self.bootstrap(*args, **kwargs))

    def sync_refresh(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """``asyncio.run`` wrapper around :meth:`refresh`."""
        return asyncio.run(self.refresh(*args, **kwargs))

    # ---------- HTTP seam ----------------------------------------------------

    async def _http_post(
        self,
        path: str,
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
    ) -> Tuple[int, Any]:
        """POST ``payload`` to ``{server_base_url}{path}``.

        Returns ``(status_code, parsed_body)``. ``parsed_body`` is
        a dict for JSON responses and the raw text otherwise (so
        error-handling code can surface it without a second parse
        round-trip).

        Tests override this with an :class:`unittest.mock.AsyncMock`
        so the test suite never opens a real socket. The signature
        is intentionally narrow (status + body) — any auth-token
        handling or retry logic should live in the caller.
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
                # Try to parse JSON; fall back to the raw body so the
                # caller can still surface a meaningful error
                # message for non-JSON responses (e.g. an upstream
                # proxy returning HTML).
                try:
                    parsed: Any = json.loads(text) if text else None
                except json.JSONDecodeError:
                    parsed = text
                return response.status, parsed

    # ---------- tier-getter wiring -------------------------------------------

    def _install_tier_getter(self) -> None:
        """Install the cache's ``load`` as the tier-getter on tier_gate.

        Called after a successful bootstrap or refresh so widgets
        that consult :func:`tier_gate.current_tier` immediately
        pick up the new envelope.

        Idempotent — safe to call multiple times. Tests verify the
        getter is wired and that ``tier_gate.current_tier()``
        returns the bootstrapped tier.
        """
        cache = self._entitlement_cache

        def _getter() -> Optional[Dict[str, Any]]:
            record = cache.load()
            if record is None:
                return None
            return record.get("envelope")

        tier_gate.set_tier_getter(_getter)


__all__ = [
    "LicenseRemote",
    "BootstrapError",
    "RefreshError",
    "RefreshRevokedError",
]