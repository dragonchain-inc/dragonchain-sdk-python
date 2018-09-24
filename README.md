# Dragonchain SDK

## Intro

This is the Python 3 SDK for interacting with a dragonchain.
It provides functionality to be able to interact with a dragonchain through a simple sdk with minimal configuration needed.

## Configuration

In order to use this SDK, you need to have an Auth Key as well as an Auth Key ID. This can be loaded into the sdk in various ways.

1. The environment variables `DRAGONCHAIN_AUTH_KEY` and `DRAGONCHAIN_AUTH_KEY_ID` can be set with the appropriate values
2. The dragonchain-sdk.client can be initialized with `auth_key=<KEY>` and `auth_key_id=<KEY_ID>`
3. An ini style credentials file saved in `~/.dragonchain/credentials` where the section name is the dragonchain id, with values for `auth_key` and `auth_key_id` like so:

    ```ini
    [35a7371c-a20a-4830-9a59-5d654fcd0a4a]
    auth_key_id = JSDMWFUJDVTC
    auth_key = BPB3BW0yCZ586BMkV8z0tuTVJgE40FmGWJVCne9noz6sP2daKju8ZMQ3I3OK8lSnD44uT524ApP6sehlqujX9t
    ```

## Installation

TBD (likely via PyPi)

## Usage

Simply import the sdk and initialize a client object with a dragonchain ID to get started.
An example of posting a transaction is shown below

```python
import dc_sdk

client = dc_sdk.client(id='DRAGONCHAIN ID HERE',
                       auth_key='OPTION AUTH KEY IF NOT ELSEWHERE',
                       auth_key_id='OPTIONAL AUTH KEY ID IF NOT ELSEWHERE')

client.get_status()
```
