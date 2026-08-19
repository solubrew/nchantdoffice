"""T-NEW-160b card 4 — NchantdOfficeContact location routing.

T-NEW-144b umbrella card 3.4 of 11. NchantdOfficeContact at
``contacts.py:88`` hardcoded
``self.document.set_location("external")`` on every load.

Same shape as cards 3.1 (Sketch), 3.2 (Form), 3.3
(FormManager) — drop the umbrella hardcode, keep the
location-aware dispatch intact.

Note: contacts.py has 2 live hardcode sites — this card
fixes the ``NchantdOfficeContact.initView`` (contacts.py:88)
site only. Card 5 (T-NEW-160b/5) handles the sibling
``NchantdOfficeRolodex.initView`` (contacts.py:239) site.
Pinning is class-scoped so tests can ship one widget per
commit.
"""

import ast
from pathlib import Path


CONTACTS_PATH = (
    Path(__file__).parents[1] / "nchantdoffice/widgets/documents/atnrg/contacts.py"
)


def _function_source(name: str, class_name: str) -> str:
    tree = ast.parse(CONTACTS_PATH.read_text())
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
    """``NchantdOfficeContact.initView`` body must NOT call ``set_location(\"external\")``."""
    source = _function_source("initView", "NchantdOfficeContact")
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
        "NchantdOfficeContact.initView must NOT call "
        "self.document.set_location('external') — the umbrella "
        "hardcode blocks the .pyof internal-blob load. "
        "T-NEW-160b/4 drops it."
    )


def test_init_view_dispatch_intact():
    """The location-aware dispatch stays intact."""
    source = _function_source("initView", "NchantdOfficeContact")
    has_external_dispatch = (
        "location == 'external'" in source and "self.open_file" in source
    )
    assert has_external_dispatch, (
        "NchantdOfficeContact.initView must keep the location-aware "
        "dispatch: `if self.document.location == 'external': "
        "self.open_file(...)`."
    )


def test_pull_marker_removed():
    """The marker is gone from NchantdOfficeContact class body specifically."""
    src_text = CONTACTS_PATH.read_text()
    tree = ast.parse(src_text)
    import re

    target = next(
        (
            n
            for n in tree.body
            if isinstance(n, ast.ClassDef) and n.name == "NchantdOfficeContact"
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
        f"NchantdOfficeContact still has the marker: {marker_lines}."
    )
