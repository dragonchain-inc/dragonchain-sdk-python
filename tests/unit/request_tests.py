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
from unittest.mock import MagicMock
import requests
import json
import copy
import dc_sdk.lib.request


class TestRequests(TestCase):
    def test_get_requests_method(self):
        self.assertEqual(dc_sdk.lib.request.get_requests_method('get'), requests.get)
        self.assertEqual(dc_sdk.lib.request.get_requests_method('post'), requests.post)
        self.assertEqual(dc_sdk.lib.request.get_requests_method('put'), requests.put)
        self.assertEqual(dc_sdk.lib.request.get_requests_method('patch'), requests.patch)
        self.assertEqual(dc_sdk.lib.request.get_requests_method('delete'), requests.delete)
        self.assertEqual(dc_sdk.lib.request.get_requests_method('head'), requests.head)
        self.assertEqual(dc_sdk.lib.request.get_requests_method('options'), requests.options)
        self.assertRaises(ValueError, dc_sdk.lib.request.get_requests_method, 'NOTAMETHOD')
        self.assertRaises(ValueError, dc_sdk.lib.request.get_requests_method, 1234)

    def test_get_content_and_type(self):
        test_obj = {'thing': 'data'}
        self.assertEqual(dc_sdk.lib.request.get_content_and_type('a type', '', ''), ('', ''))
        self.assertEqual(dc_sdk.lib.request.get_content_and_type('a type', b'some bytes', ''), ('a type', 'some bytes'))
        self.assertEqual(dc_sdk.lib.request.get_content_and_type('a type', 'some data', ''), ('a type', 'some data'))
        self.assertEqual(dc_sdk.lib.request.get_content_and_type('', '', json=test_obj), ('application/json', json.dumps(test_obj)))
        self.assertRaises(ValueError, dc_sdk.lib.request.get_content_and_type, '', '', 'not a dict')
        self.assertRaises(ValueError, dc_sdk.lib.request.get_content_and_type, 123, 'data', '')
        self.assertRaises(ValueError, dc_sdk.lib.request.get_content_and_type, '', 123, '')

    def test_status_code_is_ok(self):
        self.assertEqual(dc_sdk.lib.request.status_code_is_ok(100), False)
        self.assertEqual(dc_sdk.lib.request.status_code_is_ok(199), False)
        self.assertEqual(dc_sdk.lib.request.status_code_is_ok(200), True)
        self.assertEqual(dc_sdk.lib.request.status_code_is_ok(299), True)
        self.assertEqual(dc_sdk.lib.request.status_code_is_ok(300), False)
        self.assertEqual(dc_sdk.lib.request.status_code_is_ok(399), False)
        self.assertEqual(dc_sdk.lib.request.status_code_is_ok(400), False)

    def test_make_query_string(self):
        dict_params = {
            'key': 'value'
        }
        self.assertEqual(dc_sdk.lib.request.generate_query_string(dict_params), '?key=value')
        dict_params['keys'] = 'values'
        self.assertEqual(dc_sdk.lib.request.generate_query_string(dict_params), '?key=value&keys=values')
        self.assertEqual(dc_sdk.lib.request.generate_query_string({}), '')
        self.assertRaises(ValueError, dc_sdk.lib.request.generate_query_string, 'not a dict')

    def test_lucene_query_string(self):
        self.assertEqual(dc_sdk.lib.request.get_lucene_query_params('q', 's', 1, 2), '?offset=1&limit=2&q=q&sort=s')
        self.assertEqual(dc_sdk.lib.request.get_lucene_query_params(None, None, 1, 2), '?offset=1&limit=2')
        self.assertRaises(ValueError, dc_sdk.lib.request.get_lucene_query_params, 1)
        self.assertRaises(ValueError, dc_sdk.lib.request.get_lucene_query_params, 'a', 1)
        self.assertRaises(ValueError, dc_sdk.lib.request.get_lucene_query_params, 'a', 'a', 'a')
        self.assertRaises(ValueError, dc_sdk.lib.request.get_lucene_query_params, 'a', 'a', 1, 'a')

    def test_make_headers(self):
        dcid = 'an id'
        timestamp = 'a timestamp'
        authorization = 'some authorization'
        content_type = 'a content type'
        expected = {
            'dragonchain': dcid,
            'timestamp': timestamp,
            'Authorization': authorization
        }
        user_key = 'custom'
        user_value = 'value'
        user_header = {
            user_key: user_value
        }
        self.assertDictEqual(dc_sdk.lib.request.make_headers(dcid, timestamp, '', authorization, None), expected)
        expected['Content-Type'] = content_type
        self.assertDictEqual(dc_sdk.lib.request.make_headers(dcid, timestamp, content_type, authorization, None), expected)
        expected[user_key] = user_value
        self.assertDictEqual(dc_sdk.lib.request.make_headers(dcid, timestamp, content_type, authorization, user_header), expected)
        user_header['dragonchain'] = 'reserved keyword'
        self.assertDictEqual(dc_sdk.lib.request.make_headers(dcid, timestamp, content_type, authorization, user_header), expected)
        self.assertRaises(ValueError, dc_sdk.lib.request.make_headers, 123, '', '', '', {})
        self.assertRaises(ValueError, dc_sdk.lib.request.make_headers, '', 123, '', '', {})
        self.assertRaises(ValueError, dc_sdk.lib.request.make_headers, '', '', 123, '', {})
        self.assertRaises(ValueError, dc_sdk.lib.request.make_headers, '', '', '', 123, {})
        self.assertRaises(ValueError, dc_sdk.lib.request.make_headers, 'a', 'a', 'a', 'a', 'not a dict')

    def test_make_request(self):
        good_response = requests.Response()
        setattr(good_response, '_content', b'{"valid":"json"}')
        good_response_obj = {'valid': 'json'}
        good_response_str = '{"valid":"json"}'
        setattr(good_response, 'status_code', 200)
        bad_response = copy.deepcopy(good_response)
        setattr(bad_response, 'status_code', 400)
        invalid_response = copy.deepcopy(good_response)
        setattr(invalid_response, '_content', b'invalid json')
        to_test = dc_sdk.lib.request
        kwargs = {
            'endpoint': 'https://an_endpoint',
            'auth_key_id': 'an id',
            'auth_key': 'a key',
            'dcid': 'a dcid',
            'http_verb': 'get',
            'path': '/some/path',
            'parse_json': True,
        }
        # Test valid response
        to_test.get_requests_method = MagicMock(return_value=MagicMock(return_value=good_response))
        self.assertDictEqual(to_test.make_request(**kwargs), good_response_obj)
        kwargs['parse_json'] = False
        self.assertEqual(to_test.make_request(**kwargs), good_response_str)
        kwargs['parse_json'] = True
        # Test non-2XX response
        to_test.get_requests_method = MagicMock(return_value=MagicMock(return_value=bad_response))
        self.assertRaises(RuntimeError, to_test.make_request, **kwargs)
        # Test response where non-valid json is returned
        to_test.get_requests_method = MagicMock(return_value=MagicMock(return_value=invalid_response))
        self.assertRaises(RuntimeError, to_test.make_request, **kwargs)
        # Test exception thrown while making a request
        to_test.get_requests_method = MagicMock(return_value=MagicMock(side_effect=Exception))
        self.assertRaises(RuntimeError, to_test.make_request, **kwargs)
        # Test invalid input
        kwargs['endpoint'] = 123
        self.assertRaises(ValueError, to_test.make_request, **kwargs)
        kwargs['endpoint'] = 'https://an_endpoint'
        kwargs['auth_key_id'] = 123
        self.assertRaises(ValueError, to_test.make_request, **kwargs)
        kwargs['auth_key_id'] = 'an id'
        kwargs['auth_key'] = 123
        self.assertRaises(ValueError, to_test.make_request, **kwargs)
        kwargs['auth_key'] = 'a key'
        kwargs['path'] = 123
        self.assertRaises(ValueError, to_test.make_request, **kwargs)
        kwargs['path'] = 'not a path'
        self.assertRaises(ValueError, to_test.make_request, **kwargs)
