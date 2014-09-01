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
import shutil

DEFAULT_BUILD_DIR = 'debian/dh_virtualenv'


class Build(object):
    def __init__(self, extra_urls=None, preinstall=None,
                 pypi_url=None, setuptools=False, python=None,
                 builtin_venv=False, sourcedirectory=None,
                 build_dir=None, verbose=False, extra_pip_arg=[]):
        self.build_dir = build_dir if build_dir is not None else DEFAULT_BUILD_DIR
        self.bin_dir = os.path.join(self.build_dir, 'bin')
        self.local_bin_dir = os.path.join(self.build_dir, 'local', 'bin')

        self.extra_urls = extra_urls
        self.preinstall = preinstall
        self.extra_pip_arg = extra_pip_arg
        self.pypi_url = pypi_url
        self.log_file = tempfile.NamedTemporaryFile()
        self.verbose = verbose
        self.setuptools = setuptools
        self.python = python
        self.builtin_venv = builtin_venv
        self.sourcedirectory = sourcedirectory if sourcedirectory is not None else "."

    @classmethod
    def from_options(cls, options):
        verbose = options.verbose or os.environ.get('DH_VERBOSE') == '1'
        return cls(extra_urls=options.extra_index_url,
                   preinstall=options.preinstall,
                   pypi_url=options.pypi_url,
                   setuptools=options.setuptools,
                   python=options.python,
                   builtin_venv=options.builtin_venv,
                   sourcedirectory=options.sourcedirectory,
                   build_dir=options.build_dir,
                   verbose=verbose,
                   extra_pip_arg=options.extra_pip_arg)

    def clean(self):
        shutil.rmtree(self.build_dir)

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

        virtualenv.append(self.build_dir)
        subprocess.check_call(virtualenv)

        if self.builtin_venv:
            # When using the venv module, pip is in local/bin
            self.pip_prefix = [os.path.abspath(os.path.join(self.local_bin_dir,
                                                            'pip'))]
        else:
            # We need to prefix the pip run with the location of python
            # executable. Otherwise it would just blow up due to too long
            # shebang-line.
            self.pip_prefix = [
                os.path.abspath(os.path.join(self.bin_dir, 'python')),
                os.path.abspath(os.path.join(self.bin_dir, 'pip')),
            ]

        if self.verbose:
            self.pip_prefix.append('-v')

        self.pip_prefix.append('install')

        if self.pypi_url:
            self.pip_prefix.append('--pypi-url={0}'.format(self.pypi_url))
        self.pip_prefix.extend([
            '--extra-index-url={0}'.format(url) for url in self.extra_urls
        ])
        self.pip_prefix.append('--log={0}'.format(os.path.abspath(self.log_file.name)))
        # Add in any user supplied pip args
        if self.extra_pip_arg:
            self.pip_prefix.extend(self.extra_pip_arg)

    def pip(self, *args):
        return self.pip_prefix + list(args)

    def install_dependencies(self):
        # Install preinstall stage packages. This is handy if you need
        # a custom package to install dependencies (think something
        # along lines of setuptools), but that does not get installed
        # by default virtualenv.
        if self.preinstall:
            subprocess.check_call(self.pip(*self.preinstall))

        requirements_path = os.path.join(self.sourcedirectory,
                                         'requirements.txt')
        if os.path.exists(requirements_path):
            subprocess.check_call(self.pip('-r', requirements_path))

    def run_tests(self):
        python = os.path.abspath(os.path.join(self.bin_dir, 'python'))
        setup_py = os.path.join(self.sourcedirectory, 'setup.py')
        if os.path.exists(setup_py):
            subprocess.check_call([python, 'setup.py', 'test'],
                                  cwd=self.sourcedirectory)

    def install_package(self):
        subprocess.check_call(self.pip('.'),
                              cwd=os.path.abspath(self.sourcedirectory))
