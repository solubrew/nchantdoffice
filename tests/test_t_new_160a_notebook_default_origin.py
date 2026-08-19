"""T-NEW-160a — NchantdOfficeNotebook default-origin threading.

The T-NEW-144b umbrella replaces ``set_location("external")``
hardcodes across widget classes with proper location-driven
routing. Card 2 (T-NEW-160a) implements this for
``NchantdOfficeNotebook``.

Notebook is a SPECIAL case: the ``save()`` method
(notebooks.py:1207) is ALREADY correct — it writes external
``.ipynb` files AND handles the to_dict/both save modes for
internal-blob persistence. The T-NEW-160a scope is therefore
limited to the two location hardcodes that block the
default-origin threading:

  - initView (line 237) — hardcodes "external" even when the
    notebook was opened from the DB blob (internal).
  - open_file (line 1172) — hardcodes "external" on every call,
    including the no-arg init-lifecycle call.

Post-fix:

  def initView:
      # leave location as-is (None default; respects caller-set
      # location when the notebook loads from .pyof).
      ...

  def open_file:
      ...
      if file is not None:
          self.document.set_location("external")
      self.populate_document()

Mirrors the T-NEW-160 routing fix for NchantdOfficeImage,
but without the save-seam work (Notebook save was already
correct — see commit history at the parent save()).

Tests are AST-source structural (mirror T-NEW-160 pattern).
"""

import ast
from pathlib import Path


NOTEBOOKS_PATH = (
    Path(__file__).parents[1] / "nchantdoffice/widgets/documents/workbooks/notebooks.py"
)


def _function_source(name: str) -> str:
    tree = ast.parse(NOTEBOOKS_PATH.read_text())
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return ast.unparse(node)
    raise AssertionError(f"{name} not found")


def _class_for_method(name: str) -> str | None:
    """Return the enclosing class name for the named method."""
    tree = ast.parse(NOTEBOOKS_PATH.read_text())
    found = None
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            for body_node in node.body:
                if (
                    isinstance(body_node, ast.FunctionDef)
                    and body_node.name == name
                ):
                    found = node.name
    return found


def test_init_view_no_longer_hardcodes_external():
    """``NchantdOfficeNotebook.initView`` body must NOT call ``set_location("external")``.

    Pre-fix body at notebooks.py:237 hardcoded ``external`` for
    every notebook doc, blocking the internal-blob load path.
    """
    assert _class_for_method("initView") == "NchantdOfficeNotebook", (
        "initView must be defined on NchantdOfficeNotebook (T-NEW-160a "
        "target class)."
    )
    source = _function_source("initView")
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
        "NchantdOfficeNotebook.initView body must NOT call "
        "self.document.set_location('external') — the hardcode "
        "blocked the .pyof internal-blob load path. T-NEW-160a "
        "drops it; the doc location threads through open_file "
        "/ populate_data instead."
    )


def test_open_file_guards_set_location_with_file_check():
    """``open_file(file)`` sets ``external`` only when file is not None.

    Pre-fix body at notebooks.py:1172 unconditionally hardcoded
    ``external``. Post-fix: only fire the hint when the user
    passes a real disk path.
    """
    source = _function_source("open_file")
    src_text = NOTEBOOKS_PATH.read_text()
    tree = ast.parse(source)
    guarded = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        cond = ast.unparse(node.test)
        if (
            "file" in cond
            and (
                "is not None" in cond
                or cond.strip().endswith("file")
                or cond.strip().endswith("file is not None")
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
    assert guarded, (
        "open_file must guard the set_location('external') hint "
        "with `if file is not None:` so a None file doesn't "
        "overwrite an internal-blob location."
    )


def test_save_is_unchanged():
    """``save()`` is already correct — leave the existing impl alone.

    The Notebook save flow already handles external (.ipynb
    write) and internal (to_dict / both save_mode) cases
    correctly (notebooks.py:1207). T-NEW-160a is ROUTING-ONLY:
    no save-seam changes.
    """
    source = _function_source("save")
    # Sanity check: save() must still call super().save() (the
    # parent contract from NchantdOfficeDocument.save at
    # documents.py:1203). No regression in the save flow.
    has_super_call = False
    for sub in ast.walk(ast.parse(source)):
        if isinstance(sub, ast.Call):
            func = sub.func
            if (
                isinstance(func, ast.Attribute)
                and isinstance(func.value, ast.Call)
            ):
                inner = func.value.func
                if (
                    isinstance(inner, ast.Name)
                    and inner.id == "super"
                    and func.attr == "save"
                ):
                    has_super_call = True
    assert has_super_call, (
        "save() must still call super().save() — that's the parent "
        "doc_media / app_media_content write-back. T-NEW-160a is "
        "routing-only; no save flow changes."
    )


def test_pull_marker_removed():
    """The literal ``# PUSH to 0.0.3 force external until`` marker is gone.

    The marker lived at the now-fixed hardcode site (notebooks.py:236).
    """
    src_text = NOTEBOOKS_PATH.read_text()
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
        # Exclude prose mentions (T-NEW-160a docstring references
        # the marker in quotes, not as a live marker).
        and not ('"force external until"' in ln or "'force external until'" in ln)
    ]
    assert not marker_lines, (
        f"notebooks.py still has the deferred-feature marker "
        f"# PUSH*-to-0.0.3 ... 'force external until' on these lines: "
        f"{marker_lines}. T-NEW-160a removes the marker."
    )
