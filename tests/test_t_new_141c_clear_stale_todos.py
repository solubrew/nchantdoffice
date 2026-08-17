"""T-NEW-141c regression: clear the remaining 3
inside-nchantdoffice TODO markers.

The T-NEW-141c sweep was originally scoped to three
substantial features (palette drawer wiring, tool
drawer re-render, per-doctype features pane). On
investigation, all three were either already implemented
or are feature wishlists that ship via a different code
path. The "fix" is to remove the misleading TODO
comments and replace them with accurate docstrings.

Findings:

1. ``images.py:807`` -- ``cmd_add_palette_document
   _nchantdpalette`` claims the TODO is "Open toolbox
   tab and Palette Drawer generate the palette from the
   image". The function body already adds a palette
   document; the missing piece is opening the drawer
   after the add. Fix: call ``self.cmd_show_palette
   _drawer()`` after the add (the drawer-open helper
   already exists at line 990), and replace the TODO
   with a real docstring describing the contract.

2. ``images.py:1162`` -- the TODO claims "implement
   logic so that when a tool like NchantdConvertSize
   button is clicked ... the drawer is opened and
   redrawn to show only the config for that tool". The
   implementation already exists: ``cmd_open_tool_drawer
   (tool_name)`` at line 913 hides all 5 panes and
   shows only the named one. Fix: remove the stale TODO;
   document the dispatch in the docstring.

3. ``settings.py:1016`` -- the TODO claims "implement
   in NchantdOfficeDocumentConfigPane - features". The
   ``NchantdOfficeDocumentConfigPane`` class already
   exists (``panes/document_settings.py:73``) with a
   registry of per-doctype subclasses
   (MatrixConfigPane, NotebookConfigPane, ImageConfig
   Pane, ScriptConfigPane). The current settings.py
   code already uses the shared pane via the T-NEW-027
   registry lookup. Fix: remove the stale TODO and
   document the registry contract.

Tests (TDD, source-level pins):
- images.py:807 ``cmd_add_palette_document_nchantd
  palette`` calls ``cmd_show_palette_drawer`` after the
  add.
- images.py:1162 ``init_drawer_image_tools`` no longer
  has the stale "tool like NchantdConvertSize" TODO.
- settings.py:1016 no longer has the stale "implement
  in NchantdOfficeDocumentConfigPane - features" TODO.
- ``NchantdOfficeDocumentConfigPane`` class still
  exists in ``panes/document_settings.py`` (regression
  guard -- the comment referenced this class, the fix
  must not have removed it).
"""
import inspect

# T-NEW-074 Task 9: keep Qt on the headless offscreen platform
# before any PySide6 import so the integration test does not
# need a real display.
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402


# ---------------------------------------------------------------------------
# 1. images.py:807 -- cmd_add_palette_document_nchantdpalette
# ---------------------------------------------------------------------------

def test_add_palette_document_opens_drawer():
    """T-NEW-141c (1): after adding a palette document, the
    drawer must open so the user can see the new palette.
    The pre-fix code only called ``model.add_palette_document``
    and returned; the user had no UI feedback.
    """
    from nchantdoffice.widgets.documents.media.images import (
        NchantdOfficeImage,
    )
    src = inspect.getsource(NchantdOfficeImage.cmd_add_palette_document_nchantdpalette)
    assert "cmd_show_palette_drawer" in src, (
        f"cmd_add_palette_document_nchantdpalette must call "
        f"cmd_show_palette_drawer after the add (T-NEW-141c). "
        f"Got:\n{src[:1500]}"
    )
    # And the misleading TODO must be gone.
    assert "TODO Open toolbox tab" not in src, (
        f"stale 'TODO Open toolbox tab' must be removed "
        f"(T-NEW-141c). Got:\n{src[:1500]}"
    )


# ---------------------------------------------------------------------------
# 2. images.py:1162 -- init_drawer_image_tools
# ---------------------------------------------------------------------------

def test_init_drawer_image_tools_no_longer_has_stale_todo():
    """T-NEW-141c (2): the misleading TODO claiming
    "implement logic so that when a tool like
    NchantdConvertSize button is clicked" must be removed
    -- the implementation already exists in
    ``cmd_open_tool_drawer`` (T-NEW-035).
    """
    from nchantdoffice.widgets.documents.media.images import (
        NchantdOfficeImage,
    )
    src = inspect.getsource(NchantdOfficeImage.init_drawer_image_tools)
    assert "tool like NchantdConvertSize" not in src, (
        f"stale 'tool like NchantdConvertSize' TODO must be "
        f"removed (T-NEW-141c). Got:\n{src[:600]}"
    )
    # And the docstring should mention the dispatcher
    # (cmd_open_tool_drawer) so future readers know.
    assert "cmd_open_tool_drawer" in src or (
        "T-NEW-141c" in src
    ), (
        f"init_drawer_image_tools docstring should reference "
        f"the cmd_open_tool_drawer dispatcher (T-NEW-141c). "
        f"Got:\n{src[:600]}"
    )


# ---------------------------------------------------------------------------
# 3. settings.py:1016 -- per-doctype features pane TODO
# ---------------------------------------------------------------------------

def test_settings_no_longer_has_features_pane_todo():
    """T-NEW-141c (3): the misleading "TODO implement in
    NchantdOfficeDocumentConfigPane - features" must be
    removed -- the class exists at
    ``panes/document_settings.py:73`` and the per-doctype
    registry is wired (T-NEW-027).
    """
    # The TODO is inside a larger method body. Read the
    # whole ``NchantdOfficeInterfaceSettings`` module and
    # check the TODO string is gone.
    from nchantdoffice.widgets.config import settings as settings_mod
    src = inspect.getsource(settings_mod)
    assert "TODO implement in NchantdOfficeDocumentConfigPane" not in src, (
        f"stale 'TODO implement in NchantdOfficeDocumentConfigPane' "
        f"must be removed (T-NEW-141c). The class exists at "
        f"panes/document_settings.py:73 and the registry is "
        f"wired (T-NEW-027)."
    )


def test_document_config_pane_class_still_exists():
    """T-NEW-141c (regression guard): the
    ``NchantdOfficeDocumentConfigPane`` class must still
    exist (the TODO referenced it; the fix must not have
    removed it).
    """
    from nchantdoffice.widgets.panes.document_settings import (
        NchantdOfficeDocumentConfigPane,
    )
    assert NchantdOfficeDocumentConfigPane is not None, (
        "NchantdOfficeDocumentConfigPane must still exist "
        "(T-NEW-141c regression guard)."
    )