---
name: anakin-wire
description: Use when a task targets a specific well-known website — extracting products, listings, prices, profiles, reviews or dashboard data from sites like Amazon, Walmart, LinkedIn, Airbnb or Zillow, or performing an interaction there such as submitting a form, adding to a cart, or posting content. Covers Anakin's Wire catalog of pre-built actions - wire_discover, wire_catalog, wire_read_action, wire_write_action, wire_identities, wire_login, wire_build. Check this before hand-scraping any popular site.
---

# Anakin Wire: pre-built site actions

Wire is a catalog of vetted, pre-built automation actions across hundreds of
popular websites. An action returns clean structured data — not markdown you
have to parse.

## The single most important point

**Wire is not login-only.** Actions come in two kinds, and each has its own
execution tool:

- **READ** actions *extract data* and change nothing — search listings, fetch a
  category's products, get a product's price/specs/reviews, read a profile, pull
  dashboard metrics. Run with **`wire_read_action`**.
- **WRITE** actions *change state* — submit a form, add to a cart, post or send
  content, update account settings. Run with **`wire_write_action`**.

**Many read actions need no authentication at all.** If you assume Wire is only
for logins and skip it, you will hand-scrape sites that already have a one-call
extractor. For any task on a recognizable site, try `wire_discover` first.

## The loop

```
wire_discover (or wire_catalog)  →  check the action's type
                                      ├─ "read"  → wire_read_action
                                      └─ "write" → wire_write_action
                                            ↓ auth error only
                         wire_identities / wire_login → retry with credential_id
```

### 1. Find an action

- `wire_discover` — natural-language intent → ranked candidate actions. Pass `q`
  (e.g. `"top phones on walmart"`, `"search airbnb listings in Lisbon"`), and
  optionally `limit` (default 5). Returns each candidate's `action_id`, required
  and optional params, credit cost, and whether auth is needed.
- `wire_catalog` — browse instead of guess. No arguments lists every supported
  site and its action count. Pass a `slug` (`"walmart"`, `"amazon"`,
  `"linkedin"`) for that site's full action list with exact parameter schemas,
  each action's type (read/write), `auth_mode` (`none`/`optional`/`required`),
  credit cost, and login fields.

Use `wire_discover` when you know the intent, `wire_catalog` when you want to
see everything a site can do.

### 2. Run it — pick the tool that matches the action's type

Both take `action_id` plus `params` matching that action's schema, and both poll
the async job to completion for you. **Confirm the action's `type` from
discovery before choosing** — passing a write action to `wire_read_action` (or
the reverse) is an error, not a fallback.

- `wire_read_action` — for `type: "read"`. Most need no auth.
- `wire_write_action` — for `type: "write"`. Most *do* need auth.

Neither executes payments or transfers funds; such actions are refused.

### 3. Authenticate, only if the action demands it

If execution returns `AUTH_REQUIRED`, `AUTH_EXPIRED`, or `FORBIDDEN`, the error
text tells you what to do. In short:

- `wire_identities` — list saved identities and their credentials. Each
  credential's `id` is the `credential_id` you pass. Filter with `catalog_id`.
  **Check the credential's status is `active`, not `expired`.**
- `wire_login` — sign in to a credentials-mode site and get a usable
  `credential_id` immediately. Pass `catalog_slug` and `params` matching that
  catalog's `login_input_schema` (from `wire_catalog`). The password is never
  stored — only an encrypted session.

Not every site supports password sign-in. Cookie-based sites use the dashboard
connect flow instead; when that applies, the error includes a `connect_url` to
give the user.

Never invent credentials. Ask the user, or send them to the `connect_url`.

## When no action exists

`wire_build` requests a brand-new action: pass `website_url` and a specific
`goal` describing what to extract or do. Wire generates and auto-tests a
scraper, then publishes it.

- Async — returns `pending`.
- Charges credits, automatically refunded if the build fails.
- `visibility` defaults to `private`.
- Rejected with `ACTION_EXISTS` if similar actions exist; pass `force: true` to
  override.

**Only call this after `wire_discover` and `wire_catalog` confirm nothing
covers the site.** Building duplicates wastes credits and time.

## Choosing Wire vs. the alternatives

| Situation | Use |
|---|---|
| Recognizable site, want structured data | `wire_read_action` |
| Recognizable site, state-changing interaction | `wire_write_action` |
| Arbitrary/long-tail URL | `scrape` (`anakin-web-data`) |
| Whole-site ingestion | `crawl` (`anakin-web-data`) |
| Recognizable site, no action, recurring need | `wire_build`, then run it |
| Multi-step interaction, no action exists, one-off | `browser_task` (`anakin-browser`) |
| Need to watch an action's output over time | `monitor_create` with `scope: "wire"` (`anakin-monitoring`) |

Rule of thumb: if you could name the site to a colleague and they would
recognize it, check Wire before scraping it. Wire actions are faster and cheaper
than `browser_task` — always check `wire_discover` before driving a browser.
