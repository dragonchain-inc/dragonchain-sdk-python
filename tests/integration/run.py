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
import unittest

from tests.integration import test_transaction_types
from tests.integration import test_transactions
from tests.integration import test_smart_contracts
from tests.integration import test_blocks
from tests.integration import test_api_keys
from tests.integration import test_misc

if __name__ == "__main__":
    test_suites = [test_transaction_types, test_transactions, test_smart_contracts, test_blocks, test_api_keys, test_misc]
    # Make one suite and add all our tests
    suite = unittest.TestSuite()
    for test in test_suites:
        suite.addTests(test.suite())
    # Run tests and exit with appropriate status code
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
