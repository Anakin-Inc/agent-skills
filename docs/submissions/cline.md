# Cline MCP Marketplace — submission draft

Cline is the one client in [docs/CLIENTS.md](../CLIENTS.md) with a real,
submittable, third-party directory: [github.com/cline/mcp-marketplace](https://github.com/cline/mcp-marketplace).
Submission is a GitHub issue against that repo using their
`mcp-server-submission.yml` template — not a PR, and not something this repo
can do on its own behalf. This file is the content to paste into that issue;
filing it is a manual step for whoever owns the Anakin GitHub presence.

## Blocking on: a 400×400 PNG logo

The template requires a 400×400 PNG. This repo only has SVGs
(`assets/logo.svg`, `assets/logo-square.svg` — the latter is already the
right 1:1 aspect ratio with an opaque background plate, from the Cursor
submission). No SVG rasterizer was available in this environment to convert
it. Before filing: export `assets/logo-square.svg` to a 400×400 PNG (e.g.
Figma, or `rsvg-convert -w 400 -h 400 assets/logo-square.svg -o logo-400.png`
on a machine that has it installed) and attach it to the issue.

## Issue content

**Repository URL:** `https://github.com/Anakin-Inc/anakin-mcp`

**Server name:** Anakin

**Short description:** Web scraping, search, crawling, deep research, and
pre-built Wire actions across hundreds of popular websites — 21 tools over
`api.anakin.io`.

**Category:** Web / Data

**Why it should be included:**
Anakin gives coding agents structured access to the live web without a
custom scraper: `scrape`/`map`/`crawl` turn any page or site into clean
markdown or structured JSON, `search`/`agentic_search` run AI-native search
and multi-source research, the `wire_*` family executes pre-built read/write
actions on hundreds of known sites (so the agent doesn't have to reverse-
engineer each site's DOM), `monitor_*` watches pages for changes on a
schedule, and `browser_task` drives a real cloud browser from natural
language for anything scraping alone can't reach. Full tool list in
[`@anakin-io/mcp`](https://github.com/Anakin-Inc/anakin-mcp)'s `server.json`.

**Install command (for the issue body / README they'll check):**

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

**Auth:** free API key at [anakin.io/dashboard](https://anakin.io/dashboard),
500 credits, no card required.

**Maturity signal:** already shipped and reviewed for Claude Code, Cursor,
OpenAI Codex, Grok, Gemini CLI, and GitHub Copilot via this same repo
(`Anakin-Inc/agent-skills`) — link that repo in the issue as evidence this
isn't a first-time/unmaintained submission.
