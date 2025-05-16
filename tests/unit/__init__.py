"""
Unit tests for Jarvis.
"""

import unittest

def run_tests():
    """Run all unit tests."""
    loader = unittest.TestLoader()
    start_dir = '.'
    suite = loader.discover(start_dir, pattern='test_*.py')
    runner = unittest.TextTestRunner()
    runner.run(suite) 