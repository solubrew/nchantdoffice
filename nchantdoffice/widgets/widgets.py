# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
        docid:
        name:
        description: >
        version: 0.0.0.0.0.0
        authority: filesystem
        security: seclvl2
        <(WT)>: -32
"""

# -*- coding: utf-8 -*-
from __future__ import annotations

# ======================================Standard Library Modules======================================================|
from os.path import abspath, dirname, join
import datetime as dt

# ======================================3rd Party Library Modules======================================================|
from kahndor import kahndor
from kahndor.logma import Logma
from nchantrs.libraries import pyqt
from nchantrs.widgets.tabsets import NchantdTabSet
from nchantrs.libraries.pyqt import QTimer
from nchantdoffice.models import NchantdOfficeTabSetModel
from nchantdoffice.widgets.controls.toolboxes import NchantdOfficeApplicationToolBox
from nchantdoffice.widgets.controls.floated_tab import FloatedTab
from nchantdoffice.nchantdoffice import NchantdDocumentStandaloneWindow
from typing import Any, Self

# from nchantdoffice.widgets.documents.media.notes import NchantdOfficeNote

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = False
logma = Logma(__name__)
if not log:
    logma.off()
# ====================================================================================================================||
pxcfg = join(here, "_data_", "widgets.yaml")


class NchantdOfficeTabSet(NchantdTabSet):
    """"""

    def __init__(self, parent=None, cfg=None) -> None:
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeTabSet").override(cfg))
        self.model = NchantdOfficeTabSetModel(self, self.config)

    def initModel(self, create_objects=True) -> Self:
        """ """
        super().initModel(create_objects)
        return self

    def initView(self) -> Self:
        """Wire the tabset UI.

        T-NEW-170 WIRE-4: also call ``_wire_pop_out_triggers``
        so the right-click menu + toolbar 'detach tab' trigger
        come up alongside the rest of the tabset.
        """
        super().initView()
        try:
            self._wire_pop_out_triggers()
        except Exception as e:
            logma.warning(
                f"[NchantdOfficeTabSet.initView] "
                f"_wire_pop_out_triggers failed (non-blocking): "
                f"{e!r}"
            )
        return self

    def initWidget(self, cfg=None) -> Self:
        """ """
        if cfg is None:
            cfg = {}
        self.initModel(cfg.get("create_objects", True))
        self.initView()
        return self

    # PUSH to 0.0.3
    # def launch_note(self, cfg=None):
    #     """"""
    #     if cfg is None:
    #         cfg = {}
    #     # NOTE: launch_note is temporarily disabled. Was causing Note object
    #     # failures. The Note widget path needs a full review before re-enabling.
    #     # note = NchantdOfficeNote(self.app.main, cfg).initWidget()
    #     note = NchantdOfficeNote(self, cfg).initWidget()
    #     self.app.view.panes["center"].model.current_tab.append_note(note)
    #     return self

    def create_toolbox(self, parent=None, cfg=None) -> NchantdOfficeApplicationToolBox:
        """ """
        toolbox = NchantdOfficeApplicationToolBox(parent, cfg)
        toolbox.initWidget()
        return toolbox

    def _find_right_toolbox(self) -> NchantdOfficeApplicationToolBox | None:
        """Return the live (materialized) toolbox widget in the right pane, or None.

        The visible toolbox is a right-pane tab whose widget is a
        NchantdOfficeApplicationToolBox. Prefer the app-level reference
        (``self.app.toolbox``, set by nchantrs.load_tab when a tab is named
        "ToolBox"), but fall back to scanning the right pane's materialized tab
        widgets by capability -- these office tabs are not necessarily named
        "ToolBox", and non-active tabs are lazy ``dummy`` placeholders that cannot
        be refreshed (they build correctly on their own first focus).
        """
        toolbox = getattr(self.app, "toolbox", None)
        if toolbox is not None and hasattr(toolbox, "refresh_for_document"):
            return toolbox
        right_pane = self.app.view.panes.get("right")
        model = getattr(right_pane, "model", None)
        for candidate in getattr(model, "tab_widgets", []) or []:
            if getattr(candidate, "dummy", False):
                continue
            if hasattr(candidate, "refresh_for_document") and hasattr(candidate, "build_toolbox"):
                return candidate
        return None

    def go_to_previous_tab(self) -> None:
        """T-NEW-141: move focus to the previous tab in the
        current tabset. Called by ``cmd_delete_tab`` after a
        tab is removed; without this, focus stays on the
        now-deleted index (Qt renders an empty pane). Clamps
        at index 0 so deleting at index 0 is a no-op rather
        than an IndexError."""
        try:
            current = self.app.view.panes["center"].currentIndex()
        except Exception:
            return
        try:
            self.app.view.panes["center"].setCurrentIndex(max(0, current - 1))
        except Exception:
            pass

    def pop_out_tab(self, tab_index: int) -> FloatedTab:
        """T-NEW-170 WIRE-2 -- detach the tab at `tab_index` into
        a FloatedTab dialog.

        The operator right-clicks a tab (or clicks the toolbar
        `↗` button -- T-NEW-170 WIRE-4) → pop_out_tab fires →
        the tab is detached into a FloatedTab dialog (T-NEW-170
        WIRE-1, the QDialog subclass) wrapping a
        NchantdDocumentStandaloneWindow (T-NEW-169 WIRE-2, the
        QMainWindow 2-pane shell) → the dialog is shown.

        LOCKED DESIGN (operator-approved 2026-08-19):
          DECIDE-1 (a) — re-attach only on dialog close / app
            close. pop_out_tab does NOT register any
            node-change hook that would re-attach on
            navigation events; the tab stays detached for
            the entire dialog lifetime.
          DECIDE-2 (ii) — full standalone 2-pane shell that
            reuses the T-NEW-169 standalone window. The
            FloatedTab dialog composes the standalone
            window as its body.

        What pop_out_tab does:
          1. Reads the document widget from the center pane
             at `tab_index`.
          2. Reads the home node id from the model (or a
             sensible default if the model doesn't expose one).
          3. Records home_node_id, home_position, home_tabset
             so re_attach_tab can put the tab back later.
          4. Constructs a NchantdDocumentStandaloneWindow with
             the document widget + type + path.
          5. Constructs a FloatedTab dialog wrapping the
             standalone window + the home coordinates.
          6. Shows the dialog.
          7. Removes the tab from the center pane (it now
             lives in the dialog).

        Returns the FloatedTab instance so callers can keep
        a reference if they want to.

        Failure modes:
          - tab_index out of bounds → returns None, logs a
            warning, does NOT show a dialog.
          - widget at index has no `.open_file()` and no
            standalone-shell support → best-effort: wraps
            the bare widget in a generic placeholder.
        """
        try:
            center = self.app.view.panes["center"]
            document_widget = center.widget(tab_index)
        except Exception as e:
            logma.warning(
                f"[pop_out_tab] could not read widget at "
                f"index {tab_index}: {e!r}"
            )
            return None  # type: ignore[return-value]
        if document_widget is None:
            logma.warning(
                f"[pop_out_tab] no widget at index {tab_index}"
            )
            return None  # type: ignore[return-value]

        # T-NEW-170 WIRE-2: home coordinates for re-attach.
        # The center tabset is `center` itself; the home
        # position is the supplied tab_index; the home node
        # id is read from the model (best-effort — fall back
        # to a stringly-typed sentinel if the model doesn't
        # expose `current_node.nid`).
        home_tabset = center
        home_position = tab_index
        try:
            home_node_id = (
                self.app.model.current_node.nid  # type: ignore[attr-defined]
                if self.app.model.current_node is not None
                else "unknown-node"
            )
        except Exception:
            home_node_id = "unknown-node"

        # T-NEW-170 WIRE-2: dispatch the document_type for
        # the standalone shell. Read the dispatched type
        # from the document widget's own name or default to
        # "script". The standalone window's
        # DOCUMENT_TYPE_DISPATCH applies downstream.
        document_type = (
            getattr(document_widget, "PYTYPE", None) or "script"
        )

        # T-NEW-170 WIRE-2: construct the standalone shell
        # (T-NEW-169 WIRE-2) wrapping the document widget.
        # Per DECIDE-2 (ii), the body of the FloatedTab is
        # the full 2-pane shell, not a minimal stripped-down
        # editor.
        standalone_window = NchantdDocumentStandaloneWindow(
            parent=None,
            document_type=document_type,
            preload_path=getattr(document_widget, "file_path", None),
        )
        # T-NEW-170 WIRE-2: after the constructor the
        # standalone window's initView builds a placeholder
        # central widget (since we don't pass a real document
        # type lookup). For the pop-out use case we want the
        # REAL document_widget rendered. Swap the central
        # widget to the actual document — best-effort,
        # silently fall back if not possible.
        try:
            if hasattr(standalone_window, "setCentralWidget"):
                standalone_window.setCentralWidget(document_widget)
        except Exception as e:
            logma.warning(
                f"[pop_out_tab] setCentralWidget swap failed: {e!r}"
            )

        # T-NEW-170 WIRE-2: construct the FloatedTab dialog
        # (T-NEW-170 WIRE-1) wrapping the standalone window
        # + the home coordinates. The dialog's
        # closeEvent will read those coordinates and call
        # `home_tabset.re_attach_tab(self)` (T-NEW-170
        # WIRE-3, the next commit).
        floated_tab = FloatedTab(
            parent=self,
            standalone_window=standalone_window,
            document_widget=document_widget,
            home_node_id=home_node_id,
            home_position=home_position,
            home_tabset=home_tabset,
        )

        # T-NEW-170 WIRE-2: remove the original tab from the
        # center pane. The tab now lives in the FloatedTab
        # dialog; showing it again in the tabset would
        # double-display.
        try:
            center.removeTab(tab_index)
        except Exception as e:
            logma.warning(
                f"[pop_out_tab] center.removeTab({tab_index}) "
                f"failed: {e!r}"
            )

        # T-NEW-170 WIRE-2: show the dialog. FloatedTab
        # inherits QDialog's show() method.
        floated_tab.show()
        logma.info(
            f"[pop_out_tab] detached tab {tab_index} ({document_type}) "
            f"to standalone dialog"
        )
        return floated_tab

    def _wire_pop_out_triggers(self) -> None:
        """T-NEW-170 WIRE-4 -- install the operator triggers
        that fire ``pop_out_tab``.

        Two trigger surfaces:

        1. **Right-click context menu** on a tab. The QTabBar
           exposes ``tab_bar`` after the tabset is
           constructed (we rely on Qt's tab-bar default).
           Right-clicking builds a small ``QMenu`` whose
           'Detach to window' action calls
           ``self.pop_out_tab(indexAt(event.pos()))``.

        2. **Toolbar 'detach tab' button**. The toolbar
           mirrors the right-click action. When triggered
           we call ``self.pop_out_tab(currentIndex())`` so
           the operator gets the same detach UX whether
           they right-click or click the toolbar button.

        Best-effort: if a trigger surface is missing (e.g.
        in a stripped-down test environment) the helper
        logs the absence and moves on. The T-NEW-170
        feature is still reachable via the direct API.

        LOCKED DESIGN:
          DECIDE-1 (a) -- the wire helper has NO node-change
            hook. The tab stays detached for the entire
            dialog lifetime; re-attach only on close.
        """
        try:
            # --- Right-click context menu on the tab bar ---
            tab_bar = getattr(self, "tabBar", lambda: None)()
            if tab_bar is not None and hasattr(
                tab_bar, "setContextMenuPolicy"
            ):
                try:
                    tab_bar.setContextMenuPolicy(
                        pyqt.Qt.CustomContextMenu
                    )
                except Exception:
                    # Some Qt bindings need the module-level
                    # Qt enum; fall back to the integer value
                    # (Qt.CustomContextMenu = 3).
                    try:
                        tab_bar.setContextMenuPolicy(3)
                    except Exception as _inner:
                        logma.warning(
                            f"[_wire_pop_out_triggers] "
                            f"setContextMenuPolicy failed: {_inner!r}"
                        )

                def _show_pop_out_menu(pos):
                    try:
                        index = tab_bar.tabAt(pos)
                        if index < 0:
                            return
                        try:
                            menu = pyqt.QMenu(tab_bar)
                        except Exception:
                            return
                        try:
                            action = menu.addAction("Detach to window")
                        except Exception:
                            return
                        try:
                            triggered = menu.exec_(
                                tab_bar.mapToGlobal(pos)
                            )
                        except Exception:
                            triggered = None
                        if triggered is not None:
                            self.pop_out_tab(index)
                    except Exception as e:
                        logma.warning(
                            f"[_wire_pop_out_triggers] "
                            f"right-click handler failed: {e!r}"
                        )

                try:
                    tab_bar.customContextMenuRequested.connect(
                        _show_pop_out_menu
                    )
                except Exception as e:
                    logma.warning(
                        f"[_wire_pop_out_triggers] "
                        f"customContextMenuRequested.connect "
                        f"failed: {e!r}"
                    )
            else:
                logma.info(
                    "[_wire_pop_out_triggers] no QTabBar available; "
                    "right-click trigger skipped (toolbar trigger "
                    "still operational)"
                )
        except Exception as e:
            logma.warning(
                f"[_wire_pop_out_triggers] right-click setup "
                f"failed (best-effort): {e!r}"
            )

        try:
            # --- Toolbar 'detach tab' button ---
            # The toolbar comes from the app's main window's
            # toolbars collection. Read it best-effort via
            # the app.view.panes["center"] / app.toolbar
            # access paths the rest of the codebase uses.
            toolbar = None
            try:
                toolbar = getattr(self.app, "toolbar", None)
            except Exception:
                toolbar = None
            if toolbar is None:
                # Last-ditch: look for an `app.toolbars` attr.
                toolbars = getattr(self.app, "toolbars", None)
                if toolbars:
                    toolbar = next(iter(toolbars), None)
            if toolbar is None:
                logma.info(
                    "[_wire_pop_out_triggers] no toolbar available; "
                    "toolbar trigger skipped"
                )
                return

            try:
                detach_action = pyqt.QAction("\u2197", toolbar)
            except Exception:
                detach_action = None
            if detach_action is None:
                return
            try:
                detach_action.setToolTip(
                    "Detach the current tab to a separate dialog"
                )
                detach_action.setStatusTip(
                    "Pop out the current tab into a standalone window"
                )
            except Exception:
                pass

            def _on_detach_clicked():
                try:
                    self.pop_out_tab(self.currentIndex())
                except Exception as e:
                    logma.warning(
                        f"[_wire_pop_out_triggers] "
                        f"toolbar detach click failed: {e!r}"
                    )

            try:
                detach_action.triggered.connect(_on_detach_clicked)
                toolbar.addAction(detach_action)
            except Exception as e:
                logma.warning(
                    f"[_wire_pop_out_triggers] toolbar addAction "
                    f"failed: {e!r}"
                )
        except Exception as e:
            logma.warning(
                f"[_wire_pop_out_triggers] toolbar setup "
                f"failed (best-effort): {e!r}"
            )

    def re_attach_tab(self, floated_tab) -> None:
        """T-NEW-170 WIRE-3 -- re-attach a FloatedTab to its
        home tabset at its home position.

        Called by ``FloatedTab.closeEvent`` (T-NEW-170 WIRE-1).
        The dialog carries the home coordinates
        (`home_node_id`, `home_position`, `home_tabset`) and
        the `document_widget` to be re-parented. ``re_attach_tab``
        reads those values, calls ``insertTab(home_position,
        document_widget)`` on the center tabset, and logs the
        re-attach.

        Best-effort: any Qt re-insert failure (the model is
        gone, the widget is already mounted, etc.) is logged
        and swallowed. The dialog's closeEvent must not raise
        an unhandled exception -- Qt treats that as a Qt
        crash.

        LOCKED DESIGN (operator-approved 2026-08-19):
          DECIDE-1 (a) -- re-attach only on dialog close /
            app close. This is the canonical receiver for the
            dialog-close path; the app-quit path (T-NEW-170
            WIRE-5) re-uses this same method via the
            ``aboutToQuit`` signal.
        """
        try:
            home_position = getattr(floated_tab, "home_position", None)
            document_widget = getattr(
                floated_tab, "document_widget", None
            )
            if home_position is None or document_widget is None:
                logma.warning(
                    f"[re_attach_tab] missing home_position or "
                    f"document_widget on floated_tab; skipping"
                )
                return
            try:
                self.app.view.panes["center"].insertTab(
                    home_position, document_widget
                )
                # T-NEW-170 WIRE-3: select the freshly
                # re-attached tab so the operator lands
                # where they expect.
                self.app.view.panes["center"].setCurrentIndex(
                    home_position
                )
            except Exception as e:
                logma.warning(
                    f"[re_attach_tab] insertTab({home_position}, "
                    f"...) failed: {e!r}; tab left orphaned"
                )
                return
            logma.info(
                f"[re_attach_tab] re-attached document to "
                f"position {home_position}"
            )
        except Exception as e:
            logma.warning(
                f"[re_attach_tab] top-level failure (swallowed): "
                f"{e!r}"
            )

    def setTabText(self, position, text, store=True) -> None:
        """ """
        super().setTabText(position, text)
        if store:
            cfg = {"name_txt": text}
            self.app.model.update_tab(self.app.model.get_current_tab(), cfg)

    def on_tab_focus(self, tabn=None) -> Self:
        """"""
        # logma.inspect_caller()
        if tabn is None:
            tabn = self.currentIndex()

        logma.info(f"on_tab_focus: tabn={tabn}, pane={self.pane_position}")

        # check if it's the " + " tab (it won't be in model.tabsdata)
        if tabn >= 0 and tabn < len(self.model.tabsdata):
            widget = self.widget(tabn)
            if hasattr(widget, "dummy") and widget.dummy:
                # [off-by-one FIX] Materializing a lazy tab replaces the dummy via
                # removeTab(tabn)+insertTab(tabn, real_widget) (QTabWidget has no
                # replace-in-place). Two Qt side effects broke first-click focus:
                #   1) insertTab at an index <= the current index increments Qt's
                #      currentIndex, shifting the visible page off the clicked tab.
                #   2) base removeTab() unblocks signals at its end, so the shift in
                #      (1) re-fires currentChanged -> re-enters on_tab_focus for the
                #      wrong (shifted) index, lazily loading a tab nobody clicked.
                # This is why the first click landed one tab away and only the second
                # click (dummy already materialized) showed the right tab.
                # The guard swallows the re-entrant signal; the outer call restores
                # the current index (signals blocked) to the tab the user clicked.
                if getattr(self, "_materializing_tab", False):
                    return self
                logma.info(f"Loading Lazy Tab {tabn}")
                self._materializing_tab = True
                try:
                    self.model.load_tab(self.model.tabsdata[tabn], tabn, self.pane_position)
                    if self.currentIndex() != tabn:
                        self.blockSignals(True)
                        self.setCurrentIndex(tabn)
                        self.blockSignals(False)
                finally:
                    self._materializing_tab = False
                widget = self.widget(tabn)

            # Persist last selected tab
            # if self.model.current_node:
            #     self.model.current_node.parameters["active_tab_position"] = tabn
            #     import json
            #
            #     try:
            #         self.app.model.update_node(
            #             self.model.current_node, {"parameters_dict": json.dumps(self.model.current_node.parameters)}
            #         )
            #     except Exception as e:
            #         logma.error(f"Failed to persist active tab position: {e}")

            # Refresh the VISIBLE right-pane toolbox for the newly focused center
            # document. The toolbox the user sees is the right-pane "ToolBox" tab,
            # held on the app as `self.app.toolbox` (set when that tab is loaded in
            # nchantrs tabsetmodels.load_tab). Its drawers are rebuilt from the
            # active center document's `toolbox_config`, so switching center tabs
            # must rebuild them.
            #
            # Only CENTER focus changes drive the toolbox: switching right-pane tabs
            # does not change the center document, and the toolbox is itself a
            # right-pane tab. The deferred QTimer.singleShot lets Qt settle the new
            # currentWidget() (which build_toolbox reads) before we rebuild.
            #
            # NOTE: the previous implementation refreshed `right_pane.toolbox`, a
            # separate toolbox built via create_toolbox() that is never added to any
            # layout/tab (a phantom). Refreshing it had no visible effect, so
            # switching center tabs left the visible toolbox showing the prior
            # document's drawers -- it only appeared to refresh on node selection /
            # new-tab because those rebuild the right pane (reloading the ToolBox tab
            # from scratch).
            if self.pane_position == "center":
                toolbox = self._find_right_toolbox()
                if toolbox is not None:
                    logma.info("Refreshing right-pane toolbox for focused document")
                    QTimer.singleShot(0, lambda tb=toolbox, doc=widget: tb.refresh_for_document(doc))

            # T-NEW-036: Refresh journal content on tab focus.
            # The journal's initModel fetched text once at
            # initWidget time; subsequent tab switches never
            # re-fetched. When the focused widget exposes
            # refresh_content (currently only the journal), call
            # it so the editor shows the current journal text.
            if hasattr(widget, "refresh_content"):
                try:
                    widget.refresh_content()
                except Exception as e:
                    logma.warning(
                        f"on_tab_focus: refresh_content failed ({type(e).__name__}: {e})"
                    )

        # Ensure tabn is valid for super class to avoid IndexError in set_focus.
        # RESOLVED [off-by-one]: the first-click-off-by-one on center/right tabsets
        # was caused by lazy-tab materialization shifting Qt's currentIndex (see the
        # restore in the dummy-load branch above), NOT by this boundary check. The
        # `<= len - 1` guard below is equivalent to the earlier strict `<` check and
        # is intentionally kept.
        if tabn >= 0 and tabn <= len(self.model.tabsdata) - 1:
            super().on_tab_focus(tabn)
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
