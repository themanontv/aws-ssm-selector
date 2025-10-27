import sys
import os
import unittest
from unittest import mock
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from aws_connect import is_executable

class TestExecutable(unittest.TestCase):
    """
    Test cases for the is_executable function
    """
    @mock.patch("aws_connect.os.access", return_value=True)
    @mock.patch("aws_connect.shutil.which", return_value="/usr/local/bin/aws")
    def test_is_executable_returns_true(self, mock_which, mock_access):
        
        result = is_executable("aws")
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
