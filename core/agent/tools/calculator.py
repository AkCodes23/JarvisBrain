"""
Calculator tool implementation for the agent.
"""

import logging
from typing import Union, Dict, Any
import math
import operator

class CalculatorTool:
    """Tool for performing mathematical calculations."""
    
    def __init__(self):
        """Initialize the calculator tool."""
        self.logger = logging.getLogger(__name__)
        
        # Define supported operations
        self.operations = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv,
            '**': operator.pow,
            'sqrt': math.sqrt,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'log': math.log,
            'log10': math.log10,
            'exp': math.exp
        }
    
    def calculate(self, expression: str) -> Union[float, int]:
        """
        Evaluate a mathematical expression.
        
        Args:
            expression: The mathematical expression to evaluate
            
        Returns:
            The result of the calculation
        """
        try:
            # TODO: Implement proper expression parsing
            # This is a simple implementation that only handles basic operations
            parts = expression.split()
            if len(parts) != 3:
                raise ValueError("Expression must be in format: number operator number")
            
            num1 = float(parts[0])
            op = parts[1]
            num2 = float(parts[2])
            
            if op not in self.operations:
                raise ValueError(f"Unsupported operation: {op}")
            
            return self.operations[op](num1, num2)
            
        except Exception as e:
            self.logger.error(f"Calculation failed: {e}")
            raise
    
    def evaluate_function(self, func_name: str, *args: float) -> float:
        """
        Evaluate a mathematical function.
        
        Args:
            func_name: Name of the function to evaluate
            *args: Arguments to pass to the function
            
        Returns:
            The result of the function evaluation
        """
        try:
            if func_name not in self.operations:
                raise ValueError(f"Unsupported function: {func_name}")
            
            return self.operations[func_name](*args)
            
        except Exception as e:
            self.logger.error(f"Function evaluation failed: {e}")
            raise 