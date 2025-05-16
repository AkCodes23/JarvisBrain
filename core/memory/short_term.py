"""
Short-term memory for conversation context.
"""

import logging
from typing import Dict, Any, List, Optional, Union
import json
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class MemoryItem:
    """Container for memory items."""
    id: str
    content: Any
    metadata: Dict[str, Any]
    timestamp: datetime
    expires_at: Optional[datetime] = None

class ShortTermMemory:
    """Manages short-term memory for conversation context."""
    
    def __init__(
        self,
        max_items: int = 100,
        default_ttl: int = 3600  # 1 hour in seconds
    ):
        """
        Initialize short-term memory.
        
        Args:
            max_items: Maximum number of items to store
            default_ttl: Default time-to-live for items in seconds
        """
        self.logger = logging.getLogger(__name__)
        self.max_items = max_items
        self.default_ttl = default_ttl
        
        # Initialize memory store
        self.items: List[MemoryItem] = []
    
    def add(
        self,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None,
        ttl: Optional[int] = None
    ) -> str:
        """
        Add an item to memory.
        
        Args:
            content: Item content
            metadata: Optional item metadata
            ttl: Optional time-to-live in seconds
            
        Returns:
            Item ID
        """
        try:
            # Generate item ID
            item_id = self._generate_item_id()
            
            # Set expiration time
            expires_at = None
            if ttl is not None:
                expires_at = datetime.now() + timedelta(seconds=ttl)
            elif self.default_ttl is not None:
                expires_at = datetime.now() + timedelta(seconds=self.default_ttl)
            
            # Create memory item
            item = MemoryItem(
                id=item_id,
                content=content,
                metadata=metadata or {},
                timestamp=datetime.now(),
                expires_at=expires_at
            )
            
            # Add to memory
            self.items.append(item)
            
            # Enforce maximum items
            if len(self.items) > self.max_items:
                self.items.pop(0)
            
            return item_id
            
        except Exception as e:
            self.logger.error(f"Failed to add item to memory: {e}")
            raise
    
    def get(self, item_id: str) -> Optional[MemoryItem]:
        """
        Get an item from memory.
        
        Args:
            item_id: Item ID
            
        Returns:
            Memory item if found and not expired, None otherwise
        """
        try:
            # Find item
            for item in self.items:
                if item.id == item_id:
                    # Check if expired
                    if item.expires_at and item.expires_at < datetime.now():
                        self.items.remove(item)
                        return None
                    return item
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get item from memory: {e}")
            raise
    
    def remove(self, item_id: str) -> None:
        """
        Remove an item from memory.
        
        Args:
            item_id: Item ID
        """
        try:
            self.items = [item for item in self.items if item.id != item_id]
            
        except Exception as e:
            self.logger.error(f"Failed to remove item from memory: {e}")
            raise
    
    def clear(self) -> None:
        """Clear all items from memory."""
        try:
            self.items.clear()
            
        except Exception as e:
            self.logger.error(f"Failed to clear memory: {e}")
            raise
    
    def cleanup(self) -> None:
        """Remove expired items from memory."""
        try:
            now = datetime.now()
            self.items = [
                item for item in self.items
                if not item.expires_at or item.expires_at > now
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup memory: {e}")
            raise
    
    def get_all(self) -> List[MemoryItem]:
        """
        Get all non-expired items from memory.
        
        Returns:
            List of memory items
        """
        try:
            # Cleanup expired items
            self.cleanup()
            
            return self.items.copy()
            
        except Exception as e:
            self.logger.error(f"Failed to get all items from memory: {e}")
            raise
    
    def search(
        self,
        query: str,
        max_results: Optional[int] = None
    ) -> List[MemoryItem]:
        """
        Search memory items.
        
        Args:
            query: Search query
            max_results: Optional maximum number of results
            
        Returns:
            List of matching memory items
        """
        try:
            # Cleanup expired items
            self.cleanup()
            
            # Simple text search
            results = []
            for item in self.items:
                # Search in content
                if isinstance(item.content, str) and query.lower() in item.content.lower():
                    results.append(item)
                    continue
                
                # Search in metadata
                for value in item.metadata.values():
                    if isinstance(value, str) and query.lower() in value.lower():
                        results.append(item)
                        break
            
            # Limit results
            if max_results is not None:
                results = results[:max_results]
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to search memory: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the memory.
        
        Returns:
            Dictionary containing memory statistics
        """
        try:
            # Cleanup expired items
            self.cleanup()
            
            return {
                'total_items': len(self.items),
                'max_items': self.max_items,
                'default_ttl': self.default_ttl
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get memory stats: {e}")
            raise
    
    def _generate_item_id(self) -> str:
        """
        Generate a unique item ID.
        
        Returns:
            Unique item ID
        """
        try:
            # Use timestamp and random string
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            import random
            import string
            random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            return f"item_{timestamp}_{random_str}"
            
        except Exception as e:
            self.logger.error(f"Failed to generate item ID: {e}")
            raise 