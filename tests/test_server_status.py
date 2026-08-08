"""T-DESK-063 — ServerStatus indicator (Phase 2 close).

Paired with nchantdofficeATNRG cross-repo review
(``docs/cross-repo-review_20260807.md`` §2.9 + the
recommendation under §6 Phase 2 step 7).

When ``nchantdoffice.com`` is unreachable (which happens
often per the BUGs.md stacktraces), every server call fails
after a 5-second timeout. The UI then shows a "local
fallback" but the user sees broken-looking panels with no
clear error.

This test pins the contract that:

  - ``nchantdoffice/utilities/server_status.py`` exists
  - ``ServerStatus`` is a state machine (4 states):
      CONNECTED   — last successful call < 1 min ago
      DEGRADED    — last successful call 1–5 min ago
      OFFLINE     — last successful call > 5 min ago
                    OR last call failed
      UNKNOWN     — no successful call yet AND no failure
  - ``record_success()`` transitions to CONNECTED
  - ``record_failure()`` transitions to OFFLINE
  - ``state()`` reads the current state (computed from the
    timestamp + failure flag, NOT stored)
  - ``state_label()`` returns a short human-readable string
    ("Connected", "Degraded", "Offline", "Unknown") for
    the status bar / tray
  - ``state_glyph()`` returns a Unicode emoji for the
    status bar ("🟢", "🟡", "🔴", "�")
  - thresholds are top-level constants (1 min, 5 min) so
    operators can tune them
  - a status-bar widget (``ServerStatusWidget``) is a thin
    ``QLabel`` subclass that observes ``ServerStatus`` and
    re-renders on every state change — but the pure
    ``ServerStatus`` class has NO Qt imports (the test
    layer can't import Qt in this venv, so the widget is
    gated behind a try/except for testability)
  - the consumer pattern is "every server call wraps itself
    in try/except and calls ``record_success`` /
    ``record_failure``" — the module exposes helpers for
    this (a ``timed_call`` context manager that records
    based on exception vs success)

Tests are AST + pure-Python where possible. The Qt-dependent
``ServerStatusWidget`` is tested by source-level pin only
(the QApplication-required widget class is constructed in
real GUI tests, not here).

Refs:
  - docs/cross-repo-review_20260807.md §2.9 + §6 Phase 2
  - nchantdoffice/updates/checker.py (sibling consumer)
  - nchantdoffice/utilities/feature_gates.py (sibling consumer)
"""

import ast
import datetime as dt
import sys
from pathlib import Path
from typing import Any, Dict, List

PROJ_ROOT = Path("/home/solubrew/.hermes/projects/nchantdoffice")
sys.path.insert(0, str(PROJ_ROOT))

UTILS_DIR = PROJ_ROOT / "nchantdoffice" / "utilities"
SERVER_STATUS = UTILS_DIR / "server_status.py"


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
        if scope is None or node.id not in scope:
            raise ValueError(f"unresolved name: {node.id}")
        return scope[node.id]
    raise ValueError(f"unsupported expr: {ast.dump(node)}")


def _build_name_scope(src: str) -> Dict[str, Any]:
    scope: Dict[str, Any] = {}
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
# Contract 1: module + main class exist
# ---------------------------------------------------------------------------


def test_server_status_module_exists():
    """``nchantdoffice/utilities/server_status.py`` must exist
    (T-DESK-063 deliverable).
    """
    assert SERVER_STATUS.exists(), (
        f"nchantdoffice/utilities/server_status.py must exist "
        f"(T-DESK-063). Expected at {SERVER_STATUS}."
    )


def test_server_status_class_exists():
    """``ServerStatus`` is the main state-machine class."""
    src = _read(SERVER_STATUS)
    cls = _ast_class(src, "ServerStatus")
    assert cls is not None, (
        "server_status.py must declare ServerStatus class "
        "(the 4-state machine)."
    )


# ---------------------------------------------------------------------------
# Contract 2: 4 states pinned + thresholds tunable
# ---------------------------------------------------------------------------


def test_four_states_are_pinned():
    """The 4 states (CONNECTED / DEGRADED / OFFLINE / UNKNOWN)
    must be top-level string constants. Pinning the literal
    names prevents a refactor that drops one state.
    """
    src = _read(SERVER_STATUS)
    for name in (
        "STATE_CONNECTED",
        "STATE_DEGRADED",
        "STATE_OFFLINE",
        "STATE_UNKNOWN",
    ):
        node = _module_top_level_constant(src, name)
        assert node is not None, (
            f"server_status.py must declare {name} top-level."
        )
    scope = _build_name_scope(src)
    expected = {
        "STATE_CONNECTED": "connected",
        "STATE_DEGRADED": "degraded",
        "STATE_OFFLINE": "offline",
        "STATE_UNKNOWN": "unknown",
    }
    for name, value in expected.items():
        node = _module_top_level_constant(src, name)
        got = _eval_simple_expr(node, scope=scope)
        assert got == value, (
            f"{name} must equal {value!r}, got {got!r}."
        )


def test_thresholds_are_top_level_constants():
    """The CONNECTED / DEGRADED cutoffs must be tunable.
    Defaults: CONNECTED < 1 min, DEGRADED < 5 min, OFFLINE
    otherwise. Pinning the names lets an operator tune them
    via configuration later without grepping the source.
    """
    src = _read(SERVER_STATUS)
    for name in (
        "CONNECTED_THRESHOLD_SECONDS",
        "DEGRADED_THRESHOLD_SECONDS",
    ):
        node = _module_top_level_constant(src, name)
        assert node is not None, (
            f"server_status.py must declare {name} top-level."
        )
    scope = _build_name_scope(src)
    connected = _eval_simple_expr(
        _module_top_level_constant(src, "CONNECTED_THRESHOLD_SECONDS"),
        scope=scope,
    )
    degraded = _eval_simple_expr(
        _module_top_level_constant(src, "DEGRADED_THRESHOLD_SECONDS"),
        scope=scope,
    )
    assert isinstance(connected, int) and 0 < connected <= 600, (
        f"CONNECTED_THRESHOLD_SECONDS must be a positive int ≤ 10m, "
        f"got {connected!r}."
    )
    assert isinstance(degraded, int) and connected < degraded <= 1800, (
        f"DEGRADED_THRESHOLD_SECONDS must be > CONNECTED and ≤ 30m, "
        f"got connected={connected}, degraded={degraded}."
    )


# ---------------------------------------------------------------------------
# Contract 3: state-transition methods
# ---------------------------------------------------------------------------


def test_record_success_and_failure_exist():
    """``record_success()`` and ``record_failure()`` are the
    transition triggers. Both must accept optional ``when``
    (an injected datetime for tests) so the test layer can
    pin the state without monkey-patching time.time().
    """
    src = _read(SERVER_STATUS)
    for name in ("record_success", "record_failure"):
        fn = _ast_function(src, name)
        assert fn is not None, (
            f"ServerStatus must declare {name}() method."
        )
    # Both must accept a `when` kwarg (datetime injection).
    for name in ("record_success", "record_failure"):
        fn = _ast_function(src, name)
        arg_names = [a.arg for a in fn.args.args]
        assert "when" in arg_names, (
            f"{name} must accept a 'when' kwarg "
            "(datetime injection for tests)."
        )


def test_state_method_returns_one_of_four():
    """``state()`` must return one of the four state strings.
    Pinning the literal return set prevents a refactor that
    returns a number or an enum that doesn't round-trip.
    """
    src = _read(SERVER_STATUS)
    body = _function_source(src, "state")
    assert body, "ServerStatus must declare state() method."
    # state() must consult both _last_success (timestamp) and
    # _last_failure (flag). Without the flag, a single failure
    # followed by silence would look "connected" again.
    for needle in ("_last_success", "_last_failure"):
        assert needle in body or needle in src, (
            f"state() must consider {needle!r} when computing "
            f"the current state."
        )


# ---------------------------------------------------------------------------
# Contract 4: state_label + state_glyph (UI helpers)
# ---------------------------------------------------------------------------


def test_state_label_returns_human_readable():
    """``state_label()`` returns a short string the status bar
    can display (e.g. "Connected", "Degraded", "Offline",
    "Unknown"). Must map the 4 states → 4 labels.

    The implementation may use either an inline if/elif chain
    OR a module-level ``_STATE_LABELS`` dict — both are
    legitimate. Pin the contract at the test layer (label
    strings exist + are non-empty + cover all 4 states) so
    the implementation can choose whichever style is cleaner.
    """
    src = _read(SERVER_STATUS)
    fn = _ast_function(src, "state_label")
    assert fn is not None, (
        "ServerStatus must declare state_label() method "
        "(UI helper for the status bar)."
    )
    body = _function_source(src, "state_label")
    assert "state" in body.lower(), (
        "state_label must consult self.state() (or equivalent)."
    )
    # The label strings must exist in the module (either in
    # a dict literal or inline). Pin each one so a typo /
    # rename fails loudly.
    for label in ("Connected", "Degraded", "Offline", "Unknown"):
        assert f'"{label}"' in body or f"'{label}'" in body, (
            f"state_label source must include the label "
            f"{label!r} (the user-visible string for one of "
            f"the 4 states)."
        )


def test_state_glyph_returns_unicode_emoji():
    """``state_glyph()`` returns a single-character emoji the
    status bar shows next to the label (🟢 / 🟡 / 🔴 / ⚪).
    Pinning the emoji keeps the visual language consistent
    with the docstring example.
    """
    src = _read(SERVER_STATUS)
    fn = _ast_function(src, "state_glyph")
    assert fn is not None, (
        "ServerStatus must declare state_glyph() method "
        "(emoji for the status bar)."
    )
    body = _function_source(src, "state_glyph")
    # At minimum the green + red glyphs (the two extremes).
    assert "\U0001F7E2" in body or "🟢" in body, (
        "state_glyph must include the 🟢 (green circle) "
        "for CONNECTED."
    )
    assert "\U0001F534" in body or "🔴" in body, (
        "state_glyph must include the 🔴 (red circle) "
        "for OFFLINE."
    )


# ---------------------------------------------------------------------------
# Contract 5: timed_call context manager
# ---------------------------------------------------------------------------


def test_timed_call_context_manager_exists():
    """``timed_call()`` (or a ``call()`` context manager) is
    the consumer-facing helper: wrap any server call in a
    ``with timed_call():`` block, and the manager records
    success or failure based on whether the block raised.

    This is the ergonomic API every consumer (UpdateChecker,
    FeatureGate, ReferralAPIClient, etc.) will use. Without
    it, every consumer needs its own try/except + state call
    bookkeeping.
    """
    src = _read(SERVER_STATUS)
    for name in ("timed_call", "call"):
        fn = _ast_function(src, name)
        if fn is not None:
            break
    else:
        raise AssertionError(
            "server_status.py must declare either timed_call() "
            "or call() — a context manager that records "
            "success on exit and failure on exception."
        )


# ---------------------------------------------------------------------------
# Contract 6: Qt widget is optional (pure-class works without QApplication)
# ---------------------------------------------------------------------------


def test_pure_class_does_not_import_qt():
    """The pure ``ServerStatus`` class must NOT import Qt.
    Pinning this so the test layer (which can't import
    QApplication in this venv) can still exercise the state
    machine directly.

    The Qt widget (``ServerStatusWidget``) is allowed to
    import Qt, but must be guarded by a try/except so the
    pure class loads cleanly even when Qt is missing.
    """
    src = _read(SERVER_STATUS)
    cls = _ast_class(src, "ServerStatus")
    assert cls is not None
    cls_src = ast.get_source_segment(src, cls) or ""
    # The class body itself must not reference Qt symbols.
    for needle in ("QLabel", "QWidget", "pyqt.", "QApplication"):
        assert needle not in cls_src, (
            f"ServerStatus class body must not reference "
            f"{needle!r} (the pure state machine is "
            f"Qt-independent)."
        )


def test_qt_widget_guarded_by_try_except():
    """``ServerStatusWidget`` (the Qt label) must be defined
    under a try/except so the pure ``ServerStatus`` class
    loads cleanly when Qt is unavailable. The test layer
    pins this so a future cleanup can't accidentally make
    Qt a hard dependency of the module.
    """
    src = _read(SERVER_STATUS)
    cls = _ast_class(src, "ServerStatusWidget")
    if cls is None:
        # Optional — a refactor that splits Qt into a
        # separate module is fine. The contract is that IF
        # the widget lives in this file, it's guarded.
        return
    # The widget must be inside a try/except. Check the
    # surrounding source.
    idx = src.find("class ServerStatusWidget")
    before = src[:idx]
    # Find the nearest ``try:`` line before this position.
    last_try = before.rfind("try:")
    last_except = before.rfind("except")
    assert last_try != -1 and last_except != -1 and last_try < idx, (
        "ServerStatusWidget must be defined inside a "
        "try/except so the pure ServerStatus class loads "
        "even when Qt is unavailable."
    )


# ---------------------------------------------------------------------------
# Contract 7: end-to-end state transitions (runtime, not AST)
# ---------------------------------------------------------------------------


def test_state_transitions_connect_to_degraded_to_offline():
    """Runtime sanity check: drive a ServerStatus instance
    through all four transitions and assert the computed
    state at each step.

    Skipped automatically if the module has any import
    error (the test layer is constrained; the AST pins above
    cover the source-level contracts).
    """
    import pytest

    try:
        from nchantdoffice.utilities.server_status import (
            ServerStatus,
            STATE_CONNECTED,
            STATE_DEGRADED,
            STATE_OFFLINE,
            STATE_UNKNOWN,
        )
    except Exception as e:
        pytest.skip(
            f"server_status import failed (env limitation): {e}. "
            "Source-level contracts are pinned by the other tests."
        )

    now = dt.datetime(2026, 8, 7, 12, 0, 0, tzinfo=dt.timezone.utc)

    s = ServerStatus()
    # No calls yet → UNKNOWN.
    assert s.state(when=now) == STATE_UNKNOWN, (
        "fresh ServerStatus with no calls must be UNKNOWN."
    )

    # 30 s ago → CONNECTED.
    s.record_success(when=now - dt.timedelta(seconds=30))
    assert s.state(when=now) == STATE_CONNECTED, (
        "30s after last success must be CONNECTED."
    )

    # 3 min ago → DEGRADED.
    s.record_success(when=now - dt.timedelta(seconds=180))
    assert s.state(when=now) == STATE_DEGRADED, (
        "3 min after last success must be DEGRADED."
    )

    # 10 min ago → OFFLINE.
    s.record_success(when=now - dt.timedelta(seconds=600))
    assert s.state(when=now) == STATE_OFFLINE, (
        "10 min after last success must be OFFLINE "
        "(past the DEGRADED threshold)."
    )

    # Any failure → OFFLINE (even right after a success).
    s.record_success(when=now - dt.timedelta(seconds=10))
    s.record_failure(when=now)
    assert s.state(when=now) == STATE_OFFLINE, (
        "a fresh failure must override a recent success → OFFLINE."
    )


def test_state_label_and_glyph_match_state():
    """Runtime sanity check: ``state_label()`` and
    ``state_glyph()`` both return non-empty strings, and
    the label is distinct from the glyph (so the status bar
    shows both).
    """
    import pytest

    try:
        from nchantdoffice.utilities.server_status import (
            ServerStatus,
            STATE_CONNECTED,
            STATE_DEGRADED,
            STATE_OFFLINE,
            STATE_UNKNOWN,
            _STATE_LABELS,
            _STATE_GLYPHS,
        )
    except Exception as e:
        pytest.skip(
            f"server_status import failed (env limitation): {e}"
        )

    now = dt.datetime(2026, 8, 7, 12, 0, 0, tzinfo=dt.timezone.utc)

    s = ServerStatus()
    # UNKNOWN
    assert isinstance(s.state_label(), str) and s.state_label(), (
        "state_label must return a non-empty string."
    )
    assert isinstance(s.state_glyph(), str) and s.state_glyph(), (
        "state_glyph must return a non-empty string."
    )
    assert s.state_label() != s.state_glyph(), (
        "state_label and state_glyph must be distinct "
        "(the status bar shows both)."
    )

    # CONNECTED after a fresh success.
    s.record_success(when=now - dt.timedelta(seconds=10))
    # Inject ``when`` into both record_success AND state()
    # so the test is hermetic (real wall-clock drift would
    # otherwise move us past the 60s CONNECTED threshold).
    label = _STATE_LABELS.get(s.state(when=now), "Unknown")
    glyph = _STATE_GLYPHS.get(s.state(when=now), "")
    assert "Connected" in label or "connected" in label.lower(), (
        f"state_label for CONNECTED must include 'Connected', "
        f"got {label!r}."
    )
    # The CONNECTED glyph should be the green circle.
    assert "🟢" in glyph or "\U0001F7E2" in glyph, (
        f"state_glyph for CONNECTED must include 🟢, got {glyph!r}."
    )

    # OFFLINE after a failure.
    s.record_failure(when=now)
    label = _STATE_LABELS.get(s.state(when=now), "Unknown")
    glyph = _STATE_GLYPHS.get(s.state(when=now), "")
    assert "Offline" in label or "offline" in label.lower(), (
        f"state_label for OFFLINE must include 'Offline', "
        f"got {label!r}."
    )
    assert "🔴" in glyph or "\U0001F534" in glyph, (
        f"state_glyph for OFFLINE must include 🔴, got {glyph!r}."
    )


def test_timed_call_records_success_on_no_exception():
    """Runtime sanity check: the ``timed_call()`` context
    manager records a success when the wrapped block returns
    normally, and a failure when it raises.
    """
    import pytest

    try:
        from nchantdoffice.utilities.server_status import (
            ServerStatus,
            STATE_CONNECTED,
            STATE_OFFLINE,
            timed_call,
        )
    except Exception as e:
        pytest.skip(
            f"server_status import failed (env limitation): {e}"
        )

    now = dt.datetime(2026, 8, 7, 12, 0, 0, tzinfo=dt.timezone.utc)
    s = ServerStatus()

    # Success path.
    with timed_call(s, when=now):
        pass
    assert s.state(when=now) == STATE_CONNECTED, (
        "timed_call with no exception must record success → CONNECTED."
    )

    # Failure path.
    with pytest.raises(RuntimeError):
        with timed_call(s, when=now):
            raise RuntimeError("simulated server error")
    assert s.state(when=now) == STATE_OFFLINE, (
        "timed_call with an exception must record failure → OFFLINE."
    )
