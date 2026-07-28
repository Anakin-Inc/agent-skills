# MCP clients without a plugin marketplace

Claude Code, Codex, Grok, Cursor, Gemini CLI, and Copilot/VS Code install Anakin
as a packaged plugin — see the root [README](../README.md#install). Every
other client below has **no marketplace Anakin can submit a package to**; the
only install path is the user pasting a config snippet into that client's own
MCP settings. This page is that snippet, once per client, verified against
each vendor's current docs rather than assumed from the Claude Desktop
convention other clients are loosely modeled on.

Get a free API key at [anakin.io/dashboard](https://anakin.io/dashboard) (500
credits, no card) before configuring any of these.

**Read this before copying a snippet:** clients disagree on whether `${VAR}`
in a config file expands to your shell environment or gets passed through
*literally* as the value. Passed through literally, the server still starts
and still advertises all 21 tools — it just fails every call with an auth
error, which is a confusing way to discover the mistake. Each section below
says which is safe. When unconfirmed, the snippet uses a literal placeholder
— paste your real key in place of it, don't leave `${ANAKIN_API_KEY}` unless
that client is listed as expanding it.

| Client | Config file | `${VAR}` expands? |
|---|---|---|
| [Windsurf](#windsurf) | `~/.codeium/windsurf/mcp_config.json` | Yes (`${env:VAR}`) |
| [Cline](#cline) | via extension UI → `cline_mcp_settings.json` | **No** — literal only |
| [JetBrains AI Assistant](#jetbrains-ai-assistant) | via Settings UI (no stable on-disk path) | Unconfirmed — literal only |
| [Goose](#goose) | `~/.config/goose/config.yaml` (YAML) | Unconfirmed — use `env_keys` or literal |
| [Kiro](#kiro) | `.kiro/settings/mcp.json` (project) / `~/.kiro/settings/mcp.json` (global) | Yes, but gated behind an approved-vars allowlist |
| [LM Studio](#lm-studio) | `~/.lmstudio/mcp.json` | Unconfirmed — literal only |
| [Amp](#amp) | `~/.config/amp/settings.json` (user) / `.amp/settings.json` (workspace) | Yes |
| [Augment Code](#augment-code) | Settings panel → "Import from JSON" (no stable on-disk path) | Unconfirmed — literal only |
| [Qwen Coder](#qwen-coder) | `~/.qwen/settings.json` (user) / `.qwen/settings.json` (project) | Yes (`$VAR` or `${VAR}`) |
| [OpenCode](#opencode) | `~/.config/opencode/opencode.json` (user) / `opencode.json` (project) | Yes, but syntax is `{env:VAR}`, **not** `${VAR}` |
| [Zencoder](#zencoder) | `zencoder.mcpServers` in VS Code/JetBrains `settings.json` | Unconfirmed — literal only |
| [Trae](#trae) | `.trae/mcp.json` (project) or Settings → MCP | Unconfirmed — literal only |
| [Raycast](#raycast) | in-app "Install MCP Server" / paste JSON | Unconfirmed — literal only |

Not in this table — handled differently, see [Platforms with no snippet](#platforms-with-no-snippet):
**Zed** (needed a compiled extension, not a config snippet — built, see
`blueprint-scribe-35/external-integrations/zed/`), **Replit** (stdio isn't
supported at all — needs a remote endpoint, doc + install-link built),
**Conductor** (nothing to ship — it delegates to whichever host agent, e.g.
Claude Code, is already covered), **Roo Code** (discontinued, not pursuing).

---

## Windsurf

`~/.codeium/windsurf/mcp_config.json` — edit directly, or via Cascade's
"Manage MCP Servers" → "View raw config". Restart Windsurf after saving.

```json
{
  "mcpServers": {
    "anakin": {
      "command": "npx",
      "args": ["-y", "@anakin-io/mcp@0.2.1"],
      "env": { "ANAKIN_API_KEY": "${env:ANAKIN_API_KEY}" }
    }
  }
}
```

Cascade caps active tools at 100 across *all* configured servers — fine for
this 21-tool server alone, but worth knowing if the user stacks several.

## Cline

Open the MCP Servers icon → Installed → Configure (don't hand-edit the
backing file directly; its path moves between extension versions).

```json
{
  "mcpServers": {
    "anakin": {
      "command": "npx",
      "args": ["-y", "@anakin-io/mcp@0.2.1"],
      "env": { "ANAKIN_API_KEY": "YOUR_ANAKIN_API_KEY" },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

`${VAR}` is **not** expanded (open feature request, [cline#5147](https://github.com/cline/cline/discussions/5147)) —
paste the literal key. Cline also has a real, submittable directory; see
[docs/submissions/cline.md](submissions/cline.md).

## JetBrains AI Assistant

Settings → Tools → AI Assistant → Model Context Protocol (MCP) → add server.
The dialog also has a "Command → As JSON" paste option accepting this shape:

```json
{
  "mcpServers": {
    "anakin": {
      "command": "npx",
      "args": ["-y", "@anakin-io/mcp@0.2.1"],
      "env": { "ANAKIN_API_KEY": "YOUR_ANAKIN_API_KEY" }
    }
  }
}
```

Requires AI Assistant 251.26094.80.5+. `${VAR}` interpolation isn't
documented — paste the literal key. No submission channel exists;
`plugins.jetbrains.com` only accepts full IDE plugins, not MCP manifests.

## Goose

`~/.config/goose/config.yaml` — **YAML**, not JSON. Edit directly or via
`goose configure`.

```yaml
extensions:
  anakin:
    type: stdio
    name: anakin
    enabled: true
    cmd: npx
    args: ["-y", "@anakin-io/mcp@0.2.1"]
    envs:
      ANAKIN_API_KEY: YOUR_ANAKIN_API_KEY
    timeout: 300
```

Goose's documented secrets pattern is `env_keys` pulling from its keyring
rather than inline values — if the user has that set up, `envs` can be
dropped in favor of `env_keys: [ANAKIN_API_KEY]`. Plain `envs` with a literal
value is the simpler default. `type: stdio` is required, not inferred.

## Kiro

Project: `.kiro/settings/mcp.json`. Global: `~/.kiro/settings/mcp.json`
(workspace wins on merge). Also has an "Add to Kiro" one-click deeplink:
`https://kiro.dev/launch/mcp/add?name=anakin&config=<url-encoded-JSON>`.

```json
{
  "mcpServers": {
    "anakin": {
      "command": "npx",
      "args": ["-y", "@anakin-io/mcp@0.2.1"],
      "env": { "ANAKIN_API_KEY": "${ANAKIN_API_KEY}" },
      "disabled": false,
      "autoApprove": [],
      "disabledTools": []
    }
  }
}
```

`${VAR}` expands, but **only for variables added to Kiro's "MCP Approved Env
Vars" setting** — an unapproved variable pops a warning rather than expanding
silently, which is a safer failure mode than most clients but still means
`ANAKIN_API_KEY` needs to be added there once before the snippet above works.

## LM Studio

`~/.lmstudio/mcp.json` — edit via right sidebar → Program tab → Install →
Edit mcp.json, or hand-edit directly (auto-reloads on save).

```json
{
  "mcpServers": {
    "anakin": {
      "command": "npx",
      "args": ["-y", "@anakin-io/mcp@0.2.1"],
      "env": { "ANAKIN_API_KEY": "YOUR_ANAKIN_API_KEY" }
    }
  }
}
```

LM Studio's official docs only show remote (`url`/`headers`) examples; the
`command`/`args`/`env` shape above follows the same convention every other
stdio client uses but isn't verified against an LM-Studio-specific official
example. Also has an "Add to LM Studio" deeplink:
`lmstudio://add_mcp?name=anakin&config=<base64-JSON>`.

## Amp

User: `~/.config/amp/settings.json`. Workspace: `.amp/settings.json`
(overrides user). Or via CLI: `amp mcp add anakin -- npx -y @anakin-io/mcp@0.2.1`.

```json
{
  "amp.mcpServers": {
    "anakin": {
      "command": "npx",
      "args": ["-y", "@anakin-io/mcp@0.2.1"],
      "env": { "ANAKIN_API_KEY": "${ANAKIN_API_KEY}" },
      "disabled": false
    }
  }
}
```

Note the key is `amp.mcpServers`, not `mcpServers` — dropping the `amp.`
prefix silently produces an empty server list rather than an error.

## Augment Code

Settings panel → MCP → "Import from JSON" (no confirmed on-disk file to
hand-edit; go through the panel).

```json
{
  "mcpServers": {
    "anakin": {
      "command": "npx",
      "args": ["-y", "@anakin-io/mcp@0.2.1"]
    }
  }
}
```

Augment's panel handles the API key as a separate field rather than an inline
`env` value — set `ANAKIN_API_KEY` there after importing the JSON above.
Augment's "Easy MCP" one-click list is curated by their team with no public
submission form; getting Anakin added there means contacting Augment
directly, not a self-serve PR.

## Qwen Coder

User: `~/.qwen/settings.json`. Project: `.qwen/settings.json` (wins).

```json
{
  "mcpServers": {
    "anakin": {
      "command": "npx",
      "args": ["-y", "@anakin-io/mcp@0.2.1"],
      "env": { "ANAKIN_API_KEY": "${ANAKIN_API_KEY}" },
      "timeout": 600000,
      "trust": false
    }
  }
}
```

Both `$VAR` and `${VAR}` expand. Qwen Coder's extension system can also
ingest a Claude Code plugin marketplace or the Gemini CLI Extensions Gallery
directly — since this repo is already both, no separate Qwen-specific package
is needed beyond this snippet.

## OpenCode

User: `~/.config/opencode/opencode.json`. Project: `opencode.json` (nearest
git root wins, merges with user config).

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "anakin": {
      "type": "local",
      "command": ["npx", "-y", "@anakin-io/mcp@0.2.1"],
      "enabled": true,
      "environment": {
        "ANAKIN_API_KEY": "{env:ANAKIN_API_KEY}"
      }
    }
  }
}
```

Two things that break if you paste a Claude-Desktop-style config here
instead: `command` is a single array (`["npx", "-y", ...]`), not separate
`command`/`args` fields, and env interpolation syntax is `{env:VAR}` —
`${VAR}` is not recognized and would pass through literally.

## Zencoder

`zencoder.mcpServers` key in VS Code or JetBrains `settings.json` (same
backing config for both), or via the in-IDE "Agent Tools" menu.

```json
{
  "zencoder.mcpServers": {
    "anakin": {
      "command": "npx",
      "args": ["-y", "@anakin-io/mcp@0.2.1"],
      "env": { "ANAKIN_API_KEY": "YOUR_ANAKIN_API_KEY" }
    }
  }
}
```

`zencoder.ai/marketplace` lists MCP servers but Zencoder's own launch post
frames third-party submission as a future feature, not live today — no
self-serve path found; would need to contact them directly.

## Trae

Project: `.trae/mcp.json` (auto-loaded with a trust warning), or Settings →
MCP → "Add Manually".

```json
{
  "mcpServers": {
    "anakin": {
      "command": "npx",
      "args": ["-y", "@anakin-io/mcp@0.2.1"],
      "env": { "ANAKIN_API_KEY": "YOUR_ANAKIN_API_KEY" }
    }
  }
}
```

Trae has a curated in-app "MCP Marketplace" with no documented third-party
submission process, and explicitly disclaims reviewing third-party servers.

## Raycast

"Install MCP Server" / "Manage MCP Servers" in Raycast, or paste JSON
directly (⌘N). Native support since v1.98.0, no extension wrapper needed.

```json
{
  "anakin": {
    "command": "npx",
    "args": ["-y", "@anakin-io/mcp@0.2.1"],
    "env": { "ANAKIN_API_KEY": "YOUR_ANAKIN_API_KEY" }
  }
}
```

Note this is a flat object, not wrapped in `mcpServers` — Raycast's own paste
UI only shows the per-server object. iOS Raycast only supports HTTP
transport, not stdio. There's a community-run registry extension (not
official Raycast Store) for discovery — see
[docs/submissions/raycast.md](submissions/raycast.md).

---

## Platforms with no snippet

**Zed** reads MCP servers (`context_servers` in `settings.json`) only for
manual/local use — one-click discovery inside Zed requires shipping a
compiled Rust/WASM extension via `zed_extension_api`, not a config snippet.
Built: `blueprint-scribe-35/external-integrations/zed/` — compiles clean
against the real `zed_extension_api` 0.7.0 and produces an actual
`wasm32-wasip1` binary (verified locally), ready to push as its own repo and
submodule into `zed-industries/extensions`. Not yet tested inside a real Zed
instance — see that directory's `SUBMIT.md`.

**Replit** doesn't support stdio MCP servers from external integrations at
all — every registration path (Integrations pane, install-link badges) needs
a remote HTTPS endpoint. `mcp.anakin.io` (the existing hosted OAuth server
from `anakin-mcp-remote`) is that endpoint. Registration doc + a working
install-link (base64-encoded config, round-trip verified) at
`anakin-mcp/directory-submissions/replit/SUBMIT.md`.

**Conductor** has no MCP config of its own — it runs sessions of an
underlying agent (Claude Code, Codex, or Cursor Composer) and reads whatever
MCP config that agent already has. Anakin is already installed for Claude
Code, Codex, and Cursor via this repo's plugin manifests, so Conductor users
on any of those three already have it; nothing to build.

**Roo Code** shut down May 15, 2026 — the extension is discontinued and its
GitHub repo is archived. Not pursuing. Displaced users are pointed by the
Roo Code team toward Cline, which already has a snippet above.
