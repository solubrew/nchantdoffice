"""Sprint 18 — T-NEW-005 item 3 UI: app-instance registry browse dialog.

Per user direction (2026-07-29): the primary instance holds a
``app_instance`` registry of secondary DB files (one SQLite per
app instance). The data path is wired via
``model.get_app_instances()`` (Sprint 17); the user-facing UI
dialog was the missing piece.

This test pins:
  1. ``cmd_browse_app_instances`` exists on the toolbox.
  2. When the model returns rows, the handler routes them to a
     UI selector (QInputDialog.getItem is the canonical choice
     already used in scripts.py for selection prompts) so the
     user can pick a secondary instance to switch into.
  3. The selected row's ``path`` is fed back into
     ``_open_pyof_instance`` so the user can switch.
"""

import ast
import re
from pathlib import Path


def _toolboxes_source():
    root = Path(__file__).resolve().parent.parent
    return (root / "nchantdoffice/widgets/controls/toolboxes.py").read_text()


def _find_function_source(src, fn_name):
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == fn_name:
            return ast.get_source_segment(src, node) or ""
    return ""


def _flattened(src):
    return re.sub(r"\s+", " ", src).strip()


def test_cmd_browse_app_instances_exists_on_toolbox():
    """T-NEW-005 (item 3) UI: the toolbox must expose
    ``cmd_browse_app_instances`` so the user can open the
    primary-instance registry browser from the toolbar.
    """
    src = _toolboxes_source()
    tree = ast.parse(src)
    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "cmd_browse_app_instances":
            found = True
            break
    assert found, (
        "toolboxes.py must expose cmd_browse_app_instances for the "
        "primary-instance registry browser."
    )


def test_cmd_browse_app_instances_routes_to_ui_selector():
    """T-NEW-005 (item 3) UI: when the model returns rows, the
    handler must surface them through a UI selector so the user
    can pick one. Per user direction (2026-07-29), all
    NchantdDialogs live in ``nchantrs.dialogs``; the canonical
    selector is ``nchantrs.dialogs.selectors.NchantdSelectionDialog``.
    """
    src = _toolboxes_source()
    fn_src = _find_function_source(src, "cmd_browse_app_instances")
    flat = _flattened(fn_src)

    assert "get_app_instances" in flat, (
        f"cmd_browse_app_instances must consult "
        f"model.get_app_instances; body: {flat[:400]!r}"
    )
    # The canonical selection path: NchantdSelectionDialog
    # (which lives in nchantrs.dialogs.selectors per the project
    # convention). The handler may also fall back to a hand-rolled
    # QDialog, but the primary path is the shared selector.
    has_selector = "NchantdSelectionDialog" in flat
    has_qinputdialog = "QInputDialog" in flat and "getItem" in flat
    has_qdialog = "QDialog" in flat and ("show" in flat or "exec_" in flat)
    assert has_selector or has_qinputdialog or has_qdialog, (
        f"cmd_browse_app_instances must surface the rows via "
        f"a UI selector (NchantdSelectionDialog, "
        f"QInputDialog.getItem, or a QDialog). "
        f"Got: {flat[:600]!r}"
    )


def test_cmd_browse_app_instances_callback_switches_into_instance():
    """T-NEW-005 (item 3) UI: the selection handler must route
    the picked row's ``path`` back through ``_open_pyof_instance``
    so the user actually switches into the secondary instance.
    """
    src = _toolboxes_source()
    fn_src = _find_function_source(src, "cmd_browse_app_instances")
    flat = _flattened(fn_src)

    assert "_open_pyof_instance" in flat, (
        f"cmd_browse_app_instances must route the picked row "
        f"through _open_pyof_instance so the user actually "
        f"switches into the selected instance. Got: {flat[:600]!r}"
    )


def test_app_instances_table_schema_has_path_column():
    """T-NEW-005 (item 3) UI: the ``app_instance`` table must
    carry a path-like column so the browse dialog can route the
    selected row back to ``_open_pyof_instance``.

    Per the actual schema in
    ``nchantrs/models/_data_/applicationmodels.yaml`` line ~825
    the column is named ``instance_path_txt`` (not ``path``).
    """
    candidates = [
        Path("/home/solubrew/.hermes/projects/nchantrs")
        / "nchantrs/models/_data_/applicationmodels.yaml",
    ]
    found_column = False
    found_table = False
    for cand in candidates:
        if not cand.exists():
            continue
        text = cand.read_text()
        if "app_instance" in text:
            found_table = True
            lines = text.splitlines()
            for i, line in enumerate(lines):
                if "'app_instance'" in line or "\"app_instance\"" in line:
                    # Look at the next ~15 lines for the columns
                    # block.
                    nearby = "\n".join(lines[i : i + 15])
                    if (
                        "instance_path_txt" in nearby
                        or "application_path_txt" in nearby
                    ):
                        found_column = True
                        break
        if found_column:
            break
    assert found_table, (
        "app_instance table schema must exist in "
        "nchantrs/_data_/*.yaml"
    )
    assert found_column, (
        "app_instance table must carry an instance_path_txt or "
        "application_path_txt column so the browse dialog can "
        "route the selected row back to _open_pyof_instance."
    )


def test_nchantrs_selection_dialog_exists_in_dialogs_package():
    """T-NEW-005 (item 3) UI: per user direction, all Nchantd
    Dialogs live in ``nchantrs.dialogs``. The selection dialog
    must be importable from ``nchantrs.dialogs.selectors``.
    """
    from nchantrs.dialogs.selectors import NchantdSelectionDialog

    assert NchantdSelectionDialog is not None
