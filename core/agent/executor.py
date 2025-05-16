"""
Action executor module for executing planned tasks.
"""

import logging
from typing import Dict, List, Optional, Any, Union, Callable
import json
from datetime import datetime
import asyncio
import importlib
import inspect
from pathlib import Path

class ActionExecutor:
    """Executes planned actions and manages tool execution."""
    
    def __init__(self, tools: List[str]):
        """Initialize action executor with available tools."""
        self.logger = logging.getLogger(__name__)
        self.tools = self._load_tools(tools)
        self.execution_history: List[Dict[str, Any]] = []
    
    def _load_tools(self, tool_names: List[str]) -> Dict[str, Callable]:
        """Load tool modules and their functions."""
        try:
            tools = {}
            
            for tool_name in tool_names:
                try:
                    # Import tool module
                    module = importlib.import_module(f"core.agent.tools.{tool_name}")
                    
                    # Get all callable functions from the module
                    for name, obj in inspect.getmembers(module):
                        if inspect.isfunction(obj) and not name.startswith('_'):
                            tools[name] = obj
                    
                except Exception as e:
                    self.logger.error(f"Failed to load tool {tool_name}: {e}")
                    continue
            
            return tools
            
        except Exception as e:
            self.logger.error(f"Failed to load tools: {e}")
            raise
    
    async def execute_plan(
        self,
        plan: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a planned sequence of actions."""
        try:
            results = {
                'success': True,
                'steps': [],
                'errors': [],
                'context': context or {}
            }
            
            # Execute each step
            for step in plan['steps']:
                step_result = await self.execute_step(step, results['context'])
                results['steps'].append(step_result)
                
                # Update context with step results
                results['context'].update(step_result.get('context', {}))
                
                # Check for errors
                if not step_result['success']:
                    results['success'] = False
                    results['errors'].append(step_result['error'])
                    break
            
            # Add execution metadata
            results['execution_time'] = datetime.now().isoformat()
            results['plan'] = plan
            
            # Store in execution history
            self.execution_history.append(results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to execute plan: {e}")
            raise
    
    async def execute_step(
        self,
        step: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single step from the plan."""
        try:
            # Parse step into action and parameters
            action, params = self._parse_step(step)
            
            # Check if action exists
            if action not in self.tools:
                raise ValueError(f"Unknown action: {action}")
            
            # Execute action
            result = await self._execute_action(action, params, context)
            
            return {
                'step': step,
                'action': action,
                'parameters': params,
                'success': True,
                'result': result,
                'context': result.get('context', {})
            }
            
        except Exception as e:
            self.logger.error(f"Failed to execute step: {e}")
            return {
                'step': step,
                'success': False,
                'error': str(e)
            }
    
    def _parse_step(self, step: str) -> tuple[str, Dict[str, Any]]:
        """Parse a step string into action and parameters."""
        try:
            # Try to parse as JSON first
            try:
                data = json.loads(step)
                if isinstance(data, dict):
                    action = data.pop('action', '')
                    return action, data
            except json.JSONDecodeError:
                pass
            
            # Parse as text
            parts = step.split(' ', 1)
            action = parts[0]
            params = {}
            
            if len(parts) > 1:
                # Try to parse parameters as JSON
                try:
                    params = json.loads(parts[1])
                except json.JSONDecodeError:
                    # Parse as key-value pairs
                    for param in parts[1].split(','):
                        if ':' in param:
                            key, value = param.split(':', 1)
                            params[key.strip()] = value.strip()
            
            return action, params
            
        except Exception as e:
            self.logger.error(f"Failed to parse step: {e}")
            raise
    
    async def _execute_action(
        self,
        action: str,
        params: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a specific action with parameters."""
        try:
            # Get action function
            action_func = self.tools[action]
            
            # Check if function is async
            if inspect.iscoroutinefunction(action_func):
                result = await action_func(**params, context=context)
            else:
                result = action_func(**params, context=context)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to execute action {action}: {e}")
            raise
    
    def get_execution_history(
        self,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get execution history."""
        if limit is None:
            return self.execution_history
        return self.execution_history[-limit:]
    
    def clear_execution_history(self) -> None:
        """Clear execution history."""
        self.execution_history.clear()
    
    def get_available_actions(self) -> List[str]:
        """Get list of available actions."""
        return list(self.tools.keys())
    
    def get_action_help(self, action: str) -> Optional[str]:
        """Get help documentation for an action."""
        try:
            if action not in self.tools:
                return None
            
            return inspect.getdoc(self.tools[action])
            
        except Exception as e:
            self.logger.error(f"Failed to get action help: {e}")
            return None 