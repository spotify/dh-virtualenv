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
import contextlib

from mock import patch, call, ANY

from nose.tools import eq_
from dh_virtualenv import Deployment
from dh_virtualenv.cmdline import get_default_parser


PY_CMD = os.path.abspath('debian/test/opt/venvs/test/bin/python')
PIP_CMD = os.path.abspath('debian/test/opt/venvs/test/bin/pip')


class FakeTemporaryFile(object):
    name = 'foo'


def _test_bin(name):
    return os.path.abspath(os.path.join(
        'debian/test/opt/venvs/test/bin', name,
    ))


PY_CMD = _test_bin('python')
PIP_CMD = _test_bin('pip')
CUSTOM_PIP_CMD = _test_bin('pip-custom-platform')
LOG_ARG = '--log=' + os.path.abspath(FakeTemporaryFile.name)


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


def create_new_style_shebang(executable):
    shebang = '#!/bin/sh\n'
    shebang += "'''exec' " + executable + ' "$0" "$@"' + '\n'
    shebang += "' '''\n"
    return shebang


def test_shebangs_fix():
    """Generate a test for each possible interpreter"""
    for interpreter in ('python', 'pypy', 'ipy', 'jython'):
        yield check_shebangs_fix, interpreter, '/opt/venvs/test'


def test_shebangs_fix_overridden_root():
    """Generate a test for each possible interpreter while overriding root"""
    with patch.dict(os.environ, {'DH_VIRTUALENV_INSTALL_ROOT': 'foo'}):
        for interpreter in ('python', 'pypy', 'ipy', 'jython'):
            yield check_shebangs_fix, interpreter, 'foo/test'


def test_shebangs_fix_special_chars_in_path():
    """Shebang fix: Don't trip on special characters in path"""
    with patch.dict(
        os.environ,
        {'DH_VIRTUALENV_INSTALL_ROOT': 'some-directory:with/special_chars'}):
        for interpreter in ('python', 'pypy', 'ipy', 'jython'):
            yield (check_shebangs_fix, interpreter,
                   'some-directory:with/special_chars/test')


def test_shebangs_fix_new_pip_with_over_127_chars():
    """Shebang fix: Handle new pip with long shebangs"""
    with patch.dict(
        os.environ,
        {'DH_VIRTUALENV_INSTALL_ROOT': 127 * 'p'}):
        check_shebangs_fix_on_new_pip(127 * 'p' + '/test')


def check_shebangs_fix(interpreter, path):
    """Checks shebang substitution for the given interpreter"""
    deployment = Deployment('test')
    temp = tempfile.NamedTemporaryFile()
    # We cheat here a little. The fix_shebangs walks through the
    # project directory, however we can just point to a single
    # file, as the underlying mechanism is just grep -r.
    deployment.bin_dir = temp.name
    expected_shebang = '#!' + os.path.join(path, 'bin/python') + '\n'

    with open(temp.name, 'w') as f:
        f.write('#!/usr/bin/{0}\n'.format(interpreter))

    deployment.fix_shebangs()

    with open(temp.name) as f:
        eq_(f.read(), expected_shebang)

    with open(temp.name, 'w') as f:
        f.write('#!/usr/bin/env {0}\n'.format(interpreter))

    deployment.fix_shebangs()

    with open(temp.name) as f:
        eq_(f.readline(), expected_shebang)

    # Additional test to check for paths wrapped in quotes because they contained space
    # Example:
    #           #!"/some/local/path/dest/path/bin/python"
    # was changed to:
    #           #!/dest/path/bin/python"
    # which caused interpreter not found error

    with open(temp.name, 'w') as f:
        f.write('#!"/usr/bin/{0}"\n'.format(interpreter))

    deployment.fix_shebangs()

    with open(temp.name) as f:
        eq_(f.readline(), expected_shebang)


def check_shebangs_fix_on_new_pip(path):
    """Test new pip style shebangs get replaced properly"""
    deployment = Deployment('test')
    temp = tempfile.NamedTemporaryFile()

    # We cheat here a little. The fix_shebangs walks through the
    # project directory, however we can just point to a single
    # file, as the underlying mechanism is just grep -r.
    deployment.bin_dir = temp.name
    build_time_shebang = create_new_style_shebang(os.path.join(
        deployment.virtualenv_install_dir, 'bin', 'python'))
    expected_shebang = create_new_style_shebang(os.path.join(
        path, 'bin/python'))

    with open(temp.name, 'w') as f:
        f.write(build_time_shebang)

    deployment.fix_shebangs()

    with open(temp.name) as f:
        eq_(f.read(), expected_shebang)


@patch('os.path.exists', lambda x: False)
@patch('subprocess.check_call')
def test_install_dependencies_with_no_requirements(callmock):
    d = Deployment('test')
    d.pip_prefix = ['pip']
    d.install_dependencies()
    callmock.assert_has_calls([])


@patch('os.path.exists', lambda x: True)
@patch('subprocess.check_call')
def test_install_dependencies_with_requirements(callmock):
    d = Deployment('test')
    d.pip_prefix = ['pip']
    d.pip_args = ['install']
    d.install_dependencies()
    callmock.assert_called_with(
        ['pip', 'install', '-r', './requirements.txt'])


@patch('subprocess.check_call')
def test_install_dependencies_with_preinstall(callmock):
    d = Deployment('test', preinstall=['foobar'])
    d.pip_prefix = d.pip_preinstall_prefix = ['pip']
    d.pip_args = ['install']
    d.install_dependencies()
    callmock.assert_called_with(
        ['pip', 'install', 'foobar'])


@patch('subprocess.check_call')
def test_upgrade_pip(callmock):
    d = Deployment('test', upgrade_pip=True)
    d.pip_prefix = d.pip_preinstall_prefix = ['pip']
    d.pip_args = ['install']
    d.install_dependencies()
    callmock.assert_called_with(
        ['pip', 'install', ANY, '-U', 'pip'])


@patch('subprocess.check_call')
def test_upgrade_pip_with_preinstall(callmock):
    d = Deployment('test', upgrade_pip=True, preinstall=['foobar'])
    d.pip_prefix = d.pip_preinstall_prefix = ['pip']
    d.pip_args = ['install']
    d.install_dependencies()
    callmock.assert_has_calls([
        call(['pip', 'install', ANY, '-U', 'pip']),
        call(['pip', 'install', 'foobar'])])


@patch('os.path.exists', lambda x: True)
@patch('subprocess.check_call')
def test_install_dependencies_with_preinstall_with_requirements(callmock):
    d = Deployment('test', preinstall=['foobar'])
    d.pip_prefix = d.pip_preinstall_prefix = ['pip']
    d.pip_args = ['install']
    d.install_dependencies()
    callmock.assert_has_calls([
        call(['pip', 'install', 'foobar']),
        call(['pip', 'install', '-r', './requirements.txt'])
    ])


@patch('os.path.exists', lambda x: True)
@patch('subprocess.check_call')
def test_install_dependencies_with_requirements_with_postinstall(callmock):
    d = Deployment('test', postinstall=['foobar==1.0 --install-option=--compile'])
    d.pip_prefix = ['pip']
    d.pip_args = ['install']
    d.install_dependencies()
    callmock.assert_has_calls([
        call(['pip', 'install', '-r', './requirements.txt']),
        call(['pip', 'install', 'foobar==1.0 --install-option=--compile'])
    ])


@patch('os.path.exists', return_value=True)
@patch('tempfile.NamedTemporaryFile', FakeTemporaryFile)
@patch('subprocess.check_call')
def test_custom_pip_tool_used_for_installation(callmock, _):
    d = Deployment(
        'test', preinstall=['pip-custom-platform'],
        pip_tool='pip-custom-platform',
    )
    d.install_dependencies()
    d.install_package()
    callmock.assert_has_calls([
        call([PY_CMD, PIP_CMD, 'install', LOG_ARG, 'pip-custom-platform']),
        call([PY_CMD, CUSTOM_PIP_CMD, 'install', LOG_ARG, '-r', './requirements.txt']),
        call([PY_CMD, CUSTOM_PIP_CMD, 'install', LOG_ARG, '.'], cwd=os.path.abspath('.')),
    ])


@patch('tempfile.NamedTemporaryFile', FakeTemporaryFile)
@patch('subprocess.check_call')
def test_create_venv(callmock):
    d = Deployment('test')
    d.create_virtualenv()
    eq_('debian/test/opt/venvs/test', d.package_dir)
    callmock.assert_called_with(['virtualenv', '--no-site-packages',
                                 'debian/test/opt/venvs/test'])


@patch('tempfile.NamedTemporaryFile', FakeTemporaryFile)
@patch('subprocess.check_call')
def test_create_venv_with_verbose(callmock):
    d = Deployment('test', verbose=True)
    d.create_virtualenv()
    eq_('debian/test/opt/venvs/test', d.package_dir)
    callmock.assert_called_with(['virtualenv', '--no-site-packages',
                                 '--verbose',
                                 'debian/test/opt/venvs/test'])


@patch('tempfile.NamedTemporaryFile', FakeTemporaryFile)
@patch('subprocess.check_call')
def test_create_venv_with_extra_urls(callmock):
    d = Deployment('test', extra_urls=['foo', 'bar'])
    d.create_virtualenv()
    eq_('debian/test/opt/venvs/test', d.package_dir)
    callmock.assert_called_with(['virtualenv', '--no-site-packages',
                                 'debian/test/opt/venvs/test'])
    eq_([PY_CMD, PIP_CMD], d.pip_prefix)
    eq_(['install', '--extra-index-url=foo',
         '--extra-index-url=bar',
         LOG_ARG], d.pip_args)


@patch('tempfile.NamedTemporaryFile', FakeTemporaryFile)
@patch('subprocess.check_call')
def test_create_venv_with_extra_virtualenv(callmock):
    d = Deployment('test', extra_virtualenv_arg=["--never-download"])
    d.create_virtualenv()
    eq_('debian/test/opt/venvs/test', d.package_dir)
    callmock.assert_called_with(['virtualenv', '--no-site-packages',
                                 '--never-download',
                                 'debian/test/opt/venvs/test'])


@patch('tempfile.NamedTemporaryFile', FakeTemporaryFile)
@patch('subprocess.check_call')
def test_create_venv_with_custom_index_url(callmock):
    d = Deployment('test', extra_urls=['foo', 'bar'],
                   index_url='http://example.com/simple')
    d.create_virtualenv()
    eq_('debian/test/opt/venvs/test', d.package_dir)
    callmock.assert_called_with(['virtualenv', '--no-site-packages',
                                 'debian/test/opt/venvs/test'])
    eq_([PY_CMD, PIP_CMD], d.pip_prefix)
    eq_(['install',
         '--index-url=http://example.com/simple',
         '--extra-index-url=foo',
         '--extra-index-url=bar',
         LOG_ARG], d.pip_args)


@patch('tempfile.NamedTemporaryFile', FakeTemporaryFile)
@patch('subprocess.check_call')
def test_create_venv_with_extra_pip_arg(callmock):
    d = Deployment('test', extra_pip_arg=['--no-compile'])
    d.create_virtualenv()
    d.install_dependencies()
    eq_('debian/test/opt/venvs/test', d.package_dir)
    callmock.assert_called_with(['virtualenv', '--no-site-packages',
                                 'debian/test/opt/venvs/test'])
    eq_([PY_CMD, PIP_CMD], d.pip_prefix)
    eq_(['install', LOG_ARG, '--no-compile'], d.pip_args)


@patch('tempfile.NamedTemporaryFile', FakeTemporaryFile)
@patch('subprocess.check_call')
def test_create_venv_with_setuptools(callmock):
    d = Deployment('test', setuptools=True)
    d.create_virtualenv()
    eq_('debian/test/opt/venvs/test', d.package_dir)
    callmock.assert_called_with(['virtualenv', '--no-site-packages',
                                 '--setuptools',
                                 'debian/test/opt/venvs/test'])
    eq_([PY_CMD, PIP_CMD], d.pip_prefix)
    eq_(['install', LOG_ARG], d.pip_args)


@patch('tempfile.NamedTemporaryFile', FakeTemporaryFile)
@patch('subprocess.check_call')
def test_create_venv_with_system_packages(callmock):
    d = Deployment('test', use_system_packages=True)
    d.create_virtualenv()
    eq_('debian/test/opt/venvs/test', d.package_dir)
    callmock.assert_called_with(['virtualenv', '--system-site-packages',
                                 'debian/test/opt/venvs/test'])
    eq_([PY_CMD, PIP_CMD], d.pip_prefix)
    eq_(['install', LOG_ARG], d.pip_args)


@patch('tempfile.NamedTemporaryFile', FakeTemporaryFile)
@patch('subprocess.check_call')
def test_venv_with_custom_python(callmock):
    d = Deployment('test', python='/tmp/python')
    d.create_virtualenv()
    eq_('debian/test/opt/venvs/test', d.package_dir)
    callmock.assert_called_with(['virtualenv', '--no-site-packages',
                                 '--python', '/tmp/python',
                                 'debian/test/opt/venvs/test'])
    eq_([PY_CMD, PIP_CMD], d.pip_prefix)
    eq_(['install', LOG_ARG], d.pip_args)


@patch('tempfile.NamedTemporaryFile', FakeTemporaryFile)
@patch('subprocess.check_call')
def test_install_package(callmock):
    d = Deployment('test')
    d.bin_dir = 'derp'
    d.pip_prefix = ['derp/python', 'derp/pip']
    d.pip_args = ['install']
    d.install_package()
    callmock.assert_called_with([
        'derp/python', 'derp/pip', 'install', '.',
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

        VIRTUAL_ENV="/opt/venvs/test"

        more other things
    """)

    with patch('dh_virtualenv.deployment.os.path.join',
               return_value=temp.name):
        deployment.fix_activate_path()

    with open(temp.name) as fh:
        eq_(expected, fh.read())


@patch('os.path.exists', lambda x: True)
@patch('tempfile.NamedTemporaryFile', FakeTemporaryFile)
@patch('subprocess.check_call')
def test_custom_src_dir(callmock):
    d = Deployment('test')
    d.sourcedirectory = 'root/srv/application'
    d.create_virtualenv()
    d.install_dependencies()
    callmock.assert_called_with([
        PY_CMD,
        PIP_CMD,
        'install',
        LOG_ARG,
        '-r',
        'root/srv/application/requirements.txt'],
    )
    d.install_package()
    callmock.assert_called_with([
        PY_CMD,
        PIP_CMD,
        'install',
        LOG_ARG,
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


@patch('tempfile.NamedTemporaryFile', FakeTemporaryFile)
def test_deployment_from_options():
        options, _ = get_default_parser().parse_args([
            '--extra-index-url', 'http://example.com',
            '-O--pypi-url', 'http://example.org'
        ])
        d = Deployment.from_options('foo', options)
        eq_(d.package, 'foo')
        eq_(d.pip_args,
            ['install', '--index-url=http://example.org',
             '--extra-index-url=http://example.com', LOG_ARG])


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


@temporary_dir
def test_find_script_files_normal_shebang(bin_dir):
    d = Deployment('testing')
    d.bin_dir = bin_dir

    script_files = [os.path.join(bin_dir, s) for s in
                    ('s1', 's2', 's3')]
    for script in script_files:
        with open(os.path.join(bin_dir, script), 'w') as f:
            f.write('#!/usr/bin/python\n')

    with open(os.path.join(bin_dir, 'n1'), 'w') as f:
        f.write('#!/bin/bash')

    found_files = sorted(d.find_script_files())
    eq_(found_files, script_files)


@temporary_dir
def test_find_script_files_long_shebang(bin_dir):
    d = Deployment('testing')
    d.bin_dir = bin_dir

    script_files = [os.path.join(bin_dir, s) for s in
                    ('s1', 's2', 's3')]
    for script in script_files:
        with open(os.path.join(bin_dir, script), 'w') as f:
            # It does not really matter what we write into the
            # exec statement as executable here
            f.write(
                create_new_style_shebang('/usr/bin/python'))

    with open(os.path.join(bin_dir, 'n1'), 'w') as f:
        f.write('#!/bin/bash')

    found_files = sorted(d.find_script_files())
    eq_(found_files, script_files)
