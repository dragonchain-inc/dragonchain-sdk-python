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

TEST_TXN_TYPE = "testingType1"
EMPTY_STRING_TXN_ID = None
EMTPY_OBJECT_TXN_ID = None
STRING_CONTENT = "some content"
STRING_CONTENT_TXN_ID = None
OBJECT_CONTENT = {"something": "cool", "array": ["things", True], "number": 4.5}
OBJECT_CONTENT_TXN_ID = None
TAG_TXN_ID = None
TAG_CONTENT = "someTag"
BULK_TXN_ID = None
BULK_TXN_CONTENT = "valid txn"


class TestTransactions(unittest.TestCase):
    def setUp(self):
        self.client = dragonchain_sdk.create_client()

    def set_up_transaction_types(self):
        try:
            self.client.create_transaction_type(TEST_TXN_TYPE)
        except Exception:
            pass

    # CREATE #

    def test_create_transaction_with_empty_string_payload(self):
        response = self.client.create_transaction(transaction_type=TEST_TXN_TYPE, payload="")
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 201, response)
        jsonschema.validate(response.get("response"), schema.create_transaction_schema)
        global EMPTY_STRING_TXN_ID
        EMPTY_STRING_TXN_ID = response["response"]["transaction_id"]

    def test_create_transaction_with_nonempty_string_payload(self):
        response = self.client.create_transaction(transaction_type=TEST_TXN_TYPE, payload=STRING_CONTENT)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 201, response)
        jsonschema.validate(response.get("response"), schema.create_transaction_schema)
        global STRING_CONTENT_TXN_ID
        STRING_CONTENT_TXN_ID = response["response"]["transaction_id"]

    def test_create_transaction_with_empty_object_payload(self):
        response = self.client.create_transaction(transaction_type=TEST_TXN_TYPE, payload={})
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 201, response)
        jsonschema.validate(response.get("response"), schema.create_transaction_schema)
        global EMTPY_OBJECT_TXN_ID
        EMTPY_OBJECT_TXN_ID = response["response"]["transaction_id"]

    def test_create_transaction_with_nonempty_object_payload(self):
        response = self.client.create_transaction(transaction_type=TEST_TXN_TYPE, payload=OBJECT_CONTENT)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 201, response)
        jsonschema.validate(response.get("response"), schema.create_transaction_schema)
        global OBJECT_CONTENT_TXN_ID
        OBJECT_CONTENT_TXN_ID = response["response"]["transaction_id"]

    def test_create_transaction_with_tag(self):
        response = self.client.create_transaction(transaction_type=TEST_TXN_TYPE, payload="", tag=TAG_CONTENT)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 201, response)
        jsonschema.validate(response.get("response"), schema.create_transaction_schema)
        global TAG_TXN_ID
        TAG_TXN_ID = response["response"]["transaction_id"]

    def test_create_transaction_with_callback(self):
        # For this test, just check that the server accepts the callback url, but don't verify it actually calls back since
        # we aren't running any webserver which could recieve the callback
        response = self.client.create_transaction(transaction_type=TEST_TXN_TYPE, payload="", callback_url="http://fakeurl")
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 201, response)
        jsonschema.validate(response.get("response"), schema.create_transaction_schema)

    def test_create_transaction_fails_without_transaction_type(self):
        response = self.client.create_transaction(transaction_type="doesnotexist", payload="")
        expected_response = {
            "status": 403,
            "ok": False,
            "response": {
                "error": {
                    "type": "INVALID_TRANSACTION_TYPE",
                    "details": "The transaction type you are attempting to use either does not exist or is invalid.",
                }
            },
        }
        self.assertEqual(expected_response, response)

    def test_create_bulk_transactions_with_all_valid_transactions(self):
        response = self.client.create_bulk_transaction(
            [
                {"transaction_type": TEST_TXN_TYPE, "payload": "thing"},
                {"transaction_type": TEST_TXN_TYPE, "payload": {"object": "thing"}},
                {"transaction_type": TEST_TXN_TYPE, "payload": "", "tag": "a tag"},
            ]
        )
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 207, response)
        jsonschema.validate(response.get("response"), schema.bulk_create_transaction_schema)
        # Ensure the correct amount of transactions were posted successfully
        self.assertEqual(len(response["response"]["400"]), 0)
        self.assertEqual(len(response["response"]["201"]), 3)

    def test_create_bulk_transactions_with_some_nonexisting_transaction_types(self):
        response = self.client.create_bulk_transaction(
            [
                {"transaction_type": TEST_TXN_TYPE, "payload": BULK_TXN_CONTENT},
                {"transaction_type": "thisdoesntexist", "payload": "invalid txn", "tag": "thing"},
            ]
        )
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 207, response)
        jsonschema.validate(response.get("response"), schema.bulk_create_transaction_schema)
        # Ensure the correct amount of transactions were posted successfully
        self.assertEqual(len(response["response"]["201"]), 1)
        self.assertEqual(response["response"]["400"], [{"version": "1", "txn_type": "thisdoesntexist", "payload": "invalid txn", "tag": "thing"}])
        # Save the valid transaction id to check for later
        global BULK_TXN_ID
        BULK_TXN_ID = response["response"]["201"][0]

    def test_create_bulk_transactions_with_some_invalid_transactions(self):
        response = self.client.create_bulk_transaction(
            [
                {"transaction_type": TEST_TXN_TYPE, "payload": "valid txn"},
                {"invalid": "transaction"},
                {"typo_type": "whoops", "payload": "", "tag": "a tag"},
            ]
        )
        self.assertFalse(response.get("ok"), response)
        self.assertEqual(response.get("status"), 400, response)
        self.assertEqual(response["response"]["error"]["type"], "VALIDATION_ERROR", response)

    def test_create_bulk_transactions_with_all_nonexistant_transaction_types(self):
        response = self.client.create_bulk_transaction(
            [
                {"transaction_type": "thisdoesntexist", "payload": {"hello": "thing"}},
                {"transaction_type": "thisalsodoesntexist", "payload": "invalid txn", "tag": "thing"},
            ]
        )
        expected_response = {
            "status": 400,
            "ok": False,
            "response": {
                "201": [],
                "400": [
                    {"version": "1", "txn_type": "thisdoesntexist", "payload": {"hello": "thing"}},
                    {"version": "1", "txn_type": "thisalsodoesntexist", "payload": "invalid txn", "tag": "thing"},
                ],
            },
        }
        self.assertEqual(expected_response, response)

    def test_create_bulk_transactions_with_all_invalid_transactions(self):
        response = self.client.create_bulk_transaction([{"thisschema": "isnotcorrect"}, {}])
        self.assertFalse(response.get("ok"), response)
        self.assertEqual(response.get("status"), 400, response)
        self.assertEqual(response["response"]["error"]["type"], "VALIDATION_ERROR", response)

    def wait_for_blocks(self):
        time.sleep(15)

    # GET #

    def test_get_transaction_with_empty_string_payload(self):
        response = self.client.get_transaction(EMPTY_STRING_TXN_ID)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.get_transaction_schema)
        # Check various fields on the retrieved object
        self.assertEqual(EMPTY_STRING_TXN_ID, response["response"]["header"]["txn_id"], response)
        self.assertEqual(TEST_TXN_TYPE, response["response"]["header"]["txn_type"], response)
        self.assertEqual("", response["response"]["payload"], response)

    def test_get_transaction_with_nonempty_string_payload(self):
        response = self.client.get_transaction(STRING_CONTENT_TXN_ID)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.get_transaction_schema)
        # Check various fields on the retrieved object
        self.assertEqual(STRING_CONTENT_TXN_ID, response["response"]["header"]["txn_id"], response)
        self.assertEqual(TEST_TXN_TYPE, response["response"]["header"]["txn_type"], response)
        self.assertEqual(STRING_CONTENT, response["response"]["payload"], response)

    def test_get_transaction_with_empty_object_payload(self):
        response = self.client.get_transaction(EMTPY_OBJECT_TXN_ID)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.get_transaction_schema)
        # Check various fields on the retrieved object
        self.assertEqual(EMTPY_OBJECT_TXN_ID, response["response"]["header"]["txn_id"], response)
        self.assertEqual(TEST_TXN_TYPE, response["response"]["header"]["txn_type"], response)
        self.assertEqual({}, response["response"]["payload"], response)

    def test_get_transaction_with_nonempty_object_payload(self):
        response = self.client.get_transaction(OBJECT_CONTENT_TXN_ID)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.get_transaction_schema)
        # Check various fields on the retrieved object
        self.assertEqual(OBJECT_CONTENT_TXN_ID, response["response"]["header"]["txn_id"], response)
        self.assertEqual(TEST_TXN_TYPE, response["response"]["header"]["txn_type"], response)
        self.assertEqual(OBJECT_CONTENT, response["response"]["payload"], response)

    def test_get_transaction_with_tag(self):
        response = self.client.get_transaction(TAG_TXN_ID)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.get_transaction_schema)
        # Check various fields on the retrieved object
        self.assertEqual(TAG_TXN_ID, response["response"]["header"]["txn_id"], response)
        self.assertEqual(TEST_TXN_TYPE, response["response"]["header"]["txn_type"], response)
        self.assertEqual(TAG_CONTENT, response["response"]["header"]["tag"], response)

    def test_get_transaction_from_bulk_submission(self):
        response = self.client.get_transaction(BULK_TXN_ID)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.get_transaction_schema)
        # Check various fields on the retrieved object
        self.assertEqual(BULK_TXN_ID, response["response"]["header"]["txn_id"], response)
        self.assertEqual(TEST_TXN_TYPE, response["response"]["header"]["txn_type"], response)
        self.assertEqual(BULK_TXN_CONTENT, response["response"]["payload"], response)

    def test_get_transaction_fails_with_bad_id(self):
        response = self.client.get_transaction("not_real_id")
        expected_response = {
            "status": 404,
            "ok": False,
            "response": {"error": {"type": "NOT_FOUND", "details": "The requested resource(s) cannot be found."}},
        }
        self.assertEqual(expected_response, response)

    # QUERY #

    def test_query_transactions_works_with_no_parameters(self):
        response = self.client.query_transactions()
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.query_transaction_schema)

    def test_query_transactions_works_with_limit(self):
        response = self.client.query_transactions(limit=2)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.query_transaction_schema)
        self.assertEqual(2, len(response["response"]["results"]))

    def test_query_transactions_works_with_offset(self):
        # We'll check that these results give valid responses and aren't identical
        response1 = self.client.query_transactions(offset=0, limit=1)
        response2 = self.client.query_transactions(offset=3, limit=1)
        self.assertTrue(response1.get("ok"), response1)
        self.assertEqual(response1.get("status"), 200, response1)
        jsonschema.validate(response1.get("response"), schema.query_transaction_schema)
        self.assertTrue(response2.get("ok"), response2)
        self.assertEqual(response2.get("status"), 200, response2)
        jsonschema.validate(response2.get("response"), schema.query_transaction_schema)
        self.assertNotEqual(response1["response"]["results"], response2["response"]["results"])

    def test_query_transactions_with_sorting(self):
        response1 = self.client.query_transactions(sort="timestamp:desc", limit=5)
        response2 = self.client.query_transactions(sort="block_id:desc", limit=5)
        self.assertTrue(response1.get("ok"), response1)
        self.assertEqual(response1.get("status"), 200, response1)
        jsonschema.validate(response1.get("response"), schema.query_transaction_schema)
        self.assertTrue(response2.get("ok"), response2)
        self.assertEqual(response2.get("status"), 200, response2)
        jsonschema.validate(response2.get("response"), schema.query_transaction_schema)
        timestamp_list = []
        block_id_list = []
        for transaction in response1["response"]["results"]:
            timestamp_list.append(transaction["header"]["timestamp"])
        for transaction in response2["response"]["results"]:
            block_id_list.append(transaction["header"]["block_id"])
        # Ensure our sorting worked by checking that the timestamps and block_ids are in ascending ascending order (sorted)
        self.assertEqual(timestamp_list, sorted(timestamp_list)[::-1])
        self.assertEqual(block_id_list, sorted(block_id_list)[::-1])

    def test_query_transactions_with_lucene_query(self):
        response = self.client.query_transactions(lucene_query='tag:"{}"'.format(TAG_CONTENT))
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.query_transaction_schema)
        # Make sure we got results
        self.assertGreater(len(response["response"]["results"]), 0)
        for transaction in response["response"]["results"]:
            # Check that it's the correct result
            self.assertEqual(TAG_CONTENT, transaction["header"]["tag"], transaction)

    def test_query_transactions_with_no_result_lucene_query(self):
        response = self.client.query_transactions(lucene_query='tag:"thisdoesntexistinatag"')
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.query_transaction_schema)
        self.assertEqual(0, response["response"]["total"])
        # Make sure we got exactly 0 result
        self.assertEqual(len(response["response"]["results"]), 0)

    # TODO: Add more robust lucene query checking

    # TODO: Add tests for bad queries

    def clean_up_transaction_types(self):
        self.client.delete_transaction_type(TEST_TXN_TYPE)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestTransactions("set_up_transaction_types"))
    suite.addTest(TestTransactions("test_create_transaction_with_empty_string_payload"))
    suite.addTest(TestTransactions("test_create_transaction_with_nonempty_string_payload"))
    suite.addTest(TestTransactions("test_create_transaction_with_empty_object_payload"))
    suite.addTest(TestTransactions("test_create_transaction_with_nonempty_object_payload"))
    suite.addTest(TestTransactions("test_create_transaction_with_tag"))
    suite.addTest(TestTransactions("test_create_transaction_with_callback"))
    suite.addTest(TestTransactions("test_create_transaction_fails_without_transaction_type"))
    suite.addTest(TestTransactions("test_create_bulk_transactions_with_all_valid_transactions"))
    suite.addTest(TestTransactions("test_create_bulk_transactions_with_some_nonexisting_transaction_types"))
    suite.addTest(TestTransactions("test_create_bulk_transactions_with_some_invalid_transactions"))
    suite.addTest(TestTransactions("test_create_bulk_transactions_with_all_nonexistant_transaction_types"))
    suite.addTest(TestTransactions("test_create_bulk_transactions_with_all_invalid_transactions"))
    suite.addTest(TestTransactions("wait_for_blocks"))
    suite.addTest(TestTransactions("test_get_transaction_with_empty_string_payload"))
    suite.addTest(TestTransactions("test_get_transaction_with_nonempty_string_payload"))
    suite.addTest(TestTransactions("test_get_transaction_with_empty_object_payload"))
    suite.addTest(TestTransactions("test_get_transaction_with_nonempty_object_payload"))
    suite.addTest(TestTransactions("test_get_transaction_with_tag"))
    suite.addTest(TestTransactions("test_get_transaction_from_bulk_submission"))
    suite.addTest(TestTransactions("test_get_transaction_fails_with_bad_id"))
    suite.addTest(TestTransactions("test_query_transactions_works_with_no_parameters"))
    suite.addTest(TestTransactions("test_query_transactions_works_with_limit"))
    suite.addTest(TestTransactions("test_query_transactions_works_with_offset"))
    suite.addTest(TestTransactions("test_query_transactions_with_sorting"))
    suite.addTest(TestTransactions("test_query_transactions_with_lucene_query"))
    suite.addTest(TestTransactions("test_query_transactions_with_no_result_lucene_query"))
    suite.addTest(TestTransactions("clean_up_transaction_types"))
    return suite


if __name__ == "__main__":
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite())
    sys.exit(0 if result.wasSuccessful() else 1)
