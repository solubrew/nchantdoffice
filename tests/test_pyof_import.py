"""Regression tests for the T-NEW-074 .pyof content import contract."""

import sqlite3

from nchantdoffice.utilities.pyof_import import PyofImportContract, TableSpec


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
