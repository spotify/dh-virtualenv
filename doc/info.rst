=======================
 What is dh-virtualenv
=======================

``dh-virtualenv`` is a tool that aims to combine Debian packaging with
self-contained virtualenv based Python deployments. To do this, the
package extends debhelper's sequence by providing a new command in sequence,
``dh_virtualenv``, which effectively replaces following commands
from the sequence:

 * ``dh_auto_install``
 * ``dh_python2``
 * ``dh_pycentral``
 * ``dh_pysupport``

In the sequence the ``dh_virtualenv`` is inserted right after
``dh_perl``.
