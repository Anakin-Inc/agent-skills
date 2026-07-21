---
name: anakin-research
description: Use when answering a question from the web with Anakin rather than fetching a known URL — web search for relevant pages, multi-source deep research producing a structured answer, or checking what AI answer engines say about a brand or topic. Covers search, agentic_search, ai_visibility_search, ai_visibility_sources. Triggers on researching a topic, comparing options across sources, market or competitive intelligence, AI-SEO and brand visibility checks, finding sources for a claim, or gathering data that spans many sites.
---

# Anakin: search, research, and AI visibility

Three tools with very different cost and latency profiles. Picking the wrong one
either wastes minutes or returns something too shallow to use.

| Need | Tool | Latency |
|---|---|---|
| Find URLs relevant to a query | `search` | immediate |
| A researched answer synthesized from many sources | `agentic_search` | 1–5 min |
| What AI engines *say* about a topic or brand | `ai_visibility_search` | 1–2 min |

The third answers a different question from the other two. `search` and
`agentic_search` ask *what is true on the web*. `ai_visibility_search` asks
*what do AI assistants tell people* — which is a brand/AI-SEO question, not a
factual one. Do not substitute one for the other.

## search — find pages

Synchronous AI web search. Returns a results array of `url`, `title`, `snippet`,
`date`. No polling.

- `prompt` — natural-language query.
- `limit` (default 5, max 20).

This is a *discovery* tool. It returns snippets, not page content. The normal
pattern is `search` to find candidates, then `scrape` the ones worth reading
(see the `anakin-web-data` skill).

Use `search` when you will decide what to read, or when you need citations you
can hand back to the user.

## agentic_search — deep research

An async pipeline: it searches, scrapes the most relevant citations, and uses an
LLM to synthesize a unified structured answer. Typically 1–5 minutes.

- `prompt` — the research question. Be specific; the engine infers scope from it.
- `schema` — optional JSON Schema for the output shape. **Supply this whenever
  you know the shape you want** — it is the difference between prose you have to
  re-parse and typed data you can use directly. Omit it and the engine infers a
  schema from the prompt.
- `useBrowser` — defaults to `true` here, unlike other tools, because cited
  sources are often JS-heavy.

Returns `summary`, `structured_data`, and the `data_schema` actually used.

Use it when one URL or a flat list of search hits genuinely cannot answer the
question: comparative analysis, multi-jurisdictional research, market
intelligence, anything requiring synthesis across sources.

## ai_visibility_search — what AI engines say

Asks multiple AI answer engines (ChatGPT, Gemini, Google AI Overview) the same
question and compares their answers. Returns one result per engine — status,
answer summary, latency, credits, and a consensus/outlier verdict — plus an
AI-generated synthesis of where they agree and diverge. Async, typically 1–2
minutes, polls to completion.

- `query` (required) — the question to put to every engine.
- `sources` — engine slugs to query. Call `ai_visibility_sources` first to see
  what is available and currently enabled.
- `country` — for geo-specific AI answers.
- `include_full_content` — **leave this off by default.** Each engine's raw full
  answer is large; the summaries and synthesis are usually what you need.

Billed per source at that Wire action's rate. Failed sources are free.

Use it for: brand visibility ("what do AI engines say about X"), tracking how
answers differ across engines, and geo-specific answer checks.

`ai_visibility_sources` takes no arguments and just lists slugs plus display
labels. Call it when you want a subset rather than all engines.

## Choosing well

Do **not** reach for `agentic_search` when:

- The answer lives on one page you can already name → `scrape` it.
- You need a list of links → `search`.
- The data is on a specific popular site → check `wire_discover` first
  (`anakin-wire` skill); a pre-built action is faster and returns clean fields.
- The question is what *AI engines say* rather than what the web contains →
  `ai_visibility_search`.
- The user wants to be told when something *changes* → a monitor, not a repeated
  search (`anakin-monitoring`).

Do reach for it when a thorough answer would otherwise mean a dozen
`search` + `scrape` round-trips. It is doing exactly that work, better scoped.

## Practical notes

- Tell the user before starting an `agentic_search` — minutes of silence
  otherwise reads as a hang.
- Define a `schema` up front for anything feeding a table, report, or downstream
  code.
- Results can be served from cache (`cached` in the response); pass a more
  specific prompt if you need a genuinely fresh run.
