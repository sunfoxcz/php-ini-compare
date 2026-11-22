import json
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
        "directives": {"test.directive": entry("<value>" if source == "ubuntu" else "")},
    }
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

    def test_renderer_validates_all_six_snapshots_and_escapes_values(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            samples = root / "samples"
            samples.mkdir()
            for release in report.matrix():
                for source in report.SOURCES:
                    filename = f"{release['suite']}-{source}.json"
                    (samples / filename).write_text(json.dumps(snapshot(release, source)))
            site = root / "site"
            report.render(samples, site)
            markup = (site / "index.html").read_text()
            self.assertEqual(markup.count('class="comparison"'), 6)
            self.assertEqual(len(list((site / "data").glob("*.json"))), 6)
            self.assertIn("&lt;value&gt;", markup)
            self.assertNotIn("<value>", markup)
            (samples / "noble-sury.json").unlink()
            with self.assertRaises(FileNotFoundError):
                report.render(samples, site)
            self.assertEqual((site / "index.html").read_text(), markup)


if __name__ == "__main__":
    unittest.main()
