import json
import re
import tempfile
import unittest
from pathlib import Path

from src import report


def entry(value):
    return {"global": value, "local": value, "access": 7}


def snapshot(release, source):
    run = {
        "php": release["php"] + ".1",
        "architecture": "x86_64",
        "config": "/etc/php.ini",
        "fragments": ["/etc/conf.d/test.ini"],
        "extensions": ["test"],
        "directives": {
            "test.directive": entry("<value>" if source == "ubuntu" else ""),
            "memory_limit": entry("128M"),
            "test.escaped": entry("</script>%%CARDS%%"),
        },
    }
    if source == "sury":
        run["directives"][f"test.php{release['php']}"] = entry("1")
    return {
        **release,
        "source": source,
        "apt_policy": "APT policy",
        "packages": "php-cli\t1",
        "cli": {**run, "sapi": "cli"},
        "fpm": {**run, "sapi": "fpm-fcgi"},
    }


class ReportTest(unittest.TestCase):
    def test_directive_union_preserves_missing_null_and_empty(self):
        ubuntu = {"changed": entry(None), "left": entry(""), "same": entry("0")}
        sury = {"changed": entry(""), "right": entry(""), "same": entry("0")}
        self.assertEqual(
            [(name, status) for name, status, _, _ in report.differences(ubuntu, sury)],
            [("changed", "Changed"), ("left", "Ubuntu only"), ("right", "deb.sury.org only")],
        )

    def test_renderer_validates_all_snapshots_and_escapes_values(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            samples = root / "samples"
            samples.mkdir()
            for sample in report.sample_specs(report.matrix()):
                filename = f"{sample['filename']}.json"
                (samples / filename).write_text(json.dumps(snapshot(sample, sample["source"])))
            site = root / "site"
            report.render(samples, site)
            markup = (site / "index.html").read_text()
            self.assertEqual(markup.count('data-mode="packages"'), 6)
            self.assertEqual(markup.count('data-mode="versions"'), 1)
            self.assertIn('<option value="versions">PHP versions</option>'
                          '<option value="packages">Ubuntu vs deb.sury.org</option>', markup)
            self.assertIn('<option value="resolute-sury-8.4" selected>'
                          'Ubuntu 26.04 · deb.sury.org · PHP 8.4</option>', markup)
            self.assertIn('<option value="resolute-sury" selected>'
                          'Ubuntu 26.04 · deb.sury.org · PHP 8.5</option>', markup)
            native_options = re.search(r'<optgroup label="Native Ubuntu">(.*?)</optgroup>', markup).group(1)
            self.assertEqual(re.findall(r'<option value="([^"]+)"', native_options),
                             ["bionic-ubuntu", "focal-ubuntu", "jammy-ubuntu", "noble-ubuntu", "resolute-ubuntu"])
            metadata = json.loads(re.search(r'id="sample-metadata">(.*?)</script>', markup).group(1))
            self.assertEqual(metadata["bionic-ubuntu"]["runs"]["fpm"]["php"], "7.2.1")
            self.assertEqual(len(list((site / "data").glob("*.json"))), 24)
            data_text = re.search(r'id="directive-data">(.*?)</script>', markup).group(1)
            data = json.loads(data_text)
            for name in ("noble-sury-8.1", "noble-sury-8.5"):
                self.assertEqual(data[name]["fpm"]["memory_limit"], entry("128M"))
                self.assertEqual(data[name]["fpm"]["test.escaped"], entry("</script>%%CARDS%%"))
            self.assertIn('href="data/noble-sury.json"', markup)
            self.assertTrue((site / "data" / "noble-sury.json").is_file())
            self.assertIn("&lt;value&gt;", markup)
            self.assertNotIn("<value>", markup)
            (samples / "noble-sury-8.1.json").unlink()
            with self.assertRaises(FileNotFoundError):
                report.render(samples, site)
            self.assertEqual((site / "index.html").read_text(), markup)


if __name__ == "__main__":
    unittest.main()
