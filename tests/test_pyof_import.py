"""Regression tests for the T-NEW-074 .pyof content import contract."""

import inspect
import sqlite3
import tempfile
import uuid

from nchantdoffice.utilities.pyof_import import PyofImportContract, TableSpec, iter_table_rows


def test_import_contract_tables_match_expected_schema() -> None:
    """T-NEW-074 keeps the content-only import tables and PKs explicit and ordered."""
    expected: tuple[tuple[str, str], ...] = (
        ("app_tree_node", "nid_txt"),
        ("doc_tree_node", "nid_txt"),
        ("app_tab", "tid_txt"),
        ("doc_tab", "tid_txt"),
        ("app_media", "UUID"),
        ("doc_media", "UUID"),
    )

    assert len(PyofImportContract.TABLES) == len(expected)
    for spec, (name, pk_column) in zip(PyofImportContract.TABLES, expected):
        assert isinstance(spec, TableSpec)
        assert spec.name == name
        assert spec.pk_column == pk_column


def test_count_rows_in_table_reads_source() -> None:
    """T-NEW-074: count_rows_in_table returns the row count of a source table."""
    from nchantdoffice.utilities.pyof_import import count_rows_in_table

    conn = sqlite3.connect(":memory:")
    try:
        conn.execute("CREATE TABLE foo (id INTEGER PRIMARY KEY, value TEXT)")
        conn.executemany(
            "INSERT INTO foo (value) VALUES (?)",
            [("a",), ("b",), ("c",)],
        )
        conn.commit()
        assert count_rows_in_table(conn, "foo") == 3

        # Empty table case.
        conn.execute("CREATE TABLE empty (id INTEGER PRIMARY KEY, value TEXT)")
        assert count_rows_in_table(conn, "empty") == 0
    finally:
        conn.close()


def test_iter_table_rows_yields_dicts() -> None:
    """T-NEW-074: iter_table_rows yields dictionaries and handles empty tables."""
    conn = sqlite3.connect(":memory:")
    try:
        conn.execute("CREATE TABLE bar (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")
        conn.executemany(
            "INSERT INTO bar (name, age) VALUES (?, ?)",
            [("Alice", 30), ("Bob", 42)],
        )
        conn.commit()

        generator = iter_table_rows(conn, "bar")
        assert inspect.isgenerator(generator)
        rows = list(generator)
        assert isinstance(rows, list)
        assert len(rows) == 2
        assert rows == [
            {"id": 1, "name": "Alice", "age": 30},
            {"id": 2, "name": "Bob", "age": 42},
        ]
        assert all(set(row) == {"id", "name", "age"} for row in rows)

        conn.execute("CREATE TABLE empty_bar (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")
        assert list(iter_table_rows(conn, "empty_bar")) == []
    finally:
        conn.close()


def test_import_one_table_inserts_new_rows() -> None:
    """T-NEW-074: import_one_table inserts all source rows when host has none."""
    from nchantdoffice.utilities.pyof_import import ImportResult, import_one_table

    src = sqlite3.connect(":memory:")
    host = sqlite3.connect(":memory:")
    try:
        for conn in (src, host):
            conn.execute('CREATE TABLE "foo" (id INTEGER PRIMARY KEY, val TEXT)')
            conn.commit()

        src.executemany(
            'INSERT INTO "foo" (id, val) VALUES (?, ?)',
            [(1, "a"), (2, "b"), (3, "c")],
        )
        src.commit()

        result = import_one_table(src, host, TableSpec("foo", "id"))

        assert result == ImportResult(table="foo", inserted=3, skipped=0, errors=0)
        assert host.execute('SELECT COUNT(*) FROM "foo"').fetchone()[0] == 3
    finally:
        src.close()
        host.close()


def test_import_one_table_skips_pk_collisions() -> None:
    """T-NEW-074: import_one_table INSERT-OR-IGNOREs on PK collision; host wins."""
    from nchantdoffice.utilities.pyof_import import ImportResult, import_one_table

    src = sqlite3.connect(":memory:")
    host = sqlite3.connect(":memory:")
    try:
        for conn in (src, host):
            conn.execute('CREATE TABLE "foo" (id INTEGER PRIMARY KEY, val TEXT)')
            conn.commit()

        src.executemany(
            'INSERT INTO "foo" (id, val) VALUES (?, ?)',
            [(1, "src_a"), (2, "src_b"), (3, "src_c")],
        )
        src.commit()

        # Pre-populate host with 2 of the 3 source rows but with DIFFERENT vals.
        host.executemany(
            'INSERT INTO "foo" (id, val) VALUES (?, ?)',
            [(1, "host_a"), (2, "host_b")],
        )
        host.commit()

        result = import_one_table(src, host, TableSpec("foo", "id"))

        assert result.inserted == 1
        assert result.skipped == 2
        assert result.errors == 0

        rows = {
            r[0]: r[1]
            for r in host.execute('SELECT id, val FROM "foo" ORDER BY id').fetchall()
        }
        assert rows == {1: "host_a", 2: "host_b", 3: "src_c"}
    finally:
        src.close()
        host.close()


def test_import_one_table_handles_missing_table_on_host() -> None:
    """T-NEW-074: import_one_table is a defensive no-op when the host table is absent."""
    from nchantdoffice.utilities.pyof_import import ImportResult, import_one_table

    src = sqlite3.connect(":memory:")
    host = sqlite3.connect(":memory:")
    try:
        # src has 'foo', host does not.
        src.execute('CREATE TABLE "foo" (id INTEGER PRIMARY KEY, val TEXT)')
        src.executemany(
            'INSERT INTO "foo" (id, val) VALUES (?, ?)',
            [(1, "a"), (2, "b")],
        )
        src.commit()

        result = import_one_table(src, host, TableSpec("foo", "id"))

        assert result.inserted == 0
        assert result.skipped == 0
        assert result.errors == 0
        assert result.table == "foo"
    finally:
        src.close()
        host.close()


def test_import_pyof_returns_summary_per_table() -> None:
    """T-NEW-074: import_pyof orchestrates all six contract tables in one transaction."""
    from nchantdoffice.utilities.pyof_import import (
        ImportResult,
        count_rows_in_table,
        import_pyof,
    )

    # Minimal CREATE statements per the task spec — sufficient for the contract.
    create_statements: dict[str, str] = {
        "app_tree_node": (
            'CREATE TABLE "app_tree_node" '
            '(nid_txt TEXT PRIMARY KEY, name_txt TEXT)'
        ),
        "doc_tree_node": (
            'CREATE TABLE "doc_tree_node" '
            '(nid_txt TEXT PRIMARY KEY, pid_txt TEXT, name_txt TEXT)'
        ),
        "app_tab": (
            'CREATE TABLE "app_tab" '
            '(tid_txt TEXT PRIMARY KEY, pid_txt TEXT, name_txt TEXT)'
        ),
        "doc_tab": (
            'CREATE TABLE "doc_tab" '
            '(tid_txt TEXT PRIMARY KEY, pid_txt TEXT, name_txt TEXT)'
        ),
        "app_media": (
            'CREATE TABLE "app_media" '
            '(UUID TEXT PRIMARY KEY, name_txt TEXT)'
        ),
        "doc_media": (
            'CREATE TABLE "doc_media" '
            '(UUID TEXT PRIMARY KEY, name_txt TEXT)'
        ),
    }
    # Per-table insert templates — (table_name, sql, params-template).
    insert_specs: dict[str, tuple[str, tuple]] = {
        "app_tree_node": (
            'INSERT INTO "app_tree_node" (nid_txt, name_txt) VALUES (?, ?)',
            ("nid_txt", "name_txt"),
        ),
        "doc_tree_node": (
            'INSERT INTO "doc_tree_node" (nid_txt, pid_txt, name_txt) VALUES (?, ?, ?)',
            ("nid_txt", "pid_txt", "name_txt"),
        ),
        "app_tab": (
            'INSERT INTO "app_tab" (tid_txt, pid_txt, name_txt) VALUES (?, ?, ?)',
            ("tid_txt", "pid_txt", "name_txt"),
        ),
        "doc_tab": (
            'INSERT INTO "doc_tab" (tid_txt, pid_txt, name_txt) VALUES (?, ?, ?)',
            ("tid_txt", "pid_txt", "name_txt"),
        ),
        "app_media": (
            'INSERT INTO "app_media" (UUID, name_txt) VALUES (?, ?)',
            ("UUID", "name_txt"),
        ),
        "doc_media": (
            'INSERT INTO "doc_media" (UUID, name_txt) VALUES (?, ?)',
            ("UUID", "name_txt"),
        ),
    }

    # Build source DB on disk so import_pyof can open it via file: URI.
    with tempfile.NamedTemporaryFile(suffix=".pyof", delete=False) as src_file:
        source_path = src_file.name
    src = sqlite3.connect(source_path)
    try:
        for table, ddl in create_statements.items():
            src.execute(ddl)
        # Populate one synthetic UUID row per table.
        for table, (sql, cols) in insert_specs.items():
            synth = str(uuid.uuid4())
            values = [synth] + [f"{table}-row"] * (len(cols) - 1)
            src.execute(sql, values)
        src.commit()
    finally:
        src.close()

    # In-memory host with the same six tables (empty) — avoids the defensive no-op.
    host = sqlite3.connect(":memory:")
    try:
        for table, ddl in create_statements.items():
            host.execute(ddl)
        host.commit()

        results = import_pyof(source_path, host)

        assert len(results) == 6
        expected_tables = [
            "app_tree_node",
            "doc_tree_node",
            "app_tab",
            "doc_tab",
            "app_media",
            "doc_media",
        ]
        assert [r.table for r in results] == expected_tables
        for r in results:
            assert r == ImportResult(table=r.table, inserted=1, skipped=0, errors=0)
        for table in expected_tables:
            assert count_rows_in_table(host, table) == 1
    finally:
        host.close()
        # Clean up the on-disk source.
        import os
        try:
            os.unlink(source_path)
        except OSError:
            pass
