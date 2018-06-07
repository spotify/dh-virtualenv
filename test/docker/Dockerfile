FROM debian:sid

ENV DEBIAN_FRONTEND noninteractive

RUN echo 'deb-src http://deb.debian.org/debian sid main' >> /etc/apt/sources.list

RUN apt-get update && apt-get install -y --no-install-recommends \
    devscripts \
    equivs

# RUN cd /src && \
#     cat debian/control && \
#     mk-build-deps -r -i \
#     -t 'apt-get -o Debug::pkgProblemResolver=yes --no-install-recommends -y' \
#     debian/control
