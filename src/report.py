"""Collect and compare packaged PHP INI settings on Ubuntu LTS."""

import argparse
import html
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from shutil import copyfile


ROOT = Path(__file__).resolve().parents[1]
SOURCES = ("ubuntu", "sury")
SAPIS = {"cli": "CLI", "fpm": "PHP-FPM"}


def matrix():
    return json.loads((ROOT / "matrix.json").read_text())


def sample_specs(config):
    for release in config["releases"]:
        yield release | {"source": "ubuntu", "filename": f"{release['suite']}-ubuntu"}
        for php in config["sury_versions"]:
            # Preserve the existing download URLs for the native-versus-deb.sury.org pairs.
            filename = f"{release['suite']}-sury"
            if php != release["php"]:
                filename += f"-{php}"
            yield release | {"php": php, "source": "sury", "filename": filename}
    yield from config.get("historical_samples", [])


def load_snapshot(path, release, source):
    sample = json.loads(path.read_text())
    for key, value in {**release, "source": source}.items():
        if key not in {"php", "filename"} and sample.get(key) != value:
            raise ValueError(f"{path}: expected {key}={value}")
    for key, sapi in (("cli", "cli"), ("fpm", "fpm-fcgi")):
        run = sample[key]
        if run["sapi"] != sapi or not run["php"].startswith(release["php"] + "."):
            raise ValueError(f"{path}: unexpected SAPI or PHP version in {key}")
        if not run["directives"] or not run["config"]:
            raise ValueError(f"{path}: incomplete {key} snapshot")
    return sample


def collect(sample, output):
    source = sample["source"]
    tag = f"php-ini-compare:{sample['filename']}"
    target = output / f"{sample['filename']}.json"
    output.mkdir(parents=True, exist_ok=True)
    args = {"UBUNTU": sample["ubuntu"], "SUITE": sample["suite"],
            "PHP_VERSION": sample["php"], "SOURCE": source}
    command = ["docker", "build", "--pull", "--no-cache", "--platform", "linux/amd64", "-t", tag]
    for key, value in args.items():
        command += ["--build-arg", f"{key}={value}"]
    subprocess.run([*command, str(ROOT)], check=True)
    temporary = target.with_suffix(".json.tmp")
    try:
        with temporary.open("w") as stream:
            subprocess.run(
                ["docker", "run", "--rm", "--network", "none", "--platform", "linux/amd64", tag],
                stdout=stream, check=True,
            )
        load_snapshot(temporary, sample, source)
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)


def differences(ubuntu, sury, only=("Ubuntu only", "deb.sury.org only")):
    for name in sorted(ubuntu.keys() | sury.keys()):
        if name not in ubuntu:
            yield name, only[1], None, sury[name]
        elif name not in sury:
            yield name, only[0], ubuntu[name], None
        elif ubuntu[name] != sury[name]:
            yield name, "Changed", ubuntu[name], sury[name]


def escape(value):
    return html.escape(str(value), quote=True)


def directive_cells(entry):
    if entry is None:
        return '<td colspan="2" class="muted">Not registered</td>'

    def value_text(value):
        if value is None:
            return '<code class="muted">null</code>'
        return f"<code>{escape(json.dumps(value, ensure_ascii=False))}</code>"

    access = escape(entry["access"])
    return (
        f'<td>{value_text(entry["global"])}<small>Access {access}</small></td>'
        f'<td>{value_text(entry["local"])}</td>'
    )


def provenance(sample, sapi):
    run = sample[sapi]
    fragments = "".join(f"<li><code>{escape(path)}</code></li>" for path in run["fragments"])
    return (
        "<details><summary>Packages and configuration</summary>"
        f"<p><code>{escape(run['config'])}</code></p><ol>{fragments}</ol>"
        f"<pre>{escape(sample['packages'])}</pre><pre>{escape(sample['apt_policy'])}</pre></details>"
    )


def render_comparison(release, left_sample, right_sample, sapi):
    left, right = left_sample[sapi], right_sample[sapi]
    if left["architecture"] != right["architecture"]:
        raise ValueError("Cannot compare snapshots from different CPU architectures")

    release_id = escape(release["suite"])
    label = escape(SAPIS[sapi])
    card_id = f"{release_id}-{sapi}"
    headings = ("Ubuntu", "deb.sury.org")
    only = ("Ubuntu only", "deb.sury.org only")
    php_label = f'PHP {escape(release["php"])}'
    title = f'Ubuntu {escape(release["ubuntu"])} · {php_label} · {label}'

    rows = list(differences(left["directives"], right["directives"], only))
    table = "".join(
        f'<tr data-directive="{escape(name)}"><th scope="row"><code>{escape(name)}</code>'
        f'<small>{status}</small></th>{directive_cells(a)}{directive_cells(b)}</tr>'
        for name, status, a, b in rows
    )
    ext = []
    left_ext, right_ext = set(left["extensions"]), set(right["extensions"])
    for status, names in zip(only, (left_ext - right_ext, right_ext - left_ext)):
        if names:
            ext.append(f'{status} extensions <code>{escape(", ".join(sorted(names)))}</code>')
    extensions = " · ".join(ext) if ext else "Same loaded extensions"
    summary = (
        f'{sum(status == "Changed" for _, status, _, _ in rows)} changed · '
        f'{sum(status == only[0] for _, status, _, _ in rows)} {only[0].lower()} · '
        f'{sum(status == only[1] for _, status, _, _ in rows)} {only[1].lower()}'
    )
    table_markup = (
        '<div class="table-scroll" tabindex="0" aria-label="Directive values"'
        f'{"" if rows else " hidden"}>'
        '<table><thead><tr><th rowspan="2" scope="col">Directive</th>'
        f'<th colspan="2" scope="colgroup">{headings[0]}</th>'
        f'<th colspan="2" scope="colgroup">{headings[1]}</th></tr>'
        '<tr><th scope="col">Global</th><th scope="col">Local</th>'
        f'<th scope="col">Global</th><th scope="col">Local</th></tr></thead>'
        f'<tbody>{table}</tbody></table></div>'
        f'<p data-no-differences{" hidden" if rows else ""}>No INI directive differences.</p>'
    )
    blocks = []
    for heading, sample in zip(headings, (left_sample, right_sample)):
        version = escape(sample[sapi]["php"])
        href = f'data/{escape(sample["filename"])}.json'
        details = provenance(sample, sapi)
        blocks.append(
            f'<div><strong>{heading}</strong> <code>{version}</code>'
            f'<a href="{href}" download>JSON</a>{details}</div>'
        )
    return f"""
<section class="comparison" id="{card_id}" data-release="{release_id}" data-sapi="{sapi}"
  data-left="{escape(left_sample['filename'])}" data-right="{escape(right_sample['filename'])}" data-mode="packages">
  <h2>{title}</h2>
  <p class="summary">{summary} <span>{extensions}</span></p>
  <div class="sources">{''.join(blocks)}</div>
  {table_markup}
</section>"""


def render(input_dir, output_dir):
    config = matrix()
    # Validate the entire matrix before replacing the published report.
    samples = {}
    sample_metadata = {}
    for spec in sample_specs(config):
        path = input_dir / f'{spec["filename"]}.json'
        key = spec["suite"], spec["source"], spec["php"]
        sample = load_snapshot(path, spec, spec["source"]) | {"filename": spec["filename"]}
        samples[key] = sample
        provider = "Native" if spec["source"] == "ubuntu" else "deb.sury.org"
        label = f'Ubuntu {spec["ubuntu"]} · {provider} · PHP {spec["php"]}'
        sample_metadata[spec["filename"]] = {
            "label": label,
            "ubuntu": spec["ubuntu"],
            "source": spec["source"],
            "php": spec["php"],
            "runs": {
                sapi: {field: sample[sapi][field] for field in ("php", "extensions", "architecture")}
                for sapi in SAPIS
            },
        }

    cards = []
    releases = []
    for release in config["releases"]:
        suite, php = release["suite"], release["php"]
        ubuntu, sury = (samples[suite, source, php] for source in SOURCES)
        releases.append(f'<option value="{escape(suite)}">Ubuntu {escape(release["ubuntu"])}</option>')
        for sapi in SAPIS:
            cards.append(render_comparison(release, ubuntu, sury, sapi))

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    page = (ROOT / "src" / "report.html").read_text()
    output_dir.mkdir(parents=True, exist_ok=True)
    data_dir = output_dir / "data"
    data_dir.mkdir(exist_ok=True)
    for sample in samples.values():
        filename = f'{sample["filename"]}.json'
        copyfile(input_dir / filename, data_dir / filename)
    # Embed each directive snapshot once so a downloaded report can search offline.
    directive_index = {
        sample["filename"]: {sapi: sample[sapi]["directives"] for sapi in SAPIS}
        for sample in samples.values()
    }
    def embed_json(value):
        return json.dumps(value, separators=(",", ":"), ensure_ascii=False).replace("<", "\\u003c")

    def custom_options(selected):
        groups = []
        for source, label in (("ubuntu", "Native Ubuntu"), ("sury", "deb.sury.org")):
            options = []
            for name, meta in sorted(sample_metadata.items(), key=lambda item: item[1]["label"]):
                if meta["source"] == source:
                    options.append(
                        f'<option value="{escape(name)}"{" selected" if name == selected else ""}>'
                        f'{escape(meta["label"])}</option>'
                    )
            groups.append(f'<optgroup label="{label}">{"".join(options)}</optgroup>')
        return "".join(groups)

    latest_suite = max(config["releases"], key=lambda release: release["ubuntu"])["suite"]
    baseline_php, target_php = sorted(
        config["sury_versions"], key=lambda version: tuple(map(int, version.split("."))),
    )[-2:]
    baseline = samples[latest_suite, "sury", baseline_php]["filename"]
    target = samples[latest_suite, "sury", target_php]["filename"]

    replacements = {
        "UPDATED": now,
        "DIRECTIVES": embed_json(directive_index),
        "SAMPLE_METADATA": embed_json(sample_metadata),
        "BASELINE_OPTIONS": custom_options(baseline),
        "TARGET_OPTIONS": custom_options(target),
        "RELEASES": "".join(releases),
        "CARDS": "".join(cards),
    }
    page = re.sub(r"%%([A-Z_]+)%%", lambda match: replacements[match[1]], page)
    (output_dir / "index.html").write_text(page, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("matrix")
    collector = sub.add_parser("collect")
    collector.add_argument("--suite")
    collector.add_argument("--source", choices=SOURCES)
    collector.add_argument("--php", dest="php_version", help="PHP major.minor to collect")
    collector.add_argument("--output", type=Path, default=ROOT / "measurements")
    renderer = sub.add_parser("render")
    renderer.add_argument("--input", type=Path, default=ROOT / "measurements")
    renderer.add_argument("--output", type=Path, default=ROOT / "site")
    args = parser.parse_args()
    if args.command == "matrix":
        print(json.dumps(list(sample_specs(matrix()))))
    elif args.command == "collect":
        samples = [
            sample for sample in sample_specs(matrix())
            if args.suite in (None, sample["suite"])
            and args.source in (None, sample["source"])
            and args.php_version in (None, sample["php"])
        ]
        if not samples:
            parser.error("no configured measurement matches the filters")
        for sample in samples:
            collect(sample, args.output)
    else:
        render(args.input, args.output)


if __name__ == "__main__":
    main()
