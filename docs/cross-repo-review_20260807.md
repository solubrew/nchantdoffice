# NchantdOffice Desktop — Cross-Repo Alignment Review

**Date:** 2026-08-07
**Reviewer:** Cross-repo alignment pass
**Repos reviewed:**
- `nchantdoffice` (this) — desktop app, PySide6, version `0.0.1.0.1.4`
- `nchantdoffice_com` — public website + REST API, version `0.0.1`
- `nchantdofficeATNRG` — marketing/sales docs (source of truth for
  tiers, pricing, slogans, version roadmap)

**What this doc is:** A pass over the desktop codebase that
identifies every place the desktop diverges from the two upstream
repos. For each gap, I list the fix needed and a tentative
`T-NEW-NNN` ID for the project's `TODOs.md`.

---

## TL;DR — the 5 critical gaps

1. **🚨 CRITICAL: The desktop's `ReferralAPIClient` calls
   `/api/affiliate/referrals`, `/api/affiliate/earnings`,
   `/api/affiliate/banners`, `/api/affiliate/payouts/request`,
   `/api/affiliate/track/click/<id>`, etc. — **none of which
   exist on the live server.** The actual endpoints are at
   `/api/v1/affiliate/...` and `/api/v1/referral/...` with
   different paths and auth requirements. Result: every affiliate
   panel call fails with a 404 or 401 and falls back to a local
   YAML.
2. **🚨 CRITICAL: No `/api/check-update` consumer.** The server
   exposes an update-check endpoint (T-NEW-022) but the desktop
   has no update-checker. Users running v0.0.1.0.1.4 will never
   see a "new version available" notification even when
   v0.0.2 ships.
3. **🚨 CRITICAL: No `/api/version-config` consumer.** The
   server exposes the feature-gate matrix (T-NEW-023) but the
   desktop doesn't read it. The desktop renders all features
   regardless of whether they're enabled for the user's tier or
   app version. A free user sees the "Multi Instance" menu item
   even though the feature is Pro-only at v0.0.3.
4. **⚠️ VERSION FORMAT MISMATCH:** The desktop is `0.0.1.0.1.4`
   (5-segment). The server's `/api/check-update` parser only
   handles 3-segment versions (`0.0.1`). The comparison will
   silently fail (`return False`) and the desktop will never
   think an update is available.
5. **⚠️ `APP_PLATFORM` constant lies.** The desktop is built on
   PySide6 (Qt6) but `APP_PLATFORM = "qt5"`. The server's
   version-config logic doesn't gate on platform, but anything
   in the desktop that branches on `APP_PLATFORM` is wrong.

The 5 critical gaps above are followed by 9 more "important"
gaps, then a section on the gaps that DON'T exist (good news).

---

## Section 1: Critical gaps (block integration)

### 1.1 — ReferralAPIClient points at non-existent endpoints

**File:** `nchantdoffice/utilities/referral.py:276-340`

The `ReferralAPIClient` is documented to hit the server's
`/api/affiliate/...` namespace. The server doesn't have that
namespace — it has `/api/v1/affiliate/...` and
`/api/v1/referral/...`.

| Desktop calls | Server has it? |
|---|---|
| `GET /api/affiliate/referrals` | ❌ (server: `GET /api/v1/referral/stats/<user_id>`) |
| `GET /api/affiliate/earnings` | ❌ (server: `GET /api/v1/referral/earnings/<user_id>`) |
| `GET /api/affiliate/offers` | ❌ (server: `GET /api/v1/quicklinks/`) |
| `GET /api/affiliate/banners` | ❌ (no banner endpoint exists) |
| `POST /api/affiliate/payouts/request` | ❌ (server: `POST /api/v1/affiliate/payout/request`) |
| `POST /api/affiliate/track/click/<id>` | ❌ (server: `POST /api/v1/referral/track-click`) |
| `POST /api/affiliate/track/install` | ❌ (server: `POST /api/v1/referral/track-install`) |
| `GET /api/affiliate/dashboard` | ✅ at `/api/v1/affiliate/dashboard` |
| `POST /api/affiliate/link` | ✅ at `/api/v1/affiliate/link` |

The client also uses `Authorization: Bearer <api_key>` but the
server expects `x-api-key` for the desktop bridge endpoints.
**Every affiliate-panel call is currently a 401 or 404.**

Evidence: the BUGs.md has a stacktrace from 2026-07-31 where
`[referral_api] GET https://nchantdoffice.com/api/affiliate/earnings
failed: Connection to nchantdoffice.com timed out` — same root
cause (the live server has a 60-second rate limit per IP; the
desktop hits it without backoff and gets timeouts).

**Fix:**
- Update `ReferralAPIClient` paths to match the server
- Switch auth header from `Authorization: Bearer` to `x-api-key`
- Add a `ReferralAPIClient.register_desktop()` static method
  that calls `POST /api/desktop/register` and persists the
  returned `{desktop_uuid, api_key}` to `~/.nchantd/credentials.json`
- Add `is_feature_enabled(name, tier)` helper that consumes
  `GET /api/version-config`

**T-NEW:** T-DESK-052 (proposed)

---

### 1.2 — No `/api/check-update` consumer

**File:** None (does not exist in desktop)

The server exposes `GET /api/check-update?current_version=0.0.1&os=linux`
which returns `{latest_version, release_date, update_available,
download_url, changelog_url}`. The desktop never calls it.

Result: when v0.0.2 ships, the desktop user sees no "new version
available" notification. The user has to manually check the
website.

**Fix:** Add a `UpdateChecker` worker that:
- Calls `GET /api/check-update?current_version=<APP_VERSION>&os=<os>`
  on startup and every 6 hours
- Shows a tray notification when `update_available: true`
- Persists "dismissed" versions in `~/.nchantd/state.yaml` to
  avoid re-notifying
- Falls back to "no update check available" if the server is
  unreachable

**T-NEW:** T-DESK-053 (proposed)

---

### 1.3 — No `/api/version-config` consumer

**File:** None (does not exist in desktop)

The server exposes `GET /api/version-config` which returns the
full feature gate matrix: `{features: {name: {min_version, tier,
enabled, available, description}}}`. The desktop never calls it.

Result: the desktop renders all menu items regardless of whether
the feature is enabled for the user's tier or app version. A
free user on v0.0.1 sees the "Multi Instance" menu item (Pro-only
at v0.0.3). A user on v0.0.1 sees "RAG Search" (free at v0.0.4).

**Fix:** Add a `FeatureGate` module that:
- Calls `GET /api/version-config` on startup
- Caches to `~/.nchantd/feature_flags_cache.json`
- Exposes `is_feature_enabled(name: str, user_tier: str) -> bool`
- The `_is_visible_for_user` method on `NchantdOfficeAdTab` (in
  `widgets/advertisements.py:173`) is the right pattern — copy it
  to a new module

**T-NEW:** T-DESK-054 (proposed)

---

### 1.4 — Version format mismatch

**File:** `nchantdoffice/utilities/constants.py:72`

The desktop is `APP_VERSION: str = "0.0.1.0.1.4"` (5-segment).
The server's `_parse_version()` in
`nchantdoffice_com/app/apis/updates.py` only handles 3-segment
versions. The 5-segment version is treated as 5-tuple
`(0, 0, 1, 0, 1, 4)` vs the server's `(0, 0, 1)`. Tuple comparison
returns false in both directions, so `update_available` is always
`False` (or worse, `True` if the desktop is somehow treated as
newer than the server's 0.0.1).

This is the same problem as #1.2 — even if the desktop calls
`/api/check-update`, the comparison is wrong.

**Fix (one of):**

a) Bump the server's `_parse_version` to handle 5-segment
   versions. Pro: no desktop change needed. Con: changes the
   server's contract.

b) Bump the desktop to a 3-segment version
   (`APP_VERSION: str = "0.1.0"` for the launch). Pro: aligns
   the desktop with the version-gate system. Con: lose
   granularity for sprint tracking.

c) Add a new field `app_version_short: str` that the desktop
   sends alongside `current_version`. Pro: keeps the existing
   desktop internal version. Con: 2 version fields is
   confusing.

**Recommendation:** Option (b). The desktop's sprint-level version
(`0.0.1.0.1.4` = `release.major.minor.patch.cycle`) is internal
developer metadata. The version the server tracks for
update-notification purposes should be a marketing version
(`0.1.0` = "first Soft Launch"). Add a `APP_VERSION_SHORT: str = "0.1.0"`
constant and use THAT for the `/api/check-update` call.

**T-NEW:** T-DESK-055 (proposed) — also requires server change
T-NEW-029 (proposed) if we go with (a) or (c).

---

### 1.5 — `APP_PLATFORM` constant lies

**File:** `nchantdoffice/utilities/constants.py:77`

```python
APP_PLATFORM: str = "qt5"  # qt5, qt6, gtk, web
```

The desktop is built on PySide6. The actual `import` everywhere
in the codebase is `from PySide6 import QtCore, QtWidgets, ...`.

This hasn't caused a bug YET because nothing branches on
`APP_PLATFORM` (I checked). But it's a latent bug that will
fire the first time someone adds a platform-specific UI
branch.

**Fix:** `APP_PLATFORM: str = "qt6"`.

**T-NEW:** T-DESK-056 (proposed) — trivial 1-line fix.

---

## Section 2: Important gaps (degrade integration, don't block)

### 2.1 — `links.py` calls unauthenticated `/api/affiliate/links/`

**File:** `nchantdoffice/utilities/links.py:65`

`update_affiliate_links()` calls `client.get("affiliate/links/")`
against `https://nchantdoffice.com/api/affiliate/links/`. The
endpoint exists, but it requires `x-api-key` header. Without auth
the server returns 401.

**Fix:** Same fix as 1.1 — update `APIClient` to send `x-api-key`
when an api_key is configured.

**T-NEW:** Part of T-DESK-052.

---

### 2.2 — Ad tab fallback YAML is stale

**File:** `nchantdoffice/widgets/advertisements.py:48-78`

`FALLBACK_BANNERS` lists Notion, Railway, Supabase (3 services)
as the local fallback when the API is unreachable. The server's
affiliate catalog has 16 services across 7 categories (per
`nchantdofficeATNRG/ReferralLinks.yaml`). The fallback should
mirror the live catalog, not 3 hand-picked services.

**Fix:** Either:
- Move `FALLBACK_BANNERS` to a separate `_data_/ads.yaml` file
  that's generated from `ReferralLinks.yaml` (server-side) and
  shipped with the desktop as a build artifact
- Or just remove the fallback and show an empty state when the
  server is unreachable (the desktop's `_is_visible_for_user`
  already hides ads for Pro users, so an empty state is fine
  for Free users)

**T-NEW:** T-DESK-057 (proposed)

---

### 2.3 — Heartbeat never sent to server

**File:** None

The server has `NchantdUserDesktopModel.last_seen_at` for showing
which desktops are online. The desktop never updates it.

The simplest implementation: piggyback on any existing
authenticated call. The server's `get_updates_for_desktop`
handler stamps `last_seen_at` automatically. So if the desktop
already polls `/api/updates`, it gets the heartbeat for free.

But the desktop DOESN'T poll `/api/updates` today (see 2.4).

**Fix:** Once 1.1+1.2 are done and the desktop is regularly
calling server endpoints, the heartbeat happens automatically.
Add a smoke test that asserts `last_seen_at` updates after
the desktop's polling.

**T-NEW:** Covered by T-DESK-052 acceptance criteria.

---

### 2.4 — `/api/updates` is never polled

**File:** None

The server has `GET /api/updates?uuid=...&last_update_date=...`
which returns per-OS content updates. The desktop never calls it.
The `nchantdoffice/updates/db.py` module is for **local** DB
schema migrations, not server-pushed content updates.

Result: the desktop never gets content updates pushed by the
operator. Operators currently have no way to ship a new quicklink
catalog or a new sample document to existing installs.

**Fix:** Add a `ContentUpdateSync` worker that polls
`/api/updates?last_update_date=<ISO>` every 15 min. Apply
`binary_delta` updates with snapshot+rollback. Apply `data_json`
updates with per-collection upsert. This is the same architecture
as the `nchantdoffice_com/app/services/desktop_bridge.py`
documented in the integration plan.

**T-NEW:** T-DESK-058 (proposed) — bigger task, scope ~3-5 days.

---

### 2.5 — No desktop registration flow

**File:** None

The server has `POST /api/desktop/register` that returns
`{desktop_uuid, api_key}`. The desktop never calls it. The
`NchantdUserDesktopModel` table is empty for every desktop that
runs.

**Fix:** On first launch (no `~/.nchantd/credentials.json`):
1. Prompt for username (or skip if a FAB session is active)
2. Generate a public key (`cryptography` library — `PaillierPublicKey`
   is what the server expects per `NchantdUserDesktopModel.default_address_public_key`)
3. POST to `/api/desktop/register`
4. Persist the returned `desktop_uuid` + `api_key` to
   `~/.nchantd/credentials.json` mode 0600
5. On subsequent launches, load from disk

The `nchantdoffice/utilities/device_id.py::get_device_id()`
already generates a 128-bit device fingerprint. The public key
for the registration can be derived from the device_id.

**T-NEW:** T-DESK-059 (proposed) — depends on T-NEW-052.

---

### 2.6 — Affiliate quicklinks (16 services) not consumed

**File:** `nchantdoffice/widgets/catalogs.py` (need to check)

The server exposes `/api/v1/quicklinks/` and
`/api/v1/quicklinks/categories` and
`/api/v1/quicklinks/track-click`. The desktop has a catalogs
widget but it might not be wired to the server.

**Fix:** Audit `widgets/catalogs.py` to confirm it reads from
the server. If it doesn't, add a `QuicklinksAPIClient` that
mirrors `ReferralAPIClient` but hits `/api/v1/quicklinks/`.

**T-NEW:** T-DESK-060 (proposed) — audit first, may already be
done.

---

### 2.7 — Rate limiting not respected

**File:** All `*APIClient` classes

The server has rate limits: `/api/updates` and
`/api/affiliate/links/` are limited to 60 calls/hour per IP
(see `nchantdoffice_com/app/rate_limit.py` per the test
`test_p1_3_rate_limit.py`). The desktop's clients don't track
request counts. A user who clicks around in the UI 100 times in
an hour hits the rate limit and the API silently returns 429.

**Fix:** Add a `RateLimitTracker` to the APIClient that:
- Counts requests per endpoint per hour
- Caches responses for repeat calls in the same hour
- Adds a `Retry-After` header parser to delay retries

**T-NEW:** T-DESK-061 (proposed)

---

### 2.8 — Ad tab CTA `get_pro` button doesn't link to anything useful

**File:** `nchantdoffice/widgets/advertisements.py:280`

```python
target_url = "https://www.nchantdoffice.com/get_pro"
```

The `/get_pro` page exists on the live server (or should). But
the desktop's hardcoded URL may not match the actual route
(currently `/compare` on the server). The redirect might 404.

**Fix:** Confirm the canonical "upgrade" URL on the server and
hardcode the right path. Or call the server
(`GET /api/v1/menu/` per the integration plan) to get the
correct upgrade URL for the user's region.

**T-NEW:** T-DESK-062 (proposed) — 1-line fix once confirmed.

---

### 2.9 — No graceful "offline" mode

**File:** All clients

When `nchantdoffice.com` is unreachable (which happens often
per the BUGs.md stacktraces), every server call fails after a
5-second timeout. The UI then shows a "local fallback" but the
user sees broken-looking panels with no clear error.

**Fix:** Add a `ServerStatus` indicator (system tray icon or
status bar item) that shows:
- 🟢 Connected (last successful call < 1 min ago)
- 🟡 Degraded (last successful call 1-5 min ago)
- 🔴 Offline (last successful call > 5 min ago OR last call
  failed)

**T-NEW:** T-DESK-063 (proposed)

---

## Section 3: What's already aligned (good news!)

These things work correctly between the repos. Listed so the
desktop team knows what NOT to change.

| Feature | Status | Notes |
|---|---|---|
| `nchantdoffice` package name | ✅ | Matches in all 3 repos |
| `NchantdOffice` brand name | ✅ | Consistent across the 3 repos |
| `nchantdoffice.com` domain | ✅ | All client code points at the right host |
| `pyqt6` / `PySide6` | ⚠️ | Code is PySide6 but `APP_PLATFORM="qt5"` (see 1.5) |
| 4-tier model (Free/Pro/ProData/Enterprise) | ⚠️ | Documented in ATNRG and nchantdoffice_com. Desktop's `_is_visible_for_user` only knows about Free vs Pro (see 3.1) |
| 100 nodes / 1 instance cap | ❌ | Not enforced on the desktop at all |
| 35 hard cap on tabs per node | ✅ | Enforced in `nchantdoffice/widgets/trees.py` |
| 20 web tabs per node cap (Free) | ❌ | Not enforced |
| Device ID system | ✅ | `nchantdoffice/utilities/device_id.py` provides a 128-bit fingerprint |
| OS detection (`platform.system()`) | ✅ | Used in `device_id.py` and `__main__.py` |
| Per-OS support (linux/macos/windows) | ✅ | Build artifacts in `dist/` cover all 3 |
| `ReferralAPIClient` class exists | ✅ | Just points at the wrong endpoints (see 1.1) |
| Ad tab UI exists | ✅ | `widgets/advertisements.py` is wired into the right pane |
| Local fallback for ads | ✅ | `FALLBACK_BANNERS` exists (just stale, see 2.2) |
| `pycurity` integration for secrets | ✅ | Used to store the api_key (per BUGs.md) |

---

## Section 4: Specific files in the desktop to modify

For the 14 T-NEW items above, the concrete file changes are:

| T-NEW | File(s) | Change |
|---|---|---|
| T-DESK-052 | `nchantdoffice/utilities/referral.py:276-340` | Rewrite `ReferralAPIClient` to match server paths + `x-api-key` auth. Add `register_desktop()` static method. |
| T-DESK-053 | NEW: `nchantdoffice/updates/checker.py` | New module: `UpdateChecker` class with background polling |
| T-DESK-054 | NEW: `nchantdoffice/utilities/feature_gates.py` | New module: `FeatureGate` class consuming `/api/version-config` |
| T-DESK-055 | `nchantdoffice/utilities/constants.py:72` | Add `APP_VERSION_SHORT: str = "0.1.0"` |
| T-DESK-056 | `nchantdoffice/utilities/constants.py:77` | `APP_PLATFORM: str = "qt6"` |
| T-DESK-057 | `nchantdoffice/widgets/advertisements.py:48-78` + NEW `nchantdoffice/_data_/ads.yaml` | Move fallback banners to YAML; build the YAML from `ReferralLinks.yaml` |
| T-DESK-058 | NEW: `nchantdoffice/sync/applier.py` + `nchantdoffice/sync/rollback.py` | New module: content-update sync (binary_delta + data_json appliers) |
| T-DESK-059 | NEW: `nchantdoffice/utilities/credentials.py` | New module: `~/.nchantd/credentials.json` (mode 0600) management |
| T-DESK-060 | `nchantdoffice/widgets/catalogs.py` | Audit: confirm quicklinks widget reads from server |
| T-DESK-061 | All `*APIClient` classes | Add `RateLimitTracker` mixin |
| T-DESK-062 | `nchantdoffice/widgets/advertisements.py:280` | Fix the `/get_pro` URL to point at the actual server route |
| T-DESK-063 | NEW: `nchantdoffice/utilities/server_status.py` + `nchantdoffice/widgets/status_indicator.py` | New module + status-bar widget for connection state |
| T-DESK-052* | `nchantdoffice/widgets/advertisements.py:173` (`_is_visible_for_user`) | Update to use the new `FeatureGate` module |
| T-DESK-052* | `widgets/config/referral_panel.py:447` | Update fallback handling once the real client works |

---

## Section 5: What the desktop team should NOT change unilaterally

Per the integration plan (`nchantdoffice_com/docs/desktop-integration-plan.md`):

- **Endpoint paths** — the server's contract is the contract
- **Response field names** — same
- **Auth model** — server expects `x-api-key` header (NOT
  `Authorization: Bearer`); changing this would break every
  auth-required call

What the desktop team CAN change:

- **Poll intervals** (server doesn't care; current proposal is
  6h for update-check, 15min for content-sync, 5min for ads)
- **Cache TTLs** (server doesn't care; current proposal is 24h
  for affiliate catalog, 12h for version-config)
- **UI surface** (just match the data the server returns)
- **Retry/backoff policy** (server is forgiving)

If the desktop team needs a new endpoint, a new field, or a
different auth model, file a T-NEW in `nchantdoffice_com/TODOs.md`
and ping the server team.

---

## Section 6: Recommended sequencing

### Phase 1 — Critical fixes (1 week)
1. T-DESK-052: Fix ReferralAPIClient (also fixes Ad tab loading)
2. T-DESK-055 + T-DESK-056: 1-line constant fixes
3. T-DESK-059: Add credentials.json management
4. T-DESK-062: Fix the /get_pro URL

After Phase 1, the existing ad tab + affiliate panel + referral
panel will work correctly against the live server for the first
time.

### Phase 2 — Version + features (3 days)
5. T-DESK-053: UpdateChecker worker
6. T-DESK-054: FeatureGate module
7. T-DESK-063: Server status indicator

After Phase 2, the desktop knows its place in the version
roadmap and can render features conditionally. Users get
upgrade notifications.

### Phase 3 — Ads + sync (1 week)
8. T-DESK-057: Refresh the ad catalog fallback
9. T-DESK-058: Content-update sync (this is the biggest task)
10. T-DESK-060: Audit catalogs widget
11. T-DESK-061: Rate-limit tracking

After Phase 3, the desktop is a full client of the server.

### Phase 4 — Polish (optional, 2 days)
12. T-DESK-052* — wire FeatureGate into _is_visible_for_user

---

## Section 7: Cross-repo policy (from the integration plan)

> The public API endpoints already pinned in nchantdoffice_com's
> test suite are the contract. The desktop team should consume
> them as-is. If the desktop team needs a new endpoint or a
> new field, file a T-NEW-XXX in this repo's TODOs.md and ping
> the server team.

This means:
- The desktop team owns the 14 T-DESK-XXX items above
- The server team owns the T-NEW-025/026/027/028 items from the
  integration plan (ads API, heartbeat, crash-report, etc.)
- Neither team should change the others' code without coordination

The desktop team's branch is `gamma`. The server team's branch
is also `gamma`. Cross-repo changes ship via 2 separate PRs that
reference the same T-NEW ID.

---

## Section 8: Open questions for the desktop team

1. **Version format:** Sprint-tracking version (`0.0.1.0.1.4`)
   vs marketing version (`0.1.0`). Recommendation: add
   `APP_VERSION_SHORT` and use it for the server. (T-DESK-055)
2. **Public key for registration:** The server expects a
   `public_key` field in `/api/desktop/register`. The desktop
   doesn't generate one today. Use Paillier (the
   `NchantdUserDesktopModel.default_address_public_key` column
   is `String(128)`, suggesting the key is short) or just send
   a 128-char random string and document it as a stub for the
   real ATN RPC layer.
3. **Multi-instance desktop:** If a Pro user runs the desktop
   on 2 machines, do they share one api_key or register
   separately? The current server returns 409 on the second
   register. Need a "register additional instance" flow.
4. **Telemetry opt-out:** Should the heartbeat + ad-impression
   calls be opt-out (default ON) or opt-in (default OFF)?
   Recommendation: heartbeat default ON (it's the operational
   ground truth); ad-impression default ON but skippable in
   Settings.

---

## Section 9: References

### nchantdoffice_com (server)
- `docs/desktop-integration-plan.md` — the full integration plan
  this review is based on
- `app/apis/updates.py` — `/api/check-update` + `/api/updates`
  + `/api/desktop/register` + `/api/affiliate/links/`
- `app/apis/version_config.py` — `/api/version-config`
- `app/services/desktop_bridge.py` — the service functions
  consumed by the API
- `app/services/version_gates.py` — the gate logic
- `app/services/ad_service.py` — the ad service (server-side
  campaign management)
- `app/models/core.py::NchantdUserDesktopModel` — the per-desktop
  state (uuid, api_key, public_key, last_seen_at)
- `tests/test_desktop_bridge.py`, `test_check_update.py`,
  `test_version_gates.py` — the contract tests
- `TODOs.md` — for filing new server-side work

### nchantdofficeATNRG (marketing source of truth)
- `VersionAlignment.md` — version schedule
- `ApplicationConfigRules.md` — per-tier limits
- `PricingModel.md` — tier pricing
- `DesktopIntegration.md` — TL;DR of the integration plan
- `ReferralLinks.yaml` — 16 partnered services
- `Advertisement.md` — ad policy

### nchantdoffice (this repo)
- `nchantdoffice/utilities/referral.py` — ReferralAPIClient (1.1)
- `nchantdoffice/utilities/links.py` — APIClient (2.1)
- `nchantdoffice/utilities/constants.py` — APP_VERSION (1.4, 1.5)
- `nchantdoffice/utilities/device_id.py` — get_device_id() (2.5)
- `nchantdoffice/widgets/advertisements.py` — Ad tab (1.1, 2.2, 2.8)
- `nchantdoffice/widgets/catalogs.py` — Catalog widget (2.6)
- `BUGs.md` — historical stacktrace archive (1.1 evidence)
- `TODOs.md` — for adding the 14 T-DESK-XXX items
---

## Release checklist (added 2026-08-07 — T-DESK-066)

Items that prevent silent drift between this repo and
`nchantdofficeATNRG`. Run these before any release that ships
the Ad tab rotation.

### R-1 — Mirror `TIPS_FEED` from ATNRG `content/memes/tips.md`

The desktop bundles the 30 productivity tips locally in
`nchantdoffice/widgets/advertisements.py::TIPS_FEED` so the
rotation works offline. The canonical source is
`nchantdofficeATNRG/content/memes/tips.md` (commit `48352d3`).

When ATNRG `tips.md` changes (operator adds new tips,
rewords existing ones, removes a stale tip):

1. Open `nchantdofficeATNRG/content/memes/tips.md` and copy
   the updated numbered list (1–N).
2. Paste into `nchantdoffice/widgets/advertisements.py` in
   the `TIPS_FEED` list literal (preserve order, preserve
   the markdown bold wrappers around the actionable phrase).
3. Bump the test pin `test_tips_feed_has_at_least_thirty_entries`
   in `tests/test_ad_tab_rotation.py` if the count grew past
   30 (the test asserts `len(tips) >= 30` so additions don't
   break it, but a regression below 30 will).
4. Re-run `pytest tests/test_ad_tab_rotation.py` — all
   15 tests must stay green.
5. Commit with body:
   `chore(ad-tab): mirror N tips from ATNRG content/memes/tips.md`
   and reference both the ATNRG commit hash and the
   `T-NEW-029` card (commit `b06e022`).

**Why this matters:** `TIPS_FEED` is a static fallback.
Without this mirror step, the desktop silently shows stale
tips after every ATNRG content update. The user's first
complaint will be "the tips stopped being useful".

### R-2 — Grow `SUBSTACK_FEED` from outreach results

`SUBSTACK_FEED` in
`nchantdoffice/widgets/advertisements.py` is hand-curated
(5 starter entries: Ness Labs, Farnam Street, Productivity
Game, The Weekly Review, Refactoring). The ATNRG revenue
plan (`0-5kpm-revenue-plan.md` §"Symbiosis Substack
Strategy") has the operator running outreach that converts
interested Substacks into reciprocal placement partners.

When a new Substack partnership closes:

1. Add a `{title, url, blurb}` entry to `SUBSTACK_FEED`.
2. The rotation auto-includes it (no other wiring needed —
   `_load_slots()` iterates the full list).
3. The test pin `test_substack_feed_has_at_least_three_entries`
   only requires ≥ 3 entries, so growth never breaks the
   test (pin a stricter threshold later if you want a
   floor).

**Why this matters:** the symbiosis strategy's whole point
is "value content in the Ad tab in exchange for partnership".
A Substack that signs up but isn't added to `SUBSTACK_FEED`
is a partnership that doesn't deliver value to the user.

### R-3 — Verify `advertisements.yaml` rotation tuning

`nchantdoffice/widgets/_data_/advertisements.yaml` carries
the `interval_ms` key (default 12000). Before each release,
confirm:

- The YAML is present and well-formed (yaml.safe_load
  must succeed).
- The `interval_ms` value is in the operator-acceptable
  range (3000–60000 ms; values < 3s make the tab flicker,
  values > 60s make the rotation feel broken).

### R-4 — Cross-repo parity check

Both repos must ship in lockstep for T-NEW-029 / T-DESK-066
content changes:

- `nchantdofficeATNRG/TODOS.md` T-NEW-029 status flips
  from 🟡 Open to ✅ Complete when the desktop impl lands.
- The commit body in the desktop impl references the ATNRG
  card commit hash.
- The commit body in any ATNRG content update references
  the desktop impl commit hash.

