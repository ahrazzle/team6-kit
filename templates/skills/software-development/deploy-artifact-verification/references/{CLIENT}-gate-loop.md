<!-- GENERICIZED: 8×{CLIENT}, 1×{RELATIONSHIP} | source: skills/software-development/deploy-artifact-verification/references/{CLIENT} -->
# {CLIENT} Static Multi-Page Site — Worked Incidents

A running log of the specific verification/staging failures and fixes from the {CLIENT} site (static multi-page: `/index.html`, `/digital/index.html`, `/physical/index.html`, Vercel, no router). Each entry is one class of failure and the durable fix. The SKILL.md carries the general rules; this file is the concrete evidence.

## 1. Giant-anchor click bug (verify served DOM, not JS handlers)

- **Report:** "terminal still enters the site when I click it," despite code-level verification showing a clean `stopPropagation` + `focus()` handler.
- **Root cause:** the entire gateway panel was a single `<a class="half digi" href="/digital/" aria-label="Enter {CLIENT}">` wrapping logo, headline, and terminal. Anchor default navigation is native; `stopPropagation` on a child handler can't stop it, and there was no JS handler at all to inspect (grep "no onclick" was true and irrelevant).
- **Confirm:** `curl https://host/ | grep -o '<a class="half[^"]*"[^>]*>'` → shows the `<a>` wrapper.
- **Fix:** panel `<a>` → `<div>`; only the explicit "Enter {CLIENT} Division" text stays an `<a>`; terminal click handler adds `preventDefault()` as belt-and-braces.
- **Lesson:** interaction contract lives in the markup structure, not just handlers. Inspect the element tree.

## 2. Stale CSS against new HTML → run-on text (version CSS too)

- **Report:** pipeline labels render concatenated (`SPECspecificationC34 grade`) on the physical page.
- **Root cause:** new HTML added `SPEC`/`specification` spans but the `.route-row{display:flex;gap:8px}` layout rule lived in an **unversioned** `gateway.css`; a browser holding the old CSS (4h cache TTL) rendered the new spans with no gap. Images had `?v=3`; the stylesheet had none.
- **Confirm:** `curl -s "https://host/gateway.css?v=<sha>" | grep -o '\.route-row{[^}]*}'`.
- **Fix:** version every CSS/JS ref (`/gateway.css?v=<deploy-sha>`), bump same commit as the CSS change; verification fetches append `?cb=<deploy-sha>`.
- **Lesson:** CSS is the layout-carrying asset class and the one most often left unversioned.

## 3. Unauthorized direct-to-live push (staging-first broken)

- **Report:** "why are we making changes on the live domain and not staging?" — the user caught that live was serving an unreviewed version while the room iterated on staging.
- **Root cause:** one push to live bypassed the review gate. Everything after it went to staging only, so live stayed stuck on the unapproved build and the room argued against the wrong baseline.
- **Confirm swap:** re-curl live for a distinctive removed feature (`/api/ask` should 404, `/enter` command should be absent). Two separate "rollback done, verified" reports were both false before a real rollback landed.
- **Fix:** deploy-target lock — no deploy without explicit `--target=live|staging` + second-agent confirm; live only ever from an approved staging hash.
- **Lesson:** trust the user's directive (live → last-approved, staging → working), and ground-truth the swap yourself.

## 4. Hollow-card false alarm (read the base rule, not the first grep hit)

- **Report:** "card classes are hollow — padding only, the plain-rectangle complaint survives."
- **Actual:** the `@media(max-width:720px)` overrides legitimately adjust padding and sit after the full base rules, which carry `border-radius:24px; background; box-shadow`. The classes rendered as proper cards.
- **Confirm:** read the first non-media `.card-warm{...}` rule and/or computed style, not a grep that catches the breakpoint override.
- **Lesson:** "class exists" ≠ "class renders." Gate on computed style. And don't cry hollow off a single padding-only grep hit.

## 5. Three-column layout misread (don't over-read an accidental render)

- **Report:** "was this an intentional new layout?" — a rendering artifact (the panel→div fix letting the terminal escape into its own column) produced an accidental 3-column look the room initially liked and adopted.
- **Correction:** the user clarified it was still a 2-half layout; the real signal was *vertical space* for the flavour elements (terminal, sourcing pipeline), not a column structure. Spec: 2 halves stay; flavour elements get a dedicated inner column inside their half (`[content | terminal]` in Digital, `[pipeline | content]` in Physical).
- **Lesson:** ground-truth an "interesting" accidental render against the user's intent and the live DOM before adopting it as a redesign. A good accident isn't necessarily a new structure.

## 6. LLM-on-front-door governance (bounded showcase assistant)

- **Request:** make the terminal a live chatbot. Refused full "the firm's AI" framing — it's a brand-reality mismatch for a consulting firm whose product is judgment. Shipped instead: slash commands run client-side; raw text POSTs to a `/api/ask` Vercel serverless function (key in env var, never repo/client) with a tight system prompt + honesty guard as its spine, plus per-IP rate cap.
- **Security:** a key posted in chat is treated as exposed — rotate before real traffic; keep it out of client bytes. Serverless function is the boundary that makes that enforceable.
- **Lesson:** public unauthenticated LLM surfaces on a consulting site are a liability unless scoped as a *product showcase assistant*, not the firm answering.

## 7. Mirror-direction misread (measure geometry, don't eyeball a screenshot)

- **Report:** "make the {CLIENT} half mirror the {CLIENT} half by switching the positions of the terminal and the logo/text container." The room over-spec'd this, asked multi-option clarifying questions, and the user had to clarify three times ("you're getting confused"), finally stating the exact geometry: terminal and pipeline **beside each other in the middle**, content stacks on the outer edges.
- **Root cause of the confusion:** eyeballing screenshots. A vision read declared the current layout "balanced and symmetric" — but measuring element center-x with `getBoundingClientRect().x + width/2` exposed the truth: Digital's terminal sat at the outer-left (center-x ≈213) while Physical's pipeline sat toward center (center-x ≈1006), and `innerWidth/2` = 800. The halves were **NOT mirrored at all** — one flavour element was on the outside, the other toward center.
- **Confirm (the method that settles it):**
  ```js
  const ctr = window.innerWidth/2;
  const cx = el => { const r=el.getBoundingClientRect(); return Math.round(r.x + r.width/2); };
  // termCx, pipeCx, digiStackCx, physStackCx, then assert:
  // termCx < ctr && pipeCx > ctr  (flavour elements flank center)
  // digiStackCx < termCx && physStackCx > pipeCx  (content stacks on outer edges)
  ```
  Also check vertical symmetry with `getBoundingClientRect().top` on both content stacks (they should share a midpoint).
- **Fix:** the v6.9 CSS had a blanket `.half-stack{order:1}` that pushed Digital's stack toward center and its terminal to the outer edge. Setting `digi stack order:0` / `phys stack order:2` gave each half its correct internal arrangement.
- **Lesson:** measure before spec'ing. A terse "mirror X to Y" is unambiguous once you've measured the current state — measure first, don't ask a clarifying question when the geometry already settles it.

## 8. `no-js` flash-guard inversion (critical UI invisible by default)

- **Report:** "terminal missing from the landing page" — the Digital half showed empty navy where the terminal should be.
- **Root cause:** `<body class="no-js">` + `.no-js .term{opacity:0;visibility:hidden}` gated the flagship terminal's visibility on JS removing the class. When the old inline responder was replaced by the shared component, nothing removed the class anymore (and the init ran before the deferred component loaded), so the terminal stayed hidden forever. Visibility was inverted: visible only if JS runs.
- **Confirm:** `curl -s https://host/ | grep -o '<body[^>]*class="[^"]*"'` → still `no-js`; `curl -s https://host/gateway.css | grep -o '\.no-js[^{]*{[^}]*}'` → hiding rule still present.
- **Fix:** remove `no-js` from served HTML + delete the hiding rule; serve critical UI visible by default, JS only enhances. The claim "fixed" was false on served bytes (the fix had deployed to the production project, not staging — see #10).
- **Lesson:** the served HTML/CSS gating a load-bearing element on a JS runtime step is a permanent-hide risk, not a flash-guard. Verify served bytes, not local.

## 9. Static → interactive terminal replacement (mount AT the static spot, remove the static one)

- **Report:** "terminal is below the intro screen where it should be, where static terminal is still sitting" — repeated four times across rounds.
- **Root cause:** replacing a static terminal decoration with an interactive one kept going wrong on *placement*: the interactive mount landed in a separate mid-page section or below the hero, while the static terminal visual stayed in the hero. Two terminal-looking elements remained, or the interactive one was somewhere the user didn't expect.
- **Fix:** mount the interactive element **at the static element's exact location** (replace in place in the page flow), remove the static one so there is exactly one terminal, and make it visibly interactive at that size (visible input + blinking cursor, not a static-looking graphic). Verify placement by measuring `getBoundingClientRect().y` against the hero bottom, and count `[class*=term]` mounts.
- **Lesson:** "replace X with Y" means Y goes where X was and X is removed — not Y added somewhere else while X lingers. When a placement bug recurs, measure the mount's actual position, don't trust a "moved to the hero" claim.

## 10. Deploy-target project wiring (`vercel --prod` → wrong project)

- **Report:** fixes "verified on staging" but absent from staging's served bytes; the landing terminal stayed invisible despite a claimed fix.
- **Root cause:** `vercel --prod` was deploying to the **production** project, not the `{CLIENT}` project — the repo was wired to prod, so every "staging" deploy actually hit production. Two layers: wrong-project deploys AND the no-js inversion (#8) both hid the terminal.
- **Fix:** confirm the deploy targets the right project (`vercel link`/project id), and verify the fix on the *intended* surface's bytes. {RELATIONSHIP} caught and corrected the project routing.
- **Lesson:** a deploy command's target is whatever project the repo is linked to — verify it, don't assume. And re-curl the intended surface after every deploy.

## 11. Content-axis vs frame symmetry (the hollow vertical-length pass)

- **Report:** "give the terminals a bit more vertical length… resize the sourcing pipeline by the same amount to preserve symmetry."
- **What shipped wrong:** `min-height` was matched (330=330) — the *frame* — but `.term-body{max-height:200px}` capped the actual interactive content area. The terminal looked taller but gave zero extra content room; the pipeline, with no cap, grew meaningfully. Symmetry measured on the wrong axis.
- **Fix:** when resizing for "more room," measure and match the **content axis** (terminal body height vs pipeline content height), and raise any inner `max-height` cap in the same pass as the frame bump. Set the acceptance criterion as "terminal content area ≈ pipeline content," not "frames match."
- **Also:** served-value disputes recur ("max-height:320px" vs "200px"). The served truth is only obtainable from a cache-busted fetch of the current versioned ref — treat any claimed served value as unverified until re-curled with `?cb=`.

## 12. Shared component + single source of truth (the "works but help doesn't list it" drift)

- **Refactor:** the terminal became one shared component (`{CLIENT}`) mounted in two places, with a **data-driven command map** (`{cmds:[...], action, target}`) that drives BOTH the dispatch and the `/help` output from the same array — so a command can never work while help omits it. Target URLs (relative anchors, external hostnames) are config values, not hardcoded in the dispatch.
- **Lesson:** once a feature has many branches (10 command groups with aliases), a hardcoded `if(cmd===...)` chain is where "works but help doesn't list it" drift lives. One data structure, both consumers, zero divergence — the same principle as the shared component mount: build once, don't copy.
