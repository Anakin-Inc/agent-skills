# ChatGPT Apps manifest — tools-only

Deliberately scoped to **tools only, no custom UI** — OpenAI's own submission
guidelines note screenshots aren't needed for plugins without UI, and that
iframe/UI-based plugins get extra manual review and are "often not approved
for broad distribution." Anakin's tools (scrape/search/wire results, etc.)
don't need a rendered widget, so skipping UI entirely is both simpler to
build and more likely to clear review.

`plugin.json` follows this repo's existing per-platform convention (same
shape as `.codex-plugin/plugin.json`). `.app.json` points at the same live
remote MCP server (`https://mcp.anakin.io/mcp`, OAuth 2.1 + Dynamic Client
Registration) that the Claude Connectors Directory packet uses — see
`anakin-mcp-remote/compliance/LISTING.md` for the full metadata this reuses.
Confirmed live directly: `/healthz` → 200, `/.well-known/oauth-protected-resource`
→ real production auth server (`https://anakin.io`), `/mcp` unauthenticated →
401. No first-time deployment needed.

## Not confirmed

OpenAI's public Apps SDK docs and submission guidelines don't document an
exact schema for the "Upload plugin" button in the submission portal — the
`.app.json` shape here (`mcp.server_url` / `transport` / `auth` block) is a
best-effort construction from the build docs at
developers.openai.com/plugins/build/plugins, not a verified-working example.

That page also describes a prerequisite: registering the MCP server in
**ChatGPT Developer Mode** first to get a `plugin_asdk_app...` ID, before a
manifest like this can reference it — this may mean `.app.json` needs that
ID rather than a direct server URL. That registration step is account-gated
and can only be done by whoever owns the Anakin ChatGPT developer account.

**Next real step:** try uploading `plugin.json` as-is. If it errors, the
exact error message (missing field, wrong shape, or a prompt to register the
MCP server first) will say precisely what's actually expected — much more
reliable than continuing to guess from docs.
