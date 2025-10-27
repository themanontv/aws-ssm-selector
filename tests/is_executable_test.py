import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import unittest
from unittest import mock
import shutil
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
        mock_which.assert_called_once_with("aws")
        mock_access.assert_called_once_with("/usr/local/bin/aws", os.X_OK)

if __name__ == '__main__':
    unittest.main()
