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

# This module should never be imported on python <3.5, as it contains syntax that is not valid before 3.5

import types
import logging
import asyncio
from typing import cast, Optional, Dict, Any, TYPE_CHECKING

import aiohttp

import dragonchain_sdk
from dragonchain_sdk import exceptions

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from dragonchain_sdk import request
    from dragonchain_sdk import dragonchain_client
    from dragonchain_sdk.types import request_response


async def create_aio_client(*args: Any, **kwargs: Any) -> "dragonchain_client.Client":
    """Construct a new async ``Client`` object

    Args:
        Refer to dragonchain_sdk.create_client for arguments

    Returns:
        A new Dragonchain client which makes async requests.
    """
    client = dragonchain_sdk.create_client(*args, **kwargs)
    # Change out the client's request internals to become async-capable with aiohttp
    client.request.session = aiohttp.ClientSession(loop=asyncio.get_event_loop())
    client.request._make_request = types.MethodType(_make_request, client.request)  # type: ignore
    # Add close function to the client for aiohttp cleanup
    client.close = types.MethodType(client_close, client)  # type: ignore
    return client


async def client_close(self: "dragonchain_client.Client") -> None:
    """
    Close any aiohttp sessions associated with an instantiated async client
    """
    await self.request.session.close()


async def _make_request(
    self: "request.Request",
    http_verb: str,
    path: str,
    json_content: Optional[Dict[Any, Any]] = None,
    timeout: int = 30,
    verify: bool = True,
    parse_response: bool = True,
    additional_headers: Optional[Dict[str, str]] = None,
) -> "request_response":
    """
    Make an async http request to a dragonchain with the given information
    Should take and handle exactly like dragonchain_sdk.request.Request._make_request, but asynchronous
    """
    full_url, content, header_dict = self._generate_request_data(
        http_verb=http_verb, path=path, json_content=json_content, additional_headers=additional_headers
    )

    # Make request with appropriate data
    try:
        logger.debug("Making request. Verify SSL: {}, Timeout: {}".format(verify, timeout))
        async with self.session.request(
            method=http_verb, url=full_url, data=content, headers=header_dict, ssl=verify, timeout=aiohttp.ClientTimeout(total=timeout)
        ) as r:
            try:
                return_dict = {}
                return_dict["status"] = r.status
                logger.debug("Response status code: {}".format(r.status))
                return_dict["ok"] = True if r.status // 100 == 2 else False
                return_dict["response"] = await r.json() if parse_response else await r.text()
                return cast("request_response", return_dict)
            except Exception as e:
                raise exceptions.UnexpectedResponseException("Unexpected response from Dragonchain. Error: {}".format(e))
    except exceptions.UnexpectedResponseException:
        raise
    except Exception as e:
        raise exceptions.ConnectionException("Error while communicating with the Dragonchain: {}".format(e))
    # Can get here if context manager doesn't throw exceptions.UnexpectedResponseException which could have been raised
    raise exceptions.UnexpectedResponseException("Unkown error processing result from dragonchain")
