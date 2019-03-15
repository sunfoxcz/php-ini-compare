FROM ubuntu:16.04
MAINTAINER Tomas Jacik <tomas@jacik.cz>

ENV LC_ALL C
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update
RUN apt-get dist-upgrade -y --no-install-recommends -o Dpkg::Options::="--force-confdef"
RUN apt-get install -y --no-install-recommends \
    php7.0-bcmath \
    php7.0-bz2 \
    php7.0-cli \
    php7.0-curl \
    php7.0-gd \
    php7.0-gmp \
    php7.0-imap \
    php7.0-intl \
    php7.0-json \
    php7.0-mbstring \
    php7.0-mcrypt \
    php7.0-mysql \
    php7.0-opcache \
    php7.0-pgsql \
    php7.0-readline \
    php7.0-soap \
    php7.0-sqlite3 \
    php7.0-xml \
    php7.0-zip

RUN groupadd -g 1000 app && useradd -r -u 1000 -g app app
USER app
