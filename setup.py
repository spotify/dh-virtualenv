#! /usr/bin/env python
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


from setuptools import setup

setup(name='dh_virtualenv',
      version='0.8',
      author=u'Jyrki Pulliainen',
      author_email='jyrki@spotify.com',
      url='https://github.com/spotify/dh-virtualenv',
      description='Debian packaging sequence for Python virtualenvs.',
      license='GNU General Public License v2 or later',
      scripts=['bin/dh_virtualenv'],
      packages=['dh_virtualenv'],
      classifiers=[
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
          'Topic :: Software Development :: Build Tools',
          'Topic :: System :: Installation/Setup',
          'Topic :: Utilities',
      ])
