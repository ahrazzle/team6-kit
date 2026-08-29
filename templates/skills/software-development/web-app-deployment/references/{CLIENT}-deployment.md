<!-- GENERICIZED: 10×{CLIENT}, 7×{RELATIONSHIP} | source: skills/software-development/web-app-deployment/references/{CLIENT} -->
# {CLIENT} — Deployment Reference

**Repo:** `{RELATIONSHIP}/{CLIENT}`
**Live URL:** `https://{RELATIONSHIP}.github.io/{CLIENT}`
**Workspace:** `/Users/{RELATIONSHIP}/{CLIENT}{CLIENT}`

## Build & Deploy

```bash
cd "/Users/{RELATIONSHIP}/{CLIENT}{CLIENT}"
npx esbuild src/index.ts --bundle --outfile=dist/game.js --format=esm
git add -A && git commit -m "..." && git push
```

## Verify Before Announcing

```bash
# Check served bundle contains the fix
curl -s "https://raw.githubusercontent.com/{RELATIONSHIP}/{CLIENT}" | grep -c '<fix_identifier>'

# Check deployed URL
curl -s "https://{RELATIONSHIP}.github.io/{CLIENT}" | grep -c '<fix_identifier>'

# Check last-modified
curl -sI "https://{RELATIONSHIP}.github.io/{CLIENT}" | grep -i last-modified
```

## Key Files

| File | Purpose |
|---|---|
| `src/index.ts` | Entry point — exports all public classes |
| `src/feedback-layer.ts` | Visual feel layer (keyboard, particles, approach rings) |
| `src/BeatClockJudge.ts` | Timing judgment engine |
| `src/beatmap-generator.ts` | Converts text content into rhythmic note arrays |
| `demo.html` | Main game page — loads `./dist/game.js` |
| `dist/game.js` | Bundled output (committed to repo for GH Pages) |

## Common Bugs & Fixes

| Bug | Root Cause | Fix |
|---|---|---|
| Correct keys register as MISS | `setStartTime()` called after `rawBus.start()` | Call `setStartTime()` BEFORE starting bus |
| First-key approach ring invisible | `LEAD_IN_MS` > `preemptTime` | Set `LEAD_IN_MS` = preempt time per difficulty |
| Duplicate letters on hard | `injectDoubledNotes` re-processes inserted notes | Capture `originalLength` before iterating |
| Spaces disappear on medium | `shouldSkip` drops spaces on medium | Spaces are content — never skip |
| Red circle stuck on "7" | `stop()` doesn't clear nudge highlights | Call `keyboard.reset()` + `nudgeKeys.clear()` in `stop()` |
| Game freezes on completion | `demo.html` calls methods not in bundle | Verify methods exist in served bundle |
| Two keyboards overlaid | Orphaned event listeners from previous game | Null out old judge/bus references in `endGame()` |
