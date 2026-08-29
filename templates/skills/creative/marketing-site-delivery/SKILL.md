<!-- GENERICIZED: 1×{AMOUNT}, 7×{CLIENT} | source: skills/creative/marketing-site-delivery/SKILL.md -->
---
name: marketing-site-delivery
description: Use when building or shipping a marketing website.
---

# Marketing Site Delivery (team builds)

## When to Use

Building, reviewing, or deploying a client brand/marketing site (multi-page static, Vercel/GitHub Pages class); auditing logo/asset files entering a web build; diagnosing "site looks broken live" reports; running domain migrations or auto-deploy pipelines for team-built sites.

Class-level playbook learned on real deploys ({CLIENT}). Covers architecture decisions, asset discipline, QA gating, and the failure classes that recur.

Class-level playbook for taking a brand/marketing site from spec to live production, learned on real deploys ({CLIENT}). Covers architecture decisions, asset discipline, QA gating, and the failure classes that recur.

## Architecture: multipage static beats SPA shells

For any site under ~10 pages, ship **real files per page** (`/index.html`, `/digital/index.html`, …) with plain `<a href="/digital/">` links.

**Never** hand-roll a JS router on a single shell page. The failure mode (seen in production): one `index.html` serving three URLs via `showArm()`/`replaceState` juggling hashes + rewrites + pathname fallbacks. Every bug that shipped — white-on-white text, dead division pages, canonical confusion — traced to that machinery. Multipage costs *less* code, works with JS disabled, and canonical/meta are trivially correct because they're just files.

If clean URLs are needed anyway: `vercel.json` rewrites serve `index.html` per path; legacy paths get 308 redirects landing on rewrites, not hashes.

## Asset discipline (the checkerboard trap)

- **PNG with alpha or nothing.** JPEG cannot store transparency; a `.png` extension proves nothing — verify with PIL (`im.mode == 'RGBA'`, alpha extrema includes 0). Three of six "PNGs" in one real project were JPEG-encoded fakes.
- **Duplicate asset directories accrete impostors.** Two files named `{CLIENT}` coexisted: one true-alpha, one 2048×2048 RGB with baked checkerboard. Settle conflicts with `shasum -a 256` across every candidate path — never argue from memory.
- **One source-of-truth directory** (`assets/`); everything else (`mats/`, `logos/`, `vers/`) is reference-only. QA verifies builds reference zero outside files via manifest diff.
- **`MANIFEST.sha256` written at build time**; QA diffs against it.
- **Source assets immutable.** Derived variants (e.g., brightness-lifted logo for dark backgrounds) go in `assets/derived/` with their own manifest entry. Never flood-fill/mutate originals mid-build — anti-aliased edges leave halos.
- Viewer screenshots show checkerboard behind transparent PNGs — that's the transparency indicator, not baked content. Verify pixels before "fixing" anything.
- **Canonical artwork replacement — retire ALL derived variants of the old mark.** When a client ships a "backless" replacement logo, first check whether it's the SAME mark at higher resolution or a genuinely DIFFERENT artwork (compare motifs, don't assume size-only — a user's "here's the right logo" was a different faceted-A design, not a bigger copy). On swap: grep every page for stale references to derived variants of the OLD artwork (`assets/opt/*.png`, `-light`, `-v2`) AND retune any CSS palette baked from the old colors — the rejected mark kept shipping in production via a stale `assets/opt/{CLIENT}` ref even after the main asset was replaced. Archive superseded marks to a `vers/` archive, never delete mid-project. Add `?v=` cache-bust to the new refs so stale browser caches can't serve the old mark.

## Vectorization fidelity (PNG→SVG)

When converting brand marks to SVG (vtracer etc.), auto-tracing is the one step that can silently flatten what the original preserved. **Always verify the vector, not just that it exists.** Fidelity-check workflow:

- **Prove it's a real vector, not PNG-wrapped-in-SVG**: zero `base64`/`<image>` raster embeds; sane `<path>` counts (tens to ~1100 for complex marks); no `<img>` self-references.
- **Rasterize and vision-check the SVG** — this is the definitive fidelity test. Gradient banding/flattening, and fine detail loss (network nodes, circuit traces, gear teeth) only show up in a render, never in the XML. cairosvg (Python) is the common route but **fails on macOS without libcairo** (`cannot load library 'libcairo.2.dylib'`), and `DYLD_LIBRARY_PATH=/opt/homebrew/lib` does NOT fix it — cairosvg's ctypes ignores the env var. **Working macOS fallback: `qlmanage -t -s 720 -o . file.svg`** (Quick Look renders SVG natively, no deps) — produces `file.svg.png` for vision_analyze.
- **Serve-location pitfall**: SVGs may live at `/assets/svg/` rather than `/assets/` — a `?v=1` fetch to the wrong path returns a ~79-byte NOT_FOUND. Grep the live DOM for the actual `src` before fetching.
- Vision-check both the divisional mark AND the master mark (the fine-trace one is the real risk — nodes/circuits usually die first). See `scripts/verify-logo-svg.sh` for the mechanical checks.

## Component contracts

Any shared visual component (`.glass` cards etc.) **declares its surface contract explicitly**: variant class per background (`.on-light.glass`), no defaults assuming a dark/light surface. Translucent-white-on-light = invisible card + hardcoded white headings = the classic white-on-white bug. Scope color overrides to the variant, never global.

## Flair = interactive proof, not decoration; honesty is non-negotiable

"Blow them away" / "we can do the impossible" asks are answered by an *interactive proof moment*, not more decorative motion.

- **Best cheap form: a parameter-driven responder**, not a canned script. User types a domain ("/build supply chain", "/fund 5M raise", "/source c34 steel") → the terminal "responds" with a plausible engagement path from a client-side lookup table. A fixed `$ {CLIENT} deploy` script reads as decoration; a system responding to *their* input reads as capability. Full command set discoverable via `/help`. Pure client-side (zero network — this is a marketing site), `prefers-reduced-motion` renders instantly, hidden entirely on mobile.
- **Honesty guard on every demo.** End each response with "→ scheduled: intro call — we map this to your actual situation." A consulting brand that sells judgment must never fake a diagnosis.
- **Never fabricate a stats/count-up strip.** Plausible-feeling counters (MW commissioned, capital raised) beside an honesty guard is incoherent, and fabricated credentials are a live-site liability. Either real numbers the client supplies, or honest capability language ("data centres from feasibility through commissioning") — never invented counters. "Make it impressive" does not authorize inventing evidence.
- **Interactive demos must be presented, not just functional.** A working terminal that ships raw seed content reads as broken code: never ship the author's test residue (`$ test`), never concatenate a `try /build… /fund… /source…` run-on hint, keep seed state to a few clean typed lines (`$ {CLIENT} deploy --emerging-tech --funded` + `✓ ready` + a styled hint), and style the input as part of the device (inset dark field, mono, colored caret), not a detached form box. Device chrome (frame, title bar, traffic lights) + restrained content beats a wall of CLI history. This is the "presentation pass" — built *functional* is not shipped *presented*.

## Contrast on dark surfaces

Deep-navy logo strokes die on dark hero/cards. Fix by deriving a luminance-targeted light variant (lift only pixels below a luminance threshold toward brighter hue-preserving blue; pass cyan accents through), into `assets/derived/`, verified visually. Algorithmic lift ships fine; a native light export from the design tool is strictly better when available.

## Contrast on light surfaces (containers must read)

The inverse failure recurs on light themes and is easy to miss: a container whose fill nearly matches the cream/off-white background and whose border is faint renders as "can barely see the outline" — a flat white block floating on the page. This reappeared across four review rounds on the same site (dark cards passed, light cards kept failing), so fix it as a measured token, not a visual-pass finding: define a `--line-strong` token tuned so border-vs-background reads at a glance (≥1.5:1 against the warm bg — e.g. `#C9C2B2` on `#F4EFE6`) and use it on every light-theme card's border, plus a visible shadow. The OUTLINE is what makes a container read; a low-contrast border is indistinguishable from "no container," no matter how much rounding it has.

## Responsive system (full-width fluid; mobile is non-negotiable)

Users of this class of site repeatedly reject fixed-width pixel cages ("containers look archaic") and any non-responsive mobile ("horrible on mobile is unacceptable in the modern day"). Treat responsive as a *system pass*, not a patch:

- **Fluid containers, not fixed-width cages.** `.section { width: min(100% - 48px, 1200px); margin-inline: auto }`, `.section-narrow` at an ~840px cap. Kill stacked fixed caps (a real build had six: 1120/840/680/640/620/520px) that leave side gutters at every window size. Keep the *container* non-clamped; put `clamp()` on the **type scale** instead (`clamp(28px, 5.5vw, 48px)` hero, `clamp(96px, 18vh, 160px)` hero padding) so text and spacing scale with the viewport.
- **Real mobile tier, not skeletal.** Breakpoints ≤900 (2-col grids → 1fr) → ≤720 (stacked, touch targets ≥44px, compact CTA-only nav — desktop-width nav must not appear on a phone) → ≤560 (1-col, smaller gutters). Add `overflow-x: clip` on body so nothing overflows horizontally. **Verify each page-specific sheet has its OWN mobile breakpoint** — a page that only inherits `system.css` fallbacks stacks but keeps desktop type size (functional, not intentional); add a per-page mobile hero type step-down (`clamp(30px, 8vw, 44px)` under 720px).
- **Mobile-emulation capture pitfall — verify computed styles, not stale screenshots.** A `Page.captureScreenshot` taken *before* the emulated viewport applies renders the DESKTOP layout — a "2/10 split-screen on mobile" verdict from such a capture is a harness artifact, not a bug. Before judging a responsive state: (1) confirm the media query is in the served CSS (cache-busted); (2) read computed styles at the emulated width — `getComputedStyle(hero).flexDirection === 'column'` proves stacking objectively; (3) only then screenshot. In CDP, set `Emulation.setDeviceMetricsOverride` BEFORE navigating, and persist via `Page.captureScreenshot` base64 (the CLI `capture_screenshot` helper may not write a file). Note the emulated viewport can report a larger `innerWidth` (e.g. 437 at width=390) — check the media query still matches.
- **Audit bar for this client**: user measures against Palantir / bshiyat / Aalo / Anduril — monoline-sans, dark-tech, proof-dense landing pages. A gateway that is "two anchor halves and one H1" is objectively underbuilt (bshiyat: 1 H1 / 7 H2 / 22 H3 / 8 sections / 23 links). If a page has a hero and nothing beneath it, that is a content-depth gap, not a styling miss — the fix is more sections (benefits → how-it-works → proof → FAQ → final CTA), not more styling.
- **Hero emptiness is a composition gap, not a texture gap.** On a dark hero, texture/grid is invisible (`rgba({AMOUNT},.06)` grid reads on a light page but dies on navy). Filling the "~70% dead space" needs a **right-side balancing element** (rendered product visual / terminal motif / orbital diagram) PLUS a light-stroke grid at visible opacity — a left-aligned text column alone leaves the emptiness users flag. Left column stays; the dead zone fills with intent.
- **Contained-card rule is blanket, not piecemeal.** If the middle cards are rounded contained cards, EVERY dark surface below the hero (quote strip, how-it-works, contact CTA) must be a contained card with the same radius/margin rhythm — a site mixing 4 contained cards with full-bleed edge-to-edge bands is exactly the "awkward" users keep flagging. No full-bleed dark bands inside a light page.
- **Persistent cross-page navigation.** On multi-surface sites, put a persistent switch button to the sibling surface in the header AND mirror it in each page's footer — users who scroll past the header otherwise lose the path.

## Design-intelligence upgrade pass (ui-ux-pro-max generator)

When the client asks to "upgrade the web design" and a design-intelligence skill (ui-ux-pro-max) is installed, drive it as a *layer on top of locked brand DNA*, never a replacement:

- **Run the `--design-system` generator for the product.** A consulting/enterprise hybrid resolves to the **Trust & Authority + Conversion** pattern (section order: Hero mission/credibility → Proof → Solution overview → Clear CTA). Persist it to the workspace root (`--persist --output-dir <project-root>` writes `design-system/<slug>/MASTER.md`, retrievable across sessions). Invoke skill scripts by ABSOLUTE PATH — Hermes has no `CLAUDE_PLUGIN_ROOT`, and run from the skill's `scripts/` dir so `from core import …` resolves.
- **Client's explicit non-negotiables override the skill's output, always.** The terminal, split-gateway, and locked palette/type are sacred; the skill refines the *layer above* them. Concrete v6 outcome: skill recommended Plus Jakarta Sans body (kept the client-locked Rostex wordmarks), SplitText hero headline reveals, and a Proof band — all applied without touching the terminal or split-screen.
- **Real-proof band satisfies "proof right after hero" without fabricating stats.** The Trust & Authority pattern wants credentials after the hero; when no real numbers exist, use the site's actual portfolio deployments (live portfolio links) as visible proof — the honest analog of a stats strip.
- **SplitText / headline-reveal guard**: animate headlines only (≤8 words), never long paragraphs; split-revert on cleanup; `prefers-reduced-motion` renders final state instantly.

## Load-animation sequencing check

Two load-triggered animations on ONE hero (e.g. a headline cascade AND a device auto-typing its content) can read as chaos on first paint if they overlap. Don't assume — verify the timing relationship: capture ~1s and ~3.5s after load and confirm the headline settles BEFORE the device types (cascade first, device after it lands). The reduced-motion guard covers that case; the open risk is normal-load overlap, which a mid-load screenshot catches. If they collide, stagger: cascade, then device.

## Render-harness fallback (don't loop a flaky capture tool)

When the CDP/browser capture harness is flaky (js `scrollTo` times out, `PageDown` doesn't advance the capture, or captures keep returning only the fold), STOP retrying the harness and fall back to served-bytes + computed-style verification — the same evidence the computed-style gate amendment relies on. A fold-only screenshot is not proof of a mid-page state either way; a fresh curl of the versioned CSS + a `getComputedStyle()` read is. Don't burn review cycles re-triggering a tool that isn't giving you the pixels.

## Deploy chain protocol

- **Micro-stages**: each stage = one bounded command batch (≤2 min) ending in a STATE.md write + report. Timeouts under batching discipline mean task granularity is wrong, not agent discipline.
- **Persist state to disk as you go** — any session resumes mid-task after cutoff.
- **Diagnose-first before rebuilds**: reproduce the live failure server-side (curl status, served HTML inspection) before discarding architecture; two minutes of diagnosis prevents rebuilding around the wrong cause.
- **Staging-first review loop (client directive).** Deploy every new version to a staging subdomain (`staging.{CLIENT}`) and WAIT for the client's review before promoting to main. Sequence: build → staging → QA + visual pass on staging → client review → promote. The client reviews a QA-passed artifact, never a raw build, and the main site stays on the last approved version untouched.
- **Pre-deploy root-marker guard (the cross-page-copy clobber).** A single `cp digital/index.html index.html` once replaced the gateway with a leaf page in production — a command error, not a design change. Before ANY push, guard the deploy: verify root `index.html` carries the site's gateway marker (e.g. `.gw-hero` + terminal element) and FAIL the deploy if it matches a leaf page. One grep-style check in the deploy micro-stage kills the entire class of "a page copied over the wrong target" accidents. Verify the restore (root still serves the gateway) with the same check before trusting a teammate's "restored" claim.
- **Vercel tokens expire (~24h TTL)**; CLI self-refreshes — `vercel whoami` first, don't treat auth failure as broken infra.
- **Version CSS/JS in the SAME commit as the layout change.** The asset class that carries layout is the one that must be cache-busted. Versioning only images (`?v=`) while leaving `/gateway.css` unversioned is the gap that repeatedly shipped stale-layout complaints: assets carry `cache-control: public, max-age=14400` (4h TTL), so an unversioned stylesheet change is invisible to browsers for up to 4h — they render NEW HTML against OLD CSS → run-on/collapsed text ("SPECspecificationC34 grade"). Every deploy that changes layout bumps the CSS/JS ref (`/gateway.css?v=<sha>`) in the same commit, not after. If a fix changes layout, the version bump ships with it.
- **Domain migrations, order matters**: create destination DNS + verify it serves BEFORE releasing the old binding; enumerate every project's domain bindings first (stray bindings from killed sessions block claims silently).
- **Private-repo constraint is a gate item**: confirm repo visibility via API before pushing if privacy was required.
- **Performance gate**: mobile Lighthouse ≥80 against PRODUCTION, not local. First offender: unoptimized hero PNGs (800KB–1.4MB) — WebP variants behind `<picture>` took 69 → 96. Apply the same optimizer pass to inner-page images, not just heroes.

## Launch checklist (per page)

- Per-page `<title>`, meta description, `<link rel="canonical">`
- Open Graph + Twitter tags (`og:title/description/image`, `twitter:card=summary_large_image`) — absent og tags render shared links as bare URLs
- Division-specific display typeface actually loaded (a "different register" page using only body font reads as same-design dark mode)
- **Favicon uses the current mark.** After a rebrand or artwork swap the favicon is the first thing to drift and the easiest to forget — a stale favicon ships the retired logo in the browser tab (and often is only caught by the client). Grep the served `rel="icon"` target and confirm it carries the current artwork, not the old silhouette.
- **Presentation integrity, not just structure** — a gate that checks structure ships raw scaffold as "weird text." Verify no unstyled/raw copy is visible: a terminal shipping its author's test residue, a concatenated `try /build…` hint, or a bare abbreviation with no legend (`SPEC`/`SRC`/`NEG`/`DLV` with no full-word labels) all read as debug text to the lay audience the page converts. Interactive demos keep seed state to a few clean lines; cryptic labels get full-word legends.
- Hard refresh / cache-busting check before reporting visual fixes live
- **One primary CTA per surface, verify hrefs DIFFER** — a "Book" button next to an "Email" button that both mailto the same address is a QA slip; on multi-surface sites conversions live only on leaf pages, the gateway converts on the choice and carries no competing CTA
- **Audits must read fresh, cache-busted production bytes.** Teammate audit reports that "X isn't live" have repeatedly been stale-cache false alarms on real fixes, and vice-versa. Before either trusting a teammate's "verified dead" OR declaring a fix shipped, curl the served HTML/CSS fresh (include `?v=` on the asset, confirm the CSS path is the real one — e.g. `/digital.css` not `/digital/digital.css`) and grep for the actual token/ref. Verify against served bytes, never against a report or the workspace tree (which may be a stale duplicate copy).
- **"Class applied but not styled" — the bytes-check that lies.** A shared component class can be present in BOTH the markup AND the CSS yet still render as a flat rectangle, because the CSS rule sets only padding/position (`padding:40px 24px`) and omits the visual treatment (border-radius, background gradient, border, shadow, accent line). Grepping for the class NAME in served HTML+CSS passes while the visual fails — exactly how a "plain rectangle" survived a green bytes-check after a container-refactor claimed to fix it (`.card-warm`/`.card-dark` wrapped the right elements but carried no card styling). Always verify the RULE's actual properties, not just the class's presence, AND render + screenshot the section — a class in markup and CSS is not proof the component looks like a component. **The mirror trap — the grep FALSE alarm.** Grepping a class can also produce the opposite failure: `.card-warm{...}` in the served CSS may show only `padding:40px 24px;` when that is a `@media(max-width:720px)` OVERRIDE sitting after the full base rule (which carries the real radius/gradient/shadow/border). Reading the override as the whole rule and raising a blocker off it stalled a promotion twice in one project. When a grep shows a class as "hollow," read the FIRST/full non-media base rule (or check computed style) BEFORE raising anything — the same grep-partial-match habit produces both false-pass AND false-alarm. And when you DO raise a correct finding (a genuinely hollow class), say it plainly and own it if you later got it wrong — the correction, not the blocker, is the contribution.

## References
- See `references/session-findings.md` for the condensed incident log these rules came from.
