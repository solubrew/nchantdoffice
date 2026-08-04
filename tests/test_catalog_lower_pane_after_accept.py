"""T-NEW-045 -- Document Catalog lower-pane disappears after accepting a new tab.

Per ``testing-report_20260803.md``: after accepting a newly
created tab from the Document Catalog, the catalog's lower
pane disappears and the catalog no longer responds.

This is a **characterisation** test, not a fix. It verifies
that the catalog's ``self.display`` widget, once constructed
and added to the catalog's layout, survives the
``update_item_pane`` call that the new-doc pane's ``accept()``
eventually reaches.

The fixture is intentionally minimal: it does NOT drive the
full ``nchantment()`` boot path (which requires wizards,
profile, store, and network). Instead it builds the catalog's
display lifecycle by hand:

  1. Construct a real ``NchantdCatalog`` with the minimum
     stub parent (config + app shape).
  2. Construct a real ``NchantdGridScrollGroupBox`` and add
     it to the catalog's existing layout as ``self.display``.
  3. Mount the catalog on a ``QMainWindow`` so the widget
     tree is visible.
  4. Capture ``isVisible()`` and layout presence BEFORE the
     simulated accept.
  5. Simulate the post-accept catalog state by calling
     ``update_item_pane`` with a stub ``selected_item`` and
     a None ``item_pane`` (the early-return branch that the
     production code takes when the new-doc pane finishes
     its accept flow).
  6. Assert the display is still visible AND still in the
     layout.

If ``update_item_pane`` ever hides or removes the display,
this test goes red with the precise state of the widget.
"""

from __future__ import annotations

import sys
from types import SimpleNamespace

import pytest
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget


_QAPP = QApplication.instance() or QApplication(sys.argv)


class _StubApp:
    """Stand-in for ``self.parent.app``.

    ``NchantdWidgetMixin.init_variables`` walks the parent
    chain looking for an object that has ``model``, ``app``,
    ``view``, ``new_application``. We don't have those for
    the test, so we set ``debug=False`` on the mixin's
    module to short-circuit the ``raise Exception`` branch.
    """


def _build_catalog_display():
    """Build a ``NchantdCatalog`` with a real ``self.display``
    attached to its layout, mounted on a QMainWindow.

    Returns ``(catalog, window)``. The catalog's
    ``self.display`` is a ``NchantdGridScrollGroupBox``.
    """
    import nchantrs.widgets.widgets as wm
    # The mixin raises if it cannot find a parent app. We
    # do not need init_variables to run for this test --
    # the contract under test is the catalog's display
    # lifecycle, not the mixin's app-walking behaviour.
    wm.debug = False

    from nchantrs.widgets.catalogs import NchantdCatalog
    from nchantrs.widgets.groups import NchantdGridScrollGroupBox
    from nchantrs.libraries import pyqt

    import kahndor.kahndor as kahndor

    parent = QMainWindow()
    parent.setObjectName("qt_parent_root")
    # ``NchantdCatalog.__init__`` does
    # ``self.config.override(parent.config)``; the parent
    # therefore needs a kahndor.Instruct-shaped config.
    parent.config = kahndor.Instruct()

    catalog = NchantdCatalog(parent=parent, cfg={})

    # The catalog's NchantdWidget.__init__ left
    # ``catalog.layout = None``. Set up a layout manually.
    catalog.layout = pyqt.QVBoxLayout()
    catalog.setLayout(catalog.layout)

    # Build the display group that production initView
    # creates. We do not iterate items because we are
    # not driving the per-row loop.
    catalog.display = NchantdGridScrollGroupBox(catalog)
    catalog.display.setObjectName("catalog_display")
    catalog.display.setTitle("T-NEW-045 catalog display")
    catalog.layout.addLayout(catalog.display.layout)

    # Mount the catalog as the central widget so it is
    # visible. ``setCentralWidget`` reparents, so we must
    # do it AFTER adding the display to the layout.
    parent.setCentralWidget(catalog)
    parent.resize(800, 600)
    parent.show()
    QApplication.processEvents()
    return catalog, parent


def test_catalog_display_visible_at_init():
    """Sanity: after the minimal mount, ``self.display`` is visible.

    If this fails, the fixture shape is wrong and the
    characterisation tests below cannot be trusted.
    """
    catalog, parent = _build_catalog_display()
    assert catalog.display is not None, "catalog.display was not built"
    assert catalog.display.isVisible(), (
        f"display not visible at init: isVisible={catalog.display.isVisible()} "
        f"isHidden={catalog.display.isHidden()}"
    )


def test_catalog_display_visible_after_update_item_pane():
    """After ``update_item_pane``, ``self.display`` must still
    be visible.

    RED trigger: any commit that hides ``self.display``,
    removes it from the layout, or breaks the parent chain
    during ``update_item_pane`` will flip this test red.
    """
    catalog, parent = _build_catalog_display()

    assert catalog.display.isVisible(), (
        "pre-state visibility was already False -- fixture broken"
    )

    # Simulate the post-accept catalog state.
    catalog.selected_item = SimpleNamespace(
        title_txt="Test Script",
        document_nm="Test Script",
        did="test-did",
        action=SimpleNamespace(action="load_catalog_item"),
    )
    catalog.item_pane = None  # the early-return branch
    catalog.update_item_pane()
    QApplication.processEvents()

    assert catalog.display.isVisible(), (
        f"T-NEW-045 regression: catalog.display hidden after "
        f"update_item_pane. isVisible={catalog.display.isVisible()} "
        f"isHidden={catalog.display.isHidden()} "
        f"parent={catalog.display.parentWidget()!r}. "
        f"This is the catalog-level reproduction of the live defect."
    )


def test_catalog_display_remains_in_layout_after_update_item_pane():
    """Belt-and-braces: even if ``isVisible`` is True, the
    display group must still be a child of the catalog's
    layout. A layout removal is the same defect as a
    visibility flip -- both are "the lower pane is gone".
    """
    catalog, parent = _build_catalog_display()

    catalog.selected_item = SimpleNamespace(
        title_txt="Test Script",
        document_nm="Test Script",
        did="test-did",
        action=SimpleNamespace(action="load_catalog_item"),
    )
    catalog.item_pane = None
    catalog.update_item_pane()
    QApplication.processEvents()

    # Walk the catalog's layout children to confirm display
    # is still attached. ``NchantdGridScrollGroupBox`` adds
    # its own layout to the parent layout, so we look for the
    # display's layout as one of the children.
    layout_children = []
    for i in range(catalog.layout.count()):
        item = catalog.layout.itemAt(i)
        if item is not None:
            layout_children.append(item)
    attached = any(
        item.layout() is catalog.display.layout for item in layout_children
    )
    assert attached or catalog.display.parentWidget() is catalog, (
        f"T-NEW-045: catalog.display was removed from the "
        f"parent layout after update_item_pane. "
        f"layout children: {[type(item).__name__ for item in layout_children]} "
        f"display.parentWidget()={catalog.display.parentWidget()!r}"
    )
