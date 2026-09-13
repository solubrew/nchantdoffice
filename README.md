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
- **Per-user quotas (T-NEW-129, 131, 132, 135, 137)**: app_user
  seeded on first boot; child-node creates denied under
  Home/Journal/Settings; tab creates denied in the Settings tree;
  100-node cap pre-flight-checks both manual creates and `.pyof`
  imports, redirecting to the Nchantd Account upsell page when
  hit.

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

## Settings tab and login persistence

The Settings tab embeds a QtWebEngine browser whose target URL is
always the server's `/user-account/home` (`urls.user_account_url()`,
XDG-overridable). The server decides what the user sees:

- Valid session cookie → the account dashboard
- No/expired cookie → 302 to `/auth/login?next=/user-account/home`
  (that page carries a "Create Account" link for fresh installs)

The session cookie itself is a 30-day persistent Flask session
(`session.permanent = True` server-side); ticking "Remember me" on
the login form additionally issues a 180-day `remember_token`.
Both survive desktop restarts and container rebuilds.

**Do not** try to read the QtWebEngine cookie store from desktop
code — PySide6's `QWebEngineCookieStore` has no public synchronous
read API, and the `cookieAdded` signal path is racy (see
CHANGES.md T-NEW-140 history). For a programmatic identity check
use `GET {server}/api/auth/whoami` (200 = logged in, 401 = not),
which is exactly what the embedded browser sends cookies to.

Pro users (`user.has_pro`) land on `urls.whats_new_url()` instead —
deliberate changelog view, no upsell.

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
dev_mode: false                         # true points at http://localhost:5000 (Flask dev server, no docker)
server:
  url: "https://nchantdoffice.com"     # prod default; resolve via urls.py
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
[`nchantdofficeATNRG/cross-repo-changelog.md`](../nchantdofficeATNRG/cross-repo-changelog.md)
— the canonical "current reality" anchor for all 3 repos
(`nchantdofficeATNRG/`, `nchantdofficeCOM/`, this repo). Path
is a sibling repo in the same `/home/solubrew/.hermes/projects/`
directory; the older `gitlab.example.com` URL was a placeholder
that did not resolve and has been retired.

Latest verified local commit on `gamma`:
[`07fc18b fix(pyof): guard bare Qt parent access`]. The branch also
contains the 2026-08-17 T-NEW-117, T-NEW-122, and chart-segfault
fixes documented in `CHANGES.md`.

**Reality-anchor update (2026-08-19, gamma `655f36b`):** the
2026-08-18 / 2026-08-19 sweep closed the **T-NEW-144b umbrella**
(12 children, multi-format `set_location` cleanup across
13 widget classes) and shipped **T-NEW-152 / 154 / 155 / 156 /
157 / 158** (P1 operator-asks: ToolBox refresh, add_tab
timing, Ctrl+D date shortcut, underscore priority sort,
active_tab_position clamp, T-NEW-XXX → T-NEW-158 marker fix).
Plus **T-NEW-169 / 170 / 171 / 172** filed 2026-08-19 (standalone
2-pane boot, pullable-tab dialog, performance campaign,
async via pyularity). See [`CHANGES.md`](./CHANGES.md) for the
new `[Unreleased]` anchor that consolidates these 16+
commits between `18336e5` and `655f36b`. T-NEW-only test files
report **307 passed / 0 failed** at this branch tip.

**Reality-anchor update (2026-09-12, gamma `64ee4c4`):** the
Ad tab gained a **telemetry emitter** (T-NEW-167) —
`nchantdoffice/widgets/documents/atnrg/ad_telemetry.py`
(`AdTabTelemetry`) emits `rotation` (layout load), `click`
(Get Pro interception), and 30 s `session_tick` events to the
server's `POST /api/ads/telemetry/events` (best-effort batch,
max 200), and appends `inst/uid/ut/stk/top` params to the slim
URL so page-side beacons carry the desktop's stack context.
Identity = `desktop_uuid` (server-issued) → `install_id`
fallback. 17 tests in
`tests/test_ad_tab_telemetry_tnew167.py`; the stale
`initModel_defaults_to_stack5_not_stack2` pin was renamed to
assert `LAYOUT_ROTATE` (T-NEW-164's contract). Server side
landed in `nchantdoffice_com@a741145`.

For a repo-local cross-reference of every shipped + filed
T-NEW card with commit SHAs, see
[`CHANGES.md`](./CHANGES.md) `[Unreleased]` block.

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

> **Snapshot of the `gamma` branch HEAD `5b6397e` (2026-08-16).**
> For an up-to-date tree see `directory_tree.md` (note: that
> file's body is a 2026-07-16 snapshot — regenerate with
> `tree -L 4 -I '__pycache__|*.egg-info|node_modules'`
> before relying on it).

```
nchantdoffice/
├── __main__.py            # python -m nchantdoffice entry point
├── nchantdoffice/         # Main package
│   ├── __init__.py        # version + APP_* constants
│   ├── __main__.py
│   ├── cli.py             # CLI command surface (used by cmds/)
│   ├── models.py          # Tabset + document models
│   ├── views.py
│   ├── nchantdoffice.py   # Main application (NchantdOfficeCloakModel)
│   ├── _data_/            # Config and resources
│   ├── dialogs/           # Document dialogs
│   ├── sync/              # app<->doc sync helpers
│   ├── updates/           # Update handlers (checker, db)
│   ├── utilities/         # Helpers (constants, users, config, pyof_import, …)
│   ├── widgets/           # UI widgets
│   └── wizards/           # Wizard dialogs
├── cmds/                  # CLI commands and run scripts
├── tests/                 # Test suites (1130+ entries — integration + unit + fixtures + qt_parent)
├── docs/                  # API and reference docs
├── .github/workflows/     # CI + docs deployment
├── AXN.md                 # Account-experience notes
├── BUGs.md                # Historical stack-trace archive
├── CHANGES.md             # Changelog
├── CI_CD.md               # CI/CD pipeline reference
├── CLI.md                 # CLI reference
├── CODING_STANDARDS.md    # V4 standards compliance
├── directory_tree.md      # File-tree snapshot (2026-07-16)
├── FALCON_TEST.yaml       # Last sasquatch-falcon test run summary
├── LICENSE                # MIT
├── license_dependencies.txt
├── profile.html           # SB workspace profile export
├── profile.json           # SB workspace profile export
├── PROJECT_TRACKER.yaml   # Last full sasquatch audit
├── pyproject.toml         # Package metadata (version 0.0.1.0.1.4)
├── pytest.ini             # Test config
├── README.md              # This file
├── testing-report_20260817.md  # Latest live-testing issues
└── TODOs.md               # Active task inventory (T-NEW-NNN tracker)
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

- [TODOs.md](./TODOs.md) - Active task inventory and T-NEW-NNN tracker
- [CHANGES.md](./CHANGES.md) - Changelog (current `gamma` `[Unreleased]` block mirrors TODOs.md)
- [CLI.md](./CLI.md) - CLI reference
- [CI_CD.md](./CI_CD.md) - CI/CD pipeline reference
- [CODING_STANDARDS.md](./CODING_STANDARDS.md) - V4 standards compliance
- [directory_tree.md](./directory_tree.md) - File-tree snapshot (2026-07-16, regenerate before relying)
- [BUGs.md](./BUGs.md) - Historical stack-trace archive (read-only)
- [testing-report_20260817.md](./testing-report_20260817.md) - Latest live-testing issues

## Dependencies

- **Core**: nchantrs, pyffice, kahndor, pycurity, subtrix
- **GUI**: PySide6
- **Data**: pandas (DataFrames only — used in calendars.py, filesystems.py, atnrg/browsers.py); **persistence via `squirl` + `micromole` (NOT SQLAlchemy — this is a hard working agreement).**

## License

See [LICENSE](./LICENSE) and [license_dependencies.txt](./license_dependencies.txt)
