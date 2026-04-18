# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
        docid: ''
        name:
        description: >
        expirary: <[expiration]>
        version: <[version]>
        path: <[LEXIvrs]>
        authority: document|this
        security: sec|lvl2
        <(WT)>: -32
"""

# -*- coding: utf-8 -*-
# ================================Core Modules===================================||
from os.path import abspath, dirname, exists, join
from os import listdir
import json as j

# ===============================================================================||
from pandas import concat, DataFrame
from numpy import argsort

# ===============================================================================||
from kahndor import kahndor  # 										||
from squirl.orgnql import yonql
from nchantrs.models import models, treemodels, tabsetmodels

# ===============================================================================||
# ===============================================================================||
here = join(dirname(__file__), "")  # 												||
log = True
# ===============================================================================||
pxcfg = join(abspath(here), "_data_", "models.yaml")


class NINavTreeModel(treemodels.NchantdFileSystemModel):
    """ """

    def __init__(self, parent=None, root=None, cfg={}):
        """ """
        self.parent = parent
        self.config = kahndor.instruct(pxcfg).select("NINavTreeModel")
        self.config.override(cfg)
        if parent:
            self.config.override(parent.config)
        super(NINavTreeModel, self).__init__(parent, root)
        self.nodes = []
        self.tabsets = self.config.dikt["gui"]["desktop"]["tabsets"]
        self.base = [0, 0, 1, 1, 1, 1, 0, 0]
        self.tbase = ["center", 0, 1, 1]
        self.src = self.parent.src
        self.name = "nchantdimagery"
        nid = models.getLastNodeId(self.src, self.name)

        # 		self.src.setReader({'table': ['vw_tokens']}, self.name)
        # 		self.src.initExtract('symbol', 'set')

        self.rows, self.tabs = [], []

    def initModel(self, newInstance=False):
        """ """
        self.buildNodes()
        # self.buildTabSet(nid, tset, self.tbase, datatabs)
        super().initModel()
        return self

    def buildNodes(self):
        """the trnodes table doesn't make sense with the file system as the
        data source but I need to figure out how to turn of the expectation"""
        # nid = models.getLastNodeId(self.src, self.name)
        # pos = 0
        # lock = 0
        # if self.config.dikt['gui']['desktop']['nodes']['Viewer'] and not lock:#	||
        # 	nid = self.buildNEWSLNodes(nid, 0, pos)
        # 	pos += 1
        # super().buildNodes()
        # return self

    # def buildNEWSLNodes(self, nid, pid, pos):
    # 	''' '''
    # 	tset = 'NIDirectoryManagerTabSet'
    # 	nid = self.buildNode(nid, 'NEWSL', 'appnode', pid, pos, tset)
    # 	return nid


class NITabSetModel(tabsetmodels.NchantdTabSetModel):
    """ """

    def __init__(self, parent=None, cfg={}):
        """ """
        self.parent = parent
        self.config = kahndor.instruct(pxcfg).select("NITabSetModel")
        self.config.override(cfg)
        if parent:
            self.config.override(parent.config)
        super(NITabSetModel, self).__init__(parent, parent.src, self.config)
