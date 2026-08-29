<!-- GENERICIZED: 5×{CLIENT}, 1×{RELATIONSHIP} | source: skills/software-development/rhythm-typing-game-framework/references/{CLIENT} -->
# {CLIENT} Debug Session — Incident Record

Project: {CLIENT} (typing-rhythm game framework for kids). Workspace `~/{CLIENT}{CLIENT}`, GitHub `{RELATIONSHIP}/{CLIENT}`, served via GitHub Pages. TypeScript, esbuild bundle to `dist/bundle.js` (later renamed `dist/game.js`), 94-98 unit tests across RawBus/NormalizedBus/BeatClockJudge + BeatMapGenerator.

Each bug below cost at least one session. The pattern: fix announced as "live," user tested, still broken, because either (a) the bundle was never rebuilt from src, or (b) the Pages CDN lagged, or (c) the fix addressed a symptom not the root cause. See `deploy-artifact-verification` for the served-artifact discipline.

## Bug-by-bug record

### Timing: every correct key = MISS
- Root cause: `delta = evt.raw.timestamp - expected.time` where `evt.raw.timestamp` is absolute `performance.now()` (billions of ms) and `expected.time` is relative (0, 1500, 3000...). Delta always huge → outside all windows.
- Fix: `setStartTime(startTime)` captured at game start and set BEFORE `rawBus.start()`; delta = `(evt.raw.timestamp - startTime) - expected.time`. Then add `getSongTime() = performance.now() - startTime`.
- Double bug: even after the method existed, `demo.html` didn't call `setStartTime` at all (defaulted to 0), so the same symptom returned. Order matters: set start time before wiring the bus.

### Hard-difficulty duplicate letters
- Root cause: `injectDoubledNotes` mutated the array with `notes.splice(i + inserted + 1, 0, doubled)` while iterating `i++`, so inserted notes got re-processed → exponential duplication ("is this my content" → "iiss tthiiss ...").
- Fix: capture `const originalLength = notes.length`, iterate `for (i < originalLength)`, push doubled notes to the end, then `notes.sort((a,b) => a.time - b.time)`. (Later removed entirely — hard just gets tighter windows, same content order.)

### Medium-difficulty spaces disappear
- Root cause: `shouldSkip(key, difficulty)` had `case "medium": return key === " ";` — dropped spaces on medium only.
- Fix: return `false` for all difficulties. Spaces are part of the user's content; never drop them.

### Approach ring missing for first key / for pasted uppercase text
- Root cause A (case): beat-map preserved case; keyboard stores lowercase ids. Pasting "Hello..." made a note for `H`; `getKeyElement('H')` → undefined → no ring. Also the judge's strict `evt.char !== expected.key` then punished capitals/caps-lock as guaranteed misses.
- Fix: lowercase both sides of the judge comparison + lowercase key lookups; map `" " → "space"`.
- Root cause B (timing): first note at `time = LEAD_IN_MS`; ring spawn guard `if (timeUntilHit > preemptTime) continue` skipped it at t=0 when LEAD_IN > preempt. A tempting temp fix (inject a "ghost" char before content) visibly broke the user's text. Correct fix: set `LEAD_IN_MS` per difficulty equal to its preempt time (easy 1500, medium 1000, hard 600, expert 350).

### Ripple negative-radius canvas crash (`IndexSizeError`)
- Root cause: perfect-hit spawned a second ripple with `startTime: performance.now() + 80` (future). First frame `elapsed` negative → negative `progress` → negative radius → `ctx.arc` throws in the rAF loop → uncaught error every frame.
- Fix: clamp `const progress = Math.max(0, Math.min(1, elapsed / duration))`; cleanup expired effects before rendering.

### Approach rings drift from "Type This" feed
- Root cause: rings shrank toward `note.time` while the feed advanced the instant a key was judged. On an early hit the character advanced before the ring finished shrinking → looked out of sync (not actually two clocks; both used `getSongTime()`).
- Fix: collapse the ring on judgment (`markJudged`), not on `note.time`, so it shrinks the same frame the feed advances.

### Orphaned judge events / "two keyboards" after second game
- Root cause: each Start created a new judge/bus/SVG but old ones stayed attached; old `keydown` listeners fired into orphaned judges → ghost MISS logs + stacked keyboards + stuck highlights.
- Fix: teardown before recreate — `rawBus.stop()` → `judge.detach()` → null refs → `gameActive=false`; destroy/remove old DOM (not just reset styles); `if (gameActive) return;` double-start guard; fresh debugPlugin per game.

### Results overlay freeze on completion
- Root cause: `demo.html` called `feedbackLayer.getAccuracy()/.getRanking()/.playCelebration()` and read `feedbackLayer.judgmentCounts`, but served `game.js` didn't define those methods / used `stats` not `judgmentCounts`. Last note → `endGame()` → `TypeError: getAccuracy is not a function` → freeze. Cross-file reference mismatch (see deploy-artifact-verification).
- Fix: implement + export the methods; align property names (`stats`).

### Final-polish items the user flagged
- Debug overlay (cyan event log) showing over the game — it was a dev tool; gate behind `showDebugUI=false` (keep it off in a kids' product).
- "Type This" feed must color each completed key by judgment (perfect=cyan, great=green, good=yellow, miss=red), matching the stats display.
- Results screen: "Round Complete" not "Song Complete"; offer both "Play Again" and "Change Setup"; strip "Framework Validation" from the title and remove the now-false "wrong keys are silently ignored" copy.
- Stats must persist after song end (reset in `startGame()`, not `endGame()`).
- BPM slider must update its displayed number on `input`.

## End state
Framework MVP defensible: rhythm mechanic (Perfect/Great/Good), approach rings synced to judgment, per-key judgment colors, results overlay with accuracy % + S/A/B/C/D/F rank + celebration, per-difficulty lead-in + timing windows, case-insensitive input, spaces preserved, no duplicate letters.
