.. image:: https://img.shields.io/pypi/v/dragonchain-sdk.svg
   :target: https://pypi.org/project/dragonchain-sdk/
   :alt: Latest PyPI version
.. image:: https://travis-ci.org/dragonchain-inc/dragonchain-sdk-python.svg?branch=master
   :target: https://travis-ci.org/dragonchain-inc/dragonchain-sdk-python
   :alt: Build Status
.. image:: https://api.codeclimate.com/v1/badges/d9ab43d29af318ec4121/test_coverage
   :target: https://codeclimate.com/github/dragonchain-inc/dragonchain-sdk-python/test_coverage
   :alt: Test Coverage
.. image:: https://img.shields.io/pypi/pyversions/dragonchain-sdk.svg
   :target: https://github.com/dragonchain-inc/dragonchain-sdk-python/
   :alt: Python Version Support
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/python/black
   :alt: Code Style Black
.. image:: https://img.shields.io/pypi/l/dragonchain-sdk.svg
   :target: https://github.com/dragonchain-inc/dragonchain-sdk-python/blob/master/LICENSE
   :alt: License

Intro
-----

This is the Python 3 SDK for interacting with a dragonchain. It provides
functionality to be able to interact with a dragonchain through a simple
sdk with minimal configuration needed.

Documentation
-------------

All documentation for this SDK can be found `here <https://python-sdk-docs.dragonchain.com/latest/>`_

Installation
------------

Windows note: If running on a Windows computer, for the following
section, you will probably have to replace ``python3`` with ``python``
in the commands below depending on how python3 was installed on your
computer.

First ensure that you have python3 installed on your machine.

The easiest way to install this repository is with pip. Simply run:

::

   python3 -m pip install -U dragonchain-sdk

You can also install this package from source. To do so, get the source
code (via git clone like
``git clone https://github.com/dragonchain-inc/dragonchain-sdk-python.git``
or simply downloading/extracting a source tarball from releases), then
navigate into the root project directory. Now ensure that you have pip
installed and you can install all the requirements for this project
with:

::

   python3 -m pip install -U -r requirements.txt

Once these requirements successfully install, run:

.. code:: sh

   ./run.sh build
   sudo ./run.sh install

On windows, simply replace the above 2 commands with:

.. code:: bat

   python setup.py build
   python setup.py install

Configuration
-------------

Please view the `docs <https://python-sdk-docs.dragonchain.com/latest/configuration.html>`_ for configuration

Contributing
------------

Dragonchain is happy to welcome contributions from the community.
You can get started `on github <https://github.com/dragonchain-inc/dragonchain-sdk-python/blob/master/CONTRIBUTING.rst>`_.
