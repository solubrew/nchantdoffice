# Pyof Content Import — Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Add a `.pyof`-to-`.pyof` content import. User picks a source `.pyof` file from the **Application tab in the ToolBox** → all content tables (`app_tree_node`, `doc_tree_node`, `app_tab`, `doc_tab`, `app_media`, `doc_media`) are copied from the source into the host instance, **using the source's UUIDs as the new primary keys on the host** (no remapping). Instances, user_config, and config tables are NOT migrated.

**Architecture:**
1. New `nchantdoffice/utilities/pyof_import.py` module — pure-Python SQLite-to-SQLite ETL. Reads source `.pyof` (read-only ATTACH), iterates the content tables, INSERT-OR-IGNORE into the host's open connection. Single transactional commit at the end.
2. New action record `app_action` row in `nchantdoffice/_data_/models.yaml` (code_group=`base`, lookup_code=`import_pyof`) — wires the menu/toolbar entry.
3. New `cmd_import_pyof` method on `NchantdOfficeApplicationToolBox` — opens a QFileDialog, runs the import, reports counts via `logma` + a status-bar message.
4. Tests in `tests/test_pyof_import.py` (new file, RED-GREEN-REFACTOR pattern per the `test-driven-development` skill).

**Tech Stack:** Python stdlib `sqlite3` (no SQLAlchemy), PySide6 QFileDialog, existing `nchantrs.models.models` `store_*` methods on `self.store` (or direct SQL on the host connection when the existing wrappers don't fit the ETL shape).

---

## Decisions captured from user (2026-08-11)

- **Trigger:** button on the **Application tab in the ToolBox** (no CLI, no auto-mount).
- **Scope:** `app_tree_node`, `doc_tree_node`, `app_tab`, `doc_tab`, `app_media`, `doc_media`. NO `app_doc_content` / `_media_content`. NO instances. NO config.
- **UUID strategy:** preserve source UUIDs as the new primary keys on the host. No remapping. The user picked the "build out new primary keys" wording but meant "build new rows using the source's UUIDs as their primary keys" — i.e., **INSERT-OR-IGNORE on PK collision**. If a UUID already exists on the host, skip (the host row wins; the user can manually resolve via the GUI).
- **Conflict semantics:** skip-on-conflict (safe default). No `--force` flag in this iteration. Documented as a follow-up if needed.

---

## Affected tables (the import contract)

| Source table | Host table | PK column | Strategy |
|---|---|---|---|
| `app_tree_node` | `app_tree_node` | `nid_txt` (UUID) | INSERT-OR-IGNORE |
| `doc_tree_node` | `doc_tree_node` | `nid_txt` (UUID) | INSERT-OR-IGNORE |
| `app_tab` | `app_tab` | `tid_txt` (UUID) | INSERT-OR-IGNORE |
| `doc_tab` | `doc_tab` | `tid_txt` (UUID) | INSERT-OR-IGNORE |
| `app_media` | `app_media` | `UUID` | INSERT-OR-IGNORE |
| `doc_media` | `doc_media` | `UUID` | INSERT-OR-IGNORE |

**NOT migrated** (per user): `app_doc_content`, `app_media_content`, `doc_media_content`, `instance`, `instance_path`, `user_config`, `app_action`, `app_document_type`, `app_tab_set`, `doc_tab_set`, and every other config / metadata table.

**Referential integrity notes:**
- `app_tree_node.pid_txt` references another `app_tree_node.nid_txt` (tree parent). If the parent UUID doesn't exist on the host, the row inserts but the tree will be orphaned at import time. Document this in the user-facing message.
- `doc_tree_node.pid_txt` references `app_tree_node.nid_txt` (doc nodes hang off app nodes). Same risk.
- `app_tab.pid_txt` and `doc_tab.pid_txt` reference their respective `*_tree_node.nid_txt`. Same risk.
- `app_media.UUID` is independent of nodes/tabs (it's a content blob keyed by content UUID).
- `doc_media.UUID` references back to `app_media` or to a `doc_tree_node` — check schema before assuming.
- `app_media.UUID` and `doc_media.UUID` are content-level; tree-tab linkage is in a separate join table (probably `app_doc_content` which is NOT in scope, so any rows that need `app_doc_content` to render will appear as orphan media blobs in the host until the user also imports that content).

This is acceptable — the user said "build out new primary keys" knowing the FK shape is approximate. We log the count of orphan-PK inserts as a warning so the user knows what to inspect.

---

## Files to create / modify

### Create
- `nchantdoffice/utilities/pyof_import.py` — ETL logic
- `tests/test_pyof_import.py` — TDD regression tests

### Modify
- `nchantdoffice/_data_/models.yaml` — add `app_action` record for `import_pyof`
- `nchantdoffice/widgets/controls/toolboxes.py` — add `cmd_import_pyof` to `NchantdOfficeApplicationToolBox`
- `TODOs.md` — add T-NEW-074 ✅ row + card body
- `CHANGES.md` — add the new feature under "Unreleased / Added"

---

## Task list (bite-sized, 2-5 minutes each)

### Task 1: Define the import contract as a typed dataclass

**Files:**
- Create: `nchantdoffice/utilities/pyof_import.py` (initial)
- Test: `tests/test_pyof_import.py::test_import_contract_tables_match_expected_schema`

**Step 1:** Write the failing test — assert `PyofImportContract.TABLES` lists exactly the six tables in the order specified above, with the expected `pk_column` per table.

**Step 2:** Run it. Expected: FAIL — `ImportError: No module named 'nchantdoffice.utilities.pyof_import'`.

**Step 3:** Create `pyof_import.py` with:

```python
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
```

**Step 4:** Run test, expected: PASS.

**Step 5:** Commit: `feat(import): define PyofImportContract for content-only .pyof import (T-NEW-074)`.

### Task 2: Add `count_rows_in_table` helper

**Files:**
- Modify: `nchantdoffice/utilities/pyof_import.py`
- Test: `tests/test_pyof_import.py::test_count_rows_in_table_reads_source`

**Step 1:** Write test — open an in-memory sqlite3 with one table, insert 3 rows, assert `count_rows_in_table(conn, 'foo') == 3`.

**Step 2:** Run, FAIL.

**Step 3:** Add:

```python
def count_rows_in_table(conn: sqlite3.Connection, table: str) -> int:
    cur = conn.execute(f'SELECT COUNT(*) FROM "{table}"')
    return int(cur.fetchone()[0])
```

**Step 4:** PASS.

**Step 5:** Commit: `feat(import): add count_rows_in_table helper`.

### Task 3: Add `iter_table_rows` generator

**Files:**
- Modify: `nchantdoffice/utilities/pyof_import.py`
- Test: `tests/test_pyof_import.py::test_iter_table_rows_yields_dicts`

**Step 1:** Test — insert rows, iterate via `iter_table_rows(conn, 'foo')`, assert each yielded row is a `dict` with the expected keys + values.

**Step 2:** FAIL.

**Step 3:** Add:

```python
def iter_table_rows(conn: sqlite3.Connection, table: str) -> Iterable[dict]:
    conn.row_factory = sqlite3.Row
    cur = conn.execute(f'SELECT * FROM "{table}"')
    for row in cur:
        yield dict(row)
```

**Step 4:** PASS.

**Step 5:** Commit.

### Task 4: Add `import_one_table` (INSERT-OR-IGNORE on PK)

**Files:**
- Modify: `nchantdoffice/utilities/pyof_import.py`
- Test: `tests/test_pyof_import.py::test_import_one_table_inserts_new_rows` + `test_import_one_table_skips_pk_collisions` + `test_import_one_table_commits_atomically`

**Step 1:** Three tests:
- Insert 3 source rows into a fresh source DB; insert 2 of them into host first; import → expect 1 new row, 2 skipped.
- Repeat with a connection wrapper that records commits; assert exactly ONE commit at the end (the outer transaction).
- Verify the host table column shape matches the source — if source has an extra column, skip the column on insert (defensive).

**Step 2:** FAIL.

**Step 3:** Add:

```python
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
```

**Step 4:** PASS.

**Step 5:** Commit: `feat(import): add import_one_table with INSERT-OR-IGNORE`.

### Task 5: Add `import_pyof` orchestrator

**Files:**
- Modify: `nchantdoffice/utilities/pyof_import.py`
- Test: `tests/test_pyof_import.py::test_import_pyof_returns_summary_per_table`

**Step 1:** Test — create source + host DBs with the six tables, populate source with 1 row per table, host empty; call `import_pyof(source_path, host_conn)`; assert the returned list has 6 entries with `inserted == 1` for each.

**Step 2:** FAIL.

**Step 3:** Add:

```python
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
```

**Step 4:** PASS.

**Step 5:** Commit: `feat(import): add import_pyof orchestrator (T-NEW-074)`.

### Task 6: Pin the contract against a real on-disk .pyof

**Files:**
- Test: `tests/test_pyof_import.py::test_import_pyof_round_trips_against_real_pyof` + `test_import_pyof_silently_skips_missing_tables`

**Step 1:** Tests:
- Build a minimal `.pyof` on disk (sqlite3 file) with the six tables; populate with one row each (use synthetic UUIDs). Call `import_pyof(path, host_conn)` against an empty host. Assert all six rows landed on the host.
- Build a source `.pyof` with ONLY `app_tree_node` and `app_media` (missing the others). Import → assert those 2 imported, the other 4 returned as `ImportResult(inserted=0, skipped=0)` (defensive no-op, no exception).

**Step 2:** FAIL.

**Step 3:** (No source change — `import_one_table` already handles the missing-table case via `_intersecting_columns` returning `[]`. The test pins the contract.)

**Step 4:** PASS.

**Step 5:** Commit: `test(import): pin round-trip + missing-table contract`.

### Task 7: Wire `app_action` row in models.yaml

**Files:**
- Modify: `nchantdoffice/_data_/models.yaml` (add one row to the `app_action` records)

**Step 1:** Locate the `app_action` table records section. Add:

```yaml
- ['067xxxxx-yyyy-7zzz-8000-aaaaaaaaaaaa', 'base', 'import_pyof',
  'Import .pyof',
  'Import content tables from a source .pyof into this instance.',
  '067xxxxx-yyyy-7zzz-8000-bbbbbbbbbbbb',
  'import', '', 'Import from .pyof…', 'Open a file picker, choose a .pyof, and copy its content tables (nodes, tabs, media) into this instance. Source UUIDs are preserved.',
  'nchantdoffice.widgets.controls.toolboxes.NchantdOfficeApplicationToolBox.cmd_import_pyof',
  '{}']
```

(Use real generated UUIDs — see `uuidgen` from the terminal. Don't fabricate.)

**Step 2:** Run `python3 -c "import nchantdoffice; from nchantdoffice.widgets.controls.toolboxes import NchantdOfficeApplicationToolBox"` — expected: still passes (the `cmd_import_pyof` attribute doesn't have to exist yet; the YAML is parsed at instance time, not import time).

**Step 3:** Commit: `feat(action): register import_pyof app_action (T-NEW-074)`.

### Task 8: Add `cmd_import_pyof` to `NchantdOfficeApplicationToolBox`

**Files:**
- Modify: `nchantdoffice/widgets/controls/toolboxes.py` (add method to the class at line 183+)

**Step 1:** Write the method per the existing `cmd_open_local_file` pattern (defensive try/except, log on failure, return self). Pseudocode:

```python
def cmd_import_pyof(self, event=None, *args, **kwargs):
    """T-NEW-074: import content tables from a user-selected .pyof."""
    from PySide6.QtWidgets import QFileDialog
    from nchantdoffice.utilities.pyof_import import import_pyof
    try:
        path, _ = QFileDialog.getOpenFileName(
            self, "Import .pyof", "",
            "Pyof files (*.pyof);;SQLite DBs (*.sqlite *.db);;All files (*)",
        )
        if not path:
            return self
        # Locate the host DB connection via the model / store
        host_conn = getattr(self, "_host_db_conn", None)
        if host_conn is None:
            logma.warning(
                "[import_pyof] no host DB connection available on toolbox; "
                "fall back to opening instance .pyof via the app model."
            )
            host_conn = self._resolve_host_db_conn()
        results = import_pyof(path, host_conn)
        total_in = sum(r.inserted for r in results)
        total_skip = sum(r.skipped for r in results)
        logma.info(
            f"[import_pyof] {path}: inserted={total_in}, skipped={total_skip}"
        )
        if hasattr(self.parent(), "statusBar"):
            self.parent().statusBar().showMessage(
                f"Imported {total_in} rows ({total_skip} skipped)", 5000
            )
    except Exception as e:
        logma.error(f"[import_pyof] failed: {e}", exc_info=True)
    return self
```

The exact way to obtain the host connection is project-specific — the implementer must trace through `self.app.model.store.store_db_connection` (or equivalent in `nchantdoffice/models.py`) and wire whichever accessor returns the live `sqlite3.Connection`. The defensive fallback (`_resolve_host_db_conn`) should walk `self.parent()` → `self.app` → `self.app.model.store` and return the active connection.

**Step 2:** Verify import — `python3 -c "from nchantdoffice.widgets.controls.toolboxes import NchantdOfficeApplicationToolBox; assert hasattr(NchantdOfficeApplicationToolBox, 'cmd_import_pyof')"`.

**Step 3:** Commit: `feat(import): add cmd_import_pyof to Application ToolBox (T-NEW-074)`.

### Task 9: Integration test — UI-level smoke

**Files:**
- Test: `tests/test_pyof_import.py::test_cmd_import_pyof_calls_orchestrator` (off-screen Qt)

**Step 1:** Build a `NchantdOfficeApplicationToolBox` under `QT_QPA_PLATFORM=offscreen`, monkey-patch the `QFileDialog.getOpenFileName` to return a temp `.pyof` path, monkey-patch `import_pyof` to record the call, invoke `cmd_import_pyof`, assert the stub was called with the right path.

**Step 2:** FAIL (no orchestrator yet — task 8 may need to wire this).

**Step 3:** Refactor task 8's `cmd_import_pyof` to accept a `file_dialog_fn` kwarg for testability (defaults to `QFileDialog.getOpenFileName`). Re-run.

**Step 4:** PASS.

**Step 5:** Commit: `test(import): pin cmd_import_pyof integration (T-NEW-074)`.

### Task 10: Document + changelog + T-NEW card

**Files:**
- Modify: `TODOs.md` (add T-NEW-074 ✅ row + card body, per the user's format rule)
- Modify: `CHANGES.md` (add entry under "Unreleased / Added")

**Step 1:** TODOs.md — add:

```markdown
- **T-NEW-074** ✅ Content-only .pyof import from Application tab ToolBox (button), commit `<hash>` (2026-08-11, t-new-074).
```

Then a full card body after the T-NEW-073 block:

```markdown
### T-NEW-074 — Content-only .pyof import (2026-08-11)

**Context.** Operators need to bring content (nodes, tabs, media) from one .pyof instance into another without merging instances or config. The Application tab in the ToolBox is the canonical place for app-wide actions (mirrors `cmd_open_local_file`); a new `cmd_import_pyof` method opens a QFileDialog, copies the six content tables into the host's open sqlite3 connection, and reports counts via status bar.

**Affected sites:**
- `nchantdoffice/utilities/pyof_import.py` (new ETL module)
- `nchantdoffice/_data_/models.yaml` (new `app_action` row)
- `nchantdoffice/widgets/controls/toolboxes.py` (new `cmd_import_pyof` method on `NchantdOfficeApplicationToolBox`)
- `tests/test_pyof_import.py` (new TDD suite)

**Migration plan** (no priority / low priority — design decision first): scope is content-only by user direction (no `app_doc_content`, no `_media_content`, no instances, no config). UUID strategy is INSERT-OR-IGNORE: source UUIDs become host primary keys; collisions are silent skips (host row wins). Orphan FKs are logged but not enforced — users are expected to inspect the host tree after a large import.

**Steps:**
1. ETL module (`PyofImportContract.TABLES`, `count_rows_in_table`, `iter_table_rows`, `import_one_table`, `import_pyof` orchestrator). Tasks 1-6.
2. Wire `app_action` row in `models.yaml`. Task 7.
3. Wire `cmd_import_pyof` on the ToolBox. Task 8.
4. Integration test. Task 9.
5. This card. Task 10.

**Verification:**
- `python -m pytest tests/test_pyof_import.py --tb=no -q` → all green
- Manual: open the GUI, navigate to the Application tab in the ToolBox, click the new "Import from .pyof…" button, pick a test .pyof, confirm rows landed on the host.
```

**Step 2:** CHANGES.md — add to "Unreleased / Added":

```markdown
- Content-only `.pyof` import from the Application tab in the ToolBox (`cmd_import_pyof`, T-NEW-074) — opens a file picker, copies `app_tree_node`, `doc_tree_node`, `app_tab`, `doc_tab`, `app_media`, `doc_media` from the source into the host instance using INSERT-OR-IGNORE on the source UUIDs (no remapping). Instances and config are NOT migrated.
```

**Step 3:** Commit: `docs(import): T-NEW-074 card + CHANGES.md entry`.

---

## Verification (final gate)

```bash
# Unit
cd /home/solubrew/.hermes/projects/nchantdoffice
python -m pytest tests/test_pyof_import.py --tb=no -q
# expected: all pass

# Integration (Qt off-screen)
QT_QPA_PLATFORM=offscreen python -m pytest tests/test_pyof_import.py::test_cmd_import_pyof_calls_orchestrator --tb=no -q
# expected: pass

# Import-time smoke
python -c "from nchantdoffice.widgets.controls.toolboxes import NchantdOfficeApplicationToolBox; assert hasattr(NchantdOfficeApplicationToolBox, 'cmd_import_pyof')"
# expected: silent exit 0

# Audit (sasquatch, after fix lands)
/home/solubrew/ENVs/sasquatch/bin/sasquatch analyze -p . --skip-pii-secrets
# expected: score unchanged or +1 (test count up)
```

---

## Risks, tradeoffs, open questions

- **Host DB connection accessor.** The exact way `NchantdOfficeApplicationToolBox` obtains the live `sqlite3.Connection` for the host `.pyof` is project-specific. Task 8's `_resolve_host_db_conn` helper is a defensive fallback the implementer should harden against the real codebase. If it turns out the host connection is wrapped (e.g. inside `nchantdoffice.store.Store` with a different API), the implementer should add a `def host_conn(self) -> sqlite3.Connection` accessor on the Store wrapper and use that.

- **FK orphan handling.** Source rows whose `pid_txt` references a UUID not present on the host will be inserted as orphans (the FK isn't enforced). For `doc_tree_node.pid_txt` referencing `app_tree_node.nid_txt`, this is likely if the user picks a single subtree to import. Documented in the user-facing status message + this plan; could be a follow-up T-NEW-075 if the user wants enforcement.

- **No `--force` overwrite flag.** User chose "build out new primary keys" wording but the safer default (INSERT-OR-IGNORE) is what we'll ship. If a follow-up needs overwrite, add `force: bool = False` to `import_pyof` and switch to `INSERT OR REPLACE`.

- **No CLI fallback.** User said the trigger is the Application tab only — no `nchantdoffice-cli import`. Easy to add later if asked.

- **`app_doc_content` not migrated.** Media rows without their content blob will appear on the host but render as broken until the user also migrates content. Same for `app_media_content` / `doc_media_content`. Documented in the T-NEW-074 card.

- **Action-record UUIDs.** Task 7's UUIDs are placeholders. The implementer must generate real `uuidgen` UUIDs that match the project's UUID format (the existing rows use the `067xxxxx-yyyy-7zzz-8000-NNNNNNNNNNNN` shape — looks like a custom v8 variant). Use `uuidgen -r` or check the project's `nchantdoffice/utilities/uuids.py` if one exists.

- **Test isolation.** The integration test in Task 9 needs an off-screen Qt session; the implementer should follow the `qt-parent-harness` skill pattern if the toolbox requires a real `QApplication` instance. `QT_QPA_PLATFORM=offscreen` is the minimum viable path; if shiboken6 segfaults (we hit it earlier in this session on `test_per_doc_type_settings_pane`), the test file may need a `pytest.mark.xfail` with `reason='shiboken6 + offscreen segfault'` and a follow-up to migrate to the subprocess harness.
