<!-- GENERICIZED: 2×{CLIENT} | source: skills/software-development/event-driven-web-ui-lifecycle/references/{CLIENT} -->
# {CLIENT} Lifecycle Bugs — Concrete Case

A rhythm-typing game framework ({CLIENT}) deployed on GitHub Pages. Event pipeline: `RawBus → NormalizedBus → BeatClockJudge → FeedbackLayer + DebugPlugin`. SVG keyboard + 2 canvas overlays. The user played the same page repeatedly, and every bug below only surfaced on the SECOND game — the classic not-torn-down signature.

## Bug 1: DOM accumulation → "two keyboards" / "double readout"

**Symptom:** Second game showed overlapping readouts on the left ("blur of symbols"), a ghost circle, stacked debug UI. Screenshot showed duplicated text stacking.

**Root cause:** `createUI()` (DebugPlugin) and `createExpectedKeyIndicator()` (FeedbackLayer) appended fresh DOM every game; old elements were never removed. Each Start Game added another copy.

**Fix:** remove-before-create at every creation site:
```javascript
// setJudge
if (this.expectedKeyIndicator) { this.expectedKeyIndicator.remove(); this.expectedKeyIndicator = null; }
this.createExpectedKeyIndicator();

// createUI / setFeedbackLayer
if (this.container) { this.container.remove(); this.container = null; }
```

**Verify:** `document.querySelectorAll('[data-role="counts"]').length` should be 1 after N games.

## Bug 2: Orphaned judge events between games

**Symptom:** After `Game Over`, the console showed `MISS pressed="t" expected="t"` for keys the NEW game was expecting — events from the old judge leaking in. The user pressed keys between games and the dead judge answered.

**Root cause:** `endGame()` stopped the raw bus but never detached the judge from the normalized bus (`judge.detach()` missing), and `gameActive` was flipped before full teardown. Old judge's `onChar` handler stayed subscribed.

**Fix:** teardown order — stop bus → `judge.detach()` → null refs → THEN `gameActive = false`. Plus guards: `if (judge !== newJudge) return;` in every hook, and `if (this._cursor >= this.beatMap.length) return;` at the top of `onChar`.

## Bug 3: Spacebar got no approach ring

**Symptom:** Every letter key showed an approach ring; the spacebar never did, despite spaces being in the beat-map.

**Root cause:** Beat-map emitted `key: " "` (literal space). Keyboard layout's key id is `"space"`. `getKeyElement(" ")` returned null → ring skipped.

**Fix:** normalize at the visual lookup boundary:
```javascript
const lookupKey = keyId === ' ' ? 'space' : keyId;
```
Applied in `getKeyPosition()` and the expected-key indicator. Data layer untouched.

## Bug 4: Inline TypeScript in demo.html → dead buttons

**Symptom:** On GitHub Pages, the page loaded but no button did anything. No console error at all.

**Root cause:** The inline `<script type="module">` contained `const preemptTimes: Record<string, number> = {...}`. Browsers can't parse TypeScript type annotations; the whole module failed at parse time, so zero listeners attached, silently.

**Fix:** stripped the annotation: `const preemptTimes = {...}`. Lesson: inline scripts in shipped HTML must be plain JS.

## Bug 5: Stuck red circle on "7"

**Symptom:** A permanent red/nudge circle on the "7" key that survived game restarts.

**Root cause:** Nudge highlights were cleared only in `reset()` (called at the START of the next game) but not in `stop()` (called at the END of the current game). A nudge applied in the final frames survived into the next session, and the cleanup timer expired while inactive.

**Fix:** `stop()` now also calls `this.keyboard.reset()` (clears every key's highlights/nudges/pulses/shakes) plus `this.nudgeKeys.clear()`.

## Meta-lesson

Unit tests (29/29, 34/34, 48/48) passed throughout while every integration bug above shipped. Unit tests cannot catch DOM lifecycle, listener subscription, or teardown-ordering defects. The single highest-value check for this class of app: run one full session end-to-end and assert (a) exactly one UI instance, (b) zero events after teardown, (c) correct input registers correct judgment.
