"""
Test fixtures for Jarvis.
"""

import os
from pathlib import Path

# Get fixtures directory
FIXTURES_DIR = Path(__file__).parent

def get_fixture_path(name: str) -> Path:
    """
    Get path to a fixture file.
    
    Args:
        name: Fixture file name
        
    Returns:
        Path to fixture file
    """
    return FIXTURES_DIR / name 