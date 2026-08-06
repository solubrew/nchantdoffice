"""T-NEW-053 regression test: Calculator keyboard input.

The testing report (2026-08-03) states:
  "NchantdOfficeCalculator still doesn't pickup input from number pad
   or number row....buttons only respond to clicks"

Root cause: the right-side Calculator tab was seeded with
``NchantdCalculator`` (the base class) which had NO ``keyPressEvent``.
Only ``NchantdAdvancedCalculator`` had keyboard routing.

Fix:
1. ``keyPressEvent`` + focus handlers moved to the base
   ``NchantdCalculator`` so ALL calculator subclasses get keyboard
   support.
2. models.yaml seed changed from ``NchantdCalculator`` to
   ``NchantdAdvancedCalculator`` (which inherits the base's new
   keyboard support).
"""

import ast
import inspect


def _get_source(cls):
    """Return the source text for a class."""
    return inspect.getsource(cls)


def _has_method(cls, name):
    """Check if a class defines a method (not inherited)."""
    src = _get_source(cls)
    return f"def {name}" in src


def test_base_calculator_has_keyPressEvent():
    """``NchantdCalculator`` (base) must define ``keyPressEvent``."""
    from nchantrs.widgets.calculators.calculators import NchantdCalculator
    assert _has_method(NchantdCalculator, "keyPressEvent"), (
        "NchantdCalculator must define keyPressEvent (T-NEW-053)"
    )


def test_base_calculator_has_focus_handlers():
    """``NchantdCalculator`` must define focusInEvent and focusOutEvent."""
    from nchantrs.widgets.calculators.calculators import NchantdCalculator
    assert _has_method(NchantdCalculator, "focusInEvent"), (
        "NchantdCalculator must define focusInEvent"
    )
    assert _has_method(NchantdCalculator, "focusOutEvent"), (
        "NchantdCalculator must define focusOutEvent"
    )


def test_base_calculator_keyPressEvent_maps_digits():
    """``keyPressEvent`` must handle Key_0 through Key_9."""
    from nchantrs.widgets.calculators.calculators import NchantdCalculator
    src = _get_source(NchantdCalculator.keyPressEvent)
    assert "Key_0" in src and "Key_9" in src, (
        "keyPressEvent must map Key_0..Key_9 for numpad + number row"
    )


def test_base_calculator_keyPressEvent_maps_operators():
    """``keyPressEvent`` must handle +, -, *, /, Enter, Backspace, Escape."""
    from nchantrs.widgets.calculators.calculators import NchantdCalculator
    src = _get_source(NchantdCalculator.keyPressEvent)
    required = ["Key_Plus", "Key_Minus", "Key_Asterisk", "Key_Slash",
                "Key_Return", "Key_Enter", "Key_Backspace", "Key_Escape"]
    missing = [k for k in required if k not in src]
    assert not missing, (
        f"keyPressEvent missing operators: {missing}"
    )


def test_base_calculator_has_press_digit_helper():
    """``_press_digit`` must exist on the base class (shared by button + key)."""
    from nchantrs.widgets.calculators.calculators import NchantdCalculator
    assert hasattr(NchantdCalculator, "_press_digit"), (
        "NchantdCalculator must have _press_digit helper"
    )


def test_models_yaml_uses_advanced_calculator():
    """The right-side Calculator tab must use NchantdAdvancedCalculator
    (which inherits keyboard support from the base)."""
    with open("nchantdoffice/_data_/models.yaml") as f:
        content = f.read()
    assert "NchantdAdvancedCalculator" in content, (
        "models.yaml must seed the Calculator tab with NchantdAdvancedCalculator"
    )
    # The old base-class seed should NOT be the one for the Calculator tab
    assert (
        "'Calculator', 'nchantrs.widgets.calculators.calculators.NchantdCalculator'"
        not in content
    ), "Calculator tab must not use the base NchantdCalculator (no keyboard)"


def test_advanced_calculator_inherits_keyPressEvent():
    """NchantdAdvancedCalculator still has keyPressEvent (own or inherited)."""
    from nchantrs.widgets.calculators.calculators import (
        NchantdAdvancedCalculator,
        NchantdCalculator,
    )
    assert hasattr(NchantdAdvancedCalculator, "keyPressEvent"), (
        "NchantdAdvancedCalculator must have keyPressEvent"
    )
    # It may define its own (override) or inherit from base — both are fine
