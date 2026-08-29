<!-- GENERICIZED: 4×{CLIENT} | source: skills/software-development/integration-testing/references/{CLIENT} -->
# {CLIENT} Integration Patterns

Concrete examples from the {CLIENT} rhythm-typing framework session ({CLIENT} to {CLIENT}).

## Session Summary

- **Unit tests:** 46/46 passing (event bus, beat-map generator)
- **Integration bugs found in production:** 7+
- **Root cause:** Components tested in isolation; wiring between them was never tested
- **Impact:** Each bug required a separate push to fix; user frustration was high

## The Bugs That Unit Tests Missed

### 1. Timing Mismatch (Absolute vs. Relative Time)

**Symptom:** Every correct keypress registered as MISS despite correct key.

**Root cause:** `BeatClockJudge.onChar()` computed `delta = evt.raw.timestamp - expected.time` where `evt.raw.timestamp` was absolute `performance.now()` (billions of ms since page load) and `expected.time` was relative to song start (0, 1000, 2000...). Delta was always ~2000ms+, so every correct key fell outside timing windows.

**Fix:** Added `setStartTime(startTime)` called BEFORE the bus starts listening. Now `delta = (evt.raw.timestamp - startTime) - expected.time`.

**Why unit tests missed it:** The unit test called `judge.onChar()` directly with a pre-stamped `RawKeyEvent`. It never tested the full flow from `keydown` → bus → judge.

### 2. DOM Accumulation (Debug Plugin)

**Symptom:** Double readout overlaid on left side; text became a blur of symbols.

**Root cause:** A new `DebugPlugin` was created each game but the old one was never destroyed. Multiple containers stacked up in the same absolute position.

**Fix:** Added `debugPlugin.destroy()` before creating a new one. `destroy()` removes the container DOM element.

**Why unit tests missed it:** Unit tests tested a single game session. No test ran the lifecycle start → play → end → restart.

### 3. Orphaned Event Listeners

**Symptom:** After Game Over, `MISS pressed="t" expected="t"` continued firing on keypresses.

**Root cause:** The old judge and bus were stopped but their hooks still referenced the old debugPlugin. When the old judge processed a queued event, it logged to the old plugin.

**Fix:** Null out `judge = null` in `endGame()` before setting `gameActive = false`. Guard keydown handler: `if (!judge) return;`.

### 4. Stale Nudge Highlight on "7"

**Symptom:** Permanent red circle around the 7 key that never cleared.

**Symptom:** `nudgeKeys` Map was cleared in `reset()` but the SVG elements created by `setNudgeGlow()` persisted because the 8-second cleanup timer expired during the previous game state.

**Fix:** Call `this.keyboard.reset()` in `stop()` which clears all visual state from every key.

### 5. Ripple Negative Radius Crash

**Symptom:** `IndexSizeError: The radius provided (-59.7718) is negative` flooding the console.

**Root cause:** The second perfect-hit ripple got `startTime: performance.now() + 80` — 80ms in the future. On the next frame, `elapsed = now - (now + 80) = -80`. Then `progress = -80/700 = -0.114`, radius became negative.

**Fix:** Clamp elapsed to non-negative: `const elapsed = Math.max(0, now - r.startTime)`.

### 6. Bundle vs. Source Mismatch

**Symptom:** Source code had `setStartTime()`/`getSongTime()` but deployed version was broken.

**Root cause:** `dist/` folder was in `.gitignore`, so `bundle.js` never got pushed. The served bundle was from before the timing fixes.

**Fix:** Removed `dist/` from `.gitignore` and verified served bundle contains expected exports via `curl | grep`.

### 7. Teardown Sequence Bug

**Symptom:** Correct keys registered as MISS on second game (without refresh).

**Root cause:** `endGame()` set `gameActive = false` but didn't stop the bus or null the judge until the *next* `startGame()`. That window allowed orphaned events to leak through.

**Fix:** Reordered teardown: stop bus → null judge → set `gameActive = false`.

## The Integration Test That Would Have Caught All of These

```javascript
test('full pipeline: keypress → judgment → visual feedback', async () => {
  // Setup
  const { rawBus, normBus, judge, feedbackLayer } = createGame();
  
  // Start game
  judge.setStartTime(performance.now());
  rawBus.start();
  
  // Simulate a correctly-timed keypress
  rawBus.inject('f', 'KeyF', 'keydown', performance.now() + 1000);
  
  // Assert
  expect(judge.state.cursor).toBe(1);
  expect(debugPlugin.judgmentCounts.perfect).toBe(1);
});

test('lifecycle: start → play → end → restart has no orphans', async () => {
  // Game 1
  await startGame();
  await pressKey('a');
  expect(getKeyboardCount()).toBe(1);
  
  await endGame();
  
  // Game 2
  await startGame();
  expect(getKeyboardCount()).toBe(1); // Not 2 — no accumulation
  expect(getEventListeners()).toHaveLength(1);
  
  await pressKey('b');
  expect(getCombo()).toBe(1); // Not 2 — new game
});

test('served bundle matches source', async () => {
  const bundle = await fetch('https://example.com/bundle.js');
  expect(bundle).toContain('setStartTime');
  expect(bundle).toContain('getSongTime');
});
```

## Lessons Learned

1. **Unit tests prove components work. Integration tests prove they work together.**
2. **Timing bugs are invisible to unit tests** — you must test the full flow from input to judgment.
3. **DOM accumulation is invisible to single-session tests** — you must test the lifecycle start → end → restart.
4. **Deployment verification is mandatory** — fetch the served bundle and verify it contains expected code.
5. **Teardown order matters** — stop bus → null references → destroy DOM → set inactive.
6. **Clamp animation values** — elapsed time, radius, opacity should never go negative.
7. **Cache-busting prevents stale bundles** — always add `?v=N` to bundle imports and increment on each push.
