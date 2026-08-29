<!-- GENERICIZED: 2×{CLIENT} | source: skills/software-development/drift-monitoring/references/{CLIENT} -->
# {CLIENT} Bundle Drift — Worked Example ({CLIENT})

Repeated session where fixes were announced as "live" and "verified" but the served bundle did not contain them. User wasted cycles testing non-existent fixes.

## The Pattern

1. Team member fixes source locally
2. Announces "committed and pushed" + "verified in served bundle"
3. User hard-refreshes, bug persists
4. No one checks the actual served artifact
5. Repeat

## Root Causes (multiple, compounding)

### A. Stale Bundle
Source has fixes, but `dist/bundle.js` was never rebuilt from new source. Local source and served bundle are decoupled.

**Fix:** Rebuild bundle AFTER every source change. `npx esbuild src/index.ts --bundle --outfile=dist/game.js --format=esm`

### B. GitHub Pages CDN Caching
Raw GitHub URL has `cache-control: max-age=300` (5 min). Pages deployment takes 1-3 min after push. Users get stale files during this window.

**Fix:** Add version query param to the import URL (`./dist/game.js?v=6`). Bump on every release. Browser treats new param as a different URL, bypasses cache.

### C. Announcement Without Verification
Team members verified by reading local source, not the served artifact. "Confirmed in served bundle" was based on local file inspection.

**Fix:** Verify in the actual served URL: `curl https://raw.githubusercontent.com/<repo>/main/dist/bundle.js | grep <fix-string>` or `curl https://<pages-url>/dist/bundle.js | grep <fix-string>`.

## The Rule (already in skill as Principle 6)

Announcement drift — prose claims decoupled from machine reality. The fix exists in local source or in the announcement, but not in what the browser actually loads.

**A fix is not "verified" until `curl <served-url> | grep <fix-string>` returns a match.**

## Session-Specific Compounds

| Issue | Local Source | Served Bundle | User Impact |
|---|---|---|---|
| Timing windows ±500ms | ✅ types.ts line 139 | ❌ Still ±150ms | Every press = MISS |
| LEAD_IN_MS per-difficulty | ✅ beatmap-generator.ts line 37 | ❌ Still 3000 constant | No first-key ring |
| getAccuracy/getRanking | ✅ feedback-layer.ts lines 606-637 | ❌ Not present | Freeze on completion |
| Spacebar lookupKey | ✅ approach-ring-system.ts line 115 | ❌ Not present | No ring on spacebar |

## Prevention Checklist

For every "fix deployed" announcement:

- [ ] Source change committed AND pushed
- [ ] Bundle rebuilt from current source (`npx esbuild ...`)
- [ ] Bundle committed AND pushed (if dist is tracked)
- [ ] Verified in served artifact via `curl` or `grep` on raw GitHub URL
- [ ] Cache-buster query param bumped (if applicable)
- [ ] User instructed to hard refresh AFTER verification

## Why This Matters

The user was told "hard refresh, it's fixed" **five times** in one session. Each time the served bundle didn't contain the fix. Trust erodes. The systematic-debugging skill's "tight feedback loop" principle applies: the red/green signal is the served file content, not the announcement.
