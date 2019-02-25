====================
 Packaging Cookbook
====================

This chapter has recipes and tips for specific dh-virtualenv use-cases,
like proper handling of binary ``manylinux1`` wheels.
It also demonstrates some Debian packaging and debhelper features
that are useful in the context of Python software packaging.

.. contents:: List of Recipes
    :local:


.. _py3-package:

Building Packages for Python3
=============================

The Python2 EOL in 2020 is not so far away, so you better start to use
Python3 for new projects, and port old ones that you expect to survive until then.
The following is for *Ubuntu Xenial* or *Debian Stretch* with Python 3.5,
and on *Ubuntu Bionic* you get Python 3.6.

In ``debian/control``, the ``Build-Depends`` and ``Pre-Depends`` lists
have to refer to Python3 packages.

.. code-block:: ini

    Source: py3software
    Section: contrib/python
    …
    Build-Depends: debhelper (>= 9), python3, dh-virtualenv (>= 1.0),
        python3-setuptools, python3-pip, python3-dev, libffi-dev
    …

    Package: py3software
    …
    Pre-Depends: dpkg (>= 1.16.1), python3 (>= 3.5), ${misc:Pre-Depends}

And the Python update triggers in ``debian/«pkgname».triggers`` need to be adapted, too.

.. code-block:: ini

    …
    interest-noawait /usr/bin/python3.5
    …

You may also need to add the :option:`--python` option in ``debian/rules``.

.. code-block:: make

    %:
        dh $@ --with python-virtualenv

    override_dh_virtualenv:
        dh_virtualenv --python python3

If you're using the buildsystem alternative, it is instead specified through
the :envvar:`DH_VIRTUALENV_ARGUMENTS` variable.

.. code-block:: make

    export DH_VIRTUALENV_ARGUMENTS := --no-site-packages --python python3

    %:
        dh $@ --buildsystem dh_virtualenv


.. _fhs-links:

Making executables available
============================

To make executables in your virtualenv's ``bin`` directory callable from any shell prompt,
do **not** add that directory to the global ``PATH`` by a ``profile.d`` hook or similar.
This would add all the other stuff in there too, and you simply do not want that.

So use the ``debian/«pkgname».links`` file to add a symbolic link to *those* exectuables
you want to be visible, typically the one created by your main application package.

.. code-block:: ini

    opt/venvs/«venvname»/bin/«cmdname» usr/bin/«cmdname»

Replace the contained ``«placeholders»`` with the correct names.
Add more links if there are additional tools, one line per extra executable.
For ``root``-only commands, use ``usr/sbin/…``.


.. _manylinux1:

Handling binary wheels
======================

The introduction of `manylinux`_ wheels via `PEP 513`_ is a gift,
sent by the PyPA community to us lowly developers wanting to use
packages like Numpy while *not* installing a Fortran compiler just for that.

However, two steps during package building often clash with the contained shared libraries,
namely *stripping* (reducing the size of symbol tables)
and scraping package dependencies out of shared libraries (*shlibdeps*).

So if you get errors thrown at you by either ``dh_strip`` or ``dh_shlibdeps``,
extend your ``debian/rules`` file as outlined below.

.. code-block:: makefile

    .PHONY: override_dh_strip override_dh_shlibdeps

    override_dh_strip:
            dh_strip --exclude=cffi

    override_dh_shlibdeps:
            dh_shlibdeps -X/x86/ -X/numpy/.libs -X/scipy/.libs -X/matplotlib/.libs

This example works for the Python data science stack
– you have to list the packages that cause *you* trouble.

.. _manylinux: https://github.com/pypa/manylinux
.. _`PEP 513`: https://www.python.org/dev/peps/pep-0513/


.. _node-env:

Adding Node.js to your virtualenv
=================================

There are polyglot projects with a mix of Python and Javascript code,
and some of the JS code might be executed server-side in a Node.js runtime.
A typical example is server-side rendering for Angular apps with `Angular Universal`_.

If you have this requirement, there is a useful helper named ``nodeenv``,
which extends a Python virtualenv to also support installation of NPM packages.

The following changes in ``debian/control`` require *Node.js* to be available on both
the build and the target hosts.
As written, the current LTS version is selected (i.e. `8.x` in mid 2018).
The `NodeSource packages`_ are recommended to provide that dependency.

.. code-block:: ini

    …
    Build-Depends: debhelper (>= 9), python3, dh-virtualenv (>= 1.0),
        python3-setuptools, python3-pip, python3-dev, libffi-dev,
        nodejs (>= 8), nodejs (<< 9)
    …
    Depends: ${shlibs:Depends}, ${misc:Depends}, nodejs (>= 8), nodejs (<< 9)
    …


You also need to extend ``debian/rules`` as follows,
change the variables in the first section to define different versions and filesystem locations.

.. code-block:: make

    export DH_VIRTUALENV_INSTALL_ROOT=/opt/venvs
    SNAKE=/usr/bin/python3
    EXTRA_REQUIREMENTS=--upgrade-pip --preinstall "setuptools>=17.1" --preinstall "wheel"
    NODEENV_VERSION=1.3.1

    PACKAGE=$(shell dh_listpackages)
    DH_VENV_ARGS=--setuptools --python $(SNAKE) $(EXTRA_REQUIREMENTS)
    DH_VENV_DIR=debian/$(PACKAGE)$(DH_VIRTUALENV_INSTALL_ROOT)/$(PACKAGE)

    ifeq (,$(wildcard $(CURDIR)/.npmrc))
        NPM_CONFIG=~/.npmrc
    else
        NPM_CONFIG=$(CURDIR)/.npmrc
    endif


    %:
            dh $@ --with python-virtualenv $(DH_VENV_ARGS)

    .PHONY: override_dh_virtualenv

    override_dh_virtualenv:
            dh_virtualenv $(DH_VENV_ARGS)
            $(DH_VENV_DIR)/bin/python $(DH_VENV_DIR)/bin/pip install nodeenv==$(NODEENV_VERSION)
            $(DH_VENV_DIR)/bin/nodeenv -C '' -p -n system
            . $(DH_VENV_DIR)/bin/activate \
                && node /usr/bin/npm install --userconfig=$(NPM_CONFIG) \
                        -g configurable-http-proxy

You want to always copy all but the last line literally.
The lines above it install and embed ``nodeenv`` into the virtualenv
freshly created by the ``dh_virtualenv`` call.
Also remember to use TABs in makefiles (``debian/rules`` is one).

The last (logical) line globally installs the ``configurable-http-proxy`` NPM package
– one important result of using ``-g`` is that Javascript commands appear
in the ``bin`` directory just like Python ones.
That in turn means that in the activated virtualenv Python can easily call those JS commands,
because they're on the ``PATH``.

Change the NPM package name to what you want to install.
``npm`` uses either a local ``.npmrc`` file in the project root,
or else the ``~/.npmrc`` one.
Add local repository URLs and credentials to one of these files.

.. _`NodeSource packages`: https://github.com/nodesource/distributions
.. _`Angular Universal`: https://universal.angular.io/


.. _docker-builds:

Multi-platform builds in Docker
===============================

The code shown here is taken from the :ref:`example-debianized-jupyterhub` project,
and explains how to build a package in a Docker container.

Why build a package in a container? This is why:

* *repeatable* builds in a *clean* environment
* explicitly *documented installation* of build requirements *(as code)*
* easy *multi-distro multi-release builds*

The build is driven by a small shell script named ``build.sh``,
which we use to get the target platform and some project metadata we already have,
and feed that into the Dockerfile via simple ``sed`` templating.

So we work on a copy of the Dockerfile, and that is one reason for
anything in the project workdir that is controlled by git being copied to a staging area (a separate build directory).
The other reason is performance – we present Docker with a pristine copy of our workdir,
and so there are no accidents like ``COPY``\ ing a full development virtualenv
or all of ``.git`` into the container build.

.. rubric:: The build script

Let's get to the code – since we apply the :ref:`node-env` recipe,
we first set the repository where to get Node.js from.

.. literalinclude:: examples/build.sh
    :language: shell
    :end-at: NODEREPO

Next, the given platform and existing project metadata is stored into a bunch of variables.

.. literalinclude:: examples/build.sh
    :language: shell
    :start-after: NODEREPO
    :end-before: Prepare

Based on the collected input parameters, the staging area is set up in the ``build/staging`` directory.
``tar`` does the selective copy work, and ``sed`` is used to inject dynamic values into the copied files.

.. literalinclude:: examples/build.sh
    :language: shell
    :start-at: Prepare
    :end-before: Build in Docker

After all that prep work, we finally get to build our package.
The results are copied from ``/dpkg`` where the Dockerfile put them (see below),
and then the package metadata is shown for a quick visual check if everything looks OK.

.. literalinclude:: examples/build.sh
    :language: shell
    :start-at: Build in Docker


.. rubric:: The Dockerfile

This is the complete Dockerfile, the important things are the two ``RUN`` directives.

.. literalinclude:: examples/Dockerfile.build
    :language: docker

The first ``RUN`` installs all the build dependencies on top of the base image.
The second one then builds the package and makes a copy of the resulting files,
for the build script to pick them up.


.. rubric:: Putting it all together

Here's a sample run of building for *Ubuntu Bionic*.

.. code-block:: console

    $ ./build.sh ubuntu:bionic
    Sending build context to Docker daemon    106kB
    Step 1/6 : FROM ubuntu:bionic AS dpkg-build
    …
    Successfully tagged debianized-jupyterhub-ubuntu-bionic:latest
    ./
    ./jupyterhub_0.9.1-1~bionic_amd64.deb
    ./jupyterhub_0.9.1-1~bionic_amd64.buildinfo
    ./jupyterhub-dbgsym_0.9.1-1~bionic_amd64.ddeb
    ./jupyterhub_0.9.1-1~bionic_amd64.changes
     new debian package, version 2.0.
     size 265372284 bytes: control archive=390780 bytes.
          84 bytes,     3 lines      conffiles
        1214 bytes,    25 lines      control
     2350661 bytes, 17055 lines      md5sums
        4369 bytes,   141 lines   *  postinst             #!/bin/sh
        1412 bytes,    47 lines   *  postrm               #!/bin/sh
         696 bytes,    35 lines   *  preinst              #!/bin/sh
        1047 bytes,    41 lines   *  prerm                #!/bin/sh
         217 bytes,     6 lines      shlibs
         419 bytes,    10 lines      triggers
     Package: jupyterhub
     Version: 0.9.1-1~bionic
     Architecture: amd64
     Maintainer: 1&1 Group <jh@web.de>
     Installed-Size: 563574
     Pre-Depends: dpkg (>= 1.16.1), python3 (>= 3.5)
     Depends: perl:any, libc6 (>= 2.25), libexpat1 (>= 2.1~beta3), libgcc1 (>= 1:4.0), …
     Suggests: oracle-java8-jre | openjdk-8-jre | zulu-8
     Section: contrib/python
     Priority: extra
     Homepage: https://github.com/1and1/debianized-jupyterhub
     Description: Debian packaging of JupyterHub, a multi-user server for Jupyter notebooks.
    …

The package files are now in ``build/``, and you can ``dput`` them into your local repository.


.. _cross-package:

Cross-packaging for ARM targets
===============================

If you need to create packages that can be installed on ARM architectures,
but want to use any build host (e.g. a CI worker),
first install the ``qemu-user-static`` and ``binfmt-support`` packages.

Then build the package by starting a container in QEMU using this ``Dockerfile``.

.. code-block:: docker

    FROM arm32v7/debian:latest

    RUN apt-get update && apt-get -y upgrade && apt-get update \
        && apt-get -y install sudo dpkg-dev debhelper dh-virtualenv python3 python3-venv
    …

The build might fail from time to time, due to unknown causes (maybe instabilities in QEMU).
If you get a package out of it, that works 100% fine, however.

See :ref:`example-configsite` for the full project that uses this.

.. epigraph::

   — with input from `@Nadav-Ruskin`_

.. _`@Nadav-Ruskin`: https://github.com/Nadav-Ruskin
