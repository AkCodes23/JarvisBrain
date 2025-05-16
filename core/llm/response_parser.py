"""
Response parser for handling LLM outputs.
"""

import logging
from typing import Dict, Any, List, Optional, Union
import json
import re
from dataclasses import dataclass
from enum import Enum

class ResponseType(Enum):
    """Types of responses that can be parsed."""
    TEXT = "text"
    JSON = "json"
    CODE = "code"
    LIST = "list"
    TABLE = "table"

@dataclass
class ParsedResponse:
    """Container for parsed response data."""
    type: ResponseType
    content: Any
    metadata: Dict[str, Any]

class ResponseParser:
    """Parses and validates LLM responses."""
    
    def __init__(self):
        """Initialize the response parser."""
        self.logger = logging.getLogger(__name__)
        
        # Regular expressions for parsing
        self.patterns = {
            'code_block': re.compile(r'```(?:(\w+)\n)?(.*?)```', re.DOTALL),
            'json_block': re.compile(r'```json\n(.*?)```', re.DOTALL),
            'list_item': re.compile(r'^\s*[-*]\s+(.+)$', re.MULTILINE),
            'table_row': re.compile(r'^\s*\|(.+)\|\s*$', re.MULTILINE)
        }
    
    def parse(self, response: str) -> ParsedResponse:
        """
        Parse a response and determine its type.
        
        Args:
            response: The response text to parse
            
        Returns:
            ParsedResponse object containing the parsed content
        """
        try:
            # Try to parse as JSON first
            try:
                content = json.loads(response)
                return ParsedResponse(
                    type=ResponseType.JSON,
                    content=content,
                    metadata={'format': 'json'}
                )
            except json.JSONDecodeError:
                pass
            
            # Check for code blocks
            code_blocks = self.patterns['code_block'].findall(response)
            if code_blocks:
                # If there's only one code block, return it
                if len(code_blocks) == 1:
                    lang, code = code_blocks[0]
                    return ParsedResponse(
                        type=ResponseType.CODE,
                        content=code.strip(),
                        metadata={'language': lang or 'text'}
                    )
                # Otherwise, return all code blocks
                return ParsedResponse(
                    type=ResponseType.CODE,
                    content=[code.strip() for _, code in code_blocks],
                    metadata={'languages': [lang or 'text' for lang, _ in code_blocks]}
                )
            
            # Check for list items
            list_items = self.patterns['list_item'].findall(response)
            if list_items:
                return ParsedResponse(
                    type=ResponseType.LIST,
                    content=list_items,
                    metadata={'format': 'markdown'}
                )
            
            # Check for table
            table_rows = self.patterns['table_row'].findall(response)
            if table_rows:
                # Parse table headers and rows
                headers = [h.strip() for h in table_rows[0].split('|') if h.strip()]
                rows = []
                for row in table_rows[1:]:
                    cells = [cell.strip() for cell in row.split('|') if cell.strip()]
                    if len(cells) == len(headers):
                        rows.append(dict(zip(headers, cells)))
                
                return ParsedResponse(
                    type=ResponseType.TABLE,
                    content=rows,
                    metadata={'headers': headers}
                )
            
            # Default to plain text
            return ParsedResponse(
                type=ResponseType.TEXT,
                content=response.strip(),
                metadata={'format': 'text'}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to parse response: {e}")
            raise
    
    def validate(self, response: ParsedResponse) -> bool:
        """
        Validate a parsed response.
        
        Args:
            response: The parsed response to validate
            
        Returns:
            True if the response is valid, False otherwise
        """
        try:
            if response.type == ResponseType.JSON:
                # Validate JSON structure
                if not isinstance(response.content, (dict, list)):
                    return False
            
            elif response.type == ResponseType.CODE:
                # Validate code content
                if not isinstance(response.content, (str, list)):
                    return False
            
            elif response.type == ResponseType.LIST:
                # Validate list content
                if not isinstance(response.content, list):
                    return False
            
            elif response.type == ResponseType.TABLE:
                # Validate table content
                if not isinstance(response.content, list):
                    return False
                if not all(isinstance(row, dict) for row in response.content):
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate response: {e}")
            return False
    
    def format(self, response: ParsedResponse) -> str:
        """
        Format a parsed response as a string.
        
        Args:
            response: The parsed response to format
            
        Returns:
            Formatted response string
        """
        try:
            if response.type == ResponseType.JSON:
                return json.dumps(response.content, indent=2)
            
            elif response.type == ResponseType.CODE:
                if isinstance(response.content, list):
                    return '\n\n'.join(
                        f"```{lang}\n{code}\n```"
                        for lang, code in zip(response.metadata['languages'], response.content)
                    )
                return f"```{response.metadata['language']}\n{response.content}\n```"
            
            elif response.type == ResponseType.LIST:
                return '\n'.join(f"- {item}" for item in response.content)
            
            elif response.type == ResponseType.TABLE:
                # Format table with headers
                headers = response.metadata['headers']
                rows = [headers] + [[row[h] for h in headers] for row in response.content]
                
                # Calculate column widths
                col_widths = [
                    max(len(str(cell)) for cell in col)
                    for col in zip(*rows)
                ]
                
                # Format table
                lines = []
                for row in rows:
                    line = '| ' + ' | '.join(
                        str(cell).ljust(width)
                        for cell, width in zip(row, col_widths)
                    ) + ' |'
                    lines.append(line)
                
                return '\n'.join(lines)
            
            return str(response.content)
            
        except Exception as e:
            self.logger.error(f"Failed to format response: {e}")
            raise 