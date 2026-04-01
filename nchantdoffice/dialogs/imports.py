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
from nchantrs.dialogs.dialogs import NchantdSigil
from ogma.logma import Logma
from nchantrs.widgets.browsers.browsers import NchantdWebViewer
from nchantrs.widgets.controls.button_groups import NchantdAcceptButtons
from nchantrs.widgets.media.editors.editors import NchantdLabeledEntry

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "imports.yaml")


class ImportDocumentNchantdSigil(NchantdSigil):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = condor.Instruct(pxcfg).select("ImportDocumentNchantdSigil")
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        super().__init__(self.parent, self.config)
        self.document_type = None

    def initModel(self):
        """"""
        super().initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        options = ["epub", "pdf", "excel", "word", "cherrytree", ""]
        cfg = {"text": "Select Document Type for Import", "options": options}
        self.document_type = NchantdLabeledEntry(self, cfg).initWidget()
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        self.run()
        return self


class ImportExcelNchantdSigil(NchantdSigil):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = condor.Instruct(pxcfg).select("ImportExcelNchantdSigil")
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        super().__init__(self.parent, self.config)

    def initModel(self):
        """"""
        super().initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class ImportPDFNchantdSigil(NchantdSigil):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = condor.Instruct(pxcfg).select("ImportPDFNchantdSigil")
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        super().__init__(self.parent, self.config)

    def initModel(self):
        """"""
        super().initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdGoogleDriveSigil(NchantdSigil):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = condor.Instruct(pxcfg).select("NchantdGoogleDriveSigil")
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        super().__init__("gdrive", self.parent, self.config)
        self.viewer = None
        self.buttons = None
        self.file_selected = None

    def initModel(self):
        """"""
        super().initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        self.hide_title()
        cfg = {"url": "https://drive.google.com/drive/u/0/search?q=type:document"}
        self.viewer = NchantdWebViewer(self, self.config.override(cfg)).initWidget(cfg["url"])
        self.layout.addWidget(self.viewer)
        self.setGeometry(150, 250, 1000, 600)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        self.finalizeView()
        self.run()
        return self

    def accept(self):
        """"""
        super().accept()
        if self.ok:
            # self.file_selected = self.selectedFiles()[0]
            logma.info(f"{self.file_selected}")
        return self.file_selected

    def finalizeView(self):
        """"""
        self.add_accept_buttons()
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
