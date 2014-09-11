# dh-virtualenv

[![Build Status](https://travis-ci.org/spotify/dh-virtualenv.png)](https://travis-ci.org/spotify/dh-virtualenv)

dh-virtualenv is a tool that aims to combine Debian packaging with
self-contained virtualenv based Python deployments.

The idea behind the dh-virtualenv is to be able to combine power of
Debian packaging with the sandboxed nature of virtualenvs. In addition
to this, using virtualenv enables installing requirements via
[Python Package Index](http://pypi.python.org) instead of relying on
the operating system provided Python packages. The only limiting
factor is that you have to run the same Python interpreter as the
operating system.

## Using dh-virtualenv

Using dh-virtualenv is fairly straightforward. First, you need to
define the requirements of your package in `requirements.txt` file, in
[the format defined by pip](http://www.pip-installer.org/en/latest/cookbook.html#requirements-files).

To build a package using dh-virtualenv, you need to add dh-virtualenv
in to your build dependencies and write following `debian/rules` file:

```Makefile
%:
	dh $@ --with python-virtualenv
```

Note that you might need to provide
additional build dependencies too, if your requirements require them.

Also, you are able to define the root path for your source directory using
`--sourcedirectory` or `-D` argument:

```Makefile
%:
	dh $@ --with python-virtualenv --sourcedirectory=root/srv/application
```

NOTE: Be aware that the configuration in debian/rules expects tabs instead of spaces!

Once the package is built, you have a virtualenv contained in a Debian
package and upon installation it gets placed, by default, under
`/usr/share/python/<packagename>`.

For more information and usage documentation, check the accompanying
documentation in the `doc` folder.

## How does it work?

To do the packaging, the package extends debhelper's sequence by
providing a new commands in sequence:
* `dh_virtualenv_build`: Create virtualenv and install software in it.  
* `dh_virtualenv_install`: Copy virtualenv in the good place
* `dh_virtualenv_clean`: Suppress temporary files

Have a look to [this file](debhelper/python_virtualenv.pm) for more details about order.

## Example

`debian/rules`:

```Makefile
#!/usr/bin/make -f
# -*- makefile -*-

# Uncomment this to turn on verbose mode.
#export DH_VERBOSE=1

export DH_ALWAYS_EXCLUDE := .pyc

%:
	dh $@ --with python-virtualenv

override_dh_virtualenv_build:
	dh_virtualenv_build --no-test --extra-index-url https://pypi.fury.io/myrepo/

override_dh_virtualenv_install:
	myCommandToUse.py
	dh_virtualenv_install --package=myPackage
```

## Running tests

    $ nosetests ./test/test_deployment.py

## License

Copyright (c) 2013 Spotify AB

dh-virtualenv is licensed under GPL v2 or later. Full license is
available in the [`LICENSE`](LICENSE) file.
