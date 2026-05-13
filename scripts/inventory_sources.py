#!/usr/bin/env python3
"""Inventory local thesis source materials."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".svn",
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
    ".mypy_cache",
    ".pytest_cache",
    ".tox",
}

EXCLUDED_SUFFIXES = {
    ".aux",
    ".bbl",
    ".bcf",
    ".blg",
    ".fls",
    ".fdb_latexmk",
    ".log",
    ".out",
    ".run.xml",
    ".synctex.gz",
    ".toc",
}

CATEGORY_EXTENSIONS = {
    "pdf": {".pdf"},
    "word": {".docx", ".doc"},
    "spreadsheet": {".xlsx", ".xls", ".csv", ".tsv"},
    "image": {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tif", ".tiff", ".webp", ".svg"},
    "latex": {".tex", ".cls", ".sty"},
    "bibliography": {".bib"},
    "markdown": {".md", ".markdown", ".rst", ".txt"},
    "code": {
        ".py",
        ".r",
        ".jl",
        ".m",
        ".c",
        ".cc",
        ".cpp",
        ".h",
        ".hpp",
        ".java",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".go",
        ".rs",
        ".sh",
        ".ps1",
        ".sql",
        ".ipynb",
    },
    "data": {".json", ".jsonl", ".yaml", ".yml", ".xml", ".parquet", ".feather", ".pkl"},
    "config": {".toml", ".ini", ".cfg", ".conf", ".lock"},
    "archive": {".zip", ".tar", ".gz", ".tgz", ".rar", ".7z"},
}


def category_for(path: Path) -> str:
    suffix = "".join(path.suffixes[-2:]).lower()
    if suffix in EXCLUDED_SUFFIXES:
        return "build-artifact"
    ext = path.suffix.lower()
    for category, extensions in CATEGORY_EXTENSIONS.items():
        if ext in extensions:
            return category
    if path.name.lower() in {"readme", "makefile", "dockerfile"}:
        return "markdown" if path.name.lower() == "readme" else "config"
    return "other"


def is_excluded_file(path: Path) -> bool:
    lowered = path.name.lower()
    if lowered.endswith(".synctex.gz"):
        return True
    return path.suffix.lower() in EXCLUDED_SUFFIXES or category_for(path) == "build-artifact"


def sha256_for(path: Path, max_bytes: int = 64 * 1024 * 1024) -> str | None:
    try:
        if path.stat().st_size > max_bytes:
            return None
        digest = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except OSError:
        return None


def run_git(root: Path, args: list[str]) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def collect_git_summary(root: Path) -> dict[str, object] | None:
    top_level = run_git(root, ["rev-parse", "--show-toplevel"])
    if not top_level:
        return None
    return {
        "top_level": top_level,
        "branch": run_git(root, ["branch", "--show-current"]),
        "head": run_git(root, ["rev-parse", "--short", "HEAD"]),
        "status_short": run_git(root, ["status", "--short"]) or "",
        "recent_commits": (run_git(root, ["log", "--oneline", "-n", "20"]) or "").splitlines(),
    }


def inventory(root: Path) -> dict[str, object]:
    files: list[dict[str, object]] = []
    counts: dict[str, int] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS and not d.startswith(".Trash")]
        for filename in filenames:
            path = current / filename
            if is_excluded_file(path):
                continue
            try:
                stat = path.stat()
            except OSError:
                continue
            rel = path.relative_to(root).as_posix()
            category = category_for(path)
            counts[category] = counts.get(category, 0) + 1
            files.append(
                {
                    "path": rel,
                    "category": category,
                    "extension": path.suffix.lower(),
                    "size_bytes": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                    "sha256": sha256_for(path),
                }
            )
    files.sort(key=lambda item: item["path"])
    return {
        "root": str(root),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "counts": dict(sorted(counts.items())),
        "files": files,
        "git": collect_git_summary(root),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="Directory to inventory.")
    parser.add_argument("--output", default="source_inventory.json", help="JSON output path.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    data = inventory(root)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {output} with {len(data['files'])} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
