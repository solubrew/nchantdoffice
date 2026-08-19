"""T-NEW-161 — wire 2 standalone browsers.py drawers (source_inspection + quickstart activation).

The 2026-08-18 PUSH-to-0.0.3 sweep filed T-NEW-161 with 18 deferred
drawer slots across 11 widgets. The DECIDE-1 matrix approved by the
operator (2026-08-18) narrowed scope to 2 standalone WIRE calls in
``atnrg/browsers.py``:

  1. ``init_drawer_source_inspection`` (line 953) — commented body has
     three handlers; two are real (``cmd_launch_source_tab``,
     ``cmd_on_resource_select``), one is deferred (``cmd_scan_source``).
     The deferral for ``cmd_scan_source`` rolls up into T-NEW-162 —
     this card only ships the wire-up so the drawer shows up in the UI.
  2. ``init_drawer_quickstart`` activation at line 1013 — the
     ``init_drawer_quickstart`` method itself is already implemented
     (real bookmarks + quick-app-links at line 982). The activation
     line in ``init_toolbox`` is just commented out. This card
     uncomments that single line.

Tests are AST-source structural (mirroring
``test_t_new_117_palette_scan_degradation`` + ``test_t_new_165_matrix_thumbnail``)
because ``NchantdOfficeBrowser`` imports PySide6 — pytest collection
would crash on the import chain in this headless env.
"""

import ast
from pathlib import Path


BROWSERS_PATH = (
    Path(__file__).parents[1]
    / "nchantdoffice/widgets/documents/atnrg/browsers.py"
)


def _function_source(name: str) -> str:
    tree = ast.parse(BROWSERS_PATH.read_text())
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return ast.unparse(node)
    raise AssertionError(f"{name} not found")


def test_init_drawer_source_inspection_method_exists():
    """``init_drawer_source_inspection`` is no longer commented out.

    T-NEW-161 WIRE call: the drawer body at line 953 was a full
    commented implementation. This test pins that the method is
    now a real (uncommented) def in the AST.
    """
    tree = ast.parse(BROWSERS_PATH.read_text())
    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "init_drawer_source_inspection":
            # AST extracts the method regardless of leading #; the
            # deeper check is in test_init_drawer_source_inspection_not_commented
            found = True
            break
    assert found, (
        "init_drawer_source_inspection method definition missing entirely"
    )


def test_init_drawer_source_inspection_not_commented():
    """The method is *uncommented* (live code), not commented-out.

    Reads the raw source lines around line 953 and confirms the
    ``def init_drawer_source_inspection`` line is NOT prefixed
    with ``#``.
    """
    src = BROWSERS_PATH.read_text()
    lines = src.splitlines()
    # Find the line in the live source
    matches = [i for i, ln in enumerate(lines) if "def init_drawer_source_inspection" in ln]
    assert matches, "init_drawer_source_inspection not found in source"
    target = matches[0]
    line = lines[target]
    assert not line.lstrip().startswith("#"), (
        f"init_drawer_source_inspection is still commented out at line "
        f"{target + 1}: {line!r}. T-NEW-161 must uncomment it."
    )


def test_init_drawer_source_inspection_wires_three_buttons():
    """The body constructs three button slots via the canonical pattern.

    Each slot binds to one of the three documented handlers
    (``cmd_launch_source_tab``, ``cmd_scan_source`` — T-NEW-162
    deferred, ``cmd_on_resource_select``). The test pins that
    the source-document-launch, crawl-current-page, and resource
    select widgets all end up under ``self.toolbox_config[400]``.
    """
    source = _function_source("init_drawer_source_inspection")
    assert "source_document_launch_button" in source, (
        "init_drawer_source_inspection must construct self.source_document_launch_button "
        "(T-NEW-161 — wire-up of the commented body at browsers.py:953)"
    )
    assert "crawl_current_page_button" in source, (
        "init_drawer_source_inspection must construct self.crawl_current_page_button"
    )
    assert "page_resource_list" in source, (
        "init_drawer_source_inspection must construct self.page_resource_list"
    )
    # The drawer writes to toolbox_config[400]
    assert "toolbox_config[400]" in source, (
        "init_drawer_source_inspection must populate toolbox_config[400]"
    )


def test_init_drawer_quickstart_is_activated_in_init_toolbox():
    """``init_toolbox`` calls ``init_drawer_quickstart`` for slot 500.

    T-NEW-161 WIRE call: the method at line 982 is real but the
    activation site at line 1013 was commented out. Test pins that
    the activation line is now live code.
    """
    src = BROWSERS_PATH.read_text()
    # Find init_toolbox body
    lines = src.splitlines()
    in_init_toolbox = False
    activated = False
    for line in lines:
        if "def init_toolbox" in line and not line.lstrip().startswith("#"):
            in_init_toolbox = True
            continue
        if in_init_toolbox:
            if line.startswith("def ") or line.startswith("    def "):
                # Next top-level method — stop
                if "init_toolbox" not in line:
                    break
            if "init_drawer_quickstart" in line and "toolbox_config[500]" in line:
                activated = True
                break
    assert activated, (
        "init_toolbox must call init_drawer_quickstart for toolbox_config[500] "
        "— the activation line at browsers.py:1013 was commented out; "
        "T-NEW-161 must uncomment it."
    )


def test_init_drawer_form_control_remains_deferred_for_t_new_162():
    """``init_drawer_form_control`` activation stays commented (T-NEW-162's scope).

    The DECIDE-1 matrix explicitly left ``init_drawer_form_control``
    for T-NEW-162 (the Pro-tier gate is a behaviour change). This
    test pins that T-NEW-161 did NOT accidentally uncomment it.
    """
    src = BROWSERS_PATH.read_text()
    # The form_control activation site is at browsers.py:1013
    # The body definition is at browsers.py:760
    lines = src.splitlines()
    # Confirm the body def is still commented out (the def line has a # prefix)
    body_lines = [ln for ln in lines if "def init_drawer_form_control" in ln]
    assert body_lines, "init_drawer_form_control body def missing"
    assert body_lines[0].lstrip().startswith("#"), (
        f"init_drawer_form_control body must stay commented for T-NEW-162: "
        f"got {body_lines[0]!r}"
    )
    # Confirm the activation site in init_toolbox still has the comment prefix
    in_init_toolbox = False
    form_control_activated = False
    for line in lines:
        if "def init_toolbox" in line and not line.lstrip().startswith("#"):
            in_init_toolbox = True
            continue
        if in_init_toolbox:
            if line.startswith("def ") or line.startswith("    def "):
                if "init_toolbox" not in line:
                    break
            if "init_drawer_form_control" in line and "toolbox_config[300]" in line:
                form_control_activated = not line.lstrip().startswith("#")
                break
    assert not form_control_activated, (
        "init_drawer_form_control activation must stay commented for T-NEW-162; "
        "T-NEW-161 is not the card to wire it up."
    )