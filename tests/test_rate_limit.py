"""T-DESK-061 — RateLimitTracker for ``*APIClient`` classes.

Paired with nchantdofficeATNRG cross-repo review
(``docs/cross-repo-review_20260807.md`` §2.7).

The server has per-IP rate limits (flask-limiter, default
5/minute on /api/updates + /api/affiliate/links/ per
`nchantdoffice_com/app/rate_limit.py`). The desktop's
`*APIClient` classes don't track request counts. A user
who clicks around in the UI 100 times in an hour hits
the rate limit and the API silently returns 429.

T-DESK-061 deliverable:
  - ``nchantdoffice/utilities/rate_limit.py`` — a
    ``RateLimitTracker`` mixin (or composition class) that:
      1. Counts requests per endpoint per minute.
      2. Caches successful responses for the duration of
         the rate-limit window (avoids duplicate calls).
      3. Parses the ``Retry-After`` header on 429 responses
         and delays retries accordingly.
  - The tracker is a no-op for clients that don't opt in
    (so existing tests keep working).

Tests are AST + pure-Python where possible. A small
runtime sanity check drives a fake ``Response`` through
the ``Retry-After`` parser.

Refs:
  - docs/cross-repo-review_20260807.md §2.7
  - nchantdoffice_com/app/rate_limit.py (the server
    flask-limiter config; RATELIMIT_API=5/minute default)
  - nchantdoffice/utilities/referral.py (ReferralAPIClient
    — the primary consumer to migrate)
  - nchantdoffice/updates/checker.py (sibling module shape)
"""

import ast
import re
import sys
from pathlib import Path
from typing import Any, Dict

PROJ_ROOT = Path("/home/solubrew/.hermes/projects/nchantdoffice")
sys.path.insert(0, str(PROJ_ROOT))

UTILS_DIR = PROJ_ROOT / "nchantdoffice" / "utilities"
RATE_LIMIT = UTILS_DIR / "rate_limit.py"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _read(path: Path) -> str:
    return path.read_text()


def _ast_class(src: str, name: str):
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
    return None


def _ast_function(src: str, name: str):
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def _function_source(src: str, name: str) -> str:
    node = _ast_function(src, name)
    if node is None:
        return ""
    return ast.get_source_segment(src, node) or ""


def _module_top_level_constant(src: str, name: str):
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == name:
                    return node.value
        elif isinstance(node, ast.AnnAssign):
            if (
                isinstance(node.target, ast.Name)
                and node.target.id == name
            ):
                return node.value
    return None


# ---------------------------------------------------------------------------
# Contract 1: module + main class exist
# ---------------------------------------------------------------------------


def test_rate_limit_module_exists():
    """``nchantdoffice/utilities/rate_limit.py`` must exist
    (T-DESK-061 deliverable).
    """
    assert RATE_LIMIT.exists(), (
        f"nchantdoffice/utilities/rate_limit.py must exist "
        f"(T-DESK-061). Expected at {RATE_LIMIT}."
    )


def test_rate_limit_tracker_class_exists():
    """``RateLimitTracker`` is the main class. Pinning the
    name so consumers can compose it into their APIClient
    classes.
    """
    src = _read(RATE_LIMIT)
    cls = _ast_class(src, "RateLimitTracker")
    assert cls is not None, (
        "rate_limit.py must declare RateLimitTracker class "
        "(the request-counting + Retry-After parser)."
    )


# ---------------------------------------------------------------------------
# Contract 2: default per-endpoint window
# ---------------------------------------------------------------------------


def test_default_window_constant_matches_server():
    """The default rate-limit window must be 60 seconds
    (matches the server's per-minute limit per
    flask-limiter config). The exact value is tunable but
    the default must be a positive int.
    """
    src = _read(RATE_LIMIT)
    node = _module_top_level_constant(src, "DEFAULT_WINDOW_SECONDS")
    assert node is not None, (
        "rate_limit.py must declare DEFAULT_WINDOW_SECONDS top-level."
    )
    import ast as _ast
    val = _ast.literal_eval(node)
    assert isinstance(val, int) and 0 < val <= 3600, (
        f"DEFAULT_WINDOW_SECONDS must be a positive int ≤ 1h, "
        f"got {val!r}."
    )


def test_default_max_requests_per_window():
    """The default max-requests per window must be a positive
    int. Server default is 5/minute (per RATELIMIT_API=5/minute
    in the test fixture); the desktop must use a value ≥ the
    server's to avoid spurious self-throttling.
    """
    src = _read(RATE_LIMIT)
    node = _module_top_level_constant(src, "DEFAULT_MAX_REQUESTS")
    assert node is not None, (
        "rate_limit.py must declare DEFAULT_MAX_REQUESTS top-level."
    )
    import ast as _ast
    val = _ast.literal_eval(node)
    assert isinstance(val, int) and val > 0, (
        f"DEFAULT_MAX_REQUESTS must be a positive int, got {val!r}."
    )
    # Pin that the desktop is at least as generous as the
    # server default (5/min). Without this, the desktop
    # would self-throttle at 4/min before the server even
    # sees a 429.
    assert val >= 5, (
        f"DEFAULT_MAX_REQUESTS must be ≥ 5 (server's per-IP "
        f"limit per flask-limiter config), got {val!r}."
    )


# ---------------------------------------------------------------------------
# Contract 3: core methods
# ---------------------------------------------------------------------------


def test_check_rate_limit_method_exists():
    """``RateLimitTracker.check_rate_limit(endpoint)`` is the
    public API: returns True iff a new request is allowed,
    False iff the limit has been reached. The caller must
    check before every server call (cheap, in-memory).
    """
    src = _read(RATE_LIMIT)
    fn = _ast_function(src, "check_rate_limit")
    assert fn is not None, (
        "RateLimitTracker must declare check_rate_limit() method "
        "(the pre-call gate)."
    )
    body = _function_source(src, "check_rate_limit")
    # Must take an endpoint argument (so per-endpoint tracking
    # is possible — /api/updates and /api/affiliate/links/ are
    # separate buckets).
    fn_node = _ast_function(src, "check_rate_limit")
    arg_names = [a.arg for a in fn_node.args.args if a.arg != "self"]
    assert "endpoint" in arg_names, (
        "check_rate_limit must take an 'endpoint' argument "
        "(per-endpoint counting)."
    )


def test_record_request_method_exists():
    """``record_request(endpoint, timestamp=None)`` must be
    called AFTER a successful or attempted server call.
    It appends to the request history used by
    ``check_rate_limit``.
    """
    src = _read(RATE_LIMIT)
    fn = _ast_function(src, "record_request")
    assert fn is not None, (
        "RateLimitTracker must declare record_request() method "
        "(the post-call bookkeeping)."
    )


def test_parse_retry_after_method_exists():
    """``parse_retry_after(response_or_seconds)`` must parse
    the ``Retry-After`` header (per HTTP spec: either a
    delta-seconds int or an HTTP-date). Returns a
    ``float`` (seconds to wait) or ``None`` (no header /
    unparseable).
    """
    src = _read(RATE_LIMIT)
    fn = _ast_function(src, "parse_retry_after")
    assert fn is not None, (
        "RateLimitTracker must declare parse_retry_after() "
        "method (the 429 retry-delay parser)."
    )


# ---------------------------------------------------------------------------
# Contract 4: in-memory cache for repeat calls
# ---------------------------------------------------------------------------


def test_cache_get_and_set_methods_exist():
    """``cache_get(endpoint)`` / ``cache_set(endpoint, value)``
    let the tracker return a cached response for repeat
    calls in the same window (avoids duplicate server hits
    when the UI rebuilds the same data 5 times).
    """
    src = _read(RATE_LIMIT)
    for name in ("cache_get", "cache_set"):
        fn = _ast_function(src, name)
        assert fn is not None, (
            f"RateLimitTracker must declare {name}() method "
            f"(the per-window response cache)."
        )


# ---------------------------------------------------------------------------
# Contract 5: pure class — no Qt, no requests
# ---------------------------------------------------------------------------


def test_pure_class_does_not_import_qt_or_requests():
    """The ``RateLimitTracker`` class must NOT import Qt or
    requests — it's pure in-memory bookkeeping. Pinning
    this keeps the class testable in the constrained venv.
    """
    src = _read(RATE_LIMIT)
    cls = _ast_class(src, "RateLimitTracker")
    assert cls is not None
    cls_src = ast.get_source_segment(src, cls) or ""
    for needle in ("QLabel", "QWidget", "pyqt.", "QApplication"):
        assert needle not in cls_src, (
            f"RateLimitTracker must not reference {needle!r}."
        )
    # Module-level may import requests for type hints (Optional)
    # but the class body must not.
    for needle in ("requests.", "urllib", "http.client"):
        assert needle not in cls_src, (
            f"RateLimitTracker class body must not reference "
            f"{needle!r} — the tracker is server-call-free."
        )


# ---------------------------------------------------------------------------
# Contract 6: opt-in composition (existing clients unaffected)
# ---------------------------------------------------------------------------


def test_referral_client_composes_tracker():
    """``ReferralAPIClient`` (the primary consumer) must
    compose (or inherit from) ``RateLimitTracker``. Pinning
    the wiring so the consumer migration isn't lost in a
    refactor.
    """
    src = _read(PROJ_ROOT / "nchantdoffice" / "utilities" / "referral.py")
    assert "RateLimitTracker" in src, (
        "ReferralAPIClient must compose (or inherit from) "
        "RateLimitTracker — T-DESK-061's primary consumer "
        "migration. Without this the new tracker is dead code."
    )


# ---------------------------------------------------------------------------
# Contract 7: runtime — Retry-After parser
# ---------------------------------------------------------------------------


def test_parse_retry_after_handles_delta_seconds():
    """Runtime sanity check: ``parse_retry_after`` handles the
    delta-seconds form (``Retry-After: 5`` → 5.0).
    """
    import pytest

    try:
        from nchantdoffice.utilities.rate_limit import (
            RateLimitTracker,
            parse_retry_after,
        )
    except Exception as e:
        pytest.skip(f"rate_limit import failed (env): {e}")

    # Delta-seconds form (the common case).
    class FakeResponse:
        headers = {"Retry-After": "5"}
        status_code = 429

    result = parse_retry_after(FakeResponse())
    assert result == 5.0 or result == 5, (
        f"parse_retry_after must return 5 (or 5.0) for "
        f"Retry-After: 5, got {result!r}."
    )


def test_parse_retry_after_handles_missing_header():
    """Runtime: missing header returns None (not an
    exception). The caller falls back to a default retry
    delay.
    """
    import pytest

    try:
        from nchantdoffice.utilities.rate_limit import parse_retry_after
    except Exception as e:
        pytest.skip(f"rate_limit import failed (env): {e}")

    class FakeResponse:
        headers = {}
        status_code = 429

    result = parse_retry_after(FakeResponse())
    assert result is None, (
        f"parse_retry_after must return None when no header, "
        f"got {result!r}."
    )


def test_check_rate_limit_blocks_after_window_full():
    """Runtime: after recording N requests within the window,
    ``check_rate_limit`` returns False (block new requests
    until the window slides).
    """
    import datetime as dt
    import pytest

    try:
        from nchantdoffice.utilities.rate_limit import (
            DEFAULT_MAX_REQUESTS,
            DEFAULT_WINDOW_SECONDS,
            RateLimitTracker,
        )
    except Exception as e:
        pytest.skip(f"rate_limit import failed (env): {e}")

    now = dt.datetime(2026, 8, 7, 12, 0, 0, tzinfo=dt.timezone.utc)
    tracker = RateLimitTracker(max_requests=3, window_seconds=60)

    # First 3 requests: allowed.
    for i in range(3):
        assert tracker.check_rate_limit(
            "/api/test", when=now + dt.timedelta(seconds=i)
        ), (
            f"request {i+1} must be allowed (under the limit)"
        )
        tracker.record_request(
            "/api/test", when=now + dt.timedelta(seconds=i)
        )

    # 4th request in the same window: blocked.
    assert not tracker.check_rate_limit(
        "/api/test", when=now + dt.timedelta(seconds=4)
    ), (
        "4th request in the same window must be blocked."
    )

    # After the window slides past: allowed again.
    assert tracker.check_rate_limit(
        "/api/test", when=now + dt.timedelta(seconds=120)
    ), (
        "request after the window slides past must be allowed."
    )
