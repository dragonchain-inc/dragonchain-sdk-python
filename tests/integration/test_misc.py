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

import jsonschema

from tests.integration import schema
import dragonchain_sdk

VERIFIED_BLOCK_ID = None


class TestMisc(unittest.TestCase):
    def setUp(self):
        self.client = dragonchain_sdk.create_client()

    # STATUS #

    def test_get_status(self):
        response = self.client.get_status()
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.get_status_schema)

    # BLOCKCHAIN ADDRESSES #

    def test_get_blockchain_addresses(self):
        response = self.client.get_public_blockchain_addresses()
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.get_blockchain_addresses_schema)

    # CREATE BITCOIN TRANSACTION #

    def test_create_bitcoin_transaction_with_insufficient_crypto(self):
        response = self.client.create_bitcoin_transaction(network="BTC_MAINNET")
        expected_response = {
            "status": 400,
            "ok": False,
            "response": {
                "error": {
                    "type": "INSUFFICIENT_CRYPTO",
                    "details": "You do not have enough UTXOs or funds in this address to sign a transaction with",
                }
            },
        }
        self.assertEqual(expected_response, response)

    # TODO automated way to get test btc to test actually functionality with funds

    # CREATE ETHEREUM TRANSACTION #

    def test_create_ethereum_transaction_with_no_value(self):
        response = self.client.create_ethereum_transaction(network="ETH_ROPSTEN", to="0x0000000000000000000000000000000000000000", value="0x0")
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.created_ethereum_transaction_schema)

    def test_create_ethereum_transaction_with_data(self):
        response = self.client.create_ethereum_transaction(
            network="ETH_ROPSTEN", to="0x0000000000000000000000000000000000000000", value="0x0", data="0xdeadbeef"
        )
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.created_ethereum_transaction_schema)

    def test_create_ethereum_transaction_with_gas_price(self):
        response = self.client.create_ethereum_transaction(
            network="ETH_ROPSTEN", to="0x0000000000000000000000000000000000000000", value="0x0", gas_price="0x1234"
        )
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.created_ethereum_transaction_schema)

    def test_create_ethereum_transaction_with_gas_limit(self):
        response = self.client.create_ethereum_transaction(
            network="ETH_ROPSTEN", to="0x0000000000000000000000000000000000000000", value="0x0", gas="0x1234"
        )
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.created_ethereum_transaction_schema)

    def test_create_ethereum_transaction_with_all_values(self):
        response = self.client.create_ethereum_transaction(
            network="ETH_ROPSTEN", to="0x249A52D7115039a4eB5cd42ca10bbF744F3B678A", value="0x1234", gas="0x4321", gas_price="0xabcd", data="0xbadf00d"
        )
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.created_ethereum_transaction_schema)

    # GET VERIFICATIONS #

    # First we have to find the block id of a block with verifications through level 5 to test
    def find_verified_block(self):
        response = self.client.query_blocks(lucene_query="l5_verifications:1")
        # Ensure that we found results
        self.assertGreater(response["response"]["total"], 0, "No block could be found with a level 5 verification")
        global VERIFIED_BLOCK_ID
        VERIFIED_BLOCK_ID = response["response"]["results"][0]["header"]["block_id"]

    def test_get_l2_verifications(self):
        self.assertIsNotNone(VERIFIED_BLOCK_ID, "No block with all verification levels found")
        response = self.client.get_verifications(VERIFIED_BLOCK_ID, 2)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.l2_verifications_schema)

    def test_get_l3_verifications(self):
        self.assertIsNotNone(VERIFIED_BLOCK_ID, "No block with all verification levels found")
        response = self.client.get_verifications(VERIFIED_BLOCK_ID, 3)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.l3_verifications_schema)

    def test_get_l4_verifications(self):
        self.assertIsNotNone(VERIFIED_BLOCK_ID, "No block with all verification levels found")
        response = self.client.get_verifications(VERIFIED_BLOCK_ID, 4)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.l4_verifications_schema)

    def test_get_l5_verifications(self):
        self.assertIsNotNone(VERIFIED_BLOCK_ID, "No block with all verification levels found")
        response = self.client.get_verifications(VERIFIED_BLOCK_ID, 5)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.l5_verifications_schema)

    def test_get_all_verifications_for_block(self):
        self.assertIsNotNone(VERIFIED_BLOCK_ID, "No block with all verification levels found")
        response = self.client.get_verifications(block_id=VERIFIED_BLOCK_ID)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.all_verifications_schema)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestMisc("test_get_status"))
    suite.addTest(TestMisc("test_get_blockchain_addresses"))
    suite.addTest(TestMisc("test_create_bitcoin_transaction_with_insufficient_crypto"))
    suite.addTest(TestMisc("test_create_ethereum_transaction_with_no_value"))
    suite.addTest(TestMisc("test_create_ethereum_transaction_with_data"))
    suite.addTest(TestMisc("test_create_ethereum_transaction_with_gas_price"))
    suite.addTest(TestMisc("test_create_ethereum_transaction_with_gas_limit"))
    suite.addTest(TestMisc("test_create_ethereum_transaction_with_all_values"))
    suite.addTest(TestMisc("find_verified_block"))
    suite.addTest(TestMisc("test_get_l2_verifications"))
    suite.addTest(TestMisc("test_get_l3_verifications"))
    suite.addTest(TestMisc("test_get_l4_verifications"))
    suite.addTest(TestMisc("test_get_l5_verifications"))
    suite.addTest(TestMisc("test_get_all_verifications_for_block"))
    return suite


if __name__ == "__main__":
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite())
    sys.exit(0 if result.wasSuccessful() else 1)
