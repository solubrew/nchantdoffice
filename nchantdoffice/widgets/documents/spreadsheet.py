# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
	docid:
	name:
	description: NchantdOffice implementation of PyfficeSpreadSheet and PyfficeMatrix
	version: 0.0.0.0.0.0
	authority: filesystem
	security: seclvl2
	<(WT)>: -32
"""
# -*- coding: utf-8 -*
# ======================================Standard Library Modules======================================================||
from os.path import dirname, join

# ======================================3rd Party Library Modules=====================================================||
from ogma.logma import Logma
from pyffice.spreadsheet.spreadsheet import PyfficeSpreadSheet, PyfficeMatrix
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
logma = Logma(__name__)
# logma.off()

# ====================================================================================================================||


class NchantdOfficeSpreadSheet(NchantdOfficeDocument, PyfficeSpreadSheet):
    """NchantdOffice implementation of PyfficeSpreadSheet.
    
    This class implements the PyfficeSpreadSheet document type for NchantdOffice,
    providing spreadsheet functionality with full GUI integration.
    
    Inherits from:
        - NchantdOfficeDocument: Base GUI document class
        - PyfficeSpreadSheet: Pyffice data model for spreadsheets
    
    Attributes:
        cells: Dictionary of cell addresses to cell objects
        charts: List of chart objects
        data: Pandas DataFrame representation
    """
    
    PYTYPE = PyfficeSpreadSheet
    
    def __init__(self, name=None, parent=None, cfg=None):
        """Initialize NchantdOfficeSpreadSheet document.
        
        Args:
            name: Document name
            parent: Parent widget/document
            cfg: Configuration dictionary
        """
        NchantdOfficeDocument.__init__(self, name, parent, cfg)
        PyfficeSpreadSheet.__init__(self, cfg)
        self.document_type = "spreadsheet"
    
    def get_pyffice_tools(self):
        """Get toolbox tools for spreadsheet documents.
        
        Returns:
            list: Toolbox configuration for spreadsheet operations
        """
        return [
            {'id': 'formula', 'icon': 'function', 'label': 'Formula Bar', 'method': 'show_formula_bar'},
            {'id': 'cell_format', 'icon': 'grid', 'label': 'Cell Format', 'method': 'format_cells'},
            {'id': 'charts', 'icon': 'chart-bar', 'label': 'Charts', 'method': 'insert_chart'},
            {'id': 'pivot', 'icon': 'pivot', 'label': 'Pivot Tables', 'method': 'create_pivot'},
            {'id': 'import', 'icon': 'import', 'label': 'Import Data', 'method': 'import_data'},
            {'id': 'filter', 'icon': 'filter', 'label': 'Filter', 'method': 'toggle_filter'},
            {'id': 'sort', 'icon': 'sort', 'label': 'Sort', 'method': 'sort_data'},
            {'id': 'freeze', 'icon': 'pin', 'label': 'Freeze Panes', 'method': 'freeze_panes'},
        ]
    
    def show_formula_bar(self):
        """Show the formula bar for cell editing.
        
        Returns:
            self
        """
        logma.info("Show formula bar")
        return self
    
    def format_cells(self, address=None, format=None):
        """Format cells at the given address.
        
        Args:
            address: Cell address (e.g., "A1")
            format: Format configuration
            
        Returns:
            self
        """
        logma.info(f"Format cells at {address}")
        return self
    
    def insert_chart(self, chart_type='bar', data_range=None):
        """Insert a chart into the spreadsheet.
        
        Args:
            chart_type: Type of chart ('bar', 'line', 'pie', etc.)
            data_range: Data range for the chart
            
        Returns:
            self
        """
        logma.info(f"Insert chart type={chart_type}")
        return self
    
    def create_pivot(self, data_range=None, rows=None, cols=None, values=None):
        """Create a pivot table.
        
        Args:
            data_range: Source data range
            rows: Row fields
            cols: Column fields
            values: Value fields
            
        Returns:
            self
        """
        logma.info("Create pivot table")
        return self
    
    def import_data(self, file_path=None, file_type='csv'):
        """Import data from external file.
        
        Args:
            file_path: Path to the file
            file_type: Type of file ('csv', 'excel', etc.)
            
        Returns:
            self
        """
        logma.info(f"Import data from {file_path}")
        return self
    
    def toggle_filter(self, range=None):
        """Toggle filter on a range.
        
        Args:
            range: Cell range to filter
            
        Returns:
            self
        """
        logma.info(f"Toggle filter on {range}")
        return self
    
    def sort_data(self, range=None, column=None, ascending=True):
        """Sort data in a range.
        
        Args:
            range: Cell range to sort
            column: Column to sort by
            ascending: Sort direction
            
        Returns:
            self
        """
        logma.info(f"Sort data by column {column}")
        return self
    
    def freeze_panes(self, address=None):
        """Freeze panes at the given address.
        
        Args:
            address: Cell address to freeze at
            
        Returns:
            self
        """
        logma.info(f"Freeze panes at {address}")
        return self


class NchantdOfficeMatrix(NchantdOfficeDocument, PyfficeMatrix):
    """NchantdOffice implementation of PyfficeMatrix (workbook).
    
    This class implements the PyfficeMatrix document type for NchantdOffice,
    providing multi-sheet workbook functionality with full GUI integration.
    
    Inherits from:
        - NchantdOfficeDocument: Base GUI document class
        - PyfficeMatrix: Pyffice data model for matrix/workbook
    
    Attributes:
        sheets: Dictionary of sheet names to sheet objects
        active_worksheet: Currently active worksheet
    """
    
    PYTYPE = PyfficeMatrix
    
    def __init__(self, name=None, parent=None, cfg=None):
        """Initialize NchantdOfficeMatrix document.
        
        Args:
            name: Document name
            parent: Parent widget/document
            cfg: Configuration dictionary
        """
        NchantdOfficeDocument.__init__(self, name, parent, cfg)
        PyfficeMatrix.__init__(self, cfg)
        self.document_type = "matrix"
    
    def get_pyffice_tools(self):
        """Get toolbox tools for matrix/workbook documents.
        
        Returns:
            list: Toolbox configuration for matrix operations
        """
        return [
            {'id': 'add_sheet', 'icon': 'plus', 'label': 'Add Sheet', 'method': 'add_worksheet'},
            {'id': 'delete_sheet', 'icon': 'trash', 'label': 'Delete Sheet', 'method': 'delete_worksheet'},
            {'id': 'rename_sheet', 'icon': 'edit', 'label': 'Rename Sheet', 'method': 'rename_worksheet'},
            {'id': 'move_sheet', 'icon': 'move', 'label': 'Move Sheet', 'method': 'move_worksheet'},
            {'id': 'formula', 'icon': 'function', 'label': 'Formula', 'method': 'show_formula_bar'},
            {'id': 'pivot', 'icon': 'pivot', 'label': 'Pivot Table', 'method': 'create_pivot'},
            {'id': 'chart', 'icon': 'chart', 'label': 'Insert Chart', 'method': 'insert_chart'},
            {'id': 'protect', 'icon': 'lock', 'label': 'Protect Sheet', 'method': 'protect_sheet'},
        ]
    
    def add_worksheet(self, name=None, tabn=None):
        """Add a new worksheet to the workbook.
        
        Args:
            name: Name of the new sheet
            tabn: Tab number
            
        Returns:
            NchantdOfficeSpreadSheet: New worksheet
        """
        logma.info(f"Add worksheet: {name}")
        return self
    
    def delete_worksheet(self, name=None):
        """Delete a worksheet from the workbook.
        
        Args:
            name: Name of the sheet to delete
            
        Returns:
            self
        """
        logma.info(f"Delete worksheet: {name}")
        return self
    
    def rename_worksheet(self, old_name, new_name):
        """Rename a worksheet.
        
        Args:
            old_name: Current name
            new_name: New name
            
        Returns:
            self
        """
        logma.info(f"Rename worksheet: {old_name} -> {new_name}")
        return self
    
    def move_worksheet(self, name, position):
        """Move a worksheet to a new position.
        
        Args:
            name: Name of the sheet
            position: New position
            
        Returns:
            self
        """
        logma.info(f"Move worksheet {name} to position {position}")
        return self
    
    def protect_sheet(self, name=None, password=None):
        """Protect a worksheet.
        
        Args:
            name: Name of the sheet
            password: Protection password
            
        Returns:
            self
        """
        logma.info(f"Protect sheet: {name}")
        return self
    
    def insert_chart(self, sheet_name=None, chart_type='bar', data_range=None):
        """Insert a chart into a worksheet.
        
        Args:
            sheet_name: Target sheet name
            chart_type: Type of chart
            data_range: Data range for the chart
            
        Returns:
            self
        """
        logma.info(f"Insert chart in {sheet_name}")
        return self
    
    def create_pivot(self, sheet_name=None, data_range=None, rows=None, cols=None, values=None):
        """Create a pivot table in a worksheet.
        
        Args:
            sheet_name: Target sheet name
            data_range: Source data range
            rows: Row fields
            cols: Column fields
            values: Value fields
            
        Returns:
            self
        """
        logma.info(f"Create pivot in {sheet_name}")
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
