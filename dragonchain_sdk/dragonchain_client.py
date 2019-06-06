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
from typing import cast, Optional, Union, List, TYPE_CHECKING

from dragonchain_sdk import request
from dragonchain_sdk import credentials

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    import mypy_extensions

    custom_index_type = mypy_extensions.TypedDict("custom_index_type", {"key": str, "path": str})


class Client(object):
    """Construct a new ``Client`` object

    Args:
        dragonchain_id (str): The ID of the chain to connect to.
        auth_key_id (str): The authorization key ID
        auth_key (str): The authorization key
        endpoint (str): The endpoint of the Dragonchain
        verify (bool): Verify the TLS cert of the Dragonchain
        algorithm (str): The hashing algorithm used for HMAC authentication

    Returns:
        A new Dragonchain client.
    """

    def __init__(
        self,
        dragonchain_id: Optional[str],
        auth_key_id: Optional[str],
        auth_key: Optional[str],
        endpoint: Optional[str],
        verify: bool,
        algorithm: str,
    ):
        self.credentials = credentials.Credentials(dragonchain_id, auth_key, auth_key_id, algorithm)
        self.request = request.Request(self.credentials, endpoint, verify)
        logger.debug("Client finished initialization")

    def get_smart_contract_secret(self, secret_name: str) -> str:
        """Gets secrets for smart contracts

        Args:
            secret_name (str): name of the secret to retrieve

        Raises:
            TypeError: with bad parameter types
            RuntimeError: if not running in a smart contract environment

        Returns:
            String of the value of the specified secret
        """
        if not isinstance(secret_name, str):
            raise TypeError('Parameter "secret_name" must be of type str.')
        if not os.environ.get("SMART_CONTRACT_ID"):
            raise RuntimeError('Missing "SMART_CONTRACT_ID" from environment')
        path = os.path.join(
            os.path.abspath(os.sep), "var", "openfaas", "secrets", "sc-{}-{}".format(os.environ.get("SMART_CONTRACT_ID"), secret_name)
        )
        return open(path, "r").read()

    def get_status(self):
        """Get the status from a chain

        Returns:
            Returns the status of a Dragonchain
        """
        return self.request.get("/status")

    def query_smart_contracts(self, lucene_query: Optional[str] = None, sort: Optional[str] = None, offset: int = 0, limit: int = 10):
        """Perform a query on a chain's smart contracts

        Args:
            lucene_query (str, optional): Lucene query parameter (e.g.: ``is_serial:true``)
            sort (str, optional): Sort syntax of 'field:direction' (e.g.: ``name:asc``)
            offset (int, optional): Pagination offset of query (default 0)
            limit (int, optional): Pagination limit (default 10)

        Returns:
            The results of the query
        """
        query_params = self.request.get_lucene_query_params(lucene_query, sort, offset, limit)
        return self.request.get("/contract{}".format(query_params))

    def get_smart_contract(self, smart_contract_id: Optional[str] = None, transaction_type: Optional[str] = None):
        """Perform a query on a chain's smart contracts

        Args:
            smart_contract_id (str, exclusive): Id of the contract to get
            transaction_type (str, exclusive): Name of the Transaction Type bound to this contract. Usually the contract "name"

        Raises:
            TypeError: with bad parameter types

        Returns:
            The contract returned from the request
        """
        if smart_contract_id is not None and not isinstance(smart_contract_id, str):
            raise TypeError('Parameter "smart_contract_id" must be of type str.')
        if transaction_type is not None and not isinstance(transaction_type, str):
            raise TypeError('Parameter "transaction_type" must be of type str.')
        if smart_contract_id and transaction_type:
            raise TypeError('Only one of "smart_contract_id" and "transaction_type" can be specified')
        if smart_contract_id:
            return self.request.get("/contract/{}".format(smart_contract_id))
        elif transaction_type:
            return self.request.get("/contract/txn_type/{}".format(transaction_type))
        else:
            raise TypeError('At least one of "smart_contract_id" or "transaction_type" must be specified')

    def create_smart_contract(
        self,
        transaction_type: str,
        image: str,
        cmd: str,
        args: Optional[list] = None,
        execution_order: str = "parallel",
        environment_variables: Optional[dict] = None,
        secrets: Optional[dict] = None,
        scheduler_interval_in_seconds: Optional[int] = None,
        cron_expression: Optional[str] = None,
        registry_credentials: Optional[str] = None,
    ):
        """Post a contract to a chain

        Args:
            transaction_type (str): transaction_type of the contract to create
            image (str): Docker image containing the smart contract logic
            cmd (str): Entrypoint command to run in the docker container
            execution_order (optional, str): Order of execution. Valid values are 'serial' or 'parallel'. default: 'parallel'
            args (optional, list): List of arguments to the cmd field
            environment_variables (optional, dict): dict mapping of environment variables for your contract runtime
            secrets (optional, dict): dict mapping of secrets for your contract runtime
            scheduler_interval_in_seconds (optional, int): The seconds of scheduled execution in seconds. Must not be set if cron_expression is set
            cron_expression (optional, str): The rate of scheduled execution specified as a cron. Must not be set if scheduler_interval_in_seconds is set
            registry_credentials (optional, str): basic-auth for pulling docker images, base64 encoded (e.g. username:password)

        Raises:
            TypeError: with bad parameter types

        Returns:
            Success or failure object
        """
        if not isinstance(transaction_type, str):
            raise TypeError('Parameter "transaction_type" must be of type str.')
        if not isinstance(image, str):
            raise TypeError('Parameter "image" must be of type str.')
        if not isinstance(cmd, str):
            raise TypeError('Parameter "cmd" must be of type str.')
        if args is not None and not isinstance(args, list):
            raise TypeError('Parameter "args" must be of type list.')
        if not isinstance(execution_order, str):
            raise TypeError('Parameter "execution_order" must be of type str.')
        if execution_order is not None and execution_order not in ["parallel", "serial"]:
            raise ValueError('Parameter "execution_order" must be either "serial" or "parallel".')
        if environment_variables is not None and not isinstance(environment_variables, dict):
            raise TypeError('Parameter "environment_variables" must be of type dict.')
        if secrets is not None and not isinstance(secrets, dict):
            raise TypeError('Parameter "secrets" must be of type dict.')
        if scheduler_interval_in_seconds is not None and cron_expression is not None:
            raise ValueError('Parameter "scheduler_interval_in_seconds" and "cron_expression" can not both be set')
        if scheduler_interval_in_seconds is not None and not isinstance(scheduler_interval_in_seconds, int):
            raise TypeError('Parameter "scheduler_interval_in_seconds" must be of type int.')
        if cron_expression is not None and not isinstance(cron_expression, str):
            raise TypeError('Parameter "cron_expression" must be of type str.')
        if registry_credentials is not None and not isinstance(registry_credentials, str):
            raise TypeError('Parameter "registry_credentials" must be of type str.')

        body = cast(dict, {"version": "3", "txn_type": transaction_type, "image": image, "cmd": cmd, "execution_order": execution_order})
        if environment_variables:
            body["env"] = environment_variables
        if args:
            body["args"] = args
        if secrets:
            body["secrets"] = secrets
        if scheduler_interval_in_seconds:
            body["seconds"] = scheduler_interval_in_seconds
        if cron_expression:
            body["cron"] = cron_expression
        if registry_credentials:
            body["auth"] = registry_credentials
        return self.request.post("/contract", body)

    def update_smart_contract(  # noqa: C901
        self,
        smart_contract_id: str,
        image: Optional[str] = None,
        cmd: Optional[str] = None,
        args: Optional[list] = None,
        execution_order: Optional[str] = None,
        enabled: Optional[bool] = None,
        environment_variables: Optional[dict] = None,
        secrets: Optional[dict] = None,
        scheduler_interval_in_seconds: Optional[int] = None,
        cron_expression: Optional[str] = None,
        registry_credentials: Optional[str] = None,
    ):
        """Update an existing smart contract. The contract_id and at least one optional parameter must be supplied.

        Args:
            smart_contract_id (str): id of the contract to update
            image (str): Docker image containing the smart contract logic
            cmd (str): Entrypoint command to run in the docker container
            execution_order (str): Order of execution. Valid values are 'serial' or 'parallel'
            enabled (bool, optional): Enabled status of contract
            args (list, optional): List of arguments to the cmd field
            environment_variables (dict, optional): dict mapping of environment variables for your contract runtime
            secrets (dict, optional): dict mapping of secrets for your contract runtime
            scheduler_interval_in_seconds (int, optional): The seconds of scheduled execution in seconds
            cron_expression (str, optional): The rate of scheduled execution specified as a cron
            registry_credentials (str, optional): basic-auth for pulling docker images, base64 encoded (e.g. username:password)

        Raises:
            TypeError: with bad parameter types

        Returns:
            Success or failure object
        """
        if not isinstance(smart_contract_id, str):
            raise TypeError('Parameter "contract_id" must be of type str.')
        if image is not None and not isinstance(image, str):
            raise TypeError('Parameter "image" must be of type str.')
        if cmd is not None and not isinstance(cmd, str):
            raise TypeError('Parameter "cmd" must be of type str.')
        if execution_order is not None and not isinstance(execution_order, str):
            raise TypeError('Parameter "execution_order" must be of type str.')
        if execution_order is not None and execution_order not in ["parallel", "serial"]:
            raise ValueError('Parameter "execution_order" must be either "serial" or "parallel".')
        if enabled is not None and not isinstance(enabled, bool):
            raise TypeError('Parameter "enabled" must be of type bool.')
        if args is not None and not isinstance(args, list):
            raise TypeError('Parameter "args" must be of type list.')
        if environment_variables is not None and not isinstance(environment_variables, dict):
            raise TypeError('Parameter "env" must be of type dict.')
        if secrets is not None and not isinstance(secrets, dict):
            raise TypeError('Parameter "secrets" must be of type dict.')
        if scheduler_interval_in_seconds is not None and not isinstance(scheduler_interval_in_seconds, int):
            raise TypeError('Parameter "scheduler_interval_in_seconds" must be of type int.')
        if cron_expression is not None and not isinstance(cron_expression, str):
            raise TypeError('Parameter "cron_expression" must be of type str.')
        if registry_credentials is not None and not isinstance(registry_credentials, str):
            raise TypeError('Parameter "registry_credentials" must be of type str.')

        body = cast(dict, {"version": "3"})
        if image:
            body["image"] = image
        if cmd:
            body["cmd"] = cmd
        if execution_order:
            body["execution_order"] = execution_order
        if enabled is False:
            body["desired_state"] = "inactive"
        if enabled is True:
            body["desired_state"] = "active"
        if args:
            body["args"] = args
        if environment_variables:
            body["env"] = environment_variables
        if secrets:
            body["secrets"] = secrets
        if scheduler_interval_in_seconds:
            body["seconds"] = scheduler_interval_in_seconds
        if cron_expression:
            body["cron"] = cron_expression
        if registry_credentials:
            body["auth"] = registry_credentials

        return self.request.put("/contract/{}".format(smart_contract_id), body)

    def delete_smart_contract(self, smart_contract_id: str):
        """Delete an existing contract

        Args:
            smart_contract_id (str): Transaction type of the contract to delete

        Raises:
            TypeError: with bad parameter types

        Returns:
            The results of the delete request
        """
        if not isinstance(smart_contract_id, str):
            raise TypeError('Parameter "state" must be of type str.')
        return self.request.delete("/contract/{}".format(smart_contract_id))

    def query_transactions(self, lucene_query: Optional[str] = None, sort: Optional[str] = None, offset: int = 0, limit: int = 10):
        """Perform a query on a chain's transactions

        Args:
            lucene_query (str, optional): Lucene query parameter (e.g.: ``is_serial:true``)
            sort (str, optional): Sort syntax of 'field:direction' (e.g.: ``txn_type:asc``)
            offset (int, optional): Pagination offset of query (default 0)
            limit (int, optional): Pagination limit (default 10)

        Returns:
            The results of the query
        """
        query_params = self.request.get_lucene_query_params(lucene_query, sort, offset, limit)
        return self.request.get("/transaction{}".format(query_params))

    def get_transaction(self, transaction_id: str):
        """Get a specific transaction by id

        Args:
            transaction_id (str): ID of the transaction to get (should be a UUID)

        Raises:
            TypeError: with bad parameter types

        Returns:
            The transaction searched for
        """
        if not isinstance(transaction_id, str):
            raise TypeError('Paramter "transaction_id" must be of type str.')
        return self.request.get("/transaction/{}".format(transaction_id))

    def create_transaction(self, transaction_type: str, payload: Union[str, dict], tag: Optional[str] = None, callback_url: Optional[str] = None):
        """Post a transaction to a chain

        Args:
            transaction_type (str): Type of transaction
            payload (dict or string): The payload of the transaction
            tag (str, optional): A tag string to search on

        Returns:
            Transaction ID on success
        """
        headers = {}
        if callback_url:
            headers["X-Callback-Url"] = callback_url

        return self.request.post("/transaction", _build_transaction_dict(transaction_type, payload, tag), additional_headers=headers)

    def create_bulk_transaction(self, transaction_list: list):
        """Post many transactions to a chain at once, over a single connnection

        Args:
            transaction_list (list): List of transaction dictionaries. Schema: ``{'transaction_type': 'str', 'payload': 'str or dict', 'tag': 'str (optional)'}``

        Raises:
            TypeError: with bad parameter types

        Returns:
            List of succeeded transaction id's and list of failed transactions
        """
        if not isinstance(transaction_list, list):
            raise TypeError('Parameter "transaction_list" must be of type list.')

        post_data = []

        for transaction in transaction_list:
            if not isinstance(transaction, dict):
                raise TypeError('All items in parameter "transaction_list" must be of type dict.')
            post_data.append(
                _build_transaction_dict(transaction.get("transaction_type") or "", transaction.get("payload") or "", transaction.get("tag") or "")
            )

        return self.request.post("/transaction_bulk", post_data)

    def query_blocks(self, lucene_query: Optional[str] = None, sort: Optional[str] = None, offset: int = 0, limit: int = 10):
        """Perform a query on a chain's blocks

        Args:
            lucene_query (str, optional): Lucene query parameter (e.g.: ``is_serial:true``)
            sort (str, optional): Sort syntax of 'field:direction' (e.g.: ``block_id:asc``)
            offset (int, optional): Pagination offset of query (default 0)
            limit (int, optional): Pagination limit (default 10)

        Returns:
            The results of the query
        """
        query_params = self.request.get_lucene_query_params(lucene_query, sort, offset, limit)
        return self.request.get("/block{}".format(query_params))

    def get_block(self, block_id: str):
        """Get a specific block by id

        Args:
            block_id (str): ID of the block to get

        Raises:
            TypeError: with bad parameter types

        Returns:
            The block which was retrieved from the chain
        """
        if not isinstance(block_id, str):
            raise TypeError('Parameter "block_id" must be of type str.')
        return self.request.get("/block/{}".format(block_id))

    def get_verifications(self, block_id: str, level: Optional[int] = None):
        """Get higher level block verifications by level 1 block id

        Args:
            block_id (str): ID of the block to get
            level (int, optional): Level of verifications to get (valid values are 2, 3, 4 and 5)

        Raises:
            TypeError: with bad parameter types

        Returns:
            Higher level block verifications
        """
        if not isinstance(block_id, str):
            raise TypeError('Parameter "block_id" must be of type str.')
        if level is not None:
            if not isinstance(level, int):
                raise TypeError('Parameter "level" must be of int.')
            if level not in [2, 3, 4, 5]:
                raise ValueError('Parameter "level" must be between 2 and 5 inclusive.')
            return self.request.get("/verifications/{}?level={}".format(block_id, level))
        return self.request.get("/verifications/{}".format(block_id))

    def get_api_key(self, key_id: str):
        """Get information about an HMAC API key

        Args:
            key_id (str): The ID of the api key to retrieve data about

        Raises:
            TypeError: with bad parameter types

        Returns:
            Data about the API key
        """
        if not isinstance(key_id, str):
            raise TypeError('Parameter "key_id" must be of type str.')
        return self.request.get("/api-key/{}".format(key_id))

    def list_api_keys(self):
        """List of HMAC API keys

        Returns:
            A list of key IDs and their associated data
        """
        return self.request.get("/api-key")

    def create_api_key(self):
        """Generate a new HMAC API key

        Returns:
            A new API key ID and key
        """
        return self.request.post("/api-key", {})

    def delete_api_key(self, key_id: str):
        """Delete an existing HMAC API key

        Returns:
            204 No Content on success
        """
        if not isinstance(key_id, str):
            raise TypeError('Parameter "key_id" must be of type str.')
        return self.request.delete("/api-key/{}".format(key_id))

    def get_smart_contract_object(self, key: str, smart_contract_id: str = None):
        """Retrieve data from the object storage of a smart contract
        Note: When ran in an actual smart contract, smart_contract_id will be pulled automatically from the environment if not explicitly provided

        Args:
            key (str): The key stored in the heap to retrieve
            smart_contract_id (str, optional): The ID of the smart contract, optional if called from within a smart contract

        Raises:
            TypeError: with bad parameter types

        Returns:
            The value of the object in the heap
        """
        if not isinstance(key, str):
            raise TypeError('Parameter "key" must be of type str.')
        if smart_contract_id is None:
            smart_contract_id = os.environ.get("SMART_CONTRACT_ID")
        if not isinstance(smart_contract_id, str):
            raise TypeError('Parameter "smart_contract_id" must be of type str.')
        return self.request.get("/get/{}/{}".format(smart_contract_id, key), parse_response=False)

    def list_smart_contract_objects(self, prefix_key: Optional[str] = None, smart_contract_id: Optional[str] = None):
        """Lists all objects stored in a smart contracts heap
        Note: When ran in an actual smart contract, smart_contract_id will be pulled automatically from the environment if not explicitly provided

        Args:
            smart_contract_id (str, optional): smart_contract_id heap to list. If not provided explicitly, it must be in the SMART_CONTRACT_NAME env var
            prefix_key (str, optional): the prefix_key or "folder" from which to list objects. Must NOT contain trailing slash "/".
                                        Note: Defaults to the root of the accessable filesystem + /list/{smart_contract_id}/

        Raises:
            TypeError: with bad parameter types
            ValueError: with bad parameter values

        Returns:
            Parsed json response from the chain
        """
        if smart_contract_id is None:
            smart_contract_id = os.environ.get("SMART_CONTRACT_ID")
        if not isinstance(smart_contract_id, str):
            raise TypeError('Parameter "smart_contract_id" must be of type str.')
        if prefix_key is not None:
            if not isinstance(prefix_key, str):
                raise TypeError('Parameter "prefix_key" must be of type str.')
            if prefix_key.endswith("/"):
                raise ValueError('Parameter "prefix_key" cannot end with /.')
            return self.request.get("/list/{}/{}/".format(smart_contract_id, prefix_key))
        return self.request.get("/list/{}/".format(smart_contract_id))

    def create_bitcoin_transaction(
        self,
        network: str,
        satoshis_per_byte: Optional[float] = None,
        data: Optional[str] = None,
        change_address: Optional[str] = None,
        outputs: Optional[list] = None,
    ):
        """Create and sign a bitcoin transaction using your chain's private keys

        Args:
            network (str): network to create transaction for. Only valid values are:
                BTC_MAINNET
                BTC_TESTNET3
            satoshis_per_byte (optional, int): fee to pay in satoshis/byte. If not supplied, it will be estimated for you.
            data (optional, str): string to embed in the transaction as null-data output type
            change_address (optional, str): address to send change to. If not supplied, it will default to the address you are sending from
            outputs (optional, list): (list of {'to': str, 'value': float})
                If no options are provided for BTC, a transaction will be created that consolidates your UTXOs

        Raises:
            TypeError: with bad parameter types
            ValueError: with bad parameter values

        Returns:
            The built and signed transaction
        """
        valid_networks = ["BTC_MAINNET", "BTC_TESTNET3"]
        if not isinstance(network, str):
            raise TypeError('Parameter "network" must be of type str.')
        if satoshis_per_byte is not None and not isinstance(satoshis_per_byte, float):
            raise TypeError('Parameter "satoshis_per_byte" must be of type float.')
        if data is not None and not isinstance(data, str):
            raise TypeError('Parameter "data" must be of type str.')
        if change_address is not None and not isinstance(change_address, str):
            raise TypeError('Parameter "change_address" must be of type str.')
        if outputs is not None and not isinstance(outputs, list):
            raise TypeError('Parameter "outputs" must be of type list.')
        if network not in valid_networks:
            raise ValueError('Parameter "network" must be one of {}.'.format(valid_networks))

        body = cast(dict, {"network": network, "transaction": {}})

        if outputs:
            body["transaction"]["outputs"] = outputs
        if satoshis_per_byte:
            body["transaction"]["fee"] = satoshis_per_byte
        if data:
            body["transaction"]["data"] = data
        if change_address:
            body["transaction"]["change"] = change_address
        return self.request.post("/public-blockchain-transaction", body=body)

    def create_ethereum_transaction(
        self, network: str, to: str, value: str, data: Optional[str] = None, gas_price: Optional[str] = None, gas: Optional[str] = None
    ):
        """Create and sign a public ethereum transaction using your chain's private keys

        Args:
            network (str): network to create transaction for. Only valid values are:
                ETH_MAINNET
                ETH_ROPSTEN
                ETC_MAINNET
                ETC_MORDEN

                to (hex str): the address to send to
                value (hex str): value in wei to send
                data (optional, hex str): data to publish in the transaction
                gas_price (optional, str): gas price in gwei to pay, if not supplied it will be estimated for you.
                gas (optional, str): maximum amount of gas allowed (gasLimit), if not supplied it will be estimated for you.

        Raises:
            TypeError: with bad parameter types
            ValueError: with bad parameter values

        Returns:
            The built and signed transaction
        """
        valid_networks = ["ETH_MAINNET", "ETH_ROPSTEN", "ETC_MAINNET", "ETC_MORDEN"]
        if not isinstance(network, str):
            raise TypeError('Parameter "network" must be of type str.')
        if network not in valid_networks:
            raise ValueError('Parameter "network" must be one of {}.'.format(valid_networks))
        if not isinstance(to, str):
            raise TypeError('Parameter "to" must be of type str.')
        if not isinstance(value, str):
            raise TypeError('Parameter "value" must be of type str.')
        if data is not None and not isinstance(data, str):
            raise TypeError('Parameter "data" must be of type str.')
        if gas_price is not None and not isinstance(gas_price, str):
            raise TypeError('Parameter "gas_price" must be of type str.')
        if gas is not None and not isinstance(gas, str):
            raise TypeError('Parameter "gas" must be of type str.')

        body = cast(dict, {"network": network, "transaction": {"to": to, "value": value}})

        if data:
            body["transaction"]["data"] = data
        if gas_price:
            body["transaction"]["gas_price"] = gas_price
        if gas:
            body["transaction"]["gas"] = gas

        return self.request.post("/public-blockchain-transaction", body=body)

    def get_public_blockchain_addresses(self):
        """Get interchain addresses for this Dragonchain node (L1 and L5 only)

        Returns:
            Dictionary containing addresses
        """
        return self.request.get("/public-blockchain-address")

    def get_transaction_type(self, transaction_type: str):
        """Gets information on a registered transaction type

        Args:
            transaction_type (str): transaction_type to retrieve data for

        Raises:
            TypeError: with bad parameter types

        Returns:
            parsed json response of the transaction type or None
        """
        if not isinstance(transaction_type, str):
            raise TypeError('Parameter "transaction_type" must be of type str.')
        return self.request.get("/transaction-type/{}".format(transaction_type))

    def list_transaction_types(self):
        """Lists out all registered transaction types for a chain

        Returns:
            list of registered transaction types
        """
        return self.request.get("/transaction-types")

    def update_transaction_type(self, transaction_type: str, custom_indexes: List["custom_index_type"]):
        """Updates the custom index of a given registered transaction type
        Transaction Types can optionally link custom search indexes to your transactions for easyier querying later.
        A CustomIndex is a dictionairy with two keys: 'key' and 'path'.

        key (str): The search term, on which the path will be searched.

        path(str): the JSON path of your transaction payload you would like to result form a search on the "key".

        For More details on JSONpath see https://pypi.org/project/jsonpath/

        Args:
            transaction_type (str): transaction_type to update
            custom_indexes (list): custom_indexes to update. Ex.: [{"key": "myKey", "path": "jsonPath"}]

        Raises:
            TypeError: with bad parameter types

        Returns:
            Parsed json with success message
        """
        if not isinstance(transaction_type, str):
            raise TypeError('Parameter "transaction_type" must be of type str.')
        if not isinstance(custom_indexes, list):
            raise TypeError('Parameter "custom_indexes" must be of type list.')
        params = {"version": "1", "custom_indexes": custom_indexes}
        return self.request.put("/transaction-type/{}".format(transaction_type), params)

    def create_transaction_type(self, transaction_type: str, custom_indexes: Optional[List["custom_index_type"]] = None):
        """Creates a new custom transaction type.

        Transaction Types can optionally link custom search indexes to your transactions for easyier querying later.
        A CustomIndex is a dictionairy with two keys: 'key' and 'path'.

        key (str): The search term, on which the path will be searched.

        path(str): the JSON path of your transaction payload you would like to result form a search on the "key".

        For More details on JSONpath see https://pypi.org/project/jsonpath/

        Args:
            transaction_type (str): transaction_type to update
            custom_indexes (list): custom_indexes to update. Ex.: [{"key": "myKey", "path": "jsonPath"}]

        Raises:
            TypeError: with bad parameter types

        Returns:
            Parsed json with success message
        """
        if custom_indexes is None:
            custom_indexes = []
        if not isinstance(transaction_type, str):
            raise TypeError('Parameter "transaction_type" must be of type str.')
        if custom_indexes and not isinstance(custom_indexes, list):
            raise TypeError('Parameter "custom_indexes" must be of type list.')
        params = cast(dict, {"version": "1", "txn_type": transaction_type})
        if custom_indexes:
            params["custom_indexes"] = custom_indexes
        return self.request.post("/transaction-type", params)

    def delete_transaction_type(self, transaction_type: str):
        """Deletes a transaction type registration

        Args:
            transaction_type (str): transaction_type to delete

        Raises:
            TypeError: with bad parameter types

        Returns:
            Parsed json with success message
        """
        if not isinstance(transaction_type, str):
            raise TypeError('Parameter "transaction_type" must be of type str.')
        return self.request.delete("/transaction-type/{}".format(transaction_type))


def _build_transaction_dict(transaction_type: str, payload: Union[str, dict], tag: Optional[str] = None) -> dict:
    """Build the json (dictionary) body for a transaction given its inputs

    Args:
        transaction_type (str): The transaction type for this transaction
        payload (str, dict): The intended payload for this transaction
        tag (str, optional): The intended tag for this transaction

    Raises:
        TypeError: with bad parameter types

    Returns:
        Dictionary body to use for sending as a transaction
    """
    if not isinstance(transaction_type, str):
        raise TypeError('Parameter "transaction_type" must be of type str.')
    if not isinstance(payload, str) and not isinstance(payload, dict):
        raise TypeError('Parameter "payload" must be of type dict or str.')
    if tag is not None and not isinstance(tag, str):
        raise TypeError('Parameter "tag" must be of type str.')

    body = {"version": "1", "txn_type": transaction_type, "payload": payload}
    if tag:
        body["tag"] = tag

    return body
