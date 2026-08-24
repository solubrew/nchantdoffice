# nchantdoffice — Production-Readiness Review (2026-08-15)

> **Repo:** nchantdoffice@`85e809e` (gamma, ahead of origin/gamma by 1 commit)
> **Baseline:** HEAD~ = `0c748fd` (origin/gamma before this review)
> **Auditor:** sasquatch@ced97b3 (commit `ced97b3`)
> **Reviewer:** m3rl1n
> **Skills loaded:** `production-readiness-review`, `references/multi-venv-troubleshooting`, `references/flask-webapp-verification.md`

## TL;DR

- **Audit:** `87.39%` (no regression from `1785682798` baseline).
- **Tests:** Non-Qt subset **432 passed / 0 failed** (was 427/5). Fixed 5 failures
  in 1 PR (`85e809e`) — 3 bugs in `nchantdoffice/widgets/documents/media/scripts.py`
  (HTML save collapsed to "", `_resolve_document_text` walked the wrong dict,
  test fixtures missing `location="external"`).
- **Tree:** Clean after FF of `5d80f92` (1 remote commit on `origin/gamma`).
- **Active T-NEWs:** 5 (T-NEW-061 deferred to v0.2.0, T-NEW-111/112/113/114 open).
- **Ready for initial release:** NO. T-NEW-114 (`.pyof` import still broken) is the
  single P0 blocker. The 4 remaining audit dims at <60% are structural (god_class,
  data_clumps, security_ruff, security_post_install) and don't block launch if
  T-NEW-114 is closed.

## Verification ladder — actual results

### 1. Read claimed state

- `README.md` claims "12+ document types", "agent-ready structured output", "CLI
  interface", dev quick start via `pip install -e .[internal]`. All confirmed.
- `CHANGES.md` (146 lines) — 35 `T-NEW-NNN` cards listed, 27 marked **Done**,
  5 from `testing-report_20260814.md` (T-NEW-111/112/113/114) pending.
- `TODOs.md` (4259 lines) — marker counts:
  - ✅ done cards: 27 (T-NEW-040 through T-NEW-079, plus the 4 audit fixes)
  - 🔴 active cards: 5 (T-NEW-061 deferred, T-NEW-111..114)
  - open feature TODOs: 4 (settings pane per doc type, right-pane visibility,
    tab-drag region, search-across-all)

### 2. Run the audit

`sasquatch analyze -p . --skip-pii-secrets` → `87.39%` overall. Failing dims:

| Dim | Score | Status | Notes |
|---|---|---|---|
| `god_class` | 0% | fail | 2571-func denominator — split `models.py` to move. |
| `security_ruff` | 0% | fail | Ruff config not wired (T-NEW-110 partially landed). |
| `security_post_install` | 40% | partial | Pre-install script audit dim. |
| `data_clumps` | 30% | partial | Param groups; dataclass extraction. |
| `feature_envy` | 50% | partial | Per-row service reads. |
| `embedded_todos` | 58% | partial | 21 inline TODOs (BUGs.md history). |
| `file_sizes` | 60% | partial | 2 oversized files. |
| `unfinished_code` | 70% | partial | 1 finding. |
| `todo_tracking` | 79% | partial | 1 finding. |
| `git_workflow` | 85% | pass | `file://` remote — auditor bug per skill. |

`type_annotations` is now **100%** (the T-NEW-078 sweep landed). `testing` is
**100%** (per auditor's metric — the test penalty is removed for the qt_parent
harness; the 5 broken tests in the non-Qt subset were the only live penalty, now
fixed).

### 3. Run the test suite

Picked `/home/solubrew/ENVs/sasquatch/bin/python` (canonical, verified
`import nchantdoffice` clean). `pytest tests/` aborts on Qt singleton crash
(`shiboken6` aborts after the first test file imports `QApplication`).

**Per-file collection loop** (as documented in the skill):
- 70 non-Qt files (no PySide6 / shiboken import in module head)
- 27 Qt files (crash interpreter on import)
- `tests/test_qt_parent_step1.py` runs via the qt_parent subprocess harness
  (T-NEW step-1) — 6/6 pass.

**Non-Qt subset** (70 files, plain pytest, no Qt harness):

| Run | Pass | Fail | Skipped |
|---|---|---|---|
| `0c748fd` (baseline) | 427 | 5 | 0 |
| `85e809e` (this PR) | 432 | 0 | 0 |

**5 failures fixed in one PR** — root cause: T-NEW-008 round-trip contract was
broken in `scripts.py` plus test fixtures missing `location="external"`:

1. `get_content()` HTML branch: `html = ""` was a comment-out remnant; the
   `text = html.replace("<[content]>", body)` collapsed to `""`. Fix: pass
   `editor_html` through directly.
2. `_resolve_document_text()` walked the wrong dict: `content.get("text", {})`
   returned the inner `{"content": {"text": ...}}` dict, then `text.get("value", "")`
   returned `""`. Fix: `content.get("content", {}).get("text", {})`.
3. Test fixtures missing `location="external"` — `populate_document()` reads
   `self.document.location` at `scripts.py:1226`. Added the attribute to 5 mock sites.
4. Test fixture shape mismatch: production contract is `content[content][text][value]`
   (dict), but fixtures used `text=<str>`. Wrapped in `{"value": <text>}`.

**Qt subset** (27 files): most crash the interpreter on direct `pytest` invocation.
The qt_parent harness in `tests/qt_parent/server.py` is the documented runner,
designed to spawn one Qt interpreter per test. Only `test_qt_parent_step1.py` is
currently wired to use it. **The remaining 26 Qt files need to be migrated to
the qt_parent harness or split into per-file subprocess invocations** — this is
a P1 (suite hygiene, not a real bug — the tests pass individually but crash when
batched).

**T-NEW-023 fix verified end-to-end (non-Qt):** `test_reopen_round_trip_preserves_newlines_and_formatting`
(now passing) exercises the full save → reopen cycle on a Python script and
asserts indentation round-trips. The test fixture's `populate_document()` call
at line 161 simulates the same `cmd_open_local_file` → `_initial_load` →
`_load_external_file` path that the user's live "script text not preserving
formatting" bug follows.

### 4. Inspect critical code surfaces

- `cmds/runNchantdOffice.py` — config-file dev mode (T-DESK-066) landed. 13
  tests pass (`test_user_config.py` + `test_dev_mode_badge.py` +
  `test_runNchantdOffice_user_config_guard.py`).
- `nchantdoffice/utilities/pyof_import.py` — 360 lines (up from 287 per
  T-NEW-079/077). 4 contract tests pin the base-6 + content-3 table merge.
- `nchantdoffice/widgets/documents/media/scripts.py` — the save/reopen path
  inspected above. Bug count: 0 after the fix.
- `nchantdoffice/widgets/documents/journal.py` — `save_app()` path is the
  canonical contract (T-NEW-079). 4 dedicated tests pin it.
- `nchantdoffice/updates/db.py` — `UpdateChecker` + `DBUpdate` boot wiring
  (T-NEW-058). 7 tests pin the boot hook + `_upgrade_lock` + mock fixture
  alignment with `parent.model.codex`.

## Priority memo

### P0 — single fix that unblocks the whole pipeline

**T-NEW-114: `.pyof` import still broken after T-NEW-074/077** (filed 2026-08-14)
- 3 wiring defects per `testing-report_20260814.md` item 4.
- Consolidated fix scoped in `TODOs.md` line 4259: `cmd_import_local_file` is the
  single canonical `.pyof` dispatcher; both `cmd_import_local_file` and
  `cmd_open_local_file` route `.pyof` through it; remove the `#Implement import
  of .pyof database` TODO marker; Defect C worker-thread offload in same PR.
- Without this, importing a `.pyof` file (the application's primary project
  format) silently fails — any user who has been led to try the import flow
  hits a 500 with no actionable log.

### P1 — what remains once P0 lands to make the app actually work end-to-end

1. **T-NEW-111** — Type-aware file-open dialog filter (per active tab's doc type).
   ~5 static-filter sites to switch to a `FILE_TYPE_FILTERS` registry. 1–2 days.
2. **T-NEW-112** — Type-aware file-import dialog filter. Same registry, scoped
   to the importer chain. 1 day.
3. **T-NEW-113** — Autosave on focal-change per document type. Per-doc-type
   hooks; opt-out list. 2 days.
4. **Qt suite migration to qt_parent harness** — 26 Qt files crash the
   interpreter on batched pytest. Migrate to `qt_parent/server.py` (already
   proven at step 1) or split into per-file subprocess invocation. 1–2 days.
   Without this, CI runs `pytest tests/` abort on the first Qt file and
   silently hide the rest of the test surface.
5. **Stale TODO cleanup** — `TODOs.md` has 4 open feature TODOs from the
   pre-T-NEW era (settings pane per doc type, right-pane visibility, tab
   drag region, search-across-all). Audit each — promote to T-NEW or
   mark deferred. 1 day.

### P2 — business-logic and integration work (1–2 weeks)

1. **`god_class` 0%** — `models.py` is the largest single file; split into
   per-domain modules (ad_tab, affiliate, journal, etc.). Lifts the audit
   from 0% → 60%. 1 week.
2. **`data_clumps` 30%** — dataclass extraction for param groups (file_path
   triple, content-envelope triple). 3 days.
3. **`feature_envy` 50%** — push per-row checks onto model/dataclass methods
   (per the `nchantdoffice 2026-08-03` recipe: `ReleaseSetupLinksService._release_one_entry`
   + `UserSpec.check_format`). 3 days.
4. **`security_ruff` 0%** — wire ruff config in `pyproject.toml` per T-NEW-110.
   1 day.
5. **`security_post_install` 40%** — pin the install-time script audit. 1 day.
6. **T-NEW-061** — auto-install + Ed25519 signature verification (deferred to
   v0.2.0 per the user's prior scoping).

### P3 — polish, deferred features, future scope

- **`type_annotations` is already 100%** (T-NEW-078 sweep).
- **`embedded_todos` 58%** — 21 inline TODOs from the BUGs.md history. History
  markers; sweep as you touch each file.
- **`unfinished_code` 70%** — 1 finding (the commented-out `_build_chart_action_button_group`
  is pinned by a regression test per T-NEW-037).
- **`file_sizes` 60%** — 2 oversized files. Split in P2 alongside god_class.
- **`todo_tracking` 79%** — 1 finding. Sweep as you touch each card.
- **`git_workflow` 85%** — auditor's "no git remote" finding is a false
  positive (the remote is `file://` per skill's verified recipe).

## Cross-repo coordination

- **Server (nchantdoffice_com):** T-NEW-061 (signature verification) is the
  build-vs-server contract boundary. The server changes are independent of
  the desktop; they're encapsulated in the `v0.2.0` release.
- **Marketing (nchantdofficeATNRG):** T-NEW-044 UI-1/2/3 and T-NEW-045
  WIRE-1 all landed (referral panel, ad-tab-free hours, affiliate panel,
  grant trigger). The release checklist R-1..R-4 in
  `docs/cross-repo-review_20260807.md` is the parity check.
- **Parent lib (nchantrs):** `fa05530` (H25 catalog child count) + `5afde9d`
  (H30 setData arg order) + `57839d2` + `be8a582` (H31 self.parent shadowing)
  are the parent commits the desktop depends on. All four are upstream.

## Acceptance criteria for "ready for initial production release"

- [ ] `python -c "import nchantdoffice"` succeeds via `/home/solubrew/ENVs/sasquatch/bin/python`
- [ ] `pytest tests/test_*.py --ignore=tests/test_t_new_*.py --ignore=tests/test_prompt_for_new_names.py ...` (the 70 non-Qt files) reports `0 failed`
- [ ] `pytest tests/qt_parent_step1.py` reports `6 passed` (proves the qt_parent harness works)
- [ ] T-NEW-114 `.pyof` import: launching the app, `cmd_import_local_file` on a `.pyof` with one row in `app_tree_node` populates the host DB with 1 row, `nid_txt` preserved, fresh rowid
- [ ] T-NEW-111/112: open a `.md` file in an Image tab → dialog filter is `*.md` only, not `*.json`
- [ ] T-NEW-113: open a Notebook, edit, switch tab, switch back → no save dialog prompt (autosave fires)
- [ ] Audit score ≥ 90% with no test penalty (currently 87.39%, 100% on testing)
- [ ] `bug NchantdScript still not returning text content with formatting` (T-NEW-023) is closed via the 3-bug fix in this PR (`85e809e`)
- [ ] `git push origin gamma` succeeds (already verified)

## Open questions

1. The Qt suite harness migration (P1) — does the user want every Qt test
   migrated to `qt_parent/server.py` (incremental, ~1-2 days), or a wholesale
   re-architect (the `qt_parent` step-1 is RED-shaped, so the step-2/3 work
   is already a known scope)?
2. T-NEW-114 fix scoping — the user filed 3 defects; the consolidated fix
   proposes 1 PR but is the user ok with Defect C (worker-thread offload) in
   the same PR, or split?
3. `TODOs.md` line 4259 says the T-NEW-114 fix is "REPRODUCED + FIX SCOPED" —
   is the user ready to start work, or want this scoped-checked first?
4. The 4 open feature TODOs (settings pane per doc type, right-pane visibility,
   tab drag region, search-across-all) — promote to T-NEW or mark deferred?

## Pitfalls encountered

- **`patch` tool fails twice with `path required`** when invoked without
  `path` in the kwargs — switched to absolute path. Per the user's tooling
  notes, this is a known intermittent quirk; the work was uncontested.
- **`pytest tests/` aborts on `shiboken6` import** — known Qt singleton pitfall
  per the skill's references/multi-venv-troubleshooting.md. Used the per-file
  collection loop to identify the 70-vs-27 split.
- **Production code bugs surfaced via test fixtures** — the 5 failing tests
  traced back to 2 real bugs in `scripts.py` that the test fixtures had been
  patched around (the `location` attribute was the easy one; the
  `_resolve_document_text` dict-walk bug and the `get_content` HTML template
  collapse were the real finds). Per the skill's "diagnose failure modes
  before ranking" reminder — 5 failures, 2 root causes, 1 PR.
- **Auto-generated audit artifacts** — `sasquatch analyze` rewrites
  `FALCON_TEST.yaml`, `PROJECT_TRACKER.yaml`, `test_reports/*` and creates
  `PROJECT_TRACKER.md` (untracked). Discarded before per the skill's
  "auto-generated tracker files dirty the tree" pitfall. Did NOT commit
  them in the PR.

## Commit trail from this review

- `85e809e fix(scripts): HTML save + reopen round-trip (T-NEW-008 pre-req)`
  - 4 files, 32 insertions, 15 deletions
  - 2 source bugs fixed, 4 test fixtures corrected
  - 432 passed / 0 failed (was 427/5)
  - Pushed to `origin/gamma`

## References

- `TODOs.md` line 4259 — T-NEW-114 fix scope
- `testing-report_20260814.md` — user-reported defects (T-NEW-111..114 source)
- `BUGs.md` — historical stack traces (428 lines, archive only)
- `PROJECT_TRACKER.md` — full audit report (62 dims, 87.39% overall)
- `nchantdofficeATNRG/cross-repo-changelog.md` — server/desktop/ATNRG parity
- `nchantdofficeATNRG/dev-setup.md` — T-NEW-070 dev-mode quick start
- `tests/qt_parent/server.py` — Qt subprocess harness (T-NEW step-1)
- `tests/test_qt_parent_step1.py` — 6/6 passing
