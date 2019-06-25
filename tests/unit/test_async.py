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

import unittest
import importlib

import dragonchain_sdk
from dragonchain_sdk import exceptions
from tests import unit

if unit.PY36:
    from unittest.mock import MagicMock, patch
else:
    from mock import MagicMock, patch

if dragonchain_sdk.ASYNC_SUPPORT:
    import asyncio
    import aiohttp
    from dragonchain_sdk import async_helpers


def async_test(function):
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(function)
        future = coro(*args, **kwargs)
        asyncio.get_event_loop().run_until_complete(future)

    return wrapper


class AsyncContextManagerMock(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for key in ("aenter_return", "aexit_return"):
            setattr(self, key, kwargs[key] if key in kwargs else MagicMock())

    async def __aenter__(self):
        return self.aenter_return

    async def __aexit__(self, *args):
        return self.aexit_return


@unittest.skipUnless(dragonchain_sdk.ASYNC_SUPPORT, "Can't run tests without async support")
class TestAsync(unittest.TestCase):
    @unittest.skipUnless(unit.CI_COVERAGE_VERSION, "Only run this test for code coverage purposes")
    @patch("typing.TYPE_CHECKING", True)
    def test_type_checking(self):
        importlib.reload(async_helpers)

    @patch("dragonchain_sdk.async_helpers.aiohttp")
    @patch("dragonchain_sdk.async_helpers.dragonchain_sdk.create_client")
    @async_test
    async def test_create_aio_client_passes_params_to_create_client(self, mock_create_client, mock_aiohttp):
        await async_helpers.create_aio_client("blah", some="kwarg")
        mock_create_client.assert_called_once_with("blah", some="kwarg")

    @patch("dragonchain_sdk.async_helpers.aiohttp")
    @patch("dragonchain_sdk.async_helpers.dragonchain_sdk.create_client")
    @patch("dragonchain_sdk.async_helpers.types.MethodType", return_value="thing")
    @async_test
    async def test_create_aio_client_sets_client_close_function(self, mock_method_bind, mock_create_client, mock_aiohttp):
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        await async_helpers.create_aio_client("blah", some="kwarg")
        mock_method_bind.assert_called_with(async_helpers.client_close, mock_client)
        self.assertEqual(mock_client.close, "thing")

    @patch("dragonchain_sdk.async_helpers.aiohttp.ClientSession", return_value="ok")
    @patch("dragonchain_sdk.async_helpers.dragonchain_sdk.create_client")
    @async_test
    async def test_create_aio_client_sets_client_request_session(self, mock_create_client, mock_aiohttp):
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        await async_helpers.create_aio_client("blah", some="kwarg")
        self.assertEqual(mock_client.request.session, "ok")

    @async_test
    async def test_close_client_closes_async_resources(self):
        mock_client = MagicMock()
        mock_client.request.session.close.return_value = asyncio.Future()
        mock_client.request.session.close.return_value.set_result("ok")
        await async_helpers.client_close(mock_client)
        # Check that it closes instantiated request ClientSession
        mock_client.request.session.close.assert_called_once()

    @async_test
    async def test_make_request_raises_connectionexception_error_on_request_failure(self):
        mock_request = MagicMock()
        mock_request._generate_request_data = MagicMock(return_value=(None, None, None))
        mock_request.session.request.side_effect = Exception
        # Can't use self.assertRaises because of async limitations
        try:
            await async_helpers._make_request(mock_request, "GET", "/transaction")
        except exceptions.ConnectionException:
            return
        self.fail("Did not throw ConnectionException")

    @async_test
    async def test_make_request_returns_ok_false_on_bad_response_status(self):
        mock_request = MagicMock()
        mock_request._generate_request_data = MagicMock(return_value=(None, None, None))
        mock_return_json = asyncio.Future()
        mock_return_json.set_result({"error": "some error"})
        mock_request.session.request.return_value = AsyncContextManagerMock(
            aenter_return=MagicMock(status=400, json=MagicMock(return_value=mock_return_json))
        )

        expected_response = {"ok": False, "status": 400, "response": {"error": "some error"}}
        self.assertEqual(await async_helpers._make_request(mock_request, "GET", "/transaction"), expected_response)

    @async_test
    async def test_make_request_parse_json(self):
        mock_request = MagicMock()
        mock_request._generate_request_data = MagicMock(return_value=(None, None, None))
        mock_return_json = asyncio.Future()
        mock_return_json.set_result({"test": "object"})
        mock_request.session.request.return_value = AsyncContextManagerMock(
            aenter_return=MagicMock(status=200, json=MagicMock(return_value=mock_return_json))
        )

        expected_response = {"ok": True, "status": 200, "response": {"test": "object"}}
        self.assertEqual(await async_helpers._make_request(mock_request, "GET", "/transaction"), expected_response)

    @async_test
    async def test_make_request_no_parse_json(self):
        mock_request = MagicMock()
        mock_request._generate_request_data = MagicMock(return_value=(None, None, None))
        mock_return_text = asyncio.Future()
        mock_return_text.set_result('{"test": "object"}')
        mock_request.session.request.return_value = AsyncContextManagerMock(
            aenter_return=MagicMock(status=200, text=MagicMock(return_value=mock_return_text))
        )

        expected_response = {"ok": True, "status": 200, "response": '{"test": "object"}'}
        self.assertEqual(await async_helpers._make_request(mock_request, "GET", "/transaction", parse_response=False), expected_response)

    @async_test
    async def test_make_request_raises_unexpectedresponseexception_error_on_no_context_raise(self):
        mock_request = MagicMock()
        mock_request._generate_request_data = MagicMock(return_value=(None, None, None))
        mock_fail_json = asyncio.Future()
        mock_fail_json.set_exception(RuntimeError("JSON Parse Error"))
        mock_request.session.request.return_value = AsyncContextManagerMock(
            aenter_return=MagicMock(status=200, json=MagicMock(return_value=mock_fail_json)), aexit_return=True
        )

        try:
            await async_helpers._make_request(mock_request, "GET", "/transaction")
        except exceptions.UnexpectedResponseException:
            return
        self.fail("Did not throw UnexpectedResponseException")

    @async_test
    async def test_make_request_raises_unexpectedresponseexception_error_on_parse_json_error(self):
        mock_request = MagicMock()
        mock_request._generate_request_data = MagicMock(return_value=(None, None, None))
        mock_fail_json = asyncio.Future()
        mock_fail_json.set_exception(RuntimeError("JSON Parse Error"))
        mock_request.session.request.return_value = AsyncContextManagerMock(
            aenter_return=MagicMock(status=200, json=MagicMock(return_value=mock_fail_json)), aexit_return=False
        )

        try:
            await async_helpers._make_request(mock_request, "GET", "/transaction")
        except exceptions.UnexpectedResponseException:
            return
        self.fail("Did not throw UnexpectedResponseException")

    @async_test
    async def test_make_request_calls_session_request_with_correct_params(self):
        mock_request = MagicMock()
        mock_request._generate_request_data = MagicMock(return_value=("url", b"content", {"some": "headers"}))
        json = asyncio.Future()
        json.set_result("")
        mock_request.session.request.return_value = AsyncContextManagerMock(aenter_return=MagicMock(status=200, json=MagicMock(return_value=json)))

        await async_helpers._make_request(mock_request, "POST", "/transaction")

        mock_request.session.request.assert_called_once_with(
            method="POST", url="url", data=b"content", headers={"some": "headers"}, ssl=True, timeout=aiohttp.ClientTimeout(total=30)
        )
