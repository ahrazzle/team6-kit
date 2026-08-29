<!-- GENERICIZED: 10×{CLIENT}, 1×{RELATIONSHIP} | source: skills/software-development/verify-deployed-artifacts/SKILL.md -->
---
name: verify-deployed-artifacts
description: "Use when debugging deployed apps. Verify the artifact."
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [debugging, deployment, build, verification, bundle, artifact, cdn]
    related_skills: [systematic-debugging, fullstack-monorepo-dev, dogfood]
---

# Verify Deployed Artifacts

## When to Use

Use when debugging any application where the user runs a **built/compiled/bundled/deployed artifact** rather than raw source code. This includes:

- Web apps served from a bundled file (`dist/bundle.js`, `build/main.js`, webpack/vite output)
- Compiled binaries (Go, Rust, C++, Java `.class`/`.jar`)
- Docker images running in a container
- Mobile apps installed from a build (APK, IPA, Expo build)
- Serverless/PaaS deployments (Vercel, Netlify, Cloudflare Workers, AWS Lambda)
- CDN-served assets with caching

**Use this ESPECIALLY when:**
- A fix was announced as "live" but the user reports it's still broken
- Multiple agents are working on the same codebase and announcing fixes independently
- A build step (esbuild, webpack, tsc, cargo build, docker build) sits between source and what runs
- The team is in a "fix → announce → still broken → repeat" cycle

## The Core Principle

A fix in source code that never made into the deployed artifact is indistinguishable from no fix at all. **The user's browser/process loads bytes, not intentions.**

## The Divergence Points

These are the common ways source and deployed artifact drift apart:

### Bundled Web Apps (esbuild/webpack/vite/rollup)

- **Source edited, bundler never re-run.** The fix exists in `src/*.ts` but `dist/bundle.js` still has the old code.
- **Bundler re-run but old bundle cached.** CDN, browser, or reverse proxy serves a stale `bundle.js` with a content-hash that doesn't match.
- **Cache-busting query parameter not updated.** `bundle.js?v=2` still points to the old file because `v` wasn't bumped.
- **Wrong output path.** Bundler wrote to `dist/bundle.js` but the server serves from `public/build/`.
- **Rebuilt the wrong file.** The served HTML imports `./dist/game.js` but the rebuild wrote to `dist/bundle.js` (or vice versa). The browser loads the file named in the HTML — grep THAT file, not the one you think you built. Read the import path in the served HTML FIRST.

### Compiled Languages (Go, Rust, C++, Java)

- **Source changed, `build` never invoked.** The old binary is what's running.
- **Binary rebuilt but old process still running.** The running process has the old code in memory; restart required.
- **Cross-compilation target mismatch.** Built for the wrong OS/architecture; deployment silently fell back to old image.

### Docker / Containers

- **New image built but old container still running.** `docker compose up` without `--force-recreate` keeps the old container.
- **Image tag not updated.** Deployment manifest still references `myapp:v1.2.3` while the fix is in `v1.2.4`.
- **Multi-stage build cache.** A cached layer prevents the fix from being included in the final image.

### Serverless / PaaS (Vercel, Netlify, Cloudflare, AWS Lambda)

- **Deployment step skipped or failed silently.** Platform is still serving the previous successful deployment.
- **Preview deployment vs. production.** Fix is in a preview URL but production wasn't promoted.
- **Edge cache / CDN.** Platform cached the old response; cache invalidation didn't propagate.

### Mobile (Expo, native builds)

- **JS bundle cached on device.** Old bundle loaded from disk; reload required.
- **OTA update not fetched.** `expo-updates` bundle is stale; app needs a restart or forced update.
- **Native binary not rebuilt.** JS changed but the native build that wraps it wasn't regenerated.

## The Verification Workflow

**BEFORE announcing a fix as "live" or asking the user to test:**

### 1. Identify the exact artifact the user loads

Ask yourself: what bytes does the user's browser/process actually execute?

- **Web:** The exact URL of the bundle/HTML file (e.g. `https://example.com/dist/bundle.js`)
- **Docker:** The exact image name + tag (e.g. `myapp:v1.2.4`)
- **Binary:** The exact path to the running binary (e.g. `/usr/local/bin/myapp`)
- **Serverless:** The deployment URL or function version

### 2. Read the served artifact directly

**NOT from local source. From the public URL or deployed location.**

```bash
# Web bundle — read the exact bytes the browser loads
curl -s https://raw.githubusercontent.com/user/repo/main/dist/bundle.js | grep "fix_pattern"

# Running binary — check what's actually in the file on disk
strings /usr/local/bin/myapp | grep "fix_pattern"

# Docker — inspect the running container's image
docker inspect --format '{{.Image}}' my_container

# HTTP endpoint — fetch from the user's perspective
curl -I https://example.com | grep -i etag
```

For browser-loaded assets, use `web_extract` or `curl` on the **raw public URL** — not the local file in the workspace.

### 3. Search for the fix pattern in the artifact

Look for the exact string, function name, or behavior that the fix introduces:

```bash
# Count occurrences of the fix marker
curl -s <artifact_url> | grep -c "Math.max(0, elapsed)"

# Verify timing values match what was changed
curl -s <artifact_url> | grep "perfect: 500\|great: 700"

# Check that the fix is present AND the old buggy code is absent
curl -s <artifact_url> | grep "elapsed / r.duration"  # should NOT appear unclamped
```

### 4. Only announce after confirming

- Fix pattern present in served artifact → announce as live, ask user to test
- Fix pattern absent → rebuild/redeploy, verify again

## The Anti-Pattern That Destroys Trust

```
Agent: "Fixed and pushed. Try again."
User:  *hard refreshes* Still broken.
Agent: "Fixed and pushed again. Hard refresh?"
User:  *hard refreshes* Still broken.
Agent: "Verified in source. Must be cache."
```

Each cycle wastes user trust and debugging time. The fix existed in someone's local source but never made it into the deployed artifact. **Verify in the served artifact FIRST.**

## Integration with Debugging Workflow

This skill extends `systematic-debugging` Phase {CLIENT} (Implementation):

| Systematic Debugging Phase | This Skill's Addition |
|---|---|
| Phase {CLIENT}: Root Cause | Same |
| Phase {CLIENT}: Pattern Analysis | Same |
| Phase {CLIENT}: Hypothesis | Same |
| Phase {CLIENT}: Implementation | Fix source → **Rebuild artifact** → **Read served artifact** → **Verify fix present** → Only THEN announce |
| Phase {CLIENT}: Verify | Same — but verify in the served artifact, not local source |

## Real-World Example (from session)

A web typing-game framework had a bug where correct keypresses registered as "miss." The fix was:
1. Widened timing windows in `src/types.ts` — `easy: { perfect: 500, great: 700, good: 1000 }`
2. Added a 3-second lead-in in `src/beatmap-generator.ts` — `LEAD_IN_MS = 3000`
3. Clamped ripple animation in `src/particle-system.ts` — `Math.max(0, now - r.startTime)`

The team announced "fixed and pushed" four times. The user reported it was still broken four times.

**Root cause:** The source was fixed but `dist/bundle.js` was never rebuilt. The served bundle still had the old `easy: { perfect: 150, great: 200, good: 300 }`, no lead-in, and unclamped ripple animation.

**Fix:** Run `npx esbuild src/index.ts --bundle --outfile=dist/bundle.js --format=esm`, then verify with `curl https://raw.githubusercontent.com/.../dist/bundle.js | grep "perfect: 500"`. Only then announce.

## Pitfalls

### 1. Verifying local source instead of served artifact

Reading `src/types.ts` on your local machine tells you what the source looks like. It tells you NOTHING about what the user's browser loads. Always verify at the public URL.

### 2. Assuming "pushed = deployed"

A git push is not a deployment. The CI/CD pipeline must run, the build must succeed, the new artifact must be uploaded, and the cache must be invalidated. Each step can silently fail. Verify the artifact, not the git log.

### 3. Browser cache masquerading as broken code

If the fix IS in the served bundle but the user's browser cached the old version, the user will still see the old behavior. Add cache-busting (`bundle.js?v=2`), or ask the user to hard-refresh. But FIRST verify the fix is in the served bundle — otherwise you're blaming cache for a missing fix.

### 4. Multiple agents announcing fixes independently

In multi-agent sessions, different agents may fix different bugs and announce them simultaneously. One agent's push can overwrite another's, or a rebuild can pick up stale source. After any push, re-verify the served artifact before announcing.

### 5. Build step exists but isn't in the deploy pipeline

Some projects build locally and commit `dist/` to git. Others build in CI. If the build step is manual, it's easy to forget. Check whether `dist/` is gitignored (build happens in CI) or committed (build happens locally). If committed, verify the committed bundle has the fix.

### 6. Rebuilt the wrong file (import path mismatch)

The served HTML's import statement names the file the browser loads. If `demo.html` imports `./dist/game.js` but you rebuilt `dist/bundle.js`, the fix never reaches the user even though a "bundle" was rebuilt. **Before rebuilding, read the import path in the served HTML, then rebuild and grep exactly that file.** After the file is renamed (e.g. `bundle.js` → `game.js`), every rebuild must target the new name.

### 7. Methods called in HTML but never implemented in bundle

HTML/CSS skeletons can reference JS methods that don't exist in the bundle (e.g., `feedbackLayer.getAccuracy()` called in overlay code but never defined on the class). The browser doesn't error until the method is invoked — often late in the game flow (e.g., on completion), freezing the UI. **Verify every method called from HTML exists in the bundle, not just that the bundle loads.**

### 8. Property name mismatches between HTML and bundle

`demo.html` called `feedbackLayer.judgmentCounts` but the class exposed `feedbackLayer.stats`. **Grep for property names in both HTML and source — ensure the call site matches the class API.**

### 9. Ghost notes / temp workarounds masking real bugs

A "temp fix" that modifies user-injected content (ghost note before first character) masks the real bug (per-difficulty lead-in mismatch). When reverted, user content starts where typed. **Rule:** revert temporary workarounds once the real fix lands — they create phantom behavior users report as bugs.

### 10. Character order is sacred (typing games)

Typing games have one invariant rhythm games don't: the user's content must appear in exactly the order typed. Difficulty scaling = timing windows only. **No shuffling, no note-doubling, no post-hoc reordering.** `injectDoubledNotes` (rhythm-game pattern) turned "is this my content" into nonsense. Wrong domain.

GitHub Pages and raw.githubusercontent.com cache aggressively (`cache-control: max-age=300` on raw; Pages deployment takes 1-3 minutes after push). A push is not immediately live:

- Verify at the commit SHA first — the source of truth: `curl https://raw.githubusercontent.com/<user>/<repo>/<sha>/dist/<file> | grep "fix_pattern"`. If the fix is at the SHA, it was committed; if it's missing there, it was never committed.
- Then re-verify at `main` and at the live Pages URL (`https://<user>.github.io/<repo>/...`) after waiting for deployment. The `main` CDN can serve stale bytes for minutes while the SHA URL is already correct.
- Permanent cache-buster: bump a query param on the import in the HTML (`./dist/game.js?v=6`) so browsers fetch fresh bytes on every change. Without it, every update needs a manual hard-refresh, and "it's just cache" becomes the default excuse that hides genuinely missing fixes.

## Verification Checklist for Bundled Web Apps

When fixing a bug in a bundled web app:

1. [ ] Read the import path in the served HTML (`grep "import.*dist" demo.html`)
2. [ ] Rebuild exactly that file (`npx esbuild ... --outfile=dist/<file>`)
3. [ ] Verify fix at commit SHA URL (`curl .../<sha>/dist/<file> | grep fix`)
4. [ ] Verify fix at `main` URL after propagation
5. [ ] Verify fix at live Pages URL (what user loads)
6. [ ] Check for property/method name mismatches between HTML and bundle
7. [ ] Check for temp workarounds that should be reverted
8. [ ] Bump cache-buster on import (`?v=N+1`)

## Quick Reference

| Artifact Type | How to Verify |
|---|---|
| Web bundle (JS/CSS) | `curl <raw_url> \| grep "fix_pattern"` |
| GitHub Pages bundle | Check the served HTML's import path first; `curl https://raw.githubusercontent.com/<user>/<repo>/<sha>/dist/<file>` (SHA = source of truth), then the live `https://<user>.github.io/<repo>/dist/<file>` after deploy |
| Compiled binary | `strings <path> \| grep "fix_pattern"` or `otool -l <binary>` |
| Docker image | `docker inspect <container> --format '{{.Image}}'` then `docker run --rm <image> <check_command>` |
| Serverless function | Invoke with a test payload and check response |
| Mobile OTA bundle | Fetch the bundle URL the device loads and inspect |
| CDN asset | `curl -H "Cache-Control: no-cache" <url> \| grep "fix_pattern"` |

## Session Reference

See `references/{CLIENT}` for a real-world case study of this skill in action.
See `references/{CLIENT}` for Phase {CLIENT} divergence points and domain-specific design patterns (typing games).
