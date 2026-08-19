# NchantdOffice TODOs — current state (2026-08-17)

> **Consolidation date:** 2026-08-17.
>
> This file replaces the previous `TODOs.md`, the historical `STATE.md`,
> and the session-only `SESSION_NOTES.md` (both now in
> `_data_/archive/2026-07-29/`). It captures the project state after the
> closed-loop of Sprints 1-17 across nchantdoffice / nchantrs / pyffice /
> pycurity / pyside6pandas, plus the 2026-08-10 → 2026-08-17 T-NEW
> sweep (110..147) and the 2026-08-17 batch
> (`260886a` / `419a317` / `899962c` / `07fc18b` — closes
> T-NEW-122, T-NEW-117, T-NEW-037-followup, and the pyof
> bare-parent segfault respectively).
>
> **T-NEW-NNN card numbering — per-repo convention.** This
> repo's `T-NEW-NNN` numbers are local to nchantdoffice
> (desktop) and do NOT match the numbering in the server
> (nchantdoffice_com) or ATNRG repos. Example: `T-NEW-040`
> means "Toolbar init tech debt" here but "Defensive Admin
> role creation" in nchantdoffice_com and "Affiliate
> rotation expansion" in ATNRG. When cross-referencing a
> card from another repo, always prefix it: "DESK
> T-NEW-NNN" / "COM T-NEW-NNN" / "ATNRG T-NEW-NNN" —
> without the prefix the reference is ambiguous.

> **Other top-level notes** (preserved as separate files):
> - `README.md` — project overview
> - `CHANGES.md` — Keep-a-Changelog history
> - `CI_CD.md` — pipeline overview
> - `CLI.md` — command-line reference
> - `CODING_STANDARDS.md` — V4 standards compliance
> - `directory_tree.md` — file-tree snapshot (2026-07-16)
> - `BUGs.md` — raw stack-trace archive (historical reference)

---
# New TODOs
- Pycurity password vault initialization in SetupWizard — **FIXED** (private store at ~/.local/share/nchantdoffice/pycurity/)

- Image Document tab is push the width instead of resizing the image, image should fit to width and size the height maintaining the aspect ratio — **FIXED** (`"scaled": True` at images.py:710)
- NchantdOfficeBrowser is not keeping track of url navigation or reloading to the last visited site — **FIXED** (populate_document loads saved URL from app_media)
- FileDetailsPane refresh on initial file open — **FIXED** (refresh() helper + set_file_path calls refresh)
 
 
- fix and finish Affiliate Manager tab — **FIXED** (referral_panel.py implemented with 11 tests passing)
- add a settings pane for each document type in the Center Pane Settings of the Interface Tab
- fix Right Pane tabs to select which ones can be adjusted in the right side tabset in the Interface Tab
- Tab drag and drop needs to only initiate when the mouse is clicked on to the tab name area not the main widget area
- implement the ability to drag a tab to a different node - and it saves the new parent
- implement the ability to drag a tab to the rightside tabset and it reloads to its original location
- add to Settings/Interface tab config to allow a user to select that tab name updates to the file name when a file is opened 
- implement search across all nodes and tabs as well as node specific and tab specific search as well finish code in the NchantdOfficeApplicationToolBox 
- NchantdOfficeJournalEditor always-save functionality fixed (outer save() now calls _parse_entry + parent.save) — **SUPERSEDED** by the
  app_media restoration work (T-NEW-079). The current canonical save contract: outer save() calls `self.save_app()` ONLY. The
  `_parse_entry()` / `parent.save()` blocks are intentionally commented out (the always-save follow-up is a separate card). The inner
  `NchantdOfficeJournalAppendEditor.save()` does call `_parse_entry()` -> `add_entry()` -> `parent.save()` chain which populates the entries
  dict. `parse(content)` splits the full text on `--|YYYY-MM-DD HH:MM:SS|--` markers and stores the `{timestamp: block_text}` dict in
  `self.entries` (the in-memory cache). Do NOT re-introduce `super().save()` on the journal path -- it persists to `doc_media_content` which
  is the wrong table for an app_media document. See `nchantdoffice/widgets/documents/journal.py`, `save_app()` docstring at
  `nchantdoffice/widgets/documents/documents.py:625`, and the full T-NEW-079 card body in this file.

- Name-entry dialog for new nodes/tabs — checkboxes now in Settings/Interface tab — **FIXED** (prompt_for_new_node_name, prompt_for_new_tab_name checkboxes added to settings.py)
- Tab drag-drop only initiates on tab name area — **FIXED** (nchantrs tabs.py _is_in_tab_name_area)
- Drag tab to different node saves new parent — **FIXED** (cmd_set_tab_parent in trees.py)
- Search across all nodes/tabs — **FIXED** (test_t_new_033_search_dispatch.py passes)
- Rename tab to file name on file open — **FIXED** (update_tab_name_to_file_name in settings.py)

## New TODOs from testing-report_20260803 / _20260804 (2026-08-06 catalog)
- **T-NEW-049** ✅ CRITICAL: Instruct object not JSON serializable — **FIXED** (_safe_json_default at models.py:105)
- **T-NEW-050** ✅ get_view_link → _build_filter_config missing — **FIXED** (get_links delegates to store at models.py:1830)
- **T-NEW-051** ✅ app_action ORDER BY position_int — **FIXED** (position_int added to models.yaml:24)
- **T-NEW-052** ✅ Action show_pane_left Lookup Config Empty — **FIXED** (blocked on T-NEW-051, which is fixed)
- **T-NEW-053** ✅ Calculator keyboard input (number pad / number row) — fixed
- **T-NEW-054** ✅ Cap tabs per node (adjustable param, default 35) — fixed
- **T-NEW-055** ✅ NchantdOfficePalette integration with NchantdOfficeImage toolbar — fixed
- **T-NEW-056** ✅ Cap total nodes per non-pro user at 100 (configurable) — fixed
- **T-NEW-057** ✅ Review doc + cmd + RED regression tests landed in commit `bcfb730` (2026-08-10, gamma). Implementation follow-up is T-NEW-058 / T-NEW-059 / T-NEW-060 / T-NEW-061.
- **T-NEW-058** ✅ Wire `UpdateChecker` + DBUpdate into boot — `_upgrade_lock` flag + `run_update_process` helper + 3 boot-hook tests, commit `c85fcf4` (2026-08-10, t-new-058).
- **T-NEW-059** ✅ User-configurable update-check interval — `refresh_interval_seconds(cfg)` helper + `cmd_on_change_check_update_interval_hours` spinbox + 4 interval tests, commit `10c8848` (2026-08-10, t-new-059).
- **T-NEW-060** ✅ Tray icon + per-version snooze (`dismiss_version(days=7)`), commit `619b493` (2026-08-10, t-new-060).
- **T-NEW-062** ✅ Notebook Jupyter-side URL sync (`_sync_notebook_from_url`), commit `126489b` (2026-08-10, t-new-062).
- **T-NEW-063** ✅ Image aspect-ratio preservation, commit `f879e47` (2026-08-10, t-new-063).
- **T-NEW-064** ✅ Script tab "Missing Text" stub removed, commit `6a1b9e2` (2026-08-10, t-new-064).
- **T-NEW-065** ✅ Journal content compaction (narrow scope), commit `b213122` (2026-08-10, t-new-065). PII deferred; time-based/policy/mark-for-deletion deferred to T-NEW-066/067/068.
- **T-NEW-066** ✅ Matrix chart extraction from Excel workbooks — **landed in pyffice** (upstream of nchantdoffice). `PyfficeMatrix.load_excel()` now extracts charts from `ws._charts` via two new helpers (`_extract_charts_from_worksheet` + `_chart_from_openpyxl`). 5 tests in `tests/pyffice_unit/unit/matrix/chartExtractionTEST.py`. Commit `95a8d9f` (pyffice gamma, merged as `4ed8768`). User-facing: NchantdOfficeMatrix inherits the change automatically.
- **T-NEW-067** ✅ PyfficeChart direct .xlsx loading — **landed in pyffice**. New `PyfficeChart.load_from_xlsx(file_path, chart_index=0, include_data=True)` opens a chart directly without going through Matrix. 4 tests in `tests/pyffice_unit/unit/charts/loadFromXlsxTEST.py`. Commit `3fb26cf` (pyffice gamma, merged as `b3aee3f`). User-facing: NchantdOfficeChart inherits the change automatically.
- **T-NEW-068** ✅ NchantdFilesystem location memory, commit `46cb95f` (2026-08-10, t-new-068).

- **test fix** test_script_open_format failing — test mock missing `.content` attribute
- **test fix** test_per_doc_type_settings_pane segfaulting in initView (nchantrs line 193)


---

## 1. Project snapshot

| Dimension | Value |
|---|---|
| Project | NchantdOffice |
| Type | Desktop GUI application (PySide6) |
| Branch | `gamma` (ahead of `origin/gamma`: `c246108` t-new-068 merge, `9f18e30` Script external save-to-disk via syntax-aware exporter, `cbec5b3` PDF internal binary storage + canonical envelope; plus Script cell mirror / Matrix toolbar / Matrix DB encoded payload / T-NEW-122 Qt-collection guard fixes) |
| HEAD | `cbec5b3` (nchantdoffice/gamma, 2026-08-18) |
| Working agreement | Internal projects are CORE INTEGRATED; never stub them out |
| Test env | `QT_QPA_PLATFORM=offscreen /home/solubrew/ENVs/sasquatch/bin/python` |
| Test command | `QT_QPA_PLATFORM=offscreen /home/solubrew/ENVs/sasquatch/bin/python -m pytest tests --continue-on-collection-errors -q` |
| Current test surface (T-NEW-122 baseline) | `260886a` post-fix full-suite run with `--ignore=tests/test_cmd_pyof_routing_consolidation.py` (the file exposed the unrelated pre-existing pyof bare-parent SIGSEGV, fixed the same day in `07fc18b`): **19 failed, 836 passed, 6 skipped** (100% collection reached; pre-`260886a` the run aborted at 8% of collection). The 19 functional failures are pre-existing logic bugs unrelated to collection stability; the 6 skips are defensive `pytest.skip()` guards against a pre-existing Qt+offscreen SIGSEGV in production `initView` (`widgets.py:193`, `document_settings.py:158`). Full-suite final count NOT independently re-measured after the `07fc18b` pyof fix on 2026-08-17 — see `testing-report_20260817.md` for next-day targeted evidence. |

### Internal-project stack (CORE INTEGRATED)

| Project | Purpose | Install |
|---|---|---|
| `nchantrs` | Core widget library | `pip install -e /home/solubrew/.hermes/projects/nchantrs --no-deps` |
| `nchantdoffice_com` | Companion web app (Flask) | `pip install -e /home/solubrew/.hermes/projects/nchantdoffice_com --no-deps` |
| `pyffice` | Document model (`PyfficeDocument` etc.) | `pip install -e /home/solubrew/.hermes/projects/pyffice --no-deps` |
| `kahndor` | Config / instruct / logma | `pip install -e /home/solubrew/.hermes/projects/kahndor --no-deps` |
| `pycurity` | Secrets, encryption, hash, key management | `pip install -e /home/solubrew/.hermes/projects/pycurity --no-deps` |
| `pyularity` | **NEW (T-NEW-172):** process supervisor (crash-detect + restart + lifecycle hooks + health-check protocol). Stub repo today; first useful version ships in T-NEW-172's WIRE-1 step. | `pip install -e /home/solubrew/.hermes/projects/pyularity --no-deps` (planned — repo exists at the path but no install lane is wired into the desktop yet) |
| `subtrix` | UUID generator | `pip install -e /home/solubrew/.hermes/projects/subtrix --no-deps` |
| `falcon` | CLI / scaffolding engine | `pip install -e /home/solubrew/.hermes/projects/falcon --no-deps` |
| `sasquatch` | Audit + test pipeline | bundled with sasquatch venv |
| `squirl` / `micromole` | Desktop persistence (NOT SQLAlchemy) | bundled with nchantdoffice |
| `pyside6pandas` | Pandas-Qt table widget (was 0.0.0 placeholder; fixed in Sprint 11) | `pip install -e /home/solubrew/.hermes/projects/pyside6pandas --no-deps` |

### Working agreements (still in force)

1. **Fix in project source, not auditor.**
2. **No log+return-self stubs** — implement real logic.
3. **Don't change `(parent, cfg)` constructor signatures** without explicit user approval.
4. **Don't rename `Pyffice<Document>` classes** to satisfy parallel-inheritance refactors.
5. **Explain-before-action** on architectural changes.
6. **One commit per file/logical group** with terse messages.
7. **All secrets via PyKeyStore** — never env vars (per working agreement).
8. **Desktop must NOT use SQLAlchemy** — uses squirl + micromole.

---

## 2. Canonical active backlog (2026-08-18)

This section is the source of truth for current work. Historical card
bodies remain below for traceability, but do not override this list.

### P0 -- confirmed broken in operator testing

1. **T-NEW-148 -- External Script Save writes back to disk.**
   ✅ FIXED in `9f18e30`. `NchantdOfficeScript.save()` now exports
   the editor payload through the syntax-aware helper
   (``toHtml`` / ``toMarkdown`` / ``toPlainText``), writes it
   atomically through ``.tmp + os.replace``, and only when
   ``document.location == "external"``. Internal Script persistence
   is unchanged. 5 new tests in
   ``tests/test_t_new_148_script_external_save.py``.
2. **T-NEW-149 -- Matrix internal value persistence and restore.**
   ✅ PARTIAL via `cbec5b3` comm flow -- the actual Matrix fix for
   `content_enc64_txt` preserving the grid through the save chain was
   landed via the `_legacy_export_editor_payload` envelope changes; see
   `widgets/documents/workbooks/matricies.py:1280-1310`. The full DB
   round-trip still needs an integration pin. Cell mirror lives in
   `matricies.py:1739-1765` (`_mirror_cell_to_document`).
3. **T-NEW-150 -- Disable Matrix formula toolbar until 0.0.3.**
   ✅ FIXED in `5a95c54`. `_FORMULA_TOOLBAR_ENABLED = False` guards
   both `Apply Formula` and `Auto Calculate` actions; the methods
   remain defined for 0.0.3 re-enable. 5 tests in
   `tests/test_t_new_150_matrix_formula_toolbar_disable.py`.
4. **T-NEW-151 -- Fix nchantrs password verifier mismatch.**
   ✅ FIXED in `5e1999d` (upstream nchantrs). Added a single-line
   alias `verify_password = verify_pword` inside `NchantdUser`
   so both names resolve to the same impl. The operator's
   first-boot `app_user` bootstrap now finds the method the
   caller asks for. 4 new AST-source tests in
   `tests/unit/nchantrs/utilities/test_verify_password.py`.

### P0.b -- T-NEW-144b phase 2 completed (2026-08-18)

- **T-NEW-159 -- NchantdOfficePDF internal binary storage.**
  ✅ FIXED in `cbec5b3` (downstream) and `4a7914c` (upstream pyffice).
  `populate_document` honours origin: ``internal`` -> load from
  ``document.binary`` / ``bytes`` via ``QPdfDocument.loadFromData``,
  ``external`` -> load from ``file_path``. ``get_content`` returns
  the canonical envelope (``{"content": {"file_path": ...,
  "bytes": ...}, "data": None}`` when internal). Pyffice
  ``PyfficePDF.get_binary`` returns the stored blob when set,
  otherwise disk bytes. PDF widget remains read-only; no
  external-save seam yet. 5+5 new tests.

### P1 -- operator workflow and performance

5. **T-NEW-152 -- Refresh ToolBox after node deletion.**
   `cmd_delete_node` refreshes the tree but not the document ToolBox.
   **Affected site:** `widgets/panes/documents.py:127-159`.
6. **T-NEW-153 -- Node-delete navigation fallback.**
   Navigate previous node first, then sibling, then parent when deleting
   the active node. Upstream `go_to_previous_node` currently handles only
   `previous_index` (`nchantrs/views/treeviews.py:110-117`).
7. **T-NEW-154 -- Profile new-document creation performance.**
   Add stage timing before optimizing; no timing instrumentation currently
   identifies the bottleneck in `widgets/panes/new.py` / document create.
8. **T-NEW-155 -- Script date/time insert and Ctrl+D.**
   Add the toolbar action and shortcut requested in the latest operator
   report; no Ctrl+D registration currently exists.
9. **T-NEW-156 -- Sort `_`-prefixed nodes first.**
   Add an explicit underscore-priority comparator while preserving the
   selected ascending/descending order for the remaining names.

### P2 -- parsing, privacy, and technical debt

10. **T-NEW-118 -- Journal parsing + PII integration only.**
    Full-text save/restore and retention already work and MUST NOT be
    changed. Integrate existing `pycurity.pymatch.extract_all_pii()` into
    journal parsing/redaction/PIN-copy behavior. Any expansion of base PII
    functionality belongs upstream in pycurity.
11. **T-NEW-121 -- Source-encoding guard and ASCII cleanup.**
12. **T-NEW-157 -- Search correction-position fallback.**
    Resolve `models.py:3039` instead of silently forcing position 0.
13. **T-NEW-158 -- Referral desktop passphrase guard.**
    Replace the unnumbered `T-NEW-XXX` marker at
    `widgets/config/referral_panel.py:395` with the real Qt masked-entry
    flow so the desktop never falls into a CLI getpass prompt.

### Active umbrella sequencing

- **T-NEW-144b -- Multi-format external editing:** ✅ CLOSED 2026-08-19.
  Work proceeded one widget at a time per the umbrella rule.
  All 12 children shipped:

    * **T-NEW-148 / NchantdOfficeScript** -- DONE (`9f18e30`).
      Syntax-aware atomic external save, internal save untouched.
    * **T-NEW-159 / NchantdOfficePDF** -- DONE (`cbec5b3` +
      `4a7914c`). Internal binary storage via blob; external path
      remains file-only because the widget is read-only.
    * **T-NEW-160 / NchantdOfficeImage** -- DONE (`f499b7c`).
      Drop the `set_location("external")` hardcode in `initView` +
      guard the hint in `open_file`. The .pyof internal-blob load
      path now works. (Image external-save seam requires upstream
      `NchantdImage.pixmap()` or `self.document.to_bytes()` —
      tracked separately, not in this card.)
    * **T-NEW-160a / NchantdOfficeNotebook** -- DONE (`7bc68dc`).
      Same routing fix as Image: drop initView hardcode + guard
      `open_file`. `save()` was already correct (handles external
      `.ipynb` write + to_dict/both save modes).
    * **T-NEW-160b/1-9 (Sketch, Form, FormManager, Contact,
      Rolodex, ContextListPane, PromptManager, Prompt, Chart)**
      -- DONE (`a1c5932`, `54fbedc`, `ab0307b`, `883373c`,
      `41fb641`, `01194b9`, `a9e56c3`, `cb3c607`, `73dd4fd`).
      Each card removed the umbrella hardcode on one widget,
      kept the location-aware dispatch intact, and added
      3 AST-source structural regression guards.
    * **T-NEW-160b/10 / NchantdCompressPane** -- DONE (`47a0c6e`,
      special case). Pane extends `NchantdPane` (not a document);
      the flag-only `set_location("external")` and its dead
      commented-out dispatch were both removed.
    * **T-NEW-160b/11 / NchantdOfficeFileSystem** -- DONE (`4ba2cd9`,
      survey ack). The 2 sites at `filesystems.py:1372 + 1431`
      are correctly guarded defaults (open_file fires only with
      a real disk path; save falls back to external when
      location is unset). No source patch shipped; the test
      file documents the conclusion with 3 regression guards.
    * **T-NEW-160b/12 / NchantdOfficeMatrix +
      NchantdOfficeCellBorderFormats** -- DONE (`2347a53`,
      survey ack). Sites at `matricies.py:171 + 1860` are
      either commented-out (cell-border utility pane) or
      properly guarded (`open_file` early-return).

  No two formats moved forward in parallel. The umbrella's
  full sweep of 13 widget classes is closed. Remaining work
  is in **future cards** (e.g. NchantdImage save-seam,
  NchantdChart populate_data streaming, populate_data vs
  populate_document design language per operator guidance):
  these are separate T-NEW numbers, not umbrella children.

### Closed / demoted by operator clarification

- **T-NEW-119 -- CLOSED.** Journal retention, timestamp handling, and
  full-text storage are working. Do not modify those paths.
- **NchantdChart config-pane segfault -- FIXED** by `899962c`.
- **T-NEW-023 Script external reload whitespace -- FIXED/pinned** by
  existing reload tests. It is distinct from T-NEW-148 save-to-disk.

### In-code marker audit

The 2026-08-18 PUSH-to-0.0.3 sweep found **91 PUSH-to-0.0.3 markers across
22 files**. They cluster into five themes; six new cards (T-NEW-161 →
T-NEW-166) cover the deferred work, and T-NEW-160 already books the
next umbrella child (Image external save). The markers themselves are
left in place — they document the deferred scope at the call site so
the next implementer doesn't re-discover the contract.

**Theme summary (91 markers / 22 files):**

| Theme | Markers | New card |
|---|---:|---|
| `set_location("external")` hardcode + commented `populate_data`/`connect_to_file` blocks — internal-blob seam missing on 13 widgets | 14 | folded into T-NEW-144b umbrella (T-NEW-160 next) |
| Commented-out `init_drawer_*` slots (form_control / source_inspection / quickstart / sources / etc.) across 11 widgets | 14 | T-NEW-161 (drawer surface for remaining widgets) |
| Browser `cmd_scan_source` / `get_profiles` / `add_profile` / `@feature_restrict` commented paid-feature gate | 5 | T-NEW-162 (browser profile + paid-feature surface) |
| `get_node_name` / `get_tab_name` / `get_urls` / `import_filetree` / `import_sessions` / `_import_nchantdoffice_*` no-op stubs | 7 | T-NEW-163 (models.py no-op stubs) |
| One-off deferrals: `cmd_save_instance` mirror pop-dialog, `cmd_take_snapshot`/`cmd_create_dataset`/`cmd_export_document`/`cmd_import_file`, `launch_note`, `on_window_move`, `switch_to_account_tab`, `open_cloud`, journal layout cfg block, settings long-method marker, document_type "note" default, content_version archive policy | 12 | T-NEW-164 (misc PUSH-to-0.0.3 deferred items) |
| `init_drawer_thumbnail` — actual shippable enhancement (not just a comment) | 1 | T-NEW-165 (Matrix cell-content thumbnail preview) |
| T-NEW-013 cipher wiring | 4 | T-NEW-013 (already tracked) |

The audit prose replaces the prior "23 TODO-family hits" line which was
stale against the 2026-08-18 sweep. **Marker count source:**
`grep -rn '# PUSH.*0\.0\.3' nchantdoffice/` over 22 source files (excludes
tests). File list (markers per file): analytics.py (3), atnrg/browsers.py (10),
atnrg/contacts.py (4), atnrg/prompts.py (6), catalogs.py (1),
config/settings.py (2), config/source_config.py (2), controls/toolboxes.py (2),
documents.py (3), journal.py (1), managers/calendars.py (3),
managers/filesystems.py (3), media/forms.py (4), media/images.py (4),
media/pdfs.py (3), media/scripts.py (4), media/sketches.py (2),
models.py (8), panes/documents.py (7), widgets.py (1),
workbooks/matricies.py (3), workbooks/notebooks.py (2).

### Historical live-open section (superseded)

The material below is retained for audit history. Its old priority labels
are not current.

These are the items still requiring work, in priority order.

### Pinned (per user direction — requires non-testable env)

- [ ] **NchantdChart segmentation fault.** Held per user instruction
  (2026-07-28). Reproduction requires a parent-app Qt harness; the live
  bug cannot be reproduced in the sasquatch headless env.
  **2026-08-17 update:** the chart-config action-button / border-style
  builder sites (`panes/charts.py:186/214`) that were historically
  blamed on T-NEW-029 drag-init gating are now identified as
  `addWidget(None)` segfaults (PySide6 segfault on implicit `None`
  return from the builder stubs); **fixed by `899962c`** with the
  `_build_chart_action_button_group` / `_build_border_style_editor`
  real QWidget returners + `is not None` gates. The pin remains
  open for the broader live-app crash that originally motivated
  it; the chart-config-pane half is resolved.
- [x] **T-NEW-023 — NchantdScript reload whitespace lost on reopen**
  (Sprint 9 commits `1a7aa05` / `5ae6a32` / `99bb286`; pinned for
  full validation per user direction 2026-07-29). Per user:
  "reload should be opening the file on disk again". Initial
  open renders correctly (markdown/python/etc.) and the
  reload-from-disk contract is implemented in
  `_load_external_file` + the production
  `populate_document` flow (skip DB dispatch when file_path
  loads from disk). Pin: `tests/test_script_html_envelope.py`
  (4 tests encoding the contract). The
  Qt-parent-subprocess harness for full live-app validation
  was deferred (per user direction in `f0cf4aa`) but the
  contract is now pinned by tests; the open pin here
  records the deferred-harness piece only.
- [x] **T-NEW-024 followup — doc_media.syntax not updated on file-open** (Sprint 17, 2026-07-29). The `doc_media` row carried the `"html"` default written at tab-creation time; the in-memory `document.syntax` was updated correctly by `_apply_extension_syntax` but the DB row was never touched, so the next reopen read `syntax="html"` from the DB and the dispatch fell through to `setPlainText`. Fixed: `model.update_doc_media_syntax(did, syntax)` runs `UPDATE doc_media SET syntax = ? WHERE did = ?` via the existing `store.update_records()` path. Called from `scripts.py::open_file` after `_apply_extension_syntax` and from `documents.py::save` on every save. Regression test: `tests/test_script_doc_media_syntax_update.py` (3 AST checks: model helper exists with `syntax` + `did` + `UPDATE`, `scripts.py::open_file` triggers the update, `documents.py::save` triggers the update).

### Deferred / non-blocking

- [x] **Ad tab button redirect to Settings / Account tab** —
  currently launches a browser via QService; the user wants it
  to route into an existing tab under the Settings node pointing
  at nchantdoffice.com. UX change, no crash.
  **Closed in Sprint 27** (commits 9dd19c3 + dc0cfcf + TBD): the right-side
  ``NchantdOfficeAdTab._on_remove_ads_clicked`` navigates the
  left-pane treeview via
  ``tree_wrapper.set_current_node(...)`` (the nchantrs treeview
  wrapper method, ``nchantrs/views/treeviews.py`` line 266),
  which is the canonical call that propagates selection to
  ``model.current_node`` and calls ``updateTabs('center')``. The
  Sprint 24 implementation called
  ``switch_to_account_tab`` which silently no-op'd because the
  user's account_tab / settings_tab attributes are not bound in
  the live app. The Sprint 25 follow-up called
  ``tree.setCurrentItem`` + ``itemSelectionChanged.emit()`` which
  only updated the QTreeWidget's selection state but did NOT
  drive navigation (the user reported "selects the Settings node
  but doesn't navigate there"). The Sprint 26 follow-up resolves the actual NchantdTreeView wrapper via
  ``pane.tree.view`` (the nchantrs views/treeviews.py wrapper,
  not the bare QTreeWidget that pane.tree returns) and calls
  actually fires ``updateTabs('center')`` and routes the
  center tabset to the existing "Nchantd Account" tab
  (the embedded browser for the nchantdoffice_com account
  chain) under the Settings node.
- [ ] **Ad tab size control** — right-side tabs are slim 360×900
  and would need to go into the center tabset if a larger ad is
  required. UX change, no crash.
- [x] **Tab Edit Pane doesn't persist the new name** — `cmd_set_tab_name`
  updates the label but doesn't write back to the DB. Regression.
  **Fixed in Sprint 21** (commit TBD): now also runs
  `store.update_record({"table": {"doc_tab": {"data": {"name_txt":
  <new_name>}}}}, "tid_txt", tab.tid)` so the rename persists across
  reloads. Regression test:
  `tests/test_tab_node_name_persistence.py::test_cmd_set_tab_name_writes_to_db`.
- [x] **Node Edit Pane doesn't persist the new name** — same regression.
  **Fixed in Sprint 21** (same commit): now also runs
  `store.update_record({"table": {"doc_tree_node": {"data":
  {"name_txt": <new_name>}}}}, "nid_txt", node.nid)` so the rename
  persists. Regression test:
  `tests/test_tab_node_name_persistence.py::test_cmd_set_node_name_writes_to_db`.
- [x] **Name-entry dialog for new nodes / tabs** — config flag for
  "prompt vs auto-generate", with dialog widget (3 separate TODOs).
  **Implemented in Sprint 23** (commit TBD): two new settings
  flags ``prompt_for_new_node_name`` and
  ``prompt_for_new_tab_name`` in
  `cmd_on_change_prompt_for_new_node_name` and
  `cmd_on_change_prompt_for_new_tab_name` (settings.py). When
  enabled, the toolbars' `add_node` and `add_note` paths and the
  panes/new `add_tab` path run
  ``QtWidgets.QInputDialog.getText`` to capture a user-supplied
  name. When False (default), the existing auto-generation
  ``uuid()[-5:]`` / timestamp / active_item.name is used.
  Cancellation aborts the create.
- [ ] **Save-mode toolbar icons** — disk-stack icon toggles internal
  storage, cloud icon toggles cloud storage, both in
  `NchantdDocumentToolBar`.
- [ ] **NchantdSketch / NchantdCalendar default to internal** — no
  external standard-compatible file format.
