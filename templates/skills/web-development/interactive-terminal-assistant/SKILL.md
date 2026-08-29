<!-- GENERICIZED: 1×{MODEL}, 1×{RELATIONSHIP} | source: skills/web-development/interactive-terminal-assistant/SKILL.md -->
---
name: interactive-terminal-assistant
description: Use when adding a terminal/CLI chatbot to a web page.
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
---

# Interactive Terminal Assistant

Embed an interactive terminal into a web page that responds to slash commands and/or talks to an LLM. Proven on a consulting marketing site's gateway (2026-08): the flagship "watch us work" proof-of-capability element.

## When to Use

- Adding a CLI-style terminal/console to a static site as a demo or assistant
- Wiring a terminal input to an LLM API
- Building interactive proof elements that demonstrate capability ("we can do the impossible")

## Architecture

1. **Static front + one serverless function.** The terminal lives in the page; LLM calls go to a single function (`api/ask.mjs` on Vercel) that holds the API key, enforces caps, and applies the system prompt server-side. The key NEVER ships to the browser or the repo. Crossing from pure-static to "static + one endpoint" is a deliberate boundary — keep the function in its own route group so the whole surface deletes with zero residue if the experiment dies.
2. **Slash vs raw dispatch, one input.** Input starting with `/` stays client-side command dispatch (nav, help, canned demos — zero network). Anything else POSTs to the function. The slash path keeps working even if the LLM endpoint dies — a resilience property of the static core.
3. **Showcase assistant, not the firm.** The system prompt explains what the company does, never gives advice/quotes/prices, never invents credentials or track-record numbers, and appends an honesty-guard line (e.g. "→ scheduled: intro call — we map this to your actual situation") ONLY when the user expresses genuine interest or asks for next steps — never unconditionally. An unconditional closing line made the model append it to EVERY answer, and the user flagged it as broken repetition ("the llm keeps saying 'scheduled: intro call'"). Informational questions should end with a suggestion ("Try /digital or /physical to explore"). The terminal's canned-demo honesty guard becomes the model's prompt spine, but conditional. An unauthenticated bot answering AS the firm is a brand liability; a showcase assistant is a differentiator.

## UX / interaction rules (user-verified)

- **Click = focus/type; navigation lives only on explicit CTA anchors.** A clickable terminal panel that also navigates traps users (accidental entry). Make the terminal click focus the input (`stopPropagation` + `preventDefault`), and make the "Enter" text a styled `<a>` with hover states — the instrument and the door are separate surfaces.
- **Data-driven command map (single source of truth).** Define commands as an array of `{cmds:[...aliases], action, target, label}` records; build BOTH the dispatch lookup AND the `/help` output from the same array, so the "command works but help doesn't list it" drift is structurally impossible. Group aliases (`/home`, `/back`, `/reset` → one action) in a single record. Mounts take a `commands` config so the landing terminal and inner-page terminals can expose different command surfaces while sharing the LLM path — context-aware command sets per mount.
- **Auto-type intro** — the terminal types its first command on load before accepting input. Desktop-only.
- **Mobile perf gate is JS-level, not CSS-level.** CSS-hiding the terminal does NOT stop its JS from parsing/running on mobile — gate the script with a `matchMedia('(max-width: 820px)')` early-return plus `defer`, or mobile Lighthouse drops below budget.
- **Visible by default; JS only enhances — NEVER gate on a `no-js` class.** An early revision hid the terminal under a `no-js` class that JS removed at runtime; when the class-removal lost the race (defer ordering, cached script, JS error), the flagship terminal stayed `visibility:hidden` for multiple user-facing rounds while every claim said "fixed". Serve critical UI visible on first paint; JS adds auto-type/commands/live data, never reveals. If a flash-guard class must exist, strip it server-side in the served HTML — not client-side at runtime.
- **Zero test residue** — the seed state must never contain the author's test history (ghost `$ test` lines) or concatenated scaffolding copy. Ship exactly: typed intro, ready confirmation, styled hint. Seed copy needs designed affordance styling (muted hint line, cyan command chips), never raw unstyled text.
- Respect `prefers-reduced-motion` (instant render, no type-out).

## Serverless function shape (Vercel)

- Env vars via `vercel env add NAME production` (reads stdin; never in repo/client). Env vars are PROJECT-scoped: a separate staging project needs its own `vercel env add NAME staging` — production-only keys make staging's `/api/ask` return 503 "Assistant not configured".
- Validate: POST-only (405 otherwise), non-empty query, length cap (~500 chars), upstream error mapping (502/500), graceful "(no response)".
- Rate limiting is mandatory for public endpoints — unbounded public LLM access is a cost + abuse surface.
- Model + monthly budget are user gates; default to a cheap flash-tier model (`{MODEL}` class), low `max_tokens` (~220), low temperature.
- A key posted in chat must be treated as exposed even on free tier — rotate before real traffic; the serverless key boundary limits the blast radius.

## Pitfalls

- Unauthenticated public LLM = prompt injection + cost + brand liability. The honesty guard covers canned demo output, NOT hostile prompts — the system prompt must scope the model to only discuss the company.
- Versioned CSS refs (`?v=<sha>`) must carry layout changes to the terminal, or users see stale run-on styles for up to the cache TTL.
- Pre-deploy guard: the root page must carry its terminal marker, or a bad sync silently ships a terminal-less build.
- Test the dispatch in a live browser (type a command, verify navigation/URL), not just by grepping served bytes.
