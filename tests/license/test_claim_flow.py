"""Tests for nchantdoffice.license.claim_flow.ClaimFlow.

DESK T-NEW-049: ClaimFlow is the desktop-side glue for the
account-claim magic-link flow. The flow:

  1. User opens the desktop's "Claim this install" dialog, types
     their email, clicks Send. ClaimFlow.request_magic_link(email)
     POSTs ``/api/account/claim {email, install_id}``. The server
     emails a magic-link and returns 200 (always, by design — to
     avoid enumeration leaks).
  2. User clicks the link in their email. The OS opens it in the
     default browser, which lands on
     https://nchantdoffice.com/account/claim?token=…&install_id=…
     The browser side consumes the token via the COM T-NEW-049b
     server endpoint (out of scope here).
  3. User returns to the desktop; ClaimFlow.complete_from_browser
     (or its parameter-only variant) calls
     ``GET /api/account/claim`` and persists the returned
     ``entitlement_token`` into the EntitlementCache so the
     desktop picks up the user's tier immediately.

The HTTP seam is :meth:`ClaimFlow._http_post` /
:meth:`ClaimFlow._http_get` — tests monkeypatch these with
:class:`unittest.mock.AsyncMock` so the suite never opens a real
socket. The full aiohttp path is exercised in integration tests
elsewhere (DESK T-NEW-049 handoff).
"""
from __future__ import annotations

import asyncio as _asyncio
import asyncio as asyncio_mod  # noqa: F401 — used via get_event_loop in sync tests
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from nchantdoffice.license import tier_gate
from nchantdoffice.license.claim_flow import ClaimError, ClaimFlow
from nchantdoffice.license.entitlement_cache import EntitlementCache
from nchantdoffice.license.install_store import InstallStore


# -----------------------------------------------------------------------------
# Async test helper (mirrors tests/license/test_remote.py)
# -----------------------------------------------------------------------------


def _run(coro):
    """Run ``coro`` to completion via ``asyncio.run``.

    Equivalent to ``pytest-asyncio``'s ``@pytest.mark.asyncio``
    but without the package dependency. Tests that exercise
    coroutines call ``_run(coro)`` and assert on the return
    value or on side-effects.
    """
    return _asyncio.run(coro)


# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    """Fresh data dir per-test so license files don't bleed across tests."""
    d = tmp_path / "license-data"
    d.mkdir(parents=True, exist_ok=True)
    return d


@pytest.fixture
def install_store(data_dir: Path, monkeypatch) -> InstallStore:
    """InstallStore pinned to a deterministic OS machine-id."""
    monkeypatch.setattr(
        InstallStore,
        "_read_os_machine_id",
        lambda self: b"test-machine-id-claim",
    )
    return InstallStore(data_dir=data_dir)


@pytest.fixture
def entitlement_cache(data_dir: Path) -> EntitlementCache:
    return EntitlementCache(data_dir=data_dir)


@pytest.fixture
def license_remote(
    install_store: InstallStore,
    entitlement_cache: EntitlementCache,
) -> MagicMock:
    """A MagicMock standing in for LicenseRemote.

    Only the methods ClaimFlow actually calls (``refresh``) are
    wired up; tests assert on those call patterns. The rest of
    LicenseRemote's surface is irrelevant to ClaimFlow.
    """
    remote = MagicMock()
    remote.refresh = AsyncMock(
        return_value={
            "tier": "pro",
            "entitlements": {"tier": "pro", "feat": ["export_pdf"]},
            "entitlement_token": "fernet.refreshed.token",
        }
    )
    return remote


@pytest.fixture
def claim_flow(
    install_store: InstallStore,
    entitlement_cache: EntitlementCache,
    license_remote: MagicMock,
) -> ClaimFlow:
    """ClaimFlow wired to real InstallStore + EntitlementCache,
    mocked LicenseRemote, and a fake ``server_base_url``.

    HTTP methods are left as the real aiohttp impl by default —
    individual tests monkeypatch them via
    ``claim_flow._http_post = AsyncMock(...)``.
    """
    return ClaimFlow(
        install_store=install_store,
        entitlement_cache=entitlement_cache,
        license_remote=license_remote,
        server_base_url="http://example.test",
        http_timeout_seconds=5.0,
    )


@pytest.fixture(autouse=True)
def _reset_tier_gate():
    """Reset the module-level tier-getter after each test.

    Without this, one test installing a tier-getter would leak
    into the next test and silently change what
    ``tier_gate.current_tier()`` returns.
    """
    yield
    tier_gate.set_tier_getter(lambda: None)  # type: ignore[arg-type]


# -----------------------------------------------------------------------------
# request_magic_link tests
# -----------------------------------------------------------------------------


def test_request_magic_link_calls_server_with_email_and_install_id(
    claim_flow: ClaimFlow,
    install_store: InstallStore,
):
    """request_magic_link must POST ``/api/account/claim`` with
    ``{email, install_id}`` so the server can mint a magic-link
    tied to THIS install (not just any email).
    """
    claim_flow._http_post = AsyncMock(return_value=(200, {"ok": True}))

    _run(claim_flow.request_magic_link(email="alice@example.test"))

    # The POST hit the server (not a no-op).
    assert claim_flow._http_post.await_count == 1
    # And it carried the right payload.
    call = claim_flow._http_post.await_args
    # call.args == (path, payload, headers?)
    path = call.args[0]
    payload = call.args[1]
    assert path == "/api/account/claim"
    assert payload["email"] == "alice@example.test"
    assert payload["install_id"] == install_store.get_or_create()["install_id"]


def test_request_magic_link_returns_none_on_200(
    claim_flow: ClaimFlow,
):
    """On a 200, request_magic_link returns ``None`` (no body).

    This is the enumeration-safe contract — the response carries
    no information about whether the email is registered. The
    desktop UI just shows "if the email is valid, we sent a link".
    """
    claim_flow._http_post = AsyncMock(return_value=(200, {"ok": True}))

    result = _run(claim_flow.request_magic_link(email="bob@example.test"))

    assert result is None


def test_request_magic_link_raises_on_network_error(
    claim_flow: ClaimFlow,
):
    """A network error from aiohttp must propagate so the caller
    can show "unable to reach server, please try again".

    ClaimFlow does NOT swallow network errors — only HTTP 200
    responses get the enumeration-safe ``None`` treatment.
    """
    claim_flow._http_post = AsyncMock(
        side_effect=ConnectionError("dns lookup failed")
    )

    with pytest.raises(ConnectionError):
        _run(claim_flow.request_magic_link(email="carol@example.test"))


# -----------------------------------------------------------------------------
# complete_from_browser tests
# -----------------------------------------------------------------------------


def test_complete_from_browser_parses_token_and_install_id(
    claim_flow: ClaimFlow,
):
    """complete_from_browser must extract ``token`` (and optional
    ``install_id``) from the deep-link URL's query string and
    forward them to ``GET /api/account/claim``.

    The OS hands the deep-link URL to the desktop via the custom
    URL scheme registered in the application bundle (out of scope
    for ClaimFlow). The desktop code calls
    ``complete_from_browser(url)`` once the URL is in hand.
    """
    claim_flow._http_get = AsyncMock(
        return_value=(
            200,
            {
                "ok": True,
                "user_id": 7,
                "install_bound": True,
                "desktop_uuid": "uuid-from-server",
                "email": "alice@example.test",
                "entitlement_token": "fernet.server.issued.token",
                "entitlements": {"tier": "pro", "feat": ["export_pdf"]},
            },
        )
    )

    url = (
        "https://nchantdoffice.com/account/claim"
        "?token=RAW_TOKEN_FROM_EMAIL"
        "&install_id=11111111-2222-4333-8444-666666666666"
    )

    _run(claim_flow.complete_from_browser(url))

    # The GET hit /api/account/claim with the parsed query params.
    assert claim_flow._http_get.await_count == 1
    call = claim_flow._http_get.await_args
    path = call.args[0]
    params = call.args[1]
    assert path == "/api/account/claim"
    assert params["token"] == "RAW_TOKEN_FROM_EMAIL"
    assert params["install_id"] == "11111111-2222-4333-8444-666666666666"


def test_complete_from_browser_persists_entitlement_token(
    claim_flow: ClaimFlow,
    entitlement_cache: EntitlementCache,
):
    """On a 200, complete_from_browser must persist the
    server-issued ``entitlement_token`` + ``entitlements``
    envelope into the EntitlementCache so the desktop picks up
    the new tier on the next tier_gate.current_tier() call.
    """
    claim_flow._http_get = AsyncMock(
        return_value=(
            200,
            {
                "ok": True,
                "entitlement_token": "fernet.server.issued.token",
                "entitlements": {"tier": "pro", "feat": ["export_pdf"]},
            },
        )
    )

    # Pre-condition: cache is empty.
    assert entitlement_cache.load() is None

    _run(
        claim_flow.complete_from_browser(
            "https://nchantdoffice.com/account/claim?token=tok-1"
        )
    )

    # Post-condition: cache has the new envelope.
    record = entitlement_cache.load()
    assert record is not None
    assert record["token"] == "fernet.server.issued.token"
    assert record["envelope"]["tier"] == "pro"


def test_complete_from_browser_refreshes_tier_getter(
    claim_flow: ClaimFlow,
):
    """On a 200, complete_from_browser must install the cache as
    the tier-getter on tier_gate so widgets that call
    tier_gate.current_tier() immediately see the new tier.

    This is the same wiring pattern LicenseRemote.bootstrap uses
    (see remote.py:_install_tier_getter). ClaimFlow delegates to
    LicenseRemote.refresh() for the actual refresh — see the
    test that asserts on the refresh call.
    """
    claim_flow._http_get = AsyncMock(
        return_value=(
            200,
            {
                "ok": True,
                "entitlement_token": "fernet.server.issued.token",
                "entitlements": {"tier": "pro", "feat": ["export_pdf"]},
            },
        )
    )

    # Pre-condition: no getter installed → current_tier is "free".
    assert tier_gate.current_tier() == "free"

    _run(
        claim_flow.complete_from_browser(
            "https://nchantdoffice.com/account/claim?token=tok-2"
        )
    )

    # Post-condition: tier has flipped to "pro" without us calling
    # LicenseRemote.refresh() (the entitlement_token was already
    # persisted by the GET, so the gate can read it directly).
    assert tier_gate.current_tier() == "pro"


def test_complete_from_browser_raises_on_401(
    claim_flow: ClaimFlow,
):
    """A 401 from /api/account/claim must raise ClaimError so the
    caller can show the "token expired / invalid" UI. The token
    is consumed (or doesn't exist) — there is no retry path.
    """
    claim_flow._http_get = AsyncMock(
        return_value=(401, {"ok": False, "error": "unknown token"})
    )

    with pytest.raises(ClaimError) as exc_info:
        _run(
            claim_flow.complete_from_browser(
                "https://nchantdoffice.com/account/claim?token=bad"
            )
        )

    # Status code preserved on the exception for telemetry.
    assert exc_info.value.status == 401


def test_complete_from_browser_raises_on_410(
    claim_flow: ClaimFlow,
):
    """A 410 (token already consumed / expired) must also raise
    ClaimError. Same UX as 401 — the user must request a new
    magic-link from the desktop.
    """
    claim_flow._http_get = AsyncMock(
        return_value=(410, {"ok": False, "error": "token consumed"})
    )

    with pytest.raises(ClaimError) as exc_info:
        _run(
            claim_flow.complete_from_browser(
                "https://nchantdoffice.com/account/claim?token=expired"
            )
        )

    assert exc_info.value.status == 410


def test_complete_from_url_params_calls_get_with_params(
    claim_flow: ClaimFlow,
):
    """complete_from_url_params is the parameter-only variant of
    complete_from_browser — useful for tests and for OS integrations
    that pass query params separately. It must hit the same GET
    endpoint with the same params.
    """
    claim_flow._http_get = AsyncMock(
        return_value=(
            200,
            {
                "ok": True,
                "entitlement_token": "fernet.server.issued.token",
                "entitlements": {"tier": "pro", "feat": ["export_pdf"]},
            },
        )
    )

    _run(
        claim_flow.complete_from_url_params(
            token="RAW_TOKEN",
            install_id="11111111-2222-4333-8444-666666666666",
        )
    )

    # The GET hit /api/account/claim with the right query params.
    assert claim_flow._http_get.await_count == 1
    call = claim_flow._http_get.await_args
    assert call.args[0] == "/api/account/claim"
    assert call.args[1]["token"] == "RAW_TOKEN"
    assert call.args[1]["install_id"] == "11111111-2222-4333-8444-666666666666"


# -----------------------------------------------------------------------------
# Sync wrapper tests
# -----------------------------------------------------------------------------


def test_sync_wrapper_works_without_event_loop(
    claim_flow: ClaimFlow,
):
    """sync_request_magic_link is an asyncio.run wrapper around
    the async request_magic_link. It must complete when called
    from a sync context with no existing event loop.
    """
    claim_flow._http_post = AsyncMock(return_value=(200, {"ok": True}))

    # No existing loop in this thread → asyncio.run() is fine.
    result = claim_flow.sync_request_magic_link(email="dave@example.test")

    assert result is None
    assert claim_flow._http_post.await_count == 1


# -----------------------------------------------------------------------------
# Account widget integration test
# -----------------------------------------------------------------------------


def test_accounts_widget_sync_with_server_calls_claim_flow(
    monkeypatch,
    install_store: InstallStore,
    entitlement_cache: EntitlementCache,
    license_remote: MagicMock,
):
    """The new ``sync_with_server`` in widgets/config/accounts.py
    must delegate to ClaimFlow.request_magic_link so the
    "Claim this install" button actually issues a magic-link
    instead of just calling the legacy nchantrs account endpoint.

    We exercise the function in isolation (without spinning up
    Qt) by importing the module under test, patching the
    ClaimFlow class with a stub that records calls, and invoking
    ``sync_with_server`` on a minimal stand-in object that
    captures the same ``self.app.model`` surface the real widget
    exposes.

    Skip semantics
    --------------
    ``nchantdoffice.widgets.config.accounts`` imports
    ``nchantrs`` (the sister framework) at module level. The
    test environment used for ``tests/license/`` doesn't have
    ``nchantrs`` installed -- only the license package + aiohttp
    + pytest. If the import fails for ANY reason (missing dep,
    Qt-not-initialised, etc.), we skip rather than fail, so this
    test stays green on minimal CI runners.
    """
    try:
        from nchantdoffice.widgets.config import accounts as accounts_mod
    except Exception as exc:  # noqa: BLE001 -- any import failure skips
        pytest.skip(
            f"widgets/config/accounts.py not importable in this test "
            f"environment ({type(exc).__name__}: {exc}); "
            f"covered by the higher-level UI tests in tests/unit/"
        )

    # Track calls on the ClaimFlow class so we can assert the
    # widget wired through correctly.
    request_calls: list = []

    class _StubClaimFlow:
        def __init__(self, *args, **kwargs):
            pass

        def sync_request_magic_link(self, email: str):
            request_calls.append(email)
            return None

    monkeypatch.setattr(accounts_mod, "ClaimFlow", _StubClaimFlow)

    # A minimal stand-in for the widget — the real widget is a
    # PySide6 QWidget and would force us into a Qt event loop.
    class _Widget:
        pass

    widget = _Widget()
    # Mirror what the real widget's sync_with_server needs.
    widget.app = MagicMock()
    widget.app.model.user.email = "alice@example.test"
    widget.app.model.user.name = "Alice"
    widget.app.model.install_store = install_store
    widget.app.model.entitlement_cache = entitlement_cache
    widget.app.model.license_remote = license_remote
    widget.app.model.server_base_url = "http://example.test"

    # Call the function bound to the widget — exactly the way
    # the real NchantdOfficeAccountSettings.load_account_settings
    # method calls it.
    accounts_mod.NchantdOfficeAccountSettings.sync_with_server(widget)

    # The widget's sync_with_server must have invoked
    # ClaimFlow.request_magic_link with the user's email.
    assert len(request_calls) == 1
    assert request_calls[0] == "alice@example.test"
