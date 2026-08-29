<!-- GENERICIZED: 2×{CLIENT} | source: skills/static-site-production/references/bundle-deploy-case-study.md -->
# Bundle Deploy Case Study — {CLIENT} (GitHub Pages served-vs-source drift)

## Context

{CLIENT}: a TypeScript rhythm-typing game framework, bundled with esbuild into
`dist/bundle.js`, demo at `demo.html` importing `./dist/bundle.js?v=N`, deployed
to GitHub Pages via `git push`. Every source change required: rebuild bundle →
commit page+bundle together → push → wait for Pages CDN → verify served bytes.

## Failure sequence (the user-facing saga)

1. **`dist/` was in `.gitignore`.** The bundle never got pushed. The page
   imported a missing/stale file; the user reported "can't get past the Welcome
   screen", "buttons do nothing". Root cause found only after multiple rounds:
   `git ls-files dist/` showed no bundle.
2. **Bundle not rebuilt after source fixes.** Team announced "timing fixed",
   "accuracy/ranking added" — but only `demo.html` was committed; the served
   `bundle.js` lacked `getAccuracy` / `getRanking` / `playCelebration`. On game
   end, `showResultsOverlay()` called `feedbackLayer.getAccuracy()` →
   `TypeError: getAccuracy is not a function` → game froze with rings stuck.
   Diagnosis: `curl -sL <live>/dist/bundle.js | grep -c "getAccuracy"` returned 0.
3. **Repeated "hard refresh" (Cmd+Shift+R) instructions failed.** The browser
   cache kept serving the old bundle. Definitive bypasses: incognito window
   (Cmd+Shift+N), or a NEW `?v=N` on the URL. Telling the user to hard-refresh a
   fourth time is not a fix.
4. **Temp fix pollution.** To make the first approach ring visible, a "ghost
   note" (space key at half lead-in) was injected into the beat-map. Once the
   real fix landed (per-difficulty `LEAD_IN_MS` matching preempt time), the
   ghost was NOT removed — the user reported "game is injecting spacebar key
   before user content". Removing the ghost was a separate later fix.

## The verification recipe (do this BEFORE telling the user "fixed")

```bash
# 1. Confirm the bundle is actually tracked by git
git ls-files dist/bundle.js

# 2. Rebuild bundle in the same step as the page commit
npx esbuild src/index.ts --bundle --outfile=dist/bundle.js --format=esm
git add -A && git commit -m "..." && git push

# 3. Verify the SERVED artifact (Pages CDN lags 1-3 min after push)
curl -sL https://<user>.github.io/<repo>/dist/bundle.js | grep -c "getAccuracy"
curl -sL https://<user>.github.io/<repo>/demo.html | grep -c "getAccuracy"

# 4. Confirm cache-busting is in the served page
curl -sL https://<user>.github.io/<repo>/demo.html | grep -o "bundle.js?v=[0-9]*"
```

If step 3 returns 0 for a method the page calls, the fix is NOT live. Do not
announce it is.

## Cache-busting that worked

- `<meta http-equiv="cache-control" content="no-cache, no-store, must-revalidate">` in `<head>`
- Bundle import `./dist/bundle.js?v=3` (bump per deploy — later versions: v=5, v=6)
- New `?v=N` on the URL is the reliable user-side cache bypass, not hard-refresh

## Integration contract lesson

Unit tests (46/46) passed while the deployed app froze: the page called methods
the served bundle did not define. Unit tests prove components in isolation;
nothing proved demo.html ⇄ bundle.js contract until a human curl-grepped the
live artifact. Add a post-push verification step to the deploy pipeline — it
would have caught every one of the ~7 integration bugs this project shipped.
