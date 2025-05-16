"""
Integration tests for Jarvis.
"""

import unittest

def run_tests():
    """Run all integration tests."""
    loader = unittest.TestLoader()
    start_dir = '.'
    suite = loader.discover(start_dir, pattern='test_*.py')
    runner = unittest.TextTestRunner()
    runner.run(suite) 