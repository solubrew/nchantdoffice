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
from nchantrs.libraries import pyqt
from nchantrs.widgets.annotations import NchantdLabel
from nchantrs.widgets.controls.buttons import NchantdButton
from nchantrs.widgets.widgets import NchantdWidget
from nchantrs.widgets.groups import NchantdVScrollGroupBox, NchantdHGroupBox
from kahndor.logma import Logma

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", ".yaml")


class NchantdOfficeExtensionsSettings(NchantdWidget):
    """"""

    def __init__(self, parent, cfg=None):
        """"""
        super().__init__(parent, cfg)
        self.config.override(kahndor.instruct(pxcfg).select("NchantdExtensionsSettingsTab").override(cfg))
        self.extensions = []

    def initModel(self):
        """"""
        super().initModel()
        # self.model.data['extensions'] = []
        # self.extensions = self.model.data['extensions']

    def initView(self):
        """"""
        # layout = NchantdScrollVBoxLayout()
        layout = pyqt.QVBoxLayout()
        group = pyqt.QGroupBox()
        top_layout = pyqt.QHBoxLayout()
        cfg = {"text": "Extension Settings", "font": {"size": 20}}
        top_layout.addWidget(NchantdLabel(self, cfg).initWidget())
        top_layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop)
        group.setLayout(top_layout)

        layout.addWidget(group)
        if len(self.extensions) != 0:
            for extension in self.extensions:
                button_layout = pyqt.QVBoxLayout()
                button_group = pyqt.QGroupBox()
                button = pyqt.QPushButton(extension)
                button_layout.addWidget(button)
                button_group.setLayout(button_layout)
                layout.addWidget(button_group)
        else:
            no_extensions_layout = pyqt.QVBoxLayout()
            cfg = {"label": "Add Extension", "text": "No Extensions Installed"}
            no_extensions = NchantdButton(self, cfg).initWidget()
            no_extensions_group = pyqt.QGroupBox()
            no_extensions_layout.addWidget(no_extensions)
            extension_catalog_preview = NchantdExtensionsCatalog(self, self.config).initWidget()
            no_extensions_group.setLayout(no_extensions_layout)
            layout.addWidget(no_extensions_group)
        self.setLayout(layout)  #  .make_scrollable())

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdIntegrationSettings(NchantdWidget):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.instruct(pxcfg).select("NchantdIntegrationSettings").override(cfg))

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


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
