========================
 Trouble-Shooting Guide
========================


Installing on older Debian releases
===================================

**TODO**


Fixing package building problems
================================

'pkg-resources not found' or similar
------------------------------------

If you get errors regarding ``pkg-resources`` during the virtualenv creation,
update your build machine's ``pip`` and ``virtualenv``.
The versions on previous releases of many distros
are just too old to handle current infrastructure (especially PyPI)
– even Debian Jessie comes with the ancient pip 1.5.6.

This is the one exception to “never sudo pip”, so go ahead and do this:

.. code-block:: shell

    sudo pip install -U pip virtualenv

Then try building the package again.


Fixing package installation problems
====================================

dpkg: too-long line or missing newline in '…/triggers'
------------------------------------------------------

**TODO** https://github.com/spotify/dh-virtualenv/pull/84
