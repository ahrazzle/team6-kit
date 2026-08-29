<!-- GENERICIZED: 8×{CLIENT}, 5×{RELATIONSHIP} | source: skills/software-development/verify-deployed-artifacts/references/{CLIENT} -->
# {CLIENT} Session Example — Source/Artifact Divergence

## Context

A multi-agent team (6 agents) was building a rhythm-typing game framework ({CLIENT}) as a bundled web app. The app was deployed to GitHub Pages, where the browser loads `dist/bundle.js` — a bundled artifact built from TypeScript source via esbuild.

## The Bug Cycle

The user reported three bugs:
1. Correct keypresses registered as "miss"
2. Approach rings (rhythm-game timing indicators) not visible
3. Permanent red circle on the "7" key

The team announced fixes as "live" and "pushed" **four consecutive times**. Each time, the user reported the bugs persisted. Trust eroded.

## Root Cause

The source code (`src/*.ts`) had been fixed:
- `types.ts`: `easy: { perfect: 500, great: 700, good: 1000 }` (was 150/200/300)
- `beatmap-generator.ts`: `LEAD_IN_MS = 3000` lead-in before first note
- `particle-system.ts`: `Math.max(0, now - r.startTime)` ripple clamp

But `dist/bundle.js` was **never rebuilt**. The served bundle still had the old values. The team was verifying local source files, not the artifact the browser actually loaded.

## The Fix

```bash
# Rebuild the bundle from current source
npx esbuild src/index.ts --bundle --outfile=dist/bundle.js --format=esm

# Verify the fix is in the SERVED artifact (not local source)
curl -s https://raw.githubusercontent.com/{RELATIONSHIP}/{CLIENT} | grep "perfect: 500"
# Output: easy: { perfect: 500, great: 700, good: 1e3 },

# Commit, push, verify again after deployment
git add -A && git commit -m "fix: rebuild bundle with verified fixes" && git push
# Wait 30s for GitHub Pages deployment, then re-verify
curl -s https://raw.githubusercontent.com/{RELATIONSHIP}/{CLIENT} | grep "perfect: 500"
```

## Key Lesson

**A fix in source code that never made it into the deployed artifact is indistinguishable from no fix at all.**

The verification workflow:
1. Identify the artifact the user loads (`dist/bundle.js` at a public URL)
2. Read that artifact directly (via `curl` or `web_extract` on the raw URL)
3. Search for the fix pattern in the artifact
4. Only announce after confirming the fix is present

## Anti-Pattern

```
Agent: "Fixed and pushed. Try again."
User:  *hard refreshes* Still broken.
Agent: "Fixed and pushed again. Hard refresh?"
User:  *hard refreshes* Still broken.
Agent: "Verified in source. Must be cache."
```

This cycle repeated four times. Each cycle wasted user trust and debugging time. The fix existed in local source but never made it into the deployed artifact.

## Phase {CLIENT} — New Divergence Points After the First Fix

The first rebuild worked, then a second wave of "fixed but still broken" reports surfaced new divergence points:

### 1. Rebuilt the wrong file (bundle.js → game.js)

Someone renamed the bundle and switched `demo.html`'s import from `./dist/bundle.js` to `./dist/game.js`, but rebuilds kept writing to `dist/bundle.js`. The served HTML imported `game.js`; the fresh build went to `bundle.js`. Result: `curl .../dist/bundle.js | grep fix` showed the fix present while the browser loaded the stale `game.js`.

**Fix:** read the import path in the served HTML first (`grep "import.*dist" demo.html`), rebuild exactly that file, then grep the file the HTML actually names.

### 2. CDN propagation lag

After committing the correct rebuild, `curl https://raw.githubusercontent.com/{RELATIONSHIP}/{CLIENT} | grep -c "lookupKey"` returned `0` for ~2 minutes even though the local file had 22 matches and the commit was pushed. The `main` CDN serves `cache-control: max-age=300`.

**Fix:** verify at the commit SHA URL — `curl https://raw.githubusercontent.com/{RELATIONSHIP}/{CLIENT}<sha>/dist/game.js | grep -c "lookupKey"` returned `22` immediately. The SHA URL is the source of truth; `main` and the live Pages URL propagate later.

### 3. No version param on the bundle import

`demo.html` imported `./dist/game.js` with no `?v=` query param, so browsers cached the old file and every fix appeared broken until a manual hard-refresh. The permanent fix was `import ... from './dist/game.js?v=6'` — bump the version on every release so the browser fetches fresh bytes.

### 4. Verify the live Pages URL, not just raw

The definitive check after deployment is the URL the user actually hits: `curl https://{RELATIONSHIP}.github.io/{CLIENT} | grep -c "lookupKey"` → `22` confirmed the spacebar-ring and stats-display fixes were live. Raw.githubusercontent and github.io can differ during propagation; check both, and check the one the user loads last.
