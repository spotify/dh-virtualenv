#! /usr/bin/perl
# debhelper sequence for wrapping packages inside virtualenvs

# Copyright (c) Spotify AB 2013

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

use warnings;
use strict;
use Debian::Debhelper::Dh_Lib;

insert_after("dh_perl", "dh_virtualenv");

# dh_auto_test can cause system python to run 'python setup.py test',
# which will break due missing dependencies.
remove_command("dh_auto_test");

# dh_auto_build causes system python to run 'python setup.py build'
# which is unnecessary as we will run that inside the virtualenv
# anyway
remove_command("dh_auto_build");

# Same for dh_auto_install and dh_auto_clean
remove_command("dh_auto_install");
remove_command("dh_auto_clean");
remove_command("dh_python2");
remove_command("dh_pycentral");
remove_command("dh_pysupport");

1
