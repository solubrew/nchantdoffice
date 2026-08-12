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
# import crow  # Commented out - not needed for local system

# crow.crowLoad removed

from kahndor import kahndor
from nchantrs.nchantrs import distortion, nchantment
from nchantrs.widgets.calculators.calculators import NchantdCalculator, NchantdGraphingCalculator
from nchantrs.widgets.media.editors.editors import NchantdEntryEditor
from nchantdoffice.nchantdoffice import NchantdOfficeCloak
from nchantdoffice.wizards.wizards import NchantdOfficeApplicationStartupWizard
from kahndor.logma import Logma

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
logma = Logma(__name__)
log = True

# ====================================================================================================================||
pxcfg = join(here, "_data_", "runMain.yaml")


def run(args: list[str]) -> None:
    """Run individual tabs with mock data for development purposes"""
    if args[1] == "calculator":
        """"""
        name = "NchantdCalculator"
        widget = NchantdCalculator
        distortion(name, args, widget)

    elif args[1] == "calculator":
        """"""
        name = "NchantdGraphingCalculator"
        widget = NchantdGraphingCalculator
        distortion(name, args, widget)

    elif args[1] == "note":
        name = "NchantdNote"
        widget = NchantdEntryEditor
        distortion(name, args, widget)

    elif args[1] == "import":
        app = NchantdOfficeCloak
        wizard = NchantdOfficeApplicationStartupWizard
        path = join("~", "iverse", "JDB", "1_Path", "JDB.ctd")
        nchantment("NchantdOffice", args, app, wizard, path)


if __name__ == "__main__":
    start = dt.datetime.now()
    logma.info("Start")
    run(argv)
    end = dt.datetime.now()
    logma.info(f"End Duration {end - start}")


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
