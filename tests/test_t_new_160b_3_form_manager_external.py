"""T-NEW-160b card 3 — NchantdOfficeFormManager location routing.

T-NEW-144b umbrella card 3.3 of 11. NchantdOfficeFormManager
at ``forms.py:415`` (the document-manager wrapper class, not
the document class itself — see T-NEW-160b/2 at forms.py:77
for the sibling). Same umbrella hardcode fix shape, applied
to the manager class.

NchantdOfficeFormManager extends NchantdOfficeDocumentManager
(not NchantdOfficeDocument) so it's a special case: the
``set_location`` call here serves as the manager-side flag
that mirrors the document's location. The post-fix shape is
the same — drop the hardcode, let location thread through.

The dispatch (if ``location == 'external'``: open_file) stays
intact — same pattern as Sketch/Form/etc.
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
    """``NchantdOfficeFormManager.initView`` body must NOT call ``set_location(\"external\")``."""
    source = _function_source("initView", "NchantdOfficeFormManager")
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
        "NchantdOfficeFormManager.initView must NOT call "
        "self.document.set_location('external') — the umbrella "
        "hardcode blocks the .pyof internal-blob load. "
        "T-NEW-160b/3 drops it."
    )


def test_init_view_dispatch_intact():
    """The location-aware dispatch stays."""
    source = _function_source("initView", "NchantdOfficeFormManager")
    has_external_dispatch = (
        "location == 'external'" in source and "self.open_file" in source
    )
    assert has_external_dispatch, (
        "NchantdOfficeFormManager.initView must keep the "
        "location-aware dispatch."
    )


def test_pull_marker_removed():
    """The marker is gone from NchantdOfficeFormManager class body."""
    src_text = FORMS_PATH.read_text()
    tree = ast.parse(src_text)
    import re

    target = next(
        (
            n
            for n in tree.body
            if isinstance(n, ast.ClassDef) and n.name == "NchantdOfficeFormManager"
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
    assert not marker_lines, (
        f"NchantdOfficeFormManager still has the marker: {marker_lines}. "
        f"T-NEW-160b/3 removes it."
    )
