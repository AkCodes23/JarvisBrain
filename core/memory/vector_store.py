"""
Vector store for memory system.
"""

import logging
from typing import Dict, Any, List, Optional, Union
import json
from pathlib import Path
import numpy as np
from datetime import datetime
import faiss
import pickle

class VectorStore:
    """Manages vector storage for memory system."""
    
    def __init__(
        self,
        dimension: int = 768,
        index_type: str = "L2",
        store_path: str = "data/vector_store"
    ):
        """
        Initialize vector store.
        
        Args:
            dimension: Dimension of vectors
            index_type: Type of FAISS index
            store_path: Path to store index and metadata
        """
        self.logger = logging.getLogger(__name__)
        self.dimension = dimension
        self.index_type = index_type
        self.store_path = Path(store_path)
        self.store_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize FAISS index
        self._init_index()
        
        # Initialize metadata storage
        self.metadata: List[Dict[str, Any]] = []
    
    def _init_index(self) -> None:
        """Initialize FAISS index."""
        try:
            if self.index_type == "L2":
                self.index = faiss.IndexFlatL2(self.dimension)
            elif self.index_type == "IP":
                self.index = faiss.IndexFlatIP(self.dimension)
            else:
                raise ValueError(f"Unsupported index type: {self.index_type}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize index: {e}")
            raise
    
    def add_vectors(
        self,
        vectors: List[List[float]],
        metadata: Optional[List[Dict[str, Any]]] = None
    ) -> List[int]:
        """
        Add vectors to the store.
        
        Args:
            vectors: List of vectors to add
            metadata: Optional list of metadata for vectors
            
        Returns:
            List of vector IDs
        """
        try:
            # Convert vectors to numpy array
            vectors = np.array(vectors).astype('float32')
            
            # Add to index
            start_id = self.index.ntotal
            self.index.add(vectors)
            
            # Generate IDs
            vector_ids = list(range(start_id, start_id + len(vectors)))
            
            # Add metadata
            if metadata:
                for i, meta in enumerate(metadata):
                    meta['vector_id'] = vector_ids[i]
                    meta['added_at'] = datetime.now().isoformat()
                    self.metadata.append(meta)
            else:
                for vector_id in vector_ids:
                    self.metadata.append({
                        'vector_id': vector_id,
                        'added_at': datetime.now().isoformat()
                    })
            
            return vector_ids
            
        except Exception as e:
            self.logger.error(f"Failed to add vectors: {e}")
            raise
    
    def search(
        self,
        query_vector: List[float],
        k: int = 5,
        filter_func: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.
        
        Args:
            query_vector: Query vector
            k: Number of results to return
            filter_func: Optional function to filter results
            
        Returns:
            List of results with distances and metadata
        """
        try:
            # Convert query to numpy array
            query = np.array([query_vector]).astype('float32')
            
            # Search index
            distances, indices = self.index.search(query, k)
            
            # Get results
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx == -1:  # FAISS returns -1 for empty slots
                    continue
                
                # Get metadata
                meta = next(
                    (m for m in self.metadata if m['vector_id'] == idx),
                    None
                )
                
                if meta and (filter_func is None or filter_func(meta)):
                    results.append({
                        'vector_id': idx,
                        'distance': float(distance),
                        'metadata': meta
                    })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to search vectors: {e}")
            raise
    
    def get_vector(self, vector_id: int) -> Optional[List[float]]:
        """
        Get a vector by ID.
        
        Args:
            vector_id: Vector ID
            
        Returns:
            Vector if found, None otherwise
        """
        try:
            if vector_id >= self.index.ntotal:
                return None
            
            # Get vector from index
            vector = faiss.vector_to_array(
                self.index.reconstruct(vector_id)
            ).tolist()
            
            return vector
            
        except Exception as e:
            self.logger.error(f"Failed to get vector: {e}")
            raise
    
    def update_metadata(
        self,
        vector_id: int,
        metadata: Dict[str, Any]
    ) -> None:
        """
        Update metadata for a vector.
        
        Args:
            vector_id: Vector ID
            metadata: New metadata
        """
        try:
            # Find and update metadata
            for meta in self.metadata:
                if meta['vector_id'] == vector_id:
                    meta.update(metadata)
                    meta['updated_at'] = datetime.now().isoformat()
                    break
            
        except Exception as e:
            self.logger.error(f"Failed to update metadata: {e}")
            raise
    
    def delete_vector(self, vector_id: int) -> None:
        """
        Delete a vector from the store.
        
        Args:
            vector_id: Vector ID
        """
        try:
            # Remove from metadata
            self.metadata = [
                meta for meta in self.metadata
                if meta['vector_id'] != vector_id
            ]
            
            # Note: FAISS doesn't support direct deletion
            # We'll need to rebuild the index
            self._rebuild_index()
            
        except Exception as e:
            self.logger.error(f"Failed to delete vector: {e}")
            raise
    
    def _rebuild_index(self) -> None:
        """Rebuild the FAISS index from metadata."""
        try:
            # Create new index
            self._init_index()
            
            # Add vectors back
            for meta in self.metadata:
                vector_id = meta['vector_id']
                vector = self.get_vector(vector_id)
                if vector:
                    self.index.add(np.array([vector]).astype('float32'))
            
        except Exception as e:
            self.logger.error(f"Failed to rebuild index: {e}")
            raise
    
    def save(self) -> None:
        """Save the vector store to disk."""
        try:
            # Save index
            index_path = self.store_path / "index.faiss"
            faiss.write_index(self.index, str(index_path))
            
            # Save metadata
            metadata_path = self.store_path / "metadata.pkl"
            with open(metadata_path, 'wb') as f:
                pickle.dump(self.metadata, f)
            
        except Exception as e:
            self.logger.error(f"Failed to save vector store: {e}")
            raise
    
    def load(self) -> None:
        """Load the vector store from disk."""
        try:
            # Load index
            index_path = self.store_path / "index.faiss"
            if index_path.exists():
                self.index = faiss.read_index(str(index_path))
            
            # Load metadata
            metadata_path = self.store_path / "metadata.pkl"
            if metadata_path.exists():
                with open(metadata_path, 'rb') as f:
                    self.metadata = pickle.load(f)
            
        except Exception as e:
            self.logger.error(f"Failed to load vector store: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.
        
        Returns:
            Dictionary containing vector store statistics
        """
        try:
            return {
                'num_vectors': self.index.ntotal,
                'dimension': self.dimension,
                'index_type': self.index_type,
                'store_path': str(self.store_path)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get vector store stats: {e}")
            raise 