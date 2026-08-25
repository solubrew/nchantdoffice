"""nchantdoffice.license — tier-gating decorator + helpers.

DESK T-NEW-047: tier_gate is the pure-Python decorator and helper
module widget code uses to gate features by entitlement tier
("if the user is on free tier, hide the pro export button").

Design principles
=================

1. **Pure Python, no Qt.** The decorator works on any callable
   so the test suite can exercise it WITHOUT spinning up a
   Qt event loop. Widget integration (DESK T-NEW-049) catches
   the :class:`TierGateDenied` exception at the call site and
   surfaces an upgrade dialog — that's a separate concern.

2. **Single global getter.** :data:`_DEFAULT_TIER_GETTER` is a
   module-level callable. DESK T-NEW-048 installs one on app
   start via :func:`set_tier_getter`. The getter's signature is
   ``fn() -> dict | None`` — the envelope from
   :class:`EntitlementCache.load()`, or ``None`` if no
   entitlement is loaded yet.

3. **Fail-closed defaults.** No getter installed → current tier
   is ``"free"`` (the most-restrictive tier). The desktop MUST
   boot into a known-safe state; we never assume privilege.

4. **Tier hierarchy.** :data:`TIER_HIERARCHY` is a numeric
   ordering (free=0 < pro=1 < pro_data=2 < enterprise=3).
   ``@requires_tier('pro')`` opens the gate for pro AND anything
   ABOVE pro (pro_data, enterprise).

5. **Decorator, not context manager.** ``requires_tier`` is a
   function decorator, not a ``with`` block. The widget call
   sites in DESK T-NEW-049 decorate methods like::

       @requires_tier('pro')
       def export_to_pdf(self) -> None:
           ...
"""
from __future__ import annotations

import functools
from typing import Any, Callable, Dict, Optional

__all__ = [
    "TIER_HIERARCHY",
    "TierGateDenied",
    "set_tier_getter",
    "current_tier",
    "current_envelope",
    "has_feature",
    "requires_tier",
]


# -----------------------------------------------------------------------------
# Tier hierarchy
# -----------------------------------------------------------------------------

# Ordered map of tier name → numeric rank. Used by @requires_tier
# to compute whether the current tier is at-or-above the required
# minimum.
#
# Adding a new tier: choose a name the server agrees on, pick a
# numeric slot at the right position in the ordering, and the
# gate automatically admits it.
TIER_HIERARCHY: Dict[str, int] = {
    "free": 0,
    "pro": 1,
    "pro_data": 2,
    "enterprise": 3,
}

# Default tier the desktop boots into when no entitlement has
# loaded yet. Chosen to be the LEAST privileged — fail closed.
_DEFAULT_BOOT_TIER: str = "free"


# -----------------------------------------------------------------------------
# Tier-getter state
# -----------------------------------------------------------------------------

# Module-level getter. ``None`` until DESK T-NEW-048 installs one
# at app start.
_DEFAULT_TIER_GETTER: Optional[Callable[[], Optional[Dict[str, Any]]]] = None


def set_tier_getter(fn: Callable[[], Optional[Dict[str, Any]]]) -> None:
    """Install the function that returns the current envelope.

    Called by the remote client (DESK T-NEW-048) on app start.
    Signature: ``fn() -> dict | None``. Returns the cached
    envelope from EntitlementCache, or ``None`` if no
    entitlement is available yet.

    Tests use this to inject a fake getter without touching the
    production cache.
    """
    global _DEFAULT_TIER_GETTER
    _DEFAULT_TIER_GETTER = fn


def current_envelope() -> Optional[Dict[str, Any]]:
    """Return the full envelope (or ``None`` if no entitlement
    is loaded).

    Used by tests + the startup refresh flow.
    """
    if _DEFAULT_TIER_GETTER is None:
        return None
    try:
        return _DEFAULT_TIER_GETTER()
    except Exception:  # noqa: BLE001 — getter is untrusted code
        # If the getter raises, treat as "no envelope". Better
        # to fall back to the safe default than to crash a
        # widget render path.
        return None


def current_tier() -> str:
    """Return the current tier string.

    Reads from the installed tier-getter. Falls back to
    ``"free"`` if no entitlement is loaded yet (the desktop
    MUST boot into a known-safe state).

    Unknown tier strings (anything not in :data:`TIER_HIERARCHY`)
    also fall back to ``"free"`` so a malformed server envelope
    cannot escalate privilege.
    """
    envelope = current_envelope()
    if not isinstance(envelope, dict):
        return _DEFAULT_BOOT_TIER
    tier = envelope.get("tier")
    if not isinstance(tier, str) or tier not in TIER_HIERARCHY:
        return _DEFAULT_BOOT_TIER
    return tier


def has_feature(name: str) -> bool:
    """Return ``True`` if the current envelope's ``feat`` list
    includes ``name``. Returns ``False`` if no envelope is
    loaded OR if the envelope has no usable ``feat`` list.

    Fail-closed: a missing envelope is treated as if NO
    features were granted.
    """
    envelope = current_envelope()
    if not isinstance(envelope, dict):
        return False
    feat = envelope.get("feat")
    if not isinstance(feat, list):
        return False
    return name in feat


# -----------------------------------------------------------------------------
# Gate decorator
# -----------------------------------------------------------------------------


class TierGateDenied(Exception):
    """Raised by :func:`requires_tier` when the current tier is
    below the required minimum.

    Attributes
    ----------
    required_tier : str
        The tier the caller demanded (e.g. ``"pro"``).
    current_tier : str
        The tier the user actually has at the time of the call
        (e.g. ``"free"``). Defaults to the boot tier
        (``"free"``) if no envelope is loaded.
    """

    def __init__(self, required_tier: str, current_tier: str) -> None:
        self.required_tier = required_tier
        self.current_tier = current_tier
        super().__init__(
            f"tier gate denied: requires {required_tier!r}, "
            f"current is {current_tier!r}"
        )


def requires_tier(min_tier: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator: gate a function/method by minimum tier.

    Usage::

        @requires_tier('pro')
        def export_to_pdf(self):
            ...

    The decorator:

      1. Resolves ``min_tier`` against :data:`TIER_HIERARCHY`.
         Unknown ``min_tier`` strings raise :class:`TierGateDenied`
         immediately at decoration time — this is intentional:
         a typo in the decorator should be a hard failure, not a
         silently open gate.
      2. On each call, compares the caller's current tier against
         ``min_tier``. If the current tier is BELOW ``min_tier``,
         raises :class:`TierGateDenied(min_tier, current_tier)`.
      3. Otherwise calls the wrapped function and returns the
         result.

    The decorator is synchronous (no event-loop interaction);
    the widget code is expected to handle :class:`TierGateDenied`
    by showing an "upgrade to <min_tier>" dialog.
    """
    if min_tier not in TIER_HIERARCHY:
        raise TierGateDenied(
            required_tier=min_tier,
            current_tier=_DEFAULT_BOOT_TIER,
        )

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            current = current_tier()
            if TIER_HIERARCHY.get(current, -1) < TIER_HIERARCHY[min_tier]:
                raise TierGateDenied(
                    required_tier=min_tier,
                    current_tier=current,
                )
            return fn(*args, **kwargs)

        return wrapper

    return decorator
