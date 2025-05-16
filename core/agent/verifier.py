"""
Result verifier module for validating execution results.
"""

import logging
from typing import Dict, List, Optional, Any, Union
import json
from datetime import datetime
import asyncio
from ..llm.model_manager import ModelManager
from ..llm.prompt_templates import PromptTemplates

class ResultVerifier:
    """Validates and verifies execution results."""
    
    def __init__(
        self,
        model_manager: ModelManager,
        prompt_templates: PromptTemplates
    ):
        """Initialize result verifier with components."""
        self.logger = logging.getLogger(__name__)
        self.model_manager = model_manager
        self.prompt_templates = prompt_templates
    
    async def verify_results(
        self,
        results: Dict[str, Any],
        expected_outcome: Optional[str] = None
    ) -> Dict[str, Any]:
        """Verify execution results against expected outcome."""
        try:
            # Prepare verification data
            verification_data = {
                'results': results,
                'expected_outcome': expected_outcome,
                'verification_time': datetime.now().isoformat()
            }
            
            # Generate verification prompt
            system_prompt = self.prompt_templates.get_prompt(
                "result_verification",
                results=json.dumps(results, indent=2),
                expected_outcome=expected_outcome
            )
            
            # Generate verification
            response = await self.model_manager.generate_response(
                input_text="Verify these execution results",
                context=json.dumps(results, indent=2),
                system_prompt=system_prompt
            )
            
            # Parse verification
            verification = self._parse_verification(response)
            
            # Add verification data
            verification.update(verification_data)
            
            return verification
            
        except Exception as e:
            self.logger.error(f"Failed to verify results: {e}")
            raise
    
    def _parse_verification(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into a structured verification."""
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
            verification = {
                'success': False,
                'verification': '',
                'issues': [],
                'suggestions': []
            }
            
            current_section = None
            for line in response.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                if line.lower().startswith('verification:'):
                    verification['verification'] = line[12:].strip()
                elif line.lower().startswith('success:'):
                    verification['success'] = line[7:].strip().lower() == 'true'
                elif line.lower().startswith('issues:'):
                    current_section = 'issues'
                elif line.lower().startswith('suggestions:'):
                    current_section = 'suggestions'
                elif current_section and line.startswith('-'):
                    verification[current_section].append(line[1:].strip())
            
            return verification
            
        except Exception as e:
            self.logger.error(f"Failed to parse verification: {e}")
            raise
    
    async def verify_step(
        self,
        step_result: Dict[str, Any],
        step_definition: str
    ) -> Dict[str, Any]:
        """Verify a single step execution result."""
        try:
            # Prepare verification data
            verification_data = {
                'step_result': step_result,
                'step_definition': step_definition,
                'verification_time': datetime.now().isoformat()
            }
            
            # Generate verification prompt
            system_prompt = self.prompt_templates.get_prompt(
                "step_verification",
                step_result=json.dumps(step_result, indent=2),
                step_definition=step_definition
            )
            
            # Generate verification
            response = await self.model_manager.generate_response(
                input_text="Verify this step execution result",
                context=json.dumps(step_result, indent=2),
                system_prompt=system_prompt
            )
            
            # Parse verification
            verification = self._parse_verification(response)
            
            # Add verification data
            verification.update(verification_data)
            
            return verification
            
        except Exception as e:
            self.logger.error(f"Failed to verify step: {e}")
            raise
    
    async def suggest_improvements(
        self,
        results: Dict[str, Any],
        verification: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Suggest improvements based on verification results."""
        try:
            # Prepare improvement data
            improvement_data = {
                'results': results,
                'verification': verification,
                'suggestion_time': datetime.now().isoformat()
            }
            
            # Generate improvement prompt
            system_prompt = self.prompt_templates.get_prompt(
                "improvement_suggestions",
                results=json.dumps(results, indent=2),
                verification=json.dumps(verification, indent=2)
            )
            
            # Generate suggestions
            response = await self.model_manager.generate_response(
                input_text="Suggest improvements for these results",
                context=json.dumps(improvement_data, indent=2),
                system_prompt=system_prompt
            )
            
            # Parse suggestions
            try:
                suggestions = json.loads(response)
            except json.JSONDecodeError:
                # Parse as structured text
                suggestions = []
                current_suggestion = {}
                
                for line in response.split('\n'):
                    line = line.strip()
                    if not line:
                        if current_suggestion:
                            suggestions.append(current_suggestion)
                            current_suggestion = {}
                        continue
                    
                    if line.startswith('Suggestion'):
                        if current_suggestion:
                            suggestions.append(current_suggestion)
                        current_suggestion = {'title': line}
                    elif ':' in line:
                        key, value = line.split(':', 1)
                        current_suggestion[key.strip()] = value.strip()
                
                if current_suggestion:
                    suggestions.append(current_suggestion)
            
            return suggestions
            
        except Exception as e:
            self.logger.error(f"Failed to suggest improvements: {e}")
            raise 