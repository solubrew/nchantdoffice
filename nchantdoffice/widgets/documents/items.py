# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
	docid:
	name:
	description: NchantdOffice implementation of PyfficeText
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
from pyffice.items.text import PyfficeText
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
logma = Logma(__name__)
# logma.off()

# ====================================================================================================================||


class NchantdOfficeText(NchantdOfficeDocument, PyfficeText):
    """NchantdOffice implementation of PyfficeText.
    
    This class implements the PyfficeText document type for NchantdOffice,
    providing basic text document functionality with full GUI integration.
    
    Inherits from:
        - NchantdOfficeDocument: Base GUI document class
        - PyfficeText: Pyffice data model for text objects
    
    Attributes:
        value: Text content
        font: Font configuration
        alignment: Text alignment
    """
    
    PYTYPE = PyfficeText
    
    def __init__(self, name=None, parent=None, cfg=None):
        """Initialize NchantdOfficeText document.
        
        Args:
            name: Document name
            parent: Parent widget/document
            cfg: Configuration dictionary
        """
        NchantdOfficeDocument.__init__(self, name, parent, cfg)
        PyfficeText.__init__(self, cfg)
        self.document_type = "text"
    
    def get_pyffice_tools(self):
        """Get toolbox tools for text documents.
        
        Returns:
            list: Toolbox configuration for text operations
        """
        return [
            {'id': 'format', 'icon': 'format', 'label': 'Format', 'method': 'show_format'},
            {'id': 'font', 'icon': 'font', 'label': 'Font', 'method': 'set_font'},
            {'id': 'align_left', 'icon': 'align-left', 'label': 'Align Left', 'method': 'align_left'},
            {'id': 'align_center', 'icon': 'align-center', 'label': 'Align Center', 'method': 'align_center'},
            {'id': 'align_right', 'icon': 'align-right', 'label': 'Align Right', 'method': 'align_right'},
            {'id': 'find', 'icon': 'search', 'label': 'Find & Replace', 'method': 'find_replace'},
            {'id': 'spellcheck', 'icon': 'spell', 'label': 'Spell Check', 'method': 'spell_check'},
            {'id': 'wordcount', 'icon': 'counter', 'label': 'Word Count', 'method': 'word_count'},
        ]
    
    def show_format(self):
        """Show format toolbar.
        
        Returns:
            self
        """
        logma.info("Show format toolbar")
        return self
    
    def set_font(self, font_name=None, size=None, bold=False, italic=False):
        """Set font properties.
        
        Args:
            font_name: Font family name
            size: Font size
            bold: Bold flag
            italic: Italic flag
            
        Returns:
            self
        """
        logma.info(f"Set font: {font_name} {size} bold={bold} italic={italic}")
        return self
    
    def align_left(self):
        """Align text left.
        
        Returns:
            self
        """
        self.set_alignment(horizontal='left')
        return self
    
    def align_center(self):
        """Align text center.
        
        Returns:
            self
        """
        self.set_alignment(horizontal='center')
        return self
    
    def align_right(self):
        """Align text right.
        
        Returns:
            self
        """
        self.set_alignment(horizontal='right')
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
        text = self.value or ""
        words = len(text.split())
        chars = len(text)
        lines = text.count('\n') + 1
        logma.info(f"Words: {words}, Characters: {chars}, Lines: {lines}")
        return {'words': words, 'characters': chars, 'lines': lines}


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
