# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
    docid:
    name: NchantdAgent Store
    description: >
        Agent-enabled storage for NchantdOffice with GlainMixin integration
        for context memory and advanced agent capabilities
    version: 0.3.0
"""
# -*- coding: utf-8 -*
# ======================================Standard Library Modules======================================================||
from os.path import dirname, join

# ======================================3rd Party Library Modules=====================================================||
import glain

# ======================================Solutions Brewer Library Modules==============================================||


# ====================================================================================================================||

class GlainAgentMixin(glain.GlainMixin):
    """
    Mixin class that adds Glain context memory capabilities to NchantdOfficeStore.
    Provides semantic memory, query context, and knowledge graph features.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._glain_initialized = False
        
    def init_glain(self):
        """Initialize Glain context memory"""
        if not self._glain_initialized:
            # Glain is automatically initialized by the mixin
            self._glain_initialized = True
            
    def remember_context(self, key: str, value: str, metadata: dict = None):
        """
        Store context in Glain memory.
        
        Args:
            key: Context key
            value: Context value
            metadata: Optional metadata
        """
        if not self._glain_initialized:
            self.init_glain()
            
        # Use Glain's add method
        glain.action("add", text=f"{key}: {value}", metadata=metadata or {})
        
    def recall_context(self, query: str, top_k: int = 5):
        """
        Recall context from memory.
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            List of context results
        """
        if not self._glain_initialized:
            return []
            
        result = glain.action("query", text=query, use_hybrid=True)
        return result
        
    def get_related_context(self, entity: str):
        """
        Get related entities from knowledge graph.
        
        Args:
            entity: Entity to find relations for
            
        Returns:
            Related entities
        """
        if not self._glain_initialized:
            return []
            
        result = glain.action("graph_related", entity=entity)
        return result
        
    def add_knowledge_link(self, doc_id: int, related_doc_id: int):
        """
        Link documents in knowledge graph.
        
        Args:
            doc_id: First document ID
            related_doc_id: Related document ID
        """
        if not self._glain_initialized:
            self.init_glain()
            
        glain.action("link_docs", doc_id=doc_id, doc_id_b=related_doc_id)


class NchantdAgentStore(GlainAgentMixin):
    """
    Extended NchantdOfficeStore with agent capabilities.
    Combines NchantdStore with GlainMixin for context-aware storage.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_glain()


# ====================================================================================================================||
