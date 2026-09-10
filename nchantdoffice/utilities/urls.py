r"""DESK T-NEW-052 — canonical URL resolver for the desktop.

Every external hostname the desktop hits lives in one place:
``nchantdoffice/utilities/_data_/urls.yaml`` (bundled defaults).
The XDG user-config layer (``nchantdoffice.utilities.user_config``)
can override any of these via a top-level ``urls:`` block in
``~/.config/nchantdoffice/config.yaml`` (or
``./nchantdoffice.yaml`` for project-local overrides).

This module is the single entry point every caller must use.
**Do NOT hardcode a hostname in a module-level constant.** New
call sites must:

  1. Add a key to ``_data_/urls.yaml``.
  2. Add a typed accessor here.
  3. Call the accessor from the call site.

The ``KNOWN_URL_KEYS`` set + the alphabetical ``_rstrip`` helper
make regressions easy to grep for::

  grep -rn "nchantdoffice.com\|api.nchantdoffice.com" nchantdoffice/ \
       --include='*.py' | grep -v utilities/urls.py

Any hit in that grep is a regression (besides this module and
docs/comments). The bundled defaults are intentionally pinned
to production — internal/staging environments override via the
XDG config so the binary that ships is always the production
binary.

Layering (highest priority last in the merge):

  1. Explicit per-access kwarg (``server_base_url=...`` on the
     constructors that accept one) — call-site pin.
  2. ``run-mode`` profile (DESK T-NEW-053) — set via
     :func:`set_run_mode` at process startup. Either the
     dev profile (internal docker) or the prod profile
     (external cloud). Default is ``prod``.
  3. Hardcoded ``_BUNDLED_DEFAULTS`` in this module (the
     fallback if ``_data_/urls.yaml`` is missing or unparseable).
  4. Bundled YAML ``nchantdoffice/utilities/_data_/urls.yaml``
     (shipped with the package — the canonical defaults).
  5. XDG user config ``urls:`` block (the per-deploy override).

Per the T-NEW-070 directive: no env-var reads. The XDG YAML
file is the only source of operator-overridable values.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from kahndor.logma import Logma


__all__ = [
    "server_base_url",
    "affiliate_api_base",
    "feature_gates_url",
    "updates_url",
    "sync_url",
    "home_page",
    "upgrade_compare_url",
    "share_landing_url",
    "registration_url",
    "whats_new_url",
    "affiliate_marketing_url",
    "marketing_base_url",
    "all_urls",
    "reload",
]


logma = Logma(__name__)


# Hardcoded fallback if the bundled yaml is missing or unparseable.
# Production defaults — operators override via XDG ``urls:`` block,
# not by editing this dict (which would require a code change).
_BUNDLED_DEFAULTS: Dict[str, str] = {
    "server_base_url":          "https://api.nchantdoffice.com",
    "affiliate_api_base":       "https://nchantdoffice.com/api/affiliate",
    "feature_gates_url":        "https://nchantdoffice.com",
    "updates_url":              "https://nchantdoffice.com",
    "sync_url":                 "https://nchantdoffice.com",
    "home_page":                "https://www.nchantdoffice.com/",
    "upgrade_compare_url":      "https://www.nchantdoffice.com/compare",
    "share_landing_url":        "https://nchantdoffice.com",
    "registration_url":         "https://www.nchantdoffice.com/registration",
    "whats_new_url":            "https://www.nchantdoffice.com/whats_new",
    "affiliate_marketing_url":  "https://www.nchantdoffice.com/affiliate_marketing",
    "marketing_base_url":       "https://nchantdoffice.com",
}


# All canonical keys. Used to validate user overrides and to
# surface a warning if the operator typos one in XDG config.
KNOWN_URL_KEYS = frozenset(_BUNDLED_DEFAULTS.keys())


_BUNDLED_YAML_PATH = Path(__file__).parent / "_data_" / "urls.yaml"


# -----------------------------------------------------------------------------
# run-mode profiles (DESK T-NEW-053)
# -----------------------------------------------------------------------------
#
# Two named profiles let the operator pick a complete URL set
# at launch without editing any config file. The launch entrypoint
# (cmds/runNchantdOffice.py) reads the ``run-mode`` value from
# the cfg dict and calls :func:`set_run_mode` BEFORE any caller
# invokes a ``urls.*`` accessor.
#
#   - ``prod`` — external production cloud (nchantdoffice.com).
#     The default. Every accessor returns the bundled YAML
#     / XDG-override value.
#   - ``dev``  — internal docker stack on the operator's LAN.
#     The nchantdoffice_com Flask app serves BOTH the marketing
#     site and the API on a single port (no separate web
#     frontend in the LAN-deploy path). The default
#     ``DEV_INTERNAL_PORT`` is 8081 to match
#     ``scripts/dev/cluster-up.lan.sh`` on the server side.
#     Switched on by ``run-mode: dev`` at launch.
#
# Both tables use the same keys as ``_BUNDLED_DEFAULTS`` /
# ``urls.yaml`` so swapping profiles is a wholesale replace.
#
# The dev profile intentionally overwrites EVERY key — including
# marketing deep-links — so the embedded browser, account tab,
# upgrade prompts, etc. all point at the internal site. Operators
# who only want to flip the API endpoint should leave run-mode at
# prod and use the XDG ``urls:`` block instead.
#
# Override the port by editing these constants if your LAN
# deploy uses a different host port. Both marketing and API
# MUST live on the same port — the nchantdoffice_com Flask app
# serves both behind Caddy. Per T-NEW-070, no env-var reads —
# the operator edits these constants to retarget the dev box.
#
# COM-SEC (2026-09-10): the LAN deploy is TLS-terminated by Caddy
# at https://192.168.1.67 (internal CA; the server issues Secure
# session cookies that Chromium only honors on trustworthy
# origins). The plain-HTTP :5000 binding is gone — traffic goes
# through Caddy on :443, so the port is empty and the base URL
# carries the https scheme. Clients trust Caddy's root CA via
# nchantdoffice_com/scripts/trust-lan-ca.sh (operator host) or
# trust-lan-ca-remote.sh (other LAN machines).
DEV_INTERNAL_HOST = "https://192.168.1.67"
DEV_INTERNAL_PORT = ""
DEV_API_BASE = (
    f"{DEV_INTERNAL_HOST}:{DEV_INTERNAL_PORT}" if DEV_INTERNAL_PORT else DEV_INTERNAL_HOST
)
DEV_WEB_BASE = DEV_API_BASE

DEV_URLS: Dict[str, str] = {
    "server_base_url":          f"{DEV_API_BASE}",
    "affiliate_api_base":       f"{DEV_WEB_BASE}/api/affiliate",
    "feature_gates_url":        DEV_WEB_BASE,
    "updates_url":              DEV_WEB_BASE,
    "sync_url":                 DEV_WEB_BASE,
    "home_page":                f"{DEV_WEB_BASE}/",
    "upgrade_compare_url":      f"{DEV_WEB_BASE}/compare",
    "share_landing_url":        DEV_WEB_BASE,
    "registration_url":         f"{DEV_WEB_BASE}/registration",
    "whats_new_url":            f"{DEV_WEB_BASE}/whats_new",
    "affiliate_marketing_url":  f"{DEV_WEB_BASE}/affiliate_marketing",
    "marketing_base_url":       DEV_WEB_BASE,
}

# ``prod`` is the empty-override marker — the resolver falls
# through to the bundled YAML / XDG block. Keeping an explicit
# table makes the contract symmetric and gives the resolver
# one place to look up the active profile.
PROD_URLS: Dict[str, str] = {}  # empty = "no override; use bundled"


_VALID_RUN_MODES = frozenset({"prod", "dev"})


# Module-level state — the active run-mode. Set once at
# process startup by :func:`set_run_mode`. Defaults to ``prod``
# so accessor calls before ``set_run_mode`` are still safe.
_run_mode: str = "prod"


def get_run_mode() -> str:
    """Return the currently-active run-mode (``"prod"`` or ``"dev"``).

    The default is ``"prod"``. The launch entrypoint flips this
    to ``"dev"`` when the operator launches with
    ``run-mode: dev`` in the cfg dict.
    """
    return _run_mode


def set_run_mode(mode: str) -> None:
    """Switch the active run-mode profile.

    Called once at process startup by
    :func:`cmds.runNchantdOffice.run`. Idempotent — re-setting
    the same mode is a no-op (besides logging). Invalid modes
    raise :class:`ValueError` (fail loud; the launch entrypoint
    should have validated the value before passing it in).

    Side effect: invalidates the resolver cache so the next
    accessor call returns values from the new profile.

    Args:
        mode: ``"prod"`` for external cloud defaults, ``"dev"``
            for the operator's internal docker stack.
    """
    global _run_mode
    if not isinstance(mode, str):
        raise ValueError(
            f"run-mode must be a string, got {type(mode).__name__}: {mode!r}"
        )
    mode = mode.strip().lower()
    if mode not in _VALID_RUN_MODES:
        raise ValueError(
            f"invalid run-mode {mode!r}; expected one of {sorted(_VALID_RUN_MODES)}"
        )
    if mode == _run_mode:
        logma.info(f"[urls] run-mode unchanged: {mode}")
        return
    logma.info(f"[urls] run-mode: {_run_mode} -> {mode}")
    _run_mode = mode
    # Invalidate the resolver cache so accessor calls pick up the
    # new profile values on the next call.
    _resolve.cache_clear()


def _active_profile() -> Dict[str, str]:
    """Return the URL table for the currently-active run-mode.

    ``prod`` returns ``PROD_URLS`` (empty — the resolver uses the
    bundled defaults instead). ``dev`` returns ``DEV_URLS`` which
    contains a complete URL set pointing at the internal docker.
    """
    if _run_mode == "dev":
        return DEV_URLS
    return PROD_URLS


# -----------------------------------------------------------------------------
# Loading
# -----------------------------------------------------------------------------


def _load_bundled_yaml() -> Dict[str, str]:
    """Read ``_data_/urls.yaml`` (shipped with the package).

    Falls back to ``_BUNDLED_DEFAULTS`` if the file is missing or
    unparseable — never raises. The bundled yaml is the canonical
    defaults; this function is read once per process and cached
    via :func:`_resolve`.
    """
    if not _BUNDLED_YAML_PATH.exists():
        logma.warning(
            f"[urls] bundled yaml missing at {_BUNDLED_YAML_PATH}; "
            f"using hardcoded defaults"
        )
        return dict(_BUNDLED_DEFAULTS)
    try:
        with _BUNDLED_YAML_PATH.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except (yaml.YAMLError, OSError) as exc:
        logma.warning(
            f"[urls] bundled yaml at {_BUNDLED_YAML_PATH} unparseable: "
            f"{exc}; using hardcoded defaults"
        )
        return dict(_BUNDLED_DEFAULTS)
    if not isinstance(data, dict):
        logma.warning(
            f"[urls] bundled yaml root must be a mapping, got "
            f"{type(data).__name__}; using hardcoded defaults"
        )
        return dict(_BUNDLED_DEFAULTS)
    return data


def _load_user_overrides() -> Dict[str, str]:
    """Read the ``urls:` block from the XDG user config.

    Mirrors the precedence of :func:`user_config.load_config`:
    cwd override (``./nchantdoffice.yaml``) > XDG
    (``~/.config/nchantdoffice/config.yaml``). Only the ``urls:``
    top-level key is consulted here; ``server.url`` (the legacy
    T-NEW-070 key) is NOT consulted — every URL has its own
    canonical key in the new schema.
    """
    try:
        from nchantdoffice.utilities.user_config import load_config
    except ImportError as exc:
        logma.warning(f"[urls] user_config import failed: {exc}")
        return {}
    cfg = load_config()
    overrides = cfg.get("urls") or {}
    if not isinstance(overrides, dict):
        logma.warning(
            f"[urls] user config 'urls:' must be a mapping, got "
            f"{type(overrides).__name__}; ignoring"
        )
        return {}
    # Surface typos early: warn on unknown keys rather than silently
    # dropping them.
    for k in overrides:
        if k not in KNOWN_URL_KEYS:
            logma.warning(
                f"[urls] user override '{k}' is not a known URL key "
                f"(expected one of {sorted(KNOWN_URL_KEYS)})"
            )
    return {k: v for k, v in overrides.items() if k in KNOWN_URL_KEYS}


@lru_cache(maxsize=1)
def _resolve() -> Dict[str, str]:
    """Layered URL resolver: profile → bundled → user override → strip slashes.

    Cached for process lifetime so we don't re-read yaml on every
    call. To pick up runtime changes (e.g. a settings-tab edit
    or a run-mode flip via :func:`set_run_mode`), call
    :func:`reload` to invalidate the cache.

    Layer order (lowest to highest priority):

      1. ``_BUNDLED_DEFAULTS`` (defensive fallback).
      2. Bundled YAML ``_data_/urls.yaml``.
      3. XDG user config ``urls:`` block.
      4. The active run-mode profile (DESK T-NEW-053): when
         ``run-mode == "dev"``, the ``DEV_URLS`` table wholesale
         replaces the merged dict so the operator's internal
         docker wins for every key. When ``run-mode == "prod"``
         the profile is empty (``PROD_URLS = {}``) and the
         merged dict survives unchanged.
    """
    merged: Dict[str, Any] = dict(_BUNDLED_DEFAULTS)
    bundled = _load_bundled_yaml()
    if isinstance(bundled, dict):
        for k in KNOWN_URL_KEYS:
            if k in bundled and isinstance(bundled[k], str):
                merged[k] = bundled[k]
    overrides = _load_user_overrides()
    merged.update(overrides)
    # DESK T-NEW-053: run-mode profile wins over everything except
    # an explicit per-call kwarg (call-site pin). ``prod`` is a
    # no-op (PROD_URLS is empty); ``dev`` replaces the entire dict.
    profile = _active_profile()
    if profile:
        merged.update(profile)
    # Normalise: strip trailing slashes so callers can do
    # ``f"{base}{path}"`` without doubled ``//``. Exception:
    # ``home_page`` keeps its trailing slash because some Qt
    # consumers (QUrl) treat the slash as part of the root.
    out: Dict[str, str] = {}
    for k, v in merged.items():
        v = str(v).strip()
        if k == "home_page":
            # keep trailing slash if present, otherwise add one
            if not v.endswith("/"):
                v = v + "/"
        else:
            v = v.rstrip("/")
        out[k] = v
    logma.info(
        f"[urls] resolved: run-mode={_run_mode} "
        f"server_base_url={out['server_base_url']} "
        f"home_page={out['home_page']}"
    )
    return out


def reload() -> None:
    """Invalidate the resolver cache.

    Call after writing to the XDG config from a settings-tab edit,
    or from tests that monkey-patch the config. Cheap — no I/O
    happens until the next accessor call.
    """
    _resolve.cache_clear()


# -----------------------------------------------------------------------------
# Public accessors
# -----------------------------------------------------------------------------


def server_base_url() -> str:
    """Base URL for the license server (bootstrap / refresh / claim).

    Override key: ``urls.server_base_url``.
    """
    return _resolve()["server_base_url"]


def affiliate_api_base() -> str:
    """Base URL for the affiliate API (quicklinks + dashboard).

    Override key: ``urls.affiliate_api_base``.
    """
    return _resolve()["affiliate_api_base"]


def feature_gates_url() -> str:
    """Base URL for the feature-gate endpoint (``.api/version-config``).

    Override key: ``urls.feature_gates_url``.
    """
    return _resolve()["feature_gates_url"]


def updates_url() -> str:
    """Base URL for the update-check endpoint (``.api/check-update``).

    Override key: ``urls.updates_url``.
    """
    return _resolve()["updates_url"]


def sync_url() -> str:
    """Base URL for the content-sync endpoint (``.api/updates``).

    Override key: ``urls.sync_url``.
    """
    return _resolve()["sync_url"]


def home_page() -> str:
    """Marketing homepage loaded by the embedded browser.

    Override key: ``urls.home_page``. Trailing slash is preserved.
    """
    return _resolve()["home_page"]


def upgrade_compare_url() -> str:
    """Deep-link to the upgrade comparison page (Pro upsell).

    Override key: ``urls.upgrade_compare_url``.
    """
    return _resolve()["upgrade_compare_url"]


def share_landing_url() -> str:
    """Base URL for shareable referral landing pages (``/download?ref=…``).

    Override key: ``urls.share_landing_url``.
    """
    return _resolve()["share_landing_url"]


def registration_url() -> str:
    """Account sign-up page (rendered in the embedded account browser).

    Override key: ``urls.registration_url``.
    """
    return _resolve()["registration_url"]


def whats_new_url() -> str:
    """Changelog page shown to paid users in the embedded account browser.

    Override key: ``urls.whats_new_url``.
    """
    return _resolve()["whats_new_url"]


def affiliate_marketing_url() -> str:
    """Affiliate dashboard landing page.

    Override key: ``urls.affiliate_marketing_url``.
    """
    return _resolve()["affiliate_marketing_url"]


def marketing_base_url() -> str:
    """Base for composing marketing deep-links (used by ad CTAs).

    Pattern::

        url = f"{urls.marketing_base_url()}{path}"   # e.g. ``/compare#prodata``

    Override key: ``urls.marketing_base_url``.
    """
    return _resolve()["marketing_base_url"]


def all_urls() -> Dict[str, str]:
    """Return the fully-resolved URL table (snapshot, not a live view).

    Useful for diagnostics, settings-pane rendering, and tests that
    want to assert the full surface. Returns a shallow copy so
    callers can't mutate the cache.
    """
    return dict(_resolve())


# -----------------------------------------------------------------------------
# Diagnostic: warn at startup if a caller still hardcodes a hostname.
# -----------------------------------------------------------------------------
#
# This is a developer-time guard, not a runtime feature. New code
# that hardcodes ``nchantdoffice.com`` / ``api.nchantdoffice.com``
# will not be caught at runtime — but the tests in
# ``tests/test_urls_config.py`` walk the source tree on import
# and flag regressions in the test suite. Run them as part of CI.