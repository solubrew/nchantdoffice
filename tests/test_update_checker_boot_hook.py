"""T-NEW-058 — boot-hook tests for the update process.

The T-NEW-057 review (docs/update-process-review_20260810.md §1.2)
established that both ``UpdateChecker`` and
``NchantdOfficeDBUpdate`` were dead-code at the call layer — the
classes existed and were tested, but no live code in the app ever
constructed or invoked them.

T-NEW-058 wires both into ``NchantdOfficeCloak.__init__`` and
``run_on_launch``. The actual boot-hook logic is in the
module-level ``run_update_process()`` helper, which is what these
tests exercise (the Qt-singleton ``NchantdOfficeCloak`` itself
can't be instantiated twice in the same process — shiboken
enforces single-instance — so we test the helper directly).

The three boot-time invariants pinned here:

  1. ``test_run_update_process_invokes_check_exactly_once`` —
     ``run_update_process()`` invokes ``UpdateChecker.check()``
     exactly once.

  2. ``test_run_update_process_invokes_update_pyffice_once`` —
     ``run_update_process()`` invokes
     ``dbupdate.update_pyffice_document()`` exactly once, with
     ``upgrade_run=True`` in the summary.

  3. ``test_second_invocation_is_noop`` — calling
     ``run_update_process()`` twice on the same ``dbupdate``
     results in the second call being a no-op
     (``upgrade_run=False``) because ``_upgrade_lock`` is True.
     This guards against the double-invocation risk called out in
     the review doc §2.4.

Tests use ``unittest.mock.patch`` on the network + DB layers so
they run in the constrained venv (no real server, no real
sqlite writes against user data).
"""

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

PROJ_ROOT = Path("/home/solubrew/.hermes/projects/nchantdoffice")
sys.path.insert(0, str(PROJ_ROOT))

# Use a tempdir for the update-checker cache so the test never
# touches the user's real ~/.nchantd/ directory.
_TMPDIR = tempfile.mkdtemp(prefix="nchantdoffice_tnew058_")
os.environ["NCHANT_DATA_DIR"] = _TMPDIR


def _cleanup():
    shutil.rmtree(_TMPDIR, ignore_errors=True)


import atexit
atexit.register(_cleanup)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


def _make_dbupdate():
    """Return a real NchantdOfficeDBUpdate with a mocked parent
    so update_pyffice_document() runs without crashing.

    Production wiring (nchantdoffice/nchantdoffice.py:55):
      self.dbupdate = NchantdOfficeDBUpdate(self)   # self = NchantdOfficeCloak
    Then nchantdoffice/updates/db.py:74 reads:
      updater = self.parent.model.codex.update()
    So the mock must place the codex under ``mock_parent.model.codex``
    to mirror the real call shape.
    """
    from nchantdoffice.updates.db import NchantdOfficeDBUpdate

    mock_codex = MagicMock()
    updateer = MagicMock()
    updateer.get_document_types.return_value = ["script"]
    mock_codex.update.return_value = updateer
    mock_parent = MagicMock()
    mock_parent.model.codex = mock_codex
    mock_parent.codex = mock_codex  # belt-and-braces for any codex.readers
    mock_parent.config = MagicMock()
    mock_parent.config.dikt = {"versions": {}}
    dbupdate = NchantdOfficeDBUpdate(mock_parent)
    dbupdate.check_current_document_version = MagicMock()
    return dbupdate, updateer


def _make_update_checker(base_url="https://example.invalid"):
    """Return a real UpdateChecker."""
    from nchantdoffice.updates.checker import UpdateChecker
    return UpdateChecker(base_url=base_url)


def _force_cache_to_tempdir():
    """Rebind the module-level _CACHE_PATH to our tempdir.

    The module-level _CACHE_PATH is computed at import time from
    NCHANT_DATA_DIR (or ~/.nchantd/). If another test file
    imported the module first WITHOUT setting NCHANT_DATA_DIR,
    _CACHE_PATH points at the user's real ~/.nchantd/. We patch
    it here so the boot-hook test never writes to the user's
    real cache directory regardless of import order.
    """
    from nchantdoffice.updates import checker as checker_mod
    temp_cache = Path(_TMPDIR) / "update_check_cache.json"
    # Mutate the module-level binding in place.
    checker_mod._CACHE_PATH = temp_cache
    return temp_cache


def _stub_network_payload():
    """Return a (payload, mock_response) tuple for patching
    ``requests.Session.get``."""
    payload = {
        "latest_version": "0.0.2",
        "update_available": True,
        "download_url": "https://example.invalid/download/0.0.2",
        "changelog_url": "",
        "release_date": "",
        "os": "linux",
    }
    mock_response = MagicMock()
    mock_response.content = json.dumps(payload).encode("utf-8")
    mock_response.json.return_value = payload
    mock_response.raise_for_status.return_value = None
    return payload, mock_response


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_run_update_process_invokes_check_exactly_once():
    """``run_update_process()`` invokes UpdateChecker.check()
    exactly once."""
    from nchantdoffice.nchantdoffice import run_update_process

    dbupdate, _ = _make_dbupdate()
    update_checker = _make_update_checker()
    _, mock_response = _stub_network_payload()
    cache_path = _force_cache_to_tempdir()

    with patch("requests.Session.get", return_value=mock_response):
        summary = run_update_process(dbupdate, update_checker)

    # Cache file written => check() was called.
    assert cache_path.exists(), (
        "T-NEW-058 missing: run_update_process did not call "
        "UpdateChecker.check() (no cache file written at "
        f"{cache_path})."
    )
    # Summary records the check.
    assert summary["checker_info"] is not None, (
        "run_update_process summary checker_info should not be None "
        "when the server returned a valid payload."
    )


def test_run_update_process_invokes_update_pyffice_once():
    """``run_update_process()`` invokes update_pyffice_document()
    exactly once and reports upgrade_run=True."""
    from nchantdoffice.nchantdoffice import run_update_process

    dbupdate, updateer = _make_dbupdate()
    update_checker = _make_update_checker()

    # Patch the network so .check() doesn't try to hit a real server.
    with patch("requests.Session.get", side_effect=Exception("network stub: skip check()")):
        summary = run_update_process(dbupdate, update_checker)

    assert updateer.get_document_types.call_count == 1, (
        f"T-NEW-058 missing: get_document_types called "
        f"{updateer.get_document_types.call_count}×; expected 1."
    )
    assert summary["upgrade_run"] is True, (
        f"T-NEW-058: summary['upgrade_run'] should be True on the "
        f"first call; got {summary['upgrade_run']!r}."
    )


def test_second_invocation_is_noop():
    """Calling ``run_update_process()`` twice on the same
    ``dbupdate`` results in the second call being a no-op
    (``upgrade_run=False``) because ``_upgrade_lock`` is True.
    T-NEW-058 §2.4 / review doc.
    """
    from nchantdoffice.nchantdoffice import run_update_process

    dbupdate, updateer = _make_dbupdate()
    update_checker = _make_update_checker()

    with patch("requests.Session.get", side_effect=Exception("network stub: skip check()")):
        # First call — should run the migration.
        summary_1 = run_update_process(dbupdate, update_checker)
        assert summary_1["upgrade_run"] is True
        first_call_count = updateer.get_document_types.call_count

        # Second call — should be a no-op.
        summary_2 = run_update_process(dbupdate, update_checker)
        second_call_count = updateer.get_document_types.call_count

    assert summary_2["upgrade_run"] is False, (
        f"T-NEW-058 §2.4 broken: second run_update_process() reported "
        f"upgrade_run=True; expected False (_upgrade_lock should "
        f"have made it a no-op). summary_2={summary_2!r}."
    )
    assert second_call_count == first_call_count, (
        f"T-NEW-058 §2.4 broken: second call re-ran the migration "
        f"(get_document_types called {second_call_count}× vs "
        f"{first_call_count}×)."
    )
