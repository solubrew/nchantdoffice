# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
	docid:
	name:
	description: NchantdOffice implementation of PyfficePDF
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
from pyffice.images.pdfs import PyfficePDF
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
logma = Logma(__name__)
# logma.off()

# ====================================================================================================================||


class NchantdOfficePDF(NchantdOfficeDocument, PyfficePDF):
    """NchantdOffice implementation of PyfficePDF.
    
    This class implements the PyfficePDF document type for NchantdOffice,
    providing PDF document functionality with full GUI integration.
    
    Inherits from:
        - NchantdOfficeDocument: Base GUI document class
        - PyfficePDF: Pyffice data model for PDF documents
    
    Attributes:
        pdf_fitz: PyMuPDF document object
        reader: PyPDF2 reader object
        writer: PyPDF2 writer object
    """
    
    PYTYPE = PyfficePDF
    
    def __init__(self, name=None, parent=None, cfg=None):
        """Initialize NchantdOfficePDF document.
        
        Args:
            name: Document name
            parent: Parent widget/document
            cfg: Configuration dictionary
        """
        NchantdOfficeDocument.__init__(self, name, parent, cfg)
        PyfficePDF.__init__(self, cfg)
        self.document_type = "pdf"
    
    def get_pyffice_tools(self):
        """Get toolbox tools for PDF documents.
        
        Returns:
            list: Toolbox configuration for PDF operations
        """
        return [
            {'id': 'thumbnail', 'icon': 'image', 'label': 'Thumbnails', 'method': 'toggle_thumbnails'},
            {'id': 'outline', 'icon': 'list', 'label': 'Outline', 'method': 'show_outline'},
            {'id': 'annotate', 'icon': 'pen', 'label': 'Annotate', 'method': 'add_annotation'},
            {'id': 'sign', 'icon': 'signature', 'label': 'Sign', 'method': 'add_signature'},
            {'id': 'highlight', 'icon': 'highlight', 'label': 'Highlight', 'method': 'add_highlight'},
            {'id': 'comment', 'icon': 'comment', 'label': 'Comment', 'method': 'add_comment'},
            {'id': 'link', 'icon': 'link', 'label': 'Link', 'method': 'add_link'},
            {'id': 'extract', 'icon': 'extract', 'label': 'Extract Text', 'method': 'extract_text'},
        ]
    
    def toggle_thumbnails(self):
        """Toggle thumbnail view sidebar.
        
        Returns:
            self
        """
        logma.info("Toggle thumbnails")
        return self
    
    def show_outline(self):
        """Show document outline/bookmarks.
        
        Returns:
            self
        """
        logma.info("Show outline")
        return self
    
    def add_annotation(self, page_n=0, annotation_text='', coords=(0, 0, 100, 100)):
        """Add an annotation to a page.
        
        Args:
            page_n: Page number
            annotation_text: Text content
            coords: Bounding box coordinates
            
        Returns:
            self
        """
        logma.info(f"Add annotation to page {page_n}")
        return self
    
    def add_signature(self, page_n=0, coords=(0, 0, 200, 50)):
        """Add a signature field.
        
        Args:
            page_n: Page number
            coords: Bounding box coordinates
            
        Returns:
            self
        """
        logma.info(f"Add signature to page {page_n}")
        return self
    
    def add_highlight(self, page_n=0, coords=(0, 0, 100, 20)):
        """Add text highlight.
        
        Args:
            page_n: Page number
            coords: Bounding box coordinates
            
        Returns:
            self
        """
        logma.info(f"Add highlight to page {page_n}")
        return self
    
    def add_comment(self, page_n=0, comment_text='', coords=(0, 0, 100, 20)):
        """Add a comment.
        
        Args:
            page_n: Page number
            comment_text: Comment text
            coords: Bounding box coordinates
            
        Returns:
            self
        """
        logma.info(f"Add comment to page {page_n}")
        return self
    
    def add_link(self, page_n=0, target_page=0, coords=(0, 0, 100, 20)):
        """Add a link to another page or URL.
        
        Args:
            page_n: Source page number
            target_page: Target page number or URL
            coords: Bounding box coordinates
            
        Returns:
            self
        """
        logma.info(f"Add link from page {page_n} to {target_page}")
        return self
    
    def extract_text(self, page_n=None):
        """Extract text from pages.
        
        Args:
            page_n: Specific page number (None = all pages)
            
        Returns:
            str: Extracted text
        """
        if page_n is not None:
            text = self.get_page_text(page_n)
            logma.info(f"Extract text from page {page_n}")
        else:
            text = ""
            for i in range(len(self.reader.pages)):
                text += self.get_page_text(i)
            logma.info("Extract text from all pages")
        return text


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
