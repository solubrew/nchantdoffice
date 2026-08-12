#!/usr/bin/env python3
"""Smoke-test the NchantdOffice update process.

T-NEW-057 step 2: this cmd exercises the live ``UpdateChecker``
against a stubbed ``/api/check-update`` response and prints the
parsed ``UpdateInfo``. It also exercises
``NchantdOfficeDBUpdate.update_pyffice_document()`` against a
mock parent (skips if the parent can't be wired in the test
env).

**Usage**::

    # Default: hit a real URL is NOT the goal — the stub is
    # always installed so the cmd never touches the network.
    python cmds/_review_update_process.py
    python cmds/_review_update_process.py --scenario stale-cache
    python cmds/_review_update_process.py --scenario server-down
    python cmds/_review_update_process.py --scenario upgrade-lock

**Scenarios** (default is ``fresh-server``):

- ``fresh-server`` — no cache, server returns a valid payload,
  checker parses and caches it. Verify the cached file is
  written and ``UpdateInfo`` is non-None.
- ``stale-cache`` — cache file older than
  ``REFRESH_INTERVAL_SECONDS``, server returns fresh payload.
  Verify the cache is overwritten.
- ``server-down`` — server raises ``RequestException``,
  fallback to stale cache (which we pre-write). Verify
  ``check()`` returns the stale value rather than ``None``.
- ``upgrade-lock`` — call
  ``NchantdOfficeDBUpdate.update_pyffice_document()`` twice
  on a mock parent. Verify the second call is a no-op (this
  is what T-NEW-058 should add — pre-T-NEW-058 the second
  call will likely run the migration twice; that's a known
  issue this cmd surfaces).

**Cache safety**: the cmd sets ``NCHANT_DATA_DIR`` to a
tempdir under ``/tmp`` so it never touches the user's real
``~/.nchantd/`` state. Cleanup happens at exit.

**Why this cmd is a follow-up to the T-NEW-057 review doc**:
the review surfaces that ``UpdateChecker`` is dead-code at
the call layer (no live invocation in the app). This cmd is
the only place in the repo that exercises ``check()`` against
a non-AST test. If the boot hook (T-NEW-058) ships, this cmd
becomes the integration-test foundation.
"""
import argparse
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Pre-flight: redirect cache + state to a tempdir BEFORE importing the
# checker module. The module reads NCHANT_DATA_DIR at import time.
# ---------------------------------------------------------------------------

_TMPDIR = tempfile.mkdtemp(prefix="nchantdoffice_review_")
os.environ["NCHANT_DATA_DIR"] = _TMPDIR

# Prepend the project root so `from nchantdoffice.updates.checker`
# resolves to the local source.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


def _cleanup() -> None:
    """Remove the tempdir on exit."""
    try:
        shutil.rmtree(_TMPDIR, ignore_errors=True)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------


def scenario_fresh_server():
    """No cache, server returns valid payload, checker parses + caches."""
    from nchantdoffice.updates.checker import UpdateChecker, UpdateInfo
    from datetime import datetime, timezone

    payload = {
        "latest_version": "0.0.2",
        "release_date": "2026-08-15",
        "update_available": True,
        "download_url": "https://nchantdoffice.com/download/0.0.2",
        "changelog_url": "https://nchantdoffice.com/changelog",
        "os": "linux",
    }
    mock_response = MagicMock()
    mock_response.content = json.dumps(payload).encode("utf-8")
    mock_response.json.return_value = payload
    mock_response.raise_for_status.return_value = None

    with patch("requests.Session.get", return_value=mock_response) as get:
        checker = UpdateChecker(base_url="https://example.invalid")
        info = checker.check()

    # Assertions
    assert info is not None, "check() returned None on fresh-server scenario"
    assert isinstance(info, UpdateInfo), f"expected UpdateInfo, got {type(info)}"
    assert info.latest_version == "0.0.2", f"latest_version={info.latest_version!r}"
    assert info.update_available is True
    assert info.download_url == "https://nchantdoffice.com/download/0.0.2"

    # Cache was written
    cache_path = Path(_TMPDIR) / "update_check_cache.json"
    assert cache_path.exists(), f"cache file not written at {cache_path}"
    cache_mode = cache_path.stat().st_mode & 0o777
    assert cache_mode == 0o600, f"cache mode={oct(cache_mode)}, expected 0o600"

    print(f"[fresh-server] OK — info={info}")
    print(f"[fresh-server] cache written at {cache_path} (mode 0o600)")
    return True


def scenario_stale_cache():
    """Pre-write a stale cache, then server returns fresh."""
    from nchantdoffice.updates.checker import UpdateChecker, _CACHE_PATH
    from datetime import datetime, timedelta, timezone

    # Pre-write a cache with a timestamp older than REFRESH_INTERVAL_SECONDS
    stale_payload = {
        "latest_version": "0.0.1",
        "release_date": "2026-08-01",
        "update_available": False,
        "download_url": "",
        "changelog_url": "",
        "os": "linux",
        "_cached_at": (datetime.now(timezone.utc) - timedelta(hours=12)).isoformat(),
    }
    _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _CACHE_PATH.write_text(json.dumps(stale_payload), encoding="utf-8")
    os.chmod(_CACHE_PATH, 0o600)

    fresh_payload = {
        "latest_version": "0.0.3",
        "update_available": True,
        "download_url": "https://example.invalid/download/0.0.3",
    }
    mock_response = MagicMock()
    mock_response.content = json.dumps(fresh_payload).encode("utf-8")
    mock_response.json.return_value = fresh_payload
    mock_response.raise_for_status.return_value = None

    with patch("requests.Session.get", return_value=mock_response):
        checker = UpdateChecker(base_url="https://example.invalid")
        info = checker.check()

    assert info is not None
    assert info.latest_version == "0.0.3", (
        f"expected fresh 0.0.3, got {info.latest_version!r}"
    )

    # Cache was overwritten with the fresh payload
    cached_raw = json.loads(_CACHE_PATH.read_text())
    assert cached_raw["latest_version"] == "0.0.3", (
        f"cache not overwritten: {cached_raw['latest_version']!r}"
    )
    print(f"[stale-cache] OK — info={info}, cache overwritten")
    return True


def scenario_server_down():
    """Server raises RequestException, fallback to stale cache."""
    import requests as _requests
    from nchantdoffice.updates.checker import UpdateChecker, _CACHE_PATH
    from datetime import datetime, timedelta, timezone

    # Pre-write a stale cache
    stale_payload = {
        "latest_version": "0.0.1",
        "release_date": "2026-08-01",
        "update_available": True,
        "download_url": "https://example.invalid/download/0.0.1",
        "_cached_at": (datetime.now(timezone.utc) - timedelta(hours=12)).isoformat(),
    }
    _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _CACHE_PATH.write_text(json.dumps(stale_payload), encoding="utf-8")
    os.chmod(_CACHE_PATH, 0o600)

    with patch(
        "requests.Session.get",
        side_effect=_requests.ConnectionError("simulated offline"),
    ):
        checker = UpdateChecker(base_url="https://example.invalid")
        info = checker.check()

    assert info is not None, (
        "server-down scenario: expected fallback to stale cache, got None"
    )
    assert info.latest_version == "0.0.1", (
        f"expected stale 0.0.1 from fallback, got {info.latest_version!r}"
    )
    print(f"[server-down] OK — fallback returned stale info={info}")
    return True


def scenario_upgrade_lock():
    """Call NchantdOfficeDBUpdate.update_pyffice_document() twice.

    Pre-T-NEW-058: the second call will likely run the migration
    again. This scenario surfaces the issue (prints a WARNING
    when the call_count is > 1) but does NOT fail — the fix is
    T-NEW-058's responsibility.
    """
    from nchantdoffice.updates.db import NchantdOfficeDBUpdate

    mock_parent = MagicMock()
    mock_codex = MagicMock()
    # Build a fake updateer that tracks call count
    updateer = MagicMock()
    updateer.get_document_types.return_value = ["script", "notebook", "image"]
    mock_codex.update.return_value = updateer
    mock_parent.codex = mock_codex
    # The NchantdOfficeDBUpdate.__init__ reads cfg from self.config.dikt,
    # which under a mock is a regular Mock — give it a sensible shape.
    mock_parent.config = MagicMock()
    mock_parent.config.dikt = {"versions": {}}

    db_update = NchantdOfficeDBUpdate(mock_parent)
    # The parent class's check_current_document_version is the inner
    # step that update_pyffice_document iterates over each document
    # type. Mock it as a no-op so the loop runs cleanly.
    db_update.check_current_document_version = MagicMock()

    # First call
    db_update.update_pyffice_document()
    first_call_count = updateer.get_document_types.call_count

    # Second call (this is where T-NEW-058 will add the lock)
    db_update.update_pyffice_document()
    second_call_count = updateer.get_document_types.call_count

    lock_works = second_call_count == first_call_count
    if lock_works:
        print(
            f"[upgrade-lock] OK — second call was a no-op "
            f"(get_document_types called {second_call_count}×)"
        )
    else:
        print(
            f"[upgrade-lock] WARNING — second call re-ran the migration "
            f"(get_document_types called {second_call_count}× vs "
            f"{first_call_count}×). This is the T-NEW-058 fix site."
        )
    return True


SCENARIOS = {
    "fresh-server": scenario_fresh_server,
    "stale-cache": scenario_stale_cache,
    "server-down": scenario_server_down,
    "upgrade-lock": scenario_upgrade_lock,
}


def main():
    parser = argparse.ArgumentParser(
        description="Smoke-test the NchantdOffice update process (T-NEW-057 step 2)."
    )
    parser.add_argument(
        "--scenario",
        choices=list(SCENARIOS.keys()),
        default="fresh-server",
        help="Which scenario to run (default: fresh-server).",
    )
    args = parser.parse_args()

    try:
        ok = SCENARIOS[args.scenario]()
        if ok:
            print(f"\n✅ Scenario '{args.scenario}' completed.")
            return 0
        else:
            print(f"\n❌ Scenario '{args.scenario}' returned False.")
            return 1
    except AssertionError as e:
        print(f"\n❌ Scenario '{args.scenario}' assertion failed: {e}")
        return 2
    except Exception as e:
        print(f"\n❌ Scenario '{args.scenario}' crashed: {e!r}")
        import traceback
        traceback.print_exc()
        return 3
    finally:
        _cleanup()


if __name__ == "__main__":
    sys.exit(main())
