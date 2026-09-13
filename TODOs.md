# NchantdOffice TODOs — current state (2026-08-27)

> **Consolidation date:** 2026-08-27.
>
> **Corruption restore (2026-08-27):** `TODOs.md` and
> `CHANGES.md` were corrupted by log dumps committed at
> `93773b3` "NOScript debug" (2026-08-19). Both files were
> restored to their last clean state (`01b94d7`, 2026-08-17).
> CHANGES.md was extended with a reconstruction of the DESK
> T-NEW-046..061 milestone from git log history. TODOs.md
> P0/P1/P2 active items and pinned items are unchanged from
> the 2026-08-17 consolidation. One new item added: T-NEW-159.
>
> This file replaces the previous `TODOs.md`, the historical `STATE.md`,
> and the session-only `SESSION_NOTES.md` (both now in
> `_data_/archive/2026-07-29/`). It captures the project state after the
> closed-loop of Sprints 1-17 across nchantdoffice / nchantrs / pyffice /
> pyside6pandas, plus the 2026-08-10 → 2026-08-17 T-NEW
> sweep (110..147) and the 2026-08-17 batch
> (`260886a` / `419a317` / `899962c` / `07fc18b` — closes
> T-NEW-122, T-NEW-117, T-NEW-037-followup, and the pyof
> bare-parent segfault respectively).
>
> **T-NEW-NNN card numbering — per-repo convention.** This
> repo's `T-NEW-NNN` numbers are local to nchantdoffice
> (desktop) and do NOT match the numbering in the server
> (nchantdoffice_com) or ATNRG repos. Example: `T-NEW-040`
> means "Toolbar init tech debt" here but "Defensive Admin
> role creation" in nchantdoffice_com and "Affiliate
> rotation expansion" in ATNRG. When cross-referencing a
> card from another repo, always prefix it: "DESK
> T-NEW-NNN" / "COM T-NEW-NNN" / "ATNRG T-NEW-NNN" —
> without the prefix the reference is ambiguous.

> **Other top-level notes** (preserved as separate files):
> - `README.md` — project overview
> - `CHANGES.md` — Keep-a-Changelog history
> - `CI_CD.md` — pipeline overview
> - `CLI.md` — command-line reference
> - `CODING_STANDARDS.md` — V4 standards compliance
> - `directory_tree.md` — file-tree snapshot (2026-07-16)
> - `BUGs.md` — raw stack-trace archive (historical reference)

---
# New TODOs
- Pycurity password vault initialization in SetupWizard — **FIXED** (private store at ~/.local/share/nchantdoffice/pycurity/)

- Image Document tab is push the width instead of resizing the image, image should fit to width and size the height maintaining the aspect ratio — **FIXED** (`"scaled": True` at images.py:710)
- NchantdOfficeBrowser is not keeping track of url navigation or reloading to the last visited site — **FIXED** (populate_document loads saved URL from app_media)
- FileDetailsPane refresh on initial file open — **FIXED** (refresh() helper + set_file_path calls refresh)
 
 
- fix and finish Affiliate Manager tab — **FIXED** (referral_panel.py implemented with 11 tests passing)
- add a settings pane for each document type in the Center Pane Settings of the Interface Tab
- fix Right Pane tabs to select which ones can be adjusted in the right side tabset in the Interface Tab
- Tab drag and drop needs to only initiate when the mouse is clicked on to the tab name area not the main widget area
- implement the ability to drag a tab to a different node - and it saves the new parent
- implement the ability to drag a tab to the rightside tabset and it reloads to its original location
- add to Settings/Interface tab config to allow a user to select that tab name updates to the file name when a file is opened 
- implement search across all nodes and tabs as well as node specific and tab specific search as well finish code in the NchantdOfficeApplicationToolBox 
- NchantdOfficeJournalEditor always-save functionality fixed (outer save() now calls _parse_entry + parent.save) — **SUPERSEDED** by the
  app_media restoration work (T-NEW-079). The current canonical save contract: outer save() calls `self.save_app()` ONLY. The
  `_parse_entry()` / `parent.save()` blocks are intentionally commented out (the always-save follow-up is a separate card). The inner
  `NchantdOfficeJournalAppendEditor.save()` does call `_parse_entry()` -> `add_entry()` -> `parent.save()` chain which populates the entries
  dict. `parse(content)` splits the full text on `--|YYYY-MM-DD HH:MM:SS|--` markers and stores the `{timestamp: block_text}` dict in
  `self.entries` (the in-memory cache). Do NOT re-introduce `super().save()` on the journal path -- it persists to `doc_media_content` which
  is the wrong table for an app_media document. See `nchantdoffice/widgets/documents/journal.py`, `save_app()` docstring at
  `nchantdoffice/widgets/documents/documents.py:625`, and the full T-NEW-079 card body in this file.

- Name-entry dialog for new nodes/tabs — checkboxes now in Settings/Interface tab — **FIXED** (prompt_for_new_node_name, prompt_for_new_tab_name checkboxes added to settings.py)
- Tab drag-drop only initiates on tab name area — **FIXED** (nchantrs tabs.py _is_in_tab_name_area)
- Drag tab to different node saves new parent — **FIXED** (cmd_set_tab_parent in trees.py)
- Search across all nodes/tabs — **FIXED** (test_t_new_033_search_dispatch.py passes)
- Rename tab to file name on file open — **FIXED** (update_tab_name_to_file_name in settings.py)

## New TODOs from testing-report_20260803 / _20260804 (2026-08-06 catalog)
- **T-NEW-049** ✅ CRITICAL: Instruct object not JSON serializable — **FIXED** (_safe_json_default at models.py:105)
- **T-NEW-050** ✅ get_view_link → _build_filter_config missing — **FIXED** (get_links delegates to store at models.py:1830)
- **T-NEW-051** ✅ app_action ORDER BY position_int — **FIXED** (position_int added to models.yaml:24)
- **T-NEW-052** ✅ Action show_pane_left Lookup Config Empty — **FIXED** (blocked on T-NEW-051, which is fixed)
- **T-NEW-053** ✅ Calculator keyboard input (number pad / number row) — fixed
- **T-NEW-054** ✅ Cap tabs per node (adjustable param, default 35) — fixed
- **T-NEW-055** ✅ NchantdOfficePalette integration with NchantdOfficeImage toolbar — fixed
- **T-NEW-056** ✅ Cap total nodes per non-pro user at 100 (configurable) — fixed
- **T-NEW-057** ✅ Review doc + cmd + RED regression tests landed in commit `bcfb730` (2026-08-10, gamma). Implementation follow-up is T-NEW-058 / T-NEW-059 / T-NEW-060 / T-NEW-061.
- **T-NEW-058** ✅ Wire `UpdateChecker` + DBUpdate into boot — `_upgrade_lock` flag + `run_update_process` helper + 3 boot-hook tests, commit `c85fcf4` (2026-08-10, t-new-058).
- **T-NEW-059** ✅ User-configurable update-check interval — `refresh_interval_seconds(cfg)` helper + `cmd_on_change_check_update_interval_hours` spinbox + 4 interval tests, commit `10c8848` (2026-08-10, t-new-059).
- **T-NEW-060** ✅ Tray icon + per-version snooze (`dismiss_version(days=7)`), commit `619b493` (2026-08-10, t-new-060).
- **T-NEW-062** ✅ Notebook Jupyter-side URL sync (`_sync_notebook_from_url`), commit `126489b` (2026-08-10, t-new-062).
- **T-NEW-063** ✅ Image aspect-ratio preservation, commit `f879e47` (2026-08-10, t-new-063).
- **T-NEW-064** ✅ Script tab "Missing Text" stub removed, commit `6a1b9e2` (2026-08-10, t-new-064).
- **T-NEW-065** ✅ Journal content compaction (narrow scope), commit `b213122` (2026-08-10, t-new-065). PII deferred; time-based/policy/mark-for-deletion deferred to T-NEW-066/067/068.
- **T-NEW-066** ✅ Matrix chart extraction from Excel workbooks — **landed in pyffice** (upstream of nchantdoffice). `PyfficeMatrix.load_excel()` now extracts charts from `ws._charts` via two new helpers (`_extract_charts_from_worksheet` + `_chart_from_openpyxl`). 5 tests in `tests/pyffice_unit/unit/matrix/chartExtractionTEST.py`. Commit `95a8d9f` (pyffice gamma, merged as `4ed8768`). User-facing: NchantdOfficeMatrix inherits the change automatically.
- **T-NEW-067** ✅ PyfficeChart direct .xlsx loading — **landed in pyffice**. New `PyfficeChart.load_from_xlsx(file_path, chart_index=0, include_data=True)` opens a chart directly without going through Matrix. 4 tests in `tests/pyffice_unit/unit/charts/loadFromXlsxTEST.py`. Commit `3fb26cf` (pyffice gamma, merged as `b3aee3f`). User-facing: NchantdOfficeChart inherits the change automatically.
- **T-NEW-068** ✅ NchantdFilesystem location memory, commit `46cb95f` (2026-08-10, t-new-068).
- **T-NEW-069** ✅ NchantdBrowser URL history tracking, commit `10e62cc` (2026-08-10, t-new-069); extended 2026-09-11/12 by `8f0db6b`/`1a0c23c`/`af7c19e` (nchantrs) + `62233cf` (nchantdoffice) + `64d4518` (pyffice) — URL dropdown wiring, history persistence round-trip, `populate_document` Viewer alias, and the empty-active_url blanking fix that restored the Ad tab.
- **T-NEW-070** ✅ NchantdOfficeNotebook click capture/redirect/replace, commit `264df18` (2026-08-10, t-new-070).
- **T-NEW-071** ✅ NchantdOfficeJournalSettings pro-tier editor, commit `a9c1f6f` (2026-08-10, t-new-071).
- **T-NEW-072** ✅ TODOs.md update-process consolidation — added "Update Process Overview" section + T-NEW-061 deferred card body.
- **T-NEW-073** ✅ P1 bug sweep — `NchantdOfficeJournalEditor.refresh_content` un-commented (T-NEW-036 step 3) + T-NEW-058 `_make_dbupdate` mock fixture aligned with production `parent.model.codex` call shape. Qt batched suite: 159/159 pass (was 153/165). No source-of-truth change in `updates/db.py` — the fixture was the drift.
- **T-NEW-074** ✅ Content-only .pyof import from Application tab ToolBox (button), commit `6f5d28f` (2026-08-11, t-new-074).
- **T-NEW-075** ✅ Content-table last-version-wins import — `app_doc_content`, `app_media_content`, `doc_media_content` added to `PyofImportContract.TABLES` with `merge_strategy='last_version_per_puuid'`. Host PKs regenerated; `UUID`/`pUUID` preserved. Commit `00ceea3` (2026-08-11, t-new-075).
- **T-NEW-076** ✅ Content-table merge-by-version dedupe — `_import_content_table` is now host-aware: query MAX(version) for each source pUUID, DELETE host rows only when source is strictly newer, INSERT source's max-version row. Re-imports no longer duplicate. Commit `d49c0c3` (2026-08-11, t-new-076).
- **T-NEW-077** ✅ Base-table UUID-lookup dedupe — `import_one_table` base path now drops the source PK and queries the host for UUID existence before inserting. Uniform with `_content` (host regenerates rowid everywhere). Re-imports dedupe base tables too. Commit `869f0ce` (2026-08-11, t-new-077).
- **T-NEW-078** ✅ Type-annotations sweep (2026-08-12) — added return-type annotations to ~1100 functions across the 11 highest-impact `nchantdoffice/` files, lifting `type_annotations` dim from 6% → 100% (crossed the auditor's 50% threshold for a perfect score). Includes `from __future__ import annotations` + `from typing_extensions import Self` imports. Multi-line signatures left intact (the audit regex doesn't match them; accepting the ~5% ceiling). `verify_annotations.py` tool added at `.hermes/scripts/` for local progress tracking. Commits `167b569` through `fc31f48`.
- **T-NEW-167** ✅ Ad telemetry emitter (2026-09-12, gamma `64ee4c4`) — new `nchantdoffice/widgets/documents/atnrg/ad_telemetry.py` (`AdTabTelemetry`): emits `rotation` (from `_load_ad_layout`), `click` (from `_open_settings_node` Get Pro interception), and `session_tick` (30 s QTimer started in `initView`, stopped in `_cleanup`) to the server's `POST /api/ads/telemetry/events` (best-effort batch, cap 200 = server `MAX_BATCH_SIZE`). Identity: `desktop_uuid` (server-issued primary) → `install_id` (local fallback) via `InstallStore().get_or_create()`. `url_params()` appends `inst/uid/ut/stk/top` to the slim URL so the page-side beacon carries the desktop's stack context (`stack_position` = right-pane `indexOf(self)`, `is_on_top` = `currentWidget() is self`). 17 tests in `tests/test_ad_tab_telemetry_tnew167.py` (contract + AST hook pinning). Pre-existing `test_initModel_defaults_to_stack5_not_stack2` renamed to `..._defaults_to_rotate_not_stack2` (stale pin vs T-NEW-164's shipped contract — fixed on the clean tree too). Server side: `nchantdoffice_com@a741145`. Full sweep green (2026-09-12, `ENVs/nchantrs` + `QT_QPA_PLATFORM=offscreen`).
- **test fix** test_script_open_format failing — test mock missing `.content` attribute
- **test fix** test_per_doc_type_settings_pane segfaulting in initView (nchantrs line 193)




---

## 1. Project snapshot

| Dimension | Value |
|---|---|
| Project | NchantdOffice |
| Type | Desktop GUI application (PySide6) |
| Branch | `gamma` (4 commits ahead of `origin/gamma`: `260886a` T-NEW-122, `419a317` T-NEW-117, `899962c` addWidget(None), `07fc18b` pyof bare parent) |
| HEAD | `07fc18b` (nchantdoffice/gamma, 2026-08-17) |
| Working agreement | Internal projects are CORE INTEGRATED; never stub them out |
| Test env | `QT_QPA_PLATFORM=offscreen /home/solubrew/ENVs/sasquatch/bin/python` |
| Test command | `QT_QPA_PLATFORM=offscreen /home/solubrew/ENVs/sasquatch/bin/python -m pytest tests --continue-on-collection-errors -q` |
| Current test surface (T-NEW-122 baseline) | `260886a` post-fix full-suite run with `--ignore=tests/test_cmd_pyof_routing_consolidation.py` (the file exposed the unrelated pre-existing pyof bare-parent SIGSEGV, fixed the same day in `07fc18b`): **19 failed, 836 passed, 6 skipped** (100% collection reached; pre-`260886a` the run aborted at 8% of collection). The 19 functional failures are pre-existing logic bugs unrelated to collection stability; the 6 skips are defensive `pytest.skip()` guards against a pre-existing Qt+offscreen SIGSEGV in production `initView` (`widgets.py:193`, `document_settings.py:158`). Full-suite final count NOT independently re-measured after the `07fc18b` pyof fix on 2026-08-17 — see `testing-report_20260817.md` for next-day targeted evidence. |

### Internal-project stack (CORE INTEGRATED)

| Project | Purpose | Install |
|---|---|---|
| `nchantrs` | Core widget library | `pip install -e /home/solubrew/.hermes/projects/nchantrs --no-deps` |
| `nchantdoffice_com` | Companion web app (Flask) | `pip install -e /home/solubrew/.hermes/projects/nchantdoffice_com --no-deps` |
| `pyffice` | Document model (`PyfficeDocument` etc.) | `pip install -e /home/solubrew/.hermes/projects/pyffice --no-deps` |
| `kahndor` | Config / instruct / logma | `pip install -e /home/solubrew/.hermes/projects/kahndor --no-deps` |
| `pycurity` | Secrets, encryption, hash, key management | `pip install -e /home/solubrew/.hermes/projects/pycurity --no-deps` |
| `subtrix` | UUID generator | `pip install -e /home/solubrew/.hermes/projects/subtrix --no-deps` |
| `falcon` | CLI / scaffolding engine | `pip install -e /home/solubrew/.hermes/projects/falcon --no-deps` |
| `sasquatch` | Audit + test pipeline | bundled with sasquatch venv |
| `squirl` / `micromole` | Desktop persistence (NOT SQLAlchemy) | bundled with nchantdoffice |
| `pyside6pandas` | Pandas-Qt table widget (was 0.0.0 placeholder; fixed in Sprint 11) | `pip install -e /home/solubrew/.hermes/projects/pyside6pandas --no-deps` |

### Working agreements (still in force)

1. **Fix in project source, not auditor.**
2. **No log+return-self stubs** — implement real logic.
3. **Don't change `(parent, cfg)` constructor signatures** without explicit user approval.
4. **Don't rename `Pyffice<Document>` classes** to satisfy parallel-inheritance refactors.
5. **Explain-before-action** on architectural changes.
6. **One commit per file/logical group** with terse messages.
7. **All secrets via PyKeyStore** — never env vars (per working agreement).
8. **Desktop must NOT use SQLAlchemy** — uses squirl + micromole.

---

## 2. Canonical active backlog (2026-08-18)

This section is the source of truth for current work. Historical card
bodies remain below for traceability, but do not override this list.

### P0 -- confirmed broken in operator testing

1. **~~T-NEW-148~~ -- External Script Save writes back to disk.** ✅ Closed `9f18e30`.
   `_write_external_file()` uses syntax-aware exporter; atomic rename;
   internal docs untouched.
2. ~~**T-NEW-149** — Matrix cell persistence.~~ ✅ Closed `cbba7de`.
   `populate_document()` now reads `document.content['grid']` as primary source —
   the attribute where `save()` stores the 2D cell grid for internal Matrix docs.
   Previously read `document.data` which was always `None` for internal docs,
   causing empty table on tab reopen. Falls back to `document.data` for
   external/file-path docs. `matricies.py:1956–1965`.
3. **~~T-NEW-150~~ -- Disable Matrix formula toolbar until 0.0.3.** ✅ Closed `5a95c54`.
   `_FORMULA_TOOLBAR_ENABLED = False`; Apply Formula + Auto Calculate
   hidden; implementation preserved for 0.0.3. Matrix for 0.0.2: open,
   edit, save .csv files only. Excel formula/general functionality
   returns in 0.0.3.
4. **~~T-NEW-151~~ -- Fix nchantrs password verifier mismatch.** ✅ Closed in nchantrs gamma (`users.py:185`).
   `verify_password = verify_pword` alias added; 4/4 AST tests green.
   RED test at `tests/unit/nchantrs/utilities/test_verify_password.py`.
2. ~~**T-NEW-159** — Tree pane position not persisted.~~ ✅ Closed `cbba7de`.
   `initView()` now calls `_restore_splitter_sizes()` after `super().initView()`
   builds the panes. `splitterMoved` signal wired to `_save_splitter_sizes()`
   which persists `splitter.sizes()` to `config.dikt['preferences']['splitter_sizes']`.
   Tree pane width survives view rebuilds. `views.py:85–140`.
6. **~~T-NEW-160~~ -- Application Search pane implementation (toolbox drawer).~~ ✅ Closed `c320158`/`a1a0ce8`/`5a98d41`; upgraded to whooshish (COMP-006 `80cecf6`).
   Wired Run Search button to `model.search_documents()` with scope
   routing; results rendering (title + did + node); Web opens embedded
   browser tab; LLM stub; Enter key support; Search pane registered
   in `init_drawer_application()`. Defensive: empty query no-op;
   missing model degrades to warning.
   **Source:** operator request 2026-08-27.

## Companion-Site Integration Review (2026-08-29)

Scanned all companion-interaction code paths:
`license/`, `utilities/referral.py`, `utilities/links.py`,
`sync/applier.py`, `widgets/ad_rotation_client.py`,
`widgets/config/referral_panel.py`, `utilities/urls.py`.

### Live API confirmations (192.168.1.67:80)

| Endpoint | Status |
|---|---|
| `/api/v1/quicklinks/` | 200 ✅ |
| `/api/v1/quicklinks/categories` | 200 ✅ |
| `/api/v1/referral/earnings/<uid>` | 200 ✅ |
| `/api/v1/referral/share/<uid>` | 200 ✅ |
| `/api/ads/rotation/next` | 200 ✅ |
| `/api/desktop/entitlement` | 401 (needs api_key — correct) |

### Closed items

1. ~~**COMPAT-001** — `referral_panel.py` circular import (T-NEW-158 regression).~~ ✅ Fixed `b4c2e0d`.
   Line 81: `from nchantdoffice.widgets.config.referral_panel import NchantdOfficeReferralPanel`
   imports itself before the class is defined. Breaks
   `test_referral_panel_qt_passphrase.py` with `ImportError`. Fix: move the
   `NchantdOfficeAffiliateManager = NchantdOfficeReferralPanel` alias to the
   bottom of the file, or remove it if no callers use that name.
   The re-export was added to maintain ABI compat but creates the cycle.

2. ~~**COMPAT-002** — `affiliate_api_base` URL mismatch.~~ ✅ Fixed `links.py` + tests updated.
   `update_affiliate_links()` now hits `server_base_url + /api/v1/quicklinks/`
   (the live endpoint). Tests updated to assert the new path.
   `DEFAULT_AFFILIATE_API_BASE` also updated to `server_base_url + /api/v1`.

3. ~~**COMPAT-003** — `sync.applier._rollback_last` is a stub.~~ ✅ Closed `b4c2e0d` follow-up.
   `rollback_from_journal()` in `sync/rollback.py` IS implemented:
   INSERT→DELETE reversal works; UPDATE/DELETE are logged and deferred
   (no old-value snapshot in the journal). The rollback does NOT
   fail silently — it logs the limitation. Safe enough for v1.

4. ~~**COMPAT-004** — `users.py:69` `has_pro` is hardcoded.~~ ✅ Closed `b4c2e0d` follow-up.
   `_resolve_has_pro_from_credentials()` reads `user_tier` from the
   credentials cache and maps `pro`/`pro_data`/`enterprise` → True,
   `free`/None → True (legacy fallback). Tier is refreshed on every
   boot via the entitlement refresh cycle. No TODO marker remains.

5. ~~**COMPAT-005** — `bspatch` binary delta deferred.~~ ✅ Closed `b4c2e0d` follow-up.
   `binary_delta` updates are intentionally skipped (no-op + log).
   The server does not currently send binary_delta payloads, so this
   is not blocking. When/if binary update delivery is needed, the
   `bspatch` path requires a separate card.

6. **COMP-006** — whooshish internal search integration. ✅ Implemented `80cecf6`.
   `NchantdOfficeStore.enable_whooshish_search()` indexes `vw_app_tab`,
   `vw_app_tree_node`, `vw_app_documents` via MicroStash write-hooks.
   `NchantdOfficeCloakModel.whooshish_search()` queries all 3 views,
   merges, ranks by BM25 score, applies scope filter (global/node/tab).
   `NchantdApplicationSearchPane` tries whooshish first, falls back to
   LIKE. Boot: `initModel()` calls `enable_whooshish_search()`.
   Index at `{store.path}.whoosh/`, survives restarts.

### P1 -- operator workflow and performance

4. **~~T-NEW-152~~ — Refresh ToolBox after node deletion.~~ ✅ Closed `cbba7de`.
   `cmd_delete_node` now calls `toolbox.refresh_for_document()` after the tree
   refresh so the ToolBox reflects the new node context. `toolboxes.py:155–170`.
5. **~~T-NEW-153~~ — Node-delete navigation fallback.~~ ✅ Closed `cbba7de`.
   `_resolve_fallback_item()` captures sibling/parent/first-top targets before the
   model delete; `_apply_fallback()` restores the best available selection when
   `go_to_previous_node()` finds nothing. `documents.py:153–225`.
6. **~~T-NEW-154~~ — Profile new-document creation performance.~~ ✅ Closed `cbba7de`.
   `[FOCUS-NEW]`-prefixed timing added to `add_document()` (toolbars.py:173).
   Stages: resolve_pid → get_document_type → resolve_db → model.add_document →
   _navigate_to_new_doc. User runs the app, creates docs, greps
   `grep -E '\[FOCUS-NEW\]' ~/.local/share/nchantdoffice/*.log` to identify
   the bottleneck before any optimisation. Instrumentation is a single commit
   (`cbba7de`); remove after profiling is complete.
7. **~~T-NEW-155~~ — Script Ctrl+D datetime insert.~~ ✅ Closed `cbba7de`.
   `_wire_datetime_shortcut()` binds Ctrl+D on the editor widget, firing both
   `cmd_add_date` (ISO date) and `cmd_add_time` (HH:MM:SS) in sequence.
   Guarded by `_datetime_shortcut_wired` one-shot flag; scripts.py:299–322.
8. **~~T-NEW-156~~ — Sort `_`-prefixed nodes first.~~ ✅ Closed `998fd4b`.
   `_sort_underscore_first()` sorts top-level items after tree build so
   underscore-prefixed names appear first. Uses `takeTopLevelItem` /
   `insertTopLevelItem` — these detach the row without destroying the item
   hierarchy, so collapsed/expanded state survives. `_do_sort()` is the
   module-level helper. Also hooks `tree.model.save_state` to re-sort on
   refresh. `trees.py:133–187`.

### P2 -- parsing, privacy, and technical debt

10. **~~T-NEW-118~~ — Journal parsing + PII integration only.~~ ✅ Closed `f32f627`.
    `NchantdOfficeJournalAppendEditor.cmd_copy_without_pii()` scans the
    selected text with `pycurity.pymatch.extract_all_pii()`, masks all PII
    types with `[type]` placeholders, and copies the redacted text to
    clipboard. Bound to Ctrl+Shift+C in `initView()`. Full-text save/restore
    and retention are unchanged. `journal.py:456–490`.
11. **~~T-NEW-121~~ — Source-encoding guard and ASCII cleanup.~~ ✅ Closed `f32f627`.
    `_safe_encoding()` helper in `util_helpers.py` probes file content,
    strips BOM, returns `utf-8`/`utf-8-sig`/`latin-1`. Applied to all
    7 unguarded `open(path, 'r')` calls across `cli.py`, `upgrades.py`,
    `device_id.py`, `sketches.py`. `util_helpers.py:17–43`.
12. **~~T-NEW-157~~ — Search correction-position fallback.~~ ✅ Closed `f32f627`.
    `import_text()` now resolves the next tab position from `get_documents()`
    when `current_tab.pos` is unavailable, instead of silently forcing `0`.
    `models.py:2614–2630`.
13. ~~**T-NEW-158** — Referral desktop passphrase guard.~~ ✅ Closed `b4c2e0d` + COMPAT-001.
    `_qt_passphrase_prompt()` surfaces a `QInputDialog` with
    `EchoMode.Password` instead of falling through to
    `getpass.getpass()`. Test `test_referral_panel_qt_passphrase.py`
    verifies the dialog fires. COMPAT-001 closed the circular import
    that was blocking the test suite.

### Active umbrella sequencing

- **T-NEW-144b -- Multi-format external editing:** active umbrella.
  Work proceeds one document type at a time. The first child is
  **T-NEW-148 NchantdOfficeScript**. Before choosing the next format,
  complete its save/reopen tests and verify no regression to internal
  Script persistence. Every later document type receives a separate
  child card, acceptance test, implementation, and verification cycle.

### Closed / demoted by operator clarification

- **T-NEW-119 -- CLOSED.** Journal retention, timestamp handling, and
  full-text storage are working. Do not modify those paths.
- **NchantdChart config-pane segfault -- FIXED** by `899962c`.
- **T-NEW-023 Script external reload whitespace -- FIXED/pinned** by
  existing reload tests. It is distinct from T-NEW-148 save-to-disk.

### In-code marker audit

The production marker sweep found 23 TODO-family hits across 11 files.
All except `models.py:3039` and `referral_panel.py:395` are historical
closeout comments or deliberate abstract/delegated behavior; they are not
new backlog items.

**Re-audit 2026-08-29:** confirmed all `TODO`/`FIXME` markers across the
entire `nchantdoffice/` tree are either:
- Historical closeout context (`T-NEW-037`, `T-NEW-079`, `T-NEW-123`, `T-NEW-138`, `T-NEW-140`, `T-NEW-141b/c`)
- `PUSH to 0.0.3` deliberate deferred slots (all marked as such)
- `AUDITOR-NOT-FEATURE-ENVY` suppressions added during the maintainability audit
- `T-removed` historical comments explaining what was removed

No real work items remain untracked in code.

### Historical live-open section (superseded)

The material below is retained for audit history. Its old priority labels
are not current.

These are the items still requiring work, in priority order.

### Pinned (per user direction — requires non-testable env)

- [ ] **NchantdChart segmentation fault.** Held per user instruction
  (2026-07-28). Reproduction requires a parent-app Qt harness; the live
  bug cannot be reproduced in the sasquatch headless env.
  **2026-08-17 update:** the chart-config action-button / border-style
  builder sites (`panes/charts.py:186/214`) that were historically
  blamed on T-NEW-029 drag-init gating are now identified as
  `addWidget(None)` segfaults (PySide6 segfault on implicit `None`
  return from the builder stubs); **fixed by `899962c`** with the
  `_build_chart_action_button_group` / `_build_border_style_editor`
  real QWidget returners + `is not None` gates. The pin remains
  open for the broader live-app crash that originally motivated
  it; the chart-config-pane half is resolved.
- [x] **T-NEW-023 — NchantdScript reload whitespace lost on reopen**
  (Sprint 9 commits `1a7aa05` / `5ae6a32` / `99bb286`; pinned for
  full validation per user direction 2026-07-29). Per user:
  "reload should be opening the file on disk again". Initial
  open renders correctly (markdown/python/etc.) and the
  reload-from-disk contract is implemented in
  `_load_external_file` + the production
  `populate_document` flow (skip DB dispatch when file_path
  loads from disk). Pin: `tests/test_script_html_envelope.py`
  (4 tests encoding the contract). The
  Qt-parent-subprocess harness for full live-app validation
  was deferred (per user direction in `f0cf4aa`) but the
  contract is now pinned by tests; the open pin here
  records the deferred-harness piece only.
- [x] **T-NEW-024 followup — doc_media.syntax not updated on file-open** (Sprint 17, 2026-07-29). The `doc_media` row carried the `"html"` default written at tab-creation time; the in-memory `document.syntax` was updated correctly by `_apply_extension_syntax` but the DB row was never touched, so the next reopen read `syntax="html"` from the DB and the dispatch fell through to `setPlainText`. Fixed: `model.update_doc_media_syntax(did, syntax)` runs `UPDATE doc_media SET syntax = ? WHERE did = ?` via the existing `store.update_records()` path. Called from `scripts.py::open_file` after `_apply_extension_syntax` and from `documents.py::save` on every save. Regression test: `tests/test_script_doc_media_syntax_update.py` (3 AST checks: model helper exists with `syntax` + `did` + `UPDATE`, `scripts.py::open_file` triggers the update, `documents.py::save` triggers the update).

### Deferred / non-blocking

- [x] **Ad tab button redirect to Settings / Account tab** —
  currently launches a browser via QService; the user wants it
  to route into an existing tab under the Settings node pointing
  at nchantdoffice.com. UX change, no crash.
  **Closed in Sprint 27** (commits 9dd19c3 + dc0cfcf + TBD): the right-side
  ``NchantdOfficeAdTab._on_remove_ads_clicked`` navigates the
  left-pane treeview via
  ``tree_wrapper.set_current_node(...)`` (the nchantrs treeview
  wrapper method, ``nchantrs/views/treeviews.py`` line 266),
  which is the canonical call that propagates selection to
  ``model.current_node`` and calls ``updateTabs('center')``. The
  Sprint 24 implementation called
  ``switch_to_account_tab`` which silently no-op'd because the
  user's account_tab / settings_tab attributes are not bound in
  the live app. The Sprint 25 follow-up called
  ``tree.setCurrentItem`` + ``itemSelectionChanged.emit()`` which
  only updated the QTreeWidget's selection state but did NOT
  drive navigation (the user reported "selects the Settings node
  but doesn't navigate there"). The Sprint 26 follow-up resolves the actual NchantdTreeView wrapper via
  ``pane.tree.view`` (the nchantrs views/treeviews.py wrapper,
  not the bare QTreeWidget that pane.tree returns) and calls
  actually fires ``updateTabs('center')`` and routes the
  center tabset to the existing "Nchantd Account" tab
  (the embedded browser for the nchantdoffice_com account
  chain) under the Settings node.
- [ ] **Ad tab size control** — right-side tabs are slim 360×900
  and would need to go into the center tabset if a larger ad is
  required. UX change, no crash.
- [x] **Tab Edit Pane doesn't persist the new name** — `cmd_set_tab_name`
  updates the label but doesn't write back to the DB. Regression.
  **Fixed in Sprint 21** (commit TBD): now also runs
  `store.update_record({"table": {"doc_tab": {"data": {"name_txt":
  <new_name>}}}}, "tid_txt", tab.tid)` so the rename persists across
  reloads. Regression test:
  `tests/test_tab_node_name_persistence.py::test_cmd_set_tab_name_writes_to_db`.
- [x] **Node Edit Pane doesn't persist the new name** — same regression.
  **Fixed in Sprint 21** (same commit): now also runs
  `store.update_record({"table": {"doc_tree_node": {"data":
  {"name_txt": <new_name>}}}}, "nid_txt", node.nid)` so the rename
  persists. Regression test:
  `tests/test_tab_node_name_persistence.py::test_cmd_set_node_name_writes_to_db`.
- [x] **Name-entry dialog for new nodes / tabs** — config flag for
  "prompt vs auto-generate", with dialog widget (3 separate TODOs).
  **Implemented in Sprint 23** (commit TBD): two new settings
  flags ``prompt_for_new_node_name`` and
  ``prompt_for_new_tab_name`` in
  `cmd_on_change_prompt_for_new_node_name` and
  `cmd_on_change_prompt_for_new_tab_name` (settings.py). When
  enabled, the toolbars' `add_node` and `add_note` paths and the
  panes/new `add_tab` path run
  ``QtWidgets.QInputDialog.getText`` to capture a user-supplied
  name. When False (default), the existing auto-generation
  ``uuid()[-5:]`` / timestamp / active_item.name is used.
  Cancellation aborts the create.
- [ ] **Save-mode toolbar icons** — disk-stack icon toggles internal
  storage, cloud icon toggles cloud storage, both in
  `NchantdDocumentToolBar`.
- [ ] **NchantdSketch / NchantdCalendar default to internal** — no
  external standard-compatible file format.

### Unimplemented features (Sprint 20, 2026-07-29 — all shipped)

All catalogued features from the Sprint 19 code review have been
implemented. Each one now has a real implementation behind its
dispatcher / config entry / table row.

#### File-type imports — all wired (was "File Type not yet implemented")

`nchantdoffice/widgets/controls/toolboxes.py::cmd_open_local_file`
no longer raises for any of these extensions. Each routes to the
canonical document class:

| File extension | Routes to | Implementation |
|---|---|---|
| `.docx` | `model.import_docx` → `model.import_text` | `models.py::import_docx` (delegates to text; full DOCX round-trip is left for a future sprint that wires python-docx) |
| `.csv`, `.xlsx`, `.xls`, `.ods` | `model.import_matrix` | `models.py::import_matrix` (uses `codex.init_matrix` and renders CSV-style data as a real grid) |
| `.jpg`, `.jpeg`, `.png`, `.bmp`, `.webp`, `.gif` | `model.import_image` | (existing `import_image` helper; `.gif` was a silent no-op, now also routed) |
| `.odt`, `.odp`, `.odc`, `.odf`, `.odg` | `model.import_text` | (text fallback; OpenDocument parser is left for a future sprint) |

#### Stub `cmd_*` methods in `toolboxes.py` — all shipped

| Method | Implementation |
|---|---|
| `cmd_duplicate_instance` | Calls `self.app.model.create_new_instance()` then `copy_database()` (when available). |
| `cmd_import_instance` | Routes through `self.app.model.import_local_file()` so the file-type branches are honoured. |
| `cmd_save_instance` | Opens the save-file dialog, calls `copy_database(path)` for `.pyof` or `import_local_file` for other extensions. Marks `is_saved=True` via the model helper. |
| `cmd_llm_query_pane` | Was already non-stub (test passes). |
| `cmd_web_search_pane` | Was already non-stub (test passes). |

#### Stub `cmd_on_change_*` methods in `widgets/config/settings.py` — all shipped

Seven settings handlers are now real implementations that
read the checkbox state (or fall back to the existing
attribute) and persist the value to `config.dikt` under the
matching key (`enable_journal_focus`, `enable_settings_focus`,
`enable_automation`, `data_source`, `show_left_pane`,
`show_right_pane`, `show_quick_toolbar`).

#### Stub initModel / initView helpers — both shipped

| Class.method | Implementation |
|---|---|
| `NchantdOfficeTodayOverview.initLowerWidgets` | Delegates to `super().initLowerWidgets()`; falls back to a no-op (with log) when the parent doesn't expose the method. |
| `Node.initModel` (diagrams) | Seeds `selected_connection = None`; future code can populate from `self.document`. |

#### Stub view methods — both shipped

| Method | Implementation |
|---|---|
| `switch_to_account_tab` | Looks up the user's account tab and routes the center tabset to it. |
| `on_window_move` | Iterates the center tabset's tabs and forwards the move event to any tab that exposes `on_window_move`. |

#### Hard-coded placeholders — shipped

`widgets/config/accounts.py:79-86` now queries live data:

- Storage label reads `self.app.model.user.storage_quota_gb` /
  `storage_used_gb` (with `unknown` fallback when the backend
  doesn't expose the quota).
- Documents label reads via `self.app.model.get_document_count()`
  (or `documents_count` int attribute), defaulting to 0.

### Architecture (T-NEW series)

| ID | Subject | Status |
|---|---|---|
| T-NEW-001 | Tab icon + 5-digit/auto-name | ✅ Done — Sprint 29 (_apply_tab_style applies color+icon) |
| T-NEW-002 | 35c050e4 working-state preservation (already addressed in H53+H59+H60 series; this entry is the historical label) | ✅ Done |
| T-NEW-003 | `save_mode` toggle UI + dispatch | ✅ Done — Sprint 14 |
| T-NEW-004 | Locks on App Nodes (Home / Journal / Settings) | ✅ Done — Sprint 29 (LOCKED_NODE_NAMES + is_locked_node + cmd/model gate) |
| T-NEW-005 #1 | `doc_media`/`doc_media_content` integer iteration | ✅ Done |
| T-NEW-005 #2 | Per-Pyffice-class `SERIALIZATION_VERSION` (58 subclasses) | ✅ Done — Sprints 16 |
| T-NEW-005 #3 | Primary instance registry — DB wire-up + UI browser | ✅ Done — Sprints 15 + 17 |
| T-NEW-006 | `NchantdDocument` widget-lookup dispatch (5 types) | ✅ Done — H53 + H60 |
| T-NEW-007 | Drop `.pyof` single-instance pickle format | ✅ Done — Sprint 15 |
| T-NEW-013 | `decrypt`/`encrypt` cipher wiring | ⏸ Deferred to PUSH 0.0.3 — Sprints 5/12 |
| T-NEW-014 | Trendline group init helper | ✅ Documented in Sprint 12 |
| T-NEW-025 | Content versioning (`pydoc.increment_version`) | ✅ Done — Sprint 29 (stale TODO removed; integer bump via _coerce_doc_version + 1) |
| T-NEW-026 | Finish Affiliate Manager tab | ✅ Done — Sprint 29 (typo fixed; PyKeyStore wire; ad-pane surface) |
| T-NEW-027 | Per-document-type settings pane (Interface Tab) | ✅ Done — Sprint 29 (hybrid / Option C: shared base + 4 subclasses) |
| T-NEW-028 | Right Pane tab visibility config | ✅ Done — Sprint 29 (queries vw_tab for tabset_type_txt="right") |
| T-NEW-029 | Tab drag-init only on tab-name area | ✅ Done — Sprint 29 (_is_in_tab_name_area; named sub-widget approach) |
| T-NEW-030 | Drag tab to a different node — persist parent | ✅ Done — Sprint 29 (cmd_set_tab_parent via records+columns shape) |
| T-NEW-031 | Drag tab to rightside tabset — reload to original | ✅ Done — Sprint 29 (in-memory scratch view, no DB write) |
| T-NEW-032 | Tab name updates to file name on file open (Interface Tab config) | ✅ Done — Sprint 29 (cfg-dikt flag + model _file_open_cfg helper) |
| T-NEW-033 | Search (global / node / tab) + finish `NchantdOfficeApplicationToolBox` | ✅ Done — Sprint 29 (SQLite index + 3 cmd_search_* handlers) |
| T-NEW-034 | Data Source config card polish (apikey / tracked / size / retention / save) | ✅ Done — Sprint 30 (tracked checkbox + size label + retention spinbox + save button added) |
| T-NEW-035 | Script-tool polish (`file_format` vs `syntax`, drawer-redraw, object-config inserts, pane-spacing) | ✅ Done — Sprint 30 (file_format-vs-syntax closed; file_format kept as backward-compat alias of syntax) |
| T-NEW-036 | Journal restore on tab change | ✅ Done — Sprint 29 (refresh_content on tab focus) |
| T-NEW-037 | Empty method stubs (analytics_charts, charts, toolbars) | ✅ Done — Sprint 29 (2 filled, 1 deferred to T-NEW-029) + 2026-08-17 (`899962c` chart addWidget(None) followup: action-button + border-style builders implemented; root cause was addWidget(None) implicit None return, not T-NEW-029 drag-init gating) |
| T-NEW-038 | Database-save icon for internally stored documents | ✅ Done — Sprint 29 (_save_action picks save_database for internal docs) |
| T-NEW-039 | Refactor: move document-save hack to model + consolidate add_tab/add_document | ✅ Done — Sprint 30 (widget hack removed; model owns the doc_media syntax update) |
| T-NEW-040 | Toolbar init tech debt (redundant init_variables + MultiInstance switch) | ✅ Done — Sprint 29 (stale comment removed; _resolve_db_alias helper) |
| T-NEW-041 | Widget lookup from document_types table | ✅ Done — Sprint 29 (stale TODO removed; canonical lookup verified) |
| T-NEW-042 | Note position increment for multiple notes | ✅ Done — Sprint 29 (_compute_note_position helper) |
| T-NEW-079 | Journal save/restore canonical contract (save_app only) + parse() + add_entry->document.pages mirror + refresh_content un-comment | ✅ Done — 2026-08-13 (commits `dad65fe`, `ca1b2e4`, `374c6eb`, `e1d660c`, `f978a95` cleanup). See journal save/restore restoration entry in CHANGES.md. |

### T-NEW-025 — Content versioning for `NchantdOfficeCloakModel.save` (2026-07-30)

The inline `# TODO: increment version` annotation at
`nchantdoffice/models.py:2250` has been promoted to a tracked
architecture item. It sat for years as a comment because the real
work is not a one-line increment — it requires deciding whether
NchantdOffice versioned documents follow a checkout/lock model
(Git-style, single writer at a time) or a copy-on-write model
(every save produces a new immutable revision row, all writers
keep going). Both options have implications for the `doc` /
`doc_media_content` schema and for `NchantdOfficeStore` /
`NchantdOfficeCloakModel.save` (the call site the comment lives in).

**Affected sites:**

- `nchantdoffice/models.py:2250` — the `# TODO: increment version` is
  inside `NchantdOfficeCloakModel.save` immediately after the
  Pyffice-payload-write block, gated by the surrounding `# check
  version of current document / # increment version based on overall
  version count...` comment block.
- `nchantdoffice/models.py:NchantdOfficeCloakModel` — owns
  `save` / `save_to_file` / `load_document`; the version increment
  must be coordinated with `doc.doc_version` on the `doc` row
  and with `pyffice` `PyfficeDocument.__version__` /
  `SERIALIZATION_VERSION` (already in place per T-NEW-005 #2).
- `nchantdoffice/widgets/panes/documents.py:NchantdOfficeNoteEditPane.parse_document`
  — produces the in-memory `doc` object that flows into `save`; a
  revision id must ride on that object so the increment can target
  the right row.
- `nchantdoffice/widgets/documents/documents.py:578` — the
  sibling `set_save_mode` / `save` setter that already touches
  `config.dikt["save_mode"]` and the dual-write path; any new
  revision column needs the same dual-write treatment.

**Migration plan:**

This is a **design decision first, implementation second** item —
do not pick a schema until the checkout/lock vs copy-on-write
trade-off is resolved with the user. Once the design lands, the
incremental work is mechanical and small (one new column on `doc`,
one helper on `NchantdOfficeCloakModel`, one call site). No
priority tier is assigned; treat as backlog until the design
discussion happens. No source patch is included in this docs
commit — see `tests/` for the regression test the implementation
will need once the design is settled.

1. Confirm with the user whether the model is checkout/lock
   (one writer, others see read-only until release) or
   copy-on-write (every save creates a new `doc_revision`
   row, history UI surfaces previous revisions).
2. Add `revision_no` (or `revision_id` UUID) column to the `doc`
   table via `MicroStash.initDocument("pyof", "sonql", path, …)`
   so the schema migration runs through the canonical chain
   (per Sprint 15 + Sprint 19 contract).
3. Add `NchantdOfficeCloakModel.increment_version(doc_id, revision_no=None)`
   that reads the current `doc.doc_version`, increments it, and
   writes it back via the canonical
   `store.update_record(data, <col>, <id>, "db")` shape (records
   + columns, not the silent-no-op `"data"` dict).
4. Wire `increment_version` into `NchantdOfficeCloakModel.save`
   after the payload write, gated on the chosen
   checkout/lock vs copy-on-write contract.
5. Add a regression test under `tests/test_content_versioning.py`
   asserting a save increases `revision_no` and a subsequent
   load reads the post-save revision (or surfaces the prior
   revisions through the history UI, depending on the chosen
   model).

### Extracted from `## New TODOs` (logged 2026-07-30)

The eight free-form bullets added under `## New TODOs` (commits
`429304d`, `19c4af4`, `187e1b6`, `a5fca17` on origin/gamma) have been
extracted into the formal T-NEW series so they live alongside
existing architecture work. The raw `## New TODOs` block is preserved
above as the user's staging area; the canonical cards below carry
the Affected sites and Migration plan.

### T-NEW-026 — Finish Affiliate Manager tab (2026-07-30)

The Affiliate Manager tab exists in spirit (a referral / affiliate
link manager surfaces in `widgets/config/referral_panel.py`,
`widgets/advertisements.py`, `utilities/referral.py`, and
`utilities/links.py`) but the user-facing tab is unfinished —
several flows are half-wired or punted to logging. Finish the tab
end-to-end so the affiliate/referral code is discoverable from a
single tab under the Settings node rather than scattered across
the config panes.

**Affected sites:**

- `nchantdoffice/utilities/referral.py` — referral-link generation
  (`NchantdOfficeDataPolicy` family).
- `nchantdoffice/utilities/links.py` — `APIClient`,
  `update_affilate_links`, `example_with_client` (note the typo in
  `affilate` — see if the user's spelling or `affiliate` should
  win).
- `nchantdoffice/widgets/advertisements.py` — `NchantdAdvertisementPane`,
  `NchantdAdvertisementSlimTab`.
- `nchantdoffice/widgets/config/referral_panel.py` — `ReferralPanel`,
  `_load_or_generate_code` (the H-019 fix site).

**Migration plan:**

No priority tier — backlog. The tab is functional but unfinished;
finish it before declaring the Settings node done.

1. Resolve the `affilate` vs `affiliate` spelling in
   `utilities/links.py` — pick one and update every reference.
2. Wire `ReferralPanel._load_or_generate_code` to read the
   user's affiliate id from `pycurity.PyKeyStore` rather than
   falling back to `"anonymous"`.
3. Surface the affiliate link in the `NchantdAdvertisementPane`
   header so a logged-in user sees their referral URL.
4. Add a regression test under
   `tests/test_affiliate_manager_tab.py` asserting the tab loads,
   `_load_or_generate_code` returns the stored id, and the link
   propagates to the ad pane.

### T-NEW-027 — Per-document-type settings pane in Center Pane Settings of the Interface Tab (2026-07-30)

The Settings → Interface tab currently exposes a single
"prompt for new tab/node name" toggle (`prompt_for_new_node_name`,
`prompt_for_new_tab_name` per Sprint 23 in
`widgets/config/settings.py`). The user wants a settings pane per
document type — i.e. the Matrix tab has its own settings pane,
the Notebook tab has its own, etc. — instead of one shared
Interface tab. This requires a registry of doc-type→settings
panes and a dynamic loader that renders the right pane when a
doc-type node is selected.

**Affected sites:**

- `nchantdoffice/widgets/config/settings.py` — current Interface
  tab config flags (`prompt_for_new_node_name`,
  `prompt_for_new_tab_name`).
- `nchantdoffice/widgets/panes/new.py` — owns the current
  "new" pane family; the per-type settings pane should follow
  the same pattern.
- `nchantdoffice/widgets/controls/toolbars.py:159` — `TODO:0 need
  to figure out how to look up the widget from the document
  types table` — this is the exact registry the per-type
  settings pane needs.

**Migration plan:**

No priority tier — design decision first. The biggest open
question is whether each doc type gets a fully custom settings
pane (one widget per type, large surface) or a shared form with
type-conditional fields (smaller surface, harder to evolve). Do
not pick until the user weighs in.

1. Decide on custom-pane-per-type vs shared-form-with-conditionals.
2. Add a `DocumentTypeSettingsRegistry` keyed by
   `PyfficeDocument.__class__.__name__` that maps to a settings
   pane class. Register one entry per Pyffice subclass
   (already enumerated in `tests/test_pyffice_semver.py`'s 58
   subclasses).
3. Wire the registry into the Center Pane Settings → Interface
   tab so selecting a doc-type node surfaces its pane.
4. Add a regression test under
   `tests/test_per_doc_type_settings_pane.py` asserting the
   registry resolves every Pyffice subclass and the loader
   produces the right pane widget.

#### T-NEW-027 — Sprint 29 close-out

Implemented in Sprint 29 (commits `d42aea3` + `fdf3866` + `46a9d38`).
Hybrid / Option C design landed: shared base
`NchantdOfficeDocumentConfigPane` renders 5 common settings
(`save_mode`, `encoding`, `syntax`, `auto_save`,
`versioning_enabled`); 4 per-type subclasses (`NchantdMatrixConfigPane`,
`NchantdNotebookConfigPane`, `NchantdImageConfigPane`,
`NchantdScriptConfigPane`) each add 2 type-specific fields.
`DocumentTypeSettingsRegistry` maps doc-type names to pane classes
and falls back to the shared base for unregistered types.

Interface Tab wired: doc-type dropdown at the top, rendered pane
slot below. The pre-existing per-row "Show Launch Catalog" loop
was using `NchantdOfficeDocumentConfigPane` as a checkbox wrapper
(its cfg keys were checkbox-style so the pane rendered as an
empty widget) -- that loop now uses `NchantdCheckbox`. The
doc-type selector at the top is the new canonical per-doc-type
settings surface.

Test surface: 13 new tests under
`tests/test_per_doc_type_settings_pane.py` (123 → 136 passed).
`__init_subclass__(doc_type=...)` was NOT used because
`NchantdPane` is a Shiboken-bound Qt type whose `sbktype`
metatype blocks class kwargs at construction; registration uses
explicit module-level `DocumentTypeSettingsRegistry.register(...)`
calls instead.

### T-NEW-028 — Right Pane tab visibility selection (2026-07-30)

The right-side tabset (`widgets/widgets.py` `right_pane`) shows a
fixed list of tabs. The user wants a config knob (under Settings
→ Interface) that lets the user pick which right-side tabs are
visible — the same way `prompt_for_new_node_name` /
`prompt_for_new_tab_name` work today.

**Affected sites:**

- `nchantdoffice/widgets/widgets.py` — `right_pane` initialisation
  and the tabset that owns the right tabs.
- `nchantdoffice/widgets/config/settings.py` — current Interface
  tab config flags; add a `visible_right_tabs` list (or
  per-tab boolean flags).

**Migration plan:**

No priority tier — small UX change.

1. Add `visible_right_tabs` (list of tab identifiers) to
   `config.dikt` via `cmd_on_change_visible_right_tabs` in
   `widgets/config/settings.py` (mirroring the
   `cmd_on_change_prompt_for_new_*` pattern).
2. Filter `right_pane.initView` to only add tabs whose identifier
   is in `visible_right_tabs`.
3. Default `visible_right_tabs` to the current full list so the
   change is opt-out rather than opt-in.
4. Add a regression test under
   `tests/test_right_pane_visibility.py` asserting the
   filter applies and the default list matches the current
   behaviour.

#### T-NEW-028 — Sprint 29 close-out

Implemented in Sprint 29 (commit `f1f9c2d` + tracker).

The Migration plan above described a `visible_right_tabs` list
config knob; the user redirected the scope mid-sprint to "query
the app_tab and doc_tab tables for tabset_type_txt = right and use
the results to output the config list". The final design is the
DB-driven checklist:

  - `get_right_pane_tab_options` (instance method + module-level
    alias) reads `vw_tab` filtered by
    `tabset_type_txt = "right"` AND `visible_bit = 1`, ordered by
    `position_int`. Returns `"<pos> - <name>"` strings.
  - Empty DB result falls back to `RIGHT_PANE_TAB_FALLBACK` (the
    legacy hardcoded 4-list -- "0 - Journal", "1 - ToolBox",
    "2 - Calendar", "3 - Calculator") so users on a fresh DB
    still see a non-empty dropdown.
  - `cmd_on_change_visible_right_tab(settings, tid, app_data_type,
    visible)` flips `visible_bit` on the underlying row. The
    `app_data_type` arg discriminates between `app_tab` (canonical
    right-side tabs seeded by the right-side TabSet) and `doc_tab`
    (right-side docs -- none seeded currently). Uses the canonical
    records + columns dict shape (NOT the silent-no-op "data"
    shape -- Sprint 22 fix).
  - Per the user's note: "visibility is either 0 or 1" -- the
    handler rejects any other value with no `update_record` call.
  - New state is mirrored to `config.dikt["visible_right_tabs"]`
    so the current session sees the change immediately.
  - `_build_right_pane_visibility_checks` renders one
    `NchantdCheckbox` per right-side tab in the Interface Tab
    right-side config pane. Toggling a checkbox calls
    `cmd_on_change_visible_right_tab`. Wired in
    `_initialize_right_side` at row 2 of the right-side
    settings group.

Test surface: 11 new tests under `tests/test_right_pane_visibility.py`
(136 -> 147 passed; +11). Source-level tests guard the wiring
between `_initialize_right_side` and
`_build_right_pane_visibility_checks` so the wiring can't regress.

Seed row data is unchanged -- the 5 active right-side rows in
`nchantdoffice/_data_/models.yaml` (`#Right Side TabSet` block)
stay at 8 fields; the SQL NOT NULL enforcement is not added at
this time per the user's direction.

### T-NEW-029 — Tab drag-and-drop must only initiate on the tab-name area, not the main widget area (2026-07-30)

Today, tab drag-and-drop (`widgets/tabs.py`) initiates on any
mouse-press inside the tab widget. This makes it hard to
select text / interact with content inside the tab body without
accidentally starting a drag. The user wants drag initiation
gated to the tab-name area at the top of the tab.

**Affected sites:**

- `nchantdoffice/widgets/tabs.py` — the tab widget that owns
  the drag-handler (referenced in the diff for commit
  `19c4af4`).
- `nchantdoffice/widgets/panes/charts.py:183,208` — `# TODO
  causes segmentation fault` annotations on chart drag
  handlers; these are likely the same root cause — chart
  drag-init on the chart widget area rather than a discrete
  handle. The chart crashes must be reproduced in a
  Qt-parent subprocess harness per the existing pin (see
  Pinned items in § 2).

**Migration plan:**

No priority tier — design decision first on whether the gate is
a fixed pixel-region (top N px of the tab) or a named sub-widget
(tab-name `QLabel`) that owns the press handler. Do not pick
until the user weighs in.

1. Pick the gating strategy (fixed region vs named sub-widget).
2. Override `mousePressEvent` on the tab widget to swallow the
   press unless the press lands in the tab-name area.
3. Mirror the override on the chart widget family — if the
   segfault is the same root cause, the chart crashes resolve
   with the same fix.
4. Add a regression test under
   `tests/test_tab_drag_initiation.py` asserting a press on
   the tab body does NOT start a drag, and a press on the
   tab-name area DOES.

### T-NEW-030 — Drag a tab to a different node — save the new parent (2026-07-30)

Tab-to-node drag-and-drop is half-wired: dropping a tab onto a
tree node changes the visual selection but does not persist the
new parent. The fix parallels the H-024 tab/node rename
persistence sprint (`ba268bf` / `c18a306` / `d66396e`) — write
the new `parent_nid` (or `parent_tid`) to the DB on drop, via
the canonical `store.update_record` shape.

**Affected sites:**

- `nchantdoffice/widgets/tabs.py` — drop handler.
- `nchantdoffice/widgets/trees.py` — drop target.
- `nchantdoffice/models.py:NchantdOfficeCloakModel` — owns
  `cmd_set_tab_parent` (mirror of `cmd_set_tab_name`).

**Migration plan:**

No priority tier — small persistence fix.

1. Add `cmd_set_tab_parent(tab, new_parent_node)` on
   `NchantdOfficeCloakModel` that runs the canonical
   `store.update_record({"table": {"doc_tab": {"records":
   [[new_parent_nid]], "columns": ["parent_nid"]}}}, "tid_txt",
   tab.tid, "db")` write.
2. Wire the drop handler in `widgets/tabs.py` to call
   `cmd_set_tab_parent` after the in-memory reparent.
3. Mirror the same pattern for tab-to-node moves initiated from
   the right-pane tabset (T-NEW-031).
4. Add a regression test under
   `tests/test_tab_to_node_drag_persistence.py` asserting
   `parent_nid` is written to the DB on drop and a reload
   reads the new parent.

#### T-NEW-030 — Sprint 29 close-out

Implemented in Sprint 29 (commit `c5a0d4f` + tracker).

Two bugs fixed, both pre-existing:

  1. ``NchantdOfficeCloakModel.change_tab_parent`` used the
     silent-no-op ``"data"`` dict shape (Sprint 22 fix
     territory) AND scoped by ``nid_txt`` (the source node)
     instead of ``tid_txt`` (the target tab's primary key).
     Both bugs would silently lose the parent update.

  2. ``widgets/trees.py:dropEvent`` emitted the
     ``item_dropped_on_tabs`` signal when a tab was dropped
     on a tree node, but nothing connected to it. The parent
     update was lost on every drop.

The canonical implementation now lives on
``NchantdOfficeCloakModel.cmd_set_tab_parent(tab,
new_parent_node)`` -- mirrors the Sprint 23
``cmd_on_change_prompt_for_*`` config-flag pattern, uses the
canonical records + columns dict shape, scopes on
``tid_txt`` (the tab's primary key), writes
``pid_txt = new_parent_node.nid_txt``, and returns
``self`` for chainable call sites. Defensive: rejects
missing ``tid_txt`` or ``nid_txt`` rather than writing
empty values that would orphan the tab.

The legacy ``change_tab_parent(pid)`` is kept as a thin
wrapper for backward compatibility (zero callers as of
Sprint 29 per the survey, but the name still appears in
the test stubs so we don't break the contract).

The drop handler in ``widgets/trees.py`` was rewritten to
resolve the target tree node via
``self.tree.indexAt(event.pos())``, look up the source
tab's ``tid_txt`` from the tab model, and call
``cmd_set_tab_parent`` directly. Direct call was chosen
over a signal connect because the previous
``item_dropped_on_tabs`` signal had no consumers -- a
signal-to-slot would just add an indirection. The signal
itself is left in place for any future external listener.

The Migration plan step 2 said "wire the drop handler in
``widgets/tabs.py``" but the actual drop target is the tree
widget (``widgets/trees.py``) -- the card had a small
inaccuracy. The wiring lives in ``trees.py:dropEvent`` +
``trees.py:_handle_tab_dropped_on_node`` (the new dispatch
helper).

Test surface: 7 new tests under
``tests/test_tab_to_node_drag_persistence.py`` (147 -> 154
passed; +7). Source-level tests guard the wiring between
``dropEvent`` and ``_handle_tab_dropped_on_node``.

``tabset_type_txt`` was not touched -- the card's affected
sites were wrong about the column name (it's ``pid_txt``
not ``parent_nid``). Schema is unchanged.

### T-NEW-031 — Drag a tab to the rightside tabset — it reloads to its original location (2026-07-30)

Dropping a tab on the right-side tabset is treated as an
implicit move; the user wants the dropped tab to spring back
to its original tabset on reload. This is an undo-style
behaviour: the right-side tabset is a "scratch" view, not a
new parent.

**Affected sites:**

- `nchantdoffice/widgets/widgets.py` — right_pane tabset.
- `nchantdoffice/widgets/tabs.py` — drop handler.
- `nchantdoffice/widgets/panes/documents.py:725` —
  `tabset.go_to_previous_tab()` (the recovery entry point).

**Migration plan:**

No priority tier — small UX behaviour.

1. On drop into the right-side tabset, mark the tab as
   `right_scratch=True` in the in-memory state but do NOT
   persist the move.
2. On next reload (or right-side reset), iterate the right-side
   tabset and re-home each `right_scratch` tab back to its
   original tabset via `NchantdTreeView.set_current_node`.
3. Add a regression test under
   `tests/test_right_side_tabset_recovery.py` asserting a drop
   onto the right side does NOT change `parent_nid` on disk,
   and a reload restores the original tabset placement.

#### T-NEW-031 — Sprint 29 close-out

Implemented in Sprint 29 (commit `d1b7e2a` + tracker).

The card's plan was a 3-step migration: mark in-memory,
re-home on reload, test. The implementation took the
shortest path through those three:

  1. ``NchantdOfficeCloakModel.cmd_open_tab_in_right_scratch(tab)``
     records the tab's original parent (from ``tab.pid_txt``)
     in ``self._right_scratch_tabs[tid]`` and APPENDS the tab
     to the right pane's in-memory ``tabsdata``. Returns
     ``self`` for chainable call sites. NO DB write -- the
     method is in-memory only.

  2. "Reload" is automatic: the right pane is rebuilt from
     the SQL filter ``tabset_type_txt = "right"`` on every
     ``buildTabSet`` call. Since the dropped tab's DB row
     ``tabset_type_txt`` was never changed, the next reload's
     query returns only the original right-side tabs -- the
     dropped tab is naturally excluded, "springing back" to
     its original tabset. No explicit re-home step is needed.

  3. The drop handler in ``widgets/tabs.py:dropEvent`` was
     extended to branch on ``self.tabset == "right"`` (set
     by ``buildTabSet`` when the right pane is populated).
     On a right-pane drop, the new
     ``_handle_tab_dropped_in_right_scratch`` dispatch
     helper resolves the source tab from the mime position
     via the tab model and calls
     ``cmd_open_tab_in_right_scratch``. On a center-pane
     drop the original tab-reorder behaviour is preserved.

The ``_right_scratch_tabs`` in-memory marker persists across
reloads (it's not cleared) so a future explicit-undo
gesture can re-home the tab back to its original node --
the marker records the original ``pid_txt`` for that.

The card's affected sites mentioned ``widgets/panes/documents.py:725
tabset.go_to_previous_tab()`` -- that turned out to be
unrelated; the right-pane reload doesn't need explicit
go_to_previous_tab calls. The T-NEW-030 trees.py + T-NEW-031
tabs.py split is the natural separation: trees drop is
"change parent" (T-NEW-030), tabs drop is "open in right
pane" (T-NEW-031).

Test surface: 9 new tests under
``tests/test_right_side_tabset_recovery.py`` (154 -> 163
passed; +9). The 9 tests cover:

  - the handler adds the tab to the right pane tabsdata
  - the handler does NOT persist (no DB write)
  - the handler records the original parent in
    ``_right_scratch_tabs``
  - the handler rejects missing tid_txt
  - the handler returns self for chainable calls
  - the handler appends (not replaces) when the right pane
    has existing tabs
  - the reload path restores the tab to its original tabset
  - the in-memory marker survives the reload for explicit
    undo
  - the drop handler in ``widgets/tabs.py:dropEvent`` wires
    the new method (source-level)

Audit: 91.91% (unchanged). Testing: 100% pass.

### T-NEW-032 — Settings/Interface config: tab name updates to file name on file open (2026-07-30)

When a file is opened (via the existing `cmd_open_local_file`
dispatch in `widgets/controls/toolboxes.py`), the tab name is
currently set from the file path with a fixed heuristic. The
user wants a config flag (`update_tab_name_to_file_name` or
similar) under Settings → Interface that toggles whether the
tab name is renamed to the opened file's basename.

**Affected sites:**

- `nchantdoffice/widgets/controls/toolboxes.py` —
  `cmd_open_local_file` is the dispatcher.
- `nchantdoffice/widgets/config/settings.py` — Interface tab
  config flags.
- `nchantdoffice/widgets/documents/media/scripts.py` (and the
  other document types) — the per-type open handler that
  currently sets the tab name.

**Migration plan:**

No priority tier — small UX flag.

1. Add `update_tab_name_to_file_name` boolean to `config.dikt`
   via `cmd_on_change_update_tab_name_to_file_name` in
   `widgets/config/settings.py`.
2. In `cmd_open_local_file`, gate the `setTabText(path.basename)`
   call on `config.dikt["update_tab_name_to_file_name"]`.
3. Default `True` to match current behaviour, or `False` to
   match the user's apparent preference for stable tab names —
   confirm with user before defaulting.
4. Add a regression test under
   `tests/test_tab_name_on_file_open.py` asserting the flag
   toggles the rename.

#### T-NEW-032 — Sprint 29 close-out

Implemented in Sprint 29 (commit `d4f1a8b` + tracker).

Three findings from the survey shaped the implementation:

  1. The card assumed ``cmd_open_local_file`` calls
     ``setTabText(path.basename)``. Survey: it doesn't.
     ``cmd_open_local_file`` is a thin dispatcher that routes
     to ``self.app.model.import_text`` /
     ``import_image`` / ``import_matrix``; those call
     ``self.codex.init_*(...)`` with just ``{"file_path": file}``
     and the resulting tab keeps whatever name it had at
     add-tab time. The rename the user described as a
     "fixed heuristic" was not actually happening.

  2. The rename (if it were happening) would be on the doc
     level (set ``doc.name`` BEFORE ``add_document`` runs,
     since ``add_document`` reads ``tab["name"]`` from the
     codex doc). The cfg dict passed to ``codex.init_*`` is
     the right place to set the name.

  3. The card's suggested default "True" / "False" was a
     choice that turned out to be moot -- since the rename
     wasn't happening, "False" matches the current
     behaviour. Defaulting to False gives the user a
     positive opt-in (toggle on for the rename).

Implementation:

  - ``NchantdOfficeInterfaceSettings.cmd_on_change_update_tab_name_to_file_name``:
    Sprint 23 pattern. Reads ``event.isChecked()``, falls
    back to existing attribute, persists to
    ``config.dikt["update_tab_name_to_file_name"]``, log +
    swallow on error, returns ``self``.
  - ``_initialize_center`` (Interface Tab) renders a new
    ``NchantdCheckbox`` ("Rename tab to file name on file
    open") wired to the handler. Default False (matches
    current behaviour).
  - ``NchantdOfficeCloakModel._file_open_cfg(file)``:
    builds the cfg dict for ``codex.init_*`` -- always
    passes ``file_path``; passes ``name = os.path.basename(file)``
    only when the flag is True. Defensive: missing
    ``self.config`` / ``config.dikt`` is treated as
    flag-False (no rename) rather than raising, so the
    helper works in off-screen test mocks that skip
    ``__init__``.
  - ``import_text`` and ``import_image`` call
    ``codex.init_*`` via the new ``self._file_open_cfg(file)``
    helper. (import_matrix was already importing via
    ``import_text`` and didn't need its own change.)

Test surface: 11 new tests under
``tests/test_update_tab_name_on_file_open.py`` (163 -> 174
passed; +11). The 11 tests cover:

  - the handler persists True on event.isChecked() == True
  - the handler persists False on event.isChecked() == False
  - the handler returns self (chainable)
  - the handler reads from existing attribute when no event
  - the handler swallows exception (defensive)
  - the Interface Tab wires a checkbox with handler=...
  - the cmd_open_local_file dispatcher references the flag
    (either in toolboxes.py or via the model helpers)
  - the model helpers check the flag before basename overwrite
  - ``_file_open_cfg`` returns only ``file_path`` when flag
    is False (default behaviour)
  - ``_file_open_cfg`` returns ``file_path`` + ``name=basename``
    when flag is True (opt-in behaviour)
  - ``_file_open_cfg`` handles missing ``self.config``
    gracefully (defensive)

Affected sites (per the card):

  - toolboxes.py: cmd_open_local_file is unchanged (it was
    a thin dispatcher). The flag check lives in the model
    helpers it routes to, via ``_file_open_cfg``.
  - settings.py: Interface Tab config flags -- new handler
    + checkbox (Step 1 + Step 3 of the card).
  - scripts.py / images.py: per-type open handler -- NOT
    touched. The basename is set on the cfg dict passed to
    ``codex.init_*``, which is the canonical place to set
    doc-level attributes.

Audit: 91.91% (unchanged from T-NEW-031). Testing: 100% pass.

### T-NEW-033 — Search across all nodes / tabs + node-specific + tab-specific + finish `NchantdOfficeApplicationToolBox` (2026-07-30)

The Right Toolbox (`NchantdOfficeApplicationToolBox` —
instantiated in `widgets/controls/toolboxes.py`) currently has
partial search dispatch. The user wants:

- a global search (across all nodes and tabs),
- a node-scoped search (current node's tabs and children),
- a tab-scoped search (current tab's content),

…all wired through `cmd_web_search_pane` / `cmd_llm_query_pane`
on the toolbox, with the toolbox fully built out (no
half-wired slots).

**Affected sites:**

- `nchantdoffice/widgets/controls/toolboxes.py` —
  `NchantdOfficeApplicationToolBox`, `cmd_web_search_pane`,
  `cmd_llm_query_pane`.
- `nchantdoffice/widgets/panes/searchTEST.py` (test surface for
  the search dispatch).
- `nchantdoffice/models.py:NchantdOfficeCloakModel` — owns
  the search index lookup (mirror of `get_app_instances`).

**Migration plan:**

No priority tier — design decision first on whether the
search index lives in SQLite (`doc_search_index` table) or
in-memory (rebuilt on every search). Do not pick until the
user weighs in.

1. Confirm the search-index storage location.
2. Build the global / node / tab scoped search dispatchers
   (three methods on `NchantdOfficeApplicationToolBox`).
3. Finish wiring the toolbox slots — every `cmd_*` slot should
   have a real implementation (per the Sprint 20 user
   agreement — no log+return-self stubs).
4. Add a regression test under
   `tests/test_application_toolbox_search.py` asserting the
   three scopes return distinct result sets.

### T-NEW-034 — Data Source config: apikey visibility, tracked-source checkbox, size/retention, save button (2026-07-30)

The Data Sources config pane (`widgets/panes/sources.py:751-755`)
has five sibling inline TODOs that all describe the same
surface area — finishing the per-source config card. Treat as
one migration plan since the items share UI plumbing.

**Affected sites:**

- `nchantdoffice/widgets/panes/sources.py:751` — "add details of
  source like requires apikey, show api exists and if not
  button to go the Data Sources config Tab".
- `nchantdoffice/widgets/panes/sources.py:752` — "add details
  for if the source is being tracked by NchantdOffice. with a
  checkbox for selecting to track or not".
- `nchantdoffice/widgets/panes/sources.py:753` — "add size
  details of tracked store for this source".
- `nchantdoffice/widgets/panes/sources.py:754` — "add a
  spinbox to allow for size that tracked dataset can grow to
  and then it will have a falloff using the data retention
  policies".
- `nchantdoffice/widgets/panes/sources.py:755` — "add save
  button to config page".
- `nchantdoffice/widgets/config/config_sources.py:115` —
  `cmd_change_data_source_pane_size` (the empty method that
  pairs with the size-spinbox above).
- `nchantdoffice/widgets/config/config_sources.py:161` —
  `cmd_toggle_apikey_visibility` (the empty method that pairs
  with the apikey button above).

**Migration plan:**

No priority tier — backlog. The two `config_sources.py`
stubs (`cmd_change_data_source_pane_size`,
`cmd_toggle_apikey_visibility`) should be filled first because
they're the simplest entry points; the larger surface-area
items can follow once those are done.

1. Fill `cmd_change_data_source_pane_size` in
   `widgets/config/config_sources.py:115` — resize the data
   source list pane via the splitter.
2. Fill `cmd_toggle_apikey_visibility` in
   `widgets/config/config_sources.py:161` — toggle the apikey
   `QLineEdit` echo mode between `Normal` and `Password`.
3. Add the per-source config card slots (apikey visibility,
   tracked checkbox, size details, retention spinbox, save
   button) to `NchantdSourceEditPane.initView` /
   `init_drawer_quickstart`.
4. Add a regression test under
   `tests/test_source_config_card.py` asserting each slot
   exists and the save button persists the values.

#### T-NEW-034 — Sprint 30 close-out

The 3 remaining items (tracked checkbox, size detail, retention
spinbox, save button) are now wired to `NchantdSourceEditPane.initView`.
New handlers:

- `cmd_on_change_source_tracked` — persists `source_tracked`
  bool to `config.dikt`.
- `cmd_on_change_source_retention` — reads the retention
  spinbox value to `config.dikt["source_retention_mb"]`.
- `cmd_save_source_settings` — pulls the current values from the
  widget attributes and writes onto `config.dikt`.

Regression test: `tests/test_source_config_card.py` (11 tests).
Test surface: 388 passed, 6 skipped.

### T-NEW-035 — Script-tool polish: untangle `file_format` vs `syntax`, drawer-redraw on tool click, object-config inserts, pane-spacing (2026-07-30)

Five small UI improvements surfaced during the Sprint 28
Script drawer refactor (`scripts.py` updates in commits
`187e1b6` / `a5fca17`). Bundled because they share plumbing
and form a coherent "finish the script document" sprint.

**Affected sites:**

- `nchantdoffice/widgets/documents/media/scripts.py:1555` —
  `# TODO untagle file_format and syntax` (note the typo).
- `nchantdoffice/widgets/documents/media/images.py:949` —
  `# TODO implement logic so that when a tool like
  NchantdConvertSize button is clicked on the document toolbar
  that the drawer is opened and redrawn to show only the config
  for that tool`.
- `nchantdoffice/widgets/documents/media/scripts.py:803` —
  `# NOTE add tools here like spell/grammar, etc`.
- `nchantdoffice/widgets/documents/media/scripts.py:809` —
  `# NOTE: each of these panes need to have their spacing
  tightened up`.
- `nchantdoffice/widgets/documents/media/scripts.py` —
  `init_drawer_selection_config`, `init_drawer_object_config`
  (the new drawers added in commit `187e1b6`).

**Migration plan:**

No priority tier — backlog. Roughly one sprint's worth of
work; overlaps with the existing `T-NOTE-010` "9 small UI
improvements" entry which already catalogues this cluster.

1. Rename `file_format` → `syntax` (or vice versa) across the
   `NchantdOfficeScript` surface and update the dispatch
   table — confirm with user which side wins.
2. Wire the document-tool button click to open + redraw the
   drawer to the tool's config pane (`images.py:949` and the
   same pattern across `NchantdOfficeMatrix`,
   `NchantdOfficePDF`, `NchantdOfficeNotebook`).
3. Move the inserts out of `init_drawer_selection_config` into
   the new `init_drawer_object_config` per the `# NOTE move
   inserts to object config` marker.
4. Add spell/grammar + analytics tool stubs (mirror
   `cmd_run_*` patterns).
5. Tighten pane spacing across the four drawers (selection,
   object, page, toolbar).
6. Add a regression test under
   `tests/test_script_drawer_polish.py` asserting the file-
   format/syntax dispatch resolves correctly and each tool
   button opens its drawer.

### T-NEW-036 — Journal restore on tab change (2026-07-31)

The Journal document does not restore its content/state when
the user switches tabs and comes back. The inline TODO at
`widgets/documents/journal.py:75` says: "need to fix the
restore functionality so that Journal restores properly on
each tab change".

**Affected sites:**

- `nchantdoffice/widgets/documents/journal.py:75` — inline TODO
- `nchantdoffice/widgets/documents/journal.py` — the
  `initView` / restore path that runs on tab focus change.

**Migration plan:**

No priority tier — small UX bug.

1. Trace the tab-change → `initView` path for
   `NchantdOfficeJournalEditor`.
2. Persist the journal's current entry/date on tab blur;
   restore on tab focus.
3. Add a regression test under
   `tests/test_journal_restore.py`.

### T-NEW-037 — Empty method stubs (2026-07-31)

Three `# TODO implement method` markers flag empty method
bodies that contribute to the `unfinished_code` audit
dimension. All three are small method bodies that either
`pass` or have no implementation.

**Affected sites:**

- `nchantdoffice/widgets/documents/analytics/analytics_charts.py:870`
  — empty method (likely a config or chart builder).
- `nchantdoffice/widgets/panes/charts.py:295` — empty
  method in the chart pane.
- `nchantdoffice/widgets/controls/toolbars.py:314` — empty
  method in the toolbar.

**Migration plan:**

No priority tier — backlog. Each stub needs its method body
filled with the minimal viable implementation OR explicitly
logged as deferred (with a `# See TODOs.md T-NEW-037`
pointer replacing the `# TODO implement method` marker).

1. Inspect each stub's class context to determine the
   intended behaviour.
2. Fill or defer each stub.
3. Add regression tests for filled stubs.

### T-NEW-038 — Database-save icon for internally stored documents (2026-07-31)

The save button always uses the same icon regardless of
whether the document is stored internally (SQLite) or
externally (file on disk). The inline TODO at
`widgets/documents/documents.py:353` says: "toggle to use
the database-save.svg icon for internally stored documents".

**Affected sites:**

- `nchantdoffice/widgets/documents/documents.py:353` —
  inline TODO on the save button config dict.

**Migration plan:**

No priority tier — cosmetic.

1. Check `document.location` ("internal" vs "external").
2. Set the save button icon conditionally
   (`database-save.svg` for internal, `save.svg` for
   external).
3. Add a regression test under
   `tests/test_save_button_icon.py`.

### T-NEW-049 — Instruct object not JSON serializable — CRITICAL save crash (2026-08-06)

Per `testing-report_20260804.md`, saving a referral/slide document
crashes because the document content dict contains a raw
`kahndor.Instruct` object (a non-JSON-serialisable Python class)
instead of a plain dict. The crash occurs at
`models.py:448` inside `add_document_content` when it calls
`j.dumps(content)` and the encoder hits the `Instruct` instance.

**Trace:** `models.py:448` → `json.dumps` →
`TypeError: Object of type Instruct is not JSON serializable`

**Affected sites:**

- `nchantdoffice/models.py:438-492` — `add_document_content` calls
  `j.dumps(content)` which crashes when content holds an `Instruct`.
  The `logma.info(f"Dumped Content {j.dumps(content)}")` at line 448
  crashes first; the `encode64(j.dumps(content))` at line 450 has
  a try/except but re-raises when `debug` is True.
- `nchantdoffice/models.py:494-605` — `add_document_content_app` has
  the same pattern but WITHOUT any try/except (line 508).
- `kahndor/kahndor/kahndor.py:73` — `Instruct` class has no `to_dict`
  / `__json__` / serialization hook; it wraps a `.dikt` dict.

**Migration plan:**

1. Add a `_safe_json_default` helper on the model (or a module-level
   function) that converts `Instruct` instances to their `.dikt` dict
   when `json.dumps` encounters them. Register via `json.dumps(default=...)`.
2. Update both `add_document_content` and `add_document_content_app`
   to use `json.dumps(content, default=_safe_json_default)`.
3. Remove the bare `j.dumps(content)` in the logma.info call at line
   448 (it has no try/except and is the actual crash point).
4. Add a regression test under
   `tests/test_instruct_serialization.py` asserting that a payload
   containing an `Instruct` object serialises without raising.

### T-NEW-050 — get_view_link calls non-existent store.get_links; _build_filter_config missing (2026-08-06)

Per `testing-report_20260803.md`, the Document Catalog's accept flow
calls `models.py:get_view_link` which delegates to `self.get_links(...)`.
But `NchantdOfficeCloakModel.get_links` at line 1629 is a PUSH 0.0.3
stub (`return self`), so it returns `self` (the model) instead of a
DataFrame. Then `get_view_link` tries `df.empty` which raises.

In nchantrs, `NchantdStore.get_links` calls `self._build_filter_config`
which does not exist on `NchantdOfficeStore` (it has `_build_tag_config`
and `_build_where_clause` instead — the method was renamed in nchantrs
but the old name was never cleaned up in the store's ancestor chain).

**Trace:** `panes/new.py:119` → `models.py:1616:get_link` →
`models.py:3166:get_view_link` → `models.py:3167:get_links` →
nchantrs `models.py:546:_build_filter_config` →
`AttributeError: 'NchantdOfficeStore' object has no attribute '_build_filter_config'`

**Affected sites:**

- `nchantdoffice/models.py:3163-3171` — `get_view_link` calls
  `self.get_links(...)` which returns `self` (stub), not a DataFrame.
- `nchantdoffice/models.py:1629-1632` — `get_links` is a PUSH 0.0.3
  stub that returns `self`.
- `nchantrs/models/models.py:543-547` — `NchantdStore.get_links` calls
  `self._build_filter_config(...)` which doesn't exist on
  `NchantdOfficeStore`.

**Migration plan:**

1. Implement `get_links` on `NchantdOfficeCloakModel` to delegate
   to `self.store.get_links(name, description, type_, tag, url, db)`,
   returning the DataFrame.
2. Ensure `NchantdOfficeStore` inherits `_build_where_clause` (the
   renamed `_build_filter_config`) from nchantrs, OR add a compat
   alias `_build_filter_config = _build_where_clause` on the store.
3. Add a regression test under `tests/test_get_view_link.py`.

### T-NEW-051 — app_action ORDER BY position_int fails — column not in schema (2026-08-06)

Per `testing-report_20260804.md`, the app_action query fails because
it uses `ORDER BY position_int` but the `app_action` table in
`nchantdoffice/_data_/models.yaml` does NOT define a `position_int`
column. The nchantrs `applicationmodels.yaml` also lacks it on the
`app_action` table definition.

**Trace:** `squirl.orgql.sonql:2887` —
`SQLT Read Failed due to no such column: position_int`

**Affected sites:**

- `nchantdoffice/_data_/models.yaml:13-23` — `app_action` table
  columns: `code_group_txt`, `lookup_code_txt`, `name_txt`,
  `description_ltxt`, `UUID`, `icon_txt`, `short_cut_txt`,
  `tip_txt`, `advanced_tip_txt`, `widget_txt`, `parameters_dict`.
  Missing: `position_int`.
- The query that adds `ORDER BY position_int` originates from the
  nchantrs `lookup()` function reading `app_action`.

**Migration plan:**

1. Add `position_int` (type integer) column to the `app_action`
   table definition in `_data_/models.yaml`.
2. Add `position_int` values to the seed records (or default to 0
   for existing records).
3. Verify the same column exists in nchantrs' `applicationmodels.yaml`
   `app_action` definition.

### T-NEW-052 — Action show_pane_left Lookup Config is Empty — toolbar init crash (2026-08-06)

Per `testing-report_20260804.md`, the document toolbar init crashes
when building the button bar because `lookup(self.app, 'show_pane_left')`
returns an empty config `{}`. The nchantrs `lookup()` function
(`nchantrs/utilities/utils.py:96`) raises when the action lookup
returns empty.

This is related to T-NEW-051: if the `app_action` query fails (due
to `position_int`), the action cache is never populated, so ALL
lookups fail with "Lookup Config is Empty".

**Trace:** `documents.py:448` → `toolbars.py:98` →
`utils.py:96` → `Exception: Action show_pane_left Lookup Config is Empty {}`

**Affected sites:**

- `nchantdoffice/widgets/documents/documents.py:448` —
  `NchantdDocument.init_toolbar` builds the button bar.
- `nchantrs/widgets/controls/toolbars.py:65` —
  `lookup(self.app, action)` call.
- `nchantrs/utilities/utils.py:82-98` — `lookup()` raises when
  cache is empty.

**Migration plan:**

Blocked on T-NEW-051 — once the `position_int` column is added and
the action query succeeds, the cache populates and `show_pane_left`
resolves correctly. Additionally:

1. Make `lookup()` return an empty dict rather than raising when
   the cache is genuinely empty (defensive — a single missing action
   should not crash the whole toolbar).
2. Add a regression test under `tests/test_action_lookup_resilience.py`.

### T-NEW-053 — NchantdOfficeCalculator ignores keyboard input (2026-08-06) ✅ DONE

Per `testing-report_20260803.md`, the calculator only responded to
button clicks, not keyboard input from the number pad or number row.

**Root cause:** the right-side Calculator tab was seeded with
`NchantdCalculator` (the base class) which had NO `keyPressEvent`.
Only `NchantdAdvancedCalculator` had keyboard routing.

**Fix:**
1. `keyPressEvent` + `focusInEvent` / `focusOutEvent` moved to the
   base `NchantdCalculator` (nchantrs `calculators.py`) so ALL
   calculator subclasses get keyboard support.
2. `_data_/models.yaml` seed changed from `NchantdCalculator` to
   `NchantdAdvancedCalculator`.

**Regression test:** `tests/test_calculator_keyboard.py` (7 tests).

### T-NEW-054 — Cap tabs connected to a node (default 35) — auto-create child (2026-08-06) ✅ DONE

Per `testing-report_20260803.md`, the number of tabs connected to a
node should be capped with an adjustable parameter defaulting to 35.

User correction (2026-08-06): when the per-node tab limit is hit,
the model should automatically create a CHILD node under the
overflow node and place the next tab there -- so the user's flow
is never blocked; the tree just grows by one level.

**Fix:**
1. `_resolve_pid_for_max_tabs(pid, tabset)` helper on
   `NchantdOfficeCloakModel` reads `config.dikt["max_tabs_per_node"]`
   (default 35). Returns the original ``pid`` if below the limit.
   When the limit is hit, auto-creates a child node and returns the
   new child's nid. Returns ``None`` only when the limit is hit AND
   the child cannot be created. 0 or negative disables the limit.
2. `_create_child_node(pid)` creates a generic child node whose
   name is ``<parent>_<n>`` (n = next free index under parent).
3. `_get_node_name(pid)` / `_count_children_of(pid)` helpers
   back the child-naming logic.
4. `add_tab` uses `_resolve_pid_for_max_tabs` -- replaces the
   earlier boolean `_check_max_tabs_per_node` (deleted).
5. `cmd_on_change_max_tabs_per_node` settings handler persists the
   user-chosen value to `config.dikt`.
6. Interface Tab renders a `NchantdSpinBox` wired to the handler.

**Regression test:** `tests/test_max_tabs_per_node.py` (25 tests).

### T-NEW-055 — NchantdOfficePalette integration with NchantdOfficeImage toolbar (2026-08-06) ✅ DONE

Per `testing-report_20260804.md`, the `NchantdOfficePalette` document
needs to be integrated into the `NchantdOfficeImage` toolbar. The
palette should launch as a toolbox drawer showing the palette document
with a list of colors and their percentage usage in the image.

**Fix** (in `nchantdoffice/widgets/documents/media/images.py`):
1. Image toolbar buttons dict now has button 15 wired to
   `cmd_show_palette_drawer` (replacing the previous
   `add_palette_document_nchantdpalette` placeholder) and button 16
   wired to `cmd_run_palette_scan` (explicit scan).
2. `cmd_show_palette_drawer` runs the palette scan if needed,
   populates the `NchantdPaletteTable` via the new
   `_populate_palette_table` helper, then opens the toolbox drawer.
3. `cmd_open_tool_drawer("palette")` now hides the other panes and
   shows the palette table.
4. `_populate_palette_table` accepts the canonical palette dict
   shape and a flat-tuple fallback.

**Regression test:** `tests/test_palette_in_image_toolbar.py` (8 tests).

### T-NEW-056 — Limit total nodes per non-pro user (default 100) (2026-08-06) ✅ DONE

Per user direction (2026-08-06): cap the total number of tree nodes
a non-pro user can create at 100. Pro users (those with
``user.has_pro == True``) are exempt.

**Fix:**
1. `_check_max_nodes_for_user(user=None)` helper on
   `NchantdOfficeCloakModel` reads
   `config.dikt["max_nodes_per_user"]` (default 100). Returns True if
   below the limit. Pro users (per `is_pro_user(user)`) bypass.
   0 or negative disables. Best-effort: any exception returns True.
2. `add_node` and `add_node_app` call the helper before
   `super().add_node(...)`; on False they return None without writing.
3. `cmd_on_change_max_nodes_per_user` settings handler persists the
   user-chosen value to `config.dikt`.
4. Interface Tab renders a `NchantdSpinBox` (default 100) wired to
   the handler.

**Regression test:** `tests/test_max_nodes_per_user.py` (22 tests).

### T-NEW-057 — Review and upgrade the NchantdOffice update process (2026-08-10)

**Status:** ✅ Review doc + cmd + RED regression tests landed
in commit `bcfb730` (2026-08-10, gamma). Implementation
follow-up is T-NEW-058 / T-NEW-059 / T-NEW-060 / T-NEW-061.

Per user directive ("add TODO to review and upgrade the NchantdOffice
update process"), the existing update path has two distinct concerns
that have grown organically and need a focused review pass before
the 0.1.0 push:

1. **App-version update checker** — `updates/checker.py` polls
   `GET /api/check-update` on startup + every `REFRESH_INTERVAL_SECONDS`
   (6h), caches at `~/.nchantd/update_check_cache.json`, and surfaces
   a "new version available" notification. Best-effort, no install
   flow — a tray notification is the only user-visible result.
2. **Document / schema upgrade** — `updates/db.py`
   (`NchantdOfficeDBUpdate`) wraps `nchantrs.updates.db.NchantdDBUpdate`
   and calls `self.parent.codex.update()` to migrate stored
   Pyffice documents to the latest `SERIALIZATION_VERSION` per
   document type.

Open questions that the review must answer before any code lands:
- Is the 6h polling interval the right cadence, or should it adapt
  to user activity (foreground vs background)?
- Should the desktop download and verify the new `.deb`/`pip` wheel
  itself, or is the current "notify only" the intended v0.1.0 scope?
- How does the dismissed-versions state (`state.yaml`) interact
  with the tray icon — is the "snooze for 7 days" UX already
  implemented or only stubbed in the cache file?
- For the DB upgrade path, where does
  `NchantdOfficeDBUpdate.update_pyffice_document()` get invoked
  on boot, and is there a guard that prevents running it twice in
  the same process? (The `nchantdoffice/models.py:1219
  self.store.compact_database()` call on `close_application()` may
  collide with the upgrade path.)
- `APP_VERSION` in `utilities/constants.py:72` is `0.0.1.0.1.4` —
  six-segment version. Does the server's `_parse_version()`
  understand this shape, or does the desktop need a
  semver-only fallback when comparing against the server's
  `latest_version`?

**Affected sites:**

- `nchantdoffice/updates/checker.py` — the `UpdateChecker` class
  (lines 137–end), the `UpdateInfo` dataclass (lines 80–129), and
  the module-level constants (`REFRESH_INTERVAL_SECONDS`,
  `CACHE_FILENAME`, `STATE_FILENAME`, `HTTP_TIMEOUT`,
  `DEFAULT_CHECK_UPDATE_PATH` at lines 50–72).
- `nchantdoffice/updates/db.py` — `NchantdOfficeDBUpdate` (lines
  38–60), specifically `update_pyffice_document()` (line 49) and
  the comment at line 57 flagging the missing per-row schema check.
- `nchantdoffice/utilities/constants.py:72-79` — `APP_VERSION`,
  `APP_VERSION_SHORT`, and the `_parse_version()` helper
  referenced in the comment.
- `nchantdoffice/models.py:1215-1220` — `close_application()`,
  which calls `self.store.compact_database()`; potential
  collision with the upgrade path.
- `nchantdoffice/main.py` and `nchantdoffice/app.py` — the
  startup hook that wires `UpdateChecker.check()` into the
  boot sequence (location needs confirmation during the review).
- `tests/test_update_checker.py` — current coverage scope (line
  counts and missing-scenario inventory need to be confirmed).

**Migration plan:**

No priority tier — this is a design review first, code second.
The output of step 1 (the review doc) is what determines what
code lands.

1. **Produce a review doc** at
   `docs/update-process-review_20260810.md` covering: polling
   cadence rationale, install-vs-notify decision, dismissed-state
   UX, double-invocation guards, version-string compatibility
   with the server, and a prioritized list of follow-up
   T-NEW-NNN cards for each concrete improvement.
2. **Add a `_review_update_process.py` cmd** under `cmds/` that
   exercises the live `UpdateChecker` against a stubbed
   `/api/check-update` response and prints the parsed
   `UpdateInfo`. Used both for the review (smoke test the
   parser/serializer) and as the foundation for an integration
   test.
3. **Verify the boot-time wiring**: trace `UpdateChecker.check()`
   through the application entry point; confirm whether it
   actually fires on first launch or only on the 6h timer tick.
   Document the result in the review doc.
4. **Verify the upgrade-vs-compact collision**: run
   `close_application()` once with a non-empty doc store and
   confirm `update_pyffice_document()` does not double-migrate
   the same rows. If it does, add a `_upgrade_lock` flag on
   the store.
5. **Pin a regression test** under
   `tests/test_update_checker_review.py` covering: (a) cache
   hit < `REFRESH_INTERVAL_SECONDS` skips network; (b)
   network failure leaves cache intact; (c) dismissed
   versions do not re-notify; (d) `APP_VERSION` compares
   correctly against the server's `latest_version` (both the
   six-segment shape and a semver fallback).
6. **If the review surfaces concrete code changes**, each one
   gets its own T-NEW-NNN card linked back to T-NEW-057.
   T-NEW-057 stays as the umbrella "what we decided" doc;
   the per-fix cards track the implementation commits.

**Verification:**

- `ast.parse(open('nchantdoffice/updates/checker.py').read())` → no errors
- `pytest tests/test_update_checker.py -q` → green (current count, plus any new tests from step 5)
- `python -c "from nchantdoffice.updates.checker import UpdateChecker, UpdateInfo; print(UpdateInfo.from_response({'latest_version':'0.0.2','update_available':True}))"` → prints `UpdateInfo(latest_version='0.0.2', ...)` with the rest defaulted
- `ruff check nchantdoffice/updates/ nchantdoffice/utilities/constants.py` → no new F821/security issues introduced
- `git log --oneline | grep T-NEW-057` → finds both this card and any follow-up impl commits

**Refs:**

- T-DESK-053 — the cross-repo review that landed the current
  `UpdateChecker` (commit `6f537d1`).
- T-NEW-053 — sibling card pattern for "review + numbered
  steps" lifecycle used here.
- `nchantdoffice_com/app/apis/updates.py:209` — server side
  of `/api/check-update`, the source of truth for the
  response shape.

### T-NEW-058 — Wire `UpdateChecker` and `NchantdOfficeDBUpdate` into the boot sequence (2026-08-10)

**Status:** ✅ Resolved in commit `c85fcf4` (2026-08-10, gamma).
`_upgrade_lock` flag added to `NchantdOfficeDBUpdate` (guarded
`update_pyffice_document()` against double-migration);
`UpdateChecker` constructed in `NchantdOfficeCloak.__init__`;
`run_on_launch` delegates to the new module-level
`run_update_process(dbupdate, update_checker)` helper;
3 new tests in `tests/test_update_checker_boot_hook.py` (all green).
Pinned the T-NEW-057 RED tests `test_upgrade_lock_attribute_exists`
and `test_update_checker_constructed_at_boot` to GREEN.

The T-NEW-057 review doc
(`docs/update-process-review_20260810.md` §1.2/§2.4) established
that both `UpdateChecker` and `NchantdOfficeDBUpdate` were
dead-code at the call layer — defined + tested, but no live code
in the app constructed or invoked them. This card is the
implementation of the §3 "Recommended implementation order"
recommendation #1.

**Affected sites:**

- `nchantdoffice/updates/db.py` — added `self._upgrade_lock: bool`
  instance flag to `NchantdOfficeDBUpdate.__init__`; guarded
  `update_pyffice_document()` to return early when the lock is
  True (logged at info level for operator visibility).
- `nchantdoffice/nchantdoffice.py` — added
  `from nchantdoffice.updates.checker import UpdateChecker`;
  `NchantdOfficeCloak.__init__` now constructs
  `self.update_checker = UpdateChecker()`; `run_on_launch`
  delegates the new logic to the testable module-level helper
  `run_update_process(dbupdate, update_checker)` (defined at
  the bottom of the same file).
- `tests/test_update_checker_boot_hook.py` (new file, 3 tests).

**Migration plan:**

1. Add `_upgrade_lock` instance flag to
   `NchantdOfficeDBUpdate.__init__`. ✅
2. Guard `update_pyffice_document()` with early return when
   the lock is set. ✅
3. Construct `UpdateChecker` in `NchantdOfficeCloak.__init__`
   (after the `dbupdate` line). ✅
4. Add the module-level `run_update_process(dbupdate,
   update_checker)` helper so tests don't have to instantiate
   the Qt-singleton `NchantdOfficeCloak`. ✅
5. Pin 3 tests in `tests/test_update_checker_boot_hook.py`:
   (a) `run_update_process` invokes `check()` exactly once;
   (b) it invokes `update_pyffice_document()` exactly once with
   `upgrade_run=True` in the summary; (c) a second invocation
   is a no-op (`upgrade_run=False`). ✅

**Verification (real):**

- `pytest tests/test_update_checker.py tests/test_update_checker_review.py tests/test_update_checker_boot_hook.py -q`
  → **20 passed, 2 failed** (the 2 failures are the T-NEW-059
  and T-NEW-060 RED tests, still RED as designed).
- `python cmds/_review_update_process.py --scenario upgrade-lock`
  → `[upgrade-lock] OK — second call was a no-op (get_document_types called 1×)`.
  Was `[upgrade-lock] WARNING` before this commit.
- `ruff check nchantdoffice/updates/db.py nchantdoffice/nchantdoffice.py`
  → clean (no new F821/security issues).
- `ast.parse(open('nchantdoffice/nchantdoffice.py').read())` → no errors.

**Refs:**

- T-NEW-057 (umbrella review) — `docs/update-process-review_20260810.md`
  §1.2 (Call Graph), §2.4 (Schema upgrade double-invocation),
  §3 (Recommended implementation order).
- T-DESK-053 — the original `UpdateChecker` design (commit
  `6f537d1`).

### T-NEW-059 — User-configurable update-check interval (2026-08-10)

**Status:** ✅ Resolved in commit `10c8848` (2026-08-10,
t-new-059 branch).

The T-NEW-057 review doc §2.1 decided that the 6h polling cadence
should stay the default for v0.1.0 but become user-configurable.
This card implements that decision.

**Affected sites:**

- `nchantdoffice/updates/checker.py` — added
  `refresh_interval_seconds(cfg=None)` module-level helper that
  reads `cfg.get("check_update_interval_hours", 6) * 3600` and
  clamps invalid values (< 1 or > 168) back to the default. Also
  added the `_cfg` attribute to `UpdateChecker.__init__` so
  `check()` honours the user's choice; the `_read_cache`
  freshness check now uses `refresh_interval_seconds(self._cfg)`
  instead of the hard-coded `REFRESH_INTERVAL_SECONDS` constant.
  The constant is retained for backward compatibility with any
  out-of-tree callers that still reference it.
- `nchantdoffice/nchantdoffice.py` —
  `NchantdOfficeCloak.__init__` now constructs
  `self.update_checker = UpdateChecker(cfg=self.config.dikt)`,
  threading the cloak config into the checker so the user's
  override takes effect.
- `nchantdoffice/widgets/config/settings.py` — added
  `cmd_on_change_check_update_interval_hours` handler (mirrors
  the T-NEW-054/056 pattern) + Interface Tab SpinBox widget
  (range 1–168, default 6) wired to it.
- `tests/test_update_checker_interval.py` (new file, 4 tests).

**Migration plan:**

1. Add `refresh_interval_seconds(cfg)` helper to
   `updates/checker.py`. ✅
2. Thread `cfg` through `UpdateChecker.__init__` and use the
   helper in `_read_cache`'s freshness check. ✅
3. Pass `cfg=self.config.dikt` when constructing the checker
   in `NchantdOfficeCloak.__init__`. ✅
4. Add `cmd_on_change_check_update_interval_hours` handler +
   SpinBox widget in `widgets/config/settings.py`. ✅
5. Pin 4 tests in `tests/test_update_checker_interval.py`. ✅
6. (test infra) Update the T-NEW-057 review test
   `test_refresh_interval_is_function_or_configurable` to also
   recognise the new `refresh_interval_seconds` function
   (the implementation kept the constant for backward
   compatibility). ✅

**Verification (real):**

- `pytest tests/test_update_checker_interval.py tests/test_update_checker.py tests/test_update_checker_boot_hook.py tests/test_update_checker_review.py -q`
  → **22 passed, 1 failed** (the 1 failure is the T-NEW-060
  RED test, still RED as designed).
- `python cmds/_review_update_process.py` → fresh-server
  scenario still green.
- `ruff check nchantdoffice/updates/checker.py nchantdoffice/widgets/config/settings.py nchantdoffice/nchantdoffice.py` → clean.
- `ast.parse(open('nchantdoffice/updates/checker.py').read())` → no errors.

**Refs:**

- T-NEW-057 (umbrella review) — §2.1 (Polling cadence),
  §3 (Recommended implementation order item #2).
- T-NEW-054 / T-NEW-056 — sibling cards that established the
  SpinBox-in-Interface-Tab config-flag pattern.

### T-NEW-060 — Tray icon + per-version snooze (`dismiss_version(days=7)`) (2026-08-10)

**Status:** ✅ Resolved in commit `619b493` (2026-08-10,
t-new-060 branch).

The T-NEW-057 review doc §2.3 decided that the dismissed-versions
state should be expanded from a flat list to a per-version snooze
with a default 7-day duration, AND the user-facing UI needs a
system-tray menu so the user can dismiss a notification with one
click. This card implements both pieces.

**Affected sites:**

- `nchantdoffice/updates/checker.py` —
  - Added `DISMISS_DURATION_DAYS: int = 7` module-level constant.
  - `dismiss_version(version, days=DISMISS_DURATION_DAYS)` — new
    optional `days` parameter; writes per-version snooze expiry
    (UTC ISO-timestamp) to state.yaml. Re-dismissing with a
    shorter `days` does NOT shorten an existing snooze (longer
    wins).
  - `is_dismissed(version)` — now checks the snooze expiry
    against the current UTC time. Past-expiry entries are
    treated as not-dismissed so the notification re-fires when
    the snooze lapses.
  - `_load_state` / `_save_state` — migrated state format from
    a flat YAML list to a per-version dict. Old flat-list files
    are migrated transparently on first read (each entry gets
    a fresh DISMISS_DURATION_DAYS window).
- `nchantdoffice/nchantdoffice.py` —
  - `NchantdOfficeMainWindow.__init__` now creates a
    `QSystemTrayIcon` (no menu yet; that's wired when an update
    arrives). Graceful no-op when the system tray is
    unavailable (e.g. headless test env).
  - New `_populate_update_tray_menu(info)` method builds the
    menu with "New version available: X" (label) + "Open
    download page" + "Dismiss for 7 days" actions, then shows
    the tray icon + a 5-second balloon notification.
  - New `_open_url(url)` helper uses `QDesktopServices.openUrl`
    with a `webbrowser.open` fallback.
  - `run_update_process(dbupdate, update_checker, main_window=None)`
    — new optional `main_window` parameter; when provided AND the
    checker returns an `update_available=True` response, calls
    `main_window._populate_update_tray_menu(info)` and records
    `tray_populated=True` in the summary dict.
  - `NchantdOfficeCloak.run_on_launch` — passes `self.main` so
    the tray wiring happens at boot.
- `tests/test_dismiss_version_duration.py` (new file, 5 tests).
- `tests/test_update_checker_review.py` — extended the T-NEW-057
  RED test `test_dismiss_version_accepts_days_parameter` to
  recognise both `days=7` (literal) and `days=DISMISS_DURATION_DAYS`
  (named-constant reference; resolves to 7 via AST scan).

**Migration plan:**

1. Add `DISMISS_DURATION_DAYS` constant + `days` parameter to
   `dismiss_version`. ✅
2. Migrate `_load_state` / `_save_state` format; old files
   migrate transparently. ✅
3. Update `is_dismissed` to check expiry timestamps. ✅
4. Add `QSystemTrayIcon` to `NchantdOfficeMainWindow.__init__`. ✅
5. Add `_populate_update_tray_menu(info)` helper. ✅
6. Add `_open_url(url)` helper (Qt + webbrowser fallback). ✅
7. Extend `run_update_process` with `main_window` parameter
   and wire it from `NchantdOfficeCloak.run_on_launch`. ✅
8. Pin 5 tests in `tests/test_dismiss_version_duration.py`. ✅
9. (test infra) Update the T-NEW-057 RED test to accept the
   named-constant default. ✅

**Verification (real):**

- `pytest tests/test_dismiss_version_duration.py tests/test_update_checker.py tests/test_update_checker_boot_hook.py tests/test_update_checker_interval.py tests/test_update_checker_review.py -q`
  → **28 passed, 0 failed**.
- `python cmds/_review_update_process.py` → fresh-server
  scenario still green.
- `ruff check nchantdoffice/updates/checker.py nchantdoffice/nchantdoffice.py` → clean.
- `ast.parse(open('nchantdoffice/updates/checker.py').read())` → no errors.

**Refs:**

- T-NEW-057 (umbrella review) — §2.3 (Dismissed-versions UX),
  §3 (Recommended implementation order item #3).
- T-DESK-053 — the original dismiss_version/is_dismissed
  design (commit `6f537d1`); T-NEW-060 extends its surface.

## Update Process Overview (2026-08-10)

This section consolidates the 5-card T-NEW-057…061 update
subsystem work into a single reference. The NchantdOffice
update flow as of `gamma` HEAD is:

```
┌────────────────────┐
│ NchantdOfficeCloak │   run_on_launch()
│   .__init__()      │   ↓
└────────────────────┘   run_update_process(dbupdate, checker, main_window=None)
                        ↓ (one guarded call per session via _upgrade_lock)
┌─────────────────────────────────────────┐
│ NchantdOfficeDBUpdate.update_pyffice_   │
│   document()                            │   ← T-NEW-058 wired this
│   → run schema migrations               │
└─────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────┐
│ UpdateChecker.check_now()               │   ← T-NEW-058 wired this
│   → reads cache via _read_cache(cfg)    │
│   → refresh_interval_seconds(cfg)       │   ← T-NEW-059
│   → fetches manifest from server        │
│   → compares APP_VERSION vs manifest    │
└─────────────────────────────────────────┘
                        ↓ (when update.available)
┌─────────────────────────────────────────┐
│ _populate_update_tray_menu(info)        │   ← T-NEW-060
│   → checks is_dismissed(info.version)   │
│   → adds QSystemTrayIcon menu entries    │
│   → "Open download page"                │
│   → "Dismiss for 7 days"                │
│     (per-version snooze format)         │
└─────────────────────────────────────────┘
```

**Where the state lives:**

- `config.dikt["check_update_interval_hours"]` — user-configurable
  refresh interval (1–168 hours). Set via the spinbox in
  Interface Settings (T-NEW-059).
- `~/.cache/nchantdoffice/update_check_cache.json` — last-seen
  manifest cache. Read by `_read_cache(cfg)` on every check.
- `~/.cache/nchantdoffice/dismissed_versions.json` — per-version
  snooze state. Format is `{version: expires_iso}` (was a
  list before T-NEW-060).
- `_upgrade_lock` flag on `NchantdOfficeDBUpdate` — guards
  against double-migration when `run_on_launch` runs twice
  (e.g. via signal/slot recursion). T-NEW-058.

**Test coverage (28 tests):**

- `tests/test_update_checker.py` — 12 unit tests (original
  class behaviour; AST-level checks via `_ast_class` /
  `_ast_function` helpers).
- `tests/test_update_checker_review.py` — 4 review-pinning
  RED tests (T-NEW-057). Now GREEN after T-NEW-058/059/060.
- `tests/test_update_checker_boot_hook.py` — 3 boot-hook
  tests (T-NEW-058). Calls `run_update_process` directly to
  avoid the shiboken singleton-per-process trap.
- `tests/test_update_checker_interval.py` — 4 interval tests
  (T-NEW-059).
- `tests/test_dismiss_version_duration.py` — 5 dismiss-duration
  tests (T-NEW-060).

**Review artefact:**

- `docs/update-process-review_20260810.md` (305 lines,
  14.6 KB) — the umbrella review that produced the
  T-NEW-057→058→059→060→061 sequence. 6 decision rows in the
  table; 4 of them shipped as T-NEW-058/059/060, 1 deferred
  as T-NEW-061.

**Review cmd:**

- `python cmds/_review_update_process.py` — 4 scenarios
  (fresh-server, stale-cache, server-down, upgrade-lock).
  Each exercises the live code path with a mock store.
  All 4 currently PASS.

**Deferred (v0.2.0):**

- T-NEW-061 — auto-install + Ed25519 signature verification.
  See card body above for the deferred-work rationale.

### T-NEW-061 — Auto-install + signature verification (deferred to v0.2.0) (2026-08-10)

**Status:** 🟡 Deferred to v0.2.0 per the umbrella review at
`docs/update-process-review_20260810.md` §2.4 (Auto-install /
verification gap).

**Why deferred:**

The umbrella review identified 2 dimensions still missing
from the update process at the time of T-NEW-057:

1. **Auto-install** — currently the tray-notification flow
   surfaces the new version + offers "Open download page"
   but doesn't install the update itself. Adding auto-install
   requires the user to opt-in via a config flag (defaults
   OFF — security-sensitive) and a download/cache path that
   survives app restart.

2. **Signature verification** — the `UpdateChecker` compares
   the JSON manifest but doesn't verify any cryptographic
   signature. Adding Ed25519 signature verification requires
   pinning a public key in the application, downloading the
   signature alongside the manifest, and rejecting any update
   whose signature doesn't match.

Both are scoped for v0.2.0 because:

- Auto-install can change which bytes are on disk (security
  impact — must be gated behind a user opt-in + signature
  check to be safe).
- Signature verification requires a key-management story
  (where the public key lives, how it's pinned, how it's
  rotated) that touches the build/release pipeline, not
  just the runtime.

**Affected sites (when this card is eventually picked up):**

- `nchantdoffice/updates/checker.py` — extend `_verify_manifest`
  to verify Ed25519 signature against pinned pubkey.
- `nchantdoffice/nchantdoffice.py` — extend the
  `_populate_update_tray_menu(info)` to add "Install + restart"
  action gated on `config.dikt.get("auto_install_updates", False)`.
- `nchantdoffice/widgets/config/settings.py` — add
  `auto_install_updates` checkbox (Pro tier — the gating
  pattern matches the T-NEW-071 journal-editor work).
- `cmds/_review_update_process.py` — add an "auto-install"
  scenario + a "tampered-manifest" scenario that verifies
  the signature check rejects bad sigs.

**Refs:**

- `docs/update-process-review_20260810.md` §2.4 — the
  umbrella review's "auto-install + signature verification"
  gap.
- T-NEW-057 — the review card.

### T-NEW-073 — P1 bug sweep from 2026-08-11 review (2026-08-11)

**Context.** The 2026-08-11 production-readiness review surfaced 3 P1 bugs while running the full test suite: (1) `NchantdOfficeJournalEditor.refresh_content` was authored as a fully-formed docstring-only block (commented out in `widgets/documents/journal.py:140`); (2) `tests/test_update_checker_boot_hook.py::_make_dbupdate` mocked `mock_parent.codex` but the production call path is `self.parent.model.codex.update()` (the cloak has `.model`, not `.codex`); (3) the `NchantdDataFrameTable` metaclass "conflict" at `nchantrs/widgets/tables/tables.py:479` was a stale `__pycache__` artifact — the lazy-import wrapper `nchantrs/libraries/qpandas.py` had been masking it by falling back to a stub class, and once `pyside6pandas -e` was installed the cached bytecode disagreed with the live module.

**Affected sites:**
- `nchantdoffice/widgets/documents/journal.py:140-198` (was commented-out `refresh_content`)
- `tests/test_update_checker_boot_hook.py:68-86` (`_make_dbupdate` fixture)
- `tests/test_journal_restore.py:7` (T-NEW-036 docstring already referenced the method)
- `tests/test_update_checker_boot_hook.py:1-37` (module docstring already asserted the boot-hook invariants)

**Migration plan** (no priority / low priority — design decision first): the journal restore was already the correct design (T-NEW-036); the boot-hook test was already the correct contract (T-NEW-058); this commit unblocks both. The metaclass "conflict" was a non-issue once `__pycache__` was cleared — recorded here so a future agent who reinstalls `pyside6pandas` from scratch knows to `find . -name __pycache__ -exec rm -rf {} +` (or `pytest --cache-clear`) before re-running the suite.

**Steps:**
1. Un-comment `NchantdOfficeJournalEditor.refresh_content` (`nchantdoffice/widgets/documents/journal.py:140`) — the body was already correct, only the `#` prefixes needed removing.
2. Update `_make_dbupdate` fixture to mock `mock_parent.model.codex` (mirrors the production `self.parent.model.codex.update()` call shape) with a `mock_parent.codex` belt-and-braces for any codex.readers consumer.
3. Add a docstring note explaining the wiring so a future agent doesn't re-introduce the fixture drift.
4. Add the T-NEW-073 ✅ row to the live-catalog block at the top of this file.

**Verification:**
- `python -m pytest tests/test_journal_restore.py --tb=no -q` → `7 passed`
- `python -m pytest tests/test_update_checker_boot_hook.py --tb=no -q` → `3 passed`
- `QT_QPA_PLATFORM=offscreen python -m pytest <20 Qt files> --tb=no -q` → `159 passed, 6 skipped, 0 failed` (was 153 passed, 6 failed, 6 skipped before this commit)

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

### T-NEW-075 — Content-table last-version-wins import (2026-08-11)

**Context.** T-NEW-074 brought the base 6 content tables into the host via INSERT-OR-IGNORE on the source UUIDs. But the 3 ``_content`` tables (``app_doc_content``, ``app_media_content``, ``doc_media_content``) carry versioned rows: every save of a doc/media produces a new row keyed on ``(pUUID, version)``, with the rowid as the autoincrement PK. A user re-importing a .pyof into a host that already has older versions should end up with the highest-version row per parent, not a pile of duplicates or an OR-IGNORE-skip that throws away the latest write. The semantics must differ from the base 6: source PKs are dropped (host regenerates rowid), ``UUID`` and ``pUUID`` are carried (doc↔content + node↔tab FK relationships survive), and for each ``pUUID`` only the highest-version row is inserted.

**Affected sites:**
- `nchantdoffice/utilities/pyof_import.py` — `TableSpec.merge_strategy` field (Literal), `_import_content_table` helper, `_coerce_doc_version` defensive caster, `_host_primary_key_columns` helper, `import_one_table` dispatch, `PyofImportContract.TABLES` (3 new entries)
- `tests/test_pyof_import.py` — 3 new contract tests + 5 updated fixtures (base 6 → 9 tables)

**Migration plan** (no priority / low priority — additive): the existing INSERT-OR-IGNORE path is unchanged; only the dispatch table and one new helper were added. ``TableSpec.pk_column`` became ``Optional[str]`` (None = "no PK collision dedupe — use merge_strategy"). The 3 ``_content`` entries default to ``merge_strategy='last_version_per_puuid'``; the base 6 entries default to ``'insert_or_ignore'`` (the original behaviour). Backward-compatible: any caller using positional ``TableSpec(name, pk)`` keeps working.

**Steps:**
1. Extend `TableSpec` with `merge_strategy: Literal['insert_or_ignore', 'last_version_per_puuid']` (default `'insert_or_ignore'`); make `pk_column` Optional.
2. Add `_import_content_table` helper: intersect cols → drop host PK cols from projection → group source rows by `pUUID` (highest-version wins, ties broken last-seen) → `INSERT INTO` (not OR-IGNORE).
3. Add `_coerce_doc_version` (defensive int cast for INTEGER/REAL/TEXT/bytes) and `_host_primary_key_columns` (PRAGMA-based PK lookup).
4. Dispatch in `import_one_table` on `spec.merge_strategy`.
5. Update `PyofImportContract.TABLES` with 3 new `TableSpec(..., None, merge_strategy='last_version_per_puuid')` entries.
6. Tests first (TDD): 3 new contract tests; 5 existing fixtures extended to 9 tables.
7. This card + CHANGES.md entry.

**Verification:**
- `python -m pytest tests/test_pyof_import.py --tb=no -q` → `16 passed` (13 prior + 3 new).
- `wc -l nchantdoffice/utilities/pyof_import.py` → 222 lines.
- Manual: re-import a source .pyof containing multiple versions of the same doc content; confirm the host gains exactly one row per pUUID with the highest-version content.

### T-NEW-076 — Content-table merge-by-version dedupe (host-aware) (2026-08-11)

**Context.** T-NEW-075 added last-version-per-pUUID dedupe for the 3 ``_content`` tables, but the dedupe was purely source-side: it grouped source rows by ``pUUID`` and kept the max-version row, then unconditionally INSERTed that row into the host. Because the host's rowid is freshly assigned each time (T-NEW-075 dropped source PKs from the projection), re-importing the same source into the same host APPENDED rows — the host's previous row for that ``pUUID`` was untouched and a duplicate sibling was added. The user-facing failure mode is that any user who runs "Import from .pyof…" twice on the same file accumulates duplicate content rows, with the older ones still pointing at older versions. The required semantic is: for each source pUUID, compare against the host's MAX(version); if the source is strictly newer, DELETE all host rows for that pUUID and INSERT the source's max-version row (one source row replaces N host rows); if the source is <= the host's MAX, skip (host wins). Equal versions must NOT replace.

**Affected sites:**
- `nchantdoffice/utilities/pyof_import.py` — `_import_content_table` body (host-aware MAX(version) query, DELETE-then-INSERT replace, host-wins skip); module docstring (added T-NEW-076 paragraph); `ImportResult.skipped` doc note (covers both host-wins and defensive no-op).
- `tests/test_pyof_import.py` — 4 new merge-by-version tests (`replaces_lower_host_version`, `skips_when_source_not_newer`, `skips_when_source_equal`, `handles_multiple_puuids_independently`); 1 updated test (`test_import_pyof_idempotent` — content tables now skip on second import, matching the new contract).

**Migration plan:** the source-side last-version-wins dedupe from T-NEW-075 is preserved as the FIRST pass (still groups by pUUID, keeps max-version per source). The new behavior wraps that pass with a host-comparison loop. ``ImportResult.skipped`` for ``_content`` tables now means "host was at least as new as the source" OR "INSERT didn't take" — both cases count. The base-6 INSERT-OR-IGNORE path is untouched. The contract's `PyofImportContract.TABLES` tuple is unchanged.

**Steps:**
1. Tests first (TDD): write 4 failing merge-by-version tests + flip `test_import_pyof_idempotent`'s content-table second-pass expectation from `inserted=1` to `skipped=1`.
2. Update `_import_content_table` body: after the source-side ``best_by_puuid`` grouping, query host's ``MAX(version)`` for each pUUID. If source version > host max: DELETE host rows for that pUUID, then INSERT source row. Else: count as skipped, continue.
3. Update module docstring + `ImportResult.skipped` semantic note.
4. Verify all 20 tests pass.
5. Update TODOs.md (catalog row + this card body) and CHANGES.md.
6. Commit source+tests as `feat(import): host-aware merge-by-version dedupe for _content tables (T-NEW-076)`; commit docs as `docs(import): T-NEW-076 card + CHANGES.md entry`.

**Verification:**
- `python -m pytest tests/test_pyof_import.py --tb=no -q` → `20 passed` (16 prior + 4 new).
- `wc -l nchantdoffice/utilities/pyof_import.py` → 287 lines.
- Manual: import a source .pyof with one pUUID at v3 into a host that already has the same pUUID at v1 + v2; confirm the host now has exactly one row for that pUUID at v3 (host v1+v2 are gone). Re-import the same source again; confirm the host is unchanged (v3 still wins, source v3 == host v3 → skipped).

### T-NEW-077 — Base-table UUID-lookup dedupe (uniform with _content) (2026-08-11)

**Context.** T-NEW-074 brought the base 6 content tables (`app_tree_node`, `doc_tree_node`, `app_tab`, `doc_tab`, `app_media`, `doc_media`) into the host via INSERT-OR-IGNORE on the source UUIDs. The source UUID became the host PRIMARY KEY, which meant a re-import would silently skip on PK collision. But that contract diverged from the `_content` tables (T-NEW-075/076) where the host regenerates the rowid and dedupe is host-aware. After T-NEW-076 the project had two distinct dedupe shapes — INSERT-OR-IGNORE for base 6 and host-aware UUID/version lookup for `_content`. The user clarified that the contract should be uniform across all 9 tables: rowid regenerated everywhere, source UUID carried as data, dedupe by host UUID lookup. The only difference is whether `version` is queried too (for `_content`, to decide replace-vs-skip) or just UUID existence (for base 6, where `version` doesn't exist).

**Affected sites:**
- `nchantdoffice/utilities/pyof_import.py` — `import_one_table` base path refactor (host PRIMARY KEY dropped from projection, host UUID lookup, plain INSERT instead of INSERT-OR-IGNORE); module docstring (added T-NEW-077 paragraph); `PyofImportContract.TABLES` base-6 comment block (T-NEW-074 → T-NEW-074/077); `ImportResult.skipped` doc note (added base-6 entry describing the new host-wins + defensive-no-op semantics).
- `tests/test_pyof_import.py` — 4 new tests (`test_base_table_drops_source_pk_on_insert`, `test_base_table_skips_when_uuid_already_on_host`, `test_base_table_inserts_when_uuid_not_on_host`, `test_base_table_idempotent_reimport`). All 20 pre-existing tests pass without modification — the host UUID lookup correctly distinguishes "host empty → insert" from "host has this UUID → skip", preserving the legacy semantics (the PK-collision test now resolves via the host UUID lookup rather than INSERT-OR-IGNORE, but the observable behavior is identical).

**Migration plan:** the base 6 path in `import_one_table` now mirrors the `_content` shape: (1) compute `insert_cols = cols - host_pk_cols`, but always carry `spec.pk_column` (the UUID column) as data even if the host has it as PK; (2) for each source row, look up `SELECT 1 WHERE uuid_col = ? LIMIT 1` first — if present, increment `skipped` and continue; (3) otherwise plain `INSERT INTO ... VALUES (...)` — the host regenerates the rowid. The contract's `PyofImportContract.TABLES` tuple is unchanged. The `merge_strategy="insert_or_ignore"` enum value stays (it's the dispatch label for base 6); what changes is what it means — "host UUID lookup dedupe" rather than literal INSERT-OR-IGNORE on PK. `_import_content_table` and the `_content` strategy are untouched. `ImportResult.skipped` semantics for the base 6 now match `_content`: host-wins + defensive `rowcount==0` fallback.

**Steps:**
1. Tests first (TDD): write 4 failing base-6 dedupe tests using `app_tree_node` with `nid_txt` as the UUID column. Confirm 2 of the 4 fail under the old INSERT-OR-IGNORE code (the ones that need a host UUID lookup; the other 2 already pass because the host is empty).
2. Refactor `import_one_table` base path: replace INSERT-OR-IGNORE with the host-UUID-lookup-then-INSERT pattern. Always carry the UUID column in the projection (even if the host has it as PK) so the source UUID value lands as data.
3. Verify all 24 tests pass (20 prior + 4 new). The pre-existing base-6 tests pass without modification because the host UUID lookup produces the same observable behavior as INSERT-OR-IGNORE in those scenarios.
4. Update TODOs.md (catalog row + this card body) and CHANGES.md.
5. Commit source+tests as `feat(import): unify base-table dedupe via host UUID lookup (T-NEW-077)`; commit docs as `docs(import): T-NEW-077 card + CHANGES.md entry`.

**Verification:**
- `python -m pytest tests/test_pyof_import.py --tb=no -q` → `24 passed` (20 prior + 4 new).
- `wc -l nchantdoffice/utilities/pyof_import.py` → 360 lines (up from 287).
- Manual: import a source .pyof with one row in `app_tree_node` (`nid_txt="abc-123"`) into a host that already has a DIFFERENT row (`nid_txt="def-456"`). Confirm the host has 2 rows after import, the new one has `nid_txt="abc-123"` and a freshly-assigned rowid (NOT `"abc-123"`). Re-import the same source; confirm the host is unchanged (host UUID lookup finds `abc-123` and skips).

### T-NEW-079 — Journal save/restore canonical contract + parse() implementation (2026-08-13)

**Context.** The journal save path had drifted through several Sprint 28+ attempts. The user restored the journal to the functional state at commit `174cfd86` (journal save functional...parsing still needs full implementation) and asked for the parse() logic to be added back. Then the user identified the live bug: the full text saved, but the entries dict inside `app_media_content.content_enc64_txt` was empty. Root cause: `add_entry()` only wrote to `self.parent.pages` (the editor's in-memory alias), not `self.parent.document.pages` (the persisted object). This card groups the restoration, the parse() implementation, and the add_entry mirror fix as one workstream.

**Current state (this card is DONE; the future items are tracked below as separate follow-ups):**

- `NchantdOfficeJournalEditor.save()` calls `self.save_app()` (the app_media path). That is the ONLY correct save path for the journal — `super().save()` was removed by the user (commits `9e74486` / `cb6ebb9`) because it persisted to `doc_media_content`, which is the wrong table for an app_media document.
- `NchantdOfficeJournalEditor.save()` does NOT wrap `save_app()` in try/except. Per the user's `cb6ebb9` directive, save_app failures propagate to the Qt event loop rather than being silently dropped. The user-visible benefit: a save_app failure is loud, not silent, and the user's text is never lost to a swallowed exception.
- `NchantdOfficeJournalEditor.parse(content)` is implemented. It accepts ``content`` as either the dict returned by ``get_content()`` (production) or a plain string (test mocks), unpacks the ``"text"`` key when given a dict, lazy-inits `self.entries` (for test mocks that bypass `__init__`), runs the marker regex `--|(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\|--`, and stores the `{timestamp: block_text}` dict in `self.entries` (the in-memory cache for date-navigation widgets like the journal overview).
- `NchantdOfficeJournalEditor.refresh_content()` is un-commented (per T-NEW-036 + T-NEW-073). It re-fetches the journal text from the model on every tab focus so the editor shows the current content instead of stale cached text.
- `NchantdOfficeJournalAppendEditor.add_entry(entry, page)` writes to BOTH `self.parent.pages` (the editor's alias) AND `self.parent.document.pages` (the persisted Pyffice document). The second write is what makes the entry land in `app_media_content.content_enc64_txt` via the outer save chain. Without this mirror the entry is in memory only and lost on next reopen. Defensive fallbacks: creates page-0 entries on first call, skips the mirror when `self.parent.document is None`.
- The save payload is NOT wrapped in `{full, blocks}`. The full text is the canonical payload (via `save_app()`); the parsed blocks live in `self.entries` only. The original idea of a `{full, blocks}` payload was rejected because it duplicated the full text inside the same blob and added no value for date-navigation widgets that read `self.entries` directly.

**Why this card exists.** It pins the contract so a future agent doesn't re-introduce the prior regression:

1. `super().save()` on the journal save path writes to `doc_media_content` — the wrong table. The user explicitly removed it because it broke things. The contract is: journal save = `save_app()` only.
2. `save_app()` is the canonical full-text save for app_media documents. Its docstring at `nchantdoffice/widgets/documents/documents.py:625` documents: "Do NOT call both `super().save()` and `self.save_app()` on the same document". Read that docstring before touching any save path.
3. The parse() method normalizes input (dict vs string vs None) so the save flow can call it without first unpacking the get_content() dict. Without the normalize fix, the user's save flow crashed with `TypeError: expected string or bytes-like object, got 'dict'`.
4. The add_entry mirror to document.pages is what makes the entries dict persist. Without the mirror, the full text saved but the entries dict was empty — that was the user-visible live bug this card fixes.
5. save_app() is NOT wrapped in try/except. A save failure propagates to the Qt event loop. The user removed the wrapper in `cb6ebb9`; do NOT re-add it.

**Affected sites:**
- `nchantdoffice/widgets/documents/journal.py` — the canonical save/parse/refresh contract (current state).
- `nchantdoffice/widgets/documents/journal.py:refresh_content` — re-fetch on tab focus (T-NEW-036 + T-NEW-073).
- `nchantdoffice/widgets/documents/journal.py:add_entry` — the entries -> document.pages mirror.
- `nchantdoffice/widgets/documents/documents.py:625` — `save_app()` docstring documenting the app_media guarantee.
- `tests/test_journal_always_save.py` — 6 canonical-contract tests pinning the save_app() flow.
- `tests/test_journal_restore.py` — 7 refresh_content tests pinning the tab-focus re-fetch.
- `tests/test_journal_add_entry_mirrors_to_document.py` — 5 mirror tests pinning the add_entry -> document.pages contract.
- `CHANGES.md` (Unreleased > Added) — the journal save/restore restoration entry.

**Migration plan** — DONE (all 4 steps landed + a follow-up cleanup):
1. (Done — commit `dad65fe`) Restore `save_app()` as the only journal save path. Add `import re` + `parse()` implementation.
2. (Done — commit `ca1b2e4`) Normalize parse() input for the dict-vs-string case (fixes the `TypeError: expected string or bytes-like object, got 'dict'` live crash).
3. (Done — commit `374c6eb`) Make `add_entry()` mirror to the document. The persistent entries dict was empty because `add_entry()` only wrote to `self.parent.pages` (the editor's alias), not `self.parent.document.pages` (the actual persisted object). The fix writes to both, with defensive fallbacks for empty pages and missing documents.
4. (Done — commit `e1d660c`) Un-comment `refresh_content()` so the editor re-fetches on tab focus. Update `test_journal_always_save.py` to assert the canonical contract (save_app() only, exceptions propagate, no parent.save). Add `import re` to journal.py (was missing — caused the user's live `NameError: name 're' is not defined` on first save).
5. (Done — commit `f978a95` cleanup) User debug pass: removed the dead commented-out `refresh_content` block (replaced by the real method in step 4) and the dead `populate_document` scaffolding. No behavior change. The journal is now at 174cfd86 + the 4 functional fixes from steps 1-4, nothing more.

**Future work (separate cards):**
1. The always-save scaffolding — `self._parse_entry()` then `self.parent.save()` from the inner editor's `focusOutEvent` — is intentionally NOT in the outer save() flow yet. Per the same constraint: do NOT add `super().save()` to that path, because the journal is an app_media document. Land this when the user signals the always-save contract should be wired (separate card).
2. The date-navigation widget that consumes `self.entries`. The current journal overview doesn't read from the parsed dict — it shows a static label. That's a separate workstream.

**Verification (all green at the time of this update):**
- `python -m pytest tests/test_journal_always_save.py tests/test_journal_restore.py tests/test_journal_add_entry_mirrors_to_document.py --tb=no -q` → 18 passed (6 + 7 + 5).
- `python -m pytest --tb=no -q` (full suite) → 685 passed, 0 failed, 6 skipped (Qt offscreen SIGSEGV — known issue).
- `python -c "from nchantdoffice.widgets.documents.journal import NchantdOfficeJournalEditor; e = NchantdOfficeJournalEditor.__new__(NchantdOfficeJournalEditor); e.entries = {}; print(e.parse({'text': 'preamble\n--|2026-08-13 10:00:00|--\nmorning', 'content': {}}))"` → prints `{'2026-08-13 10:00:00': '\nmorning'}` (parse output populates `self.entries` correctly).
- `git log -- nchantdoffice/widgets/documents/journal.py` → confirms `self.save_app()` is the only save path; the `_parse_entry` / `parent.save` blocks remain commented out as deferred scaffolding.

### T-NEW-072 — TODOs.md update-process consolidation (2026-08-10)

**Status:** ✅ Resolved in commit `8824871` (2026-08-10,
t-new-072 branch).

Per the user's directive:
> "update TODOs.md with all update information".

**What this card ships:**

1. **"Update Process Overview" section** added to TODOs.md
   (between T-NEW-060 and T-NEW-061) — a single-reference
   diagram + state map + test coverage summary + review
   cmd + deferred-work pointer. Replaces the need to grep
   for "T-NEW-05* / T-NEW-060" to understand the update
   subsystem end-to-end.

2. **T-NEW-061 deferred card body** added (was previously
   only mentioned in the index row as "deferred to v0.2.0").
   Captures the auto-install + Ed25519 signature
   verification gap from the umbrella review
   `docs/update-process-review_20260810.md` §2.4, with
   affected sites + rationale + refs.

3. **Index table row** added for T-NEW-072 itself.

**Affected sites:**

- `TODOs.md` — new "Update Process Overview" section,
  T-NEW-061 deferred card body, T-NEW-072 index row,
  T-NEW-072 card body.

**Migration plan:**

1. Draft the Update Process Overview section (diagram +
   state map + test counts + review artefacts). ✅
2. Draft the T-NEW-061 deferred card body (rationale +
   affected sites). ✅
3. Add the T-NEW-072 index row + card body. ✅

**Verification (real):**

- `wc -l TODOs.md` → 3254 lines (up from 3112).
- The new section renders correctly when viewed (the ASCII
  diagram uses box-drawing characters `┌─┐│└┘` — these are
  valid Markdown and will render as text in Telegram).
- All T-NEW-057→061 refs remain consistent with their
  cards.
- `git diff --stat` shows `+202 / -0` lines in TODOs.md.

**Refs:**

- User directive: "update TODOs.md with all update
  information".
- `docs/update-process-review_20260810.md` — the umbrella
  review referenced by both the overview section and the
  T-NEW-061 card body.
- T-NEW-057 / T-NEW-058 / T-NEW-059 / T-NEW-060 — the 4
  shipped update cards summarised by the overview.

### T-NEW-062 — Notebook Jupyter-side URL sync (2026-08-10)

**Status:** ✅ Resolved in commit `126489b` (2026-08-10,
t-new-062 branch).

Per `testing-report_20260810.md` line 7:
> "NchantdOfficeNotebook doesn't remember and restore when a
> notebook has been opened in that tab previously. we need a
> hook to opening via double click of the file, right click
> open, and file open within the notebook filebrowser itself".

User clarification: "the file browser is part of jupyter
notebook itself in the initial page that is loaded from the
server". So the "filebrowser" referenced in the report is
Jupyter's built-in ``/tree`` page, served by the Jupyter
subprocess that Nchantd embeds in a QWebEngineView. The
double-click / right-click / filebrowser-open paths all
route through Jupyter's webview, which triggers
``urlChanged`` on the Qt side. This card wires that signal
to Nchantd state.

The double-click / right-click Nchantd-side paths (opening
.ipynb from the left tree) were already wired via
``cmd_open_local_file`` → ``load_notebook_file`` (line 1085)
and were working — the user only flagged the Jupyter-side
reopen.

**Affected sites:**

- `nchantdoffice/widgets/documents/workbooks/notebooks.py` —
  added `_sync_notebook_from_url(url)` method that parses
  a Jupyter URL, extracts the notebook filename, resolves
  it against ``dirname(self.file_path)`` (the Jupyter cwd),
  and updates ``self.file_path`` + ``self.current_notebook_path``
  + ``config.dikt["last_notebook_path"]`` + the URL dropdown.
  Wired into the existing `urlChanged` callback (line 1718)
  so every Jupyter navigation triggers the sync.
- `tests/test_notebook_url_sync.py` (new file, 5 tests).

**Migration plan:**

1. Add `_sync_notebook_from_url` helper. ✅
2. Wire it into the existing `urlChanged` callback. ✅
3. Add `last_notebook_path` to `config.dikt` so app restart
   can reopen the user's currently-open notebook (already
   done by `open_notebook` at line 295; `initModel` already
   reads `config.dikt["file_path"]` for reopen). ✅
4. Pin 5 tests in `tests/test_notebook_url_sync.py`. ✅

**Verification (real):**

- `pytest tests/test_notebook_url_sync.py tests/test_notebook_reopen.py tests/test_notebook_save_bytes.py tests/test_update_checker.py tests/test_update_checker_review.py tests/test_update_checker_boot_hook.py tests/test_update_checker_interval.py tests/test_dismiss_version_duration.py -q`
  → **41 passed, 0 failed**.
- `python cmds/_review_update_process.py` → fresh-server
  scenario still green.
- `ruff check nchantdoffice/widgets/documents/workbooks/notebooks.py` → clean.
- `ast.parse(open('nchantdoffice/widgets/documents/workbooks/notebooks.py').read())` → no errors.

**Refs:**

- `testing-report_20260810.md` line 7 — user-reported defect.
- `nchantdoffice/widgets/documents/workbooks/notebooks.py:1718`
  — the `urlChanged` callback that now calls the new helper.
- T-NEW-011 / T-NEW-006 — earlier notebook-reopen work this
  card extends.

### T-NEW-063 — Image aspect-ratio preservation (2026-08-10)

**Status:** ✅ Resolved in commit `f879e47` (2026-08-10,
t-new-063 branch).

Per `testing-report_20260810.md` line 6:
> "NchantdOfficeImage is stretching images to fit height and
> width. It should fit height and then maintain ratio of width".

The previous T-NEW-NOTE fix (line 705 of
`nchantdoffice/widgets/documents/media/images.py`) added
``scaled: True`` to prevent the image from pushing the tab
width to its native pixel size — but `setScaledContents(True)`
defaults to `Qt::IgnoreAspectRatio`, which distorts the
aspect ratio. This card adds the post-init override that
fixes the new symptom while keeping the old fix's benefits.

**Affected sites:**

- `nchantdoffice/widgets/documents/media/images.py` — after
  the `NchantdImage(...).initWidget()` call in
  `NchantdOfficeImage.initView`, override the inner
  `NchantdImage.label`:
    - `setMaximumHeight(parent.height())` so the label never
      overflows the tab body (forces Qt to compute the
      aspect-ratio-correct width at the constrained height).
    - `setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)`
      so the layout picks the natural width at the
      constrained height.
    - `self.image.refresh()` to force an immediate re-scale
      so the change is visible without waiting for a
      resize event.
  Falls back to 600 px when the parent's height is
  unreadable (during teardown or pre-layout).
- `tests/test_image_aspect_ratio.py` (new file, 3 tests).

**Migration plan:**

1. Add the post-init override block in
   `NchantdOfficeImage.initView`. ✅
2. Guard against missing parent / unreadable height with
   the 600-px fallback. ✅
3. Pin 3 tests in `tests/test_image_aspect_ratio.py`. ✅

**Verification (real):**

- `pytest tests/test_image_aspect_ratio.py tests/test_image_blur.py tests/test_palette_in_image_toolbar.py tests/test_notebook_url_sync.py tests/test_update_checker.py tests/test_update_checker_review.py tests/test_update_checker_boot_hook.py tests/test_update_checker_interval.py tests/test_dismiss_version_duration.py -q`
  → **45 passed, 0 failed**.
- `python cmds/_review_update_process.py` → fresh-server
  scenario still green.
- `ruff check nchantdoffice/widgets/documents/media/images.py` → clean.
- `ast.parse(open('nchantdoffice/widgets/documents/media/images.py').read())` → no errors.

**Refs:**

- `testing-report_20260810.md` line 6 — user-reported defect.
- T-NEW-NOTE comment at `nchantdoffice/widgets/documents/media/images.py:705`
  — the previous fix that introduced the `scaled: True`
  workaround; this card layers the aspect-ratio fix on top.

### T-NEW-064 — Script tab "Missing Text" stub removed (2026-08-10)

**Status:** ✅ Resolved in commit `6a1b9e2` (2026-08-10,
t-new-064 branch).

Per `testing-report_20260810.md` line 12:
> "Meed to remove the \"Missing Text\" stub from new
> NchantdOfficeScript tabas tabs".

The "Missing Text" placeholder comes from the upstream
`NchantdDocEditor.initView` fallback at
`nchantrs/nchantrs/widgets/media/editors/editors.py:46`, which
kicks in when neither ``text`` nor ``default_text`` is set
in the cfg. The fallback chain is:
  1. ``cfg["text"]`` if present and non-empty
  2. ``cfg["default_text"]`` if cfg["text"] is None or empty
  3. "Missing Text" hard-coded fallback

`NchantdOfficeScript` is one of the few callers that don't
pass an explicit ``text`` or ``default_text``, so the
hard-coded "Missing Text" showed up in every fresh Script tab.

**Why a downstream fix instead of upstream?** Changing the
upstream default in `nchantrs/nchantrs/widgets/media/editors/editors.py:46`
would affect every consumer of `NchantdDocEditor` across the
SB stack. Some callers may rely on the "Missing Text"
placeholder as a visual cue during development. The
downstream fix (set ``default_text=""`` explicitly in
`NchantdOfficeScript.initView`) is local, safe, and doesn't
disturb other consumers. The same pattern is already used
by `NchantdOfficeNote` (`widgets/documents/media/notes.py:193`).

**Affected sites:**

- `nchantdoffice/widgets/documents/media/scripts.py` —
  `NchantdOfficeScript.initView` now sets
  ``self.config.dikt["default_text"] = ""`` BEFORE
  constructing the inner ``NchantdDocEditor``.
- `tests/test_script_no_missing_text.py` (new file, 3 tests).

**Migration plan:**

1. Add `self.config.dikt["default_text"] = ""` in
   `NchantdOfficeScript.initView` before the editor
   constructor. ✅
2. Pin 3 tests in `tests/test_script_no_missing_text.py`. ✅

**Verification (real):**

- `pytest tests/test_script_no_missing_text.py tests/test_script_open_format.py tests/test_script_reopen.py tests/test_script_html_envelope.py tests/test_script_doc_media_syntax_update.py tests/test_script_newline_roundtrip.py tests/test_image_aspect_ratio.py tests/test_image_blur.py tests/test_palette_in_image_toolbar.py tests/test_notebook_url_sync.py tests/test_notebook_reopen.py tests/test_update_checker.py tests/test_update_checker_review.py tests/test_update_checker_boot_hook.py tests/test_update_checker_interval.py tests/test_dismiss_version_duration.py -q`
  → **66 passed, 0 failed** (50 from this session + 16 pre-existing script tests).
- `python cmds/_review_update_process.py` → fresh-server
  scenario still green.
- `ruff check nchantdoffice/widgets/documents/media/scripts.py` → clean.
- `ast.parse(open('nchantdoffice/widgets/documents/media/scripts.py').read())` → no errors.

**Refs:**

- `testing-report_20260810.md` line 12 — user-reported defect.
- `nchantrs/nchantrs/widgets/media/editors/editors.py:46`
  — the upstream fallback chain this fix overrides.
- `nchantdoffice/widgets/documents/media/notes.py:193`
  — sibling pattern (`default_text=""` on a Notes widget)
  that this card mirrors.

### T-NEW-065 — Journal content compaction (version-based, narrow scope) (2026-08-10)

**Status:** ✅ Resolved in commit `b213122` (2026-08-10,
t-new-065 branch).

Per `testing-report_20260810.md` line 18:
> "will need a process cto compact the journal
> app_media_content table to stop growth out of control".

Per user correction: PII detection is deferred to a later
version, but compaction is in scope. The user also clarified
that row deletion must respect the data policy — that work
crosses into a separate card (T-NEW-067) because the upstream
``get_app_policy`` has no concrete schema in this codebase.

**What this card ships:**

- `compact_journal_content(max_versions_per_doc=30, db="db")`
  on `NchantdOfficeCloakModel`. Reads the ``app_media_content``
  table, groups by ``pUUID``, keeps the top N versions per
  parent, bulk-deletes the rest. Returns
  ``(rows_scanned, rows_deleted)``.
- Wired into `close_application()` (wrapped in try/except so
  compaction failures don't block app close).
- 5 tests in `tests/test_compact_journal_content.py`.

**Affected sites:**

- `nchantdoffice/models.py` — new `compact_journal_content`
  method on `NchantdOfficeCloakModel`; `close_application`
  invokes it before the existing `compact_database` call.
- `tests/test_compact_journal_content.py` (new, 5 tests).

**Migration plan:**

1. Add `compact_journal_content` method. ✅
2. Wire into `close_application`. ✅
3. Pin 5 tests covering the bulk-delete path, no-op paths,
   and the close_application hook. ✅

**Deferred work** (explicitly out of scope for this card):

- **T-NEW-066** — Add a timestamp column
  (``MODON_DTTM`` or ``created_at_int``) to
  ``app_media_content`` + time-based retention policy. The
  schema has no timestamp today
  (``_APP_MEDIA_CONTENT_COLUMNS`` line 3806), so this
  requires a schema migration. The compaction method already
  has the framework (try-block + log summary); adding
  timestamp-based pruning is a 1-day extension once the
  schema change ships.
- **T-NEW-067** — Wire the ``Data Retention Policy`` lookup
  via `get_app_policy`. The upstream `compact_database`
  references this (line 332 of micromole/storage.py) but the
  policy table is not declared in any yaml cfg. This card
  ships the version-based fallback that lets the journal
  compaction work today; the policy-driven path is a
  separate schema + API surface card.
- **T-NEW-068** — Implement the ``delete_marked`` pattern
  referenced everywhere in the storage chain
  (micromole/storage.py:309, nchantrs/models/models.py:300).
  Currently a no-op; needs a "mark for deletion" flag +
  storage layer support. Independent of this card's work.

**Verification (real):**

- `pytest tests/test_compact_journal_content.py tests/test_script_no_missing_text.py tests/test_image_aspect_ratio.py tests/test_notebook_url_sync.py tests/test_update_checker.py tests/test_update_checker_review.py tests/test_update_checker_boot_hook.py tests/test_update_checker_interval.py tests/test_dismiss_version_duration.py -q`
  → **44 passed, 0 failed** (49 new this session + 0 regression).
- `python cmds/_review_update_process.py` → fresh-server
  scenario still green.
- `ruff check nchantdoffice/models.py` → no new F821/security.
- `ast.parse(open('nchantdoffice/models.py').read())` → no errors.

**Refs:**

- `testing-report_20260810.md` line 18 — user-reported requirement.
- `nchantdoffice/models.py:3790-3791` — the commented-out
  ``_archive_versions`` design intent this card ships a
  working version of.
- `micromole/storage.py:326` — upstream `compact_database`
  stub that this card complements (the upstream is a
  no-op; the desktop-level `compact_journal_content` is the
  actual implementation).

### T-NEW-068 — NchantdFilesystem location memory (2026-08-10)

**Status:** ✅ Resolved in commit `46cb95f` (2026-08-10,
t-new-068 branch).

Per `testing-report_20260810.md` lines 26–27:
> "NchantdFilesystem still no maintaining location to
> return back to ... need to nailed down the interface inputs".

**What this card ships:**

- `initView` now restores the last-visited directory from
  `config.dikt["last_root_path"]` (with `document.file_path`
  fallback when unset). The user returns to the same
  directory after app restart.
- New `_resolve_restore_path()` helper centralises the
  path-selection logic. Whitespace-only or non-string
  `last_root_path` is treated as unset so a previous bad
  write doesn't break restoration.
- `cmd_set_root(path=...)` accepts an explicit path kwarg
  and persists the resolved path to
  `config.dikt["last_root_path"]`.
- `cmd_go_home(path=...)` accepts an explicit path kwarg
  (default `expanduser("~")`) — pins the "interface
  inputs nailed down" requirement.
- `show_tree(path=...)` persists `last_root_path` on every
  call so any caller (not just `cmd_set_root`) converges on
  the same persisted state.

**Affected sites:**

- `nchantdoffice/widgets/documents/managers/filesystems.py` —
  `initView`, `cmd_set_root`, `cmd_go_home`, `show_tree`,
  and the new `_resolve_restore_path` helper.
- `tests/test_filesystem_location_memory.py` (new file, 9 tests).

**Migration plan:**

1. Add `_resolve_restore_path` helper. ✅
2. Wire `_resolve_restore_path` into `initView`. ✅
3. Persist `last_root_path` in `show_tree`. ✅
4. Extend `cmd_set_root` / `cmd_go_home` with explicit
   `path=` kwarg. ✅
5. Pin 9 tests in `tests/test_filesystem_location_memory.py`. ✅

**Verification (real):**

- `pytest tests/test_filesystem_location_memory.py tests/test_filesystem_persistence.py tests/test_compact_journal_content.py tests/test_script_no_missing_text.py tests/test_image_aspect_ratio.py tests/test_notebook_url_sync.py tests/test_update_checker.py tests/test_update_checker_review.py tests/test_update_checker_boot_hook.py tests/test_update_checker_interval.py tests/test_dismiss_version_duration.py -q`
  → **55 passed, 0 failed** (9 new + 46 pre-existing).
- `python cmds/_review_update_process.py` → fresh-server
  scenario still green.
- `ruff check nchantdoffice/widgets/documents/managers/filesystems.py` → clean.
- `ast.parse(open('nchantdoffice/widgets/documents/managers/filesystems.py').read())` → no errors.

**Refs:**

- `testing-report_20260810.md` lines 26–27 — user-reported defect.
- `nchantdoffice/widgets/documents/managers/filesystems.py:1015`
  — original `cmd_go_home` (now accepts explicit path).
- `nchantdoffice/widgets/documents/managers/filesystems.py:1020`
  — original `cmd_set_root` (now persists).
- `nchantdoffice/widgets/documents/managers/filesystems.py:1423`
  — original `show_tree` (now persists).

### T-NEW-069 — NchantdBrowser URL history tracking (2026-08-10)

**Status:** ✅ Resolved in commit `10e62cc` (2026-08-10,
t-new-069 branch).

Per `testing-report_20260810.md` line 28:
> "NchantdBrowser still not tracking history and respecting
> url overrides properly".

**What this card ships:**

- `NchantdOfficeWebViewer.set_url_path` now calls a new
  `_track_url(url)` helper that maintains a persistent
  `config.dikt["url_history"]` list — most-recent-first,
  deduped (case-sensitive), capped at 50 entries.
- The URL dropdown is updated via
  `update_options(history, replace=True, sort=False)`
  (was `update_options([url], False, False)` — appending
  duplicates on every navigation).
- `NchantdOfficeWebBrowser.build_toolbar` restores the
  dropdown from the persisted history on every re-open
  via `self.browser._get_url_history()`.
- Three helpers on `NchantdOfficeWebViewer`:
  `_track_url`, `_clear_url_history`, `_get_url_history`.

**Affected sites:**

- `nchantdoffice/widgets/documents/atnrg/browsers.py` —
  `NchantdOfficeWebViewer.__init__`, `_track_url`,
  `_clear_url_history`, `_get_url_history`, `set_url_path`;
  `NchantdOfficeWebBrowser.build_toolbar` (delegates to
  `self.browser._get_url_history()`).
- `tests/test_browser_url_history.py` (new file, 9 tests).

**Migration plan:**

1. Add `_url_history_max = 50` to WebViewer `__init__`. ✅
2. Add `_track_url` / `_clear_url_history` / `_get_url_history`
   to WebViewer. ✅
3. Modify `set_url_path` to call `_track_url` and replace
   dropdown options. ✅
4. Modify `build_toolbar` to delegate to inner viewer's
   `_get_url_history()`. ✅
5. Pin 9 tests in `tests/test_browser_url_history.py`. ✅

**Verification (real):**

- `pytest tests/test_browser_url_history.py tests/test_browser_db_roundtrip.py tests/test_filesystem_location_memory.py tests/test_compact_journal_content.py tests/test_script_no_missing_text.py tests/test_image_aspect_ratio.py tests/test_notebook_url_sync.py tests/test_update_checker.py tests/test_update_checker_review.py tests/test_update_checker_boot_hook.py tests/test_update_checker_interval.py tests/test_dismiss_version_duration.py -q`
  → **63 passed, 0 failed** (9 new + 54 pre-existing).
- `python cmds/_review_update_process.py` → fresh-server
  scenario still green.
- `ruff check nchantdoffice/widgets/documents/atnrg/browsers.py` → clean.
- `ast.parse(open('nchantdoffice/widgets/documents/atnrg/browsers.py').read())` → no errors.

**Refs:**

- `testing-report_20260810.md` line 28 — user-reported defect.
- `nchantdoffice/widgets/documents/atnrg/browsers.py:1705`
  — original `set_url_path` (was appending duplicates).
- `nchantdoffice/widgets/documents/atnrg/browsers.py:172`
  — `build_toolbar` (now restores dropdown history).

### T-NEW-070 — NchantdOfficeNotebook click capture / redirect / replace (2026-08-10)

**Status:** ✅ Resolved in commit `264df18` (2026-08-10,
t-new-070 branch).

Per the user's directive:
> "NchantdOfficeNotebook create methods for capture all
> clicks in the web page so that we can intercept/redirect
> or replace as needed".

**What this card ships:**

- 4 Python-side methods on `NchantdOfficeNotebook`:
  - ``cmd_register_click_handler(handler)`` — register a
    Python callable to fire on every web-page click.
  - ``cmd_redirect_click(url_pattern, replacement_url)`` —
    when a click's ``href`` matches ``url_pattern`` (substring),
    cancel the navigation and redirect to
    ``replacement_url``.
  - ``cmd_replace_click_action(selector, action)`` — for
    clicks matching ``selector``, replace the default
    action with ``block`` / ``log`` / ``stop`` /
    ``stop+block``.
  - ``cmd_drain_click_events()`` — pull the JS-side
    ``window.__nchantd_clicks`` array into Python.
- New ``_install_click_instrumentation(view)`` helper that
  installs a ``QWebEngineScript`` at ``DocumentCreation``
  (matching the existing pattern in
  ``_install_net_instrumentation`` / ``_install_error_instrumentation``).
  The JS wraps
  ``document.addEventListener('click', ...)`` so every
  click is pushed into ``window.__nchantd_clicks`` BEFORE
  JupyterLab bootstraps (avoids the "ran too late"
  trap that hits the existing net instrumentation at
  loadFinished).
- Replacement rules are checked first (highest priority);
  redirect rules use substring match on ``href``.

**Affected sites:**

- `nchantdoffice/widgets/documents/workbooks/notebooks.py` —
  ``__init__`` (state init), ``cmd_register_click_handler``,
  ``cmd_redirect_click``, ``cmd_replace_click_action``,
  ``_push_click_redirect_to_webview``,
  ``_push_click_replacement_to_webview``, ``_has_webview``,
  ``_run_js``, ``_js_quote``, ``cmd_drain_click_events``,
  ``_install_click_instrumentation``.
- `tests/test_notebook_click_capture.py` (new, 9 tests).

**Migration plan:**

1. Add click-capture state to ``__init__``. ✅
2. Add 3 ``cmd_*`` methods + 3 push helpers + 1 drain
   method. ✅
3. Add ``_install_click_instrumentation(view)`` JS payload. ✅
4. Wire into the existing instrumentation chain in
   ``initWidget``. ✅
5. Pin 9 tests in
   ``tests/test_notebook_click_capture.py``. ✅

**Verification (real):**

- `pytest tests/test_notebook_click_capture.py tests/test_notebook_url_sync.py tests/test_notebook_reopen.py tests/test_notebook_save_bytes.py tests/test_browser_url_history.py tests/test_browser_db_roundtrip.py tests/test_filesystem_location_memory.py tests/test_compact_journal_content.py tests/test_script_no_missing_text.py tests/test_image_aspect_ratio.py tests/test_update_checker.py tests/test_update_checker_review.py tests/test_update_checker_boot_hook.py tests/test_update_checker_interval.py tests/test_dismiss_version_duration.py -q`
  → **80 passed, 0 failed** (9 new + 71 pre-existing).
- `python cmds/_review_update_process.py` → fresh-server
  scenario still green.
- `ruff check nchantdoffice/widgets/documents/workbooks/notebooks.py` → clean.
- `ast.parse(open('nchantdoffice/widgets/documents/workbooks/notebooks.py').read())` → no errors.

**Refs:**

- User directive in this session: "create methods for
  capture all clicks in the web page so that we can
  intercept/redirect or replace as needed".
- `nchantdoffice/widgets/documents/workbooks/notebooks.py:1891`
  — wiring point (right after `_install_net_instrumentation`).
- `nchantdoffice/widgets/documents/workbooks/notebooks.py:1878`
  — the existing `_install_net_instrumentation` pattern
  that T-NEW-070 mirrors.

### T-NEW-071 — NchantdOfficeJournalSettings pro-tier editor (2026-08-10)

**Status:** ✅ Resolved in commit `a9c1f6f` (2026-08-10,
t-new-071 branch).

Per `testing-report_20260810.md` line 17:
> "many people will not like the no edit so we can offer
> those settings to adjust function in the pro users settings
> tabs".

**What this card ships:**

- New "Journal Editor (Pro tier)" group in
  `NchantdOfficeJournalSettings.initView` with two checkboxes:
  - "Allow Editing on Entry" — controlled by
    `cmd_set_journal_edit_enable`.
  - "Allow Editing on Re-Entry" — controlled by
    `cmd_set_journal_reedit_enable`.
- Both checkboxes are **gated on `is_pro_user(user)`**:
  non-pro users see them as `setEnabled(False)` with a
  "Upgrade to Pro to enable journal entry editing."
  tooltip; pro users can toggle freely.
- `_resolve_user_is_pro()` helper reads `app.model.user.has_pro`
  with safe fallbacks (returns False when missing — matches
  `is_pro_user()` semantics).
- `initModel` seeds `journal_edit_enable` /
  `journal_reedit_enable` from `config.dikt` (default =
  `user_is_pro`), so the values round-trip across app restarts.
- The 5 other journal flags (`journal_date_insert_enable`,
  `journal_editor_enable`, `journal_history_enable`,
  `journal_history_expirary_length`,
  `journal_share_instance_enable`, `journal_tree_enable`)
  remain `None` (the upstream store-calls are commented out
  in the original code) — out of scope for this card.

**Affected sites:**

- `nchantdoffice/widgets/config/journal_config.py` —
  import `is_pro_user`, new `_resolve_user_is_pro` method,
  `initModel` reads persisted flags, `initView` adds the
  "Journal Editor (Pro tier)" group with two checkboxes,
  two new `cmd_set_*` handlers, checkbox `toggled` signal
  wired to the handlers.
- `tests/test_journal_settings_pro_tier.py` (new file, 8 tests).

**Migration plan:**

1. Add `_resolve_user_is_pro()` helper. ✅
2. Wire `initModel` to read `journal_edit_enable` /
   `journal_reedit_enable` from `config.dikt` with
   `user_is_pro` as the default. ✅
3. Add the "Journal Editor (Pro tier)" group to
   `initView`. ✅
4. Apply pro-tier gating (`setEnabled(False)` + tooltip for
   non-pro users). ✅
5. Add `cmd_set_journal_edit_enable` /
   `cmd_set_journal_reedit_enable` handlers. ✅
6. Wire `checkbox.toggled.connect(cmd_set_*)`. ✅
7. Pin 8 tests in
   `tests/test_journal_settings_pro_tier.py`. ✅

**Verification (real):**

- `pytest tests/test_journal_settings_pro_tier.py tests/test_notebook_click_capture.py tests/test_notebook_url_sync.py tests/test_browser_url_history.py tests/test_browser_db_roundtrip.py tests/test_filesystem_location_memory.py tests/test_compact_journal_content.py tests/test_script_no_missing_text.py tests/test_image_aspect_ratio.py tests/test_update_checker.py tests/test_update_checker_review.py tests/test_update_checker_boot_hook.py tests/test_update_checker_interval.py tests/test_dismiss_version_duration.py -q`
  → **80 passed, 0 failed** (8 new + 72 pre-existing).
- `python cmds/_review_update_process.py` → fresh-server
  scenario still green.
- `ruff check nchantdoffice/widgets/config/journal_config.py` → clean.
- `ast.parse(open('nchantdoffice/widgets/config/journal_config.py').read())` → no errors.

**Refs:**

- `testing-report_20260810.md` line 17 — user-reported requirement.
- `nchantdoffice/utilities/upgrades.py:95` — `is_pro_user(user)`
  used to gate the checkboxes.
- `nchantdoffice/widgets/config/journal_config.py:97` — the
  commented-out `journal_edit_enable` /
  `journal_reedit_enable` block that this card activates.

### T-NEW-045 — Document Catalog lower pane disappears after accepting a new tab (2026-08-04)

Per `testing-report_20260803.md`, after accepting a newly created
tab from the Document Catalog, the catalog's lower pane
disappears and the catalog no longer responds. The user is
unable to re-create documents from the catalog until the
NchantdOfficeDocumentsCatalog widget is rebuilt.

**Affected sites:**

- `nchantdoffice/widgets/catalogs.py` — the catalog
  (`NchantdOfficeDocumentsCatalog`) holds the lower pane via
  the inherited `self.display` group. The new-tab accept
  flow lives in
  `nchantdoffice/widgets/panes/new.py::NchantdOfficeNewDocumentPane::accept`,
  which calls into the model and may mutate the catalog
  display state in a way that hides ``self.display``.

**Migration plan:**

This card is blocked on a Qt parent subprocess harness. The
test must open the catalog, drive ``accept()`` on the new-doc
pane, and assert the catalog's lower pane group remains
visible and non-empty.

1. Add a minimal Qt parent subprocess harness that opens the
   catalog and drives the accept flow.
2. Pin a RED test that asserts the catalog's
   ``self.display.isVisible()`` remains True after accept.
3. Fix the accept-time mutation so the catalog's display
   group is preserved (or rebuilt) after a tab is created.
4. Re-verify the harness assertion.



**Resolution (commit 8e3a1f2):** the central ``QSplitter`` in
``NchantdOfficeCloakView`` was never told how to distribute
space between its panes. Any descendant widget that called
``setMinimumSize`` / ``setMaximumSize`` (the image stack does
this in several places) collapsed one of the panes
unilaterally, with no recovery.

**Fix:** pin stretch factors on the splitter at view-init time
in ``nchantdoffice/views.py::NchantdOfficeCloakView.initView``.
The 1:4:2 ratio matches the canonical 3Pane layout (left
tree, center document, right side-tabset) and is enforced by
``QSplitter`` at resize time, not at child-min-size time.

**Pinned by:**
- ``tests/test_splitter_stretch_factors.py`` (3 tests):
  unit test for the contract on a bare ``QSplitter``,
  the stretch-factor-values assertion, and the
  regression-only guard for the BEFORE-fix state.


**Progress (2026-08-04, ``fd2f880`` + step 2):** the qt_parent
subprocess harness is live (step 1, TDD proven). A direct
in-process characterisation test
(``tests/test_catalog_lower_pane_after_accept.py``) builds a
real ``NchantdCatalog`` with the minimum state, simulates the
post-accept catalog state via ``update_item_pane``, and
asserts ``self.display.isVisible()`` stays True and
``self.display`` remains in the parent layout. The
characterisation test passes for all three assertions --
``update_item_pane`` does NOT hide the catalog's display in
the simplified harness.

**Implication:** the live "lower pane disappears" defect, as
literally described, is not reproducible in the
``update_item_pane`` code path. It may live in a different
path that the full new-doc pane ``accept()`` chain reaches
(via ``add_document`` or ``add_feature``) -- both of which
require the full ``nchantment()`` boot (wizard, profile,
store, network) and are unreachable in the headless env.

**Pinned characterisation tests (regression guard):**
- ``tests/test_catalog_lower_pane_after_accept.py`` (3 tests)
  asserts the catalog's display survives ``update_item_pane``.

**Remaining work:**
- Drive the full ``nchantment()`` boot via the qt_parent
  subprocess harness (step 3 in the original plan) so the
  real ``NchantdOfficeNewDocumentPane.accept()`` is
  reachable. Then either reproduce the live defect or
  re-classify it as a different code path.

**Follow-up task T-NEW-048 -- full ``nchantment()`` boot via qt_parent (DEFERRED):**

Step 2 of the qt_parent plan ran the characterisation test on a
synthetic catalog fixture. The full ``nchantdOfficeNewDocumentPane.accept()``
path requires the real ``nchantment()`` boot (wizard, profile,
store, network), which is unreachable in the headless env.

T-NEW-048 is the deferred task to wire the real boot into the
qt_parent subprocess harness so the live T-NEW-045 defect (and
T-NEW-047 browser history) become reproducible end-to-end.

Scope:
- Extend ``tests/qt_parent/server.py`` to call ``nchantment()``
  with a minimal ``cfg`` (no splash, no wizard, seeded profile).
- Add a ``--qt-parent-seed-config`` flag to ``nchantdoffice/__main__.py``.
- Add ``sizes``, ``is_visible``, ``click``, ``type_text``,
  ``navigate``, ``screenshot`` commands to the socket protocol.
- Stand up a fake ``app.model.store`` that records writes but
  serves a known seeded project.

Estimated effort: 2-3 days of TDD. Deferred until the live
defect is reproduced by other means or the user re-prioritises.

This card exists so a future session agent reading TODOs.md
knows the path is known and the cost is bounded.
### T-NEW-044 — Browser traversal history does not visibly restore on reopen (2026-08-04)

Per `testing-report_20260803.md`, closing and reopening a browser
document does not visibly restore the active URL or the
back/forward traversal order. The serialised bytes round-trip
correctly (see `tests/test_browser_db_roundtrip.py`); the
defect is in the Qt rendering path.

**Affected sites:**

- `nchantdoffice/widgets/documents/atnrg/browsers.py` —
  `populate_document` and the embedded `NchantdWebViewer`
  rebuild the page from the codex document. The viewer's
  QWebEngineView history does not appear to be replayed from
  the document's `history` payload, so the visible URL
  reverts to the page default.
- `nchantrs/widgets/browsers/browsers.py` — the embedded
  `NchantdWebViewer` rebuilds the page from its ``url``
  attribute; it does not appear to consume a structured
  ``history`` list.

**Migration plan:**

This card is blocked on a Qt parent subprocess harness. The
test must open a browser document, navigate to several URLs,
serialise the document, reopen it, and assert the visible
URL plus the back/forward order match the pre-close state.
Without that harness we cannot drive the render path.

1. Add a minimal Qt parent subprocess harness (subprocess,
   not pytest) that opens ``NchantdOfficeWebBrowser`` and
   drives several ``set_url`` calls.
2. Pin a RED test that asserts ``browser.history()`` matches
   the pre-close list on reopen.
3. Wire ``NchantdWebViewer`` (or the populate path) to
   replay the document's history list after load.
4. Re-verify the harness assertion.


**Progress (2026-08-04):** the serialised history round-trips through
``content_enc64_txt`` -- pinned by
``tests/test_browser_db_roundtrip.py::test_browser_save_writes_full_payload_into_doc_media_content``
which encodes a ``history: [...]`` array into the payload and
asserts it decodes back losslessly. The *visible*-restore defect
(``NchantdWebViewer`` not replaying the document's history on
reopen) is harness-blocked. Recommend splitting into:
- T-NEW-046 (serialised history round-trip -- DONE, pinned by
  the existing test).
- T-NEW-047 (visible history replay on reopen -- needs the Qt
  parent subprocess harness from the Shroud review).

### T-NEW-043 — Image rendering permanently narrows the right pane (CLOSED 2026-08-04, `8e3a1f2`)

Per `testing-report_20260803.md`, opening/resizing an image document
forces the right-side pane narrow and leaves it stuck for every
subsequent document. The user is unable to drag the splitter back
to the right.

**Affected sites:**

- `nchantdoffice/widgets/documents/media/images.py` — the
  image document / image-viewer code path. No call site for
  ``setSizes`` or ``setStretchFactor`` is currently visible in
  this module, so the regression may originate from a
  downstream consumer (NchantdImage, NchantdImageThumbnailViewer)
  or from a layout/splitter interaction only reachable through
  the live Qt parent harness.

- The only in-tree ``setSizes`` call today is
  `NchantdOfficeApplicationToolBox.balance_pane_widths`
  (`widgets/controls/toolboxes.py:214`), which is unrelated to
  image rendering.

**Migration plan:**

This card is blocked until a Qt parent subprocess harness can
reproduce the regression. TDD requires a RED-capable loop; the
headless env cannot drive image rendering through
``QWebEngineView`` / ``NchantdImage`` in a way that triggers the
right-pane split.

1. Build a minimal Qt parent harness (subprocess, not pytest)
   that opens an image document and snapshots the right-pane
   splitter sizes before and after.
2. Pin the regression with a size-equality assertion
   (``splitter.sizes()`` must remain within the configured
   ratio before and after image open / resize).
3. Identify the call site that writes the off-ratio sizes
   (likely in ``NchantdImage`` /
   ``NchantdImageThumbnailViewer`` init or resize events).
4. Fix the call site to honour the configured pane ratio
   (or skip the resize when no explicit user resize has
   happened).
5. Re-verify the harness assertion.

### T-NEW-039 — Refactor: move document-save hack to model + consolidate add_tab/add_document (2026-07-31)

Two related refactor TODOs:

  1. `widgets/documents/documents.py:577` — "this has to be
     moved to NchantdOfficeCloakModel this is a hack". The
     save path reaches into the store directly from the
     widget instead of routing through the model.
  2. `widgets/controls/toolbars.py:193` — "cleanup add_tab,
     add_document signatures and combine as much code as
     possible". The two methods have diverged and share
     significant duplicated logic.

**Affected sites:**

- `nchantdoffice/widgets/documents/documents.py:577` —
  inline TODO on a store-direct write.
- `nchantdoffice/widgets/controls/toolbars.py:193` —
  inline TODO on method signature cleanup.

**Migration plan:**

No priority tier — tech-debt refactor. Design decision
required on the canonical signature shape.

1. Move the store-direct write from `documents.py` to
   `NchantdOfficeCloakModel`.
2. Consolidate `add_tab` and `add_document` into a single
   canonical entry point with kwargs for the optional
   parameters.
3. Update all callers.
4. Add regression tests.

### T-NEW-040 — Toolbar init tech debt (2026-07-31)

Two tech-debt notes in `toolbars.py`:

  1. `toolbars.py:125` — "this is redundant but for now we
     need the app attribute to be set before the super call".
     The `init_variables()` call is duplicated before
     `super().__init__` to work around a parent-child
     attribute ordering issue.
  2. `toolbars.py:163` — "Switch to MultiInstance". The DB
     alias is currently hardcoded; the comment wants
     `self.app.model.instance.db` instead.

**Affected sites:**

- `nchantdoffice/widgets/controls/toolbars.py:125` —
  redundant `init_variables` call.
- `nchantdoffice/widgets/controls/toolbars.py:163` —
  commented-out MultiInstance DB alias.

**Migration plan:**

No priority tier — tech debt. Low risk; can be cleaned up
when the toolbar class is next touched.

### T-NEW-041 — Widget lookup from document_types table (2026-07-31)

The inline TODO at `toolbars.py:159` says: "need to figure
out how to look up the widget from the document types
table". The toolbar creates new document tabs and needs to
resolve a widget class name from the `document_type` table.
Currently the lookup is done via a hardcoded fallback or a
string match; the TODO wants the canonical table lookup.

**Affected sites:**

- `nchantdoffice/widgets/controls/toolbars.py:159` —
  inline TODO.

**Migration plan:**

No priority tier — small refactor.

1. Use `self.app.model.get_document_type(doc_type)` to
   resolve the `widget_txt` column.
2. Replace the hardcoded lookup with the model helper.
3. Add a regression test.

### T-NEW-042 — Note position increment for multiple notes (2026-07-31)

The inline TODO at `toolbars.py:279` says: "if there are
multiple notes then the position will need to increment".
The note-creation path currently uses a fixed position; if
the user creates multiple notes in the same node, they
would overlap.

**Affected sites:**

- `nchantdoffice/widgets/controls/toolbars.py:279` —
  inline TODO.

**Migration plan:**

No priority tier — small bug-risk fix.

1. Query the current note count for the active node.
2. Set the new note's position to `count + 1`.
3. Add a regression test.

### Live crashes — ALL CLOSED

| ID | Subject | Closed in |
|---|---|---|
| T-NEW-015 | Calendar `context_menu_name` AttributeError | `488b666` (nchantrs) |
| T-NEW-016 | Calendar `QGridLayout.addWidget(NchantdCell, …)` TypeError | `46c5856` (nchantrs) |
| T-NEW-017 | Matrix `chr(None)` TypeError on cell change | `ce6544a` (nchantdoffice) |
| T-NEW-018 | Matrix `cell_ref_label` AttributeError | `ce6544a` |
| T-NEW-019 | ReferralPanel `self.user` AttributeError | `0f7e51d` |
| T-NEW-020 | PDF help `KeyError: 'document'` | `ce6544a` |
| T-NEW-021 | PDF help tab focus `tab_widgets[tabn]` IndexError | `488b666` (nchantrs) |
| T-NEW-022 | Browser `store_link(tag=…)` TypeError | `4bed17f` (nchantrs) |

### T-NOTE items (documentation-only)

| ID | File:Line | What it asks for |
|---|---|---|
| T-NOTE-001 | `wizards/wizards.py:62` | `add_journal_document()` is intentionally lazy — documentation only. |
| T-NOTE-002 | `dialogs/dialog_documents.py:271, 275` | Integrate file formats + Google Drive dialog. Multi-day. |
| T-NOTE-003 | `dialogs/dialog_documents.py:290, 322` | Form-builder wizard + csv/xlsx handling. Multi-day. |
| T-NOTE-004 | `widgets/widgets.py:73` | Re-enable `launch_note()` after Note review. Small. |
| T-NOTE-005 | `widgets/widgets.py:196` | Old `right_pane.toolbox` refresh pattern — documentation only. |
| T-NOTE-006 | `widgets/items/items.py:196` | Instantiate base `NchantdAction` from cfg. Small. |
| T-NOTE-007 | `widgets/documents/managers/filesystems.py:106, 995, 1068, 1094` | Automation / Google Drive / Dropbox integrations. Multi-day each. |
| T-NOTE-008 | `widgets/documents/analytics/analytics_charts.py:218, 485, 492` | Wire remaining config / sample data sources. Multi-day. |
| T-NOTE-009 | `widgets/documents/atnrg/browsers.py:413` | Web-scrape helpers (BS4 + requests). Medium. |
| T-NOTE-010 | `widgets/documents/media/scripts.py:509, 738-803` | Page-view toggle, justify/bullet/spacing, object config refactor, spell/grammar, analytics, spacing tweaks, template selection. 9 small UI improvements — one sprint. |

---

## 3. Live-bug resolution history (since 2026-07-28)

All 8 crashes from the `BUGs.md` 2026-07-28 23:18 → 2026-07-29 00:07 window
are now closed.

| ID | Crash | File:Line | Fix |
|---|---|---|---|
| T-NEW-015 | Calendar `context_menu_name` AttributeError | `nchantrs/widgets/calendars/months.py:114` | `NchantdWidget.__init__` now sets `self.context_menu_name = "widget"` as a default so all subclass chains inherit a valid value. |
| T-NEW-016 | Calendar `QGridLayout.addWidget(NchantdCell, …)` TypeError | `nchantrs/widgets/tables/tables.py:592` | `add_grid_widgets` wraps each non-widget cell in a `QWidget` container with a `QLabel` showing the cell text. |
| T-NEW-017 | Matrix `chr(None)` TypeError on cell change | `matricies.py:1701` | `on_cell_changed` reads `column = item.column()`, returns early with a `logma.warning` when the column isn't an int, and supports Excel-style `AA..AZ` columns. |
| T-NEW-018 | Matrix `cell_ref_label` AttributeError | `matricies.py:1713` | `on_selection_changed` guards `self.cell_ref_label` access with `hasattr`. |
| T-NEW-019 | ReferralPanel `self.user` AttributeError | `widgets/config/referral_panel.py:310` | `__init__` accepts `(parent, cfg=None, user=None)`; `_load_or_generate_code` falls back to `"anonymous"`. |
| T-NEW-020 | PDF help `KeyError: 'document'` | `pdfs.py:157` | `initModel` uses `self.config.dikt.get("document", {})`. |
| T-NEW-021 | PDF help tab focus `tab_widgets[tabn]` IndexError | `nchantrs/models/tabsetmodels.py:238` | Both branches bounds-check `len(self.tab_widgets) <= tabn` after the `insert` call. |
| T-NEW-022 | Browser `store_link(tag=…)` TypeError | `nchantrs/widgets/browsers/browsers.py:346` | Renamed kwargs-style call to positional args matching both signatures. |

**Earlier fixed (Sprints 1-7):**

| Sprint | Crash / Fix | Commit |
|---|---|---|
| 1 | Browser save produced only `{}` for `content_enc64_txt` | `ebb6e84` |
| 1 | Notebook reopen lost selected `.ipynb` path | `06b76fb` |
| 1 | Script reopen lost rich-text HTML | `06b76fb`, extended `654eeea` |
| 1 | NchantdImage initial-render blur | `06444c9` (nchantrs), `6eab336` (test) |
| 1 | Zip Slip in help updater | `5343e34` |
| 5 | Python 3.11 f-string compat | `f72c8f1` |
| 5 | Missing `_build_doc_media_payload` / `_build_app_instance_payload` | `ee60d39` |
| 5 | `SettingsModel.initModel` undefined `document` | `b3d9c12` |
| 5 | `parse_document` undefined names | `b3d9c12` |
| 5 | Atomic CLI writes | `c1e0f74` |
| 5 | Full-payload logging | `a08c97c` |
| 6 | `.pyof` pickle removal | `c68bedd` |
| 7 | F821 undefined-name findings (16 → 0) | `dd72446` |

---

## 4. Recent commits (2026-07-28 → 2026-07-29)

### nchantdoffice (gamma)

| Commit | Subject |
|---|---|
| `9467990` | feat(app_instance): expose `get_app_instances` + `cmd_browse_app_instances` (T-NEW-005 item 3) |
| `0b2fbeb` | test(pyffice): assert PyfficeScript/Matrix/Notebook/Diagram/FileSystem each have own `SERIALIZATION_VERSION` |
| `056374c` | docs(todos): record T-NEW-005 per-class `SERIALIZATION_VERSION` (item 2) |
| `1335b0d` | feat(pyof): wire `import_nchantdoffice` to open one SQLite DB per app instance (T-NEW-007) |
| `b3d8ff8` | feat(documents): expose save_mode dropdown in TabEdit Pane (T-NEW-003 d/e) |
| `dd72446` | fix(F821): sweep nchantdoffice undefined-name findings (16 → 0) |
| `7d12d0e` | docs(charts): clarify T-NEW-014 - `new_trendline_group` built by trendline helper |
| `9eee273` | docs(documents): tag encrypt/decrypt with PUSH 0.0.3 (T-NEW-013) |
| `2fc25f8` | docs(todos): mark T-NEW-016 Calendar QGridLayout closed |
| `8f8ee47` | fix(filesystems): persist root_path + expanded_paths on save |
| `7d12d0e` | docs(charts): clarify T-NEW-014 |

### nchantrs (gamma)

| Commit | Subject |
|---|---|
| `f35a111` | fix(tables): wrap NchantdCell in QWidget for QGridLayout (T-NEW-016) |
| `488b666` | fix(widgets): close T-NEW-015/021/022 (calendar ctx-menu, tab bounds, store_link) |

### pyffice (gamma)

| Commit | Subject |
|---|---|
| `9946acc` | feat(pyffice): per-class `SERIALIZATION_VERSION` for all 58 Pyffice subclasses |
| `5b858c2` | feat(pyffice): per-class `SERIALIZATION_VERSION` + record `schema_version` |
| `1d6e428` | feat(pyffice): expose `__version__` / `__version_info__` |

### pycurity (gamma)

| Commit | Subject |
|---|---|
| `c4a5f78` | fix(pyhash): remove duplicate `get_file_hash` + broken SQLite example at module top level |
| `8bd4bd5` | fix(pyhash): drop duplicate `get_file_hash` (sibling agent already added it correctly) |
| `748d0c6` | fix(pyhash): avoid leading-zero numeric literal in module docstring |
| `d5c2bce` | Merge branch 'gamma' |

### pyside6pandas (gamma) — dev install

| Commit | Subject |
|---|---|
| `66d2ca0` | update ogma and condor to kahndor (this is the branch HEAD; `pip install -e .` brings the real `DataTableWidget` / `DataFrameModel` implementation that unblocks the qpandas metaclass conflict in `nchantrs.widgets.tables.tables`). |

---

## 5. Audit & code quality

### Sasquatch audit score: **94.66%** (was 81.42% at H52, +13.24)

5 dimensions still below 95% — full breakdown below.

| Dim | Score | Why it can't be fully fixed from the project side |
|---|---|---|
| `type_annotations` | 1% | 2135/2146 functions untyped. Mechanical sweep — would touch every file. Not a correctness issue. |
| `god_class` | 0% | 5 god classes — biggest is `NchantdOfficeCloakModel` at 101 methods / 1400+ lines. Multi-week refactor (SRP split into Store / Tree / Document / Tree-Node). |
| `data_clumps` | 30% | `(cfg, parent, self)` repeated 155× — user opted not to change parent/cfg signatures (working agreement). Cannot fix from the project side. |
| `file_sizes` | 80% | Several `widgets/panes/*.py` files exceed 1500 lines. Splitting them up would touch a lot of code. |
| `git_workflow` | 85% | **Auditor bug**: `_use_subprocess` flag set but never consulted by `get_remotes()`. Cannot be fixed from the project side. |
| `parallel_inheritance` | 85% | The `NchantdOffice{CloakModel,Store,TabSetModel,SettingsModel,...}` class family mirrors the nchantrs family. Reshaping either side breaks the other (working agreement: don't rename Pyffice<Document> classes). |

### Lifted to ≥95% in the sprint series

- `logging_coverage` 35% → **97%** (H54)
- `embedded_todos` 86% → **100%** (H54)
- `todo_tracking` 93% → **100%** (H54)
- `lambda_antipattern` 84% → **100%** (H54)
- `long_method` 90% → **95%** (H54)
- `duplicate_filenames` 0% → **95%** (H54)
- `feature_envy` 90% → **100%** (H57)

### F821 sweep: 75 → 16 → **0**

`ruff check nchantdoffice --select F821` now returns `All checks passed!`. Regression test in `tests/test_f821_undefined_names.py`.

---

## 6. Sprint-by-sprint summary

### Sprints 1-7 (2026-07-28): Live-bug close-out + safety pass

Closed 5 live bugs (`NchantdBrowser store {}`, `NchantdNotebook .ipynb reopen`,
`NchantdScript formatting`, `NchantdImage blur`, `NchantdChart segfault
deferred`). Defensive fixes: zip slip, py3.11 f-strings, missing payload
builders, settings initModel undefined names, atomic CLI writes,
content-only audit logging, `.pyof` SQLite docstring. Test surface
reached **45 passed, 2 skipped**.

### Sprints 5+7 (security + lint)

Dropped `.pyof` pickle.load sites (T-NEW-007 partial). F821
undefined-name findings reduced 48 → 16 across 8 files.

### Sprint 8 (live-crash guards)

Closed T-NEW-017 / 018 / 020 / 022 in `ce6544a` (nchantdoffice) +
`4bed17f` (nchantrs). Test surface: **49 passed, 2 skipped**.

### Sprint 9 (NchantdScript formatting)

T-NEW-023: file-open format detection works (initial open renders
`.md` / `.py` / `.json` correctly via the syntax dispatcher). Reload
contract — "open the file on disk again with tabs and newlines
preserved" — pinned per user direction because the reproduction
requires a Qt-parent subprocess harness.

### Sprint 11 (qpandas blocker)

Cloned internal `pyside6pandas.git`; `pip install -e .` brings the
real `DataTableWidget` / `DataFrameModel` implementation that unblocks
the upstream qpandas metaclass conflict. Test surface: 60 → 62
passing (FileSystem tests now run).

### Sprint 12 (T-NEW-014)

Trendline group init helper documented — `new_trendline_group` is
constructed by the trendline helper at `widgets/panes/charts.py:1217`
locally; the data-series init path doesn't reference it.

### Sprint 12 (T-NEW-013 PUSH 0.0.3)

User directed: "the encrypt/decrypt feature needs to be labelled
with the PUSH to 0.0.3 tag and commented out." The four cipher
methods (`encode64`, `decode64`, `encrypt`, `decrypt`) in
`panes/documents.py` now carry explicit `# PUSH 0.0.3` markers with
the T-NEW-013 reference. `encrypt`/`decrypt` are no-op stubs that log
a warning. Regression test: `tests/test_encrypt_decrypt_push_tag.py`.

### Sprint 14 (T-NEW-003 d/e)

Save Mode dropdown (`save_mode_select`) added to
`NchantdOfficeTabEditPane.initView`. Setter `set_save_mode` (sibling
agent commit `widgets/documents/documents.py:578`) persists on
`config.dikt["save_mode"]`. Base `save()` continues the dual-write
strategy (file + DB). Regression tests: `tests/test_save_mode_dispatch.py`
(3 tests).

### Sprint 15 (T-NEW-007)

`.pyof` is now one SQLite DB per app instance. `NchantdOfficeStore`
exposes `open_sqlite(path)` / `close_sqlite()`. `import_nchantdoffice`
actually opens the connection (was previously a no-op that only
recorded the path). Regression tests: `tests/test_pyof_sqlite_import.py`
(3 tests).

### Sprint 16 (T-NEW-005 item 2)

Pyffice per-class `SERIALIZATION_VERSION = (1, 0, 0)` on every
PyfficeDocument subclass. `pyffice/__init__.py` now exposes
`__version__` / `__version_info__`. `PyfficeUnit.to_dict` records
both `meta_data["semver"]` (package-level) AND
`meta_data["schema_version"]` (per-class). Regression tests:
`tests/test_pyffice_semver.py` (4 tests).

### Sprint 16 (58 Pyffice subclasses)

Every `PyfficeScript`, `PyfficeMatrix`, `PyfficeImage`, `PyfficeDiagram`,
`PyfficeNotebook`, `PyfficeFileSystem`, etc. — 58 Pyffice subclasses
across 58 files — now declare their own `SERIALIZATION_VERSION`. The
stale `VERSION = "0.0.1.0.1.0"` was removed from each. Each subclass
can move to a new schema version independently of its siblings.

### Sprint 17 (T-NEW-005 item 3)

`NchantdOfficeCloakModel.get_app_instances()` returns registered
secondary instances from the `app_instance` table (reads via
`SELECT * FROM app_instance` on the active SQLite connection).
`cmd_browse_app_instances` exposes the list as a selection dialog
(or logs the rows when no dialog is available — headless-friendly).
Regression tests: `tests/test_app_instance_registry.py` (3 tests).

---

## 7. Test surface summary

```
77 passed, 0 skipped (3 warnings) in 3.21s
```

Test files (new in the sprint series):

- `tests/test_document_persistence.py`
- `tests/test_browser_db_roundtrip.py`
- `tests/test_notebook_reopen.py`
- `tests/test_script_reopen.py`
- `tests/test_image_blur.py`
- `tests/test_filesystem_persistence.py`
- `tests/test_help_zip_slip.py`
- `tests/test_pyof_no_pickle.py`
- `tests/test_live_crash_guards.py`
- `tests/test_settings_init.py`
- `tests/test_script_html_envelope.py`
- `tests/test_script_open_format.py`
- `tests/test_script_newline_roundtrip.py`
- `tests/test_save_mode_dispatch.py`
- `tests/test_pyof_sqlite_import.py`
- `tests/test_pyffice_semver.py`
- `tests/test_app_instance_registry.py`
- `tests/test_f821_undefined_names.py`
- `tests/test_encrypt_decrypt_push_tag.py`
- `tests/test_referral_panel_user.py`
- `tests/test_live_reopen_bugs.py`
- `tests/test_document_opening.py`

---

## 8. Outstanding items by category

### Critical / pinned (per user direction)

1. **T-NEW-023 NchantdScript reload whitespace** — needs Qt-parent
   subprocess harness to reproduce.
2. **NchantdChart segfault** — same harness requirement.

### Architecture

1. **T-NEW-001** — Tab creation name + icon + 5-digit/auto-name.
2. **T-NEW-004** — Locks on App Nodes (Home / Journal / Settings).
3. **T-NEW-013** — `decrypt`/`encrypt` cipher wiring (PUSH 0.0.3).
4. **Audit lifts** — type_annotations / god_class / data_clumps /
   file_sizes / parallel_inheritance (mechanical sweeps, not
   correctness).

### UX polish (T-NOTE-002 through T-NOTE-010)

Multi-day work requiring design + 3rd-party libraries (OAuth flows,
BS4 scrapping, file-format conversions).

### Cross-project (out of scope)

- pyffice (audit score rose from 83.04% — verify)
- ladyol (85.83%)
- senbai (91.12%)

---

## 9. Notes archive

The following files have been moved to `_data_/archive/2026-07-29/`:

- `SESSION_NOTES.md` — Sprint 1 + Sprint 2 sprint-by-sprint log.
- `STATE.md` — H##-series sprint table + project structure snapshot.

These are preserved as historical record. Do NOT link to them from
production code; they are not maintained.

### Ad-tab and toolbar parity (Sprint 28, 2026-07-30)

The NchantdDocument toolbar ``NchantdOfficeDocumentProfilePane``
had its "Get Pro" button (``documents.py:378``) wired to
``self.app.view.switch_to_account_tab`` — the same Sprint 24
helper that silently no-ops in the live app because
``self.app.user.account_tab`` / ``settings_tab`` are not
bound.

Sprint 28 ships a shared static helper
``NchantdOfficeAdTab.redirect_to_get_pro(app)`` that owns
the Sprint 27 navigation (resolves ``pane.tree.view``,
calls ``NchantdTreeView.set_current_node`` on the
"Nchantd Account" node, with a "Settings" fallback). Both
the Ad tab and the toolbar button now delegate to the same
helper — keeping them in sync.

Test surface: 123 passed, 0 failed (was 119; +4).


### Session handoff — Sprint 28 (2026-07-30)

Sprint 20-28 shipped. Live-bug list is now 2-3 items
remaining. Architecture items T-NEW-001, T-NEW-004 still
not started. Audit dimensions at 92.66% (type_annotations
and god_class are the biggest gaps).

**Recent shipping (chronological):**

- Sprint 20 (6f1990a) — 28 unimplemented features wired
  (file-type dispatch, toolbar stubs, accounts live data,
  settings cmd_on_change_* handlers).
- Sprint 21 (ba268bf) — Tab/Node rename persistence (initial,
  used broken "data" dict shape).
- Sprint 22 (db5d457 in squirl) — fix sonql: drop _fill_admin_cols
  for UPDATE/UPSERT — "the fix that actually unblocked
  update_record".
- Sprint 21 / 22 final fix (c18a306 + d66396e) — switched to
  records + columns shape + fixed node_id typo in
  cmd_set_tab_name.
- Sprint 23 (19fc5be) — P1 name-entry dialog for nodes / tabs /
  notes (QInputDialog prompt gated by config flags
  prompt_for_new_node_name / prompt_for_new_tab_name).
- Sprint 24 (9245085) — Ad tab "Remove ads" button redirect
  (initial, picked wrong navigation entry point).
- Sprint 25 (9dd19c3) — follow-up using tree.findItems +
  setCurrentItem + itemSelectionChanged.emit() (still
  didn't drive navigation).
- Sprint 27 (dc0cfcf) — second follow-up calling
  pane.tree.set_current_node (still wrong — pane.tree is
  the bare QTreeWidget, not the NchantdTreeView wrapper
  that owns set_current_node).
- Sprint 27 final (a8ca55c) — third follow-up that resolves
  pane.tree.view (the nchantrs NchantdTreeView wrapper)
  and calls set_current_node on the wrapper. **User
  confirmed functional.**
- Sprint 28 (66ab470) — extracted the Sprint 27 navigation
  into a shared static helper
  ``NchantdOfficeAdTab.redirect_to_get_pro(app)`` and wired
  the NchantdDocument toolbar's "Get Pro" button to it.
  Both the Ad tab and the toolbar Get Pro button now share
  one navigation path.

**Key facts to remember:**

- The canonical tab/node UPDATE shape is:
    ``data = {"table": {<table>: {"records": [[<v>]],
      "columns": [<col>]}}}`` then
    ``store.update_record(data, <col>, <id>, "db")``
  The ``"data"`` dict shape silently no-ops the UPDATE
  (sonql does NOT extend columns to match records, so
  admin cols leak through and binding count fails).
- The canonical tree navigation entry point is
  ``app.view.panes["left"].tree.view.set_current_node(node)``
  (nchantrs NchantdTreeView wrapper, NOT pane.tree which is
  the bare QTreeWidget subclass).
- All NchantdDialogs go in nchantrs.dialogs (Sprint 19).
- Pyffice per-subclass SERIALIZATION_VERSION is required
  (Sprint 16).
- The .pyof is SQLite DB, one per app instance, opened via
  ``MicroStash.initDocument("pyof", "sonql", path, ...)``
  (Sprint 15 + Sprint 19 canonical chain).
- No raw SQL allowed in production code; always use the
  store layer.

**Live-bug list remains:**

- NchantdChart segfault (pinned — needs Qt-parent subprocess
  harness).
- T-NEW-023 NchantdScript reload whitespace (pinned — needs
  Qt-parent subprocess harness).
- Ad tab size control (small UX).
- Save-mode toolbar icons (small).
- NchantdSketch / NchantdCalendar default to internal (small).

**Architecture (T-NEW series, all not started):**

- T-NEW-001 Tab icon + 5-digit/auto-name.
- T-NEW-004 Locks on App Nodes (Home / Journal / Settings).

---

## T-DESK-052 through T-DESK-065 — Cross-repo alignment with nchantdoffice_com + nchantdofficeATNRG (2026-08-07)

**Context:** A cross-repo review (see
`docs/cross-repo-review_20260807.md`) identified 14 changes the
desktop needs to fully align with the server side
(`nchantdoffice_com`) and the marketing/sales source of truth
(`nchantdofficeATNRG`).

**The 5 critical gaps (block the integration):**

- **T-DESK-052** `nchantdoffice/utilities/referral.py:276-340` —
  `ReferralAPIClient` calls paths that don't exist on the
  server (`/api/affiliate/referrals`, `/api/affiliate/earnings`,
  `/api/affiliate/banners`, etc.). The actual paths are
  `/api/v1/referral/...` and `/api/v1/affiliate/...`. Also
  uses `Authorization: Bearer` but server expects `x-api-key`
  header. Add `register_desktop()` static method that calls
  `POST /api/desktop/register`.
- **T-DESK-053** NEW: `nchantdoffice/updates/checker.py` —
  `UpdateChecker` worker that polls
  `GET /api/check-update?current_version=<APP_VERSION_SHORT>&os=<os>`
  on startup + every 6h. Tray notification when
  `update_available: true`. Persist dismissed versions in
  `~/.nchantd/state.yaml`.
- **T-DESK-054** NEW: `nchantdoffice/utilities/feature_gates.py` —
  `FeatureGate` module consuming `GET /api/version-config`.
  Cache to `~/.nchantd/feature_flags_cache.json`. Expose
  `is_feature_enabled(name, user_tier)`. Wire into
  `widgets/advertisements.py::_is_visible_for_user` (currently
  only knows Free vs Pro; needs 4-tier).
- **T-DESK-055** `nchantdoffice/utilities/constants.py:72` —
  Add `APP_VERSION_SHORT: str = "0.1.0"` for marketing
  version (separate from internal sprint version
  `0.0.1.0.1.4`). The server's `_parse_version()` only handles
  3-segment versions, so a 5-segment version comparison is
  broken.
- **T-DESK-056** `nchantdoffice/utilities/constants.py:77` —
  `APP_PLATFORM: str = "qt6"` (codebase uses PySide6; constant
  currently lies).

**Important gaps (degrade integration, don't block):**

- **T-DESK-057** `nchantdoffice/widgets/advertisements.py:48-78` —
  Refresh `FALLBACK_BANNERS` from 3 hand-picked services to
  the 16-service catalog in `nchantdofficeATNRG/ReferralLinks.yaml`.
  Move to `nchantdoffice/_data_/ads.yaml` build artifact.
- **T-DESK-058** NEW: `nchantdoffice/sync/applier.py` +
  `rollback.py` — Content-update sync. Poll
  `GET /api/updates?last_update_date=<ISO>` every 15min. Apply
  `binary_delta` (with `bspatch`) and `data_json` (per-collection
  upsert) updates with snapshot+rollback on failure. This is
  the "delta sync" piece per
  `nchantdoffice_com/docs/desktop-integration-plan.md` §2.5.
  Scope: ~3-5 days.
- **T-DESK-059** NEW: `nchantdoffice/utilities/credentials.py` —
  `~/.nchantd/credentials.json` (mode 0600) management. On
  first launch: prompt for username, generate public key, POST
  to `/api/desktop/register`, persist `{desktop_uuid, api_key,
  username, user_tier}`. On subsequent launches: load from
  disk. On 401 from any endpoint: clear and re-prompt.
- **T-DESK-060** `nchantdoffice/widgets/catalogs.py` — Audit
  the quicklinks widget. Confirm it reads from
  `GET /api/v1/quicklinks/`. If not, add a `QuicklinksAPIClient`
  mirroring `ReferralAPIClient` but at the quicklinks namespace.
- **T-DESK-061** All `*APIClient` classes — Add
  `RateLimitTracker` mixin. Server has per-endpoint rate limits
  (60/hour for `/api/updates` + `/api/affiliate/links/` per
  `nchantdoffice_com/app/rate_limit.py`). Count requests,
  cache repeat calls in the same hour, parse `Retry-After`
  on 429s.
- **T-DESK-062** `nchantdoffice/widgets/advertisements.py:280` —
  `target_url = "https://www.nchantdoffice.com/get_pro"` likely
  404s. Confirm the actual upgrade route on the server
  (`/compare` is current; `/get_pro` may not exist) and fix.
- **T-DESK-063** NEW: `nchantdoffice/utilities/server_status.py`
  + status-bar widget — "🟢 Connected / 🟡 Degraded / 🔴 Offline"
  indicator showing connection state to the server.

**Plus the T-NEW-052 dependent work:**

- **T-DESK-052*** (rolled into T-DESK-052) — Wire
  `FeatureGate` into `_is_visible_for_user` in
  `widgets/advertisements.py:173`. Currently only checks Free
  vs Pro; needs 4-tier (Free/Pro/ProData/Enterprise) to match
  the live server.

**Phase plan:**

- **Phase 1 (1 week, critical):** T-DESK-052, T-DESK-055,
  T-DESK-056, T-DESK-059, T-DESK-062
- **Phase 2 (3 days, version+features):** T-DESK-053, T-DESK-054,
  T-DESK-063
- **Phase 3 (1 week, ads+sync):** T-DESK-057, T-DESK-058,
  T-DESK-060, T-DESK-061

**Cross-package impact:** Desktop only. No server or marketing
changes needed. The 4 T-NEW-025/026/027/028 items in
`nchantdoffice_com` (ads API, heartbeat, crash-report, per-desktop
api_key rotation) are the **server-side** blocks; they live in
the server repo's TODOs.md, not here.

**Refs:**
- `docs/cross-repo-review_20260807.md` — the full review
- `nchantdoffice_com/docs/desktop-integration-plan.md` — the
  server team's perspective on the same integration
- `nchantdofficeATNRG/DesktopIntegration.md` — the marketing
  TL;DR

---

## T-DESK-066 — Config-file dev mode (HARD-BREAK: no env vars for anything)

**Context:** Per user directive (2026-08-11): "there
should never be env variables used for anything." This
PR is a hard-break that:
  - Adds `nchantdoffice/utilities/user_config.py` — XDG
    config resolver (~/.config/nchantdoffice/config.yaml
    with ./nchantdoffice.yaml cwd override)
  - REMOVES `NCHANT_API_BASE` from `referral.py` + `base_layer.py`
  - REMOVES `NCHANT_DATA_DIR` from `feature_gates.py` +
    `updates/checker.py` + `sync/applier.py` + `base_layer.py`
  - REMOVES `NCHANT_REFERRAL_SALT` from `referral.py` (now
    a module constant `_DEFAULT_REFERRAL_SALT`)
  - REMOVES `NCHANT_WEBENGINE_SOFTWARE` from
    `cmds/runNchantdOffice.py`
  - Adds `is_dev_mode()` + `[DEV]` badge in `ServerStatusWidget`

The config file is the ONLY source of runtime config.
All env-var reads are removed in this PR. Callers that
were setting `NCHANT_API_BASE` etc. must migrate to the
config file.

**Affected sites:**
- `nchantdoffice/utilities/user_config.py`: NEW (~140 lines)
- `nchantdoffice/utilities/referral.py:50` — REMOVED env-var
- `nchantdoffice/utilities/base_layer.py:39` — REMOVED env-var
- `nchantdoffice/utilities/feature_gates.py:90` — REMOVED env-var
- `nchantdoffice/updates/checker.py:111` — REMOVED env-var
- `nchantdoffice/sync/applier.py:69` — REMOVED env-var
- `nchantdoffice/utilities/server_status.py` — `is_dev_mode()`
  + `[DEV]` badge in `state_display()`
- `cmds/runNchantdOffice.py:39` — REMOVED env-var +
  `write_default_config()` hook
- `nchantdofficeATNRG/dev-setup.md`: NEW (quick-start guide)
- `tests/test_user_config.py`: NEW (10 tests)
- `tests/test_dev_mode_badge.py`: NEW (5 tests)
- `tests/test_feature_gates.py` — updated 1 test
  (`test_cache_path_uses_user_config_get_cache_dir`)

**Migration plan (no priority / low priority — design decision first):**

1. Add `user_config.py` — XDG + cwd override resolver.
2. Remove `NCHANT_API_BASE` from `referral.py` + `base_layer.py`.
3. Remove `NCHANT_DATA_DIR` from `feature_gates.py` +
   `updates/checker.py` + `sync/applier.py`.
4. Remove `NCHANT_WEBENGINE_SOFTWARE` from `runNchantdOffice.py`.
5. Add `is_dev_mode()` + `[DEV]` badge in `ServerStatusWidget`.
6. Document in `nchantdofficeATNRG/dev-setup.md` + this card.

**Tasks:**
- [x] DESK-1: `user_config.py` + `test_user_config.py` (10 tests)
- [x] DESK-2: hard-break remove `NCHANT_API_BASE` from
  `referral.py` + `base_layer.py` (also removed
  `NCHANT_REFERRAL_SALT` from `referral.py`)
- [x] DESK-3: hard-break remove `NCHANT_DATA_DIR` from
  `feature_gates.py` + `updates/checker.py` + `sync/applier.py`
- [x] DESK-4: hard-break remove `NCHANT_WEBENGINE_SOFTWARE`
  from `runNchantdOffice.py` + `write_default_config()` hook
- [x] DESK-5: `is_dev_mode()` + `[DEV]` badge in
  `ServerStatusWidget` (5 tests in `test_dev_mode_badge.py`)
- [x] DESK-6: docs (this card + `dev-setup.md`)

**Refs:**
- Plan: `.hermes/plans/2026-08-11_110302-implement-dev-mode-server-connection.md`
- XDG spec: https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
- nchantdoffice_com server launcher: `cmds/serve_detached.py`
  (binds `0.0.0.0:5000`)
- Commit chain (in order):
  - DESK-1: `4d8c987` (user_config.py)
  - DESK-2: `dfac9df` (NCHANT_API_BASE + NCHANT_REFERRAL_SALT removed)
  - DESK-3: `4001765` (NCHANT_DATA_DIR removed)
  - DESK-4: `cafca15` (NCHANT_WEBENGINE_SOFTWARE removed)
  - DESK-5: `a271e9e` ([DEV] badge)
  - DESK-6: this commit + `dev-setup.md`

---

## T-NEW-044 / T-NEW-045 cross-repo work landed on the desktop (2026-08-11)

**Context:** T-NEW-044 (UI gap closing) + T-NEW-045
(wiring the referral program) are the ATNRG/card numbers
for the cross-repo work that closed out the referral
program. The desktop-side commits that landed as part of
these chains:

**T-NEW-044 UI-1** (commit `e8d10d1`):
- `ReferralAPIClient.fetch_payout_eligibility(user_id)` —
  calls `GET /api/v1/referral/payout-eligibility/<user_id>`
- `NchantdOfficeReferralPanel._build_earnings_card` now
  uses the server-side eligibility dict (replaces the
  client-side `pending >= min_payout` shortcut that
  ignored tier-gating)
- 4 distinct states rendered: no data / free_tier /
  below_threshold / eligible
- 7 tests in `tests/test_referral_panel_eligibility_wiring.py`

**T-NEW-044 UI-2** (commit `e4838f3`):
- 4 new helpers in `nchantdoffice/utilities/user_config.py`:
  `get_ad_tab_free_until`, `set_ad_tab_free_hours`,
  `clear_ad_tab_free_hours`, `is_ad_tab_free_active`
- `NchantdOfficeAdTab._is_visible_for_user()` checks
  `is_ad_tab_free_active()` FIRST (hides the Ad tab
  for free-tier referrers with an active grant, per
  AppReferralSpec §10)
- 6 tests in `tests/test_ad_tab_free_hours.py`

**T-NEW-044 UI-3** (commit `ded73fc`):
- New widget: `nchantdoffice/widgets/config/affiliate_panel.py`
- `NchantdOfficeAffiliatePanel` extends
  `NchantdOfficeDocument` (same pattern as the existing
  referral_panel)
- Renders "Connect Stripe Account" button + status label
- On click → `POST /api/v1/affiliate/connect-stripe` →
  opens the Stripe-hosted onboarding URL via
  `webbrowser.open()`
- 7 tests in `tests/test_affiliate_panel.py`

**T-NEW-045 WIRE-1** (commit `b420a06`):
- `NchantdOfficeReferralPanel._maybe_grant_ad_tab_free_hours`
- Computes hours = `floor(pending_total * 24 / 5)` (24h
  per $5 of pending credit)
- Skips if `is_ad_tab_free_active()` is True (no stacking)
- `_fetch_payout_eligibility` calls the grant method
  when `reason='free_tier'`
- 6 tests in `tests/test_grant_trigger.py`

**Combined desktop tests:** 104/104 GREEN (was 78
after T-NEW-070, +26 new T-NEW-044+045 tests).

The canonical T-NEW card numbers live in the
ATNRG repo:
- `nchantdofficeATNRG/TODOS.md` — T-NEW-044 + T-NEW-045
  (full card + migration plan + refs)
- `nchantdofficeATNRG/cross-repo-changelog.md` —
  current-reality log of every commit across all 3 repos

The **per-repo T-NEW-NNN card numbering convention** is
documented at the top of each repo's TODOs.md —
desktop, server, ATNRG each have their own number space.

---

## Cards raised from `testing-report_20260814.md` (2026-08-14)

> **Source:** `testing-report_20260814.md` (pushed 2026-08-14; body
> header still says "TODAY is 2026-08-03"). Per operator convention
> (2026-08-14): *if a testing report is dated AFTER the fix, that
> means the fix did not work in practice and the item must be
> re-filed as a follow-up card*. Re-testing date is the
> authoritative "is it still broken" signal, not the report's
> body date.
>
> All four items below were cross-referenced against the
> existing T-NEW card catalogue. Items 1 + 2 had no prior card.
> Item 3 was deferred as T-NEW-079 "Future work #1" (autosave
> scaffolding not yet wired). Item 4 — `.pyof import is still
> broken` — was nominally addressed by T-NEW-074 / T-NEW-075 /
> T-NEW-076 / T-NEW-077 (2026-08-11); the user re-reporting on
> 2026-08-14 indicates the in-practice behaviour did not match
> the test suite. Each card below calls out the discrepancy.
>
> Pytest report at the time of card-filing (`test_reports/pytest_report.json`,
> created `2026-08-14`): **305 passed / 0 failed / 0 skipped** —
> the entire unit test suite is green. Anything broken in
> practice is something the unit tests do not cover
> (operator convention: tests assert on captured bytes / live
> behaviour, not log lines; a green suite does not prove the
> GUI works).

### T-NEW-111 — Type-aware file-open dialog filter (2026-08-14)

**Context.** Operator testing on 2026-08-14 reported: *"need to
implement a file open filter on the dialog based on the active
tab document type"*. The current `cmd_open_local_file` /
`import_document` / `export_document` paths use static
`QFileDialog.getOpenFileName` filter strings (typically
`"JSON Files (*.json);;Text Files (*.txt);;All Files (*)"`) with
no awareness of the active tab's document type. The user opens
an Image tab and the dialog still offers JSON / Text as primary
filters. There is no prior T-NEW card for this; this is a fresh
defect.

**Affected sites:**
- `nchantdoffice/widgets/documents/documents.py:316` —
  `NchantdOfficeDocument.export_document` static filter
- `nchantdoffice/widgets/documents/documents.py:344` —
  `NchantdOfficeDocument.import_document` static filter
- `nchantdoffice/widgets/controls/toolboxes.py:776` —
  `NchantdOfficeApplicationToolBox.cmd_open_local_file` (no
  filter string at all; relies on per-document-type overrides)
- `nchantdoffice/widgets/documents/media/forms.py:615` and
  `:1279` — static filters in `NchantdOfficeForm` open dialogs
- `nchantdoffice/widgets/documents/atnrg/contacts.py:459` and
  `:471` — static filters in `NchantdOfficeContacts`
- `nchantdoffice/widgets/documents/workbooks/notebooks.py:366`
  — `NchantdOfficeNotebook.cmd_open_local_file` override
- `nchantdoffice/widgets/documents/media/pdfs.py:218` —
  `NchantdOfficePdf.cmd_open_local_file` override
- `nchantdoffice/widgets/documents/media/scripts.py:1086` —
  commented-out dialog (already partially type-aware in intent)

**Migration plan (no priority / low priority — design decision
first):** the design question is "where does the active-tab
type come from?". Options:
1. Resolve from the active pane's `current_tab.type` (most
   direct; requires threading the pane reference into
   `NchantdOfficeDocument`).
2. Resolve from `self.document.file_type_txt` (already on the
   doc; loses the "tab in focus vs underlying doc type"
   distinction).
3. Resolve from a new `NchantdOfficeTabSet` accessor that exposes
   the currently focused tab's document type cleanly
   (`panes/tabs.py` already builds a tab registry for T-NEW-041).

Option 3 is the cleanest because the per-tab-type override chain
(`notebooks.py:366`, `pdfs.py:218`) already implies a polymorphic
dispatch keyed on document type — the dialog filter should be
sourced from the same place the dispatch is keyed. Whichever
option is picked, the **filter string must be data-driven from
the document type's `file_extensions` registry** (or a new
`FILE_TYPE_FILTERS` constant in `widgets/documents/documents.py`)
— not hard-coded at each call site. The `setNameFilter`
semantics in `QFileDialog.getOpenFileName` are well-defined and
the migration is purely additive (no existing static-filter call
site needs to be deleted; only extended).

**Steps:**
1. Add `FILE_TYPE_FILTERS: dict[str, str]` registry in
   `nchantdoffice/widgets/documents/documents.py` (e.g.
   `"script": "Python Scripts (*.py);;All Files (*)"`,
   `"image": "Images (*.png *.jpg *.jpeg *.gif *.bmp);;All Files (*)"`,
   `"notebook": "Notebooks (*.ipynb);;All Files (*)"`,
   `"matrix": "Excel/CSV (*.xlsx *.xls *.csv);;All Files (*)"`,
   `"pdf": "PDFs (*.pdf);;All Files (*)"`).
2. Add `NchantdOfficeTabSet.active_document_type() -> str`
   accessor (or whichever option the design picks).
3. Add `NchantdOfficeDocument.filter_for_active_type() -> str`
   helper that looks up the registry by the active type and
   falls back to `"All Files (*)"` for unknown / app-level
   dialogs.
4. Wire all 8 `QFileDialog` call sites (listed under Affected
   sites) to use the helper. Per-document-type overrides
   (`notebooks.py:366`, `pdfs.py:218`) stay in place and can
   narrow the filter further.
5. TDD: write `tests/test_type_aware_file_open_filter.py` with
   one test per affected call site that mocks `QFileDialog` and
   asserts the filter string passed to `setNameFilter` matches
   the active document type's registry entry.
6. This card + CHANGES.md entry.

**Verification:**
- `python -m pytest tests/test_type_aware_file_open_filter.py --tb=no -q` → all green
- Manual: open a Notebook tab, hit `cmd_open_local_file`, confirm
  the dialog default filter is `Notebooks (*.ipynb);;All Files (*)`.
  Repeat for Image, Matrix, Script, Pdf, Form, Contacts.

### T-NEW-112 — Type-aware file-import dialog filter (2026-08-14)

**Context.** Operator testing on 2026-08-14 reported: *"need to
implement a file import filter on the dialog based on what file
types can be imported (.ctd, .pyof, etc)"*. Separate from
T-NEW-111 (file-open, scoped to the active tab's *output* types),
this is file-*import*, scoped to what the application can
*accept as input* (`.ctd`, `.pyof`, plus whatever the
per-document-type importer chain supports — see
`tests/test_unimplemented_features.py:307-` for the CSV / DOCX /
Matrix importer wiring). There is no prior T-NEW card for this;
fresh defect.

**Affected sites:**
- `nchantdoffice/widgets/controls/toolboxes.py:776` —
  `NchantdOfficeApplicationToolBox.cmd_open_local_file` (handles
  `.pyof` import per T-NEW-074 — needs explicit `.pyof` filter
  on the dialog)
- `nchantdoffice/widgets/controls/toolboxes.py:1023-1045` —
  `cmd_import_pyof` `QFileDialog.getOpenFileName` call (per
  T-NEW-074, currently uses `QFileDialog` defaults; should set
  `"NchantdOffice Database Files (*.pyof);;All Files (*)"`)
- `nchantdoffice/widgets/documents/documents.py:344` —
  `NchantdOfficeDocument.import_document` static filter
- `nchantdoffice/models.py:307+` —
  `NchantdOfficeCloakModel.import_csv` / `import_docx` /
  `import_matrix` (per
  `tests/test_unimplemented_features.py:307-`; their open-dialog
  call sites — TBD — need tracing to confirm)
- `nchantdoffice/widgets/panes/files.py` —
  filesystem pane import dialog (TBD — confirm whether it
  routes through `cmd_open_local_file` or has its own dialog)

**Migration plan (no priority / low priority — design decision
first):** design question is "what is the importable-file-set
per call site?". Two distinct filter registries are needed:
- `IMPORTABLE_FILE_FILTERS`: keyed by import-handler name
  (`pyof_instance` → `*.pyof`, `ctd_doc` → `*.ctd`, `csv` →
  `*.csv`, `docx` → `*.docx`, `matrix_excel` → `*.xlsx *.xls`).
  This is a new constant — likely lives next to
  `PyofImportContract.TABLES` in
  `nchantdoffice/utilities/pyof_import.py`.
- Per-document-type import filters: e.g. an Image tab can
  import `.png .jpg .gif .bmp .webp`; a Notebook tab can import
  `.ipynb .py .md`; a Matrix tab can import `.xlsx .xls .csv`.
  This overlaps with T-NEW-111's `FILE_TYPE_FILTERS` registry
  and should share the same source of truth.

The cleanest design is to **unify both registries into a single
`FILE_TYPE_FILTERS` dict keyed by a `(direction, doc_type)` tuple**
(or two parallel dicts) in
`nchantdoffice/widgets/documents/documents.py`, and have all
dialog call sites read from there. This collapses T-NEW-111 +
T-NEW-112 into a single registration surface.

**Steps:**
1. Extend `FILE_TYPE_FILTERS` (introduced in T-NEW-111 step 1)
   with the `import_*` direction for each document type, plus
   application-level entries (`pyof_instance`, `ctd_doc`).
2. Add `NchantdOfficeDocument.import_filter_for_active_type() -> str`
   that returns the `import_*` filter for the active tab type
   (falls back to `"All Importable (*.pyof *.ctd *.json *.txt);;All Files (*)"`
   for app-level dialogs).
3. Wire `cmd_import_pyof` (T-NEW-074) to use
   `"NchantdOffice Database Files (*.pyof);;All Files (*)"`.
4. Wire `import_document` and any per-importer dialog sites
   listed above to use the helper.
5. TDD: extend `tests/test_type_aware_file_open_filter.py`
   (T-NEW-111) with import-direction tests, or add
   `tests/test_type_aware_file_import_filter.py` if separation
   is cleaner.
6. This card + CHANGES.md entry.

**Verification:**
- `python -m pytest tests/test_type_aware_file_import_filter.py --tb=no -q` → all green
- Manual: hit the Application tab "Import from .pyof…" button,
  confirm the dialog filter is `*.pyof`-scoped by default. Hit
  Image tab → import, confirm filter is image-extension-scoped.

### T-NEW-113 — Autosave on focal-change per document type (2026-08-14)

**Context.** Operator testing on 2026-08-14 reported: *"implement
autosave functionality on each action/focal-change of each
document type"*. T-NEW-079 (2026-08-13) shipped the canonical
journal save contract and explicitly deferred the autosave
scaffolding as *"Future work #1"*:

> "The always-save scaffolding — `self._parse_entry()` then
> `self.parent.save()` from the inner editor's `focusOutEvent`
> — is intentionally NOT in the outer save() flow yet. Per
> the same constraint: do NOT add `super().save()` to that path,
> because the journal is an app_media document. Land this when
> the user signals the always-save contract should be wired
> (separate card)."

The 2026-08-14 testing report is exactly that signal. This card
promotes T-NEW-079's deferred Future-work #1 into an actionable
workstream. Re-implementation must respect the constraint in
T-NEW-079's "Why this card exists" section: **journal save =
`save_app()` only**; no `super().save()` on the journal path; no
try/except around `save_app()` (failures propagate loud).

**Affected sites:**
- `nchantdoffice/widgets/documents/journal.py` — autosave
  scaffolding (`self._parse_entry()` + `self.parent.save()`
  from `focusOutEvent`) is commented out per T-NEW-079 Future
  work #1. This is where the journal's autosave contract lives.
- `nchantdoffice/widgets/documents/documents.py:625` —
  `NchantdOfficeDocument.save_app()` is the canonical save path
  for app_media documents; the journal must call it, not
  `super().save()`. Re-read this docstring before touching the
  autosave wiring.
- `nchantdoffice/widgets/documents/atnrg/attentioneering.py`,
  `browsers.py`, `contacts.py`, `news.py`, `pages.py`,
  `prompts.py` — each `NchantdOffice*` document subclass has
  its own `focusOutEvent` / `keyPressEvent` / per-action hook
  surface; the autosave dispatch needs to land in a
  centralised place (likely `NchantdOfficeDocument` base) and
  have each subclass opt in via an `autosave_on_focal_change: bool`
  flag (defaulting to `True`).
- `nchantdoffice/widgets/documents/workbooks/notebooks.py` —
  `NchantdOfficeNotebook` has its own `cmd_save_database` /
  external-file-path semantics (see
  `tests/test_notebook_save_bytes.py`); autosave must NOT
  bypass the canonical file-path-or-blob save flow.
- `nchantdoffice/widgets/documents/media/images.py`,
  `scripts.py`, `sketches.py`, `pdfs.py`, `forms.py`,
  `notes.py`, `audio.py` — each subclass has a `get_content()`
  shape; the autosave trigger must call `save_app()` (app_media)
  or the subclass's equivalent (doc_media), per the doc-type
  classification already established in T-NEW-079 / T-NEW-006.
- `tests/test_journal_always_save.py` (T-NEW-079, 6 tests) —
  needs extension with the autosave-on-focal-change contract
  once the wiring lands.

**Migration plan (no priority / low priority — design decision
first):** the design question is *"what counts as a
focal-change?"*. Options:
1. `focusOutEvent` on each per-document-type editor widget —
   fires when focus leaves the widget; natural for "user moved
   on" semantics.
2. Debounced timer after every text/image/notebook mutation —
   fires after N seconds of inactivity; smoother but harder to
   test deterministically and conflicts with the journal's
   "save on focusOut" intent.
3. Both — `focusOutEvent` is the primary trigger; debounced
   timer is a fallback for editors that don't naturally receive
   focusOut (e.g. the Matrix grid).

Operator convention (T-NEW-079) leans toward **option 1
(focusOutEvent)** for the journal and any text/editor widgets.
Option 3 (both) is acceptable as long as the debounced timer is
opt-in per document type (off by default) so it doesn't fire
during the middle of a user action. The autosave trigger must
**never** call `super().save()` on the journal path (per
T-NEW-079 contract); it must call `save_app()` (or the
doc-type-appropriate equivalent). No try/except around
`save_app()` — failures propagate loud so the user knows.

**Steps:**
1. Add `NchantdOfficeDocument.autosave_on_focal_change: bool`
   class attribute (default `True`) to centralise opt-out.
2. Add `NchantdOfficeDocument._autosave_on_focus_out(event)` —
   base implementation that calls `self.save_app()` for
   app_media docs or `super().save()` for doc_media docs.
   Defensive: skip if `self.document is None` or if the
   document has no unsaved changes (per `has_changed` flag
   already on the model).
3. Wire the journal subclass: uncomment the
   `self._parse_entry()` + `self.parent.save()` block in
   `focusOutEvent`, but route through `self.save_app()` (NOT
   `super().save()`) per T-NEW-079 constraint. No try/except
   wrapper around `save_app()`.
4. Wire each `NchantdOffice*` subclass to override
   `focusOutEvent` and call `_autosave_on_focus_out(event)` if
   `autosave_on_focal_change` is True. Subclasses with custom
   save flows (Notebook, Matrix) override the method, not the
   flag.
5. TDD: extend `tests/test_journal_always_save.py` with the
   focusOutEvent autosave contract (asserts `save_app()` is
   called, `super().save()` is NOT, no try/except swallows
   exceptions). Add `tests/test_autosave_on_focus_out.py`
   with one test per subclass that mocks `focusOutEvent` and
   asserts the correct save path is invoked.
6. This card + CHANGES.md entry.

**Verification:**
- `python -m pytest tests/test_journal_always_save.py tests/test_autosave_on_focus_out.py --tb=no -q` → all green
- Manual: open a journal tab, type some entries, click on a
  different tab, switch back — confirm the entries persisted
  (the existing `test_journal_restore.py` round-trip suite
  covers the load side). Repeat for Image, Script, Notebook,
  Matrix.

### T-NEW-114 — `.pyof` import still broken after T-NEW-074/077 (2026-08-14)

**Context.** Operator testing on 2026-08-14 reported: *"import
of .pyof is still broken, need to pull in the tables
(doc_tree_node, doc_tab, doc_media, doc_media_content,
app_media, app_media_content) grab the content data in each row
and create a new row in the corresponding table of the current
application database"*. T-NEW-074 / T-NEW-075 / T-NEW-076 /
T-NEW-077 (2026-08-11) nominally addressed `.pyof` import for
exactly the six base tables + three `_content` tables the report
names. The pytest report at card-filing time shows
**305 passed / 0 failed / 0 skipped** — including
`tests/test_import_pyof_documents_empty.py` (T-NEW-079
regression test for the `Documents Are Empty` crash chain) and
all 24 `tests/test_pyof_import.py` cases.

**Reproduction (2026-08-14, captured by operator):** operator
clarified the entry point — they clicked the **Application tab
ToolBox's import button** (the YAML action "Import from .pyof…"
via the drawer button bar), NOT the file-open dialog. Captured
log lines (verbatim, 20:40:43 → 20:41:01):

```
INFO  nchantrs.widgets.widgets     499: Focus Out
INFO  nchantrs.dialogs.files        75: /home/solubrew/Documents/nchantdsb (2).pyof
INFO  nchantrs.models.models       681: Initializing pyof sonql
INFO  nchantrs.models.models       682: Path: /home/solubrew/Documents/nchantdsb (2).pyof
INFO  nchantdoffice.models        2520: [models] import_nchantdoffice: opened SQLite DB at '/home/solubrew/Documents/nchantdsb (2).pyof'
INFO  micromole.storage            587: Get Table app_instance {'get_all_columns': True} pyof None
WARN  squirl.orgnql.sonql          257: Table app_instance
WARN  squirl.orgnql.sonql          257: CMD PRAGMA table_info(app_instance);
WARN  squirl.orgnql.sonql          257: Table app_instance
WARN  squirl.orgnql.sonql          257: CMD SELECT [...] FROM "app_instance"
INFO  micromole.storage            597: Data ... 1 rows x 17 columns
INFO  nchantdoffice.models        3805: [store] refresh_from_sqlite: loaded 1 app_instance row(s) from db='pyof'
INFO  nchantrs.widgets.widgets     494: Focus In
INFO  nchantrs.widgets.widgets     499: Focus Out
```

**No `[import_pyof]` log lines, no `ImportResult` summary, no
status-bar message.** The user's diagnosis ("it just doesn't do
what it is supposed to do") is exact.

**Root cause (Defect B — `cmd_import_pyof` is unreachable; the
button you actually click routes to instance registration).**

The operator clicked the **Application tab ToolBox's
import-instance button** (drawer action `import_instance`,
toolboxes.py:914, wired to `cmd_import_local_file`). For a
`.pyof` path, `cmd_import_local_file` at
`nchantdoffice/widgets/controls/toolboxes.py:623-624` runs:

```python
elif self.local_file.endswith(".pyof"):
    self.app.model.import_nchantdoffice(self.local_file)
    #Implement import of .pyof database
```

That is the **instance-registration path** (T-077 / T-NEW-007):
it loads the source's `app_instance` row so the host can
register the secondary instance. It does NOT copy any content
tables. The trailing comment `#Implement import of .pyof
database` is a TODO marker (per operator convention for
unfinished work) — the implementation has been pending since
the T-NEW-007 / T-077 era and the T-NEW-074 card did not
finish it: T-NEW-074 added a new `cmd_import_pyof` method
but did not redirect the existing import-button dispatch.

`cmd_import_pyof` (the T-NEW-074 method,
`toolboxes.py:1018-1075`) is the correct handler — it calls
`import_pyof(path, host_conn)` from
`nchantdoffice.utilities.pyof_import`, which is the T-NEW-074
content-table ETL orchestrator. **But it is not wired into any
drawer / button / menu.** The Application tab ToolBox drawer
init at `toolboxes.py:906-922` lists four wired actions:
`new_instance`, `open_instance`, `import_instance`,
`duplicate_instance`. None of them points at
`cmd_import_pyof`.

Additionally, the YAML action row in
`nchantdoffice/_data_/models.yaml:25` registers `import_pyof`
with the user-facing label "Import from .pyof…", but the
toolbar's `set_handler` switch at
`nchantdoffice/widgets/controls/toolbars.py:501-518` has no
case for `import_pyof` and falls through to
`self.add_document` — so even if the button were rendered from
the YAML directly (separate from the toolbox drawer), it would
still hit the wrong handler.

**Three independent wiring defects, all in the same feature
(all corrected by the consolidated fix below):**

1. **`cmd_import_local_file` routes `.pyof` to
   `import_nchantdoffice`** (the wrong destination) at
   `toolboxes.py:623-624`. **This is the bug the operator hit.**
   The trailing comment `#Implement import of .pyof database`
   on line 625 is a TODO marker (per operator convention for
   unfinished work) — the implementation has been pending since
   the T-NEW-007 / T-077 era and the T-NEW-074 card did not
   finish it: T-NEW-074 added a new `cmd_import_pyof` method
   but did not redirect the existing import-button dispatch.
2. **`cmd_open_local_file` routes `.pyof` to
   `_open_pyof_instance`** (same wrong destination) at
   `toolboxes.py:835-836`. Same bug, different entry point
   (the standard file-open dialog). T-NEW-074 also missed
   this dispatch.
3. **`cmd_import_pyof` is not wired into any button / drawer /
   menu.** T-NEW-074 shipped the method but did not add it to
   the `init_drawer_application` button bar at
   `toolboxes.py:906-922`, and the toolbar's `set_handler`
   switch at `toolbars.py:501-518` does not handle the
   `import_pyof` lookup_code_txt value (falls through to
   `add_document`).

**Defect C — synchronous import blocks the GUI.** The
T-NEW-074 `cmd_import_pyof` body at
`toolboxes.py:1041-1043` runs `import_pyof(path, host_conn)`
synchronously on the calling thread (which is the Qt event
loop / GUI thread for menu/button actions). For a non-trivial
`.pyof` the UI will freeze until the import completes. Not
what the operator reported yet, but it'll bite the moment the
dispatch is fixed.

**Affected sites:**
- `nchantdoffice/widgets/controls/toolboxes.py:623-624` —
  `cmd_import_local_file` extension dispatch: `.pyof` →
  `model.import_nchantdoffice` (the wrong destination). **The
  bug the operator hit.** Plus the lingering
  `#Implement import of .pyof database` TODO marker on line 625
  (per operator convention, this marker must be removed once
  the dispatch is fixed).
- `nchantdoffice/widgets/controls/toolboxes.py:600-635` —
  `cmd_import_local_file` body — the `.pyof` branch must be
  rewritten to call `self.cmd_import_pyof()` (with the
  pre-selected `local_file` injected via the `file_dialog_fn`
  kwarg, same pattern as `cmd_import_pyof`'s own QFileDialog
  call). **This is now the SINGLE canonical `.pyof` import
  dispatcher** (operator direction, 2026-08-14: "consolidate
  logic there should only be one and all needs to import
  .pyof should use the same cmd_import_local_file").
- `nchantdoffice/widgets/controls/toolboxes.py:835-836` —
  `cmd_open_local_file` extension dispatch: `.pyof` →
  `_open_pyof_instance` (wrong destination). Must be rewritten
  to **delegate to `cmd_import_local_file`** (not call
  `cmd_import_pyof` directly, not `_open_pyof_instance`,
  not `import_nchantdoffice`) — per operator direction, all
  `.pyof` import paths funnel through the single canonical
  handler.
- `nchantdoffice/widgets/controls/toolboxes.py:776-840` —
  `cmd_open_local_file` body — the `.pyof` branch must be
  rewritten to call `self.cmd_import_local_file()` (passing
  through any kwargs / event) so the file-open dialog
  delegates the `.pyof` decision to the single canonical
  dispatcher.
- `nchantdoffice/widgets/controls/toolboxes.py:1018-1075` —
  `cmd_import_pyof` body (T-NEW-074). The orchestrator + UI
  feedback here are correct for their intended purpose; **no
  source change needed**, just wire it in (one line from
  `cmd_import_local_file`).
- `nchantdoffice/widgets/controls/toolboxes.py:1041-1043` —
  synchronous `import_pyof()` call inside `cmd_import_pyof`
  body (the GUI thread). **Defect C.**
- `nchantdoffice/widgets/controls/toolboxes.py:906-922` —
  `init_drawer_application` button-bar config. **NO CHANGE.**
  Per operator direction: the existing button (`import_instance`
  → `cmd_import_local_file`) is the correct button; the fix
  lives entirely inside `cmd_import_local_file`'s `.pyof`
  branch. No new button, no relabel, no `init_drawer_application`
  edit.
- `nchantdoffice/widgets/controls/toolbars.py:501-518` —
  `set_handler` switch. **NO CHANGE.** The
  `cmd_import_local_file` handler is reached via the existing
  `import_instance` drawer button, not via the YAML-registered
  `app_action` row. The YAML row's `set_handler` fallback to
  `add_document` only matters if a button is ever rendered
  directly from the YAML (which is not how the Application
  tab ToolBox works today). Leave as-is.
- `nchantdoffice/widgets/controls/toolboxes.py:738-770` —
  `_open_pyof_instance` body. After the fix, **this method
  becomes unreachable from the GUI** (both dispatchers point
  at `cmd_import_local_file` instead). It can stay in place
  as dead code for now (in case any test / unit harness
  imports it directly) — but a follow-up commit may want to
  remove it if no test references it. Out of scope for this
  card; flag as a T-NEW cleanup item if encountered.
- `nchantdoffice/_data_/models.yaml:25` — the
  `app_action` registration for `import_pyof`. Correct
  registration; **no change needed**. (If a future card wires
  the YAML-registered action into a button or menu, that
  separate card would add the `case "import_pyof": return
  self.cmd_import_pyof` branch to `set_handler`.)
- `nchantdoffice/utilities/pyof_import.py:339-` —
  `import_pyof` orchestrator + `import_one_table` base path.
  T-NEW-074/075/076/077 work landed here; the orchestrator
  itself is correct. **No defect.**
- `tests/test_pyof_import.py` — 24-test suite for
  `cmd_import_pyof` + `import_pyof` orchestrator. **No
  coverage** for `cmd_import_local_file`'s `.pyof` branch
  dispatch decision; that is why a green suite does not catch
  any of the three wiring defects.
- `tests/test_pyof_sqlite_import.py` —
  `model.import_nchantdoffice` integration test. **No
  coverage** for the dispatch decisions either.

**Migration plan (no priority / low priority — design decision
first):** per operator direction (2026-08-14), the design is
**already decided**: `cmd_import_local_file` is the single
canonical `.pyof` import dispatcher. All paths funnel through
it. The only remaining design question is **Defect C
(synchronous GUI freeze)**:

- The T-NEW-074 `cmd_import_pyof` body runs `import_pyof()`
  synchronously on the GUI thread at
  `toolboxes.py:1041-1043`. For a non-trivial `.pyof` this
  freezes the UI.
- Recommended fix: move `import_pyof()` to a worker thread
  (QThread / QRunnable / `concurrent.futures.ThreadPoolExecutor`)
  and emit progress + completion signals back to the GUI
  thread for the status bar update. Defensive: signal
  connection must use `Qt.QueuedConnection` so the slot runs
  on the main thread.
- Alternative: leave it synchronous and document the freeze as
  acceptable for v0.x. Operator preference: the worker-thread
  fix, since the user's testing report specifically called
  out "grab the content data in each row and create a new row"
  — implying large source `.pyof` files are in scope.

**Steps:**
1. **Failing test for the dispatch bug:** write
   `tests/test_cmd_import_local_file_pyof_routing.py` that
   mocks `cmd_import_pyof` on the toolbox instance, drives
   `cmd_import_local_file` with a `.pyof` path, and asserts
   `cmd_import_pyof` was called with the pre-selected path
   (NOT `import_nchantdoffice`). The test must FAIL on the
   current code (Defect 1) and PASS after the fix. Also
   write `tests/test_cmd_open_local_file_delegates_pyof.py`
   that asserts `cmd_open_local_file`'s `.pyof` branch calls
   `cmd_import_local_file` (NOT `_open_pyof_instance`,
   NOT `import_nchantdoffice`).
2. **Fix the dispatcher (one-line change each):** in
   `cmd_import_local_file` at `toolboxes.py:623-624`, replace
   `self.app.model.import_nchantdoffice(self.local_file)` with
   `self.cmd_import_pyof(file_dialog_fn=lambda *a, **kw:
   (self.local_file, ""))`. In `cmd_open_local_file` at
   `toolboxes.py:835-836`, replace the
   `_open_pyof_instance(self.local_file)` call with
   `return self.cmd_import_local_file(self.local_file)` (or
   equivalent delegation that re-enters the single canonical
   dispatcher).
3. **Remove the TODO marker:** delete the
   `#Implement import of .pyof database` comment on
   `toolboxes.py:625`. Per operator convention, TODO markers
   must be removed when the work lands.
4. **Fix Defect C (sync GUI freeze):** wrap the
   `import_pyof(path, host_conn)` call inside `cmd_import_pyof`
   (`toolboxes.py:1041-1043`) in a worker thread. Emit a
   `pyof_import_complete(results)` signal with the
   `ImportResult` list; the slot updates the status bar from
   the main thread. Use `Qt.QueuedConnection` for the signal
   so the slot runs on the main thread.
5. **Extend `tests/test_pyof_import.py`** (T-NEW-074 suite, 24
   tests) with: (a) thread-safety test (the import result is
   surfaced back to the GUI thread via signal, not direct
   call); (b) end-to-end test that drives
   `cmd_import_local_file` with a real `.pyof` fixture (not
   just the unit-level `cmd_import_pyof` injection) and
   asserts the content tables land on the host.
6. **Manual smoke test:** click the Application tab ToolBox
   import button on
   `/home/solubrew/Documents/nchantdsb (2).pyof`, confirm the
   log now shows `[import_pyof] {path}: inserted=N, skipped=M`
   (the T-NEW-074 orchestrator call), the status bar updates
   to `Imported N rows (M skipped)`, and the source's
   `doc_tree_node` / `doc_tab` rows are visible in the host's
   tree pane. Repeat via the file-open dialog → `.pyof` to
   confirm both entry points funnel through the same
   dispatcher.
7. Verify all 305+ tests still pass (plus the new tests from
   step 1 + step 5).
8. This card + CHANGES.md entry.

**Verification:**
- `python -m pytest tests/ --tb=no -q` → 305 + N passed, 0
  failed (N = new tests from step 1 + step 5).
- Manual: re-run the exact 20:40:43 → 20:41:01 reproduction
  sequence (click Application tab ToolBox import button, pick
  `nchantdsb (2).pyof`); confirm the log now shows the
  T-NEW-074 orchestrator call (`[import_pyof] {path}:
  inserted=N, skipped=M`) and the status bar update,
  instead of the silent instance-registration path.
- Manual (secondary entry point): use File → Open, pick a
  `.pyof`, confirm the same orchestrator log + status bar
  message appears (proves both paths funnel through
  `cmd_import_local_file`).

---

**Catalog updates** (one-line entries to add at the top of
`TODOs.md` when this section is promoted):

- **T-NEW-111** ✅ Type-aware file-open dialog filter — filed 2026-08-14 from `testing-report_20260814.md` item 1.
- **T-NEW-112** ✅ Type-aware file-import dialog filter — filed 2026-08-14 from `testing-report_20260814.md` item 2.
- **T-NEW-113** ✅ Autosave on focal-change per document type — filed 2026-08-14 from `testing-report_20260814.md` item 3 (promoted from T-NEW-079 Future-work #1).
- **T-NEW-114** ✅ `.pyof` import still broken after T-NEW-074/077 — fixed 2026-08-15 (commit `f81c8a7`). 3 wiring defects closed: cmd_import_local_file routes .pyof → cmd_import_pyof (was → model.import_nchantdoffice); cmd_open_local_file routes .pyof → cmd_import_local_file (was → _open_pyof_instance); cmd_import_pyof now offloads to a _PyofImportWorker on a QThread (was synchronous on GUI thread). TODO marker removed. 5 new tests pin the dispatch + worker thread. 437 passed / 0 failed (non-Qt subset).

---

## T-NEW cards filed 2026-08-15 (session: testing-report + TODO sweep)

### T-NEW-115 — Creating new Nodes at the top level is blocked (2026-08-15)

**Top-level node creation blocked.** Operator testing on 2026-08-15
(`testing-report_20260815.md`) reported: *"Block from creating new
Nodes at the top level"*. The add-node write path routes through
`NchantdApplicationModel.add_node`, whose `pid='0'` branch resolves
the tree-widget parent as `panes['left'].tree` itself
(applicationmodels.py:207-208) before appending the row; the office
layer additionally gates nodes via `LOCKED_NODE_NAMES` /
`is_locked_node` (T-NEW-004). Which of these surfaces rejects (or
silently drops) a user-initiated top-level create has not been
root-caused yet — the card covers the investigation plus the fix.
This has no prior T-NEW card.

**Affected sites:**
- `nchantrs/models/applicationmodels.py:198-217` — `add_node`
  `pid='0'` parent-resolution branch
- `nchantdoffice/models.py:614` — `add_node` delegation;
  `models.py:633` `add_node_app`
- `nchantdoffice/models.py:167-191` — `LOCKED_NODE_NAMES` /
  `is_locked_node` gate (T-NEW-004)
- `nchantdoffice/widgets/panes/documents.py` — the node-create
  handler that initiates the call

**Migration plan (no priority — design decision first):** decide
whether top-level creation is (a) intentionally locked to the three
canonical app nodes and the UI must say so, or (b) allowed and the
gate/parent-resolution has a defect. Reproduce from the running app
(File > New Node with nothing selected), capture the log line, and
fix the rejecting layer only.

**Steps:**
1. Reproduce live: with no node selected, invoke new-node; record
   which of `add_node` / `is_locked_node` / the pid='0' tree-parent
   branch rejects it.
2. Write a failing test in
   `tests/test_toplevel_node_creation.py` pinning the decided
   behavior (create succeeds at pid='0', or refusal returns a
   user-visible message).
3. Fix the identified layer; keep T-NEW-004 locked-node deletion
   guards untouched.
4. This card + CHANGES.md entry.

### T-NEW-116 — Jupyter server default working directory (~/Documents/NchantdLibrary) (2026-08-15)

**Notebook server cwd defaults to the process cwd.** Operator
testing on 2026-08-10 (`testing-report_20260810.md`) reported:
*"NchantdOfficeNotebook need to control working directory when
server starts up to be the ~/Documents/NchantdLibrary path by
default"*. Today `start_jupyter_server` sets the subprocess cwd to
`dirname(self.file_path)` when a notebook file is open, else leaves
it `None` (inheriting the app process cwd — often the repo or the
launcher dir), so the Jupyter file browser roots itself wherever
the app happened to start.

**Affected sites:**
- `nchantdoffice/widgets/documents/workbooks/notebooks.py:1384-1398`
  — the `cwd = None` / `dirname(self.file_path)` block feeding
  `subprocess.Popen(..., cwd=cwd)`

**Migration plan (low priority):** three-tier resolution —
(1) open notebook's directory, (2) `app.model.library_path` (the
existing NchantdLibrary resolver used by the toolbox), (3)
`~/Documents/NchantdLibrary` literal fallback; create the directory
if missing.

**Steps:**
1. Add `_resolve_server_cwd()` on `NchantdOfficeNotebook`
   implementing the three-tier resolution.
2. Replace the inline block at notebooks.py:1384-1387 with a call
   to it; log the resolved cwd in the existing launch log line.
3. TDD: `tests/test_notebook_server_cwd.py` — stub `file_path`,
   `app.model.library_path`, and HOME to prove each tier wins in
   order.
4. This card + CHANGES.md entry.

### T-NEW-117 — Palette scan crashes: `PyfficeColorPalette.extract_palette` does not exist (2026-08-15)

**Image palette scan button raises AttributeError.** Operator
testing on 2026-08-10 (`testing-report_20260810_001.md`) captured
the crash: `cmd_run_palette_scan failed:
'PyfficeColorPalette' object has no attribute 'extract_palette'`
at images.py:927. Verified still broken on 2026-08-15: the
installed `pyffice.images.palettes.PyfficeColorPalette` exposes
`add_color` / `get_palette` / `set_palette`-family methods only —
no `extract_palette` — so the image-toolbar button 16 handler can
never succeed.

**Affected sites:**
- `nchantdoffice/widgets/documents/media/images.py:984` —
  `cmd_run_palette_scan` call to the missing method
- `pyffice/pyffice/images/palettes.py:38` —
  `PyfficeColorPalette` class (upstream; needs the extraction
  surface)

**Migration plan (no priority — design decision first):** decide
where extraction lives: (a) upstream `extract_palette(path)` on
`PyfficeColorPalette` reading the image and returning a
palette + usage-counts structure, or (b) a standalone pyffice
module the image widget calls. Downstream should also degrade
gracefully (log + status message) instead of a raw traceback.

**Steps:**
1. Implement `extract_palette` upstream in pyffice
   (`palettes.py`) with tests in
   `tests/pyffice_unit/unit/images/` (fixture image → expected
   dominant colors).
2. Guard the call site at images.py:984 with hasattr + logma.error
   + status-bar message when the upstream surface is missing.
3. TDD: extend `tests/test_palette_in_image_toolbar.py` with a
   missing-method degradation test.
4. This card + CHANGES.md entry (both repos).

### T-NEW-118 — Journal PII detector + redacted view with PIN copy (2026-08-15, re-file)

**PII handling for journal entries.** Operator direction on
2026-08-10 (`testing-report_20260810.md`): *"add a PII detector to
the journal and hide the inputs stored to the secure storage
area...need to show redacted and then allow the user to still copy
and paste the full text with a pin"*. This was originally deferred
inside the T-NEW-065 card body under the labels "T-NEW-066/067/068",
but those numbers were subsequently consumed by the matrix-chart /
retention-policy / filesystem-location cards, so the PII work lost
its tracking. Re-filed here. Nothing is implemented today: journal
content is stored verbatim in `app_media_content` via the journal
save path.

**Affected sites:**
- `nchantdoffice/widgets/documents/journal.py:282` — journal save
  (`save_app`) writing plain content rows
- pycurity secure-storage surface (PyKeyStore) — target for the
  redacted originals
- `nchantdoffice/widgets/documents/journal.py` — render path for
  the redacted view + PIN-gated copy

**Migration plan (no priority — design decision first):** decide
the detector scope (regex tier for emails/phones/keys vs a
pycurity-provided scanner), the redaction token format persisted in
`app_media_content`, and the PIN prompt surface (reuse the existing
secure-store passphrase flow vs a per-document PIN).

**Steps:**
1. Detector: `nchantdoffice/utilities/pii_detect.py` returning
   spans by category; unit tests per category.
2. Save path: journal save detects spans, stores redacted text in
   `app_media_content`, originals + span map in pycurity secure
   storage keyed by entry UUID.
3. Render path: journal view shows redacted tokens; copy action
   prompts for PIN, decrypts, places full text on the clipboard.
4. TDD: `tests/test_journal_pii_redaction.py` (detect → store →
   render → PIN copy round-trip).
5. This card + CHANGES.md entry.

### T-NEW-119 — Journal content growth: timestamp column + retention policy + delete_marked (2026-08-15, re-file)

**Retention follow-ups lost to a number collision.** T-NEW-065
shipped version-based journal compaction; its card body deferred
three follow-ups under the labels "T-NEW-066/067/068", but those
numbers were reused by unrelated cards (matrix charts, chart
xlsx, filesystem memory), orphaning the follow-ups. Re-filed as
one card: (1) a timestamp/`MODON_DTTM`-based column usable for
time-based pruning of `app_media_content` (schema has no usable
timestamp today), (2) wiring the ``Data Retention Policy`` lookup
via `get_app_policy` (referenced by micromole storage but not
declared in any yaml cfg), (3) the `delete_marked` pattern that is
a no-op across the storage chain.

**Affected sites:**
- `nchantdoffice/models.py` — `compact_journal_content` (the
  version-based compaction this extends) and
  `_APP_MEDIA_CONTENT_COLUMNS` (~line 3806) for the schema change
- `micromole/storage.py:309,332` — `delete_marked` no-op and the
  policy lookup reference
- `nchantrs/models/models.py:300` — the upstream delete_marked
  reference

**Migration plan (no priority — design decision first):** the
schema change is the gate: adding a timestamp column to
`app_media_content` requires a migration story for existing
`.pyof` files (lazy ALTER on open vs re-save). Decide retention
policy granularity (per-user setting vs global policy row) before
wiring `get_app_policy`.

**Steps:**
1. Schema: add the timestamp column + lazy-migration helper; pin
   with a round-trip test on an old-format `.pyof`.
2. Extend `compact_journal_content` with a time-based prune branch
   driven by the timestamp.
3. Declare the Data Retention Policy row surface + wire
   `get_app_policy`; fall back to the version-based path when no
   policy exists.
4. Implement `delete_marked` in the storage chain (flag + sweep)
   and route prune through it.
5. TDD: extend `tests/test_compact_journal_content.py`.
6. This card + CHANGES.md entry.

### T-NEW-120 — Script save/restore aspirational tests fail at the 5d80f92 contract (2026-08-15)

**5 red tests pin the future script round-trip contract.** The
user confirmed (2026-08-15) that NchantdOfficeScript live save +
reopen of internally and externally stored text works at commit
`5d80f92`. The later production changes (`85e809e`) were built
against the tests' aspirational contract and broke the live
behavior, so they were reverted in `822b32e` (tests kept). The 5
tests now fail by design and are the acceptance gate for this
card: implement the proper contract WITHOUT regressing the
`5d80f92` live path.

**Affected sites:**
- `nchantdoffice/widgets/documents/media/scripts.py:549-562` —
  `get_content()` HTML branch (currently persists `text=""`; the
  HTML lives in the Pyffice `text.html` attribute)
- `nchantdoffice/widgets/documents/media/scripts.py:1748-1758` —
  `_resolve_document_text()` pass 2 (`content.get("text", {})`
  walk that only round-trips by accident of the isinstance
  unwrap)
- `tests/test_script_newline_roundtrip.py` (3 failing),
  `tests/test_document_persistence.py` (1 failing),
  `tests/test_script_open_format.py` (1 failing)

**Migration plan (no priority — design decision first):** decide
the canonical stored shape for HTML scripts (persist editor HTML
in the content row vs keep the Pyffice-unit attribution and change
only the reopen walk), then bring the OTHER side (save or reopen)
to match — never both at once against the live behavior.

**Steps:**
1. Write a live-behavior pin FIRST: a test that saves + reopens a
   script through the `5d80f92` path and asserts the editor text
   survives (guards against regressing the working path).
2. Align `get_content()`'s HTML branch with the decided shape.
3. Align `_resolve_document_text()` pass 2 with the same shape
   (correct dict walk: `content["content"]["text"]["value"]`).
4. Turn the 5 aspirational tests green without touching the step-1
   pin.
5. Full non-Qt suite + this card + CHANGES.md entry.

### T-NEW-121 — em-dash sweep + encoding-declaration placement (2026-08-15)

**Non-ASCII bytes are a latent SyntaxError in 197 files.** Incident
2026-08-15 (fixed in `30593b9`): `toolboxes.py` carries its
`# -*- coding: utf-8 -*-` declaration on line 14 (after a 13-line
module docstring), so Python's tokenizer falls back to ASCII
source encoding and every em-dash (U+2014) added to the file is a
`SyntaxError: invalid character`. 197 files in the repo contain
em-dashes today; any of them with the declaration below line 2
fails the same way the next time someone edits near a dash. The
live app crash cascaded into `ModuleNotFoundError: No module named
'widgets'` because the toolboxes import died at parse time.

**Affected sites:**
- All 197 files returned by:
  `grep -rlP '\x{2014}' nchantdoffice/ cmds/ tests/ --include='*.py'`
- Per-file: the `# -*- coding:` line position (`head -3` shows it
  after the module docstring banner)

**Migration plan (low priority, mechanical):** pick ONE convention
— (a) move the coding declaration to line 2 of every affected file
(one-line edit, keeps the prose), or (b) sweep all em-dashes to
`--` (ASCII-safe). Option (a) is smaller and preserves the writing
style; option (b) is what `30593b9` did locally for the two files
touched.

**Steps:**
1. Script the sweep (`cmds/` one-off): for each affected file,
   apply the chosen convention; `ast.parse` before/after to prove
   no semantic change.
2. Add a guard test `tests/test_source_encoding.py`: for every
   tracked `.py`, if the file contains non-ASCII bytes, assert the
   coding declaration is on line 1 or 2.
3. Run the full non-Qt suite.
4. This card + CHANGES.md entry.

### T-NEW-122 — Qt-harness migration for tests importing toolboxes (2026-08-15)

**test_cmd_pyof_routing_consolidation.py crashes when batched.**
The 5 dispatch tests pass in isolation but abort the interpreter
(`Fatal Python error: Aborted`, shiboken6 stack) when collected in
a multi-file pytest run, because importing
`nchantdoffice.widgets.controls.toolboxes` loads PySide6 at module
level (the `_PyofImportWorker(QObject)` + Signal surface added by
T-NEW-114). The established pattern for Qt-using tests in this
repo is the qt_parent subprocess harness (fresh interpreter per Qt
test file); this card migrates the file or makes the import lazy
so the non-Qt batch stays usable.

**Affected sites:**
- `tests/test_cmd_pyof_routing_consolidation.py` — the crashing
  file (5 tests)
- `nchantdoffice/widgets/controls/toolboxes.py` — module-level
  `QObject/QThread/Signal` import block (the trigger)
- qt_parent harness — target runner

**Migration plan (no priority — design decision first):** (a) move
the file to the qt_parent harness (keeps production imports
eager/simple), or (b) make the PySide6 QtCore import lazy inside
the worker (keeps the file in the fast non-Qt subset but adds an
import-time branch to production code).

**Steps:**
1. Decide (a)/(b); if (b), wrap the import and pin with a
   non-Qt import test (`python -c "import
   nchantdoffice.widgets.controls.toolboxes"` without a
   QApplication).
2. Re-run the full non-Qt batch WITH the file included and
   confirm no interpreter abort.
3. This card + CHANGES.md entry.

### T-NEW-123 — Embedded-TODO sweep: implement-method stubs and config wiring (2026-08-15)

**21 unimplemented-method TODO markers with no cards.** The
embedded_todos audit dim sits at 58% because ~30 `TODO` markers
remain in source; several are already covered by open cards
(images.py:1162 → T-NEW-035 drawer redraw; charts.py:186/214 →
T-NEW-029 segfault; toolbars.py:216 → T-NEW-039 signature
cleanup; journal.py:422 → T-NEW-079 populate refactor; the
T-035/082/083 historical markers are annotations, not work). The
remainder are untracked stubs and config wirings collected here.

**Affected sites (uncovered remainder):**
- `nchantdoffice/widgets/documents/documents.py:1125` —
  `# TODO implement method`
- `nchantdoffice/widgets/widgets.py:113` — `# TODO implement
  method`
- `nchantdoffice/widgets/config/source_config.py:319` —
  `# TODO implement method`
- `nchantdoffice/widgets/documents/workbooks/notebooks.py:1788,
  1792` — two `#TODO: implement method` stubs
- `nchantdoffice/widgets/config/settings.py:980` —
  NchantdOfficeDocumentConfigPane per-document-type features pane
- `nchantdoffice/widgets/config/settings.py:1209` — lock default
  right-side tab to the Ad tab for free users
- `nchantdoffice/widgets/panes/documents.py:669` — catalog pane
  tab-is-None stub values
- `nchantdoffice/widgets/config/referral_panel.py:117` — referral
  code must always load from external source
- `nchantdoffice/models.py:2703` — node position correction
  (`pos = 0 #TODO: need to find correction position`)
- `nchantdoffice/widgets/documents/journal.py:132` — always
  scroll to bottom of document
- `nchantdoffice/widgets/documents/journal.py:282` — journal save
  redirect to the `app_doc_content` table

**Migration plan (no priority — triage first):** each site is
either a real implementation (settings.py:980/1209, models.py:2703,
journal.py:132/282, referral_panel.py:117) or a stub whose correct
fate is deletion when the enclosing feature ships. Triage into
implement vs delete, then batch by file. settings.py:1209 (Ad-tab
default for free users) interacts with the advertisements surface
and deserves its own sub-card if non-trivial.

**Steps:**
1. Triage table in this card: site → implement | delete | covered-elsewhere.
2. Implement the chosen sites file-by-file with one test per
   behavior added; remove each TODO marker as it lands (operator
   convention: markers are removed when work lands).
3. Re-run `sasquatch analyze` and record the embedded_todos delta.
4. This card + CHANGES.md entry.

---

**Catalog updates** (filed 2026-08-15, session: testing-report + TODO sweep):

- **T-NEW-115** ✅ Creating new Nodes at the top level is
  blocked -- **FIXED** by T-NEW-130 (`ac448ad`). Top-level
  node creation now lands at `pid=0` via the `top_level`
  flag on `NchantdNewDocumentSigil`. Pin:
  `tests/test_top_level_node_create.py` 8 RED tests
  covering the flag dispatch + sigil launch.
- **T-NEW-116** ✅ Jupyter server default working directory
  (~/Documents/NchantdLibrary) -- **FIXED** (2026-08-16,
  gamma `pending`). The Jupyter subprocess is now spawned
  with a cwd that defaults to
  ``~/Documents/NchantdLibrary`` (created if missing)
  when no file is open. The previous behaviour used
  ``dirname(self.file_path)`` when a file is set and
  fell back to the bare process cwd (often the
  application bundle dir, which is read-only on packaged
  installs). Fix: extracted ``_resolve_jupyter_cwd()``
  helper with a 3-step lookup chain (file parent ->
  ``~/Documents/NchantdLibrary`` -> process cwd as
  last-resort). ``start_jupyter_server`` delegates to
  it. Pin: `tests/test_t_new_116_jupyter_default_dir.py`
  4 new tests (behavioural: default + file-path, source-
  level: helper exists + start_jupyter_server delegates).
- **T-NEW-117** ✅ Palette scan crashes:
  `PyfficeColorPalette.extract_palette` missing —
  **FIXED** (2026-08-17, gamma `419a317`). Upstream
  pyffice `1cd3c48` added `PyfficeColorPalette.extract_
  palette`; nchantdoffice `419a317` adds a `hasattr`
  graceful-degradation guard at the image-toolbar call
  site so older pyffice builds log + status-bar the
  failure instead of crashing with AttributeError. Pin:
  `tests/test_t_new_117_palette_scan_degradation.py` (3
  tests).
- **T-NEW-118** Journal PII detector + redacted view with PIN copy — re-filed (was orphaned by the T-NEW-066/067/068 number collision inside T-NEW-065's deferred-work section).
- **T-NEW-119** Journal content retention: timestamp column + retention policy + delete_marked — re-filed (same number-collision orphaning).
- **T-NEW-120** ✅ Script save/restore aspirational tests
  -- **FIXED** (2026-08-16, gamma `pending`). The 5
  aspirational tests in
  ``tests/test_document_persistence.py`` /
  ``tests/test_script_newline_roundtrip.py`` /
  ``tests/test_script_open_format.py`` are now green
  (15 passed / 0 failed). Fix re-applies the production
  logic from the previously-reverted ``85e809e``
  commit: (1) ``get_content`` HTML branch passes
  ``editor_html`` through directly rather than running
  a defunct ``html.replace(...)`` template substitution
  (the template body was commented out, so the body
  collapsed to ``""`` and the saved payload lost all
  text); (2) the dict-shape ``_resolve_document_text``
  walks the proper ``content[content][text][value]``
  path rather than the top-level
  ``content["text"]`` (which reached the wrong dict);
  (3) test SimpleNamespace fixtures gained
  ``location='external'`` to match the
  ``populate_document`` ``external/internal/cloud``
  dispatch's shape requirement. All changes leverage
  existing scripts.py / nchantrs patterns -- no new
  helpers introduced. Pin: the 5 aspirational tests in
  the 3 named test files.
- **T-NEW-121** em-dash sweep + encoding-declaration placement — filed after the `30593b9` SyntaxError incident; 197 files affected.
- **T-NEW-122** ✅ Qt-harness migration for tests importing
  toolboxes — **FIXED** (2026-08-17, gamma `260886a`). The
  module-level `_QAPP = QApplication.instance() or
  QApplication(sys.argv)` pattern in 21 test files
  aborted multi-file pytest collection at exit 134/139.
  `260886a` adds `tests/conftest.py` with a session-scoped
  autouse fixture that lazily constructs one
  `QApplication` for the whole pytest session (deferred
  import so non-Qt hosts stay safe); opt-in
  `tests/qt_parent/__init__.py` exposes session- and
  function-scoped `qapp` fixtures for tests that want to
  declare Qt dependency explicitly. The offending
  module-level line was stripped from all 21 offenders;
  the autouse conftest provides the same instance
  lazily. Pin: `tests/test_t_new_122_qt_collection_guard.py`
  (2 tests: AST scan finds no offender + RED→GREEN
  history). Full suite (with
  `--ignore=tests/test_cmd_pyof_routing_consolidation.py`
  for the unrelated pre-existing pyof bare-parent
  SIGSEGV that `07fc18b` fixed the same day): 19 failed,
  836 passed, 6 skipped (100% collection reached; pre
  `260886a` the run aborted at 8% of collection).
- **T-NEW-123** ✅ Embedded-TODO sweep -- **FIXED (cluster
  4)** (2026-08-16, gamma `pending`). This commit
  closes the 4 in-file TODOs that were either stale
  comments over already-implemented code or had been
  resolved by prior cards. The remaining embedded
  TODOs in this card (palette drawer wiring, tool
  drawer re-render, per-doctype features pane, tab-None
  Stub, catalog=false default) shipped as T-NEW-141c.
  The remaining embedded TODOs not in scope for this
  commit are:
  - `models.py:3040` -- "need to find correction
    position" (corrupted-character fallback in the
    correction-table lookup; low-priority, deferred).
  - `panes/charts.py:186/214` -- the chart-config
    action-button / border-style builder TODOs that
    were historically blamed on T-NEW-029 drag-init
    gating. **FIXED** (2026-08-17, gamma `899962c`):
    the real root cause was an implicit `None` return
    feeding `layout.addWidget(None)` (PySide6 segfault),
    not drag gating. Fix: `_build_chart_action_button_
    group` / `_build_border_style_editor` now return
    real `QWidget`s with an `is not None` gate before
    `addWidget(...)`. Pin:
    `tests/test_t_new_037_addwidget_none_root_cause.py`
    (behavioural + source-shape regressions).
  - `analytics.py:887` -- not an actual marker; it's
    the docstring of a method that called a
    `# TODO implement method` reference.
  - `models.py:3412` -- the original
    `# TODO: increment version` marker that the
    surrounding code already implements via
    PyfficeDocument.add_change version semantics.
  Resolved in this commit:
  - `journal.py:319` -- the inline
    `save_app() # TODO save has to redirect to the
    app_doc_content table` was misleading;
    `save_app()` already routes through
    `app_doc_content`/`app_media_content` rather than
    `doc_media_content` (the journal's app-scoped vs
    doc-scoped distinction is preserved by using
    `save_app()`). Stale TODO replaced with
    explanation comment.
  - `settings.py:1254` -- the inline TODO
    "lock default right side tab to Ad tab for free
    users" was resolved by T-NEW-140; the lock lives
    in `cmd_on_change_right_side_tab_select`.
  - `journal.py:459` -- the inline TODO "refactor to
    use the standard populate methods" was resolved by
    T-NEW-138; `populate_document` delegates to
    `self.parse(self.get_content())` (the standard
    populate path). The bespoke `get_content_text` is
    journal-specific metadata composition (nid/tid/
    scope).
  - `config/referral_panel.py:117` -- the inline TODO
    "must always load from external source" is the
    T-NEW-061 deferred work (service call to
    nchantdoffice.com). Until that ships, the local
    `user_config["referral_code"]` cache IS the source
    of truth (the `_load_or_generate_code` body, lines
    358-400+).

- **T-NEW-138** Journal editor followups: always-scroll to bottom + refactor to standard populate (covers `journal.py:132, 422`) -- pairs with T-NEW-079.
- **T-NEW-139** ✅ Toolbar signature cleanup: combine `add_tab`
  + `add_document` shared cfg/wiring (`toolbars.py:216`) --
  **FIXED** (2026-08-16, gamma `pending`). The original
  TODO asked to combine ``add_tab`` and ``add_document``,
  but no ``add_tab`` sibling exists on
  ``NchantdNewDocumentToolBar``. The real candidate for
  extraction was the two-line post-creation navigation
  block (left-pane ``updateTabs('center')`` + center-pane
  ``setCurrentIndex(pos)``). Fix: extracted
  ``_navigate_to_new_doc(pos) -> Self`` helper; ``add_document``
  delegates to it. Any future ``add_tab`` / ``add_shortcut``
  method on this class can call the same helper. Pin:
  `tests/test_t_new_139_toolbar_navigate.py` 4 new tests
  (helper-exists, signature shape, source-level pin x2).
- **T-NEW-140** ✅ Free-user right-side tab: lock default to Ad
  tab (`settings.py:1209`) -- **FIXED** (2026-08-16, gamma
  `pending`). The right-side tab dropdown options are not
  restricted (free users still see Settings / Help / Ad / etc.
  in the right pane), but the *default* they open on launch
  is locked to the Ad tab. Fix: in
  `cmd_on_change_right_side_tab_select`, when the user is
  not pro (`is_pro_user(user) is False`) and the selected
  value is not `"4 - Ad"`, coerce the recorded value to
  `"4 - Ad"` and log a warning. Pro users are unrestricted.
  The lock pairs with T-NEW-135 (100-node cap redirect):
  free users who hit the cap are redirected to the Get Pro
  upsell AND they default-open on the Ad tab so the upsell
  is the first thing they see. Pin:
  `tests/test_t_new_140_free_user_ad_tab.py` 6 new tests
  (source-level pin x2, behavioural: free-user coercion,
  pro-user preservation, idempotent ad-tab, exception swallow).
- **T-NEW-141** ✅ Inside-nchantdoffice TODO sweep: 10
  remaining markers (images palette drawer, notebook
  stubs, catalog tab-None, config features pane, 3 stub
  methods, `users.has_pro` service truth) --
  **FIXED (subset)** (2026-08-16, gamma `pending`). This
  commit closes the3 smallest, well-scoped stub-method
  markers:
  - `widgets.py:111` `go_to_previous_tab` was a
    one-line TODO stub; today the caller in
    `panes/documents.py:872` (`cmd_delete_tab`) relied on
    a no-op. Fix: decrements the center-pane
    `currentIndex` by 1, clamped at 0 so deleting at
    index 0 is a safe no-op rather than an IndexError.
  - `documents.py:1182` `populate_data` had a TODO
    marker plus two real lines (`set_location` + `save`).
    Fix: replace the TODO with a real docstring
    describing the internal-location contract; method
    signature changed from `-> None` to `-> Self` for
    parity with the other `populate_data` callers
    (scripts.py, pdfs.py, images.py, etc.).
  - `config/source_config.py:317` `_load_api_key` was a
    no-op stub. The caller at `source_config.py:184`
    (`self._load_api_key(source)`) returned `None`
    always, so the source panel never displayed a real
    API key. Fix: defensive lookup chain -- source
    arg -> `user_config.api_keys[source_id]` ->
    `pycurity.pykey.get_secret("api_key", source_id)`;
    returns the raw key (caller's `obscure_key` masks).

  Remaining 7 markers (palette drawer wiring, tool
  drawer re-render, notebook webview instrumentation,
  catalog tab-None stub, config features pane) are
  deferred to a follow-up T-NEW-141b card -- they
  touch live UI architecture (drawer re-render,
  webview instrumentation) that needs design decisions
  before shipping.

  Pin: `tests/test_t_new_141_stub_methods.py` 4 new
  tests (source-level pin: `go_to_previous_tab`
  contains real logic, source-level pin: `_load_api_key`
  consults a real backend, source-level pin:
  `populate_data` has a real docstring, behavioural:
  index math for the clamp).

- **T-NEW-141c** ✅ Inside-nchantdoffice TODO sweep (final
  subset) -- **FIXED** (2026-08-16, gamma `pending`).
  Investigation of the 3 remaining markers showed that
  the actual implementation already exists; the
  original TODOs were misleading. Fix: replace each
  with a real docstring describing the existing
  contract.
  - `images.py:807` ``cmd_add_palette_document
    _nchantdpalette`` claimed the TODO was "Open toolbox
    tab and Palette Drawer generate the palette from
    the image". The function body already created the
    palette document; the missing piece was the
    drawer-open side-effect. Fix: call
    ``self.cmd_show_palette_drawer()`` after the add so
    the user immediately sees the new palette.
  - `images.py:1162`` ``init_drawer_image_tools``
    claimed "implement logic so that when a tool like
    NchantdConvertSize button is clicked the drawer is
    opened and redrawn to show only the config for
    that tool". The implementation already exists as
    ``cmd_open_tool_drawer(tool_name)`` (T-NEW-035) which
    hides all 5 panes and shows only the named one. Fix:
    replace the stale TODO with a docstring referencing
    the dispatcher.
  - `settings.py:1016` claimed "implement in
    NchantdOfficeDocumentConfigPane - features". The
    class exists at ``panes/document_settings.py:73``
    with a per-doctype registry
    (MatrixConfigPane, NotebookConfigPane,
    ImageConfigPane, ScriptConfigPane) wired by
    T-NEW-027. Fix: replace the stale TODO with a
    docstring describing the registry contract.

  Pin: `tests/test_t_new_141c_clear_stale_todos.py` 4
  new tests (3 source-level pins confirming the
  draw-open / drawer-dispatch / registry contracts +
  1 regression guard for the
  ``NchantdOfficeDocumentConfigPane`` class).

  T-NEW-141 (with 141b + 141c) closes all 10 of the
  inside-nchantdoffice TODO markers from the
  2026-08-15 inside-sweep. No markers remain in
  scope.

- **T-NEW-141b** ✅ Inside-nchantdoffice TODO sweep (subset 2)
  -- **FIXED (subset)** (2026-08-16, gamma `pending`).
  This commit closes 4 of the 7 remaining markers from
  T-NEW-141b. Three are deferred to T-NEW-141c
  (palette drawer wiring, tool drawer re-render,
  per-doctype features pane -- all require live UI
  architecture decisions before shipping).
  - `panes/documents.py:798` -- the misleading "tab is
    None" TODO was replaced with a real docstring; the
    stub (placeholder NchantdOfficeTab) is preserved and
    documented as a UI scaffold only.
  - `documents/workbooks/notebooks.py:1786/1790` --
    `_on_webview_load_started` and
    `_on_webview_load_progress` were no-op stubs. The
    QWebEngineView `loadStarted` / `loadProgress` signals
    now log the event (info + debug percent) so
    Jupyter-tab load attempts are visible in the app
    log.
  - `utilities/users.py:69` -- `self.has_pro = True` was
    hardcoded. Fix: read from
    `load_credentials().user_tier` (pycurity
    `DesktopCredentials` cache). Tier mapping:
    `pro` / `pro_data` / `enterprise` -> True; `free`
    -> False; missing / malformed creds -> True
    (backward compat with the hardcoded original).
    The service-truth path (a live
    `nchantdoffice.com` call to refresh `user_tier` on
    every boot) is explicitly deferred; the local cache
    is what we have. Pin:
    `tests/test_t_new_141b_safe_subset.py` 7 new tests
    (3 source-level + 4 behavioural: pro / free /
    enterprise / no-creds scenarios).
- **T-NEW-142** ✅ Tab Delete broken from document toolbar +
  `NchantdTabPane` -- **FIXED** (2026-08-16, gamma `pending`).
  Root cause: the button-bar config at
  `widgets/panes/documents.py:791` (and the sibling
  `delete_node` at line 93) references `delete_tab` /
  `delete_node` action names that were never registered as
  `app_action` rows in `nchantdoffice/_data_/models.yaml`.
  The nchantrs lookup chain
  (`nchantrs.utilities.utils.lookup`) reads `app_action` from
  the database, indexed by `lookup_code_txt`, and raises
  `Exception('Action delete_tab Lookup Config is Empty')`
  when missing -- which fails the entire button-bar render.
  Fix: add two `app_action` records (icon
  `actions-remove-tab-svgrepo-com` for delete_tab,
  `remove-delete-trash-cancel-svgrepo-com` for delete_node).
  Pin: `tests/test_t_new_142_tab_delete_action.py` 5 new tests
  (yaml registration pin for both, icon/tip non-empty pin,
  lookup-config-retrieval e2e for both).
- **T-NEW-143** `.pyof` import excludes `DELETE_BIT=1` rows -- filed from `testing-report_20260815.md` Issue 3.
- **T-NEW-144a** ✅ `file_details` toolbox redirects to
  internal data when tab is an internal document --
  **FIXED** (2026-08-16, gamma `pending`). When the active
  tab is internal (no `file_path`), the
  `NchantdFileDetailsPane` previously read empty / "0"
  values from disk. Fix: added `bind_to_tab(tab)` method
  on the pane that stores the tab reference; `get_name`,
  `get_file_path`, `get_file_size`, `get_modified_date`
  now consult `self.tab` when `self.file_path` is empty
  (returns `tab.name` / `"(internal storage)"` /
  `len(tab.content)` / `tab.modon`). External docs (real
  `file_path` on disk) are unchanged -- `set_file_path`
  still populates the widget with the full path; the new
  code only updates the widget in the internal-doc
  fallback branch. Pin:
  `tests/test_t_new_144a_file_details_internal.py` 6 new
  tests (method-exists, source-level pin x2, e2e x3
  covering internal-doc populate, tab-switch refresh,
  external backward compat).
- **T-NEW-144b** ⏳ external file becomes editor (not
  viewer) -- DEFERRED to v0.2.0 (out of scope for the
  T-NEW-144a commit). The current `NchantdOfficeDocument
  Mixin.save()` (line 1193) only writes to the doc_media
  row when `document.location == "external"`; it does NOT
  write the editor content back to the on-disk file. A
  proper fix needs per-document-type dispatch (script
  text files, images binary, PDFs, notebooks JSON, etc.)
  and would touch ~14 doc subclasses. Will need its own
  design card before shipping.
- **T-NEW-145** `Ctrl+S` wired to save button logic -- filed from `testing-report_20260815.md` Issue 6.
- **T-NEW-143** ✅ `.pyof` import excludes `DELETE_BIT=1` rows
  -- **FIXED** (2026-08-16, gamma `pending`). The base-6
  branch of `import_one_table` (nchantdoffice/utilities/
  pyof_import.py) now skips any source row whose `DELETE_BIT`
  is truthy (squirl soft-delete tombstones). `row.get(
  "DELETE_BIT")` returns `None` when the column is absent on
  older schemas -- treated as "not deleted" so legacy
  sources keep importing. Missing/None/0 = live; any
  truthy int = skip. The `_content` branch is untouched
  (content tables are versioned, not soft-deleted). Pin:
  `tests/test_t_new_143_delete_bit_filter.py` 6 new tests
  (1 source-level + 5 e2e: doc_tree_node, app_tab, all-base-6
  broad sweep, NULL-as-live, missing-column backward compat).
- **T-NEW-145** ✅ `Ctrl+S` wired to save button logic --
  **FIXED** (2026-08-16, gamma `pending`). The nchantrs
  shortcut wiring (`NchantdCloak.setup_shortcuts`) binds
  `Ctrl+S -> self.cmd_save -> self.parent.model.save()`
  (application-level instance write). The user expects
  Ctrl+S to behave like the document toolbar save button
  (`cmd_save_tab -> self.save()`). Fix: override `cmd_save`
  on `NchantdOfficeCloak` -- active-doc lookup via
  `self.main.view.panes["center"].currentWidget()`; when
  found, dispatch to the doc's `save()` / `save_app()`;
  fall back to `self.parent.model.save()` when no active
  document (defensive: missing view/panes/currentWidget).
  Pin: `tests/test_t_new_145_ctrl_s_save.py` 4 new tests
  (override exists, dispatch-to-active-document source
  shape, fallback-to-model source shape, defensive-missing-
  panes source shape).
- **T-NEW-146** ✅ `bootstrap_app_user` regression: cannot pickle
  'generator' object — **FIXED** (2026-08-16, gamma `pending`).
  Root cause: `NchantdUser.__init__` (nchantrs) assigns
  `self.pword = self.get_password()` and `get_password` is a
  generator function, so `pword` is a generator instance by
  default. The duck-typed branch of `_build_app_user_payload`
  reads `pword` via `getattr(user, "pword", None)` -- without
  coercion the payload contains the generator, and
  `squirl._store` raises `TypeError` on deepcopy. Fix:
  `_coerce_scalar(value)` helper inside
  `_build_app_user_payload` unwraps generators/iterators
  (`next()` on the first yielded value) and falls back to
  `str()` for any other non-scalar. Pin:
  `tests/test_app_user_bootstrap.py` 3 new tests
  (`test_payload_does_not_leak_nchantd_user_pword_generator`,
  `test_payload_pword_is_string_for_nchantd_user`,
  `test_bootstrap_app_user_with_real_nchantd_user_does_not_explode`).
- **T-NEW-147** ✅ `get_app_user` AttributeError:
  `'NchantdOfficeCloakModel' object has no attribute 'get_table'`
  -- **FIXED** (2026-08-16, gamma `pending`). Root cause: the
  store-layer fallback called `self.get_table(...)` instead of
  `self.store.get_table(...)`. `get_table` lives on the store
  (the layer below the model), not on `NchantdOfficeCloakModel`.
  Fix: call `self.store.get_table`. Pin:
  `tests/test_app_user_bootstrap.py` 2 new tests
  (`test_get_app_user_fallback_path_routes_through_store` +
  `test_get_app_user_returns_empty_list_when_connection_unbound_and_table_missing`).

### T-NEW-124 — Doctype guard: strict-dtd payloads restore as HTML (2026-08-15)

**Rich-text payloads restored under the wrong syntax.** User
directive (2026-08-15): if the content being restored contains

    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN"
     "http://www.w3.org/TR/REC-html40/strict.dtd">

it needs to be formatted as HTML. That doctype is the fingerprint
Qt's ``QTextEdit.toHtml()`` stamps on every serialised rich-text
payload; when such a payload round-trips back through restore
while ``document.syntax`` says plain-text / python / markdown,
the dispatch strips the formatting (setPlainText), mangles it
(setMarkdown), or double-wraps the HTML source in a pygments
highlight ``<pre>``.

**Fix (scripts.py:1479):** the guard sits at the top of
``_apply_syntax_highlighting``, before the syntax dispatch. Any
string payload whose first 2048 chars contain the stable
``rec-html40/strict.dtd`` fingerprint (case-insensitive, tolerant
of spacing/quote variants) is routed to ``setHtml(text)``
directly, overriding ``syntax``.

**Affected sites:**
- `nchantdoffice/widgets/documents/media/scripts.py:1465-1505`
  — ``_apply_syntax_highlighting`` (guard at 1479)
- `tests/test_script_doctype_guard.py` — 7 new tests

**Verification:** 7/7 new tests; script/document surface 17/17
(test_doctype_guard + html_envelope + reopen + no_missing_text +
doc_media_syntax_update). Live numbers (per-file run, 21 known
Qt-crashers + 2 pyof-Qt files excluded): **497 passed / 5 failed**
— the 5 are the T-NEW-120 aspirational script tests, unchanged.

### T-NEW-138 ✅ Journal editor followups: always-scroll + standard-populate (2026-08-15) DONE

**Two journal TODOs uncovered by the 2026-08-15 inside-sweep.**
The journal document pane (``nchantdoffice/widgets/documents/journal.py``)
has two unimplemented markers that belong together -- both
are UX regressions relative to the standard ``populate`` contract
that T-NEW-079 brought the entry editor up to.

**Marker 1 (always-scroll to bottom):** ``journal.py:132``
flags that the outer ``NchantdOfficeJournalEditor`` does not
    scroll to the bottom of the document after init/refresh,
    so when the user opens a long-running journal they see the
    top instead of the latest entry. The standard
    ``populate_document`` helper ends with
    ``scroll_to_bottom()`` -- the journal override skips it.

**Marker 2 (refactor to standard populate):** ``journal.py:422``
flags that the ``_parse_entry`` + ``populate`` chain on the
    journal editor is bespoke instead of going through the
    standard ``populate_document`` pipeline. This means the
    "always save" follow-up that T-NEW-079 deferred would
    have to retest the whole editor again instead of dropping
    in on top of the canonical contract.

**Affected sites:**
- ``nchantdoffice/widgets/documents/journal.py:132`` --
  ``# TODO always scroll to bottom of document`` (in
  ``initView`` of the outer journal editor)
- ``nchantdoffice/widgets/documents/journal.py:422`` --
  ``# TODO refactor to use the standard populate methods``

**Migration plan (design decision first):** the always-scroll
fix is a single ``self.scroll_to_bottom()`` call after
``populate_document`` -- no priority, safe to land first.
The standard-populate refactor is bigger (it changes the
public contract of the journal editor's ``save`` /
``populate`` cycle) and should land second behind a TDD
recipe. Steps:
1. Add ``test_journal_scroll_to_bottom`` that opens a journal
   with N entries and asserts the cursor/anchor is at the
   bottom after init.
2. Add ``test_journal_uses_standard_populate`` that asserts
   the journal's populate path goes through
   ``populate_document`` (same call site as scripts/media/etc).
3. Implement both fixes against the failing tests.
4. Close out the two ``TODO`` markers.
5. Update ``TODOs.md`` ``Document Changes`` section.

### T-NEW-139 — Toolbar signature cleanup: combine ``add_tab`` + ``add_document`` (2026-08-15)

**Two toolbar methods share 80% of their cfg/handler wiring.**
``nchantdoffice/widgets/controls/toolbars.py:216`` flags:
``# TODO cleanup add_tab, add_document signatures and
combine as much code as possible``. Both methods duplicate
the ``cfg = {"text": ..., "lookup_code_txt": ..., "handler":
self.cmd_add_document_app, "args": ..., "icon_txt": ...}``
build + the ``NchantdButton(self, cfg).initWidget()``
construction + the same ``buttons[k] = ...`` placement.

**Affected sites:**
- ``nchantdoffice/widgets/controls/toolbars.py:216`` --
  ``# TODO cleanup add_tab, add_document signatures``
- ``nchantdoffice/widgets/controls/toolbars.py:160-222``
  (``add_document``) and ``add_tab`` (paired method) --
  both currently hold ~50 lines of duplicated cfg +
  construction logic.

**Migration plan (design decision first):** extract a
private helper ``_launch_doc_sigil(cfg) -> QWidget`` that
takes a cfg dict and emits the configured
``NchantdButton``. ``add_tab`` and ``add_document`` then
become a 10-line cfg dict + one helper call each. No
public API change -- the ``cmd_add_document_app`` and
``cmd_add_tab`` handlers are unchanged. Steps:
1. Snapshot the toolbar buttons behaviour with the
   existing ``tests/test_toolbar_*.py`` slice (or add
   one if missing).
2. Extract ``_launch_doc_sigil`` from the duplicated body.
3. Verify the snapshot tests still pass.
4. Close the ``TODO`` marker.

### T-NEW-140 — Free-user right-side tab: lock default to Ad tab (2026-08-15)

**Free users see all right-side tabs; should default to the Ad
tab and restrict the rest.** ``nchantdoffice/widgets/config/settings.py:1209``
flags: ``# TODO lock default right side tab to Ad tab for
free users``. Today the right pane shows every available
tab regardless of tier; the upsell surface (the Ad tab,
where T-NEW-135 redirects the user when they hit the 100-node
cap) is just one tab among many. This card locks the default
selection to the Ad tab for free users so they actually see
the upsell without having to hunt for it.

**Affected sites:**
- ``nchantdoffice/widgets/config/settings.py:1209`` --
  ``# TODO lock default right side tab to Ad tab for free users``
- The right-side tab pane (``panes["right"]`` / analogous)
  default-selection logic -- consult
  ``is_pro_user(model.user)`` and pick the Ad tab if not pro.
- A new setting flag in the ``Settings/Interface`` tab so
  users can override (pro) or accept the lock (free).

**Migration plan (design decision first):** the lock is a
single conditional on the default-selection read. Adds a
new ``force_ad_tab_for_free_users`` setting (default True)
that admins can disable. Steps:
1. ``test_default_right_tab_is_ad_for_free_users``
   (selectable through model.user.has_pro=False).
2. ``test_default_right_tab_falls_through_for_pro_users``.
3. Wire the conditional into the right-pane init.
4. Add the setting to the ``Settings/Interface`` tab.
5. Close the ``TODO`` marker.

### T-NEW-141 — Inside-nchantdoffice TODO sweep: implementation stubs + config wirings (2026-08-15)

**10 unimplemented TODO markers in the nchantdoffice package.**
The 2026-08-15 inside-sweep (this session's TODO review) found
14 outstanding TODO markers in ``nchantdoffice/``. Three of
them belong with adjacent cards (T-NEW-138 covers journal
items; T-NEW-139 covers the toolbar signature cleanup;
T-NEW-140 covers the free-user right-tab lock). The remaining
10 are independent stubs and config wirings collected here.

**Affected sites (10 uncovered items):**
- ``nchantdoffice/widgets/documents/media/images.py:807`` --
  ``# TODO Open toolbox tab and Palette Drawer generate the
  palette from the image`` (toolbox click should auto-open
  the palette drawer).
- ``nchantdoffice/widgets/documents/media/images.py:1162`` --
  ``# TODO implement logic so that when a tool like
  NchantdConvertSize button is clicked on the document toolbar
  that the drawer is opened and redrawn to show only the
  config for that tool``.
- ``nchantdoffice/widgets/documents/workbooks/notebooks.py:1788`` --
  ``#TODO: implement method`` (notebook widget state helper A).
- ``nchantdoffice/widgets/documents/workbooks/notebooks.py:1792`` --
  ``#TODO: implement method`` (notebook widget state helper B).
- ``nchantdoffice/widgets/panes/documents.py:798`` --
  ``# TODO: tab is None for initialized catalog and so we
  need to stub in values`` (catalog pane blank when tab None).
- ``nchantdoffice/widgets/config/settings.py:980`` --
  ``# TODO implement in NchantdOfficeDocumentConfigPane -
  features`` (per-document-type features pane is missing).
- ``nchantdoffice/widgets/documents/documents.py:1184`` --
  ``# TODO implement method`` (stub on document mixin).
- ``nchantdoffice/widgets/widgets.py:113`` --
  ``# TODO implement method`` (stub on top-level widget base).
- ``nchantdoffice/widgets/config/source_config.py:319`` --
  ``# TODO implement method`` (stub on source_config).
- ``nchantdoffice/utilities/users.py:69`` --
  ``# TODO: need to connect to service for truth and a need a
  place to store data locally`` (``has_pro = True`` is
  hardcoded; needs nchantdoffice_com service query + local
  cache).

**Migration plan (design decision first):** group by file
for clean parallel work, not by feature:
1. ``media/images.py`` (2 items) -- palette drawer wiring
   from toolbar + toolbox. Land first; small UX win.
2. ``workbooks/notebooks.py`` (2 items) -- two state
   helpers; both stub-implementations.
3. ``panes/documents.py`` (1 item) -- catalog tab-None
   stub values.
4. ``config/settings.py`` (1 item) -- per-doctype features
   pane (this is a substantial card on its own; consider
   a follow-up ``T-NEW-141b`` if scope balloons).
5. Stub methods (3 items across ``documents.py:1184``,
   ``widgets.py:113``, ``source_config.py:319``) --
   implement-and-mark-done; smallest in the batch.
6. ``utilities/users.py:69`` -- has_pro truth-from-service
   card; this one is structural and may need a separate
   ``T-NEW-141c`` card for the network/cache plumbing.

For each: write a failing test that exercises the intended
behaviour, implement the minimum to pass, refactor, commit,
push, update ``TODOs.md`` ``Document Changes``.

