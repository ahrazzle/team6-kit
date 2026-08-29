<!-- GENERICIZED: 7×{CLIENT}, 2×{RELATIONSHIP} | source: skills/software-development/web-build-verification/references/{CLIENT} -->
# {CLIENT} — GitHub Pages Served-Bundle Case

Framework: typing-rhythm game for kids (TypeScript, esbuild bundle, GitHub Pages + custom domain). Multi-agent team: researcher (this author), designer, coder, analyst, QA. Live at `{CLIENT}`.

## The meta-failure: announced fixes not in the served bundle (repeated 4+ times)

Cycle observed: user reports bug → agent announces "fixed, pushed, verified" → user tests → bug persists → another agent reads the *served* file and finds the fix absent. Root causes, each seen:

1. **Source fixed, bundle never rebuilt.** `src/*.ts` updated; `dist/bundle.js` (or `game.js`) not regenerated with esbuild. Fix committed to source ≠ fix shipped.
2. **Build output untracked.** `dist/` was in `.gitignore` → bundle never pushed → module import fails silently → page loads, all buttons dead, no console error. (GitHub Pages case.)
3. **HTML references a stale/new filename.** `demo.html` importing `./dist/game.js` after a rename, while the served directory still has the old name — or `?v=N` version never bumped so the browser reuses the old cached bundle.
4. **Inline-script TS annotations.** `demo.html` had `<script type="module">` containing `const preemptTimes: Record<string, number> = {...}`. Browsers throw a parse error on the first type annotation → the ENTIRE inline script fails → no event listeners attach → every button dead. The local dev server transpiled before serving (masking it); GitHub Pages serves the raw file. Fix: inline scripts on raw static hosts must be plain JS.
5. **HTML shell calling methods not in the bundle.** Results overlay called `feedbackLayer.getAccuracy() / getRanking() / playCelebration()` that existed in source but not the served bundle → `TypeError` mid-`endGame()` → screen froze with approach rings stuck. Symptom: "game freezes on completion," actually a missing-method crash.

### The verification that breaks the cycle

Before announcing ANY fix on a static-host deploy, probe the SERVED artifact:

```bash
# Raw source (updates at push, no CDN): does the fix exist anywhere?
curl -s https://raw.githubusercontent.com/<owner>/<repo>/main/dist/<bundle>.js | grep -c "methodOrStringName"
# What does the served HTML actually import?
curl -s "https://<site>/demo.html" | grep -oE '(bundle\.js|game\.js|dist/[a-z.]+)'
# Live bundle (cache-busted) — same check against what browsers load:
curl -s "https://<site>/dist/<bundle>.js?v=N" | grep -c "methodOrStringName"
```

Rules that ended the cycle:
- A claimed fix = 1+ occurrences in the served bundle; a claimed removal = 0 occurrences. Grep the bundle, not the source.
- Grep the served HTML for the real import path — the served document is the ground truth, not the repo HEAD.
- Distinguish "deploy lag" (raw file has fix, live site doesn't, wait 1–3 min) from "fix absent" (raw file lacks it).

## Cache-busting / stale-cache discipline

User kept hitting "still broken" after repeated "hard refresh" instructions. Permanent fixes shipped together:
- `?v=N` query param on the bundle import in `demo.html`, bumped on every deploy.
- `<meta http-equiv="cache-control" content="no-cache, no-store, must-revalidate">` in `<head>`.
- Confirmed stale-cache detection: `document.querySelectorAll('[data-role="counts"]').length` returning ≥1 = stale DOM from old bundle.
- Deployment propagation lag on GitHub Pages is real (1–3 min); check `raw.githubusercontent.com` to distinguish lag from absence.

## Recurring timing/judgment bugs (context for the verification pattern)

- `setStartTime()` not called before the bus starts → `delta = performance.now() - 0 - expected.time` ≈ billions of ms → every correct key = MISS. Unit tests passed because they never wired the integration; a single end-to-end integration test (keydown → judge → Perfect) would have caught every regression. Lesson: unit tests prove components in isolation; integration test + design review prove they work together.
- Hand-alternation generator shuffled characters, destroying user text order ("abcdef123456" → "a1c2e3b4fd56"). Character order is sacred in a typing game; hand-comfort is a generation-time constraint, not a post-hoc reorder.
- Case-sensitivity: generator preserved case, keyboard lookup lowercased → pasted "Hello" spawned no ring for `H`. Fixed with `toLowerCase()` on BOTH sides of the judge comparison (not just the lookup), keeping the user's text case intact — strict comparison would punish a child's caps-lock muscle memory as wrong keys.
- DOM lifecycle leak: each new game created a fresh keyboard SVG + judge without destroying the previous → ghost keyboards overlaid, orphaned listeners logged MISS forever. Fix = full teardown (detach bus, null judge, remove DOM) before new game, plus a `gameActive` guard on every hook.
- Negative radius in canvas `arc()` when ripple age exceeded lifetime without a cleanup pass → `IndexSizeError` spam every frame.

## DNS custom-domain launch (GitHub Pages + Cloudflare)

Process that worked (site verified live end-to-end):
1. GitHub side: commit `CNAME` (`{CLIENT}`) → set Pages custom domain via `gh api repos/<owner>/<repo>/pages` → confirm `{"cname":..., "status":"built"}`.
2. Cloudflare: token (zone DNS edit) → find zone id (`GET /zones?name={CLIENT}`) → check no existing record → `POST /zones/<id>/dns_records` with `{"type":"CNAME","name":"{CLIENT}","content":"{RELATIONSHIP}.github.io","ttl":1,"proxied":true}` → confirm `success:true` + record id.
3. Verify: `dig +short {CLIENT} A` → edge IP; `nc -vz <ip> 443` → TCP; `curl --resolve host:443:<ip>` → HTTP 200; precedent record on same proxy IP serves 200.

### Negative DNS cache trap (the one real wrinkle)

Earlier the host was NXDOMAIN; after record creation the local macOS resolver kept serving the negative result for minutes:
- `dig` resolved (bypasses OS cache); `curl` / urllib / browsers failed (use OS cache); `curl --resolve` to the edge IP returned HTTP 200.
- Diagnosis: deploy is fine, local cache is stale. Fixes: wait for TTL, `sudo dscacheutil -flushcache && sudo killall -HUP mDNSResponder`, test from another network/incognito. Label evidence chains separately: edge-live vs locally-resolvable.

### One-domain-owner rule (avoided via explicit coordination)

Vercel project and GitHub Pages both targeted the subdomain; two CNAME targets (`cname.vercel-dns.com` + TXT vs `{RELATIONSHIP}.github.io`) were floated in consecutive messages. Resolution: GitHub Pages won (public forkable repo, CNAME committed, build done, matches `acctraining.{CLIENT}` precedent) → Vercel project deleted + domain detached FIRST → then a single DNS record handed to the user. Never hand the user two competing DNS instructions.

## Security note

A Cloudflare API token pasted in plaintext in a group chat should be rotated after use, even when scoped to zone-DNS-edit. Treat any token that appears in chat as exposed.
