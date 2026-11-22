# PHP INI differences on Ubuntu LTS

Compare the effective PHP settings installed by Ubuntu and by
[Ondřej Surý](https://packages.sury.org/php/) on the same Ubuntu LTS release
and PHP major.minor version.

| Ubuntu LTS | Native PHP | Compared with |
| --- | --- | --- |
| 22.04 Jammy | 8.1 | Surý PHP 8.1 on Jammy |
| 24.04 Noble | 8.3 | Surý PHP 8.3 on Noble |
| 26.04 Resolute | 8.5 | Surý PHP 8.5 on Resolute |

The containers install the same versioned CLI, FPM and extension package
list on amd64. The Surý build uses the signed APT repository directly and
checks the source of each requested package. Each container runs the
same probe in CLI and through FastCGI against the default FPM pool.
The report records exact PHP and package versions, active INI files,
loaded extensions and effective global and local values. Native and Surý
patch versions can differ. PHP-FPM pool directives themselves are outside
the report's INI scope.

The **PHP versions (Surý)** view compares any two from PHP 8.1–8.5.
Each pair uses the same Ubuntu release and runs separately for CLI and PHP-FPM.
The report highlights directives and extensions that were added or removed,
as well as changes to effective values or access. Search also looks up
unchanged directives. Select **Show unchanged** to list them all.

## Build the report

Run `make` with Docker and Python 3.10 or newer. Open `site/index.html`.
To rerender existing measurements, run `make report`. To collect just
one package source, run `python3 src/report.py collect --suite noble --source sury --php 8.4`.

## GitHub Pages

Set **Settings → Pages → Build and deployment → Source** to **GitHub Actions**.
The **PHP INI report** workflow builds a downloadable HTML preview for
pull requests and publishes from `master` after a push, on Mondays, or
when run manually on `master`. Publication requires all 18 package builds
and measurements to pass. The site's project URL is
https://sunfoxcz.github.io/php-ini-compare/.
