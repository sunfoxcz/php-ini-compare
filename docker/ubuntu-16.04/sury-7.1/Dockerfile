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
    php7.1-bcmath \
    php7.1-bz2 \
    php7.1-cli \
    php7.1-curl \
    php7.1-gd \
    php7.1-gmp \
    php7.1-imap \
    php7.1-intl \
    php7.1-json \
    php7.1-mbstring \
    php7.1-mcrypt \
    php7.1-mysql \
    php7.1-opcache \
    php7.1-pgsql \
    php7.1-readline \
    php7.1-soap \
    php7.1-sqlite3 \
    php7.1-xml \
    php7.1-zip

RUN groupadd -g 1000 app && useradd -r -u 1000 -g app app
USER app
