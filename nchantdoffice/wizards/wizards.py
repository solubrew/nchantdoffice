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
from os import environ
from pathlib import Path
import datetime as dt
import time
import platform

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from condor import condor
from ogma.logma import Logma
from nchantrs.wizards.apps import NchantdApplicationStartupWizard

from nchantdoffice.updates.db import NchantdOfficeDBUpdate

from subtrix.utilities import uuid
from nchantrs.widgets.browsers.downloads import CodecDownloadThread
from nchantrs.widgets.browsers.codecs.h264 import OpenH264Downloader

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)
# logma.off()
# ====================================================================================================================||
pxcfg = join(here, "_data_", "wizards.yaml")
pxcfg = {}


class NchantdOfficeApplicationStartupWizard(NchantdApplicationStartupWizard):
    """Startup Wizard for Nchantd Office Application"""

    def __init__(self, app=None, cfg=None):
        """ """
        super().__init__(app, cfg)
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeApplicationStartupWizard")).override(cfg)
        cfg = {}
        self.db_update = NchantdOfficeDBUpdate(self, cfg)
        self.download_codec = None
        self.h264_codec = None

    def initView(self, args=None):
        """"""
        super().initView(args)
        self.add_journal_document()
        return self

    def add_journal_document(self):
        """"""
        did = uuid()
        widget = "journal"
        widgdata = {}
        doc_type = "journal"
        document = {
            "did": did,
            "name": "Journal",
            "compatibility": "pyffice",
            "type": "journal",
            "syntax": "plain-text",
            "description": "internal",
            "store_location": "",
            "encoding": "utf-8",
            "meta_data": {},
            "widget": widget,
            "pyffice_version_txt": self.app.model.instance.version,
        }
        logma.info(f"Journal Document Created: {document}")
        self.app.model.add_document_app(document, did, "0", 0, widget, widgdata, doc_type, "center", "db", False)
        return self

    def add_settings_document(self):
        """"""
        did = uuid()
        widget = "config"
        widgdata = {}
        doc_type = "config"
        document = {
            "did": did,
            "name": "Settings",
            "compatibility": "pyffice",
            "type": "config",
            "syntax": "plain-text",
            "description": "internal",
            "store_location": "",
            "encoding": "utf-8",
            "meta_data": {},
            "widget": widget,
        }
        logma.info(f"Settings Document Created: {document}")
        self.app.model.add_document_app(document, did, "0", 0, widget, widgdata, doc_type, "center", "db", False)

    def create_database_application(self):
        """"""
        super().create_database_application()
        return self

    def on_download_progress(self, event, *args, **kwargs):
        """"""

    def on_download_finished(self, event, *args, **kwargs):
        """"""
        self.downloaded = 1

    def run_application(self):
        """"""
        super().run_application()
        return self

    def run_application_install(self, paths):
        """"""
        super().run_application_install(paths)
        return self

    def run_application_update(self):
        """"""
        self.downloaded = 0
        # self.download_codec = CodecDownloadThread(OpenH264Downloader)
        # self.download_codec.progress.connect(self.on_download_progress)
        # self.download_codec.finished.connect(self.on_download_finished)
        # self.download_codec.start()
        downloader = OpenH264Downloader()
        downloader.download_and_extract()
        super().run_application_update()
        self.run_model_update()




        # while self.download_codec.isRunning():
        #     time.sleep(1)
        #     if self.downloaded == 1:
        #         break
        if not downloader.test():
            self.h264_codec = False
        else:
            self.h264_codec = True
        
        return self

    def run_model_update(self):
        """"""
        # Deactivate the Default Nchantrs Browser Type - this isn't really an update but a part of building on top of Nchantrs
        self.app.model.deactivate("app_document_type", uuid="066fae58-be2f-7095-8000-11dd4a720555")
        return self

    def run_install_complete(self):
        """"""
        super().run_install_complete()
        #This needs to be moved to something post wizard instance

        return self

# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
