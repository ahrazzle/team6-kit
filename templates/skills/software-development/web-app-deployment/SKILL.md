<!-- GENERICIZED: 2×{CLIENT}, 1×{RELATIONSHIP} | source: skills/software-development/web-app-deployment/SKILL.md -->
---
name: web-app-deployment
description: "Deploy web apps and verify served files match source."
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [deployment, github-pages, static-hosting, verification, esbuild, cdn]
---

# Web App Deployment & Verification

> Deploy browser-based web apps to static hosting and verify the served bundle matches source before announcing fixes.

## When to Use

- Deploying a web app (HTML/CSS/JS, TypeScript bundled to JS) to GitHub Pages, Netlify, Vercel, or similar static hosting
- Announcing bug fixes or features as "live" to a user
- Debugging why a fix that "should work" isn't reflected in the browser
- Setting up a build pipeline (esbuild, webpack, vite) for a static site

## The Core Anti-Pattern: "Announce and Hope"

The most common failure mode in this workflow:

1. Fix committed and pushed to git
2. Agent announces "fix is live, hard refresh to test"
3. User hard refreshes — fix doesn't work
4. Agent suggests cache issue, asks user to try incognito
5. Repeat until user is frustrated

**Root cause:** The agent announced the fix before verifying the served file at the actual deployment URL. Git being up to date ≠ deployment being up to date. CDNs cache. Build artifacts get stale. Import paths change between builds.

## The Fix: Verify Before Announcing

**Before telling the user to test, always verify the served file:**

```bash
# For GitHub Pages
curl -s "https://raw.githubusercontent.com/<user>/<repo>/main/<path>" | grep -c '<fix_identifier>'

# For the deployed URL
curl -s "https://<user>.github.io/<repo>/<path>" | grep -c '<fix_identifier>'
```

If the count is 0 (or doesn't match expected), the deployment hasn't propagated or the bundle wasn't rebuilt. **Do not announce.**

## Build Pipeline Pattern (esbuild → GitHub Pages)

### Project Structure
```
project/
├── src/
│   ├── index.ts        # Entry point — exports public API
│   ├── feedback-layer.ts
│   ├── BeatClockJudge.ts
│   └── ...
├── dist/
│   └── game.js         # Bundled output (gitignored or committed for GH Pages)
├── demo.html           # Loads ./dist/game.js
├── test/
│   └── *.test.ts
└── .gitignore          # Should NOT contain dist/ if deploying to GH Pages
```

### Build Command
```bash
npx esbuild src/index.ts --bundle --outfile=dist/game.js --format=esm
```

### Critical: .gitignore Must Not Exclude dist/
GitHub Pages serves files in the repo. If `dist/` is in `.gitignore`, the bundle never gets pushed.

### Deployment Flow
1. `git add -A && git commit -m "..." && git push`
2. Wait 1-3 minutes for GitHub Pages CDN to propagate
3. Verify served file: `curl -s "https://user.github.io/repo/dist/game.js" | grep '<fix>'`
4. **Only then** tell the user to hard refresh

## Verification Checklist

Before announcing a fix is live, confirm:

- [ ] Fix is in local source (`grep` the `.ts` file)
- [ ] Bundle was rebuilt (`npx esbuild ...`)
- [ ] Bundle was committed and pushed (`git log -1 --oneline`)
- [ ] Served file contains the fix (`curl` the raw GitHub URL or deployed URL)
- [ ] Served file timestamp is recent (`curl -I` check `last-modified`)

## Common Pitfalls

### GH Pages subpath: absolute asset paths 404 (recurred 3× in one session)
GH Pages serves a project repo under a subpath (`https://<user>.github.io/<repo>/demo/`),
so **any absolute-path asset fetch dies** — `/demo/words.json` resolves to
`<user>.github.io/demo/words.json` → 404, while the same code works perfectly on a
local dev server (where the request goes to the workspace root). This is the #1
"worked locally, broke in the live demo" class bug and it recurred three separate
times in one session:
1. `fetch("/demo/words.json")` — the one absolute fetch among relative ones.
2. `img.src = "/" + CFG.enemy.{CLIENT}` → `/assets/ccbysa/...` (relative works, this died).
3. A `loadImg()` helper that **prepended `/` to every path** — silently breaking *every*
   asset (sprites, background, audio) on the subpath, not just the one flagged line.

**Fix — repo-relative prefix applied uniformly, not per-line:** compute a single
`RP = "../"` (relative to a page at `demo/index.html`; assets sit a sibling dir away)
and prepend it in ONE helper every loader uses (`loadImg` → `RP+path`, audio fetch →
`RP+track`, face/resolve sprites, background). A file already in the same dir as the
page stays bare-relative (`words.json`, not `/words.json`).

**Verification must probe the LIVE served URL, not the local page** — the bug is
invisible locally and only appears on the subpath. After deploy, curl the live
`<user>.github.io/<repo>/demo/` path and confirm the asset fetches return 200, not
just that the local page renders. This is the {CLIENT} legacy lesson; it recurs every
time someone writes a path from memory instead of confirming the served URL.

### Staging review: a fork can't stage a GitHub Pages site under the same owner

When a change needs user review before the production push (staging → review → promote),
do **not** use a fork as the staging vehicle for a GitHub Pages site. Pages URLs are
`<owner>.github.io/<repo-name>`. Forking `<repo>` to the **same owner** keeps the name
`<repo>` → identical URL to production (two sites can't share it). You'd have to rename
the fork (e.g. `<repo>-staging`), at which point it is structurally identical to a
separate `<repo>-staging` repo — but still carries the fork's upstream link and its
"sync fork" foot-gun that can silently pull production state into staging.

**Use a separate staging repo** (`<owner>/<repo>-staging`) with its own Pages URL:
- genuinely distinct artifact, no upstream link → nothing can drift in accidentally
- promotion is a deliberate `git push`, not a fork-sync
- the fork's headline benefit (PR line-diff review) is largely moot for a static site
  with large data files — the meaningful review is the *rendered result* on the distinct
  URL, not a diff of megabytes of JSON

Carry the **full build** into staging (all data files, not a shell) so the review
exercises the real thing; hold production untouched until approval. Document known
gaps (dead source slugs, absent editions, verified-vs-pending data boundary) in the
staging review notes so nothing is discovered late.

### Stale Bundle After Rename
If you rename `dist/bundle.js` → `dist/game.js`, update the import in HTML. If the HTML still references the old name, the browser loads a 404.

### Method Exists in Source but Not in Bundle
If `demo.html` calls `feedbackLayer.getAccuracy()` but the bundle doesn't define it, the game crashes at runtime. Always verify the method exists in the served bundle, not just the source.

### Timing Window Mismatch
When the lead-in time (before first note) doesn't match the approach ring's preempt time, the first ring is invisible. Keep `LEAD_IN_MS` per-difficulty equal to the preempt time.

### Array Mutation During Iteration
When injecting notes into an array while iterating, capture the original length first or iterate backwards. Otherwise inserted notes get re-processed, causing exponential duplication.

```typescript
// WRONG — inserted notes get re-processed
for (let i = 0; i < notes.length; i++) {
  if (shouldDouble(notes[i])) {
    notes.splice(i + 1, 0, doubled); // shifts length, re-processes
  }
}

// RIGHT — capture original length
const originalLength = notes.length;
for (let i = 0; i < originalLength; i++) {
  if (shouldDouble(notes[i])) {
    notes.push(doubled); // append, don't splice
  }
}
notes.sort((a, b) => a.time - b.time);
```

## Pitfalls to Avoid

- **Don't announce "hard refresh" without verifying the served file first.** If the fix isn't in the served bundle, the user wastes time and trust.
- **Don't assume git push = deployment.** CDNs cache. Always `curl` the served file.
- **Don't blame the user's browser cache** until you've confirmed the served file actually contains the fix.
- **Don't use incognito mode as a diagnostic** — it masks the real issue (stale deployment) and frustrates the user.
