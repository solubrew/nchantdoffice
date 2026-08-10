"""T-NEW-060 — Tests for the tray-icon + dismiss-version(days=7) flow.

The T-NEW-057 review (docs/update-process-review_20260810.md §2.3)
decided that the dismissed-versions state should be expanded
from a flat list to a per-version snooze with a default 7-day
duration. T-NEW-060 wires:

  1. ``dismiss_version(version, days=DISMISS_DURATION_DAYS)`` —
     store per-version expiry timestamps in
     ``~/.nchantd/state.yaml``.
  2. ``is_dismissed(version)`` — return True only when the
     snooze has not yet expired.
  3. ``QSystemTrayIcon`` on ``NchantdOfficeMainWindow`` with a
     menu offering "Open download page" + "Dismiss for 7 days".
  4. ``run_update_process()`` wires ``main_window`` so the tray
     is populated when an update-available response comes back.
  5. ``dismiss_version()`` keeps the longer snooze when called
     twice (don't accidentally shorten an existing snooze).

This file pins 5 invariants the T-NEW-060 implementation
promises:

  1. ``test_dismiss_version_default_is_seven_days`` — calling
     ``dismiss_version("0.1.0")`` (no days arg) writes an
     expiry timestamp approximately 7 days from now.

  2. ``test_dismiss_version_custom_days`` — ``dismiss_version("0.1.0", days=30)``
     writes an expiry ~30 days from now.

  3. ``test_is_dismissed_expired_treated_as_false`` — manually
     write a past-expiry entry to state.yaml; ``is_dismissed``
     returns False.

  4. ``test_dismiss_keeps_longer_snooze`` — dismiss for 30
     days, then dismiss again for 1 day; the entry keeps the
     30-day expiry (longer snooze wins).

  5. ``test_dismiss_version_zero_or_negative_rejected`` —
     dismiss_version with days=0 or days=-1 does NOT write
     to state.
"""

import os
import shutil
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJ_ROOT = Path("/home/solubrew/.hermes/projects/nchantdoffice")
sys.path.insert(0, str(PROJ_ROOT))

# Use a tempdir for the update-checker state so the test never
# touches the user's real ~/.nchantd/.
_TMPDIR = tempfile.mkdtemp(prefix="nchantdoffice_tnew060_")
os.environ["NCHANT_DATA_DIR"] = _TMPDIR


def _cleanup():
    shutil.rmtree(_TMPDIR, ignore_errors=True)


import atexit
atexit.register(_cleanup)


def _state_path():
    """Return the state.yaml path under the temp NCHANT_DATA_DIR."""
    from nchantdoffice.updates import checker as checker_mod
    return checker_mod._STATE_PATH


def _reset_state():
    """Remove the state.yaml between tests so each test starts clean."""
    sp = _state_path()
    if sp.exists():
        sp.unlink()


def test_dismiss_version_default_is_seven_days():
    """``dismiss_version("0.1.0")`` writes an expiry ~7 days from now."""
    from nchantdoffice.updates.checker import (
        DISMISS_DURATION_DAYS,
        dismiss_version,
        is_dismissed,
    )

    _reset_state()
    assert DISMISS_DURATION_DAYS == 7
    before = datetime.now(timezone.utc)
    dismiss_version("0.1.0")
    after = datetime.now(timezone.utc)

    # The state file should now exist.
    sp = _state_path()
    assert sp.exists(), f"state.yaml not written at {sp}"

    # is_dismissed returns True immediately after.
    assert is_dismissed("0.1.0") is True

    # Inspect the written expiry timestamp — must be ~7 days from
    # the before/after window.
    text = sp.read_text()
    assert "0.1.0" in text
    # Extract the timestamp after the version colon.
    # Format: ``  0.1.0: 2026-08-17T...``
    ts_line = [ln for ln in text.splitlines() if ln.strip().startswith("0.1.0:")][0]
    ts_str = ts_line.split(":", 1)[1].strip()
    written = datetime.fromisoformat(ts_str)
    delta_to_written = written - before
    # Allow a 2-second tolerance for clock drift + write latency.
    expected_min = timedelta(days=7) - timedelta(seconds=2)
    expected_max = timedelta(days=7) + timedelta(seconds=2)
    assert expected_min <= delta_to_written <= expected_max, (
        f"dismiss_version default expiry {written!r} is not ~7 days "
        f"from now; delta={delta_to_written}"
    )
    # Sanity: the written timestamp is after `after` (the
    # upper-bound of our measurement window).
    assert written > after


def test_dismiss_version_custom_days():
    """``dismiss_version("0.1.0", days=30)`` writes ~30 days from now."""
    from nchantdoffice.updates.checker import dismiss_version

    _reset_state()
    before = datetime.now(timezone.utc)
    dismiss_version("0.1.0", days=30)

    text = _state_path().read_text()
    ts_line = [ln for ln in text.splitlines() if ln.strip().startswith("0.1.0:")][0]
    ts_str = ts_line.split(":", 1)[1].strip()
    written = datetime.fromisoformat(ts_str)
    delta_to_written = written - before
    expected_min = timedelta(days=30) - timedelta(seconds=2)
    expected_max = timedelta(days=30) + timedelta(seconds=2)
    assert expected_min <= delta_to_written <= expected_max, (
        f"dismiss_version(days=30) expiry {written!r} delta={delta_to_written}"
    )


def test_is_dismissed_expired_treated_as_false():
    """Past-expiry entries in state.yaml cause is_dismissed to return False."""
    from nchantdoffice.updates.checker import is_dismissed

    _reset_state()
    # Manually write a state.yaml with a past expiry.
    past_iso = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    sp = _state_path()
    sp.parent.mkdir(parents=True, exist_ok=True)
    sp.write_text(
        f"dismissed_versions:\n  0.1.0: {past_iso}\n",
        encoding="utf-8",
    )
    os.chmod(sp, 0o600)

    assert is_dismissed("0.1.0") is False, (
        "is_dismissed should return False when the snooze expiry "
        f"is in the past. State file:\n{sp.read_text()}"
    )


def test_dismiss_keeps_longer_snooze():
    """Re-dismissing with a shorter days does not shorten the existing snooze."""
    from nchantdoffice.updates.checker import dismiss_version

    _reset_state()
    dismiss_version("0.1.0", days=30)
    first_text = _state_path().read_text()
    first_ts_line = [
        ln for ln in first_text.splitlines() if ln.strip().startswith("0.1.0:")
    ][0]
    first_ts = datetime.fromisoformat(first_ts_line.split(":", 1)[1].strip())

    # Now dismiss again with only 1 day — must NOT shorten.
    dismiss_version("0.1.0", days=1)

    second_text = _state_path().read_text()
    second_ts_line = [
        ln for ln in second_text.splitlines() if ln.strip().startswith("0.1.0:")
    ][0]
    second_ts = datetime.fromisoformat(second_ts_line.split(":", 1)[1].strip())

    assert second_ts == first_ts, (
        f"Re-dismiss with shorter days shortened the snooze: "
        f"first={first_ts}, second={second_ts}. The longer snooze "
        f"should win."
    )


def test_dismiss_version_zero_or_negative_rejected():
    """``dismiss_version(..., days=0)`` and ``days=-1`` do NOT write state."""
    from nchantdoffice.updates.checker import dismiss_version

    _reset_state()
    dismiss_version("0.1.0", days=0)
    assert not _state_path().exists(), (
        f"dismiss_version(days=0) should not write state.yaml, "
        f"but found it at {_state_path()}"
    )

    dismiss_version("0.1.0", days=-1)
    assert not _state_path().exists(), (
        f"dismiss_version(days=-1) should not write state.yaml, "
        f"but found it at {_state_path()}"
    )

    # Sanity: a valid call DOES write the state.
    dismiss_version("0.1.0", days=7)
    assert _state_path().exists()
