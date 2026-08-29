<!-- GENERICIZED: 2×{CLIENT} | source: skills/creative/game-ux-architecture/references/{CLIENT} -->
# {CLIENT} Debugging Patterns

Concrete bugs and fixes from the {CLIENT} rhythm-typing framework session (August 2026).

## Bug 1: Timing Mismatch — Every Correct Key Registers as Miss

**Symptom:** All keys register as "MISS" even when pressed correctly. Console shows `pressed="d" expected="d"` — the key matches but judgment is still miss.

**Root Cause:** `BeatClockJudge.onChar()` computes `delta = evt.raw.timestamp - expected.time`. But `evt.raw.timestamp` is absolute `performance.now()` (billions of ms since page load) while `expected.time` is relative to song start (0, 750, 1500...). Delta is always ~2000ms+, so every correct key falls outside all timing windows.

**Fix:** Add `setStartTime(time)` to the judge. Compute `delta = (evt.raw.timestamp - startTime) - expected.time`. Call `judge.setStartTime(performance.now())` immediately before the game begins.

**Lesson:** When mixing absolute and relative timestamps, always normalize to a common reference point. The judge's `_startTime` must be set before any judging occurs.

## Bug 2: Character Order Mangled by Hand-Alternation Shuffle

**Symptom:** Typing "abcdef123456" produces "a1c2e3b4fd56" in the game. Characters appear in wrong order.

**Root Cause:** `applyHandAlternation()` in the beat-map generator swaps keys between positions to break same-hand triples. This destroys the text the player sees.

**Fix:** Remove the shuffle entirely. Character order is sacred in a typing game. Hand comfort should be a *generation-time* constraint (choose word lists that naturally alternate), not a post-hoc reorder.

**Lesson:** Never reorder content after generation. The player's text and the beat-map must match exactly.

## Bug 3: Wrong Keys Get Zero Feedback

**Symptom:** Pressing the wrong key produces no visual response — the keyboard stays static.

**Root Cause:** The judge silently ignores wrong keys (`if (evt.char !== expected.key) return;`). The feedback layer never receives a signal.

**Fix:** Add an `onWrongKey(key, expectedKey)` hook that fires when the pressed key doesn't match. The feedback layer renders a gentle red shake + tiny ripple — deliberately underwhelming, not punishing.

**Lesson:** Wrong input must always produce *some* feedback. Zero feedback = broken hardware in the player's mind.

## Bug 4: Stale Nudge Highlight Stuck on Key "7"

**Symptom:** A red circle appears around the "7" key and never disappears, even after the game ends and restarts.

**Root Cause:** `renderStale()` adds nudge highlights to a Map, but `endGame()` doesn't clear the Map. On restart, old entries persist with expired timers.

**Fix:** Clear `nudgeKeys` Map in both `reset()` AND `endGame()`. Also, `renderStale()` should be a no-op — nudges only appear on the current expected key, handled by the nudge update loop.

**Lesson:** Always clean up transient state on game end AND game restart. Don't rely on natural timeout cleanup for UI state.

## Bug 5: Combo Counter Blurry During Rapid Updates

**Symptom:** The combo counter text becomes blurry/ghosted when combo increments rapidly.

**Root Cause:** CSS `text-shadow` (for glow) + `transform: scale()` transition on rapidly-updating text creates motion blur. The browser can't composite the glow fast enough.

**Fix:** Remove `text-shadow` from the combo display. If glow is needed, use `will-change: transform` to promote to compositor layer, or use a static glow that doesn't re-render on every update.

**Lesson:** CSS glow + transform animation on frequently-updating text = motion blur. Keep text effects static during rapid updates.

## Bug 6: GitHub Pages Serves Stale Bundle — Users Permanently Stuck

**Symptom:** After pushing fixes, users still see the old broken version. Hard-refresh doesn't help. The intro screen can't be dismissed.

**Root Cause:** Browsers aggressively cache HTML files. GitHub Pages serves the old `demo.html` from before the onboarding fix. The `dist/bundle.js` was also in `.gitignore`, so it was never pushed at all.

**Fix (layered):**
1. Add `<meta http-equiv="cache-control" content="no-cache, no-store, must-revalidate">` to the HTML head
2. Version-query the bundle import: `import { ... } from './dist/bundle.js?v=3'`
3. Remove `dist/` from `.gitignore` so the bundle is tracked
4. Don't show the intro overlay on page load — let users click "How to Play" if needed, and let "Start Game" work immediately

**Lesson:** Browser caching is the #1 cause of "it works locally but not in production." Always add cache-busting to demo pages. Better yet: make the demo work without an intro overlay that can trap users.

## Bug 7: Demo Wiring Bugs Missed by Unit Tests

**Symptom:** 29/29 unit tests pass, but the demo is completely broken. `judge.setStartTime()` is never called, `nudgeKeys` is never cleared, the onboarding button doesn't reach the game loop.

**Root Cause:** Unit tests verify components in isolation. The integration wiring in `demo.html` is a separate artifact that tests don't cover.

**Fix:** After fixing framework bugs, always verify the demo end-to-end. Open the browser console, click the button, and confirm the game starts. Don't trust unit test counts as proof that the integration works.

**Lesson:** Unit tests prove components work. Design review + manual integration testing proves they work together. Both are necessary.

## Bug 8: Stale Bundle After Rebuild

**Symptom:** Source code has `setStartTime`/`getSongTime`, but the served `bundle.js` doesn't contain them.

**Root Cause:** The developer forgot to run `npx esbuild` after editing TypeScript source. The committed `dist/bundle.js` is from before the changes.

**Fix:** Always rebuild the bundle before committing: `npx esbuild src/index.ts --bundle --outfile=dist/bundle.js --format=esm`. Consider adding a pre-commit hook or CI step that verifies the bundle is in sync with source.

**Lesson:** The bundle is a build artifact, but it's also the production artifact. GitHub Pages serves the committed file, not the TypeScript source. Rebuild → commit → push, in that order.
