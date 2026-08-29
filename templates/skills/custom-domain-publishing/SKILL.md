<!-- GENERICIZED: 7×{CLIENT} | source: skills/custom-domain-publishing/SKILL.md -->
---
name: custom-domain-publishing
description: Use when pointing a domain at GitHub Pages or Vercel.
---

# Custom-Domain Publishing (registrar → Cloudflare → Pages)

Validated end-to-end {CLIENT}: Squarespace registrar → Cloudflare DNS → GitHub Pages root + subdomain, driven entirely through browser-harness CDP on the user's logged-in Chrome. Full provider-specific detail lives in `references/cloudflare-squarespace-pages.md`.

## Standard flow

1. **Cloudflare zone**: dashboard → Domains → "Add domain" → Connect a domain → Free plan. Zone list/create works via `dash.cloudflare.com/api/v4/zones` fetch with `credentials:'include'`. Note assigned NS pair (e.g. `konnor`/`marjory.ns.cloudflare.com`).
2. **Registrar NS switch**: prefer the registrar's internal REST API over its UI (UI panes often fail to render). Squarespace pattern below.
3. **DNS records**: delete stale A/AAAA at apex/www, add Pages IPs `185.199.108-111.153` (A, @) + CNAME `www → <user>.github.io`. Preserve email records (MX/SPF/DKIM) always.
4. **GitHub side**: `gh api -X PUT repos/<o>/<r>/pages --input - <<< '{"cname":"domain","build_type":"legacy","source":{"branch":"main","path":"/"}}'`. Subdomains: same call with `sub.domain.com`, plus one CNAME record per subdomain.
5. **HTTPS**: works immediately via Cloudflare edge cert even while GitHub's own cert provisions. `https_enforced:true` returns 404 "certificate does not exist yet" until GitHub's DNS check completes (minutes–24h); retry later. Never block delivery on this flag.

## Pitfalls

- **Cloudflare dashboard API bot-wall**: GETs succeed from page-context fetch, but DELETE/POST return 403 HTML. Do record mutations through UI clicks, not the API.
- **Cloudflare Add-record form**: Type is a custom combobox (click button showing current type, pick `[role=option]`). Name input has placeholder `Use @ for root`; CNAME target is a TEXTAREA (`E.g. www.example.com`), not an input. After Save, verify by reloading — the record list renders stale counts.
- **OneTrust cookie modal** overlays Cloudflare pages and swallows clicks — dismiss (`#onetrust-accept-btn-handler`) before clicking anything.
- **React inputs**: set value via prototype native setter + dispatch `input` event; plain `.value=` is ignored.
- **Squarespace deep pages** (`/dns/domain-nameservers`) sometimes render only the sidebar; SPA-nav from a rendered sibling page first, or use the API.
- **Verify with `dig NS <domain> +short` and `curl -sI https://<domain>`** before declaring done — propagation is often faster than dashboards claim.
- **Deterministic rebuilds hash identically**: a rebuilt asset can be byte-identical to an earlier version (same source + same pipeline). Verify staleness with mtime + mode/size before accusing "manifest not regenerated".
- **Version-directory drift**: the same build can exist at multiple paths with different ages. Before resuming or deploying from any announced path, hash/inspect what is actually there — a stale copy at the "obvious" path has already caused one near-miss deploy of dead architecture.

## Vercel domain verification gotchas (validated {CLIENT})

- **Tokens expire ~24h.** `auth.json` has `expiresAt`; a cached Bearer that worked earlier in the day can start returning 401 "Not authorized". Fix: run `vercel whoami` WITHOUT `--token` — the CLI auto-refreshes its session from the stored refreshToken, then plain `vercel deploy --prod --yes` works again.
- **Apex CNAME at Cloudflare**: allowed with proxy on — point apex AND www at the project's production alias (`<project>.vercel.app`) as proxied CNAMEs; no A records needed.
- **"Domain added to a different project" verify error** even when only one project lists it: delete + re-add on the correct project, then read the domain's `verification` array for a TXT requirement (`_vercel` host, `vc-domain-verify=<domain>,<hash>` value). Multiple domains share one TXT host with separate values. Add via Cloudflare API, wait ~20s, re-POST verify.
- **CLI deploy targets whatever `.vercel/project.json` links**, not the git-linked repo — check that file before assuming where a deploy lands.
- **Git link ≠ auto-deploy**: `POST /v9/projects/<id>/link` succeeds but auto-deploy needs the Vercel GitHub App installed; CLI deploys are the guaranteed path.
## Asset provenance discipline

- **Quarantine non-clean sources immediately.** Logos exported over a baked checkerboard (light OR dark squares in RGB pixels) cannot be converted cleanly — white-removal exposes dark squares underneath. Declare ONE source-of-truth directory (`assets/`), quarantine the rest (`logos/`, `mats/`), and rebuild RGBA derivatives by border flood-fill + edge softening rather than global color-threshold removal.
- **Duplicate same-named files in different dirs are the classic false-argument source.** Settle "which file is real" with a hash comparison across directories before any pixel surgery.
- **"Checkerboard in the logo" reports are usually the file viewer, not the file.** Before any fix: check alpha channel stats (uniform 255 = fully opaque screenshot of a viewer's transparency indicator, not a real asset) and hash-compare against the deployed bytes. The fix for viewer-composited exports is re-export from source; there is nothing to fix in CSS or assets if production hashes match clean workspace files.
- **Contrast variants of brand marks on dark UIs**: derive a luminance-targeted lift into `assets/derived/` (only dark strokes lifted toward brighter blue, hue + alpha untouched) instead of CSS hacks; keep originals untouched and manifest-log derivatives.
- **Glass-card surfaces need explicit light/dark variants.** A `.glass` style tuned for dark heroes (translucent white + white headings) turns invisible/white-on-white over light body backgrounds. Ship paired variants (e.g. `.on-light.glass`) with solid light gradient + dark text, and audit every surface a shared component lands on — this class of contrast bug ships invisibly because it looks fine in the section it was designed in.

## Clean-URL SPA routing on Vercel (validated {CLIENT})

When a single-page site serves multiple "pages" via client-side routing, hash-only routing (`#/path`) is NOT enough — typed/shared/print URLs 404. Full pattern, in order:

1. **`vercel.json` rewrites** serve `index.html` for each clean path; legacy/renamed paths get `statusCode: 308` rewrites pointing at the new targets (redirects land on rewrites that render the right page, not on dead hashes).
2. **Router reads `location.pathname` first**, falls back to legacy hashes (rewriting them to clean paths client-side). One function handles both.
3. **Clean path is the ONLY first-class scheme**: internal `<a href="/digital">` real paths in markup (works no-JS, copy-link correct), clicks call the render fn + `history.replaceState` to the clean path — hashes must never enter the address bar.
4. **Per-route `<link rel="canonical">`** updated on route change — otherwise crawlers index whichever form they hit and split authority.

## Multipage static beats an SPA shell (validated {CLIENT}, hard-won)

A single `index.html` with a hand-rolled JS router juggling hash schemes, rewrites, and pathname fallbacks produced four consecutive production incidents (white-on-white reuse, hash/rewrite mismatch, dead typed URLs). The fix was deletion: three real files (`index.html`, `/digital/index.html`, `/physical/index.html`) with plain `<a href="/digital/">` links. Prefer this by default for brand/marketing sites:

- Zero routing code to debug; pages work with JavaScript disabled.
- Canonical URLs are trivially correct because they are just files — no `vercel.json` needed at all.
- Per-page `<title>`/meta are free.
- Deploy structure: build in a version directory (`vers/<proj>v4/`), gate locally, then copy to deploy root. Quarantine superseded version directories with a `-STALE-v< n>` rename (never delete) so nobody resumes from dead architecture after a cutoff.
- **Verify the base file before overwriting.** When adding a feature that exists across multiple commits (e.g. a terminal added in commit X, later edits in Y), a `cp` from the wrong version directory can silently replace the feature-carrying file with a pre-feature base. Check the working file still contains the feature's marker before copying over it; if already clobbered, recover with `git show <feature-sha>:<file> > file` then re-apply the edit. Locate the right commit with `git log --oneline -S "<marker>" -- <file>`.

## Hero images dominate mobile Lighthouse

Full-res logo artwork (800KB–1.4MB PNGs) tanked mobile Lighthouse to ~69 even on a near-static page. Fix: generate resized WebP (~85% smaller) + fallback PNG behind `<picture><source srcset=... type="image/webp">`, then re-run Lighthouse against PRODUCTION — score went 69 → 96 (FCP 1.4s, LCP 1.9s). Always re-measure after deploying, never trust local-file estimates.

## Self-hosted fonts + LCP diagnosis (validated {CLIENT})

Google Fonts css2 render-blocking cost ~864ms plus a third-party render dependency (and a visitor-data leak — wrong for a consulting brand). Self-hosting removed it: mobile Lighthouse 77 → 95 (FCP 0.8s, LCP 2.2s). Full woff2 extraction recipe in `references/google-fonts-self-hosting.md`. Key rules:
- Self-host woff2 in `assets/fonts/` with `font-display:swap`; preload ONLY the LCP face (the gateway h1 display face), not every face.
- Metric-safe fallback stack (`"DM Serif Display", Georgia, "Times New Roman", serif`) so the swap is near-invisible — a generic-sans fallback shifts metrics badly when the serif arrives.
- `vercel.json` headers: `/(.*)\.svg` → `image/svg+xml`, `/(.*)\.woff2` → `font/woff2` + `Cache-Control: public, max-age=31536000, immutable` (verify live with `curl -sI`).
- Name the real LCP element from Lighthouse JSON (`audits['largest-contentful-paint-element']['details']['items'][0]['node']['selector']`) and check `network-requests` transfer sizes BEFORE optimizing — don't guess.
- **DPR2 srcset trap**: `srcset="webp 1x, svg 2x"` makes mobile emulation (DPR 2) fetch the 2x svg, so a heavy mark stays heavy. For LCP-critical images make the small webp the PRIMARY `src`; reserve svg for small chrome (topbar/footer) where size is irrelevant.

## Component surface contracts

Any shared visual component declares its surface contract explicitly: variant class required per surface (e.g. `.on-light.glass` with solid light gradient + dark text vs dark-hero glass with translucent white + white headings), no defaults that assume a background. This bug class ships invisibly because it looks fine in the section it was designed in.

## Performance gate for dynamic layers

Canvas particle fields + blurred orbiting layers + pointer parallax score well on desktop and poorly on mid-range phones. Gate: mobile Lighthouse ≥80 + throttled-CPU smoke of the hero page. Node counts and effect layers get viewport-gated constants (`min(60, w*h/density)`), and every animated layer needs a `prefers-reduced-motion` static fallback.

- **Hidden ≠ free on mobile.** A feature that is CSS-hidden on small screens (`display:none` under a media query) still has its JS parsed AND executed on mobile — enough to drop gateway mobile Lighthouse from ~99 to 78 (a 21-point regression on a user-requested flagship). Gate the SCRIPT, not just the CSS: mark it `defer` and early-return when the same media query matches (`if(matchMedia('(max-width:820px)').matches) return;`) so mobile never runs it. Verified recovery 78 → 92 with desktop functionality intact. Re-test the feature at a forced wide viewport (`Emulation.setDeviceMetricsOverride`, width 1440) because the default browser-use window is ~437px and will correctly skip init.
- **Every JS block in a hidden feature needs its own width gate.** An intro animation added INSIDE an already-gated script but OUTSIDE the width guard caused a second 15-point regression (93 → 78) — the outer init guard does not cover nested animation blocks. Each animated block (auto-type intro, count-up, etc.) checks the width/reduced-motion independently. Verified recovery 78 → 92.
- **No-JS flash guard for interactive features.** A JS-driven feature must never flash its raw pre-JS state (markup, seed text) before init runs — this is the same "presentation state leaking before the system is ready" bug class as white-on-white. Default: `<body class="no-js">` + CSS hides the feature under `.no-js`; the init script removes the class only after it confirms it is running, on ALL viewports (removal must not be inside the desktop-only early-return, or mobile keeps the feature hidden forever).
- **Flag the inversion: for flagship/critical UI, visible-by-default beats class-removal.** The no-js class-removal pattern still failed on production TWICE ("container missing"): the removal depended on a deferred-script init racing the user's browser, and when the race was lost the element stayed `visibility:hidden; opacity:0` forever — a JS runtime step gating critical UI. Robust fix for the flagship element: serve the HTML WITHOUT the no-js class (strip it server-side / don't emit it), so the element is visible on first paint and JS only ENHANCES it (auto-type, commands). Keep the guard pattern for non-critical decorations; do not gate the site's best moment on a race the user's browser can lose.

## Gate verification: cache-bust by default

Every gate/QA verification fetches through a cache-buster (`?cb=<deploy-sha>` appended to HTML/CSS URLs) so "stale bytes vs live bytes" stops being a dispute. Three separate audit disagreements in one project traced to one side reading cached bytes while another read fresh ones. Make the probe deterministic instead of asking reviewers to remember to hard-refresh — one line in the gate contract. Also: when a "verified fixed" report is challenged, re-fetch the served bytes directly (grep the CSS/HTML, check the sha) rather than re-asserting the report.

**Production asset refs need `?v=<sha>` versioning too — in the SAME commit as the layout change.** The `?cb=` rule makes the agent's probe deterministic, but the user's browser still runs on `?v=`. If a stylesheet changes layout and its filename/version does not change, browsers holding the old CSS render run-on/collapsed layout against the new HTML for the full cache TTL (a 4-hour stale-layout window — verified root cause of "weird text" reports that were never broken in source). Rules: (1) version EVERY CSS/JS reference in every page's HTML (`/gateway.css?v=<sha>`, `/system.css?v=<sha>`), not just images; (2) bump the version in the same commit that changes the layout — a version bump in a later commit still leaves the stale window. This is the completing clause of the cache contract.

## Pre-deploy root-marker guard (MANDATORY — clobber class)

A `cp digital/index.html index.html` in a deploy batch silently replaced the site root (the gateway landing page) with a division page on production — the user's favorite page vanished, and only their screenshot caught it. Any site with a multi-page structure where pages share a CSS/asset vocabulary is vulnerable to a cross-page copy accident (wrong `cp`, wrong version dir, wrong glob). The permanent guard:

- **Before any push/deploy, verify the root `index.html` carries the ROOT page's identity marker** (e.g. `.gw-hero` + `#askterm` for the gateway), and FAIL the deploy if it matches a division page. One grep-style check kills the entire class.
- Ship it as `scripts/predeploy-guard.sh` in the repo, test BOTH directions (passes on real root, fails on a division-page-as-root), and run it as the first step of every deploy.
- Related: when adding a feature that exists across multiple commits, verify the working file still contains the feature's marker BEFORE copying over it; if clobbered, recover with `git show <feature-sha>:<file> > file` (locate via `git log --oneline -S "<marker>" -- <file>`).

## Staging-first deploy review loop (user-mandated)

After the clobber, the user revoked auto-push: **all new versions deploy to a staging subdomain first, wait for user review, THEN promote to main.** Loop: build → staging → QA + visual pass on staging → user review → promote (with the guard + same-commit `?v=` bump). The user reviews a QA-passed artifact, never a raw build, and never a production site mid-migration.

- Staging setup (validated): create a separate Vercel project (API `POST /v10/projects`), attach `staging.{CLIENT}`, read the TXT verification value from the API response, add `_vercel` TXT + CNAME `staging → cname.vercel-dns.com` at Cloudflare, wait ~20s, POST verify. Deploy to staging with `vercel --project <staging-name> --prod --yes`.
- **Wrong-project trap (validated):** `vercel --prod` from a repo linked to the production project deploys to PRODUCTION, not staging. When a staging fix "doesn't land" (verify still fails), check WHICH project's deployment the URL serves — the fix may have gone to the wrong project entirely. Always deploy staging with the explicit `--project <staging-name>` flag.
- Promote = same-commit `?v=` bump + guard + `vercel deploy --prod --yes` in the root workdir.
- Keep the gateway (and any user-loved page) PRODUCTION-STABLE: when staging iteration is in flight, main stays untouched until explicit approval.

### Environment swaps silently revert approved fixes (validate EVERY fix after a swap)

Restoring a baseline (live→older approved version, staging→a different version) brings back every bug the newer versions fixed — including the giant-anchor click bug and command-set regressions. After ANY live↔staging swap: re-verify each previously-approved fix against served bytes on the target surface (panel is a `<div>` not `<a>`, terminal visible + interactive, `/api/ask` 404 or 200 as expected), not just the swap itself. Also: **a "rollback done" claim is false until the served bytes prove it** — one rollback was reported complete while the live site still served the newer version (`/api/ask` returned 200 instead of 404); only a served-bytes probe caught it. Verify rollbacks with markers the version should NOT have, never by git commit alone. And when the user asks "why is the live domain changing?": check whether an unauthorized direct-to-live push happened (staging-first violation) — one such push caused a full rollback round.

## Light-theme containers need a MEASURED contrast floor, not a hand-picked border

Light-theme cards on cream/light backgrounds failed contrast FOUR consecutive review rounds while dark cards passed — "can't see the outline" / "container is the same colour as the background" kept returning because each fix was a hand-chosen border color with no threshold. Kill the recurrence with a measured token:

- Define a strong border token (e.g. `--line-strong`) tuned so border-vs-background reads at a glance: compute with WCAG relative luminance and assert **≥1.5:1 against the page background** (validated example: `#C9C2B2` on `#F4EFE6` = 1.55:1).
- Route every light-surface card's border through the strong token so the floor is enforced in one place.
- The QA gate asserts the token numerically (border color contrast ≥ threshold) — this converts the subjective complaint into a failing check, the same move that killed the hollow-card and white-on-white dispute classes. "Can barely see the outline" stops being a visual-pass finding.

## Verify the FULL rule, not the grep (hollow-class false finding)

A QA dispute where a reviewer greps served CSS and sees only `padding` in a card class is usually a **media-query override**, not a hollow class: `@media(max-width:720px){.card-dark{padding:48px 24px;}}` sits AFTER the full base rule (`background`, `border-radius`, `shadow`, accent line) and legitimately overrides only padding at breakpoints. Before accepting "the class is hollow": (1) grep for the BASE rule (with the visual properties), not just the class name; (2) verify **computed style in a real browser** (`getComputedStyle(el).borderRadius/borderTopWidth/boxShadow`), not served-byte grep — pixels settle the argument. The deeper gate lesson: a QA gate that checks *class presence in markup + CSS* verifies the fix was attempted, never that it renders. Gate checks should assert the visual properties (border-radius + background + shadow present in the base rule) when the complaint is visual.

## Launch QA gate checklist (permanent items)

Items that shipped broken until each became a standing gate check:

- **One CTA per surface, hrefs differ.** Duplicate buttons (e.g. "Book a consultation" and "Email us" pointing at the same mailto) are a QA slip, not a design choice. Verify per page: a single primary action, and no two visible buttons share an href.
- **Mandatory mobile emulation pass.** "Looks fine on desktop" is not sufficient to close. Every surface gets a 390px screenshot plus a mobile Lighthouse run against the live deploy (gate ≥80). A desktop-only gate shipped a page that was structurally broken on phones twice in this project.
- **Versioned refs + same-commit bump** (above): no layout rule change ships without its `?v=` bump in the same commit.
- **Responsive system is a real tier, not skeletal**: fluid containers (`width:min(100% - 48px, cap)`), clamp type scale, mobile breakpoints (grid collapse → stacked → touch targets ≥44px), `overflow-x:clip` guard. Details in `references/responsive-system-pass.md`.

## See also
- `references/cloudflare-squarespace-pages.md` — exact endpoints, selectors, and the working request shapes.
- `references/{CLIENT}` — current live topology of the user's production domain (DNS map, hosting map, deploy path, user's standing rules). Validate against live state before acting.
- `references/marketing-site-flagship-interactions.md` — the interactive proof-element pattern (parameter-driven terminal responder, CONDITIONAL honesty guard, shared-component data-driven command map, viewport-gated script, giant-anchor click fix, visual-lookalike removal) for "make it blow them away" hero asks.
- `references/design-system-upgrade-pass.md` — workflow when the user installs a design-intelligence skill (run its generator, spec from it, user-locked brand DNA overrides it) + the stats-strip credibility trap (real proof only, never invented count-up numbers).
