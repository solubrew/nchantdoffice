"""Tests for nchantdoffice.license.startup_refresh.refresh_if_needed.

DESK T-NEW-050: this orchestrator decides, on every app start,
whether the desktop needs to (a) bootstrap with the server for
the first time, (b) refresh an existing entitlement, or (c) skip
because the cache is fresh.

The orchestrator wires three existing pieces together
(:class:`InstallStore`, :class:`EntitlementCache`,
:class:`LicenseRemote`) plus a tiny "preferences" shim that
holds the persistent ``entitlement_stale`` flag. The tests here
use:

  - a real ``InstallStore`` + ``EntitlementCache`` backed by a
    tmp dir so the disk-write code paths exercise for real;
  - a ``MockLicenseRemote`` whose ``sync_bootstrap`` and
    ``sync_refresh`` methods are plain callables the tests
    patch in place — no aiohttp, no asyncio, no real network;
  - a tiny ``MockPreferencesDB`` dict-shim for the
    ``entitlement_stale`` flag persistence.

Why the in-memory preferences shim, not a real ``PreferencesDB``?
================================================================

The desktop's "preferences" storage is a yaml config dict
(``self.config.dikt["preferences"]``) — there's no PreferencesDB
class yet. The orchestrator must therefore accept ANY object
exposing ``get(key, default=None)`` and ``set(key, value)``. The
tests inject a tiny in-memory implementation so the orchestrator
contract is locked in: it does NOT call into a specific
``PreferencesDB`` class — it consumes a duck-typed mapping.

Spec
====

Decision tree for :func:`refresh_if_needed`:

  1. No ``api_key`` in InstallStore       -> ``sync_bootstrap``.
  2. Has ``api_key`` but cache is empty  -> ``sync_refresh``.
  3. Cache exists and
     ``is_expired_or_close(threshold)``   -> ``sync_refresh``.
  4. Cache exists and stale flag is True -> ``sync_refresh``.
  5. Otherwise                            -> skip.

If ``sync_refresh`` raises :class:`RefreshRevokedError`, fall
back to ``sync_bootstrap`` (same ``install_id`` + ``hardware_key``
re-register). If ``sync_refresh`` raises any other transient
error (network, plain RefreshError, asyncio.TimeoutError, etc.),
swallow it and return ``{action: "skipped", reason: "offline"}``
so the desktop still boots.

On success: persist ``entitlement_stale=False``. On any failure:
persist ``entitlement_stale=True`` so the next launch retries.
"""
from __future__ import annotations

import datetime as dt
import os
import platform
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

from nchantdoffice.license import startup_refresh
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
# Test doubles
# -----------------------------------------------------------------------------


class MockPreferencesDB:
    """Tiny in-memory ``PreferencesDB`` shim.

    The real ``PreferencesDB`` (when it exists) will load + persist
    the ``entitlement_stale`` flag in the desktop's YAML config.
    The orchestrator consumes a duck-typed mapping so the tests
    can inject this mock without booting the full config stack.
    """

    def __init__(self) -> None:
        self.values: Dict[str, Any] = {}

    def get(self, key: str, default: Any = None) -> Any:
        return self.values.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.values[key] = value


class MockLicenseRemote:
    """Fake :class:`LicenseRemote` whose ``sync_bootstrap`` and
    ``sync_refresh`` are plain callables the tests patch in place.

    Mirrors the public sync surface of :class:`LicenseRemote`
    without aiohttp / asyncio. The orchestrator must never
    instantiate a real :class:`LicenseRemote`; these tests verify
    the orchestrator only calls the two sync methods.
    """

    def __init__(
        self,
        bootstrap_return: Optional[Dict[str, Any]] = None,
        refresh_return: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.bootstrap_calls: List[Dict[str, Any]] = []
        self.refresh_calls: List[Dict[str, Any]] = []
        # _bootstrap is the test's patchable callable. The default
        # returns the canned 201 body; tests can override.
        self._bootstrap_return = bootstrap_return or self._default_bootstrap_body()
        self._refresh_return = refresh_return or self._default_refresh_body()

    # ---- patchable callables ----------------------------------------------

    def sync_bootstrap(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        self.bootstrap_calls.append({"args": args, "kwargs": kwargs})
        return self._bootstrap_return

    def sync_refresh(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        self.refresh_calls.append({"args": args, "kwargs": kwargs})
        return self._refresh_return

    # ---- test-side hooks --------------------------------------------------

    def make_refresh_raise(self, exc: BaseException) -> None:
        """Make :meth:`sync_refresh` raise ``exc`` while STILL
        appending to :attr:`refresh_calls`.

        A naive ``remote.sync_refresh = lambda: raise ...`` would
        bypass the call counter; this helper monkey-patches the
        method via the class so the existing bound method is
        augmented instead of replaced.
        """
        original = self.sync_refresh

        def _patched(*args: Any, **kwargs: Any) -> Dict[str, Any]:
            self.refresh_calls.append({"args": args, "kwargs": kwargs})
            raise exc

        # Bind to the instance so ``self.refresh_calls`` resolves
        # to the same list as the rest of the mock.
        self.sync_refresh = _patched  # type: ignore[assignment]

    # ---- canned response bodies -------------------------------------------

    @staticmethod
    def _default_bootstrap_body() -> Dict[str, Any]:
        return {
            "desktop_uuid": "11111111-2222-4333-8444-555555555555",
            "api_key": "nk_test_" + "a" * 32,
            "install_id": "11111111-2222-4333-8444-666666666666",
            "user_fk": 42,
            "entitlements": {
                "tier": "pro",
                "feat": ["export_pdf"],
                "exp": (dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=30)).timestamp(),
            },
            "entitlement_token": "fernet-test-token",
        }

    @staticmethod
    def _default_refresh_body() -> Dict[str, Any]:
        return {
            "tier": "pro",
            "features": ["export_pdf"],
            "expires_at": (dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=30)).timestamp(),
            "entitlements": {
                "tier": "pro",
                "feat": ["export_pdf"],
                "exp": (dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=30)).timestamp(),
            },
            "entitlement_token": "fernet-test-token-2",
        }


# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------


@pytest.fixture
def tmp_data_dir(tmp_path: Path) -> Path:
    """Per-test data dir for InstallStore + EntitlementCache."""
    d = tmp_path / "license_data"
    d.mkdir(parents=True, exist_ok=True)
    return d


@pytest.fixture
def fixed_machine_id(monkeypatch: pytest.MonkeyPatch) -> None:
    """Pin the InstallStore's machine-id so PBKDF2 is deterministic."""
    monkeypatch.setattr(
        InstallStore,
        "_read_os_machine_id",
        lambda self: b"test-machine-id",
    )


@pytest.fixture
def install_store(tmp_data_dir: Path, fixed_machine_id: None) -> InstallStore:
    return InstallStore(data_dir=tmp_data_dir)


@pytest.fixture
def entitlement_cache(tmp_data_dir: Path) -> EntitlementCache:
    return EntitlementCache(data_dir=tmp_data_dir)


@pytest.fixture
def remote() -> MockLicenseRemote:
    return MockLicenseRemote()


@pytest.fixture
def prefs() -> MockPreferencesDB:
    return MockPreferencesDB()


# -----------------------------------------------------------------------------
# Spec tests
# -----------------------------------------------------------------------------


def test_first_launch_triggers_bootstrap(
    install_store: InstallStore,
    entitlement_cache: EntitlementCache,
    remote: MockLicenseRemote,
    prefs: MockPreferencesDB,
) -> None:
    """No api_key in InstallStore on first launch -> sync_bootstrap.

    Verifies the bootstrap path is taken and that the orchestrator
    hands the install's install_id + hardware_key to the remote.
    The bootstrap itself persists credentials into the install
    store; that's tested in test_remote — here we only verify the
    orchestrator made the call.
    """
    record = install_store.get_or_create()
    assert record["api_key"] is None  # first-launch sanity

    result = startup_refresh.refresh_if_needed(
        install_store=install_store,
        entitlement_cache=entitlement_cache,
        license_remote=remote,
        preferences_db=prefs,
    )

    assert remote.bootstrap_calls, "sync_bootstrap should have been called"
    assert len(remote.bootstrap_calls) == 1
    assert len(remote.refresh_calls) == 0, "sync_refresh must not be called on first launch"
    # The kwargs MUST carry install_id + hardware_key from the
    # InstallStore — that's how the server correlates the install.
    kwargs = remote.bootstrap_calls[0]["kwargs"]
    assert kwargs.get("install_id") == record["install_id"]
    assert kwargs.get("hardware_key") == record["hardware_key"]
    # Result contract: action="bootstrap", tier after action.
    assert result["action"] == "bootstrap"
    assert result["reason"] == "first_launch"


def test_fresh_cache_within_threshold_skips_refresh(
    install_store: InstallStore,
    entitlement_cache: EntitlementCache,
    remote: MockLicenseRemote,
    prefs: MockPreferencesDB,
) -> None:
    """Cache exists, envelope expires in 24h, no stale flag -> skip.

    Verifies the orchestrator does NOT call sync_refresh when the
    cached envelope is well within the 12h refresh threshold.
    """
    record = install_store.get_or_create()
    install_store.save_api_credentials(api_key="nk_test_x", desktop_uuid="d-uuid-1")

    # Store an envelope that expires in 24h — well outside the 12h threshold.
    future_exp = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=24)
    entitlement_cache.store(
        token="fernet-1",
        envelope={"tier": "pro", "feat": ["export_pdf"], "exp": future_exp.timestamp()},
    )
    assert prefs.get("entitlement_stale") is None  # nothing pre-set

    result = startup_refresh.refresh_if_needed(
        install_store=install_store,
        entitlement_cache=entitlement_cache,
        license_remote=remote,
        preferences_db=prefs,
    )

    assert remote.bootstrap_calls == [], "must not bootstrap on existing install"
    assert remote.refresh_calls == [], "must not refresh — cache is fresh"
    assert result["action"] == "skipped"
    assert result["reason"] == "fresh"
    # Stale flag must be cleared (False) on a healthy skip.
    assert prefs.get("entitlement_stale") is False


def test_expired_cache_triggers_refresh(
    install_store: InstallStore,
    entitlement_cache: EntitlementCache,
    remote: MockLicenseRemote,
    prefs: MockPreferencesDB,
) -> None:
    """Cache exists but envelope is already expired -> sync_refresh."""
    install_store.get_or_create()
    install_store.save_api_credentials(api_key="nk_test_x", desktop_uuid="d-uuid-1")

    # Envelope expired 1 hour ago.
    past_exp = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=1)
    entitlement_cache.store(
        token="fernet-1",
        envelope={"tier": "pro", "feat": ["export_pdf"], "exp": past_exp.timestamp()},
    )

    result = startup_refresh.refresh_if_needed(
        install_store=install_store,
        entitlement_cache=entitlement_cache,
        license_remote=remote,
        preferences_db=prefs,
    )

    assert remote.refresh_calls, "sync_refresh must be called for expired cache"
    assert remote.bootstrap_calls == [], "must not bootstrap on existing install"
    assert result["action"] == "refresh"
    assert result["reason"] == "expired_or_close"


def test_within_threshold_but_stale_flag_triggers_refresh(
    install_store: InstallStore,
    entitlement_cache: EntitlementCache,
    remote: MockLicenseRemote,
    prefs: MockPreferencesDB,
) -> None:
    """Cache is fresh (24h) BUT stale flag is True -> sync_refresh.

    The persistent-stale flag is the "last refresh raised, retry
    on next launch" signal — it must override the "cache is
    fresh" optimisation.
    """
    install_store.get_or_create()
    install_store.save_api_credentials(api_key="nk_test_x", desktop_uuid="d-uuid-1")

    future_exp = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=24)
    entitlement_cache.store(
        token="fernet-1",
        envelope={"tier": "pro", "feat": ["export_pdf"], "exp": future_exp.timestamp()},
    )
    prefs.set("entitlement_stale", True)

    result = startup_refresh.refresh_if_needed(
        install_store=install_store,
        entitlement_cache=entitlement_cache,
        license_remote=remote,
        preferences_db=prefs,
    )

    assert remote.refresh_calls, "sync_refresh must be called when stale flag is set"
    assert remote.bootstrap_calls == [], "must not bootstrap on existing install"
    assert result["action"] == "refresh"
    assert result["reason"] == "stale_flag"


def test_refresh_revoked_falls_back_to_bootstrap(
    install_store: InstallStore,
    entitlement_cache: EntitlementCache,
    remote: MockLicenseRemote,
    prefs: MockPreferencesDB,
) -> None:
    """sync_refresh raises RefreshRevokedError -> fall back to bootstrap.

    The server-side install row may have been revoked-and-rebound,
    in which case the api_key in our InstallStore no longer maps
    to anything. The orchestrator must re-bootstrap with the
    SAME install_id + hardware_key so the server can re-issue.
    """
    record = install_store.get_or_create()
    install_store.save_api_credentials(api_key="nk_test_x", desktop_uuid="d-uuid-1")

    # Empty cache forces the refresh path.
    remote.make_refresh_raise(
        RefreshRevokedError(status=410, body={"error": "install revoked"})
    )

    result = startup_refresh.refresh_if_needed(
        install_store=install_store,
        entitlement_cache=entitlement_cache,
        license_remote=remote,
        preferences_db=prefs,
    )

    assert remote.refresh_calls, "refresh was attempted first"
    assert remote.bootstrap_calls, "bootstrap was the fallback after revoke"
    bootstrap_kwargs = remote.bootstrap_calls[0]["kwargs"]
    assert bootstrap_kwargs.get("install_id") == record["install_id"]
    assert bootstrap_kwargs.get("hardware_key") == record["hardware_key"]
    assert result["action"] == "bootstrap"
    assert result["reason"] == "refresh_revoked_fallback"


def test_offline_skips_refresh_gracefully(
    install_store: InstallStore,
    entitlement_cache: EntitlementCache,
    remote: MockLicenseRemote,
    prefs: MockPreferencesDB,
) -> None:
    """Transient network error on refresh -> orchestrator returns skipped.

    The desktop MUST boot even when the user is offline. A plain
    RefreshError (network errors, 5xx, plain 401) must be
    swallowed and surfaced as ``{action: 'skipped', reason:
    'offline'}`` so the widget layer proceeds with the cached
    envelope / fails closed to free.
    """
    install_store.get_or_create()
    install_store.save_api_credentials(api_key="nk_test_x", desktop_uuid="d-uuid-1")

    remote.make_refresh_raise(
        RefreshError(
            status=0,
            body=None,
            message="simulated network failure",
        )
    )

    result = startup_refresh.refresh_if_needed(
        install_store=install_store,
        entitlement_cache=entitlement_cache,
        license_remote=remote,
        preferences_db=prefs,
    )

    assert remote.refresh_calls, "refresh was attempted"
    assert remote.bootstrap_calls == [], "must NOT bootstrap on transient failure"
    assert result["action"] == "skipped"
    assert result["reason"] == "offline"
    # Stale flag must be set so the next launch retries.
    assert prefs.get("entitlement_stale") is True


def test_successful_refresh_clears_stale_flag(
    install_store: InstallStore,
    entitlement_cache: EntitlementCache,
    remote: MockLicenseRemote,
    prefs: MockPreferencesDB,
) -> None:
    """A successful refresh writes entitlement_stale=False.

    A refresh that completes cleanly is the recovery signal: the
    cache is fresh again, no retry is needed on next launch.
    """
    install_store.get_or_create()
    install_store.save_api_credentials(api_key="nk_test_x", desktop_uuid="d-uuid-1")
    prefs.set("entitlement_stale", True)  # came in stale

    # Empty cache -> the refresh-decision branch.
    result = startup_refresh.refresh_if_needed(
        install_store=install_store,
        entitlement_cache=entitlement_cache,
        license_remote=remote,
        preferences_db=prefs,
    )

    assert remote.refresh_calls, "refresh must be called"
    assert result["action"] == "refresh"
    # The orchestrator clears the stale flag on success.
    assert prefs.get("entitlement_stale") is False


def test_failed_refresh_sets_stale_flag(
    install_store: InstallStore,
    entitlement_cache: EntitlementCache,
    remote: MockLicenseRemote,
    prefs: MockPreferencesDB,
) -> None:
    """A refresh that fails (transient error) writes stale=True.

    Symmetric with test_successful_refresh_clears_stale_flag:
    any failure path must persist the stale flag so the next
    launch retries. This is the whole point of the persistent
    flag — without it, an offline user who finally connects
    wouldn't refresh on their next launch.
    """
    install_store.get_or_create()
    install_store.save_api_credentials(api_key="nk_test_x", desktop_uuid="d-uuid-1")
    assert prefs.get("entitlement_stale") is None  # starts unset

    remote.make_refresh_raise(
        RefreshError(status=0, body=None, message="offline")
    )

    startup_refresh.refresh_if_needed(
        install_store=install_store,
        entitlement_cache=entitlement_cache,
        license_remote=remote,
        preferences_db=prefs,
    )

    # Stale flag must be set so the next launch retries.
    assert prefs.get("entitlement_stale") is True