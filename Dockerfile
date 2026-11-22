ARG UBUNTU=24.04
FROM ubuntu:${UBUNTU}

ARG SUITE=noble
ARG PHP_VERSION=8.3
ARG SOURCE=ubuntu
ENV PHP_VERSION=${PHP_VERSION} PHP_PACKAGE_SOURCE=${SOURCE} LC_ALL=C.UTF-8
COPY src/install.sh /usr/local/bin/install-php
RUN /bin/sh /usr/local/bin/install-php
COPY src/collect.sh src/snapshot.php /probe/
ENTRYPOINT ["/bin/sh", "/probe/collect.sh"]
