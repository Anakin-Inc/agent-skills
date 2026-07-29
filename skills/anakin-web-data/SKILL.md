---
name: anakin-web-data
description: Use when fetching content from the web with Anakin — reading a page, getting a site's URL structure, or bulk-collecting many pages. Covers scrape, map, and crawl, and routes to the right Anakin tool for a task. Triggers on scraping a URL, extracting page content as markdown, listing a site's pages, ingesting a site, building a corpus from a domain, or handling JS-heavy/SPA pages.
---

# Anakin: fetching web data

## Pick the right tool first

Anakin has twenty-one tools across five groups. Choosing wrong is the most
common and most expensive mistake — check this table before calling anything.

| The task | Tool | Skill |
|---|---|---|
| Read one known URL | `scrape` | this one |
| Find what pages exist on a site | `map` | this one |
| Collect many pages from one site | `crawl` | this one |
| Find pages across the web for a query | `search` | `anakin-research` |
| Answer a question needing many sources | `agentic_search` | `anakin-research` |
| See what AI engines say about something | `ai_visibility_search` | `anakin-research` |
| Extract data from a *specific popular site* | `wire_discover` → `wire_read_action` | `anakin-wire` |
| Submit a form, add to cart, post content | `wire_discover` → `wire_write_action` | `anakin-wire` |
| Watch a page for changes over time | `monitor_create` | `anakin-monitoring` |
| Multi-step interaction no Wire action covers | `browser_task` | `anakin-browser` |
| Reach login-protected content | `session_list` → pass `sessionId` | `anakin-browser` |

**Check Wire before reaching for `scrape` or `crawl` on a well-known site.**
Amazon, Walmart, LinkedIn, Airbnb, Zillow and hundreds more have vetted,
pre-built extractors that return clean structured data in one call. Scraping
those sites by hand is slower, costs more, and gives you markdown you then have
to parse. See the `anakin-wire` skill.

**Escalate in cost order.** `scrape` → `scrape` with `useBrowser` → a Wire
action → `browser_task`. Each step is slower and more expensive than the last;
do not start at the end.

## scrape — one URL to markdown

Default behavior returns clean markdown. That is the right default; do not add
options reflexively.

- `generateJson: true` — also run AI extraction and return typed fields. Use for
  product pages, listings, articles — anywhere you want structured values rather
  than prose. Returns the JSON as the primary output.
- `useBrowser: true` — render with a stealth headless browser. **Slower and more
  expensive.** Only for SPAs and JS-rendered content. Try the default first; if
  the markdown comes back empty or is missing the content you can see in a
  browser, retry with `useBrowser: true`.
- `country` — two-letter proxy egress code, defaults to `"us"`. Set it when a
  page is geo-restricted or price/inventory varies by market (`"de"`, `"in"`, …).
- `forceFresh: true` — skip the cache. Results cache for roughly 24h, which is
  usually what you want. Only force fresh for genuinely live data (stock levels,
  prices you are about to act on).
- `sessionId` / `sessionName` — a saved browser session for login-protected
  pages. Pair with `useBrowser: true`.

## map — discover a site's URLs

Returns internal links, external links, and counts. Use it to understand
structure *before* crawling, so the crawl is scoped instead of blind.

- `limit` (default 100, max 1000) — total URLs returned.
- `depth` (default 2, max 5) — link-hops followed.
- `limitPerLevel` (default 100) — breadth cap per level.
- `search` — keyword filter on path/title. Cheap way to find the section you
  care about without crawling everything.
- `includeSubdomains`, `includeExternalLinks` — both default false.

## crawl — bulk markdown from a site

For catalog ingestion or building a RAG corpus. Returns an array of pages, each
with markdown and its own status — **check per-page status**, since a crawl can
partially succeed.

- `maxPages` (default 10, max 500) — a hard cap, and the main cost lever.
- `depth` (default 1, max 5).
- `includePatterns` / `excludePatterns` — glob/regex URL filters. Use these.
  An unscoped crawl burns credits on nav pages, tag archives, and pagination.

## Working pattern

For anything beyond a single page, `map` first, then `crawl` the subset:

1. `map` the domain with a `search` filter to see what exists.
2. Derive `includePatterns` from the URLs that matter.
3. `crawl` with those patterns and a deliberate `maxPages`.

This is consistently cheaper and cleaner than crawling from the homepage and
filtering afterward.

## Cost and failure notes

- `useBrowser` is the biggest cost multiplier — leave it off unless the page
  needs it.
- Every tool returns an error envelope rather than throwing. On failure, read
  the message: it names the tool and the cause.
- API key comes from `ANAKIN_API_KEY`. Get one at https://anakin.io/dashboard —
  free tier is 300 credits, no card.
