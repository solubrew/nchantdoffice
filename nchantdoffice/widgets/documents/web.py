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
from nchantrs.libraries import pyqt

# ======================================Solutions Brewer Library Modules==============================================||
from condor import condor
from ogma.logma import Logma
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument
from pyffice.web.web import PyfficeWebPage, PyfficeWebBrowser

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "web.yaml")


class NchantdOfficeWebPage(NchantdOfficeDocument, PyfficeWebPage):
    """Web page document - implements PyfficeWebPage"""
    
    PYTYPE = 'webpage'
    
    @classmethod
    def get_pyffice_tools(cls):
        """Get toolbox tools for web page documents"""
        return [
            {'id': 'refresh', 'icon': 'refresh', 'label': 'Refresh', 'method': 'refresh_page'},
            {'id': 'back', 'icon': 'arrow-left', 'label': 'Back', 'method': 'go_back'},
            {'id': 'forward', 'icon': 'arrow-right', 'label': 'Forward', 'method': 'go_forward'},
            {'id': 'bookmark', 'icon': 'bookmark', 'label': 'Bookmark', 'method': 'add_bookmark'},
        ]
    
    def __init__(self, name="Nchantd Web Page", parent=None, cfg=None):
        """ """
        super().__init__(name, parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeWebPage"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        super().initView(cfg)
        return self

    def initWidget(self, cfg=None):
        """"""
        self.initModel(cfg)
        self.initView(cfg)
        return self
    
    def refresh_page(self):
        """Refresh page"""
        logma.info("Refreshing page...")
        return self
    
    def go_back(self):
        """Go back"""
        logma.info("Going back...")
        return self
    
    def go_forward(self):
        """Go forward"""
        logma.info("Going forward...")
        return self
    
    def add_bookmark(self):
        """Add bookmark"""
        logma.info("Adding bookmark...")
        return self


class NchantdOfficeWebBrowser(NchantdOfficeDocument, PyfficeWebBrowser):
    """Web browser document - implements PyfficeWebBrowser"""
    
    PYTYPE = 'webbrowser'
    
    @classmethod
    def get_pyffice_tools(cls):
        """Get toolbox tools for web browser documents"""
        return [
            {'id': 'url_bar', 'icon': 'link', 'label': 'URL Bar', 'method': 'show_url_bar'},
            {'id': 'tabs', 'icon': 'layers', 'label': 'Browser Tabs', 'method': 'manage_tabs'},
            {'id': 'history', 'icon': 'clock', 'label': 'History', 'method': 'show_history'},
            {'id': 'downloads', 'icon': 'download', 'label': 'Downloads', 'method': 'show_downloads'},
            {'id': 'settings', 'icon': 'settings', 'label': 'Settings', 'method': 'browser_settings'},
        ]
    
    def __init__(self, name="Nchantd Web Browser", parent=None, cfg=None):
        """ """
        super().__init__(name, parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeWebBrowser"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        super().initView(cfg)
        return self

    def initWidget(self, cfg=None):
        """"""
        self.initModel(cfg)
        self.initView(cfg)
        return self
    
    def show_url_bar(self):
        """Show URL bar"""
        logma.info("Showing URL bar...")
        return self
    
    def manage_tabs(self):
        """Manage browser tabs"""
        logma.info("Managing browser tabs...")
        return self
    
    def show_history(self):
        """Show browsing history"""
        logma.info("Showing history...")
        return self
    
    def show_downloads(self):
        """Show downloads"""
        logma.info("Showing downloads...")
        return self
    
    def browser_settings(self):
        """Browser settings"""
        logma.info("Opening browser settings...")
        return self


# ====================================================================================================================||
