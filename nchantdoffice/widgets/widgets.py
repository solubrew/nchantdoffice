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

# -*- coding: utf-8 -*
# ======================================Standard Library Modules======================================================||
from os.path import abspath, dirname, join
import datetime as dt

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from kahndor.logma import Logma
from nchantrs.widgets.tabsets import NchantdTabSet
from nchantrs.libraries.pyqt import QTimer
from nchantdoffice.models import NchantdOfficeTabSetModel
from nchantdoffice.widgets.controls.toolboxes import NchantdOfficeApplicationToolBox

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

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeTabSet").override(cfg))
        self.model = NchantdOfficeTabSetModel(self, self.config)

    def initModel(self, create_objects=True):
        """"""
        super().initModel(create_objects)
        return self

    def initView(self):
        """"""
        super().initView()
        return self

    def initWidget(self, cfg=None):
        """"""
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

    def create_toolbox(self, parent=None, cfg=None):
        """"""
        toolbox = NchantdOfficeApplicationToolBox(parent, cfg)
        toolbox.initWidget()
        return toolbox

    def _find_right_toolbox(self):
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

    def go_to_previous_tab(self):
        """Switch to the previously focused tab (if any).

        Tracks the last-focused index in ``self._prev_tab_index``
        and switches back to it. Returns ``self`` for chainable calls.
        """
        try:
            prev = getattr(self, "_prev_tab_index", None)
            if prev is not None and 0 <= prev < self.count():
                logma.info(f"[widgets] go_to_previous_tab: switching to {prev}")
                self.setCurrentIndex(prev)
            else:
                logma.debug("[widgets] go_to_previous_tab: no previous index")
            return self
        except Exception as e:
            logma.error(f"[widgets] go_to_previous_tab failed: {e}", exc_info=True)
            return self

    def setTabText(self, position, text, store=True):
        """"""
        super().setTabText(position, text)
        if store:
            cfg = {"name_txt": text}
            self.app.model.update_tab(self.app.model.get_current_tab(), cfg)

    def on_tab_focus(self, tabn=None):
        # DIAGNOSTIC-INSTRUMENTATION (H62): every step of the tab-focus
        # pipeline logs at INFO with a [FOCUS] prefix so we can
        # reconstruct the full path from log output. Remove once the
        # open regression is diagnosed and fixed.
        logma.info(
            f"[FOCUS] on_tab_focus ENTER tabn={tabn!r} pane={self.pane_position!r} "
            f"tabsdata_len={len(self.model.tabsdata) if self.model and getattr(self.model, 'tabsdata', None) else 'NO_MODEL'}"
        )
        # logma.inspect_caller()
        if tabn is None:
            tabn = self.currentIndex()
        logma.info(f"[FOCUS] on_tab_focus resolved tabn={tabn}")

        try:
            return self._on_tab_focus_body(tabn)
        except Exception as exc:
            import traceback
            logma.error(
                f"[FOCUS] on_tab_focus EXCEPTION tabn={tabn} pane={self.pane_position} "
                f"type={type(exc).__name__} message={exc!r}"
            )
            logma.error(f"[FOCUS] traceback:\n{traceback.format_exc()}")
            raise
        finally:
            logma.info(
                f"[FOCUS] on_tab_focus EXIT tabn={tabn} pane={self.pane_position} "
                f"currentIndex={self.currentIndex()}"
            )

    def _on_tab_focus_body(self, tabn):
        """Body of on_tab_focus, separated for H62 diagnostic instrumentation.

        Same logic as the original on_tab_focus body, lifted into its
        own method so the outer ``on_tab_focus`` can wrap it in a
        try/except/finally that always logs ENTER and EXIT. Keeping the
        body identical to pre-H62 ensures the existing tests still
        pass without modification.
        """

        # check if it's the " + " tab (it won't be in model.tabsdata)
        if tabn >= 0 and tabn < len(self.model.tabsdata):
            widget = self.widget(tabn)
            logma.info(
                f"[FOCUS] existing widget at tabn={tabn}: type={type(widget).__name__} "
                f"hasattr_dummy={hasattr(widget, 'dummy')} "
                f"dummy={getattr(widget, 'dummy', None)!r}"
            )
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
                    logma.info(f"[FOCUS] _materializing_tab guard tripped at tabn={tabn}; returning self")
                    return self
                logma.info(f"[FOCUS] Loading Lazy Tab {tabn}; calling model.load_tab")
                logma.info(f"[FOCUS] tabsdata[{tabn}]={self.model.tabsdata[tabn]}")
                self._materializing_tab = True
                try:
                    self.model.load_tab(self.model.tabsdata[tabn], tabn, self.pane_position)
                    logma.info(f"[FOCUS] model.load_tab returned; currentIndex={self.currentIndex()}")
                    if self.currentIndex() != tabn:
                        logma.info(
                            f"[FOCUS] currentIndex drift detected after load_tab "
                            f"(got {self.currentIndex()}, expected {tabn}); restoring"
                        )
                        self.blockSignals(True)
                        self.setCurrentIndex(tabn)
                        self.blockSignals(False)
                finally:
                    self._materializing_tab = False
                widget = self.widget(tabn)
                logma.info(
                    f"[FOCUS] post-materialize widget at tabn={tabn}: type={type(widget).__name__}"
                )

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
                logma.info(
                    f"[FOCUS] center pane focus; right-pane toolbox lookup "
                    f"result={toolbox!r}"
                )
                if toolbox is not None:
                    logma.info("[FOCUS] Refreshing right-pane toolbox for focused document")
                    # The toolbox widget itself owns the refresh logic;
                    # it exposes refresh_for_document(doc_widget). We pass
                    # the just-focused center widget so the toolbox can
                    # rebuild drawers from its toolbox_config.
                    QTimer.singleShot(
                        0,
                        self._make_toolbox_refresh_handler(toolbox, widget),
                    )

        # Ensure tabn is valid for super class to avoid IndexError in set_focus.
        # RESOLVED [off-by-one]: the first-click-off-by-one on center/right tabsets
        # was caused by lazy-tab materialization shifting Qt's currentIndex (see the
        # restore in the dummy-load branch above), NOT by this boundary check. The
        # `<= len - 1` guard below is equivalent to the earlier strict `<` check and
        # is intentionally kept.
        logma.info(
            f"[FOCUS] pre-super.on_tab_focus: tabn={tabn} "
            f"tabn_in_range={0 <= tabn <= max(0, len(self.model.tabsdata) - 1)}"
        )
        if tabn >= 0 and tabn <= len(self.model.tabsdata) - 1:
            super().on_tab_focus(tabn)
            logma.info(f"[FOCUS] super().on_tab_focus returned")
        else:
            logma.warning(
                f"[FOCUS] super().on_tab_focus SKIPPED: tabn={tabn} out of range "
                f"(tabsdata_len={len(self.model.tabsdata)})"
            )
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
