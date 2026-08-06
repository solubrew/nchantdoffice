from types import SimpleNamespace
"""T-NEW-034 close-out: data source config card polish.

Sprint 29 filled two stubs (cmd_change_data_source_pane_size,
cmd_toggle_apikey_visibility). This test pins the remaining
3 slots added to the per-source config card:
- tracked checkbox (cmd_on_change_source_tracked)
- size detail label
- retention spinbox (cmd_on_change_source_retention)
- save button (cmd_save_source_settings)

Regression test: tests/test_source_config_card.py
"""

import inspect


def test_source_edit_pane_has_tracked_checkbox():
    """NchantdSourceEditPane.initView must render a tracked checkbox."""
    from nchantdoffice.widgets.panes.sources import NchantdSourceEditPane
    src = inspect.getsource(NchantdSourceEditPane.initView)
    assert "source_tracked_checkbox" in src
    assert "Track this source" in src


def test_source_edit_pane_has_size_label():
    """NchantdSourceEditPane.initView must render a size-detail label."""
    from nchantdoffice.widgets.panes.sources import NchantdSourceEditPane
    src = inspect.getsource(NchantdSourceEditPane.initView)
    assert "source_size_label" in src
    assert "Current Size" in src


def test_source_edit_pane_has_retention_spinbox():
    """NchantdSourceEditPane.initView must render a retention spinbox."""
    from nchantdoffice.widgets.panes.sources import NchantdSourceEditPane
    src = inspect.getsource(NchantdSourceEditPane.initView)
    assert "source_retention_spinbox" in src
    assert "Max Size" in src


def test_source_edit_pane_has_save_button():
    """NchantdSourceEditPane.initView must render a save button."""
    from nchantdoffice.widgets.panes.sources import NchantdSourceEditPane
    src = inspect.getsource(NchantdSourceEditPane.initView)
    assert "source_save_button" in src
    assert "Save Source Settings" in src


def test_cmd_on_change_source_tracked_exists():
    """The tracked handler must exist on NchantdSourceEditPane."""
    from nchantdoffice.widgets.panes.sources import NchantdSourceEditPane
    assert hasattr(NchantdSourceEditPane, "cmd_on_change_source_tracked")


def test_cmd_on_change_source_retention_exists():
    """The retention handler must exist on NchantdSourceEditPane."""
    from nchantdoffice.widgets.panes.sources import NchantdSourceEditPane
    assert hasattr(NchantdSourceEditPane, "cmd_on_change_source_retention")


def test_cmd_save_source_settings_exists():
    """The save handler must exist on NchantdSourceEditPane."""
    from nchantdoffice.widgets.panes.sources import NchantdSourceEditPane
    assert hasattr(NchantdSourceEditPane, "cmd_save_source_settings")


def test_cmd_save_source_settings_persists_values():
    """Save handler must persist tracked + retention to config.dikt."""
    from nchantdoffice.widgets.panes.sources import NchantdSourceEditPane
    from types import SimpleNamespace

    pane = NchantdSourceEditPane.__new__(NchantdSourceEditPane)
    pane.config = SimpleNamespace(dikt={"source_tracked": False, "source_retention_mb": 0})
    # Stub widgets
    pane.source_tracked_checkbox = SimpleNamespace(isChecked=lambda: True)
    pane.source_retention_spinbox = SimpleNamespace(value=lambda: 4096)
    pane.cmd_save_source_settings()
    assert pane.config.dikt["source_tracked"] is True
    assert pane.config.dikt["source_retention_mb"] == 4096


def test_cmd_save_source_settings_swallows_exception():
    """Save handler must not raise on bad input."""
    from nchantdoffice.widgets.panes.sources import NchantdSourceEditPane
    pane = NchantdSourceEditPane.__new__(NchantdSourceEditPane)
    pane.config = SimpleNamespace(dikt={})
    # No widgets - source_tracked_checkbox / source_retention_spinbox missing
    result = pane.cmd_save_source_settings()
    assert result is pane


def test_cmd_on_change_source_tracked_persists():
    """Tracked handler must persist to config.dikt."""
    from nchantdoffice.widgets.panes.sources import NchantdSourceEditPane
    from types import SimpleNamespace

    pane = NchantdSourceEditPane.__new__(NchantdSourceEditPane)
    pane.config = SimpleNamespace(dikt={})
    pane.cmd_on_change_source_tracked(event=True)
    assert pane.config.dikt["source_tracked"] is True
    pane.cmd_on_change_source_tracked(event=False)
    assert pane.config.dikt["source_tracked"] is False


def test_cmd_on_change_source_retention_persists():
    """Retention handler must persist to config.dikt."""
    from nchantdoffice.widgets.panes.sources import NchantdSourceEditPane
    from types import SimpleNamespace

    pane = NchantdSourceEditPane.__new__(NchantdSourceEditPane)
    pane.config = SimpleNamespace(dikt={})
    pane.source_retention_spinbox = SimpleNamespace(value=lambda: 2048)
    pane.cmd_on_change_source_retention()
    assert pane.config.dikt["source_retention_mb"] == 2048
