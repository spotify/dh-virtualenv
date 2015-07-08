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

"""Helpers to handle debhelper command line options."""

import os

from optparse import OptionParser, SUPPRESS_HELP


class DebhelperOptionParser(OptionParser):
    """Special OptionParser for handling Debhelper options.

    Basically this means converting -O--option to --option before
    parsing.

    """
    def parse_args(self, args=None, values=None):
        args = [o[2:] if o.startswith('-O-') else o
                for o in self._get_args(args)]
        args.extend(os.environ.get('DH_OPTIONS', '').split())
        # Unfortunately OptionParser is an old style class :(
        return OptionParser.parse_args(self, args, values)


def get_default_parser():
    usage = '%prog [options]'
    parser = DebhelperOptionParser(usage, version='%prog 0.9')
    parser.add_option('-p', '--package', action='append',
                      help='act on the package named PACKAGE')
    parser.add_option('-N', '--no-package', action='append',
                      help='do not act on the specified package')
    parser.add_option('-v', '--verbose', action='store_true',
                      default=False, help='Turn on verbose mode')
    parser.add_option('-s', '--setuptools', action='store_true',
                      default=False, help='Use Setuptools instead of Distribute')
    parser.add_option('--extra-index-url', action='append',
                      help='extra index URL to pass to pip.',
                      default=[])
    parser.add_option('--preinstall', action='append',
                      help=('package to install before processing '
                            'requirements.txt.'),
                      default=[])
    parser.add_option('--extra-pip-arg', action='append',
                      help='Extra args for the pip binary.'
                      'You can use this flag multiple times to pass in'
                      ' parameters to pip.', default=[])
    parser.add_option('--pypi-url', help='Base URL of the PyPI server')
    parser.add_option('--python', help='The Python to use')
    parser.add_option('--builtin-venv', action='store_true',
                      help='Use the built-in venv module. Only works on '
                      'Python 3.4 and later.')
    parser.add_option('-D', '--sourcedirectory', dest='sourcedirectory',
                      help='The source directory')
    parser.add_option('--no-test', action='store_false', dest='test',
                      help="Don't run tests for the package. Useful "
                      "for example when you have packaged with distutils.",
                      default=True)
    parser.add_option('-n', '--noscripts', action='store_false', dest='autoscripts',
                      help="Do not modify postinst and similar scripts.",
                      default=True)
    parser.add_option('-S', '--use-system-packages', action='store_true',
                      dest='use_system_packages',
                      help="Set the --system-site-packages flag in virtualenv "
                           "creation, allowing you to use system packages.",
                      default=False)
    parser.add_option('--skip-install', action='store_true',
                      default=False, 
                      dest='skip_install',
                      help="Skip running pip install within the source directory.");
    
    # Ignore user-specified option bundles
    parser.add_option('-O', help=SUPPRESS_HELP)
    parser.add_option('-a', '--arch', dest="arch",
                      help=("Act on architecture dependent packages that "
                            "should be built for the build architecture. "
                            "This option is ignored"),
                      action="store", type="string")

    parser.add_option('-i', '--indep', dest="indep",
                      help=("Act on all architecture independent packages. "
                            "This option is ignored"),
                      action="store_true")
    return parser
