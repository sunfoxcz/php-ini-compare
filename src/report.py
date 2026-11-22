"""Collect and compare packaged PHP INI settings on Ubuntu LTS."""

import argparse
import html
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from shutil import copyfile


ROOT = Path(__file__).resolve().parents[1]
SOURCES = ("ubuntu", "sury")
SAPIS = {"cli": "CLI", "fpm": "PHP-FPM"}


def matrix():
    return json.loads((ROOT / "matrix.json").read_text())


def load_snapshot(path, release, source):
    sample = json.loads(path.read_text())
    for key, value in {**release, "source": source}.items():
        if key != "php" and sample.get(key) != value:
            raise ValueError(f"{path}: expected {key}={value}")
    for key, sapi in (("cli", "cli"), ("fpm", "fpm-fcgi")):
        run = sample[key]
        if run["sapi"] != sapi or not run["php"].startswith(release["php"] + "."):
            raise ValueError(f"{path}: unexpected SAPI or PHP version in {key}")
        if not run["directives"] or not run["config"]:
            raise ValueError(f"{path}: incomplete {key} snapshot")
    return sample


def collect(release, source, output):
    tag = f"php-ini-compare:{release['suite']}-{source}"
    target = output / f"{release['suite']}-{source}.json"
    output.mkdir(parents=True, exist_ok=True)
    args = {"UBUNTU": release["ubuntu"], "SUITE": release["suite"],
            "PHP_VERSION": release["php"], "SOURCE": source}
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
        load_snapshot(temporary, release, source)
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)


def differences(ubuntu, sury):
    for name in sorted(ubuntu.keys() | sury.keys()):
        if name not in ubuntu:
            yield name, "Surý only", None, sury[name]
        elif name not in sury:
            yield name, "Ubuntu only", ubuntu[name], None
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


def render_comparison(release, ubuntu, sury, sapi):
    left, right = ubuntu[sapi], sury[sapi]
    if left["architecture"] != right["architecture"]:
        raise ValueError("Cannot compare snapshots from different CPU architectures")
    rows = list(differences(left["directives"], right["directives"]))
    table = "".join(
        f'<tr data-difference><th scope="row"><code>{escape(name)}</code>'
        f'<small>{status}</small></th>{directive_cells(a)}{directive_cells(b)}</tr>'
        for name, status, a, b in rows
    )
    ext = []
    left_ext, right_ext = set(left["extensions"]), set(right["extensions"])
    for label, names in (("Ubuntu only", left_ext - right_ext), ("Surý only", right_ext - left_ext)):
        if names:
            ext.append(f'{label} <code>{escape(", ".join(sorted(names)))}</code>')
    extensions = " · ".join(ext) if ext else "Same loaded extensions"
    release_id = escape(release["suite"])
    label = escape(SAPIS[sapi])
    title = f'Ubuntu {escape(release["ubuntu"])} · PHP {escape(release["php"])} · {label}'
    summary = (
        f'{sum(status == "Changed" for _, status, _, _ in rows)} changed · '
        f'{sum(status != "Changed" for _, status, _, _ in rows)} registered on one side only'
    )
    table_markup = (
        '<div class="table-scroll" tabindex="0" aria-label="Directive differences">'
        '<table><thead><tr><th rowspan="2" scope="col">Directive</th>'
        '<th colspan="2" scope="colgroup">Ubuntu</th><th colspan="2" scope="colgroup">Surý</th></tr>'
        '<tr><th scope="col">Global</th><th scope="col">Local</th>'
        f'<th scope="col">Global</th><th scope="col">Local</th></tr></thead>'
        f'<tbody>{table}</tbody></table></div>' if rows else "<p>No INI directive differences.</p>"
    )
    return f'''
<section class="comparison" id="{release_id}-{sapi}" data-release="{release_id}" data-sapi="{sapi}">
  <h2>{title}</h2>
  <p class="summary">{summary} <span>{extensions}</span></p>
  <div class="sources">
    <div><strong>Ubuntu</strong> <code>{escape(left['php'])}</code>
      <a href="data/{release_id}-ubuntu.json" download>JSON</a>{provenance(ubuntu, sapi)}
    </div>
    <div><strong>Surý</strong> <code>{escape(right['php'])}</code>
      <a href="data/{release_id}-sury.json" download>JSON</a>{provenance(sury, sapi)}
    </div>
  </div>
  {table_markup}
</section>'''


def render(input_dir, output_dir):
    # Validate the entire matrix before replacing the published report.
    samples = [
        (release, *(load_snapshot(input_dir / f"{release['suite']}-{source}.json", release, source)
                    for source in SOURCES))
        for release in matrix()
    ]
    cards = "".join(render_comparison(release, ubuntu, sury, sapi)
                    for release, ubuntu, sury in samples for sapi in SAPIS)
    releases = "".join(
        f'<option value="{escape(release["suite"])}">Ubuntu {escape(release["ubuntu"])}</option>'
        for release, _, _ in samples
    )
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    page = (ROOT / "src" / "report.html").read_text()
    output_dir.mkdir(parents=True, exist_ok=True)
    data_dir = output_dir / "data"
    data_dir.mkdir(exist_ok=True)
    for release, _, _ in samples:
        for source in SOURCES:
            filename = f"{release['suite']}-{source}.json"
            copyfile(input_dir / filename, data_dir / filename)
    (output_dir / "index.html").write_text(
        page.replace("%%UPDATED%%", now).replace("%%RELEASES%%", releases).replace("%%CARDS%%", cards),
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("matrix")
    collector = sub.add_parser("collect")
    collector.add_argument("--suite")
    collector.add_argument("--source", choices=SOURCES)
    collector.add_argument("--output", type=Path, default=ROOT / "measurements")
    renderer = sub.add_parser("render")
    renderer.add_argument("--input", type=Path, default=ROOT / "measurements")
    renderer.add_argument("--output", type=Path, default=ROOT / "site")
    args = parser.parse_args()
    if args.command == "matrix":
        print(json.dumps([release | {"source": source} for release in matrix() for source in SOURCES]))
    elif args.command == "collect":
        releases = [release for release in matrix() if args.suite in (None, release["suite"])]
        if not releases:
            parser.error(f"unknown Ubuntu suite: {args.suite}")
        for release in releases:
            for source in [args.source] if args.source else SOURCES:
                collect(release, source, args.output)
    else:
        render(args.input, args.output)


if __name__ == "__main__":
    main()
