<!-- GENERICIZED: 1×{AMOUNT}, 4×{CLIENT}, 2×{RELATIONSHIP} | source: skills/software-development/static-brand-site-launch/SKILL.md -->
---
name: static-brand-site-launch
description: Use when building or deploying a brand site on Vercel.
version: 1.0
author: {RELATIONSHIP}
license: internal
---

# Static Brand Site Launch

Class-level workflow for building a client-facing marketing/brand site as a static multipage site and putting it live on a custom domain with private hosting (Vercel + Cloudflare).

## When to Use

- Building a client-facing marketing/brand site (static, multi-page).
- Deploying a static site to a custom domain via Vercel + Cloudflare.
- Diagnosing broken pages/routes on an already-deployed site.

## Architecture rule (learned the hard way)

**Build real pages, never a single-file SPA shell with a hand-rolled JS router.**
One `index.html` juggling URL schemes (hashes + rewrites + pathname fallback) produced every rendering failure in the reference project: white-on-white components, dead division pages, split SEO authority. The fix was deletion:

- `/index.html`, `/digital/index.html`, `/physical/index.html` — plain files
- Plain `<a href="/digital/">` links between them; works with JavaScript disabled
- Per-page `<title>`, meta description, `<link rel="canonical">` are trivially correct because they are just files
- No `vercel.json` rewrites needed for first-party routes

## Component surface contract

Any shared visual component (e.g. `.glass`) must declare its surface variant explicitly (`on-light`, `on-dark`). A component styled against an implicit dark background silently breaks when reused on light surfaces — translucent white on white = invisible cards. Never let a default assume a background.

**Give shared tokens ONE home.** Once a site has more than one page, ship a `system.css` (tokens: type scale, spacing, radii, palette; plus shared components: buttons, cards, sections, reveals) and one page-specific sheet per route. Duplicated per-page CSS is how surface-contract bugs come back — a fix lands in one page and the identical rule elsewhere drifts. This is the same rule as the logo asset pipeline's "one source-of-truth directory," applied to CSS.

## Asset pipeline

- Source logo directories get quarantined; build only from a verified `assets/` directory with `MANIFEST.sha256`.
- PNGs exported from viewers often have checkerboard baked in OR are screenshots of the viewer's transparency indicator. Verify with PIL: mode RGBA + corner alpha 0 means true alpha; flat RGB with gray squares means baked background.
- Flood-fill from image borders (not global threshold) removes baked checkerboard without punching holes in light-colored artwork. Lower thresholds iteratively until enclosed cutouts clear too.
- Dark logos on dark surfaces need a luminance-targeted derived variant in `assets/derived/` (only pixels below a luminance floor lifted), never a CSS hack.
- Hero marks get optimized WebP+PNG variants behind `<picture>` elements (PIL resize to ~560px max, webp q82). Raw 800KB–1.4MB hero PNGs dominated mobile LCP and held the Lighthouse score at 69; the swap to `<picture>` webp took it to 96. Gateway marks need this most — it's their only paint.
- Per-page social meta is part of the build, not a nice-to-have: `og:title`, `og:description`, `og:image` (a division/hero logo works), `og:url`, `twitter:card=summary_large_image`. Without it shared links render as bare URLs.

## Performance: self-hosted fonts + LCP tuning

Google Fonts `<link>` is the render-blocking offender on nearly every brand site: the css2 request wastes ~800ms and leaks visitor data to Google. Self-host the woff2 files and delete the external request entirely (this alone, plus image fixes, took a reference build from mobile perf 77 → 95).

- **Extract latin woff2 subsets** from `fonts.googleapis.com/css2?...`: request the CSS with a modern Chrome UA, parse the `@font-face` blocks, and take the one whose `unicode-range` starts `U+0000-00FF` (the latin subset). Request ONE weight per CSS call (`family=Inter:wght@400`) so the latin block returns that weight's static file — asking for several weights can hand back one variable-font file (check: no `fvar` table, and md5s differ per weight). Use `scripts/self-host-google-fonts.py`.
- **Serve from `/assets/fonts/`** with `@font-face { font-display: swap }` in an inline `<style id="fonts">` block; remove every `fonts.googleapis`/`fonts.gstatic` link AND both `<link rel="preconnect">` lines.
- **Preload the LCP face only**, not every weight — preloading all faces recreates the bloat. Preload the font the LCP element uses (usually the hero h1 face) plus the LCP image itself, as parallel `<link rel="preload">` entries.
- **Metric-safe fallback stack** so the swap is near-invisible: `"DM Serif Display", Georgia, "Times New Roman", serif` — a close-metric fallback avoids the jarring reflow a generic sans causes when the serif arrives.
- **Find the real LCP element** from the Lighthouse JSON: `audits['largest-contentful-paint-element'].details.items[0].node.selector`, then optimize THAT element. In the reference build the LCP was a 173KB SVG hero mark — swapping it to a webp-primary `<img srcset>` (55KB) cut LCP 4.5s → 2.2s.
- **`vercel.json` headers fix content types + cache** (Vercel otherwise serves some SVGs as text/plain):
  `"source": "/(.*)\\.svg"` → `Content-Type: image/svg+xml`; `"source": "/(.*)\\.woff2"` → `Content-Type: font/woff2` + `Cache-Control: public, max-age=31536000, immutable`.
- **Viewport-gate ambient canvas node counts** (e.g. `<640px ? 26 : 58`) — a full desktop node field is the classic mobile perf killer on hero pages; a `prefers-reduced-motion` query should drop the whole scene.

## Live verification gate

Run against production, not local files:

- All routes 200 with the correct per-page `<title>` (`/`, `/digital/`, `/physical/`, `www`, subdomain portfolio items).
- Mobile Lighthouse performance ≥ 80 on the live URL (`npx lighthouse <url> --preset=perf --form-factor=mobile --screenEmulation.mobile --output=json`). Biggest offenders on brand sites: unoptimized hero images (`uses-responsive-images`), render-blocking Google Fonts.
- Cache check: confirm `?v=`/hashed asset refs are in the served HTML, then hard-refresh — unversioned refs let users keep seeing a stale build.
- **Version EVERY asset ref, not just images.** HTML updates instantly while unversioned CSS sits in the browser cache (e.g. a 4-hour TTL) — the result is new HTML running against old layout rules (run-on text, collapsed panels, "weird text"), and it reads as a broken site to the user even though the served source is correct. Bump `?v=` on stylesheets AND scripts on every layout-changing deploy, not only images. Verify with the cache-bust probe (`?cb=`). This was the one gap in the reference project's cache contract: images got `?v=`, the CSS that carries layout got nothing.
- **Cache-bust every gate probe by default** (`?cb=<deploy-sha>` appended to HTML/CSS curls). Three "stale bytes vs live bytes" disputes happened in one project while the deploys were correct — each was a probe hitting a cached copy. Make the probe deterministic; never argue about whose cache is fresh.
- **Mobile emulation gate (binding):** 390px viewport screenshot per surface plus a mobile Lighthouse run against the live URL. "Looks fine on desktop" never closes a brand-site gate — desktop-only QA is exactly how a "horrible on mobile" site shipped.
- **One primary CTA per surface, verify the hrefs differ.** A duplicated `mailto:` under two labels ("Book a consultation" / "Email us") is a gate miss, not a design choice — an automated href-diff check catches it.

## Responsive / fluid layout (the "six fixed-width cages" trap)

"Containers look archaic" and "site looks horrible on mobile" are the two most common brand-site complaints after a desktop-first v1, and they share one root: **fixed-pixel width cages**. A build that caps content at several arbitrary `max-width`s (`1120px / 840px / 680px / 640px...`) leaves side gutters at every window size and ships zero mobile responsiveness.

- **Fluid containers:** `.section { width: min(100% - 48px, 1200px); margin-inline: auto; }` — full-width feel at every viewport with sane gutters. Kill every fixed `max-width` cage; one fluid rule beats six nested caps.
- **Clamp the type scale** so hero/display text scales with the viewport: `hero-h { font-size: clamp(28px, 5.5vw, 48px) }`, `padding: clamp(96px, 18vh, 160px)`. Static px type is the desktop-squeezed-into-390px problem.
- **Real mobile tiers, not a skeleton:** ≤900px (grids 2-col) → ≤720px (stacked layouts, touch targets ≥44px, compact CTA-only nav — never a desktop-width nav on a phone) → ≤560px (1-col, fluid gutters). Add `overflow-x: clip` on `body` so nothing overflows horizontally.
- **Responsiveness must live in the per-page sheets too** — a shared `system.css` with breakpoints but page sheets full of fixed px (hero padding, grid widths) still renders broken on mobile.
- Verify with the mobile emulation gate (above), not by resizing a desktop window.

## Deploy chain (Vercel private repo + Cloudflare DNS)

1. `gh repo create <name> --private --source . --push`
2. Vercel project via API or CLI; CLI deploys are the guaranteed path (git-link auto-deploy depends on the GitHub App being installed)
3. Attach domains via API; apex may need a TXT `_vercel` record in Cloudflare before `verify` succeeds
4. Cloudflare: apex uses CNAME flattening (CNAME at root, proxied); www CNAME same target
5. Order matters: create and verify the destination BEFORE releasing the old binding

## Staging-first review workflow (BINDING for this user)

The user's standing rule after a production regression: **every new version deploys to a staging subdomain and waits for user review; promote to the main domain only after explicit approval.** No direct-to-main pushes for client-facing brand sites. Set it up once, then every iteration is: build → deploy staging → user reviews staging → on approval promote to main (with the CSS `?v=` bump in the same commit).

Staging subdomain setup (Vercel + Cloudflare):
1. Create a separate project: `POST /v9/projects` `{"name":"<site>-staging"}` (or `vercel project add`).
2. Attach the domain: `POST /v9/projects/{pid}/domains` `{"name":"staging.<domain>"}` — returns a `_vercel` TXT verification value.
3. Cloudflare: add the TXT under `_vercel` + a CNAME `staging` → `cname.vercel-dns.com` (unproxied).
4. `POST .../domains/staging.<domain>/verify` after ~20s.
5. Deploy: `vercel --project <site>-staging --prod --yes` from the build dir (CLI deploy, not git-push).

### Environment swaps and the deploy-target lock

- **Baseline restoration:** live → the last USER-APPROVED commit, staging → the current working version. Nothing is lost, and both surfaces are independently verifiable. The user's directive was explicit: "put what's on the live domain on staging since that's the working version; on the live domain go back to the last approved version."
- **Verify BOTH surfaces by ground truth, never claims.** After a swap, POST to the removed endpoint (expect 404), grep served HTML for the removed command (expect absent), check the title/markers. A "rollback done" report that wasn't byte-verified was false — live still served the unapproved version, `/api/ask` returned 200, and the whole round re-opened. Served bytes are ground truth; STATE.md and room reports are claims.
- **Rollback mechanics gotchas:** `git checkout <commit> -- .` restores paths PRESENT in that commit but does NOT delete paths absent from it — a leftover `api/ask.mjs` from the newer tree survives a v6.3 checkout. After checkout, `git rm` the extras so the tree truly matches. A `cp`-based "sync" of one build version over the repo root can silently clobber the root page (see the never-batch-copy pitfall) — prefer `git checkout <sha> -- <files>` for restores.
- **Deploy-target lock (binding):** no deploy command runs without an explicit `--target=live|staging` intent and a second agent's confirmation. The single unauthorized push that broke staging-first was the root cause of an entire forensics round. Record what each target's baseline CONTAINS (commit + identity markers + endpoints), not just which commit — a swap that silently reverts already-approved fixes (click-split, Enter contrast) is how a user's previously-fixed complaint ships a third time.
- **Vercel env scoping gotcha:** the CLI has NO `staging` environment scope — valid scopes are production/preview/development. A staging PROJECT's env vars go in its `production` scope: `cd <linked-dir> && vercel link --project <site>-staging && echo "$KEY" | vercel env add OPENROUTER_API_KEY production --yes`. Without this, staging's `/api/ask` answers 503 "Assistant not configured" while live works.

## Navigation and container rhythm (repeated user complaints)

Three complaints recur across brand-site reviews and each has a structural fix, not a patch:

- **"No clear way to navigate between divisions/sections."** A multi-section brand site (two divisions, or services + case studies + contact) needs a **persistent cross-section switch in the header on every sub-page** — a labeled button, not just in-page anchor links. Extend it to the **footer too** ("Explore the other division"), because anyone who scrolls past the header loses the path. Verify the switcher exists in the served HTML of every sub-page, not just the gateway. When adding the footer switcher, don't bolt it into a flex `space-between` row with three children — that misaligns (a recurring complaint). Use a 3-zone grid footer: `footer .foot-wrap { display:grid; grid-template-columns:1fr auto 1fr; gap:24px; align-items:center; }` with the switcher as its own `foot-switch` block (label + button stacked, centered), collapsing to one column ≤720px. And when the user says contained cards still look like "plain rectangles," refine them to match the mid-page card language — gradient depth, a 3px accent line on top, a soft inner glow — not a flat navy block.
- **"Containers look awkward / archaic."** The recurring pattern behind this is **full-bleed dark bands inside a light page** — edge-to-edge sections (quote strip, "How it works", contact CTA) that clash against the light body. Rule: **below the hero, every dark surface is a contained card** with the same radius and margin rhythm as the mid-page cards. No full-bleed bands inside a light page, period. When the user flags "the 4 in the middle look good, top and bottom look bad," they are naming exactly this — contain the bands to match the cards that already work. Make the rule blanket from the start; fixing 1 of 4 dark surfaces just leaves the inconsistency the user flagged.
- **Light-theme container borders need a measured contrast floor, not a visual pass.** Light cards on a cream/off-white page failed FOUR review rounds while dark cards passed — "can't see the outline", "same colour as the background", "just rectangles" — because a faint 1px border line on cream does not read as a container boundary. The fix that ended the recurrence was a **`--line-strong` token tuned to a numeric contrast ratio against the page background (≥1.5:1)**, used by all light-theme card borders, plus a gate check that verifies the border color contrast numerically rather than by eyeball. Never fix light-theme outline complaints by making the border "a bit darker" — measure it. Same for the blocky-light-outer-wrapper class (a sharp-cornered, borderless white rectangle wrapping a value-prop or a "how it works" grid): give it the card vocabulary (radius, visible border, shadow) or wrap it in the shared light-card class, and kill the full-bleed white band so the card carries the section.
- **"Hero is too plain and empty."** The failure mode is a dark hero with text crammed in the upper-left and 65–70% dead viewport. Two-part fix:
  - **Composition, not texture.** Adding a grid texture alone does NOT fill the dead zone — the fix that survives is a **right-side balancing element** (a rendered product visual: framed terminal device, dashboard mock, orbital diagram) in a 2-column hero (`grid-template-columns: 1fr minmax(300px,420px)`), left text column unchanged. Texture without composition reads as "less plain," not "designed."
  - **Grid must be visible on dark.** A grid that reads on a light page is invisible against dark navy. Use a **light-stroke grid at visible opacity** (`rgba({AMOUNT},.06)`-ish) on dark heroes, not the default `rgba(...,.05)`-with-cyan that vanishes — and hide the right-side device below ~900px (it stacks to a single column on mobile).

## Interactive proof element (the "blow them away" ask)

A static brand site whose product is technological skill usually earns a request for "more flair / hit them with what we can do." The highest-leverage answer is an **interactive proof element** in the hero, not more decorative motion. Reference build shipped a parameter-driven terminal responder on the digital half and a sourcing-pipeline tracker on the physical half.

- **Parameter-driven responder, not a canned script.** A fixed `$ {CLIENT} deploy` animation reads as decoration; a responder that accepts an actual query ("/build supply chain", "/fund 5M raise", "/source c34 steel") and maps it through a small client-side lookup table to a plausible engagement path reads as a system responding to the visitor. `/help` lists the command set so nobody guesses blind. Pure client-side only — a marketing homepage must never send visitor input anywhere.
- **Honesty guard on every response** (critical for a firm selling judgment): end each reply with a line like "→ scheduled: intro call — we map this to your actual situation." That keeps a demo from crossing into fake-capability territory, which would actively hurt trust. Pair with the integrity rule below: never put invented numbers next to it.
- **no-js flash guard ({RELATIONSHIP}):** the element starts hidden under a `no-js` body class; JS removes the class only after it confirms it is running. Never let the raw scaffold flash before the designed device appears — same bug class as the white-on-white surface contract.
- **Auto-type intro:** the terminal types its first command on load before accepting input ("watch us work" moment), then shows "✓ capability demo ready" and focuses the input. Kowalski-compliant — one-time, responds to load, no ongoing motion.
- **Gate the SCRIPT by viewport, not just the style.** The element is `display:none` on mobile, but the responder JS and auto-type animation still parse and execute on narrow viewports unless gated — see the mobile-perf pitfall below.
- **Functional ≠ presented (the presentation pass).** A responder that works but ships as raw scaffold reads as "weird text" to the lay visitor — and a consulting brand's hero is exactly where that reads worst. The presentation pass is not optional polish; it is what turns the element into a product moment. Build it in the same pass as the function: device chrome (framed panel, macOS-style title bar with traffic-light dots, glow edge), a styled hint line (muted ~42% opacity, mono, colored command chips) instead of an unstyled instruction string, and full labels instead of cryptic tokens — `SPEC` + `specification`, `SRC` + `sourcing`, etc. To a lay visitor, bare acronyms read as junk tokens, not as a supply-chain proof.
- **Never ship the author's test residue in the seed state.** If you functional-tested the responder by typing commands into it, those commands are now in the DOM as seed lines — the user then sees `$ /build supply chain` "ghost" lines that are not scaffold at all, but your test history. A demo terminal must open with exactly the clean seed: the styled hint, the auto-typed first command, and the "capability demo ready" confirmation. Zero concatenated `try /build…/fund…/source…` strings — fewer, cleaner lines beat more lines.
- **CLI-style UI typography: `--flag` double hyphen, never an em-dash.** `—help` (em-dash) renders as broken-looking text in a CLI context, and it is the first thing a visitor reads in the terminal. Check the served HTML for the em-dash variant. The input field must be styled as part of the device (dark inset mono field, cyan border, visible focus ring), not a detached plain form field below the terminal.
- **Command set as data, single source of truth.** Once a responder grows beyond ~4 commands, hardcoded `if(cmd===...)` chains are where "command works but /help doesn't list it" drift lives. Define the map once as an array of `{cmds:[...], action, target, label}` — aliases grouped to one branch (`/home`,`/back`,`/reset` → one record) — build a lookup from aliases, and render `/help` from the SAME array. One structure, two consumers, zero divergence. Universal command groups worth supporting on a consulting brand site: `/help`, `/digital`, `/physical`, home aliases, `/portfolio` → `/digital/#proof` (relative anchor), contact aliases → `mailto:`, `/faq` → `/digital/#faq`, `/game` → a portfolio game URL, `/github`, call/phone aliases → `tel:`. All page-anchor targets relative (`/digital/#faq`), never hardcoding the staging hostname.
- **Shared component, mounted twice — never copy the markup.** When the same interactive element belongs on two pages (landing hero + an inner page), build it ONCE as a module (wiring: key handler, `/api/ask`-style fetch, focus management, honesty guard all in one file) and mount it with a config object (`{root, api, intro, readyLine, commands}`), themed per context. Copying the markup as a second instance guarantees drift — one mount gets fixed, the other doesn't. Config-driven mounts also enable a context-aware command surface later (Physical page gets `/source`, landing keeps `/enter`).
- **Interaction contracts live in the markup, not just the JS handlers.** The giant-anchor bug: `<a class="half" href="/digital/">` wrapping the whole clickable panel made EVERY click inside it navigate — no JS handler exists to `stopPropagation` against because it's the anchor's native behavior. This shipped three times because gates verified handlers, not the served DOM. Before claiming a click fix: confirm the panel is a `<div>`, only the labeled CTA ("Enter {CLIENT} →") is an `<a>`, and there's no nested `<a>` inside an `<a>` (invalid HTML). Belt-and-braces: the interactive element's own click handler calls `preventDefault()` + `stopPropagation()` + `focus()`.
- **Mount the interactive element WHERE the static one was — replace in place.** When the user says "the old static terminal is still in its old spot, that's where the interactive one should be," they mean a page can hold TWO terminal-like elements: a static decorative visual (a rendered `d-device` console mock in the hero) AND your new interactive mount placed elsewhere (appended mid-page). The fix is: remove the static visual, mount the interactive one at that exact position (after the hero, in the original flow), and remove any standalone section you added. Verify exactly one `#askterm` in the served DOM and zero `d-device`/static markers. Also: after any markup surgery, check div balance (`grep -c '<div'` vs `'</div>'`) per region — nested-div walks fail on unclosed blocks and browsers auto-close silently, so count opens/closes and trace the unclosed stack before committing.

## Pitfalls

- **Vercel tokens expire (~24h).** A stored raw token fails with "Not authorized" mid-project. Run `vercel whoami` WITHOUT `--token` — the CLI auto-refreshes its own session. Don't cache tokens across days.
- **CLI deploys land on whatever project the workdir's `.vercel/project.json` links to** — check it before deploying from a reused directory.
- **Leftover projects/domains from killed sessions** linger in the Vercel team; audit `v9/projects` + each project's domains before assuming a domain is free.
- Domain migrations leave users staring at dark domains mid-swap; keep the old binding serving until the new one verifies.
- **Byte-identity ≠ correct rendering:** verified-clean asset files can still ship wrong when the HTML reference chain points at a retired/stale asset (a page referencing an old derived logo). Verify the served DOM's reference chain — curl each page and grep the refs — not just the asset hashes.
- **The two-tree trap:** with multiple versioned copies of a build (`vers/vN` mirrors), edits silently land in the wrong (stale) tree — every agent in the reference project burned a cycle on this. Confirm the canonical path against STATE.md before editing; STATE.md must name the exact real path, not a near-identical one.
- **MANIFEST.sha256 must be root-relative to the build directory** so `shasum -c` passes from inside the build — a manifest that only resolves from the workspace parent is a fragile artifact.
- **Confirm the deploy mechanism before assuming push ships:** git-link auto-deploy requires the Vercel GitHub App; this project deploys only via `vercel --prod` CLI. Record the mechanism in STATE.md.
- **CSS-hidden elements still cost mobile perf if their JS runs.** `display:none` on mobile does not stop a `<script>` from parsing and executing — an interactive hero widget hidden on phones dropped mobile Lighthouse 15 points (93 → 78) twice in the reference build, once for the responder and once for its load-time animation. Gate the script itself by viewport (`matchMedia('(max-width: 820px)').matches` early-return + `defer`), and gate any auto-play animation the same way. Never rely on CSS visibility alone for a perf-sensitive widget.
- **Rebase incremental feature edits onto the version that actually carries the feature.** In the reference project the terminal-carrying build lived in one commit (`23cac17`) while a parallel base build lacked it; an edit written to the base and copied over the root silently overwrote the terminal and it had to be rebuilt from the feature commit. Before editing a file, confirm which version of it holds the feature you are extending — `git log -S "unique-marker" -- <file>` finds the commit that introduced it. The wrong-base copy is a sibling of the two-tree trap above: both silently discard work.
- **Never batch-copy a subdirectory `index.html` over the root `index.html`.** In a multi-file sync (`cp vers/vN/digital/index.html digital/index.html && cp vers/vN/index.html index.html`), a careless `cp digital/index.html index.html` from the wrong source silently replaces the LANDING PAGE with a sub-page — the user's exact words were "the landing page, the one thing I loved, is gone." A batch command with `rm`/`cp` can also trip the approval gate and stall. Sync the root page with an explicit single copy (distinct source and destination), then VERIFY the root still carries its identity markers (`gw-hero`, `askterm`, split-half classes) before committing. Recovery when it happens: restore from git — `git show <known-good-commit>:index.html > index.html`, redeploy, verify markers — the fix that worked in the reference project. This is the single most destructive variant of the two-tree/wrong-base class because it hits the most-loved page with no error message at all.
- **Never fabricate metrics for a real client site.** A count-up stats strip of invented MW / facilities / capital-raised figures is a liability the client would have to disclaim later, and it sits incoherently next to an honesty guard. Consensus ruling: hold the numbers until the client supplies real figures; ship honest capability language ("data centres from feasibility through commissioning") instead. The only thing standing between a site and a real count-up strip is real numbers from the client — say so explicitly rather than inventing them.
- **CSS percentage-height feedback loop inside a grid.** A decorative element with `height:120%` (e.g. a vertical divider) inside a grid with auto rows loops: the divider forces the row taller, the row feeds the 120% → the row balloons (1624px instead of 100vh) and content below the fold disappears. Symptom: one grid child's content sits ~870px below its sibling's though both are in the same row. Fix: fixed/100% height on the percentage element, or `overflow:hidden` on the grid — and when the row is still wrong, scan descendants for any element >1000px tall to find the loop source. Also check DOM structure: a grid child accidentally NESTED inside another grid child (from markup surgery) produces the same ballooned-row symptom; the fix is making all columns direct grid children with balanced divs.
- **Read the user's layout intent from WHAT they liked, not the accident they screenshotted.** When a user says a screenshot "gave the interesting elements more vertical space" and the team rebuilds a whole new column structure off the accident, the user corrects: "the layout was still 2 columns — the flavour elements just got more room." The durable lesson: flavor/interactive elements (terminal, pipeline tracker) earn dedicated columns INSIDE their half (`[content | terminal]` on one side, `[pipeline | content]` on the other, so the two flavour elements flank the center divider and content stacks sit on the outer edges — a true mirror), while the Digital/Physical half boundary stays sacrosanct. Ask what the user liked about the screenshot before adopting its structure wholesale.

## References

- `references/{CLIENT}` — full case history: failure modes, fixes, verification gates.
- `references/{CLIENT}` — universal command map, shared terminal component shape, gateway mirror structure, and the incident log (root clobber, false rollback, giant-anchor, grid loop, static-vs-interactive mount).
- `scripts/self-host-google-fonts.py` — download latin woff2 subsets from Google Fonts css2 (one static file per weight) and print ready-to-paste `@font-face` declarations.
