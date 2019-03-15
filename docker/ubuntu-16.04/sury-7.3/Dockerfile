FROM ubuntu:16.04
MAINTAINER Tomas Jacik <tomas@jacik.cz>

ENV LC_ALL C.UTF-8
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update
RUN apt-get dist-upgrade -y --no-install-recommends -o Dpkg::Options::="--force-confdef"
RUN apt-get install -y --no-install-recommends apt-transport-https ca-certificates software-properties-common

RUN add-apt-repository ppa:ondrej/php
RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    php7.3-bcmath \
    php7.3-bz2 \
    php7.3-cli \
    php7.3-curl \
    php7.3-gd \
    php7.3-gmp \
    php7.3-imap \
    php7.3-intl \
    php7.3-json \
    php7.3-mbstring \
    php7.3-mysql \
    php7.3-opcache \
    php7.3-pgsql \
    php7.3-readline \
    php7.3-soap \
    php7.3-sqlite3 \
    php7.3-xml \
    php7.3-zip

RUN groupadd -g 1000 app && useradd -r -u 1000 -g app app
USER app
