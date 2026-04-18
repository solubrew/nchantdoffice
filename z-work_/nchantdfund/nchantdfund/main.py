# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""#																			||
---  #																			||
<(META)>:  #																	||
        docid: ''  #								||
        name: Nchantd Funds#														||
        description: >  #															||
        expirary: <[expiration]>  #													||
        version: <[version]>  #														||
        authority: document|this  #													||
        security: sec|lvl2  #														||
        <(WT)>: -32  #																||
"""  # 																			||

# -*- coding: utf-8 -*-#														||
# =================================Core Modules==================================||
import sys
from os.path import abspath, dirname, exists, join
from pandas import DataFrame

# ===============================================================================||
import crow

# ===============================================================================||
from kahndor import kahndor  # 										||
from nchantrs import nchantrs
from nchantrs.dialogs import dialogs

from nchantrs.libraries import pyqt
from nchantrs.nchantrs import NchantdCloak

from models import NFAppModel
from dialogs import NFAccountEntry
import widgets

# ===============================================================================||
there = abspath(join(""))  # 														||set path at pheonix level
log = True
# ===============================================================================||

pxcfg = join(abspath(there), "_data_", "nchantdfund.yaml")


class NchantdFund(NchantdCloak):
    """A templated setup file for creating the initilized data structure and
    populating first entrys to an Nchantd based GUI application....
    eventually reclass this inside nchantd once standard usages are
    established....long term needs to point at available endpoints"""

    def __init__(self, args):
        ucfg = join(abspath(there), "_data_/user.yaml")  # 						||
        self.config = kahndor.instruct(pxcfg).override(ucfg).addArgs(args)  # 		||
        super(NchantdFund, self).__init__("NchantdFund", self)  # 			||
        self.model = NFAppModel(self).initModel()
        self.initApp()

    def setup(self):
        """ """
        self.newApp = True
        self.applicationSetup()
        return self

    def applicationLaunch(self):
        """ """
        return self

    def applicationSetup(self):
        """Create new database eventually have checks in place so as not to
        delete user db also have a way of backing up any nonblockchain data
        so it can be selectively reimported to a new database if needed"""
        self.instanceSetup()
        self.newApp = False
        self.newInstance = True
        return self

    def instanceLaunch(self):
        """ """
        return self

    def instanceSetup(self):
        """Ask for primes...USD/BTC...etc
        Ask for chains of interest
        Ask for addresses of interest
        Ask for additional accounts of interest...CEX, socialmedia"""
        # self.accountentry = self.launchDialog('NMBAccountEntry')
        self.model.launchModel()
        self.model.setupModel()
        self.newInstance = False
        return self

    def launchDialog(self, dialog):
        """ """
        # self.dialogs[dialog] = NMBAccountEntry('NMBAccountEntry', self)

        return self

    def update(self):
        """ """
        return self


if __name__ == "__main__":
    NchantdFund(sys.argv)


# ===========================Code Source Examples================================||
"""
"""
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
