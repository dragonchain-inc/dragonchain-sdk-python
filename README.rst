.. image:: https://travis-ci.org/dragonchain-inc/dragonchain-sdk-python.svg?branch=master
   :target: https://travis-ci.org/dragonchain-inc/dragonchain-sdk-python
   :alt: Build Status
.. image:: https://api.codeclimate.com/v1/badges/d9ab43d29af318ec4121/test_coverage
   :target: https://codeclimate.com/github/dragonchain-inc/dragonchain-sdk-python/test_coverage
   :alt: Test Coverage
.. image:: https://pypip.in/v/dragonchain-sdk/badge.png
   :target: https://pypi.org/project/dragonchain-sdk/
   :alt: Latest PyPI version

Intro
-----

This is the Python 3 SDK for interacting with a dragonchain. It provides
functionality to be able to interact with a dragonchain through a simple
sdk with minimal configuration needed.

Documentation
-------------

Documentation for this SDK can be found at the following location:

https://python-sdk-docs.dragonchain.com/latest/

Installation
------------

Windows note: If running on a Windows computer, for the following
section, you will probably have to replace ``python3`` with ``python``
in the commands below depending on how python3 was installed on your
computer.

First ensure that you have python3 installed on your machine.

The easiest way to install this repository is with pip. Simply run:

::

   python3 -m pip install dragonchain-sdk

You can also install this package from source. To do so, get the source
code (via git clone like
``git clone https://github.com/dragonchain-inc/dragonchain-sdk-python.git``
or simply downloading/extracting a source tarball from releases), then
navigate into the root project directory. Now ensure that you have pip
installed and you can install all the requirements for this project
with:

::

   python3 -m pip install -r requirements.txt

Once these requirements successfully install, run:

.. code:: sh

   ./run.sh build
   sudo ./run.sh install

On windows, simply replace the above 2 commands with:

.. code:: bat

   python3 setup.py build
   python3 setup.py install

Configuration
-------------

In order to use this SDK, you need to have an Auth Key as well as an
Auth Key ID for a given Dragonchain ID. These can be loaded into the sdk
in various ways, and are checked in the following order of precedence:

1. The ``dragonchain_sdk.client`` can be initialized with the parameters
   ``dragonchain_id=<ID>``, ``auth_key=<KEY>``, and
   ``auth_key_id=<KEY_ID>``

2. The environment variables ``DRAGONCHAIN_ID``,
   ``AUTH_KEY``, and ``AUTH_KEY_ID`` can be set
   with the appropriate values

3. An ini-style credentials file can be provided at
   ``~/.dragonchain/credentials`` (or on Windows:
   ``%LOCALAPPDATA%\dragonchain\credentials``) where the section name is
   the dragonchain id, with values for ``auth_key`` and ``auth_key_id``.
   Additionally, you can supply a value for ``dragonchain_id`` in the
   ``default`` section to initialize the client for a specific chain
   without supplying an ID any other way

   .. rubric:: Example Credentials File
      :name: example-credentials-file

   An example credentials file with keys for 2 chains and a default
   chain set.

   .. code:: ini

      [default]
      dragonchain_id = 35a7371c-a20a-4830-9a59-5d654fcd0a4a

      [35a7371c-a20a-4830-9a59-5d654fcd0a4a]
      auth_key_id = JSDMWFUJDVTC
      auth_key = n3hlldsFxFdP2De0yMu6A4MFRh1HGzFvn6rJ0ICZzkE

      [28567017-6412-44b6-80b2-12876fb3d4f5]
      auth_key_id = OGNHGLYIFVUA
      auth_key = aS73Si7agvX9gfxnLMh6ack9DEuidKiwQxkqBudXl81


Contributing
------------

Dragonchain is happy to welcome contributions from the community.
You can get started `here <https://github.com/dragonchain-inc/dragonchain-sdk-python/blob/master/CONTRIBUTING.md>`_.
