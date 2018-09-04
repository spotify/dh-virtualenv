=============
dh-virtualenv
=============

------------------------------------------------------
deploy a Python package in a self-contained virtualenv
------------------------------------------------------

:Author: Jyrki Pulliainen / Spotify AB <jyrki@spotify.com>
:Copyright: Copyright (C) 2013, Spotify AB. Licensed under
    the GNU General Public License version 2 or later
:Manual section: 1
:Manual group: DebHelper

SYNOPSIS
========

**dh_virtualenv** [*OPTIONS*]


DESCRIPTION
===========

``dh-virtualenv`` is a tool that aims to combine Debian packaging with
self-contained virtualenv based Python deployments. To do this, the
package extends debhelper's sequence by providing a new command in
sequence, ``dh_virtualenv``, which effectively replaces following
commands from the sequence:

 * ``dh_auto_install``
 * ``dh_python2``
 * ``dh_pycentral``
 * ``dh_pysupport``

In the sequence the ``dh_virtualenv`` is inserted right after
``dh_perl``.

OPTIONS
=======

-p PACKAGE, --package=PACKAGE		Act on the package named PACKAGE
-N PACKAGE, --no-package=PACKAGE	Do not act on the specified PACKAGE
-v, --verbose				Turn on verbose mode.
--extra-index-url			Pass extra index URL to pip
--preinstall=PACKAGE			Preinstall a PACKAGE before running pip.
--pip-tool=PIP_TOOL			Tool used to install requirements.
--extra-pip-arg				Extra arg for the pip executable.
--extra-virtualenv-arg			Extra arg for the virtualenv executable.
--index-url				Base URL for PyPI server.
--setuptools				Use setuptools instead of distribute.
--install-suffix=SUFFIX			Override virttualenv installation suffix
--upgrade-pip				Force upgrade pip in virtualenv
--requirements=FILE			Use FILE for requirements
--setuptools-test			Run `setup.py test` upon build.
--python=PATH				Use Python interpreter at PATH
--builtin-venv				Use built-in venv of Python 3
--skip-install				Don't run ``pip install .``

QUICK GUIDE FOR MAINTAINERS
===========================

1. Build depend on `python` or `python-all` and `dh-virtualenv`
2. Add `${python:Depends}` to Depends
3. Add `python-virtualenv` to dh's `--with` option

SEE ALSO
========

Online documentation can be found at
https://dh-virtualenv.readthedocs.io/en/latest.

This package should also ship with the complete documentation under
`/usr/share/doc/dh-virtualenv`.
