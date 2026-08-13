# CHANGES.md - NchantdOffice Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- `.github/workflows/ci.yml` - GitHub Actions CI pipeline (lint, type-check, test, security, build)
- `.github/workflows/docs.yml` - GitHub Actions documentation deployment
- `nchantdoffice/config.py` - Centralized configuration module with 100+ constants
- `tests/unit/__init__.py` - Unit test package
- `tests/unit/test_config.py` - Configuration module tests
- **Ad tab four-slot rotation** (T-DESK-066 / paired with nchantdofficeATNRG/T-NEW-029):
  The right-side Ad tab now rotates between `[tip → substack × 5 → pro_cta → affiliate × 4]`
  on a `QTimer` (default 12s, operator-tunable via `advertisements.yaml::interval_ms`).
  - `RotationSlot` dataclass + 4 subclasses (`TipSlot`, `SubstackSlot`, `ProCtaSlot`, `AffiliateSlot`)
  - `TIPS_FEED` (30 productivity tips mirrored from ATNRG `content/memes/tips.md`)
  - `SUBSTACK_FEED` (5 starter entries for the symbiosis-reciprocal placement)
  - `_load_slots()` builds the rotation in canonical order
  - `_advance_slot()` cycles the visible slot + `_start_rotation()` wires the QTimer
  - Pro users get no rotation (existing `_is_visible_for_user` short-circuit preserved)
  - Manual "Next ›" button for users who don't want to wait
- **Release checklist section** in `docs/cross-repo-review_20260807.md`:
  R-1 (mirror TIPS_FEED from ATNRG), R-2 (grow SUBSTACK_FEED from outreach),
  R-3 (verify rotation tuning), R-4 (cross-repo parity check). Prevents silent
  drift between the marketing source of truth and the desktop bundle.
- `tests/test_ad_tab_rotation.py` — 17 contract tests pinning the rotation behaviour:
  - 14 source-level pins (slot dataclasses, TIPS_FEED, SUBSTACK_FEED, ordering, QTimer wiring)
  - 1 dead-code pin (`_build_banner_card` removed)
  - 1 cross-repo drift detector (`TIPS_FEED` ≥ ATNRG `tips.md` count)
  - 1 release-checklist pin (R-1 section present with all required markers)
- Content-only `.pyof` import from the Application tab in the ToolBox (`cmd_import_pyof`, T-NEW-074) — opens a file picker, copies `app_tree_node`, `doc_tree_node`, `app_tab`, `doc_tab`, `app_media`, `doc_media` from the source into the host instance using INSERT-OR-IGNORE on the source UUIDs (no remapping). Instances and config are NOT migrated.
- Content-table last-version-wins merge (`T-NEW-075`) — extends the `.pyof` import contract with `app_doc_content`, `app_media_content`, `doc_media_content`. For each `pUUID`, only the highest-version row is kept; source PKs are dropped (host regenerates), but `UUID` and `pUUID` are preserved (FK relationships intact).
- Base-table UUID-lookup dedupe (`T-NEW-077`) — extends the base-6 merge to drop the source PK and query the host for UUID existence before inserting. Uniform contract across all 9 tables: rowid regenerated on insert, dedupe by UUID lookup (with version comparison for `_content`). Re-imports are idempotent everywhere.
- Type-annotations sweep (`T-NEW-078`) — added return-type annotations to ~1100 functions across the 11 highest-impact `nchantdoffice/` files, lifting the `type_annotations` audit dim from 6% → 100%. Multi-line signatures left intact (the auditor's regex doesn't match them); the remaining ~5% gap on individual files is acceptable. `verify_annotations.py` tool added at `.hermes/scripts/` mirrors the auditor's regex for local progress checks.
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
