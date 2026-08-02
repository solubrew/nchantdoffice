"""T-NEW-034 -- Data Source config stubs regression tests.

Two empty methods in ``NchantdOfficeDataSourcesSettings``
(``widgets/config/source_config.py``) need real
implementations:

  1. ``cmd_change_data_source_pane_size`` — read the pane-size
     dropdown ("Full", "50%", "10%"), persist the selection to
     ``config.dikt["data_source_pane_size"]``, and resize the
     parent splitter / pane.

  2. ``cmd_toggle_apikey_visibility`` — toggle the
     ``NchantdLabeledEntry.textbox`` echo mode between
     ``Password`` (obscured) and ``Normal`` (visible) for the
     apikey identified by ``event.cfg["apikey_id"]``.

Both follow the Sprint 23 config-flag handler pattern: read
from event, persist to ``config.dikt``, log + swallow on
error, return ``self``.
"""

import sys
from types import SimpleNamespace

from PySide6.QtWidgets import QApplication, QLineEdit

_QAPP = QApplication.instance() or QApplication(sys.argv)

import nchantdoffice.widgets.config.source_config  # establish import order

# ---------------------------------------------------------------------------
# Fixture: build NchantdOfficeDataSourcesSettings via __new__ + inject
# ---------------------------------------------------------------------------


def _make_settings():
    """Build a NchantdOfficeDataSourcesSettings-lite via __new__
    so we can drive the handlers without a live Qt parent
    chain (Sprint 28-29 pattern)."""
    from nchantdoffice.widgets.config.source_config import (
        NchantdOfficeDataSourcesSettings,
    )

    settings = NchantdOfficeDataSourcesSettings.__new__(NchantdOfficeDataSourcesSettings)
    settings.config = SimpleNamespace(dikt={})
    settings.apikeys = {}
    settings.data_source_size_combo = None
    settings.layout = None
    return settings


# ---------------------------------------------------------------------------
# cmd_change_data_source_pane_size
# ---------------------------------------------------------------------------


def test_cmd_change_data_source_pane_size_persists_selection():
    """The handler reads the dropdown's currentText and
    persists it to ``config.dikt["data_source_pane_size"]``.
    """
    settings = _make_settings()
    settings.data_source_size_combo = SimpleNamespace(currentText=lambda: "50%")
    result = settings.cmd_change_data_source_pane_size()
    assert settings.config.dikt["data_source_pane_size"] == "50%"
    assert result is settings


def test_cmd_change_data_source_pane_size_persists_full():
    """Test with each of the three options."""
    for option in ("Full", "50%", "10%"):
        settings = _make_settings()
        settings.data_source_size_combo = SimpleNamespace(currentText=lambda opt=option: opt)
        settings.cmd_change_data_source_pane_size()
        assert settings.config.dikt["data_source_pane_size"] == option


def test_cmd_change_data_source_pane_size_returns_self():
    """Mirrors the Sprint 23 return-self pattern for chainable
    call sites.
    """
    settings = _make_settings()
    settings.data_source_size_combo = SimpleNamespace(currentText=lambda: "Full")
    result = settings.cmd_change_data_source_pane_size()
    assert result is settings


def test_cmd_change_data_source_pane_size_swallows_exception():
    """Defensive: if the combo is missing or raises, the
    handler must log + swallow rather than crashing the UI.
    """
    settings = _make_settings()
    settings.data_source_size_combo = None  # no combo available
    # Must NOT raise
    result = settings.cmd_change_data_source_pane_size()
    assert result is settings


# ---------------------------------------------------------------------------
# cmd_toggle_apikey_visibility
# ---------------------------------------------------------------------------


def test_cmd_toggle_apikey_visibility_switches_to_normal_when_password():
    """When the entry's textbox is in Password mode, the
    handler switches it to Normal (visible).
    """
    settings = _make_settings()
    # Build a real QLineEdit so we can test echo mode
    entry_box = QLineEdit()
    entry_box.setEchoMode(QLineEdit.EchoMode.Password)
    entry = SimpleNamespace(textbox=entry_box)
    settings.apikeys = {"source-1": entry}
    event = SimpleNamespace(
        isChecked=lambda: True,
        config=SimpleNamespace(dikt={"apikey_id": "source-1"}),
    )
    settings.cmd_toggle_apikey_visibility(event=event)
    assert entry_box.echoMode() == QLineEdit.EchoMode.Normal


def test_cmd_toggle_apikey_visibility_switches_to_password_when_normal():
    """When the entry's textbox is in Normal mode, the
    handler switches it to Password (obscured).
    """
    settings = _make_settings()
    entry_box = QLineEdit()
    entry_box.setEchoMode(QLineEdit.EchoMode.Normal)
    entry = SimpleNamespace(textbox=entry_box)
    settings.apikeys = {"source-1": entry}
    event = SimpleNamespace(
        isChecked=lambda: True,
        config=SimpleNamespace(dikt={"apikey_id": "source-1"}),
    )
    settings.cmd_toggle_apikey_visibility(event=event)
    assert entry_box.echoMode() == QLineEdit.EchoMode.Password


def test_cmd_toggle_apikey_visibility_returns_self():
    """Mirrors the return-self pattern."""
    settings = _make_settings()
    entry_box = QLineEdit()
    entry = SimpleNamespace(textbox=entry_box)
    settings.apikeys = {"source-1": entry}
    event = SimpleNamespace(
        isChecked=lambda: True,
        config=SimpleNamespace(dikt={"apikey_id": "source-1"}),
    )
    result = settings.cmd_toggle_apikey_visibility(event=event)
    assert result is settings


def test_cmd_toggle_apikey_visibility_handles_missing_apikey_id():
    """Defensive: when ``apikey_id`` doesn't match any entry
    in ``self.apikeys``, the handler must log + swallow
    rather than raising KeyError.
    """
    settings = _make_settings()
    settings.apikeys = {}
    event = SimpleNamespace(
        isChecked=lambda: True,
        config=SimpleNamespace(dikt={"apikey_id": "nonexistent"}),
    )
    # Must NOT raise
    result = settings.cmd_toggle_apikey_visibility(event=event)
    assert result is settings


def test_cmd_toggle_apikey_visibility_handles_no_event():
    """Defensive: when no event is passed, the handler is a
    no-op (returns self). This covers the case where the
    handler is called programmatically without a Qt event.
    """
    settings = _make_settings()
    result = settings.cmd_toggle_apikey_visibility(event=None)
    assert result is settings
