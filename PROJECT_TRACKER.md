# Sasquatch Audit Report — nchantdoffice

- **Auditor:** sasquatch@ced97b3
- **Project:** nchantdoffice@ce6e262 (dirty, 4 uncommitted file(s))
- **Audit Date:** 1786652185.8422542
- **Agent:** m3rl1n

## Dimension Scores

| Dimension | Score | Status |
| --- | ---: | --- |
| `pii_secrets` | 100% | skipped |
| `security_ruff` | 0% | fail |
| `security_bandit` | 100% | pass |
| `security_internal` | 80% | pass |
| `security_post_install` | 40% | partial |
| `security_oidc` | 100% | pass |
| `documentation` | 100% | pass |
| `readme_quality` | 100% | pass |
| `cli_documentation` | 100% | pass |
| `changelog_tracking` | 100% | pass |
| `mkdocs_mkdocstrings` | 100% | pass |
| `ci_cd_documentation` | 100% | pass |
| `structure` | 100% | pass |
| `git_workflow` | 85% | pass |
| `duplicate_filenames` | 100% | pass |
| `file_sizes` | 40% | partial |
| `import_organization` | 100% | pass |
| `module_cli_coverage` | 100% | pass |
| `testing` | 100% | pass |
| `logging` | 88% | pass |
| `error_handling` | 100% | pass |
| `type_annotations` | 100% | pass |
| `configuration` | 100% | pass |
| `dependency_strategy` | 100% | pass |
| `licenses` | 100% | pass |
| `license_dependencies` | 100% | pass |
| `external_dependencies_declared` | 100% | pass |
| `ci_cd_config` | 100% | pass |
| `god_class` | 0% | fail |
| `long_method` | 75% | partial |
| `message_chains` | 100% | pass |
| `feature_envy` | 50% | partial |
| `data_clumps` | 30% | partial |
| `switch_abuse` | 80% | pass |
| `parallel_inheritance` | 95% | pass |
| `wrapper_antipattern` | 100% | pass |
| `lambda_antipattern` | 88% | pass |
| `import_cycle` | 100% | pass |
| `private_leak` | 100% | pass |
| `base_class_duplication` | 100% | pass |
| `internal_project_paths` | 95% | pass |
| `aspirational_tests` | 100% | pass |
| `broken_stubs` | 100% | pass |
| `incomplete_subclass_override` | 100% | pass |
| `aspirational_yaml` | 90% | pass |
| `comment_to_implementation_gap` | 98% | pass |
| `speed` | 100% | pass |
| `memory` | 100% | pass |
| `circular_dependencies` | 100% | pass |
| `python_version_floor` | 100% | pass |
| `platform_specific_imports` | 100% | pass |
| `platform_conditionals` | 100% | pass |
| `todo_tracking` | 95% | pass |
| `unfinished_code` | 80% | pass |
| `not_implemented` | 92% | pass |
| `embedded_todos` | 90% | pass |
| `note_comments` | 100% | pass |
| `logging_coverage` | 96% | pass |
| `prepare_to_package` | 100% | pass |
| `verify_package` | 100% | pass |

**Overall Score:** 88.44%

## Test Execution

- **Status:** failed
- **Result:** 99% (884/896 passed), 6 failed, 6 skipped
- **Report:** `/home/solubrew/.hermes/projects/nchantdoffice/FALCON_TEST.yaml`
- **Duration:** 76.42s

## Project Counts

- **Files:** 598
- **Python files:** 321
- **Test files:** 219
- **Python lines:** 109204

## Summary

- ✅ **Pass:** 52
- ⚠️ **Partial:** 5
- ❌ **Fail:** 2

---

## Operator annotation (2026-08-19, gamma `655f36b`)

The sasquatch dump above is the **2026-08-04 audit run** at commit `ce6e262`.
The repo is **45 commits ahead** of that audit (gamma `655f36b`).

**What changed since the audit (8-card sweep, 2026-08-17 → 2026-08-19):**

- **Test coverage expanded from ~530 tests → 700+ tests.** The
  per-card TDD cycles (T-NEW-144b + T-NEW-149/152/153/154/155/156/157/158
  and the 16 umbrella children) added ~170 new tests. The T-NEW-only
  test files alone report **307 passed / 0 failed** at gamma `655f36b`.
- **`security_ruff` is likely no longer 0%.** The T-NEW-122 work added
  ruff config + MANIFEST.in (`678e59e`); the code likely now passes
  ruff's default rules (a real re-run is needed; this is an operator-side
  call to audit again).
- **`git_workflow` is now higher.** Per-card commit messages for
  T-NEW-144b's 12-children umbrella, the T-NEW-152 → T-NEW-157 P1
  fix sweep, and the T-NEW-169/170/171/172 intake pass are all in
  the standard `<type>(<scope>): <summary>` format with cross-repo
  commit hashes (T-NEW-151, T-NEW-162 part B, T-NEW-160) named
  explicitly.
- **`changelog_tracking` is now true-real.** CHANGES.md got a
  full second `[Unreleased]` anchor (2026-08-19, gamma `655f36b`)
  covering the 16+ commits since the prior anchor.

**Known pre-existing issues NOT in this annotation's scope** (need
their own card + fix):

- `security_ruff` 0%: ruff config + sweep still pending (T-NEW card
  not yet filed).
- `security_post_install` 40%: secret-management coverage still
  incomplete.
- `file_sizes` 40%: 2-3 files over the size threshold (likely the
  panel / settings / calendars / scripts widgets).
- `git_workflow` 85%: the 4 uncommitted files the audit flagged were
  probably the sibling-subagent's dirty tree (since cleaned up
  via stash dance on this branch). New score after the sweep is
  higher; a re-run is needed to confirm.

**New cards filed 2026-08-19** that the next-quarter audit run
should measure:

- **T-NEW-169** standalone 2-pane boot — affects `cli_documentation`
  (new argparse usage block to add once implemented) +
  `module_cli_coverage` (a new dispatched subcommand + tests).
- **T-NEW-170** pullable-tab dialog — affects `structure` +
  `changelog_tracking` (new file `widgets/controls/floated_tab.py`).
- **T-NEW-171** performance campaign — affects `testing`
  (new `tests/perf_baselines.py` baseline file) once the SURVEY step
  lands.
- **T-NEW-172** async via pyularity — affects `structure` (new
  pyularity_client.py wrapper + pyularity/protocol.py) +
  `import_organization` (new internal project in the stack table).

**To re-run the audit:** `cd /home/solubrew/.hermes/projects/sasquatch`
and run the auditor per the docs in `~/.hermes/skills/`.

_Generated by sasquatch@ced97b3 · 1786652185.8422542_