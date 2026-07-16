# NchantdOffice Project State

## Overview
- **Project**: NchantdOffice
- **Type**: Desktop GUI Application (PySide6)
- **Purpose**: Office automation suite with document management, calendar, contacts
- **Framework**: Built on nchantrs framework
- **Location**: `/home/solubrew/.senbai/workspace/projects/nchantdoffice`
- **Branch**: `gamma` (per CODING_STANDARDS Git workflow)
- **Version**: 0.0.1.0.1.5
- **Last Commit**: Merge — P0 fixes H30/H31/H32 + upstream sync

---

## Current Status: ACTIVE DEVELOPMENT

## Recent H## Activity (2026-07)

| ID | Title | Status | Commit |
|----|-------|--------|--------|
| H24 | Toolbox Drawer Stale on Tab Switch | ✅ Completed (2026-07-08) | `0598d13` |
| H25 | Catalog Tab Wrong Child Count | ✅ Completed (2026-07-12) | nchantrs `fa05530` |
| H27 | Nchantd Image Save Mode (External Storage) | ✅ Completed (2026-07-12) | `c45cfc5` |
| H28 | Browser Pin Tab Persistence | ✅ Completed (2026-07-11) | `87a5264` |
| H29 | Tree Node Drag-and-Drop Regression | ✅ Completed (2026-07-12) | nchantrs `fa05530` + `c45cfc5` |
| H30 | Row Height spinbox wrong handler | ✅ Completed (2026-07-16) | `5d52364` |
| H31 | connect_signals() disabled | ✅ Completed (2026-07-16) | `5d52364` |
| H32 | rows_count_entry widget overwrite | ✅ Completed (2026-07-16) | `5d52364` |

---

## CODING_STANDARDS Compliance (V4)

| Standard | Status | Notes |
|----------|--------|-------|
| Project structure | ✅ | Uses template |
| STATE.md | ✅ | This file — updated 2026-07-16 |
| tests/ directory | ✅ | 85 test files, 95.5% coverage |
| Git workflow | ✅ | Using gamma branch |
| tuh environment | ✅ | Required for imports |
| Internal projects | ✅ | Uses nchantrs, pyffice, kahndor |
| CI/CD | ✅ | GitHub Actions configured |
| Documentation | ✅ | mkdocs + mkdocstrings |
| Inline TODO hygiene | 🟡 | 50 TODO + 63 NOTE across 27 files |

---

## Project Structure

```
nchantdoffice/
├── nchantdoffice/        # Main package
│   ├── __init__.py
│   ├── config.py         # Centralized configuration (100+ constants)
│   ├── models.py         # Tabset + document models (incl. lazy-load override)
│   ├── views.py
│   ├── nchantdoffice.py  # Main application entry
│   ├── dialogs/          # Document dialogs
│   ├── updates/          # Update handlers
│   ├── utilities/        # Helpers (canonical widget lookup, etc.)
│   ├── widgets/          # UI widgets (catalogs, documents, trees, etc.)
│   │   ├── config/       # Configuration widgets
│   │   ├── controls/     # Control widgets (toolbars, toolboxes)
│   │   ├── documents/    # Document widgets
│   │   ├── items/        # Item widgets (trees, diagrams)
│   │   └── panes/        # Pane widgets
│   └── wizards/          # Wizard dialogs
├── cmds/                 # CLI commands (run, install, launch)
├── tests/                # Test suites (unit/integration/e2e)
│   └── unit/             # 85 unit test files
├── .github/workflows/    # CI + docs deployment
├── docs/                 # Documentation
├── README.md             # Project overview
├── STATE.md              # This file
├── CHANGES.md            # Changelog
├── TODOs.md              # Active task inventory (H## + inline markers)
├── pyproject.toml        # Package metadata
└── uv.lock               # Locked dependencies
```

---

## Dependencies

| Project | Purpose | Status |
|---------|---------|--------|
| nchantrs | Core framework | ✅ Required — branch `gamma` @ `4073c12` |
| pyffice | Document automation | ✅ Integrated |
| kahndor | Configuration | ✅ Used |
| pycurity | Security | ✅ Available |
| micromole | Data utilities | ✅ Available |

---

## Testing

### Test Coverage: 95.5%

| Directory | Type | Count |
|-----------|------|-------|
| tests/unit/ | Unit Tests | 85 test files |
| tests/unit/fixtures/ | Test Fixtures | 21 files |

### Test Framework

- **Framework**: pytest
- **Config**: pytest.ini (tool.pytest in pyproject.toml)
- **Naming Convention**: `*TEST.py` suffix
- **Coverage**: 95.5% (sasquatch audit)

---

## Action Items

### Completed ✅ (2026-07)
- [x] Phase 1-7 implementation per AXN.md
- [x] Pyffice integration (12 document types)
- [x] CLI entry point (cmds/)
- [x] H24 — Toolbox Drawer Stale on Tab Switch
- [x] H25 — Catalog Tab Wrong Child Count (via nchantrs)
- [x] H27 — Image Save Mode (external storage)
- [x] H28 — Browser Pin Tab Persistence
- [x] H29 — Tree Node Drag-and-Drop (via nchantrs)
- [x] P2 — Lazy Tab Loading Audit
- [x] H30 — Row Height spinbox handler fix
- [x] H31 — connect_signals() re-enabled
- [x] H32 — row_height_entry widget naming fix
- [x] CI/CD pipeline (GitHub Actions)
- [x] Configuration module with logging
- [x] Unit test infrastructure

### Medium Priority
- [ ] Add remaining 13 PyfficeDocument types
- [ ] Improve docstrings
- [ ] M1 — Reduce 50 active inline TODOs
- [ ] M2 — Affiliate Link Data Updates
- [ ] M3 — Pro User Affiliate Opt-Out

---

## Code Quality Metrics

**Overall Score**: 60.26 (from sasquatch audit)

| Dimension | Score | Status |
|-----------|-------|--------|
| Testing | 100 | ✅ Pass |
| Documentation | 100 | ✅ Pass |
| CI/CD Config | 100 | ✅ Pass |
| Structure | 100 | ✅ Pass |
| Changelog | 100 | ✅ Pass |
| Memory | 100 | ✅ Pass |
| Speed | 100 | ✅ Pass |
| Import Cycle | 100 | ✅ Pass |
| Licenses | 100 | ✅ Pass |
| File Sizes | 100 | ✅ Pass |
| Git Workflow | 85 | ✅ Pass |

### Areas Needing Improvement

| Issue | Count | Severity |
|-------|-------|----------|
| Duplicate filenames | 35 | Medium |
| God classes | 18 | High |
| Feature envy | 23 | Medium |
| Parallel inheritance | 32 | Medium |
| Switch abuse | 24 | Medium |
| Data clumps | 11 | Medium |
| Type annotations | 7/6407 | High |

---

## Last Updated
- **Date**: 2026-07-16
- **Reviewer**: Orinbai (AI Agent)
- **Branch**: gamma
- **HEAD**: Merge commit — P0 fixes + upstream sync
- **CODING_STANDARDS**: V4 compliant
