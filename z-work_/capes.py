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
from condor import condor
from ogma.logma import Logma
from nchantdoffice.dialogs.dialogs import NchantdOfficeDocumentCape
from nchantrs.widgets.media.images import NchantdImage
from nchantrs.widgets.browsers.browsers import NchantdWebBrowser

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", ".yaml")


class NchantdOfficeCADCape(NchantdOfficeDocumentCape):
    """"""

    def __init__(self, name, instance=None, cfg=None, args=None):
        """ """
        name = "NchantdOfficeCAD"
        self.config = condor.Instruct(pxcfg).select(name)
        super().__init__(name, instance, None, None, args)
        self.config.override(cfg)
        self.document = None

    def auto_size(self):
        """"""
        width, height = self.document.open_document.get_page_size()
        self.main.setMinimumSize(width / 2, height / 2)
        self.main.showMaximized()
        return self

    def initModel(self):
        """"""
        super().initModel()
        self.model.initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        self.document = NchantdOfficeCAD(self, self.config)
        self.document.set_file_path(self.file_path)
        self.document.initWidget()
        self.main.layout.addWidget(self.document)
        self.auto_size()
        return self

    def load_file(self, filename):
        """"""
        logma.info(f"Load File: {filename}")
        self.file_path = filename
        return self


class NchantdOfficeChartCape(NchantdOfficeDocumentCape):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        name = "NchantdOfficeChart"
        self.config = condor.Instruct(pxcfg).select(name)
        super().__init__(name, instance, None, None, args)
        self.config.override(cfg)
        self.document = None

    def auto_size(self):
        """"""
        width, height = self.document.open_document.get_page_size()
        self.main.setMinimumSize(width / 2, height / 2)
        self.main.showMaximized()
        return self

    def initModel(self):
        """"""
        super().initModel()
        self.model.initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        self.document = NchantdChart(self, self.config)
        self.document.set_file_path(self.file_path)
        self.document.initWidget()
        self.main.layout.addWidget(self.document)
        self.auto_size()
        return self

    def load_file(self, filename):
        """"""
        logma.info(f"Load File: {filename}")
        self.file_path = filename
        return self


class NchantdOfficeDiagramCape(NchantdOfficeDocumentCape):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        name = "NchantdDiagram"
        self.config = condor.Instruct(pxcfg).select(name)
        super().__init__(name, instance, None, None, args)
        self.config.override(cfg)
        self.document = None

    def auto_size(self):
        """"""
        width, height = self.document.open_document.get_page_size()
        self.main.setMinimumSize(width / 2, height / 2)
        self.main.showMaximized()
        return self

    def initModel(self):
        """"""
        super().initModel()
        self.model.initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        self.document = NchantdDiagram(self, self.config)
        self.document.set_file_path(self.file_path)
        self.document.initWidget()
        self.main.layout.addWidget(self.document)
        self.auto_size()
        return self

    def load_file(self, filename):
        """"""
        logma.info(f"Load File: {filename}")
        self.file_path = filename
        return self


class NchantdOfficeFormCape(NchantdOfficeDocumentCape):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        name = "NchantdForm"
        self.config = condor.Instruct(pxcfg).select(name)
        super().__init__(name, instance, None, None, args)
        self.config.override(cfg)
        self.document = None

    def auto_size(self):
        """"""
        width, height = self.document.open_document.get_page_size()
        self.main.setMinimumSize(width / 2, height / 2)
        self.main.showMaximized()
        return self

    def initModel(self):
        """"""
        super().initModel()
        self.model.initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        self.document = NchantdForm(self, self.config)
        self.document.set_file_path(self.file_path)
        self.document.initWidget()
        self.main.layout.addWidget(self.document)
        self.auto_size()
        return self

    def load_file(self, filename):
        """"""
        logma.info(f"Load File: {filename}")
        self.file_path = filename
        return self


class NchantdOfficeImageCape(NchantdOfficeDocumentCape):
    """"""

    def __init__(self, parent=None, cfg=None, args=None):
        """ """
        self.parent = parent
        name = "NchantdImage"
        self.config = condor.Instruct(pxcfg).select(name)
        super().__init__(name, instance, None, None, args)
        self.config.override(cfg)
        self.document = None

    def auto_size(self):
        """"""
        # width, height = self.document.open_document.get_page_size()
        # self.main.setMinimumSize(width / 2, height / 2)
        self.main.showMaximized()
        return self

    def initModel(self):
        """"""
        super().initModel()
        self.model.initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        self.document = NchantdImage(self, self.config)
        self.document.set_file_path(self.file_path)
        self.document.initWidget()
        self.main.layout.addWidget(self.document)
        self.auto_size()
        return self

    def load_file(self, filename):
        """"""
        logma.info(f"Load File: {filename}")
        self.file_path = filename
        return self


class NchantdOfficeMatrixCape(NchantdOfficeDocumentCape):
    """"""

    def __init__(self, parent=None, cfg=None, args=None):
        """ """
        self.parent = parent
        name = "NchantdMatrix"
        self.config = condor.Instruct(pxcfg).select(name)
        super().__init__(name, instance, None, None, args)
        self.config.override(cfg)
        self.document = None
        self.document_initialized = False

    def auto_size(self):
        """"""
        # width, height = self.document.open_document.get_page_size()
        # self.main.setMinimumSize(width / 2, height / 2)
        self.main.showMaximized()
        return self

    def initModel(self):
        """"""
        super().initModel()
        self.model.initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        self.document = NchantdMatrix(self, self.config)
        self.document.set_file_path(self.file_path)
        self.document.initWidget()
        self.main.layout.addWidget(self.document)
        self.auto_size()
        return self

    def load_file(self, filename):
        """"""
        logma.info(f"Load File: {filename}")
        self.file_path = filename
        return self


class NchantdOfficePDFCape(NchantdOfficeDocumentCape):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        name = "NchantdPDF"
        self.config = condor.Instruct(pxcfg).select(name)
        super().__init__(name, instance, None, None, args)
        self.config.override(cfg)
        self.document = None

    def auto_size(self):
        """"""
        width, height = self.document.open_document.get_page_size()
        self.main.setMinimumSize(width / 2, height / 2)
        self.main.showMaximized()
        return self

    def initModel(self):
        """"""
        super().initModel()
        self.model.initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        self.document = NchantdPDF(self, self.config)
        self.document.set_file_path(self.file_path)
        self.document.initWidget()
        self.main.layout.addWidget(self.document)
        self.auto_size()
        return self

    def load_file(self, filename):
        """"""
        logma.info(f"Load File: {filename}")
        self.file_path = filename
        return self


class NchantdOfficePresentationCape(NchantdOfficeDocumentCape):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        name = "NchantdPresentation"
        self.config = condor.Instruct(pxcfg).select(name)
        super().__init__(name, instance, None, None, args)
        self.config.override(cfg)
        self.document = None

    def auto_size(self):
        """"""
        width, height = self.document.open_document.get_page_size()
        self.main.setMinimumSize(width / 2, height / 2)
        self.main.showMaximized()
        return self

    def initModel(self):
        """"""
        super().initModel()
        self.model.initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        self.document = NchantdPresentation(self, self.config)
        self.document.set_file_path(self.file_path)
        self.document.initWidget()
        self.main.layout.addWidget(self.document)
        self.auto_size()
        return self

    def load_file(self, filename):
        """"""
        logma.info(f"Load File: {filename}")
        self.file_path = filename
        return self


class NchantdOfficePromptCape(NchantdOfficeDocumentCape):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        name = "NchantdPrompt"
        self.config = condor.Instruct(pxcfg).select(name)
        super().__init__(name, instance, None, None, args)
        self.config.override(cfg)
        self.document = None

    def auto_size(self):
        """"""
        width, height = self.document.open_document.get_page_size()
        self.main.setMinimumSize(width / 2, height / 2)
        self.main.showMaximized()
        return self

    def initModel(self):
        """"""
        super().initModel()
        self.model.initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        self.document = NchantdPrompt(self, self.config)
        self.document.set_file_path(self.file_path)
        self.document.initWidget()
        self.main.layout.addWidget(self.document)
        self.auto_size()
        return self

    def load_file(self, filename):
        """"""
        logma.info(f"Load File: {filename}")
        self.file_path = filename
        return self


class NchantdOfficeScriptCape(NchantdOfficeDocumentCape):
    """"""

    def __init__(self, parent=None, cfg=None, args=None):
        """ """
        self.parent = parent
        name = "NchantdScript"
        self.config = condor.Instruct(pxcfg).select(name)
        super().__init__(name, instance, None, None, args)
        self.config.override(cfg)
        self.document = None
        self.document_initialized = False

    def auto_size(self):
        """"""
        # width, height = self.document.open_document.get_page_size()
        # self.main.setMinimumSize(width / 2, height / 2)
        self.main.showMaximized()
        return self

    def initModel(self):
        """"""
        super().initModel()
        self.model.initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        self.document = NchantdScript(self, self.config)
        self.document.set_file_path(self.file_path)
        self.document.initWidget()
        self.main.layout.addWidget(self.document)
        self.auto_size()
        return self

    def load_file(self, filename):
        """"""
        logma.info(f"Load File: {filename}")
        self.file_path = filename
        return self


class NchantdOfficeWebBrowserCape(NchantdOfficeDocumentCape):
    """"""

    def __init__(self, name, instance, cfg=None, args=None):
        """ """
        self.config = condor.Instruct(pxcfg).select(name)
        super().__init__(name, instance, None, None, args)
        self.config.override(cfg)
        self.document = None
        self.document_initialized = False
        self.url = "https://www.tldraw.com/"
        self.path = ".config/NchantdOfficeWebBrowserCape/"

    def auto_size(self):
        """"""
        # width, height = self.document.open_document.get_page_size()
        # self.main.setMinimumSize(width / 2, height / 2)
        self.main.showMaximized()
        return self

    def initModel(self):
        """"""
        super().initModel()
        self.model.initModel()
        return self

    def initView(self, cfg=None):
        """"""
        super().initView(cfg)
        self.document = NchantdWebBrowser(self, self.config)
        # self.document.set_url_path(self.url)
        self.document.initWidget(self.url)
        self.main.layout.addWidget(self.document)
        self.auto_size()
        return self

    def load_url(self, path):
        """"""
        self.url = path

    def load_file(self, filename):
        """"""
        logma.info(f"Load File: {filename}")
        self.file_path = filename
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
