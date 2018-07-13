=================
 Getting Started
=================

This tutorial will guide you through setting up your first project
using *dh-virtualenv*. Having some knowledge on how Debian packages
work might help, but it is not a mandatory requirement.

You also need some basic build tools, so you should install these packages:

.. code-block:: shell

    sudo apt-get install build-essential debhelper devscripts equivs

These are only required on the *build host*, not the *target hosts* you later install the built packages on.


Step 1: Install dh-virtualenv
=============================

In order to use it, you need to install *dh-virtualenv* as a debhelper add-on
on the build host. For Debian and Ubuntu, there are pre-built packages for
the 1.0 version available – note that some of this info might get outdated over time,
so take extra care to check the version numbers you're actually getting.

The following paragraphs describe the various installation options,
including building from source when your specific environment provides
no packages or only older versions.
Using pre-1.0 versions might be possible, but you don't get all features described in this document,
and not all projects using dh-virtualenv might work with older versions
(check their documentation).

To install on *Jessie* (Debian stable) from `their package repositories`_, use these commands:

.. code-block:: bash

    echo "deb http://ftp.debian.org/debian jessie-backports main" \
        | sudo tee /etc/apt/sources.list.d/jessie-backports.list >/dev/null
    sudo apt-get update -qq
    sudo apt-get install -t jessie-backports dh-virtualenv

Note that only ``jessie-backports`` offers the 1.0 version.
Newer versions (Stretch and Sid) provide 1.0 out-of-the-box.

In the `official Ubuntu repositories`_, *Zesty* provides a package
that works on older releases too. So on *Zesty* use a standard ``apt-get`` install,
and on older releases do this:

.. code-block:: bash

    ( cd /tmp && curl -LO "http://mirrors.kernel.org/ubuntu/pool/universe/d/dh-virtualenv/dh-virtualenv_1.0-1_all.deb" )
    sudo dpkg -i /tmp/dh-virtualenv_1.0-1_all.deb

Another option to check out for *Ubuntu* is `this PPA`_, maintained by the author.

For all other systems you have to build and install the tool yourself.
Steps to do that, after you have cloned the repository, are:

.. code-block:: bash

   sudo apt-get install devscripts python-virtualenv python-sphinx python-sphinx-rtd-theme git equivs # Install needed packages
   git clone https://github.com/spotify/dh-virtualenv.git       # Clone Git repository
   cd dh-virtualenv                                             # Move into the repository
   sudo mk-build-deps -ri                                       # This will install build dependencies
   dpkg-buildpackage -us -uc -b                                 # Build the *dh-virtualenv* package

   # and finally, install it (you might have to solve some
   # dependencies when doing this):
   sudo dpkg -i ../dh-virtualenv_<version>.deb


.. _`their package repositories`: https://packages.debian.org/source/sid/dh-virtualenv
.. _`official Ubuntu repositories`: http://packages.ubuntu.com/search?keywords=dh-virtualenv
.. _`this PPA`: https://launchpad.net/~spotify-jyrki/+archive/ubuntu/dh-virtualenv


Step 2: Set up Debian packaging
===============================

Grab your favourite Python project you want to use *dh-virtualenv*
with and set it up. Only requirement is that your project has a
somewhat sane ``setup.py`` and requirements listed in a
``requirements.txt`` file. Note however that defining any requirements
is not mandatory.

Next you need to define the Debian packaging for your software. To do
this, create a directory called ``debian`` in the project root.

To be able to build a debian package, a few files are needed. First, we
need to define the compatibility level of the project. For this, do:

.. code-block:: bash

   echo "9" > debian/compat

The 9 is a magic number for latest compatibility level, but we don't
need to worry about that. Next we need a file that tells what our
project is about, a file called ``control``. Enter a following
``debian/control`` file:

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
   Description: really neat package!
    second line can contain extra information about it.

The ``control`` file is used to define the build dependencies, so if you
are building a package that requires for example ``lxml``, make sure
you define ``libxml2-dev`` in *Build-Depends* etc.

*Depends* in the lower section is used to define run-time dependencies.
Following the example above, in case of lxml you would add ``libxml2``
in to the *Depends* field.

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

Note that if you provide a custom ``postinst`` script with your package,
then don't forget to put the ``#DEBHELPER#`` marker into it, else the trigger
script will be missing.

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

Now, last bit is left, which is the ``debian/rules`` file. This file
is basically a Makefile that Debian uses to build the package. Content
for that is fairly straightforward:

.. code-block:: make

  #!/usr/bin/make -f

  %:
  	dh $@ --with python-virtualenv

And there we go, debianization of your new package is ready!


Step 3: Build your project
==========================

Now you can just build your project by running ``dpkg-buildpackage -us
-uc``. Enjoy your newly baked *dh-virtualenv* backed project! ☺
