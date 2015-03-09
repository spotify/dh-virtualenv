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

0.9
===

* Support using system packages via a command line flag
  ``--use-system-packages``. Thanks to `Wes Mason
  <https://github.com/1stvamp>`_ for implementing this feature!
* Introduce a new, experimental, more modular build system. See the
  :doc:`usage` for documentation.
* Respect the ``DEB_NO_CHECK`` environment variable.

0.8
===

 * Support for running triggers upon host interpreter update. This new
   feature makes it possible to upgrade the host Python interpreter
   and avoid breakage of all the virtualenvs installed with
   virtualenv. For usage, see the the :doc:`tutorial`. Huge thanks to
   `Jürgen Hermann <https://github.com/jhermann>`_ for implementing
   this long wanted feature!
 * Add support for the built-in ``venv`` module. Thanks to `Petri
   Lehtinen <https://github.com/akheron>`_!
 * Allow custom ``pip`` flags to be passed via the
   ``--extra-pip-args`` flag. Thanks to `@labeneator
   <https://github.com/labeneator>`_ for the feature.

0.7
===

 * **Backwards incompatible** Support running tests. This change
   breaks builds that use distutils. For those cases a flag
   ``--no-test`` needs to be passed.
 * Add tutorial to documentation
 * Don't crash on debbuild parameters ``-i`` and ``-a``
 * Support custom source directory (debhelper's flag ``-D``)

0.6
===

First public release of *dh-virtualenv*
