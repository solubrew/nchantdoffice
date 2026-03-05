# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
	docid:
	name:
	description: NchantdOffice implementation of PyfficeNotebook
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
from pyffice.notebooks.notebooks import PyfficeNotebook
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
logma = Logma(__name__)
# logma.off()

# ====================================================================================================================||


class NchantdOfficeNotebook(NchantdOfficeDocument, PyfficeNotebook):
    """NchantdOffice implementation of PyfficeNotebook.
    
    This class implements the PyfficeNotebook document type for NchantdOffice,
    providing notebook/cell-based document functionality with full GUI integration.
    
    Inherits from:
        - NchantdOfficeDocument: Base GUI document class
        - PyfficeNotebook: Pyffice data model for notebooks
    
    Attributes:
        cells: List of notebook cells
        notebook: Notebook configuration and metadata
    """
    
    PYTYPE = PyfficeNotebook
    
    def __init__(self, name=None, parent=None, cfg=None):
        """Initialize NchantdOfficeNotebook document.
        
        Args:
            name: Document name
            parent: Parent widget/document
            cfg: Configuration dictionary
        """
        NchantdOfficeDocument.__init__(self, name, parent, cfg)
        PyfficeNotebook.__init__(self, cfg)
        self.document_type = "notebook"
    
    def get_pyffice_tools(self):
        """Get toolbox tools for notebook documents.
        
        Returns:
            list: Toolbox configuration for notebook operations
        """
        return [
            {'id': 'run_cell', 'icon': 'play', 'label': 'Run Cell', 'method': 'run_cell'},
            {'id': 'run_all', 'icon': 'play-circle', 'label': 'Run All', 'method': 'run_all_cells'},
            {'id': 'kernel', 'icon': 'cpu', 'label': 'Kernel', 'method': 'manage_kernel'},
            {'id': 'add_cell', 'icon': 'plus', 'label': 'Add Cell', 'method': 'insert_cell'},
            {'id': 'delete_cell', 'icon': 'trash', 'label': 'Delete Cell', 'method': 'delete_cell'},
            {'id': 'move_up', 'icon': 'arrow-up', 'label': 'Move Up', 'method': 'move_cell_up'},
            {'id': 'move_down', 'icon': 'arrow-down', 'label': 'Move Down', 'method': 'move_cell_down'},
        ]
    
    def run_cell(self, position=0):
        """Run a specific cell.
        
        Args:
            position: Cell index to run
            
        Returns:
            self
        """
        logma.info(f"Run cell at position {position}")
        return self
    
    def run_all_cells(self):
        """Run all cells in the notebook.
        
        Returns:
            self
        """
        logma.info("Run all cells")
        return self
    
    def manage_kernel(self):
        """Manage notebook kernel.
        
        Returns:
            self
        """
        logma.info("Manage kernel")
        return self
    
    def insert_cell(self, cell_type="code", position=None):
        """Insert a new cell.
        
        Args:
            cell_type: Type of cell ('code' or 'markdown')
            position: Position to insert at (None = end)
            
        Returns:
            self
        """
        if position is None:
            position = len(self.cells) if self.cells else 0
        logma.info(f"Insert cell type={cell_type} at position={position}")
        return self
    
    def delete_cell(self, position=0):
        """Delete a cell.
        
        Args:
            position: Cell index to delete
            
        Returns:
            self
        """
        logma.info(f"Delete cell at position {position}")
        return self
    
    def move_cell_up(self, position=0):
        """Move a cell up.
        
        Args:
            position: Cell index to move
            
        Returns:
            self
        """
        logma.info(f"Move cell up at position {position}")
        return self
    
    def move_cell_down(self, position=0):
        """Move a cell down.
        
        Args:
            position: Cell index to move
            
        Returns:
            self
        """
        logma.info(f"Move cell down at position {position}")
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
