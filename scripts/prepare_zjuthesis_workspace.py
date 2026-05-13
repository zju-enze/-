#!/usr/bin/env python3
"""Prepare a generated zjuthesis workspace without modifying the source template."""

from __future__ import annotations

import argparse
import os
import re
import shutil
from pathlib import Path


EXCLUDED_DIRS = {
    ".git",
    "generated-thesis",
    "out",
    "build",
    "dist",
    "target",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".cache",
    ".pytest_cache",
}

EXCLUDED_FILES = {
    ".DS_Store",
}

EXCLUDED_SUFFIXES = {
    ".aux",
    ".bbl",
    ".bcf",
    ".blg",
    ".fls",
    ".fdb_latexmk",
    ".log",
    ".run.xml",
    ".synctex.gz",
    ".toc",
}


def should_ignore(_dir: str, names: list[str]) -> set[str]:
    ignored: set[str] = set()
    for name in names:
        path = Path(name)
        if name in EXCLUDED_DIRS or name in EXCLUDED_FILES:
            ignored.add(name)
        elif name.endswith(".synctex.gz") or path.suffix.lower() in EXCLUDED_SUFFIXES:
            ignored.add(name)
    return ignored


def parse_document_options(tex_path: Path) -> dict[str, str]:
    text = tex_path.read_text(encoding="utf-8")
    match = re.search(r"\\documentclass\s*\[(.*?)\]\s*\{zjuthesis\}", text, re.S)
    if not match:
        return {}
    options: dict[str, str] = {}
    for raw_line in match.group(1).splitlines():
        line = raw_line.split("%", 1)[0].strip().rstrip(",")
        if not line or "=" not in line:
            continue
        key, value = line.split("=", 1)
        options[key.strip()] = value.strip()
    return options


def write_generation_notes(output: Path, options: dict[str, str], template_root: Path) -> None:
    notes = output / "generation_notes.md"
    lines = [
        "# Generated Thesis Workspace",
        "",
        "This directory is a copied zjuthesis workspace for generated thesis drafting.",
        "Original template files outside this directory were not modified.",
        "",
        f"Template source: `{template_root}`",
        "",
        "## Detected zjuthesis Options",
        "",
    ]
    for key in sorted(options):
        lines.append(f"- {key}: `{options[key]}`")
    notes.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def is_template_root(path: Path) -> bool:
    return (path / "zjuthesis.tex").is_file() and (path / "zjuthesis.cls").is_file()


def bundled_template_root() -> Path:
    return Path(__file__).resolve().parents[1] / "template"


def resolve_template_root(root: Path, explicit_template_root: str | None) -> Path:
    if explicit_template_root:
        template_root = Path(explicit_template_root).resolve()
        if not is_template_root(template_root):
            raise SystemExit(f"{template_root} does not look like a zjuthesis template root.")
        return template_root
    if is_template_root(root):
        return root
    template_root = bundled_template_root()
    if is_template_root(template_root):
        return template_root
    raise SystemExit(
        f"{root} does not look like a zjuthesis template root, and bundled template was not found at {template_root}."
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Working directory. If it is not a zjuthesis template root, the bundled template is used.",
    )
    parser.add_argument("--output", default="generated-thesis", help="Generated workspace directory.")
    parser.add_argument("--template-root", default=None, help="Explicit zjuthesis template root.")
    parser.add_argument("--force", action="store_true", help="Replace an existing output directory.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    output = Path(args.output).resolve()
    template_root = resolve_template_root(root, args.template_root)
    if output == template_root or template_root in output.parents:
        raise SystemExit("Refusing to copy template onto itself.")
    if output.exists():
        if not args.force:
            raise SystemExit(f"{output} already exists. Re-run with --force to replace it.")
        shutil.rmtree(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(template_root, output, ignore=should_ignore)
    options = parse_document_options(output / "zjuthesis.tex")
    write_generation_notes(output, options, template_root)
    print(f"Prepared {output}")
    print(f"Template source: {template_root}")
    if options:
        print("Detected options: " + ", ".join(f"{key}={value}" for key, value in sorted(options.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
