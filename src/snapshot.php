<?php
declare(strict_types=1);

if (PHP_SAPI !== 'cli') {
    header('Content-Type: application/json');
}

$directives = ini_get_all();
ksort($directives, SORT_STRING);
foreach ($directives as $name => $entry) {
    $directives[$name] = [
        'global' => $entry['global_value'],
        'local' => $entry['local_value'],
        'access' => $entry['access'],
    ];
}

$extensions = array_unique(array_merge(get_loaded_extensions(), get_loaded_extensions(true)));
sort($extensions, SORT_STRING);
$config = php_ini_scanned_files();

$snapshot = json_encode([
    'sapi' => PHP_SAPI,
    'php' => PHP_VERSION,
    'architecture' => php_uname('m'),
    'config' => php_ini_loaded_file() ?: null,
    'fragments' => $config ? preg_split('/,\s*/', trim($config)) : [],
    'extensions' => $extensions,
    'directives' => $directives,
], JSON_INVALID_UTF8_SUBSTITUTE);
if ($snapshot === false) {
    throw new RuntimeException(json_last_error_msg());
}
echo $snapshot, "\n";
