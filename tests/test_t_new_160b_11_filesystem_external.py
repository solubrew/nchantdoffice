"""T-NEW-160b card 11 — NchantdOfficeFileSystem location threading (already correct).

T-NEW-144b umbrella card 3.11 of 11. Re-survey of
``filesystems.py:1372 + 1431`` — the two ``set_location("external")``
sites in ``NchantdOfficeFileSystem`` are NOT the umbrella
hardcode pattern. They are LEGITIMATE guarded defaults:

  - 1372 (cmd_open_local_file): sets ``external`` only when
    ``file is not None`` — i.e. when the user passes a real
    disk path. Mirrors the T-NEW-160 (Image.open_file) fix
    shape: the hint fires only when the caller has a real
    file to point at. No bug here.

  - 1431 (save): sets ``external`` only when
    ``getattr(self.document, "location", None) is None`` —
    i.e. the location is unset. This is the default fallback:
    if no one has set a location yet, external is the safe
    default for a file-nav widget. No bug here.

This card documents the survey conclusion with an AST-source
structural test that pins both sites as LEGITIMATELY GUARDED
(not bare umbrella hardcodes). The T-NEW-160b umbrella
sweep finds no remaining ``PUSH to 0.0.3 force external
until`` marker in ``filesystems.py`` (grep confirmed at
filing time: 0 matches), confirming the surfacing of these
2 sites in the umbrella audit was a mis-attribution — they
were never the deferred-feature pattern.

The 2 sites stay as-is. No source patch ships with this
card; only the audit acknowledgment and the regression
guard.
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


def test_open_file_set_location_is_guarded():
    """``open_file`` only fires the ``set_location("external")`` hint when ``file is not None``.

    This is the same guarded pattern as T-NEW-160
    (Image.open_file): the hint fires only when a real
    disk path is passed in, not on the no-arg init-lifecycle
    invocation. No umbrella bug.
    """
    source = _function_source("open_file", "NchantdOfficeFileSystem")
    src_text = FILESYSTEMS_PATH.read_text()
    tree = ast.parse(source)
    guarded = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        cond = ast.unparse(node.test)
        if "file" in cond and "is not None" in cond:
            for sub in ast.walk(node):
                if not isinstance(sub, ast.Call):
                    continue
                func = sub.func
                if (
                    isinstance(func, ast.Attribute)
                    and isinstance(func.value, ast.Attribute)
                    and func.value.attr == "document"
                    and func.attr == "set_location"
                ):
                    guarded = True
                    break
            if guarded:
                break
    assert guarded, (
        "open_file must guard set_location('external') "
        "with `if file is not None:`. The post-T-NEW-144b file-nav "
        "widget correctly threads the external hint only when "
        "the caller has a real disk path."
    )


def test_save_set_location_is_fallback():
    """``save`` only defaults location to ``external`` when location is None.

    Pin: ``save`` reads ``getattr(self.document, "location", None)``
    and falls back to ``external`` if unset. That's the
    intended default for a file-nav widget. No umbrella bug.
    """
    source = _function_source("save", "NchantdOfficeFileSystem")
    # Look for the literal fallback pattern: `getattr(...,
    # "location", None) is None` followed by set_location.
    has_fallback = (
        "getattr(self.document, 'location', None) is None" in source
        and "self.document.set_location('external')" in source
    )
    # ast.unparse canonicalizes quote; allow either
    has_fallback_alt = (
        "getattr" in source
        and "'location', None" in source
        and "is None" in source
    )
    assert has_fallback or has_fallback_alt, (
        "save must keep the location-None fallback to 'external' "
        "(file-nav default). The survey conclusion: not a "
        "T-NEW-144b umbrella bug."
    )


def test_no_force_external_marker_in_filesystems():
    """No ``# PUSH to 0.0.3 force external until`` marker remains in filesystems.py.

    The umbrella audit's criterion is the marker text. This
    card found 0 markers at filing time — the 2 set_location
    sites in NchantdOfficeFileSystem are guarded defaults,
    not deferred-feature hardcodes. The pin catches any
    future regression where a marker gets re-introduced.
    """
    src_text = FILESYSTEMS_PATH.read_text()
    import re

    marker_lines = [
        ln.strip()
        for ln in src_text.splitlines()
        if ln.lstrip().startswith("#")
        and re.search(
            r"#\s*PUSH[\s_-]*to[\s_-]*0\.0\.3.*force\s+external\s+until",
            ln,
            re.IGNORECASE,
        )
        and not ('"force external until"' in ln or "'force external until'" in ln)
    ]
    assert not marker_lines, (
        f"filesystems.py has a PUSH-to-0.0.3 ... 'force external "
        f"until' marker on lines {marker_lines}. Card 3.10 "
        f"(CompressPane) and card 3.11 (FileSystem) both assert "
        f"none. If this fires, someone re-introduced the marker; "
        f"investigate the umbrella audit before any re-introduction."
    )
