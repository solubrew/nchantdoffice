# NchantdOffice
<img width="1921" height="1043" alt="image" src="https://github.com/user-attachments/assets/aedb19af-b112-47b5-833f-1e8abab62a1c" />

> Office automation suite built on the nchantrs framework

## Project overview

NchantdOffice is a desktop application providing office automation capabilities including document management, calendar, contacts, and more. Built on PySide6 with deep integration into the nchantrs ecosystem.

## Features

- **Document Management**: Support for 12+ document types (Notebook, Spreadsheet, Calendar, PDF, etc.)
- **Calendar Integration**: Full calendar views and scheduling
- **Contact Management**: Rolodex-style contact storage
- **Browser Integration**: Built-in web browser with tab pinning and session persistence
- **Tree Navigation**: Drag-and-drop tree nodes with persistent hierarchy
- **Image Handling**: Canonical external file storage with deprecation warnings for legacy modes
- **Agent-Ready**: Structured output (JSON/YAML) for AI agent integration
- **CLI Interface**: Programmatic access via `nchantdoffice` CLI

## Quick start

Get a working nchantdoffice setup in 3 commands:

```bash
# 1. Install with the recommended extras (internal SB packages)
pip install -e .[internal]

# 2. Launch the GUI
nchantdoffice

# 3. Or use the CLI for scripted operations
nchantdoffice-cli --help
```

## Installation

## Usage

### GUI Application

```bash
nchantdoffice
```

### CLI

```bash
nchantdoffice-cli --help
```

## Development

### Setting up a development environment

```bash
# Clone the source repo (uses the gamma branch per team convention)
git clone -b gamma file:///mnt/overse/SBST01/vein/GitVein/nchantdoffice.git
cd nchantdoffice

# Create / activate a virtualenv (project's preferred path)
python -m venv .venv && source .venv/bin/activate

# Install in editable mode with dev + internal extras
pip install -e .[internal]

# Run the test suite (continue-on-collection-errors is set for aspirational tests)
pytest tests/ --continue-on-collection-errors
```

### Code style

- **Class naming**: All public widget / document / manager classes are named ``Nchantd<Document>`` (preserved per user direction — do not rename).
- **Logging**: Use ``kahndor.logma.Logma(__name__)`` — never ``print()``.
- **Configuration**: Read project-wide constants from ``nchantdoffice.config``.
- **Internal projects**: All SB packages (``nchantrs``, ``pyffice``, ``ladyol``, ``senbai``, ``kahndor``, ``glain``) are internal — never substitute PyPI alternatives.

### Running sasquatch

The auditor is invoked from any project root via:

```bash
sasquatch analyze -p . --skip-pii-secrets
```

Score is written to ``PROJECT_TRACKER.yaml`` and ``FALCON_TEST.yaml``.

### Active work

See [TODOs.md](./TODOs.md) for the active task inventory and H## tracker.

## Project Structure

```
nchantdoffice/
├── nchantdoffice/        # Main package
│   ├── __init__.py
│   ├── cli.py             # CLI entry point
│   ├── config.py          # Centralized configuration (100+ constants)
│   ├── models.py          # Tabset + document models
│   ├── views.py
│   ├── nchantdoffice.py   # Main application
│   ├── _data_/            # Config and resources
│   ├── dialogs/           # Document dialogs
│   ├── updates/           # Update handlers
│   ├── utilities/         # Helpers and utilities
│   ├── widgets/           # UI widgets
│   └── wizards/           # Wizard dialogs
├── cmds/                  # CLI commands and run scripts
├── tests/                 # Test suites (unit/fixtures)
├── docs/                  # API and reference docs
├── .github/workflows/     # CI + docs deployment
├── STATE.md              # Current project state
├── CHANGES.md            # Changelog
├── TODOs.md              # Active task inventory (H## tracker)
├── pyproject.toml        # Package metadata
└── pytest.ini            # Test config
```

## Recent Bug Fixes (2026-07)

| ID | Title | Commit |
|----|-------|--------|
| H24 | Toolbox Drawer Stale on Tab Switch | pre-gamma |
| H25 | Catalog Tab Wrong Child Count | nchantrs `fa05530` |
| H27 | Image Save Mode (External Storage) | `c45cfc5` |
| H28 | Browser Pin Tab Persistence | `87a5264` |
| H29 | Tree Node Drag-and-Drop Regression | nchantrs `fa05530` + `c45cfc5` |

See [TODOs.md](./TODOs.md) for the complete task inventory.

## Documentation

- [TODOs.md](./TODOs.md) - Active task inventory and H## tracker
- [STATE.md](./STATE.md) - Current development status
- [CHANGES.md](./CHANGES.md) - Changelog
- [CLI.md](./CLI.md) - CLI reference
- [CODING_STANDARDS.md](./CODING_STANDARDS.md) - Development standards

## Dependencies

- **Core**: nchantrs, pyffice, kahndor
- **GUI**: PySide6
- **Data**: pandas, sqlalchemy

## License

See [LICENSE](./LICENSE) and [license_dependencies.txt](./license_dependencies.txt)
