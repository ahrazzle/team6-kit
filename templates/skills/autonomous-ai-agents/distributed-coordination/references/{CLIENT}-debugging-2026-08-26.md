<!-- GENERICIZED: 2×{CLIENT} | source: skills/autonomous-ai-agents/distributed-coordination/references/{CLIENT} -->
# {CLIENT} Debugging Session — {CLIENT}

## Summary
Multi-session debugging of a rhythm-typing game framework deployed to GitHub Pages. The core pipeline (keydown → RawBus → NormalizedBus → BeatClockJudge → FeedbackLayer) worked correctly in unit tests and integration tests, but users kept reporting bugs that "should have been fixed."

## Root Causes Found

### 1. Browser Caching of Static Assets
GitHub Pages serves with `cache-control: max-age=600`. Users kept seeing stale `bundle.js` despite fixes being pushed. Query-string cache-busting (`bundle.js?v=3`, `bundle.js?v=4`) was insufficient — some browsers/CDNs ignore query strings.

**Fix:** Renamed `bundle.js` to `game.js` — a filename the browser has never seen, forcing a fresh fetch.

### 2. Orphaned Judge Events Between Games
Each Start Game created a new `BeatClockJudge`, but the old judge's hooks still referenced the same `debugPlugin` instance. When a key was pressed, both old and new judges fired — the old one logging MISS because its game had ended.

**Fix:** 
- Create a fresh `debugPlugin` per game
- Guard hooks with `if (judge !== newJudge) return;` using proper closure capture

### 3. Duplicate `setStartTime()` Calls
Two calls to `judge.setStartTime()` — one before bus start, one after. The tick loop used the first `startTime`, the judge used the second. They diverged by ~300ms, causing the tick loop to mark notes as STALE before they were due.

**Fix:** Removed the duplicate call.

### 4. Debug UI Visible in Production
The `DebugPlugin` created visible DOM elements (combo circle, progress bar, judgment log) that overlapped and created a "blur of symbols" effect. The `showDebugUI` flag controlled UI creation but the `log()` method still wrote to console and updated DOM.

**Fix:** Added `if (!this.showDebugUI) return;` guards to ALL methods including `log()`, `onHit()`, `onMiss()`, etc.

### 5. Negative Canvas Radius
The second perfect-hit ripple was created with `startTime: performance.now() + 80` (80ms in the future). On the next frame, `elapsed` was negative, causing `easeOutQuad` to return a negative value, making `radius` negative → `IndexSizeError`.

**Fix:** `const elapsed = Math.max(0, now - r.startTime);`

## Key Lesson
**Never announce a fix without verifying the served file.** Use `curl -s https://raw.githubusercontent.com/<repo>/main/<file> | grep -c "<fix-signature>"`. If the signature isn't in the served file, the fix doesn't exist for the user.

## Integration Test Pattern
```typescript
// The single most valuable test: drive the full pipeline
const rawBus = new RawBus();
const normBus = new NormalizedBus(rawBus);
normBus.onChar((evt) => judge.onChar(evt));
normBus.start();
rawBus.start();
judge.setStartTime(performance.now());

// Press at exact note time
await waitAndPress('h', 'KeyH', notes[0].time);
assert(judgments[0].judgment === 'perfect');
```

This test caught zero regressions across multiple fix cycles — it was the only reliable signal that the core pipeline worked.
