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

    def get_secret(self, secret_name):
        """Gets secrets for smart contracts

        Args:
            secret_name (str): name of the secret to retrieve
        Returns:
            Returns the secret from the file location
        """
        if not isinstance(secret_name, str):
            raise TypeError('Parameter "secret_name" must be of type str.')
        if not os.environ.get('SMART_CONTRACT_ID'):
            raise RuntimeError('Missing "SMART_CONTRACT_ID" from environment')
        path = os.path.join(os.path.abspath(os.sep), 'var', 'openfaas', 'secrets', 'sc-{}-{}'.format(os.environ.get('SMART_CONTRACT_ID'), secret_name))
        return open(path, 'r').read()

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

    def get_contract(self, contract_id=None, txn_type=None):
        """Perform a query on a chain's smart contracts

        Args:
            contract_id (str, exclusive): Id of the contract to get
            txn_type (str, exclusive): Name of the contract to get

        Returns:
            The contract returned from the request
        """
        if contract_id is not None and not isinstance(contract_id, str):
            raise TypeError('Parameter "contract_id" must be of type str.')
        if txn_type is not None and not isinstance(txn_type, str):
            raise TypeError('Parameter "txn_type" must be of type str.')
        if contract_id and txn_type:
            raise TypeError('Only one of "contract_id" and "txn_type" can be specified')
        if contract_id:
            return self.request.get('/contract/{}'.format(contract_id))
        elif txn_type:
            return self.request.get('/contract/txn_type/{}'.format(txn_type))
        else:
            raise TypeError('At least one of "contract_id" or "txn_type" must be specified')

    def post_contract(self, txn_type, execution_order, image, cmd, args=None, env=None, secrets=None, seconds=None, cron=None, auth=None):
        """Post a contract to a chain

        Args:
            txn_type (str): txn_type of the contract to create
            execution_order (string): Order of execution. Valid values are 'serial' or 'parallel'
            image (str): Docker image containing the smart contract logic
            cmd (str): Entrypoint command to run in the docker container
            args (list, optional): List of arguments to the cmd field
            env (dict, optional): dict mapping of environment variables for your contract runtime
            secrets (dict, optional): dict mapping of secrets for your contract runtime
            seconds (string, optional): The seconds of scheduled execution in seconds
            cron (string, optional): The rate of scheduled execution specified as a cron
            auth (string, optional): basic-auth for pulling docker images, base64 encoded (e.g. username:password)

        Returns:
            Success or failure object
        """
        if not isinstance(txn_type, str):
            raise TypeError('Parameter "txn_type" must be of type str.')
        if not isinstance(image, str):
            raise TypeError('Parameter "image" must be of type str.')
        if not isinstance(cmd, str):
            raise TypeError('Parameter "cmd" must be of type str.')
        if not isinstance(execution_order, str):
            raise TypeError('Parameter "execution_order" must be of type str.')
        if args is not None and not isinstance(args, list):
            raise TypeError('Parameter "args" must be of type list.')
        if env is not None and not isinstance(env, dict):
            raise TypeError('Parameter "env" must be of type dict.')
        if secrets is not None and not isinstance(secrets, dict):
            raise TypeError('Parameter "secrets" must be of type dict.')
        if seconds is not None and not isinstance(seconds, int):
            raise TypeError('Parameter "seconds" must be of type int.')
        if cron is not None and not isinstance(cron, str):
            raise TypeError('Parameter "cron" must be of type str.')
        if auth is not None and not isinstance(auth, str):
            raise TypeError('Parameter "auth" must be of type str.')

        body = {
            'version': '3',
            'txn_type': txn_type,
            'image': image,
            'cmd': cmd,
            'execution_order': execution_order
        }
        if env:
            body['env'] = env
        if args:
            body['args'] = args
        if secrets:
            body['secrets'] = secrets
        if seconds:
            body['seconds'] = seconds
        if cron:
            body['cron'] = cron
        if auth:
            body['auth'] = auth
        return self.request.post('/contract', body)

    def update_contract(self, contract_id, execution_order=None, image=None, cmd=None, args=None, desired_state=None, env={}, secrets={}, seconds=None, cron=None, auth=None):
        """Update an existing smart contract. The contract_id and at least one optional parameter must be supplied.

        Args:
            contract_id (str): contract_id of the contract to create
            execution_order (string): Order of execution. Valid values are 'serial' or 'parallel'
            image (str): Docker image containing the smart contract logic
            cmd (str): Entrypoint command to run in the docker container
            args (list, optional): List of arguments to the cmd field
            desired_state (str, optional): Change the state of a contract. Valid values are "active" and "inactive". You may only change the state of an active or inactive contract.
            env (dict, optional): dict mapping of environment variables for your contract runtime
            secrets (dict, optional): dict mapping of secrets for your contract runtime
            seconds (int, optional): The seconds of scheduled execution in seconds
            cron (string, optional): The rate of scheduled execution specified as a cron
            auth (string, optional): basic-auth for pulling docker images, base64 encoded (e.g. username:password)

        Returns:
            Success or failure object
        """
        if not isinstance(contract_id, str):
            raise TypeError('Parameter "contract_id" must be of type str.')
        if image is not None and not isinstance(image, str):
            raise TypeError('Parameter "image" must be of type str.')
        if cmd is not None and not isinstance(cmd, str):
            raise TypeError('Parameter "cmd" must be of type str.')
        if execution_order is not None and not isinstance(execution_order, str):
            raise TypeError('Parameter "execution_order" must be of type str.')
        if desired_state is not None and not isinstance(desired_state, str):
            raise TypeError('Parameter "desired_state" must be of type str.')
        if args is not None and not isinstance(args, list):
            raise TypeError('Parameter "args" must be of type list.')
        if env is not None and not isinstance(env, dict):
            raise TypeError('Parameter "env" must be of type dict.')
        if secrets is not None and not isinstance(secrets, dict):
            raise TypeError('Parameter "secrets" must be of type dict.')
        if seconds is not None and not isinstance(seconds, int):
            raise TypeError('Parameter "seconds" must be of type int.')
        if cron is not None and not isinstance(cron, str):
            raise TypeError('Parameter "cron" must be of type str.')
        if auth is not None and not isinstance(auth, str):
            raise TypeError('Parameter "auth" must be of type str.')

        body = {
            'version': '3'
        }
        if image:
            body['image'] = image
        if cmd:
            body['cmd'] = cmd
        if execution_order:
            body['execution_order'] = execution_order
        if desired_state:
            body['desired_state'] = desired_state
        if args:
            body['args'] = args
        if env:
            body['env'] = env
        if secrets:
            body['secrets'] = secrets
        if seconds:
            body['seconds'] = seconds
        if cron:
            body['cron'] = cron
        if auth:
            body['auth'] = auth

        return self.request.put('/contract/{}'.format(contract_id), body)

    def delete_contract(self, contract_id):
        """Delete an existing contract

        Args:
            contract_id (str): Transaction type of the contract to delete

        Returns:
            The results of the delete request
        """
        if not isinstance(contract_id, str):
            raise TypeError('Parameter "state" must be of type str.')
        return self.request.delete('/contract/{}'.format(contract_id), body={})

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

    def get_sc_heap(self, sc_id=None, key=None):
        """Retrieve data from the heap storage of a smart contract
        Note: When ran in an actual smart contract, sc_id will be pulled automatically from the environment if not explicitly provided

        Args:
            key (str): The key stored in the heap to retrieve
            sc_id (str, optional): The ID of the smart contract, optional if called from within a smart contract

        Returns:
            The value of the object in the heap
        """
        if not isinstance(key, str):
            raise TypeError('Parameter "key" must be of type str.')
        if sc_id is None:
            sc_id = os.environ.get('SMART_CONTRACT_ID')
        if not isinstance(sc_id, str):
            raise TypeError('Parameter "sc_id" must be of type str.')
        return self.request.get('/get/{}/{}'.format(sc_id, key), parse_response=False)

    def list_sc_heap(self, sc_id=None, folder=None):
        """Lists all objects stored in a smart contracts heap
        Note: When ran in an actual smart contract, sc_id will be pulled automatically from the environment if not explicitly provided

        Args:
            sc_id (str, optional): sc_id heap to list. If not provided explicitly, it must be in the SMART_CONTRACT_NAME env var
            folder (str, optional): the folder to list in the heap. If not provided, it will default to the root of the heap

        Returns:
            Parsed json response from the chain
        """
        if sc_id is None:
            sc_id = os.environ.get('SMART_CONTRACT_ID')
        if not isinstance(sc_id, str):
            raise TypeError('Parameter "sc_id" must be of type str.')
        if folder is not None:
            if not isinstance(folder, str):
                raise TypeError('Parameter "folder" must be of type str.')
            if folder.endswith('/'):
                raise ValueError('Parameter "folder" cannot end with /.')
            return self.request.get('/list/{}/{}/'.format(sc_id, folder))
        return self.request.get('/list/{}/'.format(sc_id))

    def create_public_blockchain_transaction(self, network, transaction):
        """Create and sign a public blockchain transaction using your chain's private keys

        Args:
            network (str): network to create transaction for. Some valid values are:
                BTC_MAINNET
                BTC_TESTNET3
                ETH_MAINNET
                ETH_ROPSTEN
                ETC_MAINNET
                ETC_MORDEN

            transaction (dict): A dictionary representing the transaction to create
                BTC: {
                    "outputs": (array of {'to': str, 'value': float}, optional)
                    "fee": (optional, int) fee to pay in satoshis/byte. If not supplied, it will be estimated for you.
                    "data": (optional, str) string to embed in the transaction as null-data output type
                    "change": (optional, str) address to send change to. If not supplied, it will default to the address you are sending from
                }

                If no options are provided for BTC, a transaction will be created that consolidates your UTXOs

                ETH/ETC: {
                    "to": (hex str) the address to send to
                    "value": (hex str) value in wei to send
                    "data": (optional, hex str) data to publish in the transaction
                    "gasPrice": (optional, str) gas price in gwei to pay, if not supplied it will be estimated for you.
                    "gas": (optional, str) maximum amount of gas allowed (gasLimit), if not supplied it will be estimated for you.
                }

        Returns:
            The built and signed transaction
        """
        valid_networks = ['BTC_MAINNET', 'BTC_TESTNET3', 'ETH_MAINNET', 'ETH_ROPSTEN', 'ETC_MAINNET', 'ETC_MORDEN']
        if not isinstance(network, str):
            raise TypeError('Parameter "network" must be of type str.')
        if not isinstance(transaction, dict):
            raise TypeError('Parameter "transaction" must be of type str.')
        if network not in valid_networks:
            raise ValueError('Parameter "network" must be one of {}.'.format(valid_networks))

        body = {
            'network': network,
            'transaction': transaction
        }
        return self.request.post('/public-blockchain-transaction', body=body)

    def get_public_blockchain_addresses(self):
        """Get interchain addresses for this Dragonchain node (L1 and L5 only)

        Returns:
            Dictionary containing addresses

        """
        return self.request.get('/public-blockchain-address')

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
        return self.request.delete('/transaction-type/{}'.format(transaction_type), body={})
