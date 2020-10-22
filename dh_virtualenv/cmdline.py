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
from __future__ import absolute_import

import os
import warnings

from optparse import OptionParser, SUPPRESS_HELP, OptionValueError

from ._version import version


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


def _check_for_deprecated_options(
        option, opt_str, value, parser, *args, **kwargs):
    # TODO: If more deprectaed options pop up, refactor this method to
    # handle them in more generic way (or actually remove the
    # deprecated options)
    if opt_str in ('--pypi-url', '--index-url'):
        if opt_str == '--pypi-url':
            # Work around 2.7 hiding the DeprecationWarning
            with warnings.catch_warnings():
                warnings.simplefilter('default')
                warnings.warn('Use of --pypi-url is deprecated. Use '
                              '--index-url instead',
                              DeprecationWarning)
        if parser.values.index_url:
            # We've already set the index_url, which means that we have both
            # --index-url and --pypi-url passed in.
            raise OptionValueError('Deprecated --pypi-url and the new '
                                   '--index-url are mutually exclusive')
        parser.values.index_url = value
    elif opt_str in ('--no-test', '--setuptools-test'):
        if opt_str == '--no-test':
            with warnings.catch_warnings():
                warnings.simplefilter('default')
                warnings.warn('Use of --no-test is deprecated and has no '
                              'effect. Use --setuptools-test if you want to '
                              'execute `setup.py test` during package build.',
                              DeprecationWarning)
        if getattr(parser.values, '_test_flag_seen', None):
            raise OptionValueError('Deprecated --no-test and the new '
                                   '--setuptools-test are mutually exclusive')
        parser.values.setuptools_test = opt_str != '--no-test'
        setattr(parser.values, '_test_flag_seen', True)


def _set_builtin_venv(
    option, opt_str, value, parser, *args, **kwargs
):
    if parser.values.setuptools:
        raise OptionValueError(
            '--setuptools flag is not supported by builtin venv module'
        )
    else:
        parser.values.builtin_venv = True


def _set_setuptools(
    option, opt_str, value, parser, *args, **kwargs
):
    if parser.values.builtin_venv:
        raise OptionValueError(
            '--setuptools flag is not supported by builtin venv module'
        )
    else:
        parser.values.setuptools = True


def get_default_parser():
    usage = '%prog [options]'
    parser = DebhelperOptionParser(usage, version='%prog ' + version)
    parser.add_option('-p', '--package', action='append', metavar='PACKAGE',
                      help='Act on the package(s) named PACKAGE')
    parser.add_option('-N', '--no-package', action='append', metavar='PACKAGE',
                      help='Do not act on the specified package(s)')
    parser.add_option('-v', '--verbose', action='store_true',
                      default=False, help='Turn on verbose mode')
    parser.add_option('-s', '--setuptools', action='callback',
                      dest='setuptools',
                      callback=_set_setuptools,
                      default=False, help='Use Setuptools instead of Distribute')
    parser.add_option('--extra-index-url', action='append', metavar='URL',
                      help='Extra index URL(s) to pass to pip.',
                      default=[])
    parser.add_option('--preinstall', action='append', metavar='PACKAGE',
                      help=('Package(s) to install before processing '
                            'requirements.txt.'),
                      default=[])
    parser.add_option('--extras', action='append', metavar='NAME',
                      help=('Activate one or more extras of the main package.'),
                      default=[])
    parser.add_option('--pip-tool', default='pip', metavar='EXECUTABLE',
                      help="Executable that will be used to install "
                      "requirements after the preinstall stage. Usually "
                      "you'll install this program by using the --preinstall "
                      "argument. The replacement is expected to be found in "
                      "the virtualenv's bin/ directory.")
    parser.add_option('--upgrade-pip', action='store_true', default=False,
                      help='Upgrade pip to the latest available version')
    parser.add_option('--upgrade-pip-to', default='', metavar='VERSION',
                      help='Upgrade pip to a specific version')
    parser.add_option('--extra-pip-arg', action='append', metavar='ARG',
                      help='One or more extra args for the pip binary.'
                      'You can use this flag multiple times to pass in'
                      ' parameters to pip.', default=[])
    parser.add_option('--extra-virtualenv-arg', action='append', metavar='ARG',
                      help='One or more extra args for the virtualenv binary.'
                      'You can use this flag multiple times to pass in'
                      ' parameters to the virtualenv binary.', default=[])
    parser.add_option('--index-url', metavar='URL',
                      help='Base URL of the PyPI server',
                      action='callback',
                      type='string',
                      dest='index_url',
                      callback=_check_for_deprecated_options)
    parser.add_option('--python', metavar='EXECUTABLE',
                      help='The Python command to use')
    parser.add_option('--builtin-venv', action='callback',
                      dest='builtin_venv',
                      callback=_set_builtin_venv,
                      help='Use the built-in venv module. Only works on '
                      'Python 3.4 and later.')
    parser.add_option('-D', '--sourcedirectory', dest='sourcedirectory',
                      help='The source directory')
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
                      help="Skip running pip install within the source directory.")
    parser.add_option('--install-suffix', metavar='DIRNAME',
                      dest='install_suffix',
                      help="Override installation path suffix")
    parser.add_option('--requirements', metavar='FILEPATH',
                      dest='requirements_filename',
                      help='Specify the filename for requirements.txt',
                      default='requirements.txt')
    parser.add_option('--setuptools-test',
                      dest='setuptools_test',
                      default=False,
                      action='callback',
                      help='Run `setup.py test` when building the package',
                      callback=_check_for_deprecated_options)

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

    # Deprecated options
    parser.add_option('--pypi-url', metavar='URL',
                      help=('!!DEPRECATED, use --index-url instead!! '
                            'Base URL of the PyPI server'),
                      action='callback',
                      dest='index_url',
                      type='string',
                      callback=_check_for_deprecated_options)
    parser.add_option('--no-test',
                      help="!!DEPRECATED, this command has no effect. "
                      "See --setuptools-test!! "
                      "Don't run tests for the package. Useful "
                      "for example when you have packaged with distutils.",
                      action='callback',
                      callback=_check_for_deprecated_options)
    return parser
