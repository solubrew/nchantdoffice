"""T-NEW-038 close-out: FileDetailsPane refresh on initial file open.

The New TODOs staging list had:
  'FileDetailsPane is not updated on initial file open need to
   implement a refresh'

The fix: ``NchantdFileDetailsPane.set_file_path`` now also calls
``refresh()`` so every detail field (size, hash, dates) updates
when the file path changes -- including the initial file-open
case where the widgets were built at initView time with stale
empty values.

Regression test: tests/test_file_details_pane_refresh.py
"""

import inspect
import os
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock


def test_refresh_method_exists():
    """``NchantdFileDetailsPane`` must define ``refresh()``."""
    from nchantdoffice.widgets.panes.files import NchantdFileDetailsPane
    assert hasattr(NchantdFileDetailsPane, "refresh"), (
        "NchantdFileDetailsPane must define refresh() (T-NEW-038)"
    )


def test_set_file_path_calls_refresh():
    """``set_file_path`` must call ``refresh()`` after updating the entry."""
    from nchantdoffice.widgets.panes.files import NchantdFileDetailsPane
    src = inspect.getsource(NchantdFileDetailsPane.set_file_path)
    assert "self.refresh()" in src, (
        "set_file_path must call self.refresh() (T-NEW-038)"
    )


def test_refresh_calls_all_getters():
    """``refresh()`` must call each getter (size, hash, dates)."""
    from nchantdoffice.widgets.panes.files import NchantdFileDetailsPane
    src = inspect.getsource(NchantdFileDetailsPane.refresh)
    for getter in ("get_name", "get_file_path", "get_file_size",
                   "get_created_date", "get_access_date",
                   "get_modified_date", "get_hash"):
        assert getter in src, f"refresh() must call {getter} (T-NEW-038)"


def test_refresh_swallows_exception():
    """``refresh()`` must not raise on bad inputs."""
    from nchantdoffice.widgets.panes.files import NchantdFileDetailsPane
    pane = NchantdFileDetailsPane.__new__(NchantdFileDetailsPane)
    # All getters blow up
    pane.get_name = lambda: (_ for _ in ()).throw(RuntimeError("boom"))
    pane.get_file_path = lambda: (_ for _ in ()).throw(RuntimeError("boom"))
    pane.get_file_size = lambda: (_ for _ in ()).throw(RuntimeError("boom"))
    pane.get_created_date = lambda: (_ for _ in ()).throw(RuntimeError("boom"))
    pane.get_access_date = lambda: (_ for _ in ()).throw(RuntimeError("boom"))
    pane.get_modified_date = lambda: (_ for _ in ()).throw(RuntimeError("boom"))
    pane.get_hash = lambda: (_ for _ in ()).throw(RuntimeError("boom"))
    # Must not raise
    result = pane.refresh()
    assert result is pane


def test_set_file_path_with_real_file_updates_widgets():
    """End-to-end: set_file_path on a real file updates widget entries."""
    from nchantdoffice.widgets.panes.files import NchantdFileDetailsPane

    # Create a temp file with known content
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("test content for hash")
        tmp_path = f.name

    try:
        pane = NchantdFileDetailsPane.__new__(NchantdFileDetailsPane)

        # Mock the 7 entry widgets as SimpleNamespace with setText
        class _Entry:
            def __init__(self):
                self.text = ""
            def setText(self, t):
                self.text = str(t)

        pane.file_name_entry = _Entry()
        pane.file_path_entry = _Entry()
        pane.file_size_entry = _Entry()
        pane.creon_entry = _Entry()
        pane.accon_entry = _Entry()
        pane.modon_entry = _Entry()
        pane.hash_entry = _Entry()

        pane.set_file_path(tmp_path)

        # After set_file_path, all widgets should have refreshed
        assert pane.file_name_entry.text == Path(tmp_path).name
        assert str(pane.file_path_entry.text) == tmp_path
        assert int(pane.file_size_entry.text) > 0
        assert pane.modon_entry.text != "0"
        # hash may be empty if pycurity isn't installed, but the
        # widgets shouldn't crash
    finally:
        os.unlink(tmp_path)
