# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@Nchantrs@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""#																			||
---  #																			||
<(META)>:  #																	||
        docid: ''  #							||
        name: Tabs Python Document#								||
        description: >  #															||
        expirary: <[expiration]>  #													||
        version: <[version]>  #														||
        path: <[LEXIvrs]>  #														||
        outline: <[outline]>  #														||
        authority: document|this  #													||
        security: sec|lvl2  #														||
        <(WT)>: -32  #																||
"""  # 																			||

# -*- coding: utf-8 -*-#														||
# ================================Core Modules===================================||
from os.path import abspath, dirname, exists, join

# ===============================================================================||
from kahndor import kahndor
from nchantrs.widgets.trees import NchantdTree
from nchantrs.widgets.tabsets import NchantdTabSet

# ===============================================================================||
from nchantdimagery.models import NINavTreeModel, NITabSetModel

# ===============================================================================||
here = join(dirname(__file__), "")  # 												||
there = abspath(join("../../.."))  # 												||set path at pheonix level
version = "0.0.0.0.0.0"  # 														||
log = True
# ===============================================================================||
pxcfg = join(abspath(here), "_data_/widgets.yaml")


class NINavTree(NchantdTree):
    """ """

    def __init__(self, parent=None, root=None, cfg={}):
        """ """
        self.parent = parent
        self.config = kahndor.instruct(pxcfg).select("NINavTree")
        self.config.override(cfg)
        if parent:
            self.config.override(parent.config)
        super(NINavTree, self).__init__(parent, self.config)
        self.src = self.parent.src
        self.newInstance = self.parent.newInstance
        if log:
            print("NMBNavTree")
        self.model = NINavTreeModel(self, root, self.src)


class NITabSet(NchantdTabSet):
    """ """

    def __init__(self, parent=None, cfg={}):
        """ """
        self.parent = parent
        self.config = kahndor.instruct(pxcfg).select("NITabSet")
        self.config.override(cfg)
        if parent:
            self.config.override(parent.config)
        super(NITabSet, self).__init__(parent, self.config)
        self.src = self.parent.src
        self.model = NITabSetModel(self, self.src)
        self.currenttabn = 0
