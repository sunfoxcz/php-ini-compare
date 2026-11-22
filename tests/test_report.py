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
            [("changed", "Changed"), ("left", "Ubuntu only"), ("right", "Surý only")],
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
            self.assertEqual(markup.count('data-mode="versions"'), 60)
            self.assertIn('<option value="bionic-ubuntu" selected>Ubuntu 18.04 · Native · PHP 7.2</option>', markup)
            self.assertIn('<option value="jammy-sury-7.4" selected>Ubuntu 22.04 · Surý · PHP 7.4</option>', markup)
            native_options = re.search(r'<optgroup label="Native Ubuntu">(.*?)</optgroup>', markup).group(1)
            self.assertEqual(re.findall(r'<option value="([^"]+)"', native_options),
                             ["bionic-ubuntu", "focal-ubuntu", "jammy-ubuntu", "noble-ubuntu", "resolute-ubuntu"])
            metadata = json.loads(re.search(r'id="sample-metadata">(.*?)</script>', markup).group(1))
            self.assertEqual(metadata["bionic-ubuntu"]["runs"]["fpm"]["php"], "7.2.1")
            self.assertEqual(len(list((site / "data").glob("*.json"))), 24)
            version_card = markup.split('id="noble-fpm-8.1-8.5"', 1)[1].split("</section>", 1)[0]
            self.assertIn("<code>test.php8.1</code><small>Removed</small>", version_card)
            self.assertIn("<code>test.php8.5</code><small>Added</small>", version_card)
            self.assertNotIn("memory_limit", version_card)
            self.assertIn('data-left="noble-sury-8.1"', version_card)
            self.assertIn('data-right="noble-sury-8.5"', version_card)
            data_text = re.search(r'id="directive-data">(.*?)</script>', markup).group(1)
            data = json.loads(data_text)
            for name in ("noble-sury-8.1", "noble-sury-8.5"):
                self.assertEqual(data[name]["fpm"]["memory_limit"], entry("128M"))
                self.assertEqual(data[name]["fpm"]["test.escaped"], entry("</script>%%CARDS%%"))
            self.assertIn('href="data/noble-sury-8.1.json"', markup)
            self.assertTrue((site / "data" / "noble-sury.json").is_file())
            self.assertIn("&lt;value&gt;", markup)
            self.assertNotIn("<value>", markup)
            (samples / "noble-sury-8.1.json").unlink()
            with self.assertRaises(FileNotFoundError):
                report.render(samples, site)
            self.assertEqual((site / "index.html").read_text(), markup)


if __name__ == "__main__":
    unittest.main()
