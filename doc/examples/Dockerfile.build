# Build Debian package using dh-virtualenv

FROM #DIST_ID#:#CODENAME# AS dpkg-build
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -qq && apt-get install -yqq \
        build-essential debhelper devscripts equivs dh-virtualenv \
        curl tar gzip lsb-release apt-utils apt-transport-https libparse-debianchangelog-perl \
        python3 python3-setuptools python3-pip python3-dev libffi-dev \
        libxml2-dev libxslt1-dev libyaml-dev libjpeg-dev \
        libssl-dev libncurses5-dev libncursesw5-dev libzmq3-dev \
    && ( curl -s https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add - ) \
    && echo 'deb https://deb.nodesource.com/#NODEREPO# #CODENAME# main' \
            >/etc/apt/sources.list.d/nodesource.list \
    && apt-get update -qq && apt-get install -y nodejs \
    && rm -rf "/var/lib/apt/lists"/*
WORKDIR /dpkg-build
COPY ./ ./
RUN dpkg-buildpackage -us -uc -b && mkdir -p /dpkg && cp -pl /#PKGNAME#[-_]* /dpkg
# RUN pwd && dh_virtualenv --version && ls -la && du -sch . ##UUID#
