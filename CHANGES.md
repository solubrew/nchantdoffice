# CHANGES.md - NchantdOffice Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- `.github/workflows/ci.yml` - GitHub Actions CI pipeline (lint, type-check, test, security, build)
- `.github/workflows/docs.yml` - GitHub Actions documentation deployment
- `nchantdoffice/config.py` - Centralized configuration module with 100+ constants
- `tests/unit/__init__.py` - Unit test package
- `tests/unit/test_config.py` - Configuration module tests

### Changed
- Project branch: gamma → orin-ws (per Git workflow)
- `nchantdoffice/__init__.py` - Added version and config exports

### Fixed
- Lambda antipattern in toolbar buttons (fixed variable capture)
- Signal inheritance in NchantdNewDocumentToolBar
- Incorrect super().__init__() calls in toolbar classes

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
