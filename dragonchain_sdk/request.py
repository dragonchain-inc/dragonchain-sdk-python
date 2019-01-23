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

import datetime
import requests
import logging
import urllib
from json import dumps
from dragonchain_sdk.credentials import Credentials
from dragonchain_sdk import exceptions

logger = logging.getLogger(__name__)

supported_http = {
    'GET': requests.get,
    'POST': requests.post,
    'PUT': requests.put,
    'PATCH': requests.patch,
    'DELETE': requests.delete,
    'HEAD': requests.head,
    'OPTIONS': requests.options
}


class Request(object):
    """Construct a new `Request` object

    Args:
        credentials (Credentials): The credentials for the chain to associate with requests
        endpoint (str, optional): The URL for the endpoint of the chain
        verify (bool, optional): Boolean indicating whether to validate the SSL certificate of the endpoint when making requests

    Returns:
        A new Request object.
    """
    def __init__(self, credentials, endpoint=None, verify=True):
        if isinstance(credentials, Credentials):
            self.credentials = credentials
        else:
            raise TypeError('Parameter "credentials" must be of type Credentials.')

        if isinstance(verify, bool):
            self.verify = verify
            logger.debug('SSL certificates {} be verified when making requests'.format('will' if self.verify else 'will NOT'))
        else:
            raise TypeError('Parameter "verify" must be of type bool.')

        self.update_endpoint(endpoint)

    def update_endpoint(self, endpoint=None):
        """Update endpoint for this request object

        Args:
            endpoint (str, optional): Endpoint to set. Will auto-generate based on credentials dragonchain_id if not provided

        Returns:
            None, sets the endpoint of this Request instance
        """
        if endpoint is None:
            self.endpoint = 'https://{}.api.dragonchain.com'.format(self.credentials.dragonchain_id)
        elif isinstance(endpoint, str):
            self.endpoint = endpoint
        else:
            raise TypeError('Parameter "endpoint" must be of type str.')
        logger.info('Target endpoint updated to {}'.format(self.endpoint))

    def get(self, path, parse_response=True):
        """Make a GET request to a chain

        Args:
            path (str): Path of the request (including any path query parameters)
            parse_response (bool, optional): Decides whether the return from the chain should be parsed as json (default True)

        Returns:
            Returns the response of the GET operation.
        """
        return self._make_request(http_verb='GET',
                                  path=path,
                                  verify=self.verify,
                                  parse_response=parse_response)

    def post(self, path, body, parse_response=True):
        """Make a POST request to a chain

        Args:
            path (str): Path of the request (including any path query parameters)
            body (dict): A dictionary representing the JSON to post.
            parse_response (bool, optional): Decides whether the return from the chain should be parsed as json (default True)

        Returns:
            Returns the response of the POST operation.
        """
        return self._make_request(http_verb='POST',
                                  path=path,
                                  verify=self.verify,
                                  json=body,
                                  parse_response=parse_response)

    def put(self, path, body, parse_response=True):
        """Make a PUT request to a chain

        Args:
            path (str): Path of the request (including any path query parameters)
            body (dict): A dictionary representing the JSON to put.
            parse_response (bool, optional): Decides whether the return from the chain should be parsed as json (default True)

        Returns:
            Returns the response of the PUT operation.
        """
        return self._make_request(http_verb='PUT',
                                  path=path,
                                  verify=self.verify,
                                  json=body,
                                  parse_response=parse_response)

    def delete(self, path, body, parsed_response=True):
        """Make a DELETE request to the chain

        Args:
            path (str): Path of the request (including any path query parameters)
            body (dict): A dictionary representing the JSON to put.
            parse_response (bool, optional): Decides whether the return from the chain should be parsed as json (default True)

        Returns:
            Returns the response of the DELETE operation
        """
        return self._make_request(http_verb='DELETE',
                                  path=path,
                                  verify=self.verify,
                                  json=body,
                                  parse_response=parsed_response)

    def get_requests_method(self, http_verb):
        """Get the appropriate requests method for a given http_verb

        Args:
            http_verb (str): the type of http request to make (GET, POST, etc)

        Returns:
            appropriate requests http method
        """
        if not isinstance(http_verb, str):
            raise TypeError('Parameter "http_verb" must be of type str.')
        request_method = supported_http.get(http_verb.upper())
        if not request_method:
            raise ValueError(http_verb + ' is an unsupported http operation.')
        return request_method

    def generate_query_string(self, query_dict):
        """Generate an http query string from a dictionary

        Args:
            query_dict (dict): dict of parameters to use in the query string

        Returns:
            query string to use in an HTTP request path
        """
        if not isinstance(query_dict, dict):
            raise TypeError('Parameter "query_dict" must be of type dict.')
        if query_dict:
            query = '?'
            query_string = urllib.parse.urlencode(query_dict)
            logger.debug('Generated query string {}'.format(query_string))
            return '{}{}'.format(query, query_string)
        else:
            # If input is empty, return an empty string as the query string
            return ''

    def get_lucene_query_params(self, query=None, sort=None, offset=0, limit=10):
        """Generate a lucene query param string with given inputs

        Args:
            query (str): lucene query parameter (e.g.: is_serial:true)
            sort (str): sort syntax of 'field:direction' (e.g.: name:asc)
            offset (int): pagination offset of query
            limit (int): pagination limit

        Returns:
            Query string to include in request path
        """
        if query is not None and not isinstance(query, str):
            raise TypeError('Parameter "query" must be of type str.')
        if sort is not None and not isinstance(sort, str):
            raise TypeError('Parameter "sort" must be of type str.')
        if not isinstance(offset, int) or not isinstance(limit, int):
            raise TypeError('Parameters "limit" and "offset" must be of type int.')
        params = {
            'offset': offset,
            'limit': limit
        }
        if query:
            params['q'] = query
        if sort:
            params['sort'] = sort
        return self.generate_query_string(params)

    def make_headers(self, timestamp, authorization, content_type=None):
        """Create a headers dictionary to send with a request to a dragonchain

        Args:
            timestamp (str): unix timestamp to put for this request
            content_type (str): content_type to use for this request
            authorization (str): authorization header to include with the request

        Returns:
            dict of headers to use with the request
        """
        if not isinstance(timestamp, str):
            raise TypeError('Parameter "timestamp" must be of type str.')
        if not isinstance(authorization, str):
            raise TypeError('Parameter "authorization" must be of type str.')
        if content_type is not None and not isinstance(content_type, str):
            raise TypeError('Parameter "content_type" must be of type str.')
        header_dict = {
            'dragonchain': self.credentials.dragonchain_id,
            'timestamp': timestamp,
            'Authorization': authorization
        }
        if content_type:
            header_dict['Content-Type'] = content_type
        return header_dict

    def _make_request(self, http_verb, path, json=None, timeout=30, verify=True, parse_response=True):
        """Make an http request to a dragonchain with the given information

        Args:
            http_verb (str): the type of http request to make (GET, POST, etc)
            path (str): the full path to make the request (including query params if any) starting with a '/'
            json (dict, optional): dictionary object to send as json (automatically sets content-type to application/json)
            timeout (int, optional): the timeout to wait for the dragonchain to respond (defaults to 30 seconds if not set)
            verify (bool, optional): specify if the SSL cert of the chain should be verified
            parse_response (bool, optional): if the return from the chain should be parsed as json

        Returns:
            Dictionary where status is the HTTP status code, response is the return body from the chain, and ok is a boolean if the status code was in the 2XX range
            {
                'status': int (http response code from chain)
                'ok': boolean (if http response code is 200-299)
                'response': dict if parse_response, else str (actual response body from chain)
            }
        """
        if not isinstance(path, str):
            raise TypeError('Parameter "path" must be of type str.')
        if not path.startswith('/'):
            raise ValueError('Parameter "path" must start with a \'/\'.')

        logger.debug('Creating request {} {}'.format(http_verb, path))
        requests_method = self.get_requests_method(http_verb)
        content_type = 'application/json'
        content = dumps(json)
        # Add the 'Z' manually to indicate UTC (not added by isoformat)
        timestamp = datetime.datetime.utcnow().isoformat() + 'Z'
        authorization = self.credentials.get_authorization(http_verb, path, timestamp, content_type, content)
        header_dict = self.make_headers(timestamp, authorization, content_type)
        full_url = self.endpoint + path

        logger.debug('Making request. Verify SSL: {}, Timeout: {}'.format(verify, timeout))
        logger.debug('{} {}'.format(http_verb, full_url))
        logger.debug('Headers: {}'.format(header_dict))
        logger.debug('Data: {}'.format(content))

        # Make request with appropriate data
        try:
            r = requests_method(url=full_url, data=content, headers=header_dict, timeout=timeout, verify=verify)
        except Exception as e:
            raise exceptions.ConnectionException('Error while communicating with the Dragonchain: {}'.format(e))
        return_dict = {}
        # Generate the return dictionary
        try:
            return_dict['status'] = r.status_code
            logger.debug('Response status code: {}'.format(r.status_code))
            return_dict['ok'] = True if r.status_code // 100 == 2 else False
            return_dict['response'] = r.json() if parse_response else r.text
            return return_dict
        except Exception as e:
            raise exceptions.UnexpectedResponseException('Unexpected response from Dragonchain. Response: {} | Error: {}'.format(r.text, e))
