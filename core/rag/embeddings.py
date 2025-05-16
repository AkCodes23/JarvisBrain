"""
Embeddings generation for RAG system.
"""

import logging
from typing import Dict, Any, List, Optional, Union
import json
from pathlib import Path
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer

class EmbeddingGenerator:
    """Generates embeddings for text chunks."""
    
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
        batch_size: int = 32
    ):
        """
        Initialize embedding generator.
        
        Args:
            model_name: Name of the model to use
            device: Device to run the model on
            batch_size: Batch size for processing
        """
        self.logger = logging.getLogger(__name__)
        self.model_name = model_name
        self.device = device
        self.batch_size = batch_size
        
        # Load model
        self.model = SentenceTransformer(model_name, device=device)
        
        # Get embedding dimension
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
    
    def generate_embeddings(
        self,
        texts: Union[str, List[str]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate embeddings for text(s).
        
        Args:
            texts: Text or list of texts to embed
            metadata: Optional metadata for the texts
            
        Returns:
            Dictionary containing embeddings and metadata
        """
        try:
            # Convert single text to list
            if isinstance(texts, str):
                texts = [texts]
            
            # Generate embeddings
            embeddings = self.model.encode(
                texts,
                batch_size=self.batch_size,
                show_progress_bar=True,
                convert_to_numpy=True
            )
            
            # Create result dictionary
            result = {
                'embeddings': embeddings.tolist(),
                'metadata': metadata or {},
                'model': self.model_name,
                'dimension': self.embedding_dim
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to generate embeddings: {e}")
            raise
    
    def compute_similarity(
        self,
        query_embedding: List[float],
        document_embeddings: List[List[float]]
    ) -> List[float]:
        """
        Compute similarity between query and document embeddings.
        
        Args:
            query_embedding: Query embedding
            document_embeddings: List of document embeddings
            
        Returns:
            List of similarity scores
        """
        try:
            # Convert to numpy arrays
            query = np.array(query_embedding)
            documents = np.array(document_embeddings)
            
            # Compute cosine similarity
            similarities = np.dot(documents, query) / (
                np.linalg.norm(documents, axis=1) * np.linalg.norm(query)
            )
            
            return similarities.tolist()
            
        except Exception as e:
            self.logger.error(f"Failed to compute similarity: {e}")
            raise
    
    def find_most_similar(
        self,
        query_embedding: List[float],
        document_embeddings: List[List[float]],
        top_k: int = 5
    ) -> List[int]:
        """
        Find most similar documents to query.
        
        Args:
            query_embedding: Query embedding
            document_embeddings: List of document embeddings
            top_k: Number of results to return
            
        Returns:
            List of indices of most similar documents
        """
        try:
            # Compute similarities
            similarities = self.compute_similarity(query_embedding, document_embeddings)
            
            # Get top-k indices
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            return top_indices.tolist()
            
        except Exception as e:
            self.logger.error(f"Failed to find most similar documents: {e}")
            raise
    
    def save_embeddings(
        self,
        embeddings: Dict[str, Any],
        filepath: str
    ) -> None:
        """
        Save embeddings to file.
        
        Args:
            embeddings: Embeddings to save
            filepath: Path to save file
        """
        try:
            # Create directory if it doesn't exist
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            # Save embeddings
            with open(filepath, 'w') as f:
                json.dump(embeddings, f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Failed to save embeddings: {e}")
            raise
    
    def load_embeddings(self, filepath: str) -> Dict[str, Any]:
        """
        Load embeddings from file.
        
        Args:
            filepath: Path to embeddings file
            
        Returns:
            Loaded embeddings
        """
        try:
            with open(filepath, 'r') as f:
                embeddings = json.load(f)
            
            return embeddings
            
        except Exception as e:
            self.logger.error(f"Failed to load embeddings: {e}")
            raise 