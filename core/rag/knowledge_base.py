"""
Knowledge base for RAG system.
"""

import logging
from typing import Dict, Any, List, Optional, Union
import json
from pathlib import Path
from datetime import datetime
from .document_processor import DocumentProcessor
from .embeddings import EmbeddingGenerator
from .retriever import Retriever

class KnowledgeBase:
    """Manages a knowledge base for RAG system."""
    
    def __init__(
        self,
        base_dir: str = "data/knowledge_base",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        top_k: int = 5,
        similarity_threshold: float = 0.7
    ):
        """
        Initialize knowledge base.
        
        Args:
            base_dir: Base directory for knowledge base files
            chunk_size: Maximum size of text chunks
            chunk_overlap: Overlap between chunks
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score
        """
        self.logger = logging.getLogger(__name__)
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.document_processor = DocumentProcessor(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        self.embedding_generator = EmbeddingGenerator()
        self.retriever = Retriever(
            embedding_generator=self.embedding_generator,
            top_k=top_k,
            similarity_threshold=similarity_threshold
        )
        
        # Load existing knowledge base if it exists
        self._load_if_exists()
    
    def add_document(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a document to the knowledge base.
        
        Args:
            content: Document content
            metadata: Optional document metadata
            
        Returns:
            Document ID
        """
        try:
            # Process document
            document = self.document_processor.process_document(content, metadata)
            
            # Generate embeddings for chunks
            embedding_result = self.embedding_generator.generate_embeddings(
                document.chunks,
                metadata={'document_id': document.id}
            )
            
            # Add to retriever
            self.retriever.add_documents(
                [{'content': chunk, 'metadata': document.metadata} for chunk in document.chunks],
                embedding_result['embeddings']
            )
            
            # Save document
            self._save_document(document)
            
            return document.id
            
        except Exception as e:
            self.logger.error(f"Failed to add document: {e}")
            raise
    
    def query(
        self,
        query: str,
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Query the knowledge base.
        
        Args:
            query: Query text
            top_k: Optional number of results to return
            similarity_threshold: Optional minimum similarity score
            
        Returns:
            List of relevant documents with scores
        """
        try:
            return self.retriever.retrieve(
                query,
                top_k=top_k,
                similarity_threshold=similarity_threshold
            )
            
        except Exception as e:
            self.logger.error(f"Failed to query knowledge base: {e}")
            raise
    
    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a document by ID.
        
        Args:
            document_id: Document ID
            
        Returns:
            Document if found, None otherwise
        """
        try:
            doc_path = self.base_dir / f"{document_id}.json"
            if doc_path.exists():
                with open(doc_path, 'r') as f:
                    return json.load(f)
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get document: {e}")
            raise
    
    def delete_document(self, document_id: str) -> None:
        """
        Delete a document from the knowledge base.
        
        Args:
            document_id: Document ID
        """
        try:
            # Remove document file
            doc_path = self.base_dir / f"{document_id}.json"
            if doc_path.exists():
                doc_path.unlink()
            
            # Clear retriever and reload
            self.retriever.clear()
            self._load_if_exists()
            
        except Exception as e:
            self.logger.error(f"Failed to delete document: {e}")
            raise
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """
        List all documents in the knowledge base.
        
        Returns:
            List of document metadata
        """
        try:
            documents = []
            for doc_path in self.base_dir.glob("*.json"):
                with open(doc_path, 'r') as f:
                    doc = json.load(f)
                    documents.append({
                        'id': doc['id'],
                        'metadata': doc['metadata']
                    })
            return documents
            
        except Exception as e:
            self.logger.error(f"Failed to list documents: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge base.
        
        Returns:
            Dictionary containing knowledge base statistics
        """
        try:
            return {
                'num_documents': len(list(self.base_dir.glob("*.json"))),
                'retriever_stats': self.retriever.get_stats(),
                'base_dir': str(self.base_dir)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get knowledge base stats: {e}")
            raise
    
    def _save_document(self, document: Any) -> None:
        """
        Save a document to disk.
        
        Args:
            document: Document to save
        """
        try:
            doc_path = self.base_dir / f"{document.id}.json"
            with open(doc_path, 'w') as f:
                json.dump({
                    'id': document.id,
                    'content': document.content,
                    'metadata': document.metadata,
                    'chunks': document.chunks
                }, f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Failed to save document: {e}")
            raise
    
    def _load_if_exists(self) -> None:
        """Load existing knowledge base if it exists."""
        try:
            # Load all documents
            for doc_path in self.base_dir.glob("*.json"):
                with open(doc_path, 'r') as f:
                    doc = json.load(f)
                    
                    # Add to retriever
                    embedding_result = self.embedding_generator.generate_embeddings(
                        doc['chunks'],
                        metadata={'document_id': doc['id']}
                    )
                    
                    self.retriever.add_documents(
                        [{'content': chunk, 'metadata': doc['metadata']} for chunk in doc['chunks']],
                        embedding_result['embeddings']
                    )
            
        except Exception as e:
            self.logger.error(f"Failed to load knowledge base: {e}")
            raise 