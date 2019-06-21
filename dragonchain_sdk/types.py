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

from typing import Union, Dict, Any, TYPE_CHECKING

if not TYPE_CHECKING:
    raise RuntimeError("types should never be imported during runtime")

import mypy_extensions  # noqa: E402 Want to explicitly ensure not type checking before importing extensions

request_response = mypy_extensions.TypedDict("request_response", {"status": int, "ok": bool, "response": Union[Dict[Any, Any], str]})
custom_index_type = mypy_extensions.TypedDict("custom_index_type", {"key": str, "path": str})
