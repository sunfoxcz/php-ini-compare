#!/bin/sh
set -eu
. /etc/os-release
work=$(mktemp -d)
pid=
cleanup() {
    if [ -n "$pid" ]; then
        kill "$pid" 2>/dev/null || :
        wait "$pid" 2>/dev/null || :
    fi
    rm -rf "$work"
}
trap cleanup EXIT
trap 'exit 1' HUP INT TERM
mkdir -p /run/php
php="/usr/bin/php$PHP_VERSION"
"$php" /probe/snapshot.php > "$work/cli.json"

socket="/run/php/php$PHP_VERSION-fpm.sock"
"/usr/sbin/php-fpm$PHP_VERSION" -F > "$work/fpm.log" 2>&1 &
pid=$!
for attempt in $(seq 1 100); do
    [ ! -S "$socket" ] || break
    if ! kill -0 "$pid" 2>/dev/null; then break; fi
    sleep 0.1
done
if [ ! -S "$socket" ]; then
    cat "$work/fpm.log" >&2
    exit 1
fi
SCRIPT_FILENAME=/probe/snapshot.php SCRIPT_NAME=/snapshot.php REQUEST_METHOD=GET \
    cgi-fcgi -bind -connect "$socket" > "$work/response"
# Strip FastCGI headers, then validate the JSON and real FPM SAPI.
awk 'body {print; next} /^\r?$/ {body=1}' "$work/response" > "$work/fpm.json"
"$php" -n -r '
    $cli = json_decode(file_get_contents($argv[1]), true, 512, JSON_THROW_ON_ERROR);
    $fpm = json_decode(file_get_contents($argv[2]), true, 512, JSON_THROW_ON_ERROR);
    if ($cli["sapi"] !== "cli" || $fpm["sapi"] !== "fpm-fcgi" ||
        $cli["php"] !== $fpm["php"] || !$cli["config"] || !$fpm["config"] ||
        !$cli["directives"] || !$fpm["directives"]) {
        throw new RuntimeException("Incomplete CLI or FPM measurement");
    }
    echo json_encode([
        "ubuntu" => $argv[3],
        "suite" => $argv[4],
        "source" => $argv[5],
        "apt_policy" => file_get_contents("/probe/apt-policy.txt"),
        "packages" => file_get_contents("/probe/packages.tsv"),
        "cli" => $cli,
        "fpm" => $fpm,
    ], JSON_THROW_ON_ERROR | JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES), PHP_EOL;
' "$work/cli.json" "$work/fpm.json" "$VERSION_ID" "$VERSION_CODENAME" "$PHP_PACKAGE_SOURCE"
