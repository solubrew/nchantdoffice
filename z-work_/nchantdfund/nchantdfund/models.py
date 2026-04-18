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
from excalc import tree as calctr
from nchantrs.models import models, treemodels
from nchantrs.models.applicationmodels import NchantdCloakModel
from nchantrs.dstruct import trees
from rhino.versys import git
from squirl.orgnql import yonql

# ===============================================================================||
from nchantdmoonbags.wallet import Wallet

# ===============================================================================||
here = join(dirname(__file__), "")  # 												||
log = True
# ===============================================================================||
pxcfg = join(abspath(here), "_data_", "models.yaml")


class NFAppModel(NchantdCloakModel):
    """ """

    def __init__(self, parent=None, cfg={}):
        """ """
        self.parent = parent
        self.config = kahndor.instruct(pxcfg).select("NFAppModel")
        self.config.override(cfg)
        if parent:
            self.config.override(parent.config)
        self.name = self.parent.name.lower()
        super(NFAppModel, self).__init__(parent)

    def launchModel(self):
        """ """
        self.wallet = Wallet(self.name, False, self.src, self.config)
        # self.nodes = NMBNodesModel(self)
        # self.tomes = NMBTOMEsModel(self)
        return self

    def setupModel(self):
        """Executed via the launch sequence within the Nchantrs initilization"""
        self.wallet.loadWallet()
        self.wallet.updateWallet()
        self.wallet.saveWallet()
        self.buildModel()
        return self

    def updateModel(self):
        """ """
        if log:
            print("Update App Data")
        self.wallet.updateWallet()

    def buildModel(self):
        """ """
        if log:
            print("Build Nodes Model")
        self.nodes.buildNodes()
        return self
