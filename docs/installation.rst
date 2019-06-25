Installation
============

1. First ensure that you have python3 installed on your machine.
   If you don't have python installed, you can get it from `python.org <https://www.python.org/downloads/>`_,
   or a package manager (such as ``apt`` or ``yum``) on a Linux machine.

2. Choose from one of the options below to install.
   It is recommended to use PyPI

From PyPI
---------

The easiest way to install this repository is with pip.
Simply run the following in a terminal:

::

   python3 -m pip install -U dragonchain-sdk

With asyncio support
""""""""""""""""""""

For async/await support (python 3.5+ only),
be sure to install with the aio extras instead:

::

   python3 -m pip install -U dragonchain-sdk[aio]

For more information on asyncio support, visit the `aio section <aio.html>`_

From Source
-----------

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

   python3 setup.py build
   python3 setup.py install

Windows Note:
"""""""""""""
If running on a Windows computer, you will probably have to replace
``python3`` with ``python`` in the commands above, depending on how
python3 was installed on your computer.
