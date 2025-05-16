"""
Document processor for RAG system.
"""

import logging
from typing import Dict, Any, List, Optional, Union
import json
from pathlib import Path
import re
from dataclasses import dataclass
from datetime import datetime
import mimetypes
import PyPDF2
import docx
import markdown
import html2text
import chardet
import tiktoken

@dataclass
class Document:
    """Container for document data."""
    id: str
    content: str
    metadata: Dict[str, Any]
    chunks: List[str]

class DocumentProcessor:
    """Processes documents for the RAG system."""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        min_chunk_size: int = 100
    ):
        """
        Initialize document processor.
        
        Args:
            chunk_size: Maximum size of text chunks
            chunk_overlap: Overlap between chunks
            min_chunk_size: Minimum size of a chunk
        """
        self.logger = logging.getLogger(__name__)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        
        # Initialize tokenizer
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        # Initialize text converter
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = True
        self.html_converter.ignore_images = True
        
        # Regular expressions for text processing
        self.patterns = {
            'sentence': re.compile(r'[.!?]+["\']?\s+'),
            'paragraph': re.compile(r'\n\s*\n'),
            'whitespace': re.compile(r'\s+')
        }
    
    def process_document(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Document:
        """
        Process a document into chunks.
        
        Args:
            content: The document content
            metadata: Optional metadata for the document
            
        Returns:
            Processed Document object
        """
        try:
            # Clean and normalize content
            content = self._clean_text(content)
            
            # Generate document ID
            doc_id = self._generate_doc_id(content, metadata)
            
            # Create metadata if not provided
            if metadata is None:
                metadata = {}
            
            # Add processing metadata
            metadata.update({
                'processed_at': datetime.now().isoformat(),
                'chunk_size': self.chunk_size,
                'chunk_overlap': self.chunk_overlap,
                'total_chunks': 0
            })
            
            # Split into chunks
            chunks = self._split_into_chunks(content)
            metadata['total_chunks'] = len(chunks)
            
            return Document(
                id=doc_id,
                content=content,
                metadata=metadata,
                chunks=chunks
            )
            
        except Exception as e:
            self.logger.error(f"Failed to process document: {e}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        try:
            # Replace multiple whitespace with single space
            text = self.patterns['whitespace'].sub(' ', text)
            
            # Normalize line endings
            text = text.replace('\r\n', '\n').replace('\r', '\n')
            
            # Remove empty lines
            text = '\n'.join(line for line in text.split('\n') if line.strip())
            
            return text.strip()
            
        except Exception as e:
            self.logger.error(f"Failed to clean text: {e}")
            raise
    
    def _split_into_chunks(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to split
            
        Returns:
            List of text chunks
        """
        try:
            chunks = []
            start = 0
            
            while start < len(text):
                # Find chunk end
                end = start + self.chunk_size
                
                if end >= len(text):
                    # Last chunk
                    chunk = text[start:].strip()
                    if len(chunk) >= self.min_chunk_size:
                        chunks.append(chunk)
                    break
                
                # Try to find sentence boundary
                next_sentence = self.patterns['sentence'].search(text, end - 100, end + 100)
                if next_sentence:
                    end = next_sentence.end()
                
                # Extract chunk
                chunk = text[start:end].strip()
                if len(chunk) >= self.min_chunk_size:
                    chunks.append(chunk)
                
                # Move start position for next chunk
                start = end - self.chunk_overlap
            
            return chunks
            
        except Exception as e:
            self.logger.error(f"Failed to split text into chunks: {e}")
            raise
    
    def _generate_doc_id(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a unique document ID.
        
        Args:
            content: Document content
            metadata: Optional document metadata
            
        Returns:
            Unique document ID
        """
        try:
            # Use metadata ID if available
            if metadata and 'id' in metadata:
                return str(metadata['id'])
            
            # Generate ID from content hash
            import hashlib
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            # Add timestamp
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            
            return f"doc_{timestamp}_{content_hash[:8]}"
            
        except Exception as e:
            self.logger.error(f"Failed to generate document ID: {e}")
            raise
    
    def merge_chunks(self, chunks: List[str]) -> str:
        """
        Merge chunks back into a single text.
        
        Args:
            chunks: List of text chunks
            
        Returns:
            Merged text
        """
        try:
            # Remove overlapping content
            merged = []
            for i, chunk in enumerate(chunks):
                if i > 0:
                    # Find overlap with previous chunk
                    overlap = self._find_overlap(merged[-1], chunk)
                    if overlap:
                        chunk = chunk[overlap:]
                merged.append(chunk)
            
            return ' '.join(merged)
            
        except Exception as e:
            self.logger.error(f"Failed to merge chunks: {e}")
            raise
    
    def _find_overlap(self, text1: str, text2: str) -> int:
        """
        Find the length of overlapping content between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Length of overlap
        """
        try:
            # Try different overlap sizes
            for size in range(min(len(text1), len(text2)), 0, -1):
                if text1[-size:] == text2[:size]:
                    return size
            return 0
            
        except Exception as e:
            self.logger.error(f"Failed to find overlap: {e}")
            raise
    
    def process_directory(
        self,
        directory_path: str,
        file_patterns: Optional[List[str]] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """Process all documents in a directory."""
        try:
            directory = Path(directory_path)
            
            # Set default file patterns if none provided
            if file_patterns is None:
                file_patterns = ['*.txt', '*.pdf', '*.docx', '*.md', '*.html']
            
            # Process each matching file
            for pattern in file_patterns:
                for file_path in directory.glob(pattern):
                    try:
                        documents = self.process_document(str(file_path))
                        for doc in documents:
                            yield doc
                    except Exception as e:
                        self.logger.error(f"Failed to process file {file_path}: {e}")
                        continue
                        
        except Exception as e:
            self.logger.error(f"Failed to process directory: {e}")
            raise 