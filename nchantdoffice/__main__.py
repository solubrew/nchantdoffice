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
import os
import platform
# Set Qt platform for headless environments
if platform.system() != "Windows" and os.environ.get("DISPLAY") is None:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    
from os.path import abspath, dirname, join
from sys import argv
import datetime as dt

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
# import crow
# # crow.crowLoad removed
from condor import condor
from nchantrs.nchantrs import flection, nchantment
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
    cfg = {}
    profile = None
    if len(args) > 1:
        if args[1] == "multi":
            flection("NchantdOffice", args, app, cfg, wizard, profile)
            return
    nchantment("NchantdOffice", args, app, cfg, wizard, profile)


def main():
    run(argv)


if __name__ == "__main__":
    start = dt.datetime.now()
    logma.info("Start")
    main()
    end = dt.datetime.now()
    logma.info(f"End Duration {end - start}")


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
