---
name: anakin-monitoring
description: Use when the user wants to watch a web page, site, or Wire action for changes over time rather than fetch it once — price drops, stock or status changes, competitor page edits, new listings, content diffs, or scheduled checks with webhook/email alerts. Covers monitor_create, monitor_list, monitor_changes, monitor_control.
---

# Anakin: website monitoring

Scheduled checks that record a change when watched content differs from the
previous run, optionally alerting a webhook or email.

**Use this instead of re-scraping on a loop.** If the user says "tell me when",
"watch for", "alert me if", or "track over time", that is a monitor — not a
repeated `scrape`.

## Creating a monitor

`monitor_create` requires `url` and `intervalMinutes` (**minimum 15**).

### Scope — what gets watched

- `"page"` (default) — one URL.
- `"site"` — crawls the site each run and tracks pages added, removed, changed.
  Scope it with `maxPages`, `maxDepth`, `includePatterns`, `excludePatterns`.
- `"wire"` — runs a Wire action each check and diffs its JSON. Pass
  `wireActionId` (or `wireCatalogSlug`), `wireParams`, `wireCredentialId`, and
  `wireWatchPaths` to watch specific fields.

### Watch mode — this is the cost lever

- `"full_page"` — **2 credits/check**, compares the whole page.
- `"specific_data"` — **3 credits/check**, extracts only the fields in
  `outputSchema` with AI.

`specific_data` costs more per check but is usually the right choice for price,
stock, or status tracking: `full_page` fires on any incidental edit, so you pay
for checks *and* wade through noise. Define an `outputSchema` with just the
fields that matter.

`aiMode` adds **+1 credit/check** and filters trivial noise, summarizing real
changes. Worth it on pages that churn.

### Cost arithmetic before you create

Credits/day = `(1440 / intervalMinutes) x per-check cost`. A 15-minute
`specific_data` monitor with `aiMode` is `96 x 4 = 384 credits/day`. **Compute
this and tell the user before creating** — a short interval on a high-cost mode
is an easy way to burn a plan.

**Active-monitor caps: Free 5, Pro 20, Scale 100.**

### Other options

`alertWebhookUrl`, `alertEmails`, `useBrowser`, `country`, `sessionId` (for
login-protected pages — see `anakin-browser`), `expiresAt`, `isActive`.

## Managing monitors

- `monitor_list` — all monitors, or pass `id` for one monitor's full config and
  status (next/last check, active state, per-check cost, alerts). **Call this
  first** to get an id.
- `monitor_changes` — the detected changes for a monitor id, each with a
  diff/summary (plus the AI summary when `aiMode` is on).
- `monitor_control` — `"pause"`, `"resume"`, `"run_now"`, `"delete"`.
  - `resume` may hit the plan's active-monitor cap.
  - `run_now` is billed like a normal check.
  - **`delete` permanently removes the monitor and its entire history.** Confirm
    with the user first; there is no undo.

## Working pattern

1. `scrape` the URL once to confirm the data is actually there and stable.
2. Decide `watchMode` from what the user cares about — define `outputSchema` for
   `specific_data`.
3. Pick the longest `intervalMinutes` that still meets the need.
4. State the credits/day, then `monitor_create`.
5. Report the monitor id back so the user can manage it later.
