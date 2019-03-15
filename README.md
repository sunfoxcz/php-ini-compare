# Compare INI files from different versions os PHP

Set of script and Docker containers to save and compare difference between
PHP default values and `php.ini` values across different versions of PHP
and distributions.

## For now
* Ubuntu 16.04
  * Native PHP 7.0 from Ubuntu APT sources
  * PHP 5.6 from dev.sury.org
  * PHP 7.0 from dev.sury.org
  * PHP 7.1 from dev.sury.org
  * PHP 7.2 from dev.sury.org
  * PHP 7.3 from dev.sury.org

## How to
```bash
make
php src/compare-values.php
```

## TODO
* add more extensions
* add more distribution (Ubuntu 18.04 for start)
* add script that will generate HTML table with differencies accross versions
