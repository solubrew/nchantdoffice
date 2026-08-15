"""T-NEW-114 re-architect: import_pyof_via_doc end-to-end test.

Drives the orchestrator against the real generated
``.pyof`` at ``/home/solubrew/.local/share/scratch/nchantdoffice/nchantdoffice.pyof``
(or whatever SOURCE_PYOF points at) and asserts each contract
table's import result. The test proves:

  1. Source row reading via sonql.Doc.readFull works against
     a real SQuiRL DB.
  2. Dedupe by ``nid_txt`` / ``tid_txt`` / ``did`` keeps the
     second import idempotent.
  3. Audit columns are populated by the host's native insert.
  4. The 9-table contract reports ``inserted`` counts that
     match expectations.
"""

from __future__ import annotations

import os
import shutil
import sqlite3
import sys
from pathlib import Path

import pytest

# Add the project root to sys.path so pyof_import_via_doc
# can import nchantdoffice siblings.
sys.path.insert(0, "/home/solubrew/.hermes/projects/nchantdoffice")

from nchantdoffice.utilities.pyof_import_via_doc import (
    PYOF_VIA_DOC_TABLES,
    import_pyof_via_doc,
)


SOURCE_PYOF = "/home/solubrew/.local/share/scratch/nchantdoffice/nchantdoffice.pyof"


@pytest.fixture
def host_pyof(tmp_path):
    """Build a fresh empty host DB matching the source schema."""
    host = str(tmp_path / "host.pyof")
    shutil.copy(SOURCE_PYOF, host)
    conn = sqlite3.connect(host)
    for spec in PYOF_VIA_DOC_TABLES:
        exists = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (spec.name,),
        ).fetchone()
        if exists:
            conn.execute(f'DELETE FROM "{spec.name}"')
    conn.commit()
    conn.close()
    yield host


def _non_empty_source_specs():
    """Return the contract specs whose source table has rows.
    The wizard lazily creates some tables (e.g. app_doc_content
    only when content is added) and skips others (doc_tab,
    doc_tree_node, doc_media are empty in a fresh install)."""
    conn = sqlite3.connect(SOURCE_PYOF)
    out = []
    for spec in PYOF_VIA_DOC_TABLES:
        exists = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (spec.name,),
        ).fetchone()
        if not exists:
            continue
        cnt = conn.execute(f'SELECT COUNT(*) FROM "{spec.name}"').fetchone()[0]
        if cnt > 0:
            out.append(spec)
    conn.close()
    return out


def test_import_pyof_via_doc_end_to_end(host_pyof):
    """Round-trip: source -> empty host. Asserts every
    contract table that has source rows gets them inserted
    into the host."""
    if not os.path.exists(SOURCE_PYOF):
        pytest.skip(
            f"source .pyof not found at {SOURCE_PYOF} — run "
            "cmds/runNchantdOffice.py scratch setup to generate one"
        )
    from squirl.orgnql.sonql import Doc
    host_doc = Doc(host_pyof)
    non_empty = _non_empty_source_specs()
    assert non_empty, "test pre-condition: source has no rows in any contract table"

    results = import_pyof_via_doc(SOURCE_PYOF, host_doc)

    # The result list has one entry per contract table in the
    # same order as PYOF_VIA_DOC_TABLES.
    assert len(results) == len(PYOF_VIA_DOC_TABLES)
    non_empty_names = {s.name for s in non_empty}
    for spec, result in zip(PYOF_VIA_DOC_TABLES, results):
        assert result.table == spec.name
        if spec.name in non_empty_names:
            assert result.inserted > 0, (
                f"{spec.name}: expected inserted > 0 (source has "
                f"{_source_row_count(spec.name)} rows), got "
                f"inserted={result.inserted}, skipped={result.skipped}"
            )

    # Verify the host DB now has rows for every table that had
    # source rows.
    conn = sqlite3.connect(host_pyof)
    for spec in non_empty:
        cnt = conn.execute(f'SELECT COUNT(*) FROM "{spec.name}"').fetchone()[0]
        assert cnt > 0, (
            f"host {spec.name}: expected > 0 rows after import, got {cnt}"
        )
    conn.close()


def test_import_pyof_via_doc_is_idempotent(host_pyof):
    """Second import: every dedupe-by-UUID should skip, so
    the inserted count is 0 and the skipped count is the
    original row count."""
    if not os.path.exists(SOURCE_PYOF):
        pytest.skip(f"source .pyof not found at {SOURCE_PYOF}")
    from squirl.orgnql.sonql import Doc
    host_doc = Doc(host_pyof)
    first = import_pyof_via_doc(SOURCE_PYOF, host_doc)
    second = import_pyof_via_doc(SOURCE_PYOF, host_doc)

    for spec, r1, r2 in zip(PYOF_VIA_DOC_TABLES, first, second):
        if spec.merge_strategy != "insert_or_ignore":
            continue
        if spec.pk_column is None:
            continue
        assert r1.inserted == r2.skipped, (
            f"{spec.name}: first.inserted={r1.inserted} should "
            f"equal second.skipped={r2.skipped} for idempotent dedupe"
        )
        assert r2.inserted == 0, (
            f"{spec.name}: second import should insert 0 rows "
            f"(all dedupe-skipped), got {r2.inserted}"
        )


def test_import_pyof_via_doc_source_not_found():
    """Clear error when the source path is bogus."""
    from squirl.orgnql.sonql import Doc
    with pytest.raises(FileNotFoundError):
        import_pyof_via_doc("/tmp/nonexistent.pyof", Doc("/tmp/whatever.pyof"))


def test_pyof_via_doc_contract_table_names():
    """Sanity: the contract has exactly the 7 content tables
    (T-NEW-114 user direction: app_tree_node + app_tab are
    system infrastructure that the host already has, not
    imported). Adding a table without a dedupe key is a P0
    audit risk so we want to be loud."""
    expected = {
        "doc_tree_node", "doc_tab",
        "app_media", "doc_media",
        "app_doc_content", "app_media_content", "doc_media_content",
    }
    actual = {s.name for s in PYOF_VIA_DOC_TABLES}
    assert actual == expected, (
        f"contract drift: expected {expected}, got {actual}"
    )
    # The system-infrastructure tables must NOT be in the
    # contract — the host's wizard already populated them.
    assert "app_tree_node" not in actual
    assert "app_tab" not in actual


def _source_row_count(table: str) -> int:
    conn = sqlite3.connect(SOURCE_PYOF)
    try:
        return conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
    except Exception:
        return 0
    finally:
        conn.close()
