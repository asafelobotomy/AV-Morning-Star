#!/usr/bin/env python3
"""Enforce per-file line-count limits for Python source files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

DEFAULT_WARN = 200
DEFAULT_FAIL = 400

EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "ENV",
    "env",
    "build",
    "dist",
    "squashfs-root",
    "__pycache__",
    ".ruff_cache",
    ".mypy_cache",
    ".pytest_cache",
}


def iter_python_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(root.rglob("*.py")):
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        files.append(path)
    return files


def count_lines(path: Path) -> int:
    return sum(1 for _ in path.open(encoding="utf-8"))


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return str(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Report Python files exceeding line-count thresholds.",
    )
    parser.add_argument(
        "--warn",
        type=int,
        default=DEFAULT_WARN,
        help=f"Warn when a file exceeds this many lines (default: {DEFAULT_WARN})",
    )
    parser.add_argument(
        "--fail",
        type=int,
        default=DEFAULT_FAIL,
        help=f"Exit with failure when a file exceeds this many lines (default: {DEFAULT_FAIL})",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="Directories to scan (default: current directory)",
    )
    args = parser.parse_args(argv)

    warnings: list[tuple[str, int]] = []
    failures: list[tuple[str, int]] = []

    for base in args.paths:
        root = Path(base).resolve()
        if not root.exists():
            print(f"error: path not found: {root}", file=sys.stderr)
            return 2

        for path in iter_python_files(root):
            loc = count_lines(path)
            label = relative(path)
            if loc > args.fail:
                failures.append((label, loc))
            elif loc > args.warn:
                warnings.append((label, loc))

    if warnings:
        print(f"LOC warnings (>{args.warn} lines):", file=sys.stderr)
        for label, loc in sorted(warnings, key=lambda item: (-item[1], item[0])):
            print(f"  WARN {loc:4d}  {label}", file=sys.stderr)

    if failures:
        print(f"LOC failures (>{args.fail} lines):", file=sys.stderr)
        for label, loc in sorted(failures, key=lambda item: (-item[1], item[0])):
            print(f"  FAIL {loc:4d}  {label}", file=sys.stderr)

    if warnings or failures:
        print(
            f"\nSummary: {len(warnings)} warning(s), {len(failures)} failure(s)",
            file=sys.stderr,
        )
    else:
        print(f"All Python files are within {args.warn} LOC (warn) / {args.fail} LOC (hard limit).")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
