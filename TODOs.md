# NchantdOffice TODOs

**Last Updated:** 2026-07-08
**Branch:** gamma
**HEAD:** `0598d13` — "H24: deferred toolbox refresh + signal wiring + catalog-first-tab"
**Priority: P0 = Critical/Blocking | P1 = High | P2 = Medium | P3 = Low**

---

## Recent Activity (2026-07-08)

| Commit | Description |
|--------|-------------|
| `0598d13` | **H24 completed**: `QTimer.singleShot(0)` deferred toolbox refresh in `on_tab_focus()`, `current_document_changed` signal hook in `NchantdOfficeTabs`, catalog-first-tab logic in `buildTabSet()`, `NchantdOfficeTabSetModel.load_tab_set` override for lazy loading. Pushed to `origin/gamma`. |
| `856d418` | debug charts add todos |
| `7835f16` | fix(H24): wire refresh_for_document on tab switch; deduplicate toolbox method |
| `7f1672d` | fix(H24): lazy-init toolbox on tab switch; update priorities |
| `81e7801` / `665d266` / `7b6bd26` | implement notebook saving mechanisms |
| `ea87f02` | docs-only: rewrite H24 fix description; add Recent Activity log; move H26 to P2; dedupe M2/M4; promote M3 |
| `45f3406` | full rewrite; renumbered H30→F1, H31→F2, H32→H28 |


---

## New TODOs: - unprioritized
  - browser document tabs are not holding their individual position and history when new browser tab is created
  - on page video not playing is a long term issue may require significant no programming work in facebook
    # the youtube page works directly showing video fine for the first 20-30 seconds then crashes
  - Quick launch new document dialog is failing
    # 2026-07-08 17:36:35,047 - nchantrs.dialogs.dialogs                  494: INFO     - NchantdSigil.initView - layout already exists: <PySide6.QtWidgets.QHBoxLayout(0x2e2202b0) at 0x7d7eb42cf2c0>
  - Favorites / new-window links open-in-tab: attempted via createWindow hijack (nchantrs pages.py open_new_window hook + office open_web_tab). REVERTED behaviourally — hijacking window.open (returning a self-destructing blocking page) made popups "open then vanish", which Google's sign-in security JS treats as an insecure/automated browser → HARD BLOCK on login. Now gated OFF: `pages.ENABLE_NEW_WINDOW_DELEGATION = False` restores prior createWindow behaviour (login works again; favorites clicks do nothing). Feature code kept, dormant. Safer next attempt: gate on the createWindow `type_` (only WebBrowserTab, leave WebDialog/WebBrowserWindow — Google's probes — untouched), or use the `newWindowRequested` signal, and never engage on `accounts.google.com`.
  - 


---

## 🟥 CRITICAL / P0

### H24 — Toolbox Drawer Stale on Tab Switch
- **Severity:** P0 → ✅ **Completed** (commit `0598d13`, pushed `origin/gamma`)
- **Symptom:** Switching tabs in right pane destroys toolbox state (search queries, filter results, selected items)
- **Root Cause:** `NchantdOfficeApplicationToolBox` had no refresh API; toolbox was either fully rebuilt (state lost) or never updated when the document context changed.
- **Fix Applied (commits `7f1672d` → `7835f16` → `0598d13`):**
  1. `NchantdOfficeApplicationToolBox.refresh_for_document(doc)` method added in `nchantdoffice/widgets/controls/toolboxes.py` — swaps internal document context and rebuilds content widgets in place (no widget recreation, state preserved)
  2. `NchantdOfficeTabs` class added in `nchantdoffice/widgets/widgets.py` — overrides `setCurrentWidget()` and `setCurrentIndex()` to emit `current_document_changed = Signal(object)` on every tab switch
  3. Toolbox wired to `current_document_changed` signal at `NchantdOfficeTabs` construction time — auto-refreshes whenever any tab switch occurs
  4. `QTimer.singleShot(0, lambda: toolbox.refresh_for_document(widget))` added in `NchantdOfficeTabSet.on_tab_focus()` — defensive deferred refresh after widget is fully installed in the layout
  5. `NchantdOfficeTabSetModel.load_tab_set()` override in `nchantdoffice/models.py` — fully loads only the active tab and inserts dummy placeholders for the rest, preserving lazy tab loading
  6. Catalog-first-tab: `buildTabSet()` in `nchantdoffice/models.py` now inserts `NchantdOfficeDocumentsCatalog` at position 0 when `tabsdata` is empty, before the add-tab placeholder
- **Verification:** Test by opening multiple document tabs, performing searches/filters in the toolbox, then switching tabs — state should persist across switches. Also test that the catalog appears as the first tab when the tabset is empty.
- **Status:** ✅ Completed 2026-07-08 (`0598d13`)

### H25 — Catalog Tab Wrong Child Count
- **Severity:** P1
- **Symptom:** Catalog tab shows incorrect number of children in tree
- **Root Cause:** TODO (uninvestigated — likely `on_count_changed` not wired or returns stale count)
- **Fix Plan:**
  1. Add debug logging to `_update_count` in `nchantdoffice/widgets/items/tree.py`
  2. Verify signal connection in `NchantdOfficeDocumentsCatalog` and `on_tab_focus`
  3. Check `loadChildren` in `NchantdTreeNode` — log whenever `childCount()` is computed vs. actual children
- **Status:** TODO

---

## 🟨 HIGH / P1

### H27 — Nchantd Image Save Mode (Internal vs External)
- **Severity:** P1
- **Symptom:** Images saved internally as base64 don't round-trip correctly; external path mode may orphan files
- **Root Cause:** TODO (uninvestigated — two save modes exist, not unified)
- **Fix Plan:**
  1. Audit `nchantdoffice/widgets/documents/media/images.py` save logic
  2. Choose one canonical mode: external path with relative references preferred
  3. Add migration path for existing base64 entries
- **Status:** TODO

### H28 — Browser Pin Tab Doesn't Pin; Links Open New Tabs
- **Severity:** P1
- **Symptom:** "Pin Tab" action doesn't persist pinned state; clicking links in pinned tab opens new tab
- **Root Cause:** TODO (uninvestigated — likely tab state not persisted or link click handler bypasses pin check)
- **Fix Plan:**
  1. Check `on_pin_tab` wiring in `nchantdoffice/widgets/documents/web.py`
  2. Verify link-click handler respects `is_pinned` flag
  3. Add `is_pinned` to tab data model and persist to session state
- **Status:** TODO

### H29 — Tree Node Drag-and-Drop Regression
- **Severity:** P1
- **Symptom:** Dragging tree nodes no longer works; drop targets don't highlight; reordering fails silently
- **Root Cause:** TODO (uninvestigated — likely event filter or mime data issue after refactor)
- **Fix Plan:**
  1. Check `startDrag` / `dropEvent` in `nchantdoffice/widgets/items/tree.py`
  2. Verify `setDragEnabled(True)` and `setAcceptDrops(True)` are called on tree items
  3. Add debug print to `dragEnterEvent` / `dragMoveEvent`
- **Status:** TODO

---

## 🟦 MEDIUM / P2

### P1 — Startup Performance (Glain Load)
- **Severity:** P2
- **Symptom:** Application startup takes 30+ seconds due to Glain graph loading
- **Root Cause:** Glain loads entire knowledge graph synchronously on startup; no lazy loading or caching
- **Fix Plan:**
  1. Add lazy init: `GlainLoader` class that loads in background thread
  2. Show splash screen while loading
  3. Cache frequently-accessed subgraphs
- **Status:** TODO

### P2 — Lazy Tab Loading Audit
- **Severity:** P2 → ✅ **Completed** (commit `0598d13`)
- **Symptom:** Central pane and right-side tabs both loaded eagerly, slowing startup
- **Root Cause:** H9 (commit `4ac4e53`) replaced inline lazy-loading loop with `self.load_tab_set(...)` but the `nchantrs` base `load_tab_set` loads every tab eagerly (its `load_tab` dummy branch was dead code)
- **Fix Applied:** `NchantdOfficeTabSetModel.load_tab_set` override in `nchantdoffice/models.py` — fully loads only the active tab and inserts dummy placeholder widgets for the rest. Placeholders materialize on first focus via `NchantdOfficeTabSet.on_tab_focus` (widgets.py) and base `set_focus`.
- **Status:** ✅ Completed 2026-07-08 (`0598d13`)

---

## 🟩 FEATURES / F

### F1 — Nchantd FileSystem: Save Root & Tree Position
- **Severity:** P1 (data integrity)
- **Symptom:** Nchantd FileSystem does not save root directory changes or tree scroll position between sessions
- **Root Cause:** TODO
- **Fix Plan:**
  1. Add `root_path` and `scroll_position` to `NchantdFileSystemSettings` model
  2. Save on `root_changed` signal and `tree.scrollPositionChanged`
  3. Restore on `set_root` / `showEvent`
- **Status:** TODO

### F2 — Gmail Browser Compliance (GmailBrowser)
- **Severity:** P1 → ✅ **Login working** (2026-07-08). Follow-up open: shortcut links.
- **Symptom (resolved):** Google sign-in from the embedded browser either showed an
  "unsupported browser" banner or hard-blocked with "this browser or app may not be
  secure" (redirect to `signin/rejected`).
- **✅ CONFIRMED-WORKING CONFIGURATION (do not regress — Google account login
  succeeds with no error):** a *fully consistent Firefox identity*. A partial
  Firefox disguise (UA or header only) gets hard-blocked; every Chrome "tell" must
  be flipped together. All in the `nchantrs` base browser stack:
  1. `profiles.DEFAULT_USER_AGENT = firefox_user_agent()` — real Firefox 140 UA set
     at the profile level for every profile (pool `ProfileConfiguration`,
     `NchantdWebProfile.set_persistence`, `set_security_policy`,
     `engines.create_custom_profile`).
  2. `requests.ENABLE_GOOGLE_LOGIN_QUIRK = True` — on `accounts.google.com` /
     `accounts.youtube.com`: interceptor rewrites the request `User-Agent` to Firefox,
     and `profiles.install_google_login_ua_script` injects a DocumentCreation main-world
     script overriding `navigator.userAgent/appVersion/platform/oscpu/vendor(=\"\")/`
     `vendorSub/productSub(=\"20100101\")/userAgentData(=undefined)` and
     `window.chrome(=undefined)`.
  3. `graphics.py` Chromium flags include
     `--disable-features=…,UserAgentClientHint,UserAgentClientHintFullVersionList` so
     no Chrome `Sec-CH-UA` client-hint headers are emitted.
  4. Kept: `Accept-Language: en-US,en;q=0.9`, explicit JS/LocalStorage enable,
     persistent cookies.
  - **Reliable fallback** if Google tightens again: `DEFAULT_USER_AGENT =
    "CustomBrowser/1.0"` → soft "unsupported browser" banner but login still works.
- **⚠️ Known limitation / open follow-up — shortcut links not handled:** in-page
  links / Google account "favorites" that open a new window (`target="_blank"` /
  `window.open`) do not open anywhere. The new-tab handler
  (`pages.ENABLE_NEW_WINDOW_DELEGATION`, office `open_new_window`/`open_web_tab`)
  is **gated OFF** because hijacking `window.open` (returning a self-destructing
  blocking page) made popups "open then vanish", which Google's sign-in security JS
  flagged as automation → re-broke login. **Login capability must stay active.**
  Next attempt must not disturb Google's own `window.open`: gate on the
  createWindow `type_` (handle only `WebBrowserTab`/`WebBrowserBackgroundTab`, leave
  `WebDialog`/`WebBrowserWindow`), and/or never engage on `accounts.google.com`, and
  use the `[webpage] createWindow type=…` logs from a real click to confirm before
  re-enabling.
- **Status:** ✅ Login working 2026-07-08 (Firefox-identity config above). 🟡 Shortcut
  link handling still open (delegation gated off to protect login).

---

## 🟪 MAINTENANCE / M

### M1 — Inline TODO Inventory (87 locations across 27 files)
- **Severity:** P2 (tech debt)
- **Symptom:** 87 inline `# TODO` comments scattered across codebase with no centralized tracking
- **Root Cause:** Ad-hoc TODO comments never entered into this document
- **Files with TODOs:**
  - `nchantdoffice/utilities/links.py` — 1 TODO: get link table where connection to the link_affiliate table
  - `nchantdoffice/utilities/utilities.py` — 1 TODO: access database to get widget name; list defeats purpose
  - `nchantdoffice/wizards/wizards.py` — 1 TODO: `add_journal_document()` may be too soon
  - `nchantdoffice/dialogs/documents.py` — 3 TODOs: Excel format integration, Google Drive dialog, CSV/XLSX/TAB file loading
  - `nchantdoffice/widgets/documents/managers/filesystems.py` — 5 TODOs: automation rules, import automation, storage config, Google Drive API, Dropbox API
  - `nchantdoffice/widgets/documents/analytics/charts.py` — 5 TODOs: config pane wiring, toggle resize regression, data sources, view definitions, uncontained NchantdTable
  - `nchantdoffice/widgets/documents/atnrg/prompts.py` — 1 TODO: service configuration wiring
  - `nchantdoffice/widgets/documents/atnrg/browsers.py` — 5 TODOs: webapp over pinning, web scraping, address input widget (×4)
  - `nchantdoffice/widgets/documents/atnrg/contacts.py` — 2 TODOs: contact card widget, table
  - `nchantdoffice/widgets/documents/documents.py` — 3 TODOs: flip icon (×2), orphaned close handler
  - `nchantdoffice/widgets/documents/media/sketches.py` — 1 TODO: layer merging
  - `nchantdoffice/widgets/documents/media/scripts.py` — 10 TODOs: richtext, full-screen toggle, justification, bulleting, spacing, inserts, spell/grammar, analytics, pane spacing, templates, syntax debug
  - `nchantdoffice/widgets/documents/media/forms.py` — 3 TODOs: excel→google form conversion, service connection, Google Forms API, remote server/issue tracker
  - `nchantdoffice/widgets/documents/workbooks/matricies.py` — 4 TODOs: readonly data (×2), thumbnail, function dialog
  - `nchantdoffice/widgets/documents/workbooks/notebooks.py` — 4 TODOs: consolidate restart, syntax debug, save url location, jupyter save url
  - `nchantdoffice/widgets/catalogs.py` — 1 TODO: initial loading duplicates
  - `nchantdoffice/widgets/panes/charts.py` — 2 TODOs: button group, BorderConfigBar update
  - `nchantdoffice/widgets/panes/new.py` — 4 TODOs: excel format, google dialog, widget_code override, default pane handlers
  - `nchantdoffice/widgets/panes/forms.py` — 1 TODO: asked rate spinbox
  - `nchantdoffice/widgets/panes/search.py` — 1 TODO: tag tracking
  - `nchantdoffice/widgets/panes/documents.py` — 1 TODO: tag tracking
  - `nchantdoffice/widgets/config/accounts.py` — 2 TODOs: service connection details, server sync
  - `nchantdoffice/widgets/config/settings.py` — 3 TODOs: default tab, toolbox dropdown, tab sequence sort
  - `nchantdoffice/widgets/controls/toolboxes.py` — 5 TODOs: search panes, spacing, loading new instance (×2)
  - `nchantdoffice/widgets/controls/toolbars.py` — 5 TODOs: widget lookup, MultiInstance db, add_tab/add_document signatures, position increment
  - `nchantdoffice/models.py` — 10 TODOs: app table relocation, widget database addition, date filter, virtual table, tab/image/table format, session parsing, notion/evernote import, document object, external notifications, version increment, version handling
- **Fix Plan:** Audit each file and migrate actionable items to this TODOs.md, marking stubs as `// DONE: [reason]` in source
- **Status:** TODO

### M2 — Affiliate Link Data Updates
- **Severity:** P2
- **Symptom:** Affiliate link tracking data stale; no refresh mechanism for click counts and conversion rates
- **Root Cause:** No scheduled refresh or webhook for affiliate data
- **Fix Plan:**
  1. Add `AffiliateLink.refresh()` method with API call
  2. Add background scheduler in `nchantdoffice/widgets/config/affiliates.py`
  3. Show last-refreshed timestamp in UI
- **Status:** TODO

### M3 — Pro User Affiliate Opt-Out
- **Severity:** P2
- **Symptom:** Pro users cannot opt out of affiliate link injection
- **Root Cause:** No user-tier check in affiliate link injection logic
- **Fix Plan:**
  1. Add `is_pro` flag to user model
  2. Gate affiliate injection behind `if not user.is_pro:`
  3. Add toggle in Settings → Pro tab
- **Status:** TODO

---

## 🟩 GOALS / G

### G1 — Collaborative Editing (PAXN Integration)
- **Severity:** P3
- **Symptom:** No real-time collaboration features
- **Root Cause:** PAXN scope reduced/deprecated; no active real-time sync
- **Fix Plan:**
  1. Evaluate PAXN revival or switch to WebSocket-based sync via Kahndor
  2. Add `collaboration` module with presence indicators
  3. Connect to `Glain` for conflict resolution
- **Status:** TODO

---

## Completed

| ID  | Summary | Completed |
|-----|---------|-----------|
| H10 | Fix tab count badge update logic | ✅ 2026-07-07 |
| H20 | Notebook tab saving mechanisms | ✅ 2026-07-07 |
| H22 | Debug document toolbars | ✅ 2026-07-07 |
| H24 | Toolbox Drawer Stale on Tab Switch | ✅ 2026-07-08 (`0598d13`) |
| P2  | Lazy Tab Loading Audit | ✅ 2026-07-08 (`0598d13`) |

---

## Legend

| Prefix | Meaning |
|--------|---------|
| H##   | Bug / Hotfix (numeric sequence) |
| P##   | Performance / Polish |
| F##   | Feature |
| M##   | Maintenance |
| G##   | Goal / Architecture |
| TODO  | Not started |
| IN PROGRESS | Started, not complete |
| ✅   | Complete |

---

*This file is the live source of truth. All in-progress and completed work must be reflected here. Inline `# TODO` comments in source should be migrated here when addressed.*
