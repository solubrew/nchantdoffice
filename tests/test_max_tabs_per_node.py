"""T-NEW-054 regression test: cap tabs per node, default 35 — auto-create child.

Per `testing-report_20260803.md`:
  "cap number of tabs connected to a node with an adjustable
   parameter defaulting to 35"

User correction (2026-08-06): when the per-node tab limit is hit,
the model should automatically create a CHILD node under the
overflow node and place the next tab there -- so the user's flow
is never blocked; the tree just grows by one level.

The fix:
1. `_resolve_pid_for_max_tabs(pid, tabset)` returns the original
   ``pid`` if the limit isn't hit, or a new child nid if a
   child node was auto-created. Returns ``None`` only when the
   limit is hit AND a child node could not be created.
2. `_create_child_node(pid)` creates a generic child node whose
   name is ``<parent>_<n>`` (n = next free index).
3. `_get_node_name(pid)` / `_count_children_of(pid)` helpers.
4. `add_tab` uses `_resolve_pid_for_max_tabs` instead of the old
   `_check_max_tabs_per_node` boolean check.
5. `cmd_on_change_max_tabs_per_node` settings handler persists the
   user-chosen value to `config.dikt`.
6. Interface Tab renders a NchantdSpinBox wired to the handler.
"""

import inspect
from types import SimpleNamespace


def _bare_model():
    """Create a minimal NchantdOfficeCloakModel without running __init__."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    return NchantdOfficeCloakModel.__new__(NchantdOfficeCloakModel)


def _bare_settings():
    """Create a minimal NchantdOfficeInterfaceSettings without __init__."""
    from nchantdoffice.widgets.config.settings import (
        NchantdOfficeInterfaceSettings,
    )
    return NchantdOfficeInterfaceSettings.__new__(NchantdOfficeInterfaceSettings)


# ---------------------------------------------------------------------------
# Model: _resolve_pid_for_max_tabs helper
# ---------------------------------------------------------------------------

def test_resolve_pid_helper_exists():
    """NchantdOfficeCloakModel must define _resolve_pid_for_max_tabs."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    assert hasattr(NchantdOfficeCloakModel, "_resolve_pid_for_max_tabs"), (
        "NchantdOfficeCloakModel must define _resolve_pid_for_max_tabs (T-NEW-054)"
    )


def test_resolve_pid_returns_original_when_below_limit():
    """With tabs below the limit, returns the original pid unchanged."""
    model = _bare_model()
    model.config = SimpleNamespace(dikt={"max_tabs_per_node": 35})
    from pandas import DataFrame
    model.get_documents = lambda node, tabset: DataFrame([{"a": 1}] * 3)
    result = model._resolve_pid_for_max_tabs("node-1", "center")
    assert result == "node-1"


def test_resolve_pid_returns_child_when_limit_hit():
    """When the limit is reached, auto-creates a child and returns its nid."""
    model = _bare_model()
    model.config = SimpleNamespace(dikt={"max_tabs_per_node": 3})
    from pandas import DataFrame
    model.get_documents = lambda node, tabset: DataFrame([{"a": 1}] * 3)
    # Stub _create_child_node to return a synthetic nid
    model._create_child_node = lambda pid: "child-99"
    result = model._resolve_pid_for_max_tabs("node-1", "center")
    assert result == "child-99", "Must return the new child's nid, not the original"


def test_resolve_pid_returns_none_when_child_create_fails():
    """If child creation fails and the limit is hit, returns None."""
    model = _bare_model()
    model.config = SimpleNamespace(dikt={"max_tabs_per_node": 2})
    from pandas import DataFrame
    model.get_documents = lambda node, tabset: DataFrame([{"a": 1}] * 2)
    model._create_child_node = lambda pid: None
    result = model._resolve_pid_for_max_tabs("node-1", "center")
    assert result is None, "Must return None when limit hit and child cannot be created"


def test_resolve_pid_default_config_returns_original():
    """With no config at all, default limit of 35 allows creation."""
    model = _bare_model()
    model.config = SimpleNamespace(dikt={})
    from pandas import DataFrame
    model.get_documents = lambda node, tabset: DataFrame([{"a": 1}] * 3)
    result = model._resolve_pid_for_max_tabs("node-1", "center")
    assert result == "node-1"


def test_resolve_pid_zero_disables_limit():
    """When limit is 0, returns the original pid (unlimited)."""
    model = _bare_model()
    model.config = SimpleNamespace(dikt={"max_tabs_per_node": 0})
    from pandas import DataFrame
    model.get_documents = lambda node, tabset: DataFrame([{"a": 1}] * 1000)
    assert model._resolve_pid_for_max_tabs("node-1", "center") == "node-1"


def test_resolve_pid_negative_disables_limit():
    """When limit is negative, returns the original pid."""
    model = _bare_model()
    model.config = SimpleNamespace(dikt={"max_tabs_per_node": -1})
    from pandas import DataFrame
    model.get_documents = lambda node, tabset: DataFrame([{"a": 1}] * 1000)
    assert model._resolve_pid_for_max_tabs("node-1", "center") == "node-1"


# ---------------------------------------------------------------------------
# Model: _create_child_node helper
# ---------------------------------------------------------------------------

def test_create_child_node_exists():
    """NchantdOfficeCloakModel must define _create_child_node."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    assert hasattr(NchantdOfficeCloakModel, "_create_child_node"), (
        "NchantdOfficeCloakModel must define _create_child_node (T-NEW-054)"
    )


def test_create_child_node_uses_parent_name_and_count():
    """_create_child_node must name the child <parent>_<n>."""
    model = _bare_model()
    model._get_node_name = lambda pid: "research"
    model._count_children_of = lambda pid: 2
    captured = {}

    def fake_add_node(name, ntype, pid, pos, parameters=None, tabset=None, return_node=False):
        captured["name"] = name
        captured["pid"] = pid
        captured["pos"] = pos
        captured["return_node"] = return_node
        return "new-child-nid"

    model.add_node = fake_add_node
    result = model._create_child_node("parent-1")
    assert captured["name"] == "research_3"
    assert captured["pid"] == "parent-1"
    assert captured["pos"] == 3
    assert captured["return_node"] is False
    assert result == "new-child-nid"


def test_create_child_node_falls_back_to_default_name():
    """When parent name lookup fails, fallback is '<default>_<n>'."""
    model = _bare_model()
    model._get_node_name = lambda pid: None
    model._count_children_of = lambda pid: 0
    captured = {}

    def fake_add_node(name, ntype, pid, pos, parameters=None, tabset=None, return_node=False):
        captured["name"] = name
        return "x"

    model.add_node = fake_add_node
    model._create_child_node("p")
    assert captured["name"] == "node_1"


def test_create_child_node_returns_none_on_error():
    """Any exception returns None instead of crashing."""
    model = _bare_model()
    model._get_node_name = lambda pid: "ok"
    model._count_children_of = lambda pid: 0

    def bad_add_node(*a, **kw):
        raise RuntimeError("store error")

    model.add_node = bad_add_node
    assert model._create_child_node("p") is None


# ---------------------------------------------------------------------------
# Model: _get_node_name + _count_children_of helpers
# ---------------------------------------------------------------------------

def test_get_node_name_returns_name_from_store():
    """_get_node_name reads the 'name_txt' column from the store."""
    model = _bare_model()
    from pandas import DataFrame
    fake_df = DataFrame([{"name_txt": "research", "other": "x"}])

    class FakeStore:
        def get_table(self, table, cfg):
            return fake_df

    model.store = FakeStore()
    assert model._get_node_name("nid-1") == "research"


def test_get_node_name_returns_none_when_no_store():
    """No store attribute -> None."""
    model = _bare_model()
    model.store = None
    assert model._get_node_name("nid-1") is None


def test_get_node_name_returns_none_when_empty():
    """Empty DataFrame -> None."""
    model = _bare_model()
    from pandas import DataFrame
    fake_df = DataFrame()
    model.store = type("S", (), {"get_table": lambda self, t, c: fake_df})()
    assert model._get_node_name("nid-1") is None


def test_count_children_of_returns_correct_count():
    """_count_children_of counts rows whose pid_txt matches."""
    model = _bare_model()
    from pandas import DataFrame
    fake_df = DataFrame([
        {"nid_txt": "a", "pid_txt": "parent"},
        {"nid_txt": "b", "pid_txt": "parent"},
        {"nid_txt": "c", "pid_txt": "other"},
    ])
    model.get_nodes = lambda: fake_df
    assert model._count_children_of("parent") == 2
    assert model._count_children_of("other") == 1
    assert model._count_children_of("nonexistent") == 0


def test_count_children_of_returns_zero_when_no_nodes():
    """Empty or missing nodes -> 0."""
    model = _bare_model()
    from pandas import DataFrame
    model.get_nodes = lambda: DataFrame()
    assert model._count_children_of("parent") == 0


# ---------------------------------------------------------------------------
# Integration: add_tab uses _resolve_pid_for_max_tabs
# ---------------------------------------------------------------------------

def test_add_tab_uses_resolve_pid():
    """Source-level: add_tab must call _resolve_pid_for_max_tabs."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    src = inspect.getsource(NchantdOfficeCloakModel.add_tab)
    assert "_resolve_pid_for_max_tabs" in src, (
        "add_tab must call _resolve_pid_for_max_tabs (T-NEW-054)"
    )


def test_add_tab_no_longer_uses_old_check():
    """Old _check_max_tabs_per_node is gone (replaced by _resolve_pid_for_max_tabs)."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    assert not hasattr(NchantdOfficeCloakModel, "_check_max_tabs_per_node"), (
        "_check_max_tabs_per_node must be replaced by _resolve_pid_for_max_tabs"
    )


def test_add_tab_returns_none_when_no_pid():
    """When the limit is hit and child creation fails, add_tab returns None."""
    model = _bare_model()
    model.config = SimpleNamespace(dikt={"max_tabs_per_node": 1})
    from pandas import DataFrame
    model.get_documents = lambda node, tabset: DataFrame([{"a": 1}])
    model._create_child_node = lambda pid: None
    result = model.add_tab("name", "pid", 0, None)
    assert result is None


# ---------------------------------------------------------------------------
# Settings: cmd_on_change_max_tabs_per_node handler
# ---------------------------------------------------------------------------

def test_settings_handler_exists():
    """NchantdOfficeInterfaceSettings must define cmd_on_change_max_tabs_per_node."""
    from nchantdoffice.widgets.config.settings import (
        NchantdOfficeInterfaceSettings,
    )
    assert hasattr(
        NchantdOfficeInterfaceSettings, "cmd_on_change_max_tabs_per_node"
    ), "cmd_on_change_max_tabs_per_node must exist (T-NEW-054)"


def test_settings_handler_persists_value():
    """handler must persist value to config.dikt."""
    settings = _bare_settings()
    settings.config = SimpleNamespace(dikt={})

    class FakeEvent:
        def value(self):
            return 50

    result = settings.cmd_on_change_max_tabs_per_node(event=FakeEvent())
    assert settings.max_tabs_per_node == 50
    assert settings.config.dikt["max_tabs_per_node"] == 50
    assert result is settings


def test_settings_handler_default_35():
    """handler with no event defaults to 35."""
    settings = _bare_settings()
    settings.config = SimpleNamespace(dikt={})
    result = settings.cmd_on_change_max_tabs_per_node()
    assert settings.max_tabs_per_node == 35
    assert settings.config.dikt["max_tabs_per_node"] == 35


def test_settings_handler_zero_disables():
    """0 means unlimited - still persisted as 0."""
    settings = _bare_settings()
    settings.config = SimpleNamespace(dikt={})

    class FakeEvent:
        def value(self):
            return 0

    settings.cmd_on_change_max_tabs_per_node(event=FakeEvent())
    assert settings.config.dikt["max_tabs_per_node"] == 0


def test_settings_handler_swallows_exception():
    """handler must log-and-continue on bad input."""
    settings = _bare_settings()
    settings.config = SimpleNamespace(dikt={})

    class BadEvent:
        def value(self):
            raise RuntimeError("boom")

    result = settings.cmd_on_change_max_tabs_per_node(event=BadEvent())
    assert result is settings


def test_initialize_center_renders_max_tabs_spinbox():
    """_initialize_center must include a NchantdSpinBox for max_tabs_per_node."""
    from nchantdoffice.widgets.config.settings import (
        NchantdOfficeInterfaceSettings,
    )
    src = inspect.getsource(NchantdOfficeInterfaceSettings._initialize_center)
    assert "max_tabs_per_node" in src
    assert "NchantdSpinBox" in src
    assert "cmd_on_change_max_tabs_per_node" in src
