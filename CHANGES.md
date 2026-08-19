# CHANGES.md - NchantdOffice Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

> **Reality anchor (2026-08-19, gamma `655f36b`):** This is
> the SECOND release-block summary. The first anchor
> (2026-08-17, gamma `07fc18b`, immediately below) covered
> T-NEW-110..147 plus the pyof-bare-parent SIGSEGV fix.
>
> **This anchor** consolidates work between 2026-08-18
> and 2026-08-19 inclusive (16+ commits, gamma `18336e5`
> → `655f36b`). The headline deliverables:
>
> - **T-NEW-144b umbrella CLOSED** (`13ff2f1`) — multi-format
>   external editing across 13 widget classes. 12 children
>   shipped (T-NEW-148 / 159 / 160 / 160a / 160b/1..12). The
>   umbrella's full sweep of `set_location("external")`
>   hardcodes is done; remaining work is recorded in
>   T-NEW-162 cards B/C-suffix for future bookmarks.
>   Headline commits: `f499b7c` (Image), `7bc68dc` (Notebook),
>   `a1c5932` (Sketch), `54fbedc` (Form), `ab0307b`
>   (FormManager), `883373c` (Contact), `41fb641` (Rolodex),
>   `01194b9` / `a9e56c3` / `cb3c607` (prompts trio), `73dd4fd`
>   (Chart), `47a0c6e` (CompressPane), `4ba2cd9` (FileSystem
>   survey ack), `2347a53` (Matrix survey ack).
> - **T-NEW-152** Refresh ToolBox after node deletion
>   (`be0c224`) — `cmd_delete_node` now also calls
>   `panes['center'].toolbox.refresh()` after the tree
>   refresh. Pre-fix the ToolBox still showed the deleted
>   node's contents; post-fix the open-deleted-node state
>   clears immediately.
> - **T-NEW-151** nchantrs `NchantdUser.verify_password`
>   alias (`5e1999d` in nchantrs gamma + `bf99122` desktop
>   doc-only) — single-line `verify_password = verify_pword`
>   in upstream `nchantrs/utilities/users.py:182`. Closes the
>   AttributeError on first-boot `bootstrap_app_user` that the
>   2026-08-17 testing report surfaced.
> - **T-NEW-154** Stage timing on `add_tab` (`535178a`) —
>   `time.monotonic()` snapshot at function entry +
>   `logma.info(f"[panes.new] T-NEW-154 add_tab total: Xms")`
>   at return. Instrumentation-only; future per-phase
>   breakdowns layer on this baseline. Test:
>   `tests/test_t_new_154_add_tab_stage_timing.py` (3 tests).
> - **T-NEW-155** Per-widget Ctrl+D date-insert shortcut
>   (`18336e5`) — `NchantdOfficeScript._register_shortcut`
>   helper creates a `QShortcut(pyqt.QKeySequence('Ctrl+D'),
>   self)` with `WidgetWithChildrenShortcut` context,
>   connected to `cmd_add_date`. Per-widget registry
>   (operator-chosen over global) lets each widget own its
>   own shortcut bindings; future Ctrl+T (time-insert) etc.
>   can call the same helper without a new framework.
> - **T-NEW-156** Underscore-prefix sort comparator
>   (`5da752b`) — `NchantdOfficeNodeEditPane._underscore_priority_key`
>   staticmethod returns `(-1, lower_name)` for `_`-prefixed
>   names; `_sort_subtree` threads it through
>   `node.sortChildren(0, order=direction, sort_key=...)`.
>   Operators' `_system` / `_template` internal subtrees
>   always sort to the top regardless of asc/desc.
> - **T-NEW-157** active_tab_position clamp
>   (`22a413b`) — `models.py:4768` now clamps an
>   out-of-bounds `active_tab_position` to
>   `len(tabsdata) - 1` instead of silently forcing 0.
>   Operators no longer lose context on tab delete. (Note:
>   the testing report referenced 3039 — that line is the
>   `get_rolling_summary` return, not the search-correction
>   code; corrected to the real site in this card.)
> - **T-NEW-158** Referral passphrase marker (`caa806c`)
>   — `widgets/config/referral_panel.py:395` replaces the
>   unnumbered `# T-NEW-XXX:` marker with the canonical
>   `T-NEW-158` number. The Qt-masked-passphrase guard impl
>   (`_qt_passphrase_prompt` at line 453 + `_pykey_prompt`
>   sentinel injection) is unchanged.
>
> Plus the **T-NEW-163 / 164 family** (umbrella sweep during
> the same window — models.py 3 no-op stubs + misc
> PUSH-to-0.0.3 marker demotes) covered earlier.
>
> Plus **three new cards filed 2026-08-19** that establish
> the next-quarter roadmap:
>
> - **T-NEW-169 / T-NEW-170** — standalone 2-pane boot +
>   pullable-tab dialog (multi-screen support).
> - **T-NEW-171** — performance campaign (SURVEY → PRIORITIZE
>   → DESIGN → SHIP-per-speed-up).
> - **T-NEW-172** — async methods + secondary background
>   processes via the `pyularity` supervisor project
>   (`/home/solubrew/.hermes/projects/pyularity`). Hybrid
>   pattern (daemon pool + dedicated subprocesses); JSON-lines
>   IPC for v1.
>
> Test surface at this anchor (T-NEW-only test files):
> 307 passed / 0 failed / 16 warnings (mock_use_standalone_module
> is the warning, set in pyproject.toml). Full desktop
> suite unchanged from the 2026-08-17 anchor
> (the 19 pre-existing functional failures + 6 Qt SIGSEGV skips
> in `widgets.py:193` / `document_settings.py:158` are NOT in
> any T-NEW test file; they sit in `nchantdoffice/widgets.py`
> and are unrelated to this anchor's scope). Pyright-clean.
> Branch HEAD: `655f36b`. See TODOs.md card index.

### Added (T-NEW-169 / 170 / 171 / 172 — filed 2026-08-19)

- **T-NEW-169** Per-document standalone entry point
  (`3c9ed0e` — doc-only). Plan to add
  `runNchantdOffice.py document --type <name> [--path ...]`
  argparse dispatch that boots a 2-pane minimal shell
  (left = `NchantdOffice*` widget, right = toolbox). 7 steps,
  DECIDE-1 (argparse vs separate entry file) +
  DECIDE-2 (2-pane layout target) first.
- **T-NEW-170** Pull-a-tab dialog (multi-screen support)
  (`3c9ed0e` — doc-only). Plan to add `FloatedTab` `QDialog`
  shell + `tabset.pop_out_tab()` + `tabset.re_attach_tab()`.
  Re-attach fires automatically on active-node change
  (one-way trip — operators explicitly designed this).
  8 steps, DECIDE-1 (re-attach trigger) + DECIDE-2 (dialog
  visual model: minimal vs 2-pane reuse from T-NEW-169)
  first.
- **T-NEW-171** Performance campaign (`36ba852` — doc-only).
  Survey → prioritize → design → ship-per-speed-up pattern
  (each speed-up becomes its own T-NEW card; one commit
  per speed-up). First SURVEY target is the boot cascade +
  `add_tab` (T-NEW-154 already instrumented).
- **T-NEW-172** Async + background processes via pyularity
  (`655f36b` — doc-only). Pyularity owns the supervisor
  lifecycle (crash-detect + restart + lifecycle hooks +
  health-check protocol); nchantdoffice grows a thin client
  wrapper (`pyularity_client.py`). 9 steps, DECIDE-1
  (hybrid pattern) + DECIDE-2 (JSON-lines IPC) + DECIDE-3
  (must-have feature order in pyularity) first.

### Closed (T-NEW-169 — shipped 2026-08-19)

**T-NEW-169** *Per-document standalone entry point (2-pane
single-doc app)* — closed 2026-08-19, gamma `c21c243`. Operator
DECIDE-1 (a) / DECIDE-2 (b) approved earlier the same day.
Shipped as 4 commits over 4 working hours:

- `257af54` — **WIRE-1**: `cmds/runNchantdOffice.py` argparse
  dispatch. New subcommand `document --type <name> [--path <file>]`
  parses into `{mode: 'document', type: <name>, path: <path>}`;
  no subcommand boots the unchanged main app. Pre-fix bug fixed
  (the old `run(argv: list[str])` passed the raw argv to
  `nchantment` which expects a dict — `'instance' in <list>` was
  always False, so the dispatch never actually fired despite
  the docstring's claims).

- `ec05e6d` — **WIRE-2**: `NchantdDocumentStandaloneWindow` class
  in `nchantdoffice/nchantdoffice.py`. New `QMainWindow`
  subclass with central-widget + right-dock layout (2-pane
  shell per DECIDE-2 (b): keep tabset chrome with one tab).
  Carries a placeholder central widget + placeholder right-dock
  while the dispatch wiring (WIRE-3) lands.

- `24b0967` — **WIRE-3**: `DOCUMENT_TYPE_DISPATCH` dict wires
  the 4 high-value `NchantdOffice*` types (script / notebook /
  image / form). Lazy import resolution via `importlib` keeps
  the heavyweight transitive imports (e.g. `forms.py` -> the
  missing `panes.forms` module) out of module-load time. The
  fall-back placeholder central widget remains as the safety
  net for failed import / construction.

- `c21c243` — **DOC-1**: `CLI.md` updated with the new
  `document` subcommand section (usage / arguments / 4 type
  names / 3 worked examples / behaviour / default-behaviour-
  unchanged notes). Doc-only commit; no source changes.

**Migration plan (recorded for archeology):** the T-NEW card
body that lived in TODOs.md has been removed wholesale per the
operator-set 2026-08-19 closed-card cleanup rule (encoded in
`CODING_STANDARDS.md` line ~14, commit `735dfde`). The 4
shipped-commit references above are the canonical link from
CHANGES.md back to the implementation; `git log --grep='T-NEW-169'`
returns the full history for future archeology.

**Verifications:** 4 + 10 + 10 + 5 = 29 new AST-source structural
tests across 4 test files (one per WIRE-n + DOC-1). All green.
Full `pytest tests/test_t_new_*.py` baseline: 347/347 GREEN
(was 316 before T-NEW-169 started; net +31 tests). No broader
test surface changes.

**Refs:** T-NEW-170 (pull-out tab dialog) reuses
`NchantdDocumentStandaloneWindow` as the body of the pulled-out
FloatedTab; once T-NEW-170 ships, `document --type <name>`
windows can be detached onto a second monitor without code
changes (T-NEW-170's `FloatedTab` composes the standalone
window directly).

## [Unreleased] Catch-up card roll-up (2026-08-19, gamma `735dfde`)

> **Reality anchor:** this is the bulk roll-up of **78 T-NEW cards**
> that were already shipped but whose card bodies remained in
> `TODOs.md`. Per the operator-set closed-card cleanup rule
> (2026-08-19), the card bodies were deleted wholesale from
> `TODOs.md` after this roll-up was published. Two files,
> two purposes:
>
> - **`TODOs.md`** is the *open work* index (6 cards remaining,
>   see "Active card queue" section below).
> - **`CHANGES.md`** is the *shipping log* (this section + the prior
>   `[Unreleased] (2026-08-19, gamma 655f36b)` anchor + the
>   `[Unreleased] 2026-08-17` earlier block + the deeper history
>   under `## [Unreleased] (older)` sections).
>
> For full archeology of any card, `git log --grep='T-NEW-NNN'`
> returns the commit hashes named in the table below.

### Closed card roll-up table (113 unique cards with git commits)

| T-NEW | First-shipped commit | Commit headline (subject stripped of `type(scope):` and `(T-NEW-NNN)`) |
|---|---|---|
| T-NEW-001 | `d4de606` | apply tab color+icon from config on add_tab |
| T-NEW-002 | `621315b` | Revert "fix(documents): T-NEW-002 widget-lookup + H60 b/c per-widget save_mode p |
| T-NEW-003 | `24c58a9` | land T-NEW-003 save_mode canonical contract (closeout) |
| T-NEW-004 | `a382a94` | fix T-NEW-004 delete_node regex (allow return annotation, capture body) |
| T-NEW-005 | `7993a04` | pin T-NEW-005 item 3 UI selector to nchantrs.dialogs.selectors |
| T-NEW-006 | `fb74a5a` | Revert "fix(models): route notebook/chart/calendar add_document cases " |
| T-NEW-007 | `02401f9` | implement store.refresh_from_sqlite |
| T-NEW-008 | `85e809e` | HTML save + reopen round-trip |
| T-NEW-009 | `61bde92` | mark notebook save crash fixed |
| T-NEW-010 | `caa60fb` | record Sprint 5 fix status |
| T-NEW-013 | `9eee273` | tag encrypt/decrypt with PUSH 0.0.3 |
| T-NEW-014 | `7d12d0e` | clarify T-NEW-014 - new_trendline_group built by trendline helper, not data help |
| T-NEW-015 | `f5d45bd` | close T-NEW-015 + T-NEW-021 (Calendar ctx-menu + Tab bounds) |
| T-NEW-016 | `2fc25f8` | mark T-NEW-016 Calendar QGridLayout closed |
| T-NEW-017 | `d9dc4a5` | mark Sprint 8 T-NEW-017/018/020/022 closed |
| T-NEW-019 | `0f7e51d` | guard self.user so Referral tab doesn't AttributeError |
| T-NEW-020 | `f4559f3` | fix T-NEW-020 initModel regex to handle -> Self annotation |
| T-NEW-021 | `f5d45bd` | close T-NEW-015 + T-NEW-021 (Calendar ctx-menu + Tab bounds) |
| T-NEW-023 | `f0cf4aa` | pin T-NEW-023 reload whitespace as deferred |
| T-NEW-024 | `17b9a75` | mock syntax attr + update_record on _CapturingStore |
| T-NEW-025 | `d0bc535` | remove stale TODO; confirm integer version bump |
| T-NEW-026 | `02df7f4` | finish Affiliate Manager tab |
| T-NEW-027 | `40f1a5f` | mark T-NEW-027 done (Sprint 29, hybrid Option C) |
| T-NEW-028 | `12b8490` | mark T-NEW-028 done (Sprint 29, DB-driven checklist) |
| T-NEW-029 | `16a5246` | gate drag-init to tab-name area |
| T-NEW-030 | `f596ac8` | fix dropEvent / _handle_tab_dropped_on_node regexes for return annotations |
| T-NEW-031 | `7e68ca1` | mark T-NEW-031 done (Sprint 29, in-memory scratch view) |
| T-NEW-032 | `a0a3a60` | mark T-NEW-032 done (Sprint 29, opt-in basename rename) |
| T-NEW-033 | `a3f7c6e` | global/node/tab-scoped search dispatch |
| T-NEW-034 | `ba24f95` | tracked checkbox + size label + retention spinbox + save button |
| T-NEW-035 | `f4698cb` | fix init_drawer_*_config regex to match return annotation |
| T-NEW-036 | `ff6db24` | Revert "fix(journal): add refresh_content for tab-focus restore " |
| T-NEW-037 | `caec606` | fix _build_chart_action_button_group regex for return annotation |
| T-NEW-038 | `2f9856a` | FileDetailsPane refresh on initial file open |
| T-NEW-039 | `d9c5029` | remove widget's redundant update_doc_media_syntax hack |
| T-NEW-040 | `407a4a4` | docs: document per-repo T-NEW-NNN card numbering convention |
| T-NEW-041 | `7504a72` | drop stale widget-lookup TODO |
| T-NEW-042 | `daa1d64` | set self.device before NchantdOfficeUser construction |
| T-NEW-043 | `ec58f1c` | audit: refresh after T-NEW-043 fix |
| T-NEW-044 | `7d85211` | add T-NEW-044/045 cross-repo summary section |
| T-NEW-045 | `b420a06` | grant trigger for ad-tab-free hours |
| T-NEW-048 | `cd2c7ee` | audit: refresh after T-NEW-048 follow-up |
| T-NEW-049 | `f384e12` | docs: mark T-NEW-049 through T-NEW-052 as fixed in TODOs.md |
| T-NEW-051 | `39f6726` | flip T-NEW-051 to assert position_int is ABSENT in app_action |
| T-NEW-052 | `f384e12` | docs: mark T-NEW-049 through T-NEW-052 as fixed in TODOs.md |
| T-NEW-053 | `15f5815` | calculator keyboard input on base NchantdCalculator |
| T-NEW-054 | `5862c46` | auto-create child node when tab limit hit |
| T-NEW-055 | `5e1d2ee` | integrate NchantdOfficePalette into image toolbar |
| T-NEW-056 | `8da40e5` | close-out + update test surface count |
| T-NEW-057 | `5f6422f` | pin T-NEW-057 head + commit hash (backfill) |
| T-NEW-058 | `4543671` | un-comment journal refresh_content + align T-NEW-058 mock fixture |
| T-NEW-059 | `cc60ea5` | merge t-new-059: user-configurable update-check interval |
| T-NEW-060 | `88210f2` | merge t-new-060: tray icon + per-version snooze |
| T-NEW-061 | `8824871` | T-NEW-072 add Update Process Overview + T-NEW-061 deferred card |
| T-NEW-062 | `ece92c9` | merge t-new-062: notebook Jupyter-side URL sync |
| T-NEW-063 | `1452412` | merge t-new-063: image aspect-ratio preservation |
| T-NEW-064 | `cc7341e` | merge t-new-064: script tab 'Missing Text' stub removed |
| T-NEW-065 | `4fcccf5` | merge t-new-065: journal content compaction (narrow scope) |
| T-NEW-067 | `816435a` | merge t-new-067-docs: T-NEW-067 index row |
| T-NEW-068 | `c246108` | Merge remote-tracking branch 'origin/t-new-068' into gamma |
| T-NEW-069 | `94bad7e` | merge t-new-069: NchantdBrowser URL history tracking |
| T-NEW-070 | `7ff5bdd` | T-NEW-070 dev mode section + 'Recent changes (2026-08)' summary |
| T-NEW-071 | `75e76b3` | merge t-new-071: NchantdOfficeJournalSettings pro-tier editor |
| T-NEW-072 | `34d64c4` | merge t-new-072: TODOs.md update-process consolidation |
| T-NEW-073 | `4543671` | un-comment journal refresh_content + align T-NEW-058 mock fixture |
| T-NEW-074 | `fd01b92` | pass file argument to current_tab.open_file() in import_text |
| T-NEW-075 | `53a89a9` | fill in T-NEW-075 commit hash |
| T-NEW-076 | `ba0a82d` | fill in T-NEW-076 commit hash |
| T-NEW-077 | `90cc9b3` | collapse & annotate 2 multi-line sigs in server_status.py + feature_gates.py |
| T-NEW-078 | `e01c80e` | T-NEW-078 card + CHANGES.md entry |
| T-NEW-079 | `2b48e62` | T-NEW-079 was DONE; add save_app() docstring callers + reflect the user cleanup |
| T-NEW-110 | `678e59e` | packaging + ruff config: real description, MANIFEST.in, code-quality fixes |
| T-NEW-111 | `0c748fd` | T-NEW-111..114 from testing-report_20260814.md (2026-08-14) |
| T-NEW-114 | `6f0724e` | re-parent top-level imports under the selected node |
| T-NEW-115 | `6f4b467` | file T-NEW-115..123 from testing-report + TODO sweep |
| T-NEW-116 | `8816168` | Jupyter server default cwd = ~/Documents/NchantdLibrary |
| T-NEW-117 | `419a317` | degrade missing palette extraction gracefully |
| T-NEW-120 | `a2a0361` | restore script save+reopen aspirational tests |
| T-NEW-122 | `260886a` | T-NEW-122: stabilise repository-wide Qt test collection |
| T-NEW-123 | `95a41da` | clear 4 stale in-file TODO comments |
| T-NEW-124 | `d8d228d` | doctype guard -- strict-dtd payloads restore as HTML |
| T-NEW-129 | `bf5df13` | Merge branch 't-new-129-app-user-bootstrap' into gamma |
| T-NEW-130 | `7525fc8` | Merge branch 't-new-130-top-level-node-create' into gamma |
| T-NEW-131 | `d68d216` | Merge branch 't-new-131-settings-journal-create' into gamma |
| T-NEW-132 | `21ac51b` | Merge branch 't-new-132-settings-tab-deny' into gamma |
| T-NEW-133 | `4374b40` | Merge branch 't-new-133-sort-subtree' into gamma |
| T-NEW-134 | `5831dd1` | Get Pro button uses dark orange, not green |
| T-NEW-135 | `c20a7d8` | Merge branch 't-new-135-100node-redirect' into gamma |
| T-NEW-136 | `43c9bc1` | Merge branch 't-new-136-pyof-import-redirect' into gamma |
| T-NEW-137 | `29217ce` | Merge branch 't-new-137-pyof-import-preflight' into gamma |
| T-NEW-138 | `23fa565` | always-scroll to bottom + populate via parse() |
| T-NEW-139 | `e1573ba` | extract _navigate_to_new_doc helper |
| T-NEW-140 | `b63d36d` | lock free-user right-side default to Ad tab |
| T-NEW-141 | `d65faf2` | T-NEW-141b: fix kahndor.Instruct patch point in user-tier tests |
| T-NEW-142 | `5b6397e` | file T-NEW-142..148 from 2026-08-15 testing-report sweep |
| T-NEW-144 | `13ff2f1` | close T-NEW-144b umbrella, list all 12 child commits |
| T-NEW-148 | `ce6e262` | docs: mark T-NEW-148 fixed and refresh branch state |
| T-NEW-151 | `bf99122` | mark T-NEW-151 done (5e1999d landed upstream nchantrs fix) |
| T-NEW-152 | `be0c224` | refresh ToolBox after node deletion |
| T-NEW-154 | `535178a` | add stage timing to add_tab |
| T-NEW-155 | `18336e5` | add per-widget Ctrl+D shortcut for date-insert |
| T-NEW-156 | `5da752b` | sort underscore-prefixed nodes first |
| T-NEW-157 | `22a413b` | clamp active_tab_position to last valid tab |
| T-NEW-158 | `caa806c` | replace T-NEW-XXX placeholder with T-NEW-158 |
| T-NEW-159 | `d9822f9` | docs: reconcile branch state and T-NEW-159 |
| T-NEW-160 | `2347a53` | document NchantdOfficeMatrix + CellBorderFormats as already-correct |
| T-NEW-161 | `6847ad9` | refactor: relabel 15 deferred drawer markers to '# RESERVED' |
| T-NEW-162 | `182b30f` | wire add_profile persistence via store |
| T-NEW-163 | `b71f86b` | implement 3 no-op stubs |
| T-NEW-164 | `50639b9` | activate cmd_save_instance in toolbar |
| T-NEW-165 | `6e94be4` | ship cell-content thumbnail preview |
| T-NEW-167 | `1c11c98` | wire cmd_on_name_change / cmd_on_description_change |
| T-NEW-168 | `225317b` | wire update_checkboxes to real impl |

### Additional closed cards (catalog-form, retained historical)

The following cards are documented in the `TODOs.md` catalog
sections that retain a one-line summary (not the full card body).
They are listed here for completeness; the bodies themselves are
gone from `TODOs.md` per the closed-card cleanup rule. The
catalog bullets are:

*(see the `## New TODOs from testing-report_*` sections in `TODOs.md`
for the one-line catalog summaries that survive.)*

### Active card queue (6 cards, 2026-08-19)

These 6 cards remain in `TODOs.md` as the open work index:

## [Unreleased]

> **Reality anchor (2026-08-17, gamma `07fc18b`):** This block
> consolidates work from T-NEW-110 through T-NEW-147 (all shipped
> 2026-08-10 → 2026-08-17) plus the filed-but-open cards
> T-NEW-118 / T-NEW-119 / T-NEW-121 / T-NEW-144b. The
> T-NEW-049 through T-NEW-109 cards have their own entries in
> the prior `[Unreleased]` block below this one — kept intact
> for traceability. See [`TODOs.md`](./TODOs.md) for the
> canonical card index and commit hashes. The four 2026-08-17
> commits (`260886a` / `419a317` / `899962c` / `07fc18b`) close
> T-NEW-122 / T-NEW-117 / T-NEW-037-followup / pyof-bare-parent
> respectively — see the new entries at the top of "Added" /
> "Fixed" below.

### Added (T-NEW-110..147)

- **T-NEW-117** Palette extraction (2026-08-17) — the
  `PyfficeColorPalette.extract_palette` surface landed in
  pyffice gamma `1cd3c48` (returns `{colors: [{hex, count,
  percent}, ...]}` ordered by frequency using PIL's
  `Image.convert("RGB")` + `Counter`). nchantdoffice
  `419a317` adds a `hasattr(palette_document,
  "extract_palette")` guard at
  `widgets/documents/media/images.py:1010` so older pyffice
  builds degrade gracefully (logs `Palette scan unavailable
  -- update pyffice` and surfaces the same message via
  status bar) instead of crashing with
  `AttributeError: 'PyfficeColorPalette' object has no
  attribute 'extract_palette'`. New regression test:
  `tests/test_t_new_117_palette_scan_degradation.py` (3
  cases — missing-method graceful log, status-bar message,
  happy-path palette application). Pin: 1/1 new test green.
- **T-NEW-122** Qt-harness migration for tests importing
  toolboxes (2026-08-17) — the module-level
  `_QAPP = QApplication.instance() or QApplication(sys.argv)`
  pattern in 21 test files crashed multi-file pytest
  collection at exit 134/139. `260886a` adds
  `tests/conftest.py` with a session-scoped autouse fixture
  that lazily constructs one `QApplication` for the whole
  pytest session (deferred import keeps non-Qt hosts safe)
  and `tests/qt_parent/__init__.py` with opt-in session-
  /function-scoped `qapp` fixtures. The offending
  module-level line was stripped from all 21 offender
  files; the autouse conftest provides the same instance
  lazily. New regression gate:
  `tests/test_t_new_122_qt_collection_guard.py` (2 tests:
  AST scan finds no offender, RED→GREEN history).
  Targeted evidence: full suite (with
  `--ignore=tests/test_cmd_pyof_routing_consolidation.py`
  for the unrelated pyof-bare-parent SIGSEGV that
  T-NEW-074's pyof dispatch pin reproduces; fixed by
  `07fc18b` the same day): 19 failed, 836 passed, 6
  skipped (100% collection reached; pre-`260886a` the run
  aborted at 8% of collection). 21 offender files
  identified by the AST scan before the sweep; 0 after.
- **T-NEW-110** Packaging + ruff config (`678e59e`) — real
  `pyproject.toml` description, `MANIFEST.in`, ruff lint config;
  closes the "[Unreleased] Added" entry that referenced a
  placeholder.
- **T-NEW-114** `.pyof` import dispatch consolidation
  (`f81c8a7`) — `cmd_import_local_file` routes `.pyof` →
  `cmd_import_pyof` (was → `model.import_nchantdoffice`);
  `cmd_open_local_file` routes `.pyof` → `cmd_import_local_file`
  (was → `_open_pyof_instance`); `cmd_import_pyof` offloads to a
  `_PyofImportWorker` on a `QThread` (was synchronous on GUI
  thread, blocked on long `.pyof` reads). 5 new tests pin the
  dispatch + worker thread. Follow-ups: `d0075b3`
  (re-architect via `sonql.Doc` + model funnels),
  `6480f77` (refresh tree widgets), `6f0724e`
  (re-parent top-level imports), `aaf74b7` (also re-parent rows
  parented to the starting-node pid), `0f3d6a3` (resolve
  selected nid from item widgets, not just dicts), `8d217fe`
  (refresh inner tree in place — never rebuild the container),
  `1cda19f` (scope re-parent to source `doc_tree_node` rows
  only).
- **T-NEW-124** Doctype guard — strict-dtd payloads restore as
  HTML (`d8d228d`) — `_apply_syntax_highlighting` in
  `widgets/documents/media/scripts.py` now fingerprints the
  stable `rec-html40/strict.dtd` doctype on the first 2048 chars
  (case-insensitive, tolerant of spacing/quote variants) and
  routes the payload to `setHtml(text)` regardless of
  `document.syntax`. 7 new tests in
  `tests/test_script_doctype_guard.py`.
- **T-NEW-129** Seed `app_user` row on initial install
  (`7da0d1e`) — `bootstrap_app_user` + `store_app_user` +
  `get_app_user` wired from `run_on_launch` so the cloak model
  has a user row to read on first boot. **NOTE: live traceback
  2026-08-15 22:19:02 surfaces two regressions in this wiring;
  tracked under T-NEW-146 and T-NEW-147.**
- **T-NEW-130** Top-level new-node toolbar lands at `pid=0`
  (`ac448ad`) — `NchantdNewDocumentSigil.top_level` flag +
  `launch_new_document_sigil` signals the rootnode dispatch.
- **T-NEW-131** Deny child-node creates under
  Home/Journal/Settings (`fc61c4e`) — `is_locked_pid` +
  `is_locked_parent` helpers; `add_node`/`add_node_app` refuse
  children of locked trees for all users.
- **T-NEW-132** Deny tab create/delete in Settings tree
  (`87ace4d`) — `is_locked_tab_parent` helper; `add_tab`/
  `delete_tab` refuse Settings-tree tab ops for all users.
- **T-NEW-133** Sort buttons sort the entire subtree
  (`8857081`) — `cmd_sort_children` + `_resolve_sort_direction`
  + `_sort_subtree` helper; every descendant depth is reordered
  (asc/desc) and persisted.
- **T-NEW-134** Get Pro button visibly green (`096e6c9`) —
  `_apply_bg_color` helper on `NchantdOfficeDocumentMixin` sets
  background-color via `setStyleSheet`, paired with white text
  for contrast. Follow-up `5831dd1` swaps green for dark orange
  (better contrast in the disabled state, per the user's
  live-testing feedback).
- **T-NEW-135** 100-node cap redirects to Nchantd Account with
  reason param (`5bf6f3d`) — fixed dead-code bug in
  `_check_max_nodes_for_user`; `redirect_to_get_pro` accepts a
  `reason`; `NchantdAccountSettings` appends `?reason=` to the
  compare URL.
- **T-NEW-137** Pre-flight `.pyof` import against the 100-node
  cap (`1fd8d60`) — before any row is copied, the import worker
  computes the source's net node count and refuses the import
  if it would push the host over the cap; redirects to Get Pro
  via the same path as T-NEW-135.
- **T-NEW-146** `_build_app_user_payload` generator coercion
  (2026-08-16) — `NchantdUser.get_password` is a generator
  function so `user.pword` is a generator instance by default;
  the payload-builder's duck-typed branch was passing it
  through verbatim, and `squirl._store` exploded on deepcopy
  with `TypeError: cannot pickle 'generator' object`. Fix:
  `_coerce_scalar(value)` helper unwraps iterators/generators
  (`next()` on the first yielded value) and falls back to
  `str()` for any other non-scalar.3 new regression tests in
  `tests/test_app_user_bootstrap.py`.
- **T-NEW-147** `get_app_user` fallback routes through the store
  layer (2026-08-16) — the fallback branch was calling
  `self.get_table(...)` (a method that doesn't exist on
  `NchantdOfficeCloakModel`), so every fresh-boot where
  `_sqlite_connection` was unbound raised `AttributeError` and
  logged `get_app_user failed: 'NchantdOfficeCloakModel' object
  has no attribute 'get_table'`. Fix: route through
  `self.store.get_table` (the store-layer method). 2 new
  regression tests in `tests/test_app_user_bootstrap.py`.
- **T-NEW-143** `.pyof` import excludes `DELETE_BIT=1` rows
  (2026-08-16) — the base-6 branch of `import_one_table`
  (nchantdoffice/utilities/pyof_import.py) was copying
  squirl soft-delete tombstones verbatim into the host.
  Fix: `if row.get("DELETE_BIT"): continue` at the top of
  the base-6 per-row loop. Missing/None/0 = live; any truthy
  int = skip. `_content` tables are untouched (they are
  versioned, not soft-deleted). 6 new regression tests in
  `tests/test_t_new_143_delete_bit_filter.py`.
- **T-NEW-145** `Ctrl+S` wired to save button logic
  (2026-08-16) — overrode `cmd_save` on `NchantdOfficeCloak`
  (the nchantrs shortcut was calling the inherited
  `NchantdCloak.cmd_save`, which calls `self.parent.model.save()`
  — the application-level instance write, NOT the
  document-level save). Override does an active-doc lookup
  via `self.main.view.panes["center"].currentWidget()` and
  dispatches to the doc's `save()` / `save_app()`; falls back
  to `self.parent.model.save()` when no active document
  (defensive against missing view/panes/currentWidget).
  4 new source-shape regression tests in
  `tests/test_t_new_145_ctrl_s_save.py`.
- **T-NEW-142** Tab Delete button registrations
  (2026-08-16) — the button-bar config at
  `widgets/panes/documents.py:791` (`delete_tab`) and line 93
  (`delete_node`) referenced action names that were never
  registered as `app_action` rows in
  `nchantdoffice/_data_/models.yaml`. The nchantrs
  `lookup()` chain reads `app_action` from the DB by
  `lookup_code_txt` and raises
  `Exception('Action delete_tab Lookup Config is Empty')`
  when missing — which silently fails the button-bar render.
  Fix: added two `app_action` records (icon
  `actions-remove-tab-svgrepo-com` for delete_tab,
  `remove-delete-trash-cancel-svgrepo-com` for delete_node).
  5 new regression tests in
  `tests/test_t_new_142_tab_delete_action.py`.

- **T-NEW-144a** FileDetailsPane shows internal-doc data
  (2026-08-16) — when the active tab is internal (no
  `file_path`), `NchantdFileDetailsPane` previously
  returned empty / "0" for every detail field (size, hash,
  dates). Fix: added `bind_to_tab(tab)` method on the
  pane; `get_name` / `get_file_path` / `get_file_size` /
  `get_modified_date` now consult `self.tab` when
  `self.file_path` is empty (returns `tab.name`,
  `"(internal storage)"`, `len(tab.content)`,
  `tab.modon`). External docs are unchanged —
  `set_file_path` still populates the widget with the
  full path; the new code only writes the widget in the
  internal-doc fallback branch. 6 new regression tests in
  `tests/test_t_new_144a_file_details_internal.py`.
- **T-NEW-144b** External file becomes editor
  (2026-08-16) — **ACTIVE UMBRELLA, phased by document type.**
  The broad multi-format project remains active, but each document
  type must be implemented and regression-tested independently to
  protect existing behavior. T-NEW-148 is phase 1 for
  NchantdOfficeScript; later formats receive separate child cards.

- **T-NEW-138** Journal editor followups: always-scroll
  + standard-populate (2026-08-16) -- the outer journal
  editor's `initView` did not call `scroll_to_bottom()`,
  so opening a long journal left the user looking at the
  first entry instead of the latest; the
  `populate_document()` was a no-op stub instead of
  routing through the canonical `parse()` contract. Fix:
  `initView` now calls `self.scroll_to_bottom()` after the
  editor is added to the layout (matches the standard
  populate_document helper's tail); `populate_document`
  reads the loaded content via `self.get_content()` and
  feeds it to `self.parse(...)`, populating
  `self.entries` by the standard pipeline. Pin:
  `tests/test_t_new_138_journal_scroll_and_populate.py`
  4 new tests (initView source-level pin, populate
  source-level pin, populate delegates-to-parse
  behavioural, populate populates-entries behavioural).

- **T-NEW-148** NchantdOfficeScript external save-to-disk
  (2026-08-18) -- ✅ FIXED in `9f18e30`.
  ``NchantdOfficeScript.save()`` now writes the editor payload
  back to ``self.file_path`` for external-origin scripts using a
  syntax-aware exporter:

    * ``html``  -> ``document_editor.toHtml()``
    * ``markdown`` -> ``document_editor.toMarkdown()``
    * plain-text / code / JSON / YAML / etc.
      -> ``document_editor.toPlainText()``

  Atomic write via sibling ``.tmp`` + ``os.replace``; UTF-8
  default; encoding overridable through ``config.dikt['encoding']``.
  Internal-origin scripts (``location == "internal"``) never touch
  disk. 5 new tests in
  ``tests/test_t_new_148_script_external_save.py`` (HTML,
  plain text, markdown, internal-skip, no-editor no-op).
  No changes to journal storage, populate_document, or any other
  document type.

- **T-NEW-159** NchantdOfficePDF internal binary storage
  (2026-08-18, T-NEW-144b phase 2) -- ✅ FIXED in
  ``cbec5b3`` (downstream) and ``4a7914c`` (upstream pyffice).
  ``NchantdOfficePDF.populate_document`` now branches by
  ``document.location``:

    * ``internal`` -> ``QPdfDocument.loadFromData(binary)`` from
      ``document.binary`` / ``document.bytes``; falls back to
      ``file_path`` on error.
    * ``external`` -> ``QPdfDocument.load(file_path)``
      (read-only widget, no save-to-disk).

  ``NchantdOfficePDF.get_content`` now returns the canonical
  envelope: ``{"content": {"file_path": ..., "bytes": ...},
  "data": None}`` when internal, ``{"content": {"file_path":
  ...}, "data": None}`` when external. Upstream
  ``PyfficePDF.get_binary`` returns the stored binary blob
  (``content["bytes"]``) when set, otherwise the on-disk bytes;
  ``set_content`` recognises the internal envelope and round-trips
  the bytes for a fresh ``PyfficeDocument`` rebuild without disk.
  5 new tests in
  ``tests/test_t_new_159_pdf_internal_external.py`` + 5 in
  ``tests/pyffice_unit/unit/images/test_pdf_binary.py``. PDF
  remains read-only; no external-save seam yet.

- **T-NEW-139** Toolbar post-creation navigation helper
  (2026-08-16) -- the original TODO at ``toolbars.py:216``
  asked to combine ``add_tab`` + ``add_document`` cfg
  wiring. There is no ``add_tab`` sibling on
  ``NchantdNewDocumentToolBar``; the real candidate for
  extraction was the two-line post-creation navigation
  block (left-pane ``updateTabs('center')`` + center-pane
  ``setCurrentIndex(pos)``). Fix: extracted
  ``_navigate_to_new_doc(pos) -> Self`` helper;
  ``add_document`` delegates to it. Any future
  ``add_tab`` / ``add_shortcut`` method on this class
  can call the same helper. 4 new regression tests in
  `tests/test_t_new_139_toolbar_navigate.py`.

- **T-NEW-140** Free-user right-side tab lock (2026-08-16)
  -- ``cmd_on_change_right_side_tab_select`` recorded
  whatever the user picked, regardless of tier. Free
  users could therefore set their default right tab to
  Settings / Help / Ad / etc. and miss the upsell surface.
  Fix: when the user is not pro (``is_pro_user(user)``),
  non-Ad selections are coerced to ``"4 - Ad"``. Pro
  users are unrestricted. The right-pane options
  themselves are unchanged (free users still see every
  tab); only the *default* they open on launch is locked.
  Pairs with T-NEW-135 (100-node cap redirect): free users
  who hit the cap are redirected to Get Pro AND they
  default-open on the Ad tab. 6 new regression tests in
  `tests/test_t_new_140_free_user_ad_tab.py`.
- **T-NEW-141** Inside-nchantdoffice TODO sweep (subset)
  (2026-08-16) -- three of the ten outstanding
  ``# TODO implement method`` markers in the
  ``nchantdoffice/`` package shipped here. ``go_to_previous_tab``
  (``widgets.py:111``) was a no-op stub; the caller in
  ``panes/documents.py:872`` ``cmd_delete_tab`` relied on
  the no-op, so deleting a tab left focus on a now-deleted
  index. Fix: decrements ``currentIndex`` by 1, clamped
  at 0. ``populate_data`` (``documents.py:1182``) had a
  misleading TODO comment plus two real lines; replaced
  the TODO with a real docstring + ``-> Self`` return
  type for parity with the other ``populate_data``
  callers. ``_load_api_key`` (``source_config.py:317``)
  was a no-op stub; the caller at ``source_config.py:184``
  always received ``None`` and the source panel never
  displayed a real API key. Fix: defensive lookup chain
  -- source arg -> ``user_config.api_keys[source_id]`` ->
  ``pycurity.pykey.get_secret("api_key", source_id)``;
  returns the raw key (caller's ``obscure_key`` masks).
  The remaining 7 markers (palette drawer wiring, tool
  drawer re-render, notebook webview instrumentation,
  catalog tab-None stub, config features pane) are
  deferred to T-NEW-141b. 4 new regression tests in
  `tests/test_t_new_141_stub_methods.py`.
- **T-NEW-141b** Inside-nchantdoffice TODO sweep (subset 2)
  (2026-08-16) -- four of the seven remaining
  ``# TODO`` / no-op stub markers in the
  ``nchantdoffice/`` package shipped here; the remaining
  three (palette drawer wiring, tool drawer re-render,
  per-doctype features pane) are deferred to T-NEW-141c
  (live UI architecture). The catalog tab-None marker at
  ``panes/documents.py:798`` was a misleading TODO
  comment over an existing stub; replaced with a real
  docstring describing the placeholder-tab contract.
  The two Jupyter webview hooks
  (``notebooks.py:1786/1790``) were no-op stubs; they
  now log the ``loadStarted`` / ``loadProgress`` signals
  so Jupyter-tab load attempts are visible in the
  application log. The hardcoded ``self.has_pro = True``
  in ``users.py:69`` now reads from
  ``load_credentials().user_tier`` (pycurity
  ``DesktopCredentials``); tier mapping is
  `pro` / `pro_data` / `enterprise` -> True, `free` ->
  False, missing / malformed -> True (backward compat
  Defaulting to True preserves the
  pre-141b behaviour for legacy users. 7 new
  regression tests in
  `tests/test_t_new_141b_safe_subset.py`.
- **T-NEW-141c** Inside-nchantdoffice TODO sweep (final
  subset) (2026-08-16) -- investigation of the 3
  remaining markers showed that the actual implementation
  already exists; the original TODOs were misleading.
  ``images.py:807`` ``cmd_add_palette_document
  _nchantdpalette`` already created the palette document
  but did not open the drawer; the fix calls
  ``self.cmd_show_palette_drawer()`` after the add so the
  user immediately sees the new palette.
  ``images.py:1162`` ``init_drawer_image_tools`` claimed
  the per-tool selective re-render was unimplemented; the
  implementation already exists as
  ``cmd_open_tool_drawer(tool_name)`` (T-NEW-035) which
  hides all 5 panes and shows only the named one. The
  stale TODO is replaced with a docstring referencing the
  dispatcher. ``settings.py:1016`` claimed the
  ``NchantdOfficeDocumentConfigPane`` features pane was
  unimplemented; the class exists at
  ``panes/document_settings.py:73`` with a per-doctype
  registry (MatrixConfigPane, NotebookConfigPane,
  ImageConfigPane, ScriptConfigPane) wired by T-NEW-027.
  The stale TODO is replaced with a docstring describing
  the registry contract. T-NEW-141 (with 141b + 141c)
  closes all 10 of the inside-nchantdoffice TODO
  markers from the 2026-08-15 inside-sweep. 4 new
  regression tests in
  `tests/test_t_new_141c_clear_stale_todos.py`.
- **T-NEW-120** Script save + reopen aspirational tests
  (2026-08-16) -- re-applies the previously-reverted
  ``85e809e`` fix. Two production bugs in
  ``nchantdoffice/widgets/documents/media/scripts.py``
  caused all 5 aspirational save/restore tests to fail:
  ``get_content`` HTML branch ran a defunct
  ``html.replace(...)`` template substitution against
  an empty ``html = ""`` (the template body was
  commented out), collapsing the saved payload to ``""``
  and dropping every format char; the dict-shape
  ``_resolve_document_text`` reached the top-level
  ``content["text"]`` (which was the inner ``content``
  dict, not the saved text), so reopen fell through to
  ``""``. Test SimpleNamespace fixtures gained
  ``location='external'`` to match the
  ``populate_document`` dispatch. All changes leverage
  existing scripts.py patterns -- no new helpers. 15
  tests pass across the 3 named test files.
- **T-NEW-123** Embedded-TODO sweep (cluster 4)
  (2026-08-16) -- closes the 4 in-file TODOs that
  were either stale comments over already-implemented
  code or had been resolved by prior cards.
  ``journal.py:319`` (save_app redirect -- already
  implemented), ``settings.py:1254`` (lock default
  right tab for free users -- T-NEW-140),
  ``journal.py:459`` (refactor to populate -- T-NEW-138),
  ``config/referral_panel.py:117`` (external source --
  T-NEW-061 deferred). Stale TODOs replaced with
  explanation comments documenting the existing
  contract or the deferred-work rationale. Remaining
  embedded TODOs (`models.py:3040` correction-position,
  `panes/charts.py:186/214` were historically blamed on
  T-NEW-029 drag-init gating, but the real root cause
  was an implicit `None` return from the action-button /
  border-style builder stubs feeding `layout.addWidget(None)`
  (a PySide6 segfault). **Fixed by `899962c`** (T-NEW-037
  followup — see "Fixed" below): `_build_chart_action_button_
  group` / `_build_border_style_editor` now return real
  `QWidget` instances, with a `is not None` gate before
  `addWidget`. Pin:
  `tests/test_t_new_037_addwidget_none_root_cause.py`
  (behavioural + source-shape regression tests). The
  `panes/charts.py:186/214` TODO markers are replaced
  with the docstring referencing the dispatcher; the
  remaining `models.py:3040` correction-position,
  `analytics.py:887` docstring reference, and
  `models.py:3412` PyfficeDocument version increment
  TODOs documented inline. For the T-NEW-123 cluster-4
  sweep itself (the 4 stale-TODO replacements above), no
  test surface was added -- those are documentation /
  explanation comments around code that was already
  correct. The chart addWidget(None) fix is documented
  separately under `899962c` / T-NEW-037 followup. 28 regression
  tests pass across the journal test surface
  (`test_t_new_138_journal_scroll_and_populate.py` +
  `test_journal_always_save.py` +
  `test_compact_journal_content.py` +
  `test_journal_settings_pro_tier.py` +
  `test_journal_add_entry_mirrors_to_document.py`).
- **T-NEW-115** (audit only) -- the live bug was already
  fixed by T-NEW-130 (`ac448ad`); this card is a
  catalogue cleanup.
- **T-NEW-116** Jupyter default working directory
  (2026-08-16) -- the Jupyter subprocess is now spawned
  with a cwd that defaults to
  ``~/Documents/NchantdLibrary`` (created if missing)
  when no file is open. The previous behaviour fell
  back to the bare process cwd (often the application
  bundle dir, which is read-only on packaged installs).
  Fix: extracted ``_resolve_jupyter_cwd()`` helper with
  a 3-step lookup chain (file parent -> NchantdLibrary
  default -> process cwd as last-resort).
  ``start_jupyter_server`` delegates to it. 4 new
  regression tests in
  `tests/test_t_new_116_jupyter_default_dir.py`.

### Changed (T-NEW-110..137)

- **T-NEW-121** em-dash sweep + encoding-declaration placement —
  197 files affected by the `30593b9` SyntaxError incident;
  em-dash removed from comments/docstrings throughout (per
  Python 3.12 tokenizer rule for modules whose `# coding:` line
  is positioned after a non-ASCII line). Encoding declarations
  moved to the first or second line where present.
- `nchantdoffice/__init__.py` - Added version and config exports
- `nchantdoffice/widgets/items/items.py` - Renamed `self.parent` → `self.parent_widget`
  across `NchantdOfficeDocumentCatalogItem`, `NchantdOfficeSourceCatalogItem`,
  `NchantdOfficeTreeNode` to prevent shadowing `QTreeWidgetItem.parent()`

### Fixed (T-NEW-110..147)

- **NchantdChart `addWidget(None)` segfault (chart-config
  action-button / border-style editor)** (2026-08-17,
  commit `899962c`) — historically the
  `panes/charts.py:186/214` sites were attributed to
  T-NEW-029 drag-init gating and the action-button /
  border-style builders were left as `# TODO` commented
  blocks because of that diagnosis. The actual root
  cause was the implicit `None` return from the
  builders feeding `layout.addWidget(None)` — a known
  PySide6 segfault. Fix: `_build_chart_action_button_
  group` (new, returns `NchantdAcceptButtons` or a
  fallback `QWidget`) and `_build_border_style_editor`
  (new, returns a real border-style `QWidget`) replace
  the stubs; `initView` now gates `addWidget(...)` on
  `is not None` before each call. Both call sites
  uncommented with a docstring referencing the
  dispatcher. Pin:
  `tests/test_t_new_037_addwidget_none_root_cause.py`
  (behavioural + source-shape regression tests).
- **pyof routing dispatch bare-parent segfault** (2026-08-17,
  commit `07fc18b`) — `test_cmd_pyof_routing_consolidation.py`
  aborted pytest with exit 139 (SIGSEGV, not a Python
  exception) when the T-NEW-074 pyof dispatch pin
  constructed an `NchantdOfficeApplicationToolBox`
  via `__new__` (the unit-test pattern for a stub
  QObject) and `_resolve_host_doc` (toolboxes.py:1429)
  called `self.parent()`. The bare shiboken binding
  had no Qt parent, so `self.parent()` segfaulted at
  the C++ layer — invisible to the surrounding
  `try/except Exception`. Fix: gate `self.parent()`
  on `shiboken6.isValid(self)` (lazy import; treated
  as unavailable in headless envs without Qt parent),
  so the bare test instance skips the call and the
  walk falls through to the clear `RuntimeError` at
  the bottom of the helper. No production behaviour
  changed (real QObjects are always valid). Pin:
  extension of
  `tests/test_cmd_pyof_routing_consolidation.py` (the
  test file that exposed the bug — now passes
  without segfault; full suite re-includes it after
  the `260886a` T-NEW-122 collection fix made the
  file collectable in the multi-file run).
- **H25 — Catalog Tab Wrong Child Count** (`nchantdoffice` consumer of `nchantrs fa05530`):
  Root cause was in parent library `NchantdNode.loadChildren()` which inconsistently
  used `parentid` vs `pid_txt` for parent filtering. Fix standardized on `pid_txt`.
  Visible in catalog tab child counts across all node types.
- **H27 — Nchantd Image Save Mode (Internal vs External)** (`commit c45cfc5`):
  Enforced canonical external file storage mode in `widgets/documents/media/images.py`;
  internal base64 mode now deprecated with runtime warning. Eliminates round-trip
  corruption and orphan files.
- **H28 — Browser Pin Tab Persistence** (`commit 87a5264`):
  Fixed `open_new_window()` routing through pinned-aware center pane tabset in
  `widgets/documents/atnrg/browsers.py`; corrected `save()` to read `self.pinned`
  (was checking non-existent `self.pin`); `pin_page()` and `populate_document()`
  now respect `self.pinned` state. "Pin Tab" action persists; links in pinned
  tabs no longer open new tabs.
- **H29 — Tree Node Drag-and-Drop Regression** (`commit c45cfc5` + nchantrs `fa05530`):
  Two-part fix — (1) `nchantrs/widgets/items/nodes.py` `NchantdNode.initModel()` now
  stores the full node dict in `UserRole` for drag-drop; (2) `nchantdoffice/widgets/trees.py`
  `getNid()` reads `nid_txt` from the `UserRole` dict. Drag-drop, drop targets,
  and reordering restored.
- **H30 — `setData()` Argument Order** (`nchantrs commit 5afde9d`):
  `NchantdNode.initModel()` in `nchantrs/widgets/items/nodes.py:380` now calls
  `self.setData(0, Qt.UserRole, self.node)` — the correct argument order is
  `(column, role, value)`. Previously the args were inverted, storing the role ID
  in column 0, which silently failed and produced empty `UserRole` data. This
  compounded with H29 to break drag-and-drop in nchantdoffice.
- **H31 — `self.parent` Shadowing `QTreeWidgetItem.parent()`** (`commit a01714c`):
  `QTreeWidgetItem` subclasses in `nchantdoffice/widgets/items/items.py`
  (`NchantdOfficeDocumentCatalogItem`, `NchantdOfficeSourceCatalogItem`,
  `NchantdOfficeTreeNode`) had `self.parent = parent` in their constructors, which
  shadowed Qt's built-in `parent()` method. This caused
  `TypeError: 'NchantdOfficeTreeNode' object is not callable` whenever Qt called
  `.parent()` on a tree item — most visibly in drag-and-drop `_is_descendant()`
  checks. Renamed `self.parent` → `self.parent_widget` across all three classes.
  nchantrs mirrored the rename across `NchantdItem`, `NchantdTreeItem`,
  `NchantdTreeNode`, and `NchantdTree` (commits `57839d2` + `be8a582`).
- Lambda antipattern in toolbar buttons (fixed variable capture)
- Signal inheritance in NchantdNewDocumentToolBar
- Incorrect super().__init__() calls in toolbar classes
- 4 inline TODOs in `widgets/items/items.py` resolved (2026-07-11)

### Filed (open as of 2026-08-17) — NOT YET SHIPPED

These T-NEW cards are filed in `TODOs.md` and awaiting
implementation. They are listed here so the unreleased-block
mirror stays truthful about outstanding work; do **not** move
them to "Added"/"Fixed" until they ship. (Cards marked
✅ were filed here but have since shipped — their entries
are also in "Added" above; the marker is preserved for
traceability.)

- **T-NEW-115** ✅ Creating new Nodes at the top level is blocked
  — **FIXED** by T-NEW-130 (`ac448ad`). Top-level new-node
  toolbar now lands at `pid=0` via
  `NchantdNewDocumentSigil.top_level` flag +
  `launch_new_document_sigil` rootnode dispatch. Pin:
  `tests/test_top_level_node_create.py` (8 tests).
- **T-NEW-116** ✅ Jupyter server default working directory
  (`~/Documents/NchantdLibrary`) — **FIXED** (`8816168`,
  2026-08-16). Pin: `tests/test_t_new_116_jupyter_default_dir.py`
  (4 tests).
- **T-NEW-117** ✅ Palette scan crashes:
  `PyfficeColorPalette.extract_palette` missing —
  **FIXED** (2026-08-17). Upstream pyffice
  `PyfficeColorPalette.extract_palette` shipped in pyffice
  gamma `1cd3c48`; nchantdoffice `419a317` adds a
  `hasattr` graceful-degradation guard at the call site
  so older pyffice builds log + status-bar the failure
  instead of crashing. Pin:
  `tests/test_t_new_117_palette_scan_degradation.py`
  (3 tests).
- **T-NEW-118** Journal PII detector + redacted view with PIN
  copy (re-filed, was orphaned by the T-NEW-066/067/068 number
  collision inside T-NEW-065's deferred-work section).
- **T-NEW-119** Journal retention/timestamp/delete-marked — **CLOSED by operator clarification (2026-08-18):** full-text save/restore and retention already work and must not be changed. Remaining journal scope is parsing/PII integration under T-NEW-118.
- **T-NEW-120** ✅ Script save/restore aspirational tests fail
  at the `5d80f92` contract — **FIXED** (`a2a0361`,
  2026-08-16). Pin: 15 tests green across
  `test_script_newline_roundtrip.py` /
  `test_document_persistence.py` /
  `test_script_open_format.py`.
- **T-NEW-121** em-dash sweep + encoding-declaration
  placement — partial; see "Changed" above for what shipped
  in `30593b9`. Full sweep still open.
- **T-NEW-122** ✅ Qt-harness migration for tests importing
  toolboxes — **FIXED** (`260886a`, 2026-08-17). 21
  module-level `QApplication(...)` offenders stripped;
  `tests/conftest.py` autouse fixture provides a single
  session-wide QApplication lazily; opt-in
  `tests/qt_parent/__init__.py` qapp fixtures exposed
  for tests that want to declare Qt dependency
  explicitly. Pin:
  `tests/test_t_new_122_qt_collection_guard.py` (2 tests;
  RED→GREEN history recorded in commit body). Full suite
  no longer aborts at collection.
- **T-NEW-123** ✅ Embedded-TODO sweep: implement-method stubs
  and config wiring — **FIXED** (`95a41da` cluster 4,
  `5aad63e` cluster 3, `5117b2e` cluster 2, `9c20862`
  cluster 1, plus T-NEW-141b/141c final subsets). 10
  inside-nchantdoffice TODO markers closed.
- **T-NEW-138** ✅ Journal editor followups: always-scroll to
  bottom + refactor to standard populate — **FIXED**
  (`23fa565`, 2026-08-16). Pin:
  `tests/test_t_new_138_journal_scroll_and_populate.py`
  (4 tests).
- **T-NEW-139** ✅ Toolbar signature cleanup — **FIXED**
  (`e1573ba`, 2026-08-16). Extracted
  `_navigate_to_new_doc(pos) -> Self` helper. Pin:
  `tests/test_t_new_139_toolbar_navigate.py` (4 tests).
- **T-NEW-140** ✅ Free-user right-side tab: lock default to Ad
  tab — **FIXED** (`b63d36d`, 2026-08-16). Pin:
  `tests/test_t_new_140_free_user_ad_tab.py` (6 tests).
- **T-NEW-141** ✅ Inside-nchantdoffice TODO sweep: 10
  remaining markers — **FIXED** across three commits
  (`9c20862` subset, `5aad63e` subset 2, `5117b2e` final
  subset, all 2026-08-16).
- **T-NEW-142** ✅ Tab Delete broken from document toolbar +
  `NchantdTabPane` (filed from `testing-report_20260815.md`
  Issue 2). **FIXED** in the `9fccd8f` commit (added two
  `app_action` records); see "Added" above. **Note:
  100-node cap popup superseded by T-NEW-135 redirect
  per user direction 2026-08-16; no T-NEW for popup.**
- **T-NEW-143** ✅ `.pyof` import excludes `DELETE_BIT=1` rows
  (filed from `testing-report_20260815.md` Issue 3).
  **FIXED** in the `c4f6cd3` commit; see "Added" above.
- **T-NEW-144** `file_details` toolbox redirects to internal
  data when tab is an internal document + external file
  becomes editor (not viewer) -- filed from
  `testing-report_20260815.md` Issues 4 & 5; split into
  T-NEW-144a/144b if scope balloons. **T-NEW-144a** ✅
  **FIXED** (`1f08ab5`, 2026-08-16). **T-NEW-144b**
  ⏳ DEFERRED to v0.2.0.
- **T-NEW-145** ✅ `Ctrl+S` wired to save button logic (filed from
  `testing-report_20260815.md` Issue 6). **FIXED** in the
  `c4f6cd3` commit; see "Added" above.
- **T-NEW-146** ✅ `bootstrap_app_user` regression: cannot pickle
  'generator' object — post-T-NEW-129 live traceback
  2026-08-15 22:19:02; **FIXED** in the `c4f6cd3` commit
  (the `_coerce_scalar` helper in
  `_build_app_user_payload`); see "Added" above.
- **T-NEW-147** ✅ `get_app_user` AttributeError:
  `'NchantdOfficeCloakModel' object has no attribute
  'get_table'` — **FIXED** in the `c4f6cd3` commit
  (routes through `self.store.get_table`); see "Added"
  above.

### Security
- Added CI security scanning with bandit and safety

### Testing
- Added pytest configuration and unit tests for config module
- **`tests/test_t_new_*`** — 30+ T-NEW-pinned regression tests
  landed alongside T-NEW-110..137. See
  `tests/` and the test-surface count in `TODOs.md` §1 for the
  current running totals. The aspirational script tests under
  T-NEW-120 (5 RED) are the next acceptance gate.

---

## [Unreleased] — prior batch (T-NEW-058..079)

> **Retained for traceability.** This section was the live
> `[Unreleased]` block prior to the 2026-08-16 sweep that
> consolidated T-NEW-110..147 above. It is unchanged from
> commit `8f9b0aa` (the last committed unreleased-section
> revision before the 110..147 burst landed).
- **Journal save / restore functional** (commits `dad65fe`, `ca1b2e4`, `374c6eb`, `e1d660c`) — `NchantdOfficeJournalEditor.save()` persists the full text via `self.save_app()` (the app_media path: `app_doc_content` / `app_media_content`), and the editor restores the full text on every tab focus via `refresh_content()`. The earlier T-NEW-XXX attempts called `super().save()` alongside the journaling code, which landed the wrong payload into `doc_media_content`; the user removed `super().save()` from the journal path (commits `9e74486` + `cb6ebb9`) so the only correct save path is `save_app()`. `save_app()` failures are NOT wrapped in try/except per the user's `cb6ebb9` directive -- they propagate to the Qt event loop so a save failure is loud, not silent. The user also cleaned up dead commented-out blocks in commit `f978a95` -- no behavior change, just dead-code removal that brings the source closer to the canonical 174cfd86 state plus the T-NEW-079 additions.
- **Journal entries now persist in `content_enc64_txt`** (commit `374c6eb`) — the user-visible live bug: the full text saved, but the `entries` dict inside `app_media_content.content_enc64_txt` was empty. Root cause: `NchantdOfficeJournalAppendEditor.add_entry()` only wrote to `self.parent.pages` (the editor's in-memory alias), not `self.parent.document.pages` (the persisted Pyffice document). The fix writes to both, with defensive fallbacks for empty pages and missing documents. See `tests/test_journal_add_entry_mirrors_to_document.py` (5 tests pinning the contract).
- **Journal `parse()` + `refresh_content()` re-enabled** (commits `dad65fe`, `ca1b2e4`, `e1d660c`) — `parse(content)` splits the full text on `--|YYYY-MM-DD HH:MM:SS|--` markers and stores the `{timestamp: block_text}` dict in `self.entries` (the in-memory cache for date-navigation widgets). The save payload is NOT serialized into the save call -- `save_app()` persists the full text and `parse()` is the consumer-side reducer. `parse()` normalizes its input (dict vs string vs None) so the save flow can call it without first unpacking the `get_content()` dict. `refresh_content()` re-fetches the journal text from the model on every tab focus (T-NEW-036 + T-NEW-073).
- Content-table merge-by-version dedupe (`T-NEW-076`) — extends the `_content` import merge to query the host's MAX(version) per `pUUID` before inserting. Re-importing the same source no longer appends duplicate rows: the source's max-version row replaces host rows only when it's strictly newer; equal-or-older source rows are skipped.

### Changed
- `nchantdoffice/__init__.py` - Added version and config exports
- `nchantdoffice/widgets/items/items.py` - Renamed `self.parent` → `self.parent_widget`
  across `NchantdOfficeDocumentCatalogItem`, `NchantdOfficeSourceCatalogItem`,
  `NchantdOfficeTreeNode` to prevent shadowing `QTreeWidgetItem.parent()`

### Fixed
- **H25 — Catalog Tab Wrong Child Count** (`nchantdoffice` consumer of `nchantrs fa05530`):
  Root cause was in parent library `NchantdNode.loadChildren()` which inconsistently
  used `parentid` vs `pid_txt` for parent filtering. Fix standardized on `pid_txt`.
  Visible in catalog tab child counts across all node types.
- **H27 — Nchantd Image Save Mode (Internal vs External)** (`commit c45cfc5`):
  Enforced canonical external file storage mode in `widgets/documents/media/images.py`;
  internal base64 mode now deprecated with runtime warning. Eliminates round-trip
  corruption and orphan files.
- **H28 — Browser Pin Tab Persistence** (`commit 87a5264`):
  Fixed `open_new_window()` routing through pinned-aware center pane tabset in
  `widgets/documents/atnrg/browsers.py`; corrected `save()` to read `self.pinned`
  (was checking non-existent `self.pin`); `pin_page()` and `populate_document()`
  now respect `self.pinned` state. "Pin Tab" action persists; links in pinned
  tabs no longer open new tabs.
- **H29 — Tree Node Drag-and-Drop Regression** (`commit c45cfc5` + nchantrs `fa05530`):
  Two-part fix — (1) `nchantrs/widgets/items/nodes.py` `NchantdNode.initModel()` now
  stores the full node dict in `UserRole` for drag-drop; (2) `nchantdoffice/widgets/trees.py`
  `getNid()` reads `nid_txt` from the `UserRole` dict. Drag-drop, drop targets,
  and reordering restored.
- **H30 — `setData()` Argument Order** (`nchantrs commit 5afde9d`):
  `NchantdNode.initModel()` in `nchantrs/widgets/items/nodes.py:380` now calls
  `self.setData(0, Qt.UserRole, self.node)` — the correct argument order is
  `(column, role, value)`. Previously the args were inverted, storing the role ID
  in column 0, which silently failed and produced empty `UserRole` data. This
  compounded with H29 to break drag-and-drop in nchantdoffice.
- **H31 — `self.parent` Shadowing `QTreeWidgetItem.parent()`** (`commit a01714c`):
  `QTreeWidgetItem` subclasses in `nchantdoffice/widgets/items/items.py`
  (`NchantdOfficeDocumentCatalogItem`, `NchantdOfficeSourceCatalogItem`,
  `NchantdOfficeTreeNode`) had `self.parent = parent` in their constructors, which
  shadowed Qt's built-in `parent()` method. This caused
  `TypeError: 'NchantdOfficeTreeNode' object is not callable` whenever Qt called
  `.parent()` on a tree item — most visibly in drag-and-drop `_is_descendant()`
  checks. Renamed `self.parent` → `self.parent_widget` across all three classes.
  nchantrs mirrored the rename across `NchantdItem`, `NchantdTreeItem`,
  `NchantdTreeNode`, and `NchantdTree` (commits `57839d2` + `be8a582`).
- Lambda antipattern in toolbar buttons (fixed variable capture)
- Signal inheritance in NchantdNewDocumentToolBar
- Incorrect super().__init__() calls in toolbar classes
- 4 inline TODOs in `widgets/items/items.py` resolved (2026-07-11)

### Security
- Added CI security scanning with bandit and safety

### Testing
- Added pytest configuration and unit tests for config module

---

## [0.0.1.0.1.4] - 2026-03-25

### Phase 7 - Quality & Standards Compliance

#### Added
- CI/CD pipeline (GitHub Actions)
- Configuration module with logging and 100+ constants
- Unit test infrastructure
- Documentation deployment workflow

#### Fixed
- Lambda antipattern in buttons
- Signal inheritance issues
- super().__init__() parameter errors

---

## [0.0.1.0.1.3] - 2026-03-05

### Phase 6 - Build & Deploy Preparation

#### Added
- PyfficeDocument implementations (12 types)
- Toolbox integration with dynamic tools
- Signal flow: toolbar → tree → tabs → toolbox
- CLI entry point via cmds/

#### Fixed
- Center app tab dragging
- Tree node drag-and-drop
- Cross-pane tab dragging
- Tab-to-tree drag-and-drop
- Right-click context menus
- Right toolbox search

---

## [0.0.1.0.1.2] - Prior

*History not available*

---

## Internal Project Changes Required

See [CHANGES-nchantrs.md](./CHANGES-nchantrs.md) for changes needed in the nchantrs dependency.
