<!-- GENERICIZED: 19×{CLIENT}, 4×{RELATIONSHIP} | source: skills/software-development/web-build-verification/SKILL.md -->
---
name: web-build-verification
description: "Use when verifying web builds, deploys, or asset gates."
version: 1.1.0
author: {RELATIONSHIP}
license: internal
metadata:
  hermes:
    tags: [web, deployment, verification, qa, dns, assets]
    related_skills: [dogfood, systematic-debugging, requesting-code-review]
---

# Web Build Verification

## When to Use

Load this skill when any of these triggers fire:

- A teammate reports a website build "live", "fixed", or "deployed" and the claim needs independent verification.
- A build sign-off gate runs before deploy (asset gate, route matrix, repo visibility).
- Logo/image assets enter a web build (transparency/format gating).
- A domain or DNS migration is planned or suspected mid-flight.
- A long multi-step build/deploy chain needs resumability after agent timeouts.
- Re-checking another agent's completion report in any web project.

Context: class-level discipline for multi-agent web projects where completion reports are self-reports, not evidence.

## Core invariant

**A teammate's "done and verified" is a hypothesis until you reproduce the verification yourself.** This session: a v4 rebuild was reported at one path while actually living at another; a manifest failed its own checksum; a renamed public label never reached the satellite property it applied to. All were caught only by direct disk/network reads. Audit trail order: (1) read disk inventory, (2) hash-compare, (3) probe the live URL, (4) only then accept or reject the report.

## 1. Asset gate (before anything enters a build)

Run pixel truth, not filename trust:

```python
from PIL import Image
im = Image.open(p); rgba = im.convert('RGBA'); alphas = list(rgba.getdata(3))
# PASS requires: mode RGBA, min(alphas)==0 AND max(alphas)==255,
# healthy share of fully-transparent pixels, corner alphas == 0
```

- **Extension ≠ format.** Files named `.png` can be JPEG-encoded (RGB, zero alpha). Check `im.format`, not the suffix.
- **One source of truth directory (`assets/`).** Duplicate asset dirs accrete impostors — same name, different bytes (one true-alpha, one JPEG-with-baked-checkerboard). Enforce: builds reference zero files outside `assets/`; verify by manifest diff. Derivatives (e.g. light-contrast logo variants) go in `assets/derived/` with manifest entries; originals stay immutable.
- **MANIFEST.sha256 must be regenerated after any post-manifest edit.** Run `shasum -a 256 -c MANIFEST.sha256` — a FAILED line means the file changed after attestation. Treat as untrusted. Also check mtime ordering: a manifest older than any attested asset is stale by construction.
- **Stale-reference sweep before sign-off:** grep the build for retired asset paths (`assets/opt/`, `assets/derived/`, and any superseded filename — e.g. `physical-light`). A retired derivative still referenced ships rejected artwork; it is worse than a missing file. When the user has already seen stale logos, require cache-busting (`?v=N` on asset refs) in the same pass — unversioned refs keep serving old bytes from browser cache no matter what deploys.

## 2. Checkerboard claims: measure, don't look

When a human says "the logo has checkerboard baked in":

1. **Measure alpha first.** Uniform `alpha==255` everywhere = they uploaded a **screenshot of their file viewer** (viewer composites the transparency grid opaquely). Real transparent PNGs show `alpha range 0–255`.
2. **Vision models are unreliable on this exact question** — one described literally painted-in checkerboard squares as "standard viewer indicator, not baked in". Pixel measurement outranks vision analysis for alpha claims; use vision only for motif/content identification.
3. If the *live site* shows squares: pull the served bytes (`curl -o live.png <url>`), hash against workspace. Matching hashes + clean alpha = rendering/cache issue, not files. Zero matches for checker/repeating-gradient CSS in served HTML closes the CSS theory.

## 3. Live-deploy audit probes

Batch these in ONE command set (see pitfalls below on oversized payloads). **Every HTML/CSS/JS fetch carries a cache-buster** (`?cb=<deploy-sha or timestamp>`) — unversioned probes can audit a CDN edge cache instead of production, which is exactly how "stale bytes vs live bytes" disputes start. When the user reports old content after a verified deploy, tell them hard-refresh (Cmd+Shift+R). A deterministic probe kills the dispute class.

| Probe | Command | What it proves |
|---|---|---|
| DNS | `dig +short <host> A; dig +short <host> CNAME` | where the name points |
| Server identity | `curl -sI <url>` then grep `server:`, `x-github-request-id`, `x-vercel-id`, `location:` | which platform actually answers (GitHub Pages / Vercel / Cloudflare proxy) |
| Content identity | `curl -s <url> \| grep -ioE '<title>[^<]*</title>'` | WHICH site answers — catches stale deploys serving old titles |
| Byte provenance | download served asset, `md5` vs workspace copy | deployed bytes == reviewed bytes |
| Route matrix | loop every public path, print code + title | dead routes, identical-title SPA shells, redirect targets |

Read the headers, not just the status code: a 301 whose `location:` points at a dead host means the "working" surface is dark. An apex resolving to an IP with zero HTTP response = claimed-but-not-serving (mid-migration).

## 4. Domain migration safety ordering

- **Create and verify the destination BEFORE releasing the origin binding** (subdomain record + platform binding live and serving expected content first).
- Enumerate existing bindings before creating new ones — aborted prior sessions leave stray platform projects holding domains (Vercel routes domains per-project; a stale project binding blocks the new project from claiming it, failing in ways that look like DNS).
- After cutover, re-probe ALL surfaces including ones nobody mentioned (`www.` kept 301-redirecting into a dead apex after everyone signed off the apex).

## 5. Mobile & container-width readiness (static measurement)

When the user says "containers look archaic" or "horrible on mobile", measure before redesigning. Pull each linked CSS with a cache-buster and count:

- **`@media` per stylesheet** — page-specific CSS with ZERO media queries means the page renders as desktop squeezed into a phone viewport; that is the measured definition of "horrible on mobile".
- **Fluid units** — `clamp(` and `[0-9.]vw`; absence means no responsive type or spacing scale.
- **`max-width` inventory** — multiple small fixed cages (520–840px class) with no `min(100% - gutters, max)` pattern produce side gutters at every window size; that reads as "archaic containers".
- **Fixed-px `padding`/`font-size`** — hero padding like `160px` plus fixed type means layout and text do not adapt.
- **Breakpoint coverage** — grid collapse at 900/720/560px with nothing else (no stacked hero, no touch-target tier, no mobile type scale) is minimal responsiveness, not mobile support.
- **Viewport meta** — `<meta name="viewport" content="width=device-width, initial-scale=1.0">` must exist on every page.

Fix direction: containers as `min(100% - gutters, max)` (full-width sections with fluid gutters), `clamp()` type scales, a real ≤720px tier (stacked layouts, ≥44px touch targets, persistent CTA or menu).

## 5b. Presentation integrity & interactive-feature gate

A build can be functionally perfect and still read as broken. This class of failure shipped repeatedly in one project; the user's exact words were "weird text appearing on the landing page." Verify before sign-off:

- **Grep the served DOM for raw scaffold copy.** Unstyled CLI hints (`try /build supply chain  /fund 5M raise`), bare `$` prompts, and debug strings sitting in the hero read as junk, not affordance. Functional flagship elements need a designed artifact layer — frame/chrome, styled hint line, muted tone — or they ship as "UI scaffolding wearing no clothes." A structural QA pass (routes 200, JS works) does NOT catch this; the gate needs a presentation-integrity grep.
- **Typographic integrity on code-like strings.** An em-dash where a CLI flag belongs (`—help` vs `--help`) is the first thing a visitor sees and reads as broken. Check every code-like string for correct hyphen/dash characters.
- **Cryptic tokens need a legend.** `SPEC / SRC / NEG / DLV` with no full-word labels is unreadable to the lay audience a marketing site converts. Trackers and acronyms get labels (SPECIFICATION → SOURCING → NEGOTIATION → DELIVERY) or die.
- **Interactive proof for "we can do the impossible"** (consulting/brand sites): a **parameter-driven responder** beats a canned script. User types `/build <problem>` or `/fund <amount>` or `/source <material>`; a client-side lookup returns a plausible engagement path (strategy → architecture → build → fund → operate). Rules: pure client-side (zero network), `prefers-reduced-motion` renders instantly, hidden on mobile where the hero stacks. **Honesty guard is mandatory for trust-selling firms:** every demo response ends with "→ scheduled: intro call — we map this to your actual situation" so the demo demonstrates capability without faking a diagnosis.
- **CSS-hidden ≠ JS-not-run.** A terminal hidden on mobile still parsed and executed its responder JS, dropping mobile Lighthouse from ~99 to 78. Gate the script by viewport (`defer` + `innerWidth <= 820` early-return), then re-measure — the fixed version scored 92. Rule: any interactive feature adds "mobile Lighthouse ≥ 80 after the feature" to the gate, measured at a mobile viewport, not desktop.
- **Axis agreement.** When a hero uses a directional background (navy left / beige right) AND a layout split (halves), the two axes must agree at EVERY breakpoint. The failure: horizontal background + vertical stacked halves = each text color sits on the half it does not contrast with (white text on beige, black on navy). Verify layout `flex-direction` against gradient `background` direction per media query; a divider element must rotate/translate with the layout, not independently.
- **Push ≠ deploy.** A commit landing in `origin/main` does not mean the site is live. This project deploys via `vercel --prod` CLI (no git-push integration), and the push alone left the old build serving for minutes. Verify the deployment mechanism (git integration vs CLI) before assuming; treat "pushed" and "live" as different claims. Deploy-tool tokens expire mid-session (~24h TTL): an auth-refresh command (`vercel whoami`) re-establishes without user involvement.

## 6. Resumability contract for long build chains

- Work unit = one bounded stage (≤ ~2 min), ending in a **STATE.md write in the pinned workdir** (current step, done/remaining, last verified fact) plus a short report. Any agent resumes by validating STATE.md against disk before acting.
- Front-load recon as one batched read-only pass before mutations; long waits go background, never foreground polling loops.
- On a dead end: state blocker once with exactly what unblocks it, move to next independent workstream. Silence and retry-spirals are both violations.

## 7. Served-bundle discipline (static hosts, multi-agent)

**"If it's not in the served file, it doesn't exist."** In a long bug-cycle ({CLIENT} demo), the same failure repeated four+ times: a fix was announced "live / pushed / verified", the user tested, the bug persisted, and the served bundle turned out not to contain the fix. The served bytes and the announced fixes were decoupled — local source was correct, the deployed artifact was stale or the wrong file entirely. Root causes seen:

- **Source fixed, bundle never rebuilt** (`src/*.ts` updated, `dist/bundle.js` still old).
- **Build output untracked** — `dist/` in `.gitignore` means the import fails silently on GitHub Pages; page loads, nothing works, no console error.
- **Wrong file name in the HTML** (`bundle.js` vs `game.js`) — browser had never fetched the new name, serving a mix.
- **Local dev server masked the bug** — served transpiled/stripped code; GitHub Pages serves the raw file and the browser hit a syntax error the local server never saw.
- **HTML/CSS skeleton shipped with calls to methods that never landed in the bundle** — results overlay called `feedbackLayer.getAccuracy()` which didn't exist in the served JS; the whole flow crashed mid-`endGame()` and froze the screen.

Before ANYONE tells the user "fixed — hard refresh", verify the served artifact contains the fix:

```bash
# GitHub Pages raw source (no CDN cache):
curl -s https://raw.githubusercontent.com/<owner>/<repo>/main/dist/<bundle>.js | grep -c "methodName"
# Live page (cache-busted):
curl -s "https://<site>/demo.html?v=N" | grep -oE '(bundle\.js|game\.js|dist/[a-z.]+)'
curl -s "https://<site>/dist/<bundle>.js?v=N" | grep -c "methodName"
```

0 occurrences in the served bundle = the fix does not exist, regardless of what local source shows. Same rule in reverse: verify a claimed REMOVAL (a deprecated function at 0 occurrences) before trusting it.

Also grep the served HTML for the actual import path — browsers fetch what the served document references, not what the repo's latest source references.

- **Shared components hide behavior in the served JS, not the mount config.** A component mounted with a minimal config (`root, api, intro, readyLine`) keeps its real behavior — the command map, alias groups, and action targets — inside the served component file. Verifying a behavior claim (e.g. "`/call` targets the right number") by reading the HTML config alone returns nothing; fetch the served component JS itself (`curl <site>/assets/js/<component>.js?cb=...`) and read the map there. The HTML is a mount point; the component file is the behavior. Same rule as the bundle: served component file is the truth, repo HEAD is a hypothesis.

## 8. Static-host deploy pitfalls (GitHub Pages & friends)

- **TypeScript annotations in an inline `<script type="module">` break the whole page on a static host.** Browsers do not understand `const x: Record<string, number> = ...` — the script block fails to parse, NO event listeners attach, every button silently dies. A local dev server (esbuild/vite) transpiles before serving, masking it; GitHub Pages serves the raw file. Rule: the inline script in any file that will be served raw must be plain JS — no type annotations. The bundle is fine (already transpiled); only inline scripts carry this risk.
- **`dist/` (or any build output) in `.gitignore` = silent broken deploy.** The HTML imports a bundle that was never pushed; module import fails silently and the page appears dead. Before a static-host deploy: confirm the build output is git-tracked (`git ls-files dist/ | head`), or commit it explicitly.
- **Deployment propagation lag is real (1–3 min on GitHub Pages).** After a push, the edge may still serve the old bundle. Distinguish "deploy lag" from "fix absent": check `raw.githubusercontent.com/.../main/...` (updates at push time, no CDN) — if the raw file has the fix but the live site doesn't, it's lag/cache, not a missing fix.
- **Cache-busting + cache-control is the permanent fix for "hard refresh didn't help".** Add `?v=N` to the bundle import AND a `<meta http-equiv="cache-control" content="no-cache, no-store, must-revalidate">` in `<head>`, bump `N` on every deploy. Users repeatedly failing after "hard refresh" is the signature of an unversioned import.
- **A stuck onboarding/intro screen is usually a runtime error in the thing the button calls, not the button.** When dismissing the overlay does nothing, open the browser console for the actual exception — guessing "maybe it's cache" four times wastes user patience.
- **Absolute paths break subpath deployments (GH Pages `<user>.github.io/<repo>/`).** An absolute fetch (`fetch("/demo/words.json")`) works on a local dev server that serves workspace root and 404s on the Pages subpath. Audit EVERY asset reference — `fetch()`, `src=`, AND helper functions: a `loadImg()` that prepends `/` silently breaks every asset it loads, and the fix can recur in a NEW form one round after the first fix (words.json went relative; the {CLIENT} loader still had the leading slash). Rule: repo-relative paths everywhere, and the verification gate must probe the LIVE subpath URL's asset fetch, not the localhost 200.

## 9. Negative DNS cache after NXDOMAIN

If a hostname was NXDOMAIN when first checked, and a record is created minutes later: the **local OS resolver can hold the negative result for minutes** even though the record is live and correct at the edge. Classic split:

- `dig +short host A` → resolves (dig queries the resolver directly, bypassing the OS cache)
- `curl https://host` → exit 6 / "nodename nor servname provided" (curl and browsers use the OS resolver cache)
- `curl --resolve host:443:<ip>` → HTTP 200 (proves the edge and TLS are fine)
- TCP connect to the edge IP succeeds; a working precedent record on the same proxy IP serves 200

Conclusion: the deploy is fine; the local negative cache is stale. Fixes: wait for TTL expiry, `sudo dscacheutil -flushcache && sudo killall -HUP mDNSResponder` (macOS), test from another network/incognito, or check via a public resolver (`dig @1.1.1.1`). Verify record creation itself via the provider API + `dig`, not the local browser, and label the two evidence chains separately (edge-live vs locally-resolvable).

## 10. One domain owner at a time (avoid dual DNS instructions)

When two platforms (Vercel project + GitHub Pages) both target the same custom subdomain, DO NOT hand the user two competing DNS instructions (CNAME → `cname.vercel-dns.com` vs CNAME → `{RELATIONSHIP}.github.io`) in consecutive messages. Same hostname, two targets = Cloudflare serves whichever it likes, and the deploy looks broken regardless. Settle the platform owner FIRST (public forkable repo → GitHub Pages; commercial CLI-deployed site → Vercel), delete/detach the losing project, then hand the user exactly ONE record. Verify the losing project's domain is actually detached before the user touches DNS.

## 11b. Environment version forensics & rollback verification

**"Which version is deployed?" is a question the served bytes answer — never the repo state, never a room claim.** In one incident, a "swap complete" report was false: the claimed rollback had never landed, and live still served the unapproved build (proven by probing live bytes, not by trusting the report). Discipline:

- **Byte-match served HTML to git commits.** Fetch each surface cache-busted, then `git show <commit>:index.html | diff - <(curl ...)` — after stripping CDN-injected scripts (Cloudflare `email-decode.min.js`, `challenge-platform`, `__cf_email__` obfuscation). A ~12-line diff that is only CDN noise = byte-identical to that commit.
- **Marker table per environment.** Define distinctive per-version markers (endpoint behavior, command presence, titles) and probe BOTH surfaces after any deploy or rollback. Example matrix: gateway title / `/api/ask` status (404 = endpoint absent from tree, 200 = live, 503 = deployed but env var not scoped) / `/enter` command presence / terminal markers. A claim like "live = v6.3" is only true when every marker row says so.
- **Rollback = deploy the exact approved tree.** Restoring an older commit also cleanly removes surfaces that commit never had: an `api/` directory absent from the tree makes the endpoint 404, and its secrets env var goes dormant (no cost). Verify the removal by probing the endpoint (404), not by assuming the tree change removed it.
- **Env vars are scoped per environment, not per project.** A serverless function deployed to staging answers 503 "not configured" until the key is added to the staging project's scope (`vercel env add <KEY> staging`) — production scope does not carry over. Fresh staging baselines always hit this.
- **THE BASELINE-RESTORE TRAP:** restoring a baseline from an older commit silently discards every fix made in commits AFTER it. When staging was reset to the v6.5 baseline, two user-requested fixes that existed only in later commits (the click-split structural fix, the Enter-link contrast pass) vanished with it. Before restoring any baseline, list the commit range from baseline→HEAD and audit which user-visible fixes must be re-applied on top of the restored tree — otherwise the next round ships bugs the user already reported as fixed.

## 11c. Interaction contracts live in the served DOM, not just JS

- **Nested-anchor click bug class:** a panel implemented as `<a class="half" href="...">` wrapping interactive children — a terminal, an input, even a SECOND `<a>` inside it — makes `stopPropagation` on the child useless. The outer anchor's NATIVE navigation fires regardless of child handlers; only `preventDefault()` on the anchor (or removing the anchor entirely, panel→`<div>`) stops it. Invalid HTML (`<a>` inside `<a>`) is the tell. The bug survived multiple rounds because verifiers checked JS handlers (`no onclick on panel` = "clean") instead of the markup structure — the panel WAS the link. Rule: for any click-split contract, read the served DOM's element nesting (is the interactive child inside an anchor?), not just the script.
- **"Missing element" ≠ absent.** A UI element that "reads as nothing" is frequently a contrast failure, not an absence: the Enter-{CLIENT} link was present in the DOM but cyan-on-navy (≈invisible), while its orange-on-cream counterpart on the other half read fine. Before concluding an element is missing, grep the DOM for it AND read its CSS color against its background.
- **Vision reads are unreliable for layout geometry.** Two vision passes on the SAME screenshot produced conflicting readings ("3-column" vs "2-column") — adjacent elements sharing a color family (dark terminal on the dark navy half) made the model hallucinate a column boundary. Layout claims must be verified against computed DOM geometry (grid-template-columns, element rects, `termParent`/`half` structure), not pixel reads. This extends the existing "measure alpha, don't trust vision" rule to ALL geometric claims.
- **User screenshot ≠ served render → stale cache hypothesis.** When the user's screenshot shows a layout that does not match the served CSS (e.g. "link beside text" when served CSS stacks it), flag hard-refresh before building against a phantom. Cache-busted re-probe decides: if served bytes match the repo and the screenshot doesn't, the viewing side is stale — design against the served truth, not the screenshot.

## 11d. JS-gated visibility, LLM surfaces & the phantom-change trap

- **Never gate flagship UI visibility on a JS-runtime class-removal.** The `no-js` flash-guard (`.no-js .term{opacity:0;visibility:hidden}` + JS stripping the class on init) became a permanent hide when the class-removal raced the deferred component and lost in the user's browser. "Visible only if JS runs" inverts the contract: critical UI must be visible by default on first paint, JS only ENHANCES (auto-type, commands, LLM). Fix: strip the gate server-side (serve HTML without the class; delete the hiding CSS rule), not by adding more class-removal JS. Verify on served bytes (`<body>` class gone, zero hiding rules) AND in a live browser (`visibility:visible`, `opacity:1`).
- **"Fixed" claims about hidden UI need served-HTML proof — twice.** The landing terminal was reported fixed twice while the served HTML still carried `<body class="no-js">` and the served CSS still hid `.term`. Root cause of the repeated false claim: the fix had deployed to the WRONG Vercel project (production project instead of `{CLIENT}`). Per-environment projects are a real deploy-path hazard — `vercel --prod` from a repo root can target the wrong project. After any deploy, confirm WHICH project/alias the new bytes came from (check the deployment URL or alias in the Vercel output, then curl it).
- **LLM surfaces: probe the endpoint, don't just read the prompt.** When a chatbot repeats itself ("the LLM keeps saying X"), read the system prompt AND POST a live test query. The robotic-repetition root cause was an UNCONDITIONAL prompt instruction ("always end with '→ scheduled: intro call'") — the model obeys it on every answer. Fix is conditional phrasing ("append ONLY when the user expresses genuine interest or asks for next steps; otherwise end with 'Try /digital or /physical to explore'"). Verify behavior with a live POST to the endpoint (cache-busted), because the deployed function may differ from repo HEAD.
- **The phantom-change trap:** user instructions like "replace the static terminal" can reference an object that does not exist on the current baseline — the real task was "add". Before building to a request literally, byte-check whether the named object exists (grep the served page for its markers). Costs one command; prevents building against a phantom or "fixing" a removal that never happened.
- **Measure symmetry on the axis the user asked about.** Matching `min-height` on two panels (frame symmetry) while one panel's content is capped (`max-height:200px; overflow-y:auto`) is a hollow gain: frames match, content doesn't. When a user asks for "more room" or "the same size", the acceptance metric is the CONTENT area, not the frame — check for content caps on the panel that is supposed to grow.

## 11e. Served-value disputes, cross-page symmetry & design-tone signals

- **The cache-busted versioned ref is the ONLY arbiter of a served value — and "stale cache" is a claim, not evidence.** When two auditors dispute a served number (`.term-body` 200px vs 320px; favicon hash `cccf1c96…` vs `a720f157…`), the resolution is one command: fetch the CURRENT versioned ref from the served HTML with a `?cb=` and read the value. The "stale cache" explanation was wrong repeatedly — the disputed value simply was not in the served file. Publish the fresh read, name the losing number, and require the same protocol for the next dispute: any claim about a served value is only valid from a cache-busted fetch of the current ref.
- **Same class ≠ same render across pages.** Both division pages carried `cta-card`, yet rendered CTA containers at visibly different widths (screenshots: ~65% vs ~45% viewport). The tell was structural: `card-dark` occurrences 3 on one page, 1 on the other — extra wrapping on one side. Unifying a class name does not unify the container; verify rendered width/structure per page (screenshot read + class-count + container hierarchy), and fix by unifying the structure (shared width constraint, matching hierarchy), not by renaming classes.
- **Design adjectives are weight/register parameters, not family-shopping signals.** The "sleek" loop: user said "sleek, technological/futuristic while easily legible" → Geist Mono (reads technical) ✗ → Manrope 700 (thick) ✗ → Space Grotesk 500 ✓. The user's words: "I said sleek, you chose a thick font." The miss was weight, not family. For this user: sleek = weight 500–600 geometric sans, light tracking, sentence case; NOT bold, NOT mono, NOT heavy. After one rejection, adjust weight/register first; do not swap families hoping.
- **Brand-scoped treatments: scope to the brand's classes, verify the sibling is untouched.** A broad `.btn{font-family:mono}` rule would have rebranded the OTHER division's orange switcher. The correct shape: `.btn-cyan,.btn-ghost-dark{...}` for Digital buttons, plus a served-bytes check that `.btn-orange` carries zero font-family override. When applying a treatment to one brand inside a shared system, audit the sibling brand's element in the same pass.
- **Nav-command anchor targets must exist before wiring.** A slash command pointing at `#benefits` landed on a section ID that did not exist on the page (grep = 0). Verify every anchor target's ID exists on the target page, and use relative URLs (`/digital/#benefits`), never hostname-hardcoded — hardcoded staging hosts break on live and vice versa.

## 11f. Font rollouts, concrete-element styling targets & screenshot-surface ID

- **A declared `@font-face` + file in the repo ≠ file deployed.** The served HTML can reference `/assets/fonts/armstrong-regular.woff2` while the server 404s it (the deploy didn't pick up new assets). Before claiming a font is live, fetch the EXACT URL from the served `@font-face` and require 200. Probe verbatim and case-sensitive — a constructed probe with the wrong case (`Armstrong-Regular.woff2` vs the actual `armstrong-regular.woff2`) 404s and starts a false dispute.
- **User-supplied fonts: read the family's weight inventory BEFORE applying.** A user package can contain only Regular (OS/2 usWeightClass 400) + Extrabold with NO intermediate — "pick a sleek weight" may be impossible in that family (400 can read thin at button scale for a display face; Extrabold is the already-rejected "thick" register). Check the `.otf`/`.ttf` weight classes first, then use 400 or ask the user for an intermediate weight. Convert via COPIES from quarantined source dirs (`mats/` etc.) into `assets/fonts/`; originals untouched; license file presence noted.
- **"Use the font from that button" = replicate the reference's FULL computed font spec.** When the user points at a concrete element, the faithful reading is byte-faithful: family AND weight AND case AND tracking. The off-by-one-weight failure: the room applied Geist 500 while the reference `.btn-orange` computed to 600 — because the weight came from the BASE `.btn` rule, not from `.btn-orange` itself. Read the reference's computed spec through its base rules, then match all four properties, not family-plus-a-contract-picked-weight.
- **"Text too small" on a button is a RELATIVE complaint.** The user's screenshot showed the CTA at ~60-70% of the adjacent orange button's text. The fix is not "bigger than before" (12→14px), it's "equal to or larger than the sibling" — compare painted text heights across adjacent elements in one frame, and separate the user's pre-fix screenshot from the current served state before judging (the screenshot may show the previous deploy).
- **Identify WHICH surface a screenshot shows BEFORE fixing.** Two sequential fixes targeted different surfaces (topbar nav spacing, then CTA-card button spacing) because the room never confirmed what the screenshot depicted. Vision-read the context first (nav bar with links vs dark CTA card with headline + button pair), then fix that surface. A bare inline-anchor pair with ~10-15px gap inside a CTA card needs a flex wrapper (`display:flex;gap:16px;justify-content:center;flex-wrap:wrap`), not a nav-gap tweak.

## 11. Reporting contract (what the verifier ships back)

- Table of surfaces/routes with status, verified minutes ago, timestamped.
- Every claim labeled found / inferred / could-not-verify, with confidence (high/moderate/low).
- Explicitly separate "your files are clean" from "production serves clean bytes" — different evidence chains.
- **Adopt the two-state vocabulary in every report: "implemented locally" vs "live on staging/live".**
  A fix can be complete in the working tree and NOT yet pushed/deployed — both states are legitimate,
  but a report that says "done" when the artifact is only local reads as a false claim and burns trust
  (this exact gap repeated three times in one session: work verified locally, served artifact still old,
  because the push hadn't happened yet). State the state explicitly; the reviewer then checks the served
  artifact only when the claim is "live".
- Name the next owner for each open gap (@{RELATIONSHIP} fix, @{RELATIONSHIP} gate addition).

## 12. Client-side JS verification when no browser can reach localhost

The browser tool (browser_exec / browser_use) blocks `localhost` and `127.0.0.1` — requests to a private/internal address are rejected ("Blocked: URL targets a private or internal address"). So you CANNOT drive a `python3 -m http.server` local site through the browser tool to verify client-side rendering. Serving on a public host just to test is absurd overhead. Use a **Node DOM shim** instead — it executes the page's real functions against the real files and catches bugs a syntax check misses.

Trigger: a static `index.html` (or any page with inline `<script>`) needs render/behavior verification, and the browser tool is unavailable or blocked.

Method:
1. Serve the site only if you need to confirm HTTP 200s of asset paths (`curl` is enough; you don't need a browser). For logic, skip the server.
2. Extract the inline `<script>` (regex `<script>(.*)</script>` with DOTALL) from the HTML.
3. Build a minimal DOM shim: `document.getElementById` / `createElement` returning lightweight element objects with `classList` (add/remove/toggle/contains), `appendChild`, `setAttribute`, `textContent`, `innerHTML`, `value`, `querySelector(All)` (return [] / null), `addEventListener` (noop), `createTextNode`. Implement a `fetch` override that reads local files from a BASE directory (`path.join(BASE, url)`) and returns `{ok, status, json: async()=>JSON.parse(txt)}`.
4. Provide `global.location = {protocol:'http:'}` and `global.Option = (t,v)=>option` (the page may call `new Option(...)`).
5. Run the page script, then drive its REAL exported functions: `await fetch('navigation.json')` → `NAV = ...`, `populateJuzSelect()`, `populateSelectors()`, `renderVerses(await loadSurah(1), null)`, `openStudyPane(fakeWord, fakeAyah)`. Assert on shim element state (`children.filter(c=>c._cls.has('ayah-card')).length`, `_text`, `_html.includes('scaffold-badge')`).
6. Strip the page's own init IIFE (split on `// ─── Init ───`) so only your harness drives execution — avoids double-invocation and lets you set `NAV` deterministically.

What it catches that `node --check` does not: `ReferenceError: X is not defined` (an undeclared DOM binding the original dead markup never exercised), and null-deref at load time from calling a populator before the async `fetch` assigns its data (`NAV` still null). Both are page-crashing in a real browser but invisible to a syntax-only check. In this session the technique caught two such bugs in the {CLIENT} `index.html` before close (missing `juzSelect` declaration; premature `populateJuzSelect()` before `NAV` loaded).

Pitfalls within this technique:
- The shim's `innerHTML=''` must clear `children` (real DOM does) — otherwise stale nodes from a previous render leak into your assertions and throw on `.children[0]`.
- `appendChild` in real code may also call `document.createTextNode` — the shim must implement it or you get `createTextNode is not a function`.
- Hardcode the BASE directory as an absolute path string; a Python-side `ROOT` variable is NOT visible inside the Node script (the `fetch` closure won't resolve it). Inline it when generating the harness.
- The shim doesn't parse `innerHTML` into child nodes, so for markup-branch checks (e.g. a scaffold notice) read the raw `_html` string and `includes()` the marker class, rather than walking `children`.
- `document.querySelector` / `querySelectorAll` in real code return element objects (e.g. `s.querySelector('.wazn-toggle')` to bind a click handler). The shim's no-op `()=>null` will throw `Cannot read properties of null (reading 'addEventListener')` inside a handler-bound block. Make `querySelector` return a benign stub El (and `querySelectorAll` return `[]`) so handler-binding lines pass without crashing. Note this means markup-branch content is only observable as the PARENT's `_html` (children append via `appendChild`, their own `_html` not merged into the parent) — iterate `parent.children` and check each child's `_html`, not `parent._html`.
- `documentElement.style.setProperty` must work: a real browser sets CSS custom properties this way. In the shim, `style` is an object literal; `setProperty` as a method whose `this` is `style` (not `documentElement`) will fail when you do `DE.style={setProperty(k,v){this._attr[...]}}`. Make the closure capture the attribute store (e.g. `_deAttr`) so `applyTheme` (`document.documentElement.setAttribute('data-theme',...)` + `style.setProperty('--ink-arabic',...)`) is verifiable.
- Batch your assertions; a single harness run that finishes with `ALL_TESTS_DONE` and zero `HARNESS_ERR` is the proof. Re-running the page script inside one Node process more than once will double-register globals (e.g. the page's own init IIFE) — prefer one fresh `node` invocation per harness, or guard the IIFE.

## Pitfalls

- **Terminal hardline blocklist:** very long inline shell one-liners get rejected as unparseable; the payload is auto-saved to `~/.hermes/profiles/<profile>/cache/blocked-scripts/blocked-*.sh` — do NOT retry inline, run `terminal(command="bash <saved-path>")`.
- **Stale duplicate build directories** after a restart/rebuild: announced path ≠ actual path happens. Before reviewing, search for candidate dirs (`search_files`, target='files', glob for the version dir name), compare git logs + mtimes + titles; quarantine (don't delete) stale copies.
- **Verify teammate edits in the tree that actually deploys.** A teammate can truthfully report "8 stale refs replaced" and be wrong in effect: the edit landed in the stale twin tree while the canonical build still carries the old refs. Grep the canonical tree (the one STATE.md + git log + newest mtimes point at) for the claimed change — one command settles it.
- **Naming debt hides on satellite properties:** renaming a public label (project → product name) requires grepping EVERY deployed property's `<title>`/meta, not just the main site.
- **Hash-routing SPA shells fake clean URLs:** `/digital` returning 200 proves nothing if every route returns the same document+title and client JS picks the view. Multi-page static (real files per route) eliminates the entire bug class.
- **A 404 on a constructed URL may be your probe bug, not the site's.** Once I probed `assets/svg/{CLIENT}` (prefix stripped) → 404, and declared a site fault; re-probing the EXACT URL from the served DOM (`/assets/svg/{CLIENT}?v=1`) returned 200. Rule: extract URLs from the served HTML, probe them verbatim, and before reporting a broken asset re-probe with the verbatim URL. Distinguish "my probe path" from "the document's path" explicitly.
- **SVG vectorization claims need a raster-embed check, not a size check.** A "converted" SVG can be a PNG wrapped in `<image>`/base64 — same visual, no vector benefit. Gate: `grep -cE '<image|base64' file.svg` must be 0; path counts (`grep -oE '<path ' | wc -l`) give scale. Also verify `<img width/height>` attributes match the SVG's actual dimensions — stale raster-size attrs on square vector marks distort rendering (1109×1131 attrs on a 1447² SVG).
- **MANIFEST paths may be rooted at the parent dir.** Entries like `vers/{CLIENT}` make `shasum -a 256 -c` fail with "No such file" when run INSIDE the build; it passes from the parent. Check the entry prefix and run from the directory the manifest was generated in — or report the mismatch as a path-root problem, not a content failure.
- **Unreferenced dead weight still ships.** A retired derivative deleted from all HTML but left in `assets/opt/` still deploys with the bundle. Sweep for orphaned files (referenced-vs-present diff) in the same pass as the stale-reference grep.
- **Quantify "below the bar" before rebuilding:** when the user says a site is far from exemplar sites, measure both live pages — count `h1/h2/h3/<section>/<a>` occurrences and text bytes. One such audit showed {CLIENT} gateway at 2 H1, 0 H2, 0 H3, 0 sections vs bshiyat's 1/7/22/8 with 23 links — proving "a hero with no page underneath it," which dictates a section-by-section rebuild rather than styling tweaks. Numbers settle design debates faster than taste.
- **"Still not enough flair" is a design-depth signal, not a motion request.** After the functional rebuild, the user's bar was "hit them with the understanding that we can do things which to them are impossible" — the winning response was an interactive, parameter-driven proof element with an honesty guard, not more animation. Measure content depth against exemplars and add one flagship interactive moment per surface before reaching for decorative motion.
- **Perf regressions hide behind CSS gating.** A component can be `display:none` on mobile while its script still parses and runs, tanking mobile Lighthouse. The fix is viewport-gated script execution (`defer` + `innerWidth` early-return), and the gate must re-measure at a mobile viewport after every interactive feature lands.
- **Global identifier swaps (phone/email/domain) need a three-surface zero-occurrence sweep.** "Change the phone number" is only done when: (1) `git grep '<old-value>' HEAD` returns 0 across the WHOLE tree (source is fully excised), (2) each served page's HTML carries the new value and zero old ones (cache-busted), and (3) the served data/JS files (command maps, configs) carry the new target. A swap verified on pages but not in the served command map leaves `/call` dialing the old number — grep the served component file too. Report the zero-count as the evidence; it is stronger than counting new-value occurrences. Also verify the LLM prompt carries the new value if the assistant answers contact questions.
- **One unauthorized push to live breaks the entire review loop.** A single staging-intended deploy that hit live without user review caused cascading rework: the user kept screenshotting the unapproved version, the room iterated against staging-only builds, and the mismatch produced a multi-round incident. Deploy-target lock: no deploy command runs without an explicit target (`--target=live|staging`) AND a second agent's confirmation. If the tooling can't enforce it, the process contract must — and the environment swap verification (11b) is what catches it when it breaks anyway.
- **"Fixed" claims about interaction behavior need the user's ground truth, not just code truth.** The room verified click-split "in code" twice while the user still experienced navigation — the mechanism was markup-level (giant anchor), invisible to handler-level checks. When the user contradicts a verified claim, reproduce on the live URL first, then hunt the mechanism the code-inspection missed.
- **Screenshot receipts expire: artifact mtime must be ≥ source mtime.** A "verification screenshot" 9 minutes OLDER than the source it documents proves nothing — it shows the pre-fix state (old enemy {CLIENT}, old layout) and can be announced alongside real fixes. Before accepting a visual receipt, compare `stat -f %m screenshot.png` vs source mtime. A victory-screen capture also documents none of the interactive fixes — the receipt must show the mid-interaction state (mid-battle, counter live).
- **Headless sims pass; real interaction fails (announce-and-hope trap, recurring).** An autofight sim typing on a fixed cadence can play a full battle to VICTORY while real (slower, irregular, human-pace) typing dead-locks the game — the sim's cadence never exercised the failure path (late final letter, >1s pauses, early-guard swallows). "Works headless" is a one-time diagnostic pass, not an acceptance gate. The gate is real interaction on the served page; when the user reports input dead after a headless "VICTORY," the sim is the suspect, not the user.
- **Wrapper CSS ≠ element layout.** Repositioning a framework-rendered element requires targeting the element's OWN internal layout — the framework child carries its own offset/padding, so `top:0` on the wrapper moves nothing visible (user asked 4× before the real node was found). Rule: when a user repeats the same layout request, the previous fix targeted the wrong DOM node; find the element's own computed rect and verify against the live page mid-interaction.

## References

- `references/multi-agent-web-build-case.md` — condensed case file: {CLIENT} site (asset impostors, checkerboard forensics, mid-migration domain states, v3/v4 path drift, exact probe outputs).
- `references/presentation-integrity-and-interactive-proof.md` — the "weird text" incident and flagship terminal: scaffold-copy failure mode, parameter-driven responder + honesty guard spec, viewport-gated JS perf fix (Lighthouse 78→92), axis-agreement check, push≠deploy, and the user's marketing-site design bar.
- `references/{CLIENT}` — {CLIENT} typing-game framework: the served-bundle-vs-announced-fix decoupling cycle (repeated 4+ times), TS-in-inline-script breaking raw static hosts, dist/-in-.gitignore silent broken deploy, cache-busting + cache-control fix, negative-DNS-cache split, and the Cloudflare API DNS-record workflow with end-to-end verification.
- `references/{CLIENT}` — the v6.5 unauthorized-push incident and rollback round: byte-matching live to git commits, the marker-table verification that caught a false "swap complete" claim, exact-tree rollback with clean endpoint removal, the baseline-restore-loses-fixes trap, nested-anchor click bug, and the vision-misread "3-column" phantom.
- `references/{CLIENT}` — the interactive-terminal rounds (v6.9→v6.13): no-js flash-guard race (flagship hidden, two false "fixed" claims), wrong-project Vercel deploy path, conditional LLM system-prompt fix (robotic "intro call" repetition), the phantom "replace the static terminal" trap, frame-vs-content symmetry axis, and the universal slash-command map pattern (data-driven dispatch + aliases, relative anchor targets).
- `references/{CLIENT}` — late-round disputes and the tone loop: the 200px-vs-320px height dispute (settled by cache-busted fetch), the conflicting favicon-hash audit (cccf1c96 vs a720f157, re-fetch settled it), same-class-different-width CTA asymmetry, the Geist Mono → Manrope 700 → Space Grotesk 500 "sleek" loop, and brand-scoped font treatment.
- `references/{CLIENT}` — v6.17/v6.17.1 contact-info round: LLM prompt carrying email+phone with exact-contact instruction, `/call` target verified by reading the served component file (not the HTML mount config), and the three-surface phone-number swap (git grep zero-proof + served pages + served JS/prompt).
- `references/{CLIENT}` — v6.18→v6.20: user-supplied Armstrong font (weight inventory 400/Extrabold only, declared-but-404 probe bug, quarantine-copy conversion), "use the font from that button" off-by-one-weight (reference computed 600 via base `.btn` rule), relative "too small" CTA text, and the wrong-surface fix (topbar vs CTA-card spacing).
- `scripts/audit_live_site.sh` — deterministic live-site probe: cache-busted route matrix with titles, viewport-meta check, and per-CSS mobile-readiness counts (@media / clamp / vw / max-width cages).
- `references/node-dom-shim-verification.md` — the Node DOM-shim technique for verifying client-side JS logic when the browser tool is blocked from localhost: harness skeleton, the four shim pitfalls, and the two load-crashing bugs it caught in the {CLIENT} Quran-wide scaffolding build.
