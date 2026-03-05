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
from nchantrs.libraries import pyqt
from nchantrs.widgets.widgets import NchantdWidget
from nchantrs.widgets.media.images import NchantdImage
from nchantrs.widgets.trees import NchantdApplicationTree
from nchantdoffice.widgets.items.items import NchantdOfficeTreeNode

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "trees.yaml")


class NchantdOfficeApplicationTree(NchantdWidget):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeApplicationTree"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        self.tree = None
        self.image = None

    def initModel(self):
        """"""
        super().initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        cfg = {"node_widget": NchantdOfficeTreeNode}
        self.tree = NchantdApplicationTree(self.parent, cfg).initWidget()

        # Ensure the tree maintains selection highlight when not focused
        if hasattr(self.tree, "setSelectionMode"):
            self.tree.setSelectionMode(pyqt.QAbstractItemView.SingleSelection)
        if hasattr(self.tree, "setSelectionBehavior"):
            self.tree.setSelectionBehavior(pyqt.QAbstractItemView.SelectRows)

        self.layout.addWidget(self.tree)
        cfg = {
            "size": [250, 200],
            "path": join(self.app.view.themes_path, "_data_", "icons", "midnight_icons", "midnight-mist-headshot.svg"),
        }
        self.image = NchantdImage(self, cfg).initWidget()
        self.image.label.setFrameStyle(0)
        self.image.label.setStyleSheet("border: 0px;")
        self.layout.addWidget(self.image)
        self.layout.setAlignment(pyqt.Qt.AlignTop)
        return self

    def initWidget(self, cfg=None):
        """"""
        self.initModel()
        self.initView()
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
