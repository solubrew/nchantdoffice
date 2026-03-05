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
from pyffice.document import PyfficePresentation

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "presentation.yaml")


class NchantdOfficePresentation(NchantdOfficeDocument, PyfficePresentation):
    """Presentation document - implements PyfficePresentation"""
    
    PYTYPE = 'presentation'
    
    @classmethod
    def get_pyffice_tools(cls):
        """Get toolbox tools for presentation documents"""
        return [
            {'id': 'slides', 'icon': 'presentation', 'label': 'Slide Sorter', 'method': 'show_slide_sorter'},
            {'id': 'themes', 'icon': 'palette', 'label': 'Themes', 'method': 'apply_theme'},
            {'id': 'transitions', 'icon': 'transition', 'label': 'Transitions', 'method': 'set_transition'},
            {'id': 'present', 'icon': 'play', 'label': 'Present', 'method': 'start_presentation'},
        ]
    
    def __init__(self, name="Nchantd Presentation", parent=None, cfg=None):
        """ """
        super().__init__(name, parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficePresentation"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        self.current_slide = 0

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
    
    def show_slide_sorter(self):
        """Show slide sorter view"""
        logma.info("Showing slide sorter...")
        return self
    
    def apply_theme(self):
        """Apply theme"""
        logma.info("Applying theme...")
        return self
    
    def set_transition(self):
        """Set transition"""
        logma.info("Setting transition...")
        return self
    
    def start_presentation(self):
        """Start presentation"""
        logma.info("Starting presentation...")
        return self


# ====================================================================================================================||
