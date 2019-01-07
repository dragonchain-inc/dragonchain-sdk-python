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


class DragonchainException(Exception):
    """Base class exception"""


class EmptyUpdateException(DragonchainException):
    """Raised when user tries to update a resource with nothing to update"""


class AuthorizationNotFound(DragonchainException):
    """Raised when no form of authorization can be found"""


class DragonchainIdentityNotFound(DragonchainException):
    """Raised when no form of dragonchain ID can be found"""


class DragonchainServiceException(DragonchainException):
    """Raised when the request to the Dragonchain service was fulfilled, but responded with a non 200 status code"""


class ConnectionException(DragonchainException):
    """Raised when the request to the Dragonchain service was fulfilled, but responded with a non 200 status code"""


class UnexpectedResponseException(DragonchainException):
    """Raised when the Dragonchain responded with an unexpected response"""
