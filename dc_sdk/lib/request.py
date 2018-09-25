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

from json import dumps
import uuid
import time
import requests
from dc_sdk.lib.auth import get_authorization

reserved_headers = [
    'authorization',
    'timestamp',
    'dragonchain',
    'id',
    'content-type',
    'content-length',
    'accept-encoding',
    'accept',
    'connection',
    'host',
    'user-agent'
]

supported_http = {
    'GET': requests.get,
    'POST': requests.post,
    'PUT': requests.put,
    'PATCH': requests.patch,
    'DELETE': requests.delete,
    'HEAD': requests.head,
    'OPTIONS': requests.options
}


def get_requests_method(http_verb):
    """
    Get the appropriate requests method for a given http_verb
    :type http_verb: string
    :param http_verb: the type of http request to make (i.e. GET, POST, etc)
    :return: appropriate requests http method
    """
    if not isinstance(http_verb, str):
        raise ValueError('http_verb must be a string')
    request_method = supported_http.get(http_verb.upper())
    if not request_method:
        raise ValueError(http_verb + ' is an unsupported http operation')
    return request_method


def get_content_and_type(content_type, data, json):
    """
    Get the appropriate content and content_type values from input
    :type content_type: string
    :param content_type: the content-type header to set (only needed if including data, ignored if json is set)
    :type data: string or bytes
    :param data: data to include with the http request (ignored if json is set)
    :type json: dictionary
    :param json: dictionary object to send as json (automatically sets content-type to application/json)
    :return: Tuple of strings where index 0 is the content_type and index 1 is the content
    """
    # Add user data if necessary
    content = ''
    if json:
        if not isinstance(json, dict):
            raise ValueError('if json is set, it must be a dict')
        content = dumps(json)
        content_type = 'application/json'
    elif data:
        if not (isinstance(data, str) or isinstance(data, bytes)):
            raise ValueError('if data is set, it must be a string or bytes')
        # If data is supplied, content_type must be as well
        if not content_type or not isinstance(content_type, str):
            raise ValueError('if data is set, content_type must be set and a string')
        content = data
    else:
        if content_type:
            print('Warning: content_type supplied without any content. It will be ignored.')
        content_type = ''
    return content_type, content


def status_code_is_ok(status_code):
    """
    Check if a status code is ok (2XX)
    :type status_code: integer
    :param status_code: number of the status code to check
    :return: boolean true or false if the code was a 2XX
    """
    return status_code // 100 == 2


def make_headers(dcid, timestamp, rand_id, content_type, authorization, headers):
    """
    Create a headers dictionary to send with a request to a dragonchain
    :type dcid: string
    :param dcid: id of the dragonchain associated with this request
    :type timestamp: string
    :param timestamp: unix timestamp to put for this request
    :type rand_id: string
    :param rand_id: any random string to act as a unique request id
    :type content_type: NoneType or string
    :param content_type: content_type to use for this request
    :type authorization: string
    :param authorization: authorization header to include with the request
    :type headers: NoneType or dict
    :param headers: user provided headers to include with the rest of the headers object
    :return: dict of headers to use with the request
    """
    if not isinstance(dcid, str):
        raise ValueError('dcid must be a string')
    if not isinstance(timestamp, str):
        raise ValueError('timestamp must be a string')
    if not isinstance(rand_id, str):
        raise ValueError('rand_id must be a string')
    if not isinstance(authorization, str):
        raise ValueError('authorization must be a string')
    if content_type and not isinstance(content_type, str):
        raise ValueError('content_type must be a string')
    header_dict = {
        'dragonchain': dcid,
        'timestamp': timestamp,
        'id': rand_id,
        'Authorization': authorization
    }
    if content_type:
        header_dict['Content-Type'] = content_type
    if headers:
        if not isinstance(headers, dict):
            raise ValueError('if headers is set, it must be a dict')
        for key, value in headers.items():
            # Don't allow reserved headers to be modified
            if key.lower() not in reserved_headers:
                header_dict[key] = value
            else:
                print('Warning: {} is a reserved header, so the provided value for this header will be ignored'.format(key))
    return header_dict


def make_request(endpoint, auth_key_id, auth_key, dcid, http_verb, path, content_type=None, data=None, json=None, headers=None, timeout=30):
    """
    Make an http request to a dragonchain with the given information
    :type endpoint: string
    :param endpoint: the FQDN of the endpoint to hit (with protocol)
    :type auth_key_id: string
    :param auth_key_id: ID string of the auth key to use
    :type auth_key: string
    :param auth_key: String of the auth key to use
    :type dcid: string
    :param dcid: id of the dragonchain associated with this request
    :type http_verb: string
    :param http_verb: the type of http request to make (i.e. GET, POST, etc)
    :type path: string
    :param path: the full path to make the request (including query params if any) starting with a '/'
    :type content_type: string
    :param content_type: the content-type header to set (only needed if including data, ignored if json is set)
    :type data: string or bytes
    :param data: data to include with the http request (ignored if json is set)
    :type json: dictionary
    :param json: dictionary object to send as json (automatically sets content-type to application/json)
    :type headers: dictionary
    :param headers: any additional headers to include with the request to the dragonchain
    :type timeout: number
    :param timeout: the timeout to wait for the dragonchain to respond (defaults to 30 seconds if not set)
    :return: parsed json response from the dragonchain
    """
    if not isinstance(endpoint, str) or \
       not isinstance(auth_key_id, str) or \
       not isinstance(auth_key, str) or \
       not isinstance(path, str):
        raise ValueError('endpoint, auth_key_id, auth_key, and path must all be strings')
    if not path.startswith('/'):
        raise ValueError('path must start with a \'/\'')
    requests_method = get_requests_method(http_verb)
    content_type, content = get_content_and_type(content_type, data, json)
    timestamp = str(int(time.time()))
    # UUIDs are used as a unique request id
    rand_id = str(uuid.uuid4())
    authorization = get_authorization(auth_key_id, auth_key, http_verb, path, dcid, timestamp, rand_id, content_type, content)
    header_dict = make_headers(dcid, timestamp, rand_id, content_type, authorization, headers)
    # Make request with appropriate data
    try:
        r = requests_method(url=endpoint + path, data=content, headers=header_dict, timeout=timeout)
    except Exception as e:
        raise RuntimeError('Error while communicating with the dragonchain: {}'.format(e))
    try:
        if status_code_is_ok(r.status_code):
            return r.json()
    except Exception as e:
        raise RuntimeError('Unexpected response from the dragonchain. Response: {} | Error: {}'.format(r.text, e))
    raise RuntimeError('Non-2XX Response {} from dragonchain. Error: {}'.format(r.status_code, r.text))
