# PHP INI differences on Ubuntu LTS

**PHP versions** is the default view. Compare any two measured profiles,
with separate CLI and PHP-FPM results. The initial pair uses the two
latest PHP series in the matrix from [deb.sury.org](https://deb.sury.org/)
on the newest Ubuntu LTS in the matrix. The report identifies when the
Ubuntu release or package source also changes.

**Ubuntu vs deb.sury.org** compares the native and deb.sury.org packages
for the same Ubuntu release and PHP major.minor series.

| Ubuntu LTS | Native PHP | Compared with |
| --- | --- | --- |
| 22.04 Jammy | 8.1 | deb.sury.org PHP 8.1 on Jammy |
| 24.04 Noble | 8.3 | deb.sury.org PHP 8.3 on Noble |
| 26.04 Resolute | 8.5 | deb.sury.org PHP 8.5 on Resolute |

The containers use the same requested extensions on amd64. Each container
runs the probe in CLI and through FastCGI against the default FPM pool.
The report records exact PHP versions, active INI files, loaded extensions
and effective global and local values. PHP patch versions can differ.
FPM pool directives themselves are outside the report's INI scope.
Search also finds unchanged directives. Select **Show unchanged** to
list them all.

Historical native profiles use the Ubuntu public archives without Ubuntu
Pro for Ubuntu 18.04 (PHP 7.2) and 20.04 (PHP 7.4). The historical
deb.sury.org profiles on Ubuntu 22.04 offer PHP 7.2, 7.3, 7.4 and 8.0.

## Build the report

Run `make` with Docker and Python 3.10 or newer. Open `site/index.html`.
To rerender existing measurements, run `make report`. To collect just
one package source, run `python3 src/report.py collect --suite noble --source sury --php 8.4`.

## GitHub Pages

Set **Settings → Pages → Build and deployment → Source** to **GitHub Actions**.
The **PHP INI report** workflow builds a downloadable HTML preview for
pull requests and publishes from `master` after a push, on Mondays, or
when run manually on `master`. Publication requires all 24 package builds
and measurements to pass. The site's project URL is
https://sunfoxcz.github.io/php-ini-compare/.
