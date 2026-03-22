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
from pyffice.forms.surveys import PyfficeSurvey, PyfficeResponse

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "surveys.yaml")


class NchantdOfficeSurvey(NchantdOfficeDocument, PyfficeSurvey):
    """Survey document - implements PyfficeSurvey"""
    
    PYTYPE = 'survey'
    
    @classmethod
    def get_pyffice_tools(cls):
        """Get toolbox tools for survey documents"""
        return [
            {'id': 'questions', 'icon': 'list', 'label': 'Questions', 'method': 'manage_questions'},
            {'id': 'responses', 'icon': 'inbox', 'label': 'Responses', 'method': 'view_responses'},
            {'id': 'analyze', 'icon': 'chart', 'label': 'Analyze', 'method': 'analyze_results'},
            {'id': 'share', 'icon': 'share', 'label': 'Share', 'method': 'share_survey'},
        ]
    
    def __init__(self, name="Nchantd Survey", parent=None, cfg=None):
        """ """
        super().__init__(name, parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeSurvey"))
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
    
    def manage_questions(self):
        """Manage survey questions"""
        logma.info("Managing survey questions...")
        return self
    
    def view_responses(self):
        """View survey responses"""
        logma.info("Viewing survey responses...")
        return self
    
    def analyze_results(self):
        """Analyze survey results"""
        logma.info("Analyzing survey results...")
        return self
    
    def share_survey(self):
        """Share survey"""
        logma.info("Sharing survey...")
        return self


class NchantdOfficeResponse(NchantdOfficeDocument, PyfficeResponse):
    """Response document - implements PyfficeResponse"""
    
    PYTYPE = 'response'
    
    @classmethod
    def get_pyffice_tools(cls):
        """Get toolbox tools for response documents"""
        return [
            {'id': 'view', 'icon': 'eye', 'label': 'View', 'method': 'view_response'},
            {'id': 'export', 'icon': 'download', 'label': 'Export', 'method': 'export_response'},
            {'id': 'analyze', 'icon': 'chart', 'label': 'Analyze', 'method': 'analyze_response'},
        ]
    
    def __init__(self, name="Nchantd Response", parent=None, cfg=None):
        """ """
        super().__init__(name, parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeResponse"))
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
    
    def view_response(self):
        """View response"""
        logma.info("Viewing response...")
        return self
    
    def export_response(self):
        """Export response"""
        logma.info("Exporting response...")
        return self
    
    def analyze_response(self):
        """Analyze response"""
        logma.info("Analyzing response...")
        return self


# ====================================================================================================================||
