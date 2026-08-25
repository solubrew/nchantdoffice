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

## API Reference

See [Reference](reference.md) for auto-generated API documentation
(regenerate with `mkdocstrings` against `nchantdoffice/`).
