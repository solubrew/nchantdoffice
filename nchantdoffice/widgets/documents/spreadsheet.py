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
from pyffice.document import PyfficeSpreadsheet, PyfficeMatrix

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "spreadsheet.yaml")


class NchantdOfficeSpreadSheet(NchantdOfficeDocument, PyfficeSpreadsheet):
    """Spreadsheet document - implements PyfficeSpreadsheet"""
    
    PYTYPE = 'spreadsheet'
    
    @classmethod
    def get_pyffice_tools(cls):
        """Get toolbox tools for spreadsheet documents"""
        return [
            {'id': 'formula', 'icon': 'function', 'label': 'Formula', 'method': 'insert_formula'},
            {'id': 'charts', 'icon': 'chart', 'label': 'Charts', 'method': 'insert_chart'},
            {'id': 'pivot', 'icon': 'table', 'label': 'Pivot Table', 'method': 'create_pivot'},
            {'id': 'filter', 'icon': 'filter', 'label': 'Filter', 'method': 'toggle_filter'},
            {'id': 'sort', 'icon': 'sort', 'label': 'Sort', 'method': 'sort_data'},
            {'id': 'import', 'icon': 'upload', 'label': 'Import', 'method': 'import_data'},
        ]
    
    def __init__(self, name="Nchantd Spreadsheet", parent=None, cfg=None):
        """ """
        super().__init__(name, parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeSpreadSheet"))
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
    
    def insert_formula(self):
        """Insert formula"""
        logma.info("Inserting formula...")
        return self
    
    def insert_chart(self):
        """Insert chart"""
        logma.info("Inserting chart...")
        return self
    
    def create_pivot(self):
        """Create pivot table"""
        logma.info("Creating pivot table...")
        return self
    
    def toggle_filter(self):
        """Toggle filter"""
        logma.info("Toggling filter...")
        return self
    
    def sort_data(self):
        """Sort data"""
        logma.info("Sorting data...")
        return self
    
    def import_data(self):
        """Import data"""
        logma.info("Importing data...")
        return self


class NchantdOfficeMatrix(NchantdOfficeDocument, PyfficeMatrix):
    """Matrix document - implements PyfficeMatrix"""
    
    PYTYPE = 'matrix'
    
    @classmethod
    def get_pyffice_tools(cls):
        """Get toolbox tools for matrix documents"""
        return [
            {'id': 'sheet', 'icon': 'layers', 'label': 'Sheet', 'method': 'manage_sheets'},
            {'id': 'formula', 'icon': 'function', 'label': 'Formula', 'method': 'insert_formula'},
            {'id': 'pivot', 'icon': 'table', 'label': 'Pivot', 'method': 'create_pivot'},
            {'id': 'chart', 'icon': 'chart', 'label': 'Chart', 'method': 'insert_chart'},
            {'id': 'protect', 'icon': 'lock', 'label': 'Protect', 'method': 'protect_sheet'},
        ]
    
    def __init__(self, name="Nchantd Matrix", parent=None, cfg=None):
        """ """
        super().__init__(name, parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeMatrix"))
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
    
    def manage_sheets(self):
        """Manage sheets"""
        logma.info("Managing sheets...")
        return self
    
    def insert_formula(self):
        """Insert formula"""
        logma.info("Inserting formula...")
        return self
    
    def create_pivot(self):
        """Create pivot"""
        logma.info("Creating pivot...")
        return self
    
    def insert_chart(self):
        """Insert chart"""
        logma.info("Inserting chart...")
        return self
    
    def protect_sheet(self):
        """Protect sheet"""
        logma.info("Protecting sheet...")
        return self


# ====================================================================================================================||
