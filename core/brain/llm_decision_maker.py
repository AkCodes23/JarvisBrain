"""
LLM-based decision maker for the agent system.
"""

import os
from typing import Any, Dict, List, Optional
import logging
from dataclasses import dataclass
import json
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

@dataclass
class ToolDescription:
    """Description of a tool for the LLM."""
    name: str
    description: str
    parameters: Dict[str, Any]

class LLMDecisionMaker:
    """Makes decisions using an LLM."""
    
    def __init__(self, model_name: str = "meta-llama/Llama-3.3-70B-Instruct"):
        """Initialize the decision maker."""
        self.model_name = model_name
        self.logger = logging.getLogger("brain.llm_decision_maker")
        self.tools: List[ToolDescription] = []
        
        # Load model and tokenizer
        self.logger.info(f"Loading model {model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            token=os.getenv("HUGGINGFACE_TOKEN")
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto",
            token=os.getenv("HUGGINGFACE_TOKEN")
        )
        self.logger.info("Model loaded successfully")
    
    def add_tool(self, tool: ToolDescription) -> None:
        """Add a tool to the decision maker."""
        self.tools.append(tool)
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for the LLM."""
        tool_descriptions = "\n".join(
            f"Tool: {tool.name}\n"
            f"Description: {tool.description}\n"
            f"Parameters: {json.dumps(tool.parameters, indent=2)}\n"
            for tool in self.tools
        )
        
        return f"""<s>[INST] <<SYS>>
You are an AI assistant that helps users by using various tools. Your task is to:
1. Understand the user's request
2. Choose the most appropriate tool
3. Extract the necessary parameters from the request
4. Return a JSON object with the tool name and parameters

Available tools:
{tool_descriptions}

Respond with a JSON object in this format:
{{
    "tool": "tool_name",
    "parameters": {{
        "param1": "value1",
        "param2": "value2"
    }},
    "reasoning": "Brief explanation of why this tool was chosen"
}}
<</SYS>>

User: {{user_input}} [/INST]"""
    
    async def decide(self, user_input: str) -> Dict[str, Any]:
        """Make a decision about which tool to use."""
        try:
            # Create the system prompt
            prompt = self._create_system_prompt().format(user_input=user_input)
            
            # Generate response
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
            outputs = self.model.generate(
                **inputs,
                max_length=500,
                temperature=0.7,
                do_sample=True,
                top_p=0.9,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            # Decode and parse the response
            response_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            response_text = response_text.split("[/INST]")[-1].strip()
            
            # Extract JSON from response
            try:
                # Find the first { and last }
                start = response_text.find("{")
                end = response_text.rfind("}") + 1
                if start >= 0 and end > start:
                    json_str = response_text[start:end]
                    decision = json.loads(json_str)
                else:
                    raise ValueError("No JSON object found in response")
            except json.JSONDecodeError:
                raise ValueError("Failed to parse JSON from response")
            
            # Validate the decision
            if "tool" not in decision or "parameters" not in decision:
                raise ValueError("Invalid decision format")
            
            # Check if the tool exists
            if not any(tool.name == decision["tool"] for tool in self.tools):
                raise ValueError(f"Unknown tool: {decision['tool']}")
            
            return decision
            
        except Exception as e:
            self.logger.error(f"Error making decision: {e}")
            raise
    
    def get_tool_help(self) -> str:
        """Get help text for all tools."""
        return "\n\n".join(
            f"Tool: {tool.name}\n"
            f"Description: {tool.description}\n"
            f"Parameters: {json.dumps(tool.parameters, indent=2)}"
            for tool in self.tools
        ) 