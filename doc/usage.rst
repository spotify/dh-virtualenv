======================================
 Building packages with dh-virtualenv
======================================

Building packages with *dh-virtualenv* is relatively easy to start
with but it also supports lot of customization to fit in your general
needs.

By default, *dh-virtualenv* installs your packages under
``/usr/share/python/<packagename>``. The package name is provided by
the ``debian/control`` file.

To use an alternative install prefix, add a line like

.. code-block:: make

  export DH_VIRTUALENV_INSTALL_ROOT=</your/custom/install/dir>

to the top of your ``debian/rules`` file. dh_virtualenv will use
DH_VIRTUALENV_INSTALL_ROOT instead of ``/usr/share/python`` when it
constructs the install path.

To use an install suffix other than the package name, call the 
``dh_virtualenv`` command using with the ``--install-suffix`` 
command line option. See Advanced Usage for further information
on passing options.

Simple usecase
==============

To signal debhelper to use *dh-virtualenv* for building your
package, you need to pass ``--with python-virtualenv`` to debhelper
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
   project. Sequencer will run ``setup.py install`` to install the
   package inside the virtualenv.

After these are place, you can just build the package with your
favorite tool!

Command line options
====================

To change the default behavior the ``dh_virtualenv`` command accepts a
few command line options:

.. cmdoption:: -p <package>, --package <package>

   Act on the package named *<package>*

.. cmdoption:: -N <package>, --no-package <package>

   Do not act on the specified package

.. cmdoption:: -v, --verbose

   Turn on verbose mode. This has a few effects: it sets root logger
   level to ``DEBUG`` and passes verbose flag to ``pip`` when
   installing packages. This can also be provided using the standard
   ``DH_VERBOSE`` environment variable.

.. cmdoption:: --install-suffix <suffix>

   Override virtualenv installation suffix. The suffix is appended to
   ``/usr/share/python``, or the ``DH_VIRTUALENV_INSTALL_ROOT``
   environment variable if specified, to construct the installation
   path.

.. cmdoption:: --extra-index-url <url>

   Use extra index url *<url>* when running ``pip`` to install
   packages. This can be provided multiple times to pass multiple URLs
   to ``pip``. This is useful if you for example have a private Python
   Package Index.

.. cmdoption:: --preinstall <package>

   Package to install before processing the requirements. This flag
   can be used to provide a package that is installed by ``pip``
   before processing requirements file. This is handy if you need to
   install for example a custom setup script or other packages needed
   to parse ``setup.py``. This flag can be provided multiple times to
   pass multiple packages for pre-install.

.. cmdoption:: --pypi-url <URL>

   Base URL of the PyPI server. This flag can be used to pass in a
   custom URL to a PyPI mirror. It's useful if you for example have an
   internal mirror of the PyPI or you run a special instance that only
   exposes selected packages of PyPI. If this is not provided, the
   default will be whatever ``pip`` uses as default (usually
   ``http://pypi.python.org/simple``).

.. cmdoption:: --extra-pip-arg <PIP ARG>

   Extra parameters to pass to the pip executable. This is useful if
   you need to change the behaviour of pip during the packaging process.
   You can use this flag multiple times to pass in different pip flags.
   As an example passing in --extra-pip-arg "--no-compile" to the
   override_dh_virtualenv section of the debian/rules file will
   disable the generation of pyc files.

.. cmdoption:: --requirements <REQUIREMENTS FILE>

   Use a different requirements file when installing. Some packages
   such as `pbr <http://docs.openstack.org/developer/pbr/>`_ expect
   the ``requirements.txt`` file to be a simple list of requirements
   that can be copied verbatim into the ``install_requires``
   list. This command option allows specifying a different
   ``requirements.txt`` file that may include pip specific flags such
   as ``-i``, ``-r-`` and ``-e``.

.. cmdoption:: --setuptools

   Use setuptools instead of distribute in the virtualenv

.. cmdoption:: --no-test

   Skip running ``python setup.py test`` after dependencies and the
   package is installed. This is useful if the Python code is packaged
   using distutils and not setuptools.

.. cmdoption:: --python <path>

   Use a specific Python interpreter found in ``path`` as the
   interpreter for the virtualenv. Default is to use the system
   default, usually ``/usr/bin/python``.

.. cmdoption:: --builtin-venv

   Enable the use of the build-in ``venv`` module, i.e. use ``python
   -m venv`` to create the virtualenv. For this to work, requires
   Python 3.4 or later to be used, e.g. by using the option ``--python
   /usr/bin/python3.4``. (Python 3.3 has the ``venv`` module, but
   virtualenvs created with Python 3.3 are not bootstrapped with
   setuptools or pip.)

.. cmdoption:: -S, --use-system-packages

   Enable the use of system site-packages in the created virtualenv
   by passing the ``--system-site-packages`` flag to ``virtualenv``.

.. cmdoption:: --skip-install

   Skip running ``pip install .`` after dependencies have been
   installed. This will result in anything specified in setup.py being
   ignored. If this package is intended to install a virtualenv
   and a program that uses the supplied virtualenv, it is up to
   the user to ensure that if setup.py exists, any installation logic
   or dependencies contained therein are handled.

   This option is useful for web application deployments where the
   package is expected contain the virtual environment to support
   an application which itself may be installed via some other means
   -- typically, by the packages ``./debian/<packagename>.install``
   file, possibly into a directory structure unrelated to the location
   of the virtual environment.


Advanced usage
==============

To provide command line options to ``dh_virtualenv`` sequence the
override mechanism of the debhelper is the best tool.

Following ``debian/rules`` will provide *http://example.com* as
additional Python Package Index URI:

.. code-block:: make

  #!/usr/bin/make -f

  %:
  	dh $@ --with python-virtualenv

  override_dh_virtualenv:
  	dh_virtualenv --extra-index-url http://example.com


Experimental buildsystem support
================================

**Important**: Following chapters describe a completely experimental
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

The build system honors the ``DH_VIRTUALENV_INSTALL_ROOT`` environment
variable. Arguments can be passed to virtualenv by setting
``DH_VIRTUALENV_ARGUMENTS``. For example:

.. code-block:: make

  export DH_VIRTUALENV_ARGUMENTS=--no-site-packages --always-copy

The default is to create the virtual environment with ``--no-site-packages``.

Known incompabilities of the buildsystem
----------------------------------------

This section defines the known incompabilities with the sequencer
approach. There are no guarantees that these all get addressed, but
most of them, if not all, probably will.

* No custom Python interpreter supported
* ``Pyvenv`` of Python 3.x is not supported
* No custom arguments outside requirements.txt can be passed to
  ``pip``
