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

# -*- coding: utf-8 -*-
# ======================================Standard Library Modules======================================================||
from __future__ import annotations
from os.path import abspath, dirname, join
import datetime as dt
from sys import argv
from typing import Self

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from kahndor.logma import Logma
from pyularity.pyularity import Run
from nchantrs.nchantrs import nchantment
from nchantdoffice.nchantdoffice import NchantdOfficeCloak
from nchantdoffice.wizards.wizards import NchantdOfficeApplicationStartupWizard

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "run.yaml")


class NchantdOfficeRun(Run):
    """"""

    def __init__(self, cfg=None) -> None:
        """ """
        super().__init__(cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeLaunch").override(cfg))

    def run(self, args: list[str]) -> Self:
        """Run individual tabs with mock data for development purposes

        python runNchantdOffice.py scratch setup - create new file
        python runNchantdOffice.py scratch - continue file
        python runNchantdOffice.py - use the wizard to setup
        """
        super().run(args)
        app = NchantdOfficeCloak
        wizard = NchantdOfficeApplicationStartupWizard
        nchantment("NchantdOffice", args, app, None, wizard)
        return self


if __name__ == "__main__":
    start = dt.datetime.now()
    logma.info("Start")
    NchantdOfficeRun().run(argv)
    end = dt.datetime.now()
    logma.info(f"End Duration {end - start}")


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
