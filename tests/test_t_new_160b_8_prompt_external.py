"""T-NEW-160b card 8 — NchantdOfficePrompt location routing.

T-NEW-144b umbrella card 3.8 of 11. NchantdOfficePrompt at
``prompts.py:287`` hardcoded
``self.document.set_location("external")`` on every load.
Same shape as 3.1–3.7.
"""

import ast
from pathlib import Path

PROMPTS_PATH = (
    Path(__file__).parents[1] / "nchantdoffice/widgets/documents/atnrg/prompts.py"
)


def _function_source(name: str, class_name: str) -> str:
    tree = ast.parse(PROMPTS_PATH.read_text())
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
    source = _function_source("initView", "NchantdOfficePrompt")
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
        "NchantdOfficePrompt.initView must NOT hardcode "
        "set_location('external'). T-NEW-160b/8 drops it."
    )


def test_init_view_dispatch_intact():
    source = _function_source("initView", "NchantdOfficePrompt")
    assert (
        "location == 'external'" in source and "self.open_file" in source
    )


def test_pull_marker_removed():
    src_text = PROMPTS_PATH.read_text()
    tree = ast.parse(src_text)
    import re

    target = next(
        (
            n
            for n in tree.body
            if isinstance(n, ast.ClassDef) and n.name == "NchantdOfficePrompt"
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
