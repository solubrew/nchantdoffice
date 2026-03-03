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
from condor import condor
from ogma.logma import Logma
from nchantrs.utilities.utils import lookup
from nchantrs.widgets.widgets import NchantdWidget
from nchantrs.widgets.controls.buttons import NchantdButton

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", ".yaml")
pxcfg = {}


class NchantdOfficeNewDocumentAcceptButtons(NchantdWidget):
    """ """

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = condor.Instruct(pxcfg).select("NchantdOkButtons")
        if parent:
            self.config.override(self.parent.config)
        self.config.override(cfg)
        super().__init__(self.parent, self.config)
        self.ok_button = None
        self.cancel_button = None

    def initModel(self):
        """"""
        super().initModel()
        return self

    def initView(self):
        """"""
        super().initView({"layout": "horizontal"})

        self.config.override({"buttons": {"ok": lookup(self.app, "ok")}})
        logma.info(f"Ok Button {self.config.dikt['buttons']['ok']}")
        self.ok_button = NchantdButton(self, self.config.dikt["buttons"]["ok"])
        self.ok_button.initWidget()
        self.layout.addWidget(self.ok_button)

        self.config.override({"buttons": {"import_all_file": lookup(self.app, "import_all_file")}})
        logma.info(f"Cancel Button {self.config.dikt['buttons']['import_all_file']}")
        self.import_button = NchantdButton(self, self.config.dikt["buttons"]["import_all_file"])
        self.import_button.initWidget()
        self.layout.addWidget(self.import_button)

        self.config.override({"buttons": {"cancel": lookup(self.app, "cancel")}})
        logma.info(f"Cancel Button {self.config.dikt['buttons']['cancel']}")
        self.cancel_button = NchantdButton(self, self.config.dikt["buttons"]["cancel"])
        self.cancel_button.initWidget()
        self.layout.addWidget(self.cancel_button)

        self.layout.setAlignment(self.getAlignment(self.config.dikt.get("justify", "left")))
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
