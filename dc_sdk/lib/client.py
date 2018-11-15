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

import os
import re
from configparser import ConfigParser
from pathlib import Path
from dc_sdk.lib.request import make_request, get_lucene_query_params
from dc_sdk.lib.auth import get_supported_hash

valid_runtimes = [
    'nodejs6.10',
    'nodejs8.10',
    'java8',
    'python2.7',
    'python3.6',
    'dotnetcore1.0',
    'dotnetcore2.0',
    'dotnetcore2.1',
    'go1.x'
]

valid_sc_types = [
    'transaction',
    'cron'
]

valid_contract_libraries = [
    'currency',
    'ethereum_interchain_watcher',
    'neo_interchain_watcher',
    'bitcoin_interchain_watcher',
    'private_billing_watcher',
    'private_negative_balance_currency',
    'ethereum_publisher',
    'neo_Publisher',
    'bitcoin_publisher'
]


def get_credential_file_path():
    """
    Get the path for the credential file depending on the OS
    :return: string of the credential file path
    """
    if os.name == 'nt':
        return os.path.join(os.path.expandvars('%LOCALAPPDATA%'), 'dragonchain', 'credentials')
    else:
        return os.path.join(Path.home(), '.dragonchain', 'credentials')


def get_auth_key(dragonchain_id=None, auth_key=None, auth_key_id=None):
    """
    Get an auth_key/auth_key_id pair
    First checks parameters, then environment, then configuration files
    :type dragonchain_id: string
    :param dragonchain_id: (optional) dragonchain_id to get keys for (it pulling from config files)
    :type auth_key_id: string
    :param auth_key_id: (optional) Dragonchain authorization key ID
    :type auth_key: string
    :param auth_key: (optional) Dragonchain authorization key
    :return: Tuple where index 0 is the auth_key_id and index 1 is the auth_key
    """
    # if both key/keyid aren't passed in, check environment/credentials file
    if auth_key is None or auth_key_id is None:
        auth_key = os.environ.get('DRAGONCHAIN_AUTH_KEY')
        auth_key_id = os.environ.get('DRAGONCHAIN_AUTH_KEY_ID')
        if auth_key is None or auth_key_id is None:
            # If both keys aren't in environment variables, check config file
            if dragonchain_id is None:
                raise RuntimeError('Could not locate credentials for this client')
            config = ConfigParser()
            config.read(get_credential_file_path())
            try:
                auth_key = config.get(dragonchain_id, 'auth_key')
                auth_key_id = config.get(dragonchain_id, 'auth_key_id')
                return auth_key_id, auth_key
            except Exception:
                raise RuntimeError('Could not locate credentials for this client')
        else:
            return auth_key_id, auth_key
    else:
        if not isinstance(auth_key, str) or not isinstance(auth_key_id, str):
            raise ValueError('auth_key and auth_key_id must be specified as a strings')
        return auth_key_id, auth_key


def get_dragonchain_id(dragonchain_id=None):
    """
    Get the dragonchain id
    First checks parameters, then environment, then configuration files
    :type dragonchain_id: None or string
    :param dragonchain_id: (optional) the dragonchain id to check
    :return: String of the dragonchain id
    """
    dcid = ''
    if dragonchain_id is None:
        # Check environment variable if ID isn't provided explicitly
        dcid = os.environ.get('DRAGONCHAIN_ID')
        if dcid is None:
            # Check config ini file if ID isn't provided explicitly or in environment
            config = ConfigParser()
            config.read(get_credential_file_path())
            try:
                dcid = config.get('default', 'dragonchain_id')
            except Exception:
                raise RuntimeError('Could not locate credentials for this client')
    else:
        if not isinstance(dragonchain_id, str):
            raise ValueError('If provided, dragonchain_id must be a string')
        dcid = dragonchain_id
    dcid = dcid.lower()
    # Check to see if dragonchain id looks valid (is a UUIDv4)
    if re.fullmatch(r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$', dcid):
        return dcid
    raise ValueError('Dragonchain id ({}) does not appear to be valid id'.format(dcid))


def generate_dragonchain_endpoint(dragonchain_id):
    """
    Generate a dragonchain endpoint for a chain hosted by Dragonchain Inc
    :type dragonchain_id: string
    :param dragonchain_id: dragonchain id to generate the endpoint for
    :return: String of the dragonchain endpoint
    """
    return 'https://{}.api.dragonchain.com'.format(dragonchain_id)


def is_valid_runtime(runtime):
    """
    Checks if a runtime string is valid
    :type runtime: string
    :param runtime: runtime to validate
    :return: boolean if runtime is valid
    """
    if runtime not in valid_runtimes:
        return False
    return True


def is_valid_sc_type(sc_type):
    """
    Checks if a smart contract type string is valid
    :type sc_type: string
    :param sc_type: sc_type to validate
    :return: boolean if sc_type is valid
    """
    if sc_type not in valid_sc_types:
        return False
    return True


def check_print_curl(print_curl):
    """
    Simple function to check if print_curl is a boolean, raise if not
    :type print_curl: boolean
    :param print_curl: print_curl variable to check
    :return: Nothing
    """
    if not isinstance(print_curl, bool):
        raise ValueError('if provided, print_curl must be a boolean')


class Client(object):
    """
    A client that interfaces all functionality to a dragonchain with a given id and key
    """
    def __init__(self, dragonchain_id=None, auth_key_id=None,
                 auth_key=None, endpoint=None, verify=True,
                 algorithm='SHA256'):
        """
        Construct a new 'Client' object
        :type dragonchain_id: string
        :param dragonchain_id: (optional) dragonchain id to associate with this client
        :type auth_key_id: string
        :param auth_key_id: (optional) Dragonchain authorization key ID
        :type auth_key: string
        :param auth_key: (optional) Dragonchain authorization key
        :type endpoint: string
        :param endpoint: (optional) Endpoint of the dragonchain
        :type verify: boolean
        :param verify: (optional) Verify the TLS certificate of the dragonchain
        :type algorithm: string
        :param algorithm: (optional) hashing algorithm to use for hmac authentication
        """
        self.dcid = get_dragonchain_id(dragonchain_id)
        self.auth_key_id, self.auth_key = get_auth_key(self.dcid, auth_key, auth_key_id)
        if endpoint is None:
            self.endpoint = generate_dragonchain_endpoint(self.dcid)
        else:
            if not isinstance(endpoint, str):
                raise ValueError('endpoint must be specified as a string')
            self.endpoint = endpoint
        if not isinstance(verify, bool):
            raise ValueError('verify must be specified as a boolean')
        self.verify = verify
        if not isinstance(algorithm, str):
            raise ValueError('algorithm must be specified as a string')
        # Check if the provided algorithm is supported by calling to get SupportedHash enum
        get_supported_hash(algorithm)
        self.algorithm = algorithm

    def perform_get(self, path, parse_json=True, print_curl=False):
        """
        Make a GET request for this chain
        :type path: string
        :param path: path of the request (including any path query parameters)
        :type parse_json: boolean
        :param parse_json: if the return from the chain should be parsed as json
        :type print_curl: boolean
        :param print_curl: if set to true, rather than making a request, the sdk will instead print the equivalent cURL cli command to make the request instead
        :return: response of the get request
        """
        check_print_curl(print_curl)
        return make_request(endpoint=self.endpoint, auth_key=self.auth_key,
                            auth_key_id=self.auth_key_id, dcid=self.dcid,
                            http_verb='GET', path=path, verify=self.verify,
                            parse_json=parse_json, algorithm=self.algorithm,
                            print_curl=print_curl)

    def perform_post(self, path, body, parse_json=True, print_curl=False):
        """
        Make a json body POST request for this chain
        :type path: string
        :param path: path of the request (including any path query parameters)
        :type body: JSON serializable dictionary
        :param body: body of the request as a python dictionary
        :type parse_json: boolean
        :param parse_json: if the return from the chain should be parsed as json
        :type print_curl: boolean
        :param print_curl: if set to true, rather than making a request, the sdk will instead print the equivalent cURL cli command to make the request instead
        :return: response of the post request
        """
        check_print_curl(print_curl)
        return make_request(endpoint=self.endpoint, auth_key=self.auth_key,
                            auth_key_id=self.auth_key_id, dcid=self.dcid,
                            http_verb='POST', path=path, verify=self.verify,
                            json=body, parse_json=parse_json, algorithm=self.algorithm,
                            print_curl=print_curl)

    def perform_put(self, path, body, parse_json=True, print_curl=False):
        """
        Make a json body PUT request for this chain
        :type path: string
        :param path: path of the request (including any path query parameters)
        :type body: JSON serializable dictionary
        :param body: body of the request as a python dictionary
        :type parse_json: boolean
        :param parse_json: if the return from the chain should be parsed as json
        :type print_curl: boolean
        :param print_curl: if set to true, rather than making a request, the sdk will instead print the equivalent cURL cli command to make the request instead
        :return: response of the put request
        """
        check_print_curl(print_curl)
        return make_request(endpoint=self.endpoint, auth_key=self.auth_key,
                            auth_key_id=self.auth_key_id, dcid=self.dcid,
                            http_verb='PUT', path=path, verify=self.verify,
                            json=body, parse_json=parse_json, algorithm=self.algorithm,
                            print_curl=print_curl)

    def get_status(self, print_curl=False):
        """
        Get the status of a dragonchain
        :type print_curl: boolean
        :param print_curl: if set, print the cli cURL command to make the request without actually calling the chain
        :return: Parsed json response from the chain
        """
        return self.perform_get('/chains/status', print_curl=print_curl)

    def query_contracts(self, query=None, sort=None, offset=0, limit=10, print_curl=False):
        """
        Preform a query on a chain's smart contracts
        :type query: string
        :param query: lucene query parameter (i.e.: is_serial:true)
        :type sort: string
        :param sort: sort syntax of 'field:direction' (i.e.: name:asc)
        :type offset: integer
        :param offset: pagination offset of query (default 0)
        :type limit: integer
        :param limit: pagination limit (default 10)
        :type print_curl: boolean
        :param print_curl: if set, print the cli cURL command to make the request without actually calling the chain
        :return: Parsed json response from the chain
        """
        query_params = get_lucene_query_params(query, sort, offset, limit)
        return self.perform_get('/chains/contract{}'.format(query_params), print_curl=print_curl)

    def get_contract(self, name, print_curl=False):
        """
        Get a specific smart contract
        :type name: string
        :param name: name of the smart contract to get
        :type print_curl: boolean
        :param print_curl: if set, print the cli cURL command to make the request without actually calling the chain
        :return: Parsed json response from the chain
        """
        if not isinstance(name, str):
            raise ValueError('Smart contract name must be a string')
        return self.perform_get('/chains/contract/{}'.format(name), print_curl=print_curl)

    def post_library_contract(self, name, library_name, env_vars=None, print_curl=False):
        """
        Post a library contract to a chain
        :type name: string
        :param name: name of the contract to create
        :type library_name: string
        :param library_name: the type of contract to be created from the library
        :type env_vars: dictionary
        :param env_vars: environment variables to set for the smart contract
        :type print_curl: boolean
        :param print_curl: if set, print the cli cURL command to make the request without actually calling the chain
        :return: Parsed json response from the chain
        """
        if not isinstance(name, str):
            raise ValueError('name must be a string')
        if not isinstance(library_name, str) or library_name not in valid_contract_libraries:
            raise ValueError('library_name must be a string and a valid contract library from this list: {}'.format(valid_contract_libraries))
        if env_vars and not isinstance(env_vars, dict):
            raise ValueError('env_vars must be a dictionary if set')
        body = {
            'version': '2',
            'origin': 'library',
            'name': name,
            'libraryContractName': library_name
        }
        if env_vars:
            body['custom_environment_variables'] = env_vars
        return self.perform_post('/chains/contract', body, print_curl=print_curl)

    def post_custom_contract(self, name, code, runtime, sc_type, serial, env_vars=None, print_curl=False):
        """
        Post a custom contract to a chain
        :type name: string
        :param name: name of the contract to create
        :type code: string
        :param code: base64 encoded zip of the code
        :type env_vars: dictionary
        :param env_vars: environment variables to set for the smart contract
        :type runtime: string
        :param runtime: string of the runtime for this smart contract
        :type sc_type: string
        :param sc_type: how the smart contract is invoked ('transaction' or 'cron')
        :type serial: boolean
        :param serial: whether or not the smart contract must be executed in serial
        :type print_curl: boolean
        :param print_curl: if set, print the cli cURL command to make the request without actually calling the chain
        :return: Parsed json response from the chain
        """
        if not isinstance(name, str):
            raise ValueError('name must be a string')
        if not isinstance(code, str):
            raise ValueError('code must be a string')
        if not isinstance(runtime, str) or not is_valid_runtime(runtime):
            raise ValueError('runtime must be a string and valid runtime from this list: {}'.format(valid_runtimes))
        if not isinstance(sc_type, str) or not is_valid_sc_type(sc_type):
            raise ValueError('sc_type must be either "transaction" or "cron"')
        if not isinstance(serial, bool):
            raise ValueError('serial must be a boolean')
        if env_vars and not isinstance(env_vars, dict):
            raise ValueError('env_vars must be a dictionary if set')
        body = {
            'version': '2',
            'origin': 'custom',
            'name': name,
            'code': code,
            'runtime': runtime,
            'sc_type': sc_type,
            'is_serial': serial
        }
        if env_vars:
            body['custom_environment_variables'] = env_vars
        return self.perform_post('/chains/contract', body, print_curl=print_curl)

    def update_contract(self, name, status, sc_type, code, runtime, serial, env_vars=None, print_curl=False):
        """
        Update an existing smart contract
        :type name: string
        :param name: the name of the contract you are updating
        :type status: string
        :param status: status of the contract
        :type sc_type: string
        :param sc_type: how the smart contract is invoked ('transaction' or 'cron')
        :type code: string
        :param code: base64 encoded zip of the code
        :type runtime: string
        :param runtime: string of the runtime for this smart contract
        :type serial: boolean
        :param serial: whether or not the smart contract must be executed in serial
        :type env_vars: dictionary
        :param env_vars: environment variables to set for the smart contract
        :type print_curl: boolean
        :param print_curl: if set, print the cli cURL command to make the request without actually calling the chain
        :return: Parsed json response from the chain
        """
        if not isinstance(name, str):
            raise ValueError('name must be a string')
        if not isinstance(status, str):
            raise ValueError('status must be a string')
        if not isinstance(sc_type, str) or not is_valid_sc_type(sc_type):
            raise ValueError('sc_type must be either "transaction" or "cron"')
        if not isinstance(code, str):
            raise ValueError('code must be a string')
        if not isinstance(runtime, str) or not is_valid_runtime(runtime):
            raise ValueError('runtime must be a string and valid runtime from this list: {}'.format(valid_runtimes))
        if not isinstance(serial, bool):
            raise ValueError('serial must be a boolean')
        if env_vars and not isinstance(env_vars, dict):
            raise ValueError('env_vars must be a dictionary if set')
        body = {
            'version': '1',
            'name': name,
            'status': status,
            'sc_type': sc_type,
            'code': code,
            'runtime': runtime,
            'is_serial': serial
        }
        if env_vars:
            body['custom_environment_variables'] = env_vars
        return self.perform_put('/chains/contract', body, print_curl=print_curl)

    def query_transactions(self, query=None, sort=None, offset=0, limit=10, print_curl=False):
        """
        Preform a query on a chain's transactions
        :type query: string
        :param query: lucene query parameter (i.e.: is_serial:true)
        :type sort: string
        :param sort: sort syntax of 'field:direction' (i.e.: name:asc)
        :type offset: integer
        :param offset: pagination offset of query (default 0)
        :type limit: integer
        :param limit: pagination limit (default 10)
        :type print_curl: boolean
        :param print_curl: if set, print the cli cURL command to make the request without actually calling the chain
        :return: Parsed json response from the chain
        """
        query_params = get_lucene_query_params(query, sort, offset, limit)
        return self.perform_get('/chains/transaction{}'.format(query_params), print_curl=print_curl)

    def get_transaction(self, txn_id, print_curl=False):
        """
        Get a specific transaction by id
        :type txn_id: string
        :param txn_id: transaction id to get
        :type print_curl: boolean
        :param print_curl: if set, print the cli cURL command to make the request without actually calling the chain
        :return: Parsed json response from the chain
        """
        if not isinstance(txn_id, str):
            raise ValueError('txn_id must be a string')
        return self.perform_get('/chains/transaction/{}'.format(txn_id), print_curl=print_curl)

    def post_transaction(self, txn_type, payload, tag=None, print_curl=False):
        """
        Post a transaction to a chain
        :type txn_type: string
        :param txn_type: the transaction type to create
        :type payload: string or dict
        :param payload: the payload of the transaction to create
        :type tag: string
        :param tag: (optional) the tag of the transaction to create
        :type print_curl: boolean
        :param print_curl: if set, print the cli cURL command to make the request without actually calling the chain
        :return: Parsed json response from the chain
        """
        if not isinstance(txn_type, str):
            raise ValueError('txn_type must be a string')
        if not (isinstance(payload, str) or isinstance(payload, dict)):
            raise ValueError('payload must be a dictionary or a string')
        if tag and not isinstance(tag, str):
            raise ValueError('tag must be a string')
        body = {
            'version': '1',
            'txn_type': txn_type,
            'payload': payload
        }
        if tag:
            body['tag'] = tag
        return self.perform_post('/chains/transaction', body, print_curl=print_curl)

    def query_blocks(self, query=None, sort=None, offset=0, limit=10, print_curl=False):
        """
        Preform a query on a chain's blocks
        :type query: string
        :param query: lucene query parameter (i.e.: is_serial:true)
        :type sort: string
        :param sort: sort syntax of 'field:direction' (i.e.: name:asc)
        :type offset: integer
        :param offset: pagination offset of query (default 0)
        :type limit: integer
        :param limit: pagination limit (default 10)
        :type print_curl: boolean
        :param print_curl: if set, print the cli cURL command to make the request without actually calling the chain
        :return: Parsed json response from the chain
        """
        query_params = get_lucene_query_params(query, sort, offset, limit)
        return self.perform_get('/chains/block{}'.format(query_params), print_curl=print_curl)

    def get_block(self, block_id, print_curl=False):
        """
        Get a specific block by id
        :type block_id: string
        :param block_id: block id to get
        :type print_curl: boolean
        :param print_curl: if set, print the cli cURL command to make the request without actually calling the chain
        :return: Parsed json response from the chain
        """
        if not isinstance(block_id, str):
            raise ValueError('block_id must be a string')
        return self.perform_get('/chains/block/{}'.format(block_id), print_curl=print_curl)

    def get_verification(self, block_id, level=0, print_curl=False):
        """
        Get all or level specific verifications for a block by id
        :type block_id: string
        :param block_id: block id to get
        :type level: integer
        :param level: specific level of blocks to return between 2 and 5
        :type print_curl: boolean
        :param print_curl: if set, print the cli cURL command to make the request without actually calling the chain
        :return: Parsed json response from the chain
        """
        if not isinstance(block_id, str):
            raise ValueError('block_id must be a string')
        if not isinstance(level, int):
            raise ValueError('level must be an integer')
        if(level):
            return self.perform_get('/chains/verification/{}?level={}'.format(block_id, level))
        return self.perform_get('/chains/verification/{}'.format(block_id), print_curl=print_curl)

    def get_sc_heap(self, key, sc_name=None, print_curl=False):
        """
        Retrieve data from the heap storage of a smart contract
        Note: When ran in an actual smart contract, sc_name will be
              pulled automatically from the environment if not explicitly provided
        :type key: string
        :param key: key of the object to get
        :type sc_name: string
        :param sc_name: (optional) sc_name heap to get the object from
        :type print_curl: boolean
        :param print_curl: if set, print the cli cURL command to make the request without actually calling the chain
        :return: Un-parsed response from the chain
        """
        if not isinstance(key, str):
            raise ValueError('key must be a string')
        if sc_name is None:
            sc_name = os.environ.get('SMART_CONTRACT_NAME')
        if not isinstance(sc_name, str):
            raise ValueError('sc_name either must be defined in environment or explicitly provided as a string')
        return self.perform_get('/get/{}/{}'.format(sc_name, key), parse_json=False, print_curl=print_curl)
