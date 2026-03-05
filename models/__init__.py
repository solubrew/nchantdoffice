"""NchantdOffice Models Package"""

from nchantdoffice.models.vector_search import VectorSearchMixin, VectorIndexMixin

# Re-export for convenience
__all__ = [
    'VectorSearchMixin',
    'VectorIndexMixin',
]
