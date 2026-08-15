#!/usr/bin/env python3
"""PostToolUse hook: validate a site file right after it is written.

Reads the hook payload on stdin, and if the edited file is site content,
runs the scoped page checks. Errors go to stderr with exit code 2 so Claude
sees them immediately and can fix the file it just broke. Warnings and clean
runs stay silent — this must not add noise to unrelated work.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

WATCHED_SUFFIXES = {".html", ".xml", ".txt"}
HERE = Path(__file__).resolve().parent


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    tool_input = payload.get("tool_input") or {}
    raw_path = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not raw_path:
        return 0

    edited = Path(raw_path)
    if edited.suffix.lower() not in WATCHED_SUFFIXES:
        return 0

    project = Path(payload.get("cwd") or ".").resolve()
    if not (project / "index.html").exists():
        return 0

    try:
        edited = edited.resolve().relative_to(project)
    except ValueError:
        return 0

    # Only top-level site files; ignore the plugin's own docs and any nested notes.
    if len(edited.parts) != 1:
        return 0

    cmd = [sys.executable, str(HERE / "check_site.py"), "--root", str(project), "--errors-only"]
    if edited.suffix.lower() == ".html":
        cmd += ["--files", edited.name]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        return 0

    print(f"Site integrity check failed after editing {edited}:\n{result.stdout.strip()}",
          file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
