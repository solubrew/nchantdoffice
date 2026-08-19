"""T-NEW-170 WIRE-2 -- pop_out_tab on NchantdOfficeTabSet.

The T-NEW-170 plan calls for a ``pop_out_tab(tab_index)`` method
on ``NchantdOfficeTabSet`` (in ``nchantdoffice/widgets/widgets.py``).
Operator right-clicks a tab (or clicks the toolbar \u00b6 button \u2014
WIRE-4) \u2192 pop_out_tab fires \u2192 the tab is detached into a
FloatedTab dialog (T-NEW-170 WIRE-1) wrapping a
NchantdDocumentStandaloneWindow (T-NEW-169 WIRE-2).

LOCKED DESIGN (operator-approved 2026-08-19):
  DECIDE-1 (a) -- re-attach only on dialog close or app close
  DECIDE-2 (ii) -- full standalone 2-pane shell that
  composes NchantdDocumentStandaloneWindow from T-NEW-169

Note that pop_out_tab is the *first half* of the operator's
lifecycle: operator detaches \u2192 goes back to the main app
\u2192 tab stays detached for as long as the dialog is open.
On close (X / File>Close / app exit), closeEvent on the
FloatedTab (T-NEW-170 WIRE-1 already shipped) calls
``self.home_tabset.re_attach_tab(self)`` (T-NEW-170 WIRE-3, the
next commit after WIRE-2).

Tests are AST-source structural. The tabset module imports
Qt at module level \u2014 same pattern as the other T-NEW-167..170
tests; AST inspection + string patterns only.
"""

import ast
import re
from pathlib import Path


TABSET_PATH = (
    Path(__file__).parents[1] / "nchantdoffice/widgets/widgets.py"
)


def _source() -> str:
    return TABSET_PATH.read_text()


def _find_class(name: str) -> ast.ClassDef:
    tree = ast.parse(_source())
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
    raise AssertionError(
        f"{name!r} class not found in {TABSET_PATH}"
    )


def _method_source(class_name: str, method_name: str) -> str:
    cls = _find_class(class_name)
    for body_node in cls.body:
        if (
            isinstance(body_node, ast.FunctionDef)
            and body_node.name == method_name
        ):
            return ast.unparse(body_node)
    raise AssertionError(
        f"{method_name!r} method not found in {class_name}"
    )


def test_pop_out_tab_method_exists():
    """`NchantdOfficeTabSet.pop_out_tab(...)` is a method on the
    class.

    Pre-fix there was no pop_out_tab method -- the operator could
    not detach a tab into a second dialog. The method is the
    counterpart to re_attach_tab (T-NEW-170 WIRE-3).
    """
    try:
        _method_source("NchantdOfficeTabSet", "pop_out_tab")
        return
    except AssertionError:
        raise AssertionError(
            "T-NEW-170 WIRE-2: `NchantdOfficeTabSet.pop_out_tab` "
            "method does not exist. The operator has no way to "
            "detach a tab into a FloatedTab dialog without it."
        )


def test_pop_out_tab_accepts_index_argument():
    """The method signature accepts a `tab_index` (int).

    The caller (right-click handler / toolbar button / keyboard
    shortcut) passes the position of the tab to detach. The
    method body then reads the corresponding widget from
    `app.view.panes["center"].widget(tab_index)`.
    """
    src = _method_source("NchantdOfficeTabSet", "pop_out_tab")
    has_index = "tab_index" in src
    assert has_index, (
        "T-NEW-170 WIRE-2: `pop_out_tab(tab_index: int)` must "
        "accept a `tab_index` parameter. Pre-fix the method "
        "(or the missing method) had no way to know which tab "
        "to detach."
    )


def test_pop_out_tab_reads_center_pane_widget():
    """The method body reads the document widget from the
    center pane's `widget(tab_index)` call (or equivalent).
    """
    src = _method_source("NchantdOfficeTabSet", "pop_out_tab")
    patterns = [
        r"""\.widget\(\s*tab_index\s*\)""",
        r"""app\.view\.panes\[.{0,5}center.{0,5}\]\.widget\(""",
        r"""self\.app\.view\.panes\[.{0,5}center.{0,5}\]\.widget\(""",
    ]
    ok = any(re.search(p, src) for p in patterns)
    assert ok, (
        f"T-NEW-170 WIRE-2: `pop_out_tab` body must read the "
        f"document widget from `app.view.panes['center'].widget(tab_index)`. "
        f"Source: {src[:600]}"
    )


def test_pop_out_tab_records_home_coordinates():
    """The method body stores `home_node_id`, `home_position`,
    `home_tabset` for the FloatedTab to read on re-attach.

    These three values are read by `FloatedTab.__init__` (in
    T-NEW-170 WIRE-1, the dialog class). If `pop_out_tab`
    fails to read the home node id from the model, re-attach
    has no way to put the tab back in the correct spot.
    """
    src = _method_source("NchantdOfficeTabSet", "pop_out_tab")
    has_node_id = "home_node_id" in src
    has_position = "home_position" in src
    has_tabset = "home_tabset" in src
    assert all([has_node_id, has_position, has_tabset]), (
        f"T-NEW-170 WIRE-2: `pop_out_tab` must record the home "
        f"coordinates so the FloatedTab can re-attach later. "
        f"Missing: home_node_id={has_node_id}, home_position={has_position}, "
        f"home_tabset={has_tabset}."
    )


def test_pop_out_tab_constructs_floated_tab():
    """The method body constructs a `FloatedTab` instance and
    shows it. This is the operator-visible behavior of the
    feature.
    """
    src = _method_source("NchantdOfficeTabSet", "pop_out_tab")
    has_floated_tab = (
        "FloatedTab(" in src
        or "FloatedTab (" in src
    )
    has_show = (
        re.search(r"""\.show\(\s*\)""", src) is not None
        or "show()" in src
    )
    assert has_floated_tab, (
        "T-NEW-170 WIRE-2: `pop_out_tab` must construct a "
        "`FloatedTab` instance (the T-NEW-170 WIRE-1 dialog). "
        "Without this call, the operator can't see the detached tab."
    )
    assert has_show, (
        "T-NEW-170 WIRE-2: `pop_out_tab` must show the FloatedTab "
        "(via `.show()`). Without this the dialog is constructed "
        "but invisible."
    )


def test_pop_out_tab_removes_tab_from_center_pane():
    """The method body removes the original tab from the center
    pane after the FloatedTab is constructed.

    After popping a tab out, the operator should NOT see the
    tab in the center tabset anymore -- it's in the dialog.
    Pre-fix the tab would stay visible AND be in the dialog
    (double-display).
    """
    src = _method_source("NchantdOfficeTabSet", "pop_out_tab")
    has_removal = bool(
        re.search(
            r"""(?:removeTab|remove_tab|close_tab)\s*\(""",
            src,
        )
    ) or ".removeTab(" in src
    assert has_removal, (
        "T-NEW-170 WIRE-2: `pop_out_tab` must remove the "
        "original tab from the center pane (e.g. via "
        "`app.view.panes['center'].removeTab(tab_index)`). "
        "Without this the tab is double-displayed (in both "
        "the tabset AND the FloatedTab dialog)."
    )


def test_pop_out_tab_constructs_standalone_window_for_document():
    """The method body constructs a `NchantdDocumentStandaloneWindow`
    instance and passes it to the FloatedTab.

    Per DECIDE-2 (ii), the standalone window is the
    full 2-pane shell that T-NEW-169 ships. `pop_out_tab`
    composes: document_widget -> NchantdDocumentStandaloneWindow
    -> FloatedTab.
    """
    src = _method_source("NchantdOfficeTabSet", "pop_out_tab")
    has_standalone = "NchantdDocumentStandaloneWindow" in src
    assert has_standalone, (
        "T-NEW-170 WIRE-2: `pop_out_tab` must construct a "
        "`NchantdDocumentStandaloneWindow` instance (T-NEW-169 "
        "WIRE-2's QMainWindow class). DECIDE-2 (ii) requires the "
        "full standalone 2-pane shell for pulled-out tabs."
    )


def test_pop_out_tab_return_type_is_floated_tab():
    """The method's return annotation is `FloatedTab` (or a
    compatible class name with leading/trailing whitespace).

    Returns the dialog so callers can keep a reference if
    they want to (e.g. for telemetry / list-management).
    """
    tree = ast.parse(_source())
    for node in tree.body:
        if not (isinstance(node, ast.ClassDef) and node.name == "NchantdOfficeTabSet"):
            continue
        for body_node in node.body:
            if (
                not isinstance(body_node, ast.FunctionDef)
                or body_node.name != "pop_out_tab"
            ):
                continue
            ret = body_node.returns
            ann = ast.unparse(ret) if ret is not None else ""
            assert "FloatedTab" in ann, (
                f"T-NEW-170 WIRE-2: `pop_out_tab` should annotate "
                f"its return type as `FloatedTab` so callers can "
                f"chain. Found: {ann!r}."
            )
            return
    raise AssertionError(
        "`NchantdOfficeTabSet.pop_out_tab` not found"
    )
