# -*- coding: utf-8 -*-
"""T-NEW-167: desktop ad-tab telemetry emitter — AST + unit tests.

Pinned here:

  - ``AdTabTelemetry`` exists in the atnrg package with the three
    emit hooks the Ad tab calls: ``emit_rotation``, ``emit_click``,
    ``emit_session_tick``.
  - ``build_event`` produces the full server contract (closed
    field set) with ``schema_version: 1``.
  - ``_identity`` prefers ``desktop_uuid`` over ``install_id``
    (server-issued beats locally minted).
  - ``url_params`` returns '' when the instance id is unknown
    (no orphan page beacons) and carries inst/uid/ut/stk/top
    when known.
  - ``build_batch`` caps at the server's max_batch_size (200)
    and returns None for empty batches.
  - ``browsers.py`` wires the three hooks: ``_load_ad_layout``
    emits rotation, ``_open_settings_node`` emits click, and
    the telemetry timer (30s) emits session_tick; ``_cleanup``
    tears the timer down.
  - The emitter module imports headless — no Qt, no logma at
    import time (guarded imports inside functions).

AST-based where possible (same pattern as
test_ad_tab_rotation.py) so the suite runs without a Qt event
loop.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

PROJ_ROOT = Path("/home/solubrew/.hermes/projects/nchantdoffice")
sys.path.insert(0, str(PROJ_ROOT))

TELEMETRY = (
    PROJ_ROOT
    / "nchantdoffice"
    / "widgets"
    / "documents"
    / "atnrg"
    / "ad_telemetry.py"
)
BROWSERS = (
    PROJ_ROOT / "nchantdoffice" / "widgets" / "documents" / "atnrg" / "browsers.py"
)

# Server contract — must mirror nchantdoffice_com's
# AdTelemetryEventModel columns (T-NEW-167).
CONTRACT_FIELDS = {
    "event_type",
    "campaign_slug",
    "layout",
    "slot_index",
    "stack_position",
    "is_on_top",
    "client_instance_id",
    "client_user_id",
    "session_age_seconds",
    "client_ts",
    "schema_version",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text(), filename=str(path))


def _class(tree: ast.Module, name: str) -> ast.ClassDef:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
    raise AssertionError(f"class {name} not found")


def _method(cls: ast.ClassDef, name: str) -> ast.FunctionDef:
    for node in cls.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"method {name} not found in {cls.name}")


def _calls(tree: ast.AST) -> set[str]:
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Attribute):
                out.add(fn.attr)
            elif isinstance(fn, ast.Name):
                out.add(fn.id)
    return out


# ---------------------------------------------------------------------------
# Module shape
# ---------------------------------------------------------------------------


def test_module_imports_headless():
    """The module must import without Qt or a running app."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "nchantdoffice_atnrg_ad_telemetry", TELEMETRY
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert hasattr(mod, "AdTabTelemetry")


def test_class_defines_emit_hooks():
    tree = _parse(TELEMETRY)
    cls = _class(tree, "AdTabTelemetry")
    methods = {
        n.name for n in cls.body if isinstance(n, ast.FunctionDef)
    }
    assert {"emit_rotation", "emit_click", "emit_session_tick"} <= methods


def test_class_constants_match_server_contract():
    tree = _parse(TELEMETRY)
    cls = _class(tree, "AdTabTelemetry")
    assigns = {}
    for node in cls.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    try:
                        assigns[target.id] = ast.literal_eval(node.value)
                    except ValueError:
                        pass
    assert assigns["TELEMETRY_URL_PATH"] == "/api/ads/telemetry/events"
    assert assigns["MAX_BATCH_SIZE"] == 200
    assert assigns["SESSION_TICK_INTERVAL_S"] == 30


# ---------------------------------------------------------------------------
# build_event contract (live instantiation with a dummy tab)
# ---------------------------------------------------------------------------


class _DummyTabset:
    """Tabset stub that owns one tab: this one, at index 3."""

    def __init__(self, tab, current=True):
        self._tab = tab
        self._current = current

    def indexOf(self, widget):
        return 3 if widget is self._tab else -1

    def currentWidget(self):
        return self._tab if self._current else object()


class _DummyTab:
    def __init__(self, current=True):
        self._current = current

    def parent(self):
        return _DummyTabset(self, current=self._current)


def _make_emitter():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "nchantdoffice_atnrg_ad_telemetry", TELEMETRY
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.AdTabTelemetry(_DummyTab()), mod


def test_build_event_full_contract(monkeypatch):
    emitter, mod = _make_emitter()
    monkeypatch.setattr(
        emitter, "_identity", lambda: ("inst-uuid", 42), raising=True
    )
    event = emitter.build_event("rotation", layout="stack3")
    assert set(event.keys()) == CONTRACT_FIELDS
    assert event["event_type"] == "rotation"
    assert event["layout"] == "stack3"
    assert event["stack_position"] == 3
    assert event["is_on_top"] is True
    assert event["client_instance_id"] == "inst-uuid"
    assert event["client_user_id"] == 42
    assert isinstance(event["session_age_seconds"], int)
    assert event["schema_version"] == 1


def test_build_event_tab_context_off_top():
    """Tab present in tabset but NOT current -> is_on_top False."""
    emitter, _ = _make_emitter()

    class _NotCurrent:
        def indexOf(self, widget):
            return 2

        def currentWidget(self):
            return object()  # some other tab

    class _Tab:
        def parent(self):
            return _NotCurrent()

    emitter._tab = _Tab()
    event = emitter.build_event("session_tick")
    assert event["stack_position"] == 2
    assert event["is_on_top"] is False


def test_build_event_no_tabset_yields_nones():
    emitter, _ = _make_emitter()

    class _Tab:
        def parent(self):
            return None

    emitter._tab = _Tab()
    event = emitter.build_event("session_tick")
    assert event["stack_position"] is None
    assert event["is_on_top"] is None


def test_identity_prefers_desktop_uuid(monkeypatch):
    import types
    emitter, mod = _make_emitter()

    fake_store = types.ModuleType("nchantdoffice.license.install_store")

    class _Store:
        def get_or_create(self):
            return {
                "install_id": "local-uuid",
                "desktop_uuid": "server-uuid",
            }

    fake_store.InstallStore = _Store
    monkeypatch.setitem(
        sys.modules, "nchantdoffice.license.install_store", fake_store
    )
    inst, uid = emitter._identity()
    assert inst == "server-uuid"
    assert uid is None  # no QApplication in test env


def test_identity_falls_back_to_install_id(monkeypatch):
    import types
    emitter, mod = _make_emitter()

    fake_store = types.ModuleType("nchantdoffice.license.install_store")

    class _Store:
        def get_or_create(self):
            return {
                "install_id": "local-uuid",
                "desktop_uuid": None,
            }

    fake_store.InstallStore = _Store
    monkeypatch.setitem(
        sys.modules, "nchantdoffice.license.install_store", fake_store
    )
    inst, _ = emitter._identity()
    assert inst == "local-uuid"


def test_identity_survives_missing_store(monkeypatch):
    emitter, _ = _make_emitter()

    def boom():
        raise ImportError("no store")

    monkeypatch.setattr(
        "builtins.__import__",
        lambda name, *a, **k: (
            boom()
            if "install_store" in name
            else __builtins__.__import__(name, *a, **k)
        ),
    )
    inst, uid = emitter._identity()
    assert inst == ""
    assert uid is None


# ---------------------------------------------------------------------------
# url_params
# ---------------------------------------------------------------------------


def test_url_params_empty_when_no_identity(monkeypatch):
    emitter, _ = _make_emitter()
    monkeypatch.setattr(emitter, "_identity", lambda: ("", None))
    assert emitter.url_params() == ""


def test_url_params_carry_full_context(monkeypatch):
    emitter, _ = _make_emitter()
    monkeypatch.setattr(
        emitter, "_identity", lambda: ("inst-uuid", 42)
    )
    from urllib.parse import parse_qs
    params = parse_qs(emitter.url_params())
    assert params["inst"] == ["inst-uuid"]
    assert params["uid"] == ["42"]
    assert "ut" in params  # session age
    assert params["stk"] == ["3"]  # from _DummyTabset
    assert params["top"] == ["1"]


# ---------------------------------------------------------------------------
# build_batch
# ---------------------------------------------------------------------------


def test_build_batch_caps_at_server_max():
    emitter, _ = _make_emitter()
    events = [{"event_type": "session_tick"} for _ in range(250)]
    batch = emitter.build_batch(events)
    assert len(batch["events"]) == 200
    assert batch["schema_version"] == 1


def test_build_batch_none_for_empty():
    emitter, _ = _make_emitter()
    assert emitter.build_batch([]) is None


# ---------------------------------------------------------------------------
# browsers.py wiring (AST)
# ---------------------------------------------------------------------------


def test_browsers_load_ad_layout_emits_rotation():
    tree = _parse(BROWSERS)
    cls = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "NchantdOfficeAdTab":
            cls = node
            break
    assert cls is not None
    fn = _method(cls, "_load_ad_layout")
    called = _calls(fn)
    assert "emit_rotation" in called


def test_browsers_open_settings_emits_click():
    tree = _parse(BROWSERS)
    cls = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "NchantdOfficeAdTab":
            cls = node
            break
    assert cls is not None
    fn = _method(cls, "_open_settings_node")
    called = _calls(fn)
    assert "emit_click" in called


def test_browsers_telemetry_timer_started_and_cleaned():
    tree = _parse(BROWSERS)
    cls = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "NchantdOfficeAdTab":
            cls = node
            break
    assert cls is not None
    method_names = {
        n.name for n in cls.body if isinstance(n, ast.FunctionDef)
    }
    assert "_start_telemetry_timer" in method_names
    assert "_emit_telemetry_tick" in method_names
    # initView starts the timer; _cleanup stops it.
    init = _method(cls, "initView")
    assert "_start_telemetry_timer" in _calls(init)
    cleanup = _method(cls, "_cleanup")
    assert "_telemetry_timer" in ast.dump(cleanup)


def test_browsers_url_builder_appends_telemetry_params():
    tree = _parse(BROWSERS)
    cls = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "NchantdOfficeAdTab":
            cls = node
            break
    fn = _method(cls, "_ad_url_for_layout")
    assert "url_params" in _calls(fn)
