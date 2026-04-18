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
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument
from nchantdoffice.widgets.documents.media.scripts import NchantdOfficeScript
from nchantrs.widgets.groups import NchantdHScrollGroupBox, NchantdVScrollGroupBox
from nchantrs.dialogs.files import NchantdFileOpenSigil
from nchantrs.widgets.config.settings import NchantdSettingsWidget

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "apis.yaml")


class NchantdOfficeAPIFile(NchantdSettingsWidget):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeAPIFile"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        self.document = None
        self.file_path = None
        self.primary_settings_group = None

    def initModel(self):
        """"""
        super().initModel()
        cfg = {}
        self.document = NchantdOfficeScript(self, cfg).initWidget()
        return self

    def initView(self):
        """"""
        super().initView()
        if self.file_path is None:
            self.show_file_sigil()
        else:
            self.document.open(self.file_path)
            self.layout.addWidget(self.document)
        cfg = {"size": ["auto", "auto"]}
        self.primary_settings_group = NchantdVScrollGroupBox(self, cfg)
        self.primary_settings_group.setTitle("Configured APIs")
        self.layout.addLayout(self.primary_settings_group.layout)

        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def show_file_sigil(self):
        """"""

    def open_file_sigil(self, name=None, app=None, cfg=None):
        """"""
        file_sigil = NchantdFileOpenSigil("open", self.parent, self.config.override(cfg))
        self.file_path = file_sigil.initWidget()
        if self.file_path.file_selected:
            self.show_file_path()
            self.load_google = False


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
