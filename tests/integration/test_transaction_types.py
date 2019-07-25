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
import unittest
import time

import jsonschema

import dragonchain_sdk
from tests.integration import schema


NO_INDEX_TYPE_NAME = "banana-pasta"
WITH_INDEX_TYPE_NAME = "banana-butter"
SMART_CONTRACT_NAME = "bacon-sauce"
SMART_CONTRACT_ID = None
CUSTOM_INDEXES1 = [{"key": "myKey", "path": "jsonPath"}]
CUSTOM_INDEXES2 = [{"key": "newKey", "path": "something"}]

_expected_not_found_response = {
    "status": 404,
    "ok": False,
    "response": {"error": {"type": "NOT_FOUND", "details": "The requested resource(s) cannot be found."}},
}
_expected_successful_response = {"status": 200, "ok": True, "response": {"success": True}}


class TestTransactionTypes(unittest.TestCase):
    def setUp(self):
        self.client = dragonchain_sdk.create_client()

    # CREATE #

    def test_create_transaction_type_without_indexes(self):
        response = self.client.create_transaction_type(NO_INDEX_TYPE_NAME)
        self.assertEqual(_expected_successful_response, response)

    def test_create_transaction_type_with_indexes(self):
        response = self.client.create_transaction_type(WITH_INDEX_TYPE_NAME, CUSTOM_INDEXES1)
        self.assertEqual(_expected_successful_response, response)

    def test_create_transaction_type_that_already_exists_fails(self):
        response = self.client.create_transaction_type(NO_INDEX_TYPE_NAME)
        expected_response = {
            "status": 409,
            "ok": False,
            "response": {"error": {"type": "TRANSACTION_TYPE_CONFLICT", "details": "The transaction type you are trying to register already exists"}},
        }
        self.assertEqual(expected_response, response)

    # GET #

    def test_get_transaction_type_with_smart_contract(self):
        # First we need to create a smart contract for the transaction type
        response1 = self.client.create_smart_contract(SMART_CONTRACT_NAME, "alpine:latest", "echo", ["hello"])
        global SMART_CONTRACT_ID
        SMART_CONTRACT_ID = response1["response"]["id"]
        # Now check that we can get the transaction type
        response2 = self.client.get_transaction_type(SMART_CONTRACT_NAME)
        expected_response = {
            "status": 200,
            "ok": True,
            "response": {"version": "1", "txn_type": SMART_CONTRACT_NAME, "custom_indexes": [], "contract_id": SMART_CONTRACT_ID},
        }
        self.assertEqual(expected_response, response2)

    def test_get_transaction_type_without_indexes(self):
        response = self.client.get_transaction_type(NO_INDEX_TYPE_NAME)
        expected_response = {
            "status": 200,
            "ok": True,
            "response": {"version": "1", "txn_type": NO_INDEX_TYPE_NAME, "custom_indexes": [], "contract_id": False},
        }
        self.assertEqual(expected_response, response)

    def test_get_transaction_type_with_indexes(self):
        response = self.client.get_transaction_type(WITH_INDEX_TYPE_NAME)
        expected_response = {
            "status": 200,
            "ok": True,
            "response": {"version": "1", "txn_type": WITH_INDEX_TYPE_NAME, "custom_indexes": CUSTOM_INDEXES1, "contract_id": False},
        }
        self.assertEqual(expected_response, response)

    def test_get_nonexisting_transaction_type_fails_not_found(self):
        response = self.client.get_transaction_type("doesntExist")
        self.assertEqual(_expected_not_found_response, response)

    # UPDATE #

    def test_update_transaction_type_with_smart_contract(self):
        response1 = self.client.update_transaction_type(SMART_CONTRACT_NAME, CUSTOM_INDEXES1)
        expected_response1 = {"status": 200, "ok": True, "response": {"success": True}}
        self.assertEqual(expected_response1, response1)
        # Check that our updated type only has our new indexes as intended
        response2 = self.client.get_transaction_type(SMART_CONTRACT_NAME)
        expected_response2 = {
            "status": 200,
            "ok": True,
            "response": {"version": "1", "txn_type": SMART_CONTRACT_NAME, "custom_indexes": CUSTOM_INDEXES1, "contract_id": SMART_CONTRACT_ID},
        }
        self.assertEqual(expected_response2, response2)

    def test_update_transaction_type_with_indexes(self):
        response1 = self.client.update_transaction_type(WITH_INDEX_TYPE_NAME, CUSTOM_INDEXES2)
        expected_response1 = {"status": 200, "ok": True, "response": {"success": True}}
        self.assertEqual(expected_response1, response1)
        # Check that our updated type only has our new indexes as intended
        response2 = self.client.get_transaction_type(WITH_INDEX_TYPE_NAME)
        expected_response2 = {
            "status": 200,
            "ok": True,
            "response": {"version": "1", "txn_type": WITH_INDEX_TYPE_NAME, "custom_indexes": CUSTOM_INDEXES2, "contract_id": False},
        }
        self.assertEqual(expected_response2, response2)

    def test_update_transaction_type_without_indexes(self):
        response1 = self.client.update_transaction_type(NO_INDEX_TYPE_NAME, CUSTOM_INDEXES2)
        expected_response1 = {"status": 200, "ok": True, "response": {"success": True}}
        self.assertEqual(expected_response1, response1)
        # Check that our updated type only has our new indexes as intended
        response2 = self.client.get_transaction_type(NO_INDEX_TYPE_NAME)
        expected_response2 = {
            "status": 200,
            "ok": True,
            "response": {"version": "1", "txn_type": NO_INDEX_TYPE_NAME, "custom_indexes": CUSTOM_INDEXES2, "contract_id": False},
        }
        self.assertEqual(expected_response2, response2)

    def test_update_transaction_type_can_remove_existing_indexes(self):
        response1 = self.client.update_transaction_type(NO_INDEX_TYPE_NAME, [])
        expected_response1 = {"status": 200, "ok": True, "response": {"success": True}}
        self.assertEqual(expected_response1, response1)
        # Check that our updated type only has no custom indexes anymore
        response2 = self.client.get_transaction_type(NO_INDEX_TYPE_NAME)
        expected_response2 = {
            "status": 200,
            "ok": True,
            "response": {"version": "1", "txn_type": NO_INDEX_TYPE_NAME, "custom_indexes": [], "contract_id": False},
        }
        self.assertEqual(expected_response2, response2)

    def test_update_nonexisting_transaction_type_fails(self):
        response = self.client.update_transaction_type("thisdoesntexist", [])
        self.assertEqual(_expected_not_found_response, response)

    # LIST #

    def test_list_transaction_types(self):
        response = self.client.list_transaction_types()
        jsonschema.validate(response.get("response"), schema.list_transaction_type_schema)
        expected1 = {"version": "1", "txn_type": NO_INDEX_TYPE_NAME, "custom_indexes": [], "contract_id": False}
        expected2 = {"version": "1", "txn_type": WITH_INDEX_TYPE_NAME, "custom_indexes": CUSTOM_INDEXES2, "contract_id": False}
        expected3 = {"version": "1", "txn_type": SMART_CONTRACT_NAME, "custom_indexes": CUSTOM_INDEXES1, "contract_id": SMART_CONTRACT_ID}
        self.assertIn(expected1, response["response"]["transaction_types"], response)
        self.assertIn(expected2, response["response"]["transaction_types"], response)
        self.assertIn(expected3, response["response"]["transaction_types"], response)

    # DELETE #

    def test_delete_transaction_type_with_smart_contract_fails(self):
        response = self.client.delete_transaction_type(SMART_CONTRACT_NAME)
        expected_response = {
            "status": 403,
            "ok": False,
            "response": {"error": {"type": "ACTION_FORBIDDEN", "details": "Cannot delete smart contract transaction type"}},
        }
        self.assertEqual(expected_response, response)

    def test_delete_smart_contract_removes_transaction_type(self):
        time.sleep(15)
        self.client.delete_smart_contract(SMART_CONTRACT_ID)
        time.sleep(10)
        # Check that we can't get the transaction type that we just delete (expect 404)
        response = self.client.get_transaction_type(SMART_CONTRACT_NAME)
        self.assertEqual(_expected_not_found_response, response)

    def test_delete_transaction_type_without_index(self):
        response1 = self.client.delete_transaction_type(NO_INDEX_TYPE_NAME)
        self.assertEqual(_expected_successful_response, response1)
        # Check that we can't get the transaction type that we just delete (expect 404)
        response2 = self.client.get_transaction_type(NO_INDEX_TYPE_NAME)
        self.assertEqual(_expected_not_found_response, response2)

    def test_delete_transaction_type_with_index(self):
        response1 = self.client.delete_transaction_type(WITH_INDEX_TYPE_NAME)
        self.assertEqual(_expected_successful_response, response1)
        # Check that we can't get the transaction type that we just delete (expect 404)
        response2 = self.client.get_transaction_type(WITH_INDEX_TYPE_NAME)
        self.assertEqual(_expected_not_found_response, response2)

    def test_delete_nonexisting_transaction_type(self):
        response = self.client.delete_transaction_type("somethingthatdoesntexist")
        # Deleting a transaction type that doesn't exist still returns successful
        self.assertEqual(_expected_successful_response, response)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestTransactionTypes("test_create_transaction_type_without_indexes"))
    suite.addTest(TestTransactionTypes("test_create_transaction_type_with_indexes"))
    suite.addTest(TestTransactionTypes("test_create_transaction_type_that_already_exists_fails"))
    suite.addTest(TestTransactionTypes("test_get_transaction_type_with_smart_contract"))
    suite.addTest(TestTransactionTypes("test_get_transaction_type_without_indexes"))
    suite.addTest(TestTransactionTypes("test_get_transaction_type_with_indexes"))
    suite.addTest(TestTransactionTypes("test_get_nonexisting_transaction_type_fails_not_found"))
    suite.addTest(TestTransactionTypes("test_update_transaction_type_with_smart_contract"))
    suite.addTest(TestTransactionTypes("test_update_transaction_type_with_indexes"))
    suite.addTest(TestTransactionTypes("test_update_transaction_type_without_indexes"))
    suite.addTest(TestTransactionTypes("test_update_transaction_type_can_remove_existing_indexes"))
    suite.addTest(TestTransactionTypes("test_update_nonexisting_transaction_type_fails"))
    suite.addTest(TestTransactionTypes("test_list_transaction_types"))
    suite.addTest(TestTransactionTypes("test_delete_transaction_type_with_smart_contract_fails"))
    suite.addTest(TestTransactionTypes("test_delete_smart_contract_removes_transaction_type"))
    suite.addTest(TestTransactionTypes("test_delete_transaction_type_without_index"))
    suite.addTest(TestTransactionTypes("test_delete_transaction_type_with_index"))
    suite.addTest(TestTransactionTypes("test_delete_nonexisting_transaction_type"))
    return suite


if __name__ == "__main__":
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite())
    sys.exit(0 if result.wasSuccessful() else 1)
