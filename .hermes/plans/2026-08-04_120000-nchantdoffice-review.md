# NchantdOffice review — 2026-08-04

**Project:** `/home/solubrew/.hermes/projects/nchantdoffice`  
**Branch / HEAD:** `gamma` / `a48fad9` (matches `origin/gamma`)  
**Review basis:** live Sasquatch run, live pytest runs, import smoke, current source, `TODOs.md`, `BUGs.md`, `testing-report_20260803.md`, and `testing-report_20260804.md`.

## Two facts that re-rank every priority

1. The live NchantdOffice package root imports, but `nchantdoffice.models` does not: current Pyffice HEAD `04cf9a9` imports `PyfficePortCherryTree` from `pyffice.ports.ports`, while that class no longer exists there. This single cross-repo regression causes 16 collection errors and many of the 58 executable-test failures.
2. The fresh Sasquatch result is **87.97% internal / 77.97% displayed** because Falcon ran 0 tests and applied a 10-point penalty. The current tracker is for project commit `a48fad9` and Sasquatch commit `c25d9c5`, so this score is current and attributable.

## Live verification

### Sasquatch

Command:

```bash
QT_QPA_PLATFORM=offscreen /home/solubrew/ENVs/sasquatch/bin/sasquatch analyze -p . --skip-pii-secrets
```

Result:

- Internal score before test adjustment: **87.97%**
- Test adjustment: **-10.00** (`0/0` tests)
- Displayed score: **77.97%**
- Tracker versions: project `a48fad9` dirty (generated reports), Sasquatch `c25d9c5`
- Passing dimensions: 49/58
- Partial dimensions: 6/58
- Failing dimensions: 2/58

Lowest dimensions:

| Dimension | Score | Current finding |
|---|---:|---|
| `god_class` | 0 | 8 classes; reported examples include `NchantdOfficeCloakModel` (2,754 lines / 121 methods), `NchantdOfficeSettingsModel` (727/64), `NchantdOfficeWebBrowser` (1,507/91), and `NchantdOfficeSketch` (1,300/85). |
| `unfinished_code` | 0 | 87 empty methods; examples include `models.py::get_links`, `models.py::get_node_name`, `models.py::get_tab_name`, catalog edit handlers, `NchantdOfficeTabSet.go_to_previous_tab`, and journal parsing. |
| `type_annotations` | 2 | 53/2,388 functions typed. |
| `data_clumps` | 40 | 6 repeated parameter groups. |
| `feature_envy` | 50 | 5 findings, concentrated in `models.py::search_documents` and pane `parse_document` methods. |
| `embedded_todos` | 58 | 21 inline TODO markers in 12 files. |
| `todo_tracking` | 79 | Same 21 markers; journal/documents/settings are the leading files. |

`git_workflow: 85%` is a confirmed auditor false positive: Sasquatch says no remote, but `git remote -v` shows the configured `file:///mnt/overse/.../nchantdoffice.git` origin and HEAD is synchronized.

### Tests

Normal command:

```bash
QT_QPA_PLATFORM=offscreen /home/solubrew/ENVs/sasquatch/bin/python -m pytest tests -q --tb=no
```

Result: **collection interrupted with 16 errors**.

Diagnostic continuation command:

```bash
QT_QPA_PLATFORM=offscreen /home/solubrew/ENVs/sasquatch/bin/python -m pytest tests -q --tb=no --continue-on-collection-errors
```

Result: **147 passed, 58 failed, 16 collection errors**.

Primary shared root cause:

```text
ImportError: cannot import name 'PyfficePortCherryTree'
from 'pyffice.ports.ports'
```

Verified cross-repo state:

- `/home/solubrew/.hermes/projects/pyffice/pyffice/pyffice.py` still imports `PyfficePortCherryTree`.
- `/home/solubrew/.hermes/projects/pyffice/pyffice/ports/ports.py` currently defines eight other `PyfficePort*` classes but not `PyfficePortCherryTree`.
- Pyffice is itself synchronized at `04cf9a9`, so reinstalling the editable package cannot repair the source mismatch.

Independent verified failures:

- Ruff F821: `NchantdGridScrollGroupBox` is undefined at `nchantdoffice/widgets/config/referral_panel.py:169,199`.
- `tests/test_live_crash_guards.py::test_T_NEW_015...` is stale against current nchantrs source: the default now uses single quotes / guarded assignment, while the test asserts an exact double-quoted source string.
- `tests/test_unimplemented_features.py` references the deleted `nchantdoffice/widgets/timelines.py`; this is an orphan-test/refactor mismatch after the latest upstream cleanup.
- Pytest config warns that `mock_use_standalone_module` is unknown.

## Test-report review

### `testing-report_20260803.md`

The report identifies five live UX defects and one crash:

1. Calculator does not accept numpad/number-row keyboard input.
2. Browser does not save/restore URL traversal history.
3. New-node action should prompt for a name.
4. New-tab action should prompt for a name.
5. Document Catalog bottom pane disappears after accepting a newly created tab.
6. Image sizing forces the right pane narrow and leaves it stuck.
7. Crash: `NchantdOfficeStore` lacks `_build_filter_config` when `get_view_link()` calls inherited `get_links()`.

Current-state reconciliation:

- Name-entry dialogs are claimed shipped in TODOs (Sprint 23), but the report proves the live UX still did not satisfy the user on 2026-08-03; this needs a real GUI interaction regression, not another source-presence assertion.
- Browser tests currently cover serialized profile/history bytes, but the live report shows navigation traversal restore is not working end-to-end. Existing tests verify persistence shape, not visible browser traversal behavior.
- `_build_filter_config` remains absent from the current nchantrs tree while `nchantrs.models.models.get_links()` still calls it. This crash remains a confirmed cross-repo P0 candidate.
- No current tests were found for calculator keyboard input, image/right-splitter recovery, or the catalog bottom-pane lifecycle.

### `testing-report_20260804.md`

The report identifies:

1. Desktop UI triggers CLI `getpass` (`Master passphrase:`); it needs a GUI passphrase popup.
2. Affiliate Manager tab fails while building its toolbar: `Action show_pane_left Lookup Config is Empty {}`.
3. The same path logs a schema warning: `app_action` query orders by missing `position_int`.

Current-state reconciliation:

- The passphrase prompt is deliberate in PyKeyStore for CLI/non-GUI use; the desktop caller must provide a GUI passphrase flow rather than weakening PyKeyStore.
- `show_pane_left` is present in nchantrs seed YAML, so the empty lookup is not a missing static action definition. The simultaneous `position_int` warning points to stale/incomplete live `app_action` schema or seed migration, which should be tested through a fresh/upgrade DB round trip.

## Priorities

### P0 — restore a truthful test pipeline

1. **Fix the Pyffice port refactor mismatch in Pyffice.** Write a failing Pyffice import/public-API test, then either restore `PyfficePortCherryTree` in its canonical module or remove/update the stale consumer import after verifying its replacement. Reinstall editable Pyffice and rerun NchantdOffice tests.
2. **Fix the two referral-panel F821 findings.** Import/use the real `NchantdGridScrollGroupBox` symbol or replace it with the current canonical widget; pin with the existing F821 test.
3. **Re-run and reclassify.** Do not treat the current 58 failures as 58 defects. Once the Pyffice import is fixed, rerun the full suite and classify only residual failures.

### P1 — live report crashes and destructive regressions

1. Repair `_build_filter_config` ownership in nchantrs (or replace `get_links` with the current canonical filter builder) via cross-repo TDD; verify new-tab accept no longer crashes.
2. Add an `app_action` schema/seed migration test covering `position_int` and `show_pane_left`; verify Affiliate Manager opens on an upgraded DB.
3. Add a GUI passphrase provider at the NchantdOffice call site while preserving PyKeyStore's deliberate CLI `getpass` behavior.
4. Add end-to-end GUI regressions for browser history restore, image/right-splitter recovery, and catalog bottom-pane persistence.
5. Reconcile orphan/stale tests caused by upstream deletions/renames (`timelines.py` and exact-source nchantrs assertions).

### P2 — functional UX gaps

- Calculator keyboard input parity with button clicks.
- Confirm and repair new-node/new-tab prompt behavior in the actual toolbar flow.
- Finish the partially open Data Source configuration card (`T-NEW-034`).
- Restore Journal always-save behavior and remaining save-mode/default-internal behavior.

### P3 — structural audit lifts

- Split god classes only behind characterization tests; do not combine this with live-bug fixes.
- Incrementally annotate public APIs rather than mechanically touching all 2,388 functions at once.
- Resolve genuine empty methods and tracked TODOs by behavior; do not substitute log/return-self stubs.
- Defer constructor/data-clump reshaping where it conflicts with the established `(parent, cfg)` framework contract.

## Acceptance gate

- [ ] `QT_QPA_PLATFORM=offscreen .../python -c "import nchantdoffice.models"` succeeds.
- [ ] Pyffice public-API test proves the port import/refactor contract.
- [ ] `ruff check nchantdoffice --select F821` reports no findings.
- [ ] `pytest tests -q --tb=no` reports 0 collection errors and 0 failures.
- [ ] Sasquatch Falcon report has a non-zero test count and no -10 penalty.
- [ ] Fresh/upgrade database contains `app_action.position_int` and resolves `show_pane_left`.
- [ ] New-tab accept completes without `_build_filter_config` failure.
- [ ] Affiliate Manager opens without CLI passphrase input and without action lookup failure.
- [ ] Browser visible traversal history restores after close/reopen.
- [ ] Image resize does not permanently constrain the right splitter.
- [ ] Calculator accepts both number-row and numpad key events.
- [ ] Catalog lower pane remains visible after creating/accepting a tab.

## Working-tree note

The review updated generated artifacts only: `FALCON_TEST.yaml`, `PROJECT_TRACKER.yaml`, `test_reports/FALCON_TEST.yaml`, and `test_reports/pytest_report.json`. No production source was edited during this review.
