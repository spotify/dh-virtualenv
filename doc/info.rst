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

1.0 (unreleased)
=================

* **Backwards incompatible** Change the default install root to
  ``/opt/venvs``. This is due to the old installation root
  (``/usr/share/python``) clashing with Debian provided Python
  utilities. To maintain the old install location, use
  :envvar:`DH_VIRTUALENV_INSTALL_ROOT` and point it to
  ``/usr/share/python``.
* **Backwards incompatible** By default, do not run `setup.py test`
  upon building. The :option:`--no-test` flag has no longer any effect. To
  get the old behaviour, use :option:`--setuptools-test` flag instead.
* Deprecate :option:`--pypi-url` in favour of :option:`--index-url`
* Support upgrading pip to the latest release with :option:`--upgrade-pip`
  flag.
* Buildsystem: Add support for :envvar:`DH_UPGRADE_PIP`,
  :envvar:`DH_UPGRADE_SETUPTOOLS` and :envvar:`DH_UPGRADE_WHEEL`. Thanks
  to `Kris Kvilekval <https://github.com/kkvilekval>`_ for the
  implementation!
* Buildsystem: Add support for custom requirements file location
  using :envvar:`DH_REQUIREMENTS_FILE` and for custom ``pip`` command
  line arguments using :envvar:`DH_PIP_EXTRA_ARGS`. Thanks to `Einar
  Forselv <https://github.com/einarf>`_ for implementing!
* Fixing shebangs now supports multiple interpreters. Thanks `Javier
  Santacruz <https://github.com/jvrsantacruz>`_!

0.11
====

* Allow passing explicit filename for `requirements.txt` using
  :option:`--requirements` option. Thanks to `Eric Larson
  <https://github.com/ionrock>`_ for implementing!
* Ensure that venv is configured before starting any daemons. Thanks
  to `Chris Lamb <https://github.com/lamby>`_ for fixing this!
* Make sure `fix_activate_path` updates all activate scripts. Thanks
  to `walrusVision <https://github.com/walrusVision>`_ for fixing
  this!

0.10
====

* **Backwards incompatible** Fix installation using the built-in
  virtual environment on 3.4. This might break installation on Python
  versions prior to 3.4 when using :option:`--builtin-venv` flag.
  Thanks to `Elonen <https://github.com/elonen>`_ for fixing!
* Honor :envvar:`DH_VIRTUALENV_INSTALL_ROOT` in build system. Thanks to
  `Ludwig Hähne <https://github.com/Pankrat>`_ for implementing!
* Allow overriding virtualenv arguments by using the
  :envvar:`DH_VIRTUALENV_ARGUMENTS` environment variable when using the
  build system. Thanks to `Ludwig Hähne <https://github.com/Pankrat>`_
  for implementing!
* Add option to skip installation of the actual project. In other
  words using :option:`--skip-install` installs only the dependencies
  of the project found in requirements.txt. Thanks to `Phillip
  O'Donnell <https://github.com/phillipod>`_ for implementing!
* Support custom installation suffix instead of the package name via
  :option:`--install-suffix`. Thanks to `Phillip O'Donnell
  <https://github.com/phillipod>`_ for implementing!

0.9
===

* Support using system packages via a command line flag
  :option:`--use-system-packages`. Thanks to `Wes Mason
  <https://github.com/1stvamp>`_ for implementing this feature!
* Introduce a new, experimental, more modular build system. See the
  :doc:`usage` for documentation.
* Respect the :envvar:`DEB_NO_CHECK` environment variable.

0.8
===

* Support for running triggers upon host interpreter update. This new
  feature makes it possible to upgrade the host Python interpreter
  and avoid breakage of all the virtualenvs installed with
  dh-virtualenv. For usage, see the the :doc:`tutorial`. Huge thanks to
  `Jürgen Hermann <https://github.com/jhermann>`_ for implementing
  this long wanted feature!
* Add support for the built-in ``venv`` module. Thanks to `Petri
  Lehtinen <https://github.com/akheron>`_!
* Allow custom ``pip`` flags to be passed via the
  :option:`--extra-pip-arg` flag. Thanks to `@labeneator
  <https://github.com/labeneator>`_ for the feature.

0.7
===

* **Backwards incompatible** Support running tests. This change
  breaks builds that use distutils. For those cases a flag
  :option:`--no-test` needs to be passed.
* Add tutorial to documentation
* Don't crash on debbuild parameters :option:`-i` and :option:`-a`
* Support custom source directory (debhelper's flag :option:`-D`)

0.6
===

First public release of *dh-virtualenv*
