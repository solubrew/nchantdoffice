# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
	docid:
	name:
	description: NchantdOffice implementation of PyfficeScript
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
from pyffice.text.text import PyfficeScript
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
logma = Logma(__name__)
# logma.off()

# ====================================================================================================================||


class NchantdOfficeScript(NchantdOfficeDocument, PyfficeScript):
    """NchantdOffice implementation of PyfficeScript.
    
    This class implements the PyfficeScript document type for NchantdOffice,
    providing script/text document functionality with full GUI integration.
    
    Inherits from:
        - NchantdOfficeDocument: Base GUI document class
        - PyfficeScript: Pyffice data model for scripts/text
    
    Attributes:
        pages: Dictionary of document pages
        text: Full text content
        file_format: Syntax type (python, javascript, yaml, etc.)
    """
    
    PYTYPE = PyfficeScript
    
    def __init__(self, name=None, parent=None, cfg=None):
        """Initialize NchantdOfficeScript document.
        
        Args:
            name: Document name
            parent: Parent widget/document
            cfg: Configuration dictionary
        """
        NchantdOfficeDocument.__init__(self, name, parent, cfg)
        PyfficeScript.__init__(self, cfg)
        self.document_type = "script"
    
    def get_pyffice_tools(self):
        """Get toolbox tools for script/text documents.
        
        Returns:
            list: Toolbox configuration for script operations
        """
        return [
            {'id': 'run', 'icon': 'play', 'label': 'Run Script', 'method': 'run'},
            {'id': 'debug', 'icon': 'bug', 'label': 'Debug', 'method': 'debug'},
            {'id': 'terminal', 'icon': 'console', 'label': 'Terminal', 'method': 'open_terminal'},
            {'id': 'format', 'icon': 'format', 'label': 'Format', 'method': 'format_code'},
            {'id': 'find', 'icon': 'search', 'label': 'Find & Replace', 'method': 'find_replace'},
            {'id': 'spellcheck', 'icon': 'spell', 'label': 'Spell Check', 'method': 'spell_check'},
            {'id': 'wordcount', 'icon': 'counter', 'label': 'Word Count', 'method': 'word_count'},
            {'id': 'export', 'icon': 'export', 'label': 'Export', 'method': 'export_document'},
        ]
    
    def run(self):
        """Run the script.
        
        Returns:
            self
        """
        logma.info("Run script")
        return self
    
    def debug(self):
        """Debug the script.
        
        Returns:
            self
        """
        logma.info("Debug script")
        return self
    
    def open_terminal(self):
        """Open integrated terminal.
        
        Returns:
            self
        """
        logma.info("Open terminal")
        return self
    
    def format_code(self):
        """Format the code/script.
        
        Returns:
            self
        """
        logma.info("Format code")
        return self
    
    def find_replace(self, find=None, replace=None):
        """Find and replace text.
        
        Args:
            find: Text to find
            replace: Replacement text
            
        Returns:
            self
        """
        logma.info(f"Find: {find}, Replace: {replace}")
        return self
    
    def spell_check(self):
        """Run spell check on the document.
        
        Returns:
            self
        """
        logma.info("Spell check")
        return self
    
    def word_count(self):
        """Get word count statistics.
        
        Returns:
            dict: Word count statistics
        """
        text = self.full_text or ""
        words = len(text.split())
        chars = len(text)
        lines = text.count('\n') + 1
        logma.info(f"Words: {words}, Characters: {chars}, Lines: {lines}")
        return {'words': words, 'characters': chars, 'lines': lines}
    
    def export_document(self, format='pdf'):
        """Export the document.
        
        Args:
            format: Export format ('pdf', 'docx', 'html', 'txt')
            
        Returns:
            self
        """
        logma.info(f"Export as {format}")
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
