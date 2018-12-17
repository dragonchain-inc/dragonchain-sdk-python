"""
Copyright 2018 Dragonchain, Inc. or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from unittest import TestCase
from mock import patch
import os
import shutil
from configparser import ConfigParser
import dc_sdk

config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dragonchain')
config_file = os.path.join(config_dir, 'credentials')


def init_client():
    return dc_sdk.client(dragonchain_id='c456befa-9f73-4b7c-82be-3395de81ba13', auth_key_id='id',
                         auth_key='key', endpoint='endpoint', verify=True)


class TestClient(TestCase):
    def test_check_print_curl(self):
        self.assertRaises(ValueError, dc_sdk.lib.client.check_print_curl, 'banana')

    def test_generate_endpoint(self):
        self.assertEqual(dc_sdk.lib.client.generate_dragonchain_endpoint('an_id'), 'https://an_id.api.dragonchain.com')

    def test_valid_runtime(self):
        self.assertTrue(dc_sdk.lib.client.is_valid_runtime('nodejs6.10'))
        self.assertTrue(dc_sdk.lib.client.is_valid_runtime('nodejs8.10'))
        self.assertTrue(dc_sdk.lib.client.is_valid_runtime('java8'))
        self.assertTrue(dc_sdk.lib.client.is_valid_runtime('python2.7'))
        self.assertTrue(dc_sdk.lib.client.is_valid_runtime('python3.6'))
        self.assertTrue(dc_sdk.lib.client.is_valid_runtime('dotnetcore1.0'))
        self.assertTrue(dc_sdk.lib.client.is_valid_runtime('dotnetcore2.0'))
        self.assertTrue(dc_sdk.lib.client.is_valid_runtime('dotnetcore2.1'))
        self.assertTrue(dc_sdk.lib.client.is_valid_runtime('go1.x'))
        self.assertFalse(dc_sdk.lib.client.is_valid_runtime('fake_language'))

    def test_valid_sc_type(self):
        self.assertTrue(dc_sdk.lib.client.is_valid_sc_type('transaction'))
        self.assertTrue(dc_sdk.lib.client.is_valid_sc_type('cron'))
        self.assertFalse(dc_sdk.lib.client.is_valid_sc_type('not a type'))

    @patch('os.path.expandvars', return_value='thing')
    @patch('pathlib.Path.home', return_value='thing')
    def test_get_cred_path(self, mock_path, mock_expandvars):
        # Spoof os name by setting the os module name string in the dc_sdk.lib.client imported os module
        dc_sdk.lib.client.os.name = 'posix'
        dc_sdk.lib.client.get_credential_file_path()
        mock_path.assert_called_once()
        dc_sdk.lib.client.os.name = 'nt'
        dc_sdk.lib.client.get_credential_file_path()
        mock_expandvars.assert_called_with('%LOCALAPPDATA%')
        # Revert spoofed os name to correct value
        dc_sdk.lib.client.os.name = os.name

    # Need write permissions in the tests/unit directory for this to pass as it creates a mock credentials file
    @patch('dc_sdk.lib.client.get_credential_file_path', return_value=config_file)
    def test_get_auth_key(self, mock_cred_path):
        # Test getting from env
        os.environ['DRAGONCHAIN_AUTH_KEY'] = 'env_key'
        os.environ['DRAGONCHAIN_AUTH_KEY_ID'] = 'env_id'
        self.assertEqual(dc_sdk.lib.client.get_auth_key(), ('env_id', 'env_key'))
        os.environ.pop('DRAGONCHAIN_AUTH_KEY', 0)
        os.environ.pop('DRAGONCHAIN_AUTH_KEY_ID', 0)
        self.assertRaises(RuntimeError, dc_sdk.lib.client.get_auth_key)
        # Create config file for method to find
        os.makedirs(config_dir, exist_ok=True)
        config = ConfigParser()
        config.add_section('dcid')
        config.set('dcid', 'auth_key', 'config_key')
        config.set('dcid', 'auth_key_id', 'config_id')
        with open(config_file, 'w') as configfile:
            config.write(configfile)
        # Test getting from credentials ini file
        self.assertEqual(dc_sdk.lib.client.get_auth_key('dcid'), ('config_id', 'config_key'))
        self.assertRaises(RuntimeError, dc_sdk.lib.client.get_auth_key, 'nonexistant-id')
        # Cleanup temp ini config dir/files
        shutil.rmtree(config_dir, ignore_errors=True)
        # Test credentials from being passed in
        key = 'key'
        key_id = 'key_id'
        self.assertEqual(dc_sdk.lib.client.get_auth_key(None, key, key_id), (key_id, key))
        self.assertRaises(ValueError, dc_sdk.lib.client.get_auth_key, None, 123, 123)

    # Need write permissions in the tests/unit directory for this to pass as it creates a mock credentials file
    @patch('dc_sdk.lib.client.get_credential_file_path', return_value=config_file)
    def test_get_dragonchain_id(self, mock_cred_path):
        # Test getting from env
        dc_id = 'c456befa-9f73-4b7c-82be-3395de81ba13'
        os.environ['DRAGONCHAIN_ID'] = dc_id
        self.assertEqual(dc_sdk.lib.client.get_dragonchain_id(), dc_id)
        os.environ.pop('DRAGONCHAIN_ID', 0)
        self.assertRaises(RuntimeError, dc_sdk.lib.client.get_dragonchain_id)
        # Create config file for method to find
        os.makedirs(config_dir, exist_ok=True)
        config = ConfigParser()
        config.add_section('default')
        config.set('default', 'dragonchain_id', dc_id)
        with open(config_file, 'w') as configfile:
            config.write(configfile)
        # Test getting from credentials ini file
        self.assertEqual(dc_sdk.lib.client.get_dragonchain_id(), dc_id)
        # Cleanup temp ini config dir/files
        shutil.rmtree(config_dir, ignore_errors=True)
        # Test passing in id directly
        self.assertEqual(dc_sdk.lib.client.get_dragonchain_id(dc_id), dc_id)
        # Test bad input
        self.assertRaises(ValueError, dc_sdk.lib.client.get_dragonchain_id, 123)
        self.assertRaises(ValueError, dc_sdk.lib.client.get_dragonchain_id, 'not_a_valid_uuidv4')

    @patch('dc_sdk.lib.client.get_auth_key', return_value=('id', 'key'))
    @patch('dc_sdk.lib.client.generate_dragonchain_endpoint', return_value='stuff')
    def test_client_init(self, mock_get_auth, mock_dc_endpoint):
        dcid = 'c456befa-9f73-4b7c-82be-3395de81ba13'
        key_id = 'id'
        key = 'key'
        endpoint = 'endpoint'
        # Invoke client through main __init__
        dc_sdk.client(dcid)
        mock_dc_endpoint.assert_called_once()
        mock_get_auth.assert_called_once()
        # Test happy path
        client = dc_sdk.lib.client.Client(dcid, key_id, key, endpoint)
        self.assertEqual(client.dcid, dcid)
        self.assertEqual(client.auth_key, key)
        self.assertEqual(client.auth_key_id, key_id)
        self.assertEqual(client.endpoint, endpoint)
        # Test bad values
        self.assertRaises(ValueError, dc_sdk.lib.client.Client, 12345)
        self.assertRaises(ValueError, dc_sdk.lib.client.Client, dcid, 'id', 'key', 12345)
        self.assertRaises(ValueError, dc_sdk.lib.client.Client, dcid, 'id', 'key', 'endpoint', 12345)
        self.assertRaises(ValueError, dc_sdk.lib.client.Client, dcid, 'id', 'key', 'endpoint', True, 12345)

    @patch('dc_sdk.lib.client.make_request')
    def test_status(self, mock_request):
        client = init_client()
        client.get_status()
        mock_request.assert_called_with(endpoint=client.endpoint, auth_key_id=client.auth_key_id,
                                        verify=client.verify, auth_key=client.auth_key, dcid=client.dcid,
                                        http_verb='GET', path='/status',
                                        parse_json=True, algorithm=client.algorithm, print_curl=False)

    @patch('dc_sdk.lib.client.make_request')
    def test_get_transaction(self, mock_request):
        client = init_client()
        txn_id = 'an_id'
        client.get_transaction(txn_id)
        mock_request.assert_called_with(endpoint=client.endpoint, auth_key_id=client.auth_key_id,
                                        verify=client.verify, auth_key=client.auth_key, dcid=client.dcid,
                                        http_verb='GET', path='/transaction/{}'.format(txn_id),
                                        parse_json=True, algorithm=client.algorithm, print_curl=False)
        self.assertRaises(ValueError, client.get_transaction, 123)

    @patch('dc_sdk.lib.client.make_request')
    def test_get_block(self, mock_request):
        client = init_client()
        block_id = 'an_id'
        client.get_block(block_id)
        mock_request.assert_called_with(endpoint=client.endpoint, auth_key_id=client.auth_key_id,
                                        verify=client.verify, auth_key=client.auth_key, dcid=client.dcid,
                                        http_verb='GET', path='/block/{}'.format(block_id),
                                        parse_json=True, algorithm=client.algorithm, print_curl=False)
        self.assertRaises(ValueError, client.get_block, 123)

    @patch('dc_sdk.lib.client.make_request')
    def test_get_contract(self, mock_request):
        client = init_client()
        contract_id = 'an_id'
        client.get_contract(contract_id)
        mock_request.assert_called_with(endpoint=client.endpoint, auth_key_id=client.auth_key_id,
                                        verify=client.verify, auth_key=client.auth_key, dcid=client.dcid,
                                        http_verb='GET', path='/contract/{}'.format(contract_id),
                                        parse_json=True, algorithm=client.algorithm, print_curl=False)
        self.assertRaises(ValueError, client.get_contract, 123)

    @patch('dc_sdk.lib.client.make_request')
    def test_query_transaction(self, mock_request):
        client = init_client()
        query = 'q'
        sort = 's'
        offset = 1
        limit = 2
        query_string = dc_sdk.lib.request.get_lucene_query_params(query, sort, offset, limit)
        client.query_transactions(query, sort, offset, limit)
        mock_request.assert_called_with(endpoint=client.endpoint, auth_key_id=client.auth_key_id,
                                        verify=client.verify, auth_key=client.auth_key, dcid=client.dcid,
                                        http_verb='GET', path='/transaction{}'.format(query_string),
                                        parse_json=True, algorithm=client.algorithm, print_curl=False)

    @patch('dc_sdk.lib.client.make_request')
    def test_query_block(self, mock_request):
        client = init_client()
        query = 'q'
        sort = 's'
        offset = 1
        limit = 2
        query_string = dc_sdk.lib.request.get_lucene_query_params(query, sort, offset, limit)
        client.query_blocks(query, sort, offset, limit)
        mock_request.assert_called_with(endpoint=client.endpoint, auth_key_id=client.auth_key_id,
                                        verify=client.verify, auth_key=client.auth_key, dcid=client.dcid,
                                        http_verb='GET', path='/block{}'.format(query_string),
                                        parse_json=True, algorithm=client.algorithm, print_curl=False)

    @patch('dc_sdk.lib.client.make_request')
    def test_query_contract(self, mock_request):
        client = init_client()
        query = 'q'
        sort = 's'
        offset = 1
        limit = 2
        query_string = dc_sdk.lib.request.get_lucene_query_params(query, sort, offset, limit)
        client.query_contracts(query, sort, offset, limit)
        mock_request.assert_called_with(endpoint=client.endpoint, auth_key_id=client.auth_key_id,
                                        verify=client.verify, auth_key=client.auth_key, dcid=client.dcid,
                                        http_verb='GET', path='/contract{}'.format(query_string),
                                        parse_json=True, algorithm=client.algorithm, print_curl=False)

    @patch('dc_sdk.lib.client.make_request')
    def test_post_transaction(self, mock_request):
        client = init_client()
        txn_type = 'a_type'
        payload = 'a payload'
        tag = 'a tag'
        client.post_transaction(txn_type, payload)
        expected_body = {
            'version': '1',
            'txn_type': txn_type,
            'payload': payload
        }
        mock_request.assert_called_with(endpoint=client.endpoint, auth_key_id=client.auth_key_id,
                                        verify=client.verify, auth_key=client.auth_key, dcid=client.dcid,
                                        http_verb='POST', path='/transaction', json=expected_body,
                                        parse_json=True, algorithm=client.algorithm, print_curl=False)
        client.post_transaction(txn_type, payload, tag)
        expected_body['tag'] = tag
        mock_request.assert_called_with(endpoint=client.endpoint, auth_key_id=client.auth_key_id,
                                        verify=client.verify, auth_key=client.auth_key, dcid=client.dcid,
                                        http_verb='POST', path='/transaction', json=expected_body,
                                        parse_json=True, algorithm=client.algorithm, print_curl=False)
        self.assertRaises(ValueError, client.post_transaction, 123, 'a')
        self.assertRaises(ValueError, client.post_transaction, 'a', 123)
        self.assertRaises(ValueError, client.post_transaction, 'a', 'a', 123)

    @patch('dc_sdk.lib.client.make_request')
    def test_post_custom_contract(self, mock_request):
        client = init_client()
        name = 'name'
        code = 'some base64 code'
        runtime = 'nodejs8.10'
        sc_type = 'transaction'
        serial = True
        env_vars = {'variable': 'value'}
        client.post_custom_contract(name, code, runtime, sc_type, serial)
        expected_body = {
            'version': '2',
            'origin': 'custom',
            'name': name,
            'code': code,
            'runtime': runtime,
            'sc_type': sc_type,
            'is_serial': serial
        }
        mock_request.assert_called_with(endpoint=client.endpoint, auth_key_id=client.auth_key_id,
                                        verify=client.verify, auth_key=client.auth_key, dcid=client.dcid,
                                        http_verb='POST', path='/contract/{}'.format(name), json=expected_body,
                                        parse_json=True, algorithm=client.algorithm, print_curl=False)
        client.post_custom_contract(name, code, runtime, sc_type, serial, env_vars)
        expected_body['custom_environment_variables'] = env_vars
        mock_request.assert_called_with(endpoint=client.endpoint, auth_key_id=client.auth_key_id,
                                        verify=client.verify, auth_key=client.auth_key, dcid=client.dcid,
                                        http_verb='POST', path='/contract/{}'.format(name), json=expected_body,
                                        parse_json=True, algorithm=client.algorithm, print_curl=False)
        self.assertRaises(ValueError, client.post_custom_contract, 1234, code, runtime, sc_type, serial)
        self.assertRaises(ValueError, client.post_custom_contract, name, 1234, runtime, sc_type, serial)
        self.assertRaises(ValueError, client.post_custom_contract, name, code, 1234567, sc_type, serial)
        self.assertRaises(ValueError, client.post_custom_contract, name, code, runtime, 1234567, serial)
        self.assertRaises(ValueError, client.post_custom_contract, name, code, runtime, sc_type, 123456)
        self.assertRaises(ValueError, client.post_custom_contract, name, code, runtime, sc_type, serial, 123)

    @patch('dc_sdk.lib.client.make_request')
    def test_post_library_contract(self, mock_request):
        client = init_client()
        name = 'name'
        library_name = 'currency'
        env_vars = {'variable': 'value'}
        client.post_library_contract(name, library_name)
        expected_body = {
            'version': '2',
            'origin': 'library',
            'name': name,
            'libraryContractName': library_name
        }
        mock_request.assert_called_with(endpoint=client.endpoint, auth_key_id=client.auth_key_id,
                                        verify=client.verify, auth_key=client.auth_key, dcid=client.dcid,
                                        http_verb='POST', path='/contract/{}'.format(name), json=expected_body,
                                        parse_json=True, algorithm=client.algorithm, print_curl=False)
        client.post_library_contract(name, library_name, env_vars)
        expected_body['custom_environment_variables'] = env_vars
        mock_request.assert_called_with(endpoint=client.endpoint, auth_key_id=client.auth_key_id,
                                        verify=client.verify, auth_key=client.auth_key, dcid=client.dcid,
                                        http_verb='POST', path='/contract/{}'.format(name), json=expected_body,
                                        parse_json=True, algorithm=client.algorithm, print_curl=False)
        self.assertRaises(ValueError, client.post_library_contract, 1234, library_name)
        self.assertRaises(ValueError, client.post_library_contract, name, 1234)
        self.assertRaises(ValueError, client.post_library_contract, name, library_name, 12345)

    @patch('dc_sdk.lib.client.make_request')
    def test_update_contract(self, mock_request):
        client = init_client()
        name = 'name'
        status = 'status'
        sc_type = 'transaction'
        code = 'some base64 code'
        runtime = 'nodejs8.10'
        serial = True
        env_vars = {'variable': 'value'}
        client.update_contract(name, status, sc_type, code, runtime, serial)
        expected_body = {
            'version': '1',
            'name': name,
            'status': status,
            'sc_type': sc_type,
            'code': code,
            'runtime': runtime,
            'is_serial': serial
        }
        mock_request.assert_called_with(endpoint=client.endpoint, auth_key_id=client.auth_key_id,
                                        verify=client.verify, auth_key=client.auth_key, dcid=client.dcid,
                                        http_verb='PUT', path='/contract', json=expected_body,
                                        parse_json=True, algorithm=client.algorithm, print_curl=False)
        client.update_contract(name, status, sc_type, code, runtime, serial, env_vars)
        expected_body['custom_environment_variables'] = env_vars
        mock_request.assert_called_with(endpoint=client.endpoint, auth_key_id=client.auth_key_id,
                                        verify=client.verify, auth_key=client.auth_key, dcid=client.dcid,
                                        http_verb='PUT', path='/contract', json=expected_body,
                                        parse_json=True, algorithm=client.algorithm, print_curl=False)
        self.assertRaises(ValueError, client.update_contract, 123, status, sc_type, code, runtime, serial)
        self.assertRaises(ValueError, client.update_contract, name, 1234, sc_type, code, runtime, serial)
        self.assertRaises(ValueError, client.update_contract, name, status, 12345, code, runtime, serial)
        self.assertRaises(ValueError, client.update_contract, name, status, sc_type, 123456, runtime, serial)
        self.assertRaises(ValueError, client.update_contract, name, status, sc_type, code, 1234, serial)
        self.assertRaises(ValueError, client.update_contract, name, status, sc_type, code, runtime, 12345)
        self.assertRaises(ValueError, client.update_contract, name, status, sc_type, code, runtime, serial, 123)

    @patch('dc_sdk.lib.client.make_request')
    def test_get_verification(self, mock_request):
        client = init_client()
        block_id = 'block_id'
        level = 3
        client.get_verification(block_id, level)
        mock_request.assert_called_with(endpoint=client.endpoint, auth_key_id=client.auth_key_id,
                                        verify=client.verify, auth_key=client.auth_key, dcid=client.dcid,
                                        http_verb='GET', path='/verification/{}?level={}'.format(block_id, level),
                                        parse_json=True, algorithm=client.algorithm, print_curl=False)
        client.get_verification(block_id)
        mock_request.assert_called_with(endpoint=client.endpoint, auth_key_id=client.auth_key_id,
                                        verify=client.verify, auth_key=client.auth_key, dcid=client.dcid,
                                        http_verb='GET', path='/verification/{}'.format(block_id),
                                        parse_json=True, algorithm=client.algorithm, print_curl=False)
        self.assertRaises(ValueError, client.get_verification, 'block_id', '123')
        self.assertRaises(ValueError, client.get_verification, 1234)

    @patch('dc_sdk.lib.client.make_request')
    def test_get_sc_heap(self, mock_request):
        client = init_client()
        sc_name = 'sc_name'
        key = 'key'
        client.get_sc_heap(key, sc_name)
        mock_request.assert_called_with(endpoint=client.endpoint, auth_key_id=client.auth_key_id,
                                        verify=client.verify, auth_key=client.auth_key, dcid=client.dcid,
                                        http_verb='GET', path='/get/{}/{}'.format(sc_name, key),
                                        parse_json=False, algorithm=client.algorithm, print_curl=False)
        # Test pulling from env
        os.environ['SMART_CONTRACT_NAME'] = sc_name
        client.get_sc_heap(key)
        mock_request.assert_called_with(endpoint=client.endpoint, auth_key_id=client.auth_key_id,
                                        verify=client.verify, auth_key=client.auth_key, dcid=client.dcid,
                                        http_verb='GET', path='/get/{}/{}'.format(sc_name, key),
                                        parse_json=False, algorithm=client.algorithm, print_curl=False)
        # Test bad input
        self.assertRaises(ValueError, client.get_sc_heap, 123)
        self.assertRaises(ValueError, client.get_sc_heap, 'key', 123)

    @patch('dc_sdk.lib.client.make_request')
    def test_list_sc_heap(self, mock_request):
        client = init_client()
        sc_name = 'sc_name'
        client.list_sc_heap(sc_name)
        mock_request.assert_called_with(endpoint=client.endpoint, auth_key_id=client.auth_key_id,
                                        verify=client.verify, auth_key=client.auth_key, dcid=client.dcid,
                                        http_verb='GET', path='/list/{}/'.format(sc_name),
                                        parse_json=True, algorithm=client.algorithm, print_curl=False)
        # Test pulling from env
        os.environ['SMART_CONTRACT_NAME'] = 'sc_name'
        client.list_sc_heap()
        mock_request.assert_called_with(endpoint=client.endpoint, auth_key_id=client.auth_key_id,
                                        verify=client.verify, auth_key=client.auth_key, dcid=client.dcid,
                                        http_verb='GET', path='/list/{}/'.format(sc_name),
                                        parse_json=True, algorithm=client.algorithm, print_curl=False)
        # Test with folder var
        folder_name = 'test'
        client.list_sc_heap(sc_name, folder_name)
        mock_request.assert_called_with(endpoint=client.endpoint, auth_key_id=client.auth_key_id,
                                        verify=client.verify, auth_key=client.auth_key, dcid=client.dcid,
                                        http_verb='GET', path='/list/{}/{}/'.format(sc_name, folder_name),
                                        parse_json=True, algorithm=client.algorithm, print_curl=False)
        # Test bad input
        self.assertRaises(ValueError, client.list_sc_heap, 123)
        self.assertRaises(ValueError, client.list_sc_heap, 'sc', 123)
        self.assertRaises(ValueError, client.list_sc_heap, 'sc', 'thing/')
