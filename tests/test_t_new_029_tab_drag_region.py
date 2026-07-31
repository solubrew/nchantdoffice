"""T-NEW-029 -- Tab drag-init only on tab-name area (TDD tests).

The inline TODO at widgets/tabs.py:mousePressEvent says:
today's tab drag-and-drop initiates on any mouse-press
inside the tab, making it hard to select text / interact
with tab content without accidentally starting a drag.

The user picked the "named sub-widget" approach (per the
2026-07-31 clarification): the tab-name area is a logical
sub-region that owns the press handler. The body region
below the tab-name area must NOT initiate drag.

Implementation:

  1. Disable ``setMovable`` on the tab bar so Qt doesn't
     intercept drag itself.
  2. Add ``_is_in_tab_name_area(index, pos)`` helper:
     returns True when ``pos`` is inside the tab-name
     area of the tab at ``index``. The tab-name area is
     the top portion of ``tabBar().tabRect(index)`` --
     we use 70% of the height as the "name area" (the
     bottom 30% is the close-button + padding area).
  3. Override ``mousePressEvent`` so the drag-start pos
     is only recorded when the press lands in the
     tab-name area.
  4. ``mouseMoveEvent`` only initiates drag when
     ``_drag_start_pos`` is set (already gated by
     press-handler).
  5. Charts segfault (the T-NEW-029 deferred stub in
     charts.py) shares the same root cause -- chart drag
     initiates on the chart widget area rather than a
     discrete handle. The chart fix mirrors this one.

Tests:

  - test_is_in_tab_name_area_returns_true_for_top_of_tab
  - test_is_in_tab_name_area_returns_false_for_bottom_of_tab
  - test_is_in_tab_name_area_returns_false_for_invalid_index
  - test_is_in_tab_name_area_handles_empty_tab_bar
  - test_mouse_press_in_tab_name_area_records_drag_start
  - test_mouse_press_in_body_does_not_record_drag_start
  - test_tab_bar_movable_is_disabled (source-level guard)
  - test_charts_drag_init_too (source-level check)
"""

import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

from PySide6.QtWidgets import QApplication, QTabWidget, QWidget
_QAPP = QApplication.instance() or QApplication(sys.argv)


# ---------------------------------------------------------------------------
# _is_in_tab_name_area helper
# ---------------------------------------------------------------------------


def _make_tabs():
    """Build a NchantdOfficeTabs via __new__ with a
    QTabWidget parent containing 3 tabs.
    """
    from nchantdoffice.widgets.tabs import NchantdOfficeTabs
    tabs = NchantdOfficeTabs.__new__(NchantdOfficeTabs)
    parent = QTabWidget()
    parent.show()
    for i in range(3):
        parent.addTab(QWidget(), f"Tab {i}")
    tabs._parent = parent
    return tabs, parent


def _make_duck_tabs_with_rects(rects):
    """Build a duck-typed tabs instance whose tabBar() returns
    a mock with ``tabRect(index)`` values from ``rects``.

    Note: ``tabBar.pos()`` must return a real ``QPoint`` (not
    a MagicMock) so the ``translated`` arithmetic in
    ``_is_in_tab_name_area`` produces a real ``QRect``.
    """
    from nchantdoffice.widgets.tabs import NchantdOfficeTabs
    from PySide6.QtCore import QPoint
    tabs = NchantdOfficeTabs.__new__(NchantdOfficeTabs)
    fake_bar = MagicMock()
    fake_bar.tabRect.side_effect = lambda i: rects[i] if 0 <= i < len(rects) else None
    fake_bar.tabAt.side_effect = lambda pos: 0
    fake_bar.count.return_value = len(rects)
    fake_bar.pos.return_value = QPoint(0, 0)
    tabs.tabBar = lambda: fake_bar
    return tabs


def _rect(x, y, w, h):
    from PySide6.QtCore import QRect
    return QRect(x, y, w, h)


def test_is_in_tab_name_area_returns_true_for_top_of_tab():
    """A press in the top portion of a tab's rect is in the
    tab-name area.
    """
    from nchantdoffice.widgets.tabs import NchantdOfficeTabs
    # Tab rect: 0,0 to 200,30. Top 70% = top 21 px.
    rects = [_rect(0, 0, 200, 30)]
    tabs = _make_duck_tabs_with_rects(rects)
    # Press at y=10 (top quarter) -- in name area
    assert tabs._is_in_tab_name_area(0, _rect(0, 10, 200, 5)) is True


def test_is_in_tab_name_area_returns_false_for_bottom_of_tab():
    """A press in the bottom portion (close-button / padding)
    is NOT in the tab-name area.
    """
    from nchantdoffice.widgets.tabs import NchantdOfficeTabs
    rects = [_rect(0, 0, 200, 30)]
    tabs = _make_duck_tabs_with_rects(rects)
    # Press at y=25 (bottom, last 5px of 30) -- below the 70%
    # threshold (30*0.7=21)
    assert tabs._is_in_tab_name_area(0, _rect(0, 25, 200, 5)) is False


def test_is_in_tab_name_area_returns_false_for_invalid_index():
    """Defensive: an invalid index (negative, out-of-range)
    returns False (no drag-init).
    """
    rects = [_rect(0, 0, 200, 30)]
    tabs = _make_duck_tabs_with_rects(rects)
    # Negative index
    assert tabs._is_in_tab_name_area(-1, _rect(0, 10, 200, 5)) is False
    # Out of range
    assert tabs._is_in_tab_name_area(5, _rect(0, 10, 200, 5)) is False


def test_is_in_tab_name_area_handles_empty_tab_bar():
    """Defensive: when tabBar is empty / None, returns False."""
    rects = []
    tabs = _make_duck_tabs_with_rects(rects)
    assert tabs._is_in_tab_name_area(0, _rect(0, 10, 200, 5)) is False


def test_is_in_tab_name_area_handles_tabBar_returning_none():
    """Defensive: when tabBar().tabRect(index) returns None
    (e.g. tab is hidden), returns False.
    """
    from nchantdoffice.widgets.tabs import NchantdOfficeTabs
    fake_bar = MagicMock()
    fake_bar.tabRect.return_value = None
    fake_bar.count.return_value = 3
    tabs = NchantdOfficeTabs.__new__(NchantdOfficeTabs)
    tabs.tabBar = lambda: fake_bar
    assert tabs._is_in_tab_name_area(0, _rect(0, 10, 200, 5)) is False


def test_is_in_tab_name_area_handles_missing_tab_at():
    """Defensive: tabBar without tabAt() falls back to
    accepting all presses in the name area (no index).

    Note: this test only exercises the ``count`` + ``tabRect``
    path inside ``_is_in_tab_name_area``. The ``tabAt`` is
    only called in ``mousePressEvent``, not in this helper.
    """
    from nchantdoffice.widgets.tabs import NchantdOfficeTabs
    from PySide6.QtCore import QPoint, QRect
    fake_bar = MagicMock()
    fake_bar.tabRect.return_value = QRect(0, 0, 200, 30)
    fake_bar.count.return_value = 1
    # pos() must return a real QPoint for the translated() call
    fake_bar.pos.return_value = QPoint(0, 0)
    tabs = NchantdOfficeTabs.__new__(NchantdOfficeTabs)
    tabs.tabBar = lambda: fake_bar
    # The press at (0, 10) is within the top 70% of the tab
    # rect (top 21 px). Should return True.
    assert tabs._is_in_tab_name_area(0, QRect(0, 10, 200, 5)) is True


# ---------------------------------------------------------------------------
# mousePressEvent gating
# ---------------------------------------------------------------------------


def test_mouse_press_in_tab_name_area_records_drag_start():
    """Press inside the tab-name area sets ``_drag_start_pos``."""
    from nchantdoffice.widgets.tabs import NchantdOfficeTabs
    from PySide6.QtCore import QRect, QPoint, Qt
    from PySide6.QtWidgets import QApplication
    # QApplication must exist for Qt.LeftButton to compare
    # correctly in PySide6.
    QApplication.instance() or QApplication([])
    rects = [_rect(0, 0, 200, 30)]
    tabs = _make_duck_tabs_with_rects(rects)
    # Simulate a press event with pos() returning (10, 10) -- top
    event = MagicMock()
    event.button.return_value = Qt.LeftButton
    event.pos.return_value = QPoint(10, 10)
    tabs.mousePressEvent(event)
    # ``hasattr`` may raise on the unwrapped object; use a
    # try/except + explicit getattr to read the attribute
    # cleanly.
    try:
        has_pos = hasattr(tabs, "_drag_start_pos")
    except Exception:
        has_pos = False
    assert has_pos, (
        "Press in tab-name area must record _drag_start_pos"
    )


def test_mouse_press_in_body_does_not_record_drag_start():
    """Press outside the tab-name area does NOT set
    ``_drag_start_pos`` -- the user is interacting with
    the tab body and drag must not initiate.
    """
    from nchantdoffice.widgets.tabs import NchantdOfficeTabs
    from PySide6.QtCore import QPoint, Qt
    from PySide6.QtWidgets import QApplication
    QApplication.instance() or QApplication([])
    rects = [_rect(0, 0, 200, 30)]
    tabs = _make_duck_tabs_with_rects(rects)
    # y=25 is in the bottom 30% -- body / close-button area
    event = MagicMock()
    event.button.return_value = Qt.LeftButton
    event.pos.return_value = QPoint(10, 25)
    tabs.mousePressEvent(event)
    try:
        has_pos = hasattr(tabs, "_drag_start_pos")
    except Exception:
        has_pos = False
    assert not has_pos, (
        f"Press in body must NOT record _drag_start_pos. "
        f"has_pos: {has_pos}"
    )


# ---------------------------------------------------------------------------
# Source-level checks
# ---------------------------------------------------------------------------


def test_tab_bar_movable_is_disabled():
    """The tab bar must have ``setMovable(False)`` so Qt
    doesn't intercept drag itself. Source-level guard.
    """
    from pathlib import Path
    tabs_py = Path(
        "/home/solubrew/.hermes/projects/nchantdoffice/nchantdoffice/"
        "widgets/tabs.py"
    ).read_text()
    # We expect ``setMovable(False)`` to be present
    assert "setMovable(False)" in tabs_py, (
        "tab bar must call setMovable(False) so Qt doesn't "
        "intercept drag-init (T-NEW-029 named sub-widget approach)"
    )


def test_mouse_press_event_calls_is_in_tab_name_area():
    """The mousePressEvent override must call
    ``_is_in_tab_name_area`` (source-level guard).
    """
    from pathlib import Path
    tabs_py = Path(
        "/home/solubrew/.hermes/projects/nchantdoffice/nchantdoffice/"
        "widgets/tabs.py"
    ).read_text()
    assert "_is_in_tab_name_area" in tabs_py, (
        "mousePressEvent must consult _is_in_tab_name_area "
        "(T-NEW-029 named sub-widget approach)"
    )


def test_charts_drag_init_too():
    """The charts.py drag-init segments (the deferred stubs
    at L183,208) share the same root cause -- chart
    drag-init on the chart widget area rather than a
    discrete handle. A pointer to T-NEW-029 must be left
    at those sites so a follow-up fix can apply the same
    gate.
    """
    from pathlib import Path
    charts_py = Path(
        "/home/solubrew/.hermes/projects/nchantdoffice/nchantdoffice/"
        "widgets/panes/charts.py"
    ).read_text()
    assert "T-NEW-029" in charts_py, (
        "charts.py must reference T-NEW-029 (drag-init root cause)"
    )
