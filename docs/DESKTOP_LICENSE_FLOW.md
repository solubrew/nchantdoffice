# Nchantd Office — Desktop License Flow

> **Sentinel doc** — the rest of this repo's `docs/` is
> `mkdocs.yml` auto-generated API reference (regenerate via
> `mkdocstrings` against `nchantdoffice/`). The substantive
> design + usage docs for the desktop license module live in
> `nchantdoffice_com/docs/` (the sister server repo). This file
> exists so anyone landing in *this* repo can find them.

**Repo:** `nchantdoffice/` (PySide6 desktop app)
**Module:** `nchantdoffice/license/`
**Shipped:** 2026-08-24/25, 5 commits DESK T-NEW-046 through DESK T-NEW-050

## Where the authoritative docs live

| Doc | Where | Purpose |
|---|---|---|
| Server-side **operator manual** | `nchantdoffice_com/docs/OPERATOR_DESKTOP_INSTALL.md` (sister repo) | Deployment, key rotation, revoke, debugging, smoke harness, rollback |
| Server-side **user guide** | `nchantdoffice_com/docs/USER_DOWNLOAD_INSTALL.md` (sister repo) | Download + install + claim walkthrough for end users |
| Server-side **integration plan** | `nchantdoffice_com/docs/desktop-integration-plan.md` (sister repo, §10) | The full endpoint + table + module reference for the new surface |
| **Master plan** | `nchantdoffice_com/.hermes/plans/2026-08-24_1200-desktop-install-entitlement-flow.md` | The 7-phase plan that drove the milestone (Phase A–G, server + desktop) |
| **Commit trail (server)** | `nchantdoffice_com/CHANGES.md` `[Unreleased] — 2026-08-24` | 14 feature commits (COM T-NEW-046 → COM T-NEW-052) + 3 docs |
| **Commit trail (desktop, this repo)** | `git log --oneline 9021f33^..64f5a9e` | 5 feature commits (DESK T-NEW-046 → DESK T-NEW-050) |

## Desktop-side module map

```
nchantdoffice/license/
├── __init__.py
├── install_store.py        # DESK T-NEW-046+048  — salt.bin + install.bin (PBKDF2 hardware-key)
├── entitlement_cache.py    # DESK T-NEW-047      — Fernet-encrypted JSON cache
├── tier_gate.py            # DESK T-NEW-047      — @requires_tier('pro') decorator + tier hierarchy
├── remote.py               # DESK T-NEW-048      — aiohttp client (bootstrap + refresh + sync wrappers)
├── claim_flow.py           # DESK T-NEW-049      — magic-link issue + deep-link consume
└── startup_refresh.py      # DESK T-NEW-050      — refresh_if_needed() orchestrator

nchantdoffice/widgets/config/accounts.py   # DESK T-NEW-049 — sync_with_server replaced with real ClaimFlow
nchantdoffice/views.py                    # DESK T-NEW-050 — startup wires InstallStore + LicenseRemote + refresh_if_needed

tests/license/                             # 62 tests passing + 1 pre-existing skip (nchantrs env)
```

## Per-OS install behaviour

| OS | Machine-id source |
|---|---|
| Linux | `/etc/machine-id` (fallback `/proc/sys/kernel/random/boot_id`) |
| macOS | `IOPlatformUUID` via `ioreg -rd1 -c IOPlatformExpertDevice \| awk '/IOPlatformUUID/ {print $3}'` |
| Windows | `HKLM\SOFTWARE\Microsoft\Cryptography\MachineGuid` via `winreg` |

Tests monkeypatch `_read_os_machine_id` so the derivation is deterministic in CI.

## Open questions for the desktop team (from the original plan §8)

These remain valid and aren't addressed by the 2026-08-24 milestone:

1. **Auth persistence (per-user session tokens):** the install module
   identifies the machine but does not persist the user's session
   token across app restarts. The login flow still re-prompts.
2. **Telemetry heartbeat:** `DesktopInstallModel.mark_seen()` is the
   foundation; the desktop doesn't yet POST heartbeats back to the
   server on a schedule.
3. **Ad distribution, content sync, affiliate sync:** the original
   `docs/desktop-integration-plan.md` §2.4–§2.6 are deferred.

## Verification

```bash
# Unit + integration tests (62 pass + 1 pre-existing skip)
cd /home/solubrew/.hermes/projects/nchantdoffice
/home/solubrew/ENVs/senbot/bin/python -m pytest tests/license/ -v

# End-to-end smoke (in sister repo — exercises the contract both sides)
cd /home/solubrew/.hermes/projects/nchantdoffice_com
bash scripts/dev/run-e2e-desktop-install.sh
```

## Status

- `gamma` head: `64f5a9e` (this repo) / `31ee9d1` (sister repo)
- Both repos clean (`gamma...origin/gamma`)
- Pre-existing uncommitted modification on `Caddy.dockerfile` in the
  sister repo — left untouched per house rule
- The operator's `c142344 add columns redundance` + the rebased
  `8920abf` are in `gamma`'s history (sister repo merge `e319796` brought
  them in) — they pre-date this milestone and are unrelated to the
  license flow