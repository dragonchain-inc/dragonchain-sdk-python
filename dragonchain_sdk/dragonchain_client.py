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
from dragonchain_sdk.request import Request
from dragonchain_sdk.credentials import Credentials
from dragonchain_sdk import exceptions

logger = logging.getLogger(__name__)


class Client(object):
    """Construct a new ``Client`` object

    Args:
        dragonchain_id (str): The ID of the chain to connect to.
        auth_key_id (str, optional): The authorization key ID
        auth_key (str, optional): The authorization key
        endpoint (str, optional): The endpoint of the Dragonchain
        verify (bool, optional): Verify the TLS cert of the Dragonchain
        algorithm (str, optional): The hashing algorithm used for HMAC authentication

    Returns:
        A new Dragonchain client.
    """
    def __init__(self, dragonchain_id=None, auth_key_id=None, auth_key=None, endpoint=None, verify=True, algorithm='SHA256'):
        self.credentials = Credentials(dragonchain_id, auth_key, auth_key_id, algorithm)
        self.request = Request(self.credentials, endpoint, verify)
        logger.debug('Client finished initialization')

    def override_credentials(self, auth_key=None, auth_key_id=None, dragonchain_id=None, update_endpoint=True):
        """Change dragonchain_id, auth_key or auth_key_id for this client

        Args:
            auth_key (str, optional): The authorization key
            auth_key_id (str, optional): The authorization key ID
            dragonchain_id (str, optional): The Dragonchain ID
            update_endpoint (bool, optional): If endpoint should automatically be updated for a new dragonchain_id

        Returns:
            None, sets instance variables on credentials service
        """
        if auth_key is not None:
            if isinstance(auth_key, str):
                self.credentials.auth_key = auth_key
            else:
                raise TypeError('Parameter "auth_key" must be of type str.')
        if auth_key_id is not None:
            if isinstance(auth_key, str):
                self.credentials.auth_key_id = auth_key_id
            else:
                raise TypeError('Parameter "auth_key_id" must be of type str.')
        if dragonchain_id is not None:
            if isinstance(dragonchain_id, str):
                self.credentials.dragonchain_id = dragonchain_id
                if update_endpoint is True:
                    self.request.update_endpoint()
            else:
                raise TypeError('Parameter "dragonchain_id" must be of type str.')

        logger.info('Credentials updated')

    def get_status(self):
        """Make a PUT request to a chain

        Returns:
            Returns the status of a Dragonchain
        """
        return self.request.get('/status')

    def query_contracts(self, query=None, sort=None, offset=0, limit=10):
        """Perform a query on a chain's smart contracts

        Args:
            query (str, optional): Lucene query parameter (e.g.: ``is_serial:true``)
            sort (str, optional): Sort syntax of 'field:direction' (e.g.: ``name:asc``)
            offset (int, optional): Pagination offset of query (default 0)
            limit (int, optional): Pagination limit (default 10)

        Returns:
            The results of the query
        """
        query_params = self.request.get_lucene_query_params(query, sort, offset, limit)
        return self.request.get('/contract{}'.format(query_params))

    def get_contract(self, name):
        """Perform a query on a chain's smart contracts

        Args:
            name (str): Name of the contract to get

        Returns:
            The contract searched for
        """
        if not isinstance(name, str):
            raise TypeError('Parameter "name" must be of type str.')
        return self.request.get('/contract/{}'.format(name))

    def post_library_contract(self, name, library_name, env_vars=None):
        """Post a library contract to a chain

        Args:
            name (str): Name (txn_type) of the contract to create
            library_name (str): The type of contract to be created from the library
            env_vars (dict, optional): Environment variables to set for the smart contract

        Returns:
            Success or failure object
        """
        if not isinstance(name, str):
            raise TypeError('Parameter "name" must be of type str.')
        if not isinstance(library_name, str):
            raise TypeError('Parameter "library_name" must be of type str.')
        if env_vars is not None and not isinstance(env_vars, dict):
            raise TypeError('Parameter "env_vars" must be of type dict.')
        self.check_valid_library_contract(library_name)

        body = {
            'version': '2',
            'origin': 'library',
            'name': name,
            'libraryContractName': library_name
        }
        if env_vars:
            body['custom_environment_variables'] = env_vars
        return self.request.post('/contract/{}'.format(name), body)

    def post_custom_contract(self, name, code, runtime, handler, sc_type, serial, env_vars=None):
        """Post a contract to a chain

        Args:
            name (str): Name (txn_type) of the contract to create
            code (str): Base 64 encoded zip file containing the contract code
            runtime (str): The runtime for the contract
            handler (str): The name of the entrypoint for the smart contract (file.method) i.e. 'handler.main'
            sc_type (str): cron or transaction
            serial (bool): If false, the contract will be executed in parallel. Otherwise, it will execute in a queue
            env_vars (dict, optional): Environment variables to set for the smart contract

        Returns:
            Success or failure object
        """
        if not isinstance(name, str):
            raise TypeError('Parameter "name" must be of type str.')
        if not isinstance(code, str):
            raise TypeError('Parameter "code" must be of type str.')
        if not isinstance(runtime, str):
            raise TypeError('Parameter "runtime" must be of type str.')
        if not isinstance(handler, str):
            raise TypeError('Parameter "handler" must be of type str.')
        if not isinstance(sc_type, str):
            raise TypeError('Parameter "sc_type" must be of type str.')
        if not isinstance(serial, bool):
            raise TypeError('Parameter "serial" must be of type bool.')
        if env_vars is not None and not isinstance(env_vars, dict):
            raise TypeError('Parameter "env_vars" must be of type dict.')
        self.check_runtime(runtime)
        self.check_sc_type(sc_type)

        body = {
            'version': '2',
            'origin': 'custom',
            'name': name,
            'code': code,
            'runtime': runtime,
            'sc_type': sc_type,
            'is_serial': serial,
            'handler': handler
        }
        if env_vars:
            body['custom_environment_variables'] = env_vars
        return self.request.post('/contract/{}'.format(name), body)

    def update_contract(self, name=None, status=None, sc_type=None, code=None, runtime=None, serial=None, env_vars=None):
        """Update an existing smart contract. The name and at least one optional parameter must be supplied.

        Args:
            name (str): The name of the contract to update
            status (str, optional): The status of the contract. Valid values are ``disabled`` and ``enabled``
            sc_type (str, optional): cron or transaction (immutable on library contracts)
            code (str, optional): The base 64 encoded zip file. (immutable on library contracts)
            runtime (str, optional): The runtime for the contract (immutable on library contracts)
            serial (str, optional): If false, the contract will be executed in parallel. Otherwise, it will execute in a queue (immutable on library contracts)
            env_vars (dict, optional): Environment variables to set for the smart contract (immutable on library contracts)

        Returns:
            Success or failure object
        """
        if name is None:
            raise ValueError('Parameter "name" must be be defined.')
        if name is not None and not isinstance(name, str):
            raise TypeError('Parameter "name" must be of type str.')
        if status is not None and not isinstance(status, str):
            raise TypeError('Parameter "status" must be of type str.')
        if sc_type is not None and not isinstance(sc_type, str):
            raise TypeError('Parameter "sc_type" must be of type str.')
        if code is not None and not isinstance(code, str):
            raise TypeError('Parameter "code" must be of type str.')
        if runtime is not None and not isinstance(runtime, str):
            raise TypeError('Parameter "runtime" must be of type str.')
        if serial is not None and not isinstance(serial, bool):
            raise TypeError('Parameter "serial" must be of type bool.')
        if env_vars is not None and not isinstance(env_vars, dict):
            raise TypeError('Parameter "env_vars" must be of type dict.')

        body = {}
        if status is not None:
            body['status'] = status
        if sc_type is not None:
            self.check_sc_type(sc_type)
            body['sc_type'] = sc_type
        if code is not None:
            body['code'] = code
        if runtime is not None:
            self.check_runtime(runtime)
            body['runtime'] = runtime
        if serial is not None:
            body['serial'] = serial
        if env_vars is not None:
            body['custom_environment_variables'] = env_vars

        if not body:
            raise exceptions.EmptyUpdateException('No valid parameters were provided')

        return self.request.put('/contract/{}'.format(name), body)

    def query_transactions(self, query=None, sort=None, offset=0, limit=10):
        """Perform a query on a chain's transactions

        Args:
            query (str, optional): Lucene query parameter (e.g.: ``is_serial:true``)
            sort (str, optional): Sort syntax of 'field:direction' (e.g.: ``txn_type:asc``)
            offset (int, optional): Pagination offset of query (default 0)
            limit (int, optional): Pagination limit (default 10)

        Returns:
            The results of the query
        """
        query_params = self.request.get_lucene_query_params(query, sort, offset, limit)
        return self.request.get('/transaction{}'.format(query_params))

    def get_transaction(self, txn_id):
        """Get a specific transaction by id

        Args:
            txn_id (str, uuid): ID of the transaction to get

        Returns:
            The transaction searched for
        """
        if not isinstance(txn_id, str):
            raise TypeError('Paramter "txn_id" must be of type str.')
        return self.request.get('/transaction/{}'.format(txn_id))

    def post_transaction(self, txn_type, payload, tag=None):
        """Post a transaction to a chain

        Args:
            txn_type (str): Type of transaction
            payload (dict or string): The payload of the transaction
            tag (str, optional): A tag string to search on

        Returns:
            Transaction ID on success
        """
        return self.request.post('/transaction', Client.build_transaction_dict(txn_type, payload, tag))

    def post_transaction_bulk(self, txn_list):
        """Post many transactions to a chain at once, over a single connnection

        Args:
            txn_list (list): List of transaction dictionaries. Schema: ``{'txn_type': 'str', 'payload': 'str or dict', 'tag': 'str (optional)'}``

        Returns:
            List of succeeded transaction id's and list of failed transactions
        """
        if not isinstance(txn_list, list):
            raise TypeError('Parameter "txn_list" must be of type list.')

        post_data = []

        for txn in txn_list:
            if not isinstance(txn, dict):
                raise TypeError('All items in parameter "txn_list" must be of type dict.')
            post_data.append(Client.build_transaction_dict(txn.get('txn_type'), txn.get('payload'), txn.get('tag')))

        return self.request.post('/transaction_bulk', post_data)

    @staticmethod
    def build_transaction_dict(txn_type, payload, tag=None):
        if not isinstance(txn_type, str):
            raise TypeError('Parameter "txn_type" must be of type str.')
        if not isinstance(payload, str) and not isinstance(payload, dict):
            raise TypeError('Parameter "payload" must be of type dict or str.')
        if tag is not None and not isinstance(tag, str):
            raise TypeError('Parameter "tag" must be of type str.')

        body = {
            'version': '1',
            'txn_type': txn_type,
            'payload': payload
        }
        if tag:
            body['tag'] = tag

        return body

    def query_blocks(self, query=None, sort=None, offset=0, limit=10):
        """Perform a query on a chain's blocks

        Args:
            query (str, optional): Lucene query parameter (e.g.: ``is_serial:true``)
            sort (str, optional): Sort syntax of 'field:direction' (e.g.: ``block_id:asc``)
            offset (int, optional): Pagination offset of query (default 0)
            limit (int, optional): Pagination limit (default 10)

        Returns:
            The results of the query
        """
        query_params = self.request.get_lucene_query_params(query, sort, offset, limit)
        return self.request.get('/block{}'.format(query_params))

    def get_block(self, block_id):
        """Get a specific block by id

        Args:
            block_id (int): ID of the block to get

        Returns:
            The block searched for
        """
        if not isinstance(block_id, str) and not isinstance(block_id, int):
            raise TypeError('Parameter "block_id" must be of type str or int.')
        return self.request.get('/block/{}'.format(block_id))

    def get_verification(self, block_id, level=None):
        """Get higher level block verifications by level 1 block id

        Args:
            block_id (int): ID of the block to get
            level (int): Level of verifications to get (valid values are 2, 3, 4 and 5)

        Returns:
            Higher level block verifications
        """
        if not isinstance(block_id, str) and not isinstance(block_id, int):
            raise TypeError('Parameter "block_id" must be of type str.')
        if level is not None:
            if not isinstance(level, int) and not isinstance(level, str):
                raise TypeError('Parameter "level" must be of type str or int.')
            if int(level) not in [2, 3, 4, 5]:
                raise ValueError('Parameter "level" must be between 2 and 5 inclusive.')
            return self.request.get('/verifications/{}?level={}'.format(block_id, level))
        return self.request.get('/verifications/{}'.format(block_id))

    def get_sc_heap(self, sc_name=None, key=None):
        """Retrieve data from the heap storage of a smart contract
        Note: When ran in an actual smart contract, sc_name will be pulled automatically from the environment if not explicitly provided

        Args:
            key (str): The key stored in the heap to retrieve
            sc_name (str, optional): The name of the smart contract, optional if called from within a smart contract

        Returns:
            The value of the object in the heap
        """
        if not isinstance(key, str):
            raise TypeError('Parameter "key" must be of type str.')
        if sc_name is None:
            sc_name = os.environ.get('SMART_CONTRACT_NAME')
        if not isinstance(sc_name, str):
            raise TypeError('Parameter "sc_name" must be of type str.')
        return self.request.get('/get/{}/{}'.format(sc_name, key), parse_response=False)

    def list_sc_heap(self, sc_name=None, folder=None):
        """Lists all objects stored in a smart contracts heap
        Note: When ran in an actual smart contract, sc_name will be pulled automatically from the environment if not explicitly provided

        Args:
            sc_name (str, optional): sc_name heap to list. If not provided explicitly, it must be in the SMART_CONTRACT_NAME env var
            folder (str, optional): the folder to list in the heap. If not provided, it will default to the root of the heap

        Returns:
            Parsed json response from the chain
        """
        if sc_name is None:
            sc_name = os.environ.get('SMART_CONTRACT_NAME')
        if not isinstance(sc_name, str):
            raise TypeError('Parameter "sc_name" must be of type str.')
        if folder is not None:
            if not isinstance(folder, str):
                raise TypeError('Parameter "folder" must be of type str.')
            if folder.endswith('/'):
                raise ValueError('Parameter "folder" cannot end with /.')
            return self.request.get('/list/{}/{}/'.format(sc_name, folder))
        return self.request.get('/list/{}/'.format(sc_name))

    def get_transaction_type(self, transaction_type):
        """Gets information on a registered transaction type

        Args:
            transaction_type (str): transaction_type to retrieve data for

        Returns:
            parsed json response of the transaction type or None
        """
        if not isinstance(transaction_type, str):
            raise TypeError('Parameter "transaction_type" must be of type str.')
        return self.request.get('/transaction-type/{}'.format(transaction_type))

    def list_transaction_types(self):
        """Lists out all registered transaction types for a chain

        Returns:
            list of registered transaction types
        """
        return self.request.get('/transaction-types')

    def update_transaction_type(self, transaction_type, custom_indexes=None):
        """Updates the custom index of a given registered transaction type

        Args:
            transaction_type (str): transaction_type to update
            custom_indexes (list): custom_indexes to update

        Returns:
            Parsed json with success message
        """
        if custom_indexes is None:
            custom_indexes = []
        if not isinstance(transaction_type, str):
            raise TypeError('Parameter "transaction_type" must be of type str.')
        if not isinstance(custom_indexes, list):
            raise TypeError('Parameter "custom_indexes" must be of type list.')
        params = {"version": "1", "custom_indexes": custom_indexes}
        return self.request.put('/transaction-type/{}'.format(transaction_type), params)

    def register_transaction_type(self, transaction_type, custom_indexes=None):
        """Registers a new custom index

        Args:
            transaction_type (str): transaction_type to update
            custom_indexes (list): custom_indexes to update

        Returns:
            Parsed json with success message
        """
        if not isinstance(transaction_type, str):
            raise TypeError('Parameter "transaction_type" must be of type str.')
        if custom_indexes and not isinstance(custom_indexes, list):
            raise TypeError('Parameter "custom_indexes" must be of type list.')
        params = {"version": "1", "txn_type": transaction_type}
        if custom_indexes:
            params['custom_indexes'] = custom_indexes
        return self.request.post('/transaction-type', params)

    def delete_transaction_type(self, transaction_type):
        """Deletes a transaction type registration

        Args:
            transaction_type (str): transaction_type to delete

        Returns:
            Parsed json with success message
        """
        if not isinstance(transaction_type, str):
            raise TypeError('Parameter "transaction_type" must be of type str.')
        return self.request.delete('/transaction-type/{}'.format(transaction_type))

    @staticmethod
    def check_valid_library_contract(contract):
        if contract not in [
            'currency',
            'interchainWatcher',
            'neoWatcher',
            'btcWatcher',
            'ethereumPublisher',
            'neoPublisher',
            'btcPublisher'
        ]:
            raise ValueError('Parameter "library_contract" not found in list of valid contracts.')

    @staticmethod
    def check_runtime(runtime):
        """Checks if a runtime string is valid

        Args:
            runtime (str): runtime to validate

        Returns:
            True if valid, False if invalid
        """
        if runtime not in [
            'nodejs6.10',
            'nodejs8.10',
            'java8',
            'python2.7',
            'python3.6',
            'dotnetcore1.0',
            'dotnetcore2.0',
            'dotnetcore2.1',
            'go1.x'
        ]:
            raise ValueError('Parameter "runtime" not found in valid runtime list.')

    @staticmethod
    def check_sc_type(sc_type):
        """Checks if a smart contract type string is valid

        Args:
            sc_type (str): sc_type to validate

        Raises:
            ValueError if the type is invalid.
        """
        if sc_type not in ['transaction', 'cron']:
            raise ValueError('Parameter "sc_type" not found in valid list.')
