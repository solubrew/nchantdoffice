"""T-NEW-122: repository-wide guard against module-level QApplication.

RED test: this test MUST fail right now. The current code base
has 21 test files that bootstrap a ``QApplication`` at module
import time via the pattern::

    _QAPP = QApplication.instance() or QApplication(sys.argv)

That pattern passes when the file is collected alone but aborts
the entire multi-file pytest run (see ``qt-parent-harness``
skill lesson 14). The abort signature is
``Fatal Python error: Aborted (core dumped)`` with exit 134
when the order of Qt-loading files collides at collection time,
or a segfault (exit 139) later in the run because the global
``_QAPP`` singletons from multiple files conflict through
shiboken.

This guard runs the AST-based scan from
``tests/qt_parent/scan_module_level_qt.py`` and asserts that
no file under ``tests/`` (excluding the harness server and
in-function lazy constructions) has a top-level call to a
Qt constructor that touches native state. While ANY file
fails the scan, this test fails -- which is the RED state
we want.

When the migration is complete (all 21 offenders moved to the
``qapp`` fixture in :mod:`tests.qt_parent`), the scan returns
zero offenders and this test passes (GREEN).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Make sure the skill's scan script is importable. It lives
# inside the installed skill at
# ~/.hermes/skills/qt-parent-harness/scripts/scan_module_level_qt.py.
# Fall back to vendoring the scan logic below if the skill
# directory is unavailable in this environment.
_SKILL_SCRIPT = Path(
    "/home/solubrew/.hermes/skills/qt-parent-harness/scripts/scan_module_level_qt.py"
)
if _SKILL_SCRIPT.exists():
    sys.path.insert(0, str(_SKILL_SCRIPT.parent))
    from scan_module_level_qt import scan  # type: ignore[import-not-found]
else:
    from tests.qt_parent.scan_module_level_qt import scan  # type: ignore[no-redef]


REPO_ROOT = Path(__file__).resolve().parent.parent
TESTS_DIR = REPO_ROOT / "tests"

# Files exempt from the scan. The qt_parent server is a
# *subprocess entry point* that intentionally boots its own
# QApplication at top level (it's not a pytest-collected
# test, but a spawned helper) -- see SKILL.md "Server side
# (subprocess entry point)". We exclude it so the guard
# stays focused on the test-collection blast radius.
_EXEMPT = {
    REPO_ROOT / "tests" / "qt_parent" / "server.py",
    # The guard itself, in case it ever needs to do Qt work.
    REPO_ROOT / "tests" / "test_t_new_122_qt_collection_guard.py",
}


def _filter_exempt(results):
    """Drop exempt paths so the test message focuses on real offenders."""
    return {p: hits for p, hits in results.items() if p not in _EXEMPT}


def test_no_module_level_qapplication_in_tests():
    """No test file may construct a QApplication at module top level.

    This is the T-NEW-122 RED->GREEN gate. The current code
    base has 21 offenders; the migration in this card moves
    each one to the ``qapp`` fixture in
    :mod:`tests.qt_parent`. Once the migration is complete,
    this test passes.

    Offenders (current state, will be cleared by the migration):

    * tests/test_right_pane_visibility.py:27
    * tests/test_t_new_040_toolbar_init.py:42
    * tests/test_right_side_tabset_recovery.py:33
    * tests/test_journal_restore.py:24
    * tests/test_t_new_025_content_versioning.py:46
    * tests/test_catalog_lower_pane_after_accept.py:47
    * tests/test_per_doc_type_settings_pane.py:29
    * tests/test_source_config_stubs.py:27
    * tests/test_t_new_038_save_icon.py:30
    * tests/test_t_new_035_script_drawer_polish.py:45
    * tests/test_t_new_037_empty_stubs.py:34
    * tests/test_splitter_stretch_factors.py:45
    * tests/test_tab_to_node_drag_persistence.py:25
    * tests/test_t_new_033_search_dispatch.py:35
    * tests/test_t_new_042_note_position.py:26
    * tests/test_update_tab_name_on_file_open.py:31
    * tests/test_t_new_004_app_node_locks.py:44
    * tests/test_t_new_001_tab_icon.py:48
    * tests/test_t_new_041_widget_lookup.py:30
    * tests/test_t_new_026_affiliate_manager.py:44
    * tests/test_t_new_029_tab_drag_region.py:51
    """
    results = scan(TESTS_DIR)
    results = _filter_exempt(results)

    if not results:
        # GREEN: no module-level Qt constructors found.
        return

    # RED: build a helpful failure message listing every offender.
    lines = [
        "T-NEW-122 RED: module-level QApplication() found in "
        f"{len(results)} test file(s). Each is a pytest-collection "
        "abort waiting to happen.",
        "",
    ]
    for path, hits in sorted(results.items()):
        rel = path.relative_to(REPO_ROOT)
        lines.append(f"  {rel}")
        for line_no, name, source in hits:
            lines.append(f"    L{line_no}: {name}()")
            lines.append(f"        {source}")
    lines.append("")
    lines.append(
        "Fix: replace the module-level line with a pytest fixture "
        "request. In tests/, add 'from tests.qt_parent import qapp' "
        "at the top and either:\n"
        "  (a) Decorate the test with @pytest.mark.usefixtures('qapp'), OR\n"
        "  (b) Add 'qapp' as a fixture argument, OR\n"
        "  (c) For tests that never construct a QWidget, just delete "
        "the _QAPP line entirely (it was only there to satisfy a "
        "subclass constructor that the test no longer needs)."
    )
    pytest.fail("\n".join(lines))


def test_no_module_level_qwidget_in_tests():
    """Belt-and-braces: no top-level QWidget / QMainWindow either.

    The same collection-abort class applies to any Qt native
    constructor. The skill's scan covers the full list, but
    call it out as a separate test for clearer failure messages.
    """
    results = scan(TESTS_DIR)
    results = _filter_exempt(results)

    # Group by Qt class name so the failure message can be specific.
    by_class: dict[str, list[tuple[Path, int, str]]] = {}
    for path, hits in results.items():
        for line_no, name, source in hits:
            if name == "QApplication":
                continue  # covered by the primary test
            by_class.setdefault(name, []).append((path, line_no, source))

    if not by_class:
        return

    lines = [
        "T-NEW-122: module-level Qt constructors other than QApplication:",
        "",
    ]
    for cls in sorted(by_class):
        lines.append(f"  {cls}()")
        for path, line_no, source in by_class[cls]:
            rel = path.relative_to(REPO_ROOT)
            lines.append(f"    {rel}:{line_no}")
            lines.append(f"        {source}")
    pytest.fail("\n".join(lines))
