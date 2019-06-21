Configuration
=============

In order to use this SDK, you need to have an Auth Key as well as an Auth
Key ID for a running Dragonchain with an ID. It is also strongly suggested that
you also supply an endpoint locally, so that a remote service isn't called to
automatically discover your dragonchain's endpoint.

All of these can variables be loaded into the sdk in various ways,
and are checked in the following order of precedence:

On Instantiation of a Client
----------------------------

``dragonchain_sdk.create_client`` can be initialized with the parameters
``dragonchain_id=<ID>``,
``auth_key=<KEY>``,
``auth_key_id=<KEY_ID>``,
and ``endpoint=<URL>``

Example
"""""""

.. code:: python3

    import dragonchain_sdk
    client = dragonchain_sdk.create_client(
        dragonchain_id="c2dffKwiGj6AGg4zHkNswgEcyHeQaGr4Cm5SzsFVceVv",
        auth_key_id="JSDMWFUJDVTC",
        auth_key="n3hlldsFxFdP2De0yMu6A4MFRh1HGzFvn6rJ0ICZzkE",
        endpoint="https://35a7371c-a20a-4830-9a59-5d654fcd0a4a.api.dragonchain.com"
    )

Environment Variables
---------------------

The environment variables
``DRAGONCHAIN_ID``,
``AUTH_KEY``,
``AUTH_KEY_ID``,
and ``DRAGONCHAIN_ENDPOINT``,
can be set with the appropriate values before instantiating a client.

Credentials File
----------------

An ini-style credentials file can be provided at ``~/.dragonchain/credentials``
(or on Windows: ``%LOCALAPPDATA%\dragonchain\credentials``)
where the section name is the dragonchain id, with values for
``auth_key``, ``auth_key_id``, and ``endpoint``.
Additionally, you can supply a value for ``dragonchain_id`` in the
``default`` section to initialize the client for a specific chain
without supplying an ID any other way

Example
"""""""

An example credentials file with keys for 2 chains and a default
chain set:

.. code:: ini

    [default]
    dragonchain_id = c2dffKwiGj6AGg4zHkNswgEcyHeQaGr4Cm5SzsFVceVv

    [c2dffKwiGj6AGg4zHkNswgEcyHeQaGr4Cm5SzsFVceVv]
    auth_key_id = JSDMWFUJDVTC
    auth_key = n3hlldsFxFdP2De0yMu6A4MFRh1HGzFvn6rJ0ICZzkE
    endpoint = https://35a7371c-a20a-4830-9a59-5d654fcd0a4a.api.dragonchain.com

    [28VhSgtPhwkhKBgmQSW6vrsir7quEYHdCjqsW6aAYbfrw]
    auth_key_id = OGNHGLYIFVUA
    auth_key = aS73Si7agvX9gfxnLMh6ack9DEuidKiwQxkqBudXl81
    endpoint = https://28567017-6412-44b6-80b2-12876fb3d4f5.api.dragonchain.com

Note
----

These 3 methods can be mixed-and-matched. For example having a
configuration file with an auth_key/id and endpoint set for multiple
chains, and simply supplying a dragonchain_id to the ``create_client``
function.
