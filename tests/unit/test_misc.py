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
from tests import unit

if unit.PY36:
    from unittest.mock import patch
else:
    from mock import patch


class TestTypes(unittest.TestCase):
    @unittest.skipUnless(unit.CI_COVERAGE_VERSION, "Only run this test for code coverage purposes")
    def test_importing_types_raises_runtime_error(self):
        try:
            from dragonchain_sdk import types
        except RuntimeError as e:
            self.assertEqual(str(e), "types should never be imported during runtime")
            return
        self.assertRaises(RuntimeError, importlib.reload, types)


@unittest.skipUnless(dragonchain_sdk.ASYNC_SUPPORT, "Can't run tests without async support")
class TestAsyncImport(unittest.TestCase):
    @patch("sys.version_info", (3, 5, 0))
    def test_async_throws_runtime_error_with_old_python(self):
        importlib.reload(dragonchain_sdk)
        self.assertRaises(RuntimeError, dragonchain_sdk.create_aio_client)

    # Can't figure out how to mock an import error; If anyone can figure it out, feel free
    # def test_async_throws_runtime_error_without_aiohttp(self):
    #     importlib.reload(dragonchain_sdk)
    #     self.assertRaises(RuntimeError, dragonchain_sdk.create_aio_client)
