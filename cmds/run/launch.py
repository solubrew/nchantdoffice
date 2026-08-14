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
import datetime as dt
from os.path import dirname, join

# ======================================3rd Party Library Modules=====================================================||
# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from kahndor.logma import Logma
from pyularity.launch import Launch

argv = None  # noqa: F821  # placeholder until refactor

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "launch.yaml")


class NchantdOfficeLaunch(Launch):
    """"""

    def __init__(self, cfg=None) -> None:
        """"""
        super().__init__(cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeLaunch").override(cfg))

    def launch_app(self) -> "NchantdOfficeLaunch":
        """"""
        super().launch_app()
        return self

    def set_scripts(self) -> "NchantdOfficeLaunch":
        """"""
        self.scripts = self.config.dikt.get("scripts", [])
        return self


if __name__ == "__main__":
    start = dt.datetime.now()
    logma.info("Start")
    NchantdOfficeLaunch().run(argv)
    end = dt.datetime.now()
    logma.info(f"End Duration {end - start}")
# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
