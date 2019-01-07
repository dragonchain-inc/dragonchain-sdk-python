# Copyright 2019 Dragonchain, Inc. or its affiliates. All Rights Reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from unittest import TestCase
from mock import patch
import os
import configparser
import hashlib
from dragonchain_sdk.credentials import Credentials
from dragonchain_sdk import exceptions

config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_credentials')


class TestCredentialsInitialization(TestCase):
    def test_gets_credentials_from_parameters_raises_type_error(self):
        self.assertRaises(TypeError, Credentials, dragonchain_id={}, auth_key='TestKey', auth_key_id='TestKeyId')
        self.assertRaises(TypeError, Credentials, dragonchain_id='TestID', auth_key={}, auth_key_id='TestKeyId')
        self.assertRaises(TypeError, Credentials, dragonchain_id='TestID', auth_key='TestKey', auth_key_id={})

    def test_gets_credentials_from_parameters(self):
        credentials = Credentials(dragonchain_id='TestID', auth_key='TestKey', auth_key_id='TestKeyId')
        self.assertEqual(credentials.dragonchain_id, 'TestID')
        self.assertEqual(credentials.auth_key, 'TestKey')
        self.assertEqual(credentials.auth_key_id, 'TestKeyId')

    @patch('dragonchain_sdk.credentials.Credentials.get_credential_file_path', return_value='does_not_exist.ini')
    def test_raises_on_credentials_non_existent(self, mock_path):
        self.assertRaises(exceptions.DragonchainIdentityNotFound, Credentials)

    @patch('dragonchain_sdk.credentials.Credentials.get_credential_file_path', return_value=config_file)
    def test_gets_credentials_from_config_file(self, mock_path):
        credentials = Credentials()
        self.assertEqual(credentials.dragonchain_id, 'TestID')
        self.assertEqual(credentials.auth_key, 'TestKey')
        self.assertEqual(credentials.auth_key_id, 'TestKeyId')

    @patch('dragonchain_sdk.credentials.configparser.ConfigParser')
    def test_gets_credentials_from_config_file_raises_on_no_section(self, mock_configparser):
        credentials = Credentials(dragonchain_id='TestID', auth_key='TestKey', auth_key_id='TestKeyId')
        mock_configparser.return_value.get.side_effect = configparser.NoSectionError('test')
        self.assertRaises(exceptions.AuthorizationNotFound, credentials.get_credentials)

    @patch('dragonchain_sdk.credentials.configparser.ConfigParser')
    def test_gets_credentials_from_config_file_raises_on_no_option(self, mock_configparser):
        credentials = Credentials(dragonchain_id='TestID', auth_key='TestKey', auth_key_id='TestKeyId')
        mock_configparser.return_value.get.side_effect = configparser.NoOptionError('test', 'test')
        self.assertRaises(exceptions.AuthorizationNotFound, credentials.get_credentials)

    @patch('dragonchain_sdk.credentials.configparser.ConfigParser')
    def test_gets_dragonchain_id_from_config_file_raises_on_no_section(self, mock_configparser):
        credentials = Credentials(dragonchain_id='TestID', auth_key='TestKey', auth_key_id='TestKeyId')
        mock_configparser.return_value.get.side_effect = configparser.NoSectionError('test')
        self.assertRaises(exceptions.DragonchainIdentityNotFound, credentials.get_dragonchain_id)

    @patch('dragonchain_sdk.credentials.configparser.ConfigParser')
    def test_gets_dragonchain_id_credentials_from_config_file_raises_on_no_option(self, mock_configparser):
        credentials = Credentials(dragonchain_id='TestID', auth_key='TestKey', auth_key_id='TestKeyId')
        mock_configparser.return_value.get.side_effect = configparser.NoOptionError('test', 'test')
        self.assertRaises(exceptions.DragonchainIdentityNotFound, credentials.get_dragonchain_id)

    @patch.dict(os.environ, {'DRAGONCHAIN_ID': 'TestID', 'AUTH_KEY': 'TestKey', 'AUTH_KEY_ID': 'TestKeyId'})
    def test_gets_credentials_from_environ(self):
        credentials = Credentials()
        self.assertEqual(credentials.dragonchain_id, 'TestID')
        self.assertEqual(credentials.auth_key, 'TestKey')
        self.assertEqual(credentials.auth_key_id, 'TestKeyId')

    def test_get_correct_hash_algorithm_sha256_default(self):
        credentials = Credentials(dragonchain_id='test', auth_key='test', auth_key_id='test')
        self.assertEqual(credentials.algorithm, 'SHA256')
        self.assertEqual(credentials.hash_method, hashlib.sha256)

    def test_get_correct_hash_algorithm_blake2b(self):
        credentials = Credentials(dragonchain_id='test', auth_key='test', auth_key_id='test', algorithm='BLAKE2b512')
        self.assertEqual(credentials.algorithm, 'BLAKE2b512')
        self.assertEqual(credentials.hash_method, hashlib.blake2b)

    def test_get_correct_hash_algorithm_sha3_256(self):
        credentials = Credentials(dragonchain_id='test', auth_key='test', auth_key_id='test', algorithm='SHA3-256')
        self.assertEqual(credentials.algorithm, 'SHA3-256')
        self.assertEqual(credentials.hash_method, hashlib.sha3_256)


class TestCredentialsMethods(TestCase):
    def setUp(self):
        self.credentials = Credentials(dragonchain_id='TestID', auth_key='TestKey', auth_key_id='TestKeyId')

    def test_update_algorithm_raises_type_error(self):
        self.assertRaises(TypeError, self.credentials.update_algorithm, [])

    def test_update_algorithm_raises_not_implemented(self):
        self.assertRaises(NotImplementedError, self.credentials.update_algorithm, 'SHA1')

    @patch('os.path.join', return_value='full path')
    @patch('os.path.expandvars', return_value='expanded')
    @patch('pathlib.Path.home', return_value='home')
    def test_get_credential_file_path_windows(self, mock_home, mock_expand, mock_join):
        os.name = 'nt'
        self.assertEqual(self.credentials.get_credential_file_path(), 'full path')
        mock_expand.assert_called_once_with('%LOCALAPPDATA%')
        mock_join.assert_called_once_with('expanded', 'dragonchain', 'credentials')
        mock_home.assert_not_called()

    @patch('os.path.join', return_value='full path')
    @patch('os.path.expandvars', return_value='expanded')
    @patch('pathlib.Path.home', return_value='home')
    def test_get_credential_file_path_posix(self, mock_home, mock_expand, mock_join):
        os.name = 'posix'
        self.assertEqual(self.credentials.get_credential_file_path(), 'full path')
        mock_home.assert_called_once()
        mock_expand.assert_not_called()
        mock_join.assert_called_once_with('home', '.dragonchain', 'credentials')

    def test_get_hash_method_raises_not_implemented_error(self):
        self.assertRaises(NotImplementedError, self.credentials.get_hash_method, 'not_implemented')

    def test_bytes_to_b64_string_raises_type_error(self):
        self.assertRaises(TypeError, self.credentials.bytes_to_b64_str, 'not bytes')

    def test_bytes_to_b64_string(self):
        self.assertEqual(self.credentials.bytes_to_b64_str(b'stuff'), 'c3R1ZmY=')

    def test_bytes_from_input_str(self):
        self.assertEqual(self.credentials.bytes_from_input('test'), b'test')

    def test_bytes_from_input_bytes(self):
        self.assertEqual(self.credentials.bytes_from_input(b'test'), b'test')

    def test_bytes_from_input_raises_value_error(self):
        self.assertRaises(ValueError, self.credentials.bytes_from_input, '\ud83d')

    def test_bytes_from_input_raises_type_error_on_non_string_or_bytes(self):
        self.assertRaises(TypeError, self.credentials.bytes_from_input, 123)

    def test_base64_encode_input(self):
        self.assertEqual(self.credentials.base64_encode_input('stuff'), 'c3R1ZmY=')

    def test_hash_input_sha256(self):
        self.assertEqual(self.credentials.hash_input('some input'), b'+\xe3[\xc6q\xdc\x91.\x7fT\x0f\x0eZ.\x91^\xf6\xa4\xa4\xdb\xd2\xad\xa5\xba\x9c\x1d+\x11{\xfc\x90|')

    def test_hash_input_blake2b(self):
        self.credentials.update_algorithm('BLAKE2b512')
        self.assertEqual(self.credentials.hash_input('some input'), b'k\xd3_\x97J/\x0e\x93_\xa1\x15(\xbf"\xab\xb5\xb6\x9f\x9d\xee8\xed\xf6\xc2RX\xea<\xb4\xee\x03:|a@\xd8\x9f\xab\xa6\x06\x89r\x8fa-]\xf7\xda\xb9=\xa7\xd0z\xe6XB\xae$\xd0\x1fP\xa2+\xa9')

    def test_hash_input_sha3_256(self):
        self.credentials.update_algorithm('SHA3-256')
        self.assertEqual(self.credentials.hash_input('some input'), b'\x18\xd6@c\x0b\xbe\xc8`\xdb@t\x1e\xf2\xd65g\xe2Z\x04\x90\xac\xc3\x9f\xf1\xceC\xee\xde\xf4\xb1\xe7x')

    def test_create_hmac_sha256(self):
        encoded_hmac = self.credentials.bytes_to_b64_str(self.credentials.create_hmac('12345', 'message'))
        self.assertEqual(encoded_hmac, 'aaIguQeFQUkVBw64VUJQWmzzIweD5zf+NVpuwfwexBA=')

    def test_create_hmac_blake2b(self):
        self.credentials.update_algorithm('BLAKE2b512')
        encoded_hmac = self.credentials.bytes_to_b64_str(self.credentials.create_hmac('12345', 'message'))
        self.assertEqual(encoded_hmac, 'jMErAWFbeKCDRPGFhxCL+xYsjYP4SDIUXlDpXhmQ9VZ4jCIMFzQ1ksnR7hf+pkcr56QY8Hm16sTTv+g29jRXew==')

    def test_create_hmac_sha3_256(self):
        self.credentials.update_algorithm('SHA3-256')
        encoded_hmac = self.credentials.bytes_to_b64_str(self.credentials.create_hmac('12345', 'message'))
        self.assertEqual(encoded_hmac, 'EhPxZsdSWbv6ekuJvXv+nPIPdaZVdOIxXXLfvOvJlSw=')

    def test_compare_hmac_sha256(self):
        encoded_hmac = 'aaIguQeFQUkVBw64VUJQWmzzIweD5zf+NVpuwfwexBA='
        self.assertTrue(self.credentials.compare_hmac(encoded_hmac, '12345', 'message'))

    def test_compare_hmac_blake2b(self):
        self.credentials.update_algorithm('BLAKE2b512')
        encoded_hmac = 'jMErAWFbeKCDRPGFhxCL+xYsjYP4SDIUXlDpXhmQ9VZ4jCIMFzQ1ksnR7hf+pkcr56QY8Hm16sTTv+g29jRXew=='
        self.assertTrue(self.credentials.compare_hmac(encoded_hmac, '12345', 'message'))

    def test_compare_hmac_sha3_256(self):
        self.credentials.update_algorithm('SHA3-256')
        encoded_hmac = 'EhPxZsdSWbv6ekuJvXv+nPIPdaZVdOIxXXLfvOvJlSw='
        self.assertTrue(self.credentials.compare_hmac(encoded_hmac, '12345', 'message'))

    def test_get_authorization_sha256(self):
        kwargs = {
            'http_verb': 'get',
            'path': '/chain/transaction',
            'timestamp': '2017-06-10T20:40:05.191023Z',
            'content_type': '',
            'content': ''
        }
        self.assertEqual(self.credentials.get_authorization(**kwargs), 'DC1-HMAC-SHA256 TestKeyId:4RDAxss7zb3p0nZKzpCM3dNNb3UhdeIU6Aen1Jp84Eo=')

    def test_get_authorization_blake2b(self):
        kwargs = {
            'http_verb': 'get',
            'path': '/chain/transaction',
            'timestamp': '2017-06-10T20:40:05.191023Z',
            'content_type': '',
            'content': ''
        }
        self.credentials.update_algorithm('BLAKE2b512')
        self.assertEqual(self.credentials.get_authorization(**kwargs), 'DC1-HMAC-BLAKE2b512 TestKeyId:iRH9Z2/rMpqEiAHFKuRcfUnwlng3PBTCqUylUAJYNMkux0FUNnq37JemDnYlAA9lIYVI9JIVIvckTSVH3odnOg==')

    def test_get_authorization_sha3_256(self):
        kwargs = {
            'http_verb': 'get',
            'path': '/chain/transaction',
            'timestamp': '2017-06-10T20:40:05.191023Z',
            'content_type': '',
            'content': ''
        }
        self.credentials.update_algorithm('SHA3-256')
        self.assertEqual(self.credentials.get_authorization(**kwargs), 'DC1-HMAC-SHA3-256 TestKeyId:SNZShngIKiYqyDriAUoqwaxAj4JtQ7kxZDc/V8Um4Z4=')
