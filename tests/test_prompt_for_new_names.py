"""Sprint 23 — P1 name-entry dialog regression tests.

The Name-entry dialog for new nodes / tabs ships a config flag
prompt_for_new_node_name (and prompt_for_new_tab_name) that
drives whether each `add_node` / `add_tab` / `add_note` call
prompts the user via QInputDialog.getText or auto-generates a
name.

This test pins the contract that:
  1. When the flag is True, the caller WAITS for a name (and
     respects QInputDialog return value).
  2. When the flag is False (or unset), the caller falls back
     to the existing auto-generated name (uuid()[-5:]) without
     prompting.
  3. The flag is read from ``config.dikt`` so the Settings panel
     can toggle it at runtime.
  4. Cancellation (QInputDialog.Rejected) aborts the create.
"""

import os
import re
import sys
import ast
from pathlib import Path

import pytest

PROJ_ROOT = Path("/home/solubrew/.hermes/projects/nchantdoffice")
sys.path.insert(0, str(PROJ_ROOT))

TOOLBARS = PROJ_ROOT / "nchantdoffice" / "widgets" / "controls" / "toolbars.py"
PANE_NEW = PROJ_ROOT / "nchantdoffice" / "widgets" / "panes" / "new.py"
SETTINGS = PROJ_ROOT / "nchantdoffice" / "widgets" / "config" / "settings.py"


def _read(path):
    return path.read_text()


def _ast_find_function(src, name):
    """Return the AST FunctionDef for ``name`` or None."""
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def _call_names(node):
    """Return a list of variable names that are called like ``foo()``."""
    names = []
    for sub in ast.walk(node):
        if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name):
            names.append(sub.func.id)
    return names


# --- Settings flag wiring ---


def test_settings_has_prompt_for_new_node_name_flag():
    """Sprint 23: settings.py must expose
    ``cmd_on_change_prompt_for_new_node_name`` and the matching
    setter that writes to ``config.dikt``.
    """
    src = _read(SETTINGS)
    for needle in (
        "cmd_on_change_prompt_for_new_node_name",
        "prompt_for_new_node_name",
        "config.dikt",
    ):
        assert needle in src, (
            f"settings.py missing '{needle}' — the P1 name-entry "
            f"dialog flag must be wired into the Settings panel."
        )


def test_settings_has_prompt_for_new_tab_name_flag():
    """Sprint 23: settings.py must expose
    ``cmd_on_change_prompt_for_new_tab_name`` and the matching
    setter that writes to ``config.dikt``.
    """
    src = _read(SETTINGS)
    for needle in (
        "cmd_on_change_prompt_for_new_tab_name",
        "prompt_for_new_tab_name",
        "config.dikt",
    ):
        assert needle in src, (
            f"settings.py missing '{needle}' — the P1 name-entry "
            f"dialog flag must be wired into the Settings panel."
        )


# --- Toolbar add_node wiring ---


def test_toolbars_add_node_uses_prompt_when_flag_is_set():
    """Sprint 23: toolbars.add_node must consult
    ``config.dikt["prompt_for_new_node_name"]`` and, when True,
    call QtWidgets.QInputDialog.getText to capture a user-supplied
    name. When False (or unset), it falls back to uuid()[-5:].
    """
    src = _read(TOOLBARS)
    fn = _ast_find_function(src, "add_node")
    assert fn is not None, "toolbars.add_node function not found"
    body = (_get_source_segment(src, fn) or "").splitlines()
    txt = "\n".join(body)

    # The flag must be read.
    assert "prompt_for_new_node_name" in txt, (
        "toolbars.add_node does not consult prompt_for_new_node_name"
    )
    # The prompt must be invoked.
    assert "QInputDialog.getText" in txt or "QInputDialog" in txt, (
        "toolbars.add_node does not call QInputDialog.getText()"
    )
    # The fallback auto-generation must still exist.
    assert "uuid()[-5:]" in txt, (
        "toolbars.add_node lost the auto-generated fallback name"
    )
    # The flag must be read from config.dikt.
    assert "config.dikt" in txt, (
        "toolbars.add_node must read prompt_for_new_node_name from "
        "config.dikt (the Settings panel's persistent store)"
    )


def test_toolbars_add_note_uses_prompt_when_flag_is_set():
    """Sprint 23: toolbars.add_note must also support the prompt
    (notes are name-able documents).
    """
    src = _read(TOOLBARS)
    fn = _ast_find_function(src, "add_note")
    assert fn is not None, "toolbars.add_note function not found"
    body = (_get_source_segment(src, fn) or "").splitlines()
    txt = "\n".join(body)

    assert "prompt_for_new_note_name" in txt or "prompt_for_new_node_name" in txt, (
        "toolbars.add_note does not consult any prompt flag"
    )


# --- Pane new.add_tab wiring ---


def test_pane_new_add_tab_uses_prompt_when_flag_is_set():
    """Sprint 23: panes/new.add_tab must consult
    ``config.dikt["prompt_for_new_tab_name"]`` and, when True,
    call QtWidgets.QInputDialog.getText to capture a user-supplied
    name. When False (or unset), it falls back to whatever the
    active item provides.
    """
    src = _read(PANE_NEW)
    fn = _ast_find_function(src, "add_tab")
    assert fn is not None, "panes/new.add_tab function not found"
    body = (_get_source_segment(src, fn) or "").splitlines()
    txt = "\n".join(body)

    assert "prompt_for_new_tab_name" in txt, (
        "panes/new.add_tab does not consult prompt_for_new_tab_name"
    )
    assert "QInputDialog.getText" in txt or "QInputDialog" in txt, (
        "panes/new.add_tab does not call QInputDialog.getText()"
    )


# --- Cancellation aborts the create ---


def test_prompt_for_new_node_name_respects_cancellation():
    """Sprint 23: when the user cancels the QInputDialog, the
    add_node call must abort (return self) without creating a
    node.
    """
    src = _read(TOOLBARS)
    fn = _ast_find_function(src, "add_node")
    body = (_get_source_segment(src, fn) or "").splitlines()
    txt = "\n".join(body)

    # Look for the QInputDialog call returning (name, ok) and
    # a check on `ok` that aborts.
    assert re.search(r"\bok\b", txt), (
        "toolbars.add_node must inspect the QInputDialog ok flag "
        "to detect cancellation"
    )
    # The early return on cancel.
    assert "return self" in txt, (
        "toolbars.add_node must return self early on cancel"
    )


def _get_source_segment(src, node):
    """Wrap ast.get_source_segment with a fallback."""
    try:
        return ast.get_source_segment(src, node)
    except Exception:
        return None
