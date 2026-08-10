"""T-NEW-059 — Tests for the user-configurable update-check interval.

The T-NEW-057 review (docs/update-process-review_20260810.md §2.1)
decided that the 6h polling cadence should stay the default for
v0.1.0, but become user-configurable via an Interface Tab knob
("Update check interval (hours)").

This file pins 4 invariants the T-NEW-059 implementation
promises:

  1. ``test_refresh_interval_default_is_six_hours`` — when the
     config has no ``check_update_interval_hours`` key, the
     helper returns 6 × 3600 = 21600 seconds.

  2. ``test_refresh_interval_custom_value_reads_correctly`` —
     when the config sets ``check_update_interval_hours`` to 1,
     the helper returns 3600 seconds; for 24, returns 86400.

  3. ``test_refresh_interval_invalid_value_falls_back_to_default``
     — invalid values (None, "abc", negative, > 168) fall back
     to the 6h default. Defensive against operator typos.

  4. ``test_refresh_interval_zero_or_negative_rejected`` — a
     value of 0 or negative is rejected; falls back to default.
     The minimum (1) is the lower bound; the maximum (168 = 1
     week) is the upper bound.

Tests call the module-level ``refresh_interval_seconds(cfg)``
helper directly — no Qt surface needed, runs in the
constrained venv.
"""

import sys
from pathlib import Path

PROJ_ROOT = Path("/home/solubrew/.hermes/projects/nchantdoffice")
sys.path.insert(0, str(PROJ_ROOT))

from nchantdoffice.updates.checker import (
    DEFAULT_CHECK_UPDATE_INTERVAL_HOURS,
    MAX_CHECK_UPDATE_INTERVAL_HOURS,
    MIN_CHECK_UPDATE_INTERVAL_HOURS,
    REFRESH_INTERVAL_SECONDS,
    refresh_interval_seconds,
)


def test_refresh_interval_default_is_six_hours():
    """Default (no cfg key) returns 6 × 3600 = 21600 seconds."""
    # No cfg at all.
    assert refresh_interval_seconds(None) == 6 * 3600
    # Empty dict.
    assert refresh_interval_seconds({}) == 6 * 3600
    # Dict with unrelated keys.
    assert refresh_interval_seconds({"foo": "bar"}) == 6 * 3600
    # kahndor.Instruct-shaped object (duck-typed via .get).
    class FakeCfg:
        def get(self, key, default=None):
            return default
    assert refresh_interval_seconds(FakeCfg()) == 6 * 3600
    # Sanity: the module-level constant matches the function default.
    assert REFRESH_INTERVAL_SECONDS == 6 * 3600
    assert DEFAULT_CHECK_UPDATE_INTERVAL_HOURS == 6


def test_refresh_interval_custom_value_reads_correctly():
    """Custom check_update_interval_hours reads correctly."""
    # 1 hour
    assert refresh_interval_seconds({"check_update_interval_hours": 1}) == 3600
    # 12 hours
    assert refresh_interval_seconds({"check_update_interval_hours": 12}) == 12 * 3600
    # 24 hours
    assert refresh_interval_seconds({"check_update_interval_hours": 24}) == 86400
    # 168 hours (1 week — the documented maximum)
    assert (
        refresh_interval_seconds({"check_update_interval_hours": 168})
        == 168 * 3600
    )


def test_refresh_interval_invalid_value_falls_back_to_default():
    """Invalid values fall back to the 6h default (T-NEW-059 §2.1)."""
    # None
    assert refresh_interval_seconds({"check_update_interval_hours": None}) == 6 * 3600
    # Non-numeric string
    assert refresh_interval_seconds({"check_update_interval_hours": "abc"}) == 6 * 3600
    # Empty string
    assert refresh_interval_seconds({"check_update_interval_hours": ""}) == 6 * 3600
    # List (not a number)
    assert refresh_interval_seconds({"check_update_interval_hours": [1, 2]}) == 6 * 3600


def test_refresh_interval_zero_or_negative_rejected():
    """Values < MIN or > MAX fall back to default (T-NEW-059 §2.1)."""
    # 0 — below the minimum of 1
    assert refresh_interval_seconds({"check_update_interval_hours": 0}) == 6 * 3600
    # Negative
    assert refresh_interval_seconds({"check_update_interval_hours": -1}) == 6 * 3600
    # 169 — above the maximum of 168 (1 week)
    assert refresh_interval_seconds({"check_update_interval_hours": 169}) == 6 * 3600
    # Far out of range
    assert refresh_interval_seconds({"check_update_interval_hours": 10000}) == 6 * 3600
    # Sanity: MIN and MAX match the documented values.
    assert MIN_CHECK_UPDATE_INTERVAL_HOURS == 1
    assert MAX_CHECK_UPDATE_INTERVAL_HOURS == 168
