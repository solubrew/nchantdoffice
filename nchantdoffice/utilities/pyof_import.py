"""T-NEW-074 / T-NEW-075 / T-NEW-076 / T-NEW-077 — content-only .pyof → .pyof import.

Reads content tables from a source .pyof and INSERTs them into the host's
open sqlite3 connection.

T-NEW-074 base 6 tables (app_tree_node, doc_tree_node, app_tab, doc_tab,
app_media, doc_media): INSERT-OR-IGNORE — source UUIDs become host primary
keys; collisions skip (host wins).

T-NEW-075 content tables (app_doc_content, app_media_content, doc_media_content):
last-version-per-pUUID merge — source PK columns are dropped (host regenerates
rowid), but source UUID and pUUID are carried (FK relationships preserved).
For each pUUID only the highest-version row is kept. This is INSERT-with-
dedupe, not INSERT-OR-IGNORE: host PKs are fresh so skipped is always 0.

T-NEW-076 host-aware merge-by-version: for each surviving source row, query
the host's MAX(version) for that pUUID. If the source's version is strictly
greater, DELETE all host rows for that pUUID and INSERT the source's
max-version row (one source row replaces N host rows if the host had
older versions). If the source's version is <= host's MAX, skip — host
wins, no insert, no delete. ``ImportResult.skipped`` for ``_content``
tables now covers both "host had a newer version" and "INSERT didn't
take" cases.

T-NEW-077 uniform base-6 contract: the base 6 tables now follow the same
shape as ``_content`` — source PK columns are dropped from the projection
(host regenerates rowid), source UUID is carried as data, and dedupe is
by host UUID-lookup: if the host already has that UUID, skip (host
wins); otherwise INSERT. Re-imports dedupe base tables too. ``INSERT``
is now plain (no OR-IGNORE) — safe because the host UUID lookup
guarantees no duplicate. ``ImportResult.skipped`` for the base 6 now
covers both "host had this UUID" (host wins) AND the defensive
"INSERT didn't take" fallback (rowcount==0).
"""
from __future__ import annotations
import sqlite3
from dataclasses import dataclass
from typing import Iterable, Literal, Optional

MergeStrategy = Literal["insert_or_ignore", "last_version_per_puuid"]

@dataclass(frozen=True)
class TableSpec:
    name: str
    pk_column: Optional[str]
    merge_strategy: MergeStrategy = "insert_or_ignore"

class PyofImportContract:
    TABLES: tuple[TableSpec, ...] = (
        # T-NEW-074 / T-NEW-077 — base 6: source PK columns are dropped,
        # host regenerates rowid. Dedupe by host UUID lookup (the
        # pk_column points at the UUID column). Uniform with _content.
        TableSpec("app_tree_node", "nid_txt"),
        TableSpec("doc_tree_node", "nid_txt"),
        TableSpec("app_tab",       "tid_txt"),
        TableSpec("doc_tab",       "tid_txt"),
        TableSpec("app_media",     "UUID"),
        TableSpec("doc_media",     "UUID"),
        # T-NEW-075 — _content tables: last-version-wins per pUUID.
        TableSpec("app_doc_content",    None, merge_strategy="last_version_per_puuid"),
        TableSpec("app_media_content",  None, merge_strategy="last_version_per_puuid"),
        TableSpec("doc_media_content",  None, merge_strategy="last_version_per_puuid"),
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

    # NOTE on ``skipped`` semantics:
    #   * T-NEW-074 base-6 tables (INSERT-OR-IGNORE): ``skipped`` counted
    #     PK-collision rows the host already had (host wins). T-NEW-077
    #     replaced this with a host UUID lookup, so the shape is uniform
    #     with ``_content`` below — but the meaning is still "host wins".
    #   * T-NEW-075 ``_content`` tables, pre-076: ``skipped`` was always 0
    #     (host rowids are fresh; only source-side last-version-per-pUUID
    #     dedupe was applied).
    #   * T-NEW-076 ``_content`` tables: ``skipped`` covers BOTH
    #     "host had a newer-or-equal version for this pUUID" (host wins)
    #     AND the defensive "INSERT didn't take" fallback (rowcount==0).
    #     Use ``inserted`` to track successful replace / first-time
    #     inserts and ``skipped`` to track host-wins / defensive no-ops.
    #   * T-NEW-077 base 6 (uniform with ``_content``): ``skipped``
    #     covers BOTH "host already had this UUID" (host wins) AND the
    #     defensive "INSERT didn't take" fallback (rowcount==0). The
    #     host-regenerated-rowid guarantee makes the latter defensive
    #     only, but it's kept for parity with the ``_content`` path.

def _intersecting_columns(src: sqlite3.Connection, host: sqlite3.Connection, table: str) -> list[str]:
    src_cols = {r[1] for r in src.execute(f'PRAGMA table_info("{table}")')}
    host_cols = {r[1] for r in host.execute(f'PRAGMA table_info("{table}")')}
    return sorted(src_cols & host_cols)


def _host_primary_key_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    """T-NEW-075 — return the set of PRIMARY KEY column names on the host table.

    Used by ``_import_content_table`` to drop the host PK from the insert
    projection (host regenerates the rowid). Empty set if the table doesn't
    exist or has no explicit PK columns (relies on rowid).
    """
    try:
        rows = list(conn.execute(f'PRAGMA table_info("{table}")'))
    except sqlite3.DatabaseError:
        return set()
    return {r[1] for r in rows if r[5] > 0}  # pk column index > 0 == part of PK


def _coerce_doc_version(raw: object) -> int:
    """T-NEW-075 — defensively cast a ``version`` cell to ``int``.

    The source ``.pyof`` may store the column as INTEGER, REAL, or TEXT
    depending on how the row was written. We tolerate all three shapes so
    the last-version-wins comparison doesn't crash on a stray ``"3"`` or
    ``3.0`` from an older writer.
    """
    if raw is None:
        return -1
    if isinstance(raw, bool):  # bool is a subclass of int — guard explicitly.
        return int(raw)
    if isinstance(raw, int):
        return raw
    if isinstance(raw, float):
        return int(raw)
    if isinstance(raw, (bytes, bytearray)):
        raw = raw.decode("utf-8", errors="replace")
    try:
        return int(str(raw).strip())
    except (TypeError, ValueError):
        return -1


def _import_content_table(
    src: sqlite3.Connection, host: sqlite3.Connection, spec: TableSpec
) -> ImportResult:
    """T-NEW-075 / T-NEW-076 — last-version-wins import for ``_content`` tables.

    T-NEW-075 source-side dedupe: source PK columns are dropped (host
    regenerates rowid). Source UUID and pUUID are carried so doc↔content
    / node↔tab FK relationships survive. For each pUUID only the
    highest-version row is kept. ``INSERT INTO`` (not OR-IGNORE): host
    PKs are fresh, so pre-076 ``skipped`` was always 0.

    T-NEW-076 host-aware merge-by-version: for each surviving source row
    (one max-version row per pUUID) we query the host's MAX(version) for
    that pUUID. If the source's version is **strictly** greater, we
    DELETE all host rows for that pUUID and INSERT the source's
    max-version row — one source row replaces N host rows if the host
    had older versions. If the source's version is <= the host's MAX,
    we skip — host wins, no insert, no delete. ``skipped`` now covers
    BOTH "host had a newer-or-equal version" AND the defensive
    "INSERT didn't take" fallback (rowcount==0).
    """
    result = ImportResult(table=spec.name)
    cols = _intersecting_columns(src, host, spec.name)
    if not cols:
        return result  # missing on either side — silent no-op
    if "pUUID" not in cols or "version" not in cols:
        # Defensive: a _content table missing the dedupe keys can't be
        # safely merged with last-version-wins semantics. Treat as a
        # silent no-op rather than crash mid-import.
        return result
    # Drop the host's PRIMARY KEY column from the projection — host
    # regenerates the rowid. Carrying the source's id would collide on
    # the second import (idempotent re-import would crash on UNIQUE).
    host_pk_cols = _host_primary_key_columns(host, spec.name)
    insert_cols = [c for c in cols if c not in host_pk_cols]
    if not insert_cols:
        return result  # nothing to insert once host PK is excluded
    # Project only the intersecting columns (drop source PKs by virtue of
    # not selecting them; the host PK is freshly assigned on INSERT).
    placeholders = ",".join("?" for _ in insert_cols)
    col_list = ",".join(f'"{c}"' for c in insert_cols)
    insert_sql = (
        f'INSERT INTO "{spec.name}" ({col_list}) VALUES ({placeholders})'
    )

    # Group by pUUID, keep the row with the highest version. Ties broken
    # by last-seen-wins (later SELECT iteration wins — preserves the
    # "latest write" intent).
    best_by_puuid: dict[object, dict] = {}
    for row in iter_table_rows(src, spec.name):
        puuid = row.get("pUUID")
        if puuid is None:
            continue  # can't dedupe a row without a pUUID
        candidate = best_by_puuid.get(puuid)
        if candidate is None or _coerce_doc_version(row.get("version")) >= _coerce_doc_version(
            candidate.get("version")
        ):
            best_by_puuid[puuid] = row

    # T-NEW-076 host-aware merge-by-version: for each surviving source row,
    # compare against the host's MAX(version) for that pUUID.
    #   * src_version >  host_max → DELETE host rows for this pUUID, INSERT source row.
    #   * src_version <= host_max → skip (host wins; no insert, no delete).
    for kept in best_by_puuid.values():
        puuid = kept.get("pUUID")
        src_version = _coerce_doc_version(kept.get("version"))
        # Query host's MAX(version) for this pUUID. We already verified
        # "version" is in cols above; the ``"version" in cols`` check is
        # defensive in case the projection changes in the future.
        if "version" in cols:
            cur = host.execute(
                f'SELECT MAX(version) FROM "{spec.name}" WHERE "pUUID" = ?',
                (puuid,),
            )
            row = cur.fetchone()
            host_max = (
                _coerce_doc_version(row[0]) if row and row[0] is not None else -1
            )
        else:
            host_max = -1
        if src_version <= host_max:
            # Host is at least as new as the source → host wins, skip.
            result.skipped += 1
            continue
        # Source is strictly newer — drop host rows for this pUUID first,
        # then INSERT the source's max-version row. One source row
        # replaces N host rows if the host had multiple older versions.
        if puuid is not None:
            host.execute(
                f'DELETE FROM "{spec.name}" WHERE "pUUID" = ?',
                (puuid,),
            )
        values = [kept.get(c) for c in insert_cols]
        cur = host.execute(insert_sql, values)
        if cur.rowcount == 1:
            result.inserted += 1
        else:
            # rowcount==0 isn't expected here (host PKs were just
            # cleared by the DELETE) but be defensive: count it as a
            # skip rather than a hard error so a quirky SQLite build
            # doesn't poison the whole transaction.
            result.skipped += 1
    return result


def import_one_table(src: sqlite3.Connection, host: sqlite3.Connection, spec: TableSpec) -> ImportResult:
    """Copy rows from src[spec.name] into host[spec.name].

    Dispatch is controlled by ``spec.merge_strategy``:

    * ``"insert_or_ignore"`` (default — T-NEW-074 / T-NEW-077 base 6):
      source PK columns are dropped (host regenerates rowid), the source
      UUID is carried as data, and dedupe is by host UUID-lookup: if the
      host already has the source's UUID, skip (host wins); otherwise
      INSERT. Uniform contract with ``_content`` below.

    * ``"last_version_per_puuid"`` (T-NEW-075 / T-NEW-076 _content
      tables): source PKs are dropped, UUID + pUUID are carried, only
      the highest-version row per pUUID is inserted. T-NEW-076 then
      compares the source's version against the host's MAX(version) for
      that pUUID — strictly newer source rows replace host rows;
      equal-or-older source rows are skipped (host wins).
    """
    if spec.merge_strategy == "last_version_per_puuid":
        return _import_content_table(src, host, spec)

    # T-NEW-077 base 6 — uniform with _content: drop source PK columns
    # (host regenerates rowid), carry source UUID as data, dedupe by
    # host UUID lookup. Plain INSERT (no OR-IGNORE) — safe because the
    # host UUID lookup guarantees no duplicate. The host's own PK
    # column(s) are excluded from the projection so the freshly
    # generated rowid doesn't collide with a host-side autoincrement
    # PK that happens to equal the source UUID string — EXCEPT for the
    # UUID column itself, which must be carried as data (it identifies
    # the row across imports; if the host has it as PK we want the
    # source value to land there, not NULL).
    result = ImportResult(table=spec.name)
    cols = _intersecting_columns(src, host, spec.name)
    if not cols:
        return result  # missing on either side — silent no-op
    # The UUID column is ``spec.pk_column`` for the base 6. If the
    # contract forgot to set it, we have no dedupe key — defensive
    # silent no-op rather than risk duplicate rows on re-import.
    uuid_col = spec.pk_column
    if uuid_col is None or uuid_col not in cols:
        return result
    # Drop the host's PRIMARY KEY column(s) from the projection — host
    # regenerates the rowid (matches the _content path from T-NEW-075).
    # BUT always carry the UUID column itself so the source's UUID
    # value lands as data on the host. If the host has the UUID column
    # as a PK, this means we INSERT into the PK column (the UUID lookup
    # above already confirmed the value isn't there yet); if it's a
    # plain column, the source UUID just becomes data.
    host_pk_cols = _host_primary_key_columns(host, spec.name)
    insert_cols = [c for c in cols if c not in host_pk_cols or c == uuid_col]
    if not insert_cols:
        return result  # nothing to insert once host PK is excluded
    placeholders = ",".join("?" for _ in insert_cols)
    col_list = ",".join(f'"{c}"' for c in insert_cols)
    insert_sql = (
        f'INSERT INTO "{spec.name}" ({col_list}) VALUES ({placeholders})'
    )
    for row in iter_table_rows(src, spec.name):
        uuid_val = row.get(uuid_col)
        if uuid_val is None:
            # Can't dedupe without a UUID — silently skip rather than
            # risk a duplicate on re-import. Matches the defensive
            # treatment of pUUID=None in _import_content_table.
            continue
        # T-NEW-143: skip soft-deleted source rows. DELETE_BIT=1 is a
        # squirl tombstone and must not be resurrected on the host.
        # row.get() returns None when the column is absent on an older
        # source schema — treated as "not deleted" so legacy sources
        # keep importing. Missing/None/0 → live; any truthy int → skip.
        if row.get("DELETE_BIT"):
            result.skipped += 1
            continue
        # Host UUID lookup first. If the host already has this UUID,
        # skip (host wins). The host may have additional columns the
        # source doesn't (e.g. host-side metadata); we only care about
        # UUID existence here.
        cur = host.execute(
            f'SELECT 1 FROM "{spec.name}" WHERE "{uuid_col}" = ? LIMIT 1',
            (uuid_val,),
        )
        if cur.fetchone() is not None:
            result.skipped += 1
            continue
        # Host doesn't have this UUID — INSERT (host regenerates rowid).
        values = [row.get(c) for c in insert_cols]
        cur = host.execute(insert_sql, values)
        # cur.rowcount is 1 on a successful INSERT. rowcount==0 isn't
        # expected here (host UUID lookup just confirmed absence) but
        # be defensive: count it as a skip rather than a hard error so
        # a quirky SQLite build doesn't poison the whole transaction.
        if cur.rowcount == 1:
            result.inserted += 1
        else:
            result.skipped += 1
    return result

def import_pyof(
    source_path: str,
    host_conn: sqlite3.Connection,
    *,
    contract: type[PyofImportContract] = PyofImportContract,
) -> list[ImportResult]:
    """Open the source .pyof read-only via ATTACH and copy the
    contract tables into ``host_conn``. Single transaction."""
    # Defensive: validate the file exists and is a sqlite DB
    src = sqlite3.connect(f'file:{source_path}?mode=ro', uri=True)
    try:
        results: list[ImportResult] = []
        try:
            for spec in contract.TABLES:
                results.append(import_one_table(src, host_conn, spec))
            host_conn.commit()
        except Exception:
            host_conn.rollback()
            raise
        return results
    finally:
        src.close()
