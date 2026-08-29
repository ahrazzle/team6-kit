<!-- GENERICIZED: 4×{CLIENT}, 1×{RELATIONSHIP} | source: skills/software-development/event-driven-web-ui-lifecycle/SKILL.md -->
---
name: event-driven-web-ui-lifecycle
description: "Use when debugging event-driven web UIs."
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [web, debugging, dom, lifecycle, event-bus, canvas, games]
    related_skills: [systematic-debugging, verify-deployed-artifacts, dogfood]
---

# Event-Driven Web UI Lifecycle Debugging

## When to Use

Use when debugging interactive web UIs built around event buses / canvases / repeated sessions — typing games, rhythm games, canvas dashboards, editors, anything where a "session" or "game" starts and stops repeatedly in the same page:

- Keyboards / controllers that render per-session and get re-created on restart
- Event-bus pipelines (`RawBus → NormalizedBus → Judge → Hooks`)
- Canvas + DOM hybrid rendering (SVG keyboard + canvas overlay)
- Recurring symptoms: "ghost" UI, overlapping readouts, events firing after the session ended, visual highlights stuck between sessions

**Use this ESPECIALLY when:** the bug only appears on the SECOND run — the first game works, the second overlays or double-fires. That signature means state from session 1 was never torn down.

## Bug Class 1: DOM Accumulation (remove-before-create)

**Symptom:** Overlapping UI, "double readout", "two keyboards", text that blurs because multiple copies stack. Usually only visible after the second session.

**Cause:** Code creates DOM elements per session (`createUI()`, `createExpectedKeyIndicator()`) but never removes the previous instance before creating a new one. Five games = five stacked circles/bars/logs.

**Fix pattern — remove BEFORE create, at every creation site:**

```javascript
// WRONG — stacks a new element every session
setJudge(judge) {
  this.createExpectedKeyIndicator();  // appends a NEW div every call
}

// RIGHT — remove the old one first
setJudge(judge) {
  if (this.expectedKeyIndicator) {
    this.expectedKeyIndicator.remove();
    this.expectedKeyIndicator = null;
  }
  this.createExpectedKeyIndicator();
}
```

Apply the same guard in every `createUI` / `create*` method and in any setter that re-creates UI (`setFeedbackLayer`, `setJudge`). If a container is re-used, remove it before appending a fresh one.

**Check:** after N sessions, `document.querySelectorAll('[data-role="counts"]').length` should be 1, not N.

## Bug Class 2: Orphaned Event Listeners / Teardown Order

**Symptom:** Events from the PREVIOUS session fire after the current one started (`MISS pressed="i" expected="i"` between two games). The old judge/bus still processes keystrokes.

**Cause:** Session teardown stops the bus but never detaches the judge from it, or sets `gameActive = false` BEFORE stopping the bus — leaving a window where keypresses reach the old judge.

**Fix — teardown order matters:**

```javascript
function endGame() {
  // 1. Stop the raw bus FIRST — no new events enter the pipeline
  rawBus.stop();
  normBus.stop();
  clearInterval(tickHandle);
  // 2. Detach the judge from the bus
  judge.detach();
  // 3. Null references so queued events find nothing
  judge = null;
  normBus = null;
  rawBus = null;
  // 4. THEN flip the state flag
  gameActive = false;
}
```

**Defense in depth — guards inside hooks:**
- Capture the judge instance and bail if it's no longer current: `if (judge !== newJudge) return;`
- Early-return in the judge's event handler when the song is complete: `if (this._cursor >= this.beatMap.length) return;`
- `if (!gameActive) return;` at the top of every plugin hook.

## Bug Class 3: Data-Key vs Layout-Key Mismatch

**Symptom:** A specific key never renders feedback/rings (e.g. spacebar gets no approach ring while every letter key works).

**Cause:** The data layer emits one identifier and the visual layer looks up another: beat-map emits `" "` (literal space) but the keyboard layout's key id is `"space"`. `getKeyElement(" ")` finds nothing.

**Fix:** Normalize at the VISUAL lookup boundary, never by mutating data:

```javascript
const lookupKey = keyId === ' ' ? 'space' : keyId;
const keyEl = keyboard.getKeyElement(lookupKey);
```

Apply in every place a note key becomes a visual lookup: approach-ring position, hit feedback, expected-key indicator. Centralize the mapping if there are 3+ call sites.

## Bug Class 4: Inline TypeScript in a Shipped HTML Script Block

**Symptom:** Page loads, but EVERY button is dead. No console error at all. The script block never starts executing.

**Cause:** A `<script type="module">` block in the shipped HTML contains TypeScript type annotations — `const preemptTimes: Record<string, number> = {...}`. Browsers don't parse TypeScript; the module fails at parse time, so no listeners ever attach and no error is visible (the failure is silent).

**Fix:** Any inline `<script>` in shipped HTML must be plain JavaScript. Strip every `: Type` annotation before shipping. Keep TypeScript only in files that go through a compiler/bundler.

**Check:** `curl -s <served-demo.html> | grep -n ": Record<\|: string\|: number"` inside the script block — should return nothing.

## Bug Class 5: Visual State Cleared on Stop, Not Only on Reset

**Symptom:** A highlight (red circle on a key, glow) stays visible forever after a session ends, even after the next session starts.

**Cause:** Cleanup runs in `reset()` (called at the START of the next session) but not in `stop()` (called when the session ends). If a highlight is applied in the same frame the session ends, it survives the gap and persists.

**Fix:** Clear ALL visual state in `stop()` too — not just the tracking Map:

```javascript
stop() {
  this.gameActive = false;
  this.particles.stop();
  this.approachRings.stop();
  this.keyboard.reset();   // clears highlights, nudges, pulses, shakes
  this.nudgeKeys.clear();
}
```

## Bug Class 6: Animation Progress Model vs Judgment Model Desync

**Symptom:** The visual anticipation layer (approach rings, countdown) "gets ahead of the timing" — rings are still shrinking while the character/note feed has already advanced. The two views disagree about where the player is, and it reads as broken sync.

**Cause:** TWO DIFFERENT PROGRESS MODELS on the SAME clock. The feed advances the instant a note is judged (which can be EARLY — delta −300ms); the ring keeps shrinking until `note.time` reaches full shrink. Both use the same time source (`judge.getSongTime()`); they just report at different moments. This is NOT a clock drift bug — don't waste time hunting for a second timer.

**Fix — collapse the ring on the judgment frame, not on note.time:**

```javascript
onHit: (event) => {
  feedbackLayer.markNoteJudged(event.note, event.judgment); // collapse NOW
  feedbackLayer.renderHit(event.judgment, event.key, event.delta);
},
onMiss: (key, expectedKey, delta, note) => {
  if (note) feedbackLayer.markNoteJudged(note, 'miss'); // collapse NOW
},
onNoteStale: (note) => {
  feedbackLayer.markNoteJudged(note, 'miss');
},
```

Critical details:
- The judge advances its cursor BEFORE `onHit` fires, so `judge.getCurrentNote()` returns the NEXT note. Never derive the judged note from the cursor — use the `note` carried on the judgment event.
- The `onMiss` hook must pass the note through as a 4th argument (`onMiss?(key, expectedKey, delta, note?)`) or the ring can't collapse on miss — the miss path is the one most often left unwired, so the ring keeps shrinking past the feed.
- Check the hook signature in the types file when adding a parameter — the LSP error `Expected 3 arguments, but got 4` means the interface wasn't updated.

## Bug Class 7: First-Element Approach Animation Missing

**Symptom:** The FIRST key's approach ring/countdown never appears at session start; every subsequent element works. Only the first one looks broken.

**Cause:** The spawn filter `if (timeUntilHit > this.preemptTime) continue;` combined with a fixed lead-in longer than the preempt window. At t=0 the first note is `LEAD_IN_MS` away; if `LEAD_IN > preemptTime`, the ring is silently skipped until songTime catches up — nothing renders for the first ~1.5 seconds.

**Fix — make lead-in match preempt per difficulty:**

```javascript
const LEAD_IN_MS = { easy: 1500, medium: 1000, hard: 600, expert: 350 };
// note.time = LEAD_IN_MS[difficulty] + i * beatInterval
```

The first note then sits exactly at the preempt boundary at t=0, so its ring spawns immediately. A single fixed `LEAD_IN_MS = 3000` works only for the difficulty whose preempt equals it.

## Pitfall: Dev/Debug UI Must Be Flag-Gated

A visible debug readout (judgment log, combo circle, counts) gets reported by users as a "blur of symbols" or "double readout" when stacked or when it renders over itself. Gate ALL dev UI behind a flag that defaults to false:

```javascript
showDebugUI = false; // dev tool, not player-facing
createUI() {
  if (!this.showDebugUI) return; // create nothing
}
```

Keep wanted production feedback (e.g. a stats counter) as a SEPARATE core element in the feedback layer — hiding debug UI must not also remove feedback the player wants, or you get a follow-up bug report.

## Pitfall: Reset-on-END Destroys Final Results

Players want to read their final numbers after the session ends. If stats/state reset runs in `endGame()` (or a `reset()` called from it), the results vanish the instant the game completes. Reset only in `startGame()` — the results display survives until the player begins the next session.

## Pitfall: Unit Tests Do Not Prove the Wiring

In this bug family, unit tests keep passing (34/34, 48/48) while the integration breaks every session. Unit tests prove components in isolation; they cannot catch: a hook that is never emitted, a method that doesn't exist, teardown ordering, or `setStartTime()` called after the bus starts.

**Before declaring a session-based UI "fixed", drive one full session headlessly** (or with a debug plugin) and assert: exactly one UI instance exists, no events fire after teardown, and a correctly-timed input registers correctly. This single integration check catches every class above.

## Session Reference

See `references/{CLIENT}` for the concrete {CLIENT} case: every bug class above, with the exact symptoms and diffs.
See `references/{CLIENT}` for Bug Classes 6-7 (ring/feed desync, first-key ring missing) plus the stats-persist and debug-UI-gating fixes.
See `references/{CLIENT}` for the MVP polish checklist and domain patterns.
