"""
Performance metrics utility module for tracking system performance.
"""

import time
from typing import Dict, Any
from contextlib import contextmanager
from datetime import datetime

class PerformanceTracker:
    """Tracks and records performance metrics."""
    
    def __init__(self):
        """Initialize performance tracker."""
        self.metrics: Dict[str, Dict[str, Any]] = {}
    
    @contextmanager
    def track(self, operation: str):
        """Track the execution time of an operation."""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            if operation not in self.metrics:
                self.metrics[operation] = {
                    'count': 0,
                    'total_time': 0,
                    'avg_time': 0,
                    'last_execution': None
                }
            
            self.metrics[operation]['count'] += 1
            self.metrics[operation]['total_time'] += duration
            self.metrics[operation]['avg_time'] = (
                self.metrics[operation]['total_time'] / 
                self.metrics[operation]['count']
            )
            self.metrics[operation]['last_execution'] = datetime.now().isoformat()
    
    def get_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get current performance metrics."""
        return self.metrics 