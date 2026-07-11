# NchantdOffice TODOs

**Last Updated:** 2026-07-11
**Branch:** gamma
**HEAD:** `9e4f008` — "Merge branch 'gamma' of file:///mnt/overse/SBST01/vein/GitVein/nchantdoffice into gamma"
**Inline Markers:** 113 total — 63 NOTE, 50 TODO — across 27 files *(4 TODO in `widgets/items/items.py` resolved 2026-07-11)*
**Priority: P0 = Critical/Blocking | P1 = High | P2 = Medium | P3 = Low**

---

## Recent Activity (2026-07-10)

| Commit | Description |
|--------|-------------|
| `8bcdbf0` | refactor data sources configuration and settings |
| `a146c5f` | refactor data sources configuration and settings |
| `d2004eb` | Merge remote-tracking branch 'local/gamma' into gamma |
| `dbfa9d0` | refactor data sources configuration and settings |
| `d21c70c` | chore: regenerate TODOs.md — sync with inline markers |
| `b91c558` | filling in the missing code and configs for 0.0.2 feature sets |


---

# Add TODOs:
    - Journal entry needs to be made for each major activity this is a bigger development area defining "major" 
        and integrating the writing entries in the journal 

    - 

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
- **Fix Plan:** `_update_count` and `loadChildren` logic lives in the inherited parent class `nchantrs.widgets.items.nodes.NchantdTreeNode`. Also check `NchantdOfficeDocumentsCatalog` signal wiring in `widgets/catalogs.py` (`on_tab_focus`). Once `nchantrs` source is accessible, debug `_update_count` override in `NchantdOfficeTreeNode` if needed.
- **Status:** TODO

### H27 — Nchantd Image Save Mode (Internal vs External)
- **Severity:** P1
- **Symptom:** Images saved internally as base64 don't round-trip correctly; external path mode may orphan files
- **Fix Plan:** Audit `nchantdoffice/widgets/documents/media/images.py`; choose canonical mode; add migration path
- **Status:** TODO

### H28 — Browser Pin Tab Doesn't Pin; Links Open New Tabs
- **Severity:** P1
- **Symptom:** "Pin Tab" action doesn't persist pinned state; links in pinned tab open new tabs
- **Fix Plan:** Check `on_pin_tab` wiring in `nchantdoffice/widgets/documents/web.py`; verify link-click handler respects `is_pinned`; persist `is_pinned` to session state
- **Fix Applied:** `nchantdoffice/widgets/documents/atnrg/browsers.py` — fixed `open_new_window()` to route through pinned-aware center pane tabset; corrected `save()` to read `self.pinned` (was checking non-existent `self.pin`); `pin_page()` and `populate_document()` now respect `self.pinned` state.
- **Status:** ✅ **Completed** (2026-07-11)

### H29 — Tree Node Drag-and-Drop Regression
- **Severity:** P1
- **Symptom:** Dragging tree nodes no longer works; drop targets don't highlight; reordering fails silently
- **Fix Plan:** `startDrag`/`dropEvent`/`setDragEnabled`/`setAcceptDrops` live in the inherited parent class `nchantrs.widgets.items.nodes.NchantdTreeNode`. Once `nchantrs` source is accessible, debug `dragEnterEvent`/`dragMoveEvent` in `NchantdOfficeTreeNode`. May also need to verify `NchantdOfficeTreeView` overrides in `nchantrs.widgets.items.nodes`.
- **Status:** TODO

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

## Inline TODO / NOTE Inventory (HEAD `8bcdbf0`)

> Auto-generated 2026-07-10 — 117 markers (54 TODO + 63 NOTE) across 28 files

### `nchantdoffice/dialogs/documents.py` (4 markers — 0 TODO, 4 NOTE)
- `241` **NOTE**: how to integrate various formats across tools for specific tool types like a local file to open excel
- `245` **NOTE**: create a load google dialog mimic file open dialog but connect to google drive using a browser/api
- `260` **NOTE**: Launch form builder wizard
- `292` **NOTE**: needs to be able to handle .csv, .xlsx, .xls, .tab, etc

### `nchantdoffice/models.py` (13 markers — 13 TODO, 0 NOTE)
- `575` **TODO**: does this need to be moved to the app set of tables
- `885` **TODO**: need to refactor how the widget is added to the database using the app_document_type registry
- `1068` **TODO**: convert to correct formats
- `1184` **TODO**: implement view then pull data from it
- `1214` **TODO**: relocat
- `1254` **TODO**: change this so that a tab code, images and tables
- `1339` **TODO**: Implement session parsing
- `1365` **TODO**: add import of things like notion and evernote in the future
- `1395` **TODO**: Implement this method when the required 'document' object is available.
- `1465` **TODO**: increment version
- `1493` **TODO**: implement method
- `1582` **TODO**: implement method
- `1683` **TODO**: need to determine version handling etc

### `nchantdoffice/utilities/utilities.py` (1 markers — 0 TODO, 1 NOTE)
- `77` **NOTE**: This if/elif IS the canonical widget lookup. The earlier match/case

### `nchantdoffice/widgets/catalogs.py` (1 markers — 0 TODO, 1 NOTE)
- `250` **NOTE**: fix initial loading of data duplicates

### `nchantdoffice/widgets/config/accounts.py` (4 markers — 4 TODO, 0 NOTE)
- `178` **TODO**: get user name from account api
- `188` **TODO**: connect to service and get details
- `215` **TODO**: implement a larger button graphic
- `372` **TODO**: Implement actual server sync

### `nchantdoffice/widgets/config/help.py` (1 markers — 1 TODO, 0 NOTE)
- `79` **TODO**: need to implement a download of pdf files and then load an index that can navigate through them

### `nchantdoffice/widgets/config/settings.py` (15 markers — 15 TODO, 0 NOTE)
- `270` **TODO**: set current default tab
- `286` **TODO**: add a drop down to replace the word toolbox with alist of right pane tabs
- `288` **TODO**: pull from database combine sequence with name to get a proper sort in the visual and control the actual sequenc of the right side tabs
- `342` **TODO**: implement method
- `347` **TODO**: implement method
- `352` **TODO**: implement method
- `357` **TODO**: implement method
- `362` **TODO**: implement method
- `367` **TODO**: implement method
- `372` **TODO**: implement method
- `377` **TODO**: implement method
- `382` **TODO**: implement method
- `387` **TODO**: implement method
- `392` **TODO**: implement method
- `397` **TODO**: implement method

### `nchantdoffice/widgets/config/sources.py` (2 markers — 1 TODO, 1 NOTE)
- `73` **TODO**: build in additional controls for size ["full", "%10"]}
- `188` **NOTE**: get table fields

### `nchantdoffice/widgets/controls/toolbars.py` (4 markers — 4 TODO, 0 NOTE)
- `156` **TODO**: 0 need to figure out how to look up the widget from the document types table
- `160` **TODO**: Switch to MultiInstance
- `190` **TODO**: cleanup add_tab, add_document signatures and combine as much code as possible
- `238` **TODO**: if there are multiple notes then the position will need to increment

### `nchantdoffice/widgets/controls/toolboxes.py` (4 markers — 4 TODO, 0 NOTE)
- `191` **TODO**: implement search panes
- `192` **TODO**: correct spacing of Node Configuration Drawer to tighten up the Node Pane and Tab Pane
- `325` **TODO**: implement loading new nchantd office instance
- `377` **TODO**: implement loading new nchantd office instance

### `nchantdoffice/widgets/documents/analytics/charts.py` (5 markers — 0 TODO, 5 NOTE)
- `185` **NOTE**: need to wire up the rest of the config options from the config pane to the chart pane...
- `225` **NOTE**: starts hear but once toggle is used it won't come back to the right size
- `330` **NOTE**: need to connect to a starter set of data sources...sample sets and non-key data sets
- `337` **NOTE**: list out and define various views based on connected data sources
- `440` **NOTE**: fix NchantdTable uncontained widget issue

### `nchantdoffice/widgets/documents/atnrg/browsers.py` (7 markers — 0 TODO, 7 NOTE)
- `249` **NOTE**: unsure what is needed to make webapp over pinning
- `329` **NOTE**: need to connect to some basic web scrapping functions
- `671` **NOTE**: Build an Address Input widget
- `681` **NOTE**: Build an Address Input widget
- `691` **NOTE**: Build an Address Input widget
- `701` **NOTE**: Build an Address Input widget
- `811` **NOTE**: seems something related to having buttons in the drawer?

### `nchantdoffice/widgets/documents/atnrg/contacts.py` (3 markers — 0 TODO, 3 NOTE)
- `223` **NOTE**: create contact Card Widget
- `229` **NOTE**: add a table
- `706` **NOTE**: s

### `nchantdoffice/widgets/documents/atnrg/prompts.py` (1 markers — 0 TODO, 1 NOTE)
- `423` **NOTE**: will need to get configurations from user or NchantdService

### `nchantdoffice/widgets/documents/documents.py` (3 markers — 0 TODO, 3 NOTE)
- `157` **NOTE**: flip icon
- `166` **NOTE**: flip icon
- `229` **NOTE**: i'm not sure this has any other uses that arent' handled by the toolbox tab trashcan

### `nchantdoffice/widgets/documents/managers/filesystems.py` (6 markers — 0 TODO, 6 NOTE)
- `106` **NOTE**: Implement automation rules
- `226` **NOTE**: Implement automation rules for importing files
- `703` **NOTE**: needs to be implemented
- `715` **NOTE**: Implement actual storage configuration
- `788` **NOTE**: Implement actual Google Drive API integration
- `814` **NOTE**: Implement actual Dropbox API integration

### `nchantdoffice/widgets/documents/media/forms.py` (3 markers — 0 TODO, 3 NOTE)
- `368` **NOTE**: Implement service connection logic
- `530` **NOTE**: Implement Google Forms API integration
- `891` **NOTE**: Send to remote server/issue tracker

### `nchantdoffice/widgets/documents/media/scripts.py` (11 markers — 0 TODO, 11 NOTE)
- `132` **NOTE**: change to richtext
- `269` **NOTE**: Change between a full screen and a standard 8.5x11/whatever the current page size is set to
- `482` **NOTE**: add text justification
- `483` **NOTE**: Add text bulleting
- `484` **NOTE**: add text spacing
- `537` **NOTE**: move inserts to object config
- `538` **NOTE**: add tools here like spell/grammar, etc
- `539` **NOTE**: add analytics tools
- `544` **NOTE**: each of these panes need to have their spacing tightened up
- `607` **NOTE**: add template selection/management
- `724` **NOTE**: debug

### `nchantdoffice/widgets/documents/media/sketches.py` (1 markers — 0 TODO, 1 NOTE)
- `1375` **NOTE**: Implement layer merging

### `nchantdoffice/widgets/documents/workbooks/matricies.py` (7 markers — 0 TODO, 7 NOTE)
- `183` **NOTE**: implement navigation so that enter moves down one row and tab moves over one column
- `581` **NOTE**: readonly and fill in data
- `600` **NOTE**: readonly and fill in data
- `631` **NOTE**: show a thumbail of the object
- `686` **NOTE**: need to implement calculation capabilities so that formula filled cells get converted to their output
- `885` **NOTE**: PyQt QTableWidget doesn't have built-in per-cell borders
- `1486` **NOTE**: Implement function dialog

### `nchantdoffice/widgets/documents/workbooks/notebooks.py` (6 markers — 0 TODO, 6 NOTE)
- `116` **NOTE**: consolidate to only restart
- `130` **NOTE**: book when a .ipynb is double-clicked in the tree) load in THIS view
- `863` **NOTE**: debug
- `983` **NOTE**: need to have a save url location mode so that it can reopen the same file each time
- `1004` **NOTE**: connect to jupyter saving mechanism as and connect the url path to the internal viewer entry
- `1017` **NOTE**: Jupyter handles saving internally through the web interface

### `nchantdoffice/widgets/items/items.py` (0 markers — resolved 2026-07-11)
- ✅ `140` **NOTE**: documented `NchantdAction` instantiation (was: TODO investigate)
- ✅ `166` **TODO**: `cmd_update_api_key_requirements` — reads radio selection, persists mode to data-source config
- ✅ `171` **TODO**: `cmd_update_api_key_entry` — reads entry value, persists api_key_txt to data-source config
- ✅ `175` **TODO**: `get_api_key` — reads api_key_txt from data-source config, returns empty string if unset

### `nchantdoffice/widgets/panes/charts.py` (2 markers — 2 TODO, 0 NOTE)
- `169` **TODO**: implement this as button group
- `194` **TODO**: BorderConfigBar was a copy of text config and needs to be updated to apply to border styles

### `nchantdoffice/widgets/panes/documents.py` (3 markers — 1 TODO, 2 NOTE)
- `121` **TODO**: add tag tracking
- `546` **NOTE**: s_label = NchantdLabel(self, {"text": "Notes: "}).initWidget()
- `671` **NOTE**: s = self.app.model.get_notes()

### `nchantdoffice/widgets/panes/forms.py` (1 markers — 1 TODO, 0 NOTE)
- `124` **TODO**: change always asked to a asked rate spinbox really should be part of the survey and not the form itself

### `nchantdoffice/widgets/panes/new.py` (3 markers — 3 TODO, 0 NOTE)
- `189` **TODO**: how to integrate various formats across tools for specific tool types like a local file to open excel
- `193` **TODO**: create a load google dialog mimic file open dialog but connect to google drive using a browser/api
- `198` **TODO**: develop the widget_code override based on unique options selections

### `nchantdoffice/widgets/panes/search.py` (1 markers — 1 TODO, 0 NOTE)
- `123` **TODO**: add tag tracking

### `nchantdoffice/wizards/wizards.py` (1 markers — 0 TODO, 1 NOTE)
- `62` **NOTE**: add_journal_document() intentionally NOT called here. The journal

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
| H28 | Browser Pin Tab persistence | ✅ 2026-07-11 |

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

*This file is the live source of truth. Inline `# TODO` / `# NOTE` comments in source should be migrated here when addressed. Last auto-scan: 2026-07-10 — HEAD `8bcdbf0`.*
