<!-- GENERICIZED: 19×{CLIENT}, 1×{MODEL}, 3×{RELATIONSHIP} | source: skills/software-development/web-build-verification/references/{CLIENT} -->
# {CLIENT} interactive-terminal rounds (v6.9 → v6.13)

Case file for the web-build-verification umbrella. Project: {CLIENT} gateway + division pages, shared interactive terminal component, Vercel (production project `{CLIENT}`, staging project `{CLIENT}`).

## 1. The no-js flash-guard race (flagship hidden)

**Symptom:** user: "container still missing from landing page." Screenshot: empty navy space where the terminal should be; only label/logo/headline/ENTER button.

**Mechanism (served bytes):**
- Served HTML still had `<body class="no-js">`
- Served CSS still had `.no-js .term{opacity:0;visibility:hidden}`
- Terminal markup WAS present (`askterm` ×2, `{CLIENT}` loaded) — it was invisible, not missing
- The JS that removes `no-js` on init raced the deferred component load and lost in the user's browser

**Failure chain:** the flash-guard (meant to hide the raw pre-load scaffold) inverted the visibility contract — visible ONLY if JS runs. Two "fixed" claims were made while the served bytes still carried the class and the hiding rule; the fix had actually deployed to the WRONG Vercel project (production instead of `{CLIENT}`), which is why the served state never changed.

**Fix (structural):** remove `class="no-js"` from the served HTML; delete the `.no-js .term` hiding rule from CSS; terminal visible by default on first paint, JS only enhances. Verify: served HTML clean (zero `no-js`), zero hiding rules in served CSS, live-browser `visibility:visible` + `opacity:1` + input interactive.

**Rule:** never gate flagship/critical UI on a JS-runtime class-removal. Visible-by-default + JS-enhance, or strip the gate server-side.

## 2. Wrong-project Vercel deploy path

`vercel --prod` from the repo root deployed to the production project instead of the staging project (`{CLIENT}` is a SEPARATE Vercel project). Consequence: a "fix" was verified against a project the user never sees; the served surface the user reviews kept the bug. After any deploy: confirm which project/alias the new bytes came from (deployment URL/alias in Vercel output), then curl that alias cache-busted.

## 3. LLM surface: unconditional prompt line → robotic repetition

**Symptom:** user: "the llm keeps saying 'scheduled: intro call — we map this to your actual situation' for some reason, what's the prompt being injected into it?"

**Root cause:** the original system prompt REQUIRED the intro-call line on every answer (unconditional instruction). The model obeyed — even for "what does {CLIENT} do?".

**Fix (conditional phrasing):**
```
'- Add "→ scheduled: intro call — we map this to your actual situation" ONLY when the user expresses
   genuine interest in working with {CLIENT} or asks for next steps. Do NOT append it to every answer —
   for simple informational questions, answer directly and end with a suggestion like
   "Try /digital or /physical to explore."'
```

**Verification pattern:** read the prompt (repo HEAD) AND live-POST to the deployed endpoint (`curl -s -X POST https://<host>/api/ask -H 'Content-Type: application/json' -d '{"q":"what does {CLIENT} do?"}'`). The deployed function may differ from repo HEAD — probe the endpoint, not the code.

**Other durable prompt facts:**
- Model configurable via `{CLIENT}` env var (default `{MODEL}`); key server-side only (`OPENROUTER_API_KEY`), never in client bytes.
- Env vars scoped per environment: staging endpoint answers 503 "Assistant not configured" until `vercel env add OPENROUTER_API_KEY staging` — production scope does not carry over.
- Showcase-assistant framing for a real firm: "product showcase, not the firm — never give financial/legal/technical advice, never quote prices, never invent track-record numbers."
- No consulting firm in the competitive scan runs a public LLM surface at the front door — the space is empty, which is why a well-executed showcase assistant is differentiated.

## 4. Phantom-change trap ("replace the static terminal")

User instruction: "replace the static terminal on {CLIENT} page with the same interactive terminal as on the landing page."

Byte-check: the Digital page had ZERO terminal markers (no `askterm`/`term-body`/`term-input`). There was no static terminal to replace — the real task was ADD. Building literally against "replace" would have hunted a phantom. Rule: before executing a change request, grep the served page for the named object's markers; if absent, the task is add/move, and say so.

Related: later rounds showed the "static terminal still in old spot" complaint was itself a stale-cache render of the interactive terminal mid-page — the mount had landed at y~4700 (a separate section) instead of the hero. Position complaints need the element's DOM context (which section wraps it), not just "is it there".

## 5. Frame-vs-content symmetry axis

User: "give the terminals a bit more vertical length. resize the {CLIENT} counterpart (sourcing pipeline) by the same amount ... to preserve symmetry."

{RELATIONSHIP} matched `min-height` 330px=330px and declared symmetry. But `.term-body` had `max-height:200px; overflow-y:auto` — the terminal's CONTENT area was capped; only the frame grew. The pipeline (no cap) grew meaningfully. Hollow gain: frames match, content doesn't.

**Rule:** when a user asks for "more room" or "same size", measure the axis they asked about — content area, not frame. Check for content caps (`max-height` + `overflow`) on the panel that is supposed to grow, and raise the cap proportionally in the same pass.

## 6. Universal slash-command map (data-driven dispatch)

The command set grew from 3 commands to 10 groups with aliases (`/home`,`/back`,`/reset` → same action). At that scale, `if(cmd===...)` chains drift from `/help` output ("command works but help doesn't list it" bug class). Fix pattern: define the map once as data (`{cmds:[...], action, target}`), drive BOTH dispatch and `/help` from it. Targets as relative paths (`/digital/#proof`) not hostname-hardcoded (`https://staging.{CLIENT}#proof`) so they resolve on both surfaces. Verified targets before wiring: `{CLIENT}` 200, `github.com/{RELATIONSHIP}` 200, `#proof`/`#faq` anchors present — but `#benefits` (for `/info`) did NOT exist on the page; a command pointed at a dead anchor would have shipped.

## 7. Round-specific commands ({CLIENT}, for reference)

`/help` · `/digital` (+ silent alias `/enter`) · `/physical` · `/home`/`/back`/`/reset` → `/` · `/portfolio` → `/digital/#proof` · `/contact`/`/book`/`/mail`/`/email` → mailto:info@{CLIENT} · `/faq` → `/digital/#faq` · `/game` → {CLIENT} · `/github` → github.com/{RELATIONSHIP} · `/call`/`/phone` → tel:416-500-4462 · `/info` → `/digital/#benefits` (anchor had to be added).

## 8. Design-taste signals (user, {CLIENT} context)

- Height experiment rejected: "looked sleeker when it was short" — vertical length experiment scratched, reverts must be byte-verified (the first "scratched" claim was false on served bytes; taller values still live).
- Font direction: Digital division wordmark + CTA switched to Geist Mono ("sleek, terminal-grade, futuristic"); the blocky/condensed face suits Physical, feels out of place on Digital.
