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
from kahndor import kahndor
from kahndor.logma import Logma
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
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeDBUpdate").override(cfg))
        # logma.info(f"Config: {self.config.dikt}")
        self.versions = deepcopy(self.config.dikt.get("versions"))
        # logma.info(f"Versions: {self.versions}")
        # T-NEW-058 §2.4 — guard against double-migration when both the
        # boot hook (run_on_launch) and a "Force upgrade" settings
        # button invoke update_pyffice_document() in the same process.
        # First call sets the lock and runs; subsequent calls are
        # no-ops. Logged at info level so the skip is visible.
        self._upgrade_lock: bool = False

    def update_pyffice_document(self):
        """Upgrade stored Pyffice documents to the latest SERIALIZATION_VERSION.

        T-NEW-058: guarded by ``self._upgrade_lock`` so the migration
        runs at most once per process. The lock is intentionally NOT
        reset on the second call — the intent is "upgrade once on
        boot, never again until the process restarts". Persistent
        re-runs require a restart (or an explicit ``force_upgrade()``
        method, deliberately not provided yet).
        """
        if self._upgrade_lock:
            logma.info(
                "[NchantdOfficeDBUpdate] update_pyffice_document: "
                "_upgrade_lock is True — skipping duplicate migration."
            )
            return self
        self._upgrade_lock = True
        logma.info(f"Updating pyffice document")
        # self.parent.pyffice_document.update(self.versions.dikt)
        updater = self.parent.model.codex.update()
        for document_type in updater.get_document_types():
            self.check_current_document_version(document_type)
        # need a schema that can be checked against each doc_media_content and app_media_content entry latest version
        # this will verify that the document fits the pyffice_version for that document type
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
