"""T-NEW-160b card 2 — NchantdOfficeForm location routing.

T-NEW-144b umbrella card 3.2 of 11. NchantdOfficeForm at
``forms.py:77`` hardcoded
``self.document.set_location("external")`` on every load,
identical shape to NchantdOfficeSketch (T-NEW-160b/1,
commit a1c5932). Force-external until ... hardcode blocks
the .pyof internal-blob load path.

Mirrors T-NEW-160 (Image), T-NEW-160a (Notebook), and
T-NEW-160b/1 (Sketch). The post-fix flow keeps the
location-aware ``if self.document.location == "external"``
dispatch — only the unconditional set_location is removed.

Tests are AST-source structural (mirroring the umbrella
pattern). ``forms.py`` imports PySide6 via nchantrs.
"""

import ast
from pathlib import Path


FORMS_PATH = (
    Path(__file__).parents[1] / "nchantdoffice/widgets/documents/media/forms.py"
)


def _function_source(name: str, class_name: str) -> str:
    tree = ast.parse(FORMS_PATH.read_text())
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
    """``NchantdOfficeForm.initView`` body must NOT call ``set_location(\"external\")``."""
    source = _function_source("initView", "NchantdOfficeForm")
    body_calls_set_location_external = []
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
                    body_calls_set_location_external.append(sub)
    assert not body_calls_set_location_external, (
        "NchantdOfficeForm.initView must NOT call "
        "self.document.set_location('external') — the hardcode "
        "forced every form doc to file-origin even when loaded "
        "from the DB. T-NEW-160b/2 drops it."
    )


def test_init_view_dispatch_intact():
    """The location-aware dispatch (``if location == external``) stays."""
    source = _function_source("initView", "NchantdOfficeForm")
    has_external_dispatch = (
        "location == 'external'" in source and "self.open_file" in source
    )
    assert has_external_dispatch, (
        "initView must keep the location-aware dispatch: "
        "`if self.document.location == 'external': "
        "self.open_file(...)`. Post-fix the location reads "
        "from the caller (not hardcoded)."
    )


def test_pull_marker_removed():
    """The literal ``# PUSH to 0.0.3 force external until`` marker is gone from NchantdOfficeForm.

    Scope is limited to the ``NchantdOfficeForm`` class body.
    Note: ``forms.py`` has 2 live hardcode sites — this card
    fixes the ``NchantdOfficeForm.initView`` (forms.py:77) site
    only. Card 3 (T-NEW-160b/3) handles the
    ``NchantdOfficeFormManager`` site (forms.py:415). Pinning
    is class-scoped so the tests can ship one widget per
    commit (umbrella rule: one commit per widget).
    """
    # Walk every ClassDef in forms.py and find the
    # NchantdOfficeForm class body. Check only those source
    # lines for the marker.
    src_text = FORMS_PATH.read_text()
    tree = ast.parse(src_text)
    import re

    # Find class body byte offsets
    target_class = None
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "NchantdOfficeForm":
            target_class = node
            break
    assert target_class is not None, (
        "NchantdOfficeForm class not found in forms.py"
    )

    src_lines = src_text.splitlines(keepends=True)
    # Note: ast line numbers are 1-indexed
    class_lines = [
        ln
        for idx, ln in enumerate(src_lines, start=1)
        if target_class.lineno <= idx <= (target_class.end_lineno or idx)
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
    assert not marker_lines, (
        f"NchantdOfficeForm still has the deferred-feature marker "
        f"# PUSH*-to-0.0.3 ... 'force external until' on these lines: "
        f"{marker_lines}. T-NEW-160b/2 removes it. "
        f"(Other classes in forms.py may still have similar markers — "
        f"they're handled by their own T-NEW-160b/* cards.)"
    )
