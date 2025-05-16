"""
Status display for visual indicators.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path

class StatusDisplay:
    """Manages visual status indicators."""
    
    def __init__(self, status_file: str = "data/status.json"):
        """
        Initialize status display.
        
        Args:
            status_file: Path to status file
        """
        self.logger = logging.getLogger(__name__)
        self.status_file = Path(status_file)
        self.status_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize status
        self.status = {
            'system': {
                'status': 'initializing',
                'last_updated': datetime.now().isoformat()
            },
            'components': {}
        }
        
        # Load existing status if available
        self._load_status()
    
    def update_system_status(self, status: str) -> None:
        """
        Update system status.
        
        Args:
            status: New system status
        """
        try:
            self.status['system'].update({
                'status': status,
                'last_updated': datetime.now().isoformat()
            })
            self._save_status()
            
        except Exception as e:
            self.logger.error(f"Failed to update system status: {e}")
            raise
    
    def update_component_status(
        self,
        component: str,
        status: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Update component status.
        
        Args:
            component: Component name
            status: New component status
            details: Optional component details
        """
        try:
            self.status['components'][component] = {
                'status': status,
                'last_updated': datetime.now().isoformat(),
                'details': details or {}
            }
            self._save_status()
            
        except Exception as e:
            self.logger.error(f"Failed to update component status: {e}")
            raise
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current status.
        
        Returns:
            Dictionary containing current status
        """
        return self.status.copy()
    
    def _load_status(self) -> None:
        """Load status from file."""
        try:
            if self.status_file.exists():
                with open(self.status_file, 'r') as f:
                    self.status = json.load(f)
            
        except Exception as e:
            self.logger.error(f"Failed to load status: {e}")
            raise
    
    def _save_status(self) -> None:
        """Save status to file."""
        try:
            with open(self.status_file, 'w') as f:
                json.dump(self.status, f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Failed to save status: {e}")
            raise 