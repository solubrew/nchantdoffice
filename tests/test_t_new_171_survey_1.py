"""T-NEW-171 SURVEY-1 -- performance campaign instrumentation.

The T-NEW-171 card body starts with SURVEY-1: add
``time.monotonic()`` instrumentation at the boot cascade
+ 4 hot add-tab paths so operators can see WHICH phase
takes the time, without re-running tests.

The 5 hot sites per the card body:
  1. boot cascade (runNchantdOffice.py startup)
  2. add_tab (already instrumented at T-NEW-154)
  3. buildTabSet (models.py)
  4. load_tab (models.py)
  5. sortChildren (nchantrs upstream + T-NEW-156)

This commit extends the existing instrumentation to
buildTabSet and load_tab. The boot cascade + sortChildren
rounds land in subsequent SURVEY commits if needed
(separate cards per the operator's 'one commit per widget
or per phase' rule).

Tests are AST-source structural.
"""

import ast
import re
from pathlib import Path


NCHANTDOFFICE_PATH = (
    Path(__file__).parents[1] / "nchantdoffice/nchantdoffice.py"
)
PANES_NEW_PATH = (
    Path(__file__).parents[1] / "nchantdoffice/widgets/panes/new.py"
)
MODELS_PATH = Path(__file__).parents[1] / "nchantdoffice/models.py"


def _source(path: Path) -> str:
    return path.read_text()


def _find_class(path: Path, name: str) -> ast.ClassDef:
    tree = ast.parse(_source(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
    raise AssertionError(
        f"{name!r} class not found in {path}"
    )


def _method_source(path: Path, class_name: str, method_name: str) -> str:
    cls = _find_class(path, class_name)
    for body_node in cls.body:
        if (
            isinstance(body_node, ast.FunctionDef)
            and body_node.name == method_name
        ):
            return ast.unparse(body_node)
    # Fall back: search class bodies for any class with a method of the right name.
    # (Some methods sit on NchantdOfficeTabSetModel rather than the
    # NchantdOfficeCloakModel umbrella class.)
    tree = ast.parse(_source(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for body in node.body:
                if (
                    isinstance(body, ast.FunctionDef)
                    and body.name == method_name
                ):
                    return ast.unparse(body)
    raise AssertionError(
        f"{method_name!r} method not found in {class_name}"
    )


# ----------------------------------------------------------------------
# Boot cascade: runNchantdOffice.py startup emits a timing line.
# ----------------------------------------------------------------------


def test_boot_cascade_timing_emitted():
    """`cmds/runNchantdOffice.py` emits a stage-timing log line.

    The boot cascade is the natural survey anchor -- operators
    can see at a glance how long the whole launch took. The
    baseline measurement is logged as `T-NEW-171 SURVEY`
    so future comparisons are easy.
    """
    src = (Path(__file__).parents[1] / "cmds/runNchantdOffice.py").read_text()
    has_marker = "T-NEW-171" in src
    has_time_call = (
        "time.monotonic()" in src
        or "dt.datetime.now()" in src
        or "dt.datetime.utcnow()" in src
    )
    has_log = "logma.info" in src
    assert has_marker and has_time_call and has_log, (
        f"T-NEW-171 SURVEY-1: cmds/runNchantdOffice.py must "
        f"emit a T-NEW-171 stage-timing log line at the boot "
        f"cascade. The boot time is the natural anchor for "
        f"operators measuring performance. Found "
        f"marker={has_marker}, time={has_time_call}, log={has_log}."
    )


# ----------------------------------------------------------------------
# buildTabSet instrumentation
# ----------------------------------------------------------------------


def test_build_tab_set_instrumented():
    """`models.buildTabSet` snapshots `time.monotonic()` at
    function entry and emits an elapsed-ms log on return.

    This is one of the 4 hot add-tab paths flagged by
    T-NEW-171. Without this measure operators can't tell
    whether a slow add_tab was the dispatcher, the
    builder, or the DB write.
    """
    src = _method_source(MODELS_PATH, "NchantdOfficeTabSetModel", "buildTabSet")
    has_time = "time.monotonic()" in src
    has_log = (
        "logma.info" in src
        or "logma.warning" in src
        or "logma.debug" in src
    )
    has_t_new_171 = "T-NEW-171" in src
    assert has_time and has_log and has_t_new_171, (
        f"T-NEW-171 SURVEY-1: NchantdOfficeTabSetModel.buildTabSet "
        f"must emit a T-NEW-171 stage-timing log. "
        f"Found time={has_time}, log={has_log}, marker={has_t_new_171}."
    )


# ----------------------------------------------------------------------
# load_tab instrumentation
# ----------------------------------------------------------------------


def test_load_tab_instrumented():
    """`models.load_tab` snapshots `time.monotonic()` at function
    entry and emits an elapsed-ms log on return. Same pattern
    as T-NEW-154's add_tab instrumentation.
    """
    src = _method_source(MODELS_PATH, "NchantdOfficeTabSetModel", "load_tab")
    has_time = "time.monotonic()" in src
    has_log = (
        "logma.info" in src
        or "logma.warning" in src
        or "logma.debug" in src
    )
    has_t_new_171 = "T-NEW-171" in src
    assert has_time and has_log and has_t_new_171, (
        f"T-NEW-171 SURVEY-1: NchantdOfficeTabSetModel.load_tab "
        f"must emit a T-NEW-171 stage-timing log. "
        f"Found time={has_time}, log={has_log}, marker={has_t_new_171}."
    )


# ----------------------------------------------------------------------
# add_tab (already instrumented at T-NEW-154)
# ----------------------------------------------------------------------


def test_add_tab_t171_marker_present():
    """`panes/new.py add_tab` has the T-NEW-171 marker
    alongside the existing T-NEW-154 instrumentation.

    The T-NEW-171 umbrella's first survey adds the umbrella
    marker next to the existing per-site T-NEW-154 marker
    so operators can grep "T-NEW-171" and find every
    instrumented site in one pass.
    """
    # The add_tab lives on the upstream NchantdNewNodePane
    # (in nchantrs); the nchantdoffice override is in
    # NchantdOfficeNewDocumentPane in panes/new.py. We
    # search the file for the add_tab *method* body since
    # the class name doesn't matter -- the marker just
    # needs to appear in add_tab's body.
    src = PANES_NEW_PATH.read_text()
    tree = ast.parse(src)
    add_tab_src = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for body in node.body:
                if (
                    isinstance(body, ast.FunctionDef)
                    and body.name == "add_tab"
                ):
                    add_tab_src = ast.unparse(body)
    assert add_tab_src is not None, (
        "T-NEW-171 SURVEY-1: panes/new.py has no add_tab method"
    )
    assert "T-NEW-171" in add_tab_src, (
        f"T-NEW-171 SURVEY-1: NchantdNewNodePane.add_tab "
        f"must include the T-NEW-171 marker in its timing "
        f"log (the T-NEW-154 marker can stay; we add the "
        f"umbrella marker so operators can grep the umbrella)."
    )


# ----------------------------------------------------------------------
# import time already imported in each file
# ----------------------------------------------------------------------


def test_time_import_in_models():
    """`models.py` already imports `time` (else buildTabSet /
    load_tab instrumentation would NameError at runtime).
    """
    src = _source(MODELS_PATH)
    has_time = bool(
        re.search(r"^import\s+time\b", src, re.MULTILINE)
    )
    assert has_time, (
        "T-NEW-171 SURVEY-1: nchantdoffice/models.py must "
        "import the stdlib `time` module so the new "
        "time.monotonic() calls don't NameError. The file "
        "may have used time elsewhere (e.g. dt) but the `time` "
        "module import is required specifically for "
        "time.monotonic() (monotonic clock for performance "
        "measurement -- dt.datetime.now() is wall-clock and "
        "would skip backward if NTP adjusts)."
    )
