# CLI Reference

## Purpose

NchantdOffice is a GUI-based office suite application providing
document, spreadsheet, presentation, and drawing tools — built on
the Qt framework and integrated with the broader nChantrs /
shieldface ecosystem. The CLI exists primarily to launch the GUI
in development or test mode, and to provide a programmatic entry
point via `python -m nchantdoffice`.

For everyday interaction, prefer launching the GUI. The CLI is
suitable for headless CI runs (smoke tests), debugging, and
embedding the application in scripts.

## Usage

```bash
# Launch the GUI (recommended for day-to-day use)
python -m nchantdoffice [arguments]
# or
python __main__.py [arguments]
# or, from the cmds/ directory (legacy launchers with extra
# QtWebEngine render diagnostics + software-render lever):
python cmds/runNchantdOffice.py [arguments]
# or the convenience wrappers at repo root:
./runNchantdOffice.py [arguments]
# All of the above (no subcommand) boot the full NchantdOffice
# main app unchanged. To boot a SINGLE-document 2-pane shell
# use the new `document` subcommand (T-NEW-169, shipped 2026-08-19):
./runNchantdOffice.py document --type <doc-type> [--path <file>]
# See the `document` Subcommand section below for details.
```

## `document` Subcommand (T-NEW-169, 2026-08-19)

The `document` subcommand boots a **standalone 2-pane minimal
shell** for a single document type — useful when the operator
wants a focused workspace without the full main-app chrome, or
when dragging the standalone shell onto a second monitor (via
T-NEW-170 once that card ships).

**Usage:**

```bash
runNchantdOffice.py document --type <name> [--path <file>]
```

**Arguments:**

| Argument | Type | Required | Choices | Default | Description |
|----------|------|----------|---------|---------|-------------|
| `--type` | TEXT | Yes | `script`, `notebook`, `image`, `form` | — | Document type to instantiate. The dispatch maps each name to the matching `NchantdOffice*` class. |
| `--path` | TEXT | No | file path | None | Optional pre-load path. Threaded through the document's `open_file()` (best-effort; errors are logged, not raised). For notebook this can be a `.pyof` file path. |

**Document types (operator-approved priority order, T-NEW-169 WIRE-3):**

| Type       | Opens                                       |
|------------|---------------------------------------------|
| `script`   | A `NchantdOfficeScript` editor window       |
| `notebook` | A `NchantdOfficeNotebook` Jupyter window    |
| `image`    | A `NchantdOfficeImage` viewer window        |
| `form`     | A `NchantdOfficeForm` editor window         |

**Examples:**

```bash
# Boot a Script editor standalone
./runNchantdOffice.py document --type script

# Boot a Notebook standalone pre-loaded with a .pyof file
./runNchantdOffice.py document --type notebook --path ~/my_session.pyof

# Boot an Image viewer standalone
./runNchantdOffice.py document --type image --path ~/photo.png
```

**Behaviour:** When `--type` matches a known document class, the
standalone shell constructs that class lazily (via
`importlib.import_module` + `getattr`) inside the new
`NchantdDocumentStandaloneWindow.initView` (in
`nchantdoffice/nchantdoffice.py`). The class is mounted as the
central widget and a placeholder right-side dock is attached so
the operator gets the full 2-pane shell layout. If the dispatch
fails (unknown `--type` or import error), the standalone shell
falls back to a placeholder central widget with a logged
warning.

**Default behaviour (no subcommand):** the launch boots the
full `NchantdOfficeCloak` main app — unchanged from before
T-NEW-169. The `document` subcommand is additive.

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
- **Wizards**: Application startup wizard
- **Cloak**: Application wrapper for initialization
  (`NchantdOfficeCloakModel` in `nchantdoffice/nchantdoffice.py`)

## Environment

The application requires no env vars at runtime since the
**T-NEW-070 hard-break** (2026-08-11). All runtime config now
comes from a single user config file:

- **Global**: `~/.config/nchantdoffice/config.yaml` (XDG default)
- **Per-project override**: `./nchantdoffice.yaml` (cwd)

Config keys: `dev_mode`, `server.{url,timeout}`, `cache.dir`,
`webengine.software_render`, `user.uuid`. See
[`README.md`](./README.md) §"Pointing at a local test server"
and `tests/test_user_config.py` for the contract pin (10 tests).

**The PyKeyStore passphrase is the one env-var bypass** that
remains in the codebase (per the user's working agreement): set
`PYKEY_PASSPHRASE` for non-TTY deploys; for TTY-bound runs the
prompt is deliberate (and `EOFError` is the correct non-TTY
behaviour).

**Deprecated env vars (removed by T-NEW-070):**
`NCHANT_API_BASE`, `NCHANT_DATA_DIR`, `NCHANT_REFERRAL_SALT`,
`NCHANT_WEBENGINE_SOFTWARE`. Setting them has no effect.

## Test runner

```bash
# Full pytest (headless Qt6)
QT_QPA_PLATFORM=offscreen /home/solubrew/ENVs/sasquatch/bin/python \
  -m pytest tests/ --continue-on-collection-errors -q
```

Or via the legacy `cmds/runTest.py` wrapper for the same
flags + extra sasquatch-falcon hooks.

## Update check

The `UpdateChecker` runs on the user-configurable interval
(T-NEW-059, default 6 hours). Set
`force_ad_tab_free_hours` / `dismiss_version` via the
`Settings/Interface` tab, or programmatically via
`nchantdoffice.updates.checker.dismiss_version(days=7)` and
the `set_ad_tab_free_hours` helper. See T-NEW-058/059/060 in
[`CHANGES.md`](./CHANGES.md) for the full commit trail.