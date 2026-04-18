# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
        docid: <^(UUID)^>
        name:
        description: >
        expirary: <[expiration]>
        version: <[version]>
        path: <[LEXIvrs]>
        outline: <[outline]>
        authority: document|this
        security: sec|lvl2
        <(WT)>: -32
"""

# -*- coding: utf-8 -*-
# ================================Core Modules===================================||
from os.path import abspath, dirname, exists, join
from sys import argv
import datetime as dt

# ===============================================================================||
# from crow import  # Commented out crowLoad
crowLoad("NchantdTodo", "DELTA")
# ===============================================================================||

from kahndor import kahndor  # ||
from nchantrs.dialogs.dialogs import NchantdCape
from nchantdtodo.resource import Resource_Human
from kahndor.logma import Logma

# ===============================================================================||
there = abspath(join(""))
here = join(dirname(__file__), "")
log = True
logma = Logma(__name__)


# ===============================================================================||
pxcfg = join(here, "_data_", "runTab.yaml")


class NchantdTab(NchantdCape):
    """
    The NchantdTab class is a subclass of the NchantdCape class. It represents a database and provides methods for
    its creation and initialization.
    Attributes:
    - config: A configuration object that stores the configuration settings for the database.
    Methods:
    - __init__(self, args): Initializes a new instance of the NchantdTab class.
        :param args: Additional arguments to be passed to the configuration object.
        :type args: dict
        :returns: None
        :rtype: None
        Creates a new database and sets up necessary checks to avoid deleting user databases. It also provides a way
        to back up non-blockchain data for selective reimport to a new database if needed. The function initializes
        the configuration by combining the default configuration with the user-specific configuration from a YAML file.
         Then it adds any additional arguments to the configuration.

        Example:
        >> config = {...}
        >> tab = NchantdTab(config)
        >> tab.initApp()

    """

    def __init__(self, args):
        """Create new database eventually have checks in place so as not to
        delete user db also have a way of backing up any nonblockchain data
        so it can be selectively reimported to a new database if needed"""
        ucfg = f"{there}/_data_/user.yaml"
        self.config = kahndor.instruct(pxcfg).override(ucfg).addArgs(args)
        if log:
            logma.info(f"CONFIG {self.config.dikt.keys()}")
        super(NchantdTab, self).__init__("NchantdTab", self.config)
        self.initApp()


def runApplication(seq):
    """Run individual tabs with mock data for development purposes"""
    NchantdTab(seq)


if __name__ == "__main__":
    start = dt.datetime.now()
    print("Start", start)
    runApplication(argv)
    end = dt.datetime.now()
    print("End", end)
