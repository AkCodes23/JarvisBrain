"""
Memory Manager for handling conversation history and long-term memory.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

class MemoryManager:
    """Manages conversation history and long-term memory."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the memory manager."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.conversation_history = []
        
    async def initialize(self):
        """Initialize the memory system."""
        self.logger.info("Initializing memory manager...")
        
    async def add_interaction(self, text: str, role: str = "user"):
        """Add a new interaction to the conversation history."""
        self.conversation_history.append({
            "text": text,
            "role": role,
            "timestamp": datetime.now().isoformat()
        })
        
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the current memory state."""
        return {
            "conversation_length": len(self.conversation_history),
            "last_interaction": self.conversation_history[-1] if self.conversation_history else None
        }
    
    async def shutdown(self):
        """Clean up resources."""
        self.logger.info("Shutting down memory manager...") 