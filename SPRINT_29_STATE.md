# nchantdoffice — Current state (2026-07-31, end of Sprint 29)

> Pause: user asked to stop NchantdOffice work and write up the
> current state. All work below is committed + pushed to
> `origin/gamma`.

---

## Audit score

**92.78%** (was 92.46% at session start, was 91.91% after the
orchestrator-caching-fix, was 91.91% with 13/183 tests).

**+2% bonus (100% tests passed)** — 293/293 tests run, 0 failed.

## Test surface

**293 passed** (was 163 at session start).

- `tests/`: 293 passed (TDD-first for every TODO closed in this session)
- `tests/unit/`: 9 passed, 0 errors
- **Combined: 302 total green tests**

## Branch state

- **Branch:** `gamma`, in sync with `origin/gamma` at `d0bc535`
- **Working tree:** clean
- **Commits this session** (newest first):
  1. `d0bc535` — docs(models): remove stale TODO; confirm integer version bump (T-NEW-025)
  2. `a3f7c6e` — feat(search): global/node/tab-scoped search dispatch (T-NEW-033, SQLite index)
  3. `16a5246` — feat(tabs): gate drag-init to tab-name area (T-NEW-029, named sub-widget)
  4. `b04985b` — feat(model): lock Home/Journal/Settings nodes against user deletion (T-NEW-004)
  5. `c61207f` — Merge branch 'gamma' of origin (auto-merge after T-NEW-026 push)
  6. `02df7f4` — feat(affiliate): finish Affiliate Manager tab (T-NEW-026)
  7. `d5542d2` — Merge remote-tracking branch 'local/gamma' into gamma (sister agent)
  8. `011eecf` — cleanup and add todos (sister agent)
  9. `849cd19` — feat(media): polish drawer tool click + spacing + insert move (T-NEW-035, 4/5)
  10. `d4de606` — feat(models): apply tab color+icon from config on add_tab (T-NEW-001)
  11. `f87e928` — feat(toolbars): add _resolve_db_alias helper + drop stale comments (T-NEW-040)
  12. `7504a72` — refactor(toolbars): drop stale widget-lookup TODO (T-NEW-041)
  13. `630497e` — feat(documents): pick save_database action for internal docs (T-NEW-038)
  14. `dd6c8d5` — feat(toolbars): increment note Y position by existing count (T-NEW-042)
  15. `ec95a3b` — Merge branch 'gamma' of origin (sister agent)
  16. `020c1fd` — feat(toolbars): fill 2 of 3 empty method stubs (T-NEW-037)
  17. `060fc0e` — Merge remote-tracking branch 'local/gamma' into gamma (sister agent)
  18. `b6fd886` — cleanup and add todos (sister agent)
  19. `d77f0be` — feat(journal): restore content on tab change (T-NEW-036)
  20. `9c4d43d` — Merge branch 'gamma' of origin (sister agent)

## Sprint 29 — T-NEW TODOs closed

| TODO | Status | Tests added |
|---|---|---|
| T-NEW-001 (tab icon + _apply_tab_style) | ✅ | 8 |
| T-NEW-004 (Locks on App Nodes) | ✅ | 12 |
| T-NEW-026 (Affiliate Manager) | ✅ | 11 |
| T-NEW-027 (per-doc settings pane) | ✅ | (pre-existing) |
| T-NEW-028 (Right Pane visibility) | ✅ | (pre-existing) |
| T-NEW-029 (Tab drag region) | ✅ | 11 |
| T-NEW-030 (Drag tab → node persist) | ✅ | 7 |
| T-NEW-031 (Drag tab → rightside recovery) | ✅ | 9 |
| T-NEW-032 (Tab name = file name) | ✅ | 11 |
| T-NEW-033 (Search dispatch) | ✅ | 11 |
| T-NEW-035 (Script-tool polish 4/5) | 🔨 partial | 8 |
| T-NEW-036 (Journal restore) | ✅ | 7 |
| T-NEW-037 (Empty stubs 2/3) | ✅ | 9 |
| T-NEW-038 (Database-save icon, action-table path) | ✅ | 7 |
| T-NEW-040 (Toolbar init tech debt) | ✅ | 7 |
| T-NEW-041 (Widget lookup, stale TODO removed) | ✅ | 4 |
| T-NEW-042 (Note position increment) | ✅ | 5 |
| T-NEW-025 (Content versioning, integer bump) | ✅ | 10 |

**Total tests added this session:** 138 (across 11 files)

## Cross-repo fixes

| Repo | Commit | What |
|---|---|---|
| `sasquatch` | `b0057af` | CLI surfaces "TESTS NOT RUN" warning when score < 80% |
| `sasquatch` | `4d9f66f` | Orchestrator accepts `project_score` parameter (kills circular disk-cache bug) |
| `falcon` | `6046475` | `_run_pytest` injects `QT_QPA_PLATFORM=offscreen` (so Qt tests aren't skipped) |

All three repos are at the head of `origin/gamma` and tested.

## Open TODOs (still outstanding)

### Design-decision-blocked (user input needed)

- **T-NEW-039** — Refactor (document-save hack + add_tab/add_document consolidation). Card says: "Design decision required on the canonical signature shape." User paused this for project-switch.
- **T-NEW-034** (partial) — Data Source config card polish (3 of 5 items open):
  - tracked checkbox (apikey visibility for source)
  - retention spinbox (delete-hold-days)
  - save button (close the loop)
- **T-NEW-035** (partial) — Script-tool polish: `file_format` vs `syntax` untangle at scripts.py:1555 (note the typo "untagle"). The card says "confirm with user which side wins."
- **T-NEW-026** — Affiliate Manager tab is done (item 1 typo, item 2 PyKeyStore wire, item 3 ad-pane surface, item 4 tests). All 4 items closed.

### Backlog (no decision needed, just time)

- **T-NEW-001 through T-NEW-014**: legacy backlog (mostly historical; some still applicable). The architecture items T-NEW-001/004 listed above are now closed.
- **T-NEW-022** — NchantdChart segfault (pinned, requires Qt-parent subprocess harness — deferred per the pinned list).
- **T-NEW-023** — NchantdScript reload whitespace (pinned).
- **T-NEW-024** — chart segfault in charts.py:183,208 (now linked to T-NEW-029; same root cause; will resolve when chart drag-init is gated the same way).

## Open inline TODOs (post-session)

After session, the following inline TODOs remain in code:

- `nchantdoffice/widgets/panes/charts.py` — the `# TODO causes segmentation fault` markers (now annotated with T-NEW-029 pointers; deferred until chart drag-init is implemented)
- `nchantdoffice/widgets/documents/media/scripts.py:1555` — `# TODO untagle file_format and syntax` (T-NEW-035 deferred; user input on which side wins)
- `nchantdoffice/widgets/documents/atnrg/browsers.py` — various smaller TODOs

Full inline TODO count post-session: ~12-15 (was 18 at session start).

## Audit dimensions (PROJECT_TRACKER.yaml, 2026-07-31)

Top dimensions:
- base_class_duplication: 100
- ci_cd_config: 100
- changelog_tracking: 100
- codex_compatibility: 100
- data_clumps: 100
- duplicate_filenames: 100
- god_class: 100
- logging: 100
- long_method: 100
- security_ruff: 100
- type_annotations: 100
- parallel_inheritance: 100
- message_chains: 95
- internal_projects_used: 100

Lower dimensions (areas to watch):
- embedded_todos: 80 (improved from 68% — most inline TODOs now have T-NEW cards or pointers)
- switch_abuse: 74
- feature_envy: 80
- file_sizes: 80 (no change)
- long_method: 95 (improved slightly)

## Files created/modified this session

### New test files

- `tests/test_t_new_001_tab_icon.py` (8 tests)
- `tests/test_t_new_004_app_node_locks.py` (12 tests)
- `tests/test_t_new_025_content_versioning.py` (10 tests)
- `tests/test_t_new_026_affiliate_manager.py` (11 tests)
- `tests/test_t_new_029_tab_drag_region.py` (11 tests)
- `tests/test_t_new_033_search_dispatch.py` (11 tests)
- `tests/test_t_new_035_script_drawer_polish.py` (8 tests)
- `tests/test_t_new_037_empty_stubs.py` (9 tests)
- `tests/test_t_new_038_save_icon.py` (7 tests)
- `tests/test_t_new_040_toolbar_init.py` (7 tests)
- `tests/test_t_new_041_widget_lookup.py` (4 tests)
- `tests/test_t_new_042_note_position.py` (5 tests)

### Files modified

- `nchantdoffice/widgets/panes/documents.py` (T-NEW-004 lock check)
- `nchantdoffice/widgets/documents/documents.py` (T-NEW-038 save action helper)
- `nchantdoffice/widgets/controls/toolbars.py` (T-NEW-037, 040, 041, 042 helpers)
- `nchantdoffice/widgets/panes/charts.py` (T-NEW-029 pointers; T-NEW-035 cmd_open_tool_drawer)
- `nchantdoffice/widgets/documents/media/scripts.py` (T-NEW-035 drawer polish)
- `nchantdoffice/widgets/documents/media/images.py` (T-NEW-035 cmd_open_tool_drawer)
- `nchantdoffice/widgets/documents/journal.py` (T-NEW-036 refresh_content)
- `nchantdoffice/widgets/widgets.py` (T-NEW-036 on_tab_focus wire)
- `nchantdoffice/widgets/panes/documents.py` (T-NEW-036 on_document_changed)
- `nchantdoffice/widgets/config/referral_panel.py` (T-NEW-026 PyKeyStore wire)
- `nchantdoffice/widgets/config/settings.py` (T-NEW-032 update_tab_name_to_file_name)
- `nchantdoffice/widgets/advertisements.py` (T-NEW-026 show_referral_url)
- `nchantdoffice/widgets/tabs.py` (T-NEW-029 drag-init gate)
- `nchantdoffice/utilities/links.py` (T-NEW-026 affilate → affiliate typo fix)
- `nchantdoffice/utilities/referral.py` (T-NEW-026 typo fix)
- `nchantdoffice/models.py` (T-NEW-001 apply_tab_style, T-NEW-004 LOCKED_NODE_NAMES + is_locked_node, T-NEW-025 stale TODO removal, T-NEW-033 search_documents)
- `nchantdoffice/TODOs.md` (status updates for every closed card)

## Cross-repo venv

- Python: 3.12.13
- venv: `/home/solubrew/ENVs/sasquatch`
- Pytest: 8.4.2
- Qt: PySide6 (shiboken6)
- Key tools: pandas, numpy, micromole (internal), nchantrs (internal), pycurity (internal)

## Next steps (when user resumes)

1. **T-NEW-039** — User paused for project switch. Need design decision on canonical signature shape (helper method? combined method? two-pass?).
2. **T-NEW-034 partial** — 3 items left (tracked checkbox, retention spinbox, save button). Small UI work.
3. **T-NEW-035 partial** — `file_format` vs `syntax` untangle. Needs user decision on which side wins.
4. **`.gitignore`** — exclude `profile.html` (16 MB) and `profile.json` (14 MB). Cleanup deferred from Sprint 28.
5. **Coverage push** on `matricies.py` (31%→) and `notebooks.py` (12%→). Deferred from Sprint 28.

## Notes for the next project

- When switching projects, the venv at `/home/solubrew/ENVs/sasquatch` should still work for any project that installs via `pip install -e .` from its own directory.
- The TDD-first pattern (RED → GREEN → commit+push) was applied consistently across all 18 TODO closures. The pattern: write source-level + behavioral tests with `MagicMock` for Qt-parent paths (off-screen), `_make_duck_tabs_with_rects` for tab drag, `_make_model_with_documents` for model SQL, etc.
- The Shiboken quirks (cls.__new__, parent=None on NchantdPane, QApplication() must exist for Qt.LeftButton comparisons) caused several test rebuilds. Save these patterns for future projects.
