"""Tests for nchantdoffice.license.remote.LicenseRemote.

DESK T-NEW-048: LicenseRemote is the only async HTTP client in
the desktop. These tests cover the two flows the production
desktop actually calls:

  - bootstrap()  — first-launch registration. Persists api_key
                   + desktop_uuid into the InstallStore and the
                   entitlement_token + envelope into the
                   EntitlementCache. Installs a tier-getter on
                   tier_gate so widgets pick up the new tier.

  - refresh()    — token rotation. Persists a new
                   entitlement_token + envelope. Marks the cache
                   stale on 410 / 401-with-revoked-marker.

The tests use :class:`unittest.mock.AsyncMock` to monkeypatch
``LicenseRemote._http_post`` so the test suite never opens a real
socket. The full aiohttp.ClientSession path is exercised by
manual / integration tests (DESK T-NEW-049 handoff), not here.
"""
from __future__ import annotations

import asyncio as _asyncio
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from nchantdoffice.license import tier_gate
from nchantdoffice.license.entitlement_cache import EntitlementCache
from nchantdoffice.license.install_store import InstallStore
from nchantdoffice.license.remote import (
    BootstrapError,
    LicenseRemote,
    RefreshError,
    RefreshRevokedError,
)


# -----------------------------------------------------------------------------
# Async test helper
# -----------------------------------------------------------------------------
#
# The desktop test environment does NOT have pytest-asyncio
# installed (verified via `python -c "import pytest_asyncio"` —
# ImportError). The task constraint is "do not modify pyproject
# or requirements", so we run each async test via a small
# ``_run`` helper that mirrors the production ``asyncio.run``
# pattern. Tests look like::
#
#     def test_x(remote):
#         remote._http_post = AsyncMock(return_value=(201, body))
#         result = _run(
#             remote.bootstrap(install_id=..., hardware_key=..., ...)
#         )
#         assert result["api_key"] == body["api_key"]
#
# The pattern is intentionally the same one the sync wrappers
# use (``asyncio.run``) — so a regression in event-loop handling
# would surface both here AND in production.
def _run(coro):
    """Run ``coro`` to completion via ``asyncio.run``.

    Equivalent to ``pytest-asyncio``'s ``@pytest.mark.asyncio``
    but without the package dependency. Tests that exercise
    coroutines should call ``_run(coro)`` and assert on the
    return value or on side-effects.
    """
    return _asyncio.run(coro)


# -----------------------------------------------------------------------------
# Helpers + fixtures
# -----------------------------------------------------------------------------


# Server-side response shapes — these match the contract in the
# sister nchantdoffice_com repo (nchantdoffice_com/app/apis/
# desktop_install_api.py). When that contract changes, these
# fixtures must change too.
def _bootstrap_201_body() -> dict:
    """A canonical 201 response from /api/desktop/install-bootstrap.

    The fixture mirrors the server's actual response shape:
        {desktop_uuid, api_key, install_id, user_fk, entitlements,
         entitlement_token}
    """
    return {
        "desktop_uuid": "11111111-2222-4333-8444-555555555555",
        "api_key": "nk_test_" + "a" * 32,
        "install_id": "11111111-2222-4333-8444-666666666666",
        "user_fk": 42,
        "entitlements": {
            "tier": "pro",
            # ``feat`` is what tier_gate.has_feature() reads (see
            # nchantdoffice/license/tier_gate.py — single source of
            # truth for the desktop-side envelope shape). We include
            # BOTH keys here so tests against either contract path
            # pass — the server's envelope may use ``features`` in
            # the response but the desktop normalises to ``feat``
            # when the cache loads it. Tracked as a future cleanup
            # in tier_gate (out of scope for DESK T-NEW-048).
            "feat": ["export_pdf", "cloud_sync"],
            "features": ["export_pdf", "cloud_sync"],
            "exp": 9999999999,  # far future — does not trigger refresh
            "user_fk": 42,
        },
        "entitlement_token": "fernet.test.token." + "x" * 32,
    }


def _refresh_200_body() -> dict:
    """A canonical 200 response from /api/desktop/entitlement/refresh."""
    return {
        "tier": "pro_data",
        "feat": ["export_pdf", "cloud_sync", "multi_seat"],
        "features": ["export_pdf", "cloud_sync", "multi_seat"],
        "expires_at": 9999999999,
        "entitlements": {
            "tier": "pro_data",
            "feat": ["export_pdf", "cloud_sync", "multi_seat"],
            "features": ["export_pdf", "cloud_sync", "multi_seat"],
            "exp": 9999999999,
            "user_fk": 42,
        },
        "entitlement_token": "fernet.rotated.token." + "y" * 32,
    }


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
        InstallStore, "_read_os_machine_id",
        lambda self: b"test-machine-id-remote",
    )
    return InstallStore(data_dir=data_dir)


@pytest.fixture
def entitlement_cache(data_dir: Path) -> EntitlementCache:
    return EntitlementCache(data_dir=data_dir)


@pytest.fixture
def remote(
    install_store: InstallStore,
    entitlement_cache: EntitlementCache,
) -> LicenseRemote:
    """LicenseRemote with a real InstallStore + EntitlementCache.

    The ``_http_post`` method is left as the real aiohttp impl by
    default — individual tests monkeypatch it to an AsyncMock so
    the suite never opens a socket.
    """
    return LicenseRemote(
        install_store=install_store,
        entitlement_cache=entitlement_cache,
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
# bootstrap() tests
# -----------------------------------------------------------------------------


def test_bootstrap_persists_api_key_and_desktop_uuid_on_201(
    remote: LicenseRemote,
    install_store: InstallStore,
):
    """On 201, the bootstrap flow must persist api_key +
    desktop_uuid into the InstallStore (so subsequent refreshes
    have a stable api_key to send).
    """
    body = _bootstrap_201_body()
    remote._http_post = AsyncMock(return_value=(201, body))

    _run(
        remote.bootstrap(
            install_id="11111111-2222-4333-8444-666666666666",
            hardware_key="a" * 64,
            public_key="-----BEGIN PUBLIC KEY-----fake",
            os="linux",
            app_version="1.2.3",
        )
    )

    record = install_store.get_or_create()
    assert record["api_key"] == body["api_key"]
    assert record["desktop_uuid"] == body["desktop_uuid"]


def test_bootstrap_persists_entitlement_token_in_cache(
    remote: LicenseRemote,
    entitlement_cache: EntitlementCache,
):
    """On 201, the bootstrap flow must persist the
    entitlement_token + entitlements envelope into the
    EntitlementCache so widgets can gate features without a
    network round-trip.
    """
    body = _bootstrap_201_body()
    remote._http_post = AsyncMock(return_value=(201, body))

    _run(
        remote.bootstrap(
            install_id="11111111-2222-4333-8444-666666666666",
            hardware_key="a" * 64,
            public_key="fake-pem",
            os="linux",
            app_version="1.2.3",
        )
    )

    record = entitlement_cache.load()
    assert record is not None
    assert record["token"] == body["entitlement_token"]
    assert record["envelope"]["tier"] == body["entitlements"]["tier"]
    # stale flag must be False on a fresh bootstrap.
    assert record["stale"] is False


def test_bootstrap_installs_tier_getter(
    remote: LicenseRemote,
):
    """On 201, bootstrap must install the EntitlementCache as the
    tier-getter on tier_gate so widgets that call
    tier_gate.current_tier() immediately see the bootstrapped
    tier (without waiting for the next event-loop turn).
    """
    body = _bootstrap_201_body()
    remote._http_post = AsyncMock(return_value=(201, body))

    # Pre-condition: no getter installed yet → current_tier is "free"
    # (the fail-closed default).
    assert tier_gate.current_tier() == "free"

    _run(
        remote.bootstrap(
            install_id="11111111-2222-4333-8444-666666666666",
            hardware_key="a" * 64,
            public_key="fake-pem",
            os="linux",
            app_version="1.2.3",
        )
    )

    # Post-condition: getter is installed and current_tier reflects
    # the bootstrapped envelope.
    assert tier_gate.current_tier() == body["entitlements"]["tier"]
    # And has_feature() works against the new envelope.
    assert tier_gate.has_feature("export_pdf") is True


def test_bootstrap_raises_on_4xx(remote: LicenseRemote):
    """A 400 / 403 / 429 response must raise BootstrapError with
    the status + body attached so the caller can drive an
    appropriate UI message.
    """
    # 400 — bad request shape (server's actual _bad_shape helper
    # returns {"ok": False, "error": "<msg>"}, status 400).
    body = {"ok": False, "error": "missing install_id"}
    remote._http_post = AsyncMock(return_value=(400, body))

    with pytest.raises(BootstrapError) as exc_info:
        _run(
            remote.bootstrap(
                install_id="x",
                hardware_key="a" * 64,
                public_key="fake-pem",
                os="bogus-os",  # this triggers the 400 in the real server
                app_version="1.2.3",
            )
        )

    assert exc_info.value.status == 400
    assert exc_info.value.body == body


# -----------------------------------------------------------------------------
# refresh() tests
# -----------------------------------------------------------------------------


def test_refresh_persists_new_entitlement_token(
    remote: LicenseRemote,
    entitlement_cache: EntitlementCache,
):
    """On 200, refresh must persist the new entitlement_token +
    envelope into the EntitlementCache, replacing whatever was
    there before.
    """
    # Seed the cache with a stale token so we can verify it gets
    # overwritten (not appended).
    entitlement_cache.store(
        token="old.token.value",
        envelope={"tier": "free", "features": [], "exp": 1},
    )

    body = _refresh_200_body()
    remote._http_post = AsyncMock(return_value=(200, body))

    api_key = "nk_test_" + "z" * 32
    result = _run(
        remote.refresh(
            api_key=api_key,
            install_id="11111111-2222-4333-8444-666666666666",
            hardware_key="a" * 64,
        )
    )

    # Returned dict is the response body.
    assert result["tier"] == body["tier"]
    # Cache now has the NEW token, not the old one.
    record = entitlement_cache.load()
    assert record is not None
    assert record["token"] == body["entitlement_token"]
    assert record["envelope"]["tier"] == body["entitlements"]["tier"]
    # And stale flag is False on a successful refresh.
    assert record["stale"] is False


def test_refresh_marks_cache_stale_on_410(
    remote: LicenseRemote,
    entitlement_cache: EntitlementCache,
):
    """A 410 (install revoked) must:
      - mark the cache stale (so the gate stops granting pro);
      - raise RefreshRevokedError so the caller can drive a
        re-bootstrap flow.
    """
    # Seed the cache so mark_stale() has something to flip.
    entitlement_cache.store(
        token="will.be.marked.stale",
        envelope={"tier": "pro", "features": ["export_pdf"], "exp": 9999999999},
    )
    # Confirm pre-condition.
    pre_record = entitlement_cache.load()
    assert pre_record is not None and pre_record["stale"] is False

    body = {"ok": False, "error": "install revoked"}
    remote._http_post = AsyncMock(return_value=(410, body))

    with pytest.raises(RefreshRevokedError) as exc_info:
        _run(
            remote.refresh(
                api_key="nk_revoked",
                install_id="11111111-2222-4333-8444-666666666666",
                hardware_key="a" * 64,
            )
        )

    # Status code preserved on the exception for telemetry.
    assert exc_info.value.status == 410
    # Cache is now marked stale.
    post_record = entitlement_cache.load()
    assert post_record is not None and post_record["stale"] is True
    # The tier gate itself doesn't consult the stale flag — that's
    # a caller's responsibility — so we don't assert on it here.


def test_refresh_marks_cache_stale_on_401_with_revoked_marker(
    remote: LicenseRemote,
    entitlement_cache: EntitlementCache,
):
    """A 401 response whose body carries a revoked marker must be
    treated as a revoke, NOT as a transient error. The server's
    actual shape is::

        {"ok": false, "error": "install revoked"}  (status 401)

    (the server can't distinguish "unknown api_key" from
    "api_key for a revoked row" in the lookup, so it returns 401
    either way; the marker is in the body). A plain 401 without
    the marker is a different story — see the next test.
    """
    entitlement_cache.store(
        token="will.be.marked.stale",
        envelope={"tier": "pro", "features": [], "exp": 9999999999},
    )

    body = {"ok": False, "error": "install revoked"}
    remote._http_post = AsyncMock(return_value=(401, body))

    with pytest.raises(RefreshRevokedError):
        _run(
            remote.refresh(
                api_key="nk_stale",
                install_id="11111111-2222-4333-8444-666666666666",
                hardware_key="a" * 64,
            )
        )

    # Cache stale.
    record = entitlement_cache.load()
    assert record is not None and record["stale"] is True


def test_refresh_raises_plain_refresh_error_on_401_without_revoked_marker(
    remote: LicenseRemote,
    entitlement_cache: EntitlementCache,
):
    """A plain 401 (no revoked marker) must raise plain
    RefreshError — NOT RefreshRevokedError. The caller should
    treat it as "license lost, surface a dialog" rather than
    auto-rebootstrapping.
    """
    entitlement_cache.store(
        token="untouched",
        envelope={"tier": "pro", "features": [], "exp": 9999999999},
    )

    body = {"ok": False, "error": "invalid api_key"}
    remote._http_post = AsyncMock(return_value=(401, body))

    with pytest.raises(RefreshError) as exc_info:
        _run(
            remote.refresh(
                api_key="nk_garbage",
                install_id="11111111-2222-4333-8444-666666666666",
                hardware_key="a" * 64,
            )
        )

    # Must NOT be the revoked subclass — caller branches on type.
    assert not isinstance(exc_info.value, RefreshRevokedError)
    assert exc_info.value.status == 401
    # And the cache stale flag is UNCHANGED (we didn't flip it —
    # a plain 401 isn't a revoke).
    record = entitlement_cache.load()
    assert record is not None and record["stale"] is False


# -----------------------------------------------------------------------------
# Sync wrapper tests
# -----------------------------------------------------------------------------


def test_sync_bootstrap_wrapper_returns_dict(
    remote: LicenseRemote,
    install_store: InstallStore,
):
    """sync_bootstrap is an asyncio.run wrapper around the async
    bootstrap(). It must return the 201 dict when called from a
    sync context with no existing event loop.
    """
    body = _bootstrap_201_body()
    remote._http_post = AsyncMock(return_value=(201, body))

    result = remote.sync_bootstrap(
        install_id="11111111-2222-4333-8444-666666666666",
        hardware_key="a" * 64,
        public_key="fake-pem",
        os="linux",
        app_version="1.2.3",
    )

    # Returned value matches the 201 body.
    assert result == body
    # And the side-effects actually happened.
    record = install_store.get_or_create()
    assert record["api_key"] == body["api_key"]


def test_sync_refresh_wrapper_returns_dict(
    remote: LicenseRemote,
    entitlement_cache: EntitlementCache,
):
    """sync_refresh is an asyncio.run wrapper around the async
    refresh(). It must return the 200 dict when called from a
    sync context with no existing event loop.
    """
    body = _refresh_200_body()
    remote._http_post = AsyncMock(return_value=(200, body))

    result = remote.sync_refresh(
        api_key="nk_test_" + "z" * 32,
        install_id="11111111-2222-4333-8444-666666666666",
        hardware_key="a" * 64,
    )

    # Returned value matches the 200 body.
    assert result["tier"] == body["tier"]
    # And the cache was updated.
    record = entitlement_cache.load()
    assert record is not None
    assert record["envelope"]["tier"] == body["entitlements"]["tier"]