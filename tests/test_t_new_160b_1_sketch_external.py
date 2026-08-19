"""T-NEW-160b card 1 — NchantdOfficeSketch location routing.

T-NEW-144b umbrella card 3.1 of 11. NchantdOfficeSketch at
``sketches.py:1077`` hardcoded
``self.document.set_location("external")`` followed by a
literal ``if self.document.location == "external"`` dispatch
that fired on every load. The hardcode forced every sketch
doc to file-origin, breaking the .pyof internal-blob load
path. Mirrors the T-NEW-160 (Image) fix shape, applied to
the Sketch widget.

The post-fix flow is:

  def initView:
      # leave location as-is (None default; respects caller-set
      # location when the sketch loads from .pyof).
      ...
      if self.document.location == "external":
          self.open_file(self.document.file_path)
      return self

Tests are AST-source structural (mirroring T-NEW-160 / -160a
pattern). The sketches.py file imports PySide6 via the
nchantrs chain.
"""

import ast
from pathlib import Path


SKETCHES_PATH = (
    Path(__file__).parents[1] / "nchantdoffice/widgets/documents/media/sketches.py"
)


def _function_source(name: str, class_name: str | None = None) -> str:
    """Return source for the named method (optionally filtered by class).

    sketches.py has 12 ``initView`` methods (one per pane
    class). The default returns the FIRST match — for
    location-dispatch tests we MUST target the late-defined
    ``NchantdOfficeSketch.initView``. Pass ``class_name`` to
    disambiguate.
    """
    tree = ast.parse(SKETCHES_PATH.read_text())
    candidates = []
    for node in ast.walk(tree):
        if not (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == name
        ):
            continue
        if class_name is not None:
            # Walk up to enclosing class
            enclosing = next(
                (
                    top
                    for top in tree.body
                    if isinstance(top, ast.ClassDef)
                    and node.lineno >= top.lineno
                    and (top.end_lineno or 0) >= node.lineno
                ),
                None,
            )
            if enclosing is None or enclosing.name != class_name:
                continue
        candidates.append(node)
    if not candidates:
        raise AssertionError(
            f"{name}{' (class ' + class_name + ')' if class_name else ''} not found"
        )
    return ast.unparse(candidates[-1])  # last (post-fix) match wins


def _class_for_method(name: str) -> str | None:
    """Return the enclosing class name for the named method.

    Like ``_function_source``, the file has 12 ``initView``
    methods. The default returns the LAST match — for
    location-dispatch tests we MUST target
    ``NchantdOfficeSketch.initView``, which is the 11th
    ``initView`` (defined second-to-last in the class order —
    before NchantdOfficePalette).

    For this test card the target is fixed at
    NchantdOfficeSketch (T-NEW-160b/1).
    """
    target_class = "NchantdOfficeSketch"
    tree = ast.parse(SKETCHES_PATH.read_text())
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        if node.name != target_class:
            continue
        for body_node in node.body:
            if (
                isinstance(body_node, ast.FunctionDef)
                and body_node.name == name
            ):
                return node.name
    return None


def test_init_view_no_longer_hardcodes_external():
    """``NchantdOfficeSketch.initView`` body must NOT call ``set_location("external")``.

    Pre-fix body at sketches.py:1077 hardcoded ``external`` for
    every load (followed by an if/else dispatch that depended
    on the hardcode). Post-fix leaves location as-is.
    """
    assert _class_for_method("initView") == "NchantdOfficeSketch", (
        "initView must be defined on NchantdOfficeSketch "
        "(T-NEW-160b/1 target class)."
    )
    source = _function_source("initView", class_name="NchantdOfficeSketch")
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
        "NchantdOfficeSketch.initView must NOT call "
        "self.document.set_location('external') — that hardcode "
        "forced every sketch doc to file-origin even when loaded "
        "from the DB. T-NEW-160b/1 drops the hardcode; the doc "
        "location threads through the caller."
    )


def test_init_view_dispatch_intact():
    """The location-aware dispatch (``if location == external``) stays.

    Post-fix the dispatch reads the caller-set location. The
    if/else structure is preserved so external-origin docs
    continue to call ``open_file`` while internal/cloud paths
    can land a new dispatch in a future card.
    """
    source = _function_source("initView", class_name="NchantdOfficeSketch")
    has_external_dispatch = (
        "location == 'external'" in source
        and "self.open_file" in source
    )
    assert has_external_dispatch, (
        "NchantdOfficeSketch.initView must keep the location-aware "
        "dispatch: `if self.document.location == 'external': "
        "self.open_file(...)`. Post-fix the location reads "
        "from the caller (not hardcoded); the dispatch code "
        "stays intact so external-origin docs continue to work."
    )


def test_pull_marker_removed():
    """The literal ``# PUSH to 0.0.3 force external until`` marker is gone.

    The marker lived at the now-fixed hardcode site.
    """
    src_text = SKETCHES_PATH.read_text()
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
        f"sketches.py still has the deferred-feature marker "
        f"# PUSH*-to-0.0.3 ... 'force external until' on these lines: "
        f"{marker_lines}. T-NEW-160b/1 removes the marker."
    )
