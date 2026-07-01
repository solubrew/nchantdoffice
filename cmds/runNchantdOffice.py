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
import os
from sys import argv
import datetime as dt
import sys
from pathlib import Path
import shutil

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||

sys.path.insert(0, "/home/solubrew/Documents/AIM")
import crow  # Commented out - not needed for local system

crow.crowLoad("NchantdOffice", "DELTA")
from kahndor import kahndor
from nchantrs.nchantrs import nchantment
from nchantdoffice.nchantdoffice import NchantdOfficeCloak
from nchantdoffice.wizards.wizards import NchantdOfficeApplicationStartupWizard
from kahndor.logma import Logma

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
logma = Logma(__name__)
log = True

# ====================================================================================================================||
pxcfg = join(here, "_data_", "runMain.yaml")


def restart():
    """"""
    shutil.rmtree(Path.home() / ".local" / "share" / "nchantdoffice")


def run(args):
    """Run individual tabs with mock data for development purposes

    python runNchantdOffice.py scratch setup - create new file
    python runNchantdOffice.py scratch - continue file
    python runNchantdOffice.py - use the wizard to setup
    """
    # restart()
    app = NchantdOfficeCloak
    wizard = NchantdOfficeApplicationStartupWizard
    nchantment("NchantdOffice", args, app, None, wizard)


if __name__ == "__main__":

    start = dt.datetime.now()
    logma.info("Start")
    run(argv)
    end = dt.datetime.now()
    logma.info(f"End Duration {end - start}")


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
