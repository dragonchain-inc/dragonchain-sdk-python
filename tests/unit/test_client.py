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
from dragonchain_sdk import exceptions


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
    def test_check_sc_runtime_raises_value_error(self, mock_creds, mock_request):
        self.assertRaises(ValueError, Client.check_runtime, {})
        self.assertRaises(ValueError, Client.check_runtime, [])
        self.assertRaises(ValueError, Client.check_runtime, 'fortran')
        mock_creds.assert_not_called()
        mock_request.assert_not_called()

    def test_check_sc_runtime(self, mock_creds, mock_request):
        self.assertEqual(Client.check_runtime('go1.x'), None)
        self.assertEqual(Client.check_runtime('python3.6'), None)
        mock_creds.assert_not_called()
        mock_request.assert_not_called()

    def test_check_sc_type_raises_value_error(self, mock_creds, mock_request):
        self.assertRaises(ValueError, Client.check_sc_type, {})
        self.assertRaises(ValueError, Client.check_sc_type, [])
        self.assertRaises(ValueError, Client.check_sc_type, 'subscription')
        mock_creds.assert_not_called()
        mock_request.assert_not_called()

    def test_check_sc_type(self, mock_creds, mock_request):
        self.assertEqual(Client.check_sc_type('transaction'), None)
        self.assertEqual(Client.check_sc_type('cron'), None)
        mock_creds.assert_not_called()
        mock_request.assert_not_called()

    def test_check_valid_library_contract_raises_value_error(self, mock_creds, mock_request):
        self.assertRaises(ValueError, Client.check_valid_library_contract, {})
        self.assertRaises(ValueError, Client.check_valid_library_contract, [])
        self.assertRaises(ValueError, Client.check_valid_library_contract, 'subscription')
        mock_creds.assert_not_called()
        mock_request.assert_not_called()

    def test_check_valid_library_contract(self, mock_creds, mock_request):
        self.assertEqual(Client.check_valid_library_contract('currency'), None)
        self.assertEqual(Client.check_valid_library_contract('interchainWatcher'), None)
        mock_creds.assert_not_called()
        mock_request.assert_not_called()

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
        self.assertRaises(TypeError, self.client.get_contract, [])
        self.assertRaises(TypeError, self.client.get_contract, {})
        self.assertRaises(TypeError, self.client.get_contract, 1234)
        self.assertRaises(TypeError, self.client.get_contract, ())

    def test_get_contract_calls_get(self, mock_creds, mock_request):
        self.client = Client()
        self.client.get_contract('Test')
        self.client.request.get.assert_called_once_with('/contract/Test')

    def test_post_custom_contract_raises_type_error(self, mock_creds, mock_request):
        self.client = Client()
        self.assertRaises(TypeError, self.client.post_custom_contract, [], 'MyCode', 'python3.6', 'handler', 'transaction', True)
        self.assertRaises(TypeError, self.client.post_custom_contract, 'Name', [], 'python3.6', 'handler', 'transaction', True)
        self.assertRaises(TypeError, self.client.post_custom_contract, 'Name', 'MyCode', [], 'handler', 'transaction', True)
        self.assertRaises(TypeError, self.client.post_custom_contract, 'Name', 'MyCode', 'python3.6', [], 'transaction', True)
        self.assertRaises(TypeError, self.client.post_custom_contract, 'Name', 'MyCode', 'python3.6', 'handler', [], True)
        self.assertRaises(TypeError, self.client.post_custom_contract, 'Name', 'MyCode', 'python3.6', 'handler', 'transaction', [])
        self.assertRaises(TypeError, self.client.post_custom_contract, 'Name', 'MyCode', 'python3.6', 'handler', 'transaction', True, env_vars=[])

    def test_post_custom_contract_calls_post(self, mock_creds, mock_request):
        self.client = Client()
        self.client.post_custom_contract('Name', 'MyCode', 'python3.6', 'handler', 'transaction', True, env_vars={'test': 'env'})
        self.client.request.post.assert_called_once_with('/contract/Name', {
            'version': '2',
            'origin': 'custom',
            'name': 'Name',
            'code': 'MyCode',
            'runtime': 'python3.6',
            'sc_type': 'transaction',
            'is_serial': True,
            'handler': 'handler',
            'custom_environment_variables': {'test': 'env'}
        })

    def test_post_custom_contract_calls_post_no_env(self, mock_creds, mock_request):
        self.client = Client()
        self.client.post_custom_contract('Name', 'MyCode', 'python3.6', 'handler', 'transaction', True)
        self.client.request.post.assert_called_once_with('/contract/Name', {
            'version': '2',
            'origin': 'custom',
            'name': 'Name',
            'code': 'MyCode',
            'runtime': 'python3.6',
            'sc_type': 'transaction',
            'is_serial': True,
            'handler': 'handler'
        })

    def test_post_library_contract_raises_type_error(self, mock_creds, mock_request):
        self.client = Client()
        self.assertRaises(TypeError, self.client.post_library_contract, [], 'currency', env_vars=None)
        self.assertRaises(TypeError, self.client.post_library_contract, 'Name', [], env_vars=None)
        self.assertRaises(TypeError, self.client.post_library_contract, 'Name', 'currency', env_vars=[])

    def test_post_library_contract_calls_post(self, mock_creds, mock_request):
        self.client = Client()
        self.client.post_library_contract('Name', 'currency', env_vars={'test': 'env'})
        self.client.request.post.assert_called_once_with('/contract/Name', {
            'version': '2',
            'origin': 'library',
            'name': 'Name',
            'libraryContractName': 'currency',
            'custom_environment_variables': {'test': 'env'}
        })

    def test_post_library_contract_calls_post_no_env(self, mock_creds, mock_request):
        self.client = Client()
        self.client.post_library_contract('Name', 'currency')
        self.client.request.post.assert_called_once_with('/contract/Name', {
            'version': '2',
            'origin': 'library',
            'name': 'Name',
            'libraryContractName': 'currency'
        })

    def test_update_contract_raises_type_error(self, mock_creds, mock_request):
        self.client = Client()
        self.assertRaises(TypeError, self.client.update_contract, name=[])
        self.assertRaises(TypeError, self.client.update_contract, name='Name', status=[])
        self.assertRaises(TypeError, self.client.update_contract, name='Name', code=[])
        self.assertRaises(TypeError, self.client.update_contract, name='Name', runtime=[])
        self.assertRaises(TypeError, self.client.update_contract, name='Name', sc_type=[])
        self.assertRaises(TypeError, self.client.update_contract, name='Name', serial=[])
        self.assertRaises(TypeError, self.client.update_contract, name='Name', env_vars=[])

    def test_update_contract_raises_value_error(self, mock_creds, mock_request):
        self.client = Client()
        self.assertRaises(ValueError, self.client.update_contract, name=None)

    def test_update_contract_calls_put_no_env(self, mock_creds, mock_request):
        self.client = Client()
        self.client.update_contract(name='Name', status='enabled', sc_type='transaction', code='code', runtime='nodejs8.10', serial=True, env_vars=None)
        self.client.request.put.assert_called_once_with('/contract/Name', {
            'status': 'enabled',
            'sc_type': 'transaction',
            'code': 'code',
            'runtime': 'nodejs8.10',
            'serial': True
        })

    def test_update_contract_calls_put(self, mock_creds, mock_request):
        self.client = Client()
        self.client.update_contract(name='Name', status='enabled', sc_type='transaction', code='code', runtime='nodejs8.10', serial=True, env_vars={'test': 'env'})
        self.client.request.put.assert_called_once_with('/contract/Name', {
            'status': 'enabled',
            'sc_type': 'transaction',
            'code': 'code',
            'runtime': 'nodejs8.10',
            'serial': True,
            'custom_environment_variables': {'test': 'env'}
        })

    def test_update_contract_no_op(self, mock_creds, mock_request):
        self.client = Client()
        self.assertRaises(exceptions.EmptyUpdateException, self.client.update_contract, name='Name')

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
        self.assertRaises(TypeError, self.client.get_sc_heap, key=[], sc_name='Test')
        self.assertRaises(TypeError, self.client.get_sc_heap, key=[])
        self.assertRaises(TypeError, self.client.get_sc_heap, key='MyKey', sc_name=[])

    @patch.dict(os.environ, {'SMART_CONTRACT_NAME': 'MyName'})
    def test_get_sc_heap_reads_env_and_calls_get(self, mock_creds, mock_request):
        self.client = Client()
        self.client.get_sc_heap(key='MyKey')
        self.client.request.get.assert_called_once_with('/get/MyName/MyKey', parse_response=False)

    @patch.dict(os.environ, {'SMART_CONTRACT_NAME': 'MyName'})
    def test_get_sc_heap_reads_env_and_calls_get_with_override(self, mock_creds, mock_request):
        self.client = Client()
        self.client.get_sc_heap(sc_name='Override', key='MyKey')
        self.client.request.get.assert_called_once_with('/get/Override/MyKey', parse_response=False)

    def test_get_sc_heap_calls_get(self, mock_creds, mock_request):
        self.client = Client()
        self.client.get_sc_heap(key='MyKey', sc_name='MyContract')
        self.client.request.get.assert_called_once_with('/get/MyContract/MyKey', parse_response=False)

    def test_list_sc_heap_throws_type_error(self, mock_creds, mock_request):
        self.client = Client()
        self.assertRaises(TypeError, self.client.list_sc_heap, folder=[], sc_name='MyContract')
        self.assertRaises(TypeError, self.client.list_sc_heap, folder='MyFolder', sc_name=[])

    def test_list_sc_heap_throws_value_error(self, mock_creds, mock_request):
        self.client = Client()
        self.assertRaises(ValueError, self.client.list_sc_heap, folder='MyFolder/', sc_name='MyContract')

    @patch.dict(os.environ, {'SMART_CONTRACT_NAME': 'MyName'})
    def test_list_sc_heap_reads_env_and_calls_get(self, mock_creds, mock_request):
        self.client = Client()
        self.client.list_sc_heap(folder='MyFolder')
        self.client.request.get.assert_called_once_with('/list/MyName/MyFolder/')

    @patch.dict(os.environ, {'SMART_CONTRACT_NAME': 'MyName'})
    def test_list_sc_heap_reads_env_and_calls_get_with_override(self, mock_creds, mock_request):
        self.client = Client()
        self.client.list_sc_heap(sc_name='Override', folder='MyFolder')
        self.client.request.get.assert_called_once_with('/list/Override/MyFolder/')

    def test_list_sc_heap_calls_get(self, mock_creds, mock_request):
        self.client = Client()
        self.client.list_sc_heap(sc_name='MyContract', folder='MyFolder')
        self.client.request.get.assert_called_once_with('/list/MyContract/MyFolder/')

    def test_list_sc_heap_calls_get_root(self, mock_creds, mock_request):
        self.client = Client()
        self.client.list_sc_heap(sc_name='MyContract')
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
        self.client.request.delete.assert_called_once_with('/transaction-type/MyCurrentType')

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
