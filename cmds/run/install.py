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
import datetime as dt

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from kahndor.logma import Logma
from pyularity.pyularity import Package

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "install.yaml")


class NchantdOfficeInstall(Package):
    """"""

    def __init__(self, cfg=None):
        """Initialise the NchantdOffice installer and log the start.

        Records the config keys we actually consume (vs. the full
        cfg dict) so an operator can confirm what was passed in
        without dumping the entire payload. This is the canonical
        entry-point for installation — every install run should be
        visible in the log without grepping.
        """
        super().__init__(cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeInstall").override(cfg))
        cfg_keys = sorted((cfg or {}).keys()) if isinstance(cfg, dict) else []
        logma.info(f"NchantdOfficeInstall init: cfg_keys={cfg_keys}")

    def get_manifest(self):
        """"""
        # Here is where the service to NchantdOffice.com is connected for all users
        # could offload this to Ethereum or another blockchain
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
