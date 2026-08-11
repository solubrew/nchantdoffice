# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
    docid: nchantdoffice-feature-gates
    name: Feature Gate Consumer
    description: >
        T-DESK-054 (cross-repo review §1.3): consumer for the
        server's ``GET /api/version-config`` endpoint. The
        server returns the full feature-gate matrix
        (free / pro / prodata / enterprise per feature); the
        desktop consults this on UI rebuilds to decide
        whether to render a menu item, button, or whole tab.

        Best-effort: any network failure returns ``None`` /
        stale cache rather than crashing. The server is the
        authoritative source — the desktop MUST trust the
        response and not its own local copy of the version
        roadmap.

        Mirrors the cache pattern from
        ``nchantdoffice/updates/checker.py`` and
        ``nchantdoffice/utilities/base_layer.py``:
          - 6h cache TTL (``REFRESH_INTERVAL_SECONDS``)
          - mode 0o600 cache file
          - cache write only on successful response
          - stale-cache fallback when server unreachable
    version: 1.0.0
    authority: filesystem
    security: seclvl2
    <(WT)>: -32
"""
# -*- coding: utf-8 -*-
# ======================================Standard Library Modules======================================================||
import datetime as dt
import json
import logging
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# ======================================3rd Party Library Modules=====================================================||
import requests

# ======================================Solutions Brewer Library Modules=============================================||
from kahndor.logma import Logma

logma = Logma(__name__)

# ---------------------------------------------------------------------------
# T-DESK-054 — module-level constants
# ---------------------------------------------------------------------------

# Server endpoint (matches nchantdoffice_com/app/apis/version_config.py).
DEFAULT_VERSION_CONFIG_PATH: str = "/api/version-config"

# How often to re-poll the server (6 hours; mirrors checker.py
# + base_layer.REFRESH_INTERVAL_SECONDS).
REFRESH_INTERVAL_SECONDS: int = 6 * 60 * 60

# Local cache file (~/.nchantd/feature_flags_cache.json, mode 0o600).
CACHE_FILENAME: str = "feature_flags_cache.json"

# Per-call HTTP timeout (5 s; matches ReferralAPIClient +
# UpdateChecker).
HTTP_TIMEOUT: float = 5.0

# The 4-tier model (per nchantdofficeATNRG/PricingModel.md).
# Pinning the literal strings so a refactor that drops a
# tier fails the AST contract test.
TIER_FREE: str = "free"
TIER_PRO: str = "pro"
TIER_PRODATA: str = "prodata"
TIER_ENTERPRISE: str = "enterprise"
KNOWN_TIERS: List[str] = [TIER_FREE, TIER_PRO, TIER_PRODATA, TIER_ENTERPRISE]

# Tier rank (Free < Pro < ProData < Enterprise). A higher tier
# unlocks every feature a lower tier unlocks. The ``is_feature_enabled``
# check is ``feature.tier <= user_tier`` (string comparison by rank,
# NOT alphabetical — ProData must rank above Pro).
_TIER_RANK: Dict[str, int] = {
    TIER_FREE: 0,
    TIER_PRO: 1,
    TIER_PRODATA: 2,
    TIER_ENTERPRISE: 3,
}

# T-NEW-070 (DESK-3 hard-break): NCHANT_DATA_DIR env var
# removed. The cache dir now comes from the user config
# file (~/.config/nchantdoffice/config.yaml) via
# get_cache_dir(). Tests that need a custom cache dir
# should override via monkeypatch on
# nchantdoffice.utilities.user_config.get_cache_dir.
from nchantdoffice.utilities.user_config import get_cache_dir  # noqa: E402
_CACHE_DIR = get_cache_dir()
_CACHE_PATH = _CACHE_DIR / CACHE_FILENAME


# ---------------------------------------------------------------------------
# T-DESK-054 — Feature dataclass
# ---------------------------------------------------------------------------


@dataclass
class Feature:
    """A single feature entry from the server's matrix.

    Fields mirror the server response shape (see
    nchantdoffice_com/app/apis/version_config.py:60).
    """

    name: str
    min_version: str = "0.0.1"
    tier: str = TIER_FREE
    enabled: bool = True
    available: bool = True
    description: str = ""

    @classmethod
    def from_response(cls, name: str, payload: Dict[str, Any]) -> "Feature":
        """Build a ``Feature`` from a server response entry.

        Defensive against missing keys (the server is the
        source of truth; the desktop tolerates partial
        responses rather than crashing on a key rename).
        """
        return cls(
            name=name,
            min_version=str(payload.get("min_version", "0.0.1")),
            tier=str(payload.get("tier", TIER_FREE)),
            enabled=bool(payload.get("enabled", True)),
            available=bool(payload.get("available", True)),
            description=str(payload.get("description", "")),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for the cache file."""
        return {
            "name": self.name,
            "min_version": self.min_version,
            "tier": self.tier,
            "enabled": self.enabled,
            "available": self.available,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "Feature":
        """Inverse of ``to_dict`` (for cache reads)."""
        return cls(
            name=str(payload.get("name", "")),
            min_version=str(payload.get("min_version", "0.0.1")),
            tier=str(payload.get("tier", TIER_FREE)),
            enabled=bool(payload.get("enabled", True)),
            available=bool(payload.get("available", True)),
            description=str(payload.get("description", "")),
        )


# ---------------------------------------------------------------------------
# T-DESK-054 — FeatureGate
# ---------------------------------------------------------------------------


class FeatureGate:
    """Caller-driven consumer for ``GET /api/version-config``.

    The caller decides when to call ``refresh()`` (startup hook,
    settings panel button, scheduled 6h timer). The class itself
    does not start any background thread — same shape as
    ``UpdateChecker``.

    Cache behaviour (mirrors ``UpdateChecker`` + ``base_layer``):
      1. ``is_feature_enabled()`` first checks the cache.
      2. If fresh (< REFRESH_INTERVAL_SECONDS), answer from
         cache without hitting the network.
      3. If stale or missing, the caller should ``refresh()``
         — but ``is_feature_enabled`` falls back to the stale
         cache (better to show slightly-stale gates than
         nothing) if no refresh has ever succeeded.
      4. Network failure returns ``False`` (deny the feature)
         rather than raising — the Ad tab and other consumers
         must always be able to render SOMETHING.

    Auth: none. The endpoint is unauthenticated per the server's
    design (the desktop calls it BEFORE login / registration).
    """

    def __init__(
        self,
        base_url: str = "https://nchantdoffice.com",
        config_path: str = DEFAULT_VERSION_CONFIG_PATH,
        timeout: float = HTTP_TIMEOUT,
    ):
        self.base_url = base_url.rstrip("/")
        self.config_path = config_path.lstrip("/")
        self.timeout = timeout
        self._session = requests.Session()
        self._features: Dict[str, Feature] = {}
        self.current_version: str = "0.0.1"
        self.release_date: str = ""
        self.check_update_url: str = "/api/check-update"
        # Best-effort: load the cache synchronously so the
        # first is_feature_enabled() call has something to
        # answer from.
        self._load_into_memory()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_feature_enabled(
        self,
        name: str,
        tier: Optional[str] = None,
    ) -> bool:
        """Return True iff the named feature is enabled for the
        given (or current) user tier.

        Args:
          name: the feature key (matches the ``features.<name>``
              keys in the server response).
          tier: optional tier override. When None (the
              common case), the lookup falls back to the
              current user's tier via ``_resolve_user_tier()``
              (which mirrors the Ad tab's
              ``_is_visible_for_user`` pattern).

        Returns:
          True when the feature exists in the matrix, is
          ``enabled=True`` AND ``available=True`` AND the
          feature's tier is unlocked by the user's tier
          (rank-based — Pro unlocks Pro and Free features,
          ProData unlocks Pro + ProData + Free, etc.).

        Failure modes all return False:
          - feature not in matrix → False
          - feature not enabled server-side → False
          - feature not available for this version → False
          - user's tier is below the feature's tier → False
          - no cache + unreachable server → False
        """
        # Fast-path: cache freshness gate (no network call
        # for the common case of repeated UI rebuilds).
        if not self._cache_is_fresh():
            # Stale fallback — use whatever's in memory, even
            # if the cache file is older than the TTL.
            if not self._features:
                return False
        feat = self._features.get(name)
        if feat is None:
            return False
        # The version/availability gates are absolute.
        if not feat.enabled or not feat.available:
            return False
        # The tier gate is rank-based.
        user_tier = tier if tier is not None else self._resolve_user_tier()
        if user_tier not in _TIER_RANK:
            # Unknown tier — be conservative, deny.
            return False
        if feat.tier not in _TIER_RANK:
            # Server returned an unrecognised tier string —
            # be conservative, deny.
            return False
        return _TIER_RANK[user_tier] >= _TIER_RANK[feat.tier]

    def refresh(self) -> bool:
        """Re-fetch the feature matrix from the server.

        Returns True on success, False on failure (network
        error, HTTP error, malformed response). Never raises.

        On success: updates ``self._features``,
        ``self.current_version``, ``self.release_date``,
        ``self.check_update_url`` and writes the cache file.

        On failure: leaves in-memory state untouched (a
        previous successful refresh is preserved) and does
        NOT write the cache (a transient 503 must not
        clobber a good cache hit).
        """
        try:
            response = self._session.get(
                f"{self.base_url}/{self.config_path}",
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json() if response.content else {}
        except (requests.RequestException, ValueError) as e:
            logma.warning(
                f"[feature_gate] GET {self.config_path} failed: {e}"
            )
            return False

        try:
            self._apply_payload(payload)
            self._write_cache(payload)
            return True
        except Exception as e:
            logma.warning(
                f"[feature_gate] payload apply/cache write failed: {e}"
            )
            return False

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_user_tier() -> str:
        """Return the current user's tier.

        Mirrors the Ad tab's ``_is_visible_for_user`` pattern:
          - read ``pyqt.QApplication.instance().model.user``
          - if ``user.has_pro`` → ``TIER_PRO``
          - otherwise → ``TIER_FREE``

        The Ad tab only knows Free vs Pro. FeatureGate
        extends that to 4 tiers by also checking
        ``has_prodata`` / ``has_enterprise`` when those
        attributes exist (future-proofing for when the
        desktop model grows them).
        """
        try:
            from nchantrs.libraries import pyqt as _pyqt

            app = _pyqt.QApplication.instance()
            if app is None:
                return TIER_FREE
            user = getattr(getattr(app, "model", None), "user", None)
            if user is None:
                return TIER_FREE
        except Exception:
            return TIER_FREE

        # Highest tier first — Enterprise beats ProData beats Pro beats Free.
        if getattr(user, "has_enterprise", False):
            return TIER_ENTERPRISE
        if getattr(user, "has_prodata", False):
            return TIER_PRODATA
        if getattr(user, "has_pro", False):
            return TIER_PRO
        return TIER_FREE

    def _apply_payload(self, payload: Dict[str, Any]) -> None:
        """Parse the server response into ``self._features`` +
        the public version fields. Raises on malformed input
        so ``refresh()`` can swallow the exception and return
        False.
        """
        self.current_version = str(payload.get("current_version", "0.0.1"))
        self.release_date = str(payload.get("release_date", ""))
        self.check_update_url = str(
            payload.get("check_update_url", "/api/check-update")
        )
        features_payload = payload.get("features", {}) or {}
        if not isinstance(features_payload, dict):
            raise ValueError(
                f"features must be a dict, got {type(features_payload).__name__}"
            )
        new_features: Dict[str, Feature] = {}
        for name, entry in features_payload.items():
            if not isinstance(entry, dict):
                # Skip malformed entries (don't fail the whole
                # refresh for one bad row).
                logma.warning(
                    f"[feature_gate] skipping malformed feature {name!r}"
                )
                continue
            new_features[str(name)] = Feature.from_response(str(name), entry)
        # Only commit the new map if at least one feature was
        # parsed (otherwise we'd wipe the in-memory state on
        # a partial / empty response).
        if new_features:
            self._features = new_features

    # ------------------------------------------------------------------
    # Cache helpers (mirror checker.py + base_layer.py)
    # ------------------------------------------------------------------

    def _cache_is_fresh(self) -> bool:
        """Return True iff the cache file exists, parses,
        and is younger than REFRESH_INTERVAL_SECONDS.
        """
        try:
            if not _CACHE_PATH.exists():
                return False
            raw = _CACHE_PATH.read_text(encoding="utf-8")
            payload = json.loads(raw)
        except (OSError, ValueError) as e:
            logma.warning(f"[feature_gate] cache read failed: {e}")
            return False
        try:
            cache_time = dt.datetime.fromisoformat(
                payload.get("_cached_at", "")
            )
            age = (
                dt.datetime.now(dt.timezone.utc) - cache_time
            ).total_seconds()
            return age < REFRESH_INTERVAL_SECONDS
        except (ValueError, TypeError):
            return False

    def _load_into_memory(self) -> None:
        """Best-effort: load the cache file into
        ``self._features``. Used by ``__init__`` so the first
        ``is_feature_enabled()`` call has a fallback.
        """
        try:
            if not _CACHE_PATH.exists():
                return
            raw = _CACHE_PATH.read_text(encoding="utf-8")
            payload = json.loads(raw)
        except (OSError, ValueError) as e:
            logma.warning(f"[feature_gate] cache load failed: {e}")
            return
        try:
            self._apply_payload(payload)
        except Exception as e:
            logma.warning(f"[feature_gate] cache apply failed: {e}")

    def _write_cache(self, payload: Dict[str, Any]) -> None:
        """Persist the raw payload to ``_CACHE_PATH`` with
        mode 0o600 (mirrors checker.py + base_layer pattern).
        Includes ``_cached_at`` so ``_cache_is_fresh`` can
        decide without recomputing.
        """
        try:
            _CACHE_DIR.mkdir(parents=True, exist_ok=True)
            enriched = dict(payload)
            enriched["_cached_at"] = dt.datetime.now(
                dt.timezone.utc
            ).isoformat()
            _CACHE_PATH.write_text(
                json.dumps(enriched, indent=2),
                encoding="utf-8",
            )
            os.chmod(_CACHE_PATH, 0o600)
        except OSError as e:
            logma.warning(f"[feature_gate] cache write failed: {e}")


__all__ = [
    "FeatureGate",
    "Feature",
    "DEFAULT_VERSION_CONFIG_PATH",
    "REFRESH_INTERVAL_SECONDS",
    "CACHE_FILENAME",
    "TIER_FREE",
    "TIER_PRO",
    "TIER_PRODATA",
    "TIER_ENTERPRISE",
    "KNOWN_TIERS",
]
