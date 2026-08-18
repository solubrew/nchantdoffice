# CHANGES.md - NchantdOffice Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

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
