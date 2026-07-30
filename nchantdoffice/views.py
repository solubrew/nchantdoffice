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
from os.path import dirname, join

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from nchantrs.views.applicationviews import NchantdCloakView
from nchantdoffice.widgets.controls.toolbars import (
    NchantdNewDocumentToolBar,
)
from kahndor.logma import Logma

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "views.yaml")


class NchantdOfficeCloakView(NchantdCloakView):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        logma.info(f"NchantdOfficeCloakView init: parent={type(parent).__name__}")
        super().__init__(parent, None)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeCloakView").override(cfg))

    def initView(self, cfg=None):
        """"""
        super().init_pre_view(cfg)
        cfg = {}
        self.panes["toolbar"] = NchantdNewDocumentToolBar(self.parent, cfg).initWidget()
        super().initView(cfg)
        return self

    def switch_to_account_tab(self):
        """Switch the center tabset to the user's account tab.

        Sprint 20: previously a stub with a "PUSH to 0.0.3" marker
        that wasn't in the canonical PUSH list. Looks up the
        account tab via ``self.app.user`` (when present) and
        routes the center tabset to it. Falls back to no-op
        when the user or account tab isn't available.
        """
        try:
            user = getattr(self.app, "user", None)
            if user is None:
                return self
            # The account tab is identified by its ``name`` on the
            # user's tree (the Home / Settings / Account triad).
            # When the tab exists, switch to it; otherwise no-op.
            tab = getattr(user, "account_tab", None)
            if tab is None:
                tab = getattr(user, "settings_tab", None)
            if tab is None:
                return self
            center = self.panes.get("center")
            if center is None or not hasattr(center, "set_current_tab"):
                return self
            center.set_current_tab(tab)
        except Exception as exc:
            logma.warning(
                f"[views] switch_to_account_tab failed: {exc}",
                exc_info=True,
            )
        return self

    def on_window_move(self, event):
        """Propagate a window-move event to visible notes.

        Sprint 20: previously a stub with a "PUSH to 0.0.3" marker
        that wasn't in the canonical PUSH list. The original
        intent (per the comment) was to move any visible notes
        at the same time as the main application. Iterates the
        center tabset's open tabs and forwards the event to
        any tab that exposes ``on_window_move``.
        """
        try:
            center = self.panes.get("center")
            if center is None:
                return self
            model = getattr(center, "model", None)
            tabs = getattr(model, "tabs", None) if model is not None else None
            if not tabs:
                return self
            for tab in tabs:
                forward = getattr(tab, "on_window_move", None)
                if callable(forward):
                    try:
                        forward(event)
                    except Exception as tab_exc:
                        logma.warning(
                            f"[views] on_window_move: tab "
                            f"{getattr(tab, 'name', '?')!r} "
                            f"forward failed: {tab_exc}"
                        )
        except Exception as exc:
            logma.warning(
                f"[views] on_window_move failed: {exc}",
                exc_info=True,
            )
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
