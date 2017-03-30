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

For complete online documentation, see
[the documentation online](https://dh-virtualenv.readthedocs.io/en/latest/).

## Using dh-virtualenv

Using dh-virtualenv is fairly straightforward. First, you need to
define the requirements of your package in `requirements.txt` file, in
[the format defined by pip](https://pip.pypa.io/en/latest/user_guide.html#requirements-files).

To build a package using dh-virtualenv, you need to add dh-virtualenv
in to your build dependencies and write following `debian/rules` file:

      %:
              dh $@ --with python-virtualenv

Note that you might need to provide
additional build dependencies too, if your requirements require them.

Also, you are able to define the root path for your source directory using
`--sourcedirectory` or `-D` argument:

      %:
              dh $@ --with python-virtualenv --sourcedirectory=root/srv/application

NOTE: Be aware that the configuration in debian/rules expects tabs instead of spaces!

Once the package is built, you have a virtualenv contained in a Debian
package and upon installation it gets placed, by default, under
`/opt/venvs/<packagename>`.

For more information and usage documentation, check the accompanying
documentation in the `doc` folder.

## How does it work?

To do the packaging, the package extends debhelper's sequence by
providing a new command in sequence, `dh_virtualenv`, which
effectively replaces following commands from the sequence:

* `dh_auto_clean`
* `dh_auto_install`
* `dh_python2`
* `dh_pycentral`
* `dh_pysupport`

In the sequence the `dh_virtualenv` is inserted right after 
`dh_installinit`.

## Running tests

    $ nosetests ./test/test_deployment.py

## Code of conduct
This project adheres to the [Open Code of Conduct][code-of-conduct].
By participating, you are expected to honor this code.

## License

Copyright (c) 2013 Spotify AB

dh-virtualenv is licensed under GPL v2 or later. Full license is
available in the `LICENSE` file.

[code-of-conduct]: https://github.com/spotify/code-of-conduct/blob/master/code-of-conduct.md
