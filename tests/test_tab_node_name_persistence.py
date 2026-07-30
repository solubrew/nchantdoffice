"""Sprint 21 — T-NEW-024 (live bug) regression: Tab Edit Pane
and Node Edit Pane must persist name changes to the DB.

User-stated contract (2026-07-29):
  Tab Edit Pane doesn't persist the new name — ``cmd_set_tab_name``
  updates the label but doesn't write back to the DB.
  Node Edit Pane doesn't persist the new name — same regression.

The fix:
  1. ``cmd_set_tab_name`` writes the new name to ``doc_tab.name_txt``
     (or ``app_tab.name_txt``) via
     ``store.update_record({"table": {"doc_tab": {"data": {"name_txt": ...}}}}, "tid_txt", tab.tid)``.
  2. ``cmd_set_node_name`` writes the new name to ``doc_tree_node``
     via the same path.
  3. Both methods also set ``is_changed = True`` on the model so
     the parent loop knows to flush.
"""

import ast
from pathlib import Path


def _read(rel):
    return (Path(__file__).resolve().parent.parent / rel).read_text()


def _flattened(src):
    import re

    return re.sub(r"\s+", " ", src).strip()


def test_cmd_set_tab_name_writes_to_db():
    """T-NEW-024 (live bug): cmd_set_tab_name must persist the
    new name to doc_tab.name_txt via store.update_record.
    """
    src = _read("nchantdoffice/widgets/panes/documents.py")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == (
            "NchantdOfficeTabEditPane"
        ):
            for child in node.body:
                if isinstance(child, ast.FunctionDef) and (
                    child.name == "cmd_set_tab_name"
                ):
                    body = ast.get_source_segment(src, child) or ""
                    flat = _flattened(body)
                    # Must call update_record on the store.
                    assert "update_record" in flat, (
                        "cmd_set_tab_name must call store.update_record "
                        "to persist the new name to the DB; "
                        f"body: {flat[:500]!r}"
                    )
                    # Must target the doc_tab (or app_tab) table
                    # with a name_txt column update.
                    assert "doc_tab" in flat or "app_tab" in flat, (
                        "cmd_set_tab_name must target doc_tab or "
                        "app_tab in the update_record call; "
                        f"body: {flat[:500]!r}"
                    )
                    assert "name_txt" in flat, (
                        "cmd_set_tab_name must update the name_txt "
                        "column; body: {flat[:500]!r}"
                    )
                    return
    raise AssertionError(
        "NchantdOfficeTabEditPane.cmd_set_tab_name not found"
    )


def test_cmd_set_node_name_writes_to_db():
    """T-NEW-024 (live bug): cmd_set_node_name must persist the
    new name to doc_tree_node via store.update_record.
    """
    src = _read("nchantdoffice/widgets/panes/documents.py")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == (
            "NchantdOfficeNodeEditPane"
        ):
            for child in node.body:
                if isinstance(child, ast.FunctionDef) and (
                    child.name == "cmd_set_node_name"
                ):
                    body = ast.get_source_segment(src, child) or ""
                    flat = _flattened(body)
                    # Must call update_record on the store.
                    assert "update_record" in flat, (
                        "cmd_set_node_name must call "
                        "store.update_record to persist the new "
                        f"name to the DB; body: {flat[:500]!r}"
                    )
                    # Must target doc_tree_node with a name column
                    # update.
                    assert "doc_tree_node" in flat, (
                        "cmd_set_node_name must target "
                        "doc_tree_node in the update_record call; "
                        f"body: {flat[:500]!r}"
                    )
                    assert "name_txt" in flat or "name" in flat, (
                        "cmd_set_node_name must update the name "
                        f"column; body: {{flat[:500]!r}}"
                    )
                    return
    raise AssertionError(
        "NchantdOfficeNodeEditPane.cmd_set_node_name not found"
    )
