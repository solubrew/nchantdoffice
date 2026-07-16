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
from nchantrs.widgets.config.help import NchantdFAQs, NchantdHelpDocs, NchantdHelpChatDex
from nchantrs.widgets.trees import NchantdTree
from nchantdoffice.widgets.documents.media.pdfs import NchantdOfficePDF

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "help.yaml")


class NchantdOfficeFAQs(NchantdFAQs):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeFAQs").override(parent.config).override(cfg))

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        super().initView(cfg)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdOfficeHelpDocs(NchantdHelpDocs):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeHelpDocs").override(cfg))
        self.index_tree = None
        self.reader = None

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        # TODO: need to implement a download of pdf files and then load an index that can navigate through them
        # the pdf's are documentation....this may be more costly bandwidth wise than just using html pages that are
        # pulled on demand
        return self

    def initView(self, cfg=None):
        """"""
        cfg = cfg or {}
        cfg["layout"] = "horizontal"
        super().initView(cfg)
        # cfg = {}
        # self.index_tree = NchantdTree(self, cfg).initWidget()
        # self.layout.addWidget(self.index_tree)
        # cfg = {}
        # self.reader = NchantdOfficePDF(self, cfg).initWidget()
        # self.layout.addWidget(self.reader)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdOfficeHelpChatDex(NchantdHelpChatDex):
    """"""

    def __init__(self, parent=None, cfg=None):
        """"""
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdHelpChatDex").override(cfg))

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        cfg = cfg or {}
        super().initView(cfg)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
