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
from unittest.mock import MagicMock, patch
import requests
import requests_mock
from dragonchain_sdk.request import Request
from dragonchain_sdk.credentials import Credentials
from dragonchain_sdk import exceptions


class TestRequestsInitialization(TestCase):
    def setUp(self):
        self.creds = Credentials(dragonchain_id='TestID', auth_key='TestKey', auth_key_id='TestKeyId')

    def test_initialization_throws_type_error(self):
        self.assertRaises(TypeError, Request, 'not a credentials service')
        self.assertRaises(TypeError, Request, self.creds, verify=[])

    def test_initialized_correct(self):
        request = Request(self.creds)
        self.assertEqual(request.credentials, self.creds)
        self.assertEqual(request.endpoint, 'https://TestID.api.dragonchain.com')
        self.assertEqual(request.verify, True)


class TestRequestsMethods(TestCase):
    def setUp(self):
        self.creds = Credentials(dragonchain_id='TestID', auth_key='TestKey', auth_key_id='TestKeyId')
        self.request = Request(self.creds)

    def test_update_endpoint_no_params(self):
        self.creds.dragonchain_id = 'TestID2'
        self.request.update_endpoint()
        self.assertEqual(self.request.endpoint, 'https://TestID2.api.dragonchain.com')

    def test_update_endpoint(self):
        self.request.update_endpoint('https://newurl.com')
        self.assertEqual(self.request.endpoint, 'https://newurl.com')

    def test_update_endpoint_raises_type_error(self):
        self.assertRaises(TypeError, self.request.update_endpoint, [])
        self.assertRaises(TypeError, self.request.update_endpoint, {})
        self.assertRaises(TypeError, self.request.update_endpoint, 1234)

    @patch('dragonchain_sdk.request.Request._make_request', return_value='response')
    def test_get_calls_make_request(self, mock_request):
        self.assertEqual(self.request.get('/test'), 'response')
        mock_request.assert_called_once_with(
            http_verb='GET',
            path='/test',
            verify=True,
            parse_response=True
        )

    @patch('dragonchain_sdk.request.Request._make_request', return_value='response')
    def test_put_calls_make_request(self, mock_request):
        self.assertEqual(self.request.put('/test', {'body': 'hello world'}), 'response')
        mock_request.assert_called_once_with(
            http_verb='PUT',
            path='/test',
            verify=True,
            json={'body': 'hello world'},
            parse_response=True
        )

    @patch('dragonchain_sdk.request.Request._make_request', return_value='response')
    def test_post_calls_make_request(self, mock_request):
        self.assertEqual(self.request.post('/test', {'body': 'hello world'}), 'response')
        mock_request.assert_called_once_with(
            http_verb='POST',
            path='/test',
            verify=True,
            json={'body': 'hello world'},
            parse_response=True
        )

    def test_get_request_method_raises_type_error(self):
        self.assertRaises(TypeError, self.request.get_requests_method, [])
        self.assertRaises(TypeError, self.request.get_requests_method, {})
        self.assertRaises(TypeError, self.request.get_requests_method, 1234)

    def test_get_request_method_raises_value_error(self):
        self.assertRaises(ValueError, self.request.get_requests_method, 'PLACE')

    def test_get_request_method_returns_get(self):
        self.assertEqual(self.request.get_requests_method('GET'), requests.get)
        self.assertEqual(self.request.get_requests_method('get'), requests.get)

    def test_get_request_method_returns_post(self):
        self.assertEqual(self.request.get_requests_method('POST'), requests.post)
        self.assertEqual(self.request.get_requests_method('post'), requests.post)

    def test_get_request_method_returns_put(self):
        self.assertEqual(self.request.get_requests_method('PUT'), requests.put)
        self.assertEqual(self.request.get_requests_method('put'), requests.put)

    def test_get_request_method_returns_patch(self):
        self.assertEqual(self.request.get_requests_method('PATCH'), requests.patch)
        self.assertEqual(self.request.get_requests_method('patch'), requests.patch)

    def test_get_request_method_returns_delete(self):
        self.assertEqual(self.request.get_requests_method('DELETE'), requests.delete)
        self.assertEqual(self.request.get_requests_method('delete'), requests.delete)

    def test_get_request_method_returns_head(self):
        self.assertEqual(self.request.get_requests_method('HEAD'), requests.head)
        self.assertEqual(self.request.get_requests_method('head'), requests.head)

    def test_get_request_method_returns_options(self):
        self.assertEqual(self.request.get_requests_method('OPTIONS'), requests.options)
        self.assertEqual(self.request.get_requests_method('options'), requests.options)

    def test_generate_query_string_raises_type_error(self):
        self.assertRaises(TypeError, self.request.generate_query_string, [])
        self.assertRaises(TypeError, self.request.generate_query_string, 'test')
        self.assertRaises(TypeError, self.request.generate_query_string, 1234)

    def test_generate_query_string_returns_empty_string(self):
        self.assertEqual(self.request.generate_query_string({}), '')

    def test_generate_query_string(self):
        self.assertEqual(self.request.generate_query_string({
            'key1': 'val1',
            'key2': 'val2'
        }), '?key1=val1&key2=val2')

    def test_get_lucene_query_params_raises_type_error(self):
        self.assertRaises(TypeError, self.request.get_lucene_query_params, query=[])
        self.assertRaises(TypeError, self.request.get_lucene_query_params, sort=[])
        self.assertRaises(TypeError, self.request.get_lucene_query_params, limit=[])
        self.assertRaises(TypeError, self.request.get_lucene_query_params, offset=[])

    def test_get_lucene_query_params(self):
        self.assertEqual(
            self.request.get_lucene_query_params(query='test:"val"', sort='test:desc', offset=0, limit=100),
            '?offset=0&limit=100&q=test:"val"&sort=test:desc'
        )

    def test_get_lucene_query_params_no_query(self):
        self.assertEqual(
            self.request.get_lucene_query_params(sort='test:desc', offset=0, limit=100),
            '?offset=0&limit=100&sort=test:desc'
        )

    def test_get_lucene_query_params_no_sort(self):
        self.assertEqual(
            self.request.get_lucene_query_params(query='test:"val"', offset=0, limit=100),
            '?offset=0&limit=100&q=test:"val"'
        )

    def test_make_headers(self):
        self.assertEqual(self.request.make_headers('Timestamp', 'Auth', ''), {'dragonchain': 'TestID', 'timestamp': 'Timestamp', 'Authorization': 'Auth'})
        self.assertEqual(self.request.make_headers('Timestamp', 'Auth', 'application/json'), {'dragonchain': 'TestID', 'timestamp': 'Timestamp', 'Authorization': 'Auth', 'Content-Type': 'application/json'})

    def test_make_headers_throws_type_error(self):
        self.assertRaises(TypeError, self.request.make_headers, [], '', '')
        self.assertRaises(TypeError, self.request.make_headers, '', [], '')
        self.assertRaises(TypeError, self.request.make_headers, '', '', [])

    def test_make_request_raises_type_error(self):
        self.assertRaises(TypeError, self.request._make_request, 'GET', [])

    def test_make_request_raises_value_error(self):
        self.assertRaises(ValueError, self.request._make_request, 'GET', 'NoSlashPath')

    @patch('dragonchain_sdk.request.Request.get_requests_method')
    def test_make_request_raises_runtime_error_on_request_failure(self, mock_get_request):
        mock_get_request.return_value = MagicMock(side_effect=Exception)
        self.assertRaises(exceptions.ConnectionException, self.request._make_request, 'GET', '/transaction')
        mock_get_request.assert_called_once_with('GET')

    def test_make_request_returns_ok_false_on_bad_response_status(self):
        with requests_mock.mock() as m:
            m.get('https://TestID.api.dragonchain.com/transaction', status_code=400, text='{"error": "some error"}')
            expected_response = {
                'ok': False,
                'status': 400,
                'response': {'error': 'some error'}
            }
            self.assertDictEqual(self.request._make_request('GET', '/transaction'), expected_response)

    def test_make_request_parse_json(self):
        with requests_mock.mock() as m:
            m.get('https://TestID.api.dragonchain.com/transaction', status_code=200, json={'test': 'object'})
            self.request._make_request('GET', '/transaction')
            expected_response = {
                'ok': True,
                'status': 200,
                'response': {'test': 'object'}
            }
            self.assertDictEqual(self.request._make_request('GET', '/transaction', parse_response=True), expected_response)

    def test_make_request_no_parse_json(self):
        with requests_mock.mock() as m:
            m.get('https://TestID.api.dragonchain.com/transaction', status_code=200, text='{"test": "object"}')
            expected_response = {
                'ok': True,
                'status': 200,
                'response': '{"test": "object"}'
            }
            self.assertDictEqual(self.request._make_request('GET', '/transaction', parse_response=False), expected_response)

    @patch('dragonchain_sdk.request.Request.get_requests_method')
    def test_make_request_raises_runtime_error_on_parse_json_error(self, mock_get_request):
        mock_get_request.return_value.return_value.json.side_effect = RuntimeError('JSON Parse Error')
        mock_get_request.return_value.return_value.status_code = 200
        self.assertRaises(exceptions.UnexpectedResponseException, self.request._make_request, 'GET', '/transaction')
