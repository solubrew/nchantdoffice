# NchantdOffice Project State

## Overview
- **Project**: NchantdOffice
- **Type**: Desktop GUI Application (PySide6)
- **Purpose**: Office automation suite with document management, calendar, contacts
- **Framework**: Built on nchantrs framework
- **Location**: `/home/solubrew/.senbai/workspace/projects/nchantdoffice`
- **Branch**: `gamma` (per CODING_STANDARDS Git workflow)
- **Version**: 0.0.1.0.1.4
- **Last Commit**: `0598d13` — "H24: deferred toolbox refresh + signal wiring + catalog-first-tab"

---

## Current Status: ACTIVE DEVELOPMENT

## CODING_STANDARDS Compliance

| Standard | Status | Notes |
|----------|--------|-------|
| Project structure | ✅ | Uses template |
| STATE.md | ✅ | Updated per review |
| tests/ directory | ✅ | 85 test files, 95.5% coverage |
| Git workflow | ✅ | Using gamma branch |
| CI/CD | ✅ | GitHub Actions configured |
| Documentation | ✅ | mkdocs + mkdocstrings |

---

## Recent Activity (2026-07-08)

| Commit | Description |
|--------|-------------|
| `0598d13` | H24 completed: deferred toolbox refresh, signal wiring, catalog-first-tab |
| `856d418` | debug charts add todos |
| `7835f16` | fix(H24): wire refresh_for_document on tab switch |
| `7f1672d` | fix(H24): lazy-init toolbox on tab switch |
| `81e7801` | implement notebook saving mechanisms |

---

## Project Structure

```
nchantdoffice/
├── nchantdoffice/        # Main package
│   ├── __init__.py
│   ├── models.py         # 89.9 KB - Core data models
│   ├── views.py
│   ├── nchantdoffice.py  # Application cloak
│   ├── config.py         # Centralized configuration (100+ constants)
│   ├── cli.py            # CLI interface
│   ├── dialogs/          # Dialog modules
│   ├── updates/          # Database updates
│   ├── utilities/        # Utility functions
│   ├── widgets/          # Widget modules
│   │   ├── config/       # Configuration widgets
│   │   ├── controls/     # Control widgets (toolbars, toolboxes)
│   │   ├── documents/     # Document widgets
│   │   ├── items/        # Item widgets (trees, diagrams)
│   │   └── panes/         # Pane widgets
│   └── wizards/          # Application wizards
├── cmds/                 # CLI commands (run, install, launch)
├── tests/                # Test suites
│   └── unit/             # 85 unit test files
├── docs/                 # mkdocs documentation
├── .github/workflows/     # CI/CD pipelines
├── pyproject.toml        # Package metadata
└── uv.lock               # Locked dependencies
```

---

## Dependencies

| Project | Purpose | Status |
|---------|---------|--------|
| nchantrs | Core framework | ✅ Required |
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

### Completed ✅
- [x] H24: Toolbox Drawer Stale on Tab Switch (commit `0598d13`)
- [x] P2: Lazy Tab Loading Audit (commit `0598d13`)
- [x] Phase 1-7 implementation
- [x] CI/CD pipeline (GitHub Actions)
- [x] Configuration module with logging
- [x] Unit test infrastructure

### In Progress 🔄
- [ ] H25: Catalog Tab Wrong Child Count
- [ ] M1: Inline TODO Inventory (87 locations across 27 files)

### High Priority
- [ ] H27: Nchantd Image Save Mode
- [ ] H28: Browser Pin Tab Doesn't Pin
- [ ] H29: Tree Node Drag-and-Drop Regression

### Medium Priority
- [ ] P1: Startup Performance (Glain Load)
- [ ] M2: Affiliate Link Data Updates
- [ ] M3: Pro User Affiliate Opt-Out

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
- **Reviewer**: Orin (AI Agent)
- **Branch**: gamma
- **HEAD**: `0598d13`
