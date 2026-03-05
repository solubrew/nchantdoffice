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
from pyffice.document import PyfficeNotebook

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "notebooks.yaml")


class NchantdOfficeNotebook(NchantdOfficeDocument, PyfficeNotebook):
    """Notebook document - implements PyfficeNotebook"""
    
    PYTYPE = 'notebook'
    
    @classmethod
    def get_pyffice_tools(cls):
        """Get toolbox tools for notebook documents"""
        return [
            {'id': 'run_cell', 'icon': 'play', 'label': 'Run Cell', 'method': 'run_cell'},
            {'id': 'run_all', 'icon': 'forward', 'label': 'Run All', 'method': 'run_all_cells'},
            {'id': 'kernel', 'icon': 'terminal', 'label': 'Kernel', 'method': 'manage_kernel'},
            {'id': 'add_cell', 'icon': 'plus', 'label': 'Add Cell', 'method': 'add_cell'},
            {'id': 'delete_cell', 'icon': 'trash', 'label': 'Delete Cell', 'method': 'delete_cell'},
        ]
    
    def __init__(self, name="Nchantd Notebook", parent=None, cfg=None):
        """ """
        super().__init__(name, parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeNotebook"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        self.kernel = None

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
    
    def run_cell(self):
        """Run current cell"""
        logma.info("Running cell...")
        return self
    
    def run_all_cells(self):
        """Run all cells"""
        logma.info("Running all cells...")
        return self
    
    def manage_kernel(self):
        """Manage kernel"""
        logma.info("Managing kernel...")
        return self
    
    def add_cell(self):
        """Add cell"""
        logma.info("Adding cell...")
        return self
    
    def delete_cell(self):
        """Delete cell"""
        logma.info("Deleting cell...")
        return self


# ====================================================================================================================||
