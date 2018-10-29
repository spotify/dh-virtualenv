=================
 Getting Started
=================

This tutorial will guide you through setting up your first project
using *dh-virtualenv*. Having some knowledge on how Debian packages
work might help, but it is not a mandatory requirement when working
on simple projects.

You also need some basic build tools, so you should install these packages:

.. code-block:: shell

    sudo apt-get install build-essential debhelper devscripts equivs

These are only required on the *build host*,
not the *target hosts* you later install the built packages on.

If you perform your :ref:`package builds in a Docker container <docker-builds>`,
you can also skip installing these tools, because then only ``docker-ce`` is needed.


Step 1: Install dh-virtualenv
=============================

.. rubric:: Overview

In order to use it, you need to install *dh-virtualenv* as a debhelper add-on
on the build host. For Debian and Ubuntu, there are pre-built packages for
the 1.0 version available – note that some of this info might get outdated over time,
so take extra care to check the version numbers you're actually getting vs. what features you need.

The following paragraphs describe the various installation options,
including building from source when your specific environment provides
no packages or only older versions.

Using pre-1.1 versions is possible, but you don't get all features described in this document,
and not all projects using dh-virtualenv might work with older versions
(check their documentation).

.. rubric:: Package installation from OS repositories

On Debian *Stretch* (stable) it is a simple ``apt install dh-virtualenv`` to get v1.0 installed.
To install on *Jessie* (oldstable) from `their package repositories`_, use these commands:

.. code-block:: bash

    echo "deb http://ftp.debian.org/debian jessie-backports main" \
        | sudo tee /etc/apt/sources.list.d/jessie-backports.list >/dev/null
    sudo apt-get update -qq
    sudo apt-get install -t jessie-backports dh-virtualenv

Note that ``jessie-backports`` also only offers the 1.0 version.

Another option to check out for *Ubuntu* is `this PPA`_, maintained by the author.

It is also possible to get newer versions from Debian testing (sid)
or recent releases in the `official Ubuntu repositories`_.
Since dh-virtualenv has the ``all`` architecture (contains no native code),
that is generally possible, but you might need to take extra care of dependencies.
The recommendation is to only follow that route in :ref:`Docker container builds <docker-builds>`,
where manipulating dependencies has no lasting effect
– don't do that on your workstation.

.. rubric:: Build your own package

For all other platforms you have to build and install the tool yourself.
The easiest way (since v1.1) is to build the package using Docker
with the ``invoke bdist_deb`` command in a boot-strapped working directory,
see the README for details on that.
Using Docker also allows cross-distribution builds.

Otherwise, after you have cloned the repository,
you must install build tools and dependencies on your worksatation,
and then start the build:

.. code-block:: bash

   # Install needed packages
   sudo apt-get install devscripts python-virtualenv python-sphinx \
                        python-sphinx-rtd-theme git equivs
   # Clone git repository
   git clone https://github.com/spotify/dh-virtualenv.git
   # Change into working directory
   cd dh-virtualenv
   # This will install build dependencies
   sudo mk-build-deps -ri
   # Build the *dh-virtualenv* package
   dpkg-buildpackage -us -uc -b

   # And finally, install it (you might have to solve some
   # dependencies when doing this)
   sudo dpkg -i ../dh-virtualenv_<version>.deb


.. _`their package repositories`: https://packages.debian.org/source/sid/dh-virtualenv
.. _`official Ubuntu repositories`: http://packages.ubuntu.com/search?keywords=dh-virtualenv
.. _`this PPA`: https://launchpad.net/~spotify-jyrki/+archive/ubuntu/dh-virtualenv


Step 2: Set up packaging for your project
=========================================

Grab your favourite Python project you want to use *dh-virtualenv*
with and set it up. Only requirement is that your project has a
somewhat sane ``setup.py`` and requirements listed in a
``requirements.txt`` file. Note however that defining any requirements
is not mandatory, if you have none.

Instead of following all the steps outlined below,
you can use cookiecutters (project templates) to quickly create the needed information
in the ``debian/`` directory for any existing project.

 * `dh-virtualenv-mold <https://github.com/Springerle/dh-virtualenv-mold>`_ is
   a cookiecutter template to add easy Debianization to any existing Python project.
 * `debianized-pypi-mold <https://github.com/Springerle/debianized-pypi-mold>`_
   does the same for 3rd party software released to PyPI which you want to package
   for deployment.

See the related READMEs for details.

For the manual way,
start with defining the Debian packaging metadata for your software.
To do this, create a directory called ``debian`` in the project root.

To be able to build a debian package, a few files are needed. First, we
need to define the compatibility level of the project. For this, do:

.. code-block:: bash

   echo "9" > debian/compat

The 9 is a magic number for latest compatibility level, but we don't
need to worry about that. Next we need a file that tells what our
project is about, a file called ``control``.
Create a ``debian/control`` file similar to the following:

.. code-block:: control

   Source: my-awesome-python-software
   Section: python
   Priority: extra
   Maintainer: Matt Maintainer <matt@example.com>
   Build-Depends: debhelper (>= 9), python, dh-virtualenv (>= 0.8)
   Standards-Version: 3.9.5

   Package: my-awesome-python-software
   Architecture: any
   Pre-Depends: dpkg (>= 1.16.1), python2.7 | python2.6, ${misc:Pre-Depends}
   Depends: ${misc:Depends}
   Description: A short summary of what this is.
       Further indented lines can contain extra information.
       .
       A single dot separates paragraphs.

The ``control`` file is used to define the build dependencies, so if you
are building a package that requires for example ``lxml``, make sure
you define ``libxml2-dev`` in *Build-Depends*.

*Depends* in the 2nd section is used to define run-time dependencies.
The *debhelper* magic will usually take care of that via the ``${misc:Depends}`` you see above.

To help keeping your installed virtualenv in sync with the host's Python
interpreter in case of updates, create a file named
``debian/«pkgname».triggers``, where ``«pkgname»`` is what you
named your package in the ``control`` file. It triggers a special script
whenever the Python binary changes; don't worry, that script is provided
by ``dh-virtualenv`` automatically.

.. rubric:: «pkgname».triggers

.. code-block:: ini

   # Register interest in Python interpreter changes (Python 2 for now); and
   # don't make the Python package dependent on the virtualenv package
   # processing (noawait)
   interest-noawait /usr/bin/python2.6
   interest-noawait /usr/bin/python2.7

   # Also provide a symbolic trigger for all dh-virtualenv packages
   interest dh-virtualenv-interpreter-update

That file *must* end with a new-line –
if your editor is misconfigured to eat the end of the last line in a file,
you better fix that.

Note that if you provide a custom ``postinst`` script with your package,
then don't forget to put the ``#DEBHELPER#`` marker into it, else the trigger
script will be missing.
The same applies to other maintainer scripts.

Next, we need a changelog file. It is basically a documentation of
changes in your package plus the source for version number for Debian
package builder. Here's a short sample changelog to be entered in
``debian/changelog``:

::

   my-awesome-python-software (0.1-1) unstable; urgency=low

     * Initial public release

    -- Matt Maintainer <matt@example.com>  Fri, 01 Nov 2013 17:00:00 +0200

You don't need to create this file by hand, a handy tool called
``dch`` exists for entering new changelog entries.

Now, the last bit left is adding the ``debian/rules`` file. This file
is usually an executable *Makefile* that Debian uses to build the package.
The content for that is fairly simple:

.. code-block:: make

  #!/usr/bin/make -f

  %:
  	dh $@ --with python-virtualenv

And there we go, debianization of your new package is ready!

.. tip::

    Do not forget to ``git add`` the ``debian/`` directory *before*
    you build for the first time, because generated files will be added there
    that you don't want in your source code repository.


Step 3: Build your project
==========================

Now you can just build your project by running
``dpkg-buildpackage -us -uc -b``.
Enjoy your newly baked *dh-virtualenv* backed project! ☺
