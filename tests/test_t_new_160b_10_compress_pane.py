"""T-NEW-160b card 10 — NchantdCompressPane (special case).

T-NEW-144b umbrella card 3.10 of 11. Special case:
``NchantdCompressPane`` (filesystems.py:96) extends
``NchantdPane``, NOT ``NchantdOfficeDocument`` — it's a
utilities pane, not a document widget. The set_location
call here is a flag-only setter, not a real document
location contract.

The umbrella fix shape for cards 3.1–3.9 (drop hardcode,
keep the location-aware dispatch) doesn't apply here: there
is no live ``if location == 'external'`` dispatch (it's
commented out). The card removes the marker and the bare
set_location call so the Compress pane doesn't pretend to
be a document widget. The pane's "external" semantics are
preserved by the upstream caller when appropriate.
"""

import ast
from pathlib import Path

FILESYSTEMS_PATH = (
    Path(__file__).parents[1] / "nchantdoffice/widgets/documents/managers/filesystems.py"
)


def _function_source(name: str, class_name: str) -> str:
    tree = ast.parse(FILESYSTEMS_PATH.read_text())
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


def test_init_view_no_longer_hardcodes_external():
    source = _function_source("initView", "NchantdCompressPane")
    body_calls = []
    for sub in ast.walk(ast.parse(source)):
        if not isinstance(sub, ast.Call):
            continue
        func = sub.func
        if (
            isinstance(func, ast.Attribute)
            and isinstance(func.value, ast.Attribute)
            and func.value.attr == "document"
            and func.attr == "set_location"
        ):
            for arg in sub.args:
                if (
                    isinstance(arg, ast.Constant)
                    and isinstance(arg.value, str)
                    and arg.value == "external"
                ):
                    body_calls.append(sub)
    assert not body_calls, (
        "NchantdCompressPane.initView must NOT hardcode "
        "self.document.set_location('external'). T-NEW-160b/10 "
        "drops it (special case: this is a NchantdPane, not a "
        "document widget — the flag-only call doesn't belong)."
    )


def test_pull_marker_removed():
    src_text = FILESYSTEMS_PATH.read_text()
    tree = ast.parse(src_text)
    import re

    target = next(
        (
            n
            for n in tree.body
            if isinstance(n, ast.ClassDef) and n.name == "NchantdCompressPane"
        ),
        None,
    )
    assert target is not None
    src_lines = src_text.splitlines(keepends=True)
    class_lines = [
        ln
        for idx, ln in enumerate(src_lines, start=1)
        if target.lineno <= idx <= (target.end_lineno or idx)
    ]
    marker_lines = [
        ln.strip()
        for ln in class_lines
        if ln.lstrip().startswith("#")
        and re.search(
            r"#\s*PUSH[\s_-]*to[\s_-]*0\.0\.3.*force\s+external\s+until",
            ln,
            re.IGNORECASE,
        )
        and not ('"force external until"' in ln or "'force external until'" in ln)
    ]
    assert not marker_lines
