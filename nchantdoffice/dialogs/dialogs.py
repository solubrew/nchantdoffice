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
# ======================================Standard Library Modules======================================================||
from os.path import abspath, dirname, join
import datetime as dt

# ======================================3rd Party Library Modules======================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from kahndor.logma import Logma
from nchantrs.dialogs.dialogs import NchantdCape, NchantdSigil
from pyffice.pyffice import PyfficeCodex

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "dialogs.yaml")


class NchantdOfficeDocumentCape(NchantdCape):
    """"""

    def __init__(self, name, instance=None, parent=None, cfg=None, args=None):
        """ """
        logma.info(f"[dialogs] NchantdOfficeDocumentCape.__init__ name={name!r} parent={type(parent).__name__ if parent else None}")
        try:
            super().__init__(name, instance, parent, cfg, args)
            self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeDocumentCape").override(cfg))
            self.is_installable = True
            logma.debug("[dialogs] NchantdOfficeDocumentCape.__init__: is_installable=True")
        except Exception as e:
            logma.error(f"[dialogs] NchantdOfficeDocumentCape.__init__ failed: name={name!r} err={e}", exc_info=True)
            raise

    def initModel(self):
        """"""
        logma.info("[dialogs] NchantdOfficeDocumentCape.initModel: installing PyfficeCodex on model")
        try:
            super().initModel()
            self.model.codex = PyfficeCodex()
            logma.debug(f"[dialogs] NchantdOfficeDocumentCape.initModel: codex installed, codex_type={type(self.model.codex).__name__}")
        except Exception as e:
            logma.error(f"[dialogs] NchantdOfficeDocumentCape.initModel failed: {e}", exc_info=True)
            raise
        return self

    def initView(self, cfg=None):
        """"""
        logma.info(f"[dialogs] NchantdOfficeDocumentCape.initView cfg_provided={cfg is not None}")
        try:
            super().initView(cfg)
        except Exception as e:
            logma.error(f"[dialogs] NchantdOfficeDocumentCape.initView failed: {e}", exc_info=True)
            raise
        return self

    def initWidget(self):
        """"""
        logma.info("[dialogs] NchantdOfficeDocumentCape.initWidget")
        try:
            self.initModel()
            self.initView()
        except Exception as e:
            logma.error(f"[dialogs] NchantdOfficeDocumentCape.initWidget failed: {e}", exc_info=True)
            raise
        return self


class NchantdNodeNameEditSigil(NchantdSigil):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        logma.info(f"[dialogs] NchantdNodeNameEditSigil.__init__ parent={type(parent).__name__ if parent else None}")
        try:
            super().__init__(parent, cfg)
            self.config.override(kahndor.Instruct(pxcfg).select("NchantdNodeNameEditSigil").override(cfg))
        except Exception as e:
            logma.error(f"[dialogs] NchantdNodeNameEditSigil.__init__ failed: {e}", exc_info=True)
            raise

    def initModel(self, cfg=None):
        """"""
        logma.info(f"[dialogs] NchantdNodeNameEditSigil.initModel cfg_provided={cfg is not None}")
        try:
            super().initModel(cfg)
        except Exception as e:
            logma.error(f"[dialogs] NchantdNodeNameEditSigil.initModel failed: {e}", exc_info=True)
            raise
        return self

    def initView(self, cfg=None):
        """"""
        logma.info(f"[dialogs] NchantdNodeNameEditSigil.initView cfg_provided={cfg is not None}")
        try:
            super().initView(cfg)
        except Exception as e:
            logma.error(f"[dialogs] NchantdNodeNameEditSigil.initView failed: {e}", exc_info=True)
            raise
        return self

    def initWidget(self):
        """"""
        logma.info("[dialogs] NchantdNodeNameEditSigil.initWidget")
        try:
            self.initModel()
            self.initView()
        except Exception as e:
            logma.error(f"[dialogs] NchantdNodeNameEditSigil.initWidget failed: {e}", exc_info=True)
            raise
        return self


class NchantdTabNameEditSigil(NchantdSigil):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        logma.info(f"[dialogs] NchantdTabNameEditSigil.__init__ parent={type(parent).__name__ if parent else None}")
        try:
            super().__init__(parent, cfg)
            self.config.override(kahndor.Instruct(pxcfg).select("NchantdTabNameEditSigil").override(cfg))
        except Exception as e:
            logma.error(f"[dialogs] NchantdTabNameEditSigil.__init__ failed: {e}", exc_info=True)
            raise

    def initModel(self, cfg=None):
        """"""
        logma.info(f"[dialogs] NchantdTabNameEditSigil.initModel cfg_provided={cfg is not None}")
        try:
            super().initModel(cfg)
        except Exception as e:
            logma.error(f"[dialogs] NchantdTabNameEditSigil.initModel failed: {e}", exc_info=True)
            raise
        return self

    def initView(self, cfg=None):
        """"""
        logma.info(f"[dialogs] NchantdTabNameEditSigil.initView cfg_provided={cfg is not None}")
        try:
            super().initView(cfg)
        except Exception as e:
            logma.error(f"[dialogs] NchantdTabNameEditSigil.initView failed: {e}", exc_info=True)
            raise
        return self

    def initWidget(self):
        """"""
        logma.info("[dialogs] NchantdTabNameEditSigil.initWidget")
        try:
            self.initModel()
            self.initView()
        except Exception as e:
            logma.error(f"[dialogs] NchantdTabNameEditSigil.initWidget failed: {e}", exc_info=True)
            raise
        return self


# ====================================================================================================================||


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
