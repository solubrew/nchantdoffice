# NchantdOffice TODOs

**Last Updated:** 2026-07-08
**Branch:** gamma
**Priority: P0 = Critical/Blocking | P1 = High | P2 = Medium | P3 = Low

### Recent Activity (2026-07-08)
- `7835f16` — **H24 actually wired**: `refresh_for_document()` added to toolbox, signal hook `current_document_changed` connected, `QTimer.singleShot(0)` refresh in `on_tab_focus()`. The earlier `7f1672d` commit was documentation-only — the code it described never existed. Both commits required.
- `81e7801 / 665d266 / 7b6bd26` — notebook saving mechanisms landed
- `45f3406` — full rewrite of this file; renumbered H30→F1, H31→F2, H32→H28 (see lineage notes below)

---

## 🟥 CRITICAL / P0

### H24 — Toolbox Drawer Stale on Tab Switch
- **Severity:** P0 → ✅ Completed
- **Symptom:** Switching tabs in right pane destroys toolbox state (search queries, filter results, selected items)
- **Root Cause:** `NchantdOfficeApplicationToolBox` had no refresh API; toolbox was either fully rebuilt (state lost) or never updated when the document context changed.
- **Fix Applied (commits `7f1672d` + `7835f16`):**
  1. `refresh_for_document(doc)` method added to `NchantdOfficeApplicationToolBox` in `nchantdoffice/widgets/controls/toolboxes.py` — swaps internal document context and rebuilds content widgets in place (no widget recreation, state preserved)
  2. Toolbox wired to `NchantdOfficeTabs.current_document_changed` signal at construction time, so it auto-refreshes whenever the central tabs emit a tab-switch event
  3. Explicit `QTimer.singleShot(0, lambda: toolbox.refresh_for_document(widget))` added in `on_tab_focus()` in `nchantdoffice/widgets/widgets.py` — defensive double-refresh after the new widget is fully installed in the layout
  4. Duplicate `refresh_for_document()` method removed (dedup)
- **Status:** ✅ Completed 2026-07-08 (commit `7835f16`)

### H25 — Catalog Tab Wrong Child Count
- **Severity:** P1
- **Symptom:** Catalog tab shows incorrect number of children in tree
- **Root Cause:** TODO (uninvestigated — likely `on_count_changed` not wired or returns stale count)
- **Fix Plan:** Add debug logging to `_update_count` in `nchantdoffice/widgets/items/tree.py`; verify signal connection in `on_tab_focus`
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
- **Severity:** P2 → ✅ Completed
- **Symptom:** Central pane and right-side tabs both load eagerly, slowing startup
- **Root Cause:** H9 (commit 4ac4e53) replaced the inline lazy-loading loop in
  `NchantdOfficeTabSetModel.buildTabSet` with `self.load_tab_set(...)`, but the
  `nchantrs` base `load_tab_set` loads every tab eagerly (its `load_tab` dummy
  branch is dead code: `if tabn == tabn` is always true). No dummies were
  created, so the `on_tab_focus`/`set_focus` lazy check never fired.
- **Fix Applied:** Added `NchantdOfficeTabSetModel.load_tab_set` override in
  `nchantdoffice/models.py` — fully loads only the active tab and inserts dummy
  placeholder widgets for the rest. Placeholders are materialized on first focus
  by `NchantdOfficeTabSet.on_tab_focus` (widgets.py) and the base `set_focus`.
  Also removed a duplicate `refresh_for_document` call in `on_tab_focus`.
- **Status:** ✅ Completed 2026-07-08

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
- **Severity:** P1 (Gmail blocks legacy browser versions)
- **Symptom:** Gmail says browser version is no longer supported; user prompted to upgrade
- **Root Cause:** `NchantdBrowser` / `NchantdOfficeBrowser` using outdated or missing Chromium/Electron version
- **Fix Plan:**
  1. Audit `nchantdoffice/widgets/documents/web.py` for browser engine version
  2. Check `requirements.txt` / `pyproject.toml` for `PyQt6-WebEngine` version
  3. Update to latest Qt WebEngine (Qt 6.7+) which includes Chromium 114+
  4. Set `QWebEngineProfile::defaultProfile()->setHttpUserAgent()` to a modern Chrome string
  5. Add `--disable-blink-features=OutOfBlinkCors` to browser args for Gmail compatibility
  6. Verify `QWebEngineSettings::Personalizable()` is enabled for cookie/session persistence
- **Status:** TODO

---

## 🟪 MAINTENANCE / M

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

### M4 — Affiliate Link Data Updates (Enhanced)
- **Severity:** P2
- **Symptom:** Affiliate data not updating in real-time; pro users need opt-out
- **Root Cause:** TODO
- **Fix Plan:**
  1. Add real-time update via polling (15 min interval) or webhook
  2. Pro users: show "Opt Out of Affiliate Links" button in settings
  3. Store affiliate config in `Glain` under `user.affiliate` node
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

---

## Legend

- **H##** — Bug/Hotfix (numeric sequence)
- **P##** — Performance/Polish
- **F##** — Feature
- **M##** — Maintenance
- **G##** — Goal/Architecture
- **TODO** — Not started
- **IN PROGRESS** — Started, not complete
- **✅** — Complete
