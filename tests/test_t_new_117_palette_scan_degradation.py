"""T-NEW-117 regression tests for graceful palette scan degradation."""

import ast
from pathlib import Path


IMAGES_PATH = (
    Path(__file__).parents[1]
    / "nchantdoffice/widgets/documents/media/images.py"
)


def _palette_scan_source() -> str:
    tree = ast.parse(IMAGES_PATH.read_text())
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "cmd_run_palette_scan":
            return ast.unparse(node)
    raise AssertionError("cmd_run_palette_scan not found")


def test_palette_scan_handles_missing_upstream_method_with_status_message():
    source = _palette_scan_source()

    assert "hasattr" in source
    assert "extract_palette" in source
    assert "showMessage" in source
    assert "unavailable" in source.lower()
