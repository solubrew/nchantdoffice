"""T-NEW-149 (slice 3): Matrix full DB encoded-payload round-trip.

Slice 1 (88fd2f2) mirrored a cell edit into ``self.document.content``.
Slice 2 (6ea1443) closed the in-memory loop -- ``save()`` writes grid/
formulas onto ``document.content`` and ``populate_document()`` reads
them back on a fresh Matrix.

Slice 3 (this file) closes the *real DB* loop: when a Matrix is saved
through the production ``NchantdOfficeDocument.save()`` chain (the
chain the user actually runs when they click "Save"), the payload
that lands in ``doc_media_content.content_enc64_txt`` must round-trip
back to the same grid + formulas after a base64 decode.

The live bug that motivates this card:

  ``Matrix.save()`` writes grid + formulas onto ``document.content``
  (matricies.py:1971-1974).  Then ``super().save()`` enters the
  parent chain at documents.py:601.  At line 661 that chain calls
  ``self.get_content()`` -- which on a Matrix currently returns the
  canonical envelope ``{"content": {"file_path": ...}, "data":
  document.data}`` (matricies.py:1255).  Line 667 then calls
  ``self.document.set_content(widget_content)``, which invokes
  Pyffice's ``set_content`` (pyffice/document.py:1213) and *overwrites*
  ``document.content`` with the stripped envelope.  The grid + formulas
  are gone before ``add_document_content`` (models.py:646) reads
  ``document['content']`` and base64-encodes it into
  ``content_enc64_txt``.

The result: reopening the Matrix after save produces an empty table
even though the in-memory ``populate_document`` test (slice 2) passes
in isolation -- because slice 2 never ran ``NchantdOfficeDocument.save``
to completion.

This file pins the contract at the SQL-payload level:

1. Drive a bare Matrix through the FULL save chain (no early
   short-circuit).  Wire ``NchantdOfficeCloakModel.store_document``
   into a ``CapturingStore`` so we can read the actual
   ``content_enc64_txt`` that the production chain produces.
2. Decode the base64 payload back to a dict.
3. Assert the decoded dict contains the exact non-square grid + the
   parallel formulas grid + ``num_rows`` + ``num_cols`` + ``file_path``
   -- not the stripped ``{"content": {"file_path": ...}}`` envelope.
4. The empty-matrix case round-trips through the same chain.

This is a strict TDD card.  RED first: the test must fail with the
exact symptom described above (decoded payload missing the grid).
GREEN is a Matrix-only fix: update ``Matrix.get_content`` to return
the canonical envelope with grid/formulas/num_rows/num_cols/file_path,
and update ``populate_document`` to accept envelope
``content['content']['grid']`` with legacy ``content['grid']`` fallback.
"""

from __future__ import annotations

import base64
import json
import os
from types import SimpleNamespace

import nchantdoffice.models  # noqa: F401  -- side-effect import mirrors cell_mirror test

# T-NEW-074 / T-NEW-122: keep Qt on the headless offscreen platform
# before any PySide6 import so we don't need a real display.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from nchantdoffice.models import NchantdOfficeCloakModel
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
    """Stub table -- implements rowCount/columnCount/item + signals."""

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


class _CapturingStore:
    """Captures doc_media_content payloads exactly as squirl would receive them."""

    def __init__(self):
        self.media_rows = []
        self.content_rows = []

    def store_doc_media(self, document):
        self.media_rows.append(dict(document))

    def store_doc_media_content(self, payload):
        self.content_rows.append(dict(payload))

    def get_table(self, *_args, **_kwargs):
        return None

    def update_record(self, *_args, **_kwargs):
        # T-NEW-024 followup: store_document writes doc_media.syntax_txt
        # via update_record; this test asserts on the content_enc64_txt
        # blob, so the syntax update is a no-op here.
        return None


# ---------------------------------------------------------------------------
# Wiring
# ---------------------------------------------------------------------------


def _build_capture_app(store):
    """Build the app.view.panes tree that ``NchantdOfficeDocument.save``
    expects -- current_node must be non-None (early-return guard at
    documents.py:642) and current_tab must be non-None (early-return
    guard at documents.py:646).
    """
    tree_model = SimpleNamespace(current_node=SimpleNamespace(nid="matrix-node"))
    center_model = SimpleNamespace(current_tab=SimpleNamespace(position=0))
    return SimpleNamespace(
        view=SimpleNamespace(
            panes={
                "left": SimpleNamespace(tree=SimpleNamespace(model=tree_model)),
                "center": SimpleNamespace(model=center_model),
            }
        ),
        config=SimpleNamespace(dikt={"apps": ["nchantrs", "nchantdoffice"]}),
        model=None,  # wired below
        codex=SimpleNamespace(),
        user=SimpleNamespace(),
        application_name="NchantdOffice",
    )


def _build_model_with(store):
    """Wire a real ``NchantdOfficeCloakModel`` against the capturing store.

    We bypass ``__init__`` (no Qt app needed) and only attach the bits
    ``store_document`` actually touches: ``self.store`` and the
    ``_store`` plumbing.  ``store_document`` (models.py:~1985) walks
    ``self.app.config.dikt['apps']`` and calls ``add_document_content``
    which calls ``self.store.store_doc_media_content(payload)``.
    """
    model = object.__new__(NchantdOfficeCloakModel)
    model.store = store
    model.has_changed = False
    model.instance = None
    model.app = SimpleNamespace(
        model=model,
        config=SimpleNamespace(dikt={"apps": ["nchantrs", "nchantdoffice"]}),
        view=SimpleNamespace(
            panes={
                "center": SimpleNamespace(model=SimpleNamespace(tabbase=[0, 1, 1, 1]))
            }
        ),
        application_name="NchantdOffice",
    )
    return model


def _bare_matrix(rows, cols, cells, did="matrix-1"):
    """Build a bare Matrix via ``__new__`` with a stub table.

    ``did`` and ``content_original`` are required by the chain at
    documents.py:650 (``logma.info(f\"Save DID {self.document.did}\")``).
    ``set_content`` is required at documents.py:667 -- it is the
    canonical Pyffice ``set_content`` (which we stub to a setter so
    the full chain runs and we observe the overwrite).
    """
    m = NchantdOfficeMatrix.__new__(NchantdOfficeMatrix)
    document = SimpleNamespace(
        did=did,
        location="internal",
        content=None,
        data=None,
        file_path=None,
        version=1,
        syntax="plain-text",
        content_original=None,
        # Pyffice.set_content overwrites self.content = content.
        # We expose that surface here so the full chain runs.
        set_content=lambda c: setattr(document, "content", c),
        save=lambda path=None: None,
        # T-NEW-039: store_document calls update_record on doc_media
        # (T-NEW-024 followup).  Document model returns nothing useful
        # for our test.
        to_dict=lambda: {
            "did": did,
            "content": document.content,
            "version": 1,
            "syntax": "plain-text",
            "location": "internal",
            "document_type": "matrix",
        },
    )
    m.document = document
    m.table = _StubTable(rows, cols, cells)
    m.file_path = None
    return m


def _decode_payload(row):
    """Decode a captured ``store_doc_media_content`` row back to a dict.

    The production chain in ``add_document_content`` (models.py:646)
    reads ``document['content']`` and base64-encodes the JSON.  The
    row key for the encoded payload is ``content`` (it is what
    ``_store`` writes to ``content_enc64_txt`` after the column-name
    mapping).
    """
    raw = row.get("content") or row.get("content_enc64_txt")
    if raw is None:
        raise AssertionError(f"content key missing from payload: {list(row)}")
    decoded = base64.b64decode(raw).decode("utf-8")
    return json.loads(decoded)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_matrix_save_roundtrip_through_full_db_chain_preserves_grid():
    """Drive the FULL ``NchantdOfficeDocument.save()`` chain.

    The current bug: ``Matrix.get_content`` returns the stripped
    canonical envelope, ``document.set_content`` overwrites the
    grid+formulas that ``Matrix.save()`` just wrote, and the
    captured ``content_enc64_txt`` decodes back to a payload that
    does NOT contain the grid.

    After the GREEN fix (Matrix-only) the decoded payload must
    contain ``content.grid`` (or the canonical envelope's
    ``content`` field), the parallel formulas, and ``num_rows`` /
    ``num_cols`` matching the source table.
    """
    # 2 rows x 3 cols, non-square, with a real =formula in cell (1,0).
    cells = {
        (0, 0): "alpha",
        (0, 1): "beta",
        (0, 2): "gamma",
        (1, 0): "=1+2",
        (1, 1): "delta",
        (1, 2): "epsilon",
    }
    store = _CapturingStore()
    matrix = _bare_matrix(rows=2, cols=3, cells=cells, did="matrix-1")
    matrix.app = _build_capture_app(store)
    matrix.app.model = _build_model_with(store)

    # Wrap store_doc_media_content so we capture the exact payload
    # the production code builds (defensive copy of the dict).
    captured_payloads = []
    original_store_doc_media_content = store.store_doc_media_content

    def capture_and_store(payload):
        captured_payloads.append(dict(payload))
        original_store_doc_media_content(payload)

    store.store_doc_media_content = capture_and_store

    # Drive the FULL save chain.  No patching: this is the production
    # path the user runs when they click "Save".
    matrix.save()

    # First, confirm the chain actually ran -- if ``get_content``
    # short-circuited or the early-return guards fired, we'd never
    # capture a payload at all.
    assert captured_payloads, (
        "save() never invoked store_doc_media_content -- the full "
        "DB chain did not run (the test is not exercising what it "
        "thinks it is)."
    )

    payload = captured_payloads[-1]
    assert payload["pUUID"] == "matrix-1"
    assert payload["page"] == 0
    assert payload["entry"] == 0

    decoded = _decode_payload(payload)

    # The decoded payload must carry the grid -- this is the live bug.
    # Two acceptable shapes after GREEN:
    #   * canonical envelope  -> decoded["content"]["grid"] == [...]
    #   * legacy flat         -> decoded["grid"] == [...]
    # The Matrix-only fix lands the canonical envelope.  Either is
    # acceptable as long as the grid survives.
    grid = decoded.get("grid")
    if grid is None:
        nested = decoded.get("content")
        if isinstance(nested, dict):
            grid = nested.get("grid")
    assert grid == [
        ["alpha", "beta", "gamma"],
        ["=1+2", "delta", "epsilon"],
    ], f"grid did not round-trip through the DB payload: {grid!r}"

    # The formulas must round-trip too.  After the Matrix-only fix,
    # the canonical envelope carries formulas alongside grid.
    formulas = decoded.get("formulas")
    if formulas is None:
        nested = decoded.get("content")
        if isinstance(nested, dict):
            formulas = nested.get("formulas")
    assert formulas == [
        ["", "", ""],
        ["=1+2", "", ""],
    ], f"formulas did not round-trip through the DB payload: {formulas!r}"

    # The dimensions must round-trip so the reopen path can resize
    # the fresh table to match.
    num_rows = decoded.get("num_rows")
    if num_rows is None:
        nested = decoded.get("content")
        if isinstance(nested, dict):
            num_rows = nested.get("num_rows")
    assert num_rows == 2, f"num_rows did not round-trip: {num_rows!r}"
    num_cols = decoded.get("num_cols")
    if num_cols is None:
        nested = decoded.get("content")
        if isinstance(nested, dict):
            num_cols = nested.get("num_cols")
    assert num_cols == 3, f"num_cols did not round-trip: {num_cols!r}"


def test_matrix_save_decoded_payload_is_not_the_stripped_envelope():
    """Guard against a regression to the broken ``Matrix.get_content``.

    The pre-fix shape (the live bug) decodes to roughly
    ``{"content": {"file_path": ...}, "data": ...}`` -- no grid.
    After the GREEN fix, the decoded payload must NOT be that
    shape; the canonical envelope must carry grid/formulas/num_rows/
    num_cols alongside file_path.
    """
    cells = {
        (0, 0): "alpha",
        (0, 1): "beta",
        (0, 2): "gamma",
        (1, 0): "=1+2",
        (1, 1): "delta",
        (1, 2): "epsilon",
    }
    store = _CapturingStore()
    matrix = _bare_matrix(rows=2, cols=3, cells=cells, did="matrix-2")
    matrix.app = _build_capture_app(store)
    matrix.app.model = _build_model_with(store)

    captured_payloads = []
    original = store.store_doc_media_content

    def capture_and_store(payload):
        captured_payloads.append(dict(payload))
        original(payload)

    store.store_doc_media_content = capture_and_store

    matrix.save()

    assert captured_payloads, "save() did not reach store_doc_media_content"
    decoded = _decode_payload(captured_payloads[-1])

    # The legacy broken shape was:
    #   {"content": {"file_path": ...}, "data": ...}
    # i.e. decoded["content"] only had {"file_path": ...} -- no grid.
    # After GREEN, decoded["content"] must carry grid+formulas too
    # (or the top-level dict carries them).
    nested = decoded.get("content") if isinstance(decoded.get("content"), dict) else {}
    has_grid = "grid" in decoded or "grid" in nested
    assert has_grid, (
        "Decoded payload is the stripped canonical envelope "
        "(no grid).  Matrix.get_content still overwrites the "
        "document.content that Matrix.save() just wrote.  This "
        "is the live T-NEW-149 slice-3 bug."
    )


def test_matrix_save_empty_table_roundtrips_through_full_db_chain():
    """Empty-matrix case must also round-trip cleanly through the DB chain.

    An empty table (0 rows / 0 cols) must produce a payload that
    decodes back to ``{"grid": []}`` (or the canonical envelope
    with empty grid).  The reader-side reopen path expects this
    shape to build a 0x0 table without crashing.
    """
    store = _CapturingStore()
    matrix = _bare_matrix(rows=0, cols=0, cells={}, did="matrix-empty")
    matrix.app = _build_capture_app(store)
    matrix.app.model = _build_model_with(store)

    captured_payloads = []
    original = store.store_doc_media_content

    def capture_and_store(payload):
        captured_payloads.append(dict(payload))
        original(payload)

    store.store_doc_media_content = capture_and_store

    matrix.save()

    assert captured_payloads, "save() did not reach store_doc_media_content"
    decoded = _decode_payload(captured_payloads[-1])

    grid = decoded.get("grid")
    if grid is None:
        nested = decoded.get("content")
        if isinstance(nested, dict):
            grid = nested.get("grid")
    assert grid == [], (
        f"empty-matrix payload did not round-trip cleanly: {grid!r}"
    )

    num_rows = decoded.get("num_rows")
    if num_rows is None:
        nested = decoded.get("content")
        if isinstance(nested, dict):
            num_rows = nested.get("num_rows")
    assert num_rows == 0, f"empty-matrix num_rows did not round-trip: {num_rows!r}"
    num_cols = decoded.get("num_cols")
    if num_cols is None:
        nested = decoded.get("content")
        if isinstance(nested, dict):
            num_cols = nested.get("num_cols")
    assert num_cols == 0, f"empty-matrix num_cols did not round-trip: {num_cols!r}"