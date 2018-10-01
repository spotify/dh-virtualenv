#! /usr/bin/env bash
#
# Build Debian package in a Docker container
#

set -e

# Get build platform as 1st argument, and collect project metadata
image="${1:?You MUST provide a docker image name}"; shift
dist_id=${image%%:*}
codename=${image#*:}
pypi_name="$(./setup.py --name)"
pypi_version="$(./setup.py --version)"
pkgname="$(dh_listpackages)"
tag=$pypi_name-$dist_id-$codename

# Build in Docker container, save results, and show package info
rm -f dist/${pkgname}?*${pypi_version//./?}*${codename}*.*
docker build --tag $tag \
    --build-arg "DIST_ID=$dist_id" \
    --build-arg "CODENAME=$codename" \
    --build-arg "PKGNAME=$pkgname" \
    -f Dockerfile.build \
    "$@" .
mkdir -p dist
docker run --rm $tag tar -C /dpkg -c . | tar -C dist -x
ls -lh dist/${pkgname}?*${pypi_version//./?}*${codename}*.*
