#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

# This file is part of dh-virtualenv.

# dh-virtualenv is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 2 of the
# License, or (at your option) any later version.

# dh-virtualenv is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with dh-virtualenv. If not, see
# <http://www.gnu.org/licenses/>.
import os

from dh_virtualenv import cmdline
from mock import patch
from nose.tools import eq_


@patch.object(cmdline.DebhelperOptionParser, 'error')
def test_unknown_argument_is_error(error_mock):
    parser = cmdline.DebhelperOptionParser(usage='foo')
    parser.parse_args(['-f'])
    eq_(1, error_mock.call_count)


def test_test_debhelper_option_parsing():
    parser = cmdline.DebhelperOptionParser()
    parser.add_option('--sourcedirectory')
    opts, args = parser.parse_args(['-O--sourcedirectory', '/tmp'])
    eq_('/tmp', opts.sourcedirectory)
    eq_([], args)


def test_parser_picks_up_DH_OPTIONS_from_environ():
    os.environ['DH_OPTIONS'] = '--sourcedirectory=/tmp/'
    parser = cmdline.get_default_parser()
    opts, args = parser.parse_args()
    eq_('/tmp/', opts.sourcedirectory)
    del os.environ['DH_OPTIONS']


def test_get_default_parser():
    parser = cmdline.get_default_parser()
    opts, args = parser.parse_args([
        '-O--sourcedirectory', '/tmp/foo',
        '--extra-index-url', 'http://example.com'
    ])
    eq_('/tmp/foo', opts.sourcedirectory)
    eq_(['http://example.com'], opts.extra_index_url)


def test_that_default_test_option_should_be_true():
    parser = cmdline.get_default_parser()
    opts, args = parser.parse_args()
    eq_(True, opts.test)


def test_that_test_option_can_be_false():
    parser = cmdline.get_default_parser()
    opts, args = parser.parse_args(['--no-test'])
    eq_(False, opts.test)


def test_that_default_use_system_packages_option_should_be_false():
    parser = cmdline.get_default_parser()
    opts, args = parser.parse_args()
    eq_(False, opts.use_system_packages)


def test_that_use_system_packages_option_can_be_true():
    parser = cmdline.get_default_parser()
    opts, args = parser.parse_args(['--use-system-packages'])
    eq_(True, opts.use_system_packages)
