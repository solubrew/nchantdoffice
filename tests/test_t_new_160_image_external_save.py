"""T-NEW-160 — NchantdOfficeImage location routing.

The T-NEW-144b umbrella replaces ``set_location("external")``
hardcodes across 13 widget classes with proper
location-driven routing. Card 1 (T-NEW-160) implements this
for ``NchantdOfficeImage``.

Pre-fix state at ``images.py:784 / 1306`` (and the commented
branch at lines 786-797):

  def initView:
      # PUSH to 0.0.3 force external until
      self.document.set_location("external")   # ALWAYS external

  def open_file:
      ...
      self.document.set_location("external")   # ALWAYS external

The hardcode forces every image doc to file-origin even when
the document was loaded from the DB (internal blob). It blocks
the T-NEW-144b umbrella from threading location through
populate/save correctly.

Post-fix:

  def initView:
      # leave location as-is (None default or caller-set)
      ...
      self.layout.addWidget(self.image)

  def open_file:
      ...
      if file is not None:
          self.document.set_location("external")
      self.populate_document()

The save-external-seam (writing the image bytes back to disk
on external save) is a follow-up card — it requires upstream
``NchantdImage.pixmap()`` access that this card does NOT
introduce. The routing fix here is the prerequisite: once
location threads through, the save-seam card will know
exactly where to hook.

Tests are AST-source structural (mirroring T-NEW-117 / T-NEW-148 /
T-NEW-159 / T-NEW-167 / T-NEW-168) because ``images.py``
imports PySide6 via the nchantrs chain.
"""

import ast
from pathlib import Path


IMAGES_PATH = (
    Path(__file__).parents[1] / "nchantdoffice/widgets/documents/media/images.py"
)


def _function_source(name: str) -> str:
    tree = ast.parse(IMAGES_PATH.read_text())
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return ast.unparse(node)
    raise AssertionError(f"{name} not found")


def _class_for_method(name: str) -> str | None:
    """Return the enclosing class name for the named method.

    The file has many classes that define ``initView``. We want
    the LATEST match (last class defined wins, which matches
    the source order — top-level classes are utility panels,
    the document class is closer to the bottom).
    """
    tree = ast.parse(IMAGES_PATH.read_text())
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
    """``NchantdOfficeImage.initView`` body must NOT call ``set_location("external")``.

    Pre-fix body at images.py:784 hardcoded ``external`` for
    every doc. Post-fix leaves location as-is (None default
    or whatever was set previously by open_file / populate_data).
    """
    assert _class_for_method("initView") == "NchantdOfficeImage", (
        "initView must be defined on NchantdOfficeImage (T-NEW-160 "
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
        "NchantdOfficeImage.initView body must NOT call "
        "self.document.set_location('external') — that hardcode "
        "forced every image doc to file-origin even when loaded "
        "from the DB. T-NEW-160 drops the hardcode; the doc "
        "location threads through open_file / populate_data "
        "instead."
    )


def test_open_file_guards_set_location_with_file_check():
    """``open_file(file)`` sets ``external`` only when file is not None.

    Pre-fix body at images.py:1306 unconditionally hardcoded
    ``external``. Post-fix: only fire the hint when the user
    passes a real disk path. Lets ``populate_data`` (internal
    flow from open_local_document / .pyof) preserve whatever
    location the caller set.
    """
    source = _function_source("open_file")
    src_text = IMAGES_PATH.read_text()
    # Inspect the open_file function body for the canonical
    # ``if file is not None:`` (or ``if file:``) guard that wraps
    # the set_location call. Walk every if-statement in the body
    # and check whether the guard's body contains the set_location
    # call.
    tree = ast.parse(source)
    guarded = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        cond = ast.unparse(node.test)
        if ("file" in cond) and (
            "is not None" in cond
            or cond.strip().endswith("file")
            or cond.strip().endswith("file is not None")
        ):
            # Check if any statement in the if-body invokes
            # self.document.set_location(...)
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
        "with `if file is not None:` (or `if file:`) so a None "
        "file doesn't overwrite an internal-blob location. Pre-fix "
        "body hardcoded external unconditionally — that's the bug."
    )


def test_pull_marker_removed():
    """The literal ``# PUSH to 0.0.3 force external until`` marker is gone.

    The marker lived at the now-fixed hardcode site. We pin on
    a tighter pattern: a COMBINED occurrence (the marker text
    in one line, not the historical-comment mention).
    """
    src_text = IMAGES_PATH.read_text()
    # Exact pattern: the literal marker shape — matches both
    # '# PUSH to 0.0.3 force external until' (original) and any
    # quote-escaped variant ('# PUSH-to-0.0.3 / "force external
    # until"' would match the broader pattern). To distinguish, pin
    # on the marker-specific phrase.
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
        # The T-NEW-160 prose description uses the marker phrase only
        # *within quotation* (e.g. 'force external until"') — exclude
        # quoted mentions from the marker match.
        and not ('"force external until"' in ln or "'force external until'" in ln)
    ]
    assert not marker_lines, (
        f"images.py still has the deferred-feature marker "
        f"# PUSH*-to-0.0.3 ... 'force external until' on these "
        f"lines: {marker_lines}. T-NEW-160 removes the marker. "
        f"(Historical comment references in prose are fine — "
        f"only the marker shape itself must be gone.)"
    )


def test_open_file_calls_populate_document():
    """``open_file`` must invoke ``populate_document`` so the image renders.

    Post-fix routing requires that ``open_file`` actually triggers
    the location-aware populate path (which already exists at
    images.py:1310 — internal/external dispatch). Pre-fix the
    call was AFTER the hardcoded set_location; the location
    override meant populate_document always read external.
    """
    source = _function_source("open_file")
    body_calls = []
    for sub in ast.walk(ast.parse(source)):
        if not isinstance(sub, ast.Call):
            continue
        func = sub.func
        if (
            isinstance(func, ast.Attribute)
            and isinstance(func.value, ast.Name)
            and func.value.id == "self"
            and func.attr == "populate_document"
        ):
            body_calls.append(sub)
    assert body_calls, (
        "open_file must call self.populate_document() so the "
        "image renders after setting file_path. T-NEW-160 wires "
        "the dispatcher; populate_document is the existing "
        "location-aware routing (images.py:1310)."
    )