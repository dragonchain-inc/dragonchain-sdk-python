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

from base64 import b64encode, b64decode
from enum import Enum
import hashlib
import hmac


class SupportedHashes(Enum):
    blake2b = 1
    sha256 = 2
    sha3_256 = 3


def bytes_to_b64_str(unencoded_bytes):
    """
    Take a bytes object and output a base64 python string
    :type unencoded_bytes: Python bytes object
    :param unencoded_bytes: Bytes to encode
    :return: String of the base64 encoded bytes
    """
    if not isinstance(unencoded_bytes, bytes):
        raise ValueError('Method only takes bytes as input')
    return b64encode(unencoded_bytes).decode('utf-8')


def bytes_from_input(input_data):
    """
    Return python bytes from input (either bytes or utf-8 encodable string)
    :type input_data: bytes object or utf-8 encodable string
    :param input_data: input to process
    :return: bytes object representation of input
    """
    if isinstance(input_data, str):
        try:
            return input_data.encode('utf-8')
        except Exception:
            raise ValueError('Provided input_data was a string but not utf-8 encodable')
    elif isinstance(input_data, bytes):
        return input_data
    else:
        raise ValueError('Provided input_data was neither a bytes object or string')


def base64_encode_input(input_data):
    """
    Base64 encode some input (either bytes or utf-8 encodable string)
    :type input_data: bytes object or utf-8 encodable string
    :param input_data: data to encode
    :return: python string of base64 encoded input
    """
    return bytes_to_b64_str(bytes_from_input(input_data))


def hash_input(hash_type, input_data):
    """
    Hash some input_data with a specified (supported) hash type
    :type hash_type: integer
    :param hash_type: SupportedHashes enum type
    :type input_data: bytes object or utf-8 encodable string
    :param input_data: data to hash
    :return: bytes of hashed input
    """
    hash_method = get_hash_method(hash_type)
    return hash_method(bytes_from_input(input_data)).digest()


def get_hash_method(hash_type):
    """
    Return a hash method that supports the hashlib .new function
    :type hash_type: integer
    :param hash_type: SupportedHashes enum type
    :return: hash method
    """
    if hash_type == SupportedHashes.blake2b:
        return hashlib.blake2b
    elif hash_type == SupportedHashes.sha256:
        return hashlib.sha256
    elif hash_type == SupportedHashes.sha3_256:
        return hashlib.sha3_256
    else:
        raise NotImplementedError('Unsupported hash type')


def create_hmac(hash_type, secret, message):
    """
    Create an hmac from a given hash type, secret, and message
    :type hash_type: integer
    :param hash_type: SupportedHashes enum type
    :type secret: bytes object or utf-8 encodable string
    :param secret: the secret to be used to generate the hmac
    :type secret: bytes object or utf-8 encodable string
    :param message: The message to use as in the hmac generation
    :return: Bytes for the generated hmac
    """
    hash_method = get_hash_method(hash_type)
    hashed = hmac.new(key=bytes_from_input(secret), msg=bytes_from_input(message), digestmod=hash_method)
    return hashed.digest()


def compare_hmac(hash_type, hmac_string, secret, message):
    """
    Compare a provided base64 encoded hmac string with a generated hmac from the provided secret/message
    :type hash_type: integer
    :param hash_type: SupportedHashes enum type
    :type hmac_string: string
    :param hmac_string: base64 string of the hmac to compare
    :type secret: bytes object or utf-8 encodable string
    :param secret: the secret to be used to generate the hmac to compare
    :type message: bytes object or utf-8 encodable string
    :param message: The message to use with in the hmac generation to compare
    :return: Boolean if hmac matches or not
    """
    return hmac.compare_digest(b64decode(hmac_string), create_hmac(hash_type, secret, message))


def get_hmac_message_string(http_verb, full_path, dcid, timestamp, content_type="", content=""):
    """
    Generate the HMAC message string given the appropriate inputs
    :type http_verb: string
    :param http_verb: HTTP verb of the request
    :type full_path: string
    :param full_path: full path of the request after the FQDN (including any query parameters) (i.e. /chain/transaction)
    :type dcid: string
    :param dcid: dragonchain id of the request (must match dragonchain header)
    :type timestamp: int or string
    :param timestamp: timestamp of the request (must match timestamp header)
    :type content_type: string
    :param content_type: content-type header of the request (if it exists)
    :type content: bytes or utf-8 encodable string
    :param content: byte object of the body of the request (if it exists)
    :return: string to use as the message in HMAC generation
    """
    return '{}\n{}\n{}\n{}\n{}\n{}'.format(http_verb.upper(), full_path,
                                           dcid, timestamp, content_type,
                                           bytes_to_b64_str(hash_input(SupportedHashes.sha256, content)))


def get_authorization(auth_key_id, auth_key, http_verb, full_path, dcid, timestamp, content_type="", content="", algorithm="SHA256"):
    """
    Create an authorization header for making requests to dragonchains
    :type auth_key_id: string
    :param auth_key_id: ID string of the auth key to use
    :type auth_key: string
    :param auth_key: String of the auth key to use
    :type http_verb: string
    :param http_verb: HTTP verb of the request
    :type full_path: string
    :param full_path: full path of the request after the FQDN (including any query parameters) (i.e. /chain/transaction)
    :type dcid: string
    :param dcid: dragonchain id of the request (must match dragonchain header)
    :type timestamp: int or string
    :param timestamp: timestamp of the request (must match timestamp header)
    :type content_type: string
    :param content_type: content-type header of the request (if it exists)
    :type content: bytes or utf-8 encodable string
    :param content: byte object of the body of the request (if it exists)
    :type algorithm: string
    :param algorithm: hashing algorithm to use with the hmac creation
    :return: String of generated authorization header
    """
    # For now, only SHA256 is used for the HMAC/Hashing
    version = '1'
    message_string = get_hmac_message_string(http_verb, full_path, dcid, timestamp, content_type, content)
    supported_crypto_hash = None
    if algorithm == 'SHA256':
        supported_crypto_hash = SupportedHashes.sha256
    else:
        raise NotImplementedError('Hash type is not supported')
    hmac = bytes_to_b64_str(create_hmac(supported_crypto_hash, auth_key, message_string))
    return 'DC{}-HMAC-{} {}:{}'.format(version, algorithm, auth_key_id, hmac)
