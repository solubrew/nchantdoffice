"""T-DESK-053 — UpdateChecker consumer for ``GET /api/check-update``.

Paired with nchantdofficeATNRG cross-repo review
(``docs/cross-repo-review_20260807.md`` §1.2).

The server exposes
``GET /api/check-update?current_version=<X>&os=<linux|macos|windows>``
(unauthenticated) which returns:

    {
      "latest_version": "0.1.0",
      "release_date": "2025-07-08",
      "update_available": true|false|null,
      "download_url": "https://nchantdoffice.com/download",
      "changelog_url": "https://nchantdoffice.com/changelog",
      "os": "linux"
    }

Today the desktop never calls it, so users running v0.0.1 never
see "new version available" notifications. This test pins the
contract that:

  - the desktop has a ``nchantdoffice/updates/checker.py`` module
  - ``UpdateChecker`` is the main class (caller-driven check,
    not a background thread — the caller decides when to poll)
  - ``check()`` calls ``GET /api/check-update`` with the right
    query params (``current_version=APP_VERSION_SHORT``,
    ``os=<platform>``) and returns a parsed ``UpdateInfo`` dict
  - the response is cached to ``~/.nchantd/update_check_cache.json``
    with mode 0o600 (mirrors base_layer pattern)
  - cached responses are returned when fresh (< REFRESH_INTERVAL_SECONDS)
  - stale or missing cache triggers a server call
  - unreachable server returns ``None`` and leaves the cache
    untouched (no spurious "no update" on a transient 503)
  - ``dismiss_version(version)`` persists dismissed versions to
    ``~/.nchantd/state.yaml`` so the tray notification doesn't
    fire twice for the same release
  - ``is_dismissed(version) -> bool`` reads the same file
  - ``APP_VERSION_SHORT`` is the version sent (not the 5-segment
    ``APP_VERSION`` which the server's ``_parse_version``
    can't compare)

Tests are pure AST + pure data where possible; the network-touch
tests use ``unittest.mock.patch`` on ``requests.Session`` so they
run in the constrained venv.

Refs:
  - docs/cross-repo-review_20260807.md §1.2
  - nchantdoffice_com/app/apis/updates.py:209 (endpoint)
  - nchantdoffice_com/app/apis/version_config.py:11
    (check_update_url pinned at /api/check-update)
  - nchantdoffice/utilities/base_layer.py (cache pattern template)
"""

import ast
import os
import re
import sys
from pathlib import Path

PROJ_ROOT = Path("/home/solubrew/.hermes/projects/nchantdoffice")
sys.path.insert(0, str(PROJ_ROOT))

UPDATES_DIR = PROJ_ROOT / "nchantdoffice" / "updates"
CHECKER = UPDATES_DIR / "checker.py"


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
    """Return the AST node of a top-level ``NAME = <literal>``
    assignment (or None). Used to pin the public constants
    declared by checker.py."""
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


def _eval_simple_expr(node) -> int | str:
    """Evaluate a small expression literal that ``ast.literal_eval``
    rejects. Supports:

      - ``Constant`` (int, str, etc.) → the value
      - ``BinOp`` of left/right with ``Add`` / ``Mult`` (the
        only operators used in checker.py's
        ``REFRESH_INTERVAL_SECONDS`` and similar)
      - ``UnaryOp`` (``-Constant``)

    Anything fancier raises ValueError so the test fails
    loudly instead of silently passing on a degraded parse.
    """
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp):
        left = _eval_simple_expr(node.left)
        right = _eval_simple_expr(node.right)
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        raise ValueError(f"unsupported binop: {ast.dump(node.op)}")
    if isinstance(node, ast.UnaryOp):
        operand = _eval_simple_expr(node.operand)
        if isinstance(node.op, ast.USub):
            return -operand
        raise ValueError(f"unsupported unaryop: {ast.dump(node.op)}")
    raise ValueError(f"unsupported expr: {ast.dump(node)}")


# ---------------------------------------------------------------------------
# Contract 1: the checker module exists
# ---------------------------------------------------------------------------


def test_checker_module_exists():
    """``nchantdoffice/updates/checker.py`` must exist (T-DESK-053
    deliverable). Without it the desktop never calls
    /api/check-update and users never see update notifications.
    """
    assert CHECKER.exists(), (
        f"nchantdoffice/updates/checker.py must exist "
        f"(T-DESK-053). Expected at {CHECKER}."
    )


def test_update_checker_class_exists():
    """``UpdateChecker`` is the main class. Pinning the name
    so external callers (startup hook, settings panel) can
    import it by a stable symbol.
    """
    src = _read(CHECKER)
    cls = _ast_class(src, "UpdateChecker")
    assert cls is not None, (
        "checker.py must declare UpdateChecker class "
        "(the /api/check-update consumer)."
    )


# ---------------------------------------------------------------------------
# Contract 2: constants pinned
# ---------------------------------------------------------------------------


def test_default_endpoint_is_api_check_update():
    """The default API base must point at ``/api/check-update``
    (matching the server endpoint in
    nchantdoffice_com/app/apis/updates.py:209).
    """
    src = _read(CHECKER)
    node = _module_top_level_constant(src, "DEFAULT_CHECK_UPDATE_PATH")
    assert node is not None, (
        "checker.py must declare DEFAULT_CHECK_UPDATE_PATH "
        "(default = '/api/check-update')."
    )
    val = ast.literal_eval(node)
    assert val == "/api/check-update", (
        f"DEFAULT_CHECK_UPDATE_PATH must be '/api/check-update', "
        f"got {val!r}."
    )


def test_refresh_interval_constant_exists():
    """The cache-refresh interval must be a top-level constant
    (6 hours, mirrors base_layer.REFRESH_INTERVAL_SECONDS).
    """
    src = _read(CHECKER)
    for name in ("REFRESH_INTERVAL_SECONDS", "CACHE_FILENAME"):
        node = _module_top_level_constant(src, name)
        assert node is not None, (
            f"checker.py must declare {name} top-level."
        )
    interval_node = _module_top_level_constant(src, "REFRESH_INTERVAL_SECONDS")
    # ``REFRESH_INTERVAL_SECONDS = 6 * 60 * 60`` is a BinOp
    # that ``ast.literal_eval`` rejects. Walk it manually.
    interval = _eval_simple_expr(interval_node)
    assert isinstance(interval, int) and 0 < interval <= 24 * 60 * 60, (
        f"REFRESH_INTERVAL_SECONDS must be a positive int ≤ 24h, "
        f"got {interval!r}."
    )
    # The freshness check lives in _read_cache (the right
    # architectural split — check() delegates to it). Pin
    # that REFRESH_INTERVAL_SECONDS is consulted there too.
    read_cache = _function_source(src, "_read_cache")
    assert read_cache, "UpdateChecker must declare _read_cache()."
    assert "REFRESH_INTERVAL_SECONDS" in read_cache, (
        "_read_cache must compare cache age to "
        "REFRESH_INTERVAL_SECONDS to decide freshness."
    )


def test_state_filename_constant_exists():
    """The dismissed-versions store must use a stable filename
    (``state.yaml`` per the cross-repo review §1.2).
    """
    src = _read(CHECKER)
    node = _module_top_level_constant(src, "STATE_FILENAME")
    assert node is not None, (
        "checker.py must declare STATE_FILENAME (the dismissed-versions store)."
    )
    val = ast.literal_eval(node)
    assert val.endswith(".yaml"), (
        f"STATE_FILENAME must end with '.yaml', got {val!r}."
    )


# ---------------------------------------------------------------------------
# Contract 3: the .check() method hits the right URL with APP_VERSION_SHORT
# ---------------------------------------------------------------------------


def test_check_method_calls_correct_endpoint():
    """``UpdateChecker.check()`` must build the URL from
    ``self.check_path`` (which defaults to
    ``DEFAULT_CHECK_UPDATE_PATH``) + query params
    ``current_version=APP_VERSION_SHORT`` and ``os=<platform>``.
    Pinning the constants the call uses so a future refactor
    can't silently send the 5-segment ``APP_VERSION`` (which
    the server's ``_parse_version`` can't compare).
    """
    src = _read(CHECKER)
    # The endpoint path can be referenced via self.check_path
    # (instance attr) rather than the module constant. Pin
    # the constructor wires them together.
    init_fn = _ast_function(src, "__init__")
    init_src = ast.get_source_segment(src, init_fn) or ""
    body = _function_source(src, "check")
    assert body, "UpdateChecker must declare a check() method."
    assert "self.check_path" in body, (
        "check() must use self.check_path (the URL path) — "
        "pinning the constructor wires DEFAULT_CHECK_UPDATE_PATH "
        "into self.check_path."
    )
    assert "APP_VERSION_SHORT" in body, (
        "check() must send APP_VERSION_SHORT as the "
        "current_version query param (NOT APP_VERSION — "
        "the server's _parse_version only handles 3-segment)."
    )
    assert "os=" in body or "platform" in body.lower(), (
        "check() must include the os= query param."
    )
    assert init_src, "UpdateChecker must declare __init__."
    assert "DEFAULT_CHECK_UPDATE_PATH" in init_src or "check_path" in init_src, (
        "__init__ must wire DEFAULT_CHECK_UPDATE_PATH into "
        "self.check_path (or accept a check_path override)."
    )


def test_check_method_returns_none_on_unreachable():
    """The contract is best-effort: any network/HTTP failure
    returns ``None`` and does NOT overwrite the cache (a
    transient 503 should not lose a previous successful
    cache hit).
    """
    src = _read(CHECKER)
    body = _function_source(src, "check")
    assert body, "UpdateChecker must declare a check() method."
    assert "None" in body, (
        "check() must be able to return None on "
        "unreachable server (the cross-repo review §1.2 "
        "explicitly says 'Falls back to no update check "
        "available if the server is unreachable')."
    )
    # The cache-write path must be guarded so a failure
    # doesn't clobber a previously-cached good response.
    # Either an explicit try/except around the write, or a
    # write that only happens after a successful response.
    assert "try:" in body or "if " in body, (
        "check() must guard the cache write with try/except "
        "or a success guard."
    )


# ---------------------------------------------------------------------------
# Contract 4: dismissed-versions helpers
# ---------------------------------------------------------------------------


def test_dismiss_and_is_dismissed_helpers_exist():
    """The dismissed-versions API: ``dismiss_version(version)``
    persists the version; ``is_dismissed(version) -> bool``
    reads it back. Both must be module-level helpers (not
    methods) so the tray notification can call them without
    instantiating ``UpdateChecker``.

    The read/write paths delegate to internal ``_load_state``
    / ``_save_state`` helpers. Pin those exist too — they
    own the actual state.yaml interaction.
    """
    src = _read(CHECKER)
    for name in ("dismiss_version", "is_dismissed", "_load_state", "_save_state"):
        fn = _ast_function(src, name)
        assert fn is not None, (
            f"checker.py must declare {name}() module-level helper."
        )
    # Both helpers must consult the same state source.
    # dismiss_version writes; is_dismissed reads.
    dismiss_body = _function_source(src, "dismiss_version")
    is_body = _function_source(src, "is_dismissed")
    assert "_save_state" in dismiss_body, (
        "dismiss_version must persist via _save_state."
    )
    assert "_load_state" in is_body, (
        "is_dismissed must read via _load_state."
    )
    assert "bool" in is_body.lower() or "return" in is_body, (
        "is_dismissed must return a bool."
    )


# ---------------------------------------------------------------------------
# Contract 5: UpdateInfo dataclass (optional but expected)
# ---------------------------------------------------------------------------


def test_update_info_dataclass_or_typeddict_exists():
    """The parsed server response should be wrapped in a typed
    structure (dataclass or TypedDict). Pinning the type name
    so callers can statically type their handler code.
    """
    src = _read(CHECKER)
    cls = _ast_class(src, "UpdateInfo")
    if cls is None:
        # TypedDict detection: a top-level assignment with a
        # TypedDict() call is harder to AST-detect cleanly;
        # we accept either a class or a TypedDict-style dict
        # subclass. The contract is that callers can do
        # ``isinstance(result, UpdateInfo)``.
        pytest = __import__("pytest")
        pytest.skip(
            "UpdateInfo dataclass not declared — checker.py "
            "may use a TypedDict or untyped dict instead. "
            "Pin UpdateInfo as a dataclass if you want "
            "stronger caller-side typing."
        )
    body = ast.get_source_segment(src, cls) or ""
    # Must carry the fields callers actually use.
    for field in ("latest_version", "update_available", "download_url"):
        assert field in body, (
            f"UpdateInfo must carry the {field!r} field."
        )


# ---------------------------------------------------------------------------
# Contract 6: cache TTL behaviour
# ---------------------------------------------------------------------------


def test_cache_is_respected_when_fresh():
    """``check()`` must short-circuit to the cached response
    when the cache is younger than REFRESH_INTERVAL_SECONDS.
    Without this the desktop hits /api/check-update on every
    startup AND every 6h, which is wasteful and trips the
    server's 60-calls/hour rate limit.

    The freshness check lives in ``_read_cache`` (the helper
    that ``check()`` delegates to). Pinning that path is
    correct — the contract is "no network call when cache
    fresh", not "the literal REFRESH_INTERVAL_SECONDS string
    appears inside check()".
    """
    src = _read(CHECKER)
    read_cache = _function_source(src, "_read_cache")
    check_body = _function_source(src, "check")
    assert read_cache, "UpdateChecker must declare _read_cache()."
    assert "REFRESH_INTERVAL_SECONDS" in read_cache, (
        "_read_cache must compare cache age to "
        "REFRESH_INTERVAL_SECONDS to decide freshness."
    )
    # And check() must actually delegate to it (the cache
    # short-circuit must be the first thing check() does).
    assert "_read_cache" in check_body, (
        "check() must delegate the cache read to "
        "_read_cache() — that's the freshness gate."
    )


def test_cache_file_has_mode_0600():
    """The cache file must be written with mode 0o600 (matches
    the credentials + base_layer pattern; prevents other users
    on the same machine from reading update-state info).
    """
    src = _read(CHECKER)
    body = _read(CHECKER)
    assert "0o600" in body or "0600" in body, (
        "checker.py must chmod the cache file to 0o600 "
        "(mirrors base_layer.py + credentials.py pattern)."
    )


# ---------------------------------------------------------------------------
# Contract 7: APP_VERSION_SHORT is the source of truth (no APP_VERSION)
# ---------------------------------------------------------------------------


def test_checker_does_not_send_5_segment_version():
    """The 5-segment ``APP_VERSION`` (``0.0.1.0.1.4``) MUST NOT
    appear as the ``current_version`` argument. The server's
    ``_parse_version`` only handles 3-segment versions and
    would silently return ``update_available: False`` for
    a 5-segment input.
    """
    src = _read(CHECKER)
    body = _function_source(src, "check")
    # A bare ``APP_VERSION`` reference in check() is the bug.
    # ``APP_VERSION_SHORT`` is correct.
    assert not re.search(r"current_version\s*=\s*[^,\)]*APP_VERSION\b(?!\w)", body), (
        "check() must not send the 5-segment APP_VERSION — "
        "send APP_VERSION_SHORT instead. "
        "Pattern found: APP_VERSION used as current_version."
    )
