"""
Task manager module for handling personal tasks and to-dos.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from pathlib import Path

class TaskManager:
    """Manages personal tasks and to-dos."""
    
    def __init__(self, storage_path: str = "data/user_data/tasks"):
        """Initialize task manager with storage configuration."""
        self.logger = logging.getLogger(__name__)
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def add_task(self, task: Dict[str, Any]) -> None:
        """Add a new task."""
        try:
            tasks = self._load_tasks()
            task['id'] = str(len(tasks) + 1)
            task['created_at'] = datetime.now().isoformat()
            task['completed'] = False
            tasks.append(task)
            self._save_tasks(tasks)
        except Exception as e:
            self.logger.error(f"Failed to add task: {e}")
            raise
    
    def get_tasks(self, completed: Optional[bool] = None) -> List[Dict[str, Any]]:
        """Get tasks, optionally filtered by completion status."""
        try:
            tasks = self._load_tasks()
            if completed is not None:
                return [task for task in tasks if task['completed'] == completed]
            return tasks
        except Exception as e:
            self.logger.error(f"Failed to get tasks: {e}")
            raise
    
    def update_task(self, task_id: str, updates: Dict[str, Any]) -> None:
        """Update an existing task."""
        try:
            tasks = self._load_tasks()
            for task in tasks:
                if task['id'] == task_id:
                    task.update(updates)
                    break
            self._save_tasks(tasks)
        except Exception as e:
            self.logger.error(f"Failed to update task: {e}")
            raise
    
    def delete_task(self, task_id: str) -> None:
        """Delete a task."""
        try:
            tasks = self._load_tasks()
            tasks = [task for task in tasks if task['id'] != task_id]
            self._save_tasks(tasks)
        except Exception as e:
            self.logger.error(f"Failed to delete task: {e}")
            raise
    
    def _load_tasks(self) -> List[Dict[str, Any]]:
        """Load tasks from storage."""
        try:
            tasks_file = self.storage_path / "tasks.json"
            if tasks_file.exists():
                with open(tasks_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            self.logger.error(f"Failed to load tasks: {e}")
            raise
    
    def _save_tasks(self, tasks: List[Dict[str, Any]]) -> None:
        """Save tasks to storage."""
        try:
            tasks_file = self.storage_path / "tasks.json"
            with open(tasks_file, 'w') as f:
                json.dump(tasks, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save tasks: {e}")
            raise 