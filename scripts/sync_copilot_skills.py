#!/usr/bin/env python3
"""Mirror skills/ into copilot/skills/.

The Copilot plugin lives in copilot/ so that it can use the hosted MCP server:
at the repository root, Copilot runs the root .mcp.json (the local server) and
ignores a manifest's own mcpServers. Copilot also refuses a skills path that
leaves the plugin directory, so the plugin needs its own copy of the skills.

skills/ stays the only place skills are edited. Run this after changing them;
scripts/validate.py fails while the copy differs.

Run: python3 scripts/sync_copilot_skills.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "skills"
TARGET = ROOT / "copilot" / "skills"

# OS metadata and caches: never part of a skill, never copied.
IGNORED = {".DS_Store", "Thumbs.db", "desktop.ini", "__MACOSX", "__pycache__"}


def skill_files(base: Path) -> dict[Path, bytes]:
    """Every file under base, keyed by its path relative to base."""
    if not base.is_dir():
        return {}
    return {
        path.relative_to(base): path.read_bytes()
        for path in sorted(base.rglob("*"))
        if path.is_file() and not IGNORED.intersection(path.relative_to(base).parts)
    }


def main() -> int:
    source = skill_files(SOURCE)
    if not source:
        print("error: no skills found in skills/", file=sys.stderr)
        return 1
    target = skill_files(TARGET)

    changed = 0
    for rel, data in source.items():
        if target.get(rel) != data:
            dest = TARGET / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            changed += 1
    for rel in target.keys() - source.keys():
        (TARGET / rel).unlink()
        changed += 1
    # Remove directories that a deleted skill left empty, deepest first.
    for path in sorted(TARGET.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if path.is_dir() and not any(path.iterdir()):
            path.rmdir()

    if changed:
        print(f"copilot/skills/: {changed} file(s) updated from skills/")
    else:
        print("copilot/skills/ already matches skills/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
