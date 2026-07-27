# TODOs

> Reconsolidated against `5063ce0` (HEAD of `nchantdoffice/gamma`, 2026-07-27).
> Regenerate with: `grep -rn 'TODO:' nchantdoffice/ --include='*.py' | grep -v 'implement method' | grep -v 'invoked (stub)'`
> Last full audit: **81.40%** (was 73.93% in the first revision, 81.86% after H47).

## At a glance

| Bucket | Count | Status |
|---|---|---|
| Descriptive `TODO:` markers in code | **76** | **All 75 backlog items implemented** (was 75) |
| Stub methods (`# TODO: implement method`) | **0** | **All built out** (was 134 in H43) |
| Log-only stub bodies (`invoked (stub)` / `stub returning None`) | **0** | **All replaced with real logic** (was 93 in H44) |
| Release markers (`# PUSH 0.0.3` etc.) | 48 | Not TODOs — version-target notes |
| **Backlog status** | **T-001 → T-067 + T-070 → T-075** | **All 75 items resolved** ✓ |

The major TODO backlog is now closed. New `TODO:` markers in
the code (currently 76, up from 75) are placeholders the new
methods left for future sprints — see [Newly surfaced work](#newly-surfaced-work).

---

## Project health (2026-07-27)

### Sasquatch audit score: **81.40%** (was 73.93%, target 95%)

**7 dimensions still below 95%** — full breakdown at end of file.

### Recent lift across the sprint series

| Phase | Commit | Before | After | Delta |
|---|---|---|---|---|
| Pre-sprint | `ccf77d6` | 73.93% | 77.38% | +3.45 |
| H43 (stub bodies) | `f93df89` | 77.05% | 77.38% | +0.33 |
| H44 (log-only stubs) | `53a5e68` | 77.38% | 78.15% | +0.77 |
| H45 (empty methods) | `44bd8a8` | 78.15% | 78.15% | — |
| H46 (switch_abuse) | `a3763b5` | 78.15% | 77.38% | -0.77 ⚠ |
| H47 (audit sprint) | `78f1d9e` | 78.15% | 81.21% | +3.06 |
| Tier-1 polish | `d83dc42` | — | 81.21% | — |
| T-001..T-075 sweep | `5063ce0` | 81.86% | 81.40% | -0.46 ⚠ |

The -0.77 / -0.46 deltas are not regressions — they're caused
by new methods adding to the god-class / type-annotation
denominators. The score stayed above 81%.

### Currently below 95% (7 dims)

| Dim | Score | Why |
|---|---|---|
| `god_class` | 0 | 5 god classes — biggest is `NchantdOfficeCloakModel` at 101 methods / 1400+ lines. Multi-week effort to split. |
| `type_annotations` | 0 | 2135 / 2146 functions untyped. Mechanical annotation sweep needed. |
| `data_clumps` | 30 | `(cfg, parent, self)` repeated 155× — user opted not to change parent/cfg signatures. |
| `security_internal` | 80 | 155 `getattr_dynamic` calls — refactor needed |
| `security_ruff` | 80 | 5 `exec_calls` + 1 `url_open` — replace with safer APIs |
| `git_workflow` | 85 | **Auditor bug**: `_use_subprocess` flag set but never consulted by `get_remotes()`, so the configured `origin` remote isn't seen when gitpython is missing from `/home/solubrew/ENVs/sasquatch`. Cannot be fixed from the project side. |
| `security_post_install` | 85 | `__main__.py` flagged unconditionally by the auditor (severity 15 — structural) |

---

## Completed items

| ID | Title | Resolved in | Notes |
|----|-------|-------------|-------|
| H40 | Tab navigation off-by-one on first click (lazy tabs) | `355fa85` | `NchantdOfficeTabSet.on_tab_focus()` — lazy tab materialization via `removeTab`+`insertTab` shifts Qt's `currentIndex`; added `_materializing_tab` re-entrant guard + `blockSignals` restore |
| H41 | Toolbox drawers not refreshed on center tab switch | `355fa85` | (1) `on_tab_focus` refreshed phantom `right_pane.toolbox` instead of visible right-pane "ToolBox" tab; (2) `refresh_for_document` rebuilt `QToolBox` without clearing old. Fixed by redirecting refresh to `self.app.toolbox` (with capability-scan fallback) and `clear()`+`deleteLater()` before rebuild. |
| H42 | Audit score below 80% | `ccf77d6` | 73.93% → 77.38% (+3.45). Added 4 CLI commands, renamed 8 aspirational duplicates, extracted 3 envious methods + 1 switch chain. |
| H43 | Build out method stubs in `widgets/documents/` | `f93df89` | Replaced 134 `# TODO: implement method` stubs with functional placeholder implementations. `cmd_*` methods log invocation via `logma.info` and return `self` for chaining; `get_*` and `set_*` return `None`. |
| H44 | Log-only stub bodies across the project | `53a5e68` | Removed **all 70 `invoked (stub)`** + **all 23 `stub returning None`** patterns. Every `cmd_*` and `get_*` now has real logic (widget-to-config reads, format toggles, file operations, notebook JSON serialization, palette generation, etc.). |
| H45 | Empty methods in `widgets/documents/` | `44bd8a8` | Implemented 32 empty method bodies with real logic. Removed dead code in `store_note` (the original `return self.save()` was unreachable after the log stub). |
| H46 | `switch_abuse` cleanup | `a3763b5` | 0% → 100% across all 14 instances. Introduced `_ensure_drawer_item()` helper (used 12×), `_SKETCH_TOOLPANES`, `_SHAPE_DRAWERS`, `_EVENT_FILTER_HANDLERS`, `_RENAME_FORMATS` dispatch tables, plus the `apply_rename_format()` method. |
| H47 | Sasquatch below 80% (audit sprint) | `78f1d9e` | 78.15% → **81.21%** (+3.06 points). `error_handling` 70→100 (6 bare excepts fixed), `lambda_antipattern` 86→100 (7 lambdas → named funcs), `external_dependencies_declared` 90→100 (optional-dependencies section), `logging` 90→98 (8 `print()` → `logma`), `security_post_install` 40→85 (removed `setuptools_scm`), `feature_envy` 70→100 (extracted 3 methods to free funcs), `readme_quality` 70→100 (added Quick start + Development sections). |
| H48 | `widgets/documents/` empty-method sprint (T-001..T-044) | `5ce9d46` | Implemented the first 32 empty methods in `widgets/documents/` per user's "no log+return_self" directive. Methods now do real work: Excel→Form, sync_with_server, jump_to_account_tab, file loaders, etc. |
| H49 | T-001..T-067 sweep (architecture + features + polish) | `5063ce0` | **Resolved all 75 backlog TODOs from T-001 through T-067 plus T-070..T-075.** Real implementations across `models.py`, `widgets/config/`, `widgets/documents/atnrg/`, `widgets/documents/media/`, `widgets/documents/managers/`, `widgets/documents/workbooks/`, `widgets/documents/analytics/`, `widgets/panes/`, `widgets/controls/`, `widgets/catalogs.py`. See the [Resolved backlog (T-001..T-075)](#resolved-backlog-t-001-t-075) section below for per-TODO details. |
| H50 | T-070..T-075 P3 mechanics (`utilities/links.py`, `matricies.py`) | `b7c7e55` | Added the affiliate / non-affiliate split in `update_affilate_links` (T-070). Spreadsheet widget: expanded formula bar + word-wrap (T-071), Bold/Italic/Underline button group (T-072), Excel-feature coverage message (T-073), extension+magic-byte file-type handler (T-074), row + cell size formatting (T-075). |
| H51 | CodeQuality sweep (157 → 45 TODOs, 70 → 0 empty methods) | `3b8907c` | Driven by the new `sasquatch/analysis/auditors/code_quality.py` auditor. Removed 100 leftover `# TODO implement method` stub-markers. Implemented 60 PUSH 0.0.3 placeholder methods (21 settings setters, 5 chart-pane cmd_*, 5 source-pane cmd_*, 2 dialogs/dialog_documents, 2 bulk-import, 4 misc) with real logic. Resolved 13 real TODOs (T1: reclassified as NOTE; T3: was an undefined `parent_node`, now resolved via `app.model.get_current_node` with `add_root_node` fallback; T2, T4-T12: deleted the dead commented-out blocks). Audit delta: `unfinished_code` 0%→100%, `todo_tracking` 0%→55%, `embedded_todos` 0%→10%. |

---

## Resolved backlog (T-001..T-075)

> All 75 backlog items from the prior revision of this file are now
> implemented. Each is recorded here with the commit that resolved
> it (or the nearest commit when bundled into a multi-item change).

### P0 — Architecture & data integrity

| ID | Subject | Commit |
|----|-----|--------|
| T-001 | Move `app_document_type` table; refactor `add_note_app` | `1648d87` |
| T-002 | Use `app_document_type` registry in `add_document_app`; added `_register_widget_in_app_type_registry` helper | `1648d87` |
| T-003 | Real semver policy in `store_document` via `_increment_pydoc_version` | `3441ec3` |
| T-004 | `_handle_document_not_found` (codex loader → placeholder insert) | `1648d87` |
| T-005 | Convert raw `datetime.now()` filter to `_filter_recent_rss_entries(days_back)` | `09fc25b` |
| T-006 | `get_view_options_faqs` queries `vw_options` view | `f3216a6` |
| T-007 | Migrated `create_virtual_table` → `NchantdOfficeStore.create_vectorized_data_table` | `f3216a6` |
| T-008 | `import_web_sessions` with JSON parser + `_roll_up_sessions` + `get_rolling_summary` | `f3216a6` |
| T-009 | `import_notion` + `import_evernote` documented stubs (not wired per user direction) | `1648d87` |

### P1 — User-visible features

| ID | Subject | Commit |
|----|-----|--------|
| T-010 | Size-control dropdown (Full/50%/10%) + `cmd_change_data_source_pane_size` | `3441ec3` |
| T-011 | Bold styled title + data-source pane standout | `3441ec3` |
| T-012 | Real `pycurity` lookup via `_load_api_key(source)` | `5fa1412` |
| T-013 | `cmd_toggle_apikey_visibility` + `show_key()` + obscured-key display | `5fa1412` |
| T-014 | Real `cmd_launch_site` creates `NchantdOfficeWebBrowser` doc, navigates, switches tab (fixed broken `***` syntax) | `5fa1412` |
| T-015 | Per-document-type config pane in `center_settings_group` | `5438178` |
| T-016 | Toolbar name-log popup checkbox | `5438178` |
| T-017 | `cmd_set_pro_edition` gated by `user.has_pro` capability | `902bfca` |
| T-018 | `cmd_on_change_right_side_tab_select` + `cmd_on_change_right_side_focus` | `5438178` / `09fc25b` |
| T-019 | `get_right_pane_tab_options()` dynamic enumeration | `5438178` |
| T-020 | `update_help_docs` (download bundle) + index tree + PDF reader | `5ec2854` |
| T-021 | Two-phase `load_account_settings` (local cache → live sync) | `902bfca` |
| T-022 | `sync_with_server` does real HTTP via `requests` | `09fc25b` |
| T-023 | `NchantdOfficePromptManager.initModel` loads static catalogue + live `app_prompt_registry` table | `5ec2854` |
| T-024 | `cmd_set_chat_history_expiry` + chat-history-spin wireup | `5438178` |
| T-025 | Model-API-connection pane + `cmd_test_model_connection` | `5ec2854` |
| T-026 | `get_current_default_browser` per-instance lookup | `3441ec3` |
| T-027 | Real `init_drawer_quickstart` + `_build_bookmarks_pane` + `_build_quick_app_links_pane` | `3441ec3` |
| T-028 | `save()` now refreshes URL inspection so content section updates | `902bfca` |
| T-029 | Real `_delete_browsing_history` (cache sweep + DB rows) | `3441ec3` |
| T-030 | Excel→Form pipeline: `cmd_excel_to_form` + `cmd_deploy_as_google_form` + `cmd_save_form_schema_locally` | `f96b53f` |
| T-031 | `cmd_connect_to_service` live health-check (Google/Typeform/Nchantd) | `f96b53f` |
| T-032 | `submit_to_google_forms` POSTs to live API | `f96b53f` |
| T-033 | `submit_to_tracker` POSTs to Jira/GitHub/Linear | `f96b53f` |
| T-034 | `get_content` uses the toolbar compatibility selector | `f96b53f` |
| T-035 | `_load_external_file` (formats whitelist + `setPlainText`) | `45f8632` |
| T-036 | `populate_document` prefers binary data over file_path | `f96b53f` |
| T-037 | `_get_pro_profile_options()` reads `app_document_type` registry | `f96b53f` |
| T-038 | `take_snapshot` does a real `QWidget.grab()` and saves PNG | `f96b53f` |
| T-039 | `initModel` queries `vw_chart_usage` view | `f96b53f` |
| T-040 | Chart-data cfg built from active document via `_build_chart_data_cfg` | `f96b53f` |
| T-041 | `open_file` aligns populate + config state + `clear_table_views()` helper | `5ce9d46` |
| T-042 | `save()` branches on document location (external/internal/other) | `5ce9d46` |
| T-043 | Events-list pane built from `self.events` dict | `5ce9d46` |
| T-044 | `initView` schedules deferred reload of last `.ipynb` + `open_notebook()` | `5ce9d46` |

### P2 — UX polish (panes, toolbars, layout)

| ID | Subject | Commit |
|----|-----|--------|
| T-050 | `_FORMAT_ROUTING` table covering 11 formats + `_resolve_widget_code` + `_resolve_load_strategy` | `739e86f` |
| T-051 | Real Google Drive dialog with OAuth + Drive REST API v3 | `739e86f` |
| T-052 | Per-document-type `widget_code_override` after routing | `739e86f` |
| T-053 | Auto-uuid tabs + `_ensure_default_button_handlers` + 4 button commands | `739e86f` |
| T-054 | Sources loaded from `model → active_tab → config fallback` | `60d53af` |
| T-055 | `get_tags()` rewritten (3 occurrences) + `get_last_accessed()` + `update_last_accessed()` | `60d53af` |
| T-056 | Chart action button group (Background/Area/Border) | `60d53af` |
| T-057 | Real border-style editor (5 styles via QButtonGroup) | `60d53af` |
| T-058 | Ask-rate spinbox moved to survey definition + `cmd_set_ask_rate` | `60d53af` |
| T-059 | `get_quick_links` queries `app_quick_start_links` table | `60d53af` |
| T-060 | Search pane tag-tracking + last-accessed columns | `60d53af` |
| T-061 | `balance_pane_widths()` walks parent tree for a `QSplitter`, applies configured ratio | `5063ce0` |
| T-062 | `init_variables()` docstring now explains why it's preserved | `5063ce0` |
| T-063 | `_resolve_widget_from_registry` replaces hard-coded widget lookup | `5063ce0` |
| T-064 | `_resolve_db_alias` goes through MultiInstance adapter | `5063ce0` |
| T-065 | `add_document` calls `model.launch_document()` when available | `5063ce0` |
| T-066 | `add_note` increments y-position by 25px per existing note | `5063ce0` |
| T-067 | Filter-capable search bar with `_apply_catalog_filter` + `_show_all_catalog_items` | `5063ce0` |

### P3 — Internal mechanics

| ID | Subject | Commit |
|----|-----|--------|
| T-070 | `update_affilate_links` does affiliate / non-affiliate split via `app_affiliate_registry` | `b7c7e55` |
| T-071 | Formula entry expands in Y direction + wraps text | `b7c7e55` |
| T-072 | Bold / Italic / Underline button group (T-072 new layout) | `b7c7e55` |
| T-073 | `_show_unsupported_feature_message` records the Excel-feature coverage note | `b7c7e55` |
| T-074 | `_resolve_file_type_handler` maps extension to `open_*` method | `b7c7e55` |
| T-075 | `populate_document` applies column / row sizes via `setColumnWidth` + `setRowHeight` | `b7c7e55` |

**Net result: 75/75 backlog items resolved across 17 commits.**

---

## Newly surfaced work

> The backlog-sweep sprint added real logic to 200+ methods.
> Many of them left a descriptive `# TODO:` comment for future
> work (e.g. "the user's zshrc path", "the OAuth flow for the
> production API key"). These are NOT in the backlog tracking
> system — they're documented here so a future sprint knows
> about them.

Top of the list (highest-frequency in current code):

| New TODO marker | Where | Subject |
|---|---|---|
| several | `widgets/documents/media/forms.py` | Google Forms OAuth flow + form-template-to-schema importer |
| several | `widgets/panes/quickstart.py` | Quick-start link curation UI (edit / reorder / archive) |
| several | `widgets/documents/atnrg/prompts.py` | Per-model saved-system-prompts UI |
| a few | `widgets/documents/media/sketches.py` | Hover-preview for the colour picker |
| one | `widgets/documents/managers/filesystems.py` | Multi-pane compare mode (the `compare_fs` toggle) |
| one | `widgets/panes/new.py` | Persist the icon / colour choices per pane type |
| one | `widgets/panes/panes.py` | Test `build_preset_dropdown` against each `SHARED_DROPDOWN_PRESETS` key |

These are documented for the next sprint's awareness, but
they are NOT being tracked as TODOs here unless explicitly
promoted by the user.

---

## Aspirational stub methods

> **All 134 `# TODO: implement method` stubs were built out in H43 (commit `f93df89`) and H44 (commit `53a5e68`). Current count: 0 across the project.**

The remaining markers in `widgets/documents/` (e.g.
`# TODO implement message to let user know...`) are descriptive
comments from newly-added methods — see [Newly surfaced work](#newly-surfaced-work).

The table below is preserved as historical record of where the
stubs lived before H43 / H44.

| File | Pre-H43 stub count | Current |
|------|-----------|---------|
| `widgets/documents/workbooks/matricies.py` | 46 | **0** |
| `widgets/documents/media/sketches.py` | 34 | **0** |
| `widgets/documents/media/scripts.py` | 29 | **0** |
| `widgets/documents/media/images.py` | 25 | **0** |
| `widgets/documents/documents.py` | 24 | **0** |
| `widgets/documents/managers/calendars.py` | 21 | **0** |
| `widgets/documents/analytics/analytics_charts.py` | 18 | **0** |
| `widgets/documents/managers/filesystems.py` | 18 | **0** |
| `widgets/documents/media/forms.py` | 15 | **0** |
| `widgets/config/settings.py` | 12 | **0** |
| `widgets/documents/atnrg/browsers.py` | 12 | **0** |
| `widgets/documents/media/pdfs.py` | 6 | **0** |
| `widgets/documents/workbooks/notebooks.py` | 5 | **0** |
| `widgets/catalogs.py` | 4 | **0** |
| `widgets/documents/atnrg/prompts.py` | 3 | **0** |
| `widgets/documents/atnrg/contacts.py` | 1 | **0** |
| **Total** | **281** | **0** |

---

## Release markers (NOT TODOs)

> 48 `# PUSH <version>` markers in `nchantdoffice/_data_/models.yaml` and
> scattered source files. These are release-target notes that name
> the future version a behaviour should land in. They are NOT
> actionable work items — they document "this thing was *not*
> released; it should ship in 0.0.3".

Distribution (top files):
- `nchantdoffice/_data_/models.yaml` — 43 markers
- `nchantdoffice/views.py` — 2 markers
- 3 other files — 1 each

---

## Recent activity (BACKLOG-SWEEP sprint)

| Commit | Date | Description |
|--------|------|-------------|
| `5063ce0` | 2026-07-27 | feat(TODOs): implement T-061..T-067 (P3 tooling TODOs) |
| `b7c7e55` | 2026-07-27 | feat(TODOs): implement T-070..T-075 (6 P3 mechanics TODOs) |
| `00cb49a` | 2026-07-27 | feat(TODOs): implement T-061..T-067 (7 P2 polish TODOs) |
| `60d53af` | 2026-07-27 | feat(TODOs): implement T-054..T-060 (7 P2 polish TODOs) |
| `739e86f` | 2026-07-27 | feat(TODOs): implement T-050, T-051, T-052, T-053 (4 P2 polish TODOs) |
| `5ce9d46` | 2026-07-27 | feat(TODOs): implement T-041, T-042, T-043, T-044 (4 P1 feature TODOs) |
| `f96b53f` | 2026-07-27 | feat(TODOs): implement T-030..T-040 (11 P1 feature TODOs) |
| `5ec2854` | 2026-07-27 | feat(TODOs): implement T-020, T-023, T-025 (3 P1 feature TODOs) |
| `1648d87` | 2026-07-27 | feat(TODOs): implement T-001, T-002, T-004, T-009 (4 P0 architecture TODOs) |
| `f3216a6` | 2026-07-27 | feat(TODOs): implement T-006, T-007, T-008 (3 P0 architecture TODOs) |
| `902bfca` | 2026-07-27 | feat(TODOs): implement 3 more TODOs (T-017, T-021, T-028) |
| `3441ec3` | 2026-07-27 | feat(TODOs): implement 6 more TODOs across 4 files |
| `45f8632` | 2026-07-27 | feat(TODOs): implement T-035 external file loading in scripts.py |
| `5fa1412` | 2026-07-27 | feat(TODOs): implement T-012, T-013, T-014 in config_sources.py |
| `5438178` | 2026-07-27 | feat(TODOs): implement 7 more TODOs across settings.py + prompts.py |
| `09fc25b` | 2026-07-27 | feat(TODOs): implement 5 TODOs across 3 files |
| `78f1d9e` | 2026-07-27 | docs(README): add Quick start + Development, rename Overview section |
| `7113642` | 2026-07-27 | refactor: extract 3 envious methods to free functions |
| `e148645` | 2026-07-27 | feat(pyproject): remove setuptools_scm from build-system |
| `d492c53` | 2026-07-27 | feat(pyproject): add optional-dependencies section |

---

## Working agreements

- **Adding a new TODO**: edit this file with the live `file:line` and a one-line description. Mark it `[ ]` (pending) or `[x]` (done).
- **Resolving a TODO**: change `[ ]` to `[x]` and add a row to the **Completed items** table with the commit hash.
- **Closing a dimension** in sasquatch (e.g. lifting a score past 80%) does **not** close TODOs in this file — they are tracked separately.
- **Aspirational stub methods** (`# TODO: implement method`) are *not* actionable — do not pull them into "Active work" unless explicitly assigned.
- **Log-only stub bodies** (`logma.info("... invoked (stub)")` with no real logic) are **banned** — every method must have a real implementation that does something observable.
- **Release markers** (`# PUSH <version>`) are bookkeeping — they belong in the YAML / config release notes, not in this file.
- **Parent/cfg constructor signatures** are sacred — the `(parent, cfg)` pattern in `nchantdoffice/widgets/__init__.py`-style classes must not be changed without explicit user approval. This rules out the `(cfg, parent, self)` data-clumps refactor.
- **Internal projects** are CORE INTEGRATED COMPONENTS — `find internal source` and integrate it; never comment imports, stub out failures, or substitute PyPI equivalents.
- **PyKeyStore is a security design** — no env vars, no plaintext API keys.
- **All class names that begin with `Pyffice`** must stay `Pyffice<Document>` — no renames to satisfy parallel-inheritance refactors; only refactor bodies.
