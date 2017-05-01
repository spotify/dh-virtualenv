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
