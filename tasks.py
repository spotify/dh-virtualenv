# -*- coding: utf-8 -*-
# pylint: disable=wildcard-import, unused-wildcard-import, bad-continuation
""" Project automation using Invoke.
"""
from __future__ import absolute_import, unicode_literals

import os

from rituals import config
from rituals.easy import *  # pylint: disable=redefined-builtin

config.set_flat_layout()
os.environ['INVOKE_RITUALS_DOCS_SOURCES'] = os.path.join(os.path.dirname(__file__), 'doc')


@task(help={'distro': "base image name to use for building"})
def bdist_deb(ctx, distro=None):
    """Build package for Debina stable using Docker"""
    ctx.run("docker build --tag dh-venv-builder --build-arg distro={} ."
            .format(distro or 'debian:stable'))
    os.path.exists('dist') or os.makedirs('dist')
    ctx.run("docker run --rm dh-venv-builder tar -C /dpkg -c . | tar -C dist -xv")
    ctx.run("ls -lth dist/")

namespace.add_task(bdist_deb)
