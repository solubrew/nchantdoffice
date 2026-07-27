# CI/CD Documentation

This document describes the Continuous Integration / Continuous Deployment
pipeline for nchantdoffice.

## Overview

NchantdOffice is a Qt-based GUI application. Its CI/CD pipeline focuses on
smoke tests (does the GUI launch?), static analysis, and security audits
rather than a full test matrix.

## Pipeline Stages

1. **Lint & Format** — black + ruff formatting checks
2. **Smoke Tests** — Launch the GUI under `xvfb` to verify imports
3. **Security Audit** — bandit + sasquatch auditor
4. **Build** — Package assembly via setuptools
5. **Sign** — GPG sign the wheel/sdist for distribution

## Local Validation

```bash
# Run smoke test
xvfb-run python -m nchantdoffice --version
# Lint
black . && ruff check .
# Audit
sasquatch analyze -p . --skip-pii-secrets
```

## CI Configuration

CI runs smoke tests on Linux (with xvfb) and macOS, plus Windows for
native deployment. Coverage and audit artifacts are uploaded as build
artifacts for inspection.

## Secrets

- All secrets stored in PyKeyStore (encrypted at rest)
- No environment variables used for credentials
- The PyKeyStore passphrase prompt is deliberate (TTY-bound at runtime)