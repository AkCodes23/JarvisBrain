"""
System-level tools for the agent.
"""

import os
import platform
import psutil
from typing import Any, Dict, List
from datetime import datetime
from .base_tool import BaseTool, ToolResult

class SystemInfoTool(BaseTool):
    """Tool for getting system information."""
    
    def __init__(self):
        super().__init__(
            name="system_info",
            description="Get information about the system"
        )
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "info_type": {
                "type": "string",
                "description": "Type of information to get (cpu, memory, disk, all)",
                "required": False,
                "default": "all"
            }
        }
    
    async def execute(self, **kwargs) -> ToolResult:
        try:
            info_type = kwargs.get("info_type", "all")
            info = {}
            
            if info_type in ["cpu", "all"]:
                info["cpu"] = {
                    "usage_percent": psutil.cpu_percent(interval=1),
                    "count": psutil.cpu_count(),
                    "frequency": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
                }
            
            if info_type in ["memory", "all"]:
                memory = psutil.virtual_memory()
                info["memory"] = {
                    "total": memory.total,
                    "available": memory.available,
                    "used": memory.used,
                    "percent": memory.percent
                }
            
            if info_type in ["disk", "all"]:
                disk = psutil.disk_usage('/')
                info["disk"] = {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": disk.percent
                }
            
            if info_type in ["all"]:
                info["system"] = {
                    "platform": platform.platform(),
                    "python_version": platform.python_version(),
                    "hostname": platform.node(),
                    "time": datetime.now().isoformat()
                }
            
            return ToolResult(
                success=True,
                data=info
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                error=str(e)
            )

class FileSystemTool(BaseTool):
    """Tool for file system operations."""
    
    def __init__(self):
        super().__init__(
            name="file_system",
            description="Perform file system operations"
        )
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "operation": {
                "type": "string",
                "description": "Operation to perform (list, read, write, delete)",
                "required": True
            },
            "path": {
                "type": "string",
                "description": "File or directory path",
                "required": True
            },
            "content": {
                "type": "string",
                "description": "Content to write (for write operation)",
                "required": False
            }
        }
    
    async def execute(self, **kwargs) -> ToolResult:
        try:
            operation = kwargs["operation"]
            path = kwargs["path"]
            
            if operation == "list":
                if not os.path.exists(path):
                    return ToolResult(
                        success=False,
                        data=None,
                        error=f"Path does not exist: {path}"
                    )
                
                items = os.listdir(path)
                return ToolResult(
                    success=True,
                    data={
                        "path": path,
                        "items": items
                    }
                )
            
            elif operation == "read":
                if not os.path.isfile(path):
                    return ToolResult(
                        success=False,
                        data=None,
                        error=f"Not a file: {path}"
                    )
                
                with open(path, 'r') as f:
                    content = f.read()
                return ToolResult(
                    success=True,
                    data={
                        "path": path,
                        "content": content
                    }
                )
            
            elif operation == "write":
                content = kwargs.get("content", "")
                with open(path, 'w') as f:
                    f.write(content)
                return ToolResult(
                    success=True,
                    data={
                        "path": path,
                        "status": "written"
                    }
                )
            
            elif operation == "delete":
                if not os.path.exists(path):
                    return ToolResult(
                        success=False,
                        data=None,
                        error=f"Path does not exist: {path}"
                    )
                
                if os.path.isfile(path):
                    os.remove(path)
                else:
                    os.rmdir(path)
                return ToolResult(
                    success=True,
                    data={
                        "path": path,
                        "status": "deleted"
                    }
                )
            
            else:
                return ToolResult(
                    success=False,
                    data=None,
                    error=f"Unknown operation: {operation}"
                )
            
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                error=str(e)
            )

class ProcessTool(BaseTool):
    """Tool for process management."""
    
    def __init__(self):
        super().__init__(
            name="process",
            description="Manage system processes"
        )
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "operation": {
                "type": "string",
                "description": "Operation to perform (list, kill)",
                "required": True
            },
            "pid": {
                "type": "integer",
                "description": "Process ID (for kill operation)",
                "required": False
            }
        }
    
    async def execute(self, **kwargs) -> ToolResult:
        try:
            operation = kwargs["operation"]
            
            if operation == "list":
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                    try:
                        processes.append(proc.info)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                return ToolResult(
                    success=True,
                    data=processes
                )
            
            elif operation == "kill":
                pid = kwargs.get("pid")
                if not pid:
                    return ToolResult(
                        success=False,
                        data=None,
                        error="PID is required for kill operation"
                    )
                
                try:
                    process = psutil.Process(pid)
                    process.terminate()
                    return ToolResult(
                        success=True,
                        data={
                            "pid": pid,
                            "status": "terminated"
                        }
                    )
                except psutil.NoSuchProcess:
                    return ToolResult(
                        success=False,
                        data=None,
                        error=f"Process not found: {pid}"
                    )
            
            else:
                return ToolResult(
                    success=False,
                    data=None,
                    error=f"Unknown operation: {operation}"
                )
            
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                error=str(e)
            ) 