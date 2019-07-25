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

import sys
import time
import unittest

import jsonschema

from tests.integration import schema
import dragonchain_sdk

CREATED_API_KEY_ID = None
CREATED_API_KEY_TIME = None
NICKNAME_CREATED_API_KEY_ID = None
NICKNAME_CREATED_API_KEY_TIME = None
NICKNAME = "test1"


class TestApiKeys(unittest.TestCase):
    def setUp(self):
        self.client = dragonchain_sdk.create_client()

    # CREATE #

    def test_create_api_key(self):
        response = self.client.create_api_key()
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 201, response)
        global CREATED_API_KEY_ID
        global CREATED_API_KEY_TIME
        CREATED_API_KEY_ID = response.get("response").get("id")
        CREATED_API_KEY_TIME = response.get("response").get("registration_time")
        jsonschema.validate(response.get("response"), schema.api_key_create_schema)

    def test_create_api_key_with_nickname(self):
        response = self.client.create_api_key(NICKNAME)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 201, response)
        global NICKNAME_CREATED_API_KEY_ID
        global NICKNAME_CREATED_API_KEY_TIME
        NICKNAME_CREATED_API_KEY_ID = response.get("response").get("id")
        NICKNAME_CREATED_API_KEY_TIME = response.get("response").get("registration_time")
        jsonschema.validate(response.get("response"), schema.api_key_create_schema)
        self.assertEqual(response["response"].get("nickname"), NICKNAME)

    # GET #

    def test_get_existing_api_key_without_nickname(self):
        response = self.client.get_api_key(CREATED_API_KEY_ID)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        expected_dict = {"id": CREATED_API_KEY_ID, "registration_time": CREATED_API_KEY_TIME, "nickname": ""}
        self.assertEqual(response.get("response"), expected_dict)

    def test_get_existing_api_key_with_nickname(self):
        response = self.client.get_api_key(NICKNAME_CREATED_API_KEY_ID)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        expected_dict = {"id": NICKNAME_CREATED_API_KEY_ID, "registration_time": NICKNAME_CREATED_API_KEY_TIME, "nickname": NICKNAME}
        self.assertEqual(response.get("response"), expected_dict)

    def test_get_non_existing_api_key(self):
        response = self.client.get_api_key("BOGUSAPIKEY")
        self.assertFalse(response.get("ok"), response)
        self.assertEqual(response.get("status"), 404, response)
        expected_dict = {"error": {"type": "NOT_FOUND", "details": "The requested resource(s) cannot be found."}}
        self.assertEqual(response.get("response"), expected_dict)

    # LIST #

    def test_list_api_key(self):
        response = self.client.list_api_keys()
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.api_key_list_schema)
        # Check that our earlier created api key is in the output
        self.assertIn({"id": CREATED_API_KEY_ID, "registration_time": CREATED_API_KEY_TIME, "nickname": ""}, response["response"]["keys"], response)
        self.assertIn(
            {"id": NICKNAME_CREATED_API_KEY_ID, "registration_time": NICKNAME_CREATED_API_KEY_TIME, "nickname": NICKNAME},
            response["response"]["keys"],
            response,
        )

    # UPDATE #

    def test_update_api_key_without_nickname(self):
        response = self.client.update_api_key(CREATED_API_KEY_ID, "test2")
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)

        # Verify the new nickname was saved by getting it
        response2 = self.client.get_api_key(CREATED_API_KEY_ID)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        expected_dict = {"id": CREATED_API_KEY_ID, "registration_time": CREATED_API_KEY_TIME, "nickname": "test2"}
        self.assertEqual(response2.get("response"), expected_dict)

    def test_update_api_key_with_nickname(self):
        response = self.client.update_api_key(NICKNAME_CREATED_API_KEY_ID, "test3")
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)

        # Verify the new nickname was saved by getting it
        response2 = self.client.get_api_key(NICKNAME_CREATED_API_KEY_ID)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        expected_dict = {"id": NICKNAME_CREATED_API_KEY_ID, "registration_time": NICKNAME_CREATED_API_KEY_TIME, "nickname": "test3"}
        self.assertEqual(response2.get("response"), expected_dict)

    # DELETE #

    def test_delete_existing_api_key(self):
        response1 = self.client.delete_api_key(CREATED_API_KEY_ID)
        self.assertTrue(response1.get("ok"), response1)
        self.assertEqual(response1.get("status"), 200, response1)
        self.assertEqual(response1.get("response"), {"success": True})

        # Check that we can't get the api key we deleted any more (wait for delete consistency)
        time.sleep(1)
        response2 = self.client.get_api_key(CREATED_API_KEY_ID)
        self.assertFalse(response2.get("ok"), response2)
        self.assertEqual(response2.get("status"), 404, response2)

    def test_delete_nonexisting_api_key(self):
        response = self.client.delete_api_key("BOGUSAPIKEY")
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        self.assertEqual(response.get("response"), {"success": True})

    def api_key_cleanup(self):
        try:
            self.client.delete_api_key(CREATED_API_KEY_ID)
        except Exception:
            pass
        try:
            self.client.delete_api_key(NICKNAME_CREATED_API_KEY_ID)
        except Exception:
            pass


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestApiKeys("test_create_api_key"))
    suite.addTest(TestApiKeys("test_create_api_key_with_nickname"))
    suite.addTest(TestApiKeys("test_get_existing_api_key_without_nickname"))
    suite.addTest(TestApiKeys("test_get_existing_api_key_with_nickname"))
    suite.addTest(TestApiKeys("test_get_non_existing_api_key"))
    suite.addTest(TestApiKeys("test_list_api_key"))
    suite.addTest(TestApiKeys("test_update_api_key_without_nickname"))
    suite.addTest(TestApiKeys("test_update_api_key_with_nickname"))
    suite.addTest(TestApiKeys("test_delete_existing_api_key"))
    suite.addTest(TestApiKeys("test_delete_nonexisting_api_key"))
    suite.addTest(TestApiKeys("api_key_cleanup"))
    return suite


if __name__ == "__main__":
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite())
    sys.exit(0 if result.wasSuccessful() else 1)
