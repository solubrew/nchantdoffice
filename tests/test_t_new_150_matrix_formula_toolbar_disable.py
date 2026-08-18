"""T-NEW-150 -- Disable Matrix formula toolbar until 0.0.3.

The Matrix widget currently wires ``Apply Formula`` (bound to
``cmd_formula_entrybox``) and ``Auto Calculate`` (bound to
``cmd_auto_calculate``) into its toolbar at ``setup_toolbar``
construction time.  Those actions are not production-ready for
0.0.1.0.1.x and must not be visible to operators in the toolbar
until the 0.0.3 release.

This test asserts the contract from two angles:

1. **Source / version-gate** -- the module that defines
   ``NchantdOfficeMatrix`` MUST expose a module-level
   ``_FORMULA_TOOLBAR_ENABLED`` flag that is ``False`` in the
   current development version (``0.0.1.0.1.4`` per
   ``pyproject.toml``).  ``setup_toolbar`` MUST honour that
   flag instead of unconditionally adding the two formula
   actions.

2. **Behaviour** -- after invoking ``setup_toolbar`` on a
   fully-stubbed instance (no real ``__init__``, no Qt parent),
   the resulting toolbar MUST NOT contain an action whose text
   is ``"Apply Formula"`` or ``"Auto Calculate"``.

The implementations of ``cmd_formula_entrybox`` and
``cmd_auto_calculate`` MUST remain defined on the class -- they
are kept for the 0.0.3 re-enable.  That is asserted by the
third test below (``test_implementations_remain_defined``).

The toolbar construction is performed via ``__new__`` plus
minimal stub methods so we never need a real Qt parent /
Pyffice document / app model.  ``setup_toolbar`` only references
``self.toolbar`` plus a flat list of method-name attributes
that we supply as no-ops.  ``pyqt.QToolBar`` is a real Qt widget
and provides the ``actions()`` API used for assertions.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import nchantdoffice.models  # noqa: F401  -- side-effect import mirrors test_t_new_148


# Project root for reading the source file under test.
REPO_ROOT = Path(__file__).resolve().parent.parent
MATRIX_PATH = (
    REPO_ROOT
    / "nchantdoffice"
    / "widgets"
    / "documents"
    / "workbooks"
    / "matricies.py"
)


def _read_matrix_source() -> str:
    return MATRIX_PATH.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Source / version-gate assertions
# ---------------------------------------------------------------------------


def test_module_exposes_formula_toolbar_gate_false() -> None:
    """Module-level ``_FORMULA_TOOLBAR_ENABLED`` flag is defined and ``False``.

    The flag is the version gate that hides the formula actions
    in the toolbar.  Until 0.0.3 ships this MUST be ``False``.
    """
    src = _read_matrix_source()
    # Require the literal symbol assignment.
    pattern = re.compile(
        r"^_FORMULA_TOOLBAR_ENABLED\s*=\s*False",
        re.MULTILINE,
    )
    assert pattern.search(src), (
        "matricies.py must define a module-level "
        "`_FORMULA_TOOLBAR_ENABLED = False` gate (T-NEW-150). "
        "Found no such assignment."
    )


def test_setup_toolbar_honours_formula_toolbar_gate() -> None:
    """``setup_toolbar`` must consult the gate before adding formula actions.

    A naive future change that re-adds the actions inline (or
    reorders the gate below them) would re-introduce the
    toolbar entries.  This test catches that.
    """
    src = _read_matrix_source()
    # Find the body of setup_toolbar.
    match = re.search(
        r"def\s+setup_toolbar\s*\([^)]*\)\s*->\s*None:\s*\n(?P<body>.*?)(?=\n    def\s|\nclass\s|\Z)",
        src,
        re.DOTALL,
    )
    assert match, "setup_toolbar method not found"
    body = match.group("body")
    # The gate reference must appear BEFORE the Add-Action lines.
    gate_pos = body.find("_FORMULA_TOOLBAR_ENABLED")
    apply_pos = body.find('"Apply Formula"')
    auto_pos = body.find('"Auto Calculate"')
    assert gate_pos != -1, (
        "setup_toolbar must reference _FORMULA_TOOLBAR_ENABLED before "
        "adding formula actions (T-NEW-150)."
    )
    assert apply_pos == -1 or apply_pos > gate_pos
    assert auto_pos == -1 or auto_pos > gate_pos
    # And the gate reference must precede the call sites.
    # (If the gate is after the addAction calls it does nothing.)
    # Locate the earliest "Apply Formula" / "Auto Calculate" addAction
    # text that survives in the guarded branch.
    guarded_apply = body.find("Apply Formula")
    guarded_auto = body.find("Auto Calculate")
    # Either both are absent (gate fully suppresses them, our target)
    # or both appear AFTER the gate reference.
    if guarded_apply != -1 or guarded_auto != -1:
        assert guarded_apply == -1 or guarded_apply > gate_pos
        assert guarded_auto == -1 or guarded_auto > gate_pos


# ---------------------------------------------------------------------------
# Behaviour assertion against a stubbed instance
# ---------------------------------------------------------------------------


def _build_matrix_with_stub_methods() -> "object":
    """Return an ``NchantdOfficeMatrix`` instance built without ``__init__``.

    ``setup_toolbar`` only references ``self.toolbar`` and a flat
    list of method-name attributes.  We supply no-op callables
    for every method it touches so the Qt widget construction
    succeeds without a parent window or app model.
    """
    # Imported here so the module-level side-effect imports above
    # are guaranteed to have run before we touch PySide6.
    from nchantdoffice.widgets.documents.workbooks.matricies import (
        NchantdOfficeMatrix,
    )

    m = NchantdOfficeMatrix.__new__(NchantdOfficeMatrix)
    for name in (
        "cmd_show_pane_left",
        "cmd_save_tab",
        "new_sheet",
        "open_file",
        "save",
        "cut",
        "copy",
        "paste",
        "toggle_bold",
        "toggle_italic",
        "cmd_formula_entrybox",
        "cmd_auto_calculate",
        "insert_row",
        "insert_column",
        "delete_row",
        "delete_column",
        "insert_chart",
    ):
        setattr(m, name, lambda *a, **k: None)
    return m


def test_setup_toolbar_omits_apply_formula() -> None:
    """``setup_toolbar`` must NOT add an action labelled "Apply Formula"."""
    m = _build_matrix_with_stub_methods()
    m.setup_toolbar()
    labels = [a.text() for a in m.toolbar.actions() if a.text()]
    assert "Apply Formula" not in labels, (
        f"setup_toolbar still wires 'Apply Formula' into the toolbar "
        f"in version {0}.  Hide it behind _FORMULA_TOOLBAR_ENABLED "
        f"until 0.0.3.  Toolbar labels seen: {labels!r}"
    )


def test_setup_toolbar_omits_auto_calculate() -> None:
    """``setup_toolbar`` must NOT add an action labelled "Auto Calculate"."""
    m = _build_matrix_with_stub_methods()
    m.setup_toolbar()
    labels = [a.text() for a in m.toolbar.actions() if a.text()]
    assert "Auto Calculate" not in labels, (
        f"setup_toolbar still wires 'Auto Calculate' into the toolbar.  "
        f"Hide it behind _FORMULA_TOOLBAR_ENABLED until 0.0.3.  "
        f"Toolbar labels seen: {labels!r}"
    )


# ---------------------------------------------------------------------------
# Implementations remain defined (the 0.0.3 re-enable guarantee)
# ---------------------------------------------------------------------------


def test_implementations_remain_defined() -> None:
    """``cmd_formula_entrybox`` and ``cmd_auto_calculate`` stay on the class.

    The card removes them from the TOOLBAR, not from the class.
    They must still be callable when 0.0.3 flips the gate back
    to ``True``.
    """
    from nchantdoffice.widgets.documents.workbooks.matricies import (
        NchantdOfficeMatrix,
    )
    assert hasattr(NchantdOfficeMatrix, "cmd_formula_entrybox"), (
        "cmd_formula_entrybox implementation must remain defined for "
        "the 0.0.3 re-enable (T-NEW-150)."
    )
    assert hasattr(NchantdOfficeMatrix, "cmd_auto_calculate"), (
        "cmd_auto_calculate implementation must remain defined for "
        "the 0.0.3 re-enable (T-NEW-150)."
    )
    # And the bound-method objects must be callable.
    assert callable(getattr(NchantdOfficeMatrix, "cmd_formula_entrybox"))
    assert callable(getattr(NchantdOfficeMatrix, "cmd_auto_calculate"))


# ---------------------------------------------------------------------------
# Misc: silence linters / make this file a clean pytest module.
# ---------------------------------------------------------------------------

_ = os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")