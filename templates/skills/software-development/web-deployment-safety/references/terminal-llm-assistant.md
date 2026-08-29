<!-- GENERICIZED: 6×{CLIENT} | source: skills/software-development/web-deployment-safety/references/terminal-llm-assistant.md -->
# Terminal-as-Flagship: Slash Commands + Serverless LLM Assistant

Pattern for a marketing-site "interactive terminal" that is both a navigation
instrument AND a live AI assistant. Shipped on {CLIENT} ({CLIENT}) — the
"terminal talks back" flagship moment.

## Architecture (two paths, one input)

- **Input starting with `/` → client-side command dispatch.** Zero network.
  Commands: `/digital` (primary entry), `/enter` (silent alias), `/physical`,
  `/gateway`/`/home`, `/help`, demo commands, `/play` → easter-egg external
  site. The slash path keeps working even if the LLM endpoint dies — the
  static core stays resilient.
- **Raw text → POST to `/api/ask`** (Vercel serverless function, `api/ask.mjs`).
  The function holds the LLM API key in a **Vercel environment variable**
  (Production, Sensitive) — never in the repo, never in client JS. The key
  never crosses the browser boundary.

## Shared component + data-driven command map (scale past ~5 commands)

Once the command set grows beyond a handful of groups, stop scattering
`if(cmd===...)` branches:

- **Build the terminal ONCE as a shared component** (`assets/js/{CLIENT}`)
  with a mount config `{root, api, commands, intro, readyLine, focusDelay}`.
  Mount it on every page that needs it (landing gateway, division pages) —
  never copy the markup+script per page or the implementations drift and only
  one gets fixed (the v6.6 lesson).
- **Command map = DATA, single source of truth.** One array of
  `{cmds:[...aliases], action, target, label}` drives BOTH the dispatch
  lookup AND the `/help` output. At 10 groups with aliases, the hardcoded
  chain is where "command works but help doesn't list it" lives.
- **Context-aware command sets:** the component takes a per-mount command
  list, so the landing keeps nav commands while a division mount gets its
  native set; the LLM path stays shared and identical.
- **"Add, not replace":** before assuming a page has a static element to
  replace, byte-check the served page for its markers — "replace the static
  terminal on page X" was based on a phantom; the real task was ADD the
  terminal (nothing existed there).
- Universal command archetypes worth reusing: nav (`/digital`, `/physical`,
  `/home`+aliases), anchor (`/portfolio` → `/page/#proof`, `/faq` →
  `/page/#faq` — RELATIVE paths, not hostname-hardcoded, so they resolve on
  staging AND live), mailto (`/contact`, `/book`, `/mail`, `/email`), tel
  (`/call`, `/phone`), external (`/game`, `/github`).

## Serverless endpoint requirements

- **System prompt = showcase assistant, not the firm.** The model explains what
  the company does and routes to "book a consultation"; it never gives advice,
  quotes, or claims the firm can't back. The marketing site's existing honesty
  guard line (e.g. "→ scheduled: intro call — we map this to your actual
  situation") is the system-prompt spine.
- **Rate limit mandatory** — in-memory per-IP window (e.g. 10 req/min) returning
  HTTP 429. An unauthenticated public LLM endpoint without a cap is a cost
  surface and an abuse magnet.
- **Honesty/closing lines must be CONDITIONAL, never unconditional.** The
  original prompt ended EVERY answer with "→ scheduled: intro call — we map
  this to your actual situation" — the model appended it even to "what does
  {CLIENT} do?", which read as pushy and drew a user complaint ("why does the LLM
  keep saying this?"). Fix: "Add '→ scheduled: intro call' ONLY when the user
  expresses genuine interest or asks for next steps; for informational
  questions answer directly and end with a suggestion like 'Try /digital or
  /physical to explore'". Audit any mandated closing line for the same trap —
  a forced next-step pitch on every answer undercuts the showcase framing.
- **Give the assistant the firm's real contact details.** Put email + phone in
  the system prompt ("Contact: email X, phone +1-… (tel:…) — when asked for
  contact details, give these exactly") so the terminal answers "what's your
  email/phone" correctly instead of deflecting. **Contact changes propagate to
  FOUR surfaces:** page contact buttons (`tel:`/`mailto:`), the `/call`
  command-map target, the LLM system prompt, AND a repo-wide grep for zero
  occurrences of the old value. A number swap is only clean when
  `grep old-number` returns 0 in source — not just in the served bytes.
- **Key hygiene:** a key pasted in chat/commits is treated as exposed. Free-tier
  caps the damage, but rotation before real traffic is the clean move. Verify
  zero key leakage in served bytes (`grep sk-or-v1` / provider prefix).

## Interaction contract (the instrument-vs-door split)

- **Terminal panel = instrument.** Clicking it focuses the input and does NOT
  navigate. The panel must be a `<div>`, NOT an `<a>` — an anchor panel
  navigates natively on every click and `stopPropagation` on an inner handler
  cannot stop it (no handler fires; the anchor's default action wins).
- **"Enter the division" text = the door.** Only that element is an anchor with
  hover states.
- Belt-and-braces: terminal click handler does `e.preventDefault()` +
  `e.stopPropagation()` + `line.focus()`.

## QA lessons from the field

- Verify the click-split against the **served DOM structure** (is the panel an
  anchor?), not just "no onclick found" — code-level checks passed while the
  shipped markup still wrapped the panel in `<a>`.
- Functional tests: click terminal → pathname unchanged + input focused; click
  the door anchor → pathname changes. Test both on the live/staging URL.
- LLM responsiveness: POST twice and confirm two DIFFERENT coherent answers
  (proves the model is live, not a canned string).

## Visibility: the no-js flash-guard inversion (the "container missing" bug)

The landing terminal once rendered as "missing" while `askterm` markup was
present in the DOM. Mechanism: `<body class="no-js">` shipped in the served
HTML, `body.no-js .term{opacity:0;visibility:hidden}` shipped in the CSS, and
the JS step that removes the class never ran. Two compounding causes:

1. **Init race:** the mount init ran before the `defer`-loaded component
   defined its global — `if(window.{CLIENT})` was false, so the mount
   (and the class removal inside it) never happened. Fix: mount on
   `DOMContentLoaded` or poll `setTimeout` until the global exists. Symptom
   signature: component loads, `typeof X !== 'undefined'` is true, but body
   class never clears.
2. **Guard inversion:** visibility depended on JS running. The robust rule:
   serve the HTML WITHOUT `no-js` gating critical UI — the flagship terminal
   is visible by default on first paint; JS only *adds* behavior (auto-type,
   commands, LLM). Never let the flagship depend on a runtime step the
   user's browser can lose. Strip the class server-side, or delete the hiding
   rule entirely and accept a brief raw-scaffold flash over an invisible
   terminal.

## Static lookalike + affordance (one terminal, visibly interactive)

A *decorative* terminal graphic in a hero (e.g. `$ {CLIENT} assess --agentic-ai`
+ checkmark lines, no input field) reads to the user as "the static terminal"
even after an interactive mount is added elsewhere on the page. The user will
say "the static terminal is still in its old spot" while the interactive one
sits mid-page.

- When told to "replace the static terminal with the interactive one":
  byte-check what actually exists, replace the **decoration in place**, and
  verify the served DOM has exactly ONE terminal element (`#askterm` count).
- A live terminal can still read as static at hero size. Affordance pass:
  visible input border (2px bright accent), blinking caret, brighter
  placeholder, outer glow. If the user keeps calling it static, the fix is
  styling, not repositioning.

