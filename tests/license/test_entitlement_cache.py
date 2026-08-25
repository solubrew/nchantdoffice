"""Tests for nchantdoffice.license.entitlement_cache.EntitlementCache.

DESK T-NEW-047: EntitlementCache persists the server-issued
``entitlement_token`` + ``envelope`` so the desktop can gate
features WITHOUT a network round-trip on every widget render.

These tests cover:

  - the first-run path (``load()`` returns None when no file yet);
  - round-trip semantics (``store`` then ``load`` returns the same
    dict the caller stored);
  - corruption recovery (garbage bytes in ``entitlement.bin``
    must produce ``None``, not an exception);
  - the ``mark_stale()`` flag flip (last-known tier survives so
    the gate doesn't downgrade a revoked user silently);
  - the ``clear()`` wipe path (logout / fresh-install);
  - ``is_expired_or_close()`` for the startup-refresh decision
    (old envelope -> True, fresh -> False, near-threshold -> True).

Fernet key derivation mirrors ``InstallStore``: the key is cached
in ``.fernet_key`` next to ``entitlement.bin`` and is derived from
the data_dir's filesystem path alone (no salt) — that's the same
"portable to backups of the same machine only" trade-off documented
in install_store.
"""
from __future__ import annotations

import time
from pathlib import Path

import pytest

from nchantdoffice.license.entitlement_cache import EntitlementCache


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------


def _make_cache(tmp_path: Path) -> EntitlementCache:
    """Build an EntitlementCache bound to a fresh tmp_path subdir.

    Each call gets its own dir so tests that want to inspect
    "no file yet" don't have to share state.
    """
    data_dir = tmp_path / "entitlement"
    data_dir.mkdir(parents=True, exist_ok=True)
    return EntitlementCache(data_dir=data_dir)


def _sample_envelope(
    *,
    tier: str = "pro",
    feat: list[str] | None = None,
    exp: int | None = None,
) -> dict:
    """Build a representative server envelope for tests.

    The shape mirrors ``EntitlementService.mint`` on the server:
        {iid, duid, uid, tier, feat, iat, exp}
    """
    return {
        "iid": "11111111-1111-4111-8111-111111111111",
        "duid": "22222222-2222-4222-8222-222222222222",
        "uid": 42,
        "tier": tier,
        "feat": list(feat) if feat is not None else ["csv_export", "pdf_export"],
        "iat": int(time.time()) - 60,
        "exp": exp if exp is not None else int(time.time()) + 3600,
    }


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


def test_load_returns_none_on_first_run(tmp_path):
    """Brand-new data_dir → load() returns None. The caller
    treats None as "go bootstrap or refresh via the network".
    """
    cache = _make_cache(tmp_path)

    assert cache.load() is None


def test_store_then_load_round_trip(tmp_path):
    """store(token, envelope) then load() must return a dict with
    the SAME token + envelope, plus the wrapper fields
    ``stored_at`` (ISO8601) and ``stale`` (False on initial store).
    """
    cache = _make_cache(tmp_path)
    token = "gAAAAA-this-is-a-fernet-token-string.example"
    envelope = _sample_envelope(tier="pro", feat=["csv_export"])

    cache.store(token, envelope)
    loaded = cache.load()

    assert loaded is not None, "load() returned None after store()"
    assert loaded["token"] == token
    assert loaded["envelope"] == envelope
    assert loaded["stale"] is False
    # stored_at is ISO8601 (parseable by datetime.fromisoformat).
    assert isinstance(loaded["stored_at"], str)
    from datetime import datetime
    parsed = datetime.fromisoformat(loaded["stored_at"])
    # And the timestamp is recent (within the last 5 minutes —
    # generous to avoid CI flakes).
    age = (datetime.now(parsed.tzinfo) - parsed).total_seconds()
    assert -60 <= age <= 300, f"stored_at not recent: {loaded['stored_at']}"


def test_load_returns_none_on_corrupt_file(tmp_path):
    """Writing garbage to ``entitlement.bin`` must NOT crash
    ``load()``; it must return None so the caller falls back to
    the network bootstrap path. (Same tolerance as InstallStore.)
    """
    cache = _make_cache(tmp_path)
    bin_path = cache.data_dir / "entitlement.bin"
    bin_path.write_bytes(b"this-is-not-fernet-token-garbage")

    # The cache must swallow the Fernet failure and return None,
    # not raise InvalidToken / ValueError.
    assert cache.load() is None


def test_mark_stale_flips_flag(tmp_path):
    """After ``mark_stale()``, load() returns ``stale=True`` —
    and the cached token + envelope remain readable so the gate
    keeps gating based on the LAST KNOWN tier.
    """
    cache = _make_cache(tmp_path)
    token = "gAAAAA-stale-test-token"
    envelope = _sample_envelope(tier="pro")
    cache.store(token, envelope)

    pre = cache.load()
    assert pre is not None
    assert pre["stale"] is False

    cache.mark_stale()

    post = cache.load()
    assert post is not None
    assert post["stale"] is True
    # Token + envelope unchanged.
    assert post["token"] == token
    assert post["envelope"] == envelope


def test_clear_removes_file(tmp_path):
    """``clear()`` removes the on-disk cache so the next load()
    returns None. Used by logout / fresh-install paths.
    """
    cache = _make_cache(tmp_path)
    cache.store("gAAAAA-clear-test-token", _sample_envelope())
    assert cache.load() is not None

    cache.clear()

    assert cache.load() is None
    # And the on-disk file is actually gone (not just un-decryptable).
    bin_path = cache.data_dir / "entitlement.bin"
    assert not bin_path.exists()


def test_is_expired_or_close_returns_true_for_old_envelope(tmp_path):
    """An envelope whose ``exp`` is one hour in the past must be
    considered expired-or-close (the startup flow will call
    ``/refresh``).
    """
    cache = _make_cache(tmp_path)
    one_hour_ago = int(time.time()) - 3600
    envelope = _sample_envelope(exp=one_hour_ago)
    cache.store("gAAAAA-old-token", envelope)

    assert cache.is_expired_or_close() is True


def test_is_expired_or_close_returns_false_for_fresh_envelope(tmp_path):
    """An envelope expiring 24 hours from now is comfortably
    outside the default 12-hour threshold, so the startup flow
    will NOT call ``/refresh``.
    """
    cache = _make_cache(tmp_path)
    one_day_from_now = int(time.time()) + 24 * 3600
    envelope = _sample_envelope(exp=one_day_from_now)
    cache.store("gAAAAA-fresh-token", envelope)

    assert cache.is_expired_or_close() is False


def test_is_expired_or_close_respects_threshold(tmp_path):
    """The default 12-hour threshold catches envelopes expiring
    within that window. An envelope expiring 11 hours from now
    (i.e., within the 12-hour window) must be flagged True.
    """
    cache = _make_cache(tmp_path)
    eleven_hours_from_now = int(time.time()) + 11 * 3600
    envelope = _sample_envelope(exp=eleven_hours_from_now)
    cache.store("gAAAAA-near-expiry-token", envelope)

    # Default threshold is 12 hours, so 11h is inside the window.
    assert cache.is_expired_or_close() is True


def test_is_expired_or_close_returns_true_when_no_cache(tmp_path):
    """No cached envelope → is_expired_or_close() returns True so
    the startup flow falls back to /refresh (the safer default).
    """
    cache = _make_cache(tmp_path)
    assert cache.is_expired_or_close() is True
