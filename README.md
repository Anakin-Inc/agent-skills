# Anakin Agent Skills

Agent skills and MCP server packaging for [Anakin](https://anakin.io) — web
scraping, search, crawling, deep research, and Wire actions across hundreds of
popular websites.

This repository is the plugin distribution for Anakin. It is packaged for
multiple agent platforms from a single source of truth.

## Install

### Claude Code

```
/plugin marketplace add Anakin-Inc/agent-skills
/plugin install anakin
```

### Grok

Browse the plugin marketplace and install `anakin`.

### Cursor

```
/add-plugin anakin
```

### Gemini CLI

```
gemini extensions install https://github.com/Anakin-Inc/agent-skills
```

### OpenAI Codex

```
codex plugin marketplace add Anakin-Inc/agent-skills
codex plugin install anakin
```

### Any MCP client

The skills wrap the published MCP server, which works standalone:

```
npx -y @anakin-io/mcp@latest init --all
```

This path tracks `@latest` because it is a direct install you control. The
plugin itself pins an exact version — see [Versioning](#versioning).

## API key

**Set this before using the plugin.** All tools require an Anakin API key in
`ANAKIN_API_KEY`. Get one free at
[anakin.io/dashboard](https://anakin.io/dashboard) — 500 credits, no card
required.

The plugin deliberately ships **no `env` block**. The server inherits your
client's environment, so set `ANAKIN_API_KEY` wherever that client reads
environment variables from.

This is a correctness choice, not an omission. A config containing
`"ANAKIN_API_KEY": "${ANAKIN_API_KEY}"` breaks on any client that does not
expand `${VAR}`: the literal string is passed through, the server accepts it as
a key, and it starts and advertises all twenty-one tools — every call then fails at
the API. Without an `env` block a missing key instead stops the server
immediately with a message naming the variable and where to get one. Failing
loudly at startup beats failing confusingly mid-task.

## What's included

**MCP server** — [`@anakin-io/mcp`](https://github.com/Anakin-Inc/anakin-mcp),
twenty-one tools over `api.anakin.io`.

**Skills** — guidance on choosing and sequencing those tools:

| Skill | Covers |
|---|---|
| `anakin-web-data` | `scrape`, `map`, `crawl` — fetching pages and sites |
| `anakin-research` | `search`, `agentic_search`, `ai_visibility_*` — finding, synthesizing, and comparing AI answers |
| `anakin-wire` | the `wire_*` family — pre-built read and write actions on known sites |
| `anakin-monitoring` | `monitor_*` — scheduled change detection with alerts |
| `anakin-browser` | `browser_task`, `session_*` — driving a real browser and reusing login state |

## Versioning

The plugin pins an exact MCP server version (`@anakin-io/mcp@0.2.1`) rather than
tracking `@latest`.

Marketplaces install this repository at a frozen commit SHA. A floating npm tag
would undermine that in two ways: the reviewed commit could execute code nobody
reviewed, and an upstream change to a tool signature would reach already-
installed users without a plugin release. Pinning makes every server upgrade a
deliberate, reviewable change here.

Upgrading is a two-line edit to `.mcp.json` and `mcp.json`, a version bump in the
three platform manifests, and a release. CI rejects floating tags and ranges.

The cost of pinning is staleness, so it is automated away: a weekly job compares
the pin against npm and opens an issue when a newer server is published,
including a one-liner that lists the new version's tools so a signature change
is caught before it reaches anyone. Pinning decides *when* users upgrade; it does
not mean nobody notices there is something to upgrade to.

## Repository layout

```
skills/                    source of truth for all platforms
.mcp.json                  MCP server definition (Claude, Grok)
mcp.json                   MCP server definition (Cursor)
gemini-extension.json      Gemini CLI manifest (inlines its own MCP block)
.claude-plugin/            Claude Code plugin + marketplace manifests
.grok-plugin/              Grok manifest
.cursor-plugin/            Cursor manifest
.codex-plugin/             Codex manifest
.agents/plugins/           Codex marketplace index
.github/plugin/            Copilot CLI + VS Code manifest
assets/                    logo
```

The `skills/` directory is shared. Each platform directory holds only a
manifest — the skills themselves are written once and never duplicated.

The MCP server definition exists under two filenames because the platforms
disagree on the convention: Claude and Grok read `.mcp.json`, Cursor discovers
`mcp.json` at the plugin root. The contents are identical and must be kept in
sync.

## License

Apache-2.0. See [LICENSE](LICENSE).
