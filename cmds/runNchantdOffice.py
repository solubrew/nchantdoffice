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
from sys import argv
import datetime as dt

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
import crow  # Commented out - not needed for local system

crow.crowLoad("NchantdOffice", "DELTA")

from condor import condor
from nchantrs.nchantrs import nchantment
from nchantdoffice.nchantdoffice import NchantdOfficeCloak
from nchantdoffice.wizards.wizards import NchantdOfficeApplicationStartupWizard
from ogma.logma import Logma

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
logma = Logma(__name__)
log = True

# ====================================================================================================================||
pxcfg = join(here, "_data_", "runMain.yaml")


def run(args):
    """Run individual tabs with mock data for development purposes

    python runNchantdOffice.py scratch setup - create new file
    python runNchantdOffice.py scratch - continue file
    python runNchantdOffice.py - use the wizard to setup
    """
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
