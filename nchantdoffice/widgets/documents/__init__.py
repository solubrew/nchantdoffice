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
# ======================================NchantdOffice Document Widgets==============================================||

from nchantdoffice.widgets.documents.documents import (
    NchantdOfficeDocumentMixin,
    NchantdOfficeDocument,
    NchantdOfficeDocumentManager,
)

__all__ = [
    "NchantdOfficeDocumentMixin",
    "NchantdOfficeDocument",
    "NchantdOfficeDocumentManager",
]
