"""nchantdoffice.license — startup entitlement-refresh orchestrator.

DESK T-NEW-050 lives here. The desktop's license module (046
through 049) is fully implemented but nothing actually USES it on
app start. This module is the thin glue: a single function,
:func:`refresh_if_needed`, that the application calls at the end
of the boot sequence to:

  1. Register a fresh install with the server (``sync_bootstrap``);
  2. Rotate the entitlement token when the cache is expired-or-
     close to expiry (``sync_refresh``);
  3. Re-attempt the bootstrap when the server has revoked the
     install row (the api_key may have been rotated server-side;
     the same ``install_id`` + ``hardware_key`` re-bootstraps);
  4. Persist an ``entitlement_stale`` flag in the user's
     preferences so the next launch retries after a transient
     network failure.

The orchestrator is intentionally sync-only: it calls
:class:`LicenseRemote.sync_bootstrap` / :meth:`LicenseRemote.sync_refresh`
(the ``asyncio.run`` wrappers). The widget layer runs on the
GUI thread and can't await; the underlying aiohttp client has
already been wrapped for that contract.

Decision tree
=============

  ::

      +-----------+
      |  start    |
      +-----+-----+
            |
            v
      +-----------+   no   +-----------------+
      | has api_key|----+  | InstallStore    |
      +-----------+    |  +-----------------+
            | yes      |          |
            v          |          v
      +-----------+    |   +--------------------+
      | has cache |----+-->| sync_bootstrap()   |
      +-----------+        +--------------------+
            |
            v
      +-----------------------------+
      | cache expired or close?     |--yes--> sync_refresh()
      +-----------------------------+
            | no
            v
      +-----------------------------+
      | prefs stale flag is True?   |--yes--> sync_refresh()
      +-----------------------------+
            | no
            v
      +----------+
      | skip()   |
      +----------+

The ``sync_refresh`` path has its own error routing:

  - :class:`RefreshRevokedError` -> ``sync_bootstrap`` (the api_key
    is gone server-side; re-register the same install).
  - any other :class:`RefreshError` / :class:`OSError` /
    :class:`asyncio.TimeoutError` -> ``{action: 'skipped', reason:
    'offline'}`` (the desktop still boots; the next launch will
    retry when the network is back).

On every outcome, the orchestrator persists
``entitlement_stale`` to the preferences shim:

  - ``False`` on a successful bootstrap / refresh / "cache is
    fresh" skip;
  - ``True`` on any transient failure, so the next launch
    retries (the stale flag overrides the "cache is fresh"
    optimisation).

The ``preferences_db`` argument is duck-typed: any object
exposing ``get(key, default=None)`` and ``set(key, value)`` will
do. The tests inject a tiny ``MockPreferencesDB`` shim; the
production caller wires the desktop's YAML config dict via
``self.config.dikt["preferences"]``.

Raises
======
:meth:`refresh_if_needed` raises :class:`BootstrapError` when
the bootstrap fails with a real server error (4xx/5xx) —
the server told us something we cannot ignore and the user
must intervene. **Transient failures during both bootstrap
and refresh are swallowed**: DNS failures, refused
connections, :class:`asyncio.TimeoutError` on first launch
return ``{action: 'skipped', reason: 'offline'}`` so the
desktop still boots. The persistent ``entitlement_stale``
flag is set so the next launch retries the network call when
the user is back online.
"""
from __future__ import annotations

import asyncio
import datetime as dt
import logging
import os
import platform
from typing import Any, Dict, Optional

from nchantdoffice.license.entitlement_cache import EntitlementCache
from nchantdoffice.license.install_store import InstallStore
from nchantdoffice.license.remote import (
    BootstrapError,
    RefreshError,
    RefreshRevokedError,
)


__all__ = ["refresh_if_needed"]


# Module-level logger so caplog can pick up warnings in tests.
_logger = logging.getLogger("nchantdoffice.license.startup_refresh")
if not _logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(name)s %(levelname)s %(message)s"))
    _logger.addHandler(_handler)
    _logger.setLevel(logging.INFO)


# Key the orchestrator reads + writes in the preferences shim.
# Centralised so the test suite + production caller agree.
_ENTITLEMENT_STALE_KEY: str = "entitlement_stale"


# -----------------------------------------------------------------------------
# Public surface
# -----------------------------------------------------------------------------


def refresh_if_needed(
    install_store: InstallStore,
    entitlement_cache: EntitlementCache,
    license_remote: Any,
    preferences_db: Optional[Any] = None,
    refresh_threshold_seconds: int = 12 * 3600,
) -> Dict[str, Any]:
    """Decide whether to bootstrap, refresh, or skip — and run it.

    The decision tree (in evaluation order):

      1. ``InstallStore`` has no ``api_key`` -> :meth:`LicenseRemote.sync_bootstrap`.
         The bootstrap persists ``api_key`` + ``desktop_uuid`` back
         into the InstallStore.
      2. ``InstallStore`` has an ``api_key`` but no entitlement
         envelope in the cache -> :meth:`LicenseRemote.sync_refresh`
         to populate it.
      3. Cache exists AND
         :meth:`EntitlementCache.is_expired_or_close` returns True
         -> :meth:`LicenseRemote.sync_refresh`.
      4. Cache exists AND the persistent-stale flag (from
         ``preferences_db``) is True -> :meth:`LicenseRemote.sync_refresh`.
      5. Otherwise: skip (returns ``{action: 'skipped', reason: 'fresh'}``).

    If :meth:`sync_refresh` raises :class:`RefreshRevokedError`,
    fall back to :meth:`sync_bootstrap` (the server may have
    rotated the ``api_key``; the same ``install_id`` +
    ``hardware_key`` re-bootstraps).

    If :meth:`sync_refresh` raises any other
    :class:`RefreshError` (or a transient network error /
    :class:`OSError` / :class:`asyncio.TimeoutError`), swallow it
    and return ``{action: 'skipped', reason: 'offline'}`` — the
    desktop MUST boot even when the user is offline.

    On a successful bootstrap or refresh: persist
    ``entitlement_stale=False`` to ``preferences_db`` (when
    provided). On any error: persist ``entitlement_stale=True``
    so the next launch retries.

    Parameters
    ----------
    install_store : InstallStore
        The per-machine install record source. Read for
        ``install_id`` + ``hardware_key`` + ``api_key``; written
        on a successful bootstrap.
    entitlement_cache : EntitlementCache
        The on-disk cache of the entitlement envelope. Read for
        the current state; written on a successful bootstrap or
        refresh.
    license_remote : LicenseRemote-like
        Any object exposing ``sync_bootstrap(*args, **kwargs)``
        and ``sync_refresh(*args, **kwargs)`` — the production
        caller passes :class:`LicenseRemote`; tests inject
        ``MockLicenseRemote``.
    preferences_db : duck-typed mapping, optional
        Any object exposing ``get(key, default=None)`` and
        ``set(key, value)``. ``None`` is allowed: the
        orchestrator just skips the persistent stale flag.
    refresh_threshold_seconds : int
        The "expired-or-close" window passed to
        :meth:`EntitlementCache.is_expired_or_close`. Default is
        12h (the spec).

    Returns
    -------
    dict
        ``{action, reason, tier}``:

          - ``action``: ``"bootstrap"``, ``"refresh"``, or
            ``"skipped"``.
          - ``reason``: a short string explaining why this action
            was taken (e.g. ``"first_launch"``, ``"expired_or_close"``,
            ``"stale_flag"``, ``"refresh_revoked_fallback"``,
            ``"offline"``, ``"fresh"``).
          - ``tier``: the tier string after the action (read via
            :func:`tier_gate.current_tier`), or ``None`` if no
            envelope was loaded.

    Raises
    ------
    BootstrapError
        When bootstrap fails with a real server error (4xx/5xx)
        — the server told us something we cannot ignore and
        the user must intervene. **Transient failures during
        both bootstrap and refresh are swallowed**: DNS
        failures, refused connections, and
        :class:`asyncio.TimeoutError` return ``{action:
        'skipped', reason: 'offline'}`` so the desktop still
        boots. The persistent ``entitlement_stale`` flag is
        set so the next launch retries the network call when
        the user is back online.
    """
    # Lazy import keeps the orchestrator usable from test contexts
    # where the full tier_gate stack isn't initialised. Also avoids
    # a module-level cycle if tier_gate ever needs to call back
    # into startup_refresh.
    from nchantdoffice.license import tier_gate

    record = install_store.get_or_create()
    install_id = record["install_id"]
    hardware_key = record["hardware_key"]
    api_key = record.get("api_key")

    # ---- decision ----------------------------------------------------------

    if not api_key:
        # First launch — register the install with the server.
        # The bootstrap path persists credentials back into the
        # InstallStore, so a subsequent launch sees this as
        # "existing install" and falls into the refresh branch.
        try:
            bootstrap_body = license_remote.sync_bootstrap(
                install_id=install_id,
                hardware_key=hardware_key,
                public_key="",
                os=_detect_os(),
                app_version=_app_version(),
            )
        except (asyncio.TimeoutError, OSError) as exc:
            # Transient network failure on first launch (DNS
            # failure, refused connection, timeout) — the desktop
            # MUST still boot. We log the failure, persist the
            # stale flag so the next launch retries, and return a
            # ``skipped/offline`` result so the tier gate falls
            # through to free.
            #
            # Bug-fix (DESK T-NEW-051): previously this case was
            # caught by a generic ``except Exception`` and re-
            # raised, which propagated the OSError out of
            # :meth:`NchantdOfficeCloakView.__init__` and crashed
            # the desktop boot on every offline launch.
            _set_stale(preferences_db, True)
            _logger.warning(
                "startup_refresh: first-launch bootstrap failed (%s); "
                "booting offline, will retry next launch",
                exc,
            )
            return {
                "action": "skipped",
                "reason": "offline",
                "tier": _tier_or_none(None),
            }
        except Exception as exc:
            # Bootstrap raised a non-network error (a real
            # :class:`BootstrapError` from a 4xx/5xx server
            # response, or any other unexpected failure). The
            # server told us something we can't ignore — log,
            # mark stale, and re-raise so the widget layer can
            # surface "license server rejected this install".
            _set_stale(preferences_db, True)
            _logger.error(
                "startup_refresh: bootstrap failed (%s); cannot continue", exc,
                exc_info=True,
            )
            raise

        _set_stale(preferences_db, False)
        return {
            "action": "bootstrap",
            "reason": "first_launch",
            "tier": _tier_or_none(bootstrap_body),
        }

    # Existing install: try refresh (or skip).
    cache_record = entitlement_cache.load()
    stale_flag = _get_stale(preferences_db)
    expired_or_close = entitlement_cache.is_expired_or_close(
        threshold_seconds=refresh_threshold_seconds
    )

    should_refresh = (
        cache_record is None
        or expired_or_close
        or stale_flag is True
    )

    if not should_refresh:
        # Healthy cache + no stale flag -> skip. Clear the stale
        # flag defensively so a stale-flag carry-over from a
        # prior failure can't outlive the next successful run.
        _set_stale(preferences_db, False)
        return {
            "action": "skipped",
            "reason": "fresh",
            "tier": _tier_or_none(None),
        }

    # ---- refresh path ------------------------------------------------------

    try:
        refresh_body = license_remote.sync_refresh(
            api_key=api_key,
            install_id=install_id,
            hardware_key=hardware_key,
        )
    except RefreshRevokedError:
        # Server rotated or revoked the api_key. Re-bootstrap with
        # the same install_id + hardware_key. If the hardware_key
        # still matches the server's stored hash, the server will
        # re-issue a fresh api_key + desktop_uuid.
        _logger.warning(
            "startup_refresh: refresh raised RefreshRevokedError; "
            "falling back to bootstrap"
        )
        try:
            bootstrap_body = license_remote.sync_bootstrap(
                install_id=install_id,
                hardware_key=hardware_key,
                public_key="",
                os=_detect_os(),
                app_version=_app_version(),
            )
        except (asyncio.TimeoutError, OSError) as exc:
            # Network failure on the bootstrap fallback after a
            # RefreshRevokedError — same fail-soft treatment as
            # the first-launch path. The desktop still boots;
            # the next launch will retry.
            _set_stale(preferences_db, True)
            _logger.warning(
                "startup_refresh: bootstrap-fallback-after-revoke "
                "failed (%s); booting offline, will retry next launch",
                exc,
            )
            return {
                "action": "skipped",
                "reason": "offline",
                "tier": _tier_or_none(None),
            }
        except Exception as exc:
            # Real bootstrap failure on the fallback — log, mark
            # stale, re-raise so the caller surfaces a license
            # error UI.
            _set_stale(preferences_db, True)
            _logger.error(
                "startup_refresh: bootstrap fallback failed (%s); "
                "cannot continue", exc, exc_info=True,
            )
            raise
        _set_stale(preferences_db, False)
        return {
            "action": "bootstrap",
            "reason": "refresh_revoked_fallback",
            "tier": _tier_or_none(bootstrap_body),
        }
    except (RefreshError, asyncio.TimeoutError, OSError) as exc:
        # Transient failure (network error, plain 401/5xx).
        # The desktop MUST still boot — surface a skipped result
        # and persist stale=True so the next launch retries.
        _logger.warning(
            "startup_refresh: refresh failed (%s); skipping refresh, "
            "desktop boots with cached envelope / falls back to free",
            exc,
        )
        _set_stale(preferences_db, True)
        return {
            "action": "skipped",
            "reason": "offline",
            "tier": _tier_or_none(None),
        }

    _set_stale(preferences_db, False)
    return {
        "action": "refresh",
        # Differentiate "we refreshed because the cache was empty"
        # from "we refreshed because the cache was stale/expired"
        # so the operator can see the decision in logs.
        "reason": _refresh_reason(cache_record, expired_or_close, stale_flag),
        "tier": _tier_or_none(refresh_body),
    }


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------


def _refresh_reason(
    cache_record: Optional[Dict[str, Any]],
    expired_or_close: bool,
    stale_flag: bool,
) -> str:
    """Pick the most informative reason for a refresh action."""
    if cache_record is None:
        return "missing_cache"
    if expired_or_close:
        return "expired_or_close"
    if stale_flag:
        return "stale_flag"
    # Defensive — should not happen given the decision-tree above,
    # but the operator logs are easier to read with a real reason.
    return "stale_flag"


def _set_stale(preferences_db: Optional[Any], value: bool) -> None:
    """Persist ``entitlement_stale=value`` to the preferences shim.

    Duck-typed: tolerates both shapes the desktop's wiring can
    pass —

      * a PreferencesDB-style object with ``.set(key, value)``
        (used by the desktop's future real preferences store);
      * a plain ``dict`` (the production caller in
        :mod:`nchantdoffice.views` reads
        ``self.config.dikt["preferences"]``, which is a plain
        YAML config dict — dicts have no ``.set`` method, only
        ``__setitem__``).

    The two are disambiguated by ``hasattr(preferences_db, "set")``
    — a duck-typed preference for the explicit ``set`` method
    when present (preserves the SQLite-style API), falling back
    to subscript assignment for plain dicts.

    ``None`` is a no-op (the production caller always provides
    one, but tests may skip it). All write failures are logged
    as warnings and swallowed (preferences failures are
    non-fatal — the orchestrator must never block app boot on a
    config write).
    """
    if preferences_db is None:
        return
    try:
        if hasattr(preferences_db, "set"):
            preferences_db.set(_ENTITLEMENT_STALE_KEY, value)
        else:
            preferences_db[_ENTITLEMENT_STALE_KEY] = value
    except Exception as exc:  # noqa: BLE001 — preferences failures are non-fatal
        _logger.warning(
            "startup_refresh: could not write %s=%s to preferences_db: %s",
            _ENTITLEMENT_STALE_KEY, value, exc,
        )


def _get_stale(preferences_db: Optional[Any]) -> bool:
    """Read ``entitlement_stale`` from the preferences shim.

    Returns ``False`` when the key is unset, when the shim is
    ``None``, or when the read raises. Conservative default: if
    we can't read the flag, treat the cache as if it were
    healthy (the orchestrator will fall back to
    :meth:`is_expired_or_close` for the real decision).
    """
    if preferences_db is None:
        return False
    try:
        value = preferences_db.get(_ENTITLEMENT_STALE_KEY, False)
    except Exception as exc:  # noqa: BLE001 — preferences failures are non-fatal
        _logger.warning(
            "startup_refresh: could not read %s from preferences_db: %s",
            _ENTITLEMENT_STALE_KEY, exc,
        )
        return False
    return value is True


def _tier_or_none(body: Optional[Dict[str, Any]]) -> Optional[str]:
    """Extract a tier string from a bootstrap/refresh body.

    The orchestrator doesn't actually NEED the tier string — the
    callers all read it via :func:`tier_gate.current_tier`. We
    still return it for the operator log so the post-action tier
    is visible without a second lookup.
    """
    from nchantdoffice.license import tier_gate

    # Refresh from tier_gate (the source of truth) so the answer
    # matches what the widget layer will see.
    return tier_gate.current_tier()


def _detect_os() -> str:
    """Return the lowercase OS string the server expects.

    Mirrors :class:`InstallStore._read_os_machine_id`'s platform
    detection — but we keep it inline because the orchestrator
    shouldn't depend on a private InstallStore method.
    """
    system = platform.system().lower()
    if system == "linux":
        return "linux"
    if system == "darwin":
        return "macos"
    if system in ("windows", "win32"):
        return "windows"
    return system


def _app_version() -> str:
    """Best-effort desktop version string.

    The server stores this for telemetry; it doesn't validate
    it. We read from the ``NCHANTD_OFFICE_VERSION`` environment
    variable when present (mirrors the upstream pattern), and
    fall back to ``"0.0.0"`` when not.
    """
    return os.environ.get("NCHANTD_OFFICE_VERSION", "0.0.0")