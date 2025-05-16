"""
Retriever module for content retrieval from the knowledge base.
"""

import logging
from typing import Dict, List, Optional, Any, Union
import numpy as np
from pathlib import Path
import json
from datetime import datetime
import asyncio
from .embeddings import EmbeddingGenerator

class ContentRetriever:
    """Retrieves relevant content from the knowledge base."""
    
    def __init__(
        self,
        vector_store: Any,
        embedding_generator: EmbeddingGenerator,
        max_documents: int = 5,
        similarity_threshold: float = 0.7
    ):
        """Initialize content retriever with configuration."""
        self.logger = logging.getLogger(__name__)
        self.vector_store = vector_store
        self.embedding_generator = embedding_generator
        self.max_documents = max_documents
        self.similarity_threshold = similarity_threshold
    
    async def retrieve(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        max_documents: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant documents for a query."""
        try:
            # Generate query embedding
            query_embedding = await self.embedding_generator.generate_embedding(query)
            
            # Search vector store
            results = self.vector_store.search(
                query_embedding=query_embedding,
                n_results=max_documents or self.max_documents,
                where=filters
            )
            
            # Filter by similarity threshold
            filtered_results = [
                result for result in results
                if result.get('similarity', 0) >= self.similarity_threshold
            ]
            
            return filtered_results
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve content: {e}")
            raise
    
    async def retrieve_with_reranking(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        max_documents: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve and rerank documents for better relevance."""
        try:
            # Get initial results
            results = await self.retrieve(
                query=query,
                filters=filters,
                max_documents=max_documents * 2 if max_documents else self.max_documents * 2
            )
            
            if not results:
                return []
            
            # Rerank using cross-encoder
            reranked_results = await self._rerank_results(query, results)
            
            # Return top results
            return reranked_results[:max_documents or self.max_documents]
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve with reranking: {e}")
            raise
    
    async def _rerank_results(
        self,
        query: str,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Rerank results using cross-encoder for better relevance."""
        try:
            # Prepare pairs for reranking
            pairs = [(query, result['document']) for result in results]
            
            # Get reranking scores
            scores = await self.embedding_generator.generate_embeddings(
                [f"{pair[0]} [SEP] {pair[1]}" for pair in pairs]
            )
            
            # Combine results with scores
            scored_results = list(zip(results, scores))
            
            # Sort by score
            scored_results.sort(key=lambda x: x[1], reverse=True)
            
            # Return reranked results
            return [result for result, _ in scored_results]
            
        except Exception as e:
            self.logger.error(f"Failed to rerank results: {e}")
            return results
    
    async def retrieve_similar(
        self,
        document_id: str,
        max_documents: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve documents similar to a specific document."""
        try:
            # Get document from vector store
            document = self.vector_store.get_document(document_id)
            if not document:
                return []
            
            # Retrieve similar documents
            return await self.retrieve(
                query=document['document'],
                max_documents=max_documents
            )
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve similar documents: {e}")
            raise
    
    async def retrieve_by_metadata(
        self,
        metadata_filters: Dict[str, Any],
        max_documents: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve documents matching specific metadata filters."""
        try:
            # Search vector store with metadata filters
            results = self.vector_store.search(
                query_embedding=None,  # No query embedding for metadata search
                n_results=max_documents or self.max_documents,
                where=metadata_filters
            )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve by metadata: {e}")
            raise
    
    def get_retrieval_stats(self) -> Dict[str, Any]:
        """Get statistics about the retrieval system."""
        try:
            return {
                'max_documents': self.max_documents,
                'similarity_threshold': self.similarity_threshold,
                'vector_store_stats': self.vector_store.get_collection_stats()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get retrieval stats: {e}")
            raise 