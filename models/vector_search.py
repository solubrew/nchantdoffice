"""Vector Search Implementation for NchantdOfficeStore"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class VectorSearchMixin:
    """Mixin providing vector search capabilities"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._embedding_cache = {}
        self._index_cache = {}
    
    # -------------------------------------------------------------------------
    # T-2.1: Embedding Generation
    # -------------------------------------------------------------------------
    
    def create_embedding(self, text: str, model: str = 'default') -> np.ndarray:
        """Create vector embedding for text"""
        if not text:
            return np.zeros(self._get_embedding_dim(model))
        
        # Check cache
        cache_key = f"{model}:{text}"
        if cache_key in self._embedding_cache:
            return self._embedding_cache[cache_key]
        
        try:
            from sentence_transformers import SentenceTransformer
            
            if model not in self._index_cache:
                self._index_cache[model] = SentenceTransformer(model)
            
            embedding = self._index_cache[model].encode(text)
            self._embedding_cache[cache_key] = embedding
            return embedding
            
        except ImportError:
            logger.warning("sentence-transformers not available, using fallback")
            return self._fallback_embedding(text, model)
    
    def _get_embedding_dim(self, model: str = 'default') -> int:
        dims = {'default': 384, 'mini': 384, 'base': 768, 'large': 1024}
        return dims.get(model, 384)
    
    def _fallback_embedding(self, text: str, model: str) -> np.ndarray:
        dim = self._get_embedding_dim(model)
        np.random.seed(hash(text) % (2**32))
        return np.random.randn(dim)
    
    def create_embeddings_batch(self, texts: List[str], model: str = 'default') -> np.ndarray:
        if not texts:
            return np.array([])
        
        try:
            from sentence_transformers import SentenceTransformer
            if model not in self._index_cache:
                self._index_cache[model] = SentenceTransformer(model)
            return self._index_cache[model].encode(texts)
        except ImportError:
            return np.array([self._fallback_embedding(t, model) for t in texts])
    
    # -------------------------------------------------------------------------
    # T-2.2: Similarity Search
    # -------------------------------------------------------------------------
    
    def similarity_search(
        self, 
        query: str, 
        top_k: int = 10,
        model: str = 'default',
        table: str = None,
        column: str = 'embedding'
    ) -> List[Dict[str, Any]]:
        """Find similar documents using vector search"""
        query_vector = self.create_embedding(query, model)
        vectors, ids = self._get_vectors(table, column)
        
        if len(vectors) == 0:
            return []
        
        similarities = self._compute_similarities(query_vector, vectors)
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        return [
            {'id': ids[idx] if ids is not None else idx, 'score': float(similarities[idx])}
            for idx in top_indices
        ]
    
    def _get_vectors(self, table: str, column: str) -> Tuple[np.ndarray, List]:
        return np.array([]), []
    
    def _compute_similarities(self, query: np.ndarray, vectors: np.ndarray) -> np.ndarray:
        query_norm = query / (np.linalg.norm(query) + 1e-8)
        vectors_norm = vectors / (np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-8)
        return np.dot(vectors_norm, query_norm)
    
    # -------------------------------------------------------------------------
    # T-2.3: Semantic Search
    # -------------------------------------------------------------------------
    
    def semantic_search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 10,
        model: str = 'default',
        table: str = None
    ) -> List[Dict[str, Any]]:
        results = self.similarity_search(query, top_k * 2, model, table)
        if filters:
            results = self._apply_filters(results, filters)
        return results[:top_k]
    
    def _apply_filters(self, results: List[Dict], filters: Dict) -> List[Dict]:
        return results
    
    # -------------------------------------------------------------------------
    # T-2.4: Hybrid Search
    # -------------------------------------------------------------------------
    
    def hybrid_search(
        self,
        text_query: str,
        vector_query: str,
        top_k: int = 10,
        alpha: float = 0.5,
        model: str = 'default',
        table: str = None
    ) -> List[Dict[str, Any]]:
        keyword_results = self._keyword_search(text_query, top_k * 2, table)
        vector_results = self.similarity_search(vector_query, top_k * 2, model, table)
        
        keyword_scores = self._normalize_scores([r['score'] for r in keyword_results])
        vector_scores = self._normalize_scores([r['score'] for r in vector_results])
        
        return self._merge_results(
            keyword_results, keyword_scores,
            vector_results, vector_scores,
            alpha, top_k
        )
    
    def _keyword_search(self, query: str, top_k: int, table: str) -> List[Dict]:
        return []
    
    def _normalize_scores(self, scores: List[float]) -> List[float]:
        if not scores:
            return []
        min_s, max_s = min(scores), max(scores)
        if max_s == min_s:
            return [1.0] * len(scores)
        return [(s - min_s) / (max_s - min_s) for s in scores]
    
    def _merge_results(
        self, kw_results, kw_scores, vec_results, vec_scores, alpha, top_k
    ) -> List[Dict]:
        kw_map = {r['id']: s for r, s in zip(kw_results, kw_scores)}
        vec_map = {r['id']: s for r, s in zip(vec_results, vec_scores)}
        all_ids = set(kw_map.keys()) | set(vec_map.keys())
        
        combined = []
        for doc_id in all_ids:
            kw_score = kw_map.get(doc_id, 0)
            vec_score = vec_map.get(doc_id, 0)
            combined.append({'id': doc_id, 'score': alpha * kw_score + (1 - alpha) * vec_score})
        
        combined.sort(key=lambda x: x['score'], reverse=True)
        return combined[:top_k]
    
    # -------------------------------------------------------------------------
    # T-2.5: Bulk Indexing
    # -------------------------------------------------------------------------
    
    def index_documents(
        self,
        documents: List[Dict[str, Any]],
        text_column: str = 'text',
        id_column: str = 'id',
        model: str = 'default',
        table: str = None,
        batch_size: int = 32
    ):
        texts = [doc.get(text_column, '') for doc in documents]
        doc_ids = [doc.get(id_column, i) for i, doc in enumerate(documents)]
        
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            embeddings = self.create_embeddings_batch(batch, model)
            all_embeddings.append(embeddings)
        
        embeddings = np.vstack(all_embeddings) if all_embeddings else np.array([])
        self._store_embeddings(doc_ids, embeddings, table)
        
        logger.info(f"Indexed {len(documents)} documents")
        return len(documents)
    
    def _store_embeddings(self, doc_ids: List, vectors: np.ndarray, table: str):
        pass
    
    # -------------------------------------------------------------------------
    # T-2.6: Re-ranking
    # -------------------------------------------------------------------------
    
    def rerank_results(
        self,
        results: List[Dict[str, Any]],
        query: str,
        model: str = 'cross-encoder',
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        try:
            from sentence_transformers import CrossEncoder
            
            if 'cross_encoder' not in self._index_cache:
                self._index_cache['cross_encoder'] = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
            
            pairs = [(query, r.get('text', '')) for r in results]
            scores = self._index_cache['cross_encoder'].predict(pairs)
            
            for r, s in zip(results, scores):
                r['rerank_score'] = float(s)
            
            results.sort(key=lambda x: x.get('rerank_score', 0), reverse=True)
        except ImportError:
            logger.warning("cross-encoder not available, skipping re-ranking")
        
        return results[:top_k]


class VectorIndexMixin:
    """Mixin for managing vector indexes (FAISS/HNSW)"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._index = None
        self._index_type = None
    
    def create_vector_index(self, index_type: str = 'hnsw', dimensions: int = 384, **kwargs):
        self._index_type = index_type
        
        if index_type == 'faiss':
            import faiss
            self._index = faiss.IndexFlatIP(dimensions)
        elif index_type == 'hnsw':
            self._index = self._create_hnsw_index(dimensions, **kwargs)
        else:
            raise ValueError(f"Unknown index type: {index_type}")
        
        logger.info(f"Created {index_type} index with {dimensions} dimensions")
        return self._index
    
    def _create_hnsw_index(self, dimensions: int, **kwargs):
        try:
            import hnswlib
            index = hnswlib.HNSWIndex(space='cosine', dim=dimensions)
            index.init_index(
                max_elements=kwargs.get('max_elements', 10000),
                ef_construction=kwargs.get('ef_construction', 200),
                M=kwargs.get('M', 16)
            )
            return index
        except ImportError:
            logger.warning("hnswlib not available, using simple index")
            return SimpleVectorIndex(dimensions)
    
    def add_to_index(self, vectors: np.ndarray, ids: List = None):
        if self._index is None:
            raise RuntimeError("No index created")
        if hasattr(self._index, 'add_items'):
            self._index.add_items(vectors, ids)
        elif hasattr(self._index, 'add'):
            self._index.add(vectors)
    
    def search_index(self, query, top_k: int = 10):
        if self._index is None:
            raise RuntimeError("No index created")
        if hasattr(self._index, 'knn_query'):
            return self._index.knn_query(query, k=top_k)
        elif hasattr(self._index, 'search'):
            return self._index.search(query.reshape(1, -1), top_k)
        return np.array([]), np.array([])
    
    def rebuild_index(self, vectors: np.ndarray, ids: List = None):
        if self._index is not None and hasattr(self._index, 'reset'):
            self._index.reset()
        self.add_to_index(vectors, ids)
    
    def save_index(self, path: str):
        if self._index is not None and hasattr(self._index, 'save_index'):
            self._index.save_index(path)
    
    def load_index(self, path: str):
        if hasattr(self._index, 'load_index'):
            self._index.load_index(path)


class SimpleVectorIndex:
    """Simple fallback vector index"""
    
    def __init__(self, dimensions: int):
        self.dimensions = dimensions
        self.vectors = []
        self.ids = []
    
    def add_items(self, vectors, ids=None):
        self.vectors.append(vectors)
        self.ids = ids or list(range(len(vectors)))
    
    def knn_query(self, query, k=10):
        vectors = np.vstack(self.vectors) if self.vectors else np.array([])
        if len(vectors) == 0:
            return np.array([]), np.array([])
        
        similarities = np.dot(vectors, query)
        top_k = min(k, len(similarities))
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        return similarities[top_indices], np.array([self.ids[i] for i in top_indices])
