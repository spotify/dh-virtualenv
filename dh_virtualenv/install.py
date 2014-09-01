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

from dh_virtualenv.build import DEFAULT_BUILD_DIR

ROOT_ENV_KEY = 'DH_VIRTUALENV_INSTALL_ROOT'
DEFAULT_INSTALL_DIR = '/usr/share/python/'


class Install(object):
    def __init__(self, package, destination=None, package_dir=None, build_dir=None):
        self.package = package
        self.build_dir = build_dir if build_dir is not None else DEFAULT_BUILD_DIR
        install_root = os.environ.get(ROOT_ENV_KEY, DEFAULT_INSTALL_DIR)
        if destination is not None:
            self.virtualenv_install_dir = destination
        else:
            self.virtualenv_install_dir = os.path.join(install_root, self.package)

        self.debian_root = os.path.join('debian',
                                        package,
                                        install_root.lstrip('/'))
        if package_dir is not None:
            self.package_dir = package_dir
        else:
            self.package_dir = os.path.join(self.debian_root, package)
        self.bin_dir = os.path.join(self.package_dir, 'bin')
        self.local_bin_dir = os.path.join(self.package_dir, 'local', 'bin')

    def relocate(self):
        if not os.path.exists(self.build_dir):
            return
        shutil.copytree(self.build_dir, self.package_dir)
        self.fix_activate_path()
        self.fix_shebangs()

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
