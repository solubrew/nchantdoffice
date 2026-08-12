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
