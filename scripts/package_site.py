#!/usr/bin/env python3
"""Validate and stage the public site; never copy the repository wholesale."""
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import sys
from urllib.parse import unquote, urlsplit

PUBLIC_ROOT_FILES = ("index.html", ".htaccess", "favicon.ico")
ASSET_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".avif", ".ico", ".css", ".js", ".woff", ".woff2"}


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ("src", "href") and value:
                url = urlsplit(value)
                if not url.scheme and not url.netloc and url.path not in ("", "/"):
                    self.paths.append(unquote(url.path).lstrip("/"))


def package(source, output, revision):
    source = source.resolve()
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("Revision must be a full lowercase Git commit SHA")
    version = (source / "VERSION").read_text().strip()
    if not re.fullmatch(r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)", version):
        raise ValueError("VERSION must contain a semantic version such as 1.1.0")
    files = []
    for name in (*PUBLIC_ROOT_FILES, "assets"):
        path = source / name
        if path.is_symlink():
            raise ValueError(f"Symlinks are not publishable: {name}")
        if not path.exists():
            raise ValueError(f"Missing required public file: {name}")
        if name != "assets":
            if not path.is_file():
                raise ValueError(f"Expected a regular file: {name}")
            files.append(path)
    if not (source / "assets").is_dir():
        raise ValueError("assets must be a directory")
    for path in sorted((source / "assets").rglob("*")):
        relative = path.relative_to(source)
        if path.is_symlink():
            raise ValueError(f"Symlinks are not publishable: {relative}")
        if any(part.startswith(".") for part in relative.parts):
            raise ValueError(f"Unsupported public asset: {relative}")
        if path.is_dir():
            continue
        if not path.is_file() or path.suffix.lower() not in ASSET_EXTENSIONS:
            raise ValueError(f"Unsupported public asset: {relative}")
        files.append(path)
    references = References()
    references.feed((source / "index.html").read_text())
    public_paths = {p.relative_to(source).as_posix() for p in files}
    for reference in references.paths:
        if reference not in public_paths:
            raise ValueError(f"Missing local asset in deployment: {reference}")
    # An existing output is refused, so failed validation cannot leave a stale release.
    output.mkdir(parents=True, exist_ok=False)
    for path in files:
        target = output / path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    (output / "version.json").write_text(json.dumps({"version": version, "commit": revision}) + "\n")
    print(f"Packaged {len(files)} public files for version {version} ({revision})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--revision", required=True)
    args = parser.parse_args()
    try:
        package(args.source, args.output, args.revision)
    except (ValueError, OSError) as exc:
        sys.exit(str(exc))
