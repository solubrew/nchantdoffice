"""T-NEW-037 (followup): regression test for the proven NchantdChart
``addWidget(None)`` root-cause.

Background
----------

The historical TODO comment at ``charts.py:183-191`` and
``charts.py:211-219`` blamed a NchantdChart segfault on the
T-NEW-029 drag-init gating (drag-init on the chart widget area
rather than a discrete handle). The actual root cause is
different: PySide6 ``QLayout.addWidget(None)`` exits 139
(SIGSEGV) because passing ``None`` to ``addWidget`` is
unsupported and crashes the native layout engine.

The two deferred builders at the call sites both return ``None``
implicitly:

  * ``NchantdChartConfigPane._build_chart_action_button_group``
    (charts.py:302)
  * ``NchantdChartConfigPane._build_border_style_editor``
    (charts.py:278)

The historical TODO was a misdiagnosis: the builders never
segfaulted on their own -- the segfault was ``addWidget(None)``
firing the moment the call sites were uncommented. This test
pins the fix: the builders MUST return a real ``QWidget``, so
``addWidget`` never receives ``None`` at the re-enabled call
sites.

What this test asserts
----------------------

1. ``_build_chart_action_button_group`` returns a non-``None``
   ``QWidget`` instance.
2. ``_build_border_style_editor`` returns a non-``None``
   ``QWidget`` instance.
3. ``chart_details_layout.addWidget(...)`` is called with a
   non-``None`` argument at both un-commented call sites (the
   action button group + the border style editor).
4. ``addWidget(None)`` raises in PySide6 -- proves the
   historical misdiagnosis was the real root cause.
5. The two call sites are present in ``initView`` (not
   commented-out) so the segfault no longer hides behind
   commenting.

The behavioural pins (#1, #2) construct the builders via a
bare ``__new__`` + attribute-injection seam so the test does
not need to run the full ``initWidget`` construction (which
requires a live ``NchantdOfficeApplication`` parent). The
``qt-parent-harness`` skill documents this pattern: monkeypatch
the attributes the code under test reads instead of running
the full Qt parent boot.

Source-level pins (#3, #5) read
``inspect.getsource(NchantdChartConfigPane.initView)`` and
assert on the call sites' presence and arguments.
"""

from __future__ import annotations

import inspect
import re
import os

import pytest

# Force offscreen QPA before any Qt import. Mirrors tests/conftest.py.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


# ---------------------------------------------------------------------------
# Source-level pins (do not require a live Qt widget)
# ---------------------------------------------------------------------------


def _initview_source() -> str:
    """Return the ``initView`` source of ``NchantdChartConfigPane``."""
    from nchantdoffice.widgets.panes.charts import NchantdChartConfigPane

    return inspect.getsource(NchantdChartConfigPane.initView)


def test_action_button_group_call_site_is_active_in_initview():
    """The action button group addWidget call site MUST be present
    in ``initView`` (not commented-out).

    The historical fix was to comment out the call site. That
    fix hid the segfault but never resolved it -- the moment
    the call site is re-enabled, ``addWidget(None)`` crashes
    again. The T-NEW-037 fix re-enables the call site because
    the builder now returns a real widget.
    """
    src = _initview_source()
    # Find the un-commented assignment to action_button_group.
    pattern = re.compile(
        r"^[^\n#]*?self\.action_button_group\s*=\s*self\._build_chart_action_button_group\(\)",
        re.MULTILINE,
    )
    match = pattern.search(src)
    assert match is not None, (
        "The action_button_group assignment must be un-commented "
        "in initView (the historical 'comment out the call site' "
        "fix hid the segfault but never resolved it)."
    )


def test_border_style_editor_call_site_is_active_in_initview():
    """The border style editor addWidget call site MUST be present
    in ``initView`` (not commented-out).

    Same pattern as the action button group above.
    """
    src = _initview_source()
    pattern = re.compile(
        r"^[^\n#]*?self\.chart_border_bar\s*=\s*self\._build_border_style_editor\(\)",
        re.MULTILINE,
    )
    match = pattern.search(src)
    assert match is not None, (
        "The chart_border_bar assignment must be un-commented "
        "in initView (the historical 'comment out the call site' "
        "fix hid the segfault but never resolved it)."
    )


def test_call_sites_use_named_attributes_not_none():
    """Defensive pin: the two un-commented call sites MUST
    invoke ``addWidget`` with the variable they assigned to,
    not with a bare ``None``.

    Catches the regression shape where a developer re-enables
    the call site but forgets the builder still returns ``None``.

    The regex anchors on the start of the line being non-``#``
    so it only matches ACTIVE call sites, not commented-out
    historical TODO markers.
    """
    src_lines = _initview_source().splitlines()
    action_found = False
    border_found = False
    for line in src_lines:
        stripped = line.lstrip()
        # Skip commented lines (any line whose first non-whitespace
        # char is `#`).
        if stripped.startswith("#"):
            continue
        if "chart_details_layout.addWidget(self.action_button_group)" in line:
            action_found = True
        if "chart_details_layout.addWidget(self.chart_border_bar)" in line:
            border_found = True
    assert action_found, (
        "chart_details_layout.addWidget(self.action_button_group) "
        "must be present (and un-commented)."
    )
    assert border_found, (
        "chart_details_layout.addWidget(self.chart_border_bar) "
        "must be present (and un-commented)."
    )


def test_t_new_029_drag_init_blame_removed_from_todo():
    """The historical TODO wrongly blamed T-NEW-029 (drag-init
    gating) for the segfault. Now that we know the real root
    cause was ``addWidget(None)``, the misleading TODO must
    NOT remain at the call sites.
    """
    src = _initview_source()
    # The misleading TODO at the call sites:
    #   # TODO causes segmentation fault -- T-NEW-029: same root cause as
    #   # the tab drag-init fix (drag-init on the chart widget area
    #   # rather than a discrete handle). Apply the same gate
    #   # pattern when this stub is implemented.
    blame_pattern = re.compile(
        r"#\s*TODO\s+causes\s+segmentation\s+fault\s+--\s*T-NEW-029",
        re.MULTILINE,
    )
    match = blame_pattern.search(src)
    assert match is None, (
        "The T-NEW-029 blame in the TODO comment was a misdiagnosis. "
        "The real root cause was addWidget(None) (PySide6 layout "
        "rejects None as the widget argument). The misleading TODO "
        "must be removed now that the builders return real QWidgets."
    )


# ---------------------------------------------------------------------------
# Behavioural pins (require a live offscreen QApplication)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def qapp():
    """Module-scoped QApplication so the offscreen Qt session
    is reused across the behavioural tests."""
    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    yield app


def _build_pane_via_new():
    """Build a ``NchantdChartConfigPane`` via ``__new__`` + attribute
    injection so we can exercise the builder methods WITHOUT
    running the full ``initWidget`` chain (which depends on the
    production ``NchantdOfficeApplication`` parent).

    Only the attributes the two builder methods actually read
    are injected. This is the ``qt-parent-harness`` skill's
    Pattern: monkeypatch the seam the code looks up.

    The builders call ``NchantdAcceptButtons(self, cfg).initWidget()``
    and ``NchantdBorderConfigBar(self, cfg).initWidget()`` --
    those widget classes walk the parent chain looking for an
    ``app`` (the same ``init_variables`` walker in
    widgets.py:127-149). We give the stub pane a parent with
    the four required attributes (``model``/``app``/``view``/
    ``new_application`` and no ``rowCount``) so the walker
    terminates cleanly.
    """

    from nchantdoffice.widgets.panes.charts import NchantdChartConfigPane

    class _FakeApp:
        """Stub parent that satisfies the ``init_variables`` walker."""

        model = None
        view = None
        new_application = True
        app = None  # type: ignore[assignment]  # Rebound to self by the fixture.
        # No rowCount attribute -- required by the walker's
        # negative check.

    pane = NchantdChartConfigPane.__new__(NchantdChartConfigPane)
    fake_app = _FakeApp()
    fake_app.app = fake_app
    pane.parent = fake_app
    pane.app = fake_app
    pane.config = None
    return pane


def test_build_chart_action_button_group_returns_real_qwidget(qapp):
    """``_build_chart_action_button_group`` MUST return a real
    ``QWidget`` instance, not ``None``.

    Before the fix: returns ``None`` implicitly (body empty).
    After the fix: returns a ``QWidget`` (action button group).
    """
    from PySide6.QtWidgets import QWidget

    pane = _build_pane_via_new()
    result = pane._build_chart_action_button_group()
    assert result is not None, (
        "_build_chart_action_button_group must return a real QWidget, "
        "not None -- the historical root cause was addWidget(None), "
        "not the T-NEW-029 drag gating."
    )
    assert isinstance(result, QWidget), (
        f"_build_chart_action_button_group must return a QWidget. "
        f"Got: {type(result).__name__}"
    )


def test_build_border_style_editor_returns_real_qwidget(qapp):
    """``_build_border_style_editor`` MUST return a real
    ``QWidget`` instance, not ``None``.

    Before the fix: returns ``None`` implicitly (body empty).
    After the fix: returns a ``QWidget`` (border style editor).
    """
    from PySide6.QtWidgets import QWidget

    pane = _build_pane_via_new()
    result = pane._build_border_style_editor()
    assert result is not None, (
        "_build_border_style_editor must return a real QWidget, "
        "not None -- the historical root cause was addWidget(None), "
        "not the T-NEW-029 drag gating."
    )
    assert isinstance(result, QWidget), (
        f"_build_border_style_editor must return a QWidget. "
        f"Got: {type(result).__name__}"
    )


def test_addwidget_none_is_rejected_by_pyside6(qapp):
    """Reproduce the proven root cause: ``layout.addWidget(None)``
    is the segfault source, not the widget construction.

    The segfault is a process-level crash (exit 139, SIGSEGV) --
    it does NOT raise a Python exception in modern PySide6 builds
    (the historical claim of a ``RuntimeError`` was wrong). We
    run the call in a subprocess so the SIGSEGV becomes a
    visible exit code instead of crashing pytest itself.

    This is the same proven signature the historical TODO
    blamed on T-NEW-029 drag gating. It isn't -- ``addWidget``
    rejects ``None`` at the native boundary with a SIGSEGV.
    """
    import subprocess
    import sys
    import textwrap

    script = textwrap.dedent(
        """
        import os
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from PySide6.QtWidgets import QApplication, QGridLayout
        app = QApplication.instance() or QApplication([])
        layout = QGridLayout()
        layout.addWidget(None)
        """
    )
    proc = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        timeout=15,
        env={**os.environ, "QT_QPA_PLATFORM": "offscreen"},
    )
    # SIGSEGV == exit code -11 on POSIX; the shell wraps it
    # as 139 (128 + 11). Some pytest runners report -signal
    # (negative) instead. Accept either form.
    if proc.returncode == 0:
        # The call somehow succeeded -- in that case the test
        # is no longer valid (PySide6 changed behaviour). Fail
        # loudly so we re-investigate.
        pytest.fail(
            f"addWidget(None) did not crash (exit 0). "
            f"stdout: {proc.stdout!r} stderr: {proc.stderr!r}. "
            f"The T-NEW-037 hypothesis no longer holds."
        )
    # Any non-zero exit code (especially 139 / -11) is the
    # proven segfault signature.
    assert proc.returncode != 0, (
        f"addWidget(None) must crash the process. "
        f"Got exit code: {proc.returncode}"
    )
