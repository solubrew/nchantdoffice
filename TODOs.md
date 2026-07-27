# TODOs

> Reconsolidated against `78f1d9e` (HEAD of `nchantdoffice/gamma`, 2026-07-27).
> Regenerate with: `grep -rn 'TODO:' nchantdoffice/ --include='*.py' | grep -v 'implement method' | grep -v 'invoked (stub)'`
> Last full audit: **81.86%** (was 73.93% in this file's prior revision).

## At a glance

| Bucket | Count | Status |
|---|---|---|
| Descriptive `TODO:` markers in code | **75** | Active — see [Active work](#active-work) |
| Stub methods (`# TODO: implement method`) | **0** | **All built out** (was 134) |
| Log-only stub bodies (`invoked (stub)` / `stub returning None`) | **0** | **All replaced with real logic** (was 93) |
| Release markers (`# PUSH 0.0.3` etc.) | **48** | Not TODOs — version-target notes |
| **Total actionable** | **75** | |

The prior version of this file listed 116 markers with 32 stubs and 40 active TODOs. After H43–H47 the stubs are gone (0) and active TODOs grew to 75 as new work was uncovered during the build-out.

---

## Project health (2026-07-27)

### Sasquatch audit score: **81.86%** (was 73.93%)

**7 dimensions still below 95%** — full breakdown at end of file.

### Recent lift (+7.93 points since 2026-07-26)

| Dimension | Was | Now |
|---|---|---|
| `cli_documentation` | 66 | **100** |
| `ci_cd_documentation` | 0 | **100** |
| `module_cli_coverage` | 40 | **100** |
| `duplicate_filenames` | 65 | **100** |
| `switch_abuse` | 0 | **100** |
| `error_handling` | 70 | **100** |
| `feature_envy` | 70 | **100** |
| `readme_quality` | 70 | **100** |
| `lambda_antipattern` | 86 | **100** |
| `external_dependencies_declared` | 90 | **100** |
| `logging` | 90 | 98 |
| `security_post_install` | 40 | 85 |
| `parallel_inheritance` | 65 | 95 |

### Currently below 95% (7 dims)

| Dim | Score | Why |
|---|---|---|
| `god_class` | 0 | 5 god classes — biggest is `NchantdOfficeCloakModel` at 101 methods / 1416 lines |
| `type_annotations` | 0 | 2135 / 2146 functions untyped |
| `data_clumps` | 30 | `(cfg, parent, self)` repeated 155× — user opted not to change parent/cfg signatures |
| `security_internal` | 80 | 155 `getattr_dynamic` calls — refactor needed |
| `security_ruff` | 80 | 5 `exec_calls` + 1 `url_open` — replace with safer APIs |
| `git_workflow` | 85 | **Auditor bug**: `_use_subprocess` flag set but never consulted by `get_remotes()`, so the configured `origin` remote isn't seen when gitpython is missing from `/home/solubrew/ENVs/sasquatch`. Cannot be fixed from the project side. |
| `security_post_install` | 85 | `__main__.py` flagged unconditionally by the auditor (severity 15) |

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
| H47 | Sasquatch below 80% (audit sprint) | `78f1d9e` | 78.15% → **81.86%** (+3.71 points). `error_handling` 70→100 (6 bare excepts fixed), `lambda_antipattern` 86→100 (7 lambdas → named funcs), `external_dependencies_declared` 90→100 (optional-dependencies section), `logging` 90→98 (8 `print()` → `logma`), `security_post_install` 40→85 (removed `setuptools_scm`), `feature_envy` 70→100 (extracted 3 methods to free funcs), `readme_quality` 70→100 (added Quick start + Development sections). |

---

## Active work

> 75 descriptive TODOs across 19 files. Ordered by priority; each item
> carries the live `file:line` so the worker can jump straight to it.

### P0 — Architecture & data integrity (highest-impact)

- [ ] **T-001** — `nchantdoffice/models.py:613` — Move `app_document_type` table to the app schema and refactor `add_note_app` to use it.
- [ ] **T-002** — `nchantdoffice/models.py:860` — Replace ad-hoc string lookups in `add_document_app` with the `app_document_type` registry (T-001 dep).
- [ ] **T-003** — `nchantdoffice/models.py:1435` — Add real semver policy to `update_document_entry` (currently bumps `+1` literally).
- [ ] **T-004** — `nchantdoffice/models.py:1363` — Implement `_handle_document_not_found` once document loader returns the canonical `Document` (currently short-circuits).
- [ ] **T-005** — `nchantdoffice/models.py:1048` — Convert published-date filter from raw `datetime.now()` to a real format helper (`format_published_filter`).
- [ ] **T-006** — `nchantdoffice/models.py:1173` — Implement the view referenced by `create_virtual_table` then pull data from it.
- [ ] **T-007** — `nchantdoffice/models.py:1181` — Migrate `create_virtual_table` to the persistence layer (T-061 dependency).
- [ ] **T-008** — `nchantdoffice/models.py:1307` — Implement session parsing for the rolling-summary work.
- [ ] **T-009** — `nchantdoffice/models.py:1333` — "notion / evernote" importer — keep unimplemented until at least one connector is approved.

### P1 — User-visible features (panes, dialogs, config)

- [ ] **T-010** — `widgets/config/config_sources.py:73` — Build size-control widgets (`"full"`, `"%10"`).
- [ ] **T-011** — `widgets/config/config_sources.py:79` — Implement config changes that make the data-source pane stand out.
- [ ] **T-012** — `widgets/config/config_sources.py:111` — Pull API key from `pycurity` (obscured variant shown to user, real key on submit).
- [ ] **T-013** — `widgets/config/config_sources.py:125` — Add the obscured-key visibility-toggle widget at the end of the entry box.
- [ ] **T-014** — `widgets/config/config_sources.py:136` — Wire "create new NchantdOfficeWebBrowser" button to a real document factory.
- [ ] **T-015** — `widgets/config/settings.py:227` — Add a config pane for each document type.
- [ ] **T-016** — `widgets/config/settings.py:228` — Add a node-name log dialog popup option in the toolbar settings.
- [ ] **T-017** — `widgets/config/settings.py:238` — Gate `pro_edition` toggle behind a real `pro_edition` capability check.
- [ ] **T-018** — `widgets/config/settings.py:264` — Set the current default tab based on document type.
- [ ] **T-019** — `widgets/config/settings.py:280` — Replace the word "toolbox" with a drop-down of right-pane tabs.
- [ ] **T-020** — `widgets/config/help.py:75` — Implement PDF download + indexed navigation for the in-app help viewer.
- [ ] **T-021** — `widgets/config/accounts.py:164,174` — Replace placeholder user-name / service-detail fetches with live account API calls.
- [ ] **T-022** — `widgets/config/accounts.py:358` — Implement actual server sync in `sync_account_settings`.
- [ ] **T-023** — `widgets/documents/atnrg/prompts.py:89` — Decide and document the integration pattern for the unimplemented prompt registry hookup.
- [ ] **T-024** — `widgets/documents/atnrg/prompts.py:272` — Add a pane to allow setting days-to-keep on chat history.
- [ ] **T-025** — `widgets/documents/atnrg/prompts.py:293` — Show connection-availability / create-connection for model APIs.
- [ ] **T-026** — `widgets/documents/atnrg/browsers.py:450` — Surface whether browser integration is per-instance configurable.
- [ ] **T-027** — `widgets/documents/atnrg/browsers.py:950` — Build out the quick-app-link mini-catalog.
- [ ] **T-028** — `widgets/documents/atnrg/browsers.py:1041` — Debug: document is not updating the active URL in the content section.
- [ ] **T-029** — `widgets/documents/atnrg/browsers.py:1260,1267` — Delete all browsing history for this profile (on disk + non-history DB rows).
- [ ] **T-030** — `widgets/documents/media/forms.py:141` — Implement "Excel → Google Form" conversion flow.
- [ ] **T-031** — `widgets/documents/media/forms.py:368` — Implement service-connection logic for the forms sub-system.
- [ ] **T-032** — `widgets/documents/media/forms.py:530` — Google Forms API integration for `publish_to_google_forms`.
- [ ] **T-033** — `widgets/documents/media/forms.py:891` — Wire `submit_to_tracker` to a real remote server / issue tracker.
- [ ] **T-034** — `widgets/documents/media/scripts.py:475` — Use the syntax selector from toolbar in `save()` (currently hard-coded `html`).
- [ ] **T-035** — `widgets/documents/media/scripts.py:796` — Implement external loading of script file.
- [ ] **T-036** — `widgets/documents/media/images.py:998` — Open from binary data already loaded in the PyfficeDocument.
- [ ] **T-037** — `widgets/documents/documents.py:326` — Replace `has_pro` check with profile switcher / per-document-type pro features.
- [ ] **T-038** — `widgets/documents/documents.py:530` — Implement snapshot method (visual dimensions + view capture).
- [ ] **T-039** — `widgets/documents/analytics/analytics_charts.py:60` — Replace chart stub with live source list (chart usage connections).
- [ ] **T-040** — `widgets/documents/analytics/analytics_charts.py:159` — Send data from the document to populate the chart.
- [ ] **T-041** — `widgets/documents/managers/filesystems.py:1097` — Refactor: the whole document is essentially a file-nav window — decide where this fits.
- [ ] **T-042** — `widgets/documents/managers/filesystems.py:1147` — Test and refactor.
- [ ] **T-043** — `widgets/documents/managers/calendars.py:344` — Build the events-list pane from the configured events dict (currently a hard-coded comment).
- [ ] **T-044** — `widgets/documents/workbooks/notebooks.py:923` — Implement `.ipynb` re-load (without external file) for notebook persistence (T-043's load was implemented in H45 — re-load still TODO).

### P2 — UX polish (panes, toolbars, layout)

- [ ] **T-050** — `widgets/panes/new.py:186` — Decide on a unified format → tool-type routing table for the "new document" wizard.
- [ ] **T-051** — `widgets/panes/new.py:190` — Build a "load from Google Drive" dialog that mimics file-open but uses browser/API.
- [ ] **T-052** — `widgets/panes/new.py:195` — Implement `widget_code` override based on per-document-type options.
- [ ] **T-053** — `widgets/panes/new.py:410` — Set default pane handlers so root-node creation is automatic on first launch.
- [ ] **T-054** — `widgets/panes/sources.py:105` — Implement `get_available_sources` (currently returns hard-coded stub list).
- [ ] **T-055** — `widgets/panes/documents.py:113` — Add tag-tracking column to the documents pane (also tracks last-accessed timestamp).
- [ ] **T-056** — `widgets/panes/charts.py:165` — Implement BorderConfigBar as a button group.
- [ ] **T-057** — `widgets/panes/charts.py:190` — Replace `BorderConfigBar` (currently a text-config copy) with a real border-style editor.
- [ ] **T-058** — `widgets/panes/forms.py:124` — Move "ask rate" spinbox into the survey definition rather than the form template.
- [ ] **T-059** — `widgets/panes/quickstart.py:118` — Implement link collection and pull from database.
- [ ] **T-060** — `widgets/panes/search.py:123` — Add tag-tracking to the search pane (matches T-055).
- [ ] **T-061** — `widgets/controls/toolboxes.py:180` — Tighten spacing of the Node Configuration Drawer to balance Node Pane / Tab Pane widths.
- [ ] **T-062** — `widgets/controls/toolbars.py:114` — Remove the redundant `init_variables()` call (kept for now because `app` attribute must be set before `super`).
- [ ] **T-063** — `widgets/controls/toolbars.py:148` — Replace hard-coded widget lookup with a registry-based lookup against `app_document_type`.
- [ ] **T-064** — `widgets/controls/toolbars.py:152` — Switch `db` access from `self.app.model.instance.db` to a `MultiInstance` adapter (T-001 dep).
- [ ] **T-065** — `widgets/controls/toolbars.py:182` — Cleanup `add_tab`, `add_document` signatures and combine as much code as possible.
- [ ] **T-066** — `widgets/controls/toolbars.py:230` — When multiple notes are open, increment `position` per insertion rather than overwriting.
- [ ] **T-067** — `widgets/catalogs.py:281` — Add a filter-capable search bar to the catalogs layout.

### P3 — Internal mechanics

- [ ] **T-070** — `nchantdoffice/utilities/links.py:40` — Build the link_affiliate join view (currently empty).
- [ ] **T-071** — `widgets/documents/workbooks/matricies.py:1486` — Expand in the Y direction and wrap text in the spreadsheet widget.
- [ ] **T-072** — `widgets/documents/workbooks/matricies.py:1548` — Add Bold / Italic / Underline toolbar buttons to the spreadsheet widget.
- [ ] **T-073** — `widgets/documents/workbooks/matricies.py:1710` — Add a message to let users know some features of Excel files are not implemented.
- [ ] **T-074** — `widgets/documents/workbooks/matricies.py:1717` — Determine the correct file type to open based on extension / magic bytes.
- [ ] **T-075** — `widgets/documents/workbooks/matricies.py:1841` — Implement row and cell size formatting on document population.

---

## Aspirational stub methods

> **All 134 `# TODO: implement method` stubs were built out in H43 (commit `f93df89`) and H44 (commit `53a5e68`). Current count: 0 across the project.**
>
> The remaining ~5 markers in `widgets/documents/` (e.g.
> `# TODO implement message to let user know...`) are descriptive
> comments, not function stubs. They're tracked in [Active work](#active-work).
>
> The table below is preserved as historical record of where the stubs
> lived before H43 / H44.

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

## Recent activity

| Commit | Date | Description |
|--------|------|-------------|
| `78f1d9e` | 2026-07-27 | docs(README): add Quick start + Development, rename Overview section |
| `7113642` | 2026-07-27 | refactor: extract 3 envious methods to free functions (calendars + contacts) |
| `e148645` | 2026-07-27 | feat(pyproject): remove setuptools_scm from build-system |
| `c2afb24` | 2026-07-27 | refactor(utilities/links): replace 8 print() calls with logma |
| `d492c53` | 2026-07-27 | feat(pyproject): add optional-dependencies section (pdf/spreadsheet/internal/all) |
| `9c6db7e` | 2026-07-27 | refactor: convert 7 remaining lambdas to named functions/methods |
| `d83dc42` | 2026-07-27 | fix(error_handling): replace 6 bare excepts with explicit Exception types |
| `53a5e68` | 2026-07-27 | refactor: replace all 70 log-only stubs with real logic |
| `44bd8a8` | 2026-07-27 | feat(documents): implement 32 empty methods with real logic |
| `511528e` | 2026-07-26 | refactor: eliminate final 3 switch_abuse instances (score → 100%) |
| `454575b` | 2026-07-26 | script, image, pdf, matrix all saving and loading from external file path |
| `51feda6` | 2026-07-26 | refactor: convert 5 more switch_abuse instances to dispatch tables |
| `fcd89a4` | 2026-07-26 | refactor: convert 5 switch_abuse instances to dict dispatch |
| `38b94f4` | 2026-07-26 | docs: add H43 (widgets/documents stub build-out) to completed items |
| `f93df89` | 2026-07-26 | refactor(documents): clean up remaining stubs |
| `9af2563` | 2026-07-26 | docs: consolidate TODOs.md to reflect current project state |
| `ccf77d6` | 2026-07-26 | refactor(settings): introduce `_SETTING_KEYS` dispatch table |

---

## Working agreements

- **Adding a new TODO**: edit this file with the live `file:line` and a one-line description. Mark it `[ ]` (pending) or `[x]` (done).
- **Resolving a TODO**: change `[ ]` to `[x]` and add a row to the **Completed items** table with the commit hash.
- **Closing a dimension** in sasquatch (e.g. lifting a score past 80%) does **not** close TODOs in this file — they are tracked separately.
- **Aspirational stub methods** (`# TODO: implement method`) are *not* actionable — do not pull them into "Active work" unless explicitly assigned.
- **Log-only stub bodies** (`logma.info("... invoked (stub)")` with no real logic) are **banned** — every method must have a real implementation that does something observable.
- **Release markers** (`# PUSH <version>`) are bookkeeping — they belong in the YAML / config release notes, not in this file.
- **Parent / cfg constructor signatures** are sacred — do not change them. The `data_clumps` dimension will not be fixed by introducing a context dataclass.