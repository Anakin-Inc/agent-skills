---
name: anakin-browser
description: Use when a task needs a real browser driven step by step — multi-step flows, clicking and typing, complex navigation that scrape cannot handle — or when reaching login-protected content with a saved browser session. Covers browser_task, session_list, session_delete, and how sessionId works with scrape, crawl, and monitors.
---

# Anakin: browser automation and saved sessions

Two related capabilities: driving a real cloud browser with natural language,
and reusing saved login state so any tool can reach protected pages.

## browser_task — the last resort, not the first

An AI agent drives a real cloud browser: navigating, clicking, typing,
scrolling, extracting. Async, up to ~5 minutes, polls to completion.

**Check cheaper options first, in this order:**

1. `scrape` — one page, static content
2. `scrape` with `useBrowser: true` — one page, JS-rendered
3. `wire_discover` — is there a pre-built action? **Wire actions are faster and
   cheaper than driving a browser**
4. `browser_task` — only when the task is genuinely multi-step or interactive
   and nothing above covers it

Use it for: multi-step flows, form filling, interactions behind clicks, and
navigation too complex to express as a URL.

### Parameters

- `prompt` (required) — the task in natural language. Be specific about what to
  extract or do.
- `url` — where to start.
- `output_schema` — **supply this whenever you know the shape you want.** It is
  the difference between prose you must re-parse and structured JSON.
- `session_id` — for login-protected tasks (below).
- `max_steps`, `timeout_ms` — bound long-running tasks.

Returns the result plus run metadata (steps taken, duration, `run_id`).

### Two hard rules

- **Never put passwords in the `prompt`.** Use `session_id`. A prompt is not a
  credential store.
- It does not execute payments or transfer funds; such tasks are refused. Do not
  attempt to work around this.

Tell the user before starting — several minutes of silence otherwise reads as a
hang.

## Saved browser sessions

A session is encrypted login state captured through the Anakin dashboard or
Browser API. Its `id` is what you pass as `sessionId` to reach protected content
from **any** of these:

| Tool | Parameter |
|---|---|
| `scrape`, `crawl` | `sessionId` (pair with `useBrowser: true`) |
| `monitor_create` | `sessionId` |
| `browser_task` | `session_id` |

- `session_list` — your saved sessions, optionally filtered by `domain`. Call
  this first to find an id.
- `session_delete` — permanently deletes a session and its encrypted login data.

### When no session exists

**You cannot create one from here.** The user must log in once interactively in
the Anakin dashboard — that flow handles 2FA and captchas. Say so plainly and
point them there rather than attempting a login through `browser_task`.

### Before deleting

`session_delete` is **irreversible**. The user must log in again through the
dashboard to recreate it, and **any monitors or requests referencing that
`sessionId` lose authenticated access** — a monitor may keep running and silently
start recording logged-out content. Check `monitor_list` for dependents and
confirm with the user before deleting.
