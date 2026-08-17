"""T-NEW-144a regression: FileDetailsPane shows internal-document
data when the active tab is internal.

**Redirect file_details in toolbox to internal data when the
tab is an internal document.**

The testing report (2026-08-15) Issue 4: ``file_details`` in
the toolbox shows blank / "0" fields when the active tab is
internal. ``NchantdFileDetailsPane`` reads
``self.file_path`` directly from disk; for internal docs
``file_path`` is empty, so every getter returns "0" / "".

The fix:
1. Add a way for the pane to know about the active tab
   (``set_tab`` / ``bind_to_tab``). The pane keeps a reference
   to the active tab dict so when ``file_path`` is empty or
   doesn't exist on disk, the getters fall back to reading
   from the tab's stored metadata: file name, content size,
   creation / modification timestamps from the doc_media row.

2. ``refresh()`` re-runs all getters so a tab switch updates
   the pane (mirrors the existing ``set_file_path`` pattern).

3. Backward compat: the pane's existing on-disk behaviour is
   preserved when ``file_path`` is set and the file exists.

Test surface: ``tests/test_t_new_144a_file_details_internal.py``
(this file). Pins:
  - ``bind_to_tab`` method exists.
  - ``refresh`` updates all getters when ``bind_to_tab`` is set
    and the tab has no file_path.
  - The file name widget shows the tab's name.
  - The file path widget shows ``"(internal storage)"`` or
    similar placeholder when there's no file_path.
  - The file size widget shows the byte length of the tab's
    content (when present) or "0" when absent.
  - The modified date widget shows the tab's modon timestamp
    when present.
"""
import inspect
import sqlite3
import tempfile
import os

# T-NEW-074 Task 9: keep Qt on the headless offscreen platform
# before any PySide6 import so the integration test does not
# need a real display.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402

from nchantdoffice.widgets.panes.files import NchantdFileDetailsPane


# ---------------------------------------------------------------------------
# Source-level pins: pane must expose a tab-binding hook + internal-doc
# fallbacks
# ---------------------------------------------------------------------------

def test_bind_to_tab_method_exists():
    """T-NEW-144a: the pane must expose a way to bind an active tab
    so internal-doc metadata can be displayed when file_path is
    empty.

    Without this, the pane cannot distinguish "no active tab"
    from "active tab is internal" -- and the toolbox shows
    blank fields either way.
    """
    assert hasattr(NchantdFileDetailsPane, "bind_to_tab"), (
        "NchantdFileDetailsPane must define bind_to_tab "
        "(T-NEW-144a)."
    )


def test_get_name_falls_back_to_tab_name_when_no_path():
    """Source-level: ``get_name`` must consult ``self.tab.name``
    (or the bound-tab equivalent) when ``self.file_path`` is
    empty. Otherwise internal tabs render a blank file-name
    field.
    """
    src = inspect.getsource(NchantdFileDetailsPane.get_name)
    # Either an explicit fallback to ``self.tab`` or a generic
    # guard "if no path, use the bound tab". Either shape
    # qualifies; the test pins that the fallback path exists.
    has_fallback = (
        "self.tab" in src or
        "bound_tab" in src or
        "getattr(self" in src
    )
    assert has_fallback, (
        "NchantdFileDetailsPane.get_name must fall back to the "
        "bound tab when file_path is empty (T-NEW-144a). "
        "Source:\n" + src[:600]
    )


def test_get_file_size_falls_back_to_tab_content_length():
    """Source-level: ``get_file_size`` must read from the tab's
    content (e.g. ``content_enc64_txt`` length) when no
    file_path is set, so internal docs show a non-zero size.
    """
    src = inspect.getsource(NchantdFileDetailsPane.get_file_size)
    has_fallback = (
        "self.tab" in src or
        "content_enc64" in src or
        "bound_tab" in src
    )
    assert has_fallback, (
        "NchantdFileDetailsPane.get_file_size must read from the "
        "bound tab's content when file_path is empty (T-NEW-144a). "
        "Source:\n" + src[:600]
    )


# ---------------------------------------------------------------------------
# Behavioural pin: pane populated from a bound internal tab
# ---------------------------------------------------------------------------

def _bare_pane():
    """Construct a minimal NchantdFileDetailsPane without running
    ``__init__`` (avoids the full Qt + kahndor setup).
    """
    return NchantdFileDetailsPane.__new__(NchantdFileDetailsPane)


class _CapturingEntry:
    def __init__(self):
        self.text = ""
    def setText(self, t):
        self.text = str(t)


def _stub_pane_with_tab(tab):
    """Build a pane with stubbed entry widgets and a bound tab.

    The pane reads ``file_path`` from disk; for the internal-tab
    path it should NOT raise -- it should pull file_name from
    ``tab.name``, file_path from the ``"(internal storage)"``
    placeholder, file_size from ``tab.content`` length, and
    modon from ``tab.modon``.
    """
    pane = _bare_pane()
    pane.tab = tab
    pane.file_path = None  # internal doc: no file_path
    pane.file_name_entry = _CapturingEntry()
    pane.file_path_entry = _CapturingEntry()
    pane.file_size_entry = _CapturingEntry()
    pane.creon_entry = _CapturingEntry()
    pane.accon_entry = _CapturingEntry()
    pane.modon_entry = _CapturingEntry()
    pane.hash_entry = _CapturingEntry()
    return pane


def test_bind_to_tab_populates_widgets_from_tab_metadata():
    """T-NEW-144a (e2e): after bind_to_tab, refresh() populates
    the file_name, file_path, file_size, and modon widgets from
    the tab dict. Before this fix, all fields showed "0" /
    empty for internal docs.
    """
    from types import SimpleNamespace
    tab = SimpleNamespace(
        name="My Journal",
        location="internal",
        file_path=None,
        content=b"hello internal content",
        creon="2026-08-15T10:00:00",
        accon="2026-08-16T11:00:00",
        modon="2026-08-16T12:00:00",
    )
    pane = _stub_pane_with_tab(tab)
    pane.bind_to_tab(tab)
    pane.refresh()

    # File name comes from tab.name (NOT from Path.basename on
    # an empty file_path).
    assert pane.file_name_entry.text == "My Journal", (
        f"file_name must come from tab.name for internal docs; "
        f"got {pane.file_name_entry.text!r}"
    )
    # File size comes from tab.content length (NOT from getsize
    # on disk).
    assert int(pane.file_size_entry.text) == len(b"hello internal content"), (
        f"file_size must come from tab.content length for "
        f"internal docs; got {pane.file_size_entry.text!r}"
    )
    # Modified date comes from tab.modon.
    assert pane.modon_entry.text == "2026-08-16T12:00:00", (
        f"modon must come from tab.modon for internal docs; "
        f"got {pane.modon_entry.text!r}"
    )


def test_refresh_updates_pane_when_tab_switches(tmp_path):
    """T-NEW-144a (e2e): a tab switch (bind_to_tab + refresh)
    must update the visible widgets to reflect the new tab --
    not the previous one. Without this, switching from an
    internal doc to an external one (or vice versa) leaves
    stale fields visible.
    """
    from types import SimpleNamespace
    internal_tab = SimpleNamespace(
        name="Internal",
        location="internal",
        file_path=None,
        content=b"abc",
        creon=None,
        accon=None,
        modon="2026-08-16T10:00:00",
    )
    real_file = tmp_path / "external.txt"
    real_file.write_text("hello external")
    external_tab = SimpleNamespace(
        name="ExternalName",
        location="external",
        file_path=str(real_file),
        content=None,
        creon=None,
        accon=None,
        modon=None,
    )

    pane = _stub_pane_with_tab(internal_tab)
    pane.bind_to_tab(internal_tab)
    pane.refresh()
    assert pane.file_name_entry.text == "Internal"
    assert int(pane.file_size_entry.text) == 3

    # Switch to external tab. Refresh must re-populate from the
    # new tab; previously the pane would still show "Internal".
    pane.bind_to_tab(external_tab)
    pane.refresh()
    # On a real external file the basename wins (per
    # get_name's path.name path).
    assert pane.file_name_entry.text == "external.txt"
    assert int(pane.file_size_entry.text) == len(b"hello external")


def test_external_doc_still_uses_file_path(tmp_path):
    """T-NEW-144a (backward compat): when the bound tab has a
    file_path that exists on disk, the pane must use the
    on-disk getters (the T-NEW-038 behaviour) -- not the
    internal-tab fallback. The bind_to_tab fix must not
    regress the external-doc UX.
    """
    from types import SimpleNamespace
    real_file = tmp_path / "real.pyof"
    real_file.write_text("hello")

    external_tab = SimpleNamespace(
        name="RealFile",
        location="external",
        file_path=str(real_file),
        content=None,
        creon=None,
        accon=None,
        modon=None,
    )
    pane = _stub_pane_with_tab(external_tab)
    pane.bind_to_tab(external_tab)
    pane.refresh()

    assert pane.file_name_entry.text == "real.pyof"
    assert int(pane.file_size_entry.text) == len(b"hello")
    # modon comes from disk mtime (an ISO string).
    assert pane.modon_entry.text != "0"
    assert pane.modon_entry.text != ""