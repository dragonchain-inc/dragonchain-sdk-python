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
import dc_sdk.lib.auth

sha256 = dc_sdk.lib.auth.SupportedHashes.sha256
blake2b = dc_sdk.lib.auth.SupportedHashes.blake2b
sha3_256 = dc_sdk.lib.auth.SupportedHashes.sha3_256


class TestAuth(TestCase):
    def test_get_supported_hashing(self):
        self.assertEqual(dc_sdk.lib.auth.get_supported_hash('SHA256'), sha256)
        self.assertEqual(dc_sdk.lib.auth.get_supported_hash('BLAKE2b512'), blake2b)
        self.assertEqual(dc_sdk.lib.auth.get_supported_hash('SHA3-256'), sha3_256)
        self.assertRaises(NotImplementedError, dc_sdk.lib.auth.get_supported_hash, 'INVALID')
        self.assertRaises(NotImplementedError, dc_sdk.lib.auth.hash_input, 99999, 'some input')

    def test_bytes_from_input(self):
        self.assertRaises(ValueError, dc_sdk.lib.auth.bytes_from_input, 1234)
        self.assertRaises(ValueError, dc_sdk.lib.auth.bytes_from_input, "\ud83d")
        self.assertEqual(dc_sdk.lib.auth.bytes_from_input(b'stuff'), b'stuff')
        self.assertEqual(dc_sdk.lib.auth.bytes_from_input('stuff'), b'stuff')

    def test_b64_string(self):
        self.assertRaises(ValueError, dc_sdk.lib.auth.bytes_to_b64_str, 'not bytes')
        self.assertEqual(dc_sdk.lib.auth.bytes_to_b64_str(b'stuff'), 'c3R1ZmY=')
        self.assertEqual(dc_sdk.lib.auth.base64_encode_input('stuff'), 'c3R1ZmY=')

    def test_hashing(self):
        self.assertEqual(dc_sdk.lib.auth.hash_input(sha256, 'some input'), b'+\xe3[\xc6q\xdc\x91.\x7fT\x0f\x0eZ.\x91^\xf6\xa4\xa4\xdb\xd2\xad\xa5\xba\x9c\x1d+\x11{\xfc\x90|')
        self.assertEqual(dc_sdk.lib.auth.hash_input(sha3_256, 'some input'), b'\x18\xd6@c\x0b\xbe\xc8`\xdb@t\x1e\xf2\xd65g\xe2Z\x04\x90\xac\xc3\x9f\xf1\xceC\xee\xde\xf4\xb1\xe7x')
        self.assertEqual(dc_sdk.lib.auth.hash_input(blake2b, 'some input'), b'k\xd3_\x97J/\x0e\x93_\xa1\x15(\xbf"\xab\xb5\xb6\x9f\x9d\xee8\xed\xf6\xc2RX\xea<\xb4\xee\x03:|a@\xd8\x9f\xab\xa6\x06\x89r\x8fa-]\xf7\xda\xb9=\xa7\xd0z\xe6XB\xae$\xd0\x1fP\xa2+\xa9')

    def test_hmac_operations(self):
        secret = '12345'
        message = 'message'
        encoded_hmac = dc_sdk.lib.auth.bytes_to_b64_str(dc_sdk.lib.auth.create_hmac(blake2b, secret, message))
        self.assertTrue(dc_sdk.lib.auth.compare_hmac(blake2b, encoded_hmac, secret, message))
        self.assertEqual(encoded_hmac, 'jMErAWFbeKCDRPGFhxCL+xYsjYP4SDIUXlDpXhmQ9VZ4jCIMFzQ1ksnR7hf+pkcr56QY8Hm16sTTv+g29jRXew==')
        encoded_hmac = dc_sdk.lib.auth.bytes_to_b64_str(dc_sdk.lib.auth.create_hmac(sha256, secret, message))
        self.assertTrue(dc_sdk.lib.auth.compare_hmac(sha256, encoded_hmac, secret, message))
        self.assertEqual(encoded_hmac, 'aaIguQeFQUkVBw64VUJQWmzzIweD5zf+NVpuwfwexBA=')
        encoded_hmac = dc_sdk.lib.auth.bytes_to_b64_str(dc_sdk.lib.auth.create_hmac(sha3_256, secret, message))
        self.assertTrue(dc_sdk.lib.auth.compare_hmac(sha3_256, encoded_hmac, secret, message))
        self.assertEqual(encoded_hmac, 'EhPxZsdSWbv6ekuJvXv+nPIPdaZVdOIxXXLfvOvJlSw=')

    def test_authorization_header(self):
        kwargs = {
            'auth_key_id': 'id',
            'auth_key': 'key',
            'http_verb': 'get',
            'full_path': '/chain/transaction',
            'dcid': 'a dragonchain id',
            'timestamp': '2017-06-10T20:40:05.191023Z',
            'content_type': '',
            'content': '',
            'algorithm': 'SHA256'
        }
        self.assertEqual(dc_sdk.lib.auth.get_authorization(**kwargs), 'DC1-HMAC-SHA256 id:vQ0tR2yCHE9/U9aN3Cs2fXtDcgbSew0RQrPx313+nxU=')
        kwargs['algorithm'] = 'BLAKE2b512'
        self.assertEqual(dc_sdk.lib.auth.get_authorization(**kwargs), 'DC1-HMAC-BLAKE2b512 id:D5KcsMTiyblQOMmA0m3dxqnjJMVjMbmMGGNLCZedKRF6PU6TrjsQ2fatELpXKkzsNHic5T7twGjY/b1ryvH6Jg==')
        kwargs['algorithm'] = 'SHA3-256'
        self.assertEqual(dc_sdk.lib.auth.get_authorization(**kwargs), 'DC1-HMAC-SHA3-256 id:R9v3eH9iIgXUWICukGAlD8GNqOjQrm3/IUwQl1wMVqw=')
