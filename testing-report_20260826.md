# Testing Report — 2026-08-26

> Live testing on the operator's LAN (192.168.1.67) after the
> 2026-08-25 → 2026-08-26 work session. Covers DESK T-NEW-051
> through DESK T-NEW-061 + COM T-NEW-052 / COM T-NEW-058
> follow-up.

---

> **Round 2 (post-2026-08-26 ~15:00 UTC):** Two regressions caught
> by the agent's live smoke test of `192.168.1.67:8081` against
> the LAN docker. Fixed in commit `3c16c3b` (COM T-NEW-058
> follow-up round 3). Both pages now render the canonical nav +
> purple-gradient theme via the marketing partials pattern.

---

## Pass Criteria for This Session

All three flows MUST work end-to-end before operator sign-off:

1. **License bootstrap** — desktop launches, calls
   `POST /api/desktop/install-bootstrap` against the LAN
   docker, gets an `api_key`, persists it in
   `~/.local/share/nchantdoffice/install.bin`, next launch
   reuses it without a server round-trip.
2. **Account signup** — Settings → Nchantd Account tab loads
   the embedded browser at `http://192.168.1.67:8081/registration`
   and renders the sign-up form (not the AppBuilder 404
   shell).
3. **Ad rotation** — right-side Ad tab calls
   `GET /api/ads/rotation/next` every 5 minutes, renders
   whichever single ad the server returns, no lockup.

---

## Bugs / Regressions Resolved

| Time (approx) | Symptom | Card | Cause | Fix |
|---|---|---|---|---|
| 18:08 | `POST /api/desktop/install-bootstrap` returned "Page not found" (HTML) | DESK T-NEW-054 | `BootstrapError` from a 4xx re-raised to the desktop layer | Broadened `except (OSError, BootstrapError)` so transient install failures boot the desktop offline |
| 18:39 | `[links] HTTPError: 401` from `/api/affiliate/links/` | DESK T-NEW-057 | `APIClient` sent `Authorization: Bearer *** but the server's `@require_desktop_api_key` reads `x-api-key` | Switched header name; `update_affiliate_links` now reads api_key from `InstallStore` |
| 18:44 | 401 fired every launch because bootstrap hadn't minted api_key yet | DESK T-NEW-058 | Affiliate sync raced the bootstrap | Skip the call entirely when api_key is None (boot race); log clearly with debug-banner lines |
| 18:49 | `'NoneType' has no attribute 'set_value'` crash on Account tab | nchantrs #db95b58 (operator-fixed before session) | `populate_viewport` dereferences `url_select_entry` before `initView` populates it | Defensive check in `NchantdWebViewer`; upstream fixed in operator's image |
| 18:54 | `Page not found` on `/registration` | COM T-NEW-058 follow-up | Marketing `_MARKETING_PAGES` whitelist missing the key | Added `compare`/`registration`/`whats_new` to whitelist + created the two new templates |
| 18:58 | SystemTray URL stuck on production | DESK T-NEW-056 | `DEV_API_BASE` and `DEV_WEB_BASE` were split across 8080/8081 | Collapsed to single port `http://192.168.1.67:8081` (the LAN docker serves both) |
| ~21:00 | App lockup on launch (operator report) | DESK T-NEW-061 | 12-second QTimer raced with in-flight HTTP fetches | Stripped local rotation; server picks ad, desktop surfaces every 5 min |
| **15:00** | `GET /compare` → 500 (`UndefinedError: 'base_template' is undefined`); `GET /download` → 500 (same cause, pre-existing) | **COM T-NEW-058 follow-up round 3** (commit `3c16c3b`) | v1.50 theme unification (commits `32a4ddf` + `bef64b6`) migrated only templates under `templates/marketing/`; `compare.html` + `download.html` at templates/ root were missed and still extended `appbuilder/base.html`. The marketing blueprint's `render_template()` does not inject `base_template` (that's an AppBuilder context variable), so both 500'd | Migrated both templates to use `{% include "marketing/_nav.html" %}` + `{% include "marketing/_theme_css.html" %}` + `.page-body-gradient` body class. Added a Jinja context processor that exposes `current_version` + `current_release_date` from `version_gates` to every template (no more per-view kwarg plumbing). 3 regression tests added to `tests/test_marketing_routes_render.py`: 1) `test_compare_canonical_nav` (pins /compare 200 + canonical nav), 2) `test_download_renders_cleanly` (never 500), 3) `test_no_marketing_page_extends_appbuilder_base` (class-level guard — walks every `_MARKETING_PAGES` template and fails if any extends `appbuilder/base.html`) |

---

## Live Smoke Results (post-fix)

```
$ curl -s -o /dev/null -w "%{http_code}\n" http://192.168.1.67:8081/
200

$ curl -s -o /dev/null -w "%{http_code}\n" http://192.168.1.67:8081/registration
200

$ curl -s http://192.168.1.67:8081/registration | grep -o "<title>[^<]*</title>"
<title>Register — nchantdoffice</title>

$ curl -s -o /dev/null -w "%{http_code}\n" http://192.168.1.67:8081/whats_new
200

$ curl -s -o /dev/null -w "%{http_code}\n" http://192.168.1.67:8081/compare
200

$ curl -s -X POST -H "Content-Type: application/json" -d '{}' -o /dev/null \
       -w "%{http_code}\n" http://192.168.1.67:8081/api/desktop/install-bootstrap
400   # expected: empty body → endpoint is wired, validation kicks in

$ curl -s -o /dev/null -w "%{http_code}\n" http://192.168.1.67:8081/api/version-config
200

$ curl -s -o /dev/null -w "%{http_code}\n" http://192.168.1.67:8081/api/ads/base-layer/health
200

$ curl -s http://192.168.1.67:8081/api/ads/rotation/next?interval_seconds=60
{"ad": {"id": 3, "slug": "supabase-default", "title": "Supabase..."},
 "bucket": 29795174, "rotation_interval_seconds": 60}
```

All expected status codes. The two new marketing pages render
the correct `<title>` (confirming templates are served, not
generic 404 shells).

---

## Test Suite Results

### Desktop (`nchantdoffice/tests`)
- **85** license + utilities tests pass
- **11** URL resolver tests pass
- **8** ad rotation client tests pass (DESK T-NEW-061)
- **9** link URL tests pass (DESK T-NEW-055)
- **5** startup_refresh tests pass
- Pre-existing 33 unrelated failures unchanged

### Server (`nchantdoffice_com/tests`)
- **16** route + integration tests pass
  (including 10 new ad rotation endpoint tests)
- Pre-existing 1 xfail (rate-limit unit test) unchanged

---

## Operator Workflow (now stabilised)

```python
# cmds/runNchantdOffice.py
cfg = {"run-mode": "dev"}
nchantment("NchantdOffice", args, app, cfg, wizard)
```

Every URL routes to `http://192.168.1.67:8081`. The desktop
shows an ad on launch and re-surfaces every 5 minutes. License
bootstrap runs offline-resilient on transient failures.

---

## Known Issues (Not Blocking)

- **SMTP for `/api/account/claim`** — claim flow currently logs
  the magic-link at INFO for the operator to forward manually.
  Wiring real SMTP is queued (AGENTS.md pending operator
  action #b).
- **`/api/desktop/register` legacy deprecation** — the legacy
  endpoint returns 410 Gone. The first stable desktop build
  with bootstrap support will bump
  `LATEST_DESKTOP_VERSION_WITH_BOOTSTRAP` in `version_gates.py`
  to fully retire it.
- **PyKeyStore `master.key.temp` permission regression** —
  after a host-level UID mismatch, the file ends up mode 0600
  owned by the in-container `app` user (1001) which the host
  user (1000) can't read. Fix:
  `docker run --rm -u 1001:1001 -v /home/solubrew/docker-data/nchantdoffice/pycurity:/vault alpine chmod a+r /vault/master.key.temp`
  See `nchantdoffice_com/docs/deploy-lan.md` §Troubleshooting.
