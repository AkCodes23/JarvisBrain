"""
Web-based tools for searching and gathering information.
"""

import aiohttp
import asyncio
from typing import Any, Dict, List
from bs4 import BeautifulSoup
from .base_tool import BaseTool, ToolResult

class WebSearchTool(BaseTool):
    """Tool for performing web searches."""
    
    def __init__(self):
        super().__init__(
            name="web_search",
            description="Search the web for information"
        )
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "query": {
                "type": "string",
                "description": "The search query",
                "required": True
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return",
                "required": False,
                "default": 5
            }
        }
    
    async def execute(self, **kwargs) -> ToolResult:
        try:
            query = kwargs["query"]
            max_results = kwargs.get("max_results", 5)
            
            # Use a search API (you'll need to implement this)
            # For now, we'll use a simple web search
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://www.google.com/search?q={query}",
                    headers={"User-Agent": "Mozilla/5.0"}
                ) as response:
                    if response.status != 200:
                        return ToolResult(
                            success=False,
                            data=None,
                            error=f"Search failed with status {response.status}"
                        )
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract search results
                    results = []
                    for result in soup.select("div.g")[:max_results]:
                        title = result.select_one("h3")
                        link = result.select_one("a")
                        snippet = result.select_one("div.VwiC3b")
                        
                        if title and link and snippet:
                            results.append({
                                "title": title.text,
                                "url": link["href"],
                                "snippet": snippet.text
                            })
                    
                    return ToolResult(
                        success=True,
                        data=results
                    )
                    
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                error=str(e)
            )

class WeatherTool(BaseTool):
    """Tool for getting weather information."""
    
    def __init__(self):
        super().__init__(
            name="weather",
            description="Get current weather information"
        )
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "location": {
                "type": "string",
                "description": "City name or coordinates",
                "required": True
            }
        }
    
    async def execute(self, **kwargs) -> ToolResult:
        try:
            location = kwargs["location"]
            
            # Use web search to get weather information
            search_tool = WebSearchTool()
            result = await search_tool.execute(
                query=f"current weather in {location}",
                max_results=1
            )
            
            if not result.success:
                return result
            
            return ToolResult(
                success=True,
                data=result.data[0] if result.data else None
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                error=str(e)
            )

class NewsTool(BaseTool):
    """Tool for getting news information."""
    
    def __init__(self):
        super().__init__(
            name="news",
            description="Get latest news"
        )
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "topic": {
                "type": "string",
                "description": "News topic or category",
                "required": False
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return",
                "required": False,
                "default": 5
            }
        }
    
    async def execute(self, **kwargs) -> ToolResult:
        try:
            topic = kwargs.get("topic", "latest news")
            max_results = kwargs.get("max_results", 5)
            
            # Use web search to get news
            search_tool = WebSearchTool()
            result = await search_tool.execute(
                query=topic,
                max_results=max_results
            )
            
            if not result.success:
                return result
            
            return ToolResult(
                success=True,
                data=result.data
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                error=str(e)
            ) 