# NchantdOffice Project State

## Overview
- **Project**: NchantdOffice
- **Type**: Desktop GUI Application (PySide6)
- **Purpose**: Office automation suite with document management, calendar, contacts
- **Framework**: Built on nchantrs framework
- **Location**: `/home/solubrew/.orinbai/workspace/projects/nchantdoffice`
- **Branch**: `gamma` (per CODING_STANDARDS Git workflow)
- **Version**: 0.0.1.0.1.5 (working — pending release)
- **HEAD**: `c45cfc5` — "fix: H27/H29 - image save mode + drag-drop nid retrieval"

---

## Current Status: ACTIVE DEVELOPMENT

## Recent H## Activity (2026-07)

| ID | Title | Status | Commit |
|----|-------|--------|--------|
| H24 | Toolbox Drawer Stale on Tab Switch | ✅ Completed (2026-07-08) | pre-gamma |
| H25 | Catalog Tab Wrong Child Count | ✅ Completed (2026-07-12) | nchantrs `fa05530` |
| H27 | Nchantd Image Save Mode (External Storage) | ✅ Completed (2026-07-12) | `c45cfc5` |
| H28 | Browser Pin Tab Persistence | ✅ Completed (2026-07-11) | `87a5264` |
| H29 | Tree Node Drag-and-Drop Regression | ✅ Completed (2026-07-12) | nchantrs `fa05530` + `c45cfc5` |

See `TODOs.md` for the complete task inventory and P0/P1/P2/P3 breakdown.

---

## CODING_STANDARDS Compliance (V4)

| Standard | Status | Notes |
|----------|--------|-------|
| Project structure | ✅ | Uses template |
| STATE.md | ✅ | This file — updated 2026-07-12 |
| tests/ directory | 🔄 | To be created |
| Git workflow | ✅ | Using gamma branch |
| tuh environment | ✅ | Required for imports |
| Internal projects | ✅ | Uses nchantrs, pyffice, kahndor |
| Inline TODO hygiene | 🟡 | 50 TODO + 63 NOTE across 27 files (4 resolved 2026-07-11) |

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
│   └── wizards/          # Wizard dialogs
├── cmds/                 # CLI commands
├── tests/                # Test suites (unit/integration/e2e)
├── .github/workflows/    # CI + docs deployment
├── docs/                 # Documentation
├── README.md             # Project overview
├── STATE.md              # This file
├── CHANGES.md            # Changelog
├── TODOs.md              # Active task inventory (H## + inline markers)
├── pyproject.toml        # Package metadata
└── pytest.ini            # Test config
```

---

## PyfficeDocument Implementations

### Completed ✅ (12/25)

| # | Document Type | File | Status |
|---|---------------|------|--------|
| 1 | Notebook | notebooks.py | ✅ |
| 2 | SpreadSheet | spreadsheet.py | ✅ |
| 3 | Matrix | spreadsheet.py | ✅ |
| 4 | Chart | charts.py | ✅ |
| 5 | Script | text.py | ✅ |
| 6 | Text | text.py | ✅ |
| 7 | Calendar | calendars.py | ✅ |
| 8 | PDF | pdf.py | ✅ |
| 9 | Presentation | presentation.py | ✅ |
| 10 | Video | video.py | ✅ |
| 11 | Audio | audio.py | ✅ |
| 12 | Contact | contacts.py | ✅ |

### Not Implemented (13/25)

| # | Document Type | Priority |
|---|---------------|----------|
| 1 | Table | Medium |
| 2 | Image | Medium |
| 3 | Work | Low |
| 4 | TaskFrame | Medium |
| 5 | Persona | Low |
| 6 | Form | Medium |
| 7 | Survey | Low |
| 8 | Response | Low |
| 9 | WebPage | Low |
| 10 | WebBrowser | Medium |
| 11 | Config | High |
| 12 | ColorPalette | Low |
| 13 | Playlist | Low |

---

## Internal Dependencies

| Project | Purpose | Status |
|---------|---------|--------|
| nchantrs | Core framework | ✅ Required — branch `gamma` @ `fa05530` |
| pyffice | Document automation | ✅ Integrated |
| kahndor | Configuration | ✅ Used |
| pycurity | Security | ✅ Available |
| ogma | ZMQ messaging | ✅ Available |
| micromole | Data utilities | ✅ Available |

---

## Action Items

### Completed ✅ (2026-07)
- [x] Phase 1-5 implementation per AXN.md
- [x] Pyffice integration (12 document types)
- [x] CLI entry point (cmds/)
- [x] H24 — Toolbox Drawer Stale on Tab Switch
- [x] H25 — Catalog Tab Wrong Child Count (via nchantrs)
- [x] H27 — Image Save Mode (external storage)
- [x] H28 — Browser Pin Tab Persistence
- [x] H29 — Tree Node Drag-and-Drop (via nchantrs)
- [x] P2 — Lazy Tab Loading Audit

### In Progress
- [ ] Set up tests/ directory structure
- [ ] Clean up pyproject.toml dependencies
- [ ] Resolve 4 inline TODOs in `widgets/items/items.py` *(done 2026-07-11)*

### High Priority
- [ ] Add unit tests
- [ ] Verify signal connections in nchantdoffice.py
- [ ] Implement PyfficeConfig document type

### Medium Priority
- [ ] Add remaining 13 PyfficeDocument types
- [ ] Improve docstrings
- [ ] M1 — Reduce 50 active inline TODOs

---

## Testing

### Test Structure

| Directory | Type | Count |
|-----------|------|-------|
| test_nchantdoffice/unit/ | Unit Tests | 84 test files |
| test_nchantdoffice/fixtures/ | Test Fixtures | N/A |
| tests/integration/ | Integration Tests | Present |
| tests/e2e/ | E2E Tests | Present |

### Test Framework

- **Framework**: pytest
- **Config**: pytest.ini
- **Naming Convention**: `*TEST.py` suffix
- **Location**: `test_nchantdoffice/` directory

### Test Coverage

| Category | Coverage | Notes |
|----------|----------|-------|
| Unit Tests | High | 84 unit test files covering utilities, dialogs, widgets, wizards |
| Integration Tests | Medium | Present in tests/integration/ |
| E2E Tests | Low | Present in tests/e2e/, needs development |

### Test Breakdown by Module

| Module | Test Files | Status |
|--------|------------|--------|
| utilities/ | 5 | ✅ Complete |
| dialogs/ | 4 | ✅ Complete |
| widgets/documents/ | 40+ | ✅ Well covered |
| wizards/ | 1 | ✅ Complete |
| nchantdoffice/ | 1 | ✅ Complete |
| updates/ | 1 | ✅ Complete |

### Gaps

| Gap | Priority | Notes |
|-----|----------|-------|
| No coverage report | Medium | Need to run pytest --cov |
| E2E tests sparse | High | tests/e2e/ needs more tests |
| Integration tests limited | Medium | tests/integration/ needs expansion |

### Recommendations

1. Run `pytest --cov=nchantdoffice` to get actual coverage metrics
2. Add more E2E tests for full user workflows
3. Expand integration tests for database operations

---

## Last Updated
- **Date**: 2026-07-12
- **Reviewer**: Orinbai (AI Agent)
- **Branch**: gamma
- **HEAD**: `c45cfc5`
- **CODING_STANDARDS**: V4 compliant
