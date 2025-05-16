"""
Long-term memory for persistent storage.
"""

import logging
from typing import Dict, Any, List, Optional, Union
import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
import sqlite3
import hashlib

@dataclass
class MemoryEntry:
    """Container for memory entries."""
    id: str
    content: Any
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    tags: List[str]

class LongTermMemory:
    """Manages long-term memory for persistent storage."""
    
    def __init__(self, db_path: str = "data/memory.db"):
        """
        Initialize long-term memory.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.logger = logging.getLogger(__name__)
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize SQLite database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create memories table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS memories (
                        id TEXT PRIMARY KEY,
                        content TEXT NOT NULL,
                        metadata TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                """)
                
                # Create tags table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tags (
                        memory_id TEXT NOT NULL,
                        tag TEXT NOT NULL,
                        PRIMARY KEY (memory_id, tag),
                        FOREIGN KEY (memory_id) REFERENCES memories (id)
                    )
                """)
                
                conn.commit()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    def add(
        self,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Add a memory entry.
        
        Args:
            content: Entry content
            metadata: Optional entry metadata
            tags: Optional list of tags
            
        Returns:
            Entry ID
        """
        try:
            # Generate entry ID
            entry_id = self._generate_entry_id(content, metadata)
            
            # Prepare data
            now = datetime.now().isoformat()
            metadata = metadata or {}
            tags = tags or []
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Insert memory
                cursor.execute("""
                    INSERT INTO memories (id, content, metadata, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    entry_id,
                    json.dumps(content),
                    json.dumps(metadata),
                    now,
                    now
                ))
                
                # Insert tags
                for tag in tags:
                    cursor.execute("""
                        INSERT INTO tags (memory_id, tag)
                        VALUES (?, ?)
                    """, (entry_id, tag))
                
                conn.commit()
            
            return entry_id
            
        except Exception as e:
            self.logger.error(f"Failed to add memory entry: {e}")
            raise
    
    def get(self, entry_id: str) -> Optional[MemoryEntry]:
        """
        Get a memory entry.
        
        Args:
            entry_id: Entry ID
            
        Returns:
            Memory entry if found, None otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get memory
                cursor.execute("""
                    SELECT content, metadata, created_at, updated_at
                    FROM memories
                    WHERE id = ?
                """, (entry_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                content, metadata, created_at, updated_at = row
                
                # Get tags
                cursor.execute("""
                    SELECT tag
                    FROM tags
                    WHERE memory_id = ?
                """, (entry_id,))
                
                tags = [row[0] for row in cursor.fetchall()]
                
                return MemoryEntry(
                    id=entry_id,
                    content=json.loads(content),
                    metadata=json.loads(metadata),
                    created_at=datetime.fromisoformat(created_at),
                    updated_at=datetime.fromisoformat(updated_at),
                    tags=tags
                )
            
        except Exception as e:
            self.logger.error(f"Failed to get memory entry: {e}")
            raise
    
    def update(
        self,
        entry_id: str,
        content: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> None:
        """
        Update a memory entry.
        
        Args:
            entry_id: Entry ID
            content: Optional new content
            metadata: Optional new metadata
            tags: Optional new tags
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get current entry
                cursor.execute("""
                    SELECT content, metadata
                    FROM memories
                    WHERE id = ?
                """, (entry_id,))
                
                row = cursor.fetchone()
                if not row:
                    raise ValueError(f"Memory entry not found: {entry_id}")
                
                current_content, current_metadata = row
                current_content = json.loads(current_content)
                current_metadata = json.loads(current_metadata)
                
                # Update content and metadata
                if content is not None:
                    current_content = content
                if metadata is not None:
                    current_metadata.update(metadata)
                
                # Update memory
                cursor.execute("""
                    UPDATE memories
                    SET content = ?, metadata = ?, updated_at = ?
                    WHERE id = ?
                """, (
                    json.dumps(current_content),
                    json.dumps(current_metadata),
                    datetime.now().isoformat(),
                    entry_id
                ))
                
                # Update tags if provided
                if tags is not None:
                    # Remove old tags
                    cursor.execute("""
                        DELETE FROM tags
                        WHERE memory_id = ?
                    """, (entry_id,))
                    
                    # Add new tags
                    for tag in tags:
                        cursor.execute("""
                            INSERT INTO tags (memory_id, tag)
                            VALUES (?, ?)
                        """, (entry_id, tag))
                
                conn.commit()
            
        except Exception as e:
            self.logger.error(f"Failed to update memory entry: {e}")
            raise
    
    def delete(self, entry_id: str) -> None:
        """
        Delete a memory entry.
        
        Args:
            entry_id: Entry ID
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete tags first
                cursor.execute("""
                    DELETE FROM tags
                    WHERE memory_id = ?
                """, (entry_id,))
                
                # Delete memory
                cursor.execute("""
                    DELETE FROM memories
                    WHERE id = ?
                """, (entry_id,))
                
                conn.commit()
            
        except Exception as e:
            self.logger.error(f"Failed to delete memory entry: {e}")
            raise
    
    def search(
        self,
        query: str,
        tags: Optional[List[str]] = None,
        limit: Optional[int] = None
    ) -> List[MemoryEntry]:
        """
        Search memory entries.
        
        Args:
            query: Search query
            tags: Optional list of tags to filter by
            limit: Optional maximum number of results
            
        Returns:
            List of matching memory entries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build query
                sql = """
                    SELECT DISTINCT m.id, m.content, m.metadata, m.created_at, m.updated_at
                    FROM memories m
                """
                
                params = []
                
                # Add tag filter if provided
                if tags:
                    sql += """
                        INNER JOIN tags t ON m.id = t.memory_id
                        WHERE t.tag IN ({})
                    """.format(','.join(['?'] * len(tags)))
                    params.extend(tags)
                    
                    # Add content search
                    sql += " AND (m.content LIKE ? OR m.metadata LIKE ?)"
                    params.extend([f'%{query}%', f'%{query}%'])
                else:
                    # Just content search
                    sql += " WHERE m.content LIKE ? OR m.metadata LIKE ?"
                    params.extend([f'%{query}%', f'%{query}%'])
                
                # Add limit if provided
                if limit:
                    sql += f" LIMIT {limit}"
                
                # Execute query
                cursor.execute(sql, params)
                
                # Process results
                entries = []
                for row in cursor.fetchall():
                    entry_id, content, metadata, created_at, updated_at = row
                    
                    # Get tags
                    cursor.execute("""
                        SELECT tag
                        FROM tags
                        WHERE memory_id = ?
                    """, (entry_id,))
                    
                    tags = [row[0] for row in cursor.fetchall()]
                    
                    entries.append(MemoryEntry(
                        id=entry_id,
                        content=json.loads(content),
                        metadata=json.loads(metadata),
                        created_at=datetime.fromisoformat(created_at),
                        updated_at=datetime.fromisoformat(updated_at),
                        tags=tags
                    ))
                
                return entries
            
        except Exception as e:
            self.logger.error(f"Failed to search memory entries: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the memory.
        
        Returns:
            Dictionary containing memory statistics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get total entries
                cursor.execute("SELECT COUNT(*) FROM memories")
                total_entries = cursor.fetchone()[0]
                
                # Get total tags
                cursor.execute("SELECT COUNT(*) FROM tags")
                total_tags = cursor.fetchone()[0]
                
                # Get unique tags
                cursor.execute("SELECT COUNT(DISTINCT tag) FROM tags")
                unique_tags = cursor.fetchone()[0]
                
                return {
                    'total_entries': total_entries,
                    'total_tags': total_tags,
                    'unique_tags': unique_tags,
                    'db_path': str(self.db_path)
                }
            
        except Exception as e:
            self.logger.error(f"Failed to get memory stats: {e}")
            raise
    
    def _generate_entry_id(
        self,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a unique entry ID.
        
        Args:
            content: Entry content
            metadata: Optional entry metadata
            
        Returns:
            Unique entry ID
        """
        try:
            # Create hash input
            hash_input = json.dumps(content)
            if metadata:
                hash_input += json.dumps(metadata)
            
            # Generate hash
            hash_value = hashlib.md5(hash_input.encode()).hexdigest()
            
            # Add timestamp
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            
            return f"mem_{timestamp}_{hash_value[:8]}"
            
        except Exception as e:
            self.logger.error(f"Failed to generate entry ID: {e}")
            raise 