"""
Base agent class that defines core agent functionality.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import logging
from dataclasses import dataclass
from enum import Enum

class AgentState(Enum):
    """Possible states of an agent."""
    IDLE = "idle"
    THINKING = "thinking"
    EXECUTING = "executing"
    WAITING = "waiting"
    ERROR = "error"

@dataclass
class AgentContext:
    """Context information for the agent."""
    memory: Dict[str, Any]
    tools: List[Any]
    state: AgentState
    last_action: Optional[str] = None
    last_result: Optional[Any] = None

class BaseAgent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(self, name: str, description: str):
        """Initialize the agent."""
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"agent.{name}")
        self.context = AgentContext(
            memory={},
            tools=[],
            state=AgentState.IDLE
        )
    
    @abstractmethod
    async def think(self, input_data: Any) -> Dict[str, Any]:
        """Process input and decide on next action."""
        pass
    
    @abstractmethod
    async def act(self, action: Dict[str, Any]) -> Any:
        """Execute the decided action."""
        pass
    
    @abstractmethod
    async def observe(self, result: Any) -> None:
        """Process the result of an action."""
        pass
    
    async def run(self, input_data: Any) -> Any:
        """Main execution loop for the agent."""
        try:
            self.context.state = AgentState.THINKING
            action = await self.think(input_data)
            
            self.context.state = AgentState.EXECUTING
            result = await self.act(action)
            
            self.context.state = AgentState.WAITING
            await self.observe(result)
            
            self.context.state = AgentState.IDLE
            return result
            
        except Exception as e:
            self.logger.error(f"Error in agent execution: {e}")
            self.context.state = AgentState.ERROR
            raise
    
    def add_tool(self, tool: Any) -> None:
        """Add a tool to the agent's toolkit."""
        self.context.tools.append(tool)
    
    def update_memory(self, key: str, value: Any) -> None:
        """Update the agent's memory."""
        self.context.memory[key] = value
    
    def get_memory(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from the agent's memory."""
        return self.context.memory.get(key, default) 