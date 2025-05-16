"""
Main agent that coordinates the use of various tools.
"""

from typing import Any, Dict, List
import logging
from .base_agent import BaseAgent, AgentState
from ..tools.web_tools import WebSearchTool, WeatherTool, NewsTool
from ..tools.system_tools import SystemInfoTool, FileSystemTool, ProcessTool
from ..brain.llm_decision_maker import LLMDecisionMaker, ToolDescription

class MainAgent(BaseAgent):
    """Main agent that coordinates the use of various tools."""
    
    def __init__(self):
        """Initialize the main agent."""
        super().__init__(
            name="main_agent",
            description="Main agent that coordinates the use of various tools"
        )
        
        # Initialize tools
        self.tools = {
            "web_search": WebSearchTool(),
            "weather": WeatherTool(),
            "news": NewsTool(),
            "system_info": SystemInfoTool(),
            "file_system": FileSystemTool(),
            "process": ProcessTool()
        }
        
        # Add tools to agent
        for tool in self.tools.values():
            self.add_tool(tool)
        
        # Initialize LLM decision maker
        self.decision_maker = LLMDecisionMaker()
        
        # Add tool descriptions to decision maker
        for tool in self.tools.values():
            self.decision_maker.add_tool(ToolDescription(
                name=tool.name,
                description=tool.description,
                parameters=tool.parameters
            ))
    
    async def think(self, input_data: Any) -> Dict[str, Any]:
        """Process input and decide on next action using LLM."""
        try:
            # Get decision from LLM
            decision = await self.decision_maker.decide(str(input_data))
            
            # Log the decision
            self.logger.info(f"LLM decision: {decision}")
            
            return decision
            
        except Exception as e:
            self.logger.error(f"Error in decision making: {e}")
            # Fallback to simple rule-based approach
            return self._fallback_decision(input_data)
    
    def _fallback_decision(self, input_data: Any) -> Dict[str, Any]:
        """Fallback decision making when LLM fails."""
        if isinstance(input_data, str):
            input_data = input_data.lower()
            
            if "weather" in input_data:
                location = input_data.replace("weather", "").strip()
                if not location:
                    location = "current location"
                return {
                    "tool": "weather",
                    "parameters": {"location": location}
                }
            
            elif "news" in input_data:
                topic = input_data.replace("news", "").strip()
                return {
                    "tool": "news",
                    "parameters": {"topic": topic if topic else None}
                }
            
            elif "system" in input_data or "cpu" in input_data or "memory" in input_data:
                return {
                    "tool": "system_info",
                    "parameters": {"info_type": "all"}
                }
            
            elif "file" in input_data or "directory" in input_data:
                return {
                    "tool": "file_system",
                    "parameters": {
                        "operation": "list",
                        "path": "."
                    }
                }
            
            elif "process" in input_data or "task" in input_data:
                return {
                    "tool": "process",
                    "parameters": {
                        "operation": "list"
                    }
                }
            
            else:
                return {
                    "tool": "web_search",
                    "parameters": {"query": input_data}
                }
        
        return {
            "tool": "web_search",
            "parameters": {"query": str(input_data)}
        }
    
    async def act(self, action: Dict[str, Any]) -> Any:
        """Execute the decided action."""
        tool_name = action["tool"]
        parameters = action["parameters"]
        
        # Get the tool
        tool = self.tools.get(tool_name)
        if not tool:
            raise ValueError(f"Tool {tool_name} not found")
        
        # Execute the tool
        result = await tool.execute(**parameters)
        if not result.success:
            raise Exception(f"Tool execution failed: {result.error}")
        
        return result.data
    
    async def observe(self, result: Any) -> None:
        """Process the result of an action."""
        # Store the result in memory
        self.update_memory("last_result", result)
        
        # Log the result
        self.logger.info(f"Action completed with result: {result}")
        
        # Update tool usage statistics
        tool_usage = self.get_memory("tool_usage", {})
        if not isinstance(tool_usage, dict):
            tool_usage = {}
        tool_usage["total"] = tool_usage.get("total", 0) + 1
        self.update_memory("tool_usage", tool_usage) 