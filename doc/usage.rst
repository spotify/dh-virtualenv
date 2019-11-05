=================
 Packaging Guide
=================

Building packages with *dh-virtualenv* is relatively easy to start with,
but it also supports lot of customization to match your specific needs.

By default, *dh-virtualenv* installs your packages under
``/opt/venvs/«packagename»``. The package name is provided by
the ``debian/control`` file.

To use an alternative install prefix, add a line like the following
to the top of your ``debian/rules`` file.

.. code-block:: make

    export DH_VIRTUALENV_INSTALL_ROOT=«/your/custom/install/dir»

dh_virtualenv will now use the value of
:envvar:`DH_VIRTUALENV_INSTALL_ROOT` instead of ``/opt/venvs``
when it constructs the install path.

To use an install suffix other than the package name, call
``dh_virtualenv`` using the :option:`--install-suffix` command
line option. See :ref:`advanced-usage` for further information on passing
options.


Simple usecase
==============

To signal debhelper to use *dh-virtualenv* for building your
package, you need to pass ``--with python-virtualenv`` to the debhelper
sequencer.

In a nutshell, the simplest ``debian/rules`` file to build using
*dh-virtualenv* looks like this:

.. code-block:: make

    #!/usr/bin/make -f

    %:
            dh $@ --with python-virtualenv

However, the tool makes a few assumptions of your project's structure:

 * For installing requirements, you need to have a file called
   ``requirements.txt`` in the root directory of your project. The
   requirements file is not mandatory.
 * The project must have a ``setup.py`` file in the root of the
   project. ``dh_virtualenv`` will run ``setup.py install`` to add
   your project to the virtualenv.

After these preparations, you can just build the package with your favorite tool!


Environment variables
=====================

Certain environment variables can be used to customise the behaviour
of the debhelper sequencer in addition to the standard debhelper
variables.

.. envvar:: DH_VIRTUALENV_INSTALL_ROOT

   Define a custom root location to install your package(s). The
   resulting location for a specific package will be
   ``$DH_VIRTUALENV_INSTALL_ROOT/«<packagename»``,
   unless :option:`--install-suffix` is also used to change ``«<packagename»``.


Command line options
====================

To change its default behavior, the ``dh_virtualenv`` command accepts a
few command line options:

.. option:: -p <package>, --package <package>

   Act on the package named *<package>*.

.. option:: -N <package>, --no-package <package>

   Do not act on the specified package.

.. option:: -v, --verbose

   Turn on verbose mode. This has a few effects: it sets the root logger
   level to ``DEBUG``, and passes the verbose flag to ``pip`` when
   installing packages. This can also be provided using the standard
   ``DH_VERBOSE`` environment variable.

.. option:: --install-suffix <suffix>

   Override virtualenv installation suffix. The suffix is appended to
   ``/opt/venvs``, or the :envvar:`DH_VIRTUALENV_INSTALL_ROOT`
   environment variable if specified, to construct the installation
   path.

.. option:: --extra-index-url <url>

   Use extra index url *<url>* when running ``pip`` to install
   packages. This can be provided multiple times to pass multiple URLs
   to ``pip``. A common use-case is enabling a private Python package repository.

.. option:: --preinstall <package>

   Package to install before processing the requirements. This flag
   can be used to provide a package that is installed by ``pip``
   before processing the requirements file. It is handy if you need to
   install a custom setup script or other packages needed
   to parse ``setup.py``, and can be provided multiple times to
   pass multiple packages for pre-install.

.. option:: --postinstall <package>

    Package to install after processing the requirements. This flag
    can be used to provide a package that is installed by ``pip``.
    This is useful when additional ``pip`` commands are needed to install
    a package (e.g. ``--install-option``), which would otherwise cause
    packages in the requirements to not use wheel builds.

.. option:: --extras <name>

   .. versionadded:: 1.1

   Name of extras defined in the main package (specifically its ``setup.py``, in ``extras_require``).
   You can pass this multiple times to add different extra requirements.

.. option:: --pip-tool <exename>

   Executable that will be used to install requirements after the
   preinstall stage.  Usually you'll install this program by using the
   ``--preinstall`` argument. The replacement is expected to be found
   in the virtualenv's ``bin/`` directory.

.. option:: --upgrade-pip

   .. versionadded:: 1.0

   Force upgrading to the latest available release of ``pip``.
   This is the first thing done in the pre-install stage,
   and uses a separate ``pip`` call.

   Options provided via :option:`--extra-pip-arg` are ignored here,
   because the default ``pip`` of your system might not support them
   (since version 1.1).

   *Note:* This can produce non-repeatable builds. See also :option:`--upgrade-pip-to`.

.. option:: --upgrade-pip-to <VERSION>

   .. versionadded:: 1.2

   Same as :option:`--upgrade-pip`, but install an explicitly provided version.
   You can specify ``latest`` to get the exact same behaviour as with the simple option.

   *Note:* This can be used for more repeatable builds that do not have the risk of
   breaking on a new ``pip`` release.

.. option:: --index-url <URL>

   Base URL of the PyPI server. This flag can be used to pass in a
   custom URL to a PyPI mirror. It's useful if you have an
   internal PyPI mirror, or you run a special instance that only
   exposes selected packages of PyPI. If this is not provided, the
   default will be whatever ``pip`` uses as default (usually the API of
   ``https://pypi.org/``).

.. option:: --extra-pip-arg <PIP ARG>

   Extra arguments to pass to the pip executable. This is useful if
   you need to change the behaviour of pip during the packaging process.
   You can use this flag multiple times to pass in different pip flags.

   As an example, adding ``--extra-pip-arg --no-compile`` in the call of a
   ``override_dh_virtualenv`` rule in the ``debian/rules`` file will
   disable the generation of ``*.pyc`` files.

.. option:: --extra-virtualenv-arg <VIRTUALENV ARG>

   Extra parameters to pass to the virtualenv executable. This is useful if
   you need to change the behaviour of virtualenv during the packaging process.
   You can use this flag multiple times to pass in different virtualenv flags.

.. option:: --requirements <REQUIREMENTS FILE>

   Use a different requirements file when installing. Some packages
   such as `pbr <http://docs.openstack.org/developer/pbr/>`_ expect
   the ``requirements.txt`` file to be a simple list of requirements
   that can be copied verbatim into the ``install_requires``
   list. This command option allows specifying a different
   ``requirements.txt`` file that may include pip specific flags such
   as ``-i``, ``-r-`` and ``-e``.

.. option:: --setuptools

   Use setuptools instead of distribute in the virtualenv.

.. option:: --setuptools-test

   .. versionadded:: 1.0

   Run ``python setup.py test`` when building the package. This was
   the old default behaviour before version 1.0. This option is
   incompatible with the deprecated :option:`--no-test`.

.. option:: --python <path>

   Use a specific Python interpreter found in ``path`` as the
   interpreter for the virtualenv. Default is to use the system
   default, usually ``/usr/bin/python``.

.. option:: --builtin-venv

   Enable the use of the build-in ``venv`` module, i.e. use ``python -m venv``
   to create the virtualenv. It will only work with Python 3.4 or later,
   e.g. by using the option
   :option:`--python` ``/usr/bin/python3.4``.

.. option:: -S, --use-system-packages

   Enable the use of system site-packages in the created virtualenv
   by passing the ``--system-site-packages`` flag to ``virtualenv``.

.. option:: --skip-install

   Skip running ``pip install .`` after dependencies have been
   installed. This will result in anything specified in ``setup.py`` being
   ignored. If this package is intended to install a virtualenv
   and a program that uses the supplied virtualenv, it is up to
   the user to ensure that if ``setup.py`` exists, any installation logic
   or dependencies contained therein are handled.

   This option is useful for web application deployments, where the
   package's virtual environment merely supports
   an application installed via other means.
   Typically, the ``debian/«packagename».install`` file is used
   to place the application at a location outside of the virtual environment.

.. option:: --pypi-url <URL>

   .. deprecated:: 1.0
      Use :option:`--index-url` instead.

.. option:: --no-test

   .. deprecated:: 1.0
      This option has no effect. See :option:`--setuptools-test`.


.. _advanced-usage:

Advanced usage
==============

To provide command line options to the ``dh_virtualenv`` step,
use debhelper's override mechanism.

The following ``debian/rules`` will provide *http://example.com* as
an additional source of Python packages:

.. code-block:: make

    #!/usr/bin/make -f

    %:
            dh $@ --with python-virtualenv

    override_dh_virtualenv:
            dh_virtualenv --extra-index-url http://example.com


pbuilder and dh-virtualenv
==========================

Building your Debian package in a pbuilder_ environment can help to ensure
proper dependencies and repeatable builds. However, precisely because pbuilder
creates its own build environment, build failues can be much more difficult to
understand and troubleshoot. This is especially true when there is a pip error
inside the pbuilder environment. For that reason, make sure that you can build
your Debian package successfully outside of a pbuilder environment before
trying to build it inside.

With those caveats, here are some tips for making pip and dh_virtual work
inside pbuilder.

If you want pip to retrieve packages from the network, you need to
add ``USENETWORK=yes`` to your /etc/pbuilderrc or ~/.pbuilderrc file.

pip has several options that can be used to make it more compatible
with pbuilder.

Use ``--no-cache-dir`` to stop creating wheels in your home directory,
which will fail when running in a pbuilder environment, because
pbuilder sets the HOME environment variable to "/nonexistent".

Use ``--no-deps`` to make pip builds more repeatable_.

Use ``--ignore-installed`` to ensure that pip installs every package in
``requirements.txt`` in the virtualenv. This option is especially important if
you are using the --system-site-packages option in your virtualenv.

Here's an example of how to use these arguments in your ``rules`` file.

.. code-block:: make

                override_dh_virtualenv:
                	dh_virtualenv \
                	--extra-pip-arg "--ignore-installed" \
                	--extra-pip-arg "--no-deps" \
                	--extra-pip-arg "--no-cache-dir"

.. _pbuilder: https://wiki.ubuntu.com/PbuilderHowto

.. _repeatable: https://pip.readthedocs.org/en/stable/user_guide.html#ensuring-repeatability


Experimental buildsystem support
================================

.. important::

    This section describes a completely experimental
    functionality of dh-virtualenv.

Starting with version 0.9 of dh-virtualenv, there is a buildsystem alternative.
The main difference in use is that instead of the ``--with python-virtualenv``
option, ``--buildsystem=dh_virtualenv`` is passed to debhelper. The ``debian rules``
file should look like this:

.. code-block:: make

    #!/usr/bin/make -f

    %:
            dh $@ --buildsystem=dh_virtualenv

Using the buildsystem instead of the part of the sequence (in other
words, instead of the ``--with python-virtualenv``) one can get more
flexibility into the build process.

Flexibility comes from the fact that buildsystem will have individual
steps for configure, build, test and install and those can be
overridden by adding ``override_dh_auto_<STEP>`` target into the
``debian/rules`` file. For example:

.. code-block:: make

    #!/usr/bin/make -f

    %:
            dh $@ --buildsystem=dh_virtualenv

    override_dh_auto_test:
            py.test test/

In addition the separation of build and install steps makes it
possible to use ``debian/install`` files to include built files into
the Debian package. This is not possible with the sequencer addition.

The build system honors the :envvar:`DH_VIRTUALENV_INSTALL_ROOT`
environment variable. Following other environment variables can be
used to customise the functionality:

.. envvar:: DH_VIRTUALENV_ARGUMENTS

   Pass given extra arguments to the ``virtualenv`` command

   For example:

   .. code-block:: make

      export DH_VIRTUALENV_ARGUMENTS="--no-site-packages --always-copy"

   The default is to create the virtual environment with
   ``--no-site-packages``.

.. envvar:: DH_VIRTUALENV_INSTALL_SUFFIX

   Override the default virtualenv name, instead of source package name.

   For example:

   .. code-block::make

      export DH_VIRTUALENV_INSTALL_SUFFIX=venv

.. envvar:: DH_REQUIREMENTS_FILE

   .. versionadded:: 1.0

   Override the location of requirements file. See :option:`--requirements`.

.. envvar:: DH_UPGRADE_PIP

   .. versionadded:: 1.0

   Force upgrade of the ``pip`` tool by setting
   :envvar:`DH_UPGRADE_PIP` to empty (latest version) or specific
   version. For example:

   .. code-block::make

      export DH_UPGRADE_PIP=8.1.2

.. envvar:: DH_UPGRADE_SETUPTOOLS

   .. versionadded:: 1.0

   Force upgrade of setuptools by setting
   :envvar:`DH_UPGRADE_SETUPTOOLS` to empty (latest version) or
   specific version.

.. envvar:: DH_UPGRADE_WHEEL

   .. versionadded:: 1.0

   Force upgrade of wheel by setting ``DH_UPGRADE_WHEEL`` to empty
   (latest version) or specific version.

.. envvar:: DH_PIP_EXTRA_ARGS

   .. versionadded:: 1.0

   Pass additional parameters to the ``pip`` command. For example:

   .. code-block:: make

      export DH_PIP_EXTRA_ARGS="--no-index --find-links=./requirements/wheels"
