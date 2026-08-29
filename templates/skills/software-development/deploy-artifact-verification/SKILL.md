<!-- GENERICIZED: 3×{CLIENT}, 1×{RELATIONSHIP} | source: skills/software-development/deploy-artifact-verification/SKILL.md -->
---
name: deploy-artifact-verification
description: "Verify the served artifact before declaring a fix live."
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [deployment, qa, verification, github-pages, debugging, served-artifact]
    related_skills: [dogfood, systematic-debugging]
---

# Deploy Artifact Verification

## When to Use

- A fix was committed/pushed but a user reports it's "still broken" or "no change."
- A teammate announces a fix is "live," "verified," or "pushed" — before trusting or relaying it, confirm it in the SERVED file.
- An app deploys a compiled bundle (esbuild/webpack) from a `dist/` folder that can drift out of sync with `src/`.
- A page's HTML/CSS skeleton exists but its interactive logic appears dead or crashes on interaction.

## Core Principle

**The served artifact is the truth — not the git commit, not `src/`, not the announcement.**
The browser executes what the server returns. If that file is stale, missing, or out-of-sync with the source, every fix is invisible no matter how correct the code is. Unit tests passing in isolation prove nothing about what ships.

## The #1 Root Cause: Stale or Unsynchronized `dist/`

The most common reason "the fix isn't shipping": the bundle in `dist/` (and thus on the host) was never rebuilt after the source changed. Source edits do NOT propagate automatically.

**Fix (always rebuild the bundle, then re-serve):**
```bash
# esbuild example — run this after ANY src/ change
npx esbuild src/index.ts --bundle --outfile=dist/bundle.js --format=esm
git add -A && git commit -m "rebuild bundle" && git push
```
Before declaring anything live, confirm the built bundle contains the new symbol/value:
```bash
curl -s https://host/path/dist/bundle.js | grep -c 'setStartTime\|LEAD_IN_MS\|getAccuracy'
```

## Verify the Served File (do this BEFORE blaming cache or the user)

When someone says a fix is live, or a user says it's still broken, verify what the server actually returns:

```bash
# 1. Confirm the served bundle contains the fix's distinctive symbols/values
curl -s https://host/path/dist/bundle.js | grep -o 'LEAD_IN_MS = {[^}]*}'          # constants
curl -s https://host/path/dist/bundle.js | grep -o 'perfect: [0-9]*\|great: [0-9]*\|good: [0-9]*'  # config values
curl -s https://host/path/dist/bundle.js | grep -c 'methodName'                     # method presence

# 2. Check the served HTML is the version you think it is
curl -s https://host/path/demo.html | grep -n 'function startGame\|setStartTime\|results-overlay'

# 3. Confirm the HTML actually imports the file that has the fix (filenames change!)
curl -s https://host/path/demo.html | grep -o 'from .*\.js[^"]*'
```

**Pitfall — do NOT blame the browser cache first.** This session's team said "it's just your cache, hard refresh" four times, and each time the real problem was a genuinely stale/out-of-sync served file. Only claim cache after you have confirmed via `curl` that the served artifact is correct. If you can't see the served file, tell the user that — don't guess.

## GitHub Pages: Two Endpoints — Which Is Truth

GitHub Pages serves two addresses for the same commit, and they lag differently. Check the RIGHT one to avoid misreading CDN lag as a code bug:

```bash
# 1. raw.githubusercontent.com — the COMMIT. Instant, source of truth for what was pushed.
curl -s "https://raw.githubusercontent.com/<owner>/<repo>/main/dist/bundle.js"

# 2. <owner>.github.io — the CDN. Lags 1-3 min behind a push; can also serve a stale copy longer.
curl -s "https://<owner>.github.io/<repo>/dist/bundle.js"
```

- To verify a fix actually **shipped**, grep `raw.githubusercontent.com` — if the symbol is there but missing from `github.io`, the fix is committed and just waiting on Pages propagation (tell the user "wait 2-3 min", don't re-fix).
- To diagnose what the **browser is running right now**, grep `github.io` — if the symbol is there, the browser is serving stale cache (then cache-bust with `?v=N` or incognito); if it's NOT there, the fix didn't ship.
- Also compare `curl -sI` `last-modified` between the two — a `github.io` `last-modified` older than your commit time confirms CDN lag.

**Pitfall — "the bundle is current" does NOT mean "the fix is in the bundle."** A bundle can be freshly pushed yet still missing the fix, because the source changed but `npx esbuild` was never re-run (dist/ is a build artifact, not auto-updated by src edits). When grep-ing the served bundle, grep for the fix's *distinctive value*, not just any related symbol — e.g. confirm `LEAD_IN_MS = {easy: 1500...}` exists rather than only that `LEAD_IN_MS` appears. One session announced a case-insensitive judge fix as shipped, but the served bundle's single `toLowerCase()` was in an unrelated `normalizeKey2` helper — the actual `evt.char !== expected.key` comparison was untouched. Grep the exact code path the fix targets.

**Pitfall — build to the SAME filename the HTML/docs import.** A team kept running `npx esbuild src/index.ts --outfile=dist/bundle.js` while `demo.html` and the README imported `./dist/game.js`. Every fix landed in `bundle.js` (never served), so `game.js` — the file the browser actually loaded — stayed stale, and the user kept seeing old behavior. Before rebuilding, read what the HTML/docs actually import: `curl -s <host>/demo.html | grep -o 'from .*\.js'`, then build to THAT exact filename. Changing the filename in docs without changing the build output is how this drifts.

**Pitfall — docs written against source describe an API the served bundle never exports.** A "fork this repo and build a game" handoff package can pass every doc check yet be broken on arrival: README and PLUGIN_GUIDE were written against `src/session.ts` calling `createSession()`, but the shipped bundle still had the OLD export list and no `createSession` at all. A forker cloning and following the quickstart hits `import ... from './dist/bundle.js'` (404) and `createSession is not a function`. **Verify docs against the SERVED artifact, not the source:** `curl -s https://host/dist/game.js | tail -20` should show the documented exports, and every import path in the docs must match a real served file. A handoff that documents an unshipped API is worse than no docs.

## Distinguish the Three Failure Modes

| Symptom | Likely Cause | Check |
|---|---|---|
| Served file missing (`404`) | Bundle was `.gitignore`'d, never pushed | `curl -sI <served-js>` → expect `200`, not `404` |
| Served file present but old content | `dist/` stale OR host CDN lag | `curl` + grep for the new symbol; compare `last-modified` |
| HTML present, logic dead / crashes on interaction | HTML references methods the bundle never defines | Cross-file check below |

## Cross-File Reference Consistency (the "dead UI" bug)

A UI that renders but does nothing, or freezes/crashes on interaction, is often **HTML calling methods the bundle does not export.** The skeleton ships; the implementation doesn't.

Example from the field: `demo.html` called `feedbackLayer.getAccuracy()`, `.getRanking()`, and `.playCelebration()`, but the served `game.js` defined none of them. On the last note, `endGame()` called `getAccuracy()` → `TypeError: getAccuracy is not a function` → silent crash, and the UI froze with rings stuck on screen.

**Check — grep BOTH sides and diff:**
```bash
# Every method the HTML calls on framework objects...
curl -s https://host/path/demo.html | grep -oE 'feedbackLayer\.[a-zA-Z]+' | sort -u
# ...must exist in the bundle.
curl -s https://host/path/dist/bundle.js | grep -oE 'getAccuracy|getRanking|playCelebration' | sort -u
```
Any method in the left set missing from the right set is a crash waiting to happen. This is a class-level integration bug that unit tests (which exercise components in isolation) will never catch.

## Cache-Busting Best Practice

- Add `?v=N` to the bundle import in the HTML (`from './dist/bundle.js?v=3'`) and bump `N` on each deploy — forces browsers past cached copies.
- Add `<meta http-equiv="cache-control" content="no-cache, no-store, must-revalidate">` for the page itself.
- For manual debugging, a private/incognito window or `Empty Cache and Hard Reload` (right-click refresh in Chrome) bypasses cache definitively.

## Multi-Environment Deploy Loop (Staging-First + Review Gate)

When a site is user-reviewed before shipping, the loop is **build → staging → QA + visual pass on staging → user approval → promote to live**. The single biggest process failure is an **unauthorized direct-to-live push** — it breaks the review gate, and every subsequent "fix" goes to staging while live stays stuck on the unapproved version, so the user keeps seeing the old broken state and the room iterates against the wrong baseline.

**Deploy-target lock (make it structural, not a hope):** no deploy command runs without an explicit `--target=live|staging` and a second agent's confirm. If tooling can't hard-fail a staging-intended promote, the contract is: the live deployment only ever comes from an explicitly approved staging hash. Without this, "push to live" and "push to staging" are two commands on the same pipeline and nothing stops a wrong-target deploy.

**Recovering from a broken baseline (the swap):**
- The **user's directive is authoritative**: live → last-approved version, staging → the working version. Revert to exact commits (`git` commit SHAs, byte-verified), not "latest known-good."
- **Verify the swap landed by ground truth, not room claims.** In one round two separate "rollback done, verified" reports were both false — the live bytes still served the unapproved version (`/api/ask` still returned 200 instead of 404). Always re-curl the live surface yourself after a rollback: check for a distinctive removed feature (`/api/ask` → 404, a command no longer in the HTML) rather than trusting the announcement.
- When a version that added a backend endpoint is rolled back, confirm the endpoint actually 404s (the removed `api/` dir makes the route dead) and that the env var goes dormant — clean surface removal, not just code revert.

## Version CSS/Asset Refs AND Verify Through a Cache-Buster

The "stale vs live bytes" dispute recurs whenever a deploy changed layout but the stylesheet URL stayed unversioned. Images get `?v=N` but CSS is often left bare — yet CSS is the one asset class that changes layout. A browser holding the old CSS against new HTML renders **run-together/run-on text** (e.g. `SPECspecificationC34 grade` where a `display:flex;gap:8px` rule never arrived). Symptom is identical to a code bug, but it's a stale-cache-against-new-HTML artifact.

**Kill the class permanently:**
- Version **every** asset reference on every deploy — CSS included: `/gateway.css?v=<deploy-sha>`, same for `system.css` and per-page sheets. Bump `?v=` in the same commit as the CSS change (a version bump *after* the fact re-creates the stale window).
- Make verification **deterministic**: every gate/probe fetches through a cache-buster (`?cb=<deploy-sha>` appended to HTML/CSS), so "stale vs live" is never a room argument. The `?v=` on prod refs and the `?cb=` on verification fetches are two different things — the former forces browsers past cache, the latter stops agents from reading cached bytes and calling it "live."
- A raw `curl https://host/...` can return cached bytes; if you're disputing whether a fix shipped, append `?cb=` and note it.

## Verify the Served DOM Structure, Not Just JS Handlers

A UI can behave "wrong" because of **markup structure**, not JS. Example: a terminal panel that "still navigates when clicked" despite every code-level check passing — the panel was a single giant `<a class="half" href="/digital/">` wrapping logo, headline, AND terminal. `stopPropagation` on a click handler can't stop anchor default navigation (that needs `preventDefault()`), and the grep found "no onclick" because there was no handler — the anchor's *native* behavior was the navigation.

**Lesson:** verify the served DOM structure, not just the JS handlers. `curl` the page and inspect the actual element tree — is a clickable region an `<a>`/`<button>` (native behavior) or a `div` with a handler (JS behavior)? The interaction contract lives in the markup as much as the script. This is the same "served artifact is truth" principle applied to markup instead of JS.

## "Replace the static X with the interactive X" — there may be TWO elements

When a user asks to "replace the static terminal/console/container with the interactive one," verify in the served DOM whether there are actually **two** elements before building. A common setup is a **static decorative visual** (e.g. a rendered terminal graphic in the hero — `$ {CLIENT} assess` + checkmarks, no input/cursor) **plus** a separate **interactive mount** (the real component, often placed in a below-hero "console" section). The user sees both and reports the interactive one is "in the wrong place" while the static one "is still sitting there."

This recurs because each fix touches one of the two and leaves the other: removing the static class but leaving the static visual; moving the interactive mount but leaving the console section; or adding the interactive one elsewhere instead of where the static visual sits. The durable fix:
1. **The interactive element must live where the static visual is** (often the hero) — it replaces that visual in place.
2. **Remove the duplicate** (the standalone console section) so there is exactly ONE element, interactive, in the right spot.
3. **Confirm the mount is genuinely interactive** — visible input field + blinking cursor — not a component that renders like a static graphic at hero size (an auto-type seed reading as a static render is the same failure in disguise).

**Check first, don't assume "add vs replace":** run `curl` + grep the served page for how many of the element actually exist (e.g. `grep -c 'term\|console\|device'`) and whether one is a static decoration. A user saying "replace the static one" may be misremembering — the real task might be to **add** the interactive element (there's no static one to replace), or to **move** it. Ground the build in the served DOM, not the instruction's wording.

## Verify a Class RENDERS (Computed Style), Not Just That It Exists

A QA gate that greps for a class name in markup+CSS can pass while the class does nothing. "Class exists" ≠ "class renders as designed." The durable fix: the gate checks **computed style** (e.g. `border-radius` + `background` + `box-shadow` present) for container/card classes, not just class presence — so "is this a real card or a hollow wrapper?" is settled by ground truth.

**The matching false-alarm (know your own tools):** grepping a stylesheet for `.card-warm{` and seeing only `padding:40px 24px;` does NOT mean the class is hollow — that can be a `@media(max-width:720px)` override that legitimately adjusts padding and sits *after* the full base rule. Always read the base rule (first, non-media occurrence) and/or computed style before declaring a visual regression. In one session an agent raised a "hollow card" blocker that was actually a media-query override; the class was fully styled. Check the whole rule, not the first grep hit.

## Ground-Truth a Layout Against Measured Geometry, Not a Screenshot

When re-specing or reviewing a layout (especially a mirrored/symmetric composition), don't rely on eyeballing a screenshot — a vision read can call a genuinely asymmetric layout "balanced and intentional." Measure the actual positions: `getBoundingClientRect().x + width/2` (element center-x) for each component vs the viewport midpoint (`innerWidth/2`), and the computed `gridTemplateColumns`. Then check the concrete relationship you actually need (is the flavour element left or right of center? are both content stacks on the outer edges?).

Example from the field: a "mirror the two halves" instruction produced repeated over-reads. A screenshot-based read declared the gateway "balanced and symmetric" when the Digital terminal actually sat at the outer-left (center-x ≈213) while the Physical pipeline sat toward center (center-x ≈1006) — the halves were NOT mirrored at all. Measuring both center-x values against `innerWidth/2` (800) is what finally exposed it; the user had to clarify the exact geometry three times because the room kept eyeballing instead of measuring.

**Lesson:** measure before spec'ing. A terse user instruction like "mirror X to Y" is usually unambiguous once you've measured the current state — measure first, and don't ask a multi-option clarifying question about intent when the geometry already settles it. Also catch cross-halves vertical drift the same way: `getBoundingClientRect().top` on the content stacks tells you if the two columns are vertically centered at the same midpoint (a common "mirror" failure).

## Inspecting Served Vector Assets (SVG)

Vision models can't read SVG directly, and the usual rasterizers (cairosvg/rsvg/inkscape) are often not installed. To eyeball a served SVG's fidelity (e.g. confirm a vectorized logo kept its detail/gradient/colors, or that it's a true `<path>` vector and not a PNG-wrapped-in-SVG):

```bash
# 1. Confirm it's a real vector (zero raster embeds, real path geometry)
curl -s https://host/assets/logo.svg | grep -c 'base64\|<image'   # expect 0
curl -s https://host/assets/logo.svg | grep -o '<path' | wc -l    # expect > 0

# 2. Rasterize to PNG on macOS without cairo/rsvg — use Quick Look thumbnails
qlmanage -t -s 720 -o . /tmp/logo.svg     # produces logo.svg.png, inspect with vision
```

`qlmanage -t -s <px> -o <outdir> <file>` is the zero-install macOS rasterizer; point `vision_analyze` at the resulting `.svg.png`. For a high-fidelity trace, expect gear teeth/network nodes/gradients to survive — an auto-traced mark that flattened detail is a real quality signal.

## The `no-js` Flash-Guard Inversion (Critical UI Must Be Visible by Default)

A common pattern is a `no-js` body class meant to hide the raw pre-load state until JS runs. But if a **critical** element's visibility depends on JS *removing* that class, you've inverted the dependency: the element is visible only if JS runs, so any race the browser loses (deferred component not yet loaded at init time, the class-removal moving into a shared component that never fires) leaves it **permanently invisible** — and the user sees an empty area where the flagship should be, reporting "the container is missing."

Example from the field: `<body class="no-js">` + `.no-js .term{opacity:0;visibility:hidden}` kept a landing-page terminal invisible unless JS stripped the class. The init script ran before the deferred component loaded, so the class never got removed — the terminal sat hidden forever, verified "fixed" against a local build that removed the class.

**Fix (structural, not patched):** serve critical UI **visible by default** and let JS *enhance* it (auto-type, commands, LLM), rather than JS being the thing that reveals it.
- Remove the `no-js` gating from the **served** HTML/CSS for anything load-bearing; the terminal renders on first paint, JS adds behavior.
- If you keep a `no-js` guard at all, it should hide only *raw scaffold styling*, not the whole component, and its removal must not be the gating step for visibility.
- Verify against **served bytes** (`curl` + grep the `<body>` class and the hiding rule) — the fix is only real when the served HTML no longer carries the class and the served CSS no longer hides the element.

## The Deploy-Target Project Wiring (staging vs production project)

`vercel --prod` (or similar) deploys to whichever project the local repo is wired to — and that can be the **production** project even when you intend a staging deploy. In one session every "staging" deploy actually went to the production project, so fixes appeared on the wrong surface and the "verified on staging" claims were false. **Before deploying, confirm which project the deploy command targets** (`vercel link`/project id / `vercel whoami` + project list), and verify the fix on the *intended* surface's bytes, not whichever one the command happened to reach.

## Reporting Discipline

- Only say "it's fixed / it's live" AFTER you have verified the served artifact contains the fix. Never relay another agent's "verified" claim without checking.
- If you cannot inspect the served file, say so explicitly and give the user the exact console/curl command to run — do not claim certainty.
- When presenting a fix to a user who has already been told "hard refresh" repeatedly, acknowledge the frustration and lead with evidence from the served file, not another cache instruction.

## Support Files

- `references/{CLIENT}` — full worked example: repeated stale-bundle debugging, the missing-method crash, and the exact curl commands that finally pinned the truth.
- `references/{CLIENT}` — worked incidents from a static multi-page Vercel site: staging-first loop + deploy-target lock, giant-anchor click bug (verify served DOM), stale-CSS run-on text (version CSS refs), hollow-card false alarm (read the base rule), and the 3-column layout misread.
