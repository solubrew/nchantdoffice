"""Tests for nchantdoffice.license.tier_gate.

DESK T-NEW-047: tier_gate is the pure-Python decorator + helpers
that widget code uses to gate features by entitlement tier. The
gate reads its current envelope via a tier-getter callback so the
network client (DESK T-NEW-048) can plug in later without touching
this module's surface.

Key invariants under test:

  - No getter installed → the desktop boots into a KNOWN-SAFE
    "free" tier; never into "pro" or anything privileged.
  - @requires_tier honors the tier hierarchy: free < pro <
    pro_data < enterprise. Below-threshold → TierGateDenied;
    at-or-above → call passes.
  - The decorator is pure (no PySide6 / Qt event-loop
    dependency), so it's safe to import from anywhere and safe
    to test without spinning up a Qt app.
  - ``has_feature(name)`` reads the envelope's ``feat`` list.

The tests reset ``_DEFAULT_TIER_GETTER`` between cases via a
session-scoped autouse fixture so order doesn't matter.
"""
from __future__ import annotations

import pytest

from nchantdoffice.license import tier_gate
from nchantdoffice.license.tier_gate import (
    TIER_HIERARCHY,
    TierGateDenied,
    current_envelope,
    current_tier,
    has_feature,
    requires_tier,
    set_tier_getter,
)


# -----------------------------------------------------------------------------
# Helper: fake tier-getter (mirrors the pattern in the task spec).
# -----------------------------------------------------------------------------


class FakeGetter:
    """Minimal callable that returns a fixed envelope.

    Mirrors the production tier-getter signature:
        ``fn() -> dict | None``.
    """

    def __init__(self, envelope):
        self.envelope = envelope
        self.calls = 0  # for tests that want to verify caching

    def __call__(self):
        self.calls += 1
        return self.envelope


# -----------------------------------------------------------------------------
# Fixture: reset module-level tier getter around every test.
# -----------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_tier_getter():
    """Clear the module-level tier getter before AND after each test
    so test order can't pollute state.

    The gate's getter is a process-global side effect, so this
    fixture is autouse to keep every test hermetic.
    """
    tier_gate._DEFAULT_TIER_GETTER = None
    yield
    tier_gate._DEFAULT_TIER_GETTER = None


def _install_envelope(envelope):
    """Convenience: install a FakeGetter returning ``envelope``."""
    set_tier_getter(FakeGetter(envelope))


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


def test_current_tier_falls_back_to_free_when_no_getter_installed():
    """No tier getter installed → current_tier() returns 'free'.

    The desktop MUST boot into a known-safe tier; we never assume
    privilege by default.
    """
    # Autouse fixture already cleared the getter.
    assert tier_gate._DEFAULT_TIER_GETTER is None
    assert current_tier() == "free"


def test_set_tier_getter_then_current_tier_returns_envelope_tier():
    """After set_tier_getter(fn), current_tier() reads the envelope
    from fn() and returns its ``tier`` field.
    """
    _install_envelope(
        {"tier": "pro", "feat": ["x"], "uid": 1, "iat": 0, "exp": 9999999999}
    )

    assert current_tier() == "pro"


def test_requires_tier_passes_when_tier_is_above():
    """envelope tier=pro, decorator requires_tier('free') → call
    passes through and returns the wrapped function's result.

    'pro' is ABOVE 'free' in the hierarchy, so the gate is open.
    """
    _install_envelope({"tier": "pro", "feat": []})

    @requires_tier("free")
    def hello():
        return "hello"

    assert hello() == "hello"


def test_requires_tier_passes_when_tier_is_exactly_at():
    """envelope tier=pro, decorator requires_tier('pro') → call
    passes. The boundary is INCLUSIVE: at-tier == pass.
    """
    _install_envelope({"tier": "pro", "feat": []})

    @requires_tier("pro")
    def hello():
        return "passed"

    assert hello() == "passed"


def test_requires_tier_raises_when_tier_is_below():
    """envelope tier=free, decorator requires_tier('pro') → call
    raises TierGateDenied with required_tier='pro' and
    current_tier='free'.
    """
    _install_envelope({"tier": "free", "feat": []})

    @requires_tier("pro")
    def export_pdf():
        return "should not run"

    with pytest.raises(TierGateDenied) as exc_info:
        export_pdf()

    err = exc_info.value
    assert err.required_tier == "pro"
    assert err.current_tier == "free"


def test_requires_tier_raises_when_no_envelope_loaded():
    """No getter installed → current_tier falls back to 'free'.
    Therefore a requires_tier('pro') call must raise
    TierGateDenied with current_tier='free'.
    """
    # Autouse fixture cleared the getter; we're in the
    # "no entitlement loaded" state.
    assert tier_gate._DEFAULT_TIER_GETTER is None

    @requires_tier("pro")
    def export_pdf():
        return "should not run"

    with pytest.raises(TierGateDenied) as exc_info:
        export_pdf()

    err = exc_info.value
    assert err.required_tier == "pro"
    assert err.current_tier == "free"


def test_has_feature_returns_true_for_listed_feature():
    """Envelope with feat=['csv_export', 'pdf_export'] →
    has_feature('csv_export') is True.
    """
    _install_envelope(
        {"tier": "pro", "feat": ["csv_export", "pdf_export"]}
    )
    assert has_feature("csv_export") is True


def test_has_feature_returns_false_for_unlisted_feature():
    """Empty feat list → has_feature('csv_export') is False.
    """
    _install_envelope({"tier": "pro", "feat": []})
    assert has_feature("csv_export") is False


def test_has_feature_returns_false_when_no_envelope_loaded():
    """No getter installed → has_feature() is False (fail-closed).
    """
    assert tier_gate._DEFAULT_TIER_GETTER is None
    assert has_feature("csv_export") is False


def test_tier_hierarchy_orders_correctly():
    """The tier hierarchy orders as documented:
    free (0) < pro (1) < pro_data (2) < enterprise (3).
    """
    assert TIER_HIERARCHY["free"] < TIER_HIERARCHY["pro"]
    assert TIER_HIERARCHY["pro"] < TIER_HIERARCHY["pro_data"]
    assert TIER_HIERARCHY["pro_data"] < TIER_HIERARCHY["enterprise"]


def test_current_envelope_returns_envelope_dict_when_getter_installed():
    """``current_envelope()`` returns the full dict the getter
    returned (not just the tier string). Used by tests + the
    startup refresh flow.
    """
    env = {
        "tier": "pro_data",
        "feat": ["csv_export", "api_access"],
        "uid": 7,
        "iat": 1000,
        "exp": 9999999999,
    }
    _install_envelope(env)
    assert current_envelope() == env


def test_current_envelope_returns_none_when_no_envelope_loaded():
    """No getter installed → current_envelope() returns None.
    """
    assert tier_gate._DEFAULT_TIER_GETTER is None
    assert current_envelope() is None


def test_requires_tier_propagates_exception_from_wrapped_callable():
    """The decorator must NOT swallow exceptions raised inside the
    wrapped function (it should only raise TierGateDenied for the
    gate failure; anything else passes through).
    """
    _install_envelope({"tier": "enterprise", "feat": []})

    @requires_tier("free")
    def boom():
        raise RuntimeError("downstream failure")

    with pytest.raises(RuntimeError, match="downstream failure"):
        boom()
