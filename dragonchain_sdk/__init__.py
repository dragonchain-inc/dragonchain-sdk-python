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
import logging
from typing import Optional, Any

from dragonchain_sdk import dragonchain_client

__author__ = "Dragonchain, Inc."
__version__ = "3.1.1"

ASYNC_SUPPORT = False


def set_stream_logger(name: str = "dragonchain_sdk", level: int = logging.DEBUG, format_string: Optional[str] = None) -> None:
    """Set a stream logger for a module. You can set name to ``''`` to log everything.

    Args:
        name (str): Name of the module to set the stream logger for
        level (int): Log level, use logging module constants
        format_string (str): Logging format

    Returns:
        None, sets a stream logger for the whole SDK
    """
    if format_string is None:
        format_string = "%(asctime)s %(name)s [%(levelname)s] %(message)s"

    logger = logging.getLogger(name)
    logger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setLevel(level)
    formatter = logging.Formatter(format_string)
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def create_client(
    dragonchain_id: Optional[str] = None,
    auth_key_id: Optional[str] = None,
    auth_key: Optional[str] = None,
    endpoint: Optional[str] = None,
    verify: bool = True,
    algorithm: str = "SHA256",
) -> dragonchain_client.Client:
    """Construct a new ``Client`` object

    Args:
        dragonchain_id (str, optional): The ID of the chain to connect to.
        auth_key_id (str, optional): The authorization key ID
        auth_key (str, optional): The authorization key
        endpoint (str, optional): The endpoint of the Dragonchain
        verify (bool, optional): Verify the TLS cert of the Dragonchain
        algorithm (str, optional): The hashing algorithm used for HMAC authentication

    Returns:
        A new Dragonchain client.
    """
    return dragonchain_client.Client(dragonchain_id, auth_key_id, auth_key, endpoint, verify, algorithm)


logging.getLogger("dragonchain_sdk").addHandler(logging.NullHandler())

# Must be running python 3.5.3 or later and have aiohttp installed to support async functionality
if sys.version_info[:3] >= (3, 5, 3):
    try:
        from dragonchain_sdk import async_helpers

        ASYNC_SUPPORT = True
    except ImportError:
        # aiohttp is not installed. No async support
        pass

if ASYNC_SUPPORT:
    create_aio_client = async_helpers.create_aio_client
else:

    def create_aio_client(*args: Any, **kwargs: Any) -> Any:
        """This will be defined if async is supported"""
        raise RuntimeError("Extra aio dependencies not installed, or python version is too old to support asyncio")
