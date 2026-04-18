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
from os.path import dirname, join

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from nchantrs.libraries import pyqt
from nchantrs.packages.packages import NchantdToolsPackage
from nchantrs.wizards.pages import NchantdWizardPage
from kahndor.logma import Logma

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "nchantdlibrary.yaml")


class NchantdNewNchantdLibraryApplicationPage(NchantdWizardPage):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = kahndor.instruct(pxcfg).select("NchantdNewAccountNchantdLibraryPage")
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        super(NchantdNewNchantdLibraryApplicationPage, self).__init__(self.parent, self.config)

    def initModel(self):
        """"""
        super().initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        # only offer if the user is performing an install and not running as a stand Alone option...maybe?
        # Ask for how the user wants to manage the library
        # files in place
        # files relocated to a structured storage
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdLibraryToolsPackage(NchantdToolsPackage):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = kahndor.instruct(pxcfg).select("Nchantd")
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        super(NchantdLibraryToolsPackage, self).__init__(self.parent, self.config)

    def add_library_service_site(self, pid, name):
        """"""
        services = self.app.model.get_tab_set("library_catalog_site")

        self.add_tabs(services)
        return self

    def add_cloud_storage_service_site(self, pid):
        """"""
        pid = self.add_node(pid)

        self.add_tabs(online_services)

    def initModel(self):
        """"""
        return self

    def initView(self):
        """"""
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdFileViewer(pyqt.QTreeView):
    def __init__(self):
        pyqt.QTreeView.__init__(self)
        model = pyqt.QFileSystemModel()
        model.setRootPath("/home/solubrew")
        self.setModel(model)
        self.doubleClicked.connect(self.test)

    def test(self, signal):
        file_path = self.model().filePath(signal)
        print(file_path)


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
