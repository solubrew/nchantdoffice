# TODAY is 2026-08-17:

This report records the current verification state after the
2026-08-17 gamma work. The original live-testing note was limited to
a date/time insert button; the following runtime and test-harness
changes were subsequently shipped:

## Document Changes

- Date/time insert button added to the NchantdOfficeScript toolbar
  with the `Ctrl+D` hotkey.
- T-NEW-122 Qt collection guard and lazy QApplication fixtures added.
- T-NEW-117 palette extraction shipped in pyffice and graceful
  downstream fallback added.
- Chart `addWidget(None)` native-crash path fixed.
- `.pyof` worker test native-crash path fixed by guarding bare Qt
  parent access.

## Verification

- T-NEW-122 guard: 2 passed.
- Palette extraction: 30 upstream tests passed; 9 downstream palette
  tests passed.
- Chart regression: 16 tests passed.
- `.pyof` worker routing: 5 tests passed.
- The full suite reaches native Qt tests but is not green: repeated
  SIGSEGV occurs in `test_per_doc_type_settings_pane.py` through
  `nchantrs/widgets/widgets.py:193`. That is the next test-harness
  blocker and is not represented as a successful full-suite run.

## Remaining Bugs / Blockers

- Isolate the per-document-type settings tests in the Qt-parent
  subprocess harness.
- Re-run the full suite after that isolation.
- Only then classify the remaining ordinary assertion failures and
  refresh the sasquatch audit artifacts.
