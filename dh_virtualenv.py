# -*- coding: utf-8 -*-
# Copyright (c) 2013 Spotify AB

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
import shutil
import subprocess
import tempfile

ROOT_ENV_KEY = 'DH_VIRTUALENV_INSTALL_ROOT'
DEFAULT_INSTALL_DIR = '/usr/share/python/'


class Deployment(object):
    def __init__(self, package, extra_urls=None, preinstall=None,
                 pypi_url=None, setuptools=False, verbose=False, use_buildout=False, buildout_version=None,
                 buildout_srcdir = None, buildout_dir=None):

        self.package = package
        self.install_root = os.environ.get(ROOT_ENV_KEY, DEFAULT_INSTALL_DIR)
        root = self.install_root.lstrip('/')
        self.debian_root = os.path.join('debian', package, root)
        self.package_dir = os.path.join(self.debian_root, package)
        self.bin_dir = os.path.join(self.package_dir, 'bin')

        self.extra_urls = extra_urls if extra_urls is not None else []
        self.preinstall = preinstall if preinstall is not None else []
        self.pypi_url = pypi_url
        self.log_file = tempfile.NamedTemporaryFile()
        self.verbose = verbose
        self.setuptools = setuptools

        self.use_buildout = use_buildout
        self.buildout_version = buildout_version
        self.buildout_srcdir = buildout_srcdir if buildout_srcdir is not None else os.getcwd()
        self.buildout_dir = buildout_dir if buildout_dir is not None else os.getcwd()


    def clean(self):
        shutil.rmtree(self.debian_root)

    def create_virtualenv(self):
        virtualenv = ['virtualenv', '--no-site-packages']

        if self.setuptools:
            virtualenv.append('--setuptools')

        if self.verbose:
            virtualenv.append('--verbose')

        virtualenv.append(self.package_dir)
        subprocess.check_call(virtualenv)

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

        if self.use_buildout:
            dest_dir = os.path.join(self.buildout_dir, self.package_dir)
            self.buildout_prefix = [
                './bin/buildout',
                'buildout:directory={0}'.format(self.buildout_dir),
                'buildout:source_directory={0}'.format(self.buildout_srcdir),
                'buildout:bin-directory={0}/bin'.format(dest_dir),
                'buildout:eggs-directory={0}/eggs'.format(dest_dir),
            ]

    def pip(self, *args):
        return self.pip_prefix + list(args)

    def run_buildout(self):
        return self.buildout_prefix

    def install_dependencies(self):
        # Install preinstall stage packages. This is handy if you need
        # a custom package to install dependencies (think something
        # along lines of setuptools), but that does not get installed
        # by default virtualenv.
        if self.preinstall:
            subprocess.check_call(self.pip(*self.preinstall))

        if os.path.exists('requirements.txt'):
            subprocess.check_call(self.pip('-r', 'requirements.txt'))

        # look for bootstrap.py on the given source dir
        bootstrap = os.path.join(self.buildout_srcdir,'bootstrap.py')
        if self.use_buildout and os.path.exists(bootstrap):
            if self.buildout_version:
                subprocess.check_call([
                   os.path.join(self.bin_dir, 'python'),
                   '{0}'.format(bootstrap),
                   '--version', '{0}'.format(self.buildout_version),
                   ])
            else:
                subprocess.check_call([
                   os.path.join(self.bin_dir, 'python'),
                   '{0}'.format(bootstrap),
                   ])
    def fix_twistd(self):
        '''TODO:
             Sync dir to debian/ directory
             Edit twistd syspath to be correct.
        '''
        pass

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

        pythonpath = os.path.join(self.install_root, self.package, 'bin/python')
        for f in files.split('\n'):
            subprocess.check_call(
                ['sed', '-i', r's|^#!.*bin/\(env \)\?python|#!{0}|'.format(
                    pythonpath),
                 f])

    def install_package(self):
       if self.use_buildout:
            subprocess.check_call(self.run_buildout())
       else:
            temp = tempfile.NamedTemporaryFile()
            subprocess.check_call([
                os.path.join(self.bin_dir, 'python'),
                'setup.py',
                'install',
                '--record', temp.name,
                '--install-headers',
                os.path.join(self.package_dir, 'include/site/python2.6'),
            ])
