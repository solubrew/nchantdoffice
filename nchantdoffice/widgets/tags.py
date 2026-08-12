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
# ======================================Standard Library Modules======================================================||
from os.path import abspath, dirname, join
import datetime as dt

# ======================================3rd Party Library Modules=====================================================|

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from nchantrs.widgets.widgets import NchantdWidget
from kahndor.logma import Logma
from typing import Any, Self

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "tags.yaml")


class NchantdQuickTagsWidget(NchantdWidget):
    """"""

    def __init__(self, parent=None, cfg=None) -> None:
        """ """
        logma.info(f"[tags] NchantdQuickTagsWidget.__init__ parent={type(parent).__name__ if parent else None}")
        try:
            super().__init__(parent, cfg)
            self.config.override(kahndor.instruct(pxcfg).select("NchantdQuickTagsWidget").override(cfg))
        except Exception as e:
            logma.error(f"[tags] NchantdQuickTagsWidget.__init__ failed: {e}", exc_info=True)
            raise

    def initModel(self) -> Self:
        """ """
        logma.info("[tags] NchantdQuickTagsWidget.initModel: (no-op, subclasses fill in)")
        return self

    def initView(self) -> Self:
        """ """
        logma.info("[tags] NchantdQuickTagsWidget.initView: (no-op, subclasses fill in)")
        return self

    def initWidget(self) -> Self:
        """ """
        logma.info("[tags] NchantdQuickTagsWidget.initWidget")
        try:
            self.initModel()
            self.initView()
        except Exception as e:
            logma.error(f"[tags] NchantdQuickTagsWidget.initWidget failed: {e}", exc_info=True)
            raise
        return self


class NchantdTagsSideBar(NchantdWidget):
    """"""

    def __init__(self, parent=None, cfg=None) -> None:
        """ """
        logma.info(f"[tags] NchantdTagsSideBar.__init__ parent={type(parent).__name__ if parent else None}")
        try:
            super().__init__(parent, cfg)
            self.config.override(kahndor.instruct(pxcfg).select("NchantdTagsSideBar").override(cfg))
        except Exception as e:
            logma.error(f"[tags] NchantdTagsSideBar.__init__ failed: {e}", exc_info=True)
            raise

    def initModel(self) -> Self:
        """ """
        logma.info("[tags] NchantdTagsSideBar.initModel")
        try:
            super().initModel()
        except Exception as e:
            logma.error(f"[tags] NchantdTagsSideBar.initModel failed: {e}", exc_info=True)
            raise
        return self

    def initView(self) -> Self:
        """ """
        logma.info("[tags] NchantdTagsSideBar.initView")
        try:
            super().initView()
        except Exception as e:
            logma.error(f"[tags] NchantdTagsSideBar.initView failed: {e}", exc_info=True)
            raise

        return self

    def initWidget(self) -> Self:
        """ """
        logma.info("[tags] NchantdTagsSideBar.initWidget")
        try:
            self.initModel()
            self.initView()
        except Exception as e:
            logma.error(f"[tags] NchantdTagsSideBar.initWidget failed: {e}", exc_info=True)
            raise
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
