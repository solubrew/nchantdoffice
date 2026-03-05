"""Vector Search API Endpoints"""

from typing import List, Dict, Any, Optional
from flask import Blueprint, request, jsonify

vector_bp = Blueprint('vector', __name__, url_prefix='/api/vector')


class VectorSearchAPI:
    """API for vector search operations"""
    
    def __init__(self, store):
        self.store = store
    
    # -------------------------------------------------------------------------
    # Embeddings
    # -------------------------------------------------------------------------
    
    def create_embedding(self, text: str, model: str = 'default') -> Dict:
        """Create embedding for text"""
        vector = self.store.create_embedding(text, model)
        
        return {
            'success': True,
            'embedding': vector.tolist(),
            'dimensions': len(vector),
            'model': model
        }
    
    def create_embeddings_batch(self, texts: List[str], model: str = 'default') -> Dict:
        """Create embeddings for multiple texts"""
        vectors = self.store.create_embeddings_batch(texts, model)
        
        return {
            'success': True,
            'count': len(vectors),
            'embeddings': vectors.tolist() if len(vectors) > 0 else []
        }
    
    # -------------------------------------------------------------------------
    # Search
    # -------------------------------------------------------------------------
    
    def similarity_search(
        self,
        query: str,
        top_k: int = 10,
        table: str = None,
        model: str = 'default'
    ) -> Dict:
        """Similarity search"""
        results = self.store.similarity_search(
            query=query,
            top_k=top_k,
            model=model,
            table=table
        )
        
        return {
            'success': True,
            'query': query,
            'count': len(results),
            'results': results
        }
    
    def semantic_search(
        self,
        query: str,
        top_k: int = 10,
        table: str = None,
        filters: Optional[Dict] = None,
        model: str = 'default'
    ) -> Dict:
        """Semantic search"""
        results = self.store.semantic_search(
            query=query,
            filters=filters,
            top_k=top_k,
            model=model,
            table=table
        )
        
        return {
            'success': True,
            'query': query,
            'count': len(results),
            'results': results
        }
    
    def hybrid_search(
        self,
        query: str,
        top_k: int = 10,
        alpha: float = 0.5,
        table: str = None,
        model: str = 'default'
    ) -> Dict:
        """Hybrid search"""
        results = self.store.hybrid_search(
            text_query=query,
            vector_query=query,
            top_k=top_k,
            alpha=alpha,
            model=model,
            table=table
        )
        
        return {
            'success': True,
            'query': query,
            'alpha': alpha,
            'count': len(results),
            'results': results
        }
    
    # -------------------------------------------------------------------------
    # Indexing
    # -------------------------------------------------------------------------
    
    def index_documents(
        self,
        documents: List[Dict],
        text_column: str = 'text',
        id_column: str = 'id',
        model: str = 'default',
        table: str = None
    ) -> Dict:
        """Index documents"""
        count = self.store.index_documents(
            documents=documents,
            text_column=text_column,
            id_column=id_column,
            model=model,
            table=table
        )
        
        return {
            'success': True,
            'indexed': count
        }
    
    def rebuild_index(self, table: str = None) -> Dict:
        """Rebuild vector index"""
        self.store.rebuild_vector_index(table)
        
        return {
            'success': True,
            'message': 'Index rebuilt'
        }
    
    # -------------------------------------------------------------------------
    # Index Management
    # -------------------------------------------------------------------------
    
    def create_index(
        self,
        index_type: str = 'hnsw',
        dimensions: int = 384,
        **kwargs
    ) -> Dict:
        """Create vector index"""
        self.store.create_vector_index(
            index_type=index_type,
            dimensions=dimensions,
            **kwargs
        )
        
        return {
            'success': True,
            'type': index_type,
            'dimensions': dimensions
        }
    
    def save_index(self, path: str) -> Dict:
        """Save index to disk"""
        self.store.save_vector_index(path)
        
        return {
            'success': True,
            'path': path
        }
    
    def load_index(self, path: str) -> Dict:
        """Load index from disk"""
        self.store.load_vector_index(path)
        
        return {
            'success': True,
            'path': path
        }


# Flask Routes
def register_routes(api: VectorSearchAPI, app):
    """Register API routes with Flask app"""
    
    @vector_bp.route('/embed', methods=['POST'])
    def create_embedding():
        data = request.json
        text = data.get('text', '')
        model = data.get('model', 'default')
        
        result = api.create_embedding(text, model)
        return jsonify(result)
    
    @vector_bp.route('/embed/batch', methods=['POST'])
    def create_embeddings_batch():
        data = request.json
        texts = data.get('texts', [])
        model = data.get('model', 'default')
        
        result = api.create_embeddings_batch(texts, model)
        return jsonify(result)
    
    @vector_bp.route('/search/similar', methods=['POST'])
    def similarity_search():
        data = request.json
        query = data.get('query', '')
        top_k = data.get('top_k', 10)
        table = data.get('table')
        model = data.get('model', 'default')
        
        result = api.similarity_search(query, top_k, table, model)
        return jsonify(result)
    
    @vector_bp.route('/search/semantic', methods=['POST'])
    def semantic_search():
        data = request.json
        query = data.get('query', '')
        top_k = data.get('top_k', 10)
        table = data.get('table')
        filters = data.get('filters')
        model = data.get('model', 'default')
        
        result = api.semantic_search(query, top_k, table, filters, model)
        return jsonify(result)
    
    @vector_bp.route('/search/hybrid', methods=['POST'])
    def hybrid_search():
        data = request.json
        query = data.get('query', '')
        top_k = data.get('top_k', 10)
        alpha = data.get('alpha', 0.5)
        table = data.get('table')
        model = data.get('model', 'default')
        
        result = api.hybrid_search(query, top_k, alpha, table, model)
        return jsonify(result)
    
    @vector_bp.route('/index', methods=['POST'])
    def index_documents():
        data = request.json
        documents = data.get('documents', [])
        
        result = api.index_documents(
            documents=documents,
            text_column=data.get('text_column', 'text'),
            id_column=data.get('id_column', 'id'),
            model=data.get('model', 'default'),
            table=data.get('table')
        )
        return jsonify(result)
    
    @vector_bp.route('/index/rebuild', methods=['POST'])
    def rebuild_index():
        data = request.json or {}
        result = api.rebuild_index(data.get('table'))
        return jsonify(result)
    
    app.register_blueprint(vector_bp)
