"""T-NEW-134 regression test: Get Pro toolbar button is visibly green.

**Get Pro button is configured green but renders default**

The NchantdDocumentProfilePane toolbar in
``nchantdoffice/widgets/documents/documents.py:432`` sets the
Get Pro button's config to:

    cfg = {
        "text": "Get Pro",
        "handler": ...,
        "height": 24,
        "background_color": "green",
    }

The upstream ``NchantdButton.initView``
(``nchantrs/widgets/controls/buttons.py:94``) does NOT read
``background_color`` from the config at all -- the key is dead
config. Nothing applies a green stylesheet to the rendered
button, so the user sees a default-styled "Get Pro" button
indistinguishable from the other toolbar buttons.

The fix:
1. After ``NchantdButton(self, cfg).initWidget()`` at L446,
   apply ``self.profile_select_entry.setStyleSheet(...)``
   using the ``background_color`` cfg value. The ``text``
   should also be legible: pair green background with a
   high-contrast foreground (white text by convention).
2. Accept either a named color (``"green"``) or a hex
   string (``"#1d8f3a"``); both must round-trip through
   ``setStyleSheet`` cleanly.
3. Defensive: when ``background_color`` is missing/None, no
   stylesheet is applied (the button falls back to its
   platform-default styling -- never crashes).

Affected sites:
- nchantdoffice/widgets/documents/documents.py:
  ``NchantdOfficeDocumentProfilePane.initView`` after the
  Get Pro button construction (L446).

Migration plan (no priority / low priority -- design
decision first): the stylesheet is applied post-initWidget
so we don't fight the upstream ``NchantdButton`` contract.
We translate ``background_color`` from the cfg into a
single ``setStyleSheet(...)`` call. A future T-NEW could
promote this to a shared helper on
``NchantdOfficeButton`` if more call sites need it.

Steps:
1. Add a small helper ``_apply_bg_color(button, color)``
   that issues the stylesheet call with both
   ``background-color`` and ``color`` (white) for contrast.
2. After ``self.profile_select_entry = NchantdButton(...)
   .initWidget()`` at L446, call the helper with the cfg's
   ``background_color``.
"""

import inspect
from types import SimpleNamespace

import pytest


def _read(path):
    return path.read_text()


def _source():
    return _read(
        PROJ_ROOT
        / "nchantdoffice"
        / "widgets"
        / "documents"
        / "documents.py"
    )


PROJ_ROOT = __import__("pathlib").Path(
    "/home/solubrew/.hermes/projects/nchantdoffice"
)


# ---------------------------------------------------------------------------
# Source-level: button construction must include stylesheet application
# ---------------------------------------------------------------------------

def test_get_pro_button_cfg_still_has_background_color():
    """Regression guard: the cfg dict still carries the
    ``background_color`` key (so the canonical name is the
    single source of truth).
    """
    src = _source()
    # Look for the Get Pro cfg block.
    assert '"background_color": "green"' in src, (
        "Get Pro button cfg must continue to set background_color "
        "(T-NEW-134 contract)"
    )


def test_get_pro_button_applies_background_color_via_setstylesheet():
    """Source-level: after the Get Pro button is built, the
    code must call ``setStyleSheet(...)`` (or a helper that
    does) with the background_color value. Otherwise the
    key is dead config.
    """
    src = _source()
    # The Get Pro block is around L432-447. Find the part
    # after ``NchantdButton(self, cfg).initWidget()``.
    needle = (
        'self.profile_select_entry = NchantdButton(self, cfg).initWidget()'
    )
    assert needle in src, (
        "Get Pro button construction must still exist "
        "(T-NEW-134)"
    )
    # After construction, there must be a setStyleSheet call
    # (or a helper invocation that contains it) referencing
    # ``background_color``.
    idx = src.index(needle)
    after = src[idx + len(needle): idx + len(needle) + 1000]
    assert "setStyleSheet" in after, (
        "Get Pro button must apply background_color via "
        "setStyleSheet after construction (T-NEW-134)"
    )


def test_get_pro_button_helper_supports_named_and_hex_colors():
    """The styling helper must accept both named colors
    (``"green"``) and hex strings (``"#1d8f3a"``) without
    crashing or producing empty stylesheets.
    """
    from nchantdoffice.widgets.documents.documents import (
        NchantdOfficeDocumentMixin,
    )
    # The helper is expected to be a staticmethod named
    # ``_apply_bg_color`` (or similar). Probe it directly.
    helper = getattr(
        NchantdOfficeDocumentMixin,
        "_apply_bg_color",
        None,
    )
    assert callable(helper), (
        "NchantdOfficeDocumentMixin must expose an "
        "_apply_bg_color helper (T-NEW-134)"
    )

    captured: list = []

    class _StubButton:
        def __init__(self):
            self.calls = []

        def setStyleSheet(self, qss):
            captured.append(qss)

    btn = _StubButton()

    helper(btn, "green")
    assert captured, "helper must call setStyleSheet"
    qss = captured[-1]
    assert "background-color" in qss.lower(), (
        f"stylesheet must include background-color; got {qss!r}"
    )
    assert "green" in qss.lower(), (
        f"stylesheet must reference the color name; got {qss!r}"
    )

    # Hex input: must not raise and must round-trip into the
    # stylesheet.
    helper(btn, "#1d8f3a")
    assert "#1d8f3a" in captured[-1].lower() or "1d8f3a" in captured[
        -1
    ].lower(), (
        f"hex color must appear in stylesheet; got {captured[-1]!r}"
    )


def test_get_pro_button_helper_no_op_when_color_missing():
    """When ``color`` is None / missing, the helper is a
    no-op -- never raises and never applies an empty
    stylesheet (which can cause unwanted side effects on Qt).
    """
    from nchantdoffice.widgets.documents.documents import (
        NchantdOfficeDocumentMixin,
    )
    helper = NchantdOfficeDocumentMixin._apply_bg_color
    captured: list = []

    class _StubButton:
        def setStyleSheet(self, qss):
            captured.append(qss)

    btn = _StubButton()
    for falsy in (None, "", "   "):
        helper(btn, falsy)
        assert captured == [], (
            f"helper must be a no-op when color is {falsy!r}; "
            f"got {captured!r}"
        )


def test_get_pro_button_helper_text_contrast_is_white():
    """A green background needs white text for legibility.
    The stylesheet must include ``color: white``.
    """
    from nchantdoffice.widgets.documents.documents import (
        NchantdOfficeDocumentMixin,
    )
    helper = NchantdOfficeDocumentMixin._apply_bg_color
    captured: list = []

    class _StubButton:
        def setStyleSheet(self, qss):
            captured.append(qss)

    helper(_StubButton(), "green")
    qss = captured[-1]
    # Should contain color: white (or #ffffff) for contrast.
    assert (
        "color: white" in qss.lower()
        or "color:#ffffff" in qss.lower()
    ), (
        f"stylesheet must set text color to white for green bg; "
        f"got {qss!r}"
    )


# ---------------------------------------------------------------------------
# Behavioural: initView wires the helper after the button construction
# ---------------------------------------------------------------------------

def test_initview_invokes_apply_bg_color_helper():
    """Source-level: the Get Pro button construction block
    must call ``_apply_bg_color`` (or equivalent) with the
    cfg's ``background_color`` value -- this is the
    single link between the cfg key and the rendered button.
    """
    src = _source()
    assert "_apply_bg_color" in src, (
        "documents.py must call _apply_bg_color for the Get "
        "Pro button (T-NEW-134)"
    )
    # Confirm it's invoked in the Get Pro block (after the
    # NchantdButton construction).
    idx = src.index('"background_color": "green"')
    after = src[idx: idx + 1500]
    assert "_apply_bg_color" in after, (
        "_apply_bg_color must be invoked in the Get Pro block "
        "(T-NEW-134)"
    )