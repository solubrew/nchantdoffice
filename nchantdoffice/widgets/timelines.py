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
from nchantrs.widgets.calendars.timelines import NchantdTodayOverview

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "timelines.yaml")


class NchantdOfficeTodayOverview(NchantdTodayOverview):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        logma.info(f"[timelines] NchantdOfficeTodayOverview.__init__ parent={type(parent).__name__ if parent else None}")
        self.parent = parent
        self.config = kahndor.instruct(pxcfg).select("Nchantd")
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        try:
            super().__init__(self.parent, self.config)
            logma.debug(f"[timelines] NchantdOfficeTodayOverview.__init__: super complete, config_keys={list(self.config.dikt.keys())[:8]}")
        except Exception as e:
            logma.error(f"[timelines] NchantdOfficeTodayOverview.__init__ failed: {e}", exc_info=True)
            raise

    def initModel(self):
        """"""
        logma.info("[timelines] initModel")
        try:
            super().initModel()
        except Exception as e:
            logma.error(f"[timelines] initModel failed: {e}", exc_info=True)
            raise
        return self

    def initView(self):
        """"""
        logma.info("[timelines] initView")
        try:
            super().initView()
            self.initLowerWidgets()
            logma.debug("[timelines] initView: lower widgets initialised")
        except Exception as e:
            logma.error(f"[timelines] initView failed: {e}", exc_info=True)
            raise
        return self

    def initWidget(self):
        """"""
        logma.info("[timelines] initWidget")
        try:
            self.initModel()
            self.initView()
        except Exception as e:
            logma.error(f"[timelines] initWidget failed: {e}", exc_info=True)
            raise
        return self

    def initLowerWidgets(self):
        """"""
        logma.info("[timelines] initLowerWidgets: building lower-section widgets")
        # No-op stub; subclasses or post-init scripts override with calendar / weather / tasks panes.


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
