<!-- GENERICIZED: 12×{CLIENT}, 10×{RELATIONSHIP} | source: skills/software-development/deploy-artifact-verification/references/{CLIENT} -->
# Worked Example: {CLIENT} on GitHub Pages

A rhythm-typing game framework (TypeScript, esbuild → `dist/bundle.js`, hosted on GitHub Pages). The session burned many rounds because fixes were announced as "live" while the served artifact stayed stale or out-of-sync. This is a concrete reproduction of every failure mode and the exact commands that pinned the truth.

## Timeline of the Repeated Failure

1. Agent: "Fixed, committed and pushed."
2. User: "Still broken — correct keys register as MISS."
3. Agent: "It's your browser cache, hard refresh."
4. (repeat three more times)
5. Reality each time: the **served** bundle/HTML did not contain the announced fix.

## Failure Mode 1 — Bundle renamed / old file 404

The bundle was renamed `bundle.js` → `game.js`, but earlier analysis grepped the wrong URL and got a 404 HTML page ("Page not found · GitHub Pages") — which has ~9KB of HTML and no JS, so `grep` for JS symbols returned nothing, misleading the diagnosis.

**Lesson:** Always confirm the served file is actually the artifact you think it is:
```bash
curl -sI https://{RELATIONSHIP}.github.io/{CLIENT} | grep -E 'HTTP|content-type'
# expect: HTTP/2 200, content-type: application/javascript
```
A 404 returns an HTML error page; grep results on it are meaningless.

## Failure Mode 2 — HTML references methods the bundle doesn't define

`demo.html` called `feedbackLayer.getAccuracy()`, `.getRanking()`, and `.playCelebration()` at game end. The served `game.js` defined **none** of them (verified: `grep -c getAccuracy game.js` → `0`). Result: `TypeError: getAccuracy is not a function` thrown in `endGame()` → UI froze with approach rings stuck on screen. The team kept diagnosing it as a "stuck visual state" when it was a missing-method crash.

**Lesson / check:** diff the method calls in HTML against methods defined in the bundle:
```bash
curl -s https://{RELATIONSHIP}.github.io/{CLIENT} | grep -oE 'feedbackLayer\.[a-zA-Z]+' | sort -u
curl -s https://{RELATIONSHIP}.github.io/{CLIENT} | grep -c 'getAccuracy\|getRanking\|playCelebration'
```
If the first list has entries the second reports as 0, the UI will crash on that call.

## Failure Mode 3 — `dist/` in `.gitignore` means bundle never pushed

When `dist/` was in `.gitignore`, the compiled bundle never reached GitHub, so the live site imported a file that didn't exist. The HTML loaded (skeleton) but every import failed silently.

**Fix:** remove `dist/` from `.gitignore`, rebuild, commit the bundle.

## Failure Mode 4 — Served file lags the git commit

GitHub Pages CDN can serve the old file for 1–3 minutes after a push, and can cache aggressively (`cache-control: max-age=600`). So even a correct push can briefly serve the previous version.

**Lesson:** after pushing, wait for deployment propagation, then verify the served file (not the commit) before declaring live. Compare `last-modified` on the served file against the commit time.

## Failure Mode 5 — Wrong time-source / lead-in assumptions (behavioral)

The "first key has no approach ring" bug: the beat-map generator placed the first note at `LEAD_IN_MS`, but the ring system filtered `timeUntilHit > preemptTime`, so on difficulties where lead-in > preempt the first ring was silently skipped. Fix: make lead-in match the per-difficulty preempt, or widen the spawn filter for the first note.

The "rings desync from timing" bug: the ring reached full shrink at `note.time`, but hits were judged as soon as pressed (often early), so the character advanced while the ring was still ~30% un-shrunk. Fix: collapse the ring on judgment (in the same frame the character advances), not on `note.time`.

## Failure Mode 6 — Build-to-wrong-filename + docs written against source

Two compounding traps broke the "forkable handoff package" (README, PLUGIN_GUIDE, API_REFERENCE, EXAMPLE_PLUGIN, CONTRIBUTING):

1. **Build wrote to the wrong file.** The team kept running `npx esbuild src/index.ts --outfile=dist/bundle.js` while `demo.html` and all docs imported `./dist/game.js`. Every fix landed in the never-served `bundle.js`, so the file the browser actually loaded stayed stale. The export list in served `game.js` still showed the old symbols.
2. **Docs documented an API the bundle never shipped.** README's quickstart called `createSession({...})` — written against `src/session.ts` — but the served bundle had no `createSession`, `{CLIENT}`, or `SessionOptions` anywhere. A forker cloning and following the quickstart hits a 404 import + `createSession is not a function`. The handoff was internally consistent (README, PLUGIN_GUIDE all referenced `createSession`) yet entirely broken against the artifact.

**Root cause in both:** docs and build commands were verified against `src/`, not against what `raw.githubusercontent.com` actually serves.

**Fix:** after any handoff/docs change, verify against the served artifact:
```bash
# 1. Does the served bundle export the API the docs promise?
curl -s https://raw.githubusercontent.com/{RELATIONSHIP}/{CLIENT} | tail -25
#    → the export list must include createSession etc.

# 2. Do every doc's import paths match a real served file?
curl -s -o /dev/null -w "%{http_code}" https://raw.githubusercontent.com/{RELATIONSHIP}/{CLIENT}
#    → 200, not 404

# 3. Is the build filename == the import filename?
curl -s https://{RELATIONSHIP}.github.io/{CLIENT} | grep -o 'from .*\.js'
#    → must equal the --outfile used by the build command in the docs
```

**Lesson:** a handoff whose docs describe an unshipped API is worse than no docs — a stranger's FIRST command fails and they abandon the repo. Docs must be grep-verified against the served artifact, not the source, before calling a package "forkable."

## The Commands That Actually Pinned the Truth

```bash
# Did the served bundle get the fix? (grep the served file, not src)
curl -s https://{RELATIONSHIP}.github.io/{CLIENT} | grep -o 'LEAD_IN_MS = {[^}]*}'
# → var LEAD_IN_MS = { easy: 1500, medium: 1e3, hard: 600, expert: 350 };

# Timing windows actually in the served bundle
curl -s https://{RELATIONSHIP}.github.io/{CLIENT} | grep -o 'perfect: [0-9]*\|great: [0-9]*\|good: [0-9]*'

# Is the method the HTML calls actually defined in the bundle?
curl -s https://{RELATIONSHIP}.github.io/{CLIENT} | grep -c 'getAccuracy'

# Which file does the served HTML import?
curl -s https://{RELATIONSHIP}.github.io/{CLIENT} | grep -o 'from .*\.js[^"]*'
```

## Reporting Rule Derived From This Session

Do not say "it's fixed / it's live" on the strength of a git commit or another agent's claim. Verify the served artifact first. If a user has already been told "hard refresh" more than once, the served file is almost certainly the problem — show them curl evidence instead of another cache instruction.
