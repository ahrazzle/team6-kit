<!-- GENERICIZED: 3×{CLIENT} | source: skills/marketing-site-production/SKILL.md -->
---
name: marketing-site-production
description: Use when building or iterating marketing/brand sites.
---

# Marketing Site Production

Class-level playbook for building and iterating marketing / consulting / brand websites (static HTML/CSS/JS, no backend). Distilled from a multi-round consulting-firm site build ({CLIENT} at {CLIENT}) where repeated user corrections exposed durable rules.

## When to Use

- Building or rebuilding a marketing, landing, or brand site
- Iterating on a live site after user design feedback
- Choosing site architecture (router vs multi-page) for a content site
- Any deploy of a static site to Vercel / Netlify / Pages

## Architecture: multi-page static over SPA router

A hand-rolled JS router juggling hashes, pathname rewrites, and replaceState is the recurring bug class on marketing sites (white-on-white, dead division pages, canonical chaos all traced to it). **Build real files**:

- `/index.html`, `/digital/index.html`, `/physical/index.html` — one real page per route
- Plain `<a href="/digital/">` links; zero routing code; works with JS disabled
- Per-page `<title>`, meta description, canonical — trivially correct because each is a file
- Shared `system.css` (tokens + components) + one page-specific sheet per route
- **Component surface contract**: every shared component declares its surface explicitly (e.g. `.on-light.glass` variant); no defaults that assume a background — prevents the invisible-card bug class

## Design QA checklist (user-verified corrections)

Embed these from user feedback; they recur:

1. **One primary CTA per surface.** Two buttons pointing at the SAME href (e.g. duplicate mailto) is a QA slip — verify hrefs differ and only one primary action per page.
2. **Topbar/nav spacing.** Group links with explicit gaps (`.nav-links` gap), separate the CTA with real margin, add hover transitions. Ambiguous boundaries between buttons read as broken.
3. **Card integration.** Cards look "jarring" when they float: use hairline rgba borders (~6%), larger radius (20px), a resting shadow, and a hover lift + deeper shadow. Cards must sit IN the page, not on it.
4. **Hero background depth.** A flat color hero reads as "plain and empty". Layer radial glows + a masked grid overlay (mask-image radial, fading out below the fold). Content stays readable; the surface has depth.
5. **Type system.** One family for the whole site (skill-approved: Geist/Manrope/Poppins). A display face (e.g. Rostex) is allowed ONLY for brand wordmarks in the header; everything else stays the system family.
6. **No AI cliches in copy** ("Elevate", "Seamless", "Unleash"); specific numbers over vague verbs; sentence case.

Full CSS recipes for items 2–4 in `references/design-qa-checklist.md`; v5.2-round recipes (fluid containers, mobile tier, split-axis, flagship widgets) in `references/responsive-and-flair-pass.md` — load before the build/QA pass.

7. **Fluid containers, not fixed cages.** Six nested `max-width` px caps (1120/840/680/640/620/520) read as "archaic" and "clunky". Sections span the viewport with gutters: `width:min(100% - 48px, 1200px); margin-inline:auto`. Display type uses `clamp()` so it scales with the window.
8. **Real mobile tier.** "Looks horrible on mobile is unacceptable in the modern day" — a skeletal breakpoint set is not responsiveness. Three tiers minimum: ≤900px (grid collapse), ≤720px (stacked layouts, nav links collapse to CTA-only, fluid hero padding), ≤480px (type steps down, `overflow-x:clip` guard on body, touch targets ≥44px). Gate MUST include a mobile emulation pass at 390px — a desktop-only gate ships broken mobile.
9. **Split-hero axis agreement.** When a hero is split into two halves with different background colors, the halves' flow axis and the background gradient axis MUST agree: `flex-direction:row` halves need a `90deg` (horizontal) background; `flex-direction:column` needs `180deg` (vertical). A mismatch (horizontal bg + vertical halves) puts white text on the dark half and dark text on the light half — unreadable cross-contrast.
10. **Flagship proof-of-capability moment.** User: "if people are going to pay us for our technological skills, our website has to blow them away... hit with the understanding that we can do things which to them are impossible." Decorative motion is not enough; the hero needs a capability proof — terminal-style deploy log with checkmarks, pipeline/progress tracker, live data viz. Pure CSS/HTML, hidden on mobile where the split stacks.
11. **Critical UI is visible by default; JS only enhances.** Gating the flagship terminal behind `<body class="no-js">` + `.no-js .term{opacity:0;visibility:hidden}` left it invisible in the user's browser whenever the class-removal JS lost the race — repeatedly, and each time the "container missing" complaint returned. Fix structurally: render the terminal visible on first paint and let JS add behavior (auto-type, commands, LLM). Any flash-guard that inverts visibility (visible only if JS runs) is a permanent-hide bug waiting to happen.
12. **Interactive terminal: click-split + shared component.** (a) The terminal's click focuses the input and NEVER navigates (`stopPropagation`); navigation lives only on a separate "Enter" anchor. The whole-panel-`<a>` giant-anchor bug made every terminal click enter the site — and it survived two "fixes" until the panel became a `<div>` structurally. (b) Build the terminal ONCE as a data-driven component (command map = single source of truth driving both dispatch and `/help` output), mount it per context. Copies drift; one gets fixed while the other doesn't.
13. **Fonts are per-division, not just per-role.** One display face for the whole site is wrong when divisions have clashing clientele: the industrial/physical division keeps the blocky display face (Rostex); the digital/tech division gets a sleek mono treatment for wordmark + CTAs. User: "It's thick and blocky, suits the physical division but seems out of place for digital." Full interactive-terminal + LLM-assistant pattern in `references/interactive-terminal-assistant.md`.

## Screenshot gate vs reference sites

"We're at the bar" is a claim until it's a visual comparison. Deterministic protocol:

- Capture each surface at 1440px AND 390px (mobile is where the bar lives), full-page + fixed section list (hero, benefits, proof, CTA)
- Run the SAME capture protocol on the reference sites the user named
- Compare like-for-like: digital vs Palantir-class, physical vs industrial-services-class, gateway on hero/split quality
- Show the comparison to the user; do not self-report "at the bar"

## Asset pipeline

- Raster logo → SVG: see `image-to-svg-vectorization` skill (vtracer, viewBox, qlmanage QA)
- TTF/OTF font → woff2: `python3 -m fontTools.ttLib.woff2 compress X.ttf -o X.woff2`; declare with `@font-face` (use `font-style:oblique` for oblique faces); self-host; preload the main face — full recipe in `references/font-pipeline.md`
- Verify served assets return correct content-type (`image/svg+xml`, `font/woff2`) after deploy

## Deploy & verify (see also `long-run-deployment-discipline`)

- **Never assume push-to-deploy.** Confirm the platform's trigger: git integration vs CLI (`vercel --prod` from repo root). Check `.vercel/project.json`; `vercel whoami` refreshes expired tokens (24h TTL) without user involvement.
- **Verify the artifact, not the status.** "Ready" ≠ served. Poll for a new/changed asset from this release (font, svg) to return 200 with correct content-type; grep served HTML/CSS for expected markers.
- **Cache-bust every gate verification** (`?cb=<deploy-sha>` appended to HTML/CSS requests). Without it, "stale bytes vs live bytes" disputes recur — this class cost three verification rounds in one project. Make the probe deterministic; the gate fetches through the cache-buster by default.
- **Verify against SERVED bytes, not local source.** The project's #1 recurring failure class: code verified locally (or by grep on the build tree) while the user's screenshot showed the bug — "fixed" claims were contradicted by the user's reality at least four times. Discipline: after any deploy, curl the live/staging URL WITH a cache-buster and grep for the fix's markers; for interaction claims, drive a real browser on the live URL (click, type, read computed state). A local-source read is never the truth for what a user sees.
- **Staging is a separate project, not a branch.** On Vercel, `staging.<domain>` was its own project (e.g. `{CLIENT}`) while the repo linked to the production project. `vercel --prod` from the repo deploys ONLY to the linked project — pass `--project <staging-project>` explicitly or staging never receives the build. Env vars are scoped per project: a key added to production does NOT exist on staging (staging's `/api/ask` returned 503 until its own env var was added).
- **Deploy-target lock.** One unauthorized push to live (intended for staging) caused a full incident round and a rollback. No deploy command runs without an explicit target (live vs staging) and a second agent's confirmation. This is the hard boundary that prevents the class.
- **Pre-deploy guard.** Before any push, a scripted check that the root page carries its expected marker (e.g. `.gw-hero` + terminal id) and FAILS if it matches a sub-page — catches cross-page copy accidents (`cp digital/index.html index.html`) before they reach a user. Cheap, permanent, and it caught its own class within a day of being wired in.
- **Environment swaps revert approved fixes.** Rolling live back to an approved commit and staging forward to a working commit silently reverted two already-approved fixes (click-split, CTA contrast) because the baseline didn't record what it contained. When swapping environments, verify the served bytes of BOTH surfaces carry the full approved feature set, and record what each baseline contains (git tags + a line in STATE.md).
- Keep a `MANIFEST.sha256` of every built file; regenerate after each change and verify with `shasum -a 256 -c`.

## Pitfalls

- Single-page shell + JS router for a multi-audience site — always rebuild as real pages
- Duplicate CTAs with identical hrefs (QA must check)
- Per-page CSS drift — shared tokens/sheets or v6 rediscovers v3 bugs
- SVG `<source type="image/webp">` pointing at .png URLs (decode mismatch) — remove `<picture>` wrappers when swapping to SVG
- Flat hero, floating cards, cramped nav — the three most common "looks unpolished" complaints
- Split-hero axis mismatch — halves and background gradient on different axes = cross-contrast text failure (fix: row ↔ 90deg, column ↔ 180deg)
- Fixed-width section cages — use `min(100% - gutters, max)`; the page must breathe at every window size
- No mobile tier — a desktop-only QA pass ships a "horrible on mobile" site; mobile emulation is a gate requirement
