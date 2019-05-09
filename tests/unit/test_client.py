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

import os
import logging
import dragonchain_sdk
from unittest import TestCase
from mock import patch, MagicMock
from dragonchain_sdk.dragonchain_client import Client


@patch('dragonchain_sdk.dragonchain_client.Credentials')
@patch('dragonchain_sdk.dragonchain_client.Request')
class TestClientInitialization(TestCase):
    def test_client_initializes_correctly_from_module(self, mock_request, mock_creds):
        self.client = dragonchain_sdk.client()
        mock_creds.assert_called_once_with(None, None, None, 'SHA256')
        mock_request.assert_called_once_with(mock_creds(), None, True)

    @patch('dragonchain_sdk.logging')
    def test_set_stream_logger(self, mock_logging, mock_request, mock_creds):
        mock_logger, mock_stream_handler, mock_formatter = MagicMock(), MagicMock(), MagicMock()
        mock_logging.getLogger.return_value = mock_logger
        mock_logging.StreamHandler.return_value = mock_stream_handler
        mock_logging.Formatter.return_value = mock_formatter

        dragonchain_sdk.set_stream_logger(name='TestLogger', level=logging.INFO)

        mock_logging.getLogger.assert_called_once_with('TestLogger')
        mock_logger.setLevel.assert_called_once_with(logging.INFO)
        mock_logging.StreamHandler.assert_called_once()
        mock_stream_handler.setLevel.assert_called_once_with(logging.INFO)
        mock_logging.Formatter.assert_called_once_with('%(asctime)s %(name)s [%(levelname)s] %(message)s')
        mock_stream_handler.setFormatter.assert_called_once_with(mock_formatter)
        mock_logger.addHandler.assert_called_once_with(mock_stream_handler)

    @patch('dragonchain_sdk.logging')
    def test_set_stream_logger_with_format(self, mock_logging, mock_request, mock_creds):
        mock_logger, mock_stream_handler, mock_formatter = MagicMock(), MagicMock(), MagicMock()
        mock_logging.getLogger.return_value = mock_logger
        mock_logging.StreamHandler.return_value = mock_stream_handler
        mock_logging.Formatter.return_value = mock_formatter

        dragonchain_sdk.set_stream_logger(name='TestLogger', level=logging.INFO, format_string='%(message)s')

        mock_logging.getLogger.assert_called_once_with('TestLogger')
        mock_logger.setLevel.assert_called_once_with(logging.INFO)
        mock_logging.StreamHandler.assert_called_once()
        mock_stream_handler.setLevel.assert_called_once_with(logging.INFO)
        mock_logging.Formatter.assert_called_once_with('%(message)s')
        mock_stream_handler.setFormatter.assert_called_once_with(mock_formatter)
        mock_logger.addHandler.assert_called_once_with(mock_stream_handler)

    def test_client_initializes_correctly_no_params(self, mock_request, mock_creds):
        self.client = Client()
        mock_creds.assert_called_once_with(None, None, None, 'SHA256')
        mock_request.assert_called_once_with(mock_creds(), None, True)

    def test_client_initializes_correctly_with_params(self, mock_request, mock_creds):
        self.client = Client(dragonchain_id='TestID', auth_key='Auth', auth_key_id='AuthID', verify=False, endpoint='endpoint')
        mock_creds.assert_called_once_with('TestID', 'Auth', 'AuthID', 'SHA256')
        mock_request.assert_called_once_with(mock_creds(), 'endpoint', False)

    def test_override_credentials_raises_type_error(self, mock_request, mock_creds):
        self.client = Client()
        self.assertRaises(TypeError, self.client.override_credentials, auth_key={})
        self.assertRaises(TypeError, self.client.override_credentials, auth_key_id={})
        self.assertRaises(TypeError, self.client.override_credentials, dragonchain_id={})

    def test_override_credentials(self, mock_request, mock_creds):
        self.client = Client(dragonchain_id='TestID', auth_key='Auth', auth_key_id='AuthID', verify=False, endpoint='endpoint')
        self.client.override_credentials(auth_key='NewKey', auth_key_id='NewID', dragonchain_id='NewDCID', update_endpoint=True)
        self.assertEqual(self.client.credentials.auth_key, 'NewKey')
        self.assertEqual(self.client.credentials.auth_key_id, 'NewID')
        self.assertEqual(self.client.credentials.dragonchain_id, 'NewDCID')
        self.client.request.update_endpoint.assert_called_once()

    def test_override_credentials_updates_only_auth(self, mock_request, mock_creds):
        self.client = Client()
        self.client.credentials.dragonchain_id = 'default'
        self.client.override_credentials(auth_key='NewKey', auth_key_id='NewID')
        self.assertEqual(self.client.credentials.auth_key, 'NewKey')
        self.assertEqual(self.client.credentials.auth_key_id, 'NewID')
        self.assertEqual(self.client.credentials.dragonchain_id, 'default')

    def test_override_credentials_updates_only_id(self, mock_request, mock_creds):
        self.client = Client()
        self.client.credentials.auth_key_id = 'defaultID'
        self.client.credentials.auth_key = 'defaultKey'
        self.client.override_credentials(dragonchain_id='NewID')
        self.assertEqual(self.client.credentials.auth_key, 'defaultKey')
        self.assertEqual(self.client.credentials.auth_key_id, 'defaultID')
        self.assertEqual(self.client.credentials.dragonchain_id, 'NewID')

    def test_override_credentials_no_update_endpoint(self, mock_request, mock_creds):
        self.client = Client()
        self.client.credentials.auth_key_id = 'defaultID'
        self.client.credentials.auth_key = 'defaultKey'
        self.client.override_credentials(dragonchain_id='NewID', update_endpoint=False)
        self.assertEqual(self.client.credentials.auth_key, 'defaultKey')
        self.assertEqual(self.client.credentials.auth_key_id, 'defaultID')
        self.assertEqual(self.client.credentials.dragonchain_id, 'NewID')
        self.client.request.update_endpoint.assert_not_called()


@patch('dragonchain_sdk.dragonchain_client.Request')
@patch('dragonchain_sdk.dragonchain_client.Credentials')
class TestClientMehods(TestCase):
    def test_build_transaction_dict_raises_type_error(self, mock_creds, mock_request):
        self.assertRaises(TypeError, Client.build_transaction_dict, {}, {'fake': 'payload'}, 'Tag:"value"')
        self.assertRaises(TypeError, Client.build_transaction_dict, 'FAKETXN', [], 'Tag:"value"')
        self.assertRaises(TypeError, Client.build_transaction_dict, 'FAKETXN', {'fake': 'payload'}, {})
        mock_creds.assert_not_called()
        mock_request.assert_not_called()

    def test_build_transaction_dict_returns_dict(self, mock_creds, mock_request):
        self.assertEqual(Client.build_transaction_dict('FAKETXN', {}, 'Tag:"value"'), {
            'version': '1',
            'txn_type': 'FAKETXN',
            'payload': {},
            'tag': 'Tag:"value"'
        })
        mock_creds.assert_not_called()
        mock_request.assert_not_called()

    def test_build_transaction_dict_returns_dict_no_tag(self, mock_creds, mock_request):
        self.assertEqual(Client.build_transaction_dict('FAKETXN', {}), {
            'version': '1',
            'txn_type': 'FAKETXN',
            'payload': {}
        })
        mock_creds.assert_not_called()
        mock_request.assert_not_called()

    def test_get_secret_throws_type_error(self, mock_creds, mock_request):
        os.environ['SMART_CONTRACT_ID'] = ''
        self.client = Client()
        self.assertRaises(TypeError, self.client.get_secret, None)
        self.assertRaises(RuntimeError, self.client.get_secret, 'valid_secret')

    @patch('dragonchain_sdk.dragonchain_client.open')
    def test_get_secret_calls_open(self, mock_open, mock_creds, mock_request):
        os.environ['SMART_CONTRACT_ID'] = 'bogusSCID'
        self.client = Client()
        mock_open.return_value.read.return_value = 'fakeSecret'
        self.client.credentials.dragonchain_id = 'fakeDragonchainId'
        self.client.get_secret('mySecret')
        path = os.path.join(os.path.abspath(os.sep), 'var', 'openfaas', 'secrets', 'sc-bogusSCID-mySecret')
        mock_open.assert_called_once_with(path, 'r')

    def test_get_status_calls_get(self, mock_creds, mock_request):
        self.client = Client()
        self.client.get_status()
        self.client.request.get.assert_called_once_with('/status')

    def test_query_contracts_calls_get_without_params(self, mock_creds, mock_request):
        mock_request.return_value.get_lucene_query_params.return_value = ''
        self.client = Client()
        self.client.query_contracts()
        self.client.request.get.assert_called_once_with('/contract')

    def test_query_contracts_calls_get_with_params(self, mock_creds, mock_request):
        mock_request.return_value.get_lucene_query_params.return_value = '?limit=5&offset=10'
        self.client = Client()
        self.client.query_contracts()
        self.client.request.get.assert_called_once_with('/contract?limit=5&offset=10')

    def test_get_contract_throws_type_error(self, mock_creds, mock_request):
        self.client = Client()
        self.assertRaises(TypeError, self.client.get_contract, 1234, 'str')
        self.assertRaises(TypeError, self.client.get_contract, 'str', 1234)
        self.assertRaises(TypeError, self.client.get_contract)
        self.assertRaises(TypeError, self.client.get_contract, 'str', 'str')

    def test_get_contract_with_id_calls_get(self, mock_creds, mock_request):
        self.client = Client()
        self.client.get_contract('some_id')
        self.client.request.get.assert_called_once_with('/contract/some_id')

    def test_get_contract_with_txn_type_calls_get(self, mock_creds, mock_request):
        self.client = Client()
        self.client.get_contract(txn_type='Name')
        self.client.request.get.assert_called_once_with('/contract/txn_type/Name')

    def test_post_contract_raises_type_error(self, mock_creds, mock_request):
        self.client = Client()
        self.assertRaises(TypeError, self.client.post_contract, [], 'MyCode', 'python3.6', 'transaction', True)
        self.assertRaises(TypeError, self.client.post_contract, 'Name', [], 'python3.6', 'transaction', True)
        self.assertRaises(TypeError, self.client.post_contract, 'Name', 'MyCode', [], 'transaction', True)
        self.assertRaises(TypeError, self.client.post_contract, 'Name', 'MyCode', 'python3.6', [], True)
        self.assertRaises(TypeError, self.client.post_contract, 'Name', 'MyCode', 'python3.6', 'transaction', {})
        self.assertRaises(TypeError, self.client.post_contract, 'Name', 'MyCode', 'python3.6', 'serial', [], [])
        self.assertRaises(TypeError, self.client.post_contract, 'Name', 'MyCode', 'python3.6', 'serial', [], {}, [])
        self.assertRaises(TypeError, self.client.post_contract, 'Name', 'MyCode', 'python3.6', 'serial', [], {}, {}, 'seconds')
        self.assertRaises(TypeError, self.client.post_contract, 'Name', 'MyCode', 'python3.6', 'serial', [], {}, {}, 1, 1)
        self.assertRaises(TypeError, self.client.post_contract, 'Name', 'MyCode', 'python3.6', 'serial', [], {}, {}, 1, 'cron', [])
        self.assertRaises(TypeError, self.client.post_contract, 'Name', 'MyCode', 'python3.6', 'transaction', True, env_vars=[])

    def test_post_contract_calls_post(self, mock_creds, mock_request):
        self.client = Client()
        self.client.post_contract('Name', 'serial', 'ubuntu:latest', 'python3.6', None, env={'test': 'env'})
        self.client.request.post.assert_called_once_with('/contract', {
            'version': '3',
            'txn_type': 'Name',
            'image': 'ubuntu:latest',
            'cmd': 'python3.6',
            'execution_order': 'serial',
            'env': {'test': 'env'}
        })

    def test_post_custom_contract_calls_post_with_args(self, mock_creds, mock_request):
        self.client = Client()
        self.client.post_contract('Name', 'serial', 'ubuntu:latest', 'python3.6', ['something'], env={'test': 'env'})
        self.client.request.post.assert_called_once_with('/contract', {
            'version': '3',
            'txn_type': 'Name',
            'image': 'ubuntu:latest',
            'cmd': 'python3.6',
            'execution_order': 'serial',
            'env': {'test': 'env'},
            'args': ['something']
        })

    def test_post_contract_calls_post_with_secrets(self, mock_creds, mock_request):
        self.client = Client()
        self.client.post_contract('Name', 'serial', 'ubuntu:latest', 'python3.6', None, None, None, 1)
        self.client.request.post.assert_called_once_with('/contract', {
            'version': '3',
            'txn_type': 'Name',
            'image': 'ubuntu:latest',
            'cmd': 'python3.6',
            'execution_order': 'serial',
            'seconds': 1
        })

    def test_post_contract_calls_post_with_cron(self, mock_creds, mock_request):
        self.client = Client()
        self.client.post_contract('Name', 'serial', 'ubuntu:latest', 'python3.6', None, None, None, None, '* * *')
        self.client.request.post.assert_called_once_with('/contract', {
            'version': '3',
            'txn_type': 'Name',
            'image': 'ubuntu:latest',
            'cmd': 'python3.6',
            'execution_order': 'serial',
            'cron': '* * *'
        })

    def test_post_contract_calls_post_with_auth(self, mock_creds, mock_request):
        self.client = Client()
        self.client.post_contract('Name', 'serial', 'ubuntu:latest', 'python3.6', None, None, None, None, None, 'auth')
        self.client.request.post.assert_called_once_with('/contract', {
            'version': '3',
            'txn_type': 'Name',
            'image': 'ubuntu:latest',
            'cmd': 'python3.6',
            'execution_order': 'serial',
            'auth': 'auth'
        })

    def test_post_custom_contract_calls_post_with_seconds(self, mock_creds, mock_request):
        self.client = Client()
        self.client.post_contract('Name', 'serial', 'ubuntu:latest', 'python3.6', None, None, {'secret': 'test'})
        self.client.request.post.assert_called_once_with('/contract', {
            'version': '3',
            'txn_type': 'Name',
            'image': 'ubuntu:latest',
            'cmd': 'python3.6',
            'execution_order': 'serial',
            'secrets': {'secret': 'test'}
        })

    def test_post_custom_contract_calls_post_no_env(self, mock_creds, mock_request):
        self.client = Client()
        self.client.post_contract('Name', 'serial', 'ubuntu:latest', 'python3.6', None)
        self.client.request.post.assert_called_once_with('/contract', {
            'version': '3',
            'txn_type': 'Name',
            'image': 'ubuntu:latest',
            'cmd': 'python3.6',
            'execution_order': 'serial'
        })

    def test_update_contract_raises_type_error(self, mock_creds, mock_request):
        self.client = Client()
        self.assertRaises(TypeError, self.client.update_contract, contract_id=[])
        self.assertRaises(TypeError, self.client.update_contract, contract_id='some_id', image=[])
        self.assertRaises(TypeError, self.client.update_contract, contract_id='some_id', cmd=[])
        self.assertRaises(TypeError, self.client.update_contract, contract_id='some_id', execution_order=[])
        self.assertRaises(TypeError, self.client.update_contract, contract_id='some_id', desired_state=[])
        self.assertRaises(TypeError, self.client.update_contract, contract_id='some_id', args={})
        self.assertRaises(TypeError, self.client.update_contract, contract_id='some_id', env=[])
        self.assertRaises(TypeError, self.client.update_contract, contract_id='some_id', secrets=[])
        self.assertRaises(TypeError, self.client.update_contract, contract_id='some_id', seconds='seconds')
        self.assertRaises(TypeError, self.client.update_contract, contract_id='some_id', cron=1)
        self.assertRaises(TypeError, self.client.update_contract, contract_id='some_id', auth=[])

    def test_update_contract_calls_put_no_env(self, mock_creds, mock_request):
        self.client = Client()
        self.client.update_contract(contract_id='some_id', desired_state='enabled', execution_order='parallel', env=None)
        self.client.request.put.assert_called_once_with('/contract/some_id', {
            'version': '3',
            'desired_state': 'enabled',
            'execution_order': 'parallel'
        })

    def test_update_contract_calls_put(self, mock_creds, mock_request):
        self.client = Client()
        self.client.update_contract(contract_id='some_id', desired_state='active', execution_order='parallel', env={'test': 'env'})
        self.client.request.put.assert_called_once_with('/contract/some_id', {
            'version': '3',
            'desired_state': 'active',
            'execution_order': 'parallel',
            'env': {'test': 'env'}
        })

    def test_update_contract_calls_put_with_image(self, mock_creds, mock_request):
        self.client = Client()
        self.client.update_contract(contract_id='some_id', image='sampleImage')
        self.client.request.put.assert_called_once_with('/contract/some_id', {
            'version': '3',
            'image': 'sampleImage'
        })

    def test_update_contract_calls_put_with_cmd(self, mock_creds, mock_request):
        self.client = Client()
        self.client.update_contract(contract_id='some_id', cmd='command')
        self.client.request.put.assert_called_once_with('/contract/some_id', {
            'version': '3',
            'cmd': 'command'
        })

    def test_update_contract_calls_put_with_args(self, mock_creds, mock_request):
        self.client = Client()
        self.client.update_contract(contract_id='some_id', args=['arg'])
        self.client.request.put.assert_called_once_with('/contract/some_id', {
            'version': '3',
            'args': ['arg']
        })

    def test_update_contract_calls_put_with_secrets(self, mock_creds, mock_request):
        self.client = Client()
        self.client.update_contract(contract_id='some_id', secrets={'secret': 'value'})
        self.client.request.put.assert_called_once_with('/contract/some_id', {
            'version': '3',
            'secrets': {'secret': 'value'}
        })

    def test_update_contract_calls_put_with_seconds(self, mock_creds, mock_request):
        self.client = Client()
        self.client.update_contract(contract_id='some_id', seconds=1)
        self.client.request.put.assert_called_once_with('/contract/some_id', {
            'version': '3',
            'seconds': 1
        })

    def test_update_contract_calls_put_with_cron(self, mock_creds, mock_request):
        self.client = Client()
        self.client.update_contract(contract_id='some_id', cron='* * *')
        self.client.request.put.assert_called_once_with('/contract/some_id', {
            'version': '3',
            'cron': '* * *'
        })

    def test_update_contract_calls_put_with_auth(self, mock_creds, mock_request):
        self.client = Client()
        self.client.update_contract(contract_id='some_id', auth='auth')
        self.client.request.put.assert_called_once_with('/contract/some_id', {
            'version': '3',
            'auth': 'auth'
        })

    def test_delete_contract_raises_type_error(self, mock_creds, mock_request):
        self.client = Client()
        self.assertRaises(TypeError, self.client.delete_contract, {})

    def test_delete_contract_calls_delete(self, mock_creds, mock_request):
        self.client = Client()
        self.client.delete_contract(contract_id='some_id')
        self.client.request.delete.assert_called_once_with('/contract/some_id', body={})

    def test_query_transactions_calls_get_without_params(self, mock_creds, mock_request):
        mock_request.return_value.get_lucene_query_params.return_value = ''
        self.client = Client()
        self.client.query_transactions()
        self.client.request.get.assert_called_once_with('/transaction')

    def test_query_transactions_calls_get_with_params(self, mock_creds, mock_request):
        mock_request.return_value.get_lucene_query_params.return_value = '?limit=5&offset=10'
        self.client = Client()
        self.client.query_transactions()
        self.client.request.get.assert_called_once_with('/transaction?limit=5&offset=10')

    def test_post_bulk_transaction_raises_type_error(self, mock_creds, mock_request):
        self.client = Client()
        self.assertRaises(TypeError, self.client.post_transaction_bulk, {})
        self.assertRaises(TypeError, self.client.post_transaction_bulk, [
            1234,
            'not a dict'
        ])

    def test_post_bulk_transaction_calls_posts(self, mock_creds, mock_request):
        self.client = Client()
        self.client.post_transaction_bulk([
            {
                'txn_type': 'TEST_TXN',
                'payload': {'Test': 'Payload'},
                'tag': 'Test:"Tag"'
            },
            {
                'txn_type': 'TEST_TXN2',
                'payload': {'Test': 'Payload'},
                'tag': 'Test:"Tag"'
            }
        ])
        self.client.request.post.assert_called_once_with('/transaction_bulk', [
            {
                'version': '1',
                'txn_type': 'TEST_TXN',
                'payload': {'Test': 'Payload'},
                'tag': 'Test:"Tag"'
            },
            {
                'version': '1',
                'txn_type': 'TEST_TXN2',
                'payload': {'Test': 'Payload'},
                'tag': 'Test:"Tag"'
            }
        ])

    def test_post_transaction_throws_type_error(self, mock_creds, mock_request):
        self.client = Client()
        self.assertRaises(TypeError, self.client.post_transaction, txn_type=[], payload={})
        self.assertRaises(TypeError, self.client.post_transaction, txn_type='Test', payload=[])
        self.assertRaises(TypeError, self.client.post_transaction, txn_type='Test', payload={}, tag=[])

    def test_post_transaction_calls_post_with_dict_payload(self, mock_creds, mock_request):
        self.client = Client()
        self.client.post_transaction(txn_type='TEST_TXN', payload={'hello': 'world'}, tag='MyTag:"value" OtherTag:"other value"')
        self.client.request.post.assert_called_once_with('/transaction', {
            'version': '1',
            'txn_type': 'TEST_TXN',
            'payload': {'hello': 'world'},
            'tag': 'MyTag:"value" OtherTag:"other value"',
        })

    def test_post_transaction_calls_post_with_no_tag(self, mock_creds, mock_request):
        self.client = Client()
        self.client.post_transaction(txn_type='TEST_TXN', payload={'hello': 'world'})
        self.client.request.post.assert_called_once_with('/transaction', {
            'version': '1',
            'txn_type': 'TEST_TXN',
            'payload': {'hello': 'world'}
        })

    def test_post_transaction_calls_post_with_str_payload(self, mock_creds, mock_request):
        self.client = Client()
        self.client.post_transaction(txn_type='TEST_TXN', payload='Hello world', tag='MyTag:"value" OtherTag:"other value"')
        self.client.request.post.assert_called_once_with('/transaction', {
            'version': '1',
            'txn_type': 'TEST_TXN',
            'payload': 'Hello world',
            'tag': 'MyTag:"value" OtherTag:"other value"',
        })

    def test_get_transaction_throws_type_error(self, mock_creds, mock_request):
        self.client = Client()
        self.assertRaises(TypeError, self.client.get_transaction, [])
        self.assertRaises(TypeError, self.client.get_transaction, {})
        self.assertRaises(TypeError, self.client.get_transaction, 1234)
        self.assertRaises(TypeError, self.client.get_transaction, ())

    def test_get_transaction_calls_get(self, mock_creds, mock_request):
        self.client = Client()
        self.client.get_transaction('Test')
        self.client.request.get.assert_called_once_with('/transaction/Test')

    def test_query_blocks_calls_get_without_params(self, mock_creds, mock_request):
        mock_request.return_value.get_lucene_query_params.return_value = ''
        self.client = Client()
        self.client.query_blocks()
        self.client.request.get.assert_called_once_with('/block')

    def test_query_blocks_calls_get_with_params(self, mock_creds, mock_request):
        mock_request.return_value.get_lucene_query_params.return_value = '?limit=5&offset=10'
        self.client = Client()
        self.client.query_blocks()
        self.client.request.get.assert_called_once_with('/block?limit=5&offset=10')

    def test_get_block_throws_type_error(self, mock_creds, mock_request):
        self.client = Client()
        self.assertRaises(TypeError, self.client.get_block, [])
        self.assertRaises(TypeError, self.client.get_block, {})
        self.assertRaises(TypeError, self.client.get_block, ())

    def test_get_block_calls_get_with_string(self, mock_creds, mock_request):
        self.client = Client()
        self.client.get_block('1234')
        self.client.request.get.assert_called_once_with('/block/1234')

    def test_get_block_calls_get_with_integer(self, mock_creds, mock_request):
        self.client = Client()
        self.client.get_block(1234)
        self.client.request.get.assert_called_once_with('/block/1234')

    def test_get_verification_throws_type_error(self, mock_creds, mock_request):
        self.client = Client()
        self.assertRaises(TypeError, self.client.get_verification, [])
        self.assertRaises(TypeError, self.client.get_verification, {})
        self.assertRaises(TypeError, self.client.get_verification, ())
        self.assertRaises(TypeError, self.client.get_verification, '1234', level=[])
        self.assertRaises(TypeError, self.client.get_verification, '1234', level={})
        self.assertRaises(TypeError, self.client.get_verification, '1234', level=())

    def test_get_verification_throws_value_error_on_level_out_of_range(self, mock_creds, mock_request):
        self.client = Client()
        self.assertRaises(ValueError, self.client.get_verification, '1234', level=6)
        self.assertRaises(ValueError, self.client.get_verification, '1234', level='6')
        self.assertRaises(ValueError, self.client.get_verification, '1234', level=1)
        self.assertRaises(ValueError, self.client.get_verification, '1234', level='1')
        self.assertRaises(ValueError, self.client.get_verification, 1234, level=6)
        self.assertRaises(ValueError, self.client.get_verification, 1234, level='6')
        self.assertRaises(ValueError, self.client.get_verification, 1234, level=1)
        self.assertRaises(ValueError, self.client.get_verification, 1234, level='1')

    def test_get_verification_calls_get_with_string(self, mock_creds, mock_request):
        self.client = Client()
        self.client.get_verification('1234')
        self.client.request.get.assert_called_once_with('/verifications/1234')

    def test_get_verification_calls_get_with_integer(self, mock_creds, mock_request):
        self.client = Client()
        self.client.get_verification(1234)
        self.client.request.get.assert_called_once_with('/verifications/1234')

    def test_get_verification_calls_get_with_string_and_level_string(self, mock_creds, mock_request):
        self.client = Client()
        self.client.get_verification('1234', level='5')
        self.client.request.get.assert_called_once_with('/verifications/1234?level=5')

    def test_get_verification_calls_get_with_integer_and_level_string(self, mock_creds, mock_request):
        self.client = Client()
        self.client.get_verification(1234, level='5')
        self.client.request.get.assert_called_once_with('/verifications/1234?level=5')

    def test_get_verification_calls_get_with_string_and_level_integer(self, mock_creds, mock_request):
        self.client = Client()
        self.client.get_verification('1234', level=5)
        self.client.request.get.assert_called_once_with('/verifications/1234?level=5')

    def test_get_verification_calls_get_with_integer_and_level_integer(self, mock_creds, mock_request):
        self.client = Client()
        self.client.get_verification(1234, level=5)
        self.client.request.get.assert_called_once_with('/verifications/1234?level=5')

    def test_get_sc_heap_throws_type_error(self, mock_creds, mock_request):
        self.client = Client()
        self.assertRaises(TypeError, self.client.get_sc_heap, key=[], sc_id='Test')
        self.assertRaises(TypeError, self.client.get_sc_heap, key=[])
        self.assertRaises(TypeError, self.client.get_sc_heap, key='MyKey', sc_id=[])

    @patch.dict(os.environ, {'SMART_CONTRACT_ID': 'MyName'})
    def test_get_sc_heap_reads_env_and_calls_get(self, mock_creds, mock_request):
        self.client = Client()
        self.client.get_sc_heap(key='MyKey')
        self.client.request.get.assert_called_once_with('/get/MyName/MyKey', parse_response=False)

    @patch.dict(os.environ, {'SMART_CONTRACT_ID': 'MyName'})
    def test_get_sc_heap_reads_env_and_calls_get_with_override(self, mock_creds, mock_request):
        self.client = Client()
        self.client.get_sc_heap(sc_id='Override', key='MyKey')
        self.client.request.get.assert_called_once_with('/get/Override/MyKey', parse_response=False)

    def test_get_sc_heap_calls_get(self, mock_creds, mock_request):
        self.client = Client()
        self.client.get_sc_heap(key='MyKey', sc_id='MyContract')
        self.client.request.get.assert_called_once_with('/get/MyContract/MyKey', parse_response=False)

    def test_list_sc_heap_throws_type_error(self, mock_creds, mock_request):
        self.client = Client()
        self.assertRaises(TypeError, self.client.list_sc_heap, folder=[], sc_id='MyContract')
        self.assertRaises(TypeError, self.client.list_sc_heap, folder='MyFolder', sc_id=[])

    def test_list_sc_heap_throws_value_error(self, mock_creds, mock_request):
        self.client = Client()
        self.assertRaises(ValueError, self.client.list_sc_heap, folder='MyFolder/', sc_id='MyContract')

    @patch.dict(os.environ, {'SMART_CONTRACT_ID': 'MyName'})
    def test_list_sc_heap_reads_env_and_calls_get(self, mock_creds, mock_request):
        self.client = Client()
        self.client.list_sc_heap(folder='MyFolder')
        self.client.request.get.assert_called_once_with('/list/MyName/MyFolder/')

    @patch.dict(os.environ, {'SMART_CONTRACT_ID': 'MyName'})
    def test_list_sc_heap_reads_env_and_calls_get_with_override(self, mock_creds, mock_request):
        self.client = Client()
        self.client.list_sc_heap(sc_id='Override', folder='MyFolder')
        self.client.request.get.assert_called_once_with('/list/Override/MyFolder/')

    def test_list_sc_heap_calls_get(self, mock_creds, mock_request):
        self.client = Client()
        self.client.list_sc_heap(sc_id='MyContract', folder='MyFolder')
        self.client.request.get.assert_called_once_with('/list/MyContract/MyFolder/')

    def test_list_sc_heap_calls_get_root(self, mock_creds, mock_request):
        self.client = Client()
        self.client.list_sc_heap(sc_id='MyContract')
        self.client.request.get.assert_called_once_with('/list/MyContract/')

    def test_register_transaction_type_calls_post(self, mock_creds, mock_request):
        self.client = Client()
        self.client.register_transaction_type('MyNewType')
        self.client.request.post.assert_called_once_with('/transaction-type', {"version": "1", "txn_type": "MyNewType"})

    def test_register_transaction_type_calls_post_with_custom_indexes(self, mock_creds, mock_request):
        custom_indexes = [{"key": "name", "path": "body.name"}]
        self.client = Client()
        self.client.register_transaction_type('MyNewType', custom_indexes)
        self.client.request.post.assert_called_once_with('/transaction-type', {"version": "1", "txn_type": "MyNewType", "custom_indexes": custom_indexes})

    def test_register_transaction_type_raises_error_type_is_not_string(self, mock_creds, mock_request):
        self.client = Client()
        self.assertRaises(TypeError, self.client.register_transaction_type, {})

    def test_register_transaction_type_raises_error_indexes_not_array(self, mock_creds, mock_request):
        self.client = Client()
        self.assertRaises(TypeError, self.client.register_transaction_type, 'myType', 'notaobject')

    def test_update_transaction_type_calls_put(self, mock_creds, mock_request):
        self.client = Client()
        self.client.update_transaction_type('MyCurrentType')
        self.client.request.put.assert_called_once_with('/transaction-type/MyCurrentType', {"version": "1", "custom_indexes": []})

    def test_update_transaction_type_raises_error_with_invalid_txn_type(self, mock_creds, mock_request):
        self.client = Client()
        self.assertRaises(TypeError, self.client.update_transaction_type, {})

    def test_update_transaction_type_raises_error_with_invalid_indexes(self, mock_creds, mock_request):
        self.client = Client()
        self.assertRaises(TypeError, self.client.update_transaction_type, 'myType', {})

    def test_delete_transaction_type_calls_delete(self, mock_creds, mock_request):
        self.client = Client()
        self.client.delete_transaction_type('MyCurrentType')
        self.client.request.delete.assert_called_once_with('/transaction-type/MyCurrentType', body={})

    def test_delete_transaction_type_raises_error_type_not_string(self, mock_creds, mock_request):
        self.client = Client()
        self.assertRaises(TypeError, self.client.delete_transaction_type, {})

    def test_get_transaction_type_raises_type_error(self, mock_creds, mock_request):
        self.client = Client()
        self.assertRaises(TypeError, self.client.get_transaction_type, {})

    def test_get_transaction_type_succeeds(self, mock_creds, mock_request):
        self.client = Client()
        self.client.get_transaction_type('myType')
        self.client.request.get.assert_called_once_with('/transaction-type/myType')

    def test_list_transaction_types_succeeds(self, mock_creds, mock_request):
        self.client = Client()
        self.client.list_transaction_types()
        self.client.request.get.assert_called_once_with('/transaction-types')

    def test_public_blockchain_transaction_create(self, mock_creds, mock_request):
        self.client = Client()
        self.client.list_transaction_types()
        self.client.request.get.assert_called_once_with('/transaction-types')

    def test_public_blockchain_address_get(self, mock_creds, mock_request):
        self.client = Client()
        self.client.get_public_blockchain_addresses()
        self.client.request.get.assert_called_once_with('/public-blockchain-address')

    def test_create_public_transaction(self, mock_creds, mock_request):
        self.client = Client()
        self.client.create_public_transaction('ETH_ROPSTEN', {
            'to': '0x0000000000000000000000000000000000000000',
            'value': '0x0'
        })
        self.client.request.post.assert_called_once_with('/public-blockchain-transaction', body={
            'network': 'ETH_ROPSTEN',
            'transaction': {
                'to': '0x0000000000000000000000000000000000000000',
                'value': '0x0'
            }
        })

    def test_create_public_throws_value_error_on_invalid_network(self, mock_creds, mock_request):
        self.client = Client()
        self.assertRaises(ValueError, self.client.create_public_transaction, 'NEO_MAINNET', {})

    def test_create_public_throws_type_error_on_invalid_network_type(self, mock_creds, mock_request):
        self.client = Client()
        self.assertRaises(TypeError, self.client.create_public_transaction, b'ETH_MAINNET', {})

    def test_create_public_throws_type_error_on_invalid_transaction_type(self, mock_creds, mock_request):
        self.client = Client()
        self.assertRaises(TypeError, self.client.create_public_transaction, 'ETH_MAINNET', 'invalid')
