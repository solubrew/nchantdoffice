"""T-NEW-160b card 12 — NchantdOfficeMatrix + NchantdOfficeCellBorderFormats (already correct).

T-NEW-144b umbrella card 3.12 of 11. Final card of the
umbrella. Re-survey of ``matricies.py:171`` and ``:1860``.

  :171 (NchantdOfficeCellBorderFormats): the set_location
  call is COMMENTED OUT. This is a non-document utility
  pane (sets cell border styling); the location contract
  doesn't apply. The commented marker + dispatch are
  artifacts of an earlier umbrella sweep that turned out
  not to be a real bug here. Pin test guards against
  un-commenting.

  :1860 (NchantdOfficeMatrix.open_file): the set_location
  call is GUARDED by 'if not file: return self' early-return.
  Mirrors the T-NEW-160 (Image.open_file) shape: the hint
  fires only when the caller has a real disk path. No bug
  here.

The umbrella audit flagged both as candidates, but neither
is the umbrella pattern. This card ships no source patch
(the audit cleared them); only the survey-acknowledgment
test file pins the contracts as already correct.

Closes the T-NEW-160b umbrella sweep. All 12 cards shipped
(11 widget fixes + 1 survey acknowledgment, plus 2 cards
that concluded the source was already correct: 3.11
NchantdOfficeFileSystem and this 3.12).
"""

import ast
from pathlib import Path

MATRICIES_PATH = (
    Path(__file__).parents[1] / "nchantdoffice/widgets/documents/workbooks/matricies.py"
)


def _function_source(name: str, class_name: str) -> str:
    tree = ast.parse(MATRICIES_PATH.read_text())
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


def test_cell_border_formats_init_view_set_location_stays_commented():
    """``NchantdOfficeCellBorderFormats.initView`` keeps ``set_location`` as a comment.

    The 171 site is a non-document utility pane (cell border
    formatting). The location contract doesn't apply; the
    commented-out set_location call and dispatch are
    intentional dead code (special case, like
    NchantdCompressPane — card 3.10).

    Pin: the live source must NOT contain an UNCOMMENTED
    ``self.document.set_location("external")`` call in this
    class body. The COMMENTS are allowed (historical
    reference).
    """
    src_text = MATRICIES_PATH.read_text()
    tree = ast.parse(src_text)
    target = next(
        (
            n
            for n in tree.body
            if isinstance(n, ast.ClassDef)
            and n.name == "NchantdOfficeCellBorderFormats"
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
    # Find any LIVE (uncommented) call: a line starting with
    # 4+ spaces (indented body), containing
    # `self.document.set_location(`, that does NOT start
    # with `#`.
    live_calls = [
        ln.rstrip()
        for ln in class_lines
        if (ln.startswith("    ") or ln.startswith("\t"))
        and "self.document.set_location(" in ln
        and not ln.lstrip().startswith("#")
    ]
    assert not live_calls, (
        f"NchantdOfficeCellBorderFormats has an uncommented "
        f"self.document.set_location(...) call: {live_calls}. "
        f"This is a non-document utility pane; the live "
        f"set_location call doesn't belong here. T-NEW-160b/12 "
        f"survey confirms this is a deliberate special case "
        f"(commented, not removed). If you intentionally "
        f"want a live call, that's a separate card."
    )


def test_nchantd_office_matrix_open_file_is_guarded():
    """``NchantdOfficeMatrix.open_file`` only fires the ``set_location(\"external\")`` hint when ``file is not None``.

    Mirrors the T-NEW-160 (Image.open_file) shape and the
    Card 3.11 (FileSystem) fix pattern: the hint fires only
    when the caller has a real disk path.
    """
    source = _function_source("open_file", "NchantdOfficeMatrix")
    tree = ast.parse(source)
    guarded = False
    # The guard is the early-return `if not file: return self`
    # OR `if file is None: ...` — either pattern keeps the
    # hint from firing on no-arg init-lifecycle.
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        cond = ast.unparse(node.test)
        # Look for any guard referencing 'file' (truthy / not None /
        # None → fallback)
        if (
            ("file" in cond)
            and (
                "is None" in cond
                or "not file" in cond
                or "not file" in cond.replace("(", "")
            )
        ):
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
    # Alternative: the actual flow has an `if not file: return self`
    # early-return BEFORE the set_location call. Detect that the
    # set_location call only appears AFTER a `return self` guard.
    has_early_return_guard = (
        "if not file" in source
        and "return self" in source
        and source.index("if not file") < source.index("self.document.set_location('external')")
    )
    assert guarded or has_early_return_guard, (
        "NchantdOfficeMatrix.open_file must guard "
        "set_location('external') either with `if file is not "
        "None:` or via early-return `if not file: return self`. "
        "The post-T-NEW-144b file-nav widget correctly threads "
        "the external hint only when the caller has a real disk "
        "path."
    )


def test_no_force_external_marker_in_matricies():
    """No ``# PUSH to 0.0.3 force external until`` marker remains in matricies.py.

    Umbrella-audit criterion: the marker text. This card
    found 0 live markers at filing time. The marker at
    :171 is the Cell-Border-Formats pane and is part of
    the historical commented-out block (special case).
    The pin catches any future marker re-introduction
    (live, in any class body).
    """
    src_text = MATRICIES_PATH.read_text()
    import re

    # Iterate ALL class bodies in matricies.py. For each,
    # find any LIVE (uncommented) marker line.
    tree = ast.parse(src_text)
    src_lines = src_text.splitlines(keepends=True)
    live_markers = []
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        for idx, ln in enumerate(src_lines, start=1):
            if not (node.lineno <= idx <= (node.end_lineno or idx)):
                continue
            ln_clean = ln.lstrip()
            if ln_clean.startswith("#"):
                continue  # commented out
            if not re.search(
                r"#\s*PUSH[\s_-]*to[\s_-]*0\.0\.3.*force\s+external\s+until",
                ln,
                re.IGNORECASE,
            ):
                continue
            # Exclude prose mentions of the marker (in
            # docstrings / test files).
            if '"force external until"' in ln or "'force external until'" in ln:
                continue
            live_markers.append((node.name, idx, ln.rstrip()))

    assert not live_markers, (
        f"matricies.py has a LIVE '# PUSH to 0.0.3 ... "
        f"force external until' marker on lines {live_markers}. "
        f"Card 3.12 survey confirms all set_location sites in "
        f"this file are either commented-out (171) or properly "
        f"guarded (1860). If this fires, someone re-introduced "
        f"a marker; investigate the umbrella audit."
    )
