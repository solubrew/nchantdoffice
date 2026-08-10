"""T-NEW-065 — Tests for journal-content compaction.

Per `testing-report_20260810.md` line 18:
> "will need a process cto compact the journal
> app_media_content table to stop growth out of control".

The fix adds ``compact_journal_content(max_versions_per_doc=30)``
on ``NchantdOfficeCloakModel`` which:
  1. Reads the ``app_media_content`` table.
  2. Groups rows by ``pUUID`` (parent document UUID).
  3. Marks rows whose per-group rank-by-version_int exceeds
     ``max_versions_per_doc`` for deletion.
  4. Calls ``store.docs[db].delete(table, WHERE-IN)`` with the
     collected UUIDs.

Wired into ``close_application`` so the cleanup runs on every
app exit. Wrapped in try/except so a compaction failure does
NOT block app close.

This file pins 4 invariants the T-NEW-065 implementation
promises:

  1. ``test_compact_keeps_top_versions_per_doc`` — given
     multiple ``pUUID`` groups each with N+ rows, exactly the
     top ``max_versions_per_doc`` versions per group survive;
     the rest are marked for delete.

  2. ``test_compact_calls_bulk_delete`` — the method calls
     ``store.docs[db].delete(table, {"WHERE": {"IN": {"UUID": [...]}}})``
     with the UUIDs of rows to delete.

  3. ``test_compact_is_noop_on_empty_table`` — when the
     table is empty (or the columns are missing), the method
     returns ``(0, 0)`` and does NOT call delete.

  4. ``test_close_application_invokes_compact`` — the
     ``close_application`` hook calls
     ``compact_journal_content()`` exactly once.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd

PROJ_ROOT = Path("/home/solubrew/.hermes/projects/nchantdoffice")
sys.path.insert(0, str(PROJ_ROOT))


def _make_pUUID_rows(pUUID, n_versions):
    """Build ``n_versions`` rows for a single ``pUUID`` with
    monotonically increasing ``version_int``. The last row in
    the list has the highest version.
    """
    return [
        {
            "UUID": f"{pUUID}-v{i}",
            "pUUID": pUUID,
            "page_int": 0,
            "entry_int": i,
            "version_int": i,
            "hash_txt": f"hash-{pUUID}-{i}",
            "content_enc64_txt": "Zm9v",
            "context_ltxt": "",
        }
        for i in range(n_versions)
    ]


def _bare_cloak_model():
    """Return a ``NchantdOfficeCloakModel``-like object that
    has just the attributes ``compact_journal_content`` reads.

    Same pattern as test_update_checker_boot_hook.py —
    avoids Qt singleton + DB construction.
    """
    from nchantdoffice import models as models_mod

    # ``compact_journal_content`` is a real method on the class;
    # bind it to a stub instance so we can test it directly.
    cloak = type("_CloakLite", (), {})()
    cloak.compact_journal_content = (
        models_mod.NchantdOfficeCloakModel.compact_journal_content.__get__(cloak)
    )
    # ``self.store`` is the persistence layer; mock it.
    mock_docs = MagicMock()
    mock_docs.delete = MagicMock()
    mock_store = MagicMock()
    mock_store.docs = {"db": mock_docs}
    cloak.store = mock_store
    cloak._mock_docs = mock_docs
    return cloak


def test_compact_keeps_top_versions_per_doc():
    """Top ``max_versions_per_doc`` versions per pUUID survive;
    the rest are marked for delete."""
    cloak = _bare_cloak_model()
    # Two docs: doc-A has 35 versions, doc-B has 5 versions,
    # max_versions_per_doc=30.
    rows = _make_pUUID_rows("doc-A", 35) + _make_pUUID_rows("doc-B", 5)
    df = pd.DataFrame(rows)
    cloak.store.get_table = MagicMock(return_value=df)
    rows_scanned, rows_deleted = cloak.compact_journal_content(
        max_versions_per_doc=30,
    )
    assert rows_scanned == 40, (
        f"rows_scanned should be 40, got {rows_scanned}"
    )
    # doc-A keeps top 30, deletes 5; doc-B keeps all 5,
    # deletes 0. Total deleted = 5.
    assert rows_deleted == 5, (
        f"rows_deleted should be 5, got {rows_deleted}"
    )
    # Verify the bulk-delete was called with the right UUIDs.
    assert cloak._mock_docs.delete.called, (
        "compact_journal_content should call store.docs[db].delete"
    )
    args, kwargs = cloak._mock_docs.delete.call_args
    table_arg = args[0]
    cfg_arg = args[1] if len(args) > 1 else kwargs.get("cfg")
    assert table_arg == "app_media_content", (
        f"delete should target 'app_media_content', got {table_arg!r}"
    )
    where = cfg_arg.get("WHERE", {})
    in_clause = where.get("IN", {}).get("UUID", [])
    # The 5 deleted UUIDs should be doc-A-v0..v4 (the OLDEST
    # versions of doc-A, since we keep the top 30 by version_int).
    expected = {f"doc-A-v{i}" for i in range(5)}
    actual = set(in_clause)
    assert actual == expected, (
        f"delete UUIDs should be the 5 oldest doc-A versions; "
        f"expected {expected}, got {actual}"
    )


def test_compact_calls_bulk_delete():
    """Method uses WHERE-IN bulk-delete (not per-row)."""
    cloak = _bare_cloak_model()
    rows = _make_pUUID_rows("doc-X", 50)
    df = pd.DataFrame(rows)
    cloak.store.get_table = MagicMock(return_value=df)
    cloak.compact_journal_content(max_versions_per_doc=10)
    # 50 - 10 = 40 should be deleted in a single bulk call.
    assert cloak._mock_docs.delete.call_count == 1, (
        f"compact_journal_content should use ONE bulk delete call, "
        f"not {cloak._mock_docs.delete.call_count} per-row calls."
    )


def test_compact_is_noop_on_empty_table():
    """Empty table returns (0, 0) and does NOT call delete."""
    cloak = _bare_cloak_model()
    cloak.store.get_table = MagicMock(return_value=pd.DataFrame())
    rows_scanned, rows_deleted = cloak.compact_journal_content()
    assert rows_scanned == 0
    assert rows_deleted == 0
    assert not cloak._mock_docs.delete.called, (
        "compact_journal_content should NOT call delete on an empty table"
    )


def test_compact_is_noop_when_columns_missing():
    """Missing required columns → no-op + warning, no delete."""
    cloak = _bare_cloak_model()
    # DataFrame missing pUUID / version_int / UUID
    cloak.store.get_table = MagicMock(
        return_value=pd.DataFrame({"foo": [1, 2, 3]}),
    )
    rows_scanned, rows_deleted = cloak.compact_journal_content()
    assert rows_scanned == 3
    assert rows_deleted == 0
    assert not cloak._mock_docs.delete.called


def test_close_application_invokes_compact():
    """``close_application`` calls ``compact_journal_content()``."""
    from nchantdoffice import models as models_mod

    # Build a minimal stub that has the attributes
    # close_application reads.
    cloak = type("_CloakLite", (), {})()
    cloak.has_changed = False
    cloak.auto_save = MagicMock()
    # compact_journal_content is the real method; mock it to
    # observe the call without running the real DB code.
    cloak.compact_journal_content = MagicMock(return_value=(0, 0))
    # store.compact_database — the existing hook.
    cloak.store = MagicMock()
    # Bind the real close_application method.
    cloak.close_application = (
        models_mod.NchantdOfficeCloakModel.close_application.__get__(cloak)
    )
    cloak.close_application()
    assert cloak.compact_journal_content.called, (
        "T-NEW-065: close_application must invoke "
        "compact_journal_content exactly once."
    )
    assert cloak.compact_journal_content.call_count == 1, (
        f"compact_journal_content called "
        f"{cloak.compact_journal_content.call_count}×; expected 1."
    )
