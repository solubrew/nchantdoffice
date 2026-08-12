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
