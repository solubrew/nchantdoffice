# CLI Reference

NchantdOffice provides a GUI-based office suite application. CLI usage is primarily for development and testing.

## Usage

```bash
python -m nchantdoffice [arguments]
# or
python __main__.py [arguments]
```

## Arguments

| Argument | Type | Required | Description | Default |
|----------|------|----------|-------------|---------|
| `tab_name` | TEXT | No | Specific tab to open | None |
| `mode` | TEXT | No | Mode: 'scratch' or 'continue' | wizard |

## Commands

### Development Modes

| Mode | Description |
|------|-------------|
| `scratch` | Create new file |
| `continue` | Continue existing file |
| (default) | Use wizard to setup |

## Examples

```bash
# Launch with setup wizard
python -m nchantdoffice

# Open specific tab in scratch mode (create new)
python -m nchantdoffice scratch

# Continue existing file
python -m nchantdoffice continue

# Open specific tab
python -m nchantdoffice scratch documents
```

## Architecture

NchantdOffice uses a modular architecture:
- **Widgets**: Document views, workbooks, tabs
- ** Wizards**: Application startup wizard
- **Cloak**: Application wrapper for initialization

## Environment

The application requires:
- SENBOT_AGENT_NAME environment variable (for workspace paths)
- Various Nchantrs dependencies
