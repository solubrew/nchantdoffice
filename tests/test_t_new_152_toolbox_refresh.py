"""T-NEW-152 -- Refresh ToolBox after node deletion.

``cmd_delete_node`` at ``panes/documents.py:127-159`` refreshes
the tree (calls ``tree.view.go_to_previous_node()`` and
``tree.refresh()``) but does NOT refresh the document ToolBox
(``center_pane.toolbox``). After a delete, the ToolBox still
shows the deleted node's content until something else triggers
a refresh.

Pre-fix flow:

  self.app.model.delete_node(node)
  tree = self.app.view.panes["left"].tree
  tree.view.go_to_previous_node()
  tree.refresh()
  # ToolBox still shows the deleted node's contents
  return self

Post-fix:

  self.app.model.delete_node(node)
  tree = self.app.view.panes["left"].tree
  tree.view.go_to_previous_node()
  tree.refresh()
  # Refresh the document ToolBox so the open-deleted-node
  # state clears immediately.
  if hasattr(self.app, "view") and hasattr(self.app.view, "panes"):
      center = self.app.view.panes.get("center")
      if center is not None and hasattr(center, "toolbox"):
          center.toolbox.refresh()
  return self

Tests are AST-source structural (mirroring T-NEW-167 / T-NEW-168).
"""

import ast
from pathlib import Path


DOCUMENTS_PATH = (
    Path(__file__).parents[1] / "nchantdoffice/widgets/panes/documents.py"
)


def _function_source(name: str, class_name: str) -> str:
    tree = ast.parse(DOCUMENTS_PATH.read_text())
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


def test_cmd_delete_node_refreshes_tree_first():
    """``cmd_delete_node`` body still calls ``tree.refresh()`` (regression guard)."""
    source = _function_source("cmd_delete_node", "NchantdOfficeNodeEditPane")
    # ast.unparse canonicalizes quotes
    has_tree_refresh = "tree.refresh()" in source
    assert has_tree_refresh, (
        "cmd_delete_node must still call tree.refresh() — "
        "T-NEW-152 only adds ToolBox refresh; the tree "
        "refresh path is preserved."
    )


def test_cmd_delete_node_refreshes_toolbox_after():
    """``cmd_delete_node`` also refreshes the center-pane ToolBox.

    Pre-fix body skipped this step, leaving the ToolBox
    pointing at the deleted node's contents.
    """
    source = _function_source("cmd_delete_node", "NchantdOfficeNodeEditPane")
    has_toolbox_refresh = (
        "toolbox.refresh" in source
        and "panes" in source
        and "'center'" in source
    )
    assert has_toolbox_refresh, (
        "cmd_delete_node must call "
        "self.app.view.panes['center'].toolbox.refresh() after "
        "the tree refresh — that's the T-NEW-152 fix. "
        "Pre-fix the ToolBox still showed the deleted node's "
        "contents after refresh."
    )


def test_pull_marker_for_toolbox_refresh():
    """The T-NEW-152 mention remains in the docstring as historical reference."""
    source = _function_source("cmd_delete_node", "NchantdOfficeNodeEditPane")
    has_t_new_152 = "T-NEW-152" in source
    assert has_t_new_152, (
        "cmd_delete_node docstring should reference T-NEW-152 "
        "as the umbrella card for the ToolBox refresh fix."
    )
