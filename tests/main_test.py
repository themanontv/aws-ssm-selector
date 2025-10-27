import sys
import os
import json
import subprocess
import argparse
import unittest
from unittest import mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from aws_connect import main

class TestMain(unittest.TestCase):
    """
    Test cases for the preview function
    """
    def setUp(self):
        base = os.path.dirname(__file__)
        instance_data_path = os.path.join(base, 'payloads/instance_data.json')
        with open(instance_data_path, 'r') as f:
            self.instance_data = f.read()

    @mock.patch('aws_connect.os.getenv', return_value='test')
    @mock.patch('aws_connect.is_executable', return_value=True)
    @mock.patch('aws_connect.argparse.ArgumentParser.parse_args',
    return_value=argparse.Namespace(region=None))
    def test_os_profile(self, mock_args, mock_is_executable, mock_getenv):
        fake = subprocess.CompletedProcess(args=['cmd'], returncode=0, stdout=self.instance_data)
        with mock.patch('aws_connect.subprocess.run', return_value=fake):
            result = main(False)
    
    @mock.patch('aws_connect.os.getenv', return_value='test')
    @mock.patch('aws_connect.is_executable', return_value=True)
    @mock.patch('aws_connect.argparse.ArgumentParser.parse_args',
    return_value=argparse.Namespace(region="eu-west-1"))
    def test_os_profile_args(self, mock_args, mock_is_executable, mock_getenv):
        fake = subprocess.CompletedProcess(args=['cmd'], returncode=0, stdout=self.instance_data)
        with mock.patch('aws_connect.subprocess.run', return_value=fake):
            result = main(False)

    @mock.patch('aws_connect.os.getenv', return_value=None)
    @mock.patch('aws_connect.is_executable', return_value=True)
    @mock.patch('aws_connect.argparse.ArgumentParser.parse_args',
    return_value=argparse.Namespace(region="eu-west-2"))
    def test_get_profile(self, mock_args, mock_is_executable, mock_getenv):
        fake = subprocess.CompletedProcess(args=['cmd'], returncode=0, stdout=self.instance_data)
        with mock.patch('aws_connect.open', mock.mock_open(read_data="[profile test]")) as mock_file:
            with mock.patch('aws_connect.subprocess.run', return_value=fake):
                result = main(False)
    
    @mock.patch('aws_connect.os.getenv', return_value=None)
    @mock.patch('aws_connect.is_executable', return_value=True)
    @mock.patch('aws_connect.argparse.ArgumentParser.parse_args',
    return_value=argparse.Namespace(region="us-east-1"))
    def test_get_profile_args(self, mock_args, mock_is_executable, mock_getenv):
        fake = subprocess.CompletedProcess(args=['cmd'], returncode=0, stdout=self.instance_data)
        with mock.patch('aws_connect.open', mock.mock_open(read_data="[profile test]")) as mock_file:
            with mock.patch('aws_connect.subprocess.run', return_value=fake):
                result = main(False)

    @unittest.expectedFailure
    @mock.patch('aws_connect.os.getenv', return_value=None)
    @mock.patch('aws_connect.is_executable', return_value=True)
    @mock.patch('aws_connect.argparse.ArgumentParser.parse_args',
    return_value=argparse.Namespace(region="eu-west-2"))
    def test_get_profile_error(self, mock_args, mock_is_executable, mock_getenv):
        fake = subprocess.CompletedProcess(args=['cmd'], returncode=0, stdout=self.instance_data)
        with mock.patch('aws_connect.open', mock.mock_open(read_data="[test]")) as mock_file:
            with mock.patch('aws_connect.subprocess.run', return_value=fake):
                result = main(False)
                
if __name__ == '__main__':
    unittest.main()
