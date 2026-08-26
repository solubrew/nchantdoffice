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

## Cross-repo card index

The card IDs prefixed `DESK T-NEW-NNN` (this repo) and `COM T-NEW-NNN`
(sister repo) index the recent work. Both repos' `CHANGES.md`
files have an `[Unreleased]` section listing each card with its
commit SHA, scope, and follow-up operator actions.
