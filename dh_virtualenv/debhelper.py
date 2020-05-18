# -*- coding: UTF-8 -*-
# Copyright © 2010-2012 Piotr Ożarowski <piotr@debian.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import logging
from os import makedirs, chmod
from os.path import exists, join, dirname

log = logging.getLogger(__name__)


class DebHelper(object):
    """Reinvents the wheel / some dh functionality (Perl is ugly ;-P)"""

    def __init__(self, options):
        self.options = options
        self.packages = {}
        self.python_version = None
        source_section = True
        binary_package = None

        pkgs = options.package
        skip_pkgs = options.no_package

        try:
            fp = open('debian/control', 'r')
        except IOError:
            raise Exception('cannot find debian/control file')

        xspv = xpv = False
        for line in fp:
            if not line.strip():
                source_section = False
                binary_package = None
                continue
            if binary_package:
                if binary_package.startswith('python3'):
                    continue
                if pkgs and binary_package not in pkgs:
                    continue
                if skip_pkgs and binary_package in skip_pkgs:
                    continue
                if line.startswith('Architecture:'):
                    arch = line[13:].strip()
                    # TODO: if arch doesn't match current architecture:
                    #del self.packages[binary_package]
                    self.packages[binary_package]['arch'] = arch
                    continue
            elif line.startswith('Package:'):
                binary_package = line[8:].strip()
                if binary_package.startswith('python3'):
                    log.debug('skipping Python 3.X package: %s', binary_package)
                    continue
                if pkgs and binary_package not in pkgs:
                    continue
                if skip_pkgs and binary_package in skip_pkgs:
                    continue
                self.packages[binary_package] = {'substvars': {},
                                                 'autoscripts': {},
                                                 'rtupdates': [],
                                                 'arch': 'any'}
            elif line.startswith('Source:'):
                self.source_name = line[7:].strip()
            elif source_section:
                if line.lower().startswith('xs-python-version:'):
                    xspv = True
                    if not self.python_version:
                        self.python_version = line[18:].strip()
                if line.lower().startswith('x-python-version:'):
                    xpv = True
                    self.python_version = line[17:].strip()

        if xspv and xpv:
            log.error('Please remove XS-Python-Version from debian/control')

        log.debug('source=%s, binary packages=%s', self.source_name, \
                                                   self.packages.keys())

    def addsubstvar(self, package, name, value):
        """debhelper's addsubstvar"""
        self.packages[package]['substvars'].setdefault(name, []).append(value)

    def autoscript(self, package, when, template, args):
        """debhelper's autoscript"""
        self.packages[package]['autoscripts'].setdefault(when, {})\
                            .setdefault(template, []).append(args)

    def add_rtupdate(self, package, value):
        self.packages[package]['rtupdates'].append(value)

    def save_autoscripts(self):
        for package, settings in self.packages.iteritems():
            autoscripts = settings.get('autoscripts')
            if not autoscripts:
                continue

            for when, templates in autoscripts.iteritems():
                fn = "debian/%s.%s.debhelper" % (package, when)
                if exists(fn):
                    data = open(fn, 'r').read()
                else:
                    data = ''

                new_data = ''
                for tpl_name, args in templates.iteritems():
                    for i in args:
                        # try local one first (useful while testing dh_python2)
                        fpath = join(dirname(__file__), '..',
                                     "autoscripts/%s" % tpl_name)
                        if not exists(fpath):
                            fpath = "/usr/share/debhelper/autoscripts/%s" % tpl_name
                        tpl = open(fpath, 'r').read()
                        if self.options.compile_all and args:
                            # TODO: should args be checked to contain dir name?
                            tpl = tpl.replace('#PACKAGE#', '')
                        else:
                            tpl = tpl.replace('#PACKAGE#', package)
                        tpl = tpl.replace('#ARGS#', i)
                        if tpl not in data and tpl not in new_data:
                            new_data += "\n%s" % tpl
                if new_data:
                    data += "\n# Automatically added by dh_python2:" +\
                            "%s\n# End automatically added section\n" % new_data
                    fp = open(fn, 'w')
                    fp.write(data)
                    fp.close()

    def save_substvars(self):
        for package, settings in self.packages.iteritems():
            substvars = settings.get('substvars')
            if not substvars:
                continue
            fn = "debian/%s.substvars" % package
            if exists(fn):
                data = open(fn, 'r').read()
            else:
                data = ''
            for name, values in substvars.iteritems():
                p = data.find("%s=" % name)
                if p > -1:  # parse the line and remove it from data
                    e = data[p:].find('\n')
                    line = data[p + len("%s=" % name):\
                                p + e if e > -1 else None]
                    items = [i.strip() for i in line.split(',') if i]
                    if e > -1 and data[p + e:].strip():
                        data = "%s\n%s" % (data[:p], data[p + e:])
                    else:
                        data = data[:p]
                else:
                    items = []
                for j in values:
                    if j not in items:
                        items.append(j)
                if items:
                    if data:
                        data += '\n'
                    data += "%s=%s\n" % (name, ', '.join(items))
            data = data.replace('\n\n', '\n')
            if data:
                fp = open(fn, 'w')
                fp.write(data)
                fp.close()

    def save_rtupdate(self):
        for package, settings in self.packages.iteritems():
            pkg_arg = '' if self.options.compile_all else "-p %s" % package
            values = settings.get('rtupdates')
            if not values:
                continue
            d = "debian/%s/usr/share/python/runtime.d" % package
            if not exists(d):
                makedirs(d)
            fn = "%s/%s.rtupdate" % (d, package)
            if exists(fn):
                data = open(fn, 'r').read()
            else:
                data = "#! /bin/sh\nset -e"
            for dname, args in values:
                cmd = 'if [ "$1" = rtupdate ]; then' +\
                      "\n\tpyclean %s %s" % (pkg_arg, dname) +\
                      "\n\tpycompile %s %s %s\nfi" % (pkg_arg, args, dname)
                if cmd not in data:
                    data += "\n%s" % cmd
            if data:
                fp = open(fn, 'w')
                fp.write(data)
                fp.close()
                chmod(fn, 0755)

    def save(self):
        self.save_substvars()
        self.save_autoscripts()
        self.save_rtupdate()
