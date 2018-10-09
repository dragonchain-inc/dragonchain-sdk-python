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

curr_dir = os.path.dirname(os.path.abspath(__file__))
config_dir = curr_dir + '/.dragonchain/'


def init_client():
    return dc_sdk.client(dragonchain_id='test', auth_key_id='id', auth_key='key',
                         endpoint='endpoint', verify=True)


class TestClient(TestCase):
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

    @patch('pathlib.Path.home', return_value=curr_dir)
    def test_get_auth_key(self, mock_home):
        # Test getting from env
        os.environ['DRAGONCHAIN_AUTH_KEY'] = 'env_key'
        os.environ['DRAGONCHAIN_AUTH_KEY_ID'] = 'env_id'
        self.assertEqual(dc_sdk.lib.client.get_auth_key(), ('env_id', 'env_key'))
        os.environ.pop('DRAGONCHAIN_AUTH_KEY', 0)
        os.environ.pop('DRAGONCHAIN_AUTH_KEY_ID', 0)
        self.assertRaises(RuntimeError, dc_sdk.lib.client.get_auth_key)
        # Create config file for method to find
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        config = ConfigParser()
        config.add_section('dcid')
        config.set('dcid', 'auth_key', 'config_key')
        config.set('dcid', 'auth_key_id', 'config_id')
        with open(config_dir + 'credentials', 'w') as configfile:
            config.write(configfile)
        # Test getting from credentials ini file
        self.assertEqual(dc_sdk.lib.client.get_auth_key('dcid'), ('config_id', 'config_key'))
        self.assertRaises(RuntimeError, dc_sdk.lib.client.get_auth_key, 'nonexistant-id')
        # Cleanup
        shutil.rmtree(config_dir, ignore_errors=True)

    @patch('dc_sdk.lib.client.get_auth_key', return_value=('id', 'key'))
    @patch('dc_sdk.lib.client.generate_dragonchain_endpoint', return_value='stuff')
    def test_client_init(self, mock_get_auth, mock_dc_endpoint):
        # Test happy path
        dcid = 'dcid'
        key_id = 'id'
        key = 'key'
        endpoint = 'endpoint'
        client = dc_sdk.lib.client.Client(dcid, key_id, key, endpoint)
        self.assertEqual(client.dcid, dcid)
        self.assertEqual(client.auth_key, key)
        self.assertEqual(client.auth_key_id, key_id)
        self.assertEqual(client.endpoint, endpoint)
        # Invoke client through main __init__
        dc_sdk.client(dcid)
        mock_get_auth.assert_called_once()
        mock_dc_endpoint.assert_called_once()
        # Test bad values
        self.assertRaises(ValueError, dc_sdk.lib.client.Client, 12345)
        self.assertRaises(ValueError, dc_sdk.lib.client.Client, 'dcid', 12345, 'key')
        self.assertRaises(ValueError, dc_sdk.lib.client.Client, 'dcid', 'id', 'key', 12345)
        self.assertRaises(ValueError, dc_sdk.lib.client.Client, 'dcid', 'id', 'key', 'endpoint', 12345)

    @patch('dc_sdk.lib.client.make_request')
    def test_status(self, mock_request):
        client = init_client()
        client.get_status()
        mock_request.assert_called_with(endpoint=client.endpoint, auth_key_id=client.auth_key_id, verify=client.verify,
                                        auth_key=client.auth_key, dcid=client.dcid, http_verb='GET',
                                        path='/chain/status')

    @patch('dc_sdk.lib.client.make_request')
    def test_get_transaction(self, mock_request):
        client = init_client()
        txn_id = 'an_id'
        client.get_transaction(txn_id)
        mock_request.assert_called_with(endpoint=client.endpoint, auth_key_id=client.auth_key_id, verify=client.verify,
                                        auth_key=client.auth_key, dcid=client.dcid, http_verb='GET',
                                        path='/chain/transaction/{}'.format(txn_id))
        self.assertRaises(ValueError, client.get_transaction, 123)

    @patch('dc_sdk.lib.client.make_request')
    def test_get_block(self, mock_request):
        client = init_client()
        block_id = 'an_id'
        client.get_block(block_id)
        mock_request.assert_called_with(endpoint=client.endpoint, auth_key_id=client.auth_key_id, verify=client.verify,
                                        auth_key=client.auth_key, dcid=client.dcid, http_verb='GET',
                                        path='/chain/block/{}'.format(block_id))
        self.assertRaises(ValueError, client.get_block, 123)

    @patch('dc_sdk.lib.client.make_request')
    def test_get_contract(self, mock_request):
        client = init_client()
        contract_id = 'an_id'
        client.get_contract(contract_id)
        mock_request.assert_called_with(endpoint=client.endpoint, auth_key_id=client.auth_key_id, verify=client.verify,
                                        auth_key=client.auth_key, dcid=client.dcid, http_verb='GET',
                                        path='/chain/contract/{}'.format(contract_id))
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
        mock_request.assert_called_with(endpoint=client.endpoint, auth_key_id=client.auth_key_id, verify=client.verify,
                                        auth_key=client.auth_key, dcid=client.dcid, http_verb='GET',
                                        path='/chain/transaction{}'.format(query_string))

    @patch('dc_sdk.lib.client.make_request')
    def test_query_block(self, mock_request):
        client = init_client()
        query = 'q'
        sort = 's'
        offset = 1
        limit = 2
        query_string = dc_sdk.lib.request.get_lucene_query_params(query, sort, offset, limit)
        client.query_blocks(query, sort, offset, limit)
        mock_request.assert_called_with(endpoint=client.endpoint, auth_key_id=client.auth_key_id, verify=client.verify,
                                        auth_key=client.auth_key, dcid=client.dcid, http_verb='GET',
                                        path='/chain/block{}'.format(query_string))

    @patch('dc_sdk.lib.client.make_request')
    def test_query_contract(self, mock_request):
        client = init_client()
        query = 'q'
        sort = 's'
        offset = 1
        limit = 2
        query_string = dc_sdk.lib.request.get_lucene_query_params(query, sort, offset, limit)
        client.query_contracts(query, sort, offset, limit)
        mock_request.assert_called_with(endpoint=client.endpoint, auth_key_id=client.auth_key_id, verify=client.verify,
                                        auth_key=client.auth_key, dcid=client.dcid, http_verb='GET',
                                        path='/chain/contract{}'.format(query_string))

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
        mock_request.assert_called_with(endpoint=client.endpoint, auth_key_id=client.auth_key_id, verify=client.verify,
                                        auth_key=client.auth_key, dcid=client.dcid, http_verb='POST',
                                        path='/chain/transaction', json=expected_body)
        client.post_transaction(txn_type, payload, tag)
        expected_body['tag'] = tag
        mock_request.assert_called_with(endpoint=client.endpoint, auth_key_id=client.auth_key_id, verify=client.verify,
                                        auth_key=client.auth_key, dcid=client.dcid, http_verb='POST',
                                        path='/chain/transaction', json=expected_body)
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
        mock_request.assert_called_with(endpoint=client.endpoint, auth_key_id=client.auth_key_id, verify=client.verify,
                                        auth_key=client.auth_key, dcid=client.dcid, http_verb='POST',
                                        path='/chain/contract', json=expected_body)
        client.post_custom_contract(name, code, runtime, sc_type, serial, env_vars)
        expected_body['custom_environment_variables'] = env_vars
        mock_request.assert_called_with(endpoint=client.endpoint, auth_key_id=client.auth_key_id, verify=client.verify,
                                        auth_key=client.auth_key, dcid=client.dcid, http_verb='POST',
                                        path='/chain/contract', json=expected_body)
        self.assertRaises(ValueError, client.post_custom_contract, 1234, code, runtime, sc_type, serial)
        self.assertRaises(ValueError, client.post_custom_contract, name, 1234, runtime, sc_type, serial)
        self.assertRaises(ValueError, client.post_custom_contract, name, code, 1234567, sc_type, serial)
        self.assertRaises(ValueError, client.post_custom_contract, name, code, runtime, 1234567, serial)
        self.assertRaises(ValueError, client.post_custom_contract, name, code, runtime, sc_type, 123456)
        self.assertRaises(ValueError, client.post_custom_contract, name, code, runtime, sc_type, serial, 123)
