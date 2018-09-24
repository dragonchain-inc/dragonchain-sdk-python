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
from configparser import ConfigParser
from pathlib import Path


def get_auth_key(dragonchain_id=None):
    """
    Get an auth_key/auth_key_id pair
    First checks environment, then configuration files
    :type dragonchain_id: string
    :param dragonchain_id: (optional) dragonchain_id to get keys for (it pulling from config files)
    :return: Tuple where index 0 is the auth_key_id and index 1 is the auth_key
    """
    auth_key = os.environ.get('DRAGONCHAIN_AUTH_KEY')
    auth_key_id = os.environ.get('DRAGONCHAIN_AUTH_KEY_ID')
    if auth_key is None or auth_key_id is None:
        # If keys aren't in environment variables, check config file
        if dragonchain_id is None:
            raise RuntimeError('Could not locate credentials for this client')
        cred_file_path = '{}/.dragonchain/credentials'.format(Path.home())
        config = ConfigParser()
        config.read(cred_file_path)
        try:
            auth_key = config.get(dragonchain_id, 'auth_key')
            auth_key_id = config.get(dragonchain_id, 'auth_key_id')
            return auth_key_id, auth_key
        except Exception:
            raise RuntimeError('Could not locate credentials for this client')
    else:
        return auth_key_id, auth_key


def generate_dragonchain_endpoint(dragonchain_id):
    """
    Generate a dragonchain endpoint for a chain hosted by Dragonchain Inc
    :type dragonchain_id: string
    :param dragonchain_id: dragonchain id to generate the endpoint for
    :return: String of the dragonchain endpoint
    """
    return 'https://{}.api.dragonchain.com'.format(dragonchain_id)


class Client(object):
    """
    A client that interfaces all functionality to a dragonchain with a given id and key
    """
    def __init__(self, dragonchain_id=None, auth_key_id=None,
                 auth_key=None, endpoint=None):
        """
        Construct a new 'Client' object
        :type dragonchain_id: string
        :param dragonchain_id: dragonchain id to associate with this client
        :type auth_key_id: string
        :param auth_key_id: (Optional) Dragonchain authorization key ID
        :type auth_key: string
        :param auth_key: (Optional) Dragonchain authorization key
        :type endpoint: string
        :param endpoint: (Optional) Endpoint of the dragonchain
        """
        if not isinstance(dragonchain_id, str):
            raise ValueError('Dragonchain ID must be specified as a string')
        self.dcid = dragonchain_id
        if auth_key is None or auth_key_id is None:
            self.auth_key_id, self.auth_key = get_auth_key(self.dcid)
        else:
            if not isinstance(auth_key, str) or not isinstance(auth_key_id, str):
                raise ValueError('auth_key and auth_key_id must be specified as a strings')
            self.auth_key = auth_key
            self.auth_key_id = auth_key_id
        if endpoint is None:
            self.endpoint = generate_dragonchain_endpoint(dragonchain_id)
        else:
            if not isinstance(endpoint, str):
                raise ValueError('endpoint must be specified as a string')
            self.endpoint = endpoint
