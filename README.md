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

### Pointing at a local test server (T-NEW-070)

As of 2026-08-11, **the desktop no longer reads env vars** for
server URL / cache dir / referral salt / software-render mode
(per the user's hard-break directive). All runtime config now
comes from a single user config file:

```yaml
# ~/.config/nchantdoffice/config.yaml  (XDG — global default)
dev_mode: true                          # points at http://localhost:5000
server:
  url: "http://localhost:5000"
  timeout: 3
cache:
  dir: /tmp/nchantdoffice-test           # override cache for tests
webengine:
  software_render: true                 # only on Linux GPU issues
user:
  uuid: ...                              # auto-generated on first launch
```

A per-project override file `./nchantdoffice.yaml` (cwd) takes
precedence over the XDG file. See `nchantdofficeATNRG/dev-setup.md`
for the full quick-start and `tests/test_user_config.py` for the
contract pin (10 tests).

The status bar shows a `[DEV]` badge when `dev_mode: true` is
active — operators can see at a glance whether they're hitting
prod or a local server.

## Recent changes (2026-08)

Cross-repo work that landed 2026-08-11:

- **T-NEW-070 hard-break**: removed env-var reads for
  `NCHANT_API_BASE`, `NCHANT_DATA_DIR`, `NCHANT_REFERRAL_SALT`,
  `NCHANT_WEBENGINE_SOFTWARE`. Replaced with config-file reads.
  Added `nchantdoffice/utilities/user_config.py` (XDG resolver
  with cwd override). Reorganized launcher imports so
  `crow.crowLoad` runs first (sys.path setup before Qt).
  See T-DESK-066 card in `TODOs.md` for the full commit trail.
- **T-NEW-042 anti-abuse + attribution + NchantdOfficeUser**:
  device-fingerprint anti-abuse check (30-day window),
  first-touch attribution (30-day cookie), 3-opens-minimum
  anti-abuse rule (MIN_APP_OPENS=3), `record_app_open()`
  per-calendar-day idempotency. NchantdOfficeUser is now
  properly integrated as the canonical user UUID source
  (DESK-0 — replaces the hardcoded `application_NCD` string).
  Real-world crash from 2026-08-11 14:21 (T-NEW-042b) fixed:
  `self.device = Device()` set before user instantiation.
- **T-NEW-070 DESK-5 [DEV] badge**: status bar shows `[DEV]`
  badge whenever `dev_mode: true` is in the config — operators
  can see at a glance whether they're hitting prod or a local
  server.
- **T-NEW-044 UI-1** (referral panel uses server-side eligibility):
  `ReferralAPIClient.fetch_payout_eligibility(user_id)` calls
  `GET /api/v1/referral/payout-eligibility/<user_id>`.
  `NchantdOfficeReferralPanel._build_earnings_card` renders
  4 distinct states (no data / free_tier / below_threshold /
  eligible). Replaces the client-side `pending >= min_payout`
  shortcut that ignored tier-gating — a free-tier user with
  $30 pending would have been shown "Eligible for payout"
  before this fix. Commit `e8d10d1`.
- **T-NEW-044 UI-2** (ad-tab-free hours fallback): 4 new helpers
  in `user_config.py` (`get_ad_tab_free_until`,
  `set_ad_tab_free_hours`, `clear_ad_tab_free_hours`,
  `is_ad_tab_free_active`). `NchantdOfficeAdTab
  ._is_visible_for_user()` checks `is_ad_tab_free_active()`
  FIRST — hides the Ad tab for free-tier referrers with an
  active grant (per AppReferralSpec §10). Commit `e4838f3`.
- **T-NEW-044 UI-3** (affiliate panel for Stripe Connect): new
  `nchantdoffice/widgets/config/affiliate_panel.py` with
  `NchantdOfficeAffiliatePanel` widget — "Connect Stripe
  Account" button + status label. On click → POST
  `/api/v1/affiliate/connect-stripe` → opens the Stripe-hosted
  onboarding URL in the user's browser via `webbrowser.open()`.
  Commit `ded73fc`. Server endpoint: `20673f4`.
- **T-NEW-045 WIRE-1** (desktop grant trigger):
  `NchantdOfficeReferralPanel._maybe_grant_ad_tab_free_hours()`
  computes hours = floor(pending_total * 24 / 5) (24h per $5
  of pending credit, AppReferralSpec §10), skips if
  `is_ad_tab_free_active()` is True (no stacking), and is
  called from `_fetch_payout_eligibility` when
  `reason='free_tier'`. Commit `b420a06`.

The full cross-repo log (every commit, every T-NEW card,
every test total) lives at
[`nchantdofficeATNRG/cross-repo-changelog.md`](
https://gitlab.example.com/nchantdofficeATNRG/-/blob/gamma/cross-repo-changelog.md)
— the canonical "current reality" anchor for all 3 repos.

Latest commit on `gamma`:
[`b420a06 feat(desktop): grant trigger for ad-tab-free hours (T-NEW-045 WIRE-1)`]

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
