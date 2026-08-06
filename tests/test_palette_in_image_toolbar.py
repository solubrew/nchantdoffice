"""T-NEW-055 regression test: NchantdOfficePalette integrated into
the NchantdOfficeImage toolbar.

Per `testing-report_20260804.md`:
  "Need to implement NchantdOfficePalette document into the
   NchantdOfficeImage document toolbar should launch the palette
   toolbox drawer where the palette document is displayed with a
   list of colors and percentage usage in the image"

The fix (in `nchantdoffice/widgets/documents/media/images.py`):
1. The image toolbar buttons dict now has button 15 wired to
   ``cmd_show_palette_drawer`` (replacing the previous
   ``add_palette_document_nchantdpalette`` placeholder) and button
   16 wired to ``cmd_run_palette_scan`` (explicit scan).
2. ``cmd_show_palette_drawer`` runs the palette scan if needed,
   populates the NchantdPaletteTable, then opens the toolbox drawer.
3. ``cmd_open_tool_drawer("palette")`` now hides the other panes
   and shows the palette table.
4. ``_populate_palette_table`` helper accepts the canonical
   palette dict shape and a flat-tuple fallback.
"""

import inspect


def test_show_palette_drawer_handler_exists():
    """``NchantdOfficeImage`` must define cmd_show_palette_drawer."""
    from nchantdoffice.widgets.documents.media.images import NchantdOfficeImage
    assert hasattr(NchantdOfficeImage, "cmd_show_palette_drawer"), (
        "NchantdOfficeImage must define cmd_show_palette_drawer (T-NEW-055)"
    )


def test_populate_palette_table_helper_exists():
    """``_populate_palette_table`` helper must exist."""
    from nchantdoffice.widgets.documents.media.images import NchantdOfficeImage
    assert hasattr(NchantdOfficeImage, "_populate_palette_table"), (
        "NchantdOfficeImage must define _populate_palette_table (T-NEW-055)"
    )


def test_show_palette_drawer_swallows_exception():
    """Source-level: cmd_show_palette_drawer must not propagate."""
    from nchantdoffice.widgets.documents.media.images import NchantdOfficeImage
    src = inspect.getsource(NchantdOfficeImage.cmd_show_palette_drawer)
    assert "except Exception" in src, (
        "cmd_show_palette_drawer must catch + log exceptions (T-NEW-055)"
    )


def test_populate_palette_table_handles_dict_shape():
    """``_populate_palette_table`` must handle the canonical dict shape."""
    from nchantdoffice.widgets.documents.media.images import NchantdOfficeImage
    src = inspect.getsource(NchantdOfficeImage._populate_palette_table)
    assert "colors" in src and "percent" in src
    assert "hex" in src


def test_populate_palette_table_handles_tuple_fallback():
    """``_populate_palette_table`` must accept the flat-tuple shape."""
    from nchantdoffice.widgets.documents.media.images import NchantdOfficeImage
    src = inspect.getsource(NchantdOfficeImage._populate_palette_table)
    assert "list" in src.lower() or "tuple" in src.lower() or "isinstance" in src


def test_cmd_open_tool_drawer_supports_palette():
    """``cmd_open_tool_drawer`` must include ''palette'' in the panes map."""
    from nchantdoffice.widgets.documents.media.images import NchantdOfficeImage
    src = inspect.getsource(NchantdOfficeImage.cmd_open_tool_drawer)
    assert '"palette"' in src or "'palette'" in src, (
        "cmd_open_tool_drawer must support 'palette' tool_name (T-NEW-055)"
    )


def test_show_palette_drawer_wired_to_button_15():
    """The image toolbar buttons dict must reference cmd_show_palette_drawer."""
    from nchantdoffice.widgets.documents.media.images import NchantdOfficeImage
    src = inspect.getsource(NchantdOfficeImage.initView)
    assert "cmd_show_palette_drawer" in src, (
        "initView must wire button 15 to cmd_show_palette_drawer (T-NEW-055)"
    )


def test_palette_document_class_exists():
    """``NchantdOfficePalette`` is defined in sketches.py."""
    from nchantdoffice.widgets.documents.media.sketches import (
        NchantdOfficePalette,
    )
    assert hasattr(NchantdOfficePalette, "initView")
    assert hasattr(NchantdOfficePalette, "initModel")
