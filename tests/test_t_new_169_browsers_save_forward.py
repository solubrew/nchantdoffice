"""T-NEW-169 — NchantdOfficeWebViewer.save forwards to canonical nchantrs impl.

The 2026-08-18 sweep found a class of bugs that aren't tagged
with any PUSH-to-0.0.3 marker: **subclass shadows of canonical
implementations**. ``NchantdOfficeWebViewer.save()`` at
``browsers.py:1636`` is a textbook example:

  - Empty docstring (`""""""`)
  - Body just ``return self``

The canonical real impl exists in nchantrs at
``nchantrs/widgets/browsers/browsers.py:503``
(``NchantdWebViewer.save``), which persists viewer state via
``_to_dict()`` and emits a model event.

The desktop override currently has NO live caller inside the
class body (line 1688 ``self.save()`` is commented out as
dead code) — which is the reason this slipped through all the
previous Sprint-20 sweeps: the override is invisible. However,
the override is a TRAP for any future code that uncomments
line 1688 or that subclasses ``NchantdOfficeWebViewer`` —
they'd inherit a no-op instead of the canonical impl.

The fix mirrors the T-NEW-167/T-NEW-168 pattern: the override
becomes a thin pass-through to ``super().save()``. Cost is
one extra line. Benefit: any future caller gets the real
behaviour instead of the silent no-op. The override is the
smallest possible "forward-and-document" change, matching the
Sprint-20 canonical-impl contracts in
``NchantdOfficeWebBrowser.save`` (line 1172, already correct)
and in ``NchantdImage.save``.

Tests are AST-source structural — mirrors the pattern from
T-NEW-167 / T-NEW-168. ``browsers.py`` imports PySide6 via
the nchantrs chain.
"""

import ast
from pathlib import Path


BROWSERS_PATH = (
    Path(__file__).parents[1] / "nchantdoffice/widgets/documents/atnrg/browsers.py"
)


def _function_sources(name: str):
    """Return source for EVERY method with this name (not just the first).

    The browsers.py file has TWO ``save()`` methods — the rich
    one at line 1172 (``NchantdOfficeWebBrowser``) is already
    correctly wired (``super().save()`` + ``file_path`` setup);
    the empty stub at line 1636 (``NchantdOfficeWebViewer``) is
    the bug this card fixes. ``_function_source`` finds only
    the first match — but T-NEW-169 needs to target the stub
    by class membership.
    """
    tree = ast.parse(BROWSERS_PATH.read_text())
    found = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            found.append((node, ast.unparse(node)))
    return found


def _class_for_lineno(lineno: int) -> str | None:
    """Return the enclosing class name for the given source-line number."""
    tree = ast.parse(BROWSERS_PATH.read_text())
    enclosing = None
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            # ClassDef covers lines from class header through last stmt.
            if node.lineno <= lineno and (node.end_lineno or 0) >= lineno:
                if enclosing is None or node.lineno > enclosing.lineno:
                    enclosing = node
    return enclosing.name if enclosing else None


def test_nchantd_office_web_viewer_save_forwards_to_super():
    """The ``NchantdOfficeWebViewer.save()`` override forwards to ``super().save()``.

    Pre-fix body was the empty ``return self`` shape. The fix
    turns the override into a thin pass-through that delegates
    to the canonical ``NchantdWebViewer.save()`` (nchantrs).

    Targeting: ``NchantdOfficeWebViewer.save`` at browsers.py:1636.
    The OTHER ``save`` at browsers.py:1172 (in
    ``NchantdOfficeWebBrowser``) is correctly wired and is not
    the target of T-NEW-169 — we pin the FIX to the WebViewer
    class specifically to avoid false negatives from the working
    sibling.
    """
    targets = [
        (node, src) for node, src in _function_sources("save")
        if _class_for_lineno(node.lineno) == "NchantdOfficeWebViewer"
    ]
    assert targets, (
        "Expected exactly one save() in NchantdOfficeWebViewer; "
        f"found {len(targets)}."
    )
    node, source = targets[0]
    body_calls = []
    for sub in ast.walk(node):
        if not isinstance(sub, ast.Call):
            continue
        func = sub.func
        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Call):
            inner = func.value.func
            if (
                isinstance(inner, ast.Name)
                and inner.id == "super"
                and func.attr == "save"
            ):
                body_calls.append(sub)
    assert body_calls, (
        f"NchantdOfficeWebViewer.save (line {node.lineno}) must "
        f"call super().save() — the canonical nchantrs impl that "
        f"persists viewer state via _to_dict(). Pre-fix the "
        f"override was the empty 'return self' shape and "
        f"focusOutEvent-triggered auto-save was a silent no-op."
    )


def test_nchantd_office_web_browser_save_still_wired():
    """The OTHER ``save`` in NchantdOfficeWebBrowser stays correctly wired.

    Regression guard for T-NEW-169: T-NEW-169 only rewires the
    NchantdOfficeWebViewer.save override; we don't touch
    NchantdOfficeWebBrowser.save (line 1172, already correct).
    """
    targets = [
        (node, src) for node, src in _function_sources("save")
        if _class_for_lineno(node.lineno) == "NchantdOfficeWebBrowser"
    ]
    assert targets, (
        "NchantdOfficeWebBrowser.save must still exist (line 1172 "
        "or so). T-NEW-169 only touches NchantdOfficeWebViewer.save; "
        "if you removed the sibling, that's a separate cleanup."
    )
    node, source = targets[0]
    # The browser version should already have super().save() — pre-T-NEW-169.
    body_has_super = False
    for sub in ast.walk(node):
        if isinstance(sub, ast.Call):
            func = sub.func
            if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Call):
                inner = func.value.func
                if (
                    isinstance(inner, ast.Name)
                    and inner.id == "super"
                    and func.attr == "save"
                ):
                    body_has_super = True
    assert body_has_super, (
        f"NchantdOfficeWebBrowser.save (line {node.lineno}) "
        f"already had super().save() before T-NEW-169 — keep it. "
        f"If this fires, someone accidentally touched the wrong "
        f"override."
    )


def test_set_url_path_still_references_optional_save():
    """``set_url_path`` may uncomment the ``self.save()`` line in future.

    Line 1688 has ``# self.save()`` as a commented-out call.
    T-NEW-169 doesn't change that line (it's left as-is for the
    future implementer) but the test guards the related
    contract: the WebViewer.save() override is now a real
    forward to super(), so any future uncomment-and-call gets
    the canonical impl.
    """
    src = BROWSERS_PATH.read_text()
    tree = ast.parse(src)
    # Verify the override save (line 1636) has super().save()
    # and the set_url_path body (line 1662) keeps the commented
    # ``self.save()`` reference at line 1688 untouched.
    found_super_in_save = False
    found_commented_save_ref = False
    for cls_node in tree.body:
        if not isinstance(cls_node, ast.ClassDef):
            continue
        if cls_node.name != "NchantdOfficeWebViewer":
            continue
        for node in cls_node.body:
            if not isinstance(node, ast.FunctionDef):
                continue
            if node.name == "save":
                for sub in ast.walk(node):
                    if isinstance(sub, ast.Call):
                        func = sub.func
                        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Call):
                            inner = func.value.func
                            if (
                                isinstance(inner, ast.Name)
                                and inner.id == "super"
                                and func.attr == "save"
                            ):
                                found_super_in_save = True
            elif node.name == "set_url_path":
                # Look for a line containing the literal ``# self.save()``
                # within the function body (not in a comment we wrote
                # for the test file). Use raw source for this.
                start_line = node.lineno
                end_line = node.end_lineno or node.lineno
                src_lines = src.splitlines()
                for i in range(start_line - 1, min(end_line, len(src_lines))):
                    if "# self.save()" in src_lines[i]:
                        found_commented_save_ref = True
                        break
    assert found_super_in_save, (
        "NchantdOfficeWebViewer.save must call super().save() "
        "(T-NEW-169 fix)."
    )
    assert found_commented_save_ref, (
        "set_url_path should keep the commented '# self.save()' "
        "reference at line 1688 — T-NEW-169 doesn't change that "
        "line; future implementers will uncomment it to make the "
        "forward actually fire."
    )