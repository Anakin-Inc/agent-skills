#!/usr/bin/env python3
"""Report whether a newer @anakin-io/mcp has been published.

The plugin pins an exact server version so upgrades are deliberate. The cost of
pinning is staleness: nothing here would otherwise notice a new release. This
script closes that gap — CI runs it on a schedule and opens an issue when the
pinned version falls behind npm.

Exit codes:
  0  pinned version is current (or ahead — e.g. an unpublished release)
  1  a newer version exists, or the check could not complete

Writes `current=`, `latest=` and `outdated=` to $GITHUB_OUTPUT when set.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKAGE = "@anakin-io/mcp"
REGISTRY = "https://registry.npmjs.org/@anakin-io%2Fmcp/latest"


def pinned_version() -> str:
    """Read the exact version pinned in .mcp.json."""
    config = json.loads((ROOT / ".mcp.json").read_text())
    for spec in config.get("mcpServers", {}).values():
        for arg in spec.get("args", []):
            if isinstance(arg, str) and arg.startswith(PACKAGE):
                version = arg[len(PACKAGE):].lstrip("@")
                if not re.fullmatch(r"\d+\.\d+\.\d+", version):
                    raise SystemExit(f"pinned spec {arg!r} is not an exact version")
                return version
    raise SystemExit(f".mcp.json does not reference {PACKAGE}")


def latest_version() -> str:
    req = urllib.request.Request(REGISTRY, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())["version"]


def as_tuple(version: str) -> tuple[int, ...]:
    return tuple(int(p) for p in version.split("."))


def emit(current: str, latest: str, outdated: bool) -> None:
    out = os.environ.get("GITHUB_OUTPUT")
    if not out:
        return
    with open(out, "a") as fh:
        fh.write(f"current={current}\n")
        fh.write(f"latest={latest}\n")
        fh.write(f"outdated={'true' if outdated else 'false'}\n")


ISSUE_BODY = """\
The plugin pins `@anakin-io/mcp@{current}`. npm now publishes `{latest}`.

Plugin users stay on `{current}` until this is bumped and released — that is the
intended behaviour, not a bug. This issue exists so the decision gets made
rather than forgotten.

**Before bumping, confirm the tool signatures did not change.** The upstream
package is pre-1.0 and documents that signatures may change; a signature change
reaching installed users is exactly what the pin prevents.

```sh
printf '%s\\n%s\\n%s\\n' \\
  '{{"jsonrpc":"2.0","id":1,"method":"initialize","params":{{"protocolVersion":"2024-11-05","capabilities":{{}},"clientInfo":{{"name":"probe","version":"1"}}}}}}' \\
  '{{"jsonrpc":"2.0","method":"notifications/initialized"}}' \\
  '{{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{{}}}}' \\
  | ANAKIN_API_KEY=probe npx -y @anakin-io/mcp@{latest} 2>/dev/null \\
  | python3 -c "import sys,json
for line in sys.stdin:
    m=json.loads(line)
    if m.get('id')==2: print(len(m['result']['tools']), [t['name'] for t in m['result']['tools']])"
```

Compare against the {tool_count} tools the skills currently document:
{tool_list}

To upgrade:
1. Set the version in `.mcp.json` and `mcp.json` (CI enforces they match)
2. Bump `version` in the three platform manifests (CI enforces they agree)
3. Update any skill whose documented parameters changed
4. Release, then re-pin the new commit SHA in each marketplace
"""

DOCUMENTED_TOOLS = [
    "scrape", "search", "map", "crawl", "agentic_search",
    "wire_discover", "wire_catalog", "wire_action",
    "wire_identities", "wire_login", "wire_build",
]


def write_issue_body(current: str, latest: str) -> Path:
    """Render the issue body to a file for `gh issue create --body-file`.

    Generated here rather than in shell so backticks, quotes and backslashes in
    the reproduction command survive intact.
    """
    path = ROOT / ".issue-body.md"
    path.write_text(
        ISSUE_BODY.format(
            current=current,
            latest=latest,
            tool_count=len(DOCUMENTED_TOOLS),
            tool_list="\n".join(f"- `{t}`" for t in DOCUMENTED_TOOLS),
        )
    )
    return path


def main() -> int:
    current = pinned_version()
    try:
        latest = latest_version()
    except (urllib.error.URLError, KeyError, json.JSONDecodeError) as exc:
        print(f"could not reach the npm registry: {exc}", file=sys.stderr)
        return 1

    outdated = as_tuple(latest) > as_tuple(current)
    emit(current, latest, outdated)

    if outdated:
        path = write_issue_body(current, latest)
        print(f"OUTDATED: pinned {current}, latest published is {latest}")
        print(f"issue body written to {path.name}")
        return 1
    print(f"current: pinned {current} is the latest published version")
    return 0


if __name__ == "__main__":
    sys.exit(main())
