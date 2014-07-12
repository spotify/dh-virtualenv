# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Spotify AB

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

import functools
import os
import shutil
import tempfile
import textwrap

from mock import patch, call

from nose.tools import eq_
from dh_virtualenv import Deployment
from dh_virtualenv.cmdline import get_default_parser


PY_CMD = os.path.abspath('debian/test/usr/share/python/test/bin/python')
PIP_CMD = os.path.abspath('debian/test/usr/share/python/test/bin/pip')


class FakeTemporaryFile(object):
    name = 'foo'


def temporary_dir(fn):
    """Pass a temporary directory to the fn.

    This method makes sure it is destroyed at the end
    """
    @functools.wraps(fn)
    def _inner(*args, **kwargs):
        try:
            tempdir = tempfile.mkdtemp()
            return fn(tempdir, *args, **kwargs)
        finally:
            shutil.rmtree(tempdir)
    return _inner


def test_shebangs_fix():
    deployment = Deployment('test')
    temp = tempfile.NamedTemporaryFile()
    # We cheat here a little. The fix_shebangs walks through the
    # project directory, however we can just point to a single
    # file, as the underlying mechanism is just grep -r.
    deployment.bin_dir = temp.name

    with open(temp.name, 'w') as f:
        f.write('#!/usr/bin/python\n')

    deployment.fix_shebangs()

    with open(temp.name) as f:
        eq_('#!/usr/share/python/test/bin/python\n', f.read())

    with open(temp.name, 'w') as f:
        f.write('#!/usr/bin/env python\n')

    deployment.fix_shebangs()
    with open(temp.name) as f:
        eq_('#!/usr/share/python/test/bin/python\n', f.readline())


def test_shebangs_fix_overridden_root():
    os.environ['DH_VIRTUALENV_INSTALL_ROOT'] = 'foo'
    deployment = Deployment('test')
    temp = tempfile.NamedTemporaryFile()
    # We cheat here a little. The fix_shebangs walks through the
    # project directory, however we can just point to a single
    # file, as the underlying mechanism is just grep -r.
    deployment.bin_dir = temp.name

    with open(temp.name, 'w') as f:
        f.write('#!/usr/bin/python\n')

    deployment.fix_shebangs()

    with open(temp.name) as f:
        eq_('#!foo/test/bin/python\n', f.read())

    with open(temp.name, 'w') as f:
        f.write('#!/usr/bin/env python\n')

    deployment.fix_shebangs()
    with open(temp.name) as f:
        eq_('#!foo/test/bin/python\n', f.readline())
    del os.environ['DH_VIRTUALENV_INSTALL_ROOT']


@patch('os.path.exists', lambda x: False)
@patch('subprocess.check_call')
def test_install_dependencies_with_no_requirements(callmock):
    d = Deployment('test')
    d.pip_prefix = ['pip', 'install']
    d.install_dependencies()
    callmock.assert_has_calls([])


@patch('os.path.exists', lambda x: True)
@patch('subprocess.check_call')
def test_install_dependencies_with_requirements(callmock):
    d = Deployment('test')
    d.pip_prefix = ['pip', 'install']
    d.install_dependencies()
    callmock.assert_called_with(
        ['pip', 'install', '-r', './requirements.txt'])


@patch('subprocess.check_call')
def test_install_dependencies_with_preinstall(callmock):
    d = Deployment('test', preinstall=['foobar'])
    d.pip_prefix = ['pip', 'install']
    d.install_dependencies()
    callmock.assert_called_with(
        ['pip', 'install', 'foobar'])


@patch('os.path.exists', lambda x: True)
@patch('subprocess.check_call')
def test_install_dependencies_with_preinstall_with_requirements(callmock):
    d = Deployment('test', preinstall=['foobar'])
    d.pip_prefix = ['pip', 'install']
    d.install_dependencies()
    callmock.assert_has_calls([
        call(['pip', 'install', 'foobar']),
        call(['pip', 'install', '-r', './requirements.txt'])
    ])


@patch('tempfile.NamedTemporaryFile', FakeTemporaryFile)
@patch('subprocess.check_call')
def test_create_venv(callmock):
    d = Deployment('test')
    d.create_virtualenv()
    eq_('debian/test/usr/share/python/test', d.package_dir)
    callmock.assert_called_with(['virtualenv', '--no-site-packages',
                                 'debian/test/usr/share/python/test'])
    eq_([PY_CMD,
         PIP_CMD,
         'install',
         '--log=' + os.path.abspath('foo')], d.pip_prefix)


@patch('tempfile.NamedTemporaryFile', FakeTemporaryFile)
@patch('subprocess.check_call')
def test_create_venv_with_verbose(callmock):
    d = Deployment('test', verbose=True)
    d.create_virtualenv()
    eq_('debian/test/usr/share/python/test', d.package_dir)
    callmock.assert_called_with(['virtualenv', '--no-site-packages',
                                 '--verbose',
                                 'debian/test/usr/share/python/test'])
    eq_([PY_CMD,
         PIP_CMD,
         '-v',
         'install',
         '--log=' + os.path.abspath('foo')], d.pip_prefix)


@patch('tempfile.NamedTemporaryFile', FakeTemporaryFile)
@patch('subprocess.check_call')
def test_create_venv_with_extra_urls(callmock):
    d = Deployment('test', extra_urls=['foo', 'bar'])
    d.create_virtualenv()
    eq_('debian/test/usr/share/python/test', d.package_dir)
    callmock.assert_called_with(['virtualenv', '--no-site-packages',
                                 'debian/test/usr/share/python/test'])
    eq_([PY_CMD,
         PIP_CMD,
         'install', '--extra-index-url=foo',
         '--extra-index-url=bar',
         '--log=' + os.path.abspath('foo')], d.pip_prefix)


@patch('tempfile.NamedTemporaryFile', FakeTemporaryFile)
@patch('subprocess.check_call')
def test_create_venv_with_custom_index_url(callmock):
    d = Deployment('test', extra_urls=['foo', 'bar'],
                   pypi_url='http://example.com/simple')
    d.create_virtualenv()
    eq_('debian/test/usr/share/python/test', d.package_dir)
    callmock.assert_called_with(['virtualenv', '--no-site-packages',
                                 'debian/test/usr/share/python/test'])
    eq_([PY_CMD,
         PIP_CMD,
         'install',
         '--pypi-url=http://example.com/simple',
         '--extra-index-url=foo',
         '--extra-index-url=bar',
         '--log=' + os.path.abspath('foo')], d.pip_prefix)


@patch('tempfile.NamedTemporaryFile', FakeTemporaryFile)
@patch('subprocess.check_call')
def test_create_venv_with_setuptools(callmock):
    d = Deployment('test', setuptools=True)
    d.create_virtualenv()
    eq_('debian/test/usr/share/python/test', d.package_dir)
    callmock.assert_called_with(['virtualenv', '--no-site-packages',
                                 '--setuptools',
                                 'debian/test/usr/share/python/test'])
    eq_([PY_CMD,
         PIP_CMD,
         'install',
         '--log=' + os.path.abspath('foo')], d.pip_prefix)


@patch('tempfile.NamedTemporaryFile', FakeTemporaryFile)
@patch('subprocess.check_call')
def test_venv_with_custom_python(callmock):
    d = Deployment('test', python='/tmp/python')
    d.create_virtualenv()
    eq_('debian/test/usr/share/python/test', d.package_dir)
    callmock.assert_called_with(['virtualenv', '--no-site-packages',
                                 '--python', '/tmp/python',
                                 'debian/test/usr/share/python/test'])
    eq_([PY_CMD,
         PIP_CMD,
         'install',
         '--log=' + os.path.abspath('foo')], d.pip_prefix)


@patch('tempfile.NamedTemporaryFile', FakeTemporaryFile)
@patch('subprocess.check_call')
def test_install_package(callmock):
    d = Deployment('test')
    d.bin_dir = 'derp'
    d.pip_prefix = ['derp/python', 'derp/pip']
    d.install_package()
    callmock.assert_called_with([
        'derp/python', 'derp/pip', '.',
    ], cwd=os.getcwd())


def test_fix_activate_path():
    deployment = Deployment('test')
    temp = tempfile.NamedTemporaryFile()

    with open(temp.name, 'w') as fh:
        fh.write(textwrap.dedent("""
            other things

            VIRTUAL_ENV="/this/path/is/wrong/and/longer/than/new/path"

            more other things
        """))

    expected = textwrap.dedent("""
        other things

        VIRTUAL_ENV="/usr/share/python/test"

        more other things
    """)

    with patch('dh_virtualenv.deployment.os.path.join',
               return_value=temp.name):
        deployment.fix_activate_path()

    with open(temp.name) as fh:
        eq_(expected, temp.read())


@patch('os.path.exists', lambda x: True)
@patch('tempfile.NamedTemporaryFile', FakeTemporaryFile)
@patch('subprocess.check_call')
def test_custom_src_dir(callmock):
    d = Deployment('test')
    d.pip_prefix = ['pip', 'install']
    d.sourcedirectory = 'root/srv/application'
    d.create_virtualenv()
    d.install_dependencies()
    callmock.assert_called_with([
        PY_CMD,
        PIP_CMD,
        'install',
        '--log=' + os.path.abspath('foo'),
        '-r',
        'root/srv/application/requirements.txt'],
    )
    d.install_package()
    callmock.assert_called_with([
        PY_CMD,
        PIP_CMD,
        'install',
        '--log=' + os.path.abspath('foo'),
        '.',
    ], cwd=os.path.abspath('root/srv/application'))


@patch('os.path.exists', lambda *a: True)
@patch('subprocess.check_call')
def test_testrunner(callmock):
    d = Deployment('test')
    d.run_tests()
    callmock.assert_called_once_with([
        PY_CMD,
        'setup.py',
        'test',
    ], cwd='.')


@patch('os.path.exists', lambda *a: False)
@patch('subprocess.check_call')
def test_testrunner_setuppy_not_found(callmock):
    d = Deployment('test')
    d.run_tests()
    eq_(callmock.call_count, 0)


def test_deployment_from_options():
        options, _ = get_default_parser().parse_args([
            '--extra-index-url', 'http://example.com',
            '-O--pypi-url', 'http://example.org'
        ])
        d = Deployment.from_options('foo', options)
        eq_(d.package, 'foo')
        eq_(d.pypi_url, 'http://example.org')
        eq_(d.extra_urls, ['http://example.com'])


def test_deployment_from_options_with_verbose():
        options, _ = get_default_parser().parse_args([
            '--verbose'
        ])
        d = Deployment.from_options('foo', options)
        eq_(d.package, 'foo')
        eq_(d.verbose, True)


@patch('os.environ.get')
def test_deployment_from_options_with_verbose_from_env(env_mock):
        env_mock.return_value = '1'
        options, _ = get_default_parser().parse_args([])
        d = Deployment.from_options('foo', options)
        eq_(d.package, 'foo')
        eq_(d.verbose, True)


@temporary_dir
def test_fix_local_symlinks(deployment_dir):
        d = Deployment('testing')
        d.package_dir = deployment_dir

        local = os.path.join(deployment_dir, 'local')
        os.makedirs(local)
        target = os.path.join(deployment_dir, 'sometarget')
        symlink = os.path.join(local, 'symlink')
        os.symlink(target, symlink)

        d.fix_local_symlinks()
        eq_(os.readlink(symlink), '../sometarget')


@temporary_dir
def test_fix_local_symlinks_with_relative_links(deployment_dir):
        # Runs shouldn't ruin the already relative symlinks.
        d = Deployment('testing')
        d.package_dir = deployment_dir

        local = os.path.join(deployment_dir, 'local')
        os.makedirs(local)
        symlink = os.path.join(local, 'symlink')
        os.symlink('../target', symlink)

        d.fix_local_symlinks()
        eq_(os.readlink(symlink), '../target')


@temporary_dir
def test_fix_local_symlinks_does_not_blow_up_on_missing_local(deployment_dir):
        d = Deployment('testing')
        d.package_dir = deployment_dir
        d.fix_local_symlinks()
