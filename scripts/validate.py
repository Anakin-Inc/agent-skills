#!/usr/bin/env python3
"""Validate the plugin manifests and skills.

Checks the invariants that are easy to break by hand and expensive to discover
during a marketplace review:

  * every manifest is well-formed JSON
  * .mcp.json and mcp.json stay byte-identical (platforms disagree on the
    filename; the contents must not drift)
  * name/version/description agree across all three platform manifests
  * the Cursor manifest conforms to Cursor's published schema, which sets
    additionalProperties:false and rejects author.url
  * every skill has SKILL.md with name and description frontmatter, and its
    name matches its directory
  * the Claude manifest points its server at the hosted endpoint under the
    same name as .mcp.json, and no tracked file trips the Claude directory's
    blocking or held file rules

Run: python3 scripts/validate.py
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CURSOR_SCHEMA_URL = (
    "https://raw.githubusercontent.com/cursor/plugins/main/schemas/plugin.schema.json"
)

# Every file that inlines an mcpServers block. The platforms disagree on the
# filename and shape, so the same config is spelled three ways and must not
# drift between them.
MCP_CONFIG_FILES = (".mcp.json", "mcp.json", "gemini-extension.json")

# The Claude plugin uses the hosted OAuth server instead of the local npx one.
HOSTED_MCP_URL = "https://mcp.anakin.io/mcp"

# Anthropic's directory blocks OS metadata files and holds non-image binaries.
SYSTEM_FILES = {".DS_Store", "Thumbs.db", "desktop.ini", "__MACOSX"}
IMAGE_OR_FONT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".woff", ".woff2", ".ttf", ".otf"}
HELD_BINARY = {".pyc", ".ico", ".pdf", ".zip", ".mcpb", ".dxt", ".exe", ".so", ".dylib", ".jar"}

errors: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def load_json(rel: str) -> dict | None:
    path = ROOT / rel
    if not path.exists():
        err(f"{rel}: missing")
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        err(f"{rel}: invalid JSON — {exc}")
        return None


def check_mcp_in_sync() -> None:
    a, b = ROOT / ".mcp.json", ROOT / "mcp.json"
    if not (a.exists() and b.exists()):
        err("both .mcp.json (Claude/Grok) and mcp.json (Cursor) must exist")
        return
    if a.read_text() != b.read_text():
        err(".mcp.json and mcp.json have drifted — contents must be identical")


def check_gemini_matches() -> None:
    """The Gemini manifest inlines its own mcpServers block; keep it identical."""
    base = load_json(".mcp.json")
    gem = load_json("gemini-extension.json")
    if not base or not gem:
        return
    if gem.get("mcpServers") != base.get("mcpServers"):
        err("gemini-extension.json: mcpServers block differs from .mcp.json")


def check_server_version_pinned() -> None:
    """The MCP server must be pinned to an exact version.

    The marketplaces pin this repo to a frozen commit SHA. A floating npm tag
    (@latest, ^0.1.5, ...) would defeat that: the reviewed SHA would still be
    able to execute code nobody reviewed, and an upstream signature change
    would break already-installed users with no plugin release. Bumping the
    version is a deliberate, reviewable edit.
    """
    for rel in MCP_CONFIG_FILES:
        config = load_json(rel)
        if not config:
            continue
        for server, spec in config.get("mcpServers", {}).items():
            args = spec.get("args", [])
            pkgs = [
                a
                for a in args
                if isinstance(a, str) and a.startswith("@anakin-io/mcp")
            ]
            if not pkgs:
                err(f"{rel}: server {server!r} does not reference @anakin-io/mcp")
                continue
            for pkg in pkgs:
                _, _, version = pkg.partition("@anakin-io/mcp")
                version = version.lstrip("@")
                if not re.fullmatch(r"\d+\.\d+\.\d+", version):
                    err(
                        f"{rel}: {pkg!r} is not pinned to an exact version — "
                        f"floating tags and ranges defeat the marketplace SHA pin"
                    )


def check_no_env_placeholders() -> None:
    """No ``${VAR}`` placeholders in the MCP env block.

    Clients that do not expand ``${VAR}`` pass the literal string through. The
    server treats a non-empty value as a real key, so it starts and advertises
    all its tools, and every call then fails at the API — the user sees working
    tools that mysteriously do not work.

    With no ``env`` block the server inherits the client environment. An absent
    or empty key makes it exit immediately with a message naming the variable
    and where to get one, which is the failure mode we want.
    """
    for rel in MCP_CONFIG_FILES:
        config = load_json(rel)
        if not config:
            continue
        for server, spec in config.get("mcpServers", {}).items():
            for key, value in (spec.get("env") or {}).items():
                if isinstance(value, str) and re.search(r"\$\{[^}]+\}", value):
                    err(
                        f"{rel}: {server}.env.{key} contains a ${{...}} placeholder — "
                        f"clients that do not expand it pass the literal through, "
                        f"producing tools that appear to work but always fail"
                    )


def check_claude_hosted_server() -> None:
    """The Claude manifest must point every server at the hosted endpoint.

    Claude loads .mcp.json first, then the manifest's mcpServers, and a later
    entry replaces an earlier one only when the names match. If the names
    drift, Claude runs both: the hosted server, and an npx server that dies
    without ANAKIN_API_KEY -- duplicate tools, half of them broken.
    """
    manifest = load_json(".claude-plugin/plugin.json")
    local = load_json(".mcp.json")
    if not manifest or not local:
        return
    servers = manifest.get("mcpServers")
    if not isinstance(servers, dict) or not servers:
        err(".claude-plugin/plugin.json: mcpServers must inline the hosted server")
        return
    local_names = set(local.get("mcpServers", {}))
    if set(servers) != local_names:
        err(
            f".claude-plugin/plugin.json: mcpServers names {sorted(servers)} must "
            f"match .mcp.json {sorted(local_names)} so the hosted entry replaces "
            f"the local one instead of running alongside it"
        )
    for name, spec in servers.items():
        if spec.get("type") != "http":
            err(f".claude-plugin/plugin.json: server {name!r} must be type 'http'")
        if spec.get("url") != HOSTED_MCP_URL:
            err(f".claude-plugin/plugin.json: server {name!r} url must be {HOSTED_MCP_URL}")
        if "headers" in spec or "env" in spec:
            err(
                f".claude-plugin/plugin.json: server {name!r} must not carry headers "
                f"or env -- the hosted server authenticates over OAuth"
            )


def check_claude_listing_fields() -> None:
    """Directory listing fields: https URLs and an icon that exists."""
    manifest = load_json(".claude-plugin/plugin.json")
    if not manifest:
        return
    for field in ("documentationUrl", "supportUrl", "privacyPolicyUrl", "termsOfServiceUrl"):
        value = manifest.get(field)
        if not (isinstance(value, str) and value.startswith("https://")):
            err(f".claude-plugin/plugin.json: {field} must be an https:// URL")
    icon = manifest.get("icon")
    if not (isinstance(icon, str) and icon.startswith("./") and (ROOT / icon).is_file()):
        err(f".claude-plugin/plugin.json: icon {icon!r} must be a ./ path to an existing file")


def tracked_files() -> list[str] | None:
    """Files git will put in the archive the directory validates, or None."""
    try:
        out = subprocess.run(
            ["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    return [p for p in out.decode().split("\0") if p]


def check_directory_file_rules() -> None:
    """Rules Anthropic's directory blocks or holds on, checked before a push.

    The repo root is the plugin folder, so every tracked file counts. See
    https://claude.com/docs/plugins/pre-submission-checklist
    """
    files = tracked_files()
    if files is None:
        print("warning: git unavailable; skipping directory file checks", file=sys.stderr)
        return
    if len(files) > 512:
        err(f"{len(files)} tracked files -- the directory holds plugins over 512")
    for rel in files:
        parts = Path(rel).parts
        name = parts[-1]
        if name in SYSTEM_FILES or any(p in SYSTEM_FILES for p in parts):
            err(f"{rel}: OS metadata file -- the directory blocks these")
            continue
        suffix = Path(rel).suffix.lower()
        if suffix in IMAGE_OR_FONT:
            continue
        if suffix in HELD_BINARY or "__pycache__" in parts:
            err(f"{rel}: binary file -- the directory holds these for manual review")
            continue
        path = ROOT / rel
        if path.is_file() and path.stat().st_size > 256 * 1024:
            err(f"{rel}: over 256 KiB -- the directory holds these for manual review")


def check_manifests_agree() -> None:
    manifests = {
        rel: load_json(rel)
        for rel in (
            ".claude-plugin/plugin.json",
            ".grok-plugin/plugin.json",
            ".cursor-plugin/plugin.json",
            ".codex-plugin/plugin.json",
            ".github/plugin/plugin.json",
            "gemini-extension.json",
        )
    }
    present = {k: v for k, v in manifests.items() if v}
    for field in ("name", "version", "description"):
        values = {rel: m.get(field) for rel, m in present.items()}
        if len(set(values.values())) > 1:
            err(f"manifests disagree on {field}: {values}")


def check_cursor_schema() -> None:
    manifest = load_json(".cursor-plugin/plugin.json")
    if not manifest:
        return
    try:
        with urllib.request.urlopen(CURSOR_SCHEMA_URL, timeout=30) as resp:
            schema = json.loads(resp.read())
    except Exception as exc:  # network flake must not mask real failures
        print(f"warning: could not fetch Cursor schema ({exc}); skipping", file=sys.stderr)
        return

    props = schema["properties"]
    defs = schema.get("$defs", {})

    for key in schema.get("required", []):
        if key not in manifest:
            err(f".cursor-plugin/plugin.json: missing required field {key!r}")
    if schema.get("additionalProperties") is False:
        for key in manifest:
            if key not in props:
                err(f".cursor-plugin/plugin.json: field {key!r} not allowed by schema")

    pattern = props.get("name", {}).get("pattern")
    if pattern and not re.match(pattern, manifest.get("name", "")):
        err(f".cursor-plugin/plugin.json: name must match {pattern}")

    author = manifest.get("author")
    if author is not None and "author" in defs:
        spec = defs["author"]
        for key in spec.get("required", []):
            if key not in author:
                err(f".cursor-plugin/plugin.json: author missing {key!r}")
        for key in author:
            if key not in spec["properties"]:
                err(
                    f".cursor-plugin/plugin.json: author.{key} not allowed "
                    f"(schema permits {list(spec['properties'])})"
                )


# The tool surface of the pinned server, verified against a live tools/list.
# Keep in sync when bumping the pin -- check-server-version.py prints the new
# list on upgrade.
TOOLS = [
    "scrape", "search", "map", "crawl", "agentic_search",
    "wire_discover", "wire_catalog", "wire_read_action", "wire_write_action",
    "wire_identities", "wire_login", "wire_build",
    "monitor_create", "monitor_list", "monitor_changes", "monitor_control",
    "ai_visibility_search", "ai_visibility_sources",
    "session_list", "session_delete",
    "browser_task",
]

# Tools only the hosted server (mcp.anakin.io, used by the Claude plugin)
# exposes. The skills must still describe them, or Claude plugin users get a
# tool no skill explains. Keep in sync with anakin-mcp-remote's src/tools.
HOSTED_ONLY_TOOLS = ["wire_build_status"]

# Tools that existed in an earlier pin and no longer do. A skill still naming
# one of these sends the agent after a tool the server will reject.
REMOVED_TOOLS = {
    "wire_action": "split into wire_read_action / wire_write_action in 0.2.0",
}


def check_tool_coverage() -> None:
    """Every tool documented somewhere, and no skill naming a removed tool.

    Skills are the plugin's whole value; a skill describing a tool that no
    longer exists is worse than no skill, because the agent will confidently
    call it. This is the check that catches a server bump the skills did not
    follow.
    """
    skills_dir = ROOT / "skills"
    if not skills_dir.is_dir():
        return
    corpus = {
        md: md.read_text()
        for md in skills_dir.glob("*/SKILL.md")
    }
    if not corpus:
        return

    joined = "\n".join(corpus.values())
    for tool in TOOLS:
        if not re.search(rf"\b{re.escape(tool)}\b", joined):
            err(f"tool {tool!r} is exposed by the pinned server but no skill mentions it")
    for tool in HOSTED_ONLY_TOOLS:
        if not re.search(rf"\b{re.escape(tool)}\b", joined):
            err(f"tool {tool!r} is exposed by the hosted server but no skill mentions it")

    for md, text in corpus.items():
        rel = md.relative_to(ROOT)
        for gone, why in REMOVED_TOOLS.items():
            # Word boundary alone would match wire_action inside
            # wire_action_id; require the name not be followed by _ or a letter.
            if re.search(rf"\b{re.escape(gone)}(?![\w])", text):
                err(f"{rel}: references removed tool {gone!r} — {why}")


def check_skills() -> None:
    skills_dir = ROOT / "skills"
    if not skills_dir.is_dir():
        err("skills/ is missing")
        return
    found = False
    for sub in sorted(skills_dir.iterdir()):
        if not sub.is_dir():
            continue
        found = True
        md = sub / "SKILL.md"
        if not md.exists():
            err(f"skills/{sub.name}: no SKILL.md")
            continue
        text = md.read_text()
        match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
        if not match:
            err(f"skills/{sub.name}/SKILL.md: missing YAML frontmatter")
            continue
        front = match.group(1)
        name = re.search(r"^name:\s*(.+)$", front, re.MULTILINE)
        desc = re.search(r"^description:\s*(.+)$", front, re.MULTILINE)
        if not name:
            err(f"skills/{sub.name}/SKILL.md: frontmatter missing 'name'")
        elif name.group(1).strip() != sub.name:
            err(
                f"skills/{sub.name}/SKILL.md: frontmatter name "
                f"{name.group(1).strip()!r} != directory {sub.name!r}"
            )
        if not desc:
            err(f"skills/{sub.name}/SKILL.md: frontmatter missing 'description'")
    if not found:
        err("skills/ contains no skill directories")


def main() -> int:
    load_json(".mcp.json")
    load_json("mcp.json")
    load_json(".claude-plugin/marketplace.json")
    check_mcp_in_sync()
    check_gemini_matches()
    check_server_version_pinned()
    check_no_env_placeholders()
    check_claude_hosted_server()
    check_claude_listing_fields()
    check_directory_file_rules()
    check_manifests_agree()
    check_cursor_schema()
    check_skills()
    check_tool_coverage()

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        print(f"\n{len(errors)} problem(s) found.", file=sys.stderr)
        return 1
    print("All manifests and skills valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
