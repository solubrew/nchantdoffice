"""T-NEW-074 — content-only .pyof → .pyof import.

Reads content tables from a source .pyof and INSERT-OR-IGNOREs
them into the host's open sqlite3 connection. Source UUIDs are
preserved as the new primary keys on the host; collisions skip
the source row (host wins).

Tables in scope: app_tree_node, doc_tree_node, app_tab, doc_tab,
app_media, doc_media. No instance/config migration.
"""
from __future__ import annotations
import sqlite3
from dataclasses import dataclass
from typing import Iterable, Optional

@dataclass(frozen=True)
class TableSpec:
    name: str
    pk_column: str

class PyofImportContract:
    TABLES: tuple[TableSpec, ...] = (
        TableSpec("app_tree_node", "nid_txt"),
        TableSpec("doc_tree_node", "nid_txt"),
        TableSpec("app_tab",       "tid_txt"),
        TableSpec("doc_tab",       "tid_txt"),
        TableSpec("app_media",     "UUID"),
        TableSpec("doc_media",     "UUID"),
    )

def count_rows_in_table(conn: sqlite3.Connection, table: str) -> int:
    cur = conn.execute(f'SELECT COUNT(*) FROM "{table}"')
    return int(cur.fetchone()[0])


def iter_table_rows(conn: sqlite3.Connection, table: str) -> Iterable[dict]:
    conn.row_factory = sqlite3.Row
    cur = conn.execute(f'SELECT * FROM "{table}"')
    for row in cur:
        yield dict(row)

@dataclass
class ImportResult:
    table: str
    inserted: int = 0
    skipped: int = 0
    errors: int = 0

def _intersecting_columns(src: sqlite3.Connection, host: sqlite3.Connection, table: str) -> list[str]:
    src_cols = {r[1] for r in src.execute(f'PRAGMA table_info("{table}")')}
    host_cols = {r[1] for r in host.execute(f'PRAGMA table_info("{table}")')}
    return sorted(src_cols & host_cols)

def import_one_table(src: sqlite3.Connection, host: sqlite3.Connection, spec: TableSpec) -> ImportResult:
    """Copy rows from src[spec.name] into host[spec.name] preserving
    source UUIDs as the new primary keys. INSERT-OR-IGNORE so existing
    host rows win."""
    result = ImportResult(table=spec.name)
    cols = _intersecting_columns(src, host, spec.name)
    if not cols:
        return result  # missing on either side — silent no-op
    placeholders = ",".join("?" for _ in cols)
    col_list = ",".join(f'"{c}"' for c in cols)
    sql = (
        f'INSERT OR IGNORE INTO "{spec.name}" ({col_list}) '
        f'VALUES ({placeholders})'
    )
    for row in iter_table_rows(src, spec.name):
        values = [row.get(c) for c in cols]
        cur = host.execute(sql, values)
        # cur.rowcount is 1 for INSERT, 0 for OR-IGNORE-skip
        if cur.rowcount == 1:
            result.inserted += 1
        else:
            result.skipped += 1
    return result
