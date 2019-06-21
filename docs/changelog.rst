Changelog
=========

3.0.4
-----

Bugs:
  * Fixed a bug for ``create_ethereum_transaction``
    to work with a custom gas price
  * Stop sending unsolicited HTTP bodies and
    Content-Type headers when not necessary
Documentation:
  * Restructure documentation site layout
  * Add new docs for installation, configuration, getting started,
    etc (no longer use README.rst for docs)
  * Added Changelog
  * Switch to readthedocs theme
Packaging:
  * Added ``typing`` as a dependency for python < 3.5
    to fix distribution for python 3.4
  * Become compliant with `PEP 561 <https://www.python.org/dev/peps/pep-0561/>`_ typing distribution
Development:
  * Added and started enforcing stricter typing
  * Added a full suite of integration tests
  * Added code owners which are required for PR review
  * Added issue and PR templates for github
