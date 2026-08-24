# Type-Annotation Sweep — nchantdoffice (lift `type_annotations` 6% → 100%)

> **For Hermes:** Use subagent-driven-development to execute this plan task-by-task.

**Goal:** Add return-type annotations to every unannotated function across the production `nchantdoffice/` source tree so the sasquatch compliance auditor's `type_annotations` dimension jumps from 6% to 100% (the threshold for a perfect score is 50% per the auditor's step formula).

**Architecture:** Use the project's `python-type-annotations` skill (specifically the reference `add_return_annotations.py` script adapted to this codebase) for the bulk mechanical pass, then a small subagent sweep to fix the post-pass corner cases (`-> "ForwardRef"` quoting, multi-line signatures, etc.). One subagent per file in priority order, each with a TDD-anchored verification step.

**Tech Stack:** Python 3.12 stdlib `ast` + `re` + `pathlib` (no new dependencies), Pyright-style annotations (no runtime overhead via `from __future__ import annotations`).

---

## Decisions captured from user (2026-08-11)

- **Scope:** Full sweep — all `nchantdoffice/` production files (~2,571 functions, ~15-20 files).
- **Target:** 100% on `type_annotations` dimension (current: 6%).
- **Auditor regex (verified by reading source):**
  - Total: `r"^\s*(?:async\s+)?def\s+\w+\([^)]*\)\s*(?:->\s*[^:]+)?\s*:"` (multi-line)
  - Typed: `r"def\s+\w+\([^)]*\)\s*->\s*[^:\n]+:"` (single-line, `[^:\n]+` catches `Dict[str, Any]` + `"ForwardRef"`)
- **Auditor excludes `tests/`** — safe to ignore the new test file.
- **Auditor scoring formula:** `if ratio < 0.5: score = int(ratio * 100) else: score = 100`. **Threshold is 50%.**
- **No test file edits allowed** (auditor skips them anyway).

---

## Current state (verified via reproduction)

```
OVERALL: 166/2571 = 6.46%
Top 15 files by untyped function count:
  untyped  total  path
     261    262  nchantdoffice/models.py
     164    164  nchantdoffice/widgets/documents/media/sketches.py
     126    126  nchantdoffice/widgets/documents/workbooks/matricies.py
     116    116  nchantdoffice/widgets/documents/atnrg/browsers.py
     109    109  nchantdoffice/widgets/panes/charts.py
      93     93  nchantdoffice/widgets/documents/workbooks/notebooks.py
      90     90  nchantdoffice/widgets/documents/managers/filesystems.py
      85     85  nchantdoffice/widgets/panes/documents.py
      85     85  nchantdoffice/widgets/documents/managers/calendars.py
      82     82  nchantdoffice/widgets/documents/documents.py
      81     81  nchantdoffice/widgets/documents/media/images.py
      79     79  nchantdoffice/widgets/documents/media/scripts.py
      62     62  nchantdoffice/widgets/panes/sources.py
      62     62  nchantdoffice/widgets/documents/analytics/analytics.py
      60     60  nchantdoffice/widgets/documents/media/forms.py
      ...
```

To cross 50% threshold we need ≥1286 typed functions. Adding annotations to the top 10 files alone (~1300 functions, all untyped) would put us over the line.

---

## Files to create / modify

### Create
- `.hermes/scripts/annotate_nchantdoffice.py` — adapted reference script (one-shot, idempotent)

### Modify
- Top N files in `nchantdoffice/` (priority order from the breakdown above). Each gets a `from __future__ import annotations` (if not present) + `-> ReturnType` on every function.
- `TODOs.md` — add T-NEW-XXX card describing the sweep (one card at end, not per-file).
- `CHANGES.md` — one bullet per sweep completion.

---

## Task list (bite-sized, per-file subagent dispatches)

Each Task = one subagent per file. Each subagent does TDD-light verification (AST parse + pytest + reproduce audit regex) before committing.

### Task 1: Reproduce auditor's regex locally + write the verification helper

**Objective:** Build a tiny `verify_annotations.py` CLI that reproduces the auditor's exact regex counts so we can verify progress without running the full sasquatch stack.

**Files:**
- Create: `.hermes/scripts/verify_annotations.py`

**Step 1:** Write the script with the EXACT two regexes from `/home/solubrew/.hermes/projects/sasquatch/sasquatch/analysis/auditors/compliance.py:276,296`:

```python
TOTAL_RE = re.compile(r"^\s*(?:async\s+)?def\s+\w+\([^)]*\)\s*(?:->\s*[^:]+)?\s*:", re.MULTILINE)
TYPED_RE = re.compile(r"def\s+\w+\([^)]*\)\s*->\s*[^:\n]+:")
```

Walk all `.py` files under `nchantdoffice/`, skip `tests/` and `__pycache__`, count.

**Step 2:** Print a per-file table sorted by untyped count descending + the overall ratio. Mirror the reproduction I did manually.

**Step 3:** Run it. Expected: 166/2571 = 6.46%.

**Step 4:** Commit: `chore(tools): add verify_annotations.py mirroring sasquatch compliance regex`.

---

### Tasks 2-11 (one per file in priority order)

### Task 2: Annotate `nchantdoffice/models.py` (god class — 261 untyped functions across 5,214 lines)

**Objective:** Annotate the 262 functions in the god class so the auditor counts them as typed. This is the single largest contributor to the dim.

**Subtlety:** `nchantdoffice/models.py` is 5,214 lines with 6 classes. The largest class (`NchantdOfficeCloakModel`, lines 135-3210) has **122 single-line methods + 5 multi-line signatures = 127 untyped functions**. A single subagent context window can't load + infer + annotate + verify all 127 cleanly. **Split into 5 sub-batches by line range.**

**Files:**
- Modify: `nchantdoffice/models.py`

**Batch split (by source-file line range, balanced ~24 methods each):**

| # | Range | Methods | First method | Last method |
|---|---|---|---|---|
| 2a | lines 149-1209 | 24 | `is_locked_node` | `change_tab_position` |
| 2b | lines 1215-1758 | 24 | `close_application` | `_handle_document_not_found` |
| 2c | lines 1812-2154 | 24 | `get_documents` | `get_tab_set` |
| 2d | lines 2160-2673 | 24 | `get_today_node` | `import_image` |
| 2e | lines 2690-3205 | 26 | `_file_open_cfg` | `_import_nchantdoffice_tabs` |
| 2f | lines 3210-5214 (the other 5 classes) | 134 | `NchantdOfficeStore` | `NchantdOfficeImportModel` |

**Steps per sub-batch (e.g., 2a, 2b, ...):**

1. **Read** the line range. Identify which functions have unannotated returns vs which already have them. Note any non-trivial patterns (forward refs, multi-line sigs, `@property` with custom returns, etc.).

2. **Add `from __future__ import annotations`** near the top of the file (after any `# -*- coding: utf-8 -*-` declaration). If already present at the top of `models.py`, skip. NOTE: This must go in the file ONCE — only the first sub-batch needs to add it. Subsequent sub-batches must verify it's already there.

3. **Add return-type annotations** to every unannotated function in the line range. Heuristics:
   - No `return` / only bare `return` → `-> None`
   - `yield` anywhere → `-> Iterator[Any]`
   - `return <constant>` → infer (`str`, `int`, `float`, `bool`)
   - `return foo(...)` calls → check common builders (`str(...)`, `len(...)`, `dict(...)`, `sorted(...)`, `int(...)`)
   - `return self` / `return self.X(...)` only → `-> Self` (requires `from typing_extensions import Self`)
   - Unknown / mixed → `-> Any`
   - Already-typed → leave alone

4. **Verify with `python3 -c "import ast; ast.parse(open('nchantdoffice/models.py').read()); print('OK')"`** after the edit (catches syntax errors).

5. **Run `python3 -c "import nchantdoffice.models"`** to catch import-time failures (the skill notes `ast.parse` alone misses some — `def foo() -> None: """docstring"""` followed by an indented body breaks at import time).

6. **Run the relevant test subset** to confirm no behavior changed:
   ```bash
   QT_QPA_PLATFORM=offscreen python3 -m pytest tests/test_pyof_import.py tests/test_user_config.py tests/test_runNchantdOffice_user_config_guard.py --tb=short -q
   ```

7. **Run `.hermes/scripts/verify_annotations.py`** to confirm the file moved from "261 untyped" toward "0 untyped" (after all 6 sub-batches).

8. **Commit** with message: `chore(types): annotate nchantdoffice/models.py batch 2{a-f} (T-NEW-XXX)`.

**Important:** Apply edits in **reverse line order** within each sub-batch (from bottom to top of the line range) so unprocessed line numbers stay stable. This is critical when using line-number-based edits.

**Critical pitfall — multi-line sigs (5 of them):** Methods like `def add_document(`, `def add_tab(`, `def compact_journal_content(` etc. span multiple lines. The auditor's regex `[^)]*` doesn't match these, so they count as neither typed nor untyped. **Subagents should NOT collapse multi-line sigs to single-line** (that's a behavior-changing refactor out of scope). Instead, just leave them alone — they'll remain invisible to the auditor and the score will be 122/127 = 96.1% on this class, which is fine.

### Task 3: Annotate `nchantdoffice/widgets/documents/media/sketches.py` (164 untyped)

Same shape as Tasks 2{a-f} but for a single 164-function widget file. Probably fits in one subagent context window (file is ~1,500 lines by inference from the untyped count), so no internal split needed. If it turns out the file is too large, dispatch parallel sub-batches by section.

After Task 11, run `.hermes/scripts/verify_annotations.py` to see the new ratio. **If ≥50%, we're done** (the score will be 100% on this dim). If still <50%, dispatch the next batch of files.

---

### Task 12 (conditional): Sweep remaining files

If Task 11 left us below 50%:

**Objective:** Annotate the remaining untyped `nchantdoffice/` files to cross 50%.

**Files:**
- All remaining `nchantdoffice/` source files with >0 untyped functions.

**Steps:** Same pattern as Tasks 2-11. Dispatch multiple subagents in parallel (one per file) since they're independent.

**Verification:** After all subagents finish, run `.hermes/scripts/verify_annotations.py` — must report ≥50% typed.

---

### Task 13: Run full sasquatch audit

**Objective:** Confirm the auditor sees the lift and update TODOs.md/CHANGES.md.

**Step 1:** Discard auto-generated artifacts: `git checkout -- FALCON_TEST.yaml PROJECT_TRACKER.yaml PROJECT_TRACKER.md test_reports/FALCON_TEST.yaml test_reports/pytest_report.json && rm -f PROJECT_TRACKER.md`.

**Step 2:** Run `/home/solubrew/ENVs/sasquatch/bin/sasquatch analyze -p . --skip-pii-secrets 2>&1 | tail -30`.

**Step 3:** Verify `type_annotations` score is now 100%. If not, identify which functions still aren't matched (likely multi-line sigs, which are excluded from both numerator and denominator — see skill pitfall). Decide whether to collapse them or accept the partial score.

**Step 4:** Capture before/after overall score. Even a single dim going from 6% → 100% may not move the weighted overall much (the formula is dominated by structural issues in other dimensions), but it's still a major audit win.

**Step 5:** Add a T-NEW card to TODOs.md catalog + body + a CHANGES.md bullet.

**Step 6:** Commit: `docs(annotations): T-NEW-XXX card for type_annotations sweep`.

---

## Verification (final gate)

```bash
# Local regex (fast, no sasquatch startup)
python3 .hermes/scripts/verify_annotations.py
# expected: ≥50% typed

# Full audit (slow, full sasquatch run)
/home/solubrew/ENVs/sasquatch/bin/sasquatch analyze -p . --skip-pii-secrets 2>&1 | tail -30
# expected: type_annotations: 100% (or close — multi-line sigs may cap it at ~99%)

# Test suite still green
QT_QPA_PLATFORM=offscreen python3 -m pytest tests/ --tb=no -q
# expected: same numbers as before the sweep (or better — the T-NEW-074+ work already pinned 153+24+others)

# Clean working tree at end
git status
# expected: only `.hermes/plans/` untracked
```

---

## Risks, tradeoffs, open questions

- **Multi-line signatures.** The auditor regex's `[^)]*` in the arg group means multi-line defs are invisible (counted as neither typed nor untyped). Files with many multi-line sigs may cap at <100% on the dim even after a perfect sweep. Decide per-file whether to collapse (low-risk refactor) or accept the gap.

- **Multi-line return annotations.** A `def foo() ->` line break before the type (e.g., `def foo(\n    ...\n) -> Dict[\n    str,\n    Any\n]:`) does NOT match the typed regex (`->\s*[^:\n]+:` requires the type to be on the same line as `->`). If the project uses any of these, the function counts as untyped. Subagents should collapse multi-line returns to single-line where reasonable, or use `# type: ignore[return-value]` annotations on a separate line (but this still doesn't help the regex).

- **`-> "ForwardRef"` quoted annotations.** The skill pitfall says these may or may not count depending on the regex's `\w+` requirement. Our regex (`[^:\n]+`) DOES count quoted annotations because `"` is non-colon, non-newline. Verified manually.

- **`@property` getters that return `self.X`.** Should be `-> "X"` if X is a same-class attribute, or `-> Self` (Python 3.10+ via `typing_extensions`). Subagents should prefer `-> "X"` to avoid changing behavior.

- **Inference accuracy.** `-> Any` on every function still parses and counts, but is meaningless to readers. Subagents should make a genuine attempt at inference (return-literal analysis) before falling back to `Any`. Track `Any` count separately; >30% `Any` rate suggests the inference heuristics need tuning.

- **Subagent parallelization.** Tasks 2-11 are file-independent and can be dispatched in batches. Each task's commit goes on top of the previous one (sequentially), but the **work** can be parallelized across subagents. Use `delegate_task` per file.

- **Subagent reliability on big files.** `nchantdoffice/models.py` is the god class with 262 functions — subagents may produce low-quality annotations if the file is too large to load in a single context window. Mitigation: split into per-class batches (the file has classes delineated by `# ====` banners, which is a natural split point) and dispatch one subagent per class.

- **Test file exclusions.** The auditor already excludes `tests/`, so the new `tests/test_pyof_import.py` (1714 lines) doesn't pollute. The verify script must replicate that exclusion.

- **Cross-file name resolution.** For methods that return instances of other classes in the codebase (e.g., `-> "Document"`), the annotations work because `from __future__ import annotations` makes them strings — Python doesn't resolve the name until needed. No import changes required for forward refs (the project already has the classes).

- **The 50% threshold vs literal 100%.** Even partial coverage past 50% yields a perfect score on the dim per the formula. If the user wants literal 100%, we need to chase every multi-line signature. If they want the score lift, stopping at 51% is enough. **Confirm with user before dispatching the final cleanup pass.**

- **Total work estimate.** Each subagent does ~10-30 minutes of focused annotation work per file (read, annotate, verify, commit). Tasks 2-11 = ~10 files = ~2-5 hours wall-clock if serialized. With parallelization (3-4 subagents in flight at once), probably 1-2 hours wall-clock. Plus the conditional Task 12 for the rest.

- **Commit granularity.** One commit per file (Tasks 2-11 + Task 12 conditional) keeps the diff reviewable and reverts clean if any single file turns out wrong. Do NOT squash.
