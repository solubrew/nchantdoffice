# Root-cause fixes in `nchantrs` for blank `QWebEngineView` rendering

Status: **landed** in `nchantrs` gamma — `1a0c23c` (2026-09-11, Fix B `showEvent`
hoist) + `af7c19e` (2026-09-12, empty-active_url guard). The notebook workaround
in `nchantdoffice/widgets/documents/workbooks/notebooks.py` is still present —
see "Remaining work" below — but the Ad tab blanking (Cause D, added 2026-09-12)
is fully resolved.

All line numbers reference the running copy:
`.../tskNchantrs/1_DELTA/nchantrs/nchantrs/...`

---

## 1. Symptoms

Two viewers are affected, which is the key signal that the bug is **shared**,
not notebook-specific:

- **Notebook viewer** — never renders. The Jupyter server launches correctly
  (`http://localhost:8888/tree`, auth disabled — verified via logging), the view
  issues `loadStarted` → `loadProgress=10%` for `/tree`, then the committed URL
  flips back to `about:blank` and the tab stays blank.
- **Regular web browser** (`NchantdOfficeWebBrowser`) — renders correctly on
  first creation, then renders blank after the tab is closed and reopened (or
  lazily rebuilt via `on_tab_focus`).

Because the regular browser loads `duckduckgo` through the same code path and
still blanks on reopen, the fault is in the shared `QWebEngineView` /
layout / tab-lifecycle plumbing.

---

## 2. Evidence from the logs

```
webview loadStarted
webview loadProgress=0%
pages: Navigate to QUrl('http://localhost:8888/tree')  NavigationTypeTyped  main_frame=True
webview loadProgress=10%
engines 285: View URL changed: about:blank          <-- initial blank load commits LATE and wins
browsers 314: URL Changed: QUrl('about:blank')
```

- `on_tab_focus` → `Loading Lazy Tab N` → `model.load_tab(...)` rebuilds the tab
  widget from scratch on every (re)open.
- `load_tab` inserts the freshly built widget into the `QTabWidget` via
  `insertTab` (`models/tabsetmodels.py:226`).

---

## 3. Root causes

### Cause A — layout-level `AlignTop`/`AlignLeft` collapses the web view

Qt rule: when a layout has a **layout-level alignment** set, its items are given
their `sizeHint` and pinned to that corner — the alignment **overrides the
child's `Expanding` size policy**, so the child no longer stretches to fill.

Two places set exactly this on layouts that end up containing the web view:

- `widgets/widgets.py:191` — the **base** `NchantdWidget.initView` applies
  `AlignTop | AlignLeft` to *every* widget's layout. This includes the
  `NchantdOfficeNotebook` document layout that hosts the `NchantdWebViewer`.
- `widgets/browsers/browsers.py:229` — `NchantdWebViewer.initView` **again** sets
  `setAlignment(AlignTop)` on the layout that directly holds the
  `QWebEngineView` (added at line 228).

Net effect: even though `browsers.py:222` sets the view to
`QSizePolicy.Expanding`, the surrounding alignment prevents it from expanding.
The view is laid out at its `sizeHint`. On a fresh relayout (tab reopen) that can
resolve to a near-zero / tiny rectangle → blank. A `QWebEngineView` with no
usable on-screen area never produces a frame.

### Cause B — initial URL is loaded before the view has an on-screen surface

`NchantdWebViewer.initView` calls `self.cmd_goto_page()` at
`browsers.py:223`, i.e. it starts loading the configured URL **during
construction**, while the widget is not yet shown (especially under lazy tab
loading, where the widget is built off-screen and only inserted/shown later).

`QWebEngineView` defers the first load until it has a compositing surface. The
deferred `about:blank` load then commits **after** any later navigation (e.g. the
notebook's `/tree`), clobbering it back to blank — exactly the
`View URL changed: about:blank` line above. This is the notebook's specific
failure and is only masked today by the self-heal retry in `notebooks.py`.

### Cause C — no repaint/reactivation when a view is re-shown in the `QTabWidget`

`load_tab` (`models/tabsetmodels.py:207`) rebuilds the page widget and
`insertTab`s it; switching tabs hides/shows `QTabWidget` pages. `QWebEngineView`
is well known to drop its rendered frame when its page is hidden and to not
always repaint on re-show, particularly when it was first loaded while hidden
(Cause B) or sized to zero (Cause A). There is no `showEvent` hook anywhere in
`NchantdWebEngineView` (`widgets/browsers/engines.py`) to nudge a repaint or
reactivate the page lifecycle.

---

## 4. Fixes (in `nchantrs`)

Apply A + B first — they are the highest-confidence root causes. C is a
belt-and-suspenders fix for the tab hide/show path.

### Fix A1 — do not align the layout that holds the web view

`widgets/browsers/browsers.py`, `NchantdWebViewer.initView` (~line 216-231).
Remove the alignment and let the view fill:

```python
def initView(self, cfg=None):
    super().initView(cfg)
    self.browser.setSizePolicy(
        pyqt.QSizePolicy.Policy.Expanding, pyqt.QSizePolicy.Policy.Expanding
    )
    page = self.browser.page()
    logma.info(f"Page {page}")
    self.layout.addWidget(self.browser)
    # REMOVED: self.layout.setAlignment(Qt.AlignTop)  -> collapsed the view to its sizeHint
    self.layout.setAlignment(pyqt.Qt.AlignmentFlag(0))  # clear any inherited alignment
    self.layout.setContentsMargins(0, 0, 0, 0)
    self.layout.setSpacing(0)
    self.layout.addStretch(0)  # optional; only if other items follow
    return self
```

Note: `self.layout` was created by the base `initView`, which already applied
`AlignTop | AlignLeft` (Cause A). Clearing it here with
`setAlignment(Qt.AlignmentFlag(0))` (an empty flag) is what actually lets the
child expand — simply *not* re-setting it is not enough because the base class
set it.

### Fix A2 — let fill-widget containers opt out of the global alignment

`widgets/widgets.py`, base `NchantdWidget.initView` (line 178-192). The global
`AlignTop | AlignLeft` at line 191 is correct for toolbars/forms but wrong for
containers that host a single expanding document (browser, notebook, editor).
Gate it behind a config flag:

```python
# line ~191
if not self.config.dikt.get("fill", False):
    self.layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop | pyqt.Qt.AlignmentFlag.AlignLeft)
```

Then any container that embeds a web view (the `NchantdWebViewer` itself, and the
`NchantdOfficeNotebook` document widget) passes `cfg["fill"] = True` when it
builds its view. This removes the *outer* collapse that Fix A1 alone cannot,
because the notebook document's own layout (from the base class) also pins the
viewer to its `sizeHint`.

### Fix B — defer the first load until the view is actually shown

`widgets/browsers/browsers.py`, `NchantdWebViewer`. Do **not** call
`cmd_goto_page()` inside `initView`. Instead load once, on first show, so the
view has a surface and the load cannot be clobbered:

```python
def initView(self, cfg=None):
    super().initView(cfg)
    self.browser.setSizePolicy(Expanding, Expanding)
    self.layout.addWidget(self.browser)
    self.layout.setAlignment(pyqt.Qt.AlignmentFlag(0))
    self.layout.setContentsMargins(0, 0, 0, 0)
    self.layout.setSpacing(0)
    self._did_initial_load = False          # NEW
    return self

def showEvent(self, event):                 # NEW
    super().showEvent(event)
    if not getattr(self, "_did_initial_load", False):
        self._did_initial_load = True
        self.cmd_goto_page()                # load now that we have a surface
```

With this, the notebook's `_navigate_browser(...)` call always runs against a
realized view and there is no lingering `about:blank` load to race with — which
lets the `notebooks.py` self-heal retry be deleted (see §5).

### Fix C — repaint / reactivate on re-show

`widgets/browsers/engines.py`, `NchantdWebEngineView`. Add a `showEvent` that
brings the page lifecycle back to active and forces a repaint when the tab is
shown again after being hidden/rebuilt:

```python
def showEvent(self, event):
    super().showEvent(event)
    page = self.page()
    if page is not None:
        try:
            page.setLifecycleState(pyqt.QWebEnginePage.LifecycleState.Active)
        except Exception:
            pass
    self.update()
```

If blanking still occurs on some GPU stacks, force a one-shot reload on the first
re-show (cheap for local Jupyter):

```python
    if getattr(self, "_was_hidden", False):
        self._was_hidden = False
        self.reload()

def hideEvent(self, event):
    super().hideEvent(event)
    self._was_hidden = True
```

### Fix D (fallback, environment) — software/compat rendering

`widgets/browsers/engines.py` already contains `setup_qt_environment()`
(currently commented out) plus `QTWEBENGINE_DISABLE_GPU_THREAD=1` and
`QT_OPENGL=es2`. If A–C do not fully resolve blanking on this machine, the cause
is GPU compositing, and the diagnostic is to enable software rendering **before**
`QApplication` is created:

```python
environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --disable-software-rasterizer --no-sandbox"
```

This is a diagnostic toggle, not a preferred fix — prefer A–C.

---

## 5. Relationship to the current `notebooks.py` workaround

`nchantdoffice/.../workbooks/notebooks.py` currently carries a band-aid for
Cause B:

- `_target_url` / `_nav_retries` state,
- a `loadFinished` handler that re-navigates when the view settles on
  `about:blank` while the target is the Jupyter URL,
- initialising the viewer to `about:blank` and navigating to `/tree` only after
  the server is confirmed up.

Once **Fix B** lands in `nchantrs`, the `about:blank` clobber can no longer
happen, so the self-heal retry loop and the `about:blank` init can be reverted to
a single clean `_navigate_browser(f"{server_url}/tree")` after readiness. Keep
the extensive launch/URL logging and the `loadFinished ok=...` diagnostic — those
remain useful.

---

## 6. Verification

After applying the `nchantrs` fixes:

1. Open the notebook tab. Expect: `webview loadFinished ok=True current_url=http://localhost:8888/tree`
   with **no** `re-navigating (retry ...)` lines, and the tree UI visible.
2. Open a regular browser tab → renders. Switch to another tab and back →
   still renders (Fix C).
3. Close the browser tab and reopen it (forces `load_tab` rebuild) → renders.
4. Resize the window / pane → the view fills the pane rather than sitting at a
   fixed small size (confirms Fix A).

---

## 7. Cause D — empty `active_url` clobbers a loaded page (Ad tab)

**Discovered 2026-09-12 via the user's live desktop log**, while rotating the Ad tab
through the layout cycle (`stack2` → `stack3`).

### Symptom

The Ad tab's `_load_ad_layout()` correctly populated the engine with the slim-ad URL:

```
13:50:15,729  Load Document: https://192.168.1.67/ads/slim/stack3
```

…then 9 ms later, the Viewer's first `showEvent` re-loaded an **empty** URL over it:

```
13:50:15,738  [webviewer] showEvent ... | active_url=
13:50:15,738  [webviewer] first show -> loading active_url
13:50:15,738  Load Document:
```

`engine.load("")` clobbered the page that `_load_ad_layout` had just loaded, leaving
the tab visibly blank. Subsequent `showEvent` cycles never re-triggered the
blanking (`_did_initial_load = True`), so the page stayed blank for the rest of
the session.

### Root cause

`NchantdURL` **subclasses** `pyqt.QUrl`. The Viewer's `set_url_path` (called with
the AdTab's `NchantdOfficeURL` wrapper) had its isinstance branches in this order:

```python
if isinstance(url, pyqt.QUrl):    # ← fires first because NchantdURL IS-A QUrl
    url_str = url.toString()      #    reads the wrapper's empty QUrl state
elif isinstance(url, NchantdURL):
    url_str = url.get_url()       # ← never reached
```

`NchantdOfficeURL.__init__` (nchantdoffice `pages.py`) sets `self.url` from its
**config** (`config.get("url", config.get("homepage", HOMEURL))`), not from the
positional URL arg the caller passed in. For the AdTab's call site
(`initModel` at line 1929, cfg={}), the config had no `url`/`homepage`, so the
wrapper's `.url` was `HOMEURL` while the **QUrl internal state was empty**.
`url.toString()` returned `""`, which was then re-wrapped as a new empty
`NchantdURL` and assigned to `self.active_url` — silently, with no error.

The Viewer's `showEvent` first-load guard was `if active_url is not None`, which
an empty-string `active_url` passes. `engine.load("")` then blanked the page.

### Fix (`af7c19e`, 2026-09-12)

Two complementary edits in `nchantrs/widgets/browsers/browsers.py`:

1. **`set_url_path`**: reorder isinstance checks (`NchantdURL` first, fall back to
   `toString()` only when `.url` is empty); bail out cleanly when normalisation
   yields `''` (no history entry, no `active_url` clobber).
2. **`showEvent` first-load**: require a non-empty `.url` string on
   `self.active_url`; when empty, keep the engine's already-loaded page (AdTab
   pre-loads via `populate_document` before the first show), else fall back to
   `cmd_goto_page()` (config default).

### Verification

Ad tab now renders on first surface; layout rotation reloads fresh; server-side
meta-refresh (300s) still rotates. User confirmed live 2026-09-12.

---

## 8. Remaining work

The notebook workaround in `nchantdoffice/widgets/documents/workbooks/notebooks.py`
(self-heal retry loop on `about:blank`, init to `about:blank` then re-navigate
after server readiness) is still in place. With Cause B + Cause D fixed in
`nchantrs`, it can be simplified to a single clean `_navigate_browser` after
readiness. The launch/URL logging and the `loadFinished ok=...` diagnostic
remain useful — keep them.

---

## 9. File / line index

| Concern | File | Line |
|---|---|---|
| Global `AlignTop\|AlignLeft` on all layouts | `widgets/widgets.py` | 191 |
| Viewer re-applies `AlignTop` over the web view | `widgets/browsers/browsers.py` | 229 |
| Web view added to layout | `widgets/browsers/browsers.py` | 228 |
| View set to `Expanding` (overridden by alignment) | `widgets/browsers/browsers.py` | 222 |
| Initial load during construction (Cause B) | `widgets/browsers/browsers.py` | 223 |
| No `showEvent` on the view (Cause C) | `widgets/browsers/engines.py` | class `NchantdWebEngineView` |
| Qt env / GPU flags (Fix D) | `widgets/browsers/engines.py` | `setup_qt_environment()` ~48 |
| Lazy tab rebuild + `insertTab` | `models/tabsetmodels.py` | 207, 226 |
