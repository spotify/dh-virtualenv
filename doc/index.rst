.. dh-virtualenv documentation master file, created by
   sphinx-quickstart on Wed Feb 20 17:29:43 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to dh-virtualenv's documentation!
=========================================

Overview
--------

``dh-virtualenv`` is a tool that aims to combine Debian packaging with
self-contained Python software deployment in a pre-built virtualenv.
To do this, the package extends debhelper's build sequence by providing
the new ``dh_virtualenv`` command.

This new command effectively replaces the following commands in the default sequence:

 * ``dh_auto_install``
 * ``dh_python2``
 * ``dh_pycentral``
 * ``dh_pysupport``

In the debhelper build sequence, ``dh_virtualenv`` is inserted right after ``dh_perl``.


.. rubric:: Reading Guide

:doc:`tutorial` helps you to set up your build machine and then package your first simple project.
:doc:`usage` explains all available feature in more detail,
while the :doc:`howtos` demonstrates specific features and tricks
needed for packaging more challenging projects.


Contents of this Manual
-----------------------

.. toctree::
   :maxdepth: 2

   tutorial
   usage
   howtos
   trouble-shooting
   examples
   source
   changes


Indices and Tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
