"""Regression tests for the T-NEW-074 .pyof content import contract."""

import inspect
import os
import sqlite3
import tempfile
import uuid

# T-NEW-074 Task 9: keep Qt on the headless offscreen platform before any
# PySide6 import so the integration test does not need a real display and we
# avoid the shiboken6 SIGSEGV seen earlier in this session on some hosts.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402  (after QT_QPA_PLATFORM setdefault)

from nchantdoffice.utilities.pyof_import import PyofImportContract, TableSpec, iter_table_rows


def test_cmd_import_pyof_attribute_exists() -> None:
    """T-NEW-074 Task 8: NchantdOfficeApplicationToolBox must expose a
    callable ``cmd_import_pyof`` method so the YAML's app_action handler
    string resolves at runtime. The method is intentionally defensive
    (try/except, returns self), so we only assert presence + callable
    here; behavioural coverage lives in the Task 9 integration test.
    """
    from nchantdoffice.widgets.controls.toolboxes import (
        NchantdOfficeApplicationToolBox,
    )

    assert hasattr(NchantdOfficeApplicationToolBox, "cmd_import_pyof")
    assert callable(getattr(NchantdOfficeApplicationToolBox, "cmd_import_pyof"))


def test_resolve_host_db_conn_attribute_exists() -> None:
    """T-NEW-074 Task 8: the defensive helper that walks
    ``self.app.model.store._sqlite_connection`` (and falls back to an
    isinstance scan over parent/app/model/store) must exist as a
    private method on the toolbox.
    """
    from nchantdoffice.widgets.controls.toolboxes import (
        NchantdOfficeApplicationToolBox,
    )

    assert hasattr(NchantdOfficeApplicationToolBox, "_resolve_host_db_conn")
    assert callable(
        getattr(NchantdOfficeApplicationToolBox, "_resolve_host_db_conn")
    )


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


def test_import_pyof_round_trips_against_real_pyof() -> None:
    """T-NEW-074 Task 6: import_pyof round-trips all 6 contract tables against a
    real on-disk .pyof file, asserting both the ImportResult shape and the
    actual row counts on the host."""
    from nchantdoffice.utilities.pyof_import import (
        ImportResult,
        count_rows_in_table,
        import_pyof,
    )

    # Per the contract: same 6 tables as Task 5. Keep these CREATE statements
    # in sync with test_import_pyof_returns_summary_per_table above — they
    # intentionally reflect only the columns this test touches.
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
    insert_specs: dict[str, tuple[str, tuple[str, ...]]] = {
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
    expected_tables = list(create_statements.keys())

    # 1. Build a REAL on-disk .pyof file with all 6 contract tables, one row each.
    src_file = tempfile.NamedTemporaryFile(suffix=".pyof", delete=False)
    source_path = src_file.name
    src_file.close()  # import_pyof opens its own sqlite3 handle via URI.
    try:
        src = sqlite3.connect(source_path)
        try:
            for table, ddl in create_statements.items():
                src.execute(ddl)
            for table, (sql, cols) in insert_specs.items():
                synth = str(uuid.uuid4())
                values = [synth] + [f"{table}-row"] * (len(cols) - 1)
                src.execute(sql, values)
            src.commit()
        finally:
            src.close()

        # 2. Open an EMPTY in-memory host connection and create the same 6
        #    tables on it (per Task 5 schema).
        host = sqlite3.connect(":memory:")
        try:
            for ddl in create_statements.values():
                host.execute(ddl)
            host.commit()

            # Sanity: host is empty before the import.
            for table in expected_tables:
                assert count_rows_in_table(host, table) == 0

            # 3. Run the orchestrator against the real on-disk .pyof.
            results = import_pyof(source_path, host)

            # 4. Assert row counts + ImportResult shape.
            assert [r.table for r in results] == expected_tables
            for r in results:
                assert r == ImportResult(table=r.table, inserted=1, skipped=0, errors=0)
            for table in expected_tables:
                assert count_rows_in_table(host, table) == 1
        finally:
            host.close()
    finally:
        # Clean up the on-disk source.
        import os
        try:
            os.unlink(source_path)
        except OSError:
            pass


def test_import_pyof_silently_skips_missing_tables() -> None:
    """T-NEW-074 Task 6: when the source .pyof only contains a subset of the
    contract tables (here: app_tree_node + app_media), the orchestrator must
    silently no-op the missing tables (inserted=0, skipped=0, errors=0) and
    still import the present ones."""
    from nchantdoffice.utilities.pyof_import import (
        ImportResult,
        count_rows_in_table,
        import_pyof,
    )

    # Same schemas as the round-trip test — host has all 6 tables.
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

    # Source only has app_tree_node + app_media — the other 4 are missing.
    source_tables_present = ("app_tree_node", "app_media")
    source_missing = ("doc_tree_node", "app_tab", "doc_tab", "doc_media")

    src_file = tempfile.NamedTemporaryFile(suffix=".pyof", delete=False)
    source_path = src_file.name
    src_file.close()
    try:
        # 1. Build a source .pyof with ONLY app_tree_node and app_media.
        src = sqlite3.connect(source_path)
        try:
            for table in source_tables_present:
                src.execute(create_statements[table])
            # One synthetic UUID row each.
            for table in source_tables_present:
                synth = str(uuid.uuid4())
                if table == "app_tree_node":
                    src.execute(
                        'INSERT INTO "app_tree_node" (nid_txt, name_txt) VALUES (?, ?)',
                        (synth, f"{table}-row"),
                    )
                else:  # app_media
                    src.execute(
                        'INSERT INTO "app_media" (UUID, name_txt) VALUES (?, ?)',
                        (synth, f"{table}-row"),
                    )
            src.commit()
        finally:
            src.close()

        # 2. Host has all 6 tables, empty.
        host = sqlite3.connect(":memory:")
        try:
            for ddl in create_statements.values():
                host.execute(ddl)
            host.commit()

            # 3. Run the orchestrator. No exception must be raised even though
            #    4 of the 6 contract tables don't exist on the source side.
            results = import_pyof(source_path, host)

            # 4. Build a table -> result map for easy assertions.
            results_by_table: dict[str, ImportResult] = {r.table: r for r in results}
            assert set(results_by_table) == set(create_statements.keys())

            # 5. Present tables: inserted=1, skipped=0.
            for table in source_tables_present:
                r = results_by_table[table]
                assert r.inserted == 1, f"{table}: expected inserted=1, got {r}"
                assert r.skipped == 0, f"{table}: expected skipped=0, got {r}"
                assert r.errors == 0, f"{table}: expected errors=0, got {r}"
                assert count_rows_in_table(host, table) == 1

            # 6. Missing tables: inserted=0, skipped=0 (defensive no-op).
            for table in source_missing:
                r = results_by_table[table]
                assert r.inserted == 0, f"{table}: expected inserted=0, got {r}"
                assert r.skipped == 0, f"{table}: expected skipped=0, got {r}"
                assert r.errors == 0, f"{table}: expected errors=0, got {r}"
                # And the host table is still empty (no row landed).
                assert count_rows_in_table(host, table) == 0
        finally:
            host.close()
    finally:
        import os
        try:
            os.unlink(source_path)
        except OSError:
            pass


def test_import_pyof_idempotent() -> None:
    """T-NEW-074 Task 6 (bonus): re-importing the same .pyof into the same
    host is a no-op — the host's PKs block the second import, returning
    skipped=1 per table on the second pass."""
    from nchantdoffice.utilities.pyof_import import (
        ImportResult,
        import_pyof,
    )

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
    insert_specs: dict[str, tuple[str, tuple[str, ...]]] = {
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
    expected_tables = list(create_statements.keys())

    src_file = tempfile.NamedTemporaryFile(suffix=".pyof", delete=False)
    source_path = src_file.name
    src_file.close()
    try:
        # 1. Build a real on-disk .pyof with 1 row per contract table.
        src = sqlite3.connect(source_path)
        try:
            for table, ddl in create_statements.items():
                src.execute(ddl)
            for table, (sql, cols) in insert_specs.items():
                synth = str(uuid.uuid4())
                values = [synth] + [f"{table}-row"] * (len(cols) - 1)
                src.execute(sql, values)
            src.commit()
        finally:
            src.close()

        host = sqlite3.connect(":memory:")
        try:
            for ddl in create_statements.values():
                host.execute(ddl)
            host.commit()

            # First import: all 6 should insert.
            first_results = import_pyof(source_path, host)
            assert [r.table for r in first_results] == expected_tables
            for r in first_results:
                assert r == ImportResult(table=r.table, inserted=1, skipped=0, errors=0)

            # Second import against the SAME host: PKs collide, all 6 skipped.
            second_results = import_pyof(source_path, host)
            assert [r.table for r in second_results] == expected_tables
            for r in second_results:
                assert r == ImportResult(table=r.table, inserted=0, skipped=1, errors=0)
        finally:
            host.close()
    finally:
        import os
        try:
            os.unlink(source_path)
        except OSError:
            pass


def test_cmd_import_pyof_calls_orchestrator() -> None:
    """T-NEW-074 Task 9: integration test for cmd_import_pyof.

    Wires a bare ``NchantdOfficeApplicationToolBox`` instance (built with
    ``__new__`` so we skip the heavy ``__init__``), injects a fresh
    in-memory host ``sqlite3.Connection`` containing the six contract
    tables, injects a mock ``parent()`` whose ``statusBar()`` returns a
    mock with a callable ``showMessage``, and a stub
    ``fake_dialog(parent, caption, dir, filters)`` returning a real
    on-disk ``.pyof`` containing one row in ``app_tree_node``.

    Calls ``instance.cmd_import_pyof(file_dialog_fn=fake_dialog)`` and
    asserts the host gained one row in ``app_tree_node`` — proving the
    orchestrator was actually invoked end-to-end (not just that the
    method exists).
    """
    from unittest.mock import MagicMock

    from PySide6.QtWidgets import QApplication
    from nchantdoffice.widgets.controls.toolboxes import (
        NchantdOfficeApplicationToolBox,
    )

    # Singleton QApplication — Qt refuses two instances in one process.
    app = QApplication.instance() or QApplication([])

    # Build a source .pyof on disk with one row in app_tree_node (the
    # contract table we assert against). Same schema as the other
    # round-trip tests above.
    src_file = tempfile.NamedTemporaryFile(suffix=".pyof", delete=False)
    source_path = src_file.name
    src_file.close()
    try:
        src = sqlite3.connect(source_path)
        try:
            src.execute(
                'CREATE TABLE "app_tree_node" '
                "(nid_txt TEXT PRIMARY KEY, name_txt TEXT)"
            )
            synth = str(uuid.uuid4())
            src.execute(
                'INSERT INTO "app_tree_node" (nid_txt, name_txt) VALUES (?, ?)',
                (synth, "imported-node"),
            )
            src.commit()
        finally:
            src.close()

        # Bare instance — bypass __init__ (the real one constructs a Qt
        # widget tree, which is overkill for a smoke test). We inject
        # exactly the attributes cmd_import_pyof touches.
        instance = NchantdOfficeApplicationToolBox.__new__(
            NchantdOfficeApplicationToolBox
        )

        # Host DB connection in-memory with the 6 contract tables.
        host_conn = sqlite3.connect(":memory:")
        contract_ddl: dict[str, str] = {
            "app_tree_node": (
                'CREATE TABLE "app_tree_node" '
                "(nid_txt TEXT PRIMARY KEY, name_txt TEXT)"
            ),
            "doc_tree_node": (
                'CREATE TABLE "doc_tree_node" '
                "(nid_txt TEXT PRIMARY KEY, pid_txt TEXT, name_txt TEXT)"
            ),
            "app_tab": (
                'CREATE TABLE "app_tab" '
                "(tid_txt TEXT PRIMARY KEY, pid_txt TEXT, name_txt TEXT)"
            ),
            "doc_tab": (
                'CREATE TABLE "doc_tab" '
                "(tid_txt TEXT PRIMARY KEY, pid_txt TEXT, name_txt TEXT)"
            ),
            "app_media": (
                'CREATE TABLE "app_media" '
                "(UUID TEXT PRIMARY KEY, name_txt TEXT)"
            ),
            "doc_media": (
                'CREATE TABLE "doc_media" '
                "(UUID TEXT PRIMARY KEY, name_txt TEXT)"
            ),
        }
        for ddl in contract_ddl.values():
            host_conn.execute(ddl)
        host_conn.commit()

        # The method's first preference is self._host_db_conn — inject it.
        instance._host_db_conn = host_conn  # type: ignore[attr-defined]

        # Mock parent() whose statusBar().showMessage is a MagicMock so
        # the success branch can be exercised without a real QMainWindow.
        parent_mock = MagicMock()
        # ``statusBar`` itself is a MagicMock returning a MagicMock that
        # exposes ``showMessage`` (already true for MagicMock auto-spec),
        # but be explicit so the intent is obvious.
        parent_mock.statusBar.return_value.showMessage = MagicMock()
        instance.parent = MagicMock(return_value=parent_mock)  # type: ignore[method-assign]

        # The fake dialog: returns the temp .pyof path, simulating a user
        # picking the source file. Matches QFileDialog.getOpenFileName's
        # (path, filter) return shape.
        def fake_dialog(parent, caption, dir_, filters):  # noqa: ARG001
            return (source_path, "")

        # Exercise the method under test.
        result = instance.cmd_import_pyof(file_dialog_fn=fake_dialog)
        # The contract: defensive return-self on success.
        assert result is instance

        # The orchestrator actually ran: app_tree_node has one row on
        # the host (from the source file).
        row_count = host_conn.execute(
            'SELECT COUNT(*) FROM "app_tree_node"'
        ).fetchone()[0]
        assert row_count == 1, (
            f"expected 1 row in app_tree_node after import, got {row_count}"
        )
    finally:
        try:
            os.unlink(source_path)
        except OSError:
            pass

    # Touch app so the unused-variable lint doesn't fire — the
    # QApplication is needed for any future Qt work in this test.
    assert app is not None
