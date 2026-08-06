"""T-NEW-054 regression test: cap tabs per node, default 35.

Per `testing-report_20260803.md`:
  "cap number of tabs connected to a node with an adjustable
   parameter defaulting to 35"

The fix:
1. `_check_max_tabs_per_node(pid, tabset)` helper on
   `NchantdOfficeCloakModel` reads
   ``config.dikt["max_tabs_per_node"]`` (default 35).
2. `add_tab` calls the helper before creating the tab; returns None
   when the limit is reached.
3. `cmd_on_change_max_tabs_per_node` settings handler persists the
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
# Model: _check_max_tabs_per_node helper
# ---------------------------------------------------------------------------

def test_check_max_tabs_helper_exists():
    """NchantdOfficeCloakModel must define _check_max_tabs_per_node."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    assert hasattr(NchantdOfficeCloakModel, "_check_max_tabs_per_node"), (
        "NchantdOfficeCloakModel must define _check_max_tabs_per_node (T-NEW-054)"
    )


def test_check_max_tabs_default_allows_first_tab():
    """With no existing tabs and default config, the check returns True."""
    model = _bare_model()
    model.config = SimpleNamespace(dikt={})
    from pandas import DataFrame
    model.get_documents = lambda node, tabset: DataFrame()
    assert model._check_max_tabs_per_node("node-1", "center") is True


def test_check_max_tabs_at_limit_rejects():
    """When tab count equals the limit, the check returns False."""
    model = _bare_model()
    model.config = SimpleNamespace(dikt={"max_tabs_per_node": 3})
    from pandas import DataFrame
    model.get_documents = lambda node, tabset: DataFrame([{"a": 1}] * 3)
    assert model._check_max_tabs_per_node("node-1", "center") is False


def test_check_max_tabs_below_limit_allows():
    """When tab count is below the limit, the check returns True."""
    model = _bare_model()
    model.config = SimpleNamespace(dikt={"max_tabs_per_node": 5})
    from pandas import DataFrame
    model.get_documents = lambda node, tabset: DataFrame([{"a": 1}] * 3)
    assert model._check_max_tabs_per_node("node-1", "center") is True


def test_check_max_tabs_zero_disables_limit():
    """When limit is 0, the check returns True (unlimited)."""
    model = _bare_model()
    model.config = SimpleNamespace(dikt={"max_tabs_per_node": 0})
    from pandas import DataFrame
    model.get_documents = lambda node, tabset: DataFrame([{"a": 1}] * 1000)
    assert model._check_max_tabs_per_node("node-1", "center") is True


def test_check_max_tabs_negative_disables_limit():
    """When limit is negative, the check returns True (unlimited)."""
    model = _bare_model()
    model.config = SimpleNamespace(dikt={"max_tabs_per_node": -1})
    from pandas import DataFrame
    model.get_documents = lambda node, tabset: DataFrame([{"a": 1}] * 1000)
    assert model._check_max_tabs_per_node("node-1", "center") is True


def test_add_tab_calls_check_max_tabs():
    """Source-level: add_tab must call _check_max_tabs_per_node."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    src = inspect.getsource(NchantdOfficeCloakModel.add_tab)
    assert "_check_max_tabs_per_node" in src, (
        "add_tab must call _check_max_tabs_per_node (T-NEW-054)"
    )


def test_add_tab_returns_none_when_limit_hit():
    """When the limit is reached, add_tab returns None."""
    model = _bare_model()
    model.config = SimpleNamespace(dikt={"max_tabs_per_node": 1})
    from pandas import DataFrame
    model.get_documents = lambda node, tabset: DataFrame([{"a": 1}])  # already at limit
    # The helper short-circuits before super().add_tab is called,
    # so we don't need to stub anything — the test fails if super() runs
    # because the model has no store / app / view attached.
    result = model.add_tab("name", "pid", 0, None)
    assert result is None, "add_tab must return None when limit is hit"


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
    assert result is settings  # chainable


def test_settings_handler_default_35():
    """handler with no event defaults to 35."""
    settings = _bare_settings()
    settings.config = SimpleNamespace(dikt={})
    result = settings.cmd_on_change_max_tabs_per_node()
    assert settings.max_tabs_per_node == 35
    assert settings.config.dikt["max_tabs_per_node"] == 35


def test_settings_handler_zero_disables():
    """0 means unlimited — still persisted as 0."""
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
    # Should not raise; default applied
    assert result is settings


def test_initialize_center_renders_max_tabs_spinbox():
    """_initialize_center must include a NchantdSpinBox for max_tabs_per_node."""
    from nchantdoffice.widgets.config.settings import (
        NchantdOfficeInterfaceSettings,
    )
    src = inspect.getsource(NchantdOfficeInterfaceSettings._initialize_center)
    assert "max_tabs_per_node" in src, (
        "_initialize_center must mention max_tabs_per_node"
    )
    assert "NchantdSpinBox" in src, (
        "_initialize_center must add a NchantdSpinBox for max_tabs_per_node"
    )
    assert "cmd_on_change_max_tabs_per_node" in src, (
        "_initialize_center must wire the spinbox to cmd_on_change_max_tabs_per_node"
    )
