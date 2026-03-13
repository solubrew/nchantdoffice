# NchantdOffice

> Office automation suite built on the nchantrs framework

## Overview

NchantdOffice is a desktop application providing office automation capabilities including document management, calendar, contacts, and more. Built on PySide6 with deep integration into the nchantrs ecosystem.

## Features

- **Document Management**: Support for 12+ document types (Notebook, Spreadsheet, Calendar, PDF, etc.)
- **Calendar Integration**: Full calendar views and scheduling
- **Contact Management**: Rolodex-style contact storage
- **Agent-Ready**: Structured output (JSON/YAML) for AI agent integration
- **CLI Interface**: Programmatic access via `nchantdoffice` CLI

## Installation

```bash
pip install -e .
```

## Usage

### GUI Application

```bash
nchantdoffice
```

### CLI

```bash
nchantdoffice-cli --help
```

## Project Structure

```
nchantdoffice/
├── nchantdoffice/     # Main package
├── cmds/              # CLI commands
├── test_nchantdoffice/ # Tests
├── tests/             # Test suites (unit/integration/e2e)
├── STATE.md           # Current project state
└── CHANGES.md         # Changelog
```

## Documentation

- [AXN.md](./AXN.md) - Integration plan and status
- [STATE.md](./STATE.md) - Current development status
- [CHANGES.md](./CHANGES.md) - Changelog

## Dependencies

- **Core**: nchantrs, pyffice, condor
- **GUI**: PySide6
- **Data**: pandas, sqlalchemy

## License

See [LICENSE](./LICENSE) and [LICENSE.rst](./LICENSE.rst)
