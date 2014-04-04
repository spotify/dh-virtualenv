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


===========
 Changelog
===========

Following list contains most notable changes by version. For full list
consult the git history of the project.

0.7 (unreleased)
================

 * **Backwards incompatible** Support running tests. This change
   breaks builds that use distutils. For those cases a flag
   ``--no-test`` needs to be passed.
 * Add tutorial to documentation
 * Don't crash on debbuild parameters ``-i`` and ``-a``
 * Support custom source directory (debhelper's flag ``-D``)

0.6
===

First public release of *dh-virtualenv*
