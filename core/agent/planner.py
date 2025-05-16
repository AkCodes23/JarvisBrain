"""
Task planner module for the agent system.
"""

import logging
from typing import Dict, List, Optional, Any, Union
import json
from datetime import datetime
import asyncio
from ..llm.model_manager import ModelManager
from ..llm.prompt_templates import PromptTemplates

class TaskPlanner:
    """Plans and decomposes tasks into actionable steps."""
    
    def __init__(
        self,
        model_manager: ModelManager,
        prompt_templates: PromptTemplates
    ):
        """Initialize task planner with components."""
        self.logger = logging.getLogger(__name__)
        self.model_manager = model_manager
        self.prompt_templates = prompt_templates
    
    async def create_plan(
        self,
        task: str,
        context: Optional[str] = None,
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a plan for executing a task."""
        try:
            # Prepare system prompt
            system_prompt = self.prompt_templates.get_prompt(
                "task_planning",
                task=task,
                context=context,
                constraints=constraints
            )
            
            # Generate plan
            response = await self.model_manager.generate_response(
                input_text=task,
                context=context,
                system_prompt=system_prompt
            )
            
            # Parse plan
            plan = self._parse_plan(response)
            
            # Validate plan
            self._validate_plan(plan)
            
            return plan
            
        except Exception as e:
            self.logger.error(f"Failed to create plan: {e}")
            raise
    
    def _parse_plan(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into a structured plan."""
        try:
            # Try to parse as JSON first
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                pass
            
            # Try to extract JSON from text
            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass
            
            # Parse as structured text
            plan = {
                'task': '',
                'steps': [],
                'constraints': {},
                'expected_outcome': ''
            }
            
            current_section = None
            for line in response.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                if line.lower().startswith('task:'):
                    plan['task'] = line[5:].strip()
                elif line.lower().startswith('steps:'):
                    current_section = 'steps'
                elif line.lower().startswith('constraints:'):
                    current_section = 'constraints'
                elif line.lower().startswith('expected outcome:'):
                    plan['expected_outcome'] = line[16:].strip()
                elif current_section == 'steps' and line.startswith('-'):
                    plan['steps'].append(line[1:].strip())
                elif current_section == 'constraints' and ':' in line:
                    key, value = line.split(':', 1)
                    plan['constraints'][key.strip()] = value.strip()
            
            return plan
            
        except Exception as e:
            self.logger.error(f"Failed to parse plan: {e}")
            raise
    
    def _validate_plan(self, plan: Dict[str, Any]) -> None:
        """Validate the structure and content of a plan."""
        try:
            # Check required fields
            required_fields = ['task', 'steps', 'constraints', 'expected_outcome']
            for field in required_fields:
                if field not in plan:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate task
            if not plan['task']:
                raise ValueError("Task cannot be empty")
            
            # Validate steps
            if not plan['steps']:
                raise ValueError("Plan must have at least one step")
            
            # Validate constraints
            if not isinstance(plan['constraints'], dict):
                raise ValueError("Constraints must be a dictionary")
            
            # Validate expected outcome
            if not plan['expected_outcome']:
                raise ValueError("Expected outcome cannot be empty")
            
        except Exception as e:
            self.logger.error(f"Failed to validate plan: {e}")
            raise
    
    async def refine_plan(
        self,
        plan: Dict[str, Any],
        feedback: str
    ) -> Dict[str, Any]:
        """Refine a plan based on feedback."""
        try:
            # Prepare system prompt
            system_prompt = self.prompt_templates.get_prompt(
                "plan_refinement",
                plan=json.dumps(plan, indent=2),
                feedback=feedback
            )
            
            # Generate refined plan
            response = await self.model_manager.generate_response(
                input_text=feedback,
                context=json.dumps(plan, indent=2),
                system_prompt=system_prompt
            )
            
            # Parse refined plan
            refined_plan = self._parse_plan(response)
            
            # Validate refined plan
            self._validate_plan(refined_plan)
            
            return refined_plan
            
        except Exception as e:
            self.logger.error(f"Failed to refine plan: {e}")
            raise
    
    async def estimate_resources(
        self,
        plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Estimate resources needed to execute a plan."""
        try:
            # Prepare system prompt
            system_prompt = self.prompt_templates.get_prompt(
                "resource_estimation",
                plan=json.dumps(plan, indent=2)
            )
            
            # Generate resource estimation
            response = await self.model_manager.generate_response(
                input_text="Estimate resources needed for this plan",
                context=json.dumps(plan, indent=2),
                system_prompt=system_prompt
            )
            
            # Parse resource estimation
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # Parse as structured text
                resources = {
                    'time_estimate': '',
                    'required_tools': [],
                    'dependencies': [],
                    'potential_risks': []
                }
                
                current_section = None
                for line in response.split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                    
                    if line.lower().startswith('time estimate:'):
                        resources['time_estimate'] = line[14:].strip()
                    elif line.lower().startswith('required tools:'):
                        current_section = 'required_tools'
                    elif line.lower().startswith('dependencies:'):
                        current_section = 'dependencies'
                    elif line.lower().startswith('potential risks:'):
                        current_section = 'potential_risks'
                    elif current_section and line.startswith('-'):
                        resources[current_section].append(line[1:].strip())
                
                return resources
                
        except Exception as e:
            self.logger.error(f"Failed to estimate resources: {e}")
            raise 