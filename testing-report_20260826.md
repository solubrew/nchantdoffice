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
| **15:30** | A/B harness primitives + dry-run demo theme commit (`3b44739`, `5ac0de4`, `947cebc`) | Theme A/B harness | Operator decision (2026-08-26): A/B test the landing page between Theme A (marketing partials) and Theme B (extracted from `index.html`) BEFORE collapsing to one theme. Build the harness first, prove the dispatch path works with a demo dry-run, then extract `_landing/`. | `resolve_theme()` + `partials.partial_path()` registry + `_inject_theme` context processor + after_request cookie hook. `_MARKETING_PAGES` templates rewritten to use `{% include "themes/_" ~ theme ~ "/_nav.html" %}` (the dynamic include). 19 RED tests in `test_theme_harness.py`. Live verification: dry-run `?theme=demo` rendered the demo theme across all 7 marketing pages (services, compare, pricing, registration, whats_new, download, plus the home FAB route). Env-var pass-through added to `web-entrypoint.py` (operator host, not in repo) — gunicorn workers had been filtering env vars via `env_static`. 29 theme-harness tests pass end-to-end. |
| **~17:00** | `/blog/`, `/forum/`, `/gallery/` rendered under FAB slate theme — desktop's embedded browser saw Theme C (FAB slate) while every other page used Theme A (purple gradient) | **COM T-NEW-058 follow-up C7** (commit `6545138`) | The 3 community pages extended `appbuilder/base.html` (Theme C) while the rest of the site used the marketing partials (Theme A). The v1.50 theme unification missed them because they live at `templates/` root (not under `templates/marketing/`). Operator directive: migrate them to Theme A | All 3 templates rewritten to use the marketing-partials pattern: DOCTYPE + dynamic `_theme_css.html` include + `<body class="page-body-gradient">` + dynamic `_nav.html` and `_footer.html` includes. Body content unchanged (forum's pinned-only filter, blog's 3 view_modes, gallery's lightbox + 9 data attributes). Hardcoded hex colors swapped for `var(--brand)`/`var(--brand-mid)`/`var(--accent)` design tokens. 4 RED tests added pinning the C7 contract: 1) `test_no_community_template_extends_appbuilder_base` (class-level guard, strips Jinja comments first so historical-context mentions don't false-positive), 2) `test_community_pages_serve_200` (boot runSite.py subprocess + retry), 3) `test_community_pages_have_canonical_marketing_nav` (canonical logo + 5 nav links + no `slate.css`), 4) `test_community_pages_have_purple_gradient_body`. Test pattern uses `http.client` not `urllib.urlopen` (the latter's implicit body-read hangs on slow render paths). 33 theme-harness + 21 marketing-render + 6 whitelist + 17 pricing + 7 forum_auth + 11 marketing-pages-200 = **95 tests pass**. Live verification: `/blog/` 13667 bytes, `/forum/` 15688 bytes, `/gallery/` 27623 bytes, all with canonical nav + purple gradient + no FAB slate |
| **~18:30** | `/` (landing), `/login/`, `/nchantdaccountview/new_account/`, `/portal/`, 404.html, 500.html all rendered under FAB slate theme | **COM T-NEW-058 follow-up C8** (commit `68c59e5`) | After C7 + the demo dry-run, the operator still saw visual mismatch on the deployed docker: the landing, login, signup, and error pages were all on the FAB slate theme. These were the last 4 holdouts (C7 caught the community pages; C8 catches the rest). Per the operator's prior decisions ("migrate + bundle"), full migration was the right shape | 5 templates rewritten to the marketing-partials pattern: `index.html` (482→374 lines, all A/B test slots preserved: `ab_hero_logo`, `ab_hero_image`, `ab_hero_slogan`, `ab_hero_tagline`, `ab_cta_primary`, `ab_cta_secondary`); `new_account.html` (23→~92 lines, signup form); `404.html` + `500.html` (FAB error handlers rewritten); `login.html` (NEW, the FAB `/login/` route was overridden at the app level in `app/__init__.py` — registered BEFORE `AppBuilder()` so Werkzeug's first-match-wins picks the marketing-theme render over FAB's `AuthDBView`). `NchantdAccountView.login()` no longer redirects to `/auth/login`; it renders `login.html` directly. Body content of all 5 templates preserved (marketing copy, signup fields, A/B test slots, error page copy). 3 RED tests added pinning the C8 contract: 1) `test_c8_pages_serve_200` (200/404 status check across `/`, `/login/`, `/nchantdaccountview/new_account/`, `/portal/`, `/no-such-page/`), 2) `test_c8_pages_have_marketing_theme` (canonical nav logo + no `slate.css`), 3) `test_no_template_extends_appbuilder_base` (class-level guard walking all 8 C7+C8 templates). **36 theme-harness + 21 marketing-render + 6 whitelist + 17 pricing = 80 tests pass.** Live verification: every URL on the site now renders with the same canonical nav + purple gradient + 3-group footer. The visual mismatch the operator noticed is now resolved — `/` 19919 bytes, `/login/` 10287 bytes, `/nchantdaccountview/new_account/` 10471 bytes, `/portal/` 8794 bytes (404 page), `/no-such-page/` 8794 bytes (404 page), all show the marketing theme |
| **~19:00** | (continued from C8) Operator saw the consolidated marketing theme and decided they want a **config switch** between two styles — not a random A/B test | **COM T-NEW-058 follow-up phase 1** (commit `4c363ba`) | Operator: "switch all to the other template — it shouldn't A/B Test randomly but be a configuration option I can select for the entire site. Every page should have multiple body variants." This is the reverse of C8: instead of collapsing to one theme, build the chrome for both themes and let the operator pick. | `THEME_SITE` config flag (default `marketing`, env override `NCHANTDOFFICE_THEME_SITE`). `resolve_theme()` gains layer 0b: if `THEME_SITE` is set and the URL has no `?theme=` param, return the configured theme (short-circuits cookie/GA/random). 3 new partials under `themes/_landing/`: `_nav.html` (the FAB-extending emoji nav-links block), `_theme_css.html` (the original blue→purple `#4361ee/#7209b7` gradient + `.nchantd-nav-links` CSS from the pre-C8 `index.html` — flat hex, no design tokens), `_footer.html` (simple copyright + 4-link footer). 6 RED tests added pinning the phase-1 contract: 1) `test_landing_chrome_partials_exist_on_disk` (3 partials present), 2) `test_landing_theme_name_registered_in_valid_themes`, 3) `test_resolve_theme_honors_THEME_SITE_config_flag` (the core "switch all" contract), 4) `test_resolve_theme_default_is_marketing` (backwards-compat), 5) `test_resolve_theme_query_param_overrides_THEME_SITE` (per-session QA override), 6) `test_resolve_theme_invalid_site_config_falls_back` (defensive — config typos don't 500 the site). **42 theme-harness tests pass (36 prior + 6 new for phase 1). 38 regression tests pass.** Live verification: set `NCHANTDOFFICE_THEME_SITE=landing` in cluster-up.sh env file, restart container, all 10/10 sampled pages flipped (marketing logo 0→1, landing navlinks 0→4, page-body-gradient unchanged at 1 — body is phase-3). Revert flag, restart, site returns to marketing. Plan: `/Users/solubrew/.hermes/plans/2026-08-26_183000-nchantdoffice-com-theme-site-switch.md`. **Note:** phase 1 is chrome only — when `THEME_SITE=landing` the user sees the landing chrome (FAB nav-links + simple footer) wrapped around the marketing body. That's a deliberately awkward visual that proves the dispatch works without forcing 17 body variants in one commit. Phase 2 (one body variant for `/`) and phase 3 (all 17 page body variants) follow when the operator picks the winner. |
| **~19:30** | Phase 2 follow-up: shipping the body variant for just the landing page so the operator can see a full landing-theme landing (chrome + body), not just the chrome alone | **COM T-NEW-058 follow-up phase 2** (commit `d93cdf5`) | Phase 1 shipped chrome only. Phase 2 ships the landing body so the operator can compare both looks in full for the most-viewed page (the landing). The other 16 page body variants are phase 3 (deferred to a later commit since the landing page is the highest-traffic and the most representative). | 2 new body partials under `templates/_bodies/`: `index_marketing.html` (the C8 marketing body extracted from the previous monolithic `index.html` — clean `<section>` blocks, `var(--brand)`/`var(--brand-mid)`/`var(--accent)` design tokens, no hex) and `index_landing.html` (the original pre-C8 FAB-extending body recovered from commit 6374fef — inline `<style>` block with the hardcoded `#4361ee → #7209b7` gradient, the original `nchantd-section` / `nchantd-feature-card` markup, the in-body `nchantd-nav-links` row, the cookie consent banner JS, A/B test kwargs consumed in inline `style=` attributes). `templates/index.html` slimmed from 374 to 232 lines: chrome partials → body partial dispatch (`{% include "_bodies/index_" ~ theme ~ ".html" %}`) → chrome footer → GA4 init script. The `NchantdIndexView` in `app/__init__.py:207` was NOT changed — both bodies consume the same A/B test kwargs. 4 RED tests added: 1) `test_index_body_variants_exist_on_disk` (both partials present), 2) `test_index_template_dispatches_on_theme` (regex check that `index.html` has the dynamic body include — catches a future hardcoding regression), 3) `test_index_marketing_body_uses_design_tokens` (marketing body refs `var(--brand)` AND does NOT have `#4361ee`/`#7209b7` background), 4) `test_index_landing_body_has_inline_style_with_hardcoded_hex` (landing body has the `#4361ee`/`#7209b7` signature). **46 theme-harness tests pass (42 prior + 4 new for phase 2). 42 regression tests pass.** Live verification: with no flag, `/` returns 19546 bytes (0 hex, 31 design-tokens = marketing body). With `THEME_SITE=landing`, `/` returns 19848 bytes (3 occurrences of `#4361ee`, 2 of `#7209b7`, 7 of `var(--brand)` = landing body). Other pages stay marketing body in both states (their variants are phase 3). Revert the flag → `/` returns to marketing. |
| **~20:30** | Phase 3 follow-up: shipping the body variant for every other page (25 pages × 2 = 50 body partials) so the operator can flip the entire site, not just `/` | **COM T-NEW-058 follow-up phase 3** (commit `52227c6`) | Phase 2 shipped the body variant for just `/`. Phase 3 ships body variants for all 25 pages so the operator's "switch all to the other template" + "every page should have multiple body variants" directives are fully satisfied. The 25 pages: 16 marketing blueprint pages (`about`, `contact`, `services`, `pricing`, `partnerships`, `faq`, `careers`, `education`, `apprenticeships`, `privacy`, `terms`, `cookies`, `install`, `getting-started`, `registration`, `whats_new`) + 9 root-level pages (`compare`, `download`, `blog`, `forum`, `gallery`, `new_account`, `login`, `404`, `500`). | 50 new body partials under `templates/_bodies/` (25 pages × 2 themes). Marketing body = existing page body extracted from the page template. Landing body = synthesized from the marketing body via `scripts/synthesize_landing_body.py`: design tokens replaced with hardcoded hex, `<section class="page-hero">` transformed to `<div class="nchantd-hero">`, self-contained landing-theme `<style>` block injected at the top of the body so it doesn't depend on the marketing chrome's design tokens. 25 page templates transformed via `scripts/transform_page_templates.py`: page-specific `<style>` block in `<head>` wrapped in `{% if theme == "marketing" %}...{% endif %}` (only renders for the marketing theme — landing body has its own styles); body content replaced with `{% include "_bodies/<basename>_" ~ theme ~ ".html" %}`; inline `<footer>...</footer>` blocks replaced with the chrome footer include. 2 new scripts: `synthesize_landing_body.py` (one-shot extractor + synthesiser) and `transform_page_templates.py` (one-shot page-template transformer). 3 new RED tests: 1) `test_phase3_all_body_variants_exist_on_disk` (all 50 partials present), 2) `test_phase3_landing_bodies_use_hardcoded_hex` (every landing body has the landing-theme hex signature), 3) `test_phase3_marketing_bodies_have_content` (every marketing body has at least one class or heading). **49 theme-harness tests pass (46 prior + 3 new for phase 3). 42 regression tests pass.** Live verification: with no flag, 24/24 sampled pages return 200 with 18-35 design-token refs and 0 landing hex (marketing body everywhere). With `THEME_SITE=landing`, 24/24 pages return 200 with 1-7 design-token refs (only from the chrome partials) and 1+ landing hex (the landing body's `<style>` block). The full site-wide theme switch now works: flip `THEME_SITE`, restart, every page renders in the new look. No page is left out. |
| **~21:00** | Phase 4 follow-up: ship the operator's guide and umbrella CHANGES card so the operator can self-serve the switch without re-reading the commit history | **COM T-NEW-058 follow-up phase 4** (commit `95d2e13`) | Phases 1-3 shipped the technical machinery (flag, resolver, chrome, 50 bodies, 25 transformed pages, 13 RED tests). Phase 4 is pure documentation so the operator has a single source of truth for how to flip the site, when to flip, what each theme looks like, and what to do when something goes wrong. | 1 new doc at `docs/theme-site-switch.md` (~430 lines): TL;DR flip-the-site recipe (4 commands), the `THEME_SITE` flag (default + env override + config), the `?theme=marketing\|landing` per-session override, how-it-works (the resolver 5 layers, the chrome partials, the body partials, the 2 one-shot scripts), the themes-at-a-glance comparison (palette / nav / footer / body / when-to-use), decision matrix (production / A/B / demo / pick-a-winner), common pitfalls (workers don't reload, body partials missing, colors leaking), audit trail (which commit shipped which phase), future work. CHANGES.md: new `[Unreleased] — 2026-08-26 (round 4 — site-wide theme switch)` card documenting the `THEME_SITE` flag, the resolver layer 0b, the 3 chrome partials, the 50 body partials, the operator's guide, the 2 one-shot scripts, the 13 new RED tests, the 25 transformed page templates, the live verification, and the future-work roadmap. **49 theme-harness tests pass. 42 regression tests pass.** No code changes in this commit — the deployment is unchanged. |
| **~21:15** | Cross-repo doc-update follow-up: keep all docs in both repos aligned with the shipped state | **COM T-NEW-058 follow-up rounds 8** (commit `107e3f0` in `nchantdoffice_com`, commit `426b90d` in `nchantdoffice`) | The theme work touched 8+ docs across both repos (audit, operator guide, CHANGES, testing report, desktop index, desktop-integration-plan, OPERATOR_DESKTOP_INSTALL). When the operator reversed the consolidation direction, several cross-refs became stale. This commit aligns them with the shipped site-wide switch state. | `nchantdoffice_com/docs/theme-consolidation-audit_20260826.md`: added a "Status" block at the top recording the reversal — the audit was originally proposing collapse-to-one; the operator chose two-themes-with-a-switch instead. Cross-links to `docs/theme-site-switch.md` as the live source of truth. `nchantdoffice_com/docs/desktop-integration-plan.md`: added a new row in the extensions table for the site-wide switch (4 phases, 4 commits, with a one-line summary of what each phase shipped). `nchantdoffice_com/docs/OPERATOR_DESKTOP_INSTALL.md`: added a new row in the Cross-references table pointing to `docs/theme-site-switch.md`. `nchantdoffice/docs/index.md`: rewrote the sister-repo section to reflect the new state (two complete themes + site-wide config switch), the new operator's guide, the full timeline of the work, and the new "current state" statement. `/Users/solubrew/.hermes/plans/2026-08-26_183000-nchantdoffice-com-theme-site-switch.md`: appended a "Status: ✅ ALL 4 PHASES SHIPPED" block with the per-phase commit table, the live verification summary, and the next steps for the operator. **No code changes — pure doc hygiene. Tests unchanged (49 theme harness + 42 regression = 91 pass).** |

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
