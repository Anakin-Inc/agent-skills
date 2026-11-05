#!/usr/bin/env python3
"""Mirror skills/ into copilot/skills/ and augment/skills/.

The Copilot plugin lives in copilot/ so that it can use the hosted MCP server:
at the repository root, Copilot runs the root .mcp.json (the local server) and
ignores a manifest's own mcpServers. Copilot also refuses a skills path that
leaves the plugin directory, so the plugin needs its own copy of the skills.

The Auggie (Augment Code) plugin in augment/ exists for the same two reasons:
Auggie reads a plugin's MCP servers only from the .mcp.json at the plugin root,
and it skips a skills/ directory that resolves outside the plugin directory.

skills/ stays the only place skills are edited. Run this after changing them;
scripts/validate.py fails while a copy differs.

Run: python3 scripts/sync_copilot_skills.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "skills"
TARGETS = (ROOT / "copilot" / "skills", ROOT / "augment" / "skills")

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


def sync(target_dir: Path, source: dict[Path, bytes]) -> None:
    target = skill_files(target_dir)

    changed = 0
    for rel, data in source.items():
        if target.get(rel) != data:
            dest = target_dir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            changed += 1
    for rel in target.keys() - source.keys():
        (target_dir / rel).unlink()
        changed += 1
    # Remove directories that a deleted skill left empty, deepest first.
    for path in sorted(target_dir.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if path.is_dir() and not any(path.iterdir()):
            path.rmdir()

    label = f"{target_dir.relative_to(ROOT)}/"
    if changed:
        print(f"{label}: {changed} file(s) updated from skills/")
    else:
        print(f"{label} already matches skills/")


def main() -> int:
    source = skill_files(SOURCE)
    if not source:
        print("error: no skills found in skills/", file=sys.stderr)
        return 1
    for target_dir in TARGETS:
        sync(target_dir, source)
    return 0


if __name__ == "__main__":
    sys.exit(main())
