# Build dh-virtualenv's Debian package within a container for any platform
#
#   docker build --tag dh-venv-builder --build-arg distro=debian:10 .
#   docker build --tag dh-venv-builder --build-arg distro=ubuntu:bionic .
#
#   mkdir -p dist && command docker run --rm dh-venv-builder tar -C ../dpkg -c . | tar -C dist -xv
#
# Add '--build-arg opts=nodoc' to remove dependencies on Sphinx packages not available in older releases.

ARG distro="debian:stable"
ARG opts=""

FROM ${distro} AS dpkg-build
ENV DEB_BUILD_OPTIONS=${opts}
RUN apt-get update -qq -o Acquire::Languages=none \
    && env DEBIAN_FRONTEND=noninteractive apt-get install \
        -yqq --no-install-recommends -o Dpkg::Options::=--force-unsafe-io \
        build-essential debhelper devscripts equivs lsb-release libparse-debianchangelog-perl \
        python3 python3-setuptools python3-pip python3-dev \
        python3-sphinx python3-mock dh-exec dh-python python3-sphinx-rtd-theme \
    && if test "$(lsb_release -cs)" = 'bionic' ; then \
        apt-get install -yqq --no-install-recommends -o Dpkg::Options::=--force-unsafe-io \
                        -t bionic-backports debhelper; fi \
    && apt-get clean && rm -rf "/var/lib/apt/lists"/*
WORKDIR /dpkg-build
COPY ./ ./
# The "chmod" call fixes '-rwxr-xr-x' permission problems you get when running this builder from Windows.
RUN sed -i -re "1s/..unstable/~$(lsb_release -cs)) $(lsb_release -cs)/" debian/changelog \
    && chmod a-x debian/dh-virtualenv.* \
    && dpkg-buildpackage -us -uc -b && mkdir -p /dpkg && cp -pl /dh-virtualenv[-_]* /dpkg \
    && dpkg-deb -I /dpkg/dh-virtualenv_*.deb
