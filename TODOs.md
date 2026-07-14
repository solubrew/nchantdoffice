# NchantdOffice TODOs

**Last Updated:** 2026-07-13
**Branch:** gamma
**HEAD:** `a01714c` — "fix: rename self.parent to self.parent_widget to avoid shadowing Qt.parent() method"
**Inline Markers:** 113 total — 63 NOTE, 50 TODO — across 27 files *(4 TODO in `widgets/items/items.py` resolved 2026-07-11)*
**Priority: P0 = Critical/Blocking | P1 = High | P2 = Medium | P3 = Low**

---

## Recent Activity (2026-07-13)

| Commit | Description |
|--------|-------------|
| `a01714c` | fix: rename self.parent to self.parent_widget to avoid shadowing Qt.parent() method |
| nchantrs `5afde9d` | fix H30: correct setData arg order (column, role, value) in initModel |
| nchantrs `57839d2`+`be8a582` | fix H31: rename self.parent→self.parent_widget across all QTreeWidgetItem subclasses |

## Recent Activity (2026-07-13)

| Commit | Description |
|--------|-------------|
| `a01714c` | fix: rename self.parent to self.parent_widget to avoid shadowing Qt.parent() method |
| nchantrs `5afde9d` | fix H30: correct setData arg order (column, role, value) in initModel |
| nchantrs `57839d2`+`be8a582` | fix H31: rename self.parent→self.parent_widget across all QTreeWidgetItem subclasses |

## Recent Activity (2026-07-12)

| Commit | Description |
|--------|-------------|
| `c45cfc5` | fix: H27/H29 - image save mode + drag-drop nid retrieval |
| `abd700e` | fix: resolve 4 TODOs in widgets/items/items.py + reclassify H25/H29 in TODOs.md |
| `87a5264` | fix: H28 browser pin/new window routing - verify open logic and pin state |
| `9e4f008` | Merge branch 'gamma' of file:///mnt/overse/SBST01/vein/GitVein/nchantdoffice into gamma |
| `c9bc36f` | refactor data sources configuration and settings |
| `8bcdbf0` | refactor data sources configuration and settings |

## Recent Activity (2026-07-10)

| Commit | Description |
|--------|-------------|
| `a146c5f` | refactor data sources configuration and settings |
| `d2004eb` | Merge remote-tracking branch 'local/gamma' into gamma |
| `dbfa9d0` | refactor data sources configuration and settings |
| `d21c70c` | chore: regenerate TODOs.md — sync with inline markers |
| `b91c558` | filling in the missing code and configs for 0.0.2 feature sets |


---

## New TODOs from Codebase Analysis (2026-07-13)

### F3 — Journal Entry Automation
- **Severity:** P2
- **Description:** Journal entry needs to be made for each major activity. This is a bigger development area defining "major" and integrating the writing entries in the journal.
- **Related:** `nchantdoffice/wizards/wizards.py:62` — `add_journal_document()` intentionally NOT called
- **Status:** TODO

### M4 — `documents.py` Stub Methods (20+ `# TODO: implement method`)
- **Severity:** P2
- **Description:** 20+ methods in `nchantdoffice/widgets/documents/documents.py` are stubs with `# TODO: implement method`
- **Count:** 20+ inline TODOs (lines 115, 120, 125, 130, 149, 154, 177, 182, 196, 201, 206, 216, 221, 311, 329, 338, 375, 415, 420, 425, 430, 530, 535, 540)
- **Status:** TODO

### M5 — `sketches.py` Stub Methods (28+ `# TODO: implement method`)
- **Severity:** P2
- **Description:** 28+ methods in `nchantdoffice/widgets/documents/media/sketches.py` are stubs with `# TODO: implement method`
- **Count:** 28+ inline TODOs (lines 126–592)
- **Status:** TODO

### M6 — Filesystem Integrations (NOTE: needs implementation)
- **Severity:** P3
- **Description:** Multiple filesystem backends are stubbed: automation rules, Google Drive API, Dropbox API, storage config
- **Related:** `nchantdoffice/widgets/documents/managers/filesystems.py` lines 106, 226, 703, 715, 788, 814
- **Status:** TODO

---

## P0 / CRITICAL

*(none currently)*

---

## P1 / HIGH

### H24 — Toolbox Drawer Stale on Tab Switch
- **Status:** ✅ **Completed** (pre-gamma)
- **Fix:** `NchantdOfficeApplicationToolBox.refresh_for_document(doc)`, `NchantdOfficeTabs` signal hook, `QTimer.singleShot(0)` deferred refresh, `NchantdOfficeTabSetModel.load_tab_set` override, catalog-first-tab in `buildTabSet()`.

### H25 — Catalog Tab Wrong Child Count
- **Severity:** P1
- **Symptom:** Catalog tab shows incorrect number of children in tree
- **Fix Applied:** `nchantrs/widgets/items/nodes.py` — `NchantdNode.loadChildren()` now consistently uses `pid_txt` field for parent filtering, fixing child count across all node types including catalogs. Fix committed in nchantrs `fa05530`.
- **Status:** ✅ **Completed** (2026-07-12) — root cause in nchantrs parent library

### H27 — Nchantd Image Save Mode (Internal vs External)
- **Severity:** P1
- **Symptom:** Images saved internally as base64 don't round-trip correctly; external path mode may orphan files
- **Fix Applied:** `nchantdoffice/widgets/documents/media/images.py` — canonical external file storage mode enforced; internal base64 mode deprecated with warning. Fix committed in `c45cfc5`.
- **Status:** ✅ **Completed** (2026-07-12)

### H28 — Browser Pin Tab Doesn't Pin; Links Open New Tabs
- **Severity:** P1
- **Symptom:** "Pin Tab" action doesn't persist pinned state; links in pinned tab open new tabs
- **Fix Plan:** Check `on_pin_tab` wiring in `nchantdoffice/widgets/documents/web.py`; verify link-click handler respects `is_pinned`; persist `is_pinned` to session state
- **Fix Applied:** `nchantdoffice/widgets/documents/atnrg/browsers.py` — fixed `open_new_window()` to route through pinned-aware center pane tabset; corrected `save()` to read `self.pinned` (was checking non-existent `self.pin`); `pin_page()` and `populate_document()` now respect `self.pinned` state.
- **Status:** ✅ **Completed** (2026-07-11)

### H29 — Tree Node Drag-and-Drop Regression
- **Severity:** P1
- **Symptom:** Dragging tree nodes no longer works; drop targets don't highlight; reordering fails silently
- **Fix Applied:** Two-part fix — (1) `nchantrs/widgets/items/nodes.py` — `NchantdNode.initModel()` now stores the full node dict in `UserRole` for drag-drop, committed in nchantrs `fa05530`. (2) `nchantdoffice/widgets/trees.py` — `getNid()` now reads `nid_txt` from `UserRole` dict, committed in `c45cfc5`.
- **Status:** ✅ **Completed** (2026-07-12) — root cause in nchantrs parent library

### H30 — `setData()` Argument Order
- **Severity:** P1
- **Symptom:** `initModel()` stored role ID in column 0 instead of node dict in `UserRole`, silently breaking drag-drop data retrieval
- **Fix Applied:** `nchantrs/widgets/items/nodes.py:380` — corrected `setData(0, Qt.UserRole, self.node)` arg order to `(column, role, value)`. Committed in nchantrs `5afde9d`.
- **Status:** ✅ **Completed** (2026-07-13)

### H31 — `self.parent` Shadowing `QTreeWidgetItem.parent()`
- **Severity:** P1
- **Symptom:** `TypeError: 'NchantdOfficeTreeNode' object is not callable` on drag-drop `_is_descendant()` checks
- **Fix Applied:** Renamed `self.parent` → `self.parent_widget` across `NchantdOfficeDocumentCatalogItem`, `NchantdOfficeSourceCatalogItem`, `NchantdOfficeTreeNode` in `nchantdoffice/widgets/items/items.py`. Committed in `a01714c`.
- **Status:** ✅ **Completed** (2026-07-13)

---

## P2 / MEDIUM

### P1 — Startup Performance (Glain Load)
- **Severity:** P2
- **Symptom:** Application startup takes 30+ seconds due to synchronous Glain graph loading
- **Fix Plan:** Add `GlainLoader` background-thread class; splash screen; subgraph caching
- **Status:** TODO

### P2 — Lazy Tab Loading Audit
- **Status:** ✅ **Completed** (`NchantdOfficeTabSetModel.load_tab_set` override in `nchantdoffice/models.py`)

### M1 — Inline TODO Inventory (50 active TODOs across 27 files)
- **Severity:** P2 (tech debt)
- **Total:** 50 TODO, 63 NOTE — 113 markers across 27 files *(4 TODO resolved 2026-07-11 in `widgets/items/items.py`)*
- **Status:** TODO — see inline inventory below

### M2 — Affiliate Link Data Updates
- **Severity:** P2
- **Fix Plan:** Add `AffiliateLink.refresh()`; background scheduler; show last-refreshed timestamp
- **Status:** TODO

### M3 — Pro User Affiliate Opt-Out
- **Severity:** P2
- **Fix Plan:** Add `is_pro` flag to user model; gate affiliate injection; add Settings toggle
- **Status:** TODO

---

## P3 / LOW

### G1 — Collaborative Editing (PAXN Integration)
- **Severity:** P3
- **Fix Plan:** Evaluate PAXN revival or WebSocket-based sync via Kahndor; add presence indicators; connect to Glain
- **Status:** TODO

---

## Features (F)

### F1 — Nchantd FileSystem: Save Root & Tree Position
- **Severity:** P1
- **Status:** TODO

### F2 — Gmail Browser Compliance (GmailBrowser)
- **Status:** ✅ Login working (Firefox-identity config). 🟡 Shortcut link handling open (delegation gated OFF to protect login).

---

## Completed

| ID  | Summary | Completed |
|-----|---------|-----------|
| H10 | Fix tab count badge update logic | ✅ 2026-07-07 |
| H20 | Notebook tab saving mechanisms | ✅ 2026-07-07 |
| H22 | Debug document toolbars | ✅ 2026-07-07 |
| H24 | Toolbox Drawer Stale on Tab Switch | ✅ 2026-07-08 |
| P2  | Lazy Tab Loading Audit | ✅ 2026-07-08 |
| H25 | Catalog Tab Wrong Child Count | ✅ 2026-07-12 |
| H27 | Nchantd Image Save Mode (external storage) | ✅ 2026-07-12 |
| H28 | Browser Pin Tab persistence | ✅ 2026-07-11 |
| H29 | Tree Node Drag-and-Drop Regression | ✅ 2026-07-12 |
| H30 | `setData()` Argument Order | ✅ 2026-07-13 |
| H31 | `self.parent` shadowing `Qt.parent()` | ✅ 2026-07-13 |
| H30 | `setData()` Argument Order | ✅ 2026-07-13 |
| H31 | `self.parent` shadowing `Qt.parent()` | ✅ 2026-07-13 |

---

## Legend

| Prefix | Meaning |
|--------|---------|
| H##   | Bug / Hotfix (numeric sequence) |
| P##   | Performance / Polish |
| F##   | Feature |
| M##   | Maintenance |
| G##   | Goal / Architecture |
| TODO  | Not started / needs investigation |
| NOTE  | Developer note / reminder |
| ✅    | Complete |
| 🚧    | In progress |

---

*This file is the live source of truth. Inline `# TODO` / `# NOTE` comments in source should be migrated here when addressed. Last auto-scan: 2026-07-13 — HEAD `a01714c`.*
