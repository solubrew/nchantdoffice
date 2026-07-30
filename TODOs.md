# NchantdOffice TODOs — current state (2026-07-29)

> **Consolidation date:** 2026-07-29.
>
> This file replaces the previous `TODOs.md`, the historical `STATE.md`,
> and the session-only `SESSION_NOTES.md` (both now in
> `_data_/archive/2026-07-29/`). It captures the project state after the
> closed-loop of Sprints 1-17 across nchantdoffice / nchantrs / pyffice /
> pycurity / pyside6pandas.
>
> **Other top-level notes** (preserved as separate files):
> - `README.md` — project overview
> - `CHANGES.md` — Keep-a-Changelog history
> - `CI_CD.md` — pipeline overview
> - `CLI.md` — command-line reference
> - `CODING_STANDARDS.md` — V4 standards compliance
> - `directory_tree.md` — file-tree snapshot (2026-07-16)
> - `BUGs.md` — raw stack-trace archive (historical reference)

---

## 1. Project snapshot

| Dimension | Value |
|---|---|
| Project | NchantdOffice |
| Type | Desktop GUI application (PySide6) |
| Branch | `gamma` (in sync with `origin/gamma`) |
| HEAD | `9467990` (nchantdoffice/gamma) |
| Working agreement | Internal projects are CORE INTEGRATED; never stub them out |
| Test env | `QT_QPA_PLATFORM=offscreen /home/solubrew/ENVs/sasquatch/bin/python` |
| Test command | `QT_QPA_PLATFORM=offscreen /home/solubrew/ENVs/sasquatch/bin/python -m pytest tests -q` |
| Current test surface | **77 passed, 0 skipped** (was 13 at H43, 45 at Sprint 7) |

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

## 2. Live open items

These are the items still requiring work, in priority order.

### Pinned (per user direction — requires non-testable env)

- [ ] **NchantdChart segmentation fault.** Held per user instruction
  (2026-07-28). Reproduction requires a parent-app Qt harness; the live
  bug cannot be reproduced in the sasquatch headless env.
- [ ] **T-NEW-023 — NchantdScript reload whitespace lost on reopen**
  (2026-07-29). Per user: "reload should be opening the file on
  disk again". Initial open renders correctly (markdown/python/etc.)
  but reload from another tabset still does not preserve
  indentation. Marked as a pin — needs a Qt-parent subprocess harness.
- [x] **T-NEW-024 followup — doc_media.syntax not updated on file-open** (Sprint 17, 2026-07-29). The `doc_media` row carried the `"html"` default written at tab-creation time; the in-memory `document.syntax` was updated correctly by `_apply_extension_syntax` but the DB row was never touched, so the next reopen read `syntax="html"` from the DB and the dispatch fell through to `setPlainText`. Fixed: `model.update_doc_media_syntax(did, syntax)` runs `UPDATE doc_media SET syntax = ? WHERE did = ?` via the existing `store.update_records()` path. Called from `scripts.py::open_file` after `_apply_extension_syntax` and from `documents.py::save` on every save. Regression test: `tests/test_script_doc_media_syntax_update.py` (3 AST checks: model helper exists with `syntax` + `did` + `UPDATE`, `scripts.py::open_file` triggers the update, `documents.py::save` triggers the update).

### Deferred / non-blocking

- [ ] **Ad tab button redirect to Settings / Account tab** —
  currently launches a browser via QService; the user wants it
  to route into an existing tab under the Settings node pointing
  at nchantdoffice.com. UX change, no crash.
- [ ] **Ad tab size control** — right-side tabs are slim 360×900
  and would need to go into the center tabset if a larger ad is
  required. UX change, no crash.
- [ ] **Tab Edit Pane doesn't persist the new name** — `cmd_set_tab_name`
  updates the label but doesn't write back to the DB. Regression.
- [ ] **Node Edit Pane doesn't persist the new name** — same regression.
- [ ] **Name-entry dialog for new nodes / tabs** — config flag for
  "prompt vs auto-generate", with dialog widget (3 separate TODOs).
- [ ] **Save-mode toolbar icons** — disk-stack icon toggles internal
  storage, cloud icon toggles cloud storage, both in
  `NchantdDocumentToolBar`.
- [ ] **NchantdSketch / NchantdCalendar default to internal** — no
  external standard-compatible file format.

### Unimplemented features (discovered by code review, 2026-07-29)

These are features the codebase advertises (config entries, branch
arms, helper names) but the actual implementation is missing or
raises a `NotImplementedError` / "File Type not yet implemented".
They are not labelled as `PUSH to 0.0.3` in source comments — they
are silent gaps awaiting implementation.

#### File-type imports raise "File Type not yet implemented"

`nchantdoffice/widgets/controls/toolboxes.py::cmd_open_local_file`
(lines 529-578) raises an exception when the user picks a file
whose extension is in the configured branch arms but no
`model.import_<ext>()` method exists yet:

| File extension | Branch location | Importer |
|---|---|---|
| `.docx` | toolboxes.py:541-542 | ❌ `model.import_docx()` doesn't exist |
| `.csv` | toolboxes.py:552-553 (commented `import_csv` at 554) | ❌ `model.import_csv()` doesn't exist |
| `.xlsx` | toolboxes.py:555-556 | ❌ no `model.import_xlsx()` |
| `.xls` | toolboxes.py:557-558 | ❌ no `model.import_xls()` |
| `.ods` (×2 duplicate branches) | toolboxes.py:559-560, 565-566 | ❌ no `model.import_ods()` |
| `.odt` | toolboxes.py:561-562 | ❌ no `model.import_odt()` |
| `.odp` | toolboxes.py:563-564 | ❌ no `model.import_odp()` |
| `.odg` | toolboxes.py:567-568 | ❌ no `model.import_odg()` |
| `.odf` | toolboxes.py:569-570 | ❌ no `model.import_odf()` |
| `.odc` | toolboxes.py:571-572 | ❌ no `model.import_odc()` |
| `.gif` | toolboxes.py:550-551 | ⚠️ silent `pass` (no error, no import) |

#### Stub `cmd_*` methods in `toolboxes.py`

| Method | Lines | Status |
|---|---|---|
| `cmd_duplicate_instance` | 328-332 | Comment-only stub: "create new instance / copy over user items from the initial database to the new instance database". No body. |
| `cmd_import_instance` | 345-350 | Opens file dialog but never calls any `model.import_*()` method on the result. |
| `cmd_save_instance` | 581-601 | Near-empty: `pass` branches, comments only, no DB write or copy logic. |
| `cmd_llm_query_pane` | 352-354 | `return self` only. |
| `cmd_web_search_pane` | 603-605 | `return self` only. |

#### Stub `cmd_on_change_*` methods in `widgets/config/settings.py`

Seven settings handlers are explicit `# TODO implement method logic`
stubs (returns `self` after the comment):

| Method | Lines |
|---|---|
| `cmd_on_change_journal_focus` | 156-159 |
| `cmd_on_change_settings_focus` | 161-164 |
| `cmd_on_change_automation` | 166-169 |
| `cmd_on_change_data_source` | 171-174 |
| `cmd_on_change_show_left_side_pane` | 176-179 |
| `cmd_on_change_show_right_side_pane` | 181-184 |
| `cmd_on_change_quicklaunch` | 186-189 |

The other cmd_on_change_* methods in the same file
(`cmd_on_change_document_catalog`, `cmd_on_change_default_tab_bit`,
`cmd_on_change_default_tab_select`, `cmd_set_pro_edition`) are
properly implemented.

#### Stub initModel / initView helpers

| Class.method | File:Line | Status |
|---|---|---|
| `NchantdOfficeTodayOverview.initLowerWidgets` | `widgets/timelines.py:86-89` | No-op stub: comment says "subclasses or post-init scripts override with calendar / weather / tasks panes." |
| `Node.initModel` (diagram) | `widgets/items/diagrams.py:188-191` | No-op stub: log says "(no-op stub)". |

#### Stub view methods

| Method | File:Line | Status |
|---|---|---|
| `switch_to_account_tab` | `views.py:55-58` | Comment "PUSH to 0.0.3" but NOT in the canonical PUSH list — looks like a forgotten stub. |
| `on_window_move` | `views.py:60-65` | Comment "PUSH to 0.0.3" — not in the canonical PUSH list either. Same situation. |

#### Hard-coded placeholders that should be live

`widgets/config/accounts.py:79-86` shows "Storage: 0 GB / 10 GB"
and "Documents: 0" as static labels — never queries actual usage
or document count. Should query `self.app.model.user` and the
`doc_media` table for live numbers.

### Architecture (T-NEW series)

| ID | Subject | Status |
|---|---|---|
| T-NEW-001 | Tab icon + 5-digit/auto-name | Not started |
| T-NEW-002 | 35c050e4 working-state preservation (already addressed in H53+H59+H60 series; this entry is the historical label) | ✅ Done |
| T-NEW-003 | `save_mode` toggle UI + dispatch | ✅ Done — Sprint 14 |
| T-NEW-004 | Locks on App Nodes (Home / Journal / Settings) | Not started |
| T-NEW-005 #1 | `doc_media`/`doc_media_content` integer iteration | ✅ Done |
| T-NEW-005 #2 | Per-Pyffice-class `SERIALIZATION_VERSION` (58 subclasses) | ✅ Done — Sprints 16 |
| T-NEW-005 #3 | Primary instance registry — DB wire-up + UI browser | ✅ Done — Sprints 15 + 17 |
| T-NEW-006 | `NchantdDocument` widget-lookup dispatch (5 types) | ✅ Done — H53 + H60 |
| T-NEW-007 | Drop `.pyof` single-instance pickle format | ✅ Done — Sprint 15 |
| T-NEW-013 | `decrypt`/`encrypt` cipher wiring | ⏸ Deferred to PUSH 0.0.3 — Sprints 5/12 |
| T-NEW-014 | Trendline group init helper | ✅ Documented in Sprint 12 |

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