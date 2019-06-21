Getting Started
===============

After installing the SDK, getting started is easy.

You'll need your credentials and information for you chain on-hand, then you
can start playing with the SDK.

Initializing the Client
-----------------------

All functionality for interacting a chain happens with an instantiated Client
class. This should be created using the ``create_client`` function available
at the root of the module like so:

.. code:: python3

    import dragonchain_sdk

    my_client = dragonchain_sdk.create_client(
        dragonchain_id="c2dffKwiGj6AGg4zHkNswgEcyHeQaGr4Cm5SzsFVceVv",
        auth_key_id="JSDMWFUJDVTC",
        auth_key="n3hlldsFxFdP2De0yMu6A4MFRh1HGzFvn6rJ0ICZzkE",
        endpoint="https://35a7371c-a20a-4830-9a59-5d654fcd0a4a.api.dragonchain.com"
    )

    # If no exceptions were raised, my_client is now created and ready to use

(Note more detailed configuration options are in the `configuration section <configuration.html>`_)

Making calls to the Dragonchain
-------------------------------

Once the client is initialized, it can be used to make authenticated calls to
your running dragonchain. For example, we can query the chain for its current status:

(Continuing from example above)

.. code:: python3

    # Make the actual call to the dragonchain
    result = my_client.get_status()

    if result["ok"]:
        print("Successful call, here is the response from the chain:")
        print(result["response"])
    else:
        print("There was the following error making a call to the dragonchain:")
        print(result["response"])

All calls to the Dragonchain should be made by calling functions directly
on the instantiated client object.

Response Schema
---------------

All calls to a Dragonchain from the sdk return a response dictionary
with 3 parts:

1. ok: a boolean whether or not the call was successful
2. status: the http response code recieved from the call to the chain
3. response: the actual response body recieved from the chain

Example
"""""""

.. code:: python3

    {
        "ok": True,
        "status": 200,
        "response": {
            "some": "data",
            "this_data": {
                "can have": "any schema"
            }
        }
    }

Exceptions
----------

All expected exceptions thrown from the SDK derive from
``dragonchain_sdk.exceptions.DragonchainException``

You can catch with this exception to catch any exceptions that are
raised from the sdk

If any exception raised from the sdk does not derive from this class,
it should be considered a bug and reported to `the issue tracker <https://github.com/dragonchain-inc/dragonchain-sdk-python/issues>`_
with reproduction steps.

Example
"""""""

(Continued from above)

.. code:: python3

    try:
        result = my_client.get_status()
    except dragonchain_sdk.exceptions.DragonchainException as e:
        print("expected exception from sdk caught:")
        print(e)

Logging
-------

Debug logging can be enabled in the sdk by calling the
``set_stream_logger`` function

.. code:: python3

    import dragonchain_sdk

    dragonchain_sdk.set_stream_logger()

    # The sdk will now have debug logging enabled
