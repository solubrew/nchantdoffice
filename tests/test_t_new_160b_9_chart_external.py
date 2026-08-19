"""T-NEW-160b card 9 — NchantdOfficeChart location routing.

T-NEW-144b umbrella card 3.9 of 11. NchantdOfficeChart at
``analytics.py:225`` hardcoded
``self.document.set_location("external")`` on every load.
Same shape as 3.1–3.8.

Important contrast: a Chart is THE prime example of a
``populate_data`` widget per the umbrella design language
(stored snapshots that change within the document's life —
a live chart streams data while the doc holds the snapshot
+ chart-type metadata). Once the location threading is in
place, the future ``populate_data`` seam will know exactly
where to hook the streaming-data dispatch.
"""

import ast
from pathlib import Path

ANALYTICS_PATH = (
    Path(__file__).parents[1] / "nchantdoffice/widgets/documents/analytics/analytics.py"
)


def _function_source(name: str, class_name: str) -> str:
    tree = ast.parse(ANALYTICS_PATH.read_text())
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
    source = _function_source("initView", "NchantdOfficeChart")
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
        "NchantdOfficeChart.initView must NOT hardcode "
        "set_location('external'). T-NEW-160b/9 drops it."
    )


def test_init_view_dispatch_intact():
    source = _function_source("initView", "NchantdOfficeChart")
    assert (
        "location == 'external'" in source and "self.open_file" in source
    )


def test_pull_marker_removed():
    src_text = ANALYTICS_PATH.read_text()
    tree = ast.parse(src_text)
    import re

    target = next(
        (
            n
            for n in tree.body
            if isinstance(n, ast.ClassDef) and n.name == "NchantdOfficeChart"
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
