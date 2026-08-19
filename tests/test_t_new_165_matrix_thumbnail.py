"""T-NEW-165 — Matrix cell-content thumbnail preview ships a real widget.

The 2026-08-18 PUSH-to-0.0.3 sweep found a single marker at
``nchantdoffice/widgets/documents/workbooks/matricies.py:1650`` (inside
``init_drawer_cell_config``) labelled "Thumbnail preview of selected
cell content". Unlike the other 90 markers in the sweep, this one
described a concrete user-facing enhancement that could land without
the umbrella work.

The fix:
1. ``init_drawer_cell_config`` adds a ``NchantdLabel`` slot under
   ``self.cell_thumbnail`` that renders the active cell's value.
2. ``on_selection_changed`` (the existing selection hook at line
   1804) updates the label alongside the formula bar.
3. The `# PUSH 0.0.3 — Thumbnail preview ...` comment is removed
   (the slot now exists).

The tests are AST-source structural (mirroring the
``test_t_new_117_palette_scan_degradation`` recipe) because
``NchantdOfficeMatrix`` imports PySide6 — pytest collection would
crash on the import chain in this headless env.
"""

import ast
from pathlib import Path


MATRICIES_PATH = (
    Path(__file__).parents[1]
    / "nchantdoffice/widgets/documents/workbooks/matricies.py"
)


def _function_source(name: str) -> str:
    tree = ast.parse(MATRICIES_PATH.read_text())
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return ast.unparse(node)
    raise AssertionError(f"{name} not found")


def test_cell_config_drawer_has_thumbnail_label_slot():
    """``init_drawer_cell_config`` must construct ``self.cell_thumbnail``.

    T-NEW-165: the PUSH-to-0.0.3 marker at line 1650 (the
    "Thumbnail preview of selected cell content" placeholder) is
    replaced with a real ``NchantdLabel`` slot wired via
    ``_ensure_drawer_item``.
    """
    source = _function_source("init_drawer_cell_config")
    assert "cell_thumbnail" in source, (
        "init_drawer_cell_config must bind a NchantdLabel under "
        "self.cell_thumbnail — the PUSH-to-0.0.3 marker at line 1650 "
        "was a placeholder for exactly this slot."
    )
    assert "NchantdLabel" in source, (
        "init_drawer_cell_config must import + use NchantdLabel for "
        "the thumbnail slot; got a different widget class."
    )
    assert "_ensure_drawer_item" in source, (
        "init_drawer_cell_config must add the thumbnail via the "
        "centralised _ensure_drawer_item helper, matching the "
        "sibling slot pattern."
    )


def test_push_0_0_3_thumbnail_marker_removed():
    """The literal "# PUSH 0.0.3 — Thumbnail preview ..." comment is gone.

    Once the slot ships, the marker is redundant — the test file
    documents the migration by name so a future sweep doesn't
    re-investigate the same line.
    """
    src = MATRICIES_PATH.read_text()
    # The marker text from the original sweep:
    #   "# PUSH 0.0.3 — Thumbnail preview of selected cell content"
    assert "PUSH 0.0.3 — Thumbnail preview of selected cell content" not in src, (
        "The PUSH-to-0.0.3 marker for the Matrix thumbnail preview "
        "should be removed once the slot ships (T-NEW-165 CLEANUP-1)."
    )


def test_on_selection_changed_updates_cell_thumbnail():
    """``on_selection_changed`` must push the cell value into ``cell_thumbnail``.

    The existing handler at line 1804 already updates ``formula_input``
    and ``cell_ref_label``; T-NEW-165 adds a third consumer:
    ``cell_thumbnail``. The thumbnail gets the same `value` string
    the formula bar receives (text representation of the active cell).
    """
    source = _function_source("on_selection_changed")
    assert "cell_thumbnail" in source, (
        "on_selection_changed must update self.cell_thumbnail with the "
        "cell value, alongside cell_ref_label and formula_input. "
        "T-NEW-165 WIRE-2: hook the same selection signal that drives "
        "the formula bar."
    )
    # Guard: if cell_thumbnail exists but was never wired (AttributeError),
    # the update would crash. The handler must wrap in hasattr like the
    # cell_ref_label pattern, since the label is built inside init_drawer_cell_config
    # but on_selection_changed may fire before init_drawer runs in some
    # test harnesses.
    assert "hasattr" in source or "getattr" in source, (
        "on_selection_changed must guard cell_thumbnail access with "
        "hasattr/getattr — the cell_config drawer may not have been "
        "built yet when the signal first fires (mirrors the "
        "cell_ref_label hasattr guard at line 1814)."
    )


def test_init_cell_config_thumbnail_slot_position():
    """The thumbnail slot is appended at the END of init_drawer_cell_config.

    The PUSH-to-0.0.3 marker lived at the bottom of the function
    (just before ``return items``), so the slot must be added there
    to keep the diff narrow — earlier slots (border format etc.)
    are not touched per the "only touch the helper that ships the
    fix" rule.
    """
    source = _function_source("init_drawer_cell_config")
    # The thumbnail widget construction should appear after the
    # border-format slot (the prior sibling) and before the return.
    border_idx = source.find("NchantdOfficeCellBorderFormats")
    thumbnail_idx = source.find("cell_thumbnail")
    return_idx = source.find("return items")
    assert border_idx != -1, "sibling border-format slot is gone — review the diff"
    assert thumbnail_idx != -1, "cell_thumbnail slot missing"
    assert return_idx != -1, "return items missing"
    assert border_idx < thumbnail_idx < return_idx, (
        f"cell_thumbnail slot must appear AFTER border-format "
        f"(border at {border_idx}, thumbnail at {thumbnail_idx}, "
        f"return at {return_idx}) to preserve the original slot order."
    )