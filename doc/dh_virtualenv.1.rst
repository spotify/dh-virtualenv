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
--preinstall=PACKAGE			Preinstall a PACKAGE before
					running pip.
--extra-pip-arg				Extra arg for the pip executable.
--extra-virtualenv-arg      Extra arg for the virtualenv executable.
--pypi-url				Base URL for PyPI server.
--setuptools				Use setuptools instead of
					distribute.

QUICK GUIDE FOR MAINTAINERS
===========================

1. Build depend on `python` or `python-all` and `dh-virtualenv`
2. Add `${python:Depends}` to Depends
3. Add `python-virtualenv` to dh's `--with` option

SEE ALSO
========

Online documentation can be found at
http://dh-virtualenv.readthedocs.org/en/latest.

This package should also ship with documentation under
`/usr/share/doc/dh-virtualenv`.
