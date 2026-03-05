"""NchantdOffice document widgets.

Pyffice document type implementations for NchantdOffice.
"""

from ogma.logma import Logma
logma = Logma(__name__)
logma.off()
logma.off(__name__)

# Base document
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument

# Pyffice document types - Text/Documents
from nchantdoffice.widgets.documents.text import NchantdOfficeText, NchantdOfficeScript
from nchantdoffice.widgets.documents.table import NchantdOfficeTable

# Pyffice document types - Spreadsheet/Matrix
from nchantdoffice.widgets.documents.spreadsheet import NchantdOfficeSpreadSheet, NchantdOfficeMatrix

# Pyffice document types - Charts/Analytics
from nchantdoffice.widgets.documents.charts import NchantdOfficeChart
from nchantdoffice.widgets.documents.analytics import NchantdOfficeAnalytics

# Pyffice document types - Notebooks/Code
from nchantdoffice.widgets.documents.notebooks import NchantdOfficeNotebook

# Pyffice document types - PDF/Documents
from nchantdoffice.widgets.documents.pdf import NchantdOfficePDF

# Pyffice document types - Calendar/Events
from nchantdoffice.widgets.documents.calendars import NchantdOfficeCalendar

# Pyffice document types - Media
from nchantdoffice.widgets.documents.media import (
    NchantdOfficeVideo,
    NchantdOfficeAudio, 
    NchantdOfficeImage,
)
from nchantdoffice.widgets.documents.playlist import NchantdOfficePlaylist

# Pyffice document types - Contact/Persona
from nchantdoffice.widgets.documents.persona import NchantdOfficePersona
from nchantdoffice.widgets.documents.contacts import NchantdOfficeContact

# Pyffice document types - Work/Project
from nchantdoffice.widgets.documents.work import NchantdOfficeWork

# Pyffice document types - Bibliography
from nchantdoffice.widgets.documents.bibliography import NchantdOfficeBibliography

# Pyffice document types - Web
from nchantdoffice.widgets.documents.webbrowser import NchantdOfficeWebBrowser
from nchantdoffice.widgets.documents.webpage import NchantdOfficeWebPage

# Pyffice document types - Config
from nchantdoffice.widgets.documents.config import NchantdOfficeConfig

# Pyffice document types - FileSystem
from nchantdoffice.widgets.documents.filesystems import NchantdOfficeFileSystem

# Pyffice document types - Forms/Surveys
from nchantdoffice.widgets.documents.forms import NchantdOfficeForm
from nchantdoffice.widgets.documents.surveys import NchantdOfficeSurvey

# Pyffice document types - Messages
from nchantdoffice.widgets.documents.messages import NchantdOfficeMessage

# Pyffice document types - Color Palette
from nchantdoffice.widgets.documents.colorpalette import NchantdOfficeColorPalette


# Document type registry for factory pattern
DOCUMENT_TYPES = {
    'text': NchantdOfficeText,
    'script': NchantdOfficeScript,
    'table': NchantdOfficeTable,
    'spreadsheet': NchantdOfficeSpreadSheet,
    'matrix': NchantdOfficeMatrix,
    'chart': NchantdOfficeChart,
    'analytics': NchantdOfficeAnalytics,
    'notebook': NchantdOfficeNotebook,
    'pdf': NchantdOfficePDF,
    'calendar': NchantdOfficeCalendar,
    'video': NchantdOfficeVideo,
    'audio': NchantdOfficeAudio,
    'image': NchantdOfficeImage,
    'playlist': NchantdOfficePlaylist,
    'persona': NchantdOfficePersona,
    'contact': NchantdOfficeContact,
    'work': NchantdOfficeWork,
    'bibliography': NchantdOfficeBibliography,
    'webbrowser': NchantdOfficeWebBrowser,
    'webpage': NchantdOfficeWebPage,
    'config': NchantdOfficeConfig,
    'filesystem': NchantdOfficeFileSystem,
    'form': NchantdOfficeForm,
    'survey': NchantdOfficeSurvey,
    'message': NchantdOfficeMessage,
    'colorpalette': NchantdOfficeColorPalette,
}


def create_document(doc_type: str, **kwargs) -> NchantdOfficeDocument:
    """Factory function to create document by type.
    
    Args:
        doc_type: The Pyffice document type string
        **kwargs: Additional arguments passed to document constructor
    
    Returns:
        NchantdOfficeDocument instance or None if type not found
    """
    doc_class = DOCUMENT_TYPES.get(doc_type.lower())
    if doc_class:
        return doc_class(**kwargs)
    logma.warning(f"Unknown document type: {doc_type}")
    return None


def get_document_types() -> list:
    """Get list of all available document types."""
    return list(DOCUMENT_TYPES.keys())


def get_document_class(doc_type: str):
    """Get document class by type string.
    
    Args:
        doc_type: The Pyffice document type string
    
    Returns:
        NchantdOfficeDocument class or None
    """
    return DOCUMENT_TYPES.get(doc_type.lower())
