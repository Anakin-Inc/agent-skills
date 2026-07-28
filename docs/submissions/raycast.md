# Raycast MCP registry — submission draft

Raycast's native MCP support (Install MCP Server / paste JSON) needs no
submission — see [docs/CLIENTS.md](../CLIENTS.md#raycast) for the direct
config. The extra step below is for *discoverability*: a community-run
registry extension surfaces third-party servers inside Raycast's own search.
This is **not** the official Raycast Store (that's for `@raycast/api`
extensions, not raw MCP servers) — it's a separate community project, PR-based.

## Before filing

The research behind this draft confirmed the registry's existence and that
it takes PRs, but did **not** verify the exact current shape of its entry
file — repo structure and field names can drift. Before opening a PR:

1. Check the current repo, likely `raycast/model-context-protocol-registry`
   (verify this is still the right name/owner — could not confirm live).
2. Find its entries file (likely `entries.ts` or similar) and match its
   actual current TypeScript interface — don't copy the shape below
   blind.

## Draft entry content

Field values to adapt into whatever shape the registry actually wants:

```
name: "Anakin"
description: "Web scraping, search, crawling, deep research, and pre-built
  Wire actions across hundreds of popular websites."
repository: "https://github.com/Anakin-Inc/anakin-mcp"
command: "npx"
args: ["-y", "@anakin-io/mcp@0.2.1"]
env:
  ANAKIN_API_KEY: "" # user-supplied — free at anakin.io/dashboard
category: "Web / Data"
```

As with the [Cline submission](cline.md), filing the actual PR is a manual
step for whoever owns the Anakin GitHub presence — this file is prep, not a
filed submission.
