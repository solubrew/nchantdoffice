"""T-NEW-143 regression: .pyof import excludes ``DELETE_BIT=1`` rows.

**Source rows with ``DELETE_BIT=1`` get imported into the host.**

The T-NEW-074 / T-NEW-075 / T-NEW-076 / T-NEW-077 import contract
copies rows verbatim from source to host. For the base-6 tables
(``app_tree_node``, ``doc_tree_node``, ``app_tab``, ``doc_tab``,
``app_media``, ``doc_media``), the source schema carries a
``DELETE_BIT`` flag (squirl soft-delete) and rows with
``DELETE_BIT=1`` are tombstones. The current
``import_one_table`` does not filter them, so a tombstoned source
row resurrects on the host when the user imports the .pyof. The
content tables (``_content`` suffix) don't have DELETE_BIT (they
are versioned, not soft-deleted) so the filter is unnecessary
there.

The fix:
1. In ``import_one_table`` (the base-6 branch), skip any source
   row where ``DELETE_BIT`` exists AND is non-zero. Treat NULL
   and missing-column as "not deleted" (older schemas tolerated).
3. Test surface in ``tests/test_t_new_143_delete_bit_filter.py``
   (this file).

Migration plan (no priority / low priority -- design decision
first): the ``_content`` branch is untouched -- DELETE_BIT is
not a concept there. The base-6 branch adds a per-row DELETE_BIT
check at the top of the ``iter_table_rows`` loop. The check is
defensive: if the column doesn't exist on the source schema the
filter is skipped (silent no-op for that row), matching the
existing column-intersection tolerance.
"""
import inspect
import os
import sqlite3
import tempfile
from pathlib import Path

# T-NEW-074 Task 9: keep Qt on the headless offscreen platform before any
# PySide6 import so the integration test does not need a real display.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402

from nchantdoffice.utilities.pyof_import import (
    PyofImportContract,
    TableSpec,
    import_pyof,
)


def _make_source_db(tmp_path: Path) -> Path:
    """Create a source .pyof with the full contract schema, with
    DELETE_BIT on the base 6 tables. Returns the path."""
    src_path = tmp_path / "source.pyof"
    conn = sqlite3.connect(str(src_path))
    # Base 6 + content tables
    schema_sql = """
        CREATE TABLE app_tree_node (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            nid_txt TEXT NOT NULL,
            name_txt TEXT,
            type_txt TEXT,
            pid_txt TEXT,
            DELETE_BIT INTEGER DEFAULT 0
        );
        CREATE TABLE doc_tree_node (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            nid_txt TEXT NOT NULL,
            name_txt TEXT,
            type_txt TEXT,
            pid_txt TEXT,
            DELETE_BIT INTEGER DEFAULT 0
        );
        CREATE TABLE app_tab (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            tid_txt TEXT NOT NULL,
            name_txt TEXT,
            did_id TEXT,
            pid_txt TEXT,
            DELETE_BIT INTEGER DEFAULT 0
        );
        CREATE TABLE doc_tab (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            tid_txt TEXT NOT NULL,
            name_txt TEXT,
            did_id TEXT,
            pid_txt TEXT,
            DELETE_BIT INTEGER DEFAULT 0
        );
        CREATE TABLE app_media (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            UUID TEXT NOT NULL,
            name_txt TEXT,
            pid_txt TEXT,
            DELETE_BIT INTEGER DEFAULT 0
        );
        CREATE TABLE doc_media (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            UUID TEXT NOT NULL,
            name_txt TEXT,
            pid_txt TEXT,
            DELETE_BIT INTEGER DEFAULT 0
        );
        CREATE TABLE app_doc_content (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            UUID TEXT,
            pUUID TEXT,
            version INTEGER,
            content BLOB
        );
        CREATE TABLE app_media_content (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            UUID TEXT,
            pUUID TEXT,
            version INTEGER,
            content BLOB
        );
        CREATE TABLE doc_media_content (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            UUID TEXT,
            pUUID TEXT,
            version INTEGER,
            content BLOB
        );
    """
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()
    return src_path


def _make_host_db(tmp_path: Path) -> Path:
    """Create an empty host .pyof with the full contract schema.
    Returns the path."""
    host_path = tmp_path / "host.pyof"
    conn = sqlite3.connect(str(host_path))
    schema_sql = """
        CREATE TABLE app_tree_node (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            nid_txt TEXT NOT NULL,
            name_txt TEXT,
            type_txt TEXT,
            pid_txt TEXT,
            DELETE_BIT INTEGER DEFAULT 0
        );
        CREATE TABLE doc_tree_node (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            nid_txt TEXT NOT NULL,
            name_txt TEXT,
            type_txt TEXT,
            pid_txt TEXT,
            DELETE_BIT INTEGER DEFAULT 0
        );
        CREATE TABLE app_tab (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            tid_txt TEXT NOT NULL,
            name_txt TEXT,
            did_id TEXT,
            pid_txt TEXT,
            DELETE_BIT INTEGER DEFAULT 0
        );
        CREATE TABLE doc_tab (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            tid_txt TEXT NOT NULL,
            name_txt TEXT,
            did_id TEXT,
            pid_txt TEXT,
            DELETE_BIT INTEGER DEFAULT 0
        );
        CREATE TABLE app_media (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            UUID TEXT NOT NULL,
            name_txt TEXT,
            pid_txt TEXT,
            DELETE_BIT INTEGER DEFAULT 0
        );
        CREATE TABLE doc_media (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            UUID TEXT NOT NULL,
            name_txt TEXT,
            pid_txt TEXT,
            DELETE_BIT INTEGER DEFAULT 0
        );
        CREATE TABLE app_doc_content (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            UUID TEXT,
            pUUID TEXT,
            version INTEGER,
            content BLOB
        );
        CREATE TABLE app_media_content (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            UUID TEXT,
            pUUID TEXT,
            version INTEGER,
            content BLOB
        );
        CREATE TABLE doc_media_content (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            UUID TEXT,
            pUUID TEXT,
            version INTEGER,
            content BLOB
        );
    """
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()
    return host_path


def _insert_source_rows(src_path: Path, table: str, rows: list[dict]) -> None:
    conn = sqlite3.connect(str(src_path))
    cols = list(rows[0].keys()) if rows else []
    placeholders = ",".join("?" for _ in cols)
    col_list = ",".join(cols)
    for row in rows:
        conn.execute(
            f"INSERT INTO {table} ({col_list}) VALUES ({placeholders})",
            [row[c] for c in cols],
        )
    conn.commit()
    conn.close()


def _count_rows(db_path: Path, table: str) -> int:
    conn = sqlite3.connect(str(db_path))
    cur = conn.execute(f"SELECT COUNT(*) FROM {table}")
    n = cur.fetchone()[0]
    conn.close()
    return n


def _row_exists(db_path: Path, table: str, where_clause: str, params: tuple) -> bool:
    conn = sqlite3.connect(str(db_path))
    cur = conn.execute(f"SELECT 1 FROM {table} WHERE {where_clause}", params)
    exists = cur.fetchone() is not None
    conn.close()
    return exists


# ---------------------------------------------------------------------------
# Source-level pin: import_one_table must inspect DELETE_BIT
# ---------------------------------------------------------------------------

def test_import_one_table_filters_delete_bit():
    """Source-level: the base-6 branch of import_one_table must inspect
    DELETE_BIT on every source row. Rows with DELETE_BIT=1 must be
    excluded from the host. The current code does not check the
    column.
    """
    from nchantdoffice.utilities.pyof_import import import_one_table
    src = inspect.getsource(import_one_table)
    assert "DELETE_BIT" in src, (
        "import_one_table (base-6 branch) must inspect DELETE_BIT "
        "(T-NEW-143). Source:\n" + src[:1500]
    )


# ---------------------------------------------------------------------------
# End-to-end: deleted source rows do NOT land on the host
# ---------------------------------------------------------------------------

def test_doc_tree_node_with_delete_bit_1_is_excluded(tmp_path):
    """T-NEW-143 (e2e): a doc_tree_node source row with DELETE_BIT=1
    must NOT be inserted into the host. The current code copies it
    verbatim (the bug).
    """
    src_path = _make_source_db(tmp_path)
    host_path = _make_host_db(tmp_path)

    _insert_source_rows(
        src_path,
        "doc_tree_node",
        [
            {"nid_txt": "live-1", "name_txt": "LiveNode", "type_txt": "doc",
             "pid_txt": None, "DELETE_BIT": 0},
            {"nid_txt": "dead-1", "name_txt": "Tombstone", "type_txt": "doc",
             "pid_txt": None, "DELETE_BIT": 1},
            {"nid_txt": "live-2", "name_txt": "AnotherLive", "type_txt": "doc",
             "pid_txt": None, "DELETE_BIT": 0},
        ],
    )

    host_conn = sqlite3.connect(str(host_path))
    try:
        import_pyof(str(src_path), host_conn)
    finally:
        host_conn.close()

    # Host should have ONLY the two live rows, not the tombstone.
    n_total = _count_rows(host_path, "doc_tree_node")
    assert n_total == 2, (
        f"Host doc_tree_node must contain 2 live rows (DELETE_BIT=0); "
        f"got {n_total}. Tombstone row (DELETE_BIT=1) must be excluded "
        f"(T-NEW-143)."
    )

    # Tombstone must be specifically excluded
    assert not _row_exists(host_path, "doc_tree_node",
                          "nid_txt = ?", ("dead-1",)), (
        "Tombstone row (nid_txt='dead-1', DELETE_BIT=1) leaked into host "
        "(T-NEW-143)."
    )
    # Live rows must be present
    assert _row_exists(host_path, "doc_tree_node", "nid_txt = ?", ("live-1",))
    assert _row_exists(host_path, "doc_tree_node", "nid_txt = ?", ("live-2",))


def test_app_tab_with_delete_bit_1_is_excluded(tmp_path):
    """Same contract as doc_tree_node but for app_tab. Tombstones
    excluded; live rows copied."""
    src_path = _make_source_db(tmp_path)
    host_path = _make_host_db(tmp_path)

    _insert_source_rows(
        src_path,
        "app_tab",
        [
            {"tid_txt": "tab-live", "name_txt": "Live", "did_id": None,
             "pid_txt": None, "DELETE_BIT": 0},
            {"tid_txt": "tab-dead", "name_txt": "Dead", "did_id": None,
             "pid_txt": None, "DELETE_BIT": 1},
        ],
    )

    host_conn = sqlite3.connect(str(host_path))
    try:
        import_pyof(str(src_path), host_conn)
    finally:
        host_conn.close()

    assert _count_rows(host_path, "app_tab") == 1
    assert _row_exists(host_path, "app_tab", "tid_txt = ?", ("tab-live",))
    assert not _row_exists(host_path, "app_tab", "tid_txt = ?", ("tab-dead",))


def test_all_base_6_tables_exclude_delete_bit(tmp_path):
    """T-NEW-143 (broad): the DELETE_BIT filter must apply to ALL
    base 6 tables, not just doc_tree_node."""
    src_path = _make_source_db(tmp_path)
    host_path = _make_host_db(tmp_path)

    # Insert live+dead rows in each base 6 table.
    _insert_source_rows(
        src_path, "app_tree_node",
        [
            {"nid_txt": "atn-live", "name_txt": "Live", "type_txt": "app",
             "pid_txt": None, "DELETE_BIT": 0},
            {"nid_txt": "atn-dead", "name_txt": "Dead", "type_txt": "app",
             "pid_txt": None, "DELETE_BIT": 1},
        ],
    )
    _insert_source_rows(
        src_path, "doc_tree_node",
        [
            {"nid_txt": "dtn-live", "name_txt": "Live", "type_txt": "doc",
             "pid_txt": None, "DELETE_BIT": 0},
            {"nid_txt": "dtn-dead", "name_txt": "Dead", "type_txt": "doc",
             "pid_txt": None, "DELETE_BIT": 1},
        ],
    )
    _insert_source_rows(
        src_path, "app_tab",
        [
            {"tid_txt": "at-live", "name_txt": "Live", "did_id": None,
             "pid_txt": None, "DELETE_BIT": 0},
            {"tid_txt": "at-dead", "name_txt": "Dead", "did_id": None,
             "pid_txt": None, "DELETE_BIT": 1},
        ],
    )
    _insert_source_rows(
        src_path, "doc_tab",
        [
            {"tid_txt": "dt-live", "name_txt": "Live", "did_id": None,
             "pid_txt": None, "DELETE_BIT": 0},
            {"tid_txt": "dt-dead", "name_txt": "Dead", "did_id": None,
             "pid_txt": None, "DELETE_BIT": 1},
        ],
    )
    _insert_source_rows(
        src_path, "app_media",
        [
            {"UUID": "am-live", "name_txt": "Live", "pid_txt": None,
             "DELETE_BIT": 0},
            {"UUID": "am-dead", "name_txt": "Dead", "pid_txt": None,
             "DELETE_BIT": 1},
        ],
    )
    _insert_source_rows(
        src_path, "doc_media",
        [
            {"UUID": "dm-live", "name_txt": "Live", "pid_txt": None,
             "DELETE_BIT": 0},
            {"UUID": "dm-dead", "name_txt": "Dead", "pid_txt": None,
             "DELETE_BIT": 1},
        ],
    )

    host_conn = sqlite3.connect(str(host_path))
    try:
        import_pyof(str(src_path), host_conn)
    finally:
        host_conn.close()

    # Every dead row must be absent; every live row present.
    expectations = [
        ("app_tree_node", "nid_txt", "atn-dead", "atn-live"),
        ("doc_tree_node", "nid_txt", "dtn-dead", "dtn-live"),
        ("app_tab", "tid_txt", "at-dead", "at-live"),
        ("doc_tab", "tid_txt", "dt-dead", "dt-live"),
        ("app_media", "UUID", "am-dead", "am-live"),
        ("doc_media", "UUID", "dm-dead", "dm-live"),
    ]
    for table, id_col, dead_id, live_id in expectations:
        assert not _row_exists(host_path, table,
                              f"{id_col} = ?", (dead_id,)), (
            f"Tombstone row leaked into {table} ({id_col}={dead_id!r}, "
            f"DELETE_BIT=1) (T-NEW-143)."
        )
        assert _row_exists(host_path, table,
                          f"{id_col} = ?", (live_id,)), (
            f"Live row missing in {table} ({id_col}={live_id!r}, "
            f"DELETE_BIT=0) (T-NEW-143)."
        )


def test_null_delete_bit_is_treated_as_live(tmp_path):
    """Defensive: NULL DELETE_BIT must be treated as "not deleted"
    (live), matching squirl's default semantics where missing
    DELETE_BIT means the row was written by an older schema."""
    src_path = _make_source_db(tmp_path)
    host_path = _make_host_db(tmp_path)

    _insert_source_rows(
        src_path, "doc_tree_node",
        [
            {"nid_txt": "live-null", "name_txt": "Live", "type_txt": "doc",
             "pid_txt": None, "DELETE_BIT": None},
        ],
    )
    host_conn = sqlite3.connect(str(host_path))
    try:
        import_pyof(str(src_path), host_conn)
    finally:
        host_conn.close()
    assert _row_exists(host_path, "doc_tree_node", "nid_txt = ?",
                      ("live-null",)), (
        "DELETE_BIT=NULL must be treated as live (T-NEW-143)."
    )


def test_source_schema_without_delete_bit_column_still_imports(tmp_path):
    """Backward compat: source schemas that pre-date DELETE_BIT must
    continue to import all rows. The filter must skip when the
    column is absent (defensive: older schemas don't carry it)."""
    src_path = tmp_path / "old_source.pyof"
    host_path = _make_host_db(tmp_path)

    # Build a source schema WITHOUT DELETE_BIT on any table.
    conn = sqlite3.connect(str(src_path))
    conn.executescript("""
        CREATE TABLE doc_tree_node (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            nid_txt TEXT NOT NULL,
            name_txt TEXT,
            type_txt TEXT,
            pid_txt TEXT
        );
        CREATE TABLE app_doc_content (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            UUID TEXT,
            pUUID TEXT,
            version INTEGER,
            content BLOB
        );
        CREATE TABLE app_media_content (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            UUID TEXT,
            pUUID TEXT,
            version INTEGER,
            content BLOB
        );
        CREATE TABLE doc_media_content (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            UUID TEXT,
            pUUID TEXT,
            version INTEGER,
            content BLOB
        );
        CREATE TABLE app_tree_node (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            nid_txt TEXT NOT NULL,
            name_txt TEXT,
            type_txt TEXT,
            pid_txt TEXT
        );
        CREATE TABLE app_tab (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            tid_txt TEXT NOT NULL,
            name_txt TEXT,
            did_id TEXT,
            pid_txt TEXT
        );
        CREATE TABLE doc_tab (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            tid_txt TEXT NOT NULL,
            name_txt TEXT,
            did_id TEXT,
            pid_txt TEXT
        );
        CREATE TABLE app_media (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            UUID TEXT NOT NULL,
            name_txt TEXT,
            pid_txt TEXT
        );
        CREATE TABLE doc_media (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            UUID TEXT NOT NULL,
            name_txt TEXT,
            pid_txt TEXT
        );
    """)
    conn.execute(
        "INSERT INTO doc_tree_node (nid_txt, name_txt, type_txt, pid_txt) "
        "VALUES (?, ?, ?, ?)",
        ("old-node", "Old", "doc", None),
    )
    conn.commit()
    conn.close()

    host_conn = sqlite3.connect(str(host_path))
    try:
        # Must not raise. The schema mismatch on the base 6 tables
        # is handled by _intersecting_columns.
        import_pyof(str(src_path), host_conn)
    finally:
        host_conn.close()

    assert _row_exists(host_path, "doc_tree_node", "nid_txt = ?",
                      ("old-node",)), (
        "Source row from a schema without DELETE_BIT must still be "
        "imported (T-NEW-143 backward compat)."
    )