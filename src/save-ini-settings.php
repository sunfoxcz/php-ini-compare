<?php

$directives = [];
foreach (ini_get_all() as $directive => $values) {
    $directives[$directive] = $values['global_value'];
}

$fileName = __DIR__ . '/../data/' . (!empty($argv[1]) ? $argv[1] : phpversion()) . '.php';
file_put_contents($fileName, '<?php return ' . var_export([
    'name' => phpversion(),
    'directives' => $directives,
], true) . ';');

$output = [];
exec('php --ini', $output);
foreach ($output as $line) {
    if (preg_match('~^Loaded Configuration File:\s+(.+)$~', $line, $matches)) {
        $iniFile = $matches[1];
    }
}
if (isset($iniFile)) {
    $targetFile = __DIR__ . '/../ini/' . (!empty($argv[1]) ? $argv[1] : phpversion()) . '.ini';
    copy($iniFile, $targetFile);
}
