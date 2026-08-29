<!-- GENERICIZED: 2×{RELATIONSHIP} | source: skills/web-app-debugging/SKILL.md -->
---
name: web-app-debugging
description: "Verify the artifact that actually runs — served web files, built bundles, Electron asar — not local source. Use when fixes are announced but behavior doesn't match."
version: 1.0.0
author: {RELATIONSHIP} ({RELATIONSHIP}), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [debugging, web, browser, bundle, served, verification, caching]
    related_skills: [systematic-debugging, drift-monitoring]
---

# Web Application Debugging

## When to Use
- Web app behaves differently than source code suggests
- Team announces fixes but the user still sees broken behavior
- You need to verify what code the browser actually executes
- Caching issues (browser, CDN, service worker)

## The Core Principle
**Local source files, git commits, and announcements are NOT what runs in the browser. The served artifact is what matters.**

If `curl <served-url>` doesn't contain the fix, the fix doesn't exist as far as the user is concerned.

## The Three-Way Divergence
In web development, three versions of the code exist simultaneously:

1. **Local source** — what developers edit
2. **Built artifact** — bundle.js, compiled CSS, etc.
3. **Served artifact** — what the browser actually loads (after CDN caching, service workers, etc.)

Bugs often exist in the gaps between these three.

## Verification Protocol

### 1. Read the SERVED file, not local source
```bash
# Verify what's actually at the served URL
curl -s https://raw.githubusercontent.com/<user>/<repo>/main/dist/bundle.js | grep "fix-string"

# Or extract and search
curl -s https://raw.githubusercontent.com/<user>/<repo>/main/demo.html | grep -n "relevant-function"
```

### 2. Compare served vs local
```bash
# Local file
grep "fix-string" dist/bundle.js

# Served file
curl -s https://raw.githubusercontent.com/<user>/<repo>/main/dist/bundle.js | grep "fix-string"

# If local has it but served doesn't → bundle wasn't rebuilt/pushed
# If both have it but user sees broken behavior → caching issue
```

### 3. Build pipeline gotchas
- esbuild/rollup/webpack bundle must be REBUILT after source changes
- `dist/` may need to be tracked by git (not in .gitignore)
- CDN/cache propagation delay: GitHub Pages can take 1-3 minutes
- **Raw vs Pages divergence:** `raw.githubusercontent.com/<user>/<repo>/main/...` reflects the latest pushed commit almost immediately; `https://<user>.github.io/<repo>/...` (Pages CDN) lags 1-3 min behind. They can disagree — verify BOTH: raw proves the commit landed, Pages proves what the user's browser will actually load. A fix "verified at raw" is not live until Pages serves it.
- Cache-busting query params (`?v=3`) force browsers to fetch new versions

## Common Patterns

### Pattern: "Fix Announced But Still Broken"
**Symptom:** Team says "fixed and pushed." User still sees bug.

**Root cause:** Fix exists in local source but bundle wasn't rebuilt, or browser is caching old version.

**Fix:**
1. Rebuild bundle: `npx esbuild src/index.ts --bundle --outfile=dist/bundle.js`
2. Push
3. Verify with `curl` that served file contains the fix strings
4. Tell user to hard refresh (Cmd+Shift+R) or use incognito

### Pattern: "Two Overlaid Interfaces"
**Symptom:** User sees two keyboards, two cursors, or duplicate UI elements.

**Root cause:** DOM elements from previous game session not cleaned up before new session starts. Common in SPAs where `createElement` is called on each `start()` but `remove()` is never called.

**Fix:** Add cleanup in `stop()` or `reset()`:
```typescript
// Remove old element before creating new
if (this.element) {
  this.element.remove();
  this.element = null;
}
this.createElement();
```

### Pattern: "Correct Keypress = MISS"
**Symptom:** User presses the right key but gets a miss judgment.

**Root cause:** Timing window mismatch — either:
- Windows too tight for the target audience (±150ms is expert-level, not beginner)
- `setStartTime()` called after bus starts (delta = billions of ms)
- Notes start at time:0 with no lead-in (no time to react)

**Fix:** 
- Widen windows for target audience (±500ms for young kids)
- Add lead-in before first note (3000ms)
- Call `setStartTime()` BEFORE `rawBus.start()`

## Desktop / Electron Packaged Apps

The same "artifact, not source" rule applies to packaged desktop apps, where the divergence is:

1. **Working-tree source** — `src/plugins/...` edits (uncommitted or committed)
2. **Packaged bundle** — `Hermes.app/Contents/Resources/app.asar` (compiled at build time)
3. **Running process** — the binary in `Hermes.app/Contents/MacOS/`, which loads code from the asar, NOT from `src/`

**Pitfall: editing `src/` does not change a packaged app until rebuild + repackage.** A source edit with mtime later than the asar's mtime is a *seed*, not a live change. Confirmed real: "patched the bundle, signature verified" was claimed while the asar was byte-identical to a file made *before* the claimed patch (the "backup" was a pristine copy, not a pre-patch snapshot) and contained zero of the claimed strings.

**Verification recipe:**

```bash
# 1. Which binary is actually running?
ps aux | grep -i "Hermes.app\|electron" | grep -v grep

# 2. mtimes are the fastest tell — source edit later than asar build = not shipped
stat -f "%Sm %N" Hermes.app/Contents/Resources/app.asar src/plugins/<name>/plugin.js

# 3. Does the shipped bundle contain the change? (extract, then grep for distinctive strings)
node node_modules/.bin/asar extract Hermes.app/Contents/Resources/app.asar /tmp/asar-extract
grep -rl "DISTINCTIVE_STRING" /tmp/asar-extract/dist/
```

A "verified signature" on a bundle proves nothing about content. Content check = extract and grep for the claimed strings.

## Pitfalls

- **Don't trust announcements.** Verify in served artifact.
- **Don't trust local source.** It may not be built or pushed.
- **Don't assume cache is fresh.** Browser cache, CDN cache, service workers can all serve stale content.
- **Don't rebuild without verifying.** After rebuilding, check the served file contains the fix.

## References

- `references/browser-served-app-debugging.md` — detailed verification protocol and real-world examples
- `references/electron-packaged-app-debugging.md` — asar-vs-source case study: "patched bundle" claim disproven on disk, extract-and-grep recipe, mtime tells
- `references/post-mvp-polish-patterns.md` — post-MVP polish patterns: method/property mismatches, ghost notes, ring/judgment desync, first-key ring, judgment color coding, end-game flow
