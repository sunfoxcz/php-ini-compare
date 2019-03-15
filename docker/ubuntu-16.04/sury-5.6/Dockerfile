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
    php5.6-bcmath \
    php5.6-bz2 \
    php5.6-cli \
    php5.6-curl \
    php5.6-gd \
    php5.6-gmp \
    php5.6-imap \
    php5.6-intl \
    php5.6-json \
    php5.6-mbstring \
    php5.6-mcrypt \
    php5.6-mysql \
    php5.6-opcache \
    php5.6-pgsql \
    php5.6-readline \
    php5.6-soap \
    php5.6-sqlite3 \
    php5.6-xml \
    php5.6-zip

RUN groupadd -g 1000 app && useradd -r -u 1000 -g app app
USER app
