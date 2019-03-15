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
    php7.2-bcmath \
    php7.2-bz2 \
    php7.2-cli \
    php7.2-curl \
    php7.2-gd \
    php7.2-gmp \
    php7.2-imap \
    php7.2-intl \
    php7.2-json \
    php7.2-mbstring \
    php7.2-mysql \
    php7.2-opcache \
    php7.2-pgsql \
    php7.2-readline \
    php7.2-soap \
    php7.2-sqlite3 \
    php7.2-xml \
    php7.2-zip

RUN groupadd -g 1000 app && useradd -r -u 1000 -g app app
USER app
