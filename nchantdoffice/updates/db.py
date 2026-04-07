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
from copy import deepcopy

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from condor import condor
from ogma.logma import Logma
from nchantrs.updates.db import NchantdDBUpdate

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)
if not log:
    logma.off()

# ====================================================================================================================||
pxcfg = join(here, "_data_", "db.yaml")


class NchantdOfficeDBUpdate(NchantdDBUpdate):
    """"""

    def __init__(self, parent, cfg=None):
        """"""
        super().__init__(parent, cfg)
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeDBUpdate").override(cfg))
        logma.info(f"Config: {self.config.dikt}")
        self.versions = deepcopy(self.config.dikt.get("versions"))
        logma.info(f"Versions: {self.versions}")

    def update_pyffice_document(self):
        """need to track and upgrade pyffice document versioning that are stored in the database"""
        logma.info(f"Updating pyffice document")
        # self.parent.pyffice_document.update(self.versions.dikt)
        updater = self.parent.codex.update()
        for document_type in updater.get_document_types():
            self.check_current_document_version(document_type)

        # need a schema that can be checked against each doc_media_content and app_media_content entry latest version
        # this will verify that the document fits the pyffice_version for that document type


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
