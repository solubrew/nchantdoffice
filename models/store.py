"""NchantdOfficeStore with Vector Search Integration"""

import logging
from typing import List, Dict, Any, Optional
import numpy as np

from nchantrs.models.models import NchantdStore
from nchantdoffice.models.vector_search import VectorSearchMixin, VectorIndexMixin

logger = logging.getLogger(__name__)


class NchantdOfficeStore(VectorSearchMixin, VectorIndexMixin, NchantdStore):
    """
    NchantdOffice storage with vector search capabilities.
    
    Inherits from:
    - NchantdStore (micromole.MicroStash → squirl.SQuiRL)
    - VectorSearchMixin (embedding generation, similarity, semantic, hybrid search)
    - VectorIndexMixin (FAISS/HNSW index management)
    """
    
    def __init__(self, *args, **kwargs):
        # Configuration
        self.vector_dimensions = kwargs.pop('vector_dimensions', 384)
        self.vector_index_type = kwargs.pop('vector_index_type', 'hnsw')
        self.embedding_model = kwargs.pop('embedding_model', 'default')
        self._vector_table = kwargs.pop('vector_table', 'nchantd_vectors')
        
        super().__init__(*args, **kwargs)
        
        # Initialize vector search
        self._init_vector_search()
    
    def _init_vector_search(self):
        """Initialize vector search components"""
        # Create default vector index
        try:
            self.create_vector_index(
                index_type=self.vector_index_type,
                dimensions=self.vector_dimensions
            )
            logger.info(f"Initialized {self.vector_index_type} vector index ({self.vector_dimensions}D)")
        except Exception as e:
            logger.warning(f"Could not create vector index: {e}")
    
    # -------------------------------------------------------------------------
    # Database Integration
    # -------------------------------------------------------------------------
    
    def _get_vectors(self, table: str, column: str = 'embedding') -> tuple:
        """Get vectors from database table"""
        if table is None:
            table = self._vector_table
        
        try:
            # Query vectors from database
            results = self.query(f"SELECT id, {column} FROM {table}")
            
            vectors = []
            ids = []
            
            for row in results:
                doc_id = row[0]
                vector_data = row[1]
                
                if vector_data:
                    # Deserialize vector
                    if isinstance(vector_data, bytes):
                        vector = np.frombuffer(vector_data, dtype=np.float32)
                    elif isinstance(vector_data, str):
                        import json
                        vector = np.array(json.loads(vector_data))
                    else:
                        vector = np.array(vector_data)
                    
                    vectors.append(vector)
                    ids.append(doc_id)
            
            return np.array(vectors) if vectors else np.array([]), ids
            
        except Exception as e:
            logger.warning(f"Could not get vectors from table {table}: {e}")
            return np.array([]), []
    
    def _store_embeddings(self, doc_ids: List, vectors: np.ndarray, table: str):
        """Store embeddings in database"""
        if table is None:
            table = self._vector_table
        
        # Create table if not exists
        self._ensure_vector_table(table)
        
        # Store each embedding
        for doc_id, vector in zip(doc_ids, vectors):
            # Serialize vector
            vector_bytes = vector.astype(np.float32).tobytes()
            
            # Upsert into database
            self.upsert(
                table,
                {'id': doc_id, 'embedding': vector_bytes},
                keys=['id']
            )
        
        # Also add to in-memory index
        self.add_to_index(vectors, doc_ids)
        
        logger.info(f"Stored {len(doc_ids)} embeddings in {table}")
    
    def _ensure_vector_table(self, table: str):
        """Ensure vector storage table exists"""
        try:
            # Check if table exists
            existing = self.query(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table,)
            )
            
            if not existing:
                # Create table
                self.execute(f"""
                    CREATE TABLE {table} (
                        id TEXT PRIMARY KEY,
                        embedding BLOB,
                        metadata TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create index on embedding (for fast lookups)
                self.execute(f"CREATE INDEX {table}_emb_idx ON {table}(id)")
                
                logger.info(f"Created vector table: {table}")
                
        except Exception as e:
            logger.warning(f"Could not ensure vector table: {e}")
    
    # -------------------------------------------------------------------------
    # Vector Search API
    # -------------------------------------------------------------------------
    
    def search_similar(
        self,
        query: str,
        table: str = None,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        return self.similarity_search(
            query=query,
            top_k=top_k,
            model=self.embedding_model,
            table=table
        )
    
    def search_semantic(
        self,
        query: str,
        table: str = None,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Semantic search with optional filters"""
        return self.semantic_search(
            query=query,
            filters=filters,
            top_k=top_k,
            model=self.embedding_model,
            table=table
        )
    
    def search_hybrid(
        self,
        query: str,
        table: str = None,
        top_k: int = 10,
        alpha: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Hybrid keyword + vector search"""
        return self.hybrid_search(
            text_query=query,
            vector_query=query,
            top_k=top_k,
            alpha=alpha,
            model=self.embedding_model,
            table=table
        )
    
    # -------------------------------------------------------------------------
    # Index Management
    # -------------------------------------------------------------------------
    
    def rebuild_vector_index(self, table: str = None):
        """Rebuild vector index from database"""
        if table is None:
            table = self._vector_table
        
        vectors, ids = self._get_vectors(table)
        
        if len(vectors) > 0:
            self.rebuild_index(vectors, ids)
            logger.info(f"Rebuilt vector index with {len(vectors)} vectors")
    
    def save_vector_index(self, path: str = None):
        """Save vector index to disk"""
        if path is None:
            path = f"./nchantdoffice_vector_index_{self.name}.index"
        
        self.save_index(path)
        logger.info(f"Saved vector index to {path}")
    
    def load_vector_index(self, path: str = None):
        """Load vector index from disk"""
        if path is None:
            path = f"./nchantdoffice_vector_index_{self.name}.index"
        
        self.load_index(path)
        logger.info(f"Loaded vector index from {path}")
