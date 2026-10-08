# Anakin Agent Skills

Agent skills and MCP server packaging for [Anakin](https://anakin.io) — web
scraping, search, crawling, deep research, and Wire actions across hundreds of
popular websites.

This repository is the plugin distribution for Anakin. It is packaged for
multiple agent platforms from a single source of truth.

## Install

### Claude (claude.ai, Cowork, Claude Code)

Add **Anakin** from the directory in Claude, or in Claude Code from this
repository's marketplace:

```
/plugin marketplace add Anakin-Inc/agent-skills
/plugin install anakin
```

The Claude plugin connects to Anakin's hosted MCP server at
`https://mcp.anakin.io/mcp`. The first time a tool runs, Claude opens an Anakin
sign-in page. Sign in or create an account and approve access; there is no API
key to copy. In Claude Code, run `/mcp` and select `anakin` to sign in ahead of
time.

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

The Claude plugin signs in over OAuth and needs no key. Every other platform
runs the local server, which needs one.

**Set this before using the plugin outside Claude.** All tools require an Anakin
API key in `ANAKIN_API_KEY`. Get one free at
[anakin.io/dashboard](https://anakin.io/dashboard) — 300 credits, no card
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

**MCP server** — the Claude plugin uses the hosted server at
`https://mcp.anakin.io/mcp` (twenty-two tools). Every other platform runs
[`@anakin-io/mcp`](https://github.com/Anakin-Inc/anakin-mcp) locally
(twenty-one tools; it lacks `wire_build_status`). Both call `api.anakin.io`.

**Skills** — guidance on choosing and sequencing those tools:

| Skill | Covers |
|---|---|
| `anakin-web-data` | `scrape`, `map`, `crawl` — fetching pages and sites |
| `anakin-research` | `search`, `agentic_search`, `ai_visibility_*` — finding, synthesizing, and comparing AI answers |
| `anakin-wire` | the `wire_*` family — pre-built read and write actions on known sites |
| `anakin-monitoring` | `monitor_*` — scheduled change detection with alerts |
| `anakin-browser` | `browser_task`, `session_*` — driving a real browser and reusing login state |

## What this plugin runs and sends

The plugin is five skills (Markdown instructions) and one MCP server entry. It
has no hooks, commands, agents or scripts, and nothing in it runs on your
machine.

- **Where data goes.** The Claude plugin connects only to
  `https://mcp.anakin.io/mcp`, which calls `api.anakin.io`. The local server on
  other platforms calls `api.anakin.io` directly.
- **What is sent.** The arguments of each tool call you or Claude make: URLs,
  search queries, extraction schemas, Wire action inputs, monitor settings and
  browser-task instructions. Anakin then fetches the pages or runs the actions
  you asked for on the public web or on the sites you target.
- **Sign-in.** The Claude plugin signs in with your Anakin account over OAuth
  2.1. Anakin creates an API key scoped to your account for that connection and
  stores it encrypted. Claude never sees your Anakin password or the key.
- **Third-party logins.** Only if you use `wire_login`, or pass a `credential`
  to `wire_build`, do you send login details for one of your own accounts on
  another site. Anakin keeps an encrypted session, not the password. You can
  remove saved sessions in the [Anakin dashboard](https://anakin.io/dashboard).
  `browser_task` accepts no credentials.
- **Monitors.** If you create a monitor, Anakin stores the webhook URL or email
  addresses you give it and sends change alerts there.
- **AI Visibility.** `ai_visibility_search` sends your query to the AI answer
  engines you choose, such as ChatGPT, Gemini or Google AI Overview, to compare
  their answers.
- **Actions that change things.** `wire_write_action`, `wire_login`,
  `wire_build`, `monitor_create`, `monitor_control`, `session_delete` and
  `browser_task` are marked destructive, so Claude asks before each call. The
  hosted server refuses payment-style Wire actions.
- **What it never touches.** The server does not read your Claude chats,
  memory or files, and Anakin does not train models on your inputs or results.

Tool calls spend Anakin credits; see [pricing](https://anakin.io/pricing). Full
details are in the
[privacy policy](https://anakin.io/connector-privacy).

## Versioning

The Claude plugin uses the hosted server, which Anakin deploys and versions
itself, so there is nothing to pin. Every other platform runs the local server,
and for those the plugin pins an exact version (`@anakin-io/mcp@0.2.1`) rather
than tracking `@latest`.

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
.mcp.json                  local MCP server definition (Grok, Codex, Copilot)
mcp.json                   local MCP server definition (Cursor)
gemini-extension.json      Gemini CLI manifest (inlines its own MCP block)
.claude-plugin/            Claude plugin + marketplace manifests; plugin.json
                           points `anakin` at the hosted server, overriding .mcp.json
.grok-plugin/              Grok manifest
.cursor-plugin/            Cursor manifest
.codex-plugin/             Codex manifest (shared with ChatGPT -- same universal plugin directory)
.agents/plugins/           Codex marketplace index
.github/plugin/            Copilot CLI + VS Code manifest
assets/                    logo
```

The `skills/` directory is shared. Each platform directory holds only a
manifest — the skills themselves are written once and never duplicated.

The local MCP server definition exists under two filenames because the
platforms disagree on the convention: Grok reads `.mcp.json`, Cursor discovers
`mcp.json` at the plugin root. The contents are identical and must be kept in
sync.

Claude also loads `.mcp.json`, then applies the `mcpServers` block in
`.claude-plugin/plugin.json`. Because both name the server `anakin`, the hosted
entry replaces the local one instead of adding a second server.
`scripts/validate.py` fails if the names drift apart.

## License

Apache-2.0. See [LICENSE](LICENSE).
