"""Regression tests for the T-NEW-074 .pyof content import contract."""

import inspect
import sqlite3

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
