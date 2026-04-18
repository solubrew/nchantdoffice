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

# ======================================3rd Party Library Modules=====================================================||
from pandas import DataFrame

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from nchantrs.libraries import pyqt
from nchantrs.widgets.widgets import NchantdWidget
from kahndor.logma import Logma

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "packages.yaml")


class NchantdCuration:
    """A Curation will be an object containing curated entries for various tools and packages.  This will be the escence
    of a package itself and be the simplest form of an extension"""

    def __init__(self, parent, name, list=None, cfg=None):
        """ """
        self.config = kahndor.instruct(pxcfg).select("NchantdCuration")
        self.config.override(parent.config)
        self.config.override(cfg)
        self.app = pyqt.QApplication.instance()
        self.options = []
        self.options_df = DataFrame()
        self.set_options()

    def set_options(self, options=None):
        """"""
        self.options_df = self.app.model.get_curations("prompt", ["llms", "iga", "vga"])
        logma.info(f"Options {self.options_df}")
        options_df = self.options_df[["item_name_txt", "description_txt"]]
        self.options = [" - ".join(x) for x in options_df.values.tolist()]
        return self


class NchantdFocus(object):
    """A Focus represents an implementation of a package"""

    def __init__(self, name, parent, cfg=None):
        """"""
        self.config = kahndor.Instruct(pxcfg).select("NchantdFocus").override(cfg)
        self.name = name
        self.parent = parent

    def get_document_quick_launch(self):
        """"""

    def get_document_sort_sequence(self):
        """"""

    def set_theme(self):
        """"""
        self.parent.app.model.set_theme(self.name)


class NchantdToolsPackage(NchantdWidget):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = kahndor.instruct(pxcfg).select("NchantdToolsPackage")
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        super(NchantdToolsPackage, self).__init__(self.parent, self.config)

    def add_node(self, pid, tab_set, name):
        """"""
        pid = self.app.model.add_node(pid)
        self.add_tab_set(tab_set, pid, name)

    def add_tab_set(self, tab_set, pid, name):
        """"""

    def initModel(self):
        """"""
        return self

    def initView(self):
        """"""
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


def createPackageSkeleton():
    """"""
    pass


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
