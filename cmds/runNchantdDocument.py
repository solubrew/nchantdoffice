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
from os.path import abspath, dirname, join, isfile
from sys import argv
import datetime as dt

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
# import crow  # Commented out - not needed for local system
from docutils.nodes import abbreviation

# crow.crowLoad removed

from kahndor import kahndor
from kahndor.logma import Logma
from nchantrs.nchantrs import nchantment, distortion
from nchantdoffice.widgets.documents.atnrg.browsers import NchantdOfficeWebBrowser
from nchantdoffice.widgets.documents.media.scripts import NchantdOfficeScript
from nchantrs.nchantrs import aberration

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
logma = Logma(__name__)
log = True

# ====================================================================================================================||
pxcfg = join(here, "_data_", "runMain.yaml")


def run(args):
    """Run individual tabs with mock data for development purposes"""
    cfg = {}
    if args[1] == "cad" or args[1] == "all":
        cfg["path"] = join(here, "..", "test_nchantdoffice", "fixtures", "")
        distortion("NchantdOffice", args, NchantdOfficeCAD, None)

    if args[1] == "form" or args[1] == "all":
        cfg["path"] = join(here, "..", "test_nchantdoffice", "fixtures", "")
        nchantment("NchantdOffice", args, NchantdOfficeFormCape, None, cfg)

    if args[1] == "image" or args[1] == "all":
        args["path"] = join(here, "..", "test_nchantdoffice", "fixtures", "test.png")
        nchantment("NchantdOffice", args, NchantdOfficeImageCape, None, cfg)

    if args[1] == "matrix" or args[1] == "all":
        args["path"] = join(here, "..", "test_nchantdoffice", "fixtures", "test.csv")
        nchantment("NchantdOffice", args, NchantdOfficeMatrixCape, None, cfg)

    if args[1] == "pdf" or args[1] == "all":
        args["path"] = join(here, "..", "test_nchantdoffice", "fixtures", "test.pdf")
        nchantment("NchantdOffice", args, NchantdOfficePDFCape, None, cfg)

    if args[1] == "presentation" or args[1] == "all":
        args["path"] = join(here, "..", "test_nchantdoffice", "fixtures", "test.pdf")
        nchantment("NchantdOffice", args, NchantdOfficePresentationCape, None, cfg)

    if args[1] == "prompt" or args[1] == "all":
        args["path"] = join(here, "..", "test_nchantdoffice", "fixtures", "test.pdf")
        nchantment("NchantdOffice", args, NchantdOfficePromptCape, None, cfg)

    if args[1] == "script" or args[1] == "all":
        cfg["path"] = join(here, "..", "test_nchantdoffice", "fixtures", "test.html")
        aberration("NchantdOffice", args, NchantdOfficeScript, cfg)

    if args[1] == "web" or args[1] == "all":
        cfg["url"] = "https://www.google.com"
        aberration("NchantdOffice", args, NchantdOfficeWebBrowser, cfg)


if __name__ == "__main__":
    start = dt.datetime.now()
    logma.info("Start")
    run(argv)
    end = dt.datetime.now()
    logma.info(f"End Duration {end - start}")


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
