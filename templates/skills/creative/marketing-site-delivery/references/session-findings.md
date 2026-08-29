<!-- GENERICIZED: 5×{CLIENT}, 1×{RELATIONSHIP} | source: skills/creative/marketing-site-delivery/references/session-findings.md -->
# Session findings — {CLIENT} site build ({CLIENT}, Aug 2026)

Condensed incident log behind the rules in SKILL.md.

## Incidents → rules

1. **Fake PNGs**: three `mats/` "PNGs" were JPEG-encoded (RGB, zero alpha, baked checkerboard) despite extension. PIL check caught it. → Verify pixels, never trust extensions.
2. **Impostor duplicate**: `logos/{CLIENT}` (2048×2048 RGB checkerboard baked) vs clean `assets/{CLIENT}` (1463×1273 RGBA). Two agents reported contradictory facts; both were right about different files. Hash comparison settled it. → Declare one source-of-truth dir; settle conflicts by hash.
3. **White-on-white**: `.glass` component written for dark surface reused on light body sections — translucent white over #f7f8fb + hardcoded `.glass h3{color:#fff}`. → Surface-contract variant classes.
4. **SPA router disease**: single index.html with `showArm()`/`route()` handling pathname + legacy hash + replaceState + canonical rewriting. Division URLs 404'd, then rewrite layer added more machinery, then pages "not loading properly" entirely. Rebuild as three real files fixed everything at once and shipped smaller. → Multipage static under ~10 pages.
5. **Stale-copy trap**: build announced at path A but actually lived at path B; the copy at A was stale v3 with failing manifest checksums and would have been deployed by anyone resuming from STATE.md. → Quarantine stale copies with `-STALE` suffix rename (never delete); keep STATE.md pointing at real paths.
6. **Vercel domain binding collision**: killed session had moved apex A record before anything served; `www` stayed bound to an old project, silently blocking claims. {CLIENT} went effectively dark mid-migration. → Enumerate all project domain bindings first; create+verify destination BEFORE releasing old bindings.
7. **Lighthouse 69 mobile on production** despite clean local build: hero PNGs 800KB–1.4MB. WebP `<picture>` variants → 96. Inner pages still served raw PNGs — optimizer pass must cover all pages.
8. **Missing og tags** found only in final visual pass — canonical present, Open Graph absent on every page. Shared links rendered bare.
9. **Physical page missing its display typeface**: spec called for condensed industrial headline face; built with body font only, so the "different register" page read as same-design dark mode.
10. **Contrast fix pattern that worked**: luminance-targeted lift (only L<110 pixels scaled ~1.9× toward brighter blue, hue preserved, alpha untouched) took avg opaque-pixel luminance 62→110, verified visually as same logo. Manifest-logged in assets/derived/.

11. **Vectorization had to be verified, not trusted**: PNG→SVG via vtracer (3 marks, 401/1091/755 paths, zero raster embeds — {RELATIONSHIP}'s report held up). The decisive check was rasterize-and-vision: cairosvg failed on macOS (`cannot load library 'libcairo.2.dylib'`, DYLD_LIBRARY_PATH ignored by ctypes); `qlmanage -t -s 720 -o . file.svg` worked with no deps. Rendered pass confirmed gradient + fine network-nodes/circuit-traces survived. Also: SVGs served at `/assets/svg/`, not `/assets/` — first `?v=1` fetch to the wrong path returned 79-byte NOT_FOUND.

12. **CSS cache gap — the recurring one**: pipeline collapsed to run-on `SPECspecificationC34 grade` because the browser held OLD unversioned `gateway.css` (4h TTL) against NEW HTML (new spans). Images had `?v=`; the stylesheet that carries layout had none. → Version CSS/JS refs in the SAME commit as the layout change, not after. This class (user sees stale layout; teammate "verified dead" vs "verified live" arguments) recurred at least four times before the structural fix.
13. **Interactive terminal shipped un-presented**: `try /build supply chain /fund 5M raise /source` concatenated, orphaned `c34 steel`, floating ghost `$ /build supply chain`, `$ test` (the author's own functional-test residue persisted as seed), plain detached `<input>`. User: "weird text." Not cache — the flagship was built *functional* but never *presented*. Fix: device chrome + 3 clean seed lines + styled in-device input. The `--help` em-dash typo (`—help`) was a real typographic bug.
14. **Fabricated-stats trap (averted)**: proposed a count-up strip of plausible MW/hash-rate/raised-capital figures for "flair." Team ruled it out — invented credentials next to an honesty guard is incoherent and a live-site liability. Shipped an honest capability line instead; real numbers await the client. → Never invent stats on a consulting site; "make it impressive" ≠ "invent evidence."
15. **Hero emptiness = composition, not texture**: digital hero was ~65-70% dead space, flat navy. Adding Physical's grid doesn't work (reads on light, invisible on navy). Fix = right-side balancing element (terminal motif) + light-stroke grid at visible opacity. Left-aligned text column alone leaves the dead zone.
16. **Contained-card rule is blanket**: 4 middle cards contained/rounded, but quote strip + how-it-works + contact stayed full-bleed edge-to-edge bands — exactly the "awkward" inconsistency. Fix = every dark surface below the hero is a contained card with the same rhythm.
17. **Persistent cross-page nav**: user "no clear way to navigate between divisions." Header switch button added, then extended to footers (scroll-past users).

## Exemplar sites used to set the bar

Aalo (narrative scroll cascade), Palantir (outcome carousel), Anduril (industrial mono register), bshiyat (numbered capability blocks). Flatlogic repos rejected for brand-site work — they ship admin-dashboard scaffolds (SaaS back-office patterns), wrong grain for marketing pages.
