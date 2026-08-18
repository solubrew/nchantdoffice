"""T-NEW-149 (slice 2): Matrix internal save -> fresh populate_document round-trip.

Slice 1 (88fd2f2) mirrored a cell edit into ``self.document.content``.
Slice 2 (this file) closes the loop: the in-memory grid that
``save()`` stores on ``document.content`` must round-trip through
``populate_document()`` on a *fresh* Matrix instance.

The test surfaces are deliberately narrow:

1. **Bare Matrix/stub table** for the writer side.  The table
   implements only the ``rowCount`` / ``columnCount`` / ``item``
   triple that ``_read_table_to_grid`` walks, plus the
   ``itemChanged`` / ``itemSelectionChanged`` signal proxies that
   ``connect_signals`` needs.

2. **Non-square grid + formulas**.  The grid is 2 rows x 3 cols
   with a real ``=`` formula in cell ``A2`` so we can verify
   that *both* the visible values and the formula field survive
   the round-trip.

3. **Parent/base DB persistence mocked**.  ``NchantdOfficeDocument.save``
   holds the chain that ultimately persists to ``doc_media`` via
   ``self.app.model.store_document``.  We monkey-patch it to a
   no-op capture so the round-trip is asserted at the
   in-memory document layer only -- no SQLite, no file_path,
   no Pyffice.

4. **Fresh Matrix with stub ``table.update_data``**.  The reader
   side uses a Matrix that has never seen the table.  We stub
   ``table.update_data`` to capture the data passed in, then
   call ``populate_document()`` and assert the captured grid
   matches the original and the formulas live alongside it on
   ``document.content``.

The test is RED-first: it pins the round-trip contract against
the *current* save/populate implementation.  If the existing
code already satisfies it, the test passes GREEN with no
further changes.  If it does not, the failure modes guide the
minimal Matrix-only fix in slice 2.
"""

from __future__ import annotations

import os
from types import SimpleNamespace
from unittest.mock import patch

import nchantdoffice.models  # noqa: F401  -- side-effect import mirrors cell_mirror test

# T-NEW-074 / T-NEW-122: keep Qt on the headless offscreen platform
# before any PySide6 import so we don't need a real display.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument
from nchantdoffice.widgets.documents.workbooks.matricies import NchantdOfficeMatrix


# ---------------------------------------------------------------------------
# Stub helpers
# ---------------------------------------------------------------------------


class _Signal:
    """Minimal signal stub -- ``connect(callable)`` is a no-op."""

    def __init__(self):
        self._callables = []

    def connect(self, fn):
        self._callables.append(fn)

    def disconnect(self, *args, **kwargs):
        self._callables = []

    def emit(self, *args, **kwargs):
        for fn in list(self._callables):
            fn(*args, **kwargs)


class _Item:
    """Table item stub returned by ``table.item(row, col)``."""

    def __init__(self, text):
        self._text = text

    def text(self):
        return self._text


class _StubTable:
    """Stub table for the writer side.

    Provides the rowCount / columnCount / item surface that
    ``_read_table_to_grid`` walks, plus the bare signal proxies
    that ``connect_signals`` touches.  Nothing else.
    """

    def __init__(self, rows, cols, cells):
        self._rows = rows
        self._cols = cols
        self._cells = cells  # dict[(row, col)] -> text
        self.itemChanged = _Signal()
        self.itemSelectionChanged = _Signal()

    def rowCount(self):
        return self._rows

    def columnCount(self):
        return self._cols

    def item(self, r, c):
        text = self._cells.get((r, c))
        if text is None:
            return None
        return _Item(text)


class _UpdateCapture:
    """Captures the payload passed to ``table.update_data`` on the reader side."""

    def __init__(self):
        self.calls = []

    def __call__(self, data):
        self.calls.append(data)


# ---------------------------------------------------------------------------
# Wiring
# ---------------------------------------------------------------------------


def _bare_matrix(rows, cols, cells):
    """Build a bare Matrix via ``__new__`` with a stub table.

    Skips ``__init__`` entirely so we don't need a real Qt
    parent, app model, or Pyffice document.  The only state that
    matters is ``document`` (stub) and ``table`` (stub).
    """
    m = NchantdOfficeMatrix.__new__(NchantdOfficeMatrix)
    document = SimpleNamespace(
        content={},
        set_content=lambda c: None,
        location=None,
        file_path=None,
        data=None,
        save=lambda *_a, **_k: None,
    )
    m.document = document
    m.table = _StubTable(rows, cols, cells)
    m.file_path = None
    return m


def _secondary_table(rows, cols, cells):
    """Stub table for the reader side (separate instance)."""
    return _StubTable(rows, cols, cells)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_save_captures_grid_and_formulas_on_document_content():
    """``save()`` must write the grid + formulas onto the document.

    Parent/base DB persistence is mocked to a no-op so the
    assertion lands on the in-memory contract: the document
    object now carries a non-square grid and a parallel
    formulas grid.
    """
    # 2 rows x 3 cols, non-square.  Cell (1, 0) is a formula.
    cells = {
        (0, 0): "alpha",
        (0, 1): "beta",
        (0, 2): "gamma",
        (1, 0): "=1+2",
        (1, 1): "delta",
        (1, 2): "epsilon",
    }
    m = _bare_matrix(rows=2, cols=3, cells=cells)

    captured = {}
    real_save = NchantdOfficeDocument.save

    def _mocked_save(self_):
        # Capture the document content the way the parent chain
        # would see it just before the base DB persistence runs.
        captured.setdefault("contents", []).append(
            getattr(self_.document, "content", None)
        )
        # Stop the chain so we never touch SQL / pyffice.
        return self_

    with patch.object(NchantdOfficeDocument, "save", _mocked_save):
        m.save()

    # Existing chain must have been silenced.
    assert captured["contents"], "parent save() was never invoked"

    doc_content = m.document.content
    assert doc_content.get("grid") == [
        ["alpha", "beta", "gamma"],
        ["=1+2", "delta", "epsilon"],
    ], f"grid did not match: {doc_content.get('grid')!r}"
    assert doc_content.get("formulas") == [
        ["", "", ""],
        ["=1+2", "", ""],
    ], f"formulas did not match: {doc_content.get('formulas')!r}"
    assert doc_content.get("num_rows") == 2
    assert doc_content.get("num_cols") == 3

    # Sanity: the parent save() was actually called via the MRO.
    # It saw the same document.content we read above.
    assert captured["contents"][-1] is doc_content


def test_save_then_fresh_populate_roundtrip_preserves_grid_and_formulas():
    """End-to-end: ``save()`` -> capture -> fresh Matrix -> ``populate_document()``.

    The fresh Matrix never sees the writer's table.  We stub
    ``table.update_data`` on the reader side to capture the data
    the populate path pushes into the table, and assert that
    both the grid and the formulas round-trip untouched.
    """
    cells = {
        (0, 0): "alpha",
        (0, 1): "beta",
        (0, 2): "gamma",
        (1, 0): "=1+2",
        (1, 1): "delta",
        (1, 2): "epsilon",
    }
    writer = _bare_matrix(rows=2, cols=3, cells=cells)

    # Mock the parent/base DB persistence.  The test contract
    # is on the in-memory document content, not on SQL.
    with patch.object(NchantdOfficeDocument, "save", lambda self_: self_):
        writer.save()

    captured_grid = writer.document.content["grid"]
    captured_formulas = writer.document.content["formulas"]
    captured_content = dict(writer.document.content)

    # Fresh Matrix on the reader side.  It has never seen the
    # writer's table or the cells.  The table stub only knows
    # how to receive ``update_data`` and how to connect signals.
    fresh = NchantdOfficeMatrix.__new__(NchantdOfficeMatrix)
    fresh_document = SimpleNamespace(
        content=dict(captured_content),
        location=None,
        file_path=None,
        data=None,
        set_content=lambda c: None,
        save=lambda *_a, **_k: None,
    )
    fresh.document = fresh_document
    update_capture = _UpdateCapture()
    fresh_table = _secondary_table(rows=0, cols=0, cells={})
    fresh_table.update_data = update_capture
    fresh.table = fresh_table
    fresh.file_path = None
    fresh.num_rows = 0
    fresh.num_cols = 0

    fresh.populate_document()

    # populate_document() must push the same grid into the
    # reader's table.update_data.
    assert update_capture.calls, (
        "populate_document() never called table.update_data -- "
        "the reader side cannot round-trip the grid"
    )
    pushed = update_capture.calls[-1]
    assert pushed == captured_grid, (
        f"update_data received {pushed!r}, expected {captured_grid!r}"
    )

    # The formulas grid must survive on the fresh document's
    # content.  populate_document() is allowed to leave it
    # untouched on the document even after the table update.
    assert fresh.document.content.get("formulas") == captured_formulas, (
        f"formulas grid lost on round-trip: "
        f"got {fresh.document.content.get('formulas')!r}, "
        f"expected {captured_formulas!r}"
    )
    # And the grid is still on the document.
    assert fresh.document.content.get("grid") == captured_grid


def test_roundtrip_handles_empty_grid_and_missing_formulas():
    """Empty matrix round-trips: save() -> populate_document() must not crash.

    An empty table (0 rows / 0 cols) should produce an empty
    grid and *no* formulas key (or an empty one).  The reader
    side must accept that without raising.
    """
    writer = _bare_matrix(rows=0, cols=0, cells={})

    with patch.object(NchantdOfficeDocument, "save", lambda self_: self_):
        writer.save()

    captured = dict(writer.document.content)

    fresh = NchantdOfficeMatrix.__new__(NchantdOfficeMatrix)
    fresh_document = SimpleNamespace(
        content=dict(captured),
        location=None,
        file_path=None,
        data=None,
        set_content=lambda c: None,
        save=lambda *_a, **_k: None,
    )
    fresh.document = fresh_document
    update_capture = _UpdateCapture()
    fresh_table = _secondary_table(rows=0, cols=0, cells={})
    fresh_table.update_data = update_capture
    fresh.table = fresh_table
    fresh.file_path = None
    fresh.num_rows = 0
    fresh.num_cols = 0

    fresh.populate_document()

    # update_data was called with an empty grid.
    assert update_capture.calls, (
        "populate_document() never called table.update_data on empty matrix"
    )
    assert update_capture.calls[-1] == [], (
        f"update_data received {update_capture.calls[-1]!r}, expected []"
    )
