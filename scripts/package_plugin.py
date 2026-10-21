#!/usr/bin/env python3
"""Create a skills-only plugin archive with the requested manifest."""

import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


parser = argparse.ArgumentParser()
parser.add_argument("plugin_dir", type=Path)
parser.add_argument("manifest", choices=("codex", "claude"))
parser.add_argument("output", type=Path)
args = parser.parse_args()

root = args.plugin_dir
manifest = root / ("plugin.json" if args.manifest == "codex" else ".claude-plugin/plugin.json")
if not manifest.is_file():
    parser.error(f"Required plugin manifest not found: {manifest}")
files = [manifest] + sorted((root / "skills").rglob("*"))
files = [
    path for path in files
    if path.is_file()
    and path.name != ".DS_Store"
    and "__pycache__" not in path.relative_to(root).parts
]

args.output.parent.mkdir(parents=True, exist_ok=True)
with ZipFile(args.output, "w", ZIP_DEFLATED) as archive:
    for path in files:
        archive.write(path, path.relative_to(root))

print(args.output)
