"""
Main entry point for the Jarvis system.
"""

import asyncio
import logging
from typing import Optional, Any
import yaml
from pathlib import Path
from core.agent.main_agent import MainAgent

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Jarvis:
    """Main Jarvis system class."""
    
    def __init__(self):
        """Initialize the Jarvis system."""
        self.agent = MainAgent()
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """Load configuration from files."""
        try:
            # Load default config
            with open('config/default_config.yaml', 'r') as f:
                default_config = yaml.safe_load(f)
            
            # Load user config if it exists
            user_config_path = Path('config/user_config.yaml')
            if user_config_path.exists():
                with open(user_config_path, 'r') as f:
                    user_config = yaml.safe_load(f)
                # Merge configurations
                return {**default_config, **user_config}
            
            return default_config
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    async def process_input(self, input_data: str) -> Optional[Any]:
        """Process user input through the agent system."""
        try:
            result = await self.agent.run(input_data)
            return result
        except Exception as e:
            logger.error(f"Error processing input: {e}")
            return None
    
    async def run(self):
        """Main execution loop."""
        logger.info("Jarvis system started")
        
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    logger.info("Shutting down Jarvis system")
                    break
                
                # Process input
                result = await self.process_input(user_input)
                
                # Display result
                if result:
                    print("\nJarvis:", result)
                else:
                    print("\nJarvis: I'm sorry, I couldn't process that request.")
                
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt, shutting down")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                print("\nJarvis: I encountered an error. Please try again.")

async def main():
    """Main entry point."""
    jarvis = Jarvis()
    await jarvis.run()

if __name__ == "__main__":
    asyncio.run(main())
