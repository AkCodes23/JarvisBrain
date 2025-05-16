"""
Main orchestration logic for Jarvis assistant.
Handles the flow of information between components.
"""

import os
import logging
from typing import Dict, Any, List, Optional
import asyncio

from core.llm.manager import LLMManager
from core.memory.manager import MemoryManager
from core.rag.manager import RAGManager
from core.agent.manager import AgentManager
from core.tools.manager import ToolManager

class JarvisBrain:
    """Core orchestration class for the Jarvis assistant."""
    
    def __init__(self, config_path: str = "config/default_config.yaml"):
        """Initialize the Jarvis brain with configuration."""
        self.config = self._load_config(config_path)
        self.logger = self._setup_logger()
        self.logger.info("Initializing Jarvis Brain...")
        
        # Initialize components
        self.llm_manager = LLMManager(self.config.get("llm", {}))
        self.memory_manager = MemoryManager(self.config.get("memory", {}))
        self.rag_manager = RAGManager(self.config.get("rag", {}))
        self.tool_manager = ToolManager(self.config.get("tools", {}))
        self.agent_manager = AgentManager(
            self.config.get("agent", {}),
            self.llm_manager,
            self.memory_manager,
            self.tool_manager
        )
        
        self.logger.info("Jarvis Brain initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        import yaml
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Check for user config and override defaults
        user_config_path = os.path.join(os.path.dirname(config_path), "user_config.yaml")
        if os.path.exists(user_config_path):
            with open(user_config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                # Deep merge configs (simplistic version)
                for key, value in user_config.items():
                    if key in config and isinstance(value, dict) and isinstance(config[key], dict):
                        config[key].update(value)
                    else:
                        config[key] = value
        
        return config
    
    def _setup_logger(self) -> logging.Logger:
        """Set up logging for the Jarvis system."""
        logger = logging.getLogger("jarvis")
        log_level = self.config.get("system", {}).get("log_level", "INFO")
        logger.setLevel(getattr(logging, log_level))
        
        # Create console handler
        ch = logging.StreamHandler()
        ch.setLevel(getattr(logging, log_level))
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(ch)
        
        return logger
    
    async def process_input(self, user_input: str) -> str:
        """
        Process user input and return a response.
        Main processing pipeline for text input.
        """
        self.logger.info(f"Processing input: {user_input}")
        
        # 1. Update memory with new input
        await self.memory_manager.add_interaction(user_input)
        
        # 2. Use RAG to retrieve relevant information
        context = await self.rag_manager.retrieve_relevant_context(user_input)
        
        # 3. Use agent to process the input and generate response
        response = await self.agent_manager.process_input(user_input, context)
        
        # 4. Update memory with the response
        await self.memory_manager.add_interaction(response)
        
        return response
    
    async def learn_from_document(self, document_path: str):
        """Process and learn from a new document."""
        self.logger.info(f"Learning from document: {document_path}")
        await self.rag_manager.add_document(document_path)
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get a summary of the current memory state."""
        return self.memory_manager.get_summary()
    
    async def start(self):
        """Start the Jarvis assistant."""
        self.logger.info("Starting Jarvis...")
        
        # Initialize any async components
        await self.llm_manager.initialize()
        await self.memory_manager.initialize()
        await self.rag_manager.initialize()
        await self.tool_manager.initialize()
        await self.agent_manager.initialize()
        
        self.logger.info("Jarvis is ready.")
    
    async def shutdown(self):
        """Properly shut down the Jarvis assistant."""
        self.logger.info("Shutting down Jarvis...")
        
        # Clean up resources
        await self.llm_manager.shutdown()
        await self.memory_manager.shutdown()
        await self.rag_manager.shutdown()
        await self.tool_manager.shutdown()
        await self.agent_manager.shutdown()
        
        self.logger.info("Jarvis shut down successfully.")


if __name__ == "__main__":
    # Simple test to ensure the class can be instantiated
    async def test():
        brain = JarvisBrain()
        await brain.start()
        response = await brain.process_input("Hello Jarvis")
        print(response)
        await brain.shutdown()
    
    asyncio.run(test())
