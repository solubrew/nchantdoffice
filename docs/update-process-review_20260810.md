# NchantdOffice update process — review (2026-08-10)

> **Card:** T-NEW-057
> **Author:** review pass driven by user directive ("add TODO to
> review and upgrade the NchantdOffice update process").
> **Scope:** the two distinct update concerns in the desktop app:
> the **app-version update checker** (`nchantdoffice/updates/checker.py`)
> and the **document/schema upgrade path**
> (`nchantdoffice/updates/db.py`).
> **Status:** review complete. Per-card code changes are NOT
> landed in this doc — they get follow-up T-NEW-NNN cards.

---

## Executive summary

| Question | Answer | Follow-up |
|---|---|---|
| Is the update process wired into boot? | **No.** Both `UpdateChecker` and `NchantdOfficeDBUpdate` are defined and tested, but no live call site in the app ever invokes them. The classes are **dead-code at the call layer**. | **T-NEW-058** (wire boot hook + tray icon). |
| Is the 6h polling cadence right? | **Probably yes for v0.1.0**, but make it user-configurable. The cache layer is already correct (best-effort, no clobber on failure). | **T-NEW-059** (config knob in Interface Tab). |
| Should the desktop download the new `.deb`? | **No for v0.1.0.** Notify + open browser to download URL is the right scope. Auto-download / signature verification belongs in a later sprint. | None now; revisit at v0.2.0. |
| Does the dismissed-versions UX work end-to-end? | **Half.** `dismiss_version()` / `is_dismissed_version()` exist and are unit-tested, but the **tray icon UI** that calls them is not built. | **T-NEW-060** (tray icon menu). |
| Is the schema upgrade double-invocation safe? | **No collision in current code** — `NchantdOfficeDBUpdate` is constructed but `update_pyffice_document()` is never called. The collision risk only emerges once T-NEW-058 wires the boot hook. | Bundle into **T-NEW-058**. |
| Does `APP_VERSION` (`0.0.1.0.1.4`) compare correctly against the server? | **Yes via `APP_VERSION_SHORT`.** `UpdateChecker.check()` sends the short form on purpose — see `tests/test_update_checker.py:437 test_checker_does_not_send_5_segment_version`. | None — already pinned by test. |

---

## 1. Current architecture

### 1.1 Files involved

| File | Lines | Role | Tested? |
|---|---|---|---|
| `nchantdoffice/updates/checker.py` | 399 | `UpdateChecker` class + `UpdateInfo` dataclass + dismissed-version helpers (`dismiss_version`, `is_dismissed_version`, `_read_state`, `_write_state`). | ✅ 13 tests in `tests/test_update_checker.py` |
| `nchantdoffice/updates/db.py` | 63 | `NchantdOfficeDBUpdate.update_pyffice_document()` — wraps `nchantrs.updates.db.NchantdDBUpdate` and calls `self.parent.codex.update()`. | ❌ No test file. |
| `nchantdoffice/utilities/constants.py:72-79` | 8 | `APP_VERSION = "0.0.1.0.1.4"`, `APP_VERSION_SHORT = "0.0.1"`. | ✅ Implicitly via `test_checker_does_not_send_5_segment_version`. |
| `nchantdoffice/nchantdoffice.py:54` | 1 | `self.dbupdate = NchantdOfficeDBUpdate(self)` — **constructed but `.update_pyffice_document()` never called**. | ❌ |
| `nchantdoffice/models.py:1215-1220` | 6 | `close_application()` calls `self.store.compact_database()` — a different store method, not related to schema upgrade. | ❌ Not directly tested. |

### 1.2 Call graph (what actually runs at boot)

```
cmds/runNchantdOffice.py
  └─ NchantdOfficeCloak.__init__   (nchantdoffice.py:42)
       ├─ NchantdOfficeMainWindow
       ├─ NchantdOfficeCloakModel
       ├─ NchantdOfficeCloakView
       └─ NchantdOfficeDBUpdate(self)               ← constructed
                                                      ← .update_pyffice_document() NEVER called
  └─ NchantdOfficeCloak.run_on_launch   (nchantdoffice.py:65)
       ├─ super().run_on_launch()
       ├─ self.model.set_today()
       └─ self.select_initial_node()
                                                      ← no UpdateChecker.check() call
```

**Gap:** the boot sequence never invokes the update checker. The
schema-upgrade path is also never invoked. Both classes exist and
are tested, but the live app doesn't use them.

### 1.3 What the tests prove

`tests/test_update_checker.py` (452 lines, 13 tests) pins:

- Module + class existence.
- `DEFAULT_CHECK_UPDATE_PATH = "/api/check-update"`.
- `REFRESH_INTERVAL_SECONDS` constant exists.
- `STATE_FILENAME = "state.yaml"`.
- `check()` calls the correct endpoint.
- `check()` returns `None` on unreachable server (no clobber).
- Dismissed-version helpers exist.
- `UpdateInfo` dataclass exists.
- Cache is respected when fresh.
- Cache file mode is `0o600`.
- **Checker does NOT send the 5-segment version** (line 437).

All 13 are AST-only / module-attribute tests (the test file uses
`_ast_class`, `_ast_function`, `_module_top_level_constant`,
`_eval_simple_expr` helpers) — they pin the **API surface**, not
end-to-end behaviour. The actual HTTP call to the server is not
exercised.

---

## 2. Decisions per open question

### 2.1 Polling cadence — 6h

**Decision:** keep 6h for v0.1.0, expose as user-configurable knob.

**Rationale:** 6h matches the cadence of `base_layer.py` (per the
comments at `checker.py:53`). It avoids hammering the server for a
desktop app that's typically open for 8+ hours a day. Lowering to
1h adds ~7× API calls per day per user with no observable
benefit at v0.1.0 traffic levels.

**Follow-up:** **T-NEW-059** — add a `check_update_interval_hours`
config key (default 6) wired into the Interface Tab
"Updates" sub-section, alongside the dismissed-versions list and
the "check now" button.

### 2.2 Install vs notify — notify only for v0.1.0

**Decision:** notify + open browser to `download_url`. Do NOT
auto-download or auto-install the new `.deb`/wheel.

**Rationale:**
- Auto-installing a desktop app while it's running requires
  process restart, sudo on Linux (for `/usr/local/bin` installs),
  and signature verification. All three are non-trivial.
- The `download_url` from the server already goes to a
  human-curated page with checksums and release notes.
- v0.1.0 scope is "let users know there's a new version"; the
  install UX is v0.2.0 work.

**Follow-up:** none for v0.1.0. **T-NEW-061** (future card)
when the install flow is in scope: signature verification via
`sigstore` or `minisign`, restart-via-`QProcess::startDetached`
on Linux, MSIX on Windows.

### 2.3 Dismissed-versions UX — half-built, finish it

**Decision:** wire the existing helpers into a tray icon menu.

**Current state:**
- `dismiss_version(version)` writes to `~/.nchantd/state.yaml`
  (line 361 of checker.py). ✅ tested.
- `is_dismissed_version(version)` reads from the same file. ✅
  tested.
- **No tray icon UI** that calls them. The notification surfaces
  to the log (line 175 `check()`) but no Qt system tray widget
  is wired into `NchantdOfficeMainWindow`.

**Follow-up:** **T-NEW-060** — add `QSystemTrayIcon` to
`NchantdOfficeMainWindow` with a menu that shows the latest
version + a "Dismiss for 7 days" action calling
`dismiss_version()`. The 7-day snooze is a new constant
(`DISMISS_DURATION_DAYS = 7`) added to `checker.py`.

### 2.4 Schema upgrade double-invocation — bundle with boot hook

**Decision:** the current collision is hypothetical (the method
is never called). When T-NEW-058 wires the boot hook, add a
`_upgrade_lock` flag on `NchantdOfficeDBUpdate` so
`update_pyffice_document()` is a no-op on the second call within
the same process.

**Rationale:** `close_application()` calls
`self.store.compact_database()` (a different store API — not
related to schema upgrade, but worth noting in the comment).
The real risk is **two boot paths** calling
`update_pyffice_document()`: e.g. `run_on_launch` once + a
"Force upgrade" settings button once. The lock prevents the
double-migration.

**Follow-up:** bundle into **T-NEW-058** (one card, two changes).

### 2.5 Version-string compatibility — already pinned

**Decision:** no change. `APP_VERSION_SHORT` is the version sent
to the server; `APP_VERSION` (5-segment) is the local
developer-facing version.

**Evidence:**
- `utilities/constants.py:72-79` documents the choice (comment
  explicitly says the server's `_parse_version()` only handles
  3-segment versions).
- `tests/test_update_checker.py:437 test_checker_does_not_send_5_segment_version`
  pins the contract — if a future agent "simplifies" the call
  to send the 5-segment form, the test fails.

**Follow-up:** none.

---

## 3. Recommended implementation order

The review identifies 3 follow-up cards (plus a deferred
"install flow" card for v0.2.0). Each lands in its own commit +
follow-up SHA-backfill per the T-NEW single-repo lifecycle.

### T-NEW-058 — Wire `UpdateChecker` and `NchantdOfficeDBUpdate` into the boot sequence

- **Affected sites:**
  - `nchantdoffice/nchantdoffice.py:65-71` (`run_on_launch`)
    — add the two `check()` / `update_pyffice_document()` calls.
  - `nchantdoffice/updates/db.py:49` — add `_upgrade_lock`
    flag to `NchantdOfficeDBUpdate`.
  - `nchantdoffice/nchantdoffice.py:54` — wire the `dbupdate`
    attribute through `run_on_launch`.
- **Migration plan:**
  1. In `run_on_launch`, after `select_initial_node()`, call
     `self.dbupdate.update_pyffice_document()` (guarded by
     `_upgrade_lock`).
  2. Construct a `UpdateChecker` (from `nchantdoffice.updates.checker`)
     in `__init__` and store as `self.update_checker`.
  3. In `run_on_launch`, call `self.update_checker.check()`
     and log the result (tray wiring is T-NEW-060).
  4. Add `_upgrade_lock: bool = False` instance flag to
     `NchantdOfficeDBUpdate`; first call to
     `update_pyffice_document()` sets it to True and runs,
     subsequent calls are no-ops.
  5. Add `tests/test_update_checker_boot_hook.py` with 3 tests:
     boot invokes `check()` exactly once; boot invokes
     `update_pyffice_document()` exactly once; second boot in
     the same process is a no-op for the upgrade path.
- **Verification:** `pytest tests/test_update_checker.py
  tests/test_update_checker_boot_hook.py -q` → green; AST
  parse clean; ruff no F821/security regressions; live boot
  logs show "UpdateChecker check OK: latest_version=...".

### T-NEW-059 — User-configurable update-check interval

- **Affected sites:**
  - `nchantdoffice/updates/checker.py:53` — change
    `REFRESH_INTERVAL_SECONDS: int` to a function
    `refresh_interval_seconds(cfg)` that reads from config.
  - `nchantdoffice/nchantdoffice/_data_/nchantdoffice.yaml` —
    add `check_update_interval_hours: 6` key.
  - `nchantdoffice/widgets/panes/interface.py` — add
    "Updates" sub-section with a `NchantdSpinBox` (range 1–24).
- **Migration plan:**
  1. Refactor `REFRESH_INTERVAL_SECONDS` constant into a
     module-level helper that reads
     `cfg.get("check_update_interval_hours", 6) * 3600`.
  2. Add the config key to `_data_/nchantdoffice.yaml` with
     a comment explaining the default.
  3. Wire the spin box into the Interface Tab settings pane.
  4. Add `tests/test_update_checker_interval.py` with 4
     tests: default is 6h, custom value reads correctly,
     invalid value falls back to 6h, interval <= 0 is rejected.
- **Verification:** pytest green; live "Check now" button in
  the Interface Tab triggers `check()` and logs the result.

### T-NEW-060 — Tray icon for update notifications + dismiss UX

- **Affected sites:**
  - `nchantdoffice/nchantdoffice.py` — add `QSystemTrayIcon`
    to `NchantdOfficeMainWindow.__init__`.
  - `nchantdoffice/updates/checker.py:361-380` — extend
    `dismiss_version()` to accept an optional `days: int = 7`
    parameter; add `DISMISS_DURATION_DAYS` constant.
  - `nchantdoffice/nchantdoffice.py` — connect tray icon's
    "Dismiss" action to `dismiss_version()`.
- **Migration plan:**
  1. Add `QSystemTrayIcon` import + `_build_tray_menu()`
    method on `NchantdOfficeMainWindow`.
  2. When `UpdateChecker.check()` returns an `UpdateInfo`
    with `update_available=True`, populate the tray menu with
    "New version: <latest_version>" + "Open download page" +
    "Dismiss for 7 days" actions.
  3. Extend `dismiss_version(version, days=7)` to write
    `{version: now + timedelta(days=days)}` to the state file.
  4. Update `is_dismissed_version()` to compare against
    the expiry timestamp.
  5. Add `tests/test_dismiss_version_duration.py` with 5
    tests: default 7 days, custom days, expired dismiss is
    treated as not-dismissed, missing key returns False,
    malformed state returns False.
- **Verification:** pytest green; live tray icon shows on
  `QSystemTrayIcon.isSystemTrayAvailable()`; clicking
  "Dismiss" persists to `~/.nchantd/state.yaml` and the
  next `check()` skips the notification.

### T-NEW-061 — Deferred to v0.2.0: auto-install / signature verification

- **Why deferred:** the install UX requires process restart,
  platform-specific install paths (`/usr/local/bin` on Linux,
  MSIX on Windows), and signature verification (`sigstore` or
  `minisign`). None of these are in v0.1.0 scope.
- **Affected sites (planned, NOT implemented):**
  - `nchantdoffice/cmds/install_update.py` — new file.
  - `nchantdoffice/updates/checker.py` — `UpdateInfo` adds
    `signature_url` field.
- **Migration plan:** out of scope here; revisit when the
  install UX is the next blocker.

---

## 4. Verification of THIS review doc (T-NEW-057 step 1)

- `ast.parse(open('nchantdoffice/updates/checker.py').read())` → no errors
- `ast.parse(open('nchantdoffice/updates/db.py').read())` → no errors
- `wc -l nchantdoffice/updates/checker.py nchantdoffice/updates/db.py tests/test_update_checker.py` → 399, 63, 452
- `pytest tests/test_update_checker.py -q` → green (13 passed, 0 failed) — current state, no regressions
- `python -c "from nchantdoffice.updates.checker import UpdateInfo; print(UpdateInfo.from_response({'latest_version':'0.0.2','update_available':True}))"` → prints `UpdateInfo(latest_version='0.0.2', ...)` with the rest defaulted

## 5. Cross-references

- **T-NEW-057** (this card) — umbrella review.
- **T-DESK-053** — the cross-repo review that landed the
  current `UpdateChecker` (commit `6f537d1`).
- **T-NEW-058, T-NEW-059, T-NEW-060** — implementation
  follow-up cards derived from this review.
- **T-NEW-061** — deferred v0.2.0 install flow card.
- **`nchantdoffice_com/app/apis/updates.py:209`** — server
  side of `/api/check-update`, source of truth for the
  response shape.

---

*Review complete. Awaiting user direction on whether to
open T-NEW-058 / T-NEW-059 / T-NEW-060 immediately or defer
to a later sprint.*
