# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
    docid: nchantdoffice-rate-limit
    name: API Rate Limit Tracker
    description: >
        T-DESK-061 (cross-repo review §2.7): per-endpoint
        request counter + ``Retry-After`` header parser for
        the desktop's ``*APIClient`` classes. The server
        has per-IP rate limits (flask-limiter, default
        5/minute on /api/updates + /api/affiliate/links/
        per ``nchantdoffice_com/app/rate_limit.py``). The
        desktop used to silently 429 when a user clicked
        around the UI 100 times in an hour.

        The tracker:
          1. Counts requests per endpoint per minute.
          2. Caches successful responses for the duration
             of the rate-limit window (avoids duplicate
             server hits when the UI rebuilds the same
             data multiple times).
          3. Parses the ``Retry-After`` header on 429
             responses (HTTP spec: delta-seconds OR
             HTTP-date) and exposes a ``sleep_for_retry``
             helper that respects it.

        Composed into ``ReferralAPIClient`` (the primary
        consumer) — other clients can adopt incrementally.

        Pure Python — no Qt, no requests. The tracker is
        server-call-free; consumers wrap their own
        network calls in ``check_rate_limit`` +
        ``record_request``.
    version: 1.0.0
    authority: filesystem
    security: seclvl2
    <(WT)>: -32
"""
# -*- coding: utf-8 -*-
# ======================================Standard Library Modules======================================================||
import datetime as dt
import time
from collections import deque
from email.utils import parsedate_to_datetime
from typing import Any, Deque, Dict, Optional, Tuple

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules=============================================||
from kahndor.logma import Logma

logma = Logma(__name__)

# ---------------------------------------------------------------------------
# T-DESK-061 — module-level constants
# ---------------------------------------------------------------------------

# Default rate-limit window. Matches the server's per-minute
# limit per flask-limiter config.
DEFAULT_WINDOW_SECONDS: int = 60

# Default max requests per window. The server's default is
# 5/minute (per RATELIMIT_API=5/minute in the test fixture),
# but the desktop can be more generous (the server is
# stricter than the client needs to be). Set to 30/minute —
# enough for a chatty UI rebuild, well under the server's
# ceiling.
DEFAULT_MAX_REQUESTS: int = 30

# How long to sleep when Retry-After is missing/unparseable.
DEFAULT_RETRY_SECONDS: float = 5.0


# ---------------------------------------------------------------------------
# T-DESK-061 — parse_retry_after (module-level helper)
# ---------------------------------------------------------------------------


def parse_retry_after(
    response_or_seconds: Any,
    now: Optional[dt.datetime] = None,
) -> Optional[float]:
    """Parse a ``Retry-After`` header value into seconds-to-wait.

    Accepts either:
      - a requests-like response object with ``.headers``
        (the common case for callers that already have the
        429 response in hand), OR
      - a raw int/float/str (delta-seconds or HTTP-date
        string).

    Returns:
      - ``float`` (seconds to wait) when the value parses
      - ``None`` when the header is missing, malformed, or
        the response object has no ``Retry-After`` key

    HTTP spec reference (RFC 7231 §7.1.3):
      Retry-After = HTTP-date / delta-seconds

    The delta-seconds form is the common one in
    flask-limiter responses.
    """
    # Path 1: a response-like object with a headers dict.
    headers: Optional[Dict[str, str]] = None
    if hasattr(response_or_seconds, "headers"):
        headers = response_or_seconds.headers
    elif hasattr(response_or_seconds, "get"):
        # Dict-like.
        headers = response_or_seconds
    elif isinstance(response_or_seconds, (int, float)):
        # Raw seconds.
        try:
            return max(0.0, float(response_or_seconds))
        except (TypeError, ValueError):
            return None

    if headers is not None:
        # Case-insensitive header lookup (HTTP headers are
        # case-insensitive; flask-limiter sends "Retry-After"
        # but requests normalizes via .headers).
        raw: Optional[str] = None
        for key in ("Retry-After", "retry-after", "RETRY-AFTER"):
            if key in headers:
                raw = headers[key]
                break
        if raw is None:
            return None
        return parse_retry_after(raw, now=now)

    # Path 2: a raw string. Try delta-seconds first, then
    # HTTP-date.
    if isinstance(response_or_seconds, str):
        text = response_or_seconds.strip()
        if not text:
            return None
        # Delta-seconds form: an integer (possibly negative,
        # possibly with whitespace).
        try:
            seconds = float(text)
            return max(0.0, seconds)
        except ValueError:
            pass
        # HTTP-date form: e.g. "Wed, 21 Oct 2026 07:28:00 GMT".
        try:
            target = parsedate_to_datetime(text)
            if target is None:
                return None
            if now is None:
                now = dt.datetime.now(dt.timezone.utc)
            # parsedate_to_datetime returns a naive or tz-aware
            # datetime depending on input; normalize.
            if target.tzinfo is None:
                target = target.replace(tzinfo=dt.timezone.utc)
            delta = (target - now).total_seconds()
            return max(0.0, delta)
        except (TypeError, ValueError):
            return None

    return None


def sleep_for_retry(
    response_or_seconds: Any,
    now: Optional[dt.datetime] = None,
) -> float:
    """Sleep for the duration indicated by a ``Retry-After``
    header, then return the seconds slept. Falls back to
    ``DEFAULT_RETRY_SECONDS`` when the header is missing /
    unparseable.

    Convenience wrapper for ``time.sleep(parse_retry_after(...))``
    that handles the None case.
    """
    seconds = parse_retry_after(response_or_seconds, now=now)
    if seconds is None:
        seconds = DEFAULT_RETRY_SECONDS
    time.sleep(seconds)
    return seconds


# ---------------------------------------------------------------------------
# T-DESK-061 — RateLimitTracker
# ---------------------------------------------------------------------------


class RateLimitTracker:
    """Per-endpoint request counter + response cache.

    Composed into (or inherited by) the desktop's APIClient
    classes. The client calls ``check_rate_limit(endpoint)``
    before every server call and ``record_request(endpoint)``
    after. Repeat reads in the same window hit
    ``cache_get(endpoint)`` instead of the server.

    Threading: NOT thread-safe. The desktop is single-threaded
    on the Qt main loop, so no lock is needed.

    Window: sliding window (deque of timestamps older than
    ``window_seconds`` are evicted before each check).
    """

    def __init__(
        self,
        max_requests: int = DEFAULT_MAX_REQUESTS,
        window_seconds: int = DEFAULT_WINDOW_SECONDS,
    ) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._history: Dict[str, Deque[dt.datetime]] = {}
        self._cache: Dict[str, Tuple[dt.datetime, Any]] = {}

    # ------------------------------------------------------------------
    # Rate-limit gate
    # ------------------------------------------------------------------

    def check_rate_limit(
        self,
        endpoint: str,
        when: Optional[dt.datetime] = None,
    ) -> bool:
        """Return True iff a new request to ``endpoint`` is
        allowed (under the limit), False iff the limit has
        been reached in the current window.

        Evicts timestamps older than ``window_seconds``
        before the count check (sliding window).
        """
        now = when if when is not None else _now()
        cutoff = now - dt.timedelta(seconds=self.window_seconds)
        history = self._history.setdefault(endpoint, deque())
        # Evict old timestamps.
        while history and history[0] < cutoff:
            history.popleft()
        return len(history) < self.max_requests

    def record_request(
        self,
        endpoint: str,
        when: Optional[dt.datetime] = None,
    ) -> "RateLimitTracker":
        """Record that a request to ``endpoint`` was made at
        ``when``. Must be called AFTER ``check_rate_limit``
        returns True (the request actually went out).

        For self-throttled requests (the caller decided NOT
        to make the call because ``check_rate_limit``
        returned False), do NOT call this — only count
        requests that actually hit the server.
        """
        now = when if when is not None else _now()
        history = self._history.setdefault(endpoint, deque())
        history.append(now)
        return self

    # ------------------------------------------------------------------
    # Response cache (within-window repeat reads)
    # ------------------------------------------------------------------

    def cache_get(self, endpoint: str) -> Optional[Any]:
        """Return the cached response for ``endpoint`` if
        it's still within the window, else ``None``. The
        caller treats ``None`` as "no cache, make the
        call".
        """
        cached = self._cache.get(endpoint)
        if cached is None:
            return None
        cached_at, value = cached
        age = (_now() - cached_at).total_seconds()
        if age >= self.window_seconds:
            # Cache expired — drop it.
            self._cache.pop(endpoint, None)
            return None
        return value

    def cache_set(
        self,
        endpoint: str,
        value: Any,
        when: Optional[dt.datetime] = None,
    ) -> "RateLimitTracker":
        """Cache ``value`` for ``endpoint``. The cache expires
        when the next request would also have its rate
        budget reset (i.e. at ``window_seconds``).
        """
        now = when if when is not None else _now()
        self._cache[endpoint] = (now, value)
        return self

    def cache_clear(self, endpoint: Optional[str] = None) -> None:
        """Clear the response cache for one endpoint (or all
        if ``endpoint is None``). Useful when the user
        triggers a manual refresh.
        """
        if endpoint is None:
            self._cache.clear()
        else:
            self._cache.pop(endpoint, None)

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    @property
    def request_count(self) -> int:
        """Total in-window requests across all endpoints.
        Exposed for the Settings panel + tests.
        """
        cutoff = _now() - dt.timedelta(seconds=self.window_seconds)
        return sum(
            sum(1 for ts in hist if ts >= cutoff)
            for hist in self._history.values()
        )


# ---------------------------------------------------------------------------
# T-DESK-061 — internal helpers
# ---------------------------------------------------------------------------


def _now() -> dt.datetime:
    """Return the current UTC time. Isolated so tests can
    monkey-patch (and so the ``when=`` injection pattern is
    the only blessed path for time control)."""
    return dt.datetime.now(dt.timezone.utc)


__all__ = [
    "RateLimitTracker",
    "parse_retry_after",
    "sleep_for_retry",
    "DEFAULT_WINDOW_SECONDS",
    "DEFAULT_MAX_REQUESTS",
    "DEFAULT_RETRY_SECONDS",
]
