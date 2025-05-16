"""
LLM Manager for handling language model interactions.
"""

import os
import logging
from typing import Dict, Any, Optional
from transformers import pipeline

class LLMManager:
    """Manages interactions with the language model."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the LLM manager."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.model = None
        
    async def initialize(self):
        """Initialize the language model."""
        self.logger.info("Initializing LLM manager...")
        try:
            self.model = pipeline(
                "text-generation",
                model="distilgpt2",
                device_map="auto"
            )
            self.logger.info("LLM initialized with model: distilgpt2")
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM: {str(e)}")
            raise
        
    async def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate a response from the language model."""
        if not self.model:
            raise RuntimeError("LLM not initialized")
            
        try:
            # Prepare the input
            if context:
                full_prompt = f"Context: {context}\n\nQuestion: {prompt}\n\nAnswer:"
            else:
                full_prompt = f"Question: {prompt}\n\nAnswer:"
                
            # Generate response
            outputs = self.model(
                full_prompt,
                max_length=512,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True
            )
            
            # Extract response
            response = outputs[0]['generated_text']
            return response.split("Answer:")[-1].strip()
            
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            return f"Error: {str(e)}"
    
    async def shutdown(self):
        """Clean up resources."""
        self.logger.info("Shutting down LLM manager...")
        if self.model:
            del self.model 