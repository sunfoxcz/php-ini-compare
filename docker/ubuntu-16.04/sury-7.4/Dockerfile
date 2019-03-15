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
    php7.4-bcmath \
    php7.4-bz2 \
    php7.4-cli \
    php7.4-curl \
    php7.4-gd \
    php7.4-gmp \
    php7.4-imap \
    php7.4-intl \
    php7.4-json \
    php7.4-mbstring \
    php7.4-mysql \
    php7.4-opcache \
    php7.4-pgsql \
    php7.4-readline \
    php7.4-soap \
    php7.4-sqlite3 \
    php7.4-xml \
    php7.4-zip

RUN groupadd -g 1000 app && useradd -r -u 1000 -g app app
USER app
