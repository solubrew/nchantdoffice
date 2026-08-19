"""T-NEW-155 -- Script Ctrl+D shortcut for date-insert.

The 2026-08-17 testing report: 'Add the toolbar action and
shortcut requested in the latest operator report; no Ctrl+D
registration currently exists.'

Pre-fix: ``NchantdOfficeScript`` has working ``cmd_add_date``
that inserts today's date in ISO format (scripts.py:262-269),
and the toolbar wires it via the ``insert_date`` slot
(scripts.py:709). The shortcut binding was never wired —
operators had to click the toolbar button or remember the
mouse path.

Post-fix: a per-widget Ctrl+D QShortcut binds to the widget
itself, using the canonical Qt focus-based pattern. When the
script widget has focus (e.g. the operator clicked into the
editor), pressing Ctrl+D triggers cmd_add_date. Other widgets
without the shortcut are unaffected. The shortcut is created
in ``initWidget`` (lifecycle-bound) so creation/destruction
follows the widget instance, not the class.

Pattern mirror:

  class NchantdOfficeScript:
      def initWidget(self):
          super().initWidget()
          self._register_shortcut("Ctrl+D", self.cmd_add_date)
          return self

The per-widget registry uses a tiny helper
``_register_shortcut`` that:
  1. Creates a QShortcut with QKeySequence(keyseq) context=
     WidgetWithChildrenShortcut (active when the widget or any
     of its child widgets has focus).
  2. Wires activated.connect(handler).
  3. Stores the QShortcut on ``self`` (so it isn't GC'd).

The helper is reusable for future shortcut bindings (the
operator pattern is per-widget, not global).

Tests are AST-source structural (mirroring T-NEW-133 /
T-NEW-152 / T-NEW-156 / T-NEW-157). scripts.py imports
PySide6 via nchantrs.libraries.pyqt.
"""

import ast
from pathlib import Path

SCRIPTS_PATH = (
    Path(__file__).parents[1] / "nchantdoffice/widgets/documents/media/scripts.py"
)


def _function_source(name: str, class_name: str) -> str:
    tree = ast.parse(SCRIPTS_PATH.read_text())
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


def test_register_shortcut_helper_exists():
    """``NchantdOfficeScript._register_shortcut`` helper exists."""
    tree = ast.parse(SCRIPTS_PATH.read_text())
    found = False
    for node in tree.body:
        if not (isinstance(node, ast.ClassDef) and node.name == "NchantdOfficeScript"):
            continue
        for body_node in node.body:
            if isinstance(body_node, ast.FunctionDef) and body_node.name in (
                "_register_shortcut",
                "register_shortcut",
            ):
                found = True
                break
    assert found, (
        "NchantdOfficeScript._register_shortcut (or "
        "register_shortcut) helper must exist — the per-widget "
        "shortcut registry helper for T-NEW-155."
    )


def test_init_widget_calls_register_shortcut_for_ctrl_d():
    """``NchantdOfficeScript.initWidget`` wires Ctrl+D via the registry."""
    source = _function_source("initWidget", "NchantdOfficeScript")
    has_ctrl_d = (
        "Ctrl+D" in source
        and "cmd_add_date" in source
        and ("register_shortcut" in source or "_register_shortcut" in source)
    )
    assert has_ctrl_d, (
        "NchantdOfficeScript.initWidget must call the "
        "shortcut registry helper to wire Ctrl+D -> "
        "cmd_add_date. T-NEW-155 fix."
    )


def test_register_shortcut_uses_qshortcut():
    """``_register_shortcut`` body instantiates ``QShortcut`` (the Qt class)."""
    tree = ast.parse(SCRIPTS_PATH.read_text())
    found_qshortcut = False
    for node in tree.body:
        if not (isinstance(node, ast.ClassDef) and node.name == "NchantdOfficeScript"):
            continue
        for body_node in node.body:
            if isinstance(body_node, ast.FunctionDef) and body_node.name in (
                "_register_shortcut",
                "register_shortcut",
            ):
                # Walk the body for QShortcut(
                for sub in ast.walk(body_node):
                    if not isinstance(sub, ast.Call):
                        continue
                    func = sub.func
                    if (
                        isinstance(func, ast.Attribute)
                        and func.attr == "QShortcut"
                    ):
                        found_qshortcut = True
                        break
    assert found_qshortcut, (
        "_register_shortcut must create a QShortcut instance "
        "(per-widget focus-based shortcut). T-NEW-155 uses "
        "the Qt canonical pattern."
    )


def test_qkeysequence_used_for_ctrl_d():
    """The shortcut binding parses the key sequence via ``QKeySequence``."""
    tree = ast.parse(SCRIPTS_PATH.read_text())
    found_qkeyseq = False
    for node in tree.body:
        if not (isinstance(node, ast.ClassDef) and node.name == "NchantdOfficeScript"):
            continue
        for body_node in node.body:
            if isinstance(body_node, ast.FunctionDef) and body_node.name in (
                "_register_shortcut",
                "register_shortcut",
            ):
                for sub in ast.walk(body_node):
                    if not isinstance(sub, ast.Call):
                        continue
                    func = sub.func
                    if (
                        isinstance(func, ast.Attribute)
                        and func.attr == "QKeySequence"
                    ):
                        found_qkeyseq = True
                        break
    assert found_qkeyseq, (
        "_register_shortcut must parse the key sequence via "
        "QKeySequence — the Qt canonical pattern for shortcut "
        "binding. T-NEW-155 uses QShortcut + QKeySequence."
    )
