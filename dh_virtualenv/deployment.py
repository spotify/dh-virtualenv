# -*- coding: utf-8 -*-
# Copyright (c) 2013 - 2014 Spotify AB

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
import re
import shutil
import subprocess
import tempfile

ROOT_ENV_KEY = 'DH_VIRTUALENV_INSTALL_ROOT'
DEFAULT_INSTALL_DIR = '/usr/share/python/'


class Deployment(object):
    def __init__(self, package, extra_urls=None, preinstall=None, pypi_url=None,
                 setuptools=False, python=None, builtin_venv=False, sourcedirectory=None, verbose=False):
        self.package = package
        install_root = os.environ.get(ROOT_ENV_KEY, DEFAULT_INSTALL_DIR)
        self.virtualenv_install_dir = os.path.join(install_root, self.package)
        self.debian_root = os.path.join(
            'debian', package, install_root.lstrip('/'))
        self.package_dir = os.path.join(self.debian_root, package)
        self.bin_dir = os.path.join(self.package_dir, 'bin')
        self.local_bin_dir = os.path.join(self.package_dir, 'local', 'bin')

        self.extra_urls = extra_urls if extra_urls is not None else []
        self.preinstall = preinstall if preinstall is not None else []
        self.pypi_url = pypi_url
        self.log_file = tempfile.NamedTemporaryFile()
        self.verbose = verbose
        self.setuptools = setuptools
        self.python = python
        self.builtin_venv = builtin_venv
        self.sourcedirectory = '.' if sourcedirectory is None else sourcedirectory

    @classmethod
    def from_options(cls, package, options):
        verbose = options.verbose or os.environ.get('DH_VERBOSE') == '1'
        return cls(package,
                   extra_urls=options.extra_index_url,
                   preinstall=options.preinstall,
                   pypi_url=options.pypi_url,
                   setuptools=options.setuptools,
                   python=options.python,
                   builtin_venv=options.builtin_venv,
                   sourcedirectory=options.sourcedirectory,
                   verbose=verbose)

    def clean(self):
        shutil.rmtree(self.debian_root)

    def create_virtualenv(self):
        if self.builtin_venv:
            virtualenv = [self.python, '-m', 'venv']
        else:
            virtualenv = ['virtualenv', '--no-site-packages']

            if self.setuptools:
                virtualenv.append('--setuptools')

            if self.verbose:
                virtualenv.append('--verbose')

            if self.python:
                virtualenv.extend(('--python', self.python))

        virtualenv.append(self.package_dir)
        subprocess.check_call(virtualenv)

        if self.builtin_venv:
            # When using the venv module, pip is in local/bin
            self.pip_prefix = [os.path.join(self.local_bin_dir, 'pip')]
        else:
            # We need to prefix the pip run with the location of python
            # executable. Otherwise it would just blow up due to too long
            # shebang-line.
            self.pip_prefix = [
                os.path.join(self.bin_dir, 'python'),
                os.path.join(self.bin_dir, 'pip'),
            ]

        if self.verbose:
            self.pip_prefix.append('-v')

        self.pip_prefix.append('install')

        if self.pypi_url:
            self.pip_prefix.append('--pypi-url={0}'.format(self.pypi_url))
        self.pip_prefix.extend([
            '--extra-index-url={0}'.format(url) for url in self.extra_urls
        ])
        self.pip_prefix.append('--log={0}'.format(self.log_file.name))

    def pip(self, *args):
        return self.pip_prefix + list(args)

    def install_dependencies(self):
        # Install preinstall stage packages. This is handy if you need
        # a custom package to install dependencies (think something
        # along lines of setuptools), but that does not get installed
        # by default virtualenv.
        if self.preinstall:
            subprocess.check_call(self.pip(*self.preinstall))

        requirements_path = os.path.join(self.sourcedirectory, 'requirements.txt')
        if os.path.exists(requirements_path):
            subprocess.check_call(self.pip('-r', requirements_path))

    def run_tests(self):
        python = os.path.join(self.bin_dir, 'python')
        setup_py = os.path.join(self.sourcedirectory, 'setup.py')
        if os.path.exists(setup_py):
            subprocess.check_call([python, 'setup.py', 'test'])

    def fix_shebangs(self):
        """Translate /usr/bin/python and /usr/bin/env python sheband
        lines to point to our virtualenv python.
        """
        grep_proc = subprocess.Popen(
            ['grep', '-l', '-r', '-e', r'^#!.*bin/\(env \)\?python',
             self.bin_dir],
            stdout=subprocess.PIPE
        )
        files, stderr = grep_proc.communicate()
        files = files.strip()
        if not files:
            return

        pythonpath = os.path.join(self.virtualenv_install_dir, 'bin/python')
        for f in files.split('\n'):
            subprocess.check_call(
                ['sed', '-i', r's|^#!.*bin/\(env \)\?python|#!{0}|'.format(
                    pythonpath),
                 f])

    def fix_activate_path(self):
        """Replace the `VIRTUAL_ENV` path in bin/activate to reflect the
        post-install path of the virtualenv.
        """
        virtualenv_path = 'VIRTUAL_ENV="{0}"'.format(
            self.virtualenv_install_dir)
        pattern = re.compile(r'^VIRTUAL_ENV=.*$', flags=re.M)

        with open(os.path.join(self.bin_dir, 'activate'), 'r+') as fh:
            content = pattern.sub(virtualenv_path, fh.read())
            fh.seek(0)
            fh.truncate()
            fh.write(content)

    def install_package(self):
        setup_path = os.path.join(self.sourcedirectory)
        subprocess.check_call(self.pip(setup_path))

    def fix_local_symlinks(self):
        # The virtualenv might end up with a local folder that points outside the package
        # Specifically it might point at the build environment that created it!
        # Make those links relative
        # See https://github.com/pypa/virtualenv/commit/5cb7cd652953441a6696c15bdac3c4f9746dfaa1
        local_dir = os.path.join(self.package_dir, "local")
        if not os.path.isdir(local_dir):
            return
        elif os.path.samefile(self.package_dir, local_dir):
            # "local" points directly to its containing directory
            os.unlink(local_dir)
            os.symlink(".", local_dir)
            return

        for d in os.listdir(local_dir):
            path = os.path.join(local_dir, d)
            if not os.path.islink(path):
                continue

            existing_target = os.readlink(path)
            if not os.path.isabs(existing_target):
                # If the symlink is already relative, we don't
                # want to touch it.
                continue

            new_target = os.path.relpath(existing_target, local_dir)
            os.unlink(path)
            os.symlink(new_target, path)
