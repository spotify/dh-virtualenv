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
    def __init__(self, *args, **kwargs):
        kwargs['conflict_handler'] = 'resolve'
        OptionParser.__init__(self, *args, **kwargs)
        self.add_default_options()

    def parse_args(self, args=None, values=None):
        args = [o[2:] if o.startswith('-O-') else o
                for o in self._get_args(args)]
        args.extend(os.environ.get('DH_OPTIONS', '').split())
        # Unfortunately OptionParser is an old style class :(
        return OptionParser.parse_args(self, args, values)

    def add_default_options(self):
        self.add_option('-v', '--verbose', help=SUPPRESS_HELP)
        self.add_option('--no-act', help=SUPPRESS_HELP)
        self.add_option('-a', '--arch', help=SUPPRESS_HELP)
        self.add_option('-i', '--indep', help=SUPPRESS_HELP)
        self.add_option('-p', '--package', help=SUPPRESS_HELP)
        self.add_option('-s', '--same-arch', help=SUPPRESS_HELP)
        self.add_option('-N', '--no-package', help=SUPPRESS_HELP)
        self.add_option('--remaining-packages', help=SUPPRESS_HELP)
        self.add_option('--ignore', help=SUPPRESS_HELP)
        self.add_option('-P', '--tmpdir', help=SUPPRESS_HELP)
        self.add_option('--mainpackage', help=SUPPRESS_HELP)
        self.add_option('-O', help=SUPPRESS_HELP)
