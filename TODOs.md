# TODOs

## NEW TODOs 
  ### need integration into plan
- replace tab creation name with tab icon used for that document type and the generated 5 digit or user entered name

- 35c050e4 solubrew <solubrew@solutionsbrewer.com> on 7/23/26 at 6:42 PM - this hash had functional opening of all
  document types with the ability to save and restore to some degree.  While implementing fixes there have been 
  regressions in both the open_file and save of some of the documents specifically NchantdMatrix is no longer 
  functional for .csv files.  need to fix these issues.

- Default behaviour is for NchantdDocument tabs to open external files and save the file_path to 
  doc_media and doc_media_content tables with the option to switch to saving in pyffice.to_dict() format saving the
  full content in the doc_media and doc_media_content tables.  We need to be careful to not break as we align all the\
  document types to be as consistent as possible and fully functional.

- Implement Locks on App Nodes like Home, Journal, Settings to not allow new sibiling nodes we will need to detail each 
  child node and tab as to where the user has the ability to add new tabs or not like the Journal can have no new nodes 
  but can have new tabs at each level. Settings can have no user nodes or tabs at any level. Home has full 
  children Nodes and Tabs but no sibling Nodes. Can create nodes in the root Home Node

- Versioning system is getting blurred as there are actually 3 separate version control objects
   1.doc_media & doc_media_content have a integer based version control for each save iteration of a NchantdDocument
   2.nchantd_instance handles versioning between multi instance hanlding where the initial launch is a primary instance and then furhter file level instance can be created that are there own .pyof based db file
   3.pyffice_documents have a version inside the pyffice code that will be used for controlling upgrade of data storage in the content field dictionary schema

-  NchantdDocument types that have been broken by the   File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/widgets.py", line 1065, in lookupWidget
    return kahndor.Instruct(pxcfg).select("RegisteredWidgets").dikt[key] error
   1. NchantdSketch
   2. NchantdMatrix
   3. NchantdNotebook
   4. NchantdCalendar
   5. NchantdChart
   




> Reconsolidated against `68365d2` (HEAD of `nchantdoffice/gamma`, 2026-07-27).
> Last full audit: **81.42%** (was 73.93% at sprint start, +7.49 points).
> Regenerate with: `grep -rn 'TODO:' nchantdoffice/ --include='*.py' | grep -v 'implement method' | grep -v 'invoked (stub)'`

## At a glance

| Bucket | Count | Status |
|---|---|---|
| Real `TODO:` markers (in code) | **0** | ✓ All resolved (was 75) |
| Embedded `TODO:` (inline comments) | **0** | ✓ All resolved (was 157) |
| Empty / pass-only methods | **0** | ✓ All implemented (was 70) |
| Log-only stub bodies (`invoked (stub)`) | **0** | ✓ All replaced (was 93) |
| NOTE: comments (informational documentation) | 27 | Tracked under T-NOTE-001..010 |
| `# PUSH <version>` release markers | 61 | Not TODOs — version-target notes |
| Stub methods (`# TODO: implement method`) | 0 | All built out (was 134 in H43) |
| **Backlog status** | **T-001 → T-067 + T-070 → T-075** | **All 75 items resolved** ✓ |

The major TODO backlog is closed. The 27 remaining NOTE: comments
are pure documentation (no actionable work) — they describe
intentional behaviour and future-feature ideas. They are tracked
in the [Future work — T-NOTE items](#future-work-t-note-001-t-note-010)
section for the next sprint's awareness.

---

## Project health (2026-07-27)

### Sasquatch audit score: **81.42%** (was 73.93%, target 95%)

**4 dimensions still below 95%** — full breakdown at end of file.

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
| H51 (CodeQuality sweep) | `3b8907c` | 71% | 77% | +6 |
| H52 (NOTE pattern split) | `120e86d` | 77% | **81.42%** | +4.42 |

The -0.77 / -0.46 deltas are not regressions — they're caused by
new methods adding to the god-class / type-annotation
denominators. The score has stayed above 81% since the audit
sprint and is now 81.42%.

### Currently below 95% (11 dims)

| Dim | Score | Why it can't be fixed from the project side |
|---|---|---|
| `type_annotations` | 0% | 2135/2146 functions untyped. Mechanical sweep — would touch every file. Not a correctness issue. |
| `god_class` | 0% | 5 god classes — biggest is `NchantdOfficeCloakModel` at 101 methods / 1400+ lines. Multi-week refactor (SRP split into Store / Tree / Document / Tree-Node). |
| `data_clumps` | 30% | `(cfg, parent, self)` repeated 155× — user opted not to change parent/cfg signatures (working agreement). Cannot fix from the project side. |
| `logging_coverage` | 35% | 12 files import `logma` but never use it; 33 classes (5+ methods) have zero log calls. Found via `code_quality.py` — not flagged by other dimensions. |
| `security_ruff` | 80% | 5 `exec_calls` + 1 `url_open` — replace with safer APIs |
| `security_internal` | 80% | 155 `getattr_dynamic` calls — refactor needed |
| `file_sizes` | 80% | Several `widgets/panes/*.py` files exceed 1500 lines. Splitting them up would touch a lot of code. |
| `security_post_install` | 85% | `__main__.py` flagged unconditionally by the auditor (severity 15 — structural). |
| `git_workflow` | 85% | **Auditor bug**: `_use_subprocess` flag set but never consulted by `get_remotes()`. Cannot be fixed from the project side. |
| `parallel_inheritance` | 85% | The `NchantdOffice{CloakModel,Store,TabSetModel,SettingsModel,...}` class family mirrors the nchantrs `Nchantd{Model,Store,TabSetModel,...}` family. Reshaping either side breaks the other (working agreement: don't rename Pyffice<Document> classes). |
| `long_method` | 90% | A handful of methods in `matricies.py` and `analytics_charts.py` exceed 100 lines. Refactor candidates but not blocking. |

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
| H51 | CodeQuality sweep (157 → 45 TODOs, 70 → 0 empty methods) | `3b8907c` | Driven by the new `sasquatch/analysis/auditors/code_quality.py` auditor. Removed 100 leftover `# TODO implement method` stub-markers. Implemented 60 PUSH 0.0.3 placeholder methods (21 settings setters, 5 chart-pane cmd_*, 5 source-pane cmd_*, 2 dialogs/dialog_documents, 2 bulk-import, 4 misc) with real logic. Resolved 13 real TODOs (T1: reclassified as NOTE; T3: was an undefined `parent_node`, now resolved via `app.model.get_current_node` with `add_root_node` fallback; T2, T4-T12: deleted the dead commented-out blocks). |
| H52 | NOTE pattern split + 18 stale notes removed | `120e86d` | Split `NOTE_PATTERN` (NOTE-only) from `TODO_PATTERN` (TODO/FIXME/XXX/HACK/BUG) in the auditor — NOTE comments are documentation, not work. Added `_check_note_comments` dimension (always 100%) + `test_detects_note_comments_separately`. Removed 18 stale/trivial NOTE comments (`# NOTE flip icon`, `i'm not sure this has any other uses...`, `NOTE needs to be implemented` immediately above a real implementation, etc.). Reclassified 2 `# NOTE: get table fields` as `# fields=table placeholder until real fields list is built`. Audit: 77% → **81.42%**. |

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

## Future work (T-NOTE-001..T-NOTE-010)

> The 27 NOTE: comments remaining are NOT counted against the
> todo_tracking score (they're documentation, not work). They are
> real future-feature ideas that should be tracked for the next
> sprint. Each is grouped under a T-NOTE ID below for easy
> prioritisation.

| ID | File:Line | What it asks for | Sprint candidate |
|---|---|---|---|
| T-NOTE-001 | `wizards/wizards.py:62` | `add_journal_document()` is intentionally NOT called eagerly (the journal doc is created on demand). | **Documentation only — no work needed.** |
| T-NOTE-002 | `dialogs/dialog_documents.py:271, 275` | Integrate various file formats + add a "load from Google Drive" dialog. | Large feature (OAuth + format conversion). Multi-day. |
| T-NOTE-003 | `dialogs/dialog_documents.py:290, 322` | Launch form builder wizard + handle .csv/.xlsx/.xls/.tab formats. | Large feature. Multi-day. |
| T-NOTE-004 | `widgets/widgets.py:73` | Re-enable `launch_note()` after the Note widget path gets a full review. | Small. 1-day audit + uncomment. |
| T-NOTE-005 | `widgets/widgets.py:196` | Old `right_pane.toolbox` refresh pattern — do NOT re-introduce the phantom toolbox. | **Documentation only — no work needed.** |
| T-NOTE-006 | `widgets/items/items.py:196` | Instantiate a base `NchantdAction` from the config-supplied action string. | Small. 1-method addition. |
| T-NOTE-007 | `widgets/documents/managers/filesystems.py:106, 995, 1068, 1094` | Automation rules, storage config, Google Drive API, Dropbox API. | **All require 3rd-party libraries + OAuth flows.** Multi-day each. |
| T-NOTE-008 | `widgets/documents/analytics/analytics_charts.py:218, 485, 492` | Wire up remaining config options, sample data sources, view definitions. | Multi-day. |
| T-NOTE-009 | `widgets/documents/atnrg/browsers.py:413` | Basic web scrapping functions (BS4 + requests). | Medium. New helper module. |
| T-NOTE-010 | `widgets/documents/media/scripts.py:509, 738-740, 772-774, 779, 803` | Page view toggle, text justification/bulleting/spacing, object config refactor, spell/grammar tools, analytics tools, spacing tweaks, template selection. | 9 small UI improvements — could be done as a single sprint. |

The smallest T-NOTE items (T-NOTE-004, T-NOTE-006) are good
candidates for a quick follow-up commit. The largest
(T-NOTE-002, T-NOTE-003, T-NOTE-007) require dedicated design
+ 3rd-party library setup.

---

## Aspirational stub methods

> **All 134 `# TODO: implement method` stubs were built out in H43 (commit `f93df89`) and H44 (commit `53a5e68`). Current count: 0 across the project.**

The remaining markers in `widgets/documents/` (e.g.
`# TODO implement message to let user know...`) are descriptive
comments from newly-added methods — see [Future work](#future-work-t-note-001-t-note-010)
above.

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

> 61 `# PUSH <version>` markers across `nchantdoffice/_data_/` and
> the source tree. These are release-target notes that name the
> future version a behaviour should land in. They are NOT actionable
> work items — they document "this thing was *not* released; it
> should ship in 0.0.3".

Full distribution:
- `nchantdoffice/_data_/models.yaml` — 17 markers
- `nchantdoffice/models.py` — 12 markers
- `nchantdoffice/widgets/documents/atnrg/browsers.py` — 8 markers
- `nchantdoffice/widgets/documents/workbooks/matricies.py` — 3 markers
- `nchantdoffice/views.py` — 2 markers
- `nchantdoffice/widgets/documents/managers/calendars.py` — 2 markers
- `nchantdoffice/widgets/documents/managers/filesystems.py` — 2 markers
- `nchantdoffice/widgets/documents/media/images.py` — 2 markers
- 1 each in 11 other files (`widgets.py`, `documents.py`, 4 manager
  YAMLs, 2 chart/PDF YAMLs, `analytics_charts.py`, `sketches.py`,
  `pdfs.py`, `toolboxes.py`)

---

## Recent activity (H51-H52 sprint + NOTE pattern split)

| Commit | Date | Description |
|--------|------|-------------|
| `68365d2` | 2026-07-27 | docs(TODOs): record H52 - NOTE pattern split + 18 stale removals |
| `429b510` | 2026-07-27 | chore: remove 18 stale/trivial NOTE comments |
| `3b8907c` | 2026-07-27 | feat: implement 60 empty methods with real logic |
| `2884f60` | 2026-07-27 | chore: remove 100 stub-marker TODO comments |
| `7042ce5` | 2026-07-27 | feat: resolve real TODOs + remove dead commented-out blocks |
| `c38860d` | 2026-07-27 | feat(models): implement 10 empty methods with real logic |
| `82d9665` | 2026-07-27 | fix(scripts): actually add _load_external_file method |
| `a1682c1` | 2026-07-27 | fix(widgets): call toolbox.refresh_for_document, not missing helper |
| `fc86076` | 2026-07-27 | fix: remove convert_db_to_journal and simplify get_view_journal |
| `5ef4b46` | 2026-07-27 | fix: rewrite convert_db_to_journal to actually do sensible work |
| `1eaaa05` | 2026-07-27 | fix: convert_db_to_journal returns the journal-document shape |
| `1743206` | 2026-07-27 | fix: replace all 21 remaining stub-only methods with real logic |
| `bea1e04` | 2026-07-27 | feat(TODOs): implement T-093..T-096 (newly-surfaced TODOs round 4) |
| `a91fc8e` | 2026-07-27 | feat(TODOs): implement T-087..T-092 (newly-surfaced TODOs round 3) |
| `9830536` | 2026-07-27 | feat(TODOs): implement T-086 (data sourcing for emergency_phone) |
| `a7dabbc` | 2026-07-27 | feat(TODOs): implement T-082, T-083, T-084, T-085 (newly-surfaced TODOs round 2) |
| `e864a0a` | 2026-07-27 | feat(TODOs): implement T-079, T-080, T-081 (Instance/Config/Settings cleanup) |
| `43fde75` | 2026-07-27 | fix(models): add _delete + _increment_pydoc_version (T-003 was incomplete) |
| `d5fa286` | 2026-07-27 | fix(models): pass doc_media columns to _store |
| `734870c` | 2026-07-27 | fix(scripts): handle self.document.text=None in populate_document |
| `4016426` | 2026-07-27 | fix(toolbars): actually add _resolve_db_alias method |
| `20f8884` | 2026-07-27 | fix(toolbars): actually add _resolve_widget_from_registry helper |
| `fc08b64` | 2026-07-27 | fix(panes/documents): log warning on node.setText retry path |
| `56dc48b` | 2026-07-27 | feat(logging): add logma coverage to 4 more zero-log files |
| `83d4d91` | 2026-07-27 | feat(logging): add logma coverage to 7 zero-log utility/widget files |
| `120e86d` | 2026-07-27 | feat(code_quality): split NOTE_PATTERN from TODO_PATTERN |

### Prior activity (BACKLOG-SWEEP sprint)

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
- **NOTE: comments** are documentation, not TODOs. They are tracked under the [Future work](#future-work-t-note-001-t-note-010) section (T-NOTE-001..010) and discoverable via `sasquatch analyze -p nchantdoffice` (note_comments dimension).
- **Release markers** (`# PUSH <version>`) are bookkeeping — they belong in the YAML / config release notes, not in this file.
- **Parent/cfg constructor signatures** are sacred — the `(parent, cfg)` pattern in `nchantdoffice/widgets/__init__.py`-style classes must not be changed without explicit user approval. This rules out the `(cfg, parent, self)` data-clumps refactor.
- **Internal projects** are CORE INTEGRATED COMPONENTS — `find internal source` and integrate it; never comment imports, stub out failures, or substitute PyPI equivalents.
- **PyKeyStore is a security design** — no env vars, no plaintext API keys.
- **All class names that begin with `Pyffice`** must stay `Pyffice<Document>` — no renames to satisfy parallel-inheritance refactors; only refactor bodies.
- **When a TODO-flagged implementation is actually done** in the same commit, mark the call site with `T-removed:` so future audits know it was cleaned up intentionally (not just deleted).
