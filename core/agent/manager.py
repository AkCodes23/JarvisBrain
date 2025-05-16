"""
Agent Manager for handling agent-based task execution.
"""

import logging
from typing import Dict, Any, Optional

from core.llm.manager import LLMManager
from core.memory.manager import MemoryManager
from core.tools.manager import ToolManager

class AgentManager:
    def __init__(self, config: Dict[str, Any], llm_manager: LLMManager, 
                 memory_manager: MemoryManager, tool_manager: ToolManager):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.llm_manager = llm_manager
        self.memory_manager = memory_manager
        self.tool_manager = tool_manager
        
    async def initialize(self):
        """Initialize the agent system."""
        self.logger.info("Initializing agent manager...")
        
    async def process_input(self, user_input: str, context: Optional[str] = None) -> str:
        """Process user input and return response."""
        return await self.llm_manager.generate_response(user_input, context)
        
    async def shutdown(self):
        """Clean up resources."""
        self.logger.info("Shutting down agent manager...") 