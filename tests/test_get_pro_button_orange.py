"""T-NEW-134 followup: Get Pro button uses dark orange instead of green.

The green cfg was a placeholder -- green reads as "success /
approved", which doesn't match the conversion intent of an
upsell button. Dark orange (``#FF8C00``) is the universal
ecommerce upsell color (Stripe, Shopify, GitHub Pro) and
pairs with white text for the same legibility reasons.

This card just swaps the cfg value + helper docstring;
``_apply_bg_color`` already accepts named colors AND hex
literals (T-NEW-134) so no helper change is needed.

Pins the contract in tests/test_get_pro_button_green.py
(2 followup tests):
- regression guard: cfg key is now ``#FF8C00`` not ``green``
- helper supports the hex value (covered by the existing
  ``test_get_pro_button_helper_supports_named_and_hex_colors``
  but we re-pin the specific dark-orange hex used here)
"""

import inspect
from types import SimpleNamespace

import pytest


PROJ_ROOT = __import__("pathlib").Path(
    "/home/solubrew/.hermes/projects/nchantdoffice"
)


def _read(path):
    return path.read_text()


def _documents_source():
    return _read(
        PROJ_ROOT / "nchantdoffice" / "widgets" / "documents" / "documents.py"
    )


# ---------------------------------------------------------------------------
# Source-level: cfg key uses dark orange hex
# ---------------------------------------------------------------------------

def test_get_pro_button_cfg_uses_dark_orange_hex():
    """Get Pro button cfg must use ``#FF8C00`` (dark orange),
    not ``green``. Orange reads as upsell; green reads as
    success / approved.
    """
    src = _documents_source()
    assert '"background_color": "#FF8C00"' in src, (
        "Get Pro button cfg must use dark orange hex #FF8C00 "
        "(T-NEW-134 followup); got "
        f"{[line for line in src.splitlines() if 'background_color' in line]!r}"
    )
    assert '"background_color": "green"' not in src, (
        "Get Pro button cfg must no longer be 'green' "
        "(T-NEW-134 followup)"
    )


def test_helper_docstring_references_dark_orange():
    """Source-level: the _apply_bg_color helper docstring
    references dark orange so future readers understand why
    this color was picked over green.
    """
    from nchantdoffice.widgets.documents.documents import (
        NchantdOfficeDocumentMixin,
    )
    src = inspect.getsource(NchantdOfficeDocumentMixin._apply_bg_color)
    assert "orange" in src.lower() or "#FF8C00" in src, (
        "_apply_bg_color docstring should mention the dark "
        "orange hex / conversion intent (T-NEW-134 followup)"
    )


# ---------------------------------------------------------------------------
# Behavioural: helper accepts the new hex
# ---------------------------------------------------------------------------

def test_apply_bg_color_renders_dark_orange_qss():
    """The helper, given ``#FF8C00``, must emit a stylesheet
    that carries the hex verbatim (Qt accepts hex literals).
    """
    from nchantdoffice.widgets.documents.documents import (
        NchantdOfficeDocumentMixin,
    )
    captured: list = []

    class _StubButton:
        def setStyleSheet(self, qss):
            captured.append(qss)

    btn = _StubButton()
    NchantdOfficeDocumentMixin._apply_bg_color(btn, "#FF8C00")
    assert captured, "helper must call setStyleSheet"
    qss = captured[-1]
    assert "#FF8C00" in qss or "ff8c00" in qss.lower(), (
        f"stylesheet must carry the dark orange hex; got {qss!r}"
    )
    # Same contrast rule: white text on saturated fill.
    assert (
        "color: white" in qss.lower() or "color:#ffffff" in qss.lower()
    ), f"stylesheet must set white text; got {qss!r}"
