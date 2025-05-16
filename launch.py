"""
Launch script for the Jarvis system.
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

def setup_environment():
    """Set up the environment for Jarvis."""
    try:
        # Create necessary directories
        Path("data/logs").mkdir(parents=True, exist_ok=True)
        Path("data/temp").mkdir(parents=True, exist_ok=True)
        
        # Load environment variables
        load_dotenv()
        
        # Check for required environment variables
        if not os.getenv("HUGGINGFACE_TOKEN"):
            print("\nError: HUGGINGFACE_TOKEN environment variable not set")
            print("Please set your Hugging Face token using one of these methods:")
            print("1. Create a .env file with: HUGGINGFACE_TOKEN=your_token_here")
            print("2. Set it in your environment: export HUGGINGFACE_TOKEN=your_token_here")
            print("\nYou can get your token from: https://huggingface.co/settings/tokens")
            sys.exit(1)
        
    except Exception as e:
        print(f"Error setting up environment: {e}")
        raise

def main():
    """Main entry point for launching Jarvis."""
    try:
        # Set up environment first
        setup_environment()
        
        # Set up logging after directories are created
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler("data/logs/jarvis.log", mode='a')
            ]
        )
        logger = logging.getLogger("jarvis.launch")
        
        # Import and run Jarvis
        from main import Jarvis
        import asyncio
        
        print("\nStarting Jarvis...")
        print("Type 'exit', 'quit', or 'bye' to end the session")
        print("Type 'help' to see available commands")
        print("\nJarvis is ready!")
        
        # Run Jarvis
        jarvis = Jarvis()
        asyncio.run(jarvis.run())
        
    except KeyboardInterrupt:
        print("\nShutting down Jarvis...")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 