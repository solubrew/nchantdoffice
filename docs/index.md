# Project Documentation

## Overview

Nchantd Office — the PySide6 desktop client for
[nchantdoffice.com](https://nchantdoffice.com). This is the
sibling repo to `nchantdoffice_com/` (which holds the server-side
Flask app + REST API). The desktop consumes the server's API and
implements the user-facing tier-gating + account-claim flow.

## Installation

```bash
pip install .
```

## Usage

```bash
# Add usage examples
```

## Substantive docs

- **[Desktop License Flow](DESKTOP_LICENSE_FLOW.md)** — the install
  store, entitlement cache, tier gate, remote client, claim flow,
  and startup-refresh orchestrator that shipped in the
  2026-08-24/25 milestone. The full operator + user + integration
  docs live in the sister repo `nchantdoffice_com/docs/`.

## Launch profiles (run-mode: dev | prod)

The desktop resolves every URL surface (license bootstrap,
embedded browser, ad rotation, account signup CTA) through a
single config-driven resolver (`nchantdoffice/utilities/urls.py`).
At launch the operator picks the active profile via one cfg key:

```python
# cmds/runNchantdOffice.py
cfg = {"run-mode": "prod"}     # default; routes every URL to nchantdoffice.com
nchantment("NchantdOffice", args, app, cfg, wizard)

cfg = {"run-mode": "dev"}      # routes every URL to the LAN docker
nchantment("NchantdOffice", args, app, cfg, wizard)
```

The dev profile targets `http://192.168.1.67:8081` (the operator's
LAN docker stack). See `nchantdoffice_com/docs/deploy-lan.md`
for how to bring the LAN stack up and `DESK T-NEW-053` in this
repo's `CHANGES.md [Unreleased]` for the design rationale.

The AST regression guard in `tests/utilities/test_urls_config.py`
pins the no-hardcoded-hostnames invariant — if a future commit
adds a `BASE_URL = "..."` constant outside the resolver, that
test fails.

## API Reference

See [Reference](reference.md) for auto-generated API documentation
(regenerate with `mkdocstrings` against `nchantdoffice/`).

## Embedded-browser page consistency

The desktop's embedded browser (`nchantrs_webviewer`) opens the
following URLs from the LAN docker / production site:

- `/registration` — Account tab in Settings
- `/whats_new` — changelog shown to paid users
- `/compare` — Pro upsell deep-link (the desktop's "Compare Plans" CTA)
- `/download` — desktop-binary download (email-gated)
- `/` — embedded-browser homepage (when the operator clicks "Home")
- `/marketing/cookies.html` etc. — footer links from the embedded
  pages (privacy, terms, cookies)

For all of these to render with the same nav, palette, and layout,
the server-side `nchantdoffice_com` site must use a single theme
for these pages. The current state is **two complete themes**
(`marketing` and `landing`) with a site-wide config switch
(`THEME_SITE` + `NCHANTDOFFICE_THEME_SITE` env var). The operator
flips the flag, restarts gunicorn, and the entire site re-renders
in the chosen theme.

Audit + plan + operator's guide:
- [`nchantdoffice_com/docs/theme-consolidation-audit_20260826.md`](https://github.com/solubrew/nchantdoffice_com/blob/gamma/docs/theme-consolidation-audit_20260826.md) — the original audit (3 coexisting layouts)
- [`nchantdoffice_com/docs/theme-site-switch.md`](https://github.com/solubrew/nchantdoffice_com/blob/gamma/docs/theme-site-switch.md) — the operator's guide for the site-wide switch (phases 1-4, all shipped)
- `/Users/solubrew/.hermes/plans/2026-08-26_183000-nchantdoffice-com-theme-site-switch.md` — the implementation plan

**Timeline of consolidation work** (2026-08-26, all in `nchantdoffice_com` on `gamma`):
- Commit `3c16c3b` — first step: migrated `/compare` + `/download` off the FAB default (Theme A baseline established)
- Commits `3b44739`, `5ac0de4`, `947cebc` — A/B harness primitives + dry-run demo theme (Theme A/B infrastructure)
- Commit `6410a62` — docs: audit the 3 coexisting layouts + A/B harness design
- Commits `6545138`, `68c59e5` — community + landing + auth + error pages migrated to Theme A (C7 + C8 — full consolidation to one theme)
- Then operator reversed direction: "switch all to the other template" + config-driven (not random A/B)
- Commits `4c363ba`, `d93cdf5`, `52227c6`, `95d2e13` — site-wide `THEME_SITE` flag + landing chrome + 50 body partials (25 pages × 2 themes) + operator's guide (phases 1-4 of the site-wide switch)

**Current state**: every page on the site renders in the chosen theme (set via `NCHANTDOFFICE_THEME_SITE=marketing|landing` in the env file or via the per-session `?theme=` query param for QA). The desktop's embedded browser sees one consistent look throughout the user journey.

## Cross-repo card index

The card IDs prefixed `DESK T-NEW-NNN` (this repo) and `COM T-NEW-NNN`
(sister repo) index the recent work. Both repos' `CHANGES.md`
files have an `[Unreleased]` section listing each card with its
commit SHA, scope, and follow-up operator actions.
