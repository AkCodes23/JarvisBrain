"""
System tools implementation for the agent.
"""

import logging
import os
import platform
import psutil
from typing import Dict, Any, List
import subprocess
import shutil

class SystemTools:
    """Tools for interacting with the system."""
    
    def __init__(self):
        """Initialize the system tools."""
        self.logger = logging.getLogger(__name__)
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get information about the system.
        
        Returns:
            Dictionary containing system information
        """
        try:
            return {
                'platform': platform.system(),
                'platform_version': platform.version(),
                'architecture': platform.machine(),
                'processor': platform.processor(),
                'python_version': platform.python_version(),
                'memory': {
                    'total': psutil.virtual_memory().total,
                    'available': psutil.virtual_memory().available,
                    'used': psutil.virtual_memory().used,
                    'percent': psutil.virtual_memory().percent
                },
                'disk': {
                    'total': psutil.disk_usage('/').total,
                    'used': psutil.disk_usage('/').used,
                    'free': psutil.disk_usage('/').free,
                    'percent': psutil.disk_usage('/').percent
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to get system info: {e}")
            raise
    
    def get_process_info(self) -> List[Dict[str, Any]]:
        """
        Get information about running processes.
        
        Returns:
            List of dictionaries containing process information
        """
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            return processes
        except Exception as e:
            self.logger.error(f"Failed to get process info: {e}")
            raise
    
    def execute_command(self, command: str) -> Dict[str, Any]:
        """
        Execute a system command.
        
        Args:
            command: The command to execute
            
        Returns:
            Dictionary containing command output and status
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True
            )
            
            return {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode,
                'success': result.returncode == 0
            }
        except Exception as e:
            self.logger.error(f"Failed to execute command: {e}")
            raise
    
    def get_file_info(self, path: str) -> Dict[str, Any]:
        """
        Get information about a file or directory.
        
        Args:
            path: Path to the file or directory
            
        Returns:
            Dictionary containing file information
        """
        try:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Path does not exist: {path}")
            
            stats = os.stat(path)
            
            return {
                'path': path,
                'size': stats.st_size,
                'created': stats.st_ctime,
                'modified': stats.st_mtime,
                'accessed': stats.st_atime,
                'is_file': os.path.isfile(path),
                'is_dir': os.path.isdir(path),
                'permissions': oct(stats.st_mode)[-3:]
            }
        except Exception as e:
            self.logger.error(f"Failed to get file info: {e}")
            raise
    
    def get_directory_contents(self, path: str) -> List[Dict[str, Any]]:
        """
        Get contents of a directory.
        
        Args:
            path: Path to the directory
            
        Returns:
            List of dictionaries containing file/directory information
        """
        try:
            if not os.path.isdir(path):
                raise NotADirectoryError(f"Path is not a directory: {path}")
            
            contents = []
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                contents.append(self.get_file_info(item_path))
            
            return contents
        except Exception as e:
            self.logger.error(f"Failed to get directory contents: {e}")
            raise 