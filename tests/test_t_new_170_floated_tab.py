"""T-NEW-170 WIRE-1 \u2014 FloatedTab dialog class.

The T-NEW-170 plan calls for a new ``widgets/controls/floated_tab.py``
file with a ``FloatedTab`` ``QDialog`` subclass. The class hosts one
document widget that has been pulled out of the parent tabset so
the operator can move it to a second monitor.

LOCKED DESIGN (operator-approved 2026-08-19):

  DECIDE-1 (a) \u2014 re-attach only on dialog close or app close
  DECIDE-2 (ii) \u2014 full standalone 2-pane shell that
  reuses NchantdDocumentStandaloneWindow from T-NEW-169

This file ships ONLY the FloatedTab class. NchantdDocumentStandaloneWindow
(T-NEW-169) ships in a separate file \u2014 FloatedTab accepts it as a
parameter rather than instantiating, so T-NEW-169 can land in its own
commit without this file waiting. (Per the operator's "match velocity
to task size" rule: 11 commits on the T-NEW-170 path, smallest-first.)

Public API:

  FloatedTab(
      parent,                    # QWidget owner (the main app window)
      standalone_window,         # NchantdDocumentStandaloneWindow (T-NEW-169)
      document_widget,           # the pulled-out document widget (already detached)
      home_node_id,              # str/int \u2014 the node the tab belonged to
      home_position,             # int  \u2014 the position in the home tabset
      home_tabset,               # NchantdOfficeTabSet \u2014 where the tab returns to
  )

  float_tab = FloatedTab(...)
  float_tab.show()

  # When the dialog closes (operator X / File>Close), closeEvent fires
  # and calls ``home_tabset.re_attach_tab(self)`` to put the tab back
  # in its original position.

  # When the application quits, the operator-confirmed flow is:
  # QApplication.aboutToQuit signal \u2192 FloatedTab.capture_sibling_shutdown
  #   closes each dialog \u2192 closeEvent fires \u2192 re_attach.

Tests are AST-source structural (mirroring T-NEW-167..169).

NOTE on `_class_for_method`: floateTab is the only class in this file.
The test helpers narrow by explicit class name to avoid the
multi-initView / multi-initModel type race we hit elsewhere.
"""

import ast
from pathlib import Path


FLOATED_TAB_PATH = (
    Path(__file__).parents[1] / "nchantdoffice/widgets/controls/floated_tab.py"
)


def _file_exists() -> bool:
    return FLOATED_TAB_PATH.exists()


def _function_source(name: str, class_name: str) -> str:
    tree = ast.parse(FLOATED_TAB_PATH.read_text())
    for node in tree.body:
        if not (isinstance(node, ast.ClassDef) and node.name == class_name):
            continue
        for body_node in node.body:
            if (
                isinstance(body_node, ast.FunctionDef)
                and body_node.name == name
            ):
                return ast.unparse(body_node)
    raise AssertionError(f"{name} not found in {class_name}")


def test_file_exists():
    """``widgets/controls/floated_tab.py`` ships in this commit."""
    assert _file_exists(), (
        f"{FLOATED_TAB_PATH} does not exist. T-NEW-170 WIRE-1 "
        f"ships this file as the FloatedTab-dialog-class location."
    )


def test_class_floated_tab_exists():
    """``FloatedTab`` class is defined on the new file."""
    assert _file_exists(), "floated_tab.py not present"
    tree = ast.parse(FLOATED_TAB_PATH.read_text())
    classes = [n.name for n in tree.body if isinstance(n, ast.ClassDef)]
    assert "FloatedTab" in classes, (
        f"floated_tab.py must define a FloatedTab class (T-NEW-170 "
        f"WIRE-1). Found classes: {classes}."
    )


def test_floated_tab_subclasses_qdialog():
    """``FloatedTab`` subclasses ``QDialog`` (the locked design choice).

    QDialog is the Qt class for a top-level popup window with its own
    window chrome (icon / title bar / close / maximize). The dialog
    must survive being moved to a second monitor and back without
    losing state \u2014 QDialog is the right Qt primitive for that.
    """
    assert _file_exists()
    tree = ast.parse(FLOATED_TAB_PATH.read_text())
    found_qdialog = False
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        if node.name != "FloatedTab":
            continue
        for base in node.bases:
            base_src = ast.unparse(base)
            if "QDialog" in base_src:
                found_qdialog = True
                break
    assert found_qdialog, (
        "FloatedTab must subclass QDialog (T-NEW-170 LOCKED DESIGN: "
        "DECIDE-2 (ii)). QDialog is the Qt class for a top-level "
        "popup window that supports being moved to a second monitor."
    )


def test_constructor_signature_has_locked_params():
    """``FloatedTab.__init__`` accepts the locked signature: parent, standalone_window, document_widget, home_node_id, home_position, home_tabset."""
    source = _function_source("__init__", "FloatedTab")
    # Look for each locked parameter name in the function body / args
    required_params = [
        "standalone_window",
        "document_widget",
        "home_node_id",
        "home_position",
        "home_tabset",
    ]
    missing = [p for p in required_params if p not in source]
    assert not missing, (
        f"FloatedTab.__init__ must accept the locked signature "
        f"(parent, standalone_window, document_widget, home_node_id, "
        f"home_position, home_tabset). Missing params: {missing}. "
        f"Source: {source[:300]}"
    )


def test_constructor_stores_home_coordinates():
    """The constructor stores ``home_node_id``, ``home_position``, and ``home_tabset`` on the instance for re-attach."""
    source = _function_source("__init__", "FloatedTab")
    # Look for `self.home_<key> = <param>` assignments in the body
    expected_attrs = ["home_node_id", "home_position", "home_tabset"]
    missing = [a for a in expected_attrs if f"self.{a} =" not in source]
    assert not missing, (
        f"FloatedTab constructor must store home coordinates on "
        f"self for later re-attach. Missing self.<attr> assignments: "
        f"{missing}. Per the operator-approved DECIDE-1, re-attach "
        f"happens on dialog close (closeEvent) \u2014 the constructor "
        f"is the one place that captures these values."
    )


def test_closeevent_calls_re_attach_tab():
    """``FloatedTab.closeEvent`` triggers ``home_tabset.re_attach_tab(...)``.

    Per DECIDE-1 (a), re-attach happens on dialog close (and on app
    close via the same closeEvent). The implementation MUST call
    ``self.home_tabset.re_attach_tab(self)`` from closeEvent so
    closing the dialog puts the tab back in its home tabset at its
    home position.
    """
    source = _function_source("closeEvent", "FloatedTab")
    has_reattach_call = (
        "re_attach_tab" in source
        and "self.home_tabset" in source
    )
    assert has_reattach_call, (
        "FloatedTab.closeEvent must call "
        "self.home_tabset.re_attach_tab(self) per the operator-approved "
        "DECIDE-1 (a). Without this hook, closing the dialog leaves "
        "the tab orphaned (not in any tabset)."
    )


def test_show_method_unchanged_contract():
    """The class can show itself via the standard ``QDialog.show()`` \u2014 no shadow ``show()`` is needed."""
    # This is a sanity pin: there should be NO custom show() on FloatedTab
    # because the QDialog default is correct (centered on parent, restored
    # from ``Qt.WindowPosition`` etc). If a future implementer adds a
    # custom show(), this test fails and forces them to justify it.
    assert _file_exists()
    tree = ast.parse(FLOATED_TAB_PATH.read_text())
    for node in tree.body:
        if not (isinstance(node, ast.ClassDef) and node.name == "FloatedTab"):
            continue
        for body_node in node.body:
            if not isinstance(body_node, ast.FunctionDef):
                continue
            if body_node.name != "show":
                continue
            # Found a `def show` \u2014 only acceptable as a thin super().show() wrapper
            src = ast.unparse(body_node)
            # Looking for super().show(...)
            if "super().show" in src:
                # Acceptable: it defers to QDialog.show
                continue
            assert False, (
                f"FloatedTab.show() defined but not as a thin "
                f"super().show() wrapper: {src}. The QDialog default "
                f"show() is sufficient; if you need a custom show, "
                f"document why in the docstring."
            )


def test_closeevent_also_calls_super():
    """``FloatedTab.closeEvent`` calls ``super().closeEvent(event)`` so the dialog actually closes."""
    source = _function_source("closeEvent", "FloatedTab")
    has_super_call = "super().closeEvent" in source
    assert has_super_call, (
        "FloatedTab.closeEvent must call super().closeEvent(event) \u2014 "
        "without it the dialog's internal close never fires and the "
        "QDialog window doesn't actually close. Test the close hook "
        "AND the super-call (this card uses both)."
    )


def test_no_active_node_change_re_attach_hook():
    """T-NEW-170 LOCKED DESIGN (DECIDE-1 a): there is NO active-node-change re-attach hook.

    The re-attach fires ONLY on ``closeEvent`` (dialog close or app
    exit). Future implementers must NOT add a node-change hook that
    re-attaches when the operator navigates away from the home node.
    This test guards that absence.
    """
    # Search for any callable named on the active-node-change side
    # of the parent tabset \u2014 the operator-approved plan removed it.
    # Heuristic: no `go_to_previous_node`, no `cmd_delete_node`, and no
    # `_setup_node_change_hook` (or similar) on FloatedTab.
    assert _file_exists()
    tree = ast.parse(FLOATED_TAB_PATH.read_text())
    for node in tree.body:
        if not (isinstance(node, ast.ClassDef) and node.name == "FloatedTab"):
            continue
        method_names = [b.name for b in node.body if isinstance(b, ast.FunctionDef)]
    forbidden = [
        "on_node_change",
        "on_active_node_changed",
        "setup_node_change_hook",
        "node_change_handler",
        "_active_node_listener",
    ]
    accidental = [m for m in method_names if m in forbidden]
    assert not accidental, (
        f"FloatedTab must NOT have an active-node-change re-attach hook "
        f"(DECIDE-1 a: re-attach only on dialog close / app close). "
        f"Accidental methods found: {accidental}. If you intentionally "
        f"want this, that's a new operator-approved DECIDE \u2014 update "
        f"the card and re-decide."
    )
