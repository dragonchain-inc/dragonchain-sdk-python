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
import requests_mock
import os
import configparser
import requests
import dragonchain_sdk.configuration as config
from dragonchain_sdk import exceptions

config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_config')


class TestPublicConfigMethods(TestCase):
    @patch('dragonchain_sdk.configuration._get_credentials_as_smart_contract', return_value=('', ''))
    @patch('dragonchain_sdk.configuration._get_credentials_from_file', return_value=('', ''))
    @patch('dragonchain_sdk.configuration._get_credentials_from_environment', return_value=('', ''))
    def test_raises_on_credentials_non_existent(self, mock_get_env, mock_get_file, mock_get_sc):
        self.assertRaises(exceptions.DragonchainIdentityNotFound, config.get_credentials, 'test')

    @patch('dragonchain_sdk.configuration._get_credentials_as_smart_contract', return_value=('', ''))
    @patch('dragonchain_sdk.configuration._get_credentials_from_file', return_value=('', ''))
    @patch('dragonchain_sdk.configuration._get_credentials_from_environment', return_value=('a', 'b'))
    def test_get_credentials_returns_from_env(self, mock_get_env, mock_get_file, mock_get_sc):
        self.assertEqual(('a', 'b'), config.get_credentials('test'))
        mock_get_env.assert_called_once()
        mock_get_file.assert_not_called()
        mock_get_sc.assert_not_called()

    @patch('dragonchain_sdk.configuration._get_credentials_as_smart_contract', return_value=('', ''))
    @patch('dragonchain_sdk.configuration._get_credentials_from_file', return_value=('a', 'b'))
    @patch('dragonchain_sdk.configuration._get_credentials_from_environment', return_value=('', ''))
    def test_get_credentials_returns_from_file(self, mock_get_env, mock_get_file, mock_get_sc):
        self.assertEqual(('a', 'b'), config.get_credentials('test'))
        mock_get_env.assert_called_once()
        mock_get_file.assert_called_once_with('test')
        mock_get_sc.assert_not_called()

    @patch('dragonchain_sdk.configuration._get_credentials_as_smart_contract', return_value=('a', 'b'))
    @patch('dragonchain_sdk.configuration._get_credentials_from_file', return_value=('', ''))
    @patch('dragonchain_sdk.configuration._get_credentials_from_environment', return_value=('', ''))
    def test_get_credentials_returns_from_sc(self, mock_get_env, mock_get_file, mock_get_sc):
        self.assertEqual(('a', 'b'), config.get_credentials('test'))
        mock_get_env.assert_called_once()
        mock_get_file.assert_called_once_with('test')
        mock_get_sc.assert_called_once()

    @patch('dragonchain_sdk.configuration._get_config_file_path', return_value='does_not_exist.ini')
    def test_raises_on_dragonchain_id_non_existent(self, mock_path):
        self.assertRaises(exceptions.DragonchainIdentityNotFound, config.get_dragonchain_id)

    @patch.dict(os.environ, {'DRAGONCHAIN_ID': 'TestID'})
    @patch('dragonchain_sdk.configuration._get_config_file_path')
    def test_get_dragonchain_id_from_env(self, mock_path):
        self.assertEqual('TestID', config.get_dragonchain_id())
        mock_path.assert_not_called()

    @patch('dragonchain_sdk.configuration.configparser.ConfigParser')
    def test_get_dragonchain_id_from_file(self, mock_configparser):
        mock_configparser.return_value.get.return_value = 'test'
        self.assertEqual('test', config.get_dragonchain_id())

    @patch('dragonchain_sdk.configuration._get_endpoint_from_environment', return_value='')
    @patch('dragonchain_sdk.configuration._get_endpoint_from_file', return_value='')
    @patch('dragonchain_sdk.configuration._get_endpoint_from_remote', side_effect=exceptions.MatchmakingException)
    def test_raises_on_endpoint_non_existent(self, mock_get_remote, mock_get_file, mock_get_env):
        self.assertRaises(exceptions.DragonchainIdentityNotFound, config.get_endpoint, 'test')

    @patch('dragonchain_sdk.configuration._get_endpoint_from_environment', return_value='thing')
    @patch('dragonchain_sdk.configuration._get_endpoint_from_file', return_value='')
    @patch('dragonchain_sdk.configuration._get_endpoint_from_remote', side_effect=exceptions.MatchmakingException)
    def test_get_endpoint_from_env(self, mock_get_remote, mock_get_file, mock_get_env):
        self.assertEqual('thing', config.get_endpoint('test'))
        mock_get_env.assert_called_once()
        mock_get_file.assert_not_called()
        mock_get_remote.assert_not_called()

    @patch('dragonchain_sdk.configuration._get_endpoint_from_environment', return_value='')
    @patch('dragonchain_sdk.configuration._get_endpoint_from_file', return_value='thing')
    @patch('dragonchain_sdk.configuration._get_endpoint_from_remote', side_effect=exceptions.MatchmakingException)
    def test_get_endpoint_from_file(self, mock_get_remote, mock_get_file, mock_get_env):
        self.assertEqual('thing', config.get_endpoint('test'))
        mock_get_env.assert_called_once()
        mock_get_file.assert_called_once_with('test')
        mock_get_remote.assert_not_called()

    @patch('dragonchain_sdk.configuration._get_endpoint_from_environment', return_value='')
    @patch('dragonchain_sdk.configuration._get_endpoint_from_file', return_value='')
    @patch('dragonchain_sdk.configuration._get_endpoint_from_remote', return_value='thing')
    def test_get_endpoint_from_remote(self, mock_get_remote, mock_get_file, mock_get_env):
        self.assertEqual('thing', config.get_endpoint('test'))
        mock_get_env.assert_called_once()
        mock_get_file.assert_called_once_with('test')
        mock_get_remote.assert_called_once_with('test')


class TestPrivateConfigMethods(TestCase):
    @patch('dragonchain_sdk.configuration._get_config_file_path', return_value=config_file)
    def test_gets_endpoint_from_config_file(self, mock_path):
        self.assertEqual('https://an.end.point', config._get_endpoint_from_file('TestID'))

    @patch('dragonchain_sdk.configuration.configparser.ConfigParser')
    def test_gets_endpoint_from_file_returns_empty_on_no_section(self, mock_configparser):
        mock_configparser.return_value.get.side_effect = configparser.NoSectionError('test')
        self.assertEqual('', config._get_endpoint_from_file('test'))

    @patch('dragonchain_sdk.configuration.configparser.ConfigParser')
    def test_gets_endpoint_from_file_returns_empty_on_no_option(self, mock_configparser):
        mock_configparser.return_value.get.side_effect = configparser.NoOptionError('test', 'test')
        self.assertEqual('', config._get_endpoint_from_file('test'))

    @patch('dragonchain_sdk.configuration._get_config_file_path', return_value=config_file)
    def test_gets_credentials_from_config_file(self, mock_path):
        self.assertEqual(('TestKeyId', 'TestKey'), config._get_credentials_from_file('TestID'))

    @patch('dragonchain_sdk.configuration.configparser.ConfigParser')
    def test_gets_credentials_from_file_returns_empty_on_no_section(self, mock_configparser):
        mock_configparser.return_value.get.side_effect = configparser.NoSectionError('test')
        self.assertEqual(('', ''), config._get_credentials_from_file('test'))

    @patch('dragonchain_sdk.configuration.configparser.ConfigParser')
    def test_gets_credentials_from_file_returns_empty_on_no_option(self, mock_configparser):
        mock_configparser.return_value.get.side_effect = configparser.NoOptionError('test', 'test')
        self.assertEqual(('', ''), config._get_credentials_from_file('test'))

    @patch.dict(os.environ, {'AUTH_KEY': 'TestKey', 'AUTH_KEY_ID': 'TestKeyId'})
    def test_gets_credentials_from_environ(self):
        self.assertEqual(('TestKeyId', 'TestKey'), config._get_credentials_from_environment())

    @patch.dict(os.environ, {'DRAGONCHAIN_ENDPOINT': 'dummy'})
    def test_gets_endpoint_from_environ(self):
        self.assertEqual('dummy', config._get_endpoint_from_environment())

    @patch('dragonchain_sdk.configuration.open')
    def test_gets_credentials_from_smart_contract(self, mock_open):
        mock_open.return_value.read.return_value = 'bogusAuth'
        self.assertEqual(config._get_credentials_as_smart_contract(), ('bogusAuth', 'bogusAuth'))

    @patch('dragonchain_sdk.configuration.open')
    def test_gets_credentials_from_smart_contract_catches_filenotfound(self, mock_open):
        mock_open.side_effect = FileNotFoundError()
        self.assertEqual(('', ''), config._get_credentials_as_smart_contract())

    @patch('dragonchain_sdk.configuration.requests.get', side_effect=requests.ConnectionError)
    def test_gets_credentials_from_remote_raises_with_communication_error(self, mock_request):
        self.assertRaises(exceptions.MatchmakingException, config._get_endpoint_from_remote, 'test')

    @patch('dragonchain_sdk.configuration.requests.get', side_effect=Exception)
    def test_gets_credentials_from_remote_raises_with_unknown_requests_error(self, mock_request):
        self.assertRaises(exceptions.MatchmakingException, config._get_endpoint_from_remote, 'test')

    def test_gets_credentials_from_remote_raises_with_404(self):
        with requests_mock.mock() as m:
            m.get('https://matchmaking.api.dragonchain.com/registration/test', status_code=404, text='{"error": "some error"}')
            self.assertRaises(exceptions.MatchmakingException, config._get_endpoint_from_remote, 'test')

    def test_gets_credentials_from_remote_raises_with_bad_response_data_from_matchmaking(self):
        with requests_mock.mock() as m:
            m.get('https://matchmaking.api.dragonchain.com/registration/test', status_code=200, text='{"error": "some error"}')
            self.assertRaises(exceptions.MatchmakingException, config._get_endpoint_from_remote, 'test')

    def test_gets_credentials_from_remote_returns_url_from_matchmaking(self):
        with requests_mock.mock() as m:
            m.get('https://matchmaking.api.dragonchain.com/registration/test', status_code=200, text='{"url": "dummy"}')
            self.assertEqual('dummy', config._get_endpoint_from_remote('test'))

    @patch('os.path.join', return_value='full path')
    @patch('os.path.expandvars', return_value='expanded')
    def test_get_config_file_path_windows(self, mock_expand, mock_join):
        os.name = 'nt'
        self.assertEqual(config._get_config_file_path(), 'full path')
        mock_expand.assert_called_once_with('%LOCALAPPDATA%')
        mock_join.assert_called_once_with('expanded', 'dragonchain', 'credentials')

    @patch('os.path.join', return_value='full path')
    @patch('os.path.expandvars', return_value='expanded')
    @patch('os.path.expanduser', return_value='home')
    def test_get_config_file_path_posix(self, mock_home, mock_expand, mock_join):
        os.name = 'posix'
        self.assertEqual(config._get_config_file_path(), 'full path')
        mock_home.assert_called_once()
        mock_expand.assert_not_called()
        mock_join.assert_called_once_with('home', '.dragonchain', 'credentials')
