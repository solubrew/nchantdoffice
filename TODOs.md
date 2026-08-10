# NchantdOffice TODOs — current state (2026-08-06)

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
- NchantdOfficeJournalEditor always-save functionality fixed (outer save() now calls _parse_entry + parent.save)

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
- **test fix** test_script_open_format failing — test mock missing `.content` attribute
- **test fix** test_per_doc_type_settings_pane segfaulting in initView (nchantrs line 193)




---

## 1. Project snapshot

| Dimension | Value |
|---|---|
| Project | NchantdOffice |
| Type | Desktop GUI application (PySide6) |
| Branch | `gamma` (in sync with `origin/gamma`) |
| HEAD | `bcfb730` (nchantdoffice/gamma) |
| Working agreement | Internal projects are CORE INTEGRATED; never stub them out |
| Test env | `QT_QPA_PLATFORM=offscreen /home/solubrew/ENVs/sasquatch/bin/python` |
| Test command | `QT_QPA_PLATFORM=offscreen /home/solubrew/ENVs/sasquatch/bin/python -m pytest tests -q` |
| Current test surface | 20 passed (12 update_checker + 3 boot-hook + 5 review-pinning RED-tests still RED awaiting T-NEW-059/060). Pre-existing failure `test_app_action_has_position_int_nchantdoffice` is unrelated to T-NEW-058. |

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
| T-NEW-037 | Empty method stubs (analytics_charts, charts, toolbars) | ✅ Done — Sprint 29 (2 filled, 1 deferred to T-NEW-029) |
| T-NEW-038 | Database-save icon for internally stored documents | ✅ Done — Sprint 29 (_save_action picks save_database for internal docs) |
| T-NEW-039 | Refactor: move document-save hack to model + consolidate add_tab/add_document | ✅ Done — Sprint 30 (widget hack removed; model owns the doc_media syntax update) |
| T-NEW-040 | Toolbar init tech debt (redundant init_variables + MultiInstance switch) | ✅ Done — Sprint 29 (stale comment removed; _resolve_db_alias helper) |
| T-NEW-041 | Widget lookup from document_types table | ✅ Done — Sprint 29 (stale TODO removed; canonical lookup verified) |
| T-NEW-042 | Note position increment for multiple notes | ✅ Done — Sprint 29 (_compute_note_position helper) |

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
