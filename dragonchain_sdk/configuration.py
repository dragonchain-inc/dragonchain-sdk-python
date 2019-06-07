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
import configparser
from typing import Tuple

import requests

from dragonchain_sdk import exceptions


logger = logging.getLogger(__name__)


def get_dragonchain_id() -> str:
    """Get the dragonchain id if not provided. First checks environment, then configuration files

    Raises:
        DragonchainIdentityNotFound: if no dragonchain ID is found

    Returns:
        Default dragonchain id string if found
    """
    logger.debug("Checking if dragonchain_id is in the environment")
    dragonchain_id = os.environ.get("DRAGONCHAIN_ID")
    if not dragonchain_id:
        logger.debug("dragonchain_id isn't in the environment, trying to load default from ini config file")
        try:
            # Check config ini file if ID isn't provided explicitly or in environment
            config = configparser.ConfigParser()
            config.read(_get_config_file_path())
            dragonchain_id = config.get("default", "dragonchain_id")
        except (configparser.NoSectionError, configparser.NoOptionError):
            raise exceptions.DragonchainIdentityNotFound("Could not locate dragonchain_id.")
    return dragonchain_id


def get_endpoint(dragonchain_id: str) -> str:
    """Get an endpoint for a dragonchain. First checks environment, then configuration files, then a remote service

    Args:
        dragonchain_id (str): The dragonchain id to fetch the endpoint for

    Raises:
        DragonchainIdentityNotFound: if endpoint cannot be found

    Returns:
        String of the dragonchain endpoint
    """
    endpoint = _get_endpoint_from_environment()
    if endpoint:
        return endpoint
    logger.debug("Endpoint isn't in environment, trying to load from ini config file")
    endpoint = _get_endpoint_from_file(dragonchain_id)
    if endpoint:
        return endpoint
    logger.debug("Endpoint isn't in config file, trying to load from remote service")
    try:
        return _get_endpoint_from_remote(dragonchain_id)
    except exceptions.MatchmakingException:
        raise exceptions.DragonchainIdentityNotFound("Unable to locate dragonchain endpoint")


def get_credentials(dragonchain_id: str) -> Tuple[str, str]:
    """Get an auth_key/auth_key_id pair if not provided. First checks environment, then configuration files, then smart contract location

    Args:
        dragonchain_id (str): The dragonchain id to fetch credentials keys for

    Raises:
        DragonchainIdentityNotFound: if credentials can't be found for a given chain

    Returns:
        Tuple of strings where index 0 is the auth_key_id and index 1 is the auth_key
    """
    auth_key_id, auth_key = _get_credentials_from_environment()
    if bool(auth_key) and bool(auth_key_id):
        return auth_key_id, auth_key
    logger.debug("Credentials aren't in environment, trying to load from ini config file")
    auth_key_id, auth_key = _get_credentials_from_file(dragonchain_id)
    if bool(auth_key) and bool(auth_key_id):
        return auth_key_id, auth_key
    logger.debug("Credentials aren't in config file, trying to load as a smart contract")
    auth_key_id, auth_key = _get_credentials_as_smart_contract()
    if bool(auth_key) and bool(auth_key_id):
        return auth_key_id, auth_key
    raise exceptions.DragonchainIdentityNotFound("Unable to locate dragonchain authorization credentials")


def _get_endpoint_from_environment() -> str:
    """Attempt to get endpoint for a dragonchain from the environment variables

    Returns:
        String of endpoint from environment. Empty string if not found
    """
    logger.debug("Checking if Endpoint is in the environment")
    return os.environ.get("DRAGONCHAIN_ENDPOINT") or ""


def _get_endpoint_from_file(dragonchain_id: str) -> str:
    """Attempt to get endpoint for a dragonchain from the configuration file

    Args:
        dragonchain_id (str): The dragonchain id to get the endpoint for

    Returns:
        String of endpoint from file. Empty string if not found
    """
    try:
        # If both keys aren't in environment variables, check config file
        config = configparser.ConfigParser()
        config.read(_get_config_file_path())
        return config.get(dragonchain_id, "endpoint")
    except (configparser.NoSectionError, configparser.NoOptionError):
        return ""


def _get_endpoint_from_remote(dragonchain_id: str) -> str:
    """Attempt to get endpoint for a dragonchain from the configuration file

    Args:
        dragonchain_id (str): The dragonchain id to get the endpoint for

    Raises:
        MatchmakingException: with any non-200 response from matchmaking, or any errors to communicate

    Returns:
        String of endpoint from remote service if found
    """
    try:
        r = requests.get("https://matchmaking.api.dragonchain.com/registration/{}".format(dragonchain_id), timeout=30)
    except (requests.Timeout, requests.ConnectionError, requests.ConnectTimeout):  # noqa: T484  requests does indeed have ConnectTimeout
        logger.exception("Could not contact matchmaking for dragonchain endpoint. Ensure internet is working properly.")
        raise exceptions.MatchmakingException("Could not contact matchmaking")
    except Exception:
        logger.exception("Unexpected failure to make request with matchmaking")
        raise exceptions.MatchmakingException("Unexpected failure to make request with matchmaking")
    if r.status_code < 200 or r.status_code >= 300:
        raise exceptions.MatchmakingException("Non-200 response from matchmaking. Status code {} with response: {}".format(r.status_code, r.text))
    try:
        return r.json()["url"]
    except Exception:
        raise exceptions.MatchmakingException("Unexpected response contents from matchmaking\n{}".format(r.text))


def _get_credentials_from_environment() -> Tuple[str, str]:
    """Attempt to get credentials for a dragonchain from the environment

    Returns:
        Tuple of auth_key_id/auth_key of credentials from environment. Empty strings in tuple if not found
    """
    logger.debug("Checking if credentials are in the environment")
    auth_key = os.environ.get("AUTH_KEY") or ""
    auth_key_id = os.environ.get("AUTH_KEY_ID") or ""
    return auth_key_id, auth_key


def _get_credentials_from_file(dragonchain_id: str) -> Tuple[str, str]:
    """Attempt to get credentials for a dragonchain from the credentials file

    Args:
        dragonchain_id (str): The dragonchain id to get the credentials for

    Returns:
        Tuple of auth_key_id/auth_key of credentials from environment. Empty strings in tuple if not found
    """
    try:
        config = configparser.ConfigParser()
        config.read(_get_config_file_path())
        return config.get(dragonchain_id, "auth_key_id"), config.get(dragonchain_id, "auth_key")
    except (configparser.NoSectionError, configparser.NoOptionError):
        return "", ""


def _get_credentials_as_smart_contract() -> Tuple[str, str]:
    """Attempt to get credentials for a dragonchain from the standard location for a smart contract

    Returns:
        Tuple of auth_key_id/auth_key of credentials from environment. Empty strings in tuple if not found
    """
    try:
        base_path = os.path.join(os.path.abspath(os.sep), "var", "openfaas", "secrets")
        auth_key = open(os.path.join(base_path, "sc-{}-secret-key".format(os.environ.get("SMART_CONTRACT_ID"))), "r").read()
        auth_key_id = open(os.path.join(base_path, "sc-{}-auth-key-id".format(os.environ.get("SMART_CONTRACT_ID"))), "r").read()
        return auth_key_id, auth_key
    except (OSError, IOError, FileNotFoundError):
        return "", ""


def _get_config_file_path() -> str:
    """Get the path for the credential file depending on the OS

    Returns:
        Python string of the file path for the configuration file
    """
    if os.name == "nt":
        logger.debug("Windows OS detected")
        path = os.path.join(os.path.expandvars("%LOCALAPPDATA%"), "dragonchain", "credentials")
    else:
        logger.debug("Posix OS detected")
        path = os.path.join(os.path.expanduser("~"), ".dragonchain", "credentials")
    logger.debug("Credentials file path: {}".format(path))
    return os.fsdecode(path)
