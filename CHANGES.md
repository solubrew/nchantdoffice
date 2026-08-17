# CHANGES.md - NchantdOffice Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

> **Reality anchor (2026-08-16, gamma `5b6397e`):** This block
> consolidates work from T-NEW-110 through T-NEW-137 (all shipped
> 2026-08-10 → 2026-08-15) plus the filed-but-open cards
> T-NEW-138 through T-NEW-147. The T-NEW-049 through T-NEW-109
> cards have their own entries in the prior `[Unreleased]` block
> below this one — kept intact for traceability. See
> [`TODOs.md`](./TODOs.md) for the canonical card index and
> commit hashes.

### Added (T-NEW-110..137)

- **T-NEW-110** Packaging + ruff config (`678e59e`) — real
  `pyproject.toml` description, `MANIFEST.in`, ruff lint config;
  closes the "[Unreleased] Added" entry that referenced a
  placeholder.
- **T-NEW-114** `.pyof` import dispatch consolidation
  (`f81c8a7`) — `cmd_import_local_file` routes `.pyof` →
  `cmd_import_pyof` (was → `model.import_nchantdoffice`);
  `cmd_open_local_file` routes `.pyof` → `cmd_import_local_file`
  (was → `_open_pyof_instance`); `cmd_import_pyof` offloads to a
  `_PyofImportWorker` on a `QThread` (was synchronous on GUI
  thread, blocked on long `.pyof` reads). 5 new tests pin the
  dispatch + worker thread. Follow-ups: `d0075b3`
  (re-architect via `sonql.Doc` + model funnels),
  `6480f77` (refresh tree widgets), `6f0724e`
  (re-parent top-level imports), `aaf74b7` (also re-parent rows
  parented to the starting-node pid), `0f3d6a3` (resolve
  selected nid from item widgets, not just dicts), `8d217fe`
  (refresh inner tree in place — never rebuild the container),
  `1cda19f` (scope re-parent to source `doc_tree_node` rows
  only).
- **T-NEW-124** Doctype guard — strict-dtd payloads restore as
  HTML (`d8d228d`) — `_apply_syntax_highlighting` in
  `widgets/documents/media/scripts.py` now fingerprints the
  stable `rec-html40/strict.dtd` doctype on the first 2048 chars
  (case-insensitive, tolerant of spacing/quote variants) and
  routes the payload to `setHtml(text)` regardless of
  `document.syntax`. 7 new tests in
  `tests/test_script_doctype_guard.py`.
- **T-NEW-129** Seed `app_user` row on initial install
  (`7da0d1e`) — `bootstrap_app_user` + `store_app_user` +
  `get_app_user` wired from `run_on_launch` so the cloak model
  has a user row to read on first boot. **NOTE: live traceback
  2026-08-15 22:19:02 surfaces two regressions in this wiring;
  tracked under T-NEW-146 and T-NEW-147.**
- **T-NEW-130** Top-level new-node toolbar lands at `pid=0`
  (`ac448ad`) — `NchantdNewDocumentSigil.top_level` flag +
  `launch_new_document_sigil` signals the rootnode dispatch.
- **T-NEW-131** Deny child-node creates under
  Home/Journal/Settings (`fc61c4e`) — `is_locked_pid` +
  `is_locked_parent` helpers; `add_node`/`add_node_app` refuse
  children of locked trees for all users.
- **T-NEW-132** Deny tab create/delete in Settings tree
  (`87ace4d`) — `is_locked_tab_parent` helper; `add_tab`/
  `delete_tab` refuse Settings-tree tab ops for all users.
- **T-NEW-133** Sort buttons sort the entire subtree
  (`8857081`) — `cmd_sort_children` + `_resolve_sort_direction`
  + `_sort_subtree` helper; every descendant depth is reordered
  (asc/desc) and persisted.
- **T-NEW-134** Get Pro button visibly green (`096e6c9`) —
  `_apply_bg_color` helper on `NchantdOfficeDocumentMixin` sets
  background-color via `setStyleSheet`, paired with white text
  for contrast. Follow-up `5831dd1` swaps green for dark orange
  (better contrast in the disabled state, per the user's
  live-testing feedback).
- **T-NEW-135** 100-node cap redirects to Nchantd Account with
  reason param (`5bf6f3d`) — fixed dead-code bug in
  `_check_max_nodes_for_user`; `redirect_to_get_pro` accepts a
  `reason`; `NchantdAccountSettings` appends `?reason=` to the
  compare URL.
- **T-NEW-137** Pre-flight `.pyof` import against the 100-node
  cap (`1fd8d60`) — before any row is copied, the import worker
  computes the source's net node count and refuses the import
  if it would push the host over the cap; redirects to Get Pro
  via the same path as T-NEW-135.
- **T-NEW-146** `_build_app_user_payload` generator coercion
  (2026-08-16) — `NchantdUser.get_password` is a generator
  function so `user.pword` is a generator instance by default;
  the payload-builder's duck-typed branch was passing it
  through verbatim, and `squirl._store` exploded on deepcopy
  with `TypeError: cannot pickle 'generator' object`. Fix:
  `_coerce_scalar(value)` helper unwraps iterators/generators
  (`next()` on the first yielded value) and falls back to
  `str()` for any other non-scalar.3 new regression tests in
  `tests/test_app_user_bootstrap.py`.
- **T-NEW-147** `get_app_user` fallback routes through the store
  layer (2026-08-16) — the fallback branch was calling
  `self.get_table(...)` (a method that doesn't exist on
  `NchantdOfficeCloakModel`), so every fresh-boot where
  `_sqlite_connection` was unbound raised `AttributeError` and
  logged `get_app_user failed: 'NchantdOfficeCloakModel' object
  has no attribute 'get_table'`. Fix: route through
  `self.store.get_table` (the store-layer method). 2 new
  regression tests in `tests/test_app_user_bootstrap.py`.

### Changed (T-NEW-110..137)

- **T-NEW-121** em-dash sweep + encoding-declaration placement —
  197 files affected by the `30593b9` SyntaxError incident;
  em-dash removed from comments/docstrings throughout (per
  Python 3.12 tokenizer rule for modules whose `# coding:` line
  is positioned after a non-ASCII line). Encoding declarations
  moved to the first or second line where present.
- `nchantdoffice/__init__.py` - Added version and config exports
- `nchantdoffice/widgets/items/items.py` - Renamed `self.parent` → `self.parent_widget`
  across `NchantdOfficeDocumentCatalogItem`, `NchantdOfficeSourceCatalogItem`,
  `NchantdOfficeTreeNode` to prevent shadowing `QTreeWidgetItem.parent()`

### Fixed (T-NEW-110..137)

- **H25 — Catalog Tab Wrong Child Count** (`nchantdoffice` consumer of `nchantrs fa05530`):
  Root cause was in parent library `NchantdNode.loadChildren()` which inconsistently
  used `parentid` vs `pid_txt` for parent filtering. Fix standardized on `pid_txt`.
  Visible in catalog tab child counts across all node types.
- **H27 — Nchantd Image Save Mode (Internal vs External)** (`commit c45cfc5`):
  Enforced canonical external file storage mode in `widgets/documents/media/images.py`;
  internal base64 mode now deprecated with runtime warning. Eliminates round-trip
  corruption and orphan files.
- **H28 — Browser Pin Tab Persistence** (`commit 87a5264`):
  Fixed `open_new_window()` routing through pinned-aware center pane tabset in
  `widgets/documents/atnrg/browsers.py`; corrected `save()` to read `self.pinned`
  (was checking non-existent `self.pin`); `pin_page()` and `populate_document()`
  now respect `self.pinned` state. "Pin Tab" action persists; links in pinned
  tabs no longer open new tabs.
- **H29 — Tree Node Drag-and-Drop Regression** (`commit c45cfc5` + nchantrs `fa05530`):
  Two-part fix — (1) `nchantrs/widgets/items/nodes.py` `NchantdNode.initModel()` now
  stores the full node dict in `UserRole` for drag-drop; (2) `nchantdoffice/widgets/trees.py`
  `getNid()` reads `nid_txt` from the `UserRole` dict. Drag-drop, drop targets,
  and reordering restored.
- **H30 — `setData()` Argument Order** (`nchantrs commit 5afde9d`):
  `NchantdNode.initModel()` in `nchantrs/widgets/items/nodes.py:380` now calls
  `self.setData(0, Qt.UserRole, self.node)` — the correct argument order is
  `(column, role, value)`. Previously the args were inverted, storing the role ID
  in column 0, which silently failed and produced empty `UserRole` data. This
  compounded with H29 to break drag-and-drop in nchantdoffice.
- **H31 — `self.parent` Shadowing `QTreeWidgetItem.parent()`** (`commit a01714c`):
  `QTreeWidgetItem` subclasses in `nchantdoffice/widgets/items/items.py`
  (`NchantdOfficeDocumentCatalogItem`, `NchantdOfficeSourceCatalogItem`,
  `NchantdOfficeTreeNode`) had `self.parent = parent` in their constructors, which
  shadowed Qt's built-in `parent()` method. This caused
  `TypeError: 'NchantdOfficeTreeNode' object is not callable` whenever Qt called
  `.parent()` on a tree item — most visibly in drag-and-drop `_is_descendant()`
  checks. Renamed `self.parent` → `self.parent_widget` across all three classes.
  nchantrs mirrored the rename across `NchantdItem`, `NchantdTreeItem`,
  `NchantdTreeNode`, and `NchantdTree` (commits `57839d2` + `be8a582`).
- Lambda antipattern in toolbar buttons (fixed variable capture)
- Signal inheritance in NchantdNewDocumentToolBar
- Incorrect super().__init__() calls in toolbar classes
- 4 inline TODOs in `widgets/items/items.py` resolved (2026-07-11)

### Filed (open as of 2026-08-16) — NOT YET SHIPPED

These T-NEW cards are filed in `TODOs.md` and awaiting
implementation. They are listed here so the unreleased-block
mirror stays truthful about outstanding work; do **not** move
them to "Added"/"Fixed" until they ship.

- **T-NEW-115** Creating new Nodes at the top level is blocked
  (filed from `testing-report_20260815.md`).
- **T-NEW-116** Jupyter server default working directory
  (`~/Documents/NchantdLibrary`) (filed from
  `testing-report_20260810.md`).
- **T-NEW-117** Palette scan crashes:
  `PyfficeColorPalette.extract_palette` missing (filed from
  `testing-report_20260810_001.md`; verified still broken
  2026-08-15).
- **T-NEW-118** Journal PII detector + redacted view with PIN
  copy (re-filed, was orphaned by the T-NEW-066/067/068 number
  collision inside T-NEW-065's deferred-work section).
- **T-NEW-119** Journal content growth: timestamp column +
  retention policy + `delete_marked` (re-filed, same number
  collision orphaning).
- **T-NEW-120** Script save/restore aspirational tests fail at
  the `5d80f92` contract (5 RED tests are the acceptance gate
  after the `822b32e` revert).
- **T-NEW-121** em-dash sweep + encoding-declaration
  placement — partial; see "Changed" above for what shipped.
  Full sweep still open.
- **T-NEW-122** Qt-harness migration for tests importing
  toolboxes (filed after `test_cmd_pyof_routing_consolidation
  .py` batch-crash — T-NEW-114 follow-up).
- **T-NEW-123** Embedded-TODO sweep: implement-method stubs and
  config wiring — covers the 21 uncovered TODO markers
  (embedded_todos audit dim 58%). Partial — T-NEW-138/139/140/
  141 ship the inside-nchantdoffice subset.
- **T-NEW-138** Journal editor followups: always-scroll to
  bottom + refactor to standard populate (covers `journal.py
  :132, 422`).
- **T-NEW-139** Toolbar signature cleanup: combine `add_tab` +
  `add_document` shared cfg/wiring (`toolbars.py:216`).
- **T-NEW-140** Free-user right-side tab: lock default to Ad
  tab (`settings.py:1209`).
- **T-NEW-141** Inside-nchantdoffice TODO sweep: 10 remaining
  markers (images palette drawer, notebook stubs, catalog
  tab-None, config features pane, 3 stub methods,
  `users.has_pro` service truth).
- **T-NEW-142** Tab Delete broken from document toolbar +
  `NchantdTabPane` (filed from `testing-report_20260815.md`
  Issue 2). **Note: 100-node cap popup superseded by T-NEW-135
  redirect per user direction 2026-08-16; no T-NEW for popup.**
- **T-NEW-143** `.pyof` import excludes `DELETE_BIT=1` rows
  (filed from `testing-report_20260815.md` Issue 3).
- **T-NEW-144** `file_details` toolbox redirects to internal
  data when tab is an internal document + external file
  becomes editor (not viewer) (filed from
  `testing-report_20260815.md` Issues 4 & 5; split into
  T-NEW-144a/144b if scope balloons).
- **T-NEW-145** `Ctrl+S` wired to save button logic (filed from
  `testing-report_20260815.md` Issue 6).
- **T-NEW-146** `bootstrap_app_user` regression: cannot pickle
  'generator' object — post-T-NEW-129 live traceback
  2026-08-15 22:19:02; the `user` dict passed to
  `store_app_user` contains a generator value that
  `squirl.deepcopy` cannot serialise. **FIXED** in the
  T-NEW-146/147 commit; see "Added" above.
- **T-NEW-147** `get_app_user` AttributeError:
  `'NchantdOfficeCloakModel' object has no attribute
  'get_table'` — post-T-NEW-129 live traceback 2026-08-15
  22:19:02; `model.get_table` does not exist on the cloak
  model. **FIXED** in the T-NEW-146/147 commit.

### Security
- Added CI security scanning with bandit and safety

### Testing
- Added pytest configuration and unit tests for config module
- **`tests/test_t_new_*`** — 30+ T-NEW-pinned regression tests
  landed alongside T-NEW-110..137. See
  `tests/` and the test-surface count in `TODOs.md` §1 for the
  current running totals. The aspirational script tests under
  T-NEW-120 (5 RED) are the next acceptance gate.

---

## [Unreleased] — prior batch (T-NEW-058..079)

> **Retained for traceability.** This section was the live
> `[Unreleased]` block prior to the 2026-08-16 sweep that
> consolidated T-NEW-110..147 above. It is unchanged from
> commit `8f9b0aa` (the last committed unreleased-section
> revision before the 110..147 burst landed).
- **Journal save / restore functional** (commits `dad65fe`, `ca1b2e4`, `374c6eb`, `e1d660c`) — `NchantdOfficeJournalEditor.save()` persists the full text via `self.save_app()` (the app_media path: `app_doc_content` / `app_media_content`), and the editor restores the full text on every tab focus via `refresh_content()`. The earlier T-NEW-XXX attempts called `super().save()` alongside the journaling code, which landed the wrong payload into `doc_media_content`; the user removed `super().save()` from the journal path (commits `9e74486` + `cb6ebb9`) so the only correct save path is `save_app()`. `save_app()` failures are NOT wrapped in try/except per the user's `cb6ebb9` directive -- they propagate to the Qt event loop so a save failure is loud, not silent. The user also cleaned up dead commented-out blocks in commit `f978a95` -- no behavior change, just dead-code removal that brings the source closer to the canonical 174cfd86 state plus the T-NEW-079 additions.
- **Journal entries now persist in `content_enc64_txt`** (commit `374c6eb`) — the user-visible live bug: the full text saved, but the `entries` dict inside `app_media_content.content_enc64_txt` was empty. Root cause: `NchantdOfficeJournalAppendEditor.add_entry()` only wrote to `self.parent.pages` (the editor's in-memory alias), not `self.parent.document.pages` (the persisted Pyffice document). The fix writes to both, with defensive fallbacks for empty pages and missing documents. See `tests/test_journal_add_entry_mirrors_to_document.py` (5 tests pinning the contract).
- **Journal `parse()` + `refresh_content()` re-enabled** (commits `dad65fe`, `ca1b2e4`, `e1d660c`) — `parse(content)` splits the full text on `--|YYYY-MM-DD HH:MM:SS|--` markers and stores the `{timestamp: block_text}` dict in `self.entries` (the in-memory cache for date-navigation widgets). The save payload is NOT serialized into the save call -- `save_app()` persists the full text and `parse()` is the consumer-side reducer. `parse()` normalizes its input (dict vs string vs None) so the save flow can call it without first unpacking the `get_content()` dict. `refresh_content()` re-fetches the journal text from the model on every tab focus (T-NEW-036 + T-NEW-073).
- Content-table merge-by-version dedupe (`T-NEW-076`) — extends the `_content` import merge to query the host's MAX(version) per `pUUID` before inserting. Re-importing the same source no longer appends duplicate rows: the source's max-version row replaces host rows only when it's strictly newer; equal-or-older source rows are skipped.

### Changed
- `nchantdoffice/__init__.py` - Added version and config exports
- `nchantdoffice/widgets/items/items.py` - Renamed `self.parent` → `self.parent_widget`
  across `NchantdOfficeDocumentCatalogItem`, `NchantdOfficeSourceCatalogItem`,
  `NchantdOfficeTreeNode` to prevent shadowing `QTreeWidgetItem.parent()`

### Fixed
- **H25 — Catalog Tab Wrong Child Count** (`nchantdoffice` consumer of `nchantrs fa05530`):
  Root cause was in parent library `NchantdNode.loadChildren()` which inconsistently
  used `parentid` vs `pid_txt` for parent filtering. Fix standardized on `pid_txt`.
  Visible in catalog tab child counts across all node types.
- **H27 — Nchantd Image Save Mode (Internal vs External)** (`commit c45cfc5`):
  Enforced canonical external file storage mode in `widgets/documents/media/images.py`;
  internal base64 mode now deprecated with runtime warning. Eliminates round-trip
  corruption and orphan files.
- **H28 — Browser Pin Tab Persistence** (`commit 87a5264`):
  Fixed `open_new_window()` routing through pinned-aware center pane tabset in
  `widgets/documents/atnrg/browsers.py`; corrected `save()` to read `self.pinned`
  (was checking non-existent `self.pin`); `pin_page()` and `populate_document()`
  now respect `self.pinned` state. "Pin Tab" action persists; links in pinned
  tabs no longer open new tabs.
- **H29 — Tree Node Drag-and-Drop Regression** (`commit c45cfc5` + nchantrs `fa05530`):
  Two-part fix — (1) `nchantrs/widgets/items/nodes.py` `NchantdNode.initModel()` now
  stores the full node dict in `UserRole` for drag-drop; (2) `nchantdoffice/widgets/trees.py`
  `getNid()` reads `nid_txt` from the `UserRole` dict. Drag-drop, drop targets,
  and reordering restored.
- **H30 — `setData()` Argument Order** (`nchantrs commit 5afde9d`):
  `NchantdNode.initModel()` in `nchantrs/widgets/items/nodes.py:380` now calls
  `self.setData(0, Qt.UserRole, self.node)` — the correct argument order is
  `(column, role, value)`. Previously the args were inverted, storing the role ID
  in column 0, which silently failed and produced empty `UserRole` data. This
  compounded with H29 to break drag-and-drop in nchantdoffice.
- **H31 — `self.parent` Shadowing `QTreeWidgetItem.parent()`** (`commit a01714c`):
  `QTreeWidgetItem` subclasses in `nchantdoffice/widgets/items/items.py`
  (`NchantdOfficeDocumentCatalogItem`, `NchantdOfficeSourceCatalogItem`,
  `NchantdOfficeTreeNode`) had `self.parent = parent` in their constructors, which
  shadowed Qt's built-in `parent()` method. This caused
  `TypeError: 'NchantdOfficeTreeNode' object is not callable` whenever Qt called
  `.parent()` on a tree item — most visibly in drag-and-drop `_is_descendant()`
  checks. Renamed `self.parent` → `self.parent_widget` across all three classes.
  nchantrs mirrored the rename across `NchantdItem`, `NchantdTreeItem`,
  `NchantdTreeNode`, and `NchantdTree` (commits `57839d2` + `be8a582`).
- Lambda antipattern in toolbar buttons (fixed variable capture)
- Signal inheritance in NchantdNewDocumentToolBar
- Incorrect super().__init__() calls in toolbar classes
- 4 inline TODOs in `widgets/items/items.py` resolved (2026-07-11)

### Security
- Added CI security scanning with bandit and safety

### Testing
- Added pytest configuration and unit tests for config module

---

## [0.0.1.0.1.4] - 2026-03-25

### Phase 7 - Quality & Standards Compliance

#### Added
- CI/CD pipeline (GitHub Actions)
- Configuration module with logging and 100+ constants
- Unit test infrastructure
- Documentation deployment workflow

#### Fixed
- Lambda antipattern in buttons
- Signal inheritance issues
- super().__init__() parameter errors

---

## [0.0.1.0.1.3] - 2026-03-05

### Phase 6 - Build & Deploy Preparation

#### Added
- PyfficeDocument implementations (12 types)
- Toolbox integration with dynamic tools
- Signal flow: toolbar → tree → tabs → toolbox
- CLI entry point via cmds/

#### Fixed
- Center app tab dragging
- Tree node drag-and-drop
- Cross-pane tab dragging
- Tab-to-tree drag-and-drop
- Right-click context menus
- Right toolbox search

---

## [0.0.1.0.1.2] - Prior

*History not available*

---

## Internal Project Changes Required

See [CHANGES-nchantrs.md](./CHANGES-nchantrs.md) for changes needed in the nchantrs dependency.
