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
from pyffice.document import PyfficePDF

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "pdf.yaml")


class NchantdOfficePDF(NchantdOfficeDocument, PyfficePDF):
    """PDF document - implements PyfficePDF"""
    
    PYTYPE = 'pdf'
    
    @classmethod
    def get_pyffice_tools(cls):
        """Get toolbox tools for PDF documents"""
        return [
            {'id': 'thumbnails', 'icon': 'th', 'label': 'Thumbnails', 'method': 'show_thumbnails'},
            {'id': 'outline', 'icon': 'list', 'label': 'Outline', 'method': 'show_outline'},
            {'id': 'annotate', 'icon': 'pencil', 'label': 'Annotate', 'method': 'annotate_pdf'},
            {'id': 'sign', 'icon': 'signature', 'label': 'Sign', 'method': 'sign_pdf'},
        ]
    
    def __init__(self, name="Nchantd PDF", parent=None, cfg=None):
        """ """
        super().__init__(name, parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficePDF"))
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
    
    def show_thumbnails(self):
        """Show thumbnails"""
        logma.info("Showing thumbnails...")
        return self
    
    def show_outline(self):
        """Show outline"""
        logma.info("Showing outline...")
        return self
    
    def annotate_pdf(self):
        """Annotate PDF"""
        logma.info("Annotating PDF...")
        return self
    
    def sign_pdf(self):
        """Sign PDF"""
        logma.info("Signing PDF...")
        return self


# ====================================================================================================================||
