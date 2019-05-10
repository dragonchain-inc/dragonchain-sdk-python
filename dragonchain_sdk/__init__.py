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

from dragonchain_sdk.dragonchain_client import Client
import logging

__author__ = 'Dragonchain'
__version__ = '2.0.2'


def set_stream_logger(name='dragonchain_sdk', level=logging.DEBUG, format_string=None):
    """Set a stream logger for a module. You can set name to ``''`` to log everything.

    Args:
        name (str): Name of the module to set the stream logger for
        level (int): Log level, use logging module constants
        format_string (str): Logging format

    Returns:
        None, sets a stream logger
    """
    if format_string is None:
        format_string = '%(asctime)s %(name)s [%(levelname)s] %(message)s'

    logger = logging.getLogger(name)
    logger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setLevel(level)
    formatter = logging.Formatter(format_string)
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def client(*args, **kwargs):
    """Create a client for interacting with a Dragonchain. See ``dragonchain_sdk.dragonchain_client.Client`` for parameters."""
    return Client(*args, **kwargs)


logging.getLogger('dragonchain_sdk').addHandler(logging.NullHandler())
