"""T-NEW-170 WIRE-4 -- right-click menu + toolbar 'detach tab' trigger.

The T-NEW-170 plan calls for two operator-visible ways to
fire ``pop_out_tab``:

1. Right-click on a tab -> context menu with 'Detach to
   window' item -> fire pop_out_tab at the right-clicked
   index.
2. Toolbar 'detach tab' button (per the card body) -> fire
   pop_out_tab at the currently selected tab.

This commit ships a small **inline trigger layer** on the
tabset itself: a ``_wire_pop_out_triggers`` helper that's
called from ``initView``. The helper is best-effort: in
an environment where the Qt primitives (QTabBar / QToolBar)
aren't available, the helper logs the absence and moves on.

LOCKED DESIGN (operator-approved 2026-08-19):
  DECIDE-1 (a) -- re-attach only on dialog close / app close.
  DECIDE-2 (ii) -- full standalone 2-pane shell.

Tests are AST-source structural.
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


def test_pop_out_trigger_helper_exists():
    """`_wire_pop_out_triggers` helper exists on
    `NchantdOfficeTabSet`.

    The helper wires the right-click menu + toolbar button.
    """
    try:
        _method_source(
            "NchantdOfficeTabSet", "_wire_pop_out_triggers"
        )
        return
    except AssertionError:
        raise AssertionError(
            "T-NEW-170 WIRE-4: "
            "`NchantdOfficeTabSet._wire_pop_out_triggers` "
            "method does not exist. The helper that wires "
            "the right-click menu + toolbar 'detach tab' "
            "button is the operator-visible trigger for "
            "pop_out_tab."
        )


def test_init_view_calls_wire_pop_out_triggers():
    """`initView` invokes `self._wire_pop_out_triggers()`."""
    src = _method_source("NchantdOfficeTabSet", "initView")
    has_call = "self._wire_pop_out_triggers" in src
    assert has_call, (
        "T-NEW-170 WIRE-4: `initView` must call "
        "`self._wire_pop_out_triggers()` so the operator "
        "triggers come up alongside the tabset UI."
    )


def test_wire_pop_out_triggers_calls_pop_out_tab():
    """The helper invokes `pop_out_tab` (T-NEW-170 WIRE-2)."""
    src = _method_source(
        "NchantdOfficeTabSet", "_wire_pop_out_triggers"
    )
    has_call = "pop_out_tab" in src
    assert has_call, (
        "T-NEW-170 WIRE-4: the wire helper must call "
        "`self.pop_out_tab(...)` so the operator triggers "
        "delegate to the T-NEW-170 WIRE-2 primitive."
    )


def test_wire_pop_out_triggers_includes_popup_menu_setup():
    """The helper sets up a right-click context menu on the
    tab bar via `setContextMenuPolicy` + customContextMenuRequested
    or builds a `QMenu`.
    """
    src = _method_source(
        "NchantdOfficeTabSet", "_wire_pop_out_triggers"
    )
    has_context_policy = (
        "setContextMenuPolicy" in src
        or "CustomContextMenu" in src
    )
    has_menu = "QMenu" in src
    ok = has_context_policy or has_menu
    assert ok, (
        "T-NEW-170 WIRE-4: the wire helper must set up "
        "the right-click context menu (via "
        "setContextMenuPolicy or a QMenu)."
    )


def test_wire_pop_out_triggers_handles_missing_qt_gracefully():
    """The helper is best-effort: top-level try/except so a
    stripped-down environment doesn't crash initView.
    """
    src = _method_source(
        "NchantdOfficeTabSet", "_wire_pop_out_triggers"
    )
    has_try = "try:" in src
    has_except = "except" in src
    assert has_try and has_except, (
        "T-NEW-170 WIRE-4: `_wire_pop_out_triggers` must "
        "be wrapped in try/except so missing-Qt primitives "
        "in a stripped-down environment don't crash initView."
    )


def test_no_node_change_hook_in_wire_helper():
    """The wire helper does NOT register any node-change /
    navigation hook that would auto-detach.

    DECIDE-1 (a): re-attach only on dialog close / app close.
    """
    src = _method_source(
        "NchantdOfficeTabSet", "_wire_pop_out_triggers"
    )
    forbidden = [
        "on_node_change",
        "on_active_node_changed",
        "_active_node_listener",
        "node_change_handler",
    ]
    actual = [n for n in forbidden if n in src]
    assert not actual, (
        f"T-NEW-170 WIRE-4 DECIDE-1 (a) pin: "
        f"_wire_pop_out_triggers must NOT have "
        f"node-change hooks. Found: {actual}."
    )
