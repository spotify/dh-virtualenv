======================================
 Building packages with dh-virtualenv
======================================

Building packages with *dh-virtualenv* is relatively easy to start
with but it also supports lot of customization to fit in your general
needs.

By default, *dh-virtualenv* installs your packages under
``/usr/share/python/<packagename>``. The package name is provided by
the ``debian/control`` file.

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
