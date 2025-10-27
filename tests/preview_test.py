import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import unittest
from unittest import mock
from aws_connect import preview

class TestFilterMetrics(unittest.TestCase):
    """
    Test cases for the preview function
    """
        
    def test_is_executable_returns_true(self, mock_which, mock_access):
        #TODO: Add
        print("hello")

if __name__ == '__main__':
    unittest.main()
