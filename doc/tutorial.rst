========
Tutorial
========

This tutorial will guide you through setting up your first project
using *dh-virtualenv*. Having some knowledge on how Debian packages
work won't hurt, but it is not necessary a mandatory requirement. You
also need some basic build tools, so it is recommended to install
`build-essential` and `devscripts` packages.


Step 1: Install dh-virtualenv
=============================

In order to use it, you need to install the *dh-virtualenv*. If you
run Debian Jessie (testing), Debian Sid (unstable) or Ubuntu 14.04 LTS (Trusty),
you can install *dh-virtualenv* simply with *apt-get*:

.. code-block:: bash

   sudo apt-get install dh-virtualenv

For other systems the only way is to build and install it yourself.
Steps to do that, after you have cloned the repository are:

.. code-block:: bash

   sudo apt-get install devscripts python-virtualenv git equivs # Install needed packages
   git clone https://github.com/spotify/dh-virtualenv.git       # Clone Git repository
   cd dh-virtualenv                                             # Move into the repository
   sudo mk-build-deps -ri                                       # This will install build dependencies
   dpkg-buildpackage -us -uc -b                                 # Build the *dh-virtualenv* package

   # and finally, install it (you might have to solve some
   # dependencies when doing this):
   sudo dpkg -i ../dh-virtualenv_<version>.deb


Step 2: Setup the Debian packaging
==================================

Grab your favourite Python project you want to use *dh-virtualenv*
with and set it up. Only requirement is that your project has a
somewhat sane ``setup.py`` and requirements listed in a
``requirements.txt`` file. Note however that the defining requirements
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
   Build-Depends: debhelper (>= 9), python, dh-virtualenv
   Standards-Version: 3.9.5

   Package: my-awesome-python-software
   Architecture: any
   Depends: ${python:Depends}, ${misc:Depends}
   Description: really neat package!
    second line can contain extra information about it.

The ``control`` file is used to define the build dependencies, so if you
are building a package that requires for example ``lxml``, make sure
you define ``libxml2-dev`` in *Build-Depends* etc.

*Depends* in the lower section is used to define run-time dependencies.
Following the example above, in case of lxml you would add ``libxml2``
in to the *Depends* field.

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
-uc``. Enjoy your newly baked *dh-virtualenv* backed project! :)
