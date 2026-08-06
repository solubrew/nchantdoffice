"""T-NEW-056 regression test: cap total nodes per non-pro user at 100.

User direction (2026-08-06): non-pro users can create at most 100
total tree nodes. Pro users (those with ``user.has_pro is True``)
bypass the limit.

The fix:
1. `_check_max_nodes_for_user(user=None)` on NchantdOfficeCloakModel
   reads ``config.dikt["max_nodes_per_user"]`` (default 100). Returns
   True if below the limit. Pro users bypass. 0 or negative disables.
   Best-effort: any exception returns True.
2. `add_node` and `add_node_app` call the helper before
   ``super().add_node(...)``; on False they return None.
3. `cmd_on_change_max_nodes_per_user` settings handler persists the
   user-chosen value to `config.dikt`.
4. Interface Tab renders a NchantdSpinBox wired to the handler.
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
# Model: _check_max_nodes_for_user helper
# ---------------------------------------------------------------------------

def test_check_max_nodes_helper_exists():
    """NchantdOfficeCloakModel must define _check_max_nodes_for_user."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    assert hasattr(NchantdOfficeCloakModel, "_check_max_nodes_for_user"), (
        "NchantdOfficeCloakModel must define _check_max_nodes_for_user (T-NEW-056)"
    )


def test_check_max_nodes_default_allows_creation():
    """With default config (limit 100) and 0 nodes, returns True."""
    model = _bare_model()
    model.config = SimpleNamespace(dikt={})
    from pandas import DataFrame
    model.get_nodes = lambda: DataFrame()
    assert model._check_max_nodes_for_user() is True


def test_check_max_nodes_below_limit():
    """With 50 nodes and limit 100, returns True."""
    model = _bare_model()
    model.config = SimpleNamespace(dikt={"max_nodes_per_user": 100})
    from pandas import DataFrame
    model.get_nodes = lambda: DataFrame([{"a": 1}] * 50)
    assert model._check_max_nodes_for_user() is True


def test_check_max_nodes_at_limit_returns_false():
    """With 100 nodes and limit 100, returns False."""
    model = _bare_model()
    model.config = SimpleNamespace(dikt={"max_nodes_per_user": 100})
    from pandas import DataFrame
    model.get_nodes = lambda: DataFrame([{"a": 1}] * 100)
    assert model._check_max_nodes_for_user() is False


def test_check_max_nodes_above_limit_returns_false():
    """With 150 nodes and limit 100, returns False."""
    model = _bare_model()
    model.config = SimpleNamespace(dikt={"max_nodes_per_user": 100})
    from pandas import DataFrame
    model.get_nodes = lambda: DataFrame([{"a": 1}] * 150)
    assert model._check_max_nodes_for_user() is False


def test_check_max_nodes_zero_disables_limit():
    """When limit is 0, returns True (unlimited)."""
    model = _bare_model()
    model.config = SimpleNamespace(dikt={"max_nodes_per_user": 0})
    from pandas import DataFrame
    model.get_nodes = lambda: DataFrame([{"a": 1}] * 10000)
    assert model._check_max_nodes_for_user() is True


def test_check_max_nodes_negative_disables_limit():
    """When limit is negative, returns True (unlimited)."""
    model = _bare_model()
    model.config = SimpleNamespace(dikt={"max_nodes_per_user": -1})
    from pandas import DataFrame
    model.get_nodes = lambda: DataFrame([{"a": 1}] * 10000)
    assert model._check_max_nodes_for_user() is True


def test_check_max_nodes_pro_user_bypasses():
    """A user with has_pro=True bypasses the limit."""
    model = _bare_model()
    model.config = SimpleNamespace(dikt={"max_nodes_per_user": 100})
    from pandas import DataFrame
    model.get_nodes = lambda: DataFrame([{"a": 1}] * 10000)
    pro_user = SimpleNamespace(has_pro=True)
    assert model._check_max_nodes_for_user(user=pro_user) is True


def test_check_max_nodes_non_pro_user_at_limit():
    """A user with has_pro=False at the limit returns False."""
    model = _bare_model()
    model.config = SimpleNamespace(dikt={"max_nodes_per_user": 100})
    from pandas import DataFrame
    model.get_nodes = lambda: DataFrame([{"a": 1}] * 100)
    non_pro_user = SimpleNamespace(has_pro=False)
    assert model._check_max_nodes_for_user(user=non_pro_user) is False


def test_check_max_nodes_falls_back_to_self_user():
    """When no user arg is passed, falls back to self.user."""
    model = _bare_model()
    model.config = SimpleNamespace(dikt={"max_nodes_per_user": 100})
    from pandas import DataFrame
    model.get_nodes = lambda: DataFrame([{"a": 1}] * 100)
    model.user = SimpleNamespace(has_pro=True)
    assert model._check_max_nodes_for_user() is True


def test_check_max_nodes_returns_true_on_exception():
    """Any exception returns True (never block on a config error)."""
    model = _bare_model()
    model.config = SimpleNamespace(dikt={"max_nodes_per_user": 100})

    def bad_get_nodes():
        raise RuntimeError("store error")

    model.get_nodes = bad_get_nodes
    assert model._check_max_nodes_for_user() is True


# ---------------------------------------------------------------------------
# Model: add_node + add_node_app gating
# ---------------------------------------------------------------------------

def test_add_node_uses_check_max_nodes():
    """Source-level: add_node must call _check_max_nodes_for_user."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    src = inspect.getsource(NchantdOfficeCloakModel.add_node)
    assert "_check_max_nodes_for_user" in src, (
        "add_node must call _check_max_nodes_for_user (T-NEW-056)"
    )


def test_add_node_app_uses_check_max_nodes():
    """Source-level: add_node_app must call _check_max_nodes_for_user."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    src = inspect.getsource(NchantdOfficeCloakModel.add_node_app)
    assert "_check_max_nodes_for_user" in src, (
        "add_node_app must call _check_max_nodes_for_user (T-NEW-056)"
    )


def test_add_node_returns_none_when_limit_hit():
    """When limit is hit, add_node returns None without writing."""
    model = _bare_model()
    model.config = SimpleNamespace(dikt={"max_nodes_per_user": 100})
    from pandas import DataFrame
    model.get_nodes = lambda: DataFrame([{"a": 1}] * 100)  # at limit
    result = model.add_node("child", "auto_child", "parent-1", 1)
    assert result is None


def test_add_node_app_returns_none_when_limit_hit():
    """When limit is hit, add_node_app returns None without writing."""
    model = _bare_model()
    model.config = SimpleNamespace(dikt={"max_nodes_per_user": 100})
    from pandas import DataFrame
    model.get_nodes = lambda: DataFrame([{"a": 1}] * 100)
    result = model.add_node_app("child", "auto_child", "parent-1", 1)
    assert result is None


def test_add_node_pro_user_bypasses_at_limit():
    """Pro users can create nodes even at the limit."""
    model = _bare_model()
    model.config = SimpleNamespace(dikt={"max_nodes_per_user": 100})
    from pandas import DataFrame
    model.get_nodes = lambda: DataFrame([{"a": 1}] * 100)
    model.user = SimpleNamespace(has_pro=True)
    # Stub super().add_node so the test doesn't blow up on the
    # missing store/app chain.
    from nchantrs.models.applicationmodels import NchantdCloakModel
    NchantdCloakModel.add_node = lambda self, *a, **kw: "new-node"
    result = model.add_node("child", "auto_child", "parent-1", 1)
    assert result == "new-node", "Pro user must bypass the limit"


# ---------------------------------------------------------------------------
# Settings: cmd_on_change_max_nodes_per_user handler
# ---------------------------------------------------------------------------

def test_settings_handler_exists():
    """NchantdOfficeInterfaceSettings must define cmd_on_change_max_nodes_per_user."""
    from nchantdoffice.widgets.config.settings import (
        NchantdOfficeInterfaceSettings,
    )
    assert hasattr(
        NchantdOfficeInterfaceSettings, "cmd_on_change_max_nodes_per_user"
    ), "cmd_on_change_max_nodes_per_user must exist (T-NEW-056)"


def test_settings_handler_persists_value():
    """handler must persist value to config.dikt."""
    settings = _bare_settings()
    settings.config = SimpleNamespace(dikt={})

    class FakeEvent:
        def value(self):
            return 200

    result = settings.cmd_on_change_max_nodes_per_user(event=FakeEvent())
    assert settings.max_nodes_per_user == 200
    assert settings.config.dikt["max_nodes_per_user"] == 200
    assert result is settings


def test_settings_handler_default_100():
    """handler with no event defaults to 100."""
    settings = _bare_settings()
    settings.config = SimpleNamespace(dikt={})
    result = settings.cmd_on_change_max_nodes_per_user()
    assert settings.max_nodes_per_user == 100
    assert settings.config.dikt["max_nodes_per_user"] == 100


def test_settings_handler_zero_disables():
    """0 means unlimited - still persisted as 0."""
    settings = _bare_settings()
    settings.config = SimpleNamespace(dikt={})

    class FakeEvent:
        def value(self):
            return 0

    settings.cmd_on_change_max_nodes_per_user(event=FakeEvent())
    assert settings.config.dikt["max_nodes_per_user"] == 0


def test_settings_handler_swallows_exception():
    """handler must log-and-continue on bad input."""
    settings = _bare_settings()
    settings.config = SimpleNamespace(dikt={})

    class BadEvent:
        def value(self):
            raise RuntimeError("boom")

    result = settings.cmd_on_change_max_nodes_per_user(event=BadEvent())
    assert result is settings


def test_initialize_center_renders_max_nodes_spinbox():
    """_initialize_center must include a NchantdSpinBox for max_nodes_per_user."""
    from nchantdoffice.widgets.config.settings import (
        NchantdOfficeInterfaceSettings,
    )
    src = inspect.getsource(NchantdOfficeInterfaceSettings._initialize_center)
    assert "max_nodes_per_user" in src
    assert "NchantdSpinBox" in src
    assert "cmd_on_change_max_nodes_per_user" in src
