===============================
 Real-World Projects Show-Case
===============================

These complete projects show how to combine the features of dh-virtualenv
and Debian packaging in general to deliver actual software in the wild.
You'll also see some of the recipes of the :doc:`howtos` applied in a wider context.

.. contents:: List of Projects
    :local:


.. _example-debianized-sentry:

debianized-sentry
=================

:Author: Jürgen Hermann
:URL: https://github.com/1and1/debianized-sentry

The project packages `Sentry.io`, adding systemd integration and default configuration
for the Sentry Django/uWSGI app and related helper services.
It also shows how to package 3rd party software as relased on PyPI,
keeping the packaging code separate from the packaged project.

It is based on the `debianized-pypi-mold`_ cookiecutter, which allows you to set up
such projects *from scratch* to the first build in typically under an hour.

.. _`debianized-pypi-mold`: https://github.com/Springerle/debianized-pypi-mold


.. _example-debianized-jupyterhub:

debianized-jupyterhub
=====================

:Author: Jürgen Hermann
:URL: https://github.com/1and1/debianized-jupyterhub

JupyterHub has a Node.js service that implements its *configurable HTTP proxy* component,
so this project applies the :ref:`node-env` recipe to install CHP.
It also uses Python 3.5 instead of Python 2.

Otherwise, it is very similar to the :ref:`example-debianized-sentry` project,
which is no surprise since they're based on the same cookiecutter template.


.. _example-configsite:

configsite
==========

:Author: Nadav-Ruskin
:URL: https://github.com/Nadav-Ruskin/configsite

This project shows how to cross-package a web service for the ARM platform,
using `QEMU`_ and `Docker`_.


.. _`QEMU`: https://www.qemu.org/
.. _`Docker`: https://www.docker.com/
