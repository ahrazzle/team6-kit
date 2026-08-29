<!-- GENERICIZED: 3×{CLIENT}, 1×{RELATIONSHIP} | source: skills/software-development/web-deployment-safety/SKILL.md -->
---
name: web-deployment-safety
description: Use when deploying or iterating a production website.
version: 1.0.0
author: {RELATIONSHIP}
license: CC-BY-4.0
metadata:
  hermes:
    tags: [deploy, staging, vercel, cloudflare, cache-busting, web]
    related_skills: [long-run-deployment-discipline, static-webapp-verification, custom-domain-publishing]
---

# Web Deployment Safety

## When to Use

Use whenever you are about to push a change to a production website, set up a
staging subdomain, deploy a new version, or debug "the user sees something
different from the source" — stale CSS, missing layout, wrong page at the root.

Class-level playbook for shipping and iterating a production website without breaking what users see. Born from a real incident: a single `cp` command replaced a production landing page with a division page, and unversioned CSS shipped broken layout for hours across every browser.

## The review loop (staging-first, user-mandated)

- Every new version deploys to a **staging subdomain first** (e.g. `staging.example.com`), never direct-to-main.
- Order: build → deploy to staging → QA gate on staging → visual pass on staging → **user review** → promote to main.
- The user reviews a QA-passed artifact, not a raw build. Promotion happens only on explicit user approval.
- Main stays untouched while staging iterates. After a production incident the user enforced this permanently.
- **Attach screenshot pairs to every staging review request** (same viewport/section, main vs staging, one pair per surface). If the user cannot see what changed, the change does not exist for them — this is exactly how a skill-driven upgrade got rejected as "no visible improvements". Before/after must be observable, not claimed.
- **Ground-truth structural changes before adopting them.** A screenshot that renders well is ambiguous evidence: the user may like the *vertical space* an element gained, not a new *column structure*. In one round a 3-column terminal-spine was adopted from an accidental render, then the user clarified the screenshot was still the 2-half layout — what they valued was the flavour elements (terminal, sourcing pipeline) getting more room *inside* their own halves (4-columns-in-2-halves, `[content|terminal]` / `[pipeline|content]`), with the Digital/Physical boundary sacrosanct. Before any structural redesign, state the proposed structure back and confirm the user wants the structure, not just the space it happens to give.
- **Interpret design-feedback keywords as weight/register, not family-shopping.** When a user calls a font or button "sleek" / "futuristic" and rejects your attempt, the correction is usually WEIGHT + tracking, not a new family. Observed four-attempt loop: Geist Mono (technical) → Manrope 700 (thick — user: "I said sleek, you chose a thick font") → Space Grotesk 500 (sleek, correct). Standing contract for this user's Digital division: **"sleek" = weight 500–600 geometric sans, light tracking, sentence case — not bold, not mono, not heavy.** Change weight BEFORE changing family; the room only escaped the loop by dropping to 500, not by family-shopping. For user-supplied font files (OTF/TTF in a mats/ folder), convert to self-hosted woff2 with fontTools — see `references/font-conversion.md`; prefer the Regular weight over Extrabold unless heavy is explicitly wanted.
- **When the user points at a concrete element as the styling target, replicate its FULL computed font spec — family, weight, case, tracking.** "Use the font from this button" means *make it look like that button*, not "same family, weight per contract." One round shipped Geist 500 on buttons while the reference orange button rendered Geist 600 — the off-by-one weight triggered another correction. The durable rule: read the reference's `getComputedStyle` (font-family, font-weight, text-transform, letter-spacing) and match every field. "Sleek" is a register signal; a pointed-at element is a byte-faithful spec.

## Pre-deploy marker guard

- Before any push, verify each target file carries its **expected identity marker** (e.g. root `index.html` must be the gateway/landing marker, not a division page).
- Wire a grep-style check into the deploy stage; fail the deploy on mismatch. Test the guard **both ways** (pass + fail) before trusting it.
- This catches cross-page `cp`/`mv` accidents where paths differ only by directory (`cp digital/index.html index.html` clobbered a gateway once).

## Cache-busting discipline

- Version **EVERY** cacheable asset reference: CSS, JS, and images — `?v=<sha>`.
- Bump the version in the **SAME commit** as the layout change; otherwise browsers serve stale CSS against new HTML for the whole cache TTL (4h+), and the user reports broken layout that is not in the source.
- Images alone are not enough — unversioned CSS was the actual "stale layout" culprit in a long debugging loop.
- Verification fetches go through `?cb=<sha>` so "stale bytes vs live bytes" stops being a room argument.

- **Verify rendering, not presence**

- A grep for a class name proves the fix was *attempted*, not that it *renders*.
- Rendering disputes (hollow vs full, invisible-on-background, blocky vs rounded) are settled by **computed style in a browser**: border-radius, background, box-shadow — never by which side parsed the CSS most favorably.
- **Font-size claims: verify the PAINTED text, not the token.** Two buttons can both declare 14px yet render differently to a user if one is overridden. Measure actual painted text height with a Range: `document.createRange().selectNodeContents(el).getBoundingClientRect().height` (or compare both buttons' `getBoundingClientRect()` in ONE frame). A user screenshot that shows a relative size gap is ground truth even when every CSS token says equal — check the painted size, then decide whether the screenshot was stale.
- Media-query overrides (e.g. padding-only rules at breakpoints) can read as "the whole class" in a grep. Read the **base rules** before declaring a class hollow.
- **Word-split reveal markup breaks contiguous-string greps.** A B11-style word-by-word reveal renders every word as its own `<span class="tw">word</span>` — the contiguous phrase "Most firms do one of these" is NOT findable as a string even though the copy is fully present. Two auditors declared a tagline "removed, not replaced" on this false negative. Fix: join the span tokens (`re.findall(r'<span class="tw">([^<]*)</span>')` → `' '.join(...)`) or read the containing block before claiming a phrase is absent. Any animated/split content has this class of audit failure — grep the assembled text, not the raw HTML.
- **Verify the served DOM structure, not just JS handlers.** An interaction contract can live in markup: a panel that is itself an `<a>` navigates on every click via native anchor behavior — `stopPropagation` on an inner handler never fires, and there is no handler to find. Code-level "no onclick" checks pass while the served bytes still wrap the whole panel in an anchor. Grep the live DOM for wrapping elements before claiming a click-split works.

## Flash-guard inversion (no-js class hides the flagship)

A `no-js` flash-guard class (`body.no-js .term{opacity:0;visibility:hidden}`) is meant to hide raw pre-load markup until JS confirms itself — but if the JS that removes the class does not execute (init race, moved script, replaced inline responder), the guarded element stays **permanently invisible**: "container missing" while the markup is present in the DOM.

- **Critical UI must be visible by default; JS only enhances it.** Never gate the flagship element (hero terminal, primary CTA) behind a JS-runtime class removal — the user's browser can lose that race, and the served HTML/CSS still ship the hiding rule.
- If you must use a flash guard, strip the `no-js` class **server-side** (serve the HTML without it) or scope the guard to non-critical chrome. A terminal that vanishes until JS runs is a broken terminal.
- **Deferred-component init race:** an init script that runs before a `defer`-loaded component checks `if(window.Component)` and silently no-ops when the global isn't ready yet. Fix: retry until the global exists (poll with `setTimeout`) or mount on `DOMContentLoaded`. Symptom: `typeof Component !== 'undefined'` is true, the component loads, but the mount never ran.
- **Static lookalikes:** a *decorative* terminal graphic in the hero (`$ {CLIENT} assess` + checkmark list, no input) reads to the user as "the static terminal." When mounting an interactive replacement, replace the decoration **in place** and verify exactly ONE terminal element exists in the served DOM — then style it to read as interactive at a glance (visible input border, blinking caret, bright placeholder). A live terminal can still read as a static graphic if its affordances are too subtle.

## CSS grid layout escapes (layout balloons)

- **Percentage heights on auto-sized grid rows LOOP.** `.gw-divider{height:120%}` inside a grid whose row height is auto-sized forces the row taller, which feeds the percentage → the row balloons (observed: 900px intended → 1624px actual), pushing siblings below the fold. Fix: `height:100%` on the divider + `overflow:hidden` on the grid container.
- **Grid children must be DIRECT children.** A column wrapper accidentally nested inside another column (spine div left inside the left half during a restructure) makes the grid size from the wrong content and destroys centering. After any DOM restructure, verify in the rendered browser: `gridTemplateRows` ≈ expected, child order matches intent, and `gridTemplateColumns` still defines the intended columns.
- **Centering columns with extra widgets:** wrap each column's primary stack in an inner stack element (e.g. `.half-stack`) and center THAT; peripheral widgets (pipeline trackers, badges) go `position:absolute` pinned to the column edge so they do not offset the centered stack. Both columns must share the same vertical midpoint — check with `getBoundingClientRect()` midpoints, not eyeballs.
- After HTML restructures, rebalance div/anchor counts (`<div` vs `</div>`, `<a ` vs `</a>`) — stray closers from the old structure (a leftover `</a>` from a converted panel) break layout subtly and pass a quick visual check.

## Static-site coupled files: same-commit rule + served-artifact gate

Static sites with separate `app.js` + `index.html` fail in a characteristic way when the pair splits across commits: new `app.js` referencing element IDs the served `index.html` doesn't have → `document.getElementById(...)` returns null → `addEventListener` on null throws → the ENTIRE script dies before any rendering (empty dropdowns, frozen "Loading…"). Observed THREE times in one session; each was a local-vs-deployed gap where the report said "done" but the served bytes didn't match.

- **Same-commit coupling rule:** any `app.js` change that adds a `getElementById`/`$()` reference MUST ship with the `index.html` (or template) change in the SAME commit. Coupled files never split. Same rule as CSS+layout coupling on any static stack.
- **Null-guard DOM access:** use a safe helper (`function $(id){ return document.getElementById(id); }`) and guard every event-listener registration (`if (el) el.addEventListener(...)`). A missing element then degrades gracefully instead of killing the script — turns a frozen page into a non-fatal missing-widget.
- **Served-artifact consistency gate (before any "shipped" claim):** fetch the LIVE served `app.js` and `index.html`, extract every `$('id')`/`getElementById` ref, and assert each resolves in the served HTML. Dynamic elements created in JS (e.g. `link.id = 'dynamic-font'`) are correctly absent from static HTML — whitelist those by checking the JS creates them. Reports must distinguish "implemented locally" from "live on staging" — one word changes the trust calculus.
- **Staging for GitHub Pages = separate repo, not fork.** Pages URLs are `owner.github.io/repo-name`; forking `{CLIENT}` to the same owner keeps the name `{CLIENT}` → URL collision with production. The fork would have to be renamed, which collapses it into a separate repo anyway (minus the upstream link and its "sync fork" foot-gun). Create `owner/<repo>-staging`, enable Pages on `main`, push the full build (data files included — the review must exercise the real artifact), then promote to production only on user approval. GH Pages takes ~1-2 min to catch up after push — verify the served artifact (curl the file, grep a marker), not the commit, before reporting live.

## Git recovery after corrupted rebases

Multi-tree repos WILL produce rebase/merge conflicts where `--theirs`/`--ours` picks the wrong side (observed: a v6.2 commit lost the favicon + system.css fixes during conflict resolution). Recovery pattern:

1. `git reset --hard origin/main` to a known-good remote state.
2. `git checkout <good-commit> -- <files>` to restore the intended base files.
3. Re-apply ONLY the intended delta; verify the recovered tree carries the expected markers (grep for the identity markers, run the pre-deploy guard) BEFORE committing — a clean `git status` is not proof of a correct tree.
4. If a `git rebase --continue` fails with "could not read log file" or stuck rebase-merge dirs: `git rebase --abort`, then rebuild the state directly (steps 1–3) instead of fighting the rebase.
5. After ANY conflict resolution, diff the final files against the intended commit's tree, not against HEAD — the merge may have silently dropped changes.

## Environment swaps & rollbacks (baselines revert fixes)

When the user orders "live → last approved version, staging → working version", the swap itself becomes a trap:

- **A baseline revert silently drops every fix that postdates it.** Restoring live to v6.3 also removed the click-split, Enter-link contrast, and layout fixes the user had already approved (they lived in v6.5+). After ANY environment swap, re-verify the user-approved fixes are still present on the new baseline and fold them back in before the next staging round — the room shipped the click bug twice because the swap kept resetting to a tree that predated it.
- **Verify rollbacks against served bytes, not against the deploy claim.** A rollback was reported "complete and verified" twice while live still served the wrong tree (`/api/ask` returned 200 instead of 404). Distinguishing markers make this cheap: an endpoint that should 404, a command that should be absent, a title that should match. Check Vercel deployment history too — a rollback that deployed but was overwritten by a later deploy is still a failed rollback.
- **Restore baselines as exact trees, not working-directory luck.** `git checkout <commit> -- .` does NOT delete tracked files absent from that commit — a leftover `api/ask.mjs` survives onto a "clean" v6.3 tree. `git rm` files the target commit does not contain, then verify the tree has zero traces of the newer version.
- Record what each target's baseline CONTAINS (commit + markers), not just which commit it points at — the deploy-target lock is meaningless if the swap itself is unverifiable.

## Multi-page expansion: template system first

When a static site grows from a landing + a few pages to 6–12 pages (About, Pricing, Team, service details, blog, insights), the failure mode is the same drift that plagued the first two pages, multiplied. The rule: **build the shared page skeleton in the site-wide CSS BEFORE the new pages land**, so every page inherits the visual system instead of hand-rolling layout:

- Shared skeleton classes in the site CSS: `.page-hero` (interior hero with grid texture + breadcrumb), `.breadcrumb`, `.page-body` content rhythm, plus ready-made component classes for the coming pages — `.team-card`, `.pricing-card`, `.case-card`, `.article` / `.article-meta` (blog template with byline + sources block). Each page then adds only a content sheet.
- Interior `page-hero` pages must read as content pages and NOT compete with the landing/division heroes — the template gives that for free since interior pages inherit `page-hero` rather than the split/division hero styles.
- **New pages must be reachable, not URL-only.** When adding pages, update the header nav AND the footer links in the same cycle — a page with no nav link is a dead end the user hits on the first visit.
- **Flag-not-write for gated content.** When facts need user confirmation (fee numbers, named people, project claims), build the page SHELL and template now, write `[NEEDS USER CONFIRM]` markers in the plan, but do NOT ship the copy until the business gate (user confirms current + public-ready) and the source gate (claims cross-checked against the actual records) both clear. Two unrelated changes in one deploy get verified per item, not as a batch — a batch report masks one item's failure behind the other's success.
- **External content adaptation (essay → blog post):** preserve the source artifact's visual system (timeline, bars, diagrams) — re-lay the prose AROUND the existing visuals, adapt into the site's article template with the site tokens. Reuse, don't re-theme. Add the byline/date/sources convention the source asset likely lacks. A "tracked in real time" claim needs a visible last-updated + status mechanism, or a falsifiable piece becomes a liability.
- A knowledge-base / research layer can supply raw material: query it for the firm's own notes (fee philosophy, real project evidence) — those are stronger copy than marketing language, but every factual claim still passes the two gates before publication.

## Pitfalls

- **Declare ONE canonical build path.** Duplicate build trees (a `vers/` copy vs the working copy) cause stale-verification disputes: agents verify against a copy, disagree about reality, and burn a round. STATE.md must name the single source-of-truth path, and stale copies get a `-STALE-<tag>` quarantine rename, never deletion.
- `cp a/index.html index.html` can silently clobber a different page when paths differ only by directory. After any cross-path copy, grep the destination for the expected marker.
- **Vercel CLI auth tokens expire (~24h**, auth.json `expiresAt`). On "Not authorized": run `vercel whoami` WITHOUT `--token` — the CLI self-refreshes its session. Never cache raw tokens for reuse across days.
- Deploy to a specific project with `vercel --project <name> --prod`.
- **Vercel env scopes are production/preview/development — there is NO "staging" scope.** To give a staging-project deploy its secrets (e.g. `OPENROUTER_API_KEY`), `vercel link --project <staging-project>` from a temp dir, then `vercel env add VAR production` — the 'production' scope of the STAGING project is what its `--prod` deploys read. The error "Invalid environment: staging. Valid environments: production, preview, development" is the tell.
- **`vercel --prod` without `--project` deploys to whatever project the current dir is linked to** — a repo linked to the production project will deploy to PRODUCTION even when the intent was staging. If a fix "doesn't land" on staging, check which project the deploy actually hit before blaming the code.
- Baked checkerboards in logo PNGs: verify mode is RGBA and corner alpha = 0 BEFORE treating a PNG as a clean web asset; JPEG cannot store alpha.

## References

- `references/vercel-cloudflare-staging.md` — concrete staging-subdomain setup: Vercel project + domain verification, Cloudflare TXT/CNAME records.
- `references/terminal-llm-assistant.md` — interactive terminal flagship: slash-command dispatch + serverless LLM `/api/ask` (key hygiene, rate caps, showcase-assistant prompt), and the instrument-vs-door click contract.
- `references/grid-layout-recovery.md` — measured case study: grid row-height loop (120% height on auto rows), non-direct grid children, div/anchor imbalance after panel conversion, and git recovery from corrupted rebases.
- `references/font-conversion.md` — self-hosting user-supplied fonts (OTF → woff2 via fontTools), weight selection, scoped wiring, computed-style verification.
- `references/multi-page-expansion.md` — template-first expansion of a static site to many pages (page-hero/breadcrumb/article/team/pricing/case components), the two verification gates for gated copy, and external essay → blog post adaptation (preserve visuals, add byline/sources, visible tracker).
