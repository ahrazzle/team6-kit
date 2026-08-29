<!-- GENERICIZED: 2×{CLIENT} | source: skills/software-development/static-webapp-verification/references/{CLIENT} -->
# {CLIENT} Framework Bug Log ({CLIENT})

## Critical Bugs Fixed

### 1. Timing Mismatch — `setStartTime()` never called
- **Symptom:** Every correct keypress judged as MISS
- **Root cause:** `delta = evt.raw.timestamp - expected.time` mixed absolute `performance.now()` with relative note times
- **Fix:** Added `setStartTime(time)` + `getSongTime()` methods; delta is now `(timestamp - startTime) - expected.time`
- **Lesson:** In rhythm games, always anchor input timestamps to a song start reference

### 2. Character Order Destroyed by Shuffle
- **Symptom:** "abcdef123456" → "a1c2e3b4fd56"
- **Root cause:** `applyHandAlternation()` swapped keys between positions to break same-hand triples
- **Fix:** Removed the shuffle entirely — character order is sacred in typing games
- **Lesson:** Never post-process content order for "ergonomic" reasons without user consent

### 3. Wrong Keys = Zero Feedback
- **Symptom:** Wrong keypresses produced no visual feedback
- **Root cause:** Judge silently returned on wrong keys (`if (key !== expected) return;`)
- **Fix:** Added `onWrongKey(key, expectedKey)` hook → triggers `renderMiss()` with red shake

### 4. Ripple Negative Radius Crash
- **Symptom:** `IndexSizeError: radius provided (-59.2154)` flooding console
- **Root cause:** Second perfect-hit ripple had `startTime: now + 80`; on next frame `elapsed = -80`, `easeOutQuad(-0.114) = -0.241`, `radius = 180 × -0.241`
- **Fix:** `const elapsed = Math.max(0, now - r.startTime);` clamps to non-negative

### 5. Dual Feed / Double-Start
- **Symptom:** Two copies of every log message
- **Root cause:** Clicking button + Space simultaneously created two judges, two buses
- **Fix:** `if (gameActive) return;` guard at top of `startGame()`

### 6. Stale Nudge Stuck on Key ("7")
- **Symptom:** Permanent red circle on a key across games
- **Root cause:** `nudgeKeys` cleared in `reset()` but nudge loop only ran while `gameActive`; nudges added in final frame never cleaned up
- **Fix:** `stop()` now calls `clearNudgeGlow()` for each key before clearing Map

### 7. Browser Cache Serving Stale Bundle
- **Symptom:** App works on localhost but breaks on GitHub Pages
- **Root cause:** Browser cached old `bundle.js` despite new deploy
- **Fix:** Added `<meta http-equiv="cache-control" content="no-cache, no-store, must-revalidate">` and `?v=3` query parameter on bundle import

### 8. TypeScript Annotations in Browser Script
- **Symptom:** All buttons dead, no console output
- **Root cause:** `const preemptTimes: Record<string, number> = {...}` — browsers don't support TS syntax
- **Fix:** Stripped all type annotations from inline `<script>` block

### 9. Timing Windows Too Tight for Beginners
- **Symptom:** Correct presses 200-400ms late still judged MISS
- **Root cause:** Windows were ±25-150ms (osu! values) — impossible for 7-year-olds
- **Fix:** Widened to ±500ms (easy), ±300ms (medium), ±150ms (hard), ±80ms (expert) + 3s lead-in

### 10. Approach Rings Not Showing
- **Symptom:** No rings visible during gameplay
- **Root cause:** No lead-in time; first note at t=0 meant rings appeared and disappeared instantly
- **Fix:** Added `LEAD_IN_MS = 3000` so first note is at t=3000, giving rings time to shrink
