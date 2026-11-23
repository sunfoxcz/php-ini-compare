#!/bin/sh
set -eu
export DEBIAN_FRONTEND=noninteractive
. /etc/os-release
test "$ID" = ubuntu
test "$VERSION_CODENAME" = "$SUITE"

apt-get update
case "$SOURCE" in
    ubuntu) ;;
    sury)
        apt-get install -y --no-install-recommends ca-certificates curl
        curl -fsSL --retry 3 https://packages.sury.org/debsuryorg-archive-keyring.deb \
            -o /tmp/debsuryorg-archive-keyring.deb
        dpkg -i /tmp/debsuryorg-archive-keyring.deb
        rm /tmp/debsuryorg-archive-keyring.deb
        cat > /etc/apt/sources.list.d/sury-php.sources <<SOURCES
Types: deb
URIs: https://packages.sury.org/php/
Suites: $SUITE
Components: main
Signed-By: /usr/share/keyrings/debsuryorg-archive-keyring.gpg
SOURCES
        cat > /etc/apt/preferences.d/sury-php <<'PIN'
Package: php*
Pin: origin packages.sury.org
Pin-Priority: 990
PIN
        apt-get update
        ;;
    *) exit 1 ;;
esac

set -- cli fpm common curl mbstring mysql xml zip
# From PHP 8.5 OPcache is built into the interpreter.
case "$PHP_VERSION" in
    7.*) set -- "$@" opcache json ;;
    8.[0-4]) set -- "$@" opcache ;;
esac
packages=
for module; do
    packages="$packages php$PHP_VERSION-$module"
done
# Fail if any requested package in the Sury image would fall back to Ubuntu.
if [ "$SOURCE" = sury ]; then
    for package in $packages; do
        candidate=$(apt-cache policy "$package" | awk '/Candidate:/ {print $2}')
        if ! apt-cache madison "$package" |
            awk -F '|' -v version="$candidate" '
                { gsub(/^[[:space:]]+|[[:space:]]+$/, "", $2) }
                $2 == version && $3 ~ /https:\/\/packages\.sury\.org\/php/ { found = 1 }
                END { exit !found }'
        then
            printf 'No Surý APT candidate for %s (candidate %s)\n' "$package" "$candidate" >&2
            exit 1
        fi
    done
fi
# Ubuntu container images normally include this policy, but create it if absent.
if [ ! -e /usr/sbin/policy-rc.d ]; then
    printf '#!/bin/sh\nexit 101\n' >/usr/sbin/policy-rc.d
    chmod 755 /usr/sbin/policy-rc.d
fi
# The slim base excludes man pages; keep the targets PHP's alternatives register.
apt-get install -y --no-install-recommends \
    -o "Dpkg::Options::=--path-include=/usr/share/man/man1/php$PHP_VERSION.1.gz" \
    -o "Dpkg::Options::=--path-include=/usr/share/man/man1/phar*$PHP_VERSION.1.gz" \
    -o "Dpkg::Options::=--path-include=/usr/share/man/man1/phar$PHP_VERSION.phar.1.gz" \
    libfcgi-bin $packages
mkdir -p /probe
apt-cache policy "php$PHP_VERSION-cli" "php$PHP_VERSION-fpm" > /probe/apt-policy.txt
dpkg-query -W -f='${Package}\t${Version}\n' 'php*' | awk 'NF == 2' | sort > /probe/packages.tsv
rm -rf /var/lib/apt/lists/*
