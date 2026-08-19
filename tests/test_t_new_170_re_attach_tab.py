"""T-NEW-170 WIRE-3 -- re_attach_tab on NchantdOfficeTabSet.

The T-NEW-170 plan requires a ``re_attach_tab(floated_tab)``
method on ``NchantdOfficeTabSet``. The FloatedTab class
(T-NEW-170 WIRE-1) calls this in its ``closeEvent`` -- once
the operator closes the dialog, the document widget is
re-parented into the center tabset at its original
home_position.

LOCKED DESIGN (operator-approved 2026-08-19):
  DECIDE-1 (a) -- re-attach only on dialog close / app
  close. ``re_attach_tab`` is the canonical receiver for
  the dialog-close path.

Tests are AST-source structural. The tabset module imports
Qt at module level -- same as T-NEW-167..170 pattern; AST
+ string patterns only.
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


def test_re_attach_tab_method_exists():
    """`NchantdOfficeTabSet.re_attach_tab(...)` is a method on the
    class. The FloatedTab dialog calls this in its ``closeEvent``.

    Without this method the dialog has no way to put the tab
    back in its home tabset; closing the dialog would orphan
    the document widget.
    """
    try:
        _method_source("NchantdOfficeTabSet", "re_attach_tab")
        return
    except AssertionError:
        raise AssertionError(
            "T-NEW-170 WIRE-3: `NchantdOfficeTabSet.re_attach_tab` "
            "method does not exist. The FloatedTab dialog's "
            "closeEvent (T-NEW-170 WIRE-1) calls "
            "`self.home_tabset.re_attach_tab(self)` -- without "
            "this method the tab is orphaned on dialog close."
        )


def test_re_attach_tab_accepts_floated_tab_argument():
    """The method signature accepts a `floated_tab` argument.

    The FloatedTab stores `home_node_id`, `home_position`,
    `home_tabset`, AND `document_widget` so the receiver can
    read those values and re-attach the document widget at
    the right position.
    """
    src = _method_source("NchantdOfficeTabSet", "re_attach_tab")
    has_arg = "floated_tab" in src
    assert has_arg, (
        "T-NEW-170 WIRE-3: `re_attach_tab(floated_tab)` must accept "
        "a `floated_tab` argument -- the FloatedTab instance "
        "carries the home coordinates + the document_widget "
        "that needs to be re-parented."
    )


def test_re_attach_tab_reads_floated_tab_home_position():
    """The method body reads `floated_tab.home_position` (or
    the equivalent dict-style) and uses it to re-insert the
    tab at the same spot in the tabset.
    """
    src = _method_source("NchantdOfficeTabSet", "re_attach_tab")
    patterns = [
        r"floated_tab\.home_position",
        r"floated_tab\[.{0,5}home_position.{0,5}\]",
        r"home_position",
    ]
    ok = any(re.search(p, src) for p in patterns)
    assert ok, (
        "T-NEW-170 WIRE-3: `re_attach_tab` must read "
        "`floated_tab.home_position` to know where in the "
        "tabset to re-insert."
    )


def test_re_attach_tab_reinserts_widget_at_position():
    """The method body calls `insertTab(home_position, widget)`
    (or equivalent) to put the document widget back in the
    center pane at its recorded position.
    """
    src = _method_source("NchantdOfficeTabSet", "re_attach_tab")
    has_insert = "insertTab(" in src
    assert has_insert, (
        "T-NEW-170 WIRE-3: `re_attach_tab` must call "
        "`center.insertTab(home_position, document_widget)` "
        "so the detached document widget is re-inserted at "
        "its original position. Without this the tab lands "
        "at the wrong position OR not at all."
    )


def test_re_attach_tab_reads_document_widget_from_floated_tab():
    """The method body reads `floated_tab.document_widget` (or
    equivalent) and uses it as the QTabWidget page to insert.
    """
    src = _method_source("NchantdOfficeTabSet", "re_attach_tab")
    has_widget = (
        "floated_tab.document_widget" in src
        or "floated_tab['document_widget']" in src
        or "document_widget" in src
    )
    assert has_widget, (
        "T-NEW-170 WIRE-3: `re_attach_tab` must read "
        "`floated_tab.document_widget` and pass it to "
        "`insertTab()`."
    )


def test_re_attach_tab_swallows_qt_errors_best_effort():
    """The method body has error handling so a Qt re-insert
    failure (e.g. re-attach after the model is gone) does
    not crash the app. Errors are logged + swallowed; the
    document widget is best-effort re-parented.

    Without the try/except, a single re-attach failure
    during dialog close would propagate as an unhandled
    exception in the dialog's closeEvent -- which Qt
    treats as a Qt-level crash.
    """
    src = _method_source("NchantdOfficeTabSet", "re_attach_tab")
    has_try = "try:" in src
    has_except = "except" in src
    assert has_try and has_except, (
        "T-NEW-170 WIRE-3: `re_attach_tab` must be wrapped "
        "in try/except so a Qt re-insert failure doesn't "
        "crash the dialog's closeEvent path. Best-effort "
        "design -- the operator can recover via restart."
    )
