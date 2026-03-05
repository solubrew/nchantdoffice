"""Vector Index Management Utilities"""

import os
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class VectorIndexManager:
    """Manages FAISS/HNSW vector indexes"""
    
    def __init__(self, index_dir: str = './vector_indices'):
        self.index_dir = index_dir
        os.makedirs(index_dir, exist_ok=True)
        self._indexes = {}
    
    def create_index(
        self, 
        name: str, 
        index_type: str = 'hnsw', 
        dimensions: int = 384,
        **kwargs
    ):
        """Create a new vector index"""
        if index_type == 'faiss':
            import faiss
            index = faiss.IndexFlatIP(dimensions)
        elif index_type == 'hnsw':
            try:
                import hnswlib
                index = hnswlib.HNSWIndex(space='cosine', dim=dimensions)
                index.init_index(
                    max_elements=kwargs.get('max_elements', 10000),
                    ef_construction=kwargs.get('ef_construction', 200),
                    M=kwargs.get('M', 16)
                )
            except ImportError:
                logger.warning("hnswlib not available")
                return None
        else:
            raise ValueError(f"Unknown index type: {index_type}")
        
        self._indexes[name] = {
            'index': index,
            'type': index_type,
            'dimensions': dimensions,
            'count': 0
        }
        
        logger.info(f"Created {index_type} index '{name}' with {dimensions} dims")
        return index
    
    def get_index(self, name: str):
        """Get index by name"""
        return self._indexes.get(name, {}).get('index')
    
    def add_vectors(self, name: str, vectors, ids: List = None):
        """Add vectors to index"""
        if name not in self._indexes:
            raise KeyError(f"Index '{name}' does not exist")
        
        index_info = self._indexes[name]
        index = index_info['index']
        
        if hasattr(index, 'add_items'):
            index.add_items(vectors, ids)
        elif hasattr(index, 'add'):
            index.add(vectors)
        
        index_info['count'] += len(vectors)
        logger.info(f"Added {len(vectors)} vectors to index '{name}'")
    
    def search(self, name: str, query, top_k: int = 10):
        """Search index"""
        if name not in self._indexes:
            raise KeyError(f"Index '{name}' does not exist")
        
        index = self._indexes[name]['index']
        
        if hasattr(index, 'knn_query'):
            return index.knn_query(query, k=top_k)
        elif hasattr(index, 'search'):
            return index.search(query.reshape(1, -1), top_k)
        
        return np.array([]), np.array([])
    
    def save_index(self, name: str):
        """Save index to disk"""
        if name not in self._indexes:
            return
        
        index_info = self._indexes[name]
        index = index_info['index']
        
        index_path = os.path.join(self.index_dir, f"{name}.index")
        
        if hasattr(index, 'save_index'):
            index.save_index(index_path)
        
        # Save metadata
        meta_path = os.path.join(self.index_dir, f"{name}.meta.json")
        with open(meta_path, 'w') as f:
            json.dump({
                'type': index_info['type'],
                'dimensions': index_info['dimensions'],
                'count': index_info['count']
            }, f)
        
        logger.info(f"Saved index '{name}' to {index_path}")
    
    def load_index(self, name: str):
        """Load index from disk"""
        index_path = os.path.join(self.index_dir, f"{name}.index")
        meta_path = os.path.join(self.index_dir, f"{name}.meta.json")
        
        if not os.path.exists(index_path):
            logger.warning(f"Index '{name}' not found at {index_path}")
            return
        
        with open(meta_path, 'r') as f:
            meta = json.load(f)
        
        if meta['type'] == 'faiss':
            import faiss
            index = faiss.read_index(index_path)
        elif meta['type'] == 'hnsw':
            try:
                import hnswlib
                index = hnswlib.HNSWIndex(space='cosine', dim=meta['dimensions'])
                index.load_index(index_path)
            except ImportError:
                logger.warning("hnswlib not available to load index")
                return
        else:
            return
        
        self._indexes[name] = {
            'index': index,
            'type': meta['type'],
            'dimensions': meta['dimensions'],
            'count': meta['count']
        }
        
        logger.info(f"Loaded index '{name}' with {meta['count']} vectors")
    
    def delete_index(self, name: str):
        """Delete index from memory and disk"""
        if name in self._indexes:
            del self._indexes[name]
        
        index_path = os.path.join(self.index_dir, f"{name}.index")
        meta_path = os.path.join(self.index_dir, f"{name}.meta.json")
        
        for path in [index_path, meta_path]:
            if os.path.exists(path):
                os.remove(path)
        
        logger.info(f"Deleted index '{name}'")
    
    def list_indexes(self) -> List[Dict[str, Any]]:
        """List all indexes"""
        return [
            {
                'name': name,
                'type': info['type'],
                'dimensions': info['dimensions'],
                'count': info['count']
            }
            for name, info in self._indexes.items()
        ]


class IndexCommandHandler:
    """CLI commands for vector index management"""
    
    def __init__(self, manager: VectorIndexManager):
        self.manager = manager
    
    def handle_create(self, args):
        """Handle create command"""
        self.manager.create_index(
            args.name,
            index_type=args.type or 'hnsw',
            dimensions=args.dimensions or 384,
            max_elements=args.max_elements or 10000
        )
        print(f"Created index: {args.name}")
    
    def handle_add(self, args):
        """Handle add command"""
        import numpy as np
        
        # Load vectors from file
        vectors = np.load(args.vectors)
        ids = None
        
        if args.ids:
            import json
            with open(args.ids) as f:
                ids = json.load(f)
        
        self.manager.add_vectors(args.name, vectors, ids)
        print(f"Added {len(vectors)} vectors to index: {args.name}")
    
    def handle_search(self, args):
        """Handle search command"""
        import numpy as np
        
        query = np.array([float(x) for x in args.query.split(',')])
        results, indices = self.manager.search(args.name, query, top_k=args.top_k)
        
        print(f"Search results for index: {args.name}")
        for i, (score, idx) in enumerate(zip(results, indices)):
            print(f"  {i+1}. ID: {idx}, Score: {score:.4f}")
    
    def handle_save(self, args):
        """Handle save command"""
        self.manager.save_index(args.name)
        print(f"Saved index: {args.name}")
    
    def handle_load(self, args):
        """Handle load command"""
        self.manager.load_index(args.name)
        print(f"Loaded index: {args.name}")
    
    def handle_list(self, args):
        """Handle list command"""
        indexes = self.manager.list_indexes()
        
        print("Vector Indexes:")
        for idx in indexes:
            print(f"  {idx['name']}: {idx['type']}, {idx['dimensions']}D, {idx['count']} vectors")


import numpy as np
