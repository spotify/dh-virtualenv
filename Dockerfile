# Build dh-virtualenv's Debian package within a container for any platform
#
#   docker build --tag dh-venv-builder --build-arg distro=debian:9 .
#   docker build --tag dh-venv-builder --build-arg distro=ubuntu:bionic .
#
#   mkdir -p dist && docker run --rm dh-venv-builder tar -C /dpkg -c . | tar -C dist -xv

ARG distro="debian:stable"
FROM ${distro} AS dpkg-build
RUN apt-get update -qq -o Acquire::Languages=none \
    && env DEBIAN_FRONTEND=noninteractive apt-get install \
        -yqq --no-install-recommends -o Dpkg::Options::=--force-unsafe-io \
        build-essential debhelper devscripts equivs lsb-release libparse-debianchangelog-perl \
        python python-setuptools python-pip python-dev \
        python-sphinx python-mock dh-exec dh-python python-sphinx-rtd-theme \
    && apt-get clean && rm -rf "/var/lib/apt/lists"/*
WORKDIR /dpkg-build
COPY ./ ./
RUN sed -i -re "1s/..unstable/~$(lsb_release -cs)) $(lsb_release -cs)/" debian/changelog \
    && dpkg-buildpackage -us -uc -b && mkdir -p /dpkg && cp -pl /dh-virtualenv[-_]* /dpkg \
    && dpkg-deb -I /dpkg/dh-virtualenv_*.deb
