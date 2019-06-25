Asyncio Support
===============

This sdk supports `PEP 492 <https://www.python.org/dev/peps/pep-0492/>`_
async/await functionality when running on python 3.5.3+ and
installed with aio extras.

See the relevant `installation section <installation.html#with-asyncio-support>`_
for details on how to install the sdk with aio extras.

The SDK will automatically detect if these conditions are met
when imported, and an asyncio compatible dragonchain client can be
created by awaiting ``dragonchain_sdk.create_aio_client`` with the same
parameters as ``dragonchain_sdk.create_client``.

Why Use Async/Await?
--------------------

Python Async/Await is important for high performance with workloads that
have lots of i/o, as it allows for concurrent code execution.

As communicating over a network is inherantly latent, you can regain
performance for other parts of your application by allowing them to
execute concurrently within an event loop while the dragonchain_sdk may
be waiting on a result from a request to a chain.

For more information on asyncio, async/await, and the python event loop,
read the `Python Documentation <https://docs.python.org/3/library/asyncio.html>`_.

Differences between the regular and async client
------------------------------------------------

There are only a few notable differences between the regular and async client:

1. The async client must be created by awaiting
   ``dragonchain_sdk.create_aio_client`` instead calling
   ``dragonchain_sdk.create_client`` (although they take identical parameters,
   so reference `create_client <api.html#dragonchain_sdk.create_client>`_ for
   arguments)

2. Each function on the client must be awaited

3. When done using the client, its ``.close`` function should be awaited
   in order to clean up any persistent network connections. (This function
   only exists on async clients)

Other than that, everything else, including function arguments should
be identical.

Usage Example
-------------

The following is a usage example for the async client: creating the client,
making a request to a chain, then closing the client.

.. code:: python3

    import asyncio

    import dragonchain_sdk


    async def main():
        # Create our client by awaiting the function
        my_client = await dragonchain_sdk.create_aio_client(
            dragonchain_id="c2dffKwiGj6AGg4zHkNswgEcyHeQaGr4Cm5SzsFVceVv",
            auth_key_id="JSDMWFUJDVTC",
            auth_key="n3hlldsFxFdP2De0yMu6A4MFRh1HGzFvn6rJ0ICZzkE",
            endpoint="https://35a7371c-a20a-4830-9a59-5d654fcd0a4a.api.dragonchain.com",
        )

        # Ensure to await all our calls on the client
        result = await my_client.get_status()

        # Handle the response identically to the regular client
        if result["ok"]:
            print("Successful call, here is the response from the chain:")
            print(result["response"])
        else:
            print("There was the following error making a call to the dragonchain:")
            print(result["response"])

        # Make sure to call .close on the client for cleanup when we're done
        await my_client.close()


    if __name__ == "__main__":
        asyncio.get_event_loop().run_until_complete(main())


