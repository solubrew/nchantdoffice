"""T-NEW-171 SURVEY-1 step 5 -- sortChildren instrumentation.

The T-NEW-171 umbrella SURVEY-1 covers 5 hot add-tab paths.
SURVEY-1 commit 9f6b158 instrumented 4 of the 5; the 5th is
``sortChildren`` (the treeview cascade). This commit wires
the T-NEW-171 markers at the two natural call sites:

1. ``NchantdOfficeNodeEditPane.cmd_sort_children`` -- the
   toolbar / menu entry point that the operator clicks.
2. ``NchantdOfficeNodeEditPane._sort_subtree`` -- the
   recursive cascade itself.
"""

import ast
from pathlib import Path


PANES_DOCS_PATH = (
    Path(__file__).parents[1]
    / "nchantdoffice/widgets/panes/documents.py"
)


def _source() -> str:
    return PANES_DOCS_PATH.read_text()


def _function_source(name: str) -> str:
    tree = ast.parse(_source())
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        for body_node in node.body:
            if (
                isinstance(body_node, ast.FunctionDef)
                and body_node.name == name
            ):
                return ast.unparse(body_node)
    raise AssertionError(f"{name!r} not found")


def test_cmd_sort_children_t171_marker_present():
    src = _function_source("cmd_sort_children")
    assert "time.monotonic()" in src and "T-NEW-171" in src, (
        "T-NEW-171 SURVEY-1 step 5: cmd_sort_children must "
        "include the T-NEW-171 marker + time.monotonic()."
    )


def test_sort_subtree_t171_marker_present():
    src = _function_source("_sort_subtree")
    assert "time.monotonic()" in src and "T-NEW-171" in src, (
        "T-NEW-171 SURVEY-1 step 5: _sort_subtree must "
        "include the T-NEW-171 marker + time.monotonic()."
    )


def test_no_import_time_regression():
    src = _source()
    assert "import time" in src, (
        "T-NEW-171 SURVEY-1 step 5: panes/documents.py must "
        "import the stdlib time module."
    )
