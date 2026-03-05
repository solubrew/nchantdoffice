# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
    docid:
    name: NchantdOffice Vector Search Module
    description: >
        Vector search and embedding capabilities extending NchantdStore
        for semantic search and similarity matching
    version: 0.3.0
    authority: filesystem
    security: seclvl2
    <(WT)>: -32
"""
# -*- coding: utf-8 -*
# ======================================Standard Library Modules======================================================||
from os.path import dirname, join, exists
from functools import lru_cache
import threading

# ======================================3rd Party Library Modules=====================================================||
import numpy as np
from numpy.linalg import norm

# ======================================Solutions Brewer Library Modules==============================================||
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


# ====================================================================================================================||
here = join(dirname(__file__), "")

# Default embedding model
DEFAULT_EMBEDDING_MODEL = 'all-MiniLM-L6-v2'
DEFAULT_DIMENSION = 384


# ====================================================================================================================||

class VectorSearchMixin:
    """
    Mixin class providing vector search capabilities for NchantdStore.
    Extends storage with semantic search and embedding-based operations.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._embedding_model = None
        self._vector_index = None
        self._vector_dimension = DEFAULT_DIMENSION
        self._index_lock = threading.RLock()
        self._embedding_cache = {}
        
    @property
    def embedding_model(self):
        """Lazy-load embedding model"""
        if self._embedding_model is None and SENTENCE_TRANSFORMERS_AVAILABLE:
            self._embedding_model = SentenceTransformer(DEFAULT_EMBEDDING_MODEL)
        return self._embedding_model
    
    def init_vector_search(self, dimension: int = DEFAULT_DIMENSION, index_type: str = 'flat'):
        """
        Initialize vector search index.
        
        Args:
            dimension: Dimension of embedding vectors
            index_type: Type of index ('flat', 'hnsw', 'ivf')
        """
        self._vector_dimension = dimension
        
        if FAISS_AVAILABLE:
            if index_type == 'flat':
                self._vector_index = faiss.IndexFlatL2(dimension)
            elif index_type == 'hnsw':
                self._vector_index = faiss.IndexHNSWFlat(dimension, 32)
            elif index_type == 'ivf':
                quantizer = faiss.IndexFlatL2(dimension)
                self._vector_index = faiss.IndexIVFFlat(quantizer, dimension, 100)
        else:
            # Fallback to simple numpy-based index
            self._vector_index = _NumpyVectorIndex(dimension)
            
        return self
    
    def create_embedding(self, text: str) -> np.ndarray:
        """
        Create vector embedding for text using the configured embedding model.
        
        Args:
            text: Input text to embed
            
        Returns:
            numpy array of embeddings
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            # Return dummy embedding if model not available
            return np.random.rand(self._vector_dimension)
        
        # Check cache first
        if text in self._embedding_cache:
            return self._embedding_cache[text]
        
        embedding = self.embedding_model.encode(text, convert_to_numpy=True)
        
        # Cache the embedding
        self._embedding_cache[text] = embedding
        
        return embedding
    
    def create_embeddings_batch(self, texts: list) -> np.ndarray:
        """
        Create embeddings for multiple texts.
        
        Args:
            texts: List of input texts
            
        Returns:
            numpy array of embeddings (num_texts x dimension)
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            return np.random.rand(len(texts), self._vector_dimension)
        
        embeddings = self.embedding_model.encode(texts, convert_to_numpy=True, batch_size=32)
        
        # Cache individual embeddings
        for text, embedding in zip(texts, embeddings):
            self._embedding_cache[text] = embedding
            
        return embeddings
    
    def add_vector(self, vector: np.ndarray, doc_id: str, metadata: dict = None):
        """
        Add a vector to the search index.
        
        Args:
            vector: Embedding vector
            doc_id: Document ID to associate
            metadata: Optional metadata dictionary
        """
        with self._index_lock:
            if self._vector_index is None:
                self.init_vector_search()
            
            vector = np.asarray(vector).astype('float32')
            if vector.ndim == 1:
                vector = vector.reshape(1, -1)
                
            self._vector_index.add(vector)
            
    def similarity_search(self, query: str, top_k: int = 10) -> list:
        """
        Find similar documents using vector similarity.
        
        Args:
            query: Query text
            top_k: Number of results to return
            
        Returns:
            List of (doc_id, similarity_score) tuples
        """
        query_vector = self.create_embedding(query)
        return self.similarity_search_by_vector(query_vector, top_k)
    
    def similarity_search_by_vector(self, query_vector: np.ndarray, top_k: int = 10) -> list:
        """
        Find similar documents using a query vector.
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of (index, distance) tuples
        """
        with self._index_lock:
            if self._vector_index is None:
                return []
            
            query_vector = np.asarray(query_vector).astype('float32')
            if query_vector.ndim == 1:
                query_vector = query_vector.reshape(1, -1)
            
            if FAISS_AVAILABLE:
                distances, indices = self._vector_index.search(query_vector, top_k)
                return list(zip(indices[0], distances[0]))
            else:
                return self._vector_index.search(query_vector, top_k)
    
    def semantic_search(self, query: str, filters: dict = None, top_k: int = 10) -> list:
        """
        Natural language semantic search with optional filters.
        
        Args:
            query: Natural language query
            filters: Optional filters (e.g., {'tag_txt': 'important'})
            top_k: Number of results
            
        Returns:
            List of matching documents
        """
        query_vector = self.create_embedding(query)
        
        # Get similar vectors
        results = self.similarity_search_by_vector(query_vector, top_k * 2)  # Get more for filtering
        
        # Apply filters if provided (would need to query actual documents)
        # This is a placeholder - actual implementation would cross-reference
        # with the document store
        
        return results[:top_k]
    
    def hybrid_search(self, text_query: str, vector_query: str, top_k: int = 10, alpha: float = 0.5) -> list:
        """
        Combine keyword and vector search.
        
        Args:
            text_query: Keyword-based query
            vector_query: Semantic query
            top_k: Number of results
            alpha: Weight for vector search (1-alpha for text)
            
        Returns:
            Combined and reranked results
        """
        # Get text search results (using existing SQuiRL)
        text_results = self._text_search(text_query, top_k)
        
        # Get vector search results
        vector_results = self.similarity_search(vector_query, top_k)
        
        # Combine scores
        combined_scores = {}
        
        for idx, score in text_results:
            combined_scores[idx] = combined_scores.get(idx, 0) + (1 - alpha) * score
            
        for idx, score in vector_results:
            combined_scores[idx] = combined_scores.get(idx, 0) + alpha * score
        
        # Sort by combined score
        sorted_results = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_results[:top_k]
    
    def _text_search(self, query: str, top_k: int) -> list:
        """
        Basic text search using existing SQuiRL capabilities.
        Override for custom text search implementation.
        """
        # Placeholder - would use self.get_table() with LIKE queries
        return []
    
    def index_documents(self, documents: list, batch_size: int = 32):
        """
        Index multiple documents for vector search.
        
        Args:
            documents: List of dicts with 'id', 'text', and optional 'metadata'
            batch_size: Number of documents to process at once
        """
        if self._vector_index is None:
            self.init_vector_search()
            
        texts = [doc['text'] for doc in documents]
        
        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_embeddings = self.create_embeddings_batch(batch_texts)
            
            with self._index_lock:
                self._vector_index.add(batch_embeddings)
    
    def rerank_results(self, query: str, results: list, top_k: int = 10) -> list:
        """
        Rerank search results using cross-encoders for better relevance.
        
        Args:
            query: Original query
            results: List of (doc_id, score) tuples
            top_k: Number of results to return
            
        Returns:
            Reranked results
        """
        if not results:
            return []
            
        # For now, just return original results
        # Full implementation would use a cross-encoder model
        return results[:top_k]
    
    def save_index(self, path: str):
        """Save vector index to disk"""
        with self._index_lock:
            if self._vector_index is not None and FAISS_AVAILABLE:
                faiss.write_index(self._vector_index, path)
    
    def load_index(self, path: str):
        """Load vector index from disk"""
        with self._index_lock:
            if exists(path) and FAISS_AVAILABLE:
                self._vector_index = faiss.read_index(path)
    
    def clear_index(self):
        """Clear the vector index"""
        with self._index_lock:
            if self._vector_index is not None:
                if FAISS_AVAILABLE:
                    self._vector_index.reset()
                else:
                    self._vector_index = _NumpyVectorIndex(self._vector_dimension)
            self._embedding_cache.clear()


class _NumpyVectorIndex:
    """Fallback numpy-based vector index when FAISS is not available"""
    
    def __init__(self, dimension: int):
        self.dimension = dimension
        self.vectors = []
        self.doc_ids = []
    
    def add(self, vectors):
        """Add vectors to index"""
        if isinstance(vectors, list):
            self.vectors.extend(vectors)
        else:
            self.vectors.append(vectors)
    
    def search(self, query_vector, top_k: int = 10) -> list:
        """Search for similar vectors using cosine similarity"""
        if not self.vectors:
            return []
        
        query_vector = query_vector.flatten()
        
        # Calculate cosine similarity
        similarities = []
        for i, vec in enumerate(self.vectors):
            vec = np.asarray(vec).flatten()
            if len(vec) != len(query_vector):
                continue
                
            cosine_sim = np.dot(query_vector, vec) / (norm(query_vector) * norm(vec) + 1e-8)
            similarities.append((i, cosine_sim))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
    
    def reset(self):
        """Clear the index"""
        self.vectors = []
        self.doc_ids = []


# ====================================================================================================================||
# Extension methods to add to NchantdOfficeStore
# ====================================================================================================================||

def create_vector_table(self, table_name: str = 'vectorized_data', dimension: int = DEFAULT_DIMENSION):
    """
    Create a virtual table for vector storage.
    
    Args:
        table_name: Name of the table
        dimension: Embedding dimension
    """
    if not hasattr(self, 'docs') or 'db' not in self.docs:
        return
        
    db = self.docs['db']
    
    # Check if table exists
    if db.exists(table_name):
        return
        
    # Create table with vector column support
    # Using JSON to store vector data as fallback
    columns = {
        'id_txt': 'TEXT PRIMARY KEY',
        'version_txt': 'TEXT',
        'embedding_json': 'TEXT',  # Store as JSON string
        'raw_data_txt': 'TEXT',
        'did_txt': 'TEXT',
        'CREBY_USER_FK': 'INTEGER',
        'CREON_DTTM': 'TEXT',
        'MODON_USER_FK': 'INTEGER',
        'MODON_DTTM': 'TEXT',
        'DELETE_BIT': 'INTEGER DEFAULT 0',
        'ARCHIVE_BIT': 'INTEGER DEFAULT 0',
        'ACTIVE_BIT': 'INTEGER DEFAULT 1',
    }
    
    # Create table
    column_defs = ', '.join([f'{k} {v}' for k, v in columns.items()])
    db.execute(f'CREATE TABLE IF NOT EXISTS {table_name} ({column_defs})')
    db.commit()


def store_vector_embedding(self, doc_id: str, embedding: np.ndarray, raw_data: str = '', metadata: dict = None):
    """
    Store a vector embedding for a document.
    
    Args:
        doc_id: Document ID
        embedding: Vector embedding
        raw_data: Raw text data
        metadata: Optional metadata
    """
    import json
    
    table_name = 'vectorized_data'
    
    # Ensure table exists
    if not hasattr(self, '_vector_table_initialized'):
        create_vector_table(self)
        self._vector_table_initialized = True
    
    # Convert embedding to JSON
    embedding_json = json.dumps(embedding.tolist())
    
    from subtrix.utilities import uuid
    from pycurity.pyhash import encode64
    
    now = self.time.store_now() if hasattr(self, 'time') else ''
    
    record = {
        'id_txt': str(uuid()),
        'version_txt': '1.0',
        'embedding_json': embedding_json,
        'raw_data_txt': raw_data,
        'did_txt': doc_id,
        'CREBY_USER_FK': getattr(self, 'user_FK', 0),
        'CREON_DTTM': now,
        'MODON_USER_FK': getattr(self, 'user_FK', 0),
        'MODON_DTTM': now,
    }
    
    # Insert record
    columns = list(record.keys())
    placeholders = ', '.join(['?' for _ in columns])
    values = list(record.values())
    
    self.docs['db'].execute(
        f'INSERT OR REPLACE INTO {table_name} ({", ".join(columns)}) VALUES ({placeholders})',
        values
    )
    self.docs['db'].commit()


def search_vectors(self, query_embedding: np.ndarray, top_k: int = 10, table_name: str = 'vectorized_data'):
    """
    Search for similar vectors in storage.
    
    Args:
        query_embedding: Query vector
        top_k: Number of results
        table_name: Table to search
        
    Returns:
        List of (doc_id, similarity_score) tuples
    """
    import json
    
    if not self.docs['db'].exists(table_name):
        return []
    
    # Get all embeddings
    results = self.docs['db'].execute(f'SELECT did_txt, embedding_json FROM {table_name} WHERE ACTIVE_BIT = 1')
    rows = results.fetchall()
    
    if not rows:
        return []
    
    similarities = []
    query_embedding = np.asarray(query_embedding).flatten()
    query_norm = norm(query_embedding)
    
    for doc_id, embedding_json in rows:
        try:
            embedding = np.array(json.loads(embedding_json))
            embedding_norm = norm(embedding)
            
            if embedding_norm == 0:
                continue
                
            cosine_sim = np.dot(query_embedding, embedding) / (query_norm * embedding_norm)
            similarities.append((doc_id, cosine_sim))
        except:
            continue
    
    # Sort by similarity
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    return similarities[:top_k]


# ====================================================================================================================||
# Monkey-patch methods onto NchantdStore for vector search
# ====================================================================================================================||

# These will be available to NchantdOfficeStore when mixed in
VectorSearchMixin.create_vector_table = create_vector_table
VectorSearchMixin.store_vector_embedding = store_vector_embedding
VectorSearchMixin.search_vectors = search_vectors


# ====================================================================================================================||
