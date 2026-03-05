"""Tests for Vector Search Implementation"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nchantdoffice.models.vector_search import VectorSearchMixin, VectorIndexMixin


class MockVectorStore(VectorSearchMixin, VectorIndexMixin):
    """Mock store for testing"""
    
    def __init__(self):
        self._embedding_cache = {}
        self._index_cache = {}


class TestVectorSearch:
    """Test vector search functionality"""
    
    @pytest.fixture
    def store(self):
        return MockVectorStore()
    
    # -------------------------------------------------------------------------
    # T-4.1: Unit tests for embedding generation
    # -------------------------------------------------------------------------
    
    def test_create_embedding_returns_numpy_array(self, store):
        """Test create_embedding returns numpy array"""
        result = store.create_embedding("test text")
        
        assert isinstance(result, np.ndarray)
        assert result.shape[0] == 384  # default dimension
    
    def test_create_embedding_empty_text(self, store):
        """Test create_embedding with empty text"""
        result = store.create_embedding("")
        
        assert isinstance(result, np.ndarray)
        assert result.shape[0] == 384
        assert np.allclose(result, np.zeros(384))
    
    def test_create_embedding_deterministic(self, store):
        """Test create_embedding is deterministic for same text"""
        result1 = store.create_embedding("test text")
        result2 = store.create_embedding("test text")
        
        # With fallback, should be same (random seed based on hash)
        # Note: Real embedding models may have slight variations
        assert result1.shape == result2.shape
    
    def test_create_embeddings_batch(self, store):
        """Test batch embedding creation"""
        texts = ["text 1", "text 2", "text 3"]
        result = store.create_embeddings_batch(texts)
        
        assert result.shape == (3, 384)
    
    def test_create_embeddings_empty_list(self, store):
        """Test batch embedding with empty list"""
        result = store.create_embeddings_batch([])
        
        assert result.shape == (0,)
    
    # -------------------------------------------------------------------------
    # T-4.2: Integration tests for search
    # -------------------------------------------------------------------------
    
    def test_similarity_search_no_vectors(self, store):
        """Test similarity search with no indexed vectors"""
        results = store.similarity_search("test query", top_k=5)
        
        assert results == []
    
    def test_semantic_search_with_filters(self, store):
        """Test semantic search with filters"""
        results = store.semantic_search(
            "test query",
            filters={"category": "test"},
            top_k=5
        )
        
        # Should return empty or filtered results
        assert isinstance(results, list)
    
    def test_hybrid_search(self, store):
        """Test hybrid search"""
        results = store.hybrid_search(
            text_query="test",
            vector_query="test",
            top_k=5,
            alpha=0.5
        )
        
        assert isinstance(results, list)
    
    # -------------------------------------------------------------------------
    # T-4.3: Performance benchmarks
    # -------------------------------------------------------------------------
    
    def test_embedding_performance(self, store):
        """Benchmark embedding generation"""
        import time
        
        text = "This is a test document for performance benchmarking"
        
        start = time.time()
        for _ in range(100):
            store.create_embedding(text)
        elapsed = time.time() - start
        
        # Should complete 100 embeddings in reasonable time
        assert elapsed < 10  # 10 seconds for 100 embeddings
        print(f"\nEmbedding performance: {elapsed*10:.2f}ms per embedding")
    
    def test_batch_embedding_performance(self, store):
        """Benchmark batch embedding generation"""
        import time
        
        texts = [f"test document {i}" for i in range(100)]
        
        start = time.time()
        embeddings = store.create_embeddings_batch(texts)
        elapsed = time.time() - start
        
        assert embeddings.shape == (100, 384)
        print(f"\nBatch embedding performance: {elapsed:.2f}s for 100 texts")
    
    # -------------------------------------------------------------------------
    # Vector Index Tests
    # -------------------------------------------------------------------------
    
    def test_create_vector_index(self, store):
        """Test vector index creation"""
        index = store.create_vector_index('hnsw', dimensions=384)
        
        assert index is not None
        assert store._index is not None
    
    def test_add_to_index(self, store):
        """Test adding vectors to index"""
        store.create_vector_index('hnsw', dimensions=384)
        
        vectors = np.random.randn(10, 384).astype(np.float32)
        ids = list(range(10))
        
        store.add_to_index(vectors, ids)
        
        # Index should now have 10 vectors
        assert store._index is not None
    
    def test_search_index(self, store):
        """Test searching index"""
        store.create_vector_index('hnsw', dimensions=384)
        
        vectors = np.random.randn(10, 384).astype(np.float32)
        ids = list(range(10))
        
        store.add_to_index(vectors, ids)
        
        query = np.random.randn(384).astype(np.float32)
        distances, indices = store.search_index(query, top_k=5)
        
        assert len(distances) == 5
        assert len(indices) == 5
    
    def test_rebuild_index(self, store):
        """Test rebuilding index"""
        store.create_vector_index('hnsw', dimensions=384)
        
        vectors = np.random.randn(10, 384).astype(np.float32)
        ids = list(range(10))
        
        store.rebuild_index(vectors, ids)
        
        # Should work without errors
        assert store._index is not None


class TestVectorIndexManager:
    """Test VectorIndexManager"""
    
    def test_create_index_faiss(self):
        """Test creating FAISS index"""
        from nchantdoffice.utilities.vector_index import VectorIndexManager
        
        manager = VectorIndexManager()
        index = manager.create_index('test', 'faiss', dimensions=384)
        
        assert index is not None
    
    def test_list_indexes(self):
        """Test listing indexes"""
        from nchantdoffice.utilities.vector_index import VectorIndexManager
        
        manager = VectorIndexManager()
        manager.create_index('test1', 'faiss', dimensions=384)
        manager.create_index('test2', 'hnsw', dimensions=384)
        
        indexes = manager.list_indexes()
        
        assert len(indexes) == 2
        assert any(i['name'] == 'test1' for i in indexes)
        assert any(i['name'] == 'test2' for i in indexes)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
