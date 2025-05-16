"""
Base tool interface that all tools must implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging
from dataclasses import dataclass

@dataclass
class ToolResult:
    """Result of a tool execution."""
    success: bool
    data: Any
    error: Optional[str] = None

class BaseTool(ABC):
    """Base class for all tools in the system."""
    
    def __init__(self, name: str, description: str):
        """Initialize the tool."""
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"tool.{name}")
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with the given parameters."""
        pass
    
    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """Get the tool's parameter schema."""
        pass
    
    def validate_parameters(self, **kwargs) -> bool:
        """Validate the provided parameters against the schema."""
        required_params = {k: v for k, v in self.parameters.items() if v.get('required', False)}
        return all(k in kwargs for k in required_params)
    
    def get_help(self) -> str:
        """Get help text for the tool."""
        param_docs = "\n".join(
            f"  {name}: {info.get('description', 'No description')}"
            for name, info in self.parameters.items()
        )
        return f"{self.description}\n\nParameters:\n{param_docs}" 