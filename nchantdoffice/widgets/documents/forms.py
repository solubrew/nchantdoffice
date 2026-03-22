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
from pyffice.forms.forms import PyfficeForm

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "forms.yaml")


class NchantdOfficeForm(NchantdOfficeDocument, PyfficeForm):
    """Form document - implements PyfficeForm"""
    
    PYTYPE = 'form'
    
    @classmethod
    def get_pyffice_tools(cls):
        """Get toolbox tools for form documents"""
        return [
            {'id': 'add_field', 'icon': 'plus', 'label': 'Add Field', 'method': 'add_field'},
            {'id': 'preview', 'icon': 'eye', 'label': 'Preview', 'method': 'preview_form'},
            {'id': 'validate', 'icon': 'check', 'label': 'Validate', 'method': 'validate_form'},
            {'id': 'submit', 'icon': 'paper-plane', 'label': 'Submit', 'method': 'submit_form'},
        ]
    
    def __init__(self, name="Nchantd Form", parent=None, cfg=None):
        """ """
        super().__init__(name, parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeForm"))
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
    
    def add_field(self):
        """Add field to form"""
        logma.info("Adding field to form...")
        return self
    
    def preview_form(self):
        """Preview form"""
        logma.info("Previewing form...")
        return self
    
    def validate_form(self):
        """Validate form"""
        logma.info("Validating form...")
        return self
    
    def submit_form(self):
        """Submit form"""
        logma.info("Submitting form...")
        return self


# ====================================================================================================================||
