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

TEST_TRANSACTION_TYPE = "test-blocks"
EXISTING_BLOCK = None


class TestBlocks(unittest.TestCase):
    def setUp(self):
        self.client = dragonchain_sdk.create_client()

    def test_block_set_up(self):
        # We need to post some transactions so a block will be created
        self.client.create_transaction_type(TEST_TRANSACTION_TYPE)
        global TEST_TXN_ID_1
        global TEST_TXN_ID_2
        self.client.create_transaction(TEST_TRANSACTION_TYPE, "string payload", tag="tagging")
        self.client.create_transaction(TEST_TRANSACTION_TYPE, {"object": "payload"})
        time.sleep(10)

    # QUERY #

    def test_query_blocks_works_with_no_parameters(self):
        response = self.client.query_blocks()
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.query_block_schema)
        global EXISTING_BLOCK
        EXISTING_BLOCK = response["response"]["results"][0]

    def test_query_blocks_works_with_limit(self):
        response = self.client.query_blocks(limit=2)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.query_block_schema)
        self.assertEqual(2, len(response["response"]["results"]))

    def test_query_blocks_works_with_offset(self):
        # We'll check that these results give valid responses and aren't identical
        response1 = self.client.query_blocks(offset=0, limit=1)
        response2 = self.client.query_blocks(offset=2, limit=1)
        self.assertTrue(response1.get("ok"), response1)
        self.assertEqual(response1.get("status"), 200, response1)
        jsonschema.validate(response1.get("response"), schema.query_block_schema)
        self.assertTrue(response2.get("ok"), response2)
        self.assertEqual(response2.get("status"), 200, response2)
        jsonschema.validate(response2.get("response"), schema.query_block_schema)
        self.assertNotEqual(response1["response"]["results"], response2["response"]["results"])

    def test_query_blocks_works_with_sorting(self):
        response1 = self.client.query_blocks(sort="timestamp:desc", limit=5)
        response2 = self.client.query_blocks(sort="block_id:desc", limit=5)
        self.assertTrue(response1.get("ok"), response1)
        self.assertEqual(response1.get("status"), 200, response1)
        jsonschema.validate(response1.get("response"), schema.query_block_schema)
        self.assertTrue(response2.get("ok"), response2)
        self.assertEqual(response2.get("status"), 200, response2)
        jsonschema.validate(response2.get("response"), schema.query_block_schema)
        timestamp_list = []
        block_id_list = []
        for block in response1["response"]["results"]:
            timestamp_list.append(block["header"]["timestamp"])
        for block in response2["response"]["results"]:
            block_id_list.append(block["header"]["block_id"])
        # Ensure our sorting worked by checking that the timestamps and block_ids are in ascending ascending order (sorted)
        self.assertEqual(timestamp_list, sorted(timestamp_list)[::-1])
        self.assertEqual(block_id_list, sorted(block_id_list)[::-1])

    def test_query_blocks_with_basic_lucene_query(self):
        response1 = self.client.query_blocks(lucene_query='block_id:"{}"'.format(EXISTING_BLOCK["header"]["block_id"]))
        response2 = self.client.query_blocks(lucene_query='timestamp:"{}"'.format(EXISTING_BLOCK["header"]["timestamp"]))
        self.assertTrue(response1.get("ok"), response1)
        self.assertEqual(response1.get("status"), 200, response1)
        jsonschema.validate(response1.get("response"), schema.query_block_schema)
        self.assertEqual(1, response1["response"]["total"])
        self.assertTrue(response2.get("ok"), response2)
        self.assertEqual(response2.get("status"), 200, response2)
        jsonschema.validate(response2.get("response"), schema.query_block_schema)
        self.assertEqual(1, response2["response"]["total"])
        # Make sure we got exactly 1 result
        self.assertEqual(len(response1["response"]["results"]), 1)
        self.assertEqual(len(response2["response"]["results"]), 1)
        self.assertEqual(response1["response"]["results"][0], EXISTING_BLOCK)
        self.assertEqual(response2["response"]["results"][0], EXISTING_BLOCK)

    def test_query_blocks_with_compound_lucene_query(self):
        response = self.client.query_blocks(
            lucene_query='block_id:"{}" AND timestamp:"{}"'.format(EXISTING_BLOCK["header"]["block_id"], EXISTING_BLOCK["header"]["timestamp"])
        )
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.query_block_schema)
        self.assertEqual(1, response["response"]["total"], response)
        # Make sure we got exactly 1 result
        self.assertEqual(len(response["response"]["results"]), 1)
        self.assertEqual(response["response"]["results"][0], EXISTING_BLOCK)

    def test_query_blocks_with_no_result_lucene_query(self):
        response = self.client.query_blocks(lucene_query='block_id:"9876543210"')
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.query_block_schema)
        self.assertEqual(0, response["response"]["total"])
        # Make sure we got exactly 0 result
        self.assertEqual(len(response["response"]["results"]), 0)

    # TODO: Add more robust lucene query checking

    # TODO: Add tests for bad queries

    # GET #

    def test_get_block_with_valid_id(self):
        response = self.client.get_block(EXISTING_BLOCK["header"]["block_id"])
        expected_response = {"status": 200, "ok": True, "response": EXISTING_BLOCK}
        self.assertEqual(expected_response, response)

    def test_get_block_with_invalid_id_returns_404(self):
        response = self.client.get_block("9876543210")
        expected_response = {
            "status": 404,
            "ok": False,
            "response": {"error": {"details": "The requested resource(s) cannot be found.", "type": "NOT_FOUND"}},
        }
        self.assertEqual(expected_response, response)

    def test_block_tear_down(self):
        self.client.delete_transaction_type(TEST_TRANSACTION_TYPE)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestBlocks("test_block_set_up"))
    suite.addTest(TestBlocks("test_query_blocks_works_with_no_parameters"))
    suite.addTest(TestBlocks("test_query_blocks_works_with_limit"))
    suite.addTest(TestBlocks("test_query_blocks_works_with_offset"))
    suite.addTest(TestBlocks("test_query_blocks_works_with_sorting"))
    suite.addTest(TestBlocks("test_query_blocks_with_basic_lucene_query"))
    suite.addTest(TestBlocks("test_query_blocks_with_compound_lucene_query"))
    suite.addTest(TestBlocks("test_query_blocks_with_no_result_lucene_query"))
    suite.addTest(TestBlocks("test_get_block_with_valid_id"))
    suite.addTest(TestBlocks("test_get_block_with_invalid_id_returns_404"))
    suite.addTest(TestBlocks("test_block_tear_down"))
    return suite


if __name__ == "__main__":
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite())
    sys.exit(0 if result.wasSuccessful() else 1)
