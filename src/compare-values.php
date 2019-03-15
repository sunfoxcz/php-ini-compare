<?php

$translateValues = [
    'On' => '1',
    'Off' => '0',
];

foreach (scandir(__DIR__ . '/../data') as $file) {
    if (substr($file, -strlen('.php')) !== '.php') {
        continue;
    }

    $data = require __DIR__ . '/../data/' . $file;
    $directives = $data['directives'];

    echo "\e[32m--------------------------------------------------------------------------------\e[0m\n";
    echo "\e[32m{$data['name']}\e[0m\n";
    echo "\e[32m--------------------------------------------------------------------------------\e[0m\n";

    $ini = parse_ini_file(__DIR__ . '/../ini/' . str_replace('.php', '.ini', $file), false, INI_SCANNER_RAW);
    foreach ($ini as $directive => $iniValue) {
        if (!array_key_exists($directive, $directives)) {
            //echo "Missing directive '\e[31m$directive\e[0m'.\n";
            continue;
        }

        if (array_key_exists($iniValue, $translateValues)) {
            $iniValue = $translateValues[$iniValue];
        }

        $phpValue = $directives[$directive];
        if ($phpValue != $iniValue) {
            echo "Difference in directive '\e[33m$directive\e[0m', '\e[33m{$phpValue}\e[0m' => '\e[33m{$iniValue}\e[0m'.\n";
            continue;
        }
    }
}
