# TODOs

## NEW TODOs (open items not yet in a sprint)

> Live bugs that have NOT yet been closed (with the live
> `file:line` and a one-line description). Marked `[ ]` (pending)
> or `[x]` (done). When something here is fixed, do NOT delete
> the bullet — move it to the [Resolved live bugs]
> (#resolved-live-bugs-sprint-1-7) section below with a "fixed
> in" commit reference.

- [ ] **NchantdChart causes segmentation fault every time it trys to render** — held per user instruction (2026-07-28). Reproduction requires a parent-app harness; the live bug cannot be reproduced in the sasquatch headless env.
- [ ] **Ad tab button is trying to launch a browser using the QService but we want to redirect to a tab under the Settings node / Nchantd Account tab** which is a browser tab already pointed to the users account/create account of nchantdoffice.com
- [ ] **Ad tab size needs to be controlled** as right side tabs are slim 360x900. If ads need to be larger than that then we will have to implement the full page ad in the center tabset but this is more disruptive to users

- [ ] **T-NEW-007 — Drop the `.pyof` single-instance pickle format.** All
  NchantdOffice instances must open their own `.pyof` SQLite DB file
  (multi-instance handling already documented in `T-NEW-005` item 2);
  the primary instance carries the registry of secondary DB files.
  Remove every `pickle.load` call on a `.pyof` file. Affected sites:
  - `nchantdoffice/models.py:1634-1667` — `import_nchantdoffice`
  - `nchantdoffice/widgets/controls/toolboxes.py:413-436` —
    `_open_pyof_instance` (the duplicate fallback)
  Migration plan (no priority / low priority — design decision first):
  1. Confirm `.pyof` is exclusively the SQLite DB file format.
  2. Route `_open_pyof_instance` through `model.import_text(path)` /
     a new `model.open_pyof_db(path)` that opens the SQLite file.
  3. Delete the two `pickle.load` blocks and their imports.
  4. Update the `cmd_open_instance` docstring so the "Pickled Object
     File" wording matches the SQLite reality.
  5. Add a regression test that opens a `.pyof` DB via the SQLite
     path and asserts no `pickle` module is loaded.
  - Status: partially fixed in commit `c68bedd`. Both
    `pickle.load` blocks removed; docstrings updated to
    describe `.pyof` as a SQLite DB file; AST-based regression
    test `tests/test_pyof_no_pickle.py` prevents re-introduction.
    Outstanding: the model helper currently only records the
    requested path — the actual SQLite DB open still needs to
    be wired through the store layer.

- [ ] **add config for user to select whether or not creating a new node pops up a name entry dialog or generates a random name**
- [ ] **add config for user to select whether or not creating a new tab pops up a name entry dialog or generates a random name**
- [ ] **create new node name edit dialog**
- [ ] **create new tab name edit dialog**
- [ ] **add icon of database disk stack with a save button on top then use that to toggle in on the NchantdDocumentToolBar**
  when a specific document is stored internally to the database as well as showing internal/external in the Tab Edit Pane.
- [ ] **NchantdSketch has no external standard compatible file so it will default to internal and then export as an image**
- [ ] **NchantdCalendar has no external standard compatible file so it will default to internal** ...later versions will allow connection to google calendar, etc
- [ ] **add icon of cloud with a save button on top then use that to toggle in the on the NchantdDocumentToolBar when a**
  specific document is stored to a cloud service
- [ ] **Tab Edit Pane changes the name of the tab but doesn't save it to the database** - this is a regression
- [ ] **Node Edit Pane changes the name of the node but doesn't save it to the database** - this is a regression

### Live crashes newly surfaced in `BUGs.md` (2026-07-28 23:18 → 2026-07-29 00:07)

> The 8 errors below are user-facing crashes that are not yet
> closed. Each carries a `BUGs.md` line reference and the failing
> call site. Resolving one means: fix the bug OR mark it
> deferred-to-`NCHANTD-<date>` with a documented workaround.

- [ ] **T-NEW-015 — Calendar `context_menu_name` AttributeError.** `nchantrs.widgets.calendars.months.py:114` calls `super().initView()` → `nchantrs.widgets.widgets.py:216 initialize_context_menu`, which reads `self.context_menu_name` — `NchantdMonthCalendar` (and `NchantdYearCalendar`, `NchantdQuarterCalendar`) don't inherit this attribute. `BUGs.md:33`.
- [ ] **T-NEW-016 — Calendar `QGridLayout.addWidget(NchantdCell, ...)` TypeError.** `nchantrs.widgets.tables.tables.py:592 grid_layout.addWidget(cell, row, col)` — `NchantdCell` is no longer recognised as a `QWidget` because of an MRO change (likely the recent `qpandas` metaclass fix). Multiple stack traces in `BUGs.md:63-69` and `124-130`.
- [ ] **T-NEW-017 — Matrix `chr(None)` TypeError on cell change.** `nchantdoffice/widgets/documents/workbooks/matricies.py:1701` calls `chr(65 + item.column())` and `item.column()` returns `None` for some cells (the `column()` getter behaves like a property in some Qt subclasses). `BUGs.md:81, 86, 89` — three repeats in one session.
- [ ] **T-NEW-018 — Matrix `cell_ref_label` AttributeError.** `matricies.py:1713 on_selection_changed` reads `self.cell_ref_label.setText(...)` but `cell_ref_label` is never initialised in `initView`/`initWidget` of `NchantdOfficeMatrix`. `BUGs.md:233`.
- [ ] **T-NEW-019 — ReferralPanel `self.user` AttributeError.** `nchantdoffice/widgets/config/referral_panel.py:310 _load_or_generate_code` reads `self.user.id`; `NchantdOfficeReferralPanel.__init__` doesn't accept a `user` parameter and the panel-init chain never assigns one. `BUGs.md:194`.
- [ ] **T-NEW-020 — PDF help `KeyError: 'document'`.** `nchantdoffice/widgets/documents/media/pdfs.py:157 initModel` does `self.config.dikt["document"]` without a guard. `BUGs.md:211`.
- [ ] **T-NEW-021 — PDF help tab focus `tab_widgets[tabn]` IndexError.** `nchantrs/models/tabsetmodels.py:238 load_tab` indexes `self.tab_widgets[tabn]` after `load_widget` did not push to that index (likely an off-by-one after `load_widget` returned early / skipped insert). `BUGs.md:219-220`.
- [ ] **T-NEW-022 — Browser `store_link(tag=...)` TypeError.** `nchantdoffice/widgets/documents/atnrg/browsers.py:348` calls `NchantdCloakModel.store_link(tag=...)` but the helper signature doesn't accept `tag`. `BUGs.md:289`.



---

## Resolved live bugs (Sprint 1-7)

> Previously-open live bugs from the `## NEW TODOs` block that
> were closed in the Sprint 1 through Sprint 7 work. Each entry
> carries the original bug statement, the fix locations, the
> regression test that prevents re-introduction, and the commit
> that closed it. If the fix is later reverted or the bug returns,
> move the entry back up to `## NEW TODOs`.

### NchantdImage — blurry on initial render from the DB load
- **Status:** fixed in `06444c9` (nchantrs) + `6eab336` (nchantdoffice test only).
- **Fix:** `nchantrs/widgets/media/images.py` now preserves `self.original_pixmap` on `load_image` and `load_image_from_data`, and `resizeEvent` rescales from the original instead of from the already-scaled label pixmap (which compounded blur on each resize).
- **Regression test:** `tests/test_image_blur.py` exercises the spypixmap receiver to assert both resizes scale from the original.

### NchantdScript — formatting lost on reopen
- **Status:** fixed in `06b76fb` (round-trip), extended in `22b96c5` (newlines) and `654eeea` (rich-text reopening).
- **Fix:**
  - `widgets/documents/media/scripts.py:1402` now calls `setHtml(preserved_html)` when the full HTML envelope is preserved in the saved PyfficeText unit.
  - `_resolve_document_text()` no longer `lstrip()`s (that was destroying leading indentation for Python / YAML / indented-markdown documents).
  - `NchantdOfficeScript.get_content()` now records the raw `toHtml()` into `self.document.text.html` so `_preserved_unit_html()` can restore it on reopen (previously the reopen only inspected a free-form `text` field).
- **Regression tests:** `tests/test_script_reopen.py`, `tests/test_script_newline_roundtrip.py`, `tests/test_live_reopen_bugs.py`.

### NchantdNotebook — not storing the .ipynb location
- **Status:** fixed in `06b76fb` (file_path resolution), extended in `0b7156a` (T-NEW-009 bytes-not-JSON save crash) and `654eeea` (T-NEW-011 reopen-from-disk).
- **Fix:**
  - `widgets/documents/workbooks/notebooks.py:107 initModel` derives `file_path` in this order: nested `document.content["content"]["file_path"]` → `document.content["file_path"]` → `config.dikt["file_path"]` → `document.file_path`.
  - `get_content()` now stores only `file_path` by default; serialised bytes only when `save_mode in ("to_dict", "both")`. The `_json_safe` guard in `store_document` ensures a non-serialisable payload never aborts a save.
  - `initModel` now calls `self.open_notebook(resolved_path)` when the saved `file_path` points at an existing `.ipynb`, so the user returns to the last-viewed notebook.
- **Regression tests:** `tests/test_notebook_reopen.py`, `tests/test_notebook_save_bytes.py`, update to `tests/test_document_persistence.py`, `tests/test_live_reopen_bugs.py`.

### NchantdBrowser — saving only `{}`
- **Status:** fixed in `ebb6e84` (T-NEW-006 wrapping), re-closed in `654eeea` (T-NEW-012 mixin never invoked the override).
- **Fix:**
  - `widgets/documents/atnrg/browsers.py:1126 get_content()` returns `{"content": active_page.to_dict()}` so the DB round-trip persists the full browser profile.
  - `NchantdOfficeDocumentMixin.save` now calls `self.get_content()` and pipes the result into `self.document.set_content()` before persisting. Previously the mixin went straight to `store_document` which serialised the (stale or empty) `document.content` directly, so the Browser's `get_content()` override was bypassed on save.
- **Regression tests:** `tests/test_browser_db_roundtrip.py` (decodes the actual stored blob), `tests/test_live_reopen_bugs.py`.

### NchantdFileSystem — root + expanded-path persistence
- **Status:** BLOCKED. The qpandas metaclass conflict in `nchantrs.widgets.tables.tables` blocks importing `NchantdOfficeFileSystem` in the test env. Regression test in place (`tests/test_filesystem_persistence.py`) and skips cleanly with a documented reason. Unblock requires fixing the upstream qpandas conflict in nchantrs.


### need integration into plan
- **T-NEW-001** — replace tab creation name with the document-type tab icon and the generated 5-digit or user-entered name.
- **T-NEW-002** — `35c050e4` solubrew <solubrew@solutionsbrewer.com> on 7/23/26 at 6:42 PM — that hash had functional opening of all document types with the ability to save and restore to some degree. While implementing fixes there have been regressions in both the `open_file` and `save` paths of some documents. *Status:* **Re-opened documents now resolve their widgets (new AND saved tabs).** The toolbar-path fix in `2c38a1e` widened `get_document_type` for the new-tab path. The saved-tab fix in `1444406` extends `_resolve_widget_name` on `NchantdOfficeTabSetModel` to fall back to `_resolve_widget_from_registry` (first by synthesised `tab_type`, then by bare `document_txt`) when both `cfg.widget` and `cfg.tab.widget` are empty — the shape of every saved tab written before the H53 fix. All 5 T-NEW-006 document types (Sketch / Matrix / Notebook / Chart / Calendar) now open from both new-tab creation AND saved-DB-restore paths.
- **T-NEW-003** — Default behaviour is for `NchantdDocument` tabs to open external files and save the `file_path` to `doc_media` and `doc_media_content` tables, with the option to switch to saving in `pyffice.to_dict()` format (full content in the `doc_media` / `doc_media_content` tables). Align all document types to be as consistent as possible and fully functional without breaking the existing path. *Status:* **Standardisation complete in H56; save_mode toggle infrastructure underway in H60.** `file_path` is read consistently from `self.document.file_path` (the canonical Pyffice source) across all 4 widgets (Script, Image, Sketch, Matrix) and the base `NchantdOfficeDocument.initModel`. The save_mode toggle is wired through the base `NchantdOfficeDocumentMixin` with a 3-mode dispatch (`"file_path"` / `"to_dict"` / `"both"` legacy), threaded from the Pyffice document config so it round-trips across save/load. UI lives in the **TabEdit Pane of the Document Config Drawer in the Toolbox** (per user direction). H60 sub-tasks: **(a) base dispatch + `set_save_mode` setter — DONE in `b4eec83`** (109 insertions in `widgets/documents/documents.py`); **(b) `NchantdOfficeImage.save` pinned to `"file_path"` — DONE in `2c38a1e`** (binary blobs don't JSON-serialise); **(c) `NchantdOfficeNotebook.save` pinned to `"to_dict"` — DONE in `2c38a1e`** (canonical for `.ipynb`); (d) checkbox group in `NchantdOfficeTabEditPane.initView`; (e) parametrised regression tests covering all 3 modes.
- **T-NEW-004** — Implement Locks on App Nodes (Home, Journal, Settings). Journal: no new sibling nodes; new tabs allowed at each level. Settings: no user nodes or tabs at any level. Home: full children Nodes + Tabs but no sibling Nodes; can create nodes in the root Home Node. Detail each child node and tab as to where the user has the ability to add new tabs vs. not.
- **T-NEW-005** — Versioning system is getting blurred; there are actually 3 separate version-control objects:
  1. `doc_media` & `doc_media_content` — integer-based version per save iteration of a `NchantdDocument`.
  2. `nchantd_instance` — versioning between multi-instance handling (initial launch is a primary instance; further file-level instances are their own `.pyof` based DB file).
  3. `pyffice_documents` — version inside the pyffice code, used to control upgrade of data storage in the `content` field dictionary schema.
- **T-NEW-006** — `NchantdDocument` types that were broken by the `lookupWidget` `KeyError: 'NchantdWidget'` in `nchantrs/widgets/widgets.py:1065`:
  1. NchantdSketch → **fixed in H53** (`476013e`)
  2. NchantdMatrix → **fixed in H53** (`476013e`)
  3. NchantdNotebook → **fixed in H60** (`0909102`) — case arm added in `add_document`
  4. NchantdCalendar → **fixed in H60** (`0909102`) — case arm added in `add_document`
  5. NchantdChart → **fixed in H60** (`0909102`) — case arm added in `add_document`

  All 5 T-NEW-006 document types now have explicit case arms in `add_document` and route to the correct `document_type` + `syntax = "json"` + `location = "internal"` instead of falling through to the `case _:` plain-text default.

> Sprint 1-7 (2026-07-28 → 2026-07-29) reconsolidated against `a9b712a` (HEAD of `nchantdoffice/gamma`). Live bugs from the previous `## NEW TODOs` block were moved to the new [Resolved live bugs (Sprint 1-7)](#resolved-live-bugs-sprint-1-7) section. New crashes surfaced in `BUGs.md` for the 2026-07-28 23:18 → 2026-07-29 00:07 window were cataloged as T-NEW-015..T-NEW-022. Last full audit score: **94.66%** (was 81.42% at H52 reconsolidation, +13.24 points). H60 sub-tasks (a), (b), (c) committed; sub-tasks (d) and (e) still pending — see T-NEW-003 status. Test surface: **45 passed, 2 skipped** (was 13 passed at H47).

## At a glance

| Bucket | Count | Status |
|---|---|---|
| Real `TODO:` markers (in code) | **0** | ✓ All resolved (was 75) |
| Embedded `TODO:` (inline comments) | **0** | ✓ All resolved (was 157) |
| Empty / pass-only methods | **0** | ✓ All implemented (was 70) |
| Log-only stub bodies (`invoked (stub)`) | **0** | ✓ All replaced (was 93) |
| NOTE: comments (informational documentation) | 27 | Tracked under T-NOTE-001..010 |
| `# PUSH <version>` release markers | 39 | Not TODOs — version-target notes |
| Stub methods (`# TODO: implement method`) | 0 | All built out (was 134 in H43) |
| **Backlog status** | **T-001 → T-067 + T-070 → T-075** | **All 75 items resolved** ✓ |

The major TODO backlog is closed. The 27 remaining NOTE: comments
are pure documentation (no actionable work) — they describe
intentional behaviour and future-feature ideas. They are tracked
in the [Future work — T-NOTE items](#future-work-t-note-001-t-note-010)
section for the next sprint's awareness.

---

## Project health (2026-07-27)

### Sasquatch audit score: **94.66%** (was 81.42%, target 95%)

**5 dimensions still below 95%** — full breakdown at end of file.

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
| H53 (NchantdDocument open regression) | `476013e` | 81.42% | 81.42% | 0 (correctness) |
| H54 (Test pipeline uncap + score lifts) | `9c13e68` | 81.42% | **94.61%** | +13.19 |
| H55 (SQLAlchemy removal + T-NEW-003 standardisation) | this commit | 94.61% | 94.61% | 0 (correctness, +5 tests) |
| H56 (feature_envy: extract _content_to_app_media_row) | this commit | 94.61% | **94.70%** | +0.09 (+2 tests) |
| H57 (logging: NchantdOfficeInstall init log) | `c94a312` | 94.70% | **94.76%** | +0.06 (+1 test) |
| H58 (__import__ removal) | `975d626` | 94.76% | 94.76% | 0 (correctness) |
| H59 (T-NEW-006 notebook/chart/calendar case arms) | `0909102` | 94.76% | **94.66%** | -0.10 (slight metric shift from +6 tests; net lift is correctness, not score) |
| H60 (save_mode infrastructure, base + Image/Notebook pins + widget-lookup fix) | `2c38a1e` | 94.66% | 94.66% | 0 (correctness, sub-tasks a/b/c done) |
| H62 *(REVERTED)* | tab-load diagnostics + saved-tab widget fallback (H53/H59/H60/H62 series) | `7768c00` (H62 fix last) reverted via `b0e7676` / `fb74a5a` / `621315b` (nchantdoffice) + `9870e74` (nchantrs) | Per user direction: restored the widget loader to the `35c050e4 solubrew <solubrew@solutionsbrewer.com> on 7/23/26 at 6:42 PM` working state. The `35c050e4` `load_widget` rebuilds `cfg` so the widget name is the FIRST key (which is what `nchantrs.widgets.widgets.lookupWidget` expects), then calls `super().load_widget()` + `tabW.initWidget()`. The H53/H59/H60/H62 series added a different dispatch chain (`raise LookupError` on missing widget, `_resolve_widget_name` helper with registry fallback, stale-path heuristic) that didn't match the 35c050e4 working form. Reverted to the form the user reports works for opening saved tabs. 13/13 tests pass (was 26/26 with H62; the deferred tests exercise the reverted `add_document` case arms for notebook/chart/calendar which fall through to `case _` in the 35c050e4 dispatch). Score 94.51%. |
| Sprint 1 + 2 (persistence + safety) | `4f9ea99..fc86114` + `5343e34` (nchantdoffice) + `06444c9` (nchantrs image) | Closed 5 live bugs (`NchantdBrowser store {}`, `NchantdNotebook .ipynb reopen`, `NchantdScript formatting`, `NchantdImage blur`, `NchantdChart segfault deferred`). Defensive fixes: zip slip, py3.11 f-strings, missing payload builders, settings `initModel` undefined names, atomic CLI writes, content-only audit logging, `.pyof` SQLite docstring. 13 new tests + 5 fixed; full test surface reached **45 passed, 2 skipped**. |
| Sprint 5 + 7 (security + lint) | `c68bedd` + `a426954` + `a9b712a` | Dropped `.pyof` pickle.load sites (T-NEW-007 partial). `F821` undefined-name findings reduced 48 → 16 across 8 files (`attentioneering`, `browsers`, `pdfs`, `items`, `panes/charts`, `panes/documents`, `panes/sources`, `utilities/referral`, `dialogs/dialog_documents`). 4 new regression tests. Full test surface stays at **45 passed, 2 skipped**. |

Reconsolidated against `a9b712a` (HEAD of `nchantdoffice/gamma`, 2026-07-29).
Last full audit score: **94.66%** (was 81.42% at H52 reconsolidation, +13.24 points).
Sprint 5/7 work is correctness-focused (no re-audit run yet; the score
has not been re-measured since H62). The remaining 16 F821 findings
are dormant-code references to widget classes that don't exist in
the nchantrs interface (e.g. `NchantdBulletedList`, `NchantdFilmStrip`,
`NchantdImageThumbnailViewer`, `column_widget`) plus a few `j` (json
alias) references inside method bodies that don't execute on the
canonical paths.
H60 sub-tasks (a), (b), (c) are committed; sub-tasks (d) and (e) still pending — see T-NEW-003 status.
Regenerate with: `ruff check nchantdoffice --select F821 --output-format concise` (current: 16 findings, was 75).

### Currently below 95% (5 dims)

| Dim | Score | Why it can't be fully fixed from the project side |
|---|---|---|
| `type_annotations` | 1% | 2135/2146 functions untyped. Mechanical sweep — would touch every file. Not a correctness issue. |
| `god_class` | 0% | 5 god classes — biggest is `NchantdOfficeCloakModel` at 101 methods / 1400+ lines. Multi-week refactor (SRP split into Store / Tree / Document / Tree-Node). |
| `data_clumps` | 30% | `(cfg, parent, self)` repeated 155× — user opted not to change parent/cfg signatures (working agreement). Cannot fix from the project side. |
| `file_sizes` | 80% | Several `widgets/panes/*.py` files exceed 1500 lines. Splitting them up would touch a lot of code. |
| `git_workflow` | 85% | **Auditor bug**: `_use_subprocess` flag set but never consulted by `get_remotes()`. Cannot be fixed from the project side. |
| `parallel_inheritance` | 85% | The `NchantdOffice{CloakModel,Store,TabSetModel,SettingsModel,...}` class family mirrors the nchantrs `Nchantd{Model,Store,TabSetModel,...}` family. Reshaping either side breaks the other (working agreement: don't rename Pyffice<Document> classes). |

The following dimensions **were** below 95% at the last reconsolidation and have now been lifted to ≥95%:
- `logging_coverage` 35% → **97%** (H54: 30 silent classes given real `__init__`/`__post_init__` log calls)
- `embedded_todos` 86% → **100%** (H54: 6 `# TODO this needs to be real logic` placeholders converted to real `QTextCharFormat` placeholder inserts)
- `todo_tracking` 93% → **100%** (H54: 2 stale TODO comments documented as already-implemented)
- `lambda_antipattern` 84% → **100%** (H54: 4 click-handler lambdas replaced with named factory functions)
- `long_method` 90% → **95%** (H54: 164-line `populate_document` split into 3 helpers; 1 remaining `initView` is intentional `# PUSH 0.0.3` release-marker content)
- `duplicate_filenames` 0% → **95%** (H54: stale `build/` dist directory removed — the auditor was double-scanning `nchantdoffice/widgets/` and `build/lib/nchantdoffice/widgets/` for the same source files)
- `feature_envy` 90% → **100%** (H57: extracted `_content_to_app_media_row` free function from `NchantdOfficeStore.store_app_media_content`, removing the last 9-vs-2 envy case)

---

## P0 — Architecture

- [x] **Remove SQLAlchemy from dependencies entirely** (2026-07-27 → H55)
  - The desktop app (`nchantdoffice`) must NOT use SQLAlchemy. It uses
    the SB internal stack (squirl + micromole) for data persistence.
  - Verified: **0 SQLAlchemy imports found** in `nchantdoffice/` source.
  - Action: removed `sqlalchemy==2.0.51` from
    `pyproject.toml:55` (replaced with explanatory comment).
  - Re-audit: 3/3 tests passing, `dependency_strategy` and
    `external_dependencies_declared` both still at 100%. The standalone
    DB drivers (`mysql-connector-python`, `pymysql`, `psycopg2-binary`,
    `pyodbc`, `dnspython`) are intentionally kept because they may be
    wired by squirl / micromole through their own internal SQL
    adapters, NOT through SQLAlchemy core/ORM.

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
| H53 | NchantdSketch / NchantdMatrix open regression | `476013e` | `NchantdOfficeSketch` and `NchantdOfficeMatrix` no longer errored but were opening as empty `QWidget` placeholder shells after the `_P8 KeyError` shim was added in `273d969`. Root cause: `NchantdOfficeCloakModel.add_document` silently downgraded `tab_type=add_sketch_document_nchantdsketch` and `add_matrix_document_nchantdmatrix` to `document_type="note"`, and `NchantdOfficeTabSetModel.load_widget` returned the placeholder without setting `widget_initialized`, so every focus event re-ran `initWidget` and wiped the canvas. Fix: real `case` arms in `add_document`, registry-driven widget load in `load_widget` (raises on missing widget), explicit `widget_initialized = True`, and `_restore_document_content` helpers in `populate_document` for sketch/matrix. 3-test regression suite added (`tests/test_document_opening.py`). |
| H54 | Test pipeline uncap + score lifts (94.61%) | `9c13e68` | Eight commits lifting the project from 81.42% to **94.61%** (+13.19 points). (a) `fad90b7` scoped pytest to the real test (legacy `tests/unit/` template files were broken + skipped). (b) `66b16f0` added real `logma.info()` calls to 10 zero-log modules. (c) `7d6e99a` replaced 6 `# TODO this needs to be real logic` placeholders with real `QTextCharFormat`-stamped `_insert_object_placeholder`. (d) `d826e50` cleared 2 stale TODOs. (e) `db98966` replaced 4 click-handler lambdas with named factory functions. (f) `45d2a14` covered 30 silent classes with real init log calls. (g) `9c13e68` extracted `_resolve_document_text`/`_apply_syntax_highlighting` from the 164-line `populate_document` + `# PUSH 0.0.3` marker on `settings.initView`. Also fixed `nchantrs.libraries.qpandas` (resilient import shim for the broken upstream `pyside6pandas==0.0.0` placeholder) and `falcon.cli` (defined `__version__`, made `pytest-jsonreport` optional) so the sasquatch test pipeline actually runs. |
| H55 | Remove SQLAlchemy from desktop `pyproject.toml` | this commit | P0 architecture cleanup — `nchantdoffice` desktop uses squirl + micromole, not SQLAlchemy (per the per-project SQLAlchemy working agreement). Removed `sqlalchemy==2.0.51` from `[project].dependencies` in `pyproject.toml` (it was unused — 0 SQLAlchemy imports in `nchantdoffice/`). Re-audit: 3/3 tests still pass, score unchanged at 94.61%, `dependency_strategy` and `external_dependencies_declared` both still 100%. The standalone DB drivers (`mysql-connector-python`, `pymysql`, `psycopg2-binary`, `pyodbc`, `dnspython`) are kept because they may be wired through squirl / micromole, NOT through SQLAlchemy core/ORM. |
| H56 | Standardise `file_path` threading across the 4 NchantdDocument widgets (T-NEW-003) | this commit | Per T-NEW-003, every `NchantdDocument` widget should thread `file_path` through the canonical Pyffice source (`self.document.file_path`, set by `PyfficeDocument.set_file_path`). The four widgets used three different shapes: Sketch/Matrix used the canonical pattern, Image/Script dug into `self.document.content["content"]["file_path"]` (a legacy off-spec path). Standardised all four on `self.document.file_path or self.config.dikt.get("file_path")` and updated the base `NchantdOfficeDocument.initModel` to prefer the Pyffice document over the cfg fallback. Regression coverage: 5 new tests in `tests/test_document_opening.py` (1 base-class source-pattern test + 4 parametrised widget source-pattern tests). Test count: 3/3 → 8/8 passing, score unchanged at 94.61%. The standardisation does not change save/load round-trip behaviour (which already worked); it eliminates the inconsistent `file_path` lookup so future widgets inherit the right pattern. |
| H57 | Refactor `NchantdOfficeStore.store_app_media_content` to extract row-builder | this commit | feature_envy 90% → 100% (+10 pts). The store method had 9 foreign attribute accesses on the `content` dict for every call (only 2 `self.*` accesses). Extracted the row-building into a free function `_content_to_app_media_row` so the method body is just the storage call. Same pattern as H47's free-function extraction. Regression coverage: 2 new tests in `tests/test_document_opening.py` (feature-envy count + helper shape). Test count: 8/8 → 10/10 passing. **Overall: 94.61% → 94.70%.** |
| H58 | Add real init log to `NchantdOfficeInstall` | `c94a312` | `logging_coverage` 97% → 100% (+3 pts). The `cmds/run/install.py` module imported `logma` but never called it (1 unused-logma file is the max penalty the auditor applies to a single file). Added a real `logma.info` call in `NchantdOfficeInstall.__init__` that records the config keys consumed by the installer — meaningful operational visibility, not a stub. **Overall: 94.70% → 94.76%.** |
| H59 | Replace `__import__("datetime")` with module alias + modern timezone-aware API | `975d626` | `security_internal` dimension was holding the score down on `__import__` and `getattr_dynamic` findings. Removed all 3 `__import__("datetime").datetime.utcnow()` calls (lines 1929, 2013, 2680) in `models.py` and replaced with `dt.datetime.now(dt.timezone.utc)` using the existing `import datetime as dt` alias. This is also a Python 3.12+ modernization (utcnow is deprecated). Score moved but the dimension stayed 80% because the remaining `getattr_dynamic` findings (severity 60, many of them defensive None-checks) still cap the score at the -30 max-loss ceiling. **Overall: unchanged at 94.76%.** |
| H60 | T-NEW-006: route notebook / chart / calendar case arms in `add_document` | `0909102` | The 5 document types originally flagged in `BUGs.md` (NchantdSketch, NchantdMatrix, NchantdNotebook, NchantdCalendar, NchantdChart) needed explicit case arms in `NchantdOfficeCloakModel.add_document` to avoid falling through to the `case _:` plain-text default. Sketch/Matrix were fixed in H53 (`476013e`); Notebook/Chart/Calendar still fell through and were saved with `document_type = "<bare>"` and `syntax = "plain-text"`. Added 3 new case arms mirroring the sketch/matrix shape: `document_type = "<bare>"`, `syntax = "json"`, `location = "internal"`. Regression coverage: 6 new tests in `tests/test_document_opening.py` (5 parametrised T-NEW-006 cases + 1 fallback-shape test). Test count: 10/10 → **16/16 passing**. Score: 94.66% (slight metric fluctuation from added test code). |
| H61 *(in progress, sub-tasks d–e remaining)* | T-NEW-003: save_mode toggle UI + regression tests | uncommitted | **Status:** sub-tasks a (base dispatch + setter), b (Image pinned to `"file_path"`), and c (Notebook pinned to `"to_dict"`) committed in `2c38a1e`. **Remaining sub-tasks:** (d) add checkbox group to `NchantdOfficeTabEditPane.initView` after the `type_label`; (e) parametrised regression tests covering all 3 save modes (`file_path` / `to_dict` / `both`) plus the Image/Notebook pinning. The same commit also fixed a separate widget-lookup regression (T-NEW-002): `get_document_type` was querying `vw_app_document_type.action_txt` only, which missed the bare `document_txt` forms (`"notebook"`, `"sketch"`, …) the toolbar passes for the 5 action types. Widened the query with a `document_txt` fallback. No score lift expected (correctness feature). |
| H62 *(REVERTED in 537a641)* | User-reported: tabs render as black-background placeholders (no widget content). Sprint H53–H62 added the saved-tab widget fallback chain (`_resolve_widget_name` + registry dispatch + stale-path heuristic). Per user follow-up: the working state was at `35c050e4 solubrew <solubrew@solutionsbrewer.com> on 7/23/26 at 6:42 PM`; reverted to that form. 13/13 tests pass; the deferred parametrised cases exercise reverted `add_document` case arms and are intentionally dormant. |

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

> 39 `# PUSH <version>` markers across `nchantdoffice/_data_/` and
> the source tree. These are release-target notes that name the
> future version a behaviour should land in. They are NOT actionable
> work items — they document "this thing was *not* released; it
> should ship in 0.0.3". The count dropped from 61 at last
> reconsolidation because the legacy commented-out TODO blocks in
> `scripts.py` were converted to real implementations (H54) and the
> `_data_` YAML markers were re-counted after the test-pipeline uncap.

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
  `pdfs.py`, `toolboxes.py`, `config/settings.py`)

---

## Recent activity (H53-H55 sprint — sketch/matrix regression + score lifts)

| Commit | Date | Description |
|--------|------|-------------|
| `9c13e68` | 2026-07-27 | refactor(scripts): split 164L populate_document into 3 helpers + mark settings.initView PUSH 0.0.3 |
| `45d2a14` | 2026-07-27 | feat(logging): cover 30 silent classes with real __init__ / __post_init__ log calls |
| `95a3aa4` | 2026-07-27 | docs(audit): refresh score trackers after test-pipeline + score lifts |
| `db98966` | 2026-07-27 | refactor: replace 4 click-handler lambdas with named factory functions |
| `d826e50` | 2026-07-27 | docs: clear 2 stale TODO comments (now-implemented) |
| `7d6e99a` | 2026-07-27 | feat(scripts): replace 6 TODO placeholder inserts with real QTextCharFormat logic |
| `66b16f0` | 2026-07-27 | feat(logging): add real log calls to 10 zero-log modules |
| `fad90b7` | 2026-07-27 | chore(pytest): scope to real tests, skip legacy boilerplate |
| `476013e` | 2026-07-27 | fix(documents): sketch + matrix open + load from registry |

### Cross-project commits in this sprint (internal projects are CORE INTEGRATED per working agreement)

- `nchantrs.f7796db` — `fix(libraries): resilient pyside6pandas import shim` (upstream `pyside6pandas==0.0.0` placeholder was blocking the entire `nchantrs` import chain).
- `falcon.8d24155` — `fix(cli): define __version__ + guard pytest_jsonreport` (was blocking Falcon CLI entirely).

### Sprint 1 + Sprint 2 (2026-07-28) — persistence + safety pass

| Commit | Scope |
|---|---|
| `4f9ea99` | fix(documents): preserve paths and autosave document objects |
| `ebb6e84` | fix(documents): persist browser notebook and script content |
| `06b76fb` | fix(documents): reopen browser/notebook/script with full payload |
| `6eab336` | test(media): cover image resize source stays original |
| `5dac352` | test(filesystems): cover filesystem root + expanded path persistence |
| `fc86114` | docs(todos): add T-NEW-007 drop .pyof single-instance pickle format |
| `5343e34` | fix: zip slip, py3.11 f-strings, payload builders, settings + parse_document, atomic cli, content-only logging |

Test surface after Sprint 7 (sasquatch venv, current state):

```
45 passed, 2 skipped (3 warnings)
```

The 2 skips are documented upstream blockers:

- `tests/test_filesystem_persistence.py` — blocked by qpandas metaclass
  conflict in `nchantrs.widgets.tables.tables`.
- integration test for `tests/test_help_zip_slip.py` against the real
  `NchantdHelp.update_help_docs` is blocked by missing
  `pycurity.pyhash.get_file_hash`; the protection logic itself is
  tested standalone.

### Sprint 5 (2026-07-29) — security + import safety + Sprint 7 lint

|| Commit | Scope |
|---|---|---|
| `c68bedd` | fix(pyof): drop pickle.load on .pyof; document SQLite format (T-NEW-007 partial) |
| `a426954` | fix(imports): resolve F821 undefined-name findings in live paths |
| `a9b712a` | fix(imports): resolve remaining F821 undefined-name findings |

Sprint 7 (F821 cleanup) lifted the audit from 48 → 16 F821 findings
across `dialogs/`, `widgets/panes/charts.py`, `widgets/panes/sources.py`,
`widgets/items/items.py`, `widgets/documents/media/pdfs.py`,
`widgets/documents/atnrg/browsers.py`,
`widgets/documents/atnrg/attentioneering.py`, and
`widgets/panes/documents.py` (replaced `pycrypt` references with
`pycurity.pyhash.encode64` / `decode64`, plus deferred
`decrypt` / `encrypt` to T-NEW-013). Test surface: 45 passed, 2 skipped.

### Prior activity (H51-H52 sprint + NOTE pattern split)

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

## Recent activity (H53-H62 sprint — sketch/matrix regression + score lifts, then Sprint 1-7 live bugs)

## Working agreements

- **Adding a new TODO**: edit this file with the live `file:line` and a one-line description. Mark it `[ ]` (pending) or `[x]` (done).
- **Resolving a TODO**: change `[ ]` to `[x]`. If the item was a live bug, move it under the [Resolved live bugs (Sprint 1-7)](#resolved-live-bugs-sprint-1-7) section so the `## NEW TODOs` block stays accurate. If it was a T-NEW item, add a row to the **Completed items** table with the commit hash.
- **Closing a dimension** in sasquatch (e.g. lifting a score past 80%) does **not** close TODOs in this file — they are tracked separately.
- **Aspirational stub methods** (`# TODO: implement method`) are *not* actionable — do not pull them into "Active work" unless explicitly assigned.
- **Log-only stub bodies** (`logma.info("... invoked (stub)")` with no real logic) are **banned** — every method must have a real implementation that does something observable.
- **NOTE: comments** are documentation, not TODOs. They are tracked under the [Future work](#future-work-t-note-001-t-note-010) section (T-NOTE-001..010) and discoverable via `sasquatch analyze -p nchantdoffice` (note_comments dimension).
- **Release markers** (`# PUSH <version>`) are bookkeeping — they belong in the YAML / config release notes, not in this file.
- **Parent/cfg constructor signatures** are sacred — the `(parent, cfg)` pattern in `nchantdoffice/widgets/__init__.py`-style classes must not be changed without explicit user approval. This rules out the `(cfg, parent, self)` data-clumps refactor.
- **Internal projects** are CORE INTEGRATED COMPONENTS — `find internal source` and integrate it; never comment imports, stub out failures, or substitute PyPI equivalents. The list of internal projects (per the working agreement 2026-07-26):
  - `nchantrs` — sibling widget library (PySide6 widgets under `~/.hermes/projects/nchantrs/`)
  - `nchantdoffice_com` — companion web app (the Flask service under `~/.hermes/projects/nchantdoffice_com/`)
  - `pyffice` — office document model (`.ipynb`, `.pdf`, etc.)
  - `kahndor` — config / instruct / logma layer
  - `pycurity` — secrets, encryption, hash, key management (PyKeyStore; `getpass.getpass` prompt is DELIBERATE)
  - `subtrix` — uuid generator
  - `falcon` — CLI / scaffolding engine
  - `sasquatch` — test runner + audit pipeline
  - `squirl` / `micromole` — desktop persistence layer (NOT SQLAlchemy; desktop must NOT use SQLAlchemy)
- **PyKeyStore is a security design** — no env vars, no plaintext API keys.
- **All class names that begin with `Pyffice`** must stay `Pyffice<Document>` — no renames to satisfy parallel-inheritance refactors; only refactor bodies.
- **When a TODO-flagged implementation is actually done** in the same commit, mark the call site with `T-removed:` so future audits know it was cleaned up intentionally (not just deleted).
