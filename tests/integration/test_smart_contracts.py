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

SMART_CONTRACT_BASIC_NAME = "bacon-cream"
SMART_CONTRACT_BASIC_ID = None
SMART_CONTRACT_ARGS_NAME = "bacon-cake"
SMART_CONTRACT_ARGS_ID = None
SMART_CONTRACT_ENV_NAME = "tomato-soup"
SMART_CONTRACT_ENV_ID = None
SMART_CONTRACT_SECRETS_NAME = "bacon-spaghetti"
SMART_CONTRACT_SECRETS_ID = None
SMART_CONTRACT_SCHEDULER_NAME = "bacon-time"
SMART_CONTRACT_SCHEDULER_ID = None
SMART_CONTRACT_ORDER_NAME = "bacon-soup"
SMART_CONTRACT_ORDER_ID = None
SMART_CONTRACT_CRON_NAME = "banana-cron"
SMART_CONTRACT_CRON_ID = None
ARGS_CONTRACT_BODY = None
CREATION_TIMESTAMP = None

SCHEDULER = 60
CRON = "* * * * *"

_expected_not_found_response = {
    "status": 404,
    "ok": False,
    "response": {"error": {"type": "NOT_FOUND", "details": "The requested resource(s) cannot be found."}},
}


class TestSmartContracts(unittest.TestCase):
    def setUp(self):
        self.client = dragonchain_sdk.create_client()
        self.maxDiff = 3000

    def test_create_basic_contract(self):
        response = self.client.create_smart_contract(transaction_type=SMART_CONTRACT_BASIC_NAME, image="alpine:latest", cmd="uptime")
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 202, response)
        jsonschema.validate(response.get("response"), schema.smart_contract_create_schema)
        global SMART_CONTRACT_BASIC_ID
        SMART_CONTRACT_BASIC_ID = response["response"]["success"]["id"]
        time.sleep(3)

    def test_create_contract_with_args(self):
        response = self.client.create_smart_contract(transaction_type=SMART_CONTRACT_ARGS_NAME, image="alpine:latest", cmd="echo", args=["hello"])
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 202, response)
        jsonschema.validate(response.get("response"), schema.smart_contract_create_schema)
        global SMART_CONTRACT_ARGS_ID
        SMART_CONTRACT_ARGS_ID = response["response"]["success"]["id"]
        time.sleep(3)

    def test_create_contract_with_custom_env(self):
        response = self.client.create_smart_contract(
            transaction_type=SMART_CONTRACT_ENV_NAME,
            image="alpine:latest",
            cmd="echo",
            args=["hello"],
            environment_variables={"MY_VAR": "custom value"},
        )
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 202, response)
        jsonschema.validate(response.get("response"), schema.smart_contract_create_schema)
        global SMART_CONTRACT_ENV_ID
        SMART_CONTRACT_ENV_ID = response["response"]["success"]["id"]
        time.sleep(3)

    def test_create_contract_with_serial_execution_order(self):
        response = self.client.create_smart_contract(
            transaction_type=SMART_CONTRACT_ORDER_NAME, image="alpine:latest", cmd="echo", args=["hello"], execution_order="serial"
        )
        self.assertTrue(response.get("ok"))
        self.assertEqual(response.get("status"), 202)
        jsonschema.validate(response.get("response"), schema.smart_contract_create_schema)
        global SMART_CONTRACT_ORDER_ID
        SMART_CONTRACT_ORDER_ID = response["response"]["success"]["id"]
        time.sleep(3)

    def test_create_contract_with_secrets(self):
        response = self.client.create_smart_contract(
            transaction_type=SMART_CONTRACT_SECRETS_NAME, image="alpine:latest", cmd="echo", args=["hello"], secrets={"mySecret": "super secret"}
        )
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 202, response)
        jsonschema.validate(response.get("response"), schema.smart_contract_create_schema)
        global SMART_CONTRACT_SECRETS_ID
        SMART_CONTRACT_SECRETS_ID = response["response"]["success"]["id"]
        time.sleep(3)

    def test_create_contract_with_scheduler(self):
        response = self.client.create_smart_contract(
            transaction_type=SMART_CONTRACT_SCHEDULER_NAME, image="alpine:latest", cmd="echo", args=["hello"], schedule_interval_in_seconds=SCHEDULER
        )
        global CREATION_TIMESTAMP
        CREATION_TIMESTAMP = str(time.time())
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 202, response)
        jsonschema.validate(response.get("response"), schema.smart_contract_create_schema)
        global SMART_CONTRACT_SCHEDULER_ID
        SMART_CONTRACT_SCHEDULER_ID = response["response"]["success"]["id"]
        time.sleep(3)

    def test_create_contract_with_cron(self):
        response = self.client.create_smart_contract(
            transaction_type=SMART_CONTRACT_CRON_NAME, image="alpine:latest", cmd="echo", args=["hello"], cron_expression=CRON
        )
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 202, response)
        jsonschema.validate(response.get("response"), schema.smart_contract_create_schema)
        global SMART_CONTRACT_CRON_ID
        SMART_CONTRACT_CRON_ID = response["response"]["success"]["id"]
        time.sleep(10)

    def test_get_contract_with_transcation_type(self):
        response = self.client.get_smart_contract(transaction_type=SMART_CONTRACT_ARGS_NAME)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.smart_contract_schema_at_rest_schema)
        global ARGS_CONTRACT_BODY
        ARGS_CONTRACT_BODY = response["response"]

    def test_get_contract_with_contract_id(self):
        response = self.client.get_smart_contract(smart_contract_id=SMART_CONTRACT_ARGS_ID)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.smart_contract_schema_at_rest_schema)

    def test_query_contracts_with_no_params(self):
        response = self.client.query_smart_contracts()
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.query_smart_contract_schema)

    def test_query_contracts_by_txn_type(self):
        response = self.client.query_smart_contracts('txn_type:"{}"'.format(SMART_CONTRACT_ARGS_NAME))
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.query_smart_contract_schema)
        self.assertEqual(response["response"]["total"], 1)
        self.assertEqual(len(response["response"]["results"]), 1)
        self.assertEqual(response["response"]["results"][0], ARGS_CONTRACT_BODY)

    def test_query_contracts_with_limit(self):
        response = self.client.query_smart_contracts(limit=2)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.query_smart_contract_schema)
        self.assertEqual(2, len(response["response"]["results"]))

    def test_query_contracts_with_offset(self):
        response1 = self.client.query_smart_contracts(offset=0, limit=1)
        response2 = self.client.query_smart_contracts(offset=2, limit=1)
        self.assertTrue(response1.get("ok"), response1)
        self.assertEqual(response1.get("status"), 200, response1)
        jsonschema.validate(response1.get("response"), schema.query_smart_contract_schema)
        self.assertTrue(response2.get("ok"), response2)
        self.assertEqual(response2.get("status"), 200, response2)
        jsonschema.validate(response2.get("response"), schema.query_smart_contract_schema)
        self.assertNotEqual(response1["response"]["results"], response2["response"]["results"])

    def test_query_contracts_with_sorting(self):
        response1 = self.client.query_smart_contracts(sort="id:desc", limit=5)
        response2 = self.client.query_smart_contracts(sort="txn_type:desc", limit=5)
        self.assertTrue(response1.get("ok"), response1)
        self.assertEqual(response1.get("status"), 200, response1)
        jsonschema.validate(response1.get("response"), schema.query_smart_contract_schema)
        self.assertTrue(response2.get("ok"), response2)
        self.assertEqual(response2.get("status"), 200, response2)
        jsonschema.validate(response2.get("response"), schema.query_smart_contract_schema)
        timestamp_list = []
        txn_type_list = []
        for contract in response1["response"]["results"]:
            timestamp_list.append(contract["status"]["timestamp"])
        for contract in response2["response"]["results"]:
            txn_type_list.append(contract["txn_type"])
        # Ensure our sorting worked by checking that the timestamps and block_ids are in ascending ascending order (sorted)
        self.assertEqual(timestamp_list, sorted(timestamp_list)[::-1])
        self.assertEqual(txn_type_list, sorted(txn_type_list)[::-1])

    def test_query_contracts_with_basic_lucene_query(self):
        response1 = self.client.query_smart_contracts(lucene_query='id:"{}"'.format(SMART_CONTRACT_ARGS_ID))
        response2 = self.client.query_smart_contracts(lucene_query='txn_type:"{}"'.format(SMART_CONTRACT_ARGS_NAME))
        self.assertTrue(response1.get("ok"), response1)
        self.assertEqual(response1.get("status"), 200, response1)
        jsonschema.validate(response1.get("response"), schema.query_smart_contract_schema)
        self.assertEqual(1, response1["response"]["total"])
        self.assertTrue(response2.get("ok"), response2)
        self.assertEqual(response2.get("status"), 200, response2)
        jsonschema.validate(response2.get("response"), schema.query_smart_contract_schema)
        self.assertEqual(1, response2["response"]["total"])
        # Make sure we got exactly 1 result
        self.assertEqual(len(response1["response"]["results"]), 1)
        self.assertEqual(len(response2["response"]["results"]), 1)
        self.assertEqual(response1["response"]["results"][0], ARGS_CONTRACT_BODY)
        self.assertEqual(response2["response"]["results"][0], ARGS_CONTRACT_BODY)

    def test_query_contracts_with_compound_lucene_query(self):
        response = self.client.query_smart_contracts(
            lucene_query='id:"{}" AND txn_type:"{}"'.format(SMART_CONTRACT_ARGS_ID, SMART_CONTRACT_ARGS_NAME)
        )
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.query_smart_contract_schema)
        self.assertEqual(1, response["response"]["total"])
        # Make sure we got exactly 1 result
        self.assertEqual(len(response["response"]["results"]), 1)
        self.assertEqual(response["response"]["results"][0], ARGS_CONTRACT_BODY)

    def test_query_contracts_with_no_result_lucene_query(self):
        response = self.client.query_blocks(lucene_query='txn_type:"watermelon"')
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.query_smart_contract_schema)
        self.assertEqual(0, response["response"]["total"])
        # Make sure we got exactly 0 result
        self.assertEqual(len(response["response"]["results"]), 0)

    def test_update_contract_with_image(self):
        response = self.client.update_smart_contract(smart_contract_id=SMART_CONTRACT_ARGS_ID, image="busybox:latest")
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 202, response)
        time.sleep(15)
        updated_smart_contract = self.client.get_smart_contract(transaction_type=SMART_CONTRACT_ARGS_NAME)
        self.assertEqual(updated_smart_contract["response"]["image"], "busybox:latest")

    def test_update_contract_with_args(self):
        response = self.client.update_smart_contract(smart_contract_id=SMART_CONTRACT_ARGS_ID, args=["bacon"])
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 202, response)
        time.sleep(15)
        updated_smart_contract = self.client.get_smart_contract(transaction_type=SMART_CONTRACT_ARGS_NAME)
        self.assertEqual(updated_smart_contract["response"]["args"][0], "bacon")

    def test_update_contract_with_env(self):
        response = self.client.update_smart_contract(smart_contract_id=SMART_CONTRACT_ENV_ID, environment_variables={"bacon": "tomato"})
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 202, response)
        time.sleep(15)
        updated_smart_contract = self.client.get_smart_contract(transaction_type=SMART_CONTRACT_ENV_NAME)
        self.assertEqual(updated_smart_contract["response"]["env"]["bacon"], "tomato")

    def test_update_contract_with_secrets(self):
        response = self.client.update_smart_contract(smart_contract_id=SMART_CONTRACT_SECRETS_ID, secrets={"secret-banana": "bananas"})
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 202, response)
        time.sleep(15)
        updated_smart_contract = self.client.get_smart_contract(transaction_type=SMART_CONTRACT_SECRETS_NAME)
        self.assertIn("secret-banana", updated_smart_contract["response"]["existing_secrets"])

    def test_update_contract_execution_order(self):
        response = self.client.update_smart_contract(smart_contract_id=SMART_CONTRACT_ORDER_ID, execution_order="parallel")
        self.assertTrue(response.get("ok"))
        self.assertEqual(response.get("status"), 202)
        updated_smart_contract = self.client.get_smart_contract(transaction_type=SMART_CONTRACT_ORDER_NAME)
        self.assertTrue(updated_smart_contract["response"]["execution_order"], "parallel")

    def wait_for_scheduler_invocation(self):
        time.sleep(60)

    def test_successful_invocation_of_scheduler(self):
        transaction_invocation = self.client.query_transactions(
            lucene_query='txn_type:"{}"'.format(SMART_CONTRACT_SCHEDULER_NAME), sort="timestamp:desc", limit=1
        )
        self.assertGreater(transaction_invocation["response"]["total"], 0)
        self.assertGreater(transaction_invocation["response"]["results"][0]["header"]["timestamp"], CREATION_TIMESTAMP)

    def test_successful_invocation_of_cron(self):
        transaction_invocation = self.client.query_transactions(
            lucene_query='txn_type:"{}"'.format(SMART_CONTRACT_CRON_NAME), sort="timestamp:desc", limit=1
        )
        self.assertGreater(transaction_invocation["response"]["total"], 0)
        self.assertGreater(transaction_invocation["response"]["results"][0]["header"]["timestamp"], CREATION_TIMESTAMP)

    def test_successful_invocation_with_transactions(self):
        args_transaction = self.client.create_transaction(SMART_CONTRACT_ARGS_NAME, "banana")
        env_transaction = self.client.create_transaction(SMART_CONTRACT_ENV_NAME, "banana")
        secrets_transaction = self.client.create_transaction(SMART_CONTRACT_SECRETS_NAME, "banana")
        time.sleep(15)
        args_query = self.client.query_transactions('invoker:"{}"'.format(args_transaction["response"]["transaction_id"]))
        env_query = self.client.query_transactions('invoker:"{}"'.format(env_transaction["response"]["transaction_id"]))
        secrets_query = self.client.query_transactions('invoker:"{}"'.format(secrets_transaction["response"]["transaction_id"]))
        self.assertEqual(args_query["response"]["results"][0]["header"]["invoker"], args_transaction["response"]["transaction_id"])
        self.assertEqual(env_query["response"]["results"][0]["header"]["invoker"], env_transaction["response"]["transaction_id"])
        self.assertEqual(secrets_query["response"]["results"][0]["header"]["invoker"], secrets_transaction["response"]["transaction_id"])
        time.sleep(10)

    def test_get_smart_contract_object_by_prefix_key(self):
        response = self.client.get_smart_contract_object("rawResponse", SMART_CONTRACT_ARGS_ID)
        self.assertEqual(response["response"], '"bacon\\n"')

    def test_list_smart_contract_objects(self):
        response = self.client.list_smart_contract_objects(smart_contract_id=SMART_CONTRACT_ARGS_ID)
        expected_response = {"status": 200, "ok": True, "response": ["/rawResponse"]}
        self.assertEqual(response, expected_response)

    def test_successful_creation_of_contract(self):
        response = self.client.get_smart_contract(SMART_CONTRACT_BASIC_ID)
        self.assertEqual(response["response"]["status"]["state"], "active", response)
        self.assertEqual(response["response"]["status"]["msg"], "Creation success", response)

    def test_successful_update_of_contract(self):
        response = self.client.get_smart_contract(SMART_CONTRACT_ARGS_ID)
        self.assertEqual(response["response"]["status"]["state"], "active", response)

    def test_delete_basic_contract(self):
        response = self.client.delete_smart_contract(SMART_CONTRACT_BASIC_ID)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 202, response)
        time.sleep(10)
        deleted_fetch = self.client.get_smart_contract(transaction_type=SMART_CONTRACT_BASIC_NAME)
        self.assertEqual(_expected_not_found_response, deleted_fetch)

    def test_delete_updated_contract(self):
        response = self.client.delete_smart_contract(SMART_CONTRACT_ARGS_ID)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 202, response)
        time.sleep(10)
        deleted_fetch = self.client.get_smart_contract(transaction_type=SMART_CONTRACT_ARGS_NAME)
        self.assertEqual(_expected_not_found_response, deleted_fetch)

    def test_delete_scheduled_contract(self):
        response = self.client.delete_smart_contract(SMART_CONTRACT_SCHEDULER_ID)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 202, response)
        time.sleep(10)
        deleted_fetch = self.client.get_smart_contract(transaction_type=SMART_CONTRACT_SCHEDULER_NAME)
        self.assertEqual(_expected_not_found_response, deleted_fetch)

    def test_delete_cron_contract(self):
        response = self.client.delete_smart_contract(SMART_CONTRACT_CRON_ID)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 202, response)
        time.sleep(10)
        deleted_fetch = self.client.get_smart_contract(transaction_type=SMART_CONTRACT_CRON_NAME)
        self.assertEqual(_expected_not_found_response, deleted_fetch)

    def smart_contract_clean_up(self):
        contracts = [
            (SMART_CONTRACT_BASIC_ID, SMART_CONTRACT_BASIC_NAME),
            (SMART_CONTRACT_ARGS_ID, SMART_CONTRACT_ARGS_NAME),
            (SMART_CONTRACT_ENV_ID, SMART_CONTRACT_ENV_NAME),
            (SMART_CONTRACT_SECRETS_ID, SMART_CONTRACT_SECRETS_NAME),
            (SMART_CONTRACT_ORDER_ID, SMART_CONTRACT_ORDER_NAME),
            (SMART_CONTRACT_SCHEDULER_ID, SMART_CONTRACT_SCHEDULER_NAME),
            (SMART_CONTRACT_CRON_ID, SMART_CONTRACT_CRON_NAME),
        ]
        for contract in contracts:
            try:
                sc_id = contract[0]
                if not sc_id:
                    sc_id = self.client.get_transaction_type(contract[1])["response"]["contract_id"]
                self.client.delete_smart_contract(sc_id)
            except Exception:
                pass


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestSmartContracts("test_create_basic_contract"))
    suite.addTest(TestSmartContracts("test_create_contract_with_args"))
    suite.addTest(TestSmartContracts("test_create_contract_with_custom_env"))
    suite.addTest(TestSmartContracts("test_create_contract_with_serial_execution_order"))
    suite.addTest(TestSmartContracts("test_create_contract_with_secrets"))
    suite.addTest(TestSmartContracts("test_create_contract_with_scheduler"))
    suite.addTest(TestSmartContracts("test_create_contract_with_cron"))
    suite.addTest(TestSmartContracts("test_get_contract_with_transcation_type"))
    suite.addTest(TestSmartContracts("test_get_contract_with_contract_id"))
    suite.addTest(TestSmartContracts("test_query_contracts_with_no_params"))
    suite.addTest(TestSmartContracts("test_query_contracts_by_txn_type"))
    suite.addTest(TestSmartContracts("test_query_contracts_with_limit"))
    suite.addTest(TestSmartContracts("test_query_contracts_with_offset"))
    # suite.addTest(TestSmartContracts("test_query_contracts_with_sorting"))
    suite.addTest(TestSmartContracts("test_query_contracts_with_basic_lucene_query"))
    suite.addTest(TestSmartContracts("test_query_contracts_with_compound_lucene_query"))
    suite.addTest(TestSmartContracts("test_query_contracts_with_no_result_lucene_query"))
    suite.addTest(TestSmartContracts("test_update_contract_with_image"))
    suite.addTest(TestSmartContracts("test_update_contract_with_args"))
    suite.addTest(TestSmartContracts("test_update_contract_with_env"))
    suite.addTest(TestSmartContracts("test_update_contract_with_secrets"))
    suite.addTest(TestSmartContracts("test_update_contract_execution_order"))
    suite.addTest(TestSmartContracts("wait_for_scheduler_invocation"))
    suite.addTest(TestSmartContracts("test_successful_invocation_of_scheduler"))
    suite.addTest(TestSmartContracts("test_successful_invocation_of_cron"))
    suite.addTest(TestSmartContracts("test_successful_invocation_with_transactions"))
    suite.addTest(TestSmartContracts("test_get_smart_contract_object_by_prefix_key"))
    suite.addTest(TestSmartContracts("test_list_smart_contract_objects"))
    suite.addTest(TestSmartContracts("test_successful_creation_of_contract"))
    suite.addTest(TestSmartContracts("test_successful_update_of_contract"))
    suite.addTest(TestSmartContracts("test_delete_basic_contract"))
    suite.addTest(TestSmartContracts("test_delete_updated_contract"))
    suite.addTest(TestSmartContracts("test_delete_scheduled_contract"))
    suite.addTest(TestSmartContracts("test_delete_cron_contract"))
    suite.addTest(TestSmartContracts("smart_contract_clean_up"))
    return suite


if __name__ == "__main__":
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite())
    sys.exit(0 if result.wasSuccessful() else 1)
