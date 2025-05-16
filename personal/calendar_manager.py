"""
Calendar manager module for handling personal calendar events.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
from pathlib import Path

class CalendarManager:
    """Manages personal calendar events and schedules."""
    
    def __init__(self, storage_path: str = "data/user_data/calendar"):
        """Initialize calendar manager with storage configuration."""
        self.logger = logging.getLogger(__name__)
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def add_event(self, event: Dict[str, Any]) -> None:
        """Add a new calendar event."""
        try:
            events = self._load_events()
            events.append(event)
            self._save_events(events)
        except Exception as e:
            self.logger.error(f"Failed to add event: {e}")
            raise
    
    def get_events(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get calendar events within a date range."""
        try:
            events = self._load_events()
            if start_date and end_date:
                return [
                    event for event in events
                    if start_date <= datetime.fromisoformat(event['start_time']) <= end_date
                ]
            return events
        except Exception as e:
            self.logger.error(f"Failed to get events: {e}")
            raise
    
    def update_event(self, event_id: str, updates: Dict[str, Any]) -> None:
        """Update an existing calendar event."""
        try:
            events = self._load_events()
            for event in events:
                if event['id'] == event_id:
                    event.update(updates)
                    break
            self._save_events(events)
        except Exception as e:
            self.logger.error(f"Failed to update event: {e}")
            raise
    
    def delete_event(self, event_id: str) -> None:
        """Delete a calendar event."""
        try:
            events = self._load_events()
            events = [event for event in events if event['id'] != event_id]
            self._save_events(events)
        except Exception as e:
            self.logger.error(f"Failed to delete event: {e}")
            raise
    
    def _load_events(self) -> List[Dict[str, Any]]:
        """Load events from storage."""
        try:
            events_file = self.storage_path / "events.json"
            if events_file.exists():
                with open(events_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            self.logger.error(f"Failed to load events: {e}")
            raise
    
    def _save_events(self, events: List[Dict[str, Any]]) -> None:
        """Save events to storage."""
        try:
            events_file = self.storage_path / "events.json"
            with open(events_file, 'w') as f:
                json.dump(events, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save events: {e}")
            raise 