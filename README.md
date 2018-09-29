# Dragonchain SDK

![Build Status](https://codebuild.us-west-2.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoieXNKb0Q3Y2doNkVsMFRZdHVqVWwyTm5lWjBjLzFVYjZCRFlhci9DbUo0aE9lcTlzQ3ErcitsV0NwSUlNVzJuMldFeEJUQUk5dnRlaXVTbUdpNW55NmFNPSIsIml2UGFyYW1ldGVyU3BlYyI6Ii9USGRmNEgxeE5wUU9FMVciLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=master)

## Intro

This is the Python 3 SDK for interacting with a dragonchain.
It provides functionality to be able to interact with a dragonchain through a simple sdk with minimal configuration needed.

## Installation

Windows note: If running on a Windows computer, for the following section, you will probably have to replace `python3` with `python` in the commands below depending on how python3 was installed on your computer.

First ensure that you have python3 installed on your machine.

The easiest way to install this repository is with pip. Simply run:

    python3 -m pip install dc_sdk

You can also install this package from source. To do so, get the source code (via git clone like `git clone https://github.com/dragonchain-inc/dragonchain-sdk-python.git` or simply downloading/extracting a source tarball from releases), then navigate into the root project directory. Now ensure that you have pip installed and you can install all the requirements for this project with:

    python3 -m pip install -r requirements.txt

Once these requirements successfully install, run:

```sh
./run.sh build
sudo ./run.sh install
```

On windows, simply replace the above 2 commands with:

```bat
python3 setup.py build
python3 setup.py install
```

## Configuration

In order to use this SDK, you need to have an Auth Key as well as an Auth Key ID for a given dragonchain. This can be loaded into the sdk in various ways.

1. The environment variables `DRAGONCHAIN_AUTH_KEY` and `DRAGONCHAIN_AUTH_KEY_ID` can be set with the appropriate values
2. The `dc_sdk.client` can be initialized with `auth_key=<KEY>` and `auth_key_id=<KEY_ID>`
3. Write an ini-style credentials file at `~/.dragonchain/credentials` where the section name is the dragonchain id, with values for `auth_key` and `auth_key_id` like so:

    ```ini
    [35a7371c-a20a-4830-9a59-5d654fcd0a4a]
    auth_key_id = JSDMWFUJDVTC
    auth_key = n3hlldsFxFdP2De0yMu6A4MFRh1HGzFvn6rJ0ICZzkE
    ```

## Usage

After installation, simply import the sdk and initialize a client object with a dragonchain ID to get started.
An example of getting a chain's status is shown below:

```python
import dc_sdk

client = dc_sdk.client(id='DRAGONCHAIN ID HERE',
                       auth_key='OPTIONAL AUTH KEY IF NOT CONFIGURED ELSEWHERE',
                       auth_key_id='OPTIONAL AUTH KEY ID IF NOT CONFIGURED ELSEWHERE')

client.get_status()
```
