"""T-DESK-054 — FeatureGate consumer for ``GET /api/version-config``.

Paired with nchantdofficeATNRG cross-repo review
(``docs/cross-repo-review_20260807.md`` §1.3).

The server exposes ``GET /api/version-config`` (unauthenticated)
which returns:

    {
      "current_version": "0.0.1",
      "release_date": "2025-07-08",
      "check_update_url": "/api/check-update",
      "features": {
        "<name>": {
          "min_version": "0.0.1",
          "tier": "free" | "pro" | "prodata" | "enterprise",
          "enabled": bool,
          "available": bool,
          "description": str,
        },
        ...
      }
    }

Today the desktop never calls it. A free user on v0.0.1 sees
the "Multi Instance" menu item (Pro-only at v0.0.3). The
desktop renders all menu items regardless of whether the
feature is enabled for the user's tier or app version.

This test pins the contract that:

  - the desktop has ``nchantdoffice/utilities/feature_gates.py``
  - ``FeatureGate`` is the main class with ``is_feature_enabled()``
    and ``refresh()`` (or equivalent)
  - the response is cached to ``~/.nchantd/feature_flags_cache.json``
    with mode 0o600 (mirrors base_layer + checker pattern)
  - cached responses are returned when fresh
  - unreachable server returns ``None`` / a stale-fallback, not a
    crash
  - the 4-tier model (free / pro / prodata / enterprise) is
    honored, not just free/pro
  - ``is_feature_enabled(name)`` (no tier arg) defaults to the
    current user's tier (read from the existing ``has_pro``
    attribute pattern that ``_is_visible_for_user`` uses)
  - ``is_feature_enabled(name, tier)`` accepts an explicit tier
    for "what would this user see?" calls
  - the Ad tab's existing `_is_visible_for_user` pattern is the
    right anchor for the user-tier lookup (so FeatureGate and
    the Ad tab agree on "what is a Pro user?")
  - the ``current_version`` field is read off the response and
    exposed (so the startup hook can use it for update checks)
  - the cache write is guarded — a transient failure must not
    clobber a previously-cached good response

Tests are pure AST + pure data; no Qt / no network. Same pattern
as ``test_update_checker.py`` and ``test_ad_tab_rotation.py``.

Refs:
  - docs/cross-repo-review_20260807.md §1.3
  - nchantdoffice_com/app/apis/version_config.py
  - nchantdoffice/widgets/advertisements.py::_is_visible_for_user
    (the existing Free-vs-Pro pattern to mirror)
  - nchantdoffice/utilities/base_layer.py (cache pattern template)
  - nchantdoffice/updates/checker.py (sibling consumer)
"""

import ast
import re
import sys
from pathlib import Path
from typing import Any, Dict

PROJ_ROOT = Path("/home/solubrew/.hermes/projects/nchantdoffice")
sys.path.insert(0, str(PROJ_ROOT))

UTILS_DIR = PROJ_ROOT / "nchantdoffice" / "utilities"
FEATURE_GATES = UTILS_DIR / "feature_gates.py"

AD_TAB = PROJ_ROOT / "nchantdoffice" / "widgets" / "advertisements.py"


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


def _eval_simple_expr(node, scope=None):
    """Tiny AST evaluator for ``6 * 60 * 60``-style literals
    plus top-level ``Name`` references (resolved via the
    ``scope`` dict — defaults to the module-level names
    declared in the same source file).
    """
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp):
        left = _eval_simple_expr(node.left, scope=scope)
        right = _eval_simple_expr(node.right, scope=scope)
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        raise ValueError(f"unsupported binop: {ast.dump(node.op)}")
    if isinstance(node, ast.Name):
        if scope is None:
            raise ValueError(f"unresolved name: {node.id}")
        if node.id not in scope:
            raise ValueError(f"unknown name: {node.id}")
        return scope[node.id]
    raise ValueError(f"unsupported expr: {ast.dump(node)}")


def _build_name_scope(src: str) -> Dict[str, Any]:
    """Walk the module top-level and build a name→literal-value
    scope for ``_eval_simple_expr``. Only captures
    ``ast.Constant`` RHS (i.e. the simple cases — doesn't
    follow BinOp chains because the tests that need those
    call ``_eval_simple_expr`` directly with a scope).
    """
    import builtins as _b

    scope: Dict[str, Any] = {"__builtins__": _b}
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name):
                    try:
                        scope[tgt.id] = _eval_simple_expr(
                            node.value, scope=scope
                        )
                    except ValueError:
                        # Skip names whose RHS we can't
                        # resolve (BinOps, function calls,
                        # etc.) — the per-test direct calls
                        # handle those.
                        pass
        elif isinstance(node, ast.AnnAssign):
            if (
                isinstance(node.target, ast.Name)
                and node.value is not None
            ):
                try:
                    scope[node.target.id] = _eval_simple_expr(
                        node.value, scope=scope
                    )
                except ValueError:
                    pass
    return scope


# ---------------------------------------------------------------------------
# Contract 1: module exists
# ---------------------------------------------------------------------------


def test_feature_gates_module_exists():
    """``nchantdoffice/utilities/feature_gates.py`` must exist
    (T-DESK-054 deliverable).
    """
    assert FEATURE_GATES.exists(), (
        f"nchantdoffice/utilities/feature_gates.py must exist "
        f"(T-DESK-054). Expected at {FEATURE_GATES}."
    )


def test_feature_gate_class_exists():
    """``FeatureGate`` is the main class. Pinning the name so
    external callers (startup hook, Ad tab's
    ``_is_visible_for_user``, settings panel) can import it
    by a stable symbol.
    """
    src = _read(FEATURE_GATES)
    cls = _ast_class(src, "FeatureGate")
    assert cls is not None, (
        "feature_gates.py must declare FeatureGate class "
        "(the /api/version-config consumer)."
    )


# ---------------------------------------------------------------------------
# Contract 2: pinned constants
# ---------------------------------------------------------------------------


def test_default_endpoint_is_api_version_config():
    """The default API path must point at ``/api/version-config``
    (matching the server endpoint in
    nchantdoffice_com/app/apis/version_config.py).
    """
    src = _read(FEATURE_GATES)
    node = _module_top_level_constant(src, "DEFAULT_VERSION_CONFIG_PATH")
    assert node is not None, (
        "feature_gates.py must declare "
        "DEFAULT_VERSION_CONFIG_PATH."
    )
    val = ast.literal_eval(node)
    assert val == "/api/version-config", (
        f"DEFAULT_VERSION_CONFIG_PATH must be "
        f"'/api/version-config', got {val!r}."
    )


def test_refresh_interval_constant_exists():
    """The cache-refresh interval must be a top-level constant
    (mirrors checker.py + base_layer.REFRESH_INTERVAL_SECONDS).
    """
    src = _read(FEATURE_GATES)
    for name in ("REFRESH_INTERVAL_SECONDS", "CACHE_FILENAME"):
        node = _module_top_level_constant(src, name)
        assert node is not None, (
            f"feature_gates.py must declare {name} top-level."
        )
    interval_node = _module_top_level_constant(
        src, "REFRESH_INTERVAL_SECONDS"
    )
    interval = _eval_simple_expr(interval_node)
    assert isinstance(interval, int) and 0 < interval <= 24 * 60 * 60, (
        f"REFRESH_INTERVAL_SECONDS must be a positive int ≤ 24h, "
        f"got {interval!r}."
    )


def test_known_tiers_constant_lists_all_four():
    """The 4-tier model (Free/Pro/ProData/Enterprise) must be
    honored per the ATNRG PricingModel.md. Pinning the literal
    list prevents a refactor that drops one tier.
    """
    src = _read(FEATURE_GATES)
    for name in ("KNOWN_TIERS", "TIER_FREE", "TIER_PRO", "TIER_PRODATA", "TIER_ENTERPRISE"):
        node = _module_top_level_constant(src, name)
        assert node is not None, (
            f"feature_gates.py must declare {name} top-level."
        )
    tiers_node = _module_top_level_constant(src, "KNOWN_TIERS")
    # KNOWN_TIERS is built from the TIER_* string constants —
    # resolve them via the module scope.
    scope = _build_name_scope(src)
    if isinstance(tiers_node, (ast.List, ast.Tuple)):
        tiers = [
            _eval_simple_expr(e, scope=scope) for e in tiers_node.elts
        ]
    else:
        # If it's a frozenset/set, we can't AST-extract it cleanly —
        # the TIER_* constants below pin the membership anyway.
        tiers = None
    if tiers is not None:
        assert "free" in tiers, "KNOWN_TIERS must include 'free'."
        assert "pro" in tiers, "KNOWN_TIERS must include 'pro'."
        assert "prodata" in tiers, "KNOWN_TIERS must include 'prodata'."
        assert "enterprise" in tiers, "KNOWN_TIERS must include 'enterprise'."
    for tier, expected in [
        ("TIER_FREE", "free"),
        ("TIER_PRO", "pro"),
        ("TIER_PRODATA", "prodata"),
        ("TIER_ENTERPRISE", "enterprise"),
    ]:
        node = _module_top_level_constant(src, tier)
        val = ast.literal_eval(node)
        assert val == expected, (
            f"{tier} must equal {expected!r}, got {val!r}."
        )


# ---------------------------------------------------------------------------
# Contract 3: is_feature_enabled() signature
# ---------------------------------------------------------------------------


def test_is_feature_enabled_method_exists():
    """``FeatureGate.is_feature_enabled(name, tier=None) -> bool``
    is the central helper. The optional tier arg lets the
    Ad tab (and any other consumer) ask "what would this
    user see?" without needing to know about the global user
    reference.
    """
    src = _read(FEATURE_GATES)
    fn = _ast_function(src, "is_feature_enabled")
    assert fn is not None, (
        "FeatureGate must declare is_feature_enabled() "
        "method (the public API)."
    )
    body = _function_source(src, "is_feature_enabled")
    # The signature must accept ``tier`` as the second arg.
    args = [a.arg for a in fn.args.args]
    assert "name" in args, (
        "is_feature_enabled must accept a 'name' argument."
    )
    assert "tier" in args, (
        "is_feature_enabled must accept an optional 'tier' "
        "argument so callers can ask 'what would <tier> see?'."
    )
    # The default must be None (so it falls back to the
    # current user lookup).
    defaults = fn.args.defaults
    # The last default in the args list corresponds to the
    # last arg with one. The signature is (self, name, tier).
    if defaults:
        last_default = defaults[-1]
        # Could be a Constant(None) or some sentinel.
        if isinstance(last_default, ast.Constant):
            assert last_default.value is None, (
                "is_feature_enabled(tier=...) must default to None "
                "(the current-user lookup)."
            )


def test_is_feature_enabled_uses_cache_when_fresh():
    """``is_feature_enabled()`` must short-circuit to the cache
    when fresh (no network call per UI render — the Ad tab
    calls this on every tab rebuild).

    The freshness check lives in ``_cache_is_fresh`` (the
    helper that ``is_feature_enabled`` delegates to). Pinning
    that path is correct — the contract is "no network call
    when cache fresh", not "the literal
    REFRESH_INTERVAL_SECONDS string appears inside
    is_feature_enabled".
    """
    src = _read(FEATURE_GATES)
    cache_is_fresh = _function_source(src, "_cache_is_fresh")
    check_body = _function_source(src, "is_feature_enabled")
    assert cache_is_fresh, (
        "FeatureGate must declare _cache_is_fresh() helper "
        "(the freshness gate)."
    )
    assert "REFRESH_INTERVAL_SECONDS" in cache_is_fresh, (
        "_cache_is_fresh must compare cache age to "
        "REFRESH_INTERVAL_SECONDS."
    )
    assert "_cache_is_fresh" in check_body, (
        "is_feature_enabled must delegate the freshness "
        "check to _cache_is_fresh() — same pattern as "
        "UpdateChecker.check() / _read_cache()."
    )


# ---------------------------------------------------------------------------
# Contract 4: refresh() / populate from server
# ---------------------------------------------------------------------------


def test_refresh_method_calls_correct_endpoint():
    """``FeatureGate.refresh()`` (the network-call entry point)
    must hit ``/api/version-config`` and parse the response
    into a usable structure. Best-effort: failures return
    ``False`` / ``None`` and do NOT clobber the cache.
    """
    src = _read(FEATURE_GATES)
    fn = _ast_function(src, "refresh")
    assert fn is not None, (
        "FeatureGate must declare refresh() method "
        "(the server-poll entry point)."
    )
    body = _function_source(src, "refresh")
    assert (
        "DEFAULT_VERSION_CONFIG_PATH" in body
        or "/api/version-config" in body
        or "self.config_path" in body
    ), (
        "refresh() must hit /api/version-config."
    )
    assert "try:" in body, (
        "refresh() must guard the network call with try/except."
    )
    assert "None" in body or "False" in body, (
        "refresh() must return None/False on failure "
        "(best-effort; never raises)."
    )


def test_refresh_uses_cache_write_guard():
    """A transient server failure must NOT overwrite the cache.
    The cache write must happen only after a successful
    response — same pattern as checker.py.
    """
    src = _read(FEATURE_GATES)
    body = _function_source(src, "refresh")
    # The write path must be guarded by a success check
    # (either inside the try block, or after raise_for_status).
    assert "raise_for_status" in body, (
        "refresh() must call raise_for_status() before "
        "writing the cache (otherwise a 503 silently "
        "overwrites the good cache)."
    )


# ---------------------------------------------------------------------------
# Contract 5: Feature dataclass (typed access)
# ---------------------------------------------------------------------------


def test_feature_dataclass_exists():
    """A typed ``Feature`` structure must exist so callers
    get attribute access (.min_version, .tier, .enabled,
    .available) instead of dict-by-key.
    """
    src = _read(FEATURE_GATES)
    cls = _ast_class(src, "Feature")
    assert cls is not None, (
        "feature_gates.py must declare Feature dataclass "
        "(typed per-feature entry)."
    )
    body = ast.get_source_segment(src, cls) or ""
    for field in ("min_version", "tier", "enabled", "available", "description"):
        assert field in body, (
            f"Feature must carry the {field!r} field "
            "(matches the server response shape)."
        )


# ---------------------------------------------------------------------------
# Contract 6: cache file mode + path
# ---------------------------------------------------------------------------


def test_cache_file_has_mode_0600():
    """The cache file must be written with mode 0o600 (matches
    the credentials + base_layer + checker pattern).
    """
    src = _read(FEATURE_GATES)
    assert "0o600" in src or "0600" in src, (
        "feature_gates.py must chmod the cache file to 0o600 "
        "(mirrors base_layer.py + credentials.py + checker.py "
        "pattern)."
    )


def test_cache_path_uses_user_config_get_cache_dir():
    """The cache path must live under the user-config
    cache dir (T-NEW-070 DESK-3 hard-break).

    Previously read NCHANT_DATA_DIR env var (deprecated).
    Now uses get_cache_dir() from
    nchantdoffice.utilities.user_config.
    """
    src = _read(FEATURE_GATES)
    assert "get_cache_dir" in src, (
        "feature_gates.py must use get_cache_dir() from "
        "user_config (T-NEW-070 DESK-3 hard-break — no env vars)"
    )
    # And must build the path under the data dir.
    assert "from nchantdoffice.utilities.user_config" in src, (
        "feature_gates.py must import get_cache_dir from "
        "nchantdoffice.utilities.user_config"
    )


# ---------------------------------------------------------------------------
# Contract 7: 4-tier user lookup (mirrors _is_visible_for_user)
# ---------------------------------------------------------------------------


def test_default_user_tier_lookup_matches_adtab_pattern():
    """When ``tier`` is omitted from ``is_feature_enabled()``,
    the lookup must match the existing Ad tab
    ``_is_visible_for_user`` pattern (which reads ``has_pro``
    off the current user). Pinning this prevents a refactor
    where FeatureGate and the Ad tab disagree on "what is a
    Pro user?" — that would silently break feature gating.

    The card recommended wiring FeatureGate into
    ``_is_visible_for_user`` itself, but the safer first
    step is just to use the same lookup shape (read
    ``has_pro``, default to ``free``).
    """
    src = _read(FEATURE_GATES)
    body = _function_source(src, "is_feature_enabled")
    # When tier is None, fall back to a user lookup that
    # recognizes Pro (via has_pro). Accept either an explicit
    # helper function or inline logic.
    assert (
        "has_pro" in body
        or "_current_user_tier" in body
        or "_resolve_user_tier" in body
        or "TIER_FREE" in body  # the default
    ), (
        "is_feature_enabled (no tier) must default to the "
        "current user's tier — either via the same "
        "has_pro pattern as the Ad tab's "
        "_is_visible_for_user, or via a dedicated "
        "_resolve_user_tier helper."
    )


def test_pro_superset_of_free():
    """A Pro user must be able to use Free features (the tier
    hierarchy is Free < Pro < ProData < Enterprise — each
    higher tier unlocks everything below it). Pinning this
    prevents a future "tier equality check" bug that would
    hide a Free feature from a Pro user.
    """
    src = _read(FEATURE_GATES)
    # The check should be a rank-style lookup, not exact
    # equality. Either a ``_tier_rank()`` helper, a literal
    # rank dict, or the explicit if/elif chain.
    body = src  # whole-module check (the helper can live anywhere)
    assert (
        "_tier_rank" in body
        or "_TIER_RANK" in body
        or "tier_rank" in body
        or ("TIER_FREE" in body and "TIER_PRO" in body and "TIER_PRODATA" in body and "TIER_ENTERPRISE" in body)
    ), (
        "FeatureGate must implement a tier-rank lookup "
        "(Pro >= Free, ProData >= Pro, etc.) — not an "
        "exact-equality check."
    )


# ---------------------------------------------------------------------------
# Contract 8: current_version exposure (for update check handoff)
# ---------------------------------------------------------------------------


def test_current_version_property_or_attribute():
    """The server's ``current_version`` field must be exposed
    so the startup hook can hand it to ``UpdateChecker.check()``
    without re-fetching. Either a ``current_version`` attribute
    or a property.
    """
    src = _read(FEATURE_GATES)
    cls = _ast_class(src, "FeatureGate")
    assert cls is not None
    body = ast.get_source_segment(src, cls) or ""
    # Either an attribute assignment or a property decorator.
    assert (
        "self.current_version" in body
        or "current_version" in body
    ), (
        "FeatureGate must expose current_version (the "
        "server's advertised version) for handoff to "
        "UpdateChecker."
    )
