# NchantdOffice TODOs

**Last Updated:** 2026-07-13
**Branch:** gamma
**HEAD:** `b70a0c4` — "Merge remote-tracking branch 'local/gamma' into gamma"
**Inline Markers:** ~280 total — ~27 descriptive TODOs + ~248 stub method TODOs + 63 NOTE — across 27 files
**Priority: P0 = Critical/Blocking | P1 = High | P2 = Medium | P3 = Low**

---

## Recent Activity (2026-07-13)

| Commit | Description |
|--------|-------------|
| `b70a0c4` | Merge remote-tracking branch 'local/gamma' into gamma |
| `9f6643c` | expand documents missing functions |
| `a72fda3` | [H32] Fix pandas Series bool check in trees.py:120 |
| `a01714c` | fix: rename self.parent to self.parent_widget to avoid shadowing Qt.parent() method |
| nchantrs `5afde9d` | fix H30: correct setData arg order (column, role, value) in initModel |
| nchantrs `57839d2`+`be8a582` | fix H31: rename self.parent→self.parent_widget across all QTreeWidgetItem subclasses |

## Recent Activity (2026-07-12)

| Commit | Description |
|--------|-------------|
| `c45cfc5` | fix: H27/H29 - image save mode + drag-drop nid retrieval |
| `abd700e` | fix: resolve 4 TODOs in widgets/items/items.py + reclassify H25/H29 in TODOs.md |
| `87a5264` | fix: H28 browser pin/new window routing - verify open logic and pin state |
| `c9bc36f` | refactor data sources configuration and settings |
| `8bcdbf0` | refactor data sources configuration and settings |

## Recent Activity (2026-07-10)

| Commit | Description |
|--------|-------------|
| `a146c5f` | refactor data sources configuration and settings |
| `d21c70c` | chore: regenerate TODOs.md — sync with inline markers |
| `b91c558` | filling in the missing code and configs for 0.0.2 feature sets |

---

## Descriptive TODOs (from 2026-07-13 scan)

### models.py (5 TODOs)
- **L575:** `TODO: does this need to be moved to the app set of tables`
- **L885:** `TODO: need to refactor how the widget is added to the database using the app_document_type registry`
- **L1185:** `TODO: implement view then pull data from it`
- **L1255:** `TODO change this so that a tab code, images and tables`
- **L1340:** `TODO: Implement session parsing`
- **L1366:** `TODO: add import of things like notion and evernote in the future`
- **L1396:** `TODO: Implement this method when the required 'document' object is available.`
- **L1466:** `TODO: increment version`

### config/accounts.py (3 TODOs)
- **L170:** `TODO: get user name from account api`
- **L180:** `TODO: connect to service and get details`
- **L207:** `TODO: implement a larger button graphic`
- **L364:** `TODO: Implement actual server sync`

### config/help.py (1 TODO)
- **L79:** `TODO: need to implement a download of pdf files and then load an index that can navigate through them`

### config/settings.py (3 TODOs)
- **L245:** `TODO: possiblly only allow pro users to turn off`
- **L289:** `TODO pull from database combine sequence with name...`
- **L290:** `TODO change right selector to a position changer`

### config/sources.py (5 TODOs)
- **L76:** `TODO: build in additional controls for size ["full", "%10"]`
- **L82:** `TODO: implement config changes to make the pane standout`
- **L114:** `TODO: get apikey from pycurity and populate using an obscured version`
- **L128:** `TODO: add a visibliity switch at the end of the entry box`
- **L139:** `TODO: create a new NchantdOfficeWebBrowser Document`
- **L154:** `TODO replace obscured key with real key`

### controls/toolbars.py (3 TODOs)
- **L156:** `TODO:0 need to figure out how to look up the widget from the document types table`
- **L160:** `TODO: Switch to MultiInstance`
- **L238:** `TODO: if there are multiple notes then the position will need to increment`

### controls/toolboxes.py (4 TODOs)
- **L191:** `TODO: implement search panes`
- **L192:** `TODO: correct spacing of Node Configuration Drawer to tighten up the Node Pane and Tab Pane`
- **L325, L377:** `TODO: implement loading new nchantd office instance`

### analytics/analytics.py (1 TODO)
- **L33:** `TODO: Integrate Orange3`

### analytics/charts.py (3 TODOs)
- **L60:** `TODO: need to get list of sources`
- **L94:** `TODO: get a list of where the chart is used/connected`
- **L193:** `TODO send over data from the document to populate the chart`

### atnrg/prompts.py (3 TODOs)
- **L89:** `TODO: unsure how to integrate this at the moment`
- **L272:** `TODO need a pane to allow setting of days to keep chat history`
- **L293:** `TODO: show either a connection available or create connection to handle apis for the model`

### panes/charts.py (2 TODOs)
- **L169:** `TODO: implement this as button group`
- **L194:** `TODO: BorderConfigBar was a copy of text config and needs to be updated to apply to border styles`

### panes/documents.py (1 TODO)
- **L121:** `TODO: add tag tracking`

### panes/forms.py (1 TODO)
- **L124:** `TODO change always asked to a asked rate spinbox really should be part of the survey and not the form itself`

### panes/new.py (2 TODOs)
- **L189:** `TODO: how to integrate various formats across tools for specific tool types like a local file to open excel`
- **L198:** `TODO: develop the widget_code override based on unique options selections`

### panes/search.py (1 TODO)
- **L123:** `TODO: add tag tracking`

### catalogs.py (1 TODO)
- **L293:** `TODO add search bar to layout...with filter capabilities`

---

## Stub Method TODOs (# TODO: implement method — 248 total)

| File | Stub Count |
|------|-----------|
| `documents/workbooks/matricies.py` | 46 |
| `documents/media/sketches.py` | 34 |
| `documents/media/scripts.py` | 29 |
| `documents/media/images.py` | 25 |
| `documents/documents.py` | 24 |
| `documents/managers/calendars.py` | 21 |
| `documents/analytics/charts.py` | 18 |
| `documents/managers/filesystems.py` | 18 |
| `documents/media/forms.py` | 15 |
| `config/settings.py` | 12 |
| `documents/atnrg/browsers.py` | 12 |
| `documents/media/pdfs.py` | 6 |
| `documents/workbooks/notebooks.py` | 5 |
| `catalogs.py` | 4 |
| `documents/atnrg/prompts.py` | 3 |
| `documents/atnrg/contacts.py` | 1 |
| **TOTAL** | **~248** |

---

## Categorized Items (H## / F## / M## / G## / P##)

### F3 — Journal Entry Automation (P2)
- **Description:** Journal entry needs to be made for each major activity.
- **Related:** `wizards/wizards.py:62` — `add_journal_document()` intentionally NOT called
- **Status:** TODO

### M4 — `documents.py` Stub Methods (P2)
- 20+ stub methods in `documents/documents.py`
- **Status:** TODO

### M5 — `sketches.py` Stub Methods (P2)
- 28+ stub methods in `documents/media/sketches.py`
- **Status:** TODO

### M6 — Filesystem Integrations (P3)
- Automation rules, Google Drive API, Dropbox API, storage config — all stubbed
- **Related:** `documents/managers/filesystems.py` lines 106, 226, 703, 715, 788, 814
- **Status:** TODO

### M1 — Inline TODO Inventory (P2 tech debt)
- ~27 active descriptive TODOs + ~248 stub method TODOs across 27 files
- **Status:** TODO

### M2 — Affiliate Link Data Updates (P2)
- **Status:** TODO

### M3 — Pro User Affiliate Opt-Out (P2)
- **Status:** TODO

### G1 — Collaborative Editing (PAXN Integration) (P3)
- **Status:** TODO

### F1 — Nchantd FileSystem: Save Root & Tree Position (P1)
- **Status:** TODO

### F2 — Gmail Browser Compliance (GmailBrowser)
- **Status:** ✅ Login working. 🟡 Shortcut link handling open.

### P1 — Startup Performance (Glain Load) (P2)
- 30+ second startup due to synchronous Glain graph loading
- **Status:** TODO

---

## P0 / CRITICAL

*(none currently)*

---

## P1 / HIGH — Completed

| ID | Title | Status | Resolved in |
|----|-------|--------|-------------|
| H24 | Toolbox Drawer Stale on Tab Switch | ✅ | pre-gamma |
| H25 | Catalog Tab Wrong Child Count | ✅ 2026-07-12 | nchantrs `fa05530` |
| H27 | Nchantd Image Save Mode (external storage) | ✅ 2026-07-12 | `c45cfc5` |
| H28 | Browser Pin Tab persistence | ✅ 2026-07-11 | `87a5264` |
| H29 | Tree Node Drag-and-Drop Regression | ✅ 2026-07-12 | nchantrs `fa05530` + `c45cfc5` |
| H30 | `setData()` Argument Order | ✅ 2026-07-13 | nchantrs `5afde9d` |
| H31 | `self.parent` shadowing `Qt.parent()` | ✅ 2026-07-13 | `a01714c` |
| H32 | pandas Series bool check in trees.py:120 | ✅ 2026-07-13 | `a72fda3` |

---

## Completed (Historical)

| ID | Summary | Completed |
|----|---------|-----------|
| H10 | Fix tab count badge update logic | ✅ 2026-07-07 |
| H20 | Notebook tab saving mechanisms | ✅ 2026-07-07 |
| H22 | Debug document toolbars | ✅ 2026-07-07 |
| H24 | Toolbox Drawer Stale on Tab Switch | ✅ 2026-07-08 |
| P2 | Lazy Tab Loading Audit | ✅ 2026-07-08 |
| H25 | Catalog Tab Wrong Child Count | ✅ 2026-07-12 |
| H27 | Nchantd Image Save Mode | ✅ 2026-07-12 |
| H28 | Browser Pin Tab persistence | ✅ 2026-07-11 |
| H29 | Tree Node Drag-and-Drop Regression | ✅ 2026-07-12 |
| H30 | `setData()` Argument Order | ✅ 2026-07-13 |
| H31 | `self.parent` shadowing | ✅ 2026-07-13 |
| H32 | pandas Series bool check | ✅ 2026-07-13 |

---

## Legend

| Prefix | Meaning |
|--------|---------|
| H## | Bug / Hotfix |
| P## | Performance / Polish |
| F## | Feature |
| M## | Maintenance |
| G## | Goal / Architecture |
| TODO | Not started / needs investigation |
| NOTE | Developer note / reminder |
| ✅ | Complete |

---

*Auto-scanned: 2026-07-13 — HEAD `b70a0c4`. Source-of-truth: this file. Inline `# TODO` markers should be migrated here when addressed.*
