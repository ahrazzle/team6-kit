<!-- GENERICIZED: 8×{CLIENT}, 3×{RELATIONSHIP} | source: skills/software-development/browser-game-development/references/{CLIENT} -->
# {CLIENT} Framework — Session Lessons

## Project Overview

{CLIENT} is a rhythm-typing game framework for kids. Players type to the beat — keystrokes land on rhythm-game timing windows (Perfect/Great/Good/Miss), with satisfying particle effects and an animated reactive keyboard.

**Workspace:** `/Users/{RELATIONSHIP}/{CLIENT}{CLIENT}`
**GitHub:** `https://github.com/{RELATIONSHIP}/{CLIENT}`
**Live demo:** `https://{RELATIONSHIP}.github.io/{CLIENT}`

## Critical Bugs & Fixes

### 1. Timing Mismatch (CRITICAL)
**Bug:** `delta = evt.raw.timestamp - expected.time` mixed absolute `performance.now()` with relative note times. Every correct key fell outside all windows → always "miss".

**Fix:** Track song start time and compute relative delta:
```javascript
const delta = (evt.raw.timestamp - startTime) - expected.time;
```

### 2. Hand-Alternation Shuffle (CRITICAL)
**Bug:** `applyHandAlternation()` swapped keys between positions to break same-hand triples. Turned "abcdef123456" into "a1c2e3b4fd56".

**Fix:** Removed the shuffle entirely. Character order is sacred in a typing game.

### 3. TypeScript Annotations Break Browser Scripts (CRITICAL)
**Bug:** Inline `<script type="module">` blocks contained TypeScript type annotations like `const preemptTimes: Record<string, number> = {...}`. Browsers don't parse TypeScript — the entire script block fails silently. No console error, no event listeners attached, buttons do nothing.

**Why it's insidious:** esbuild strips types from `bundle.js`, so bundled code works fine. But inline scripts in HTML are served raw — GitHub Pages doesn't transpile them. The browser throws a syntax error on the first `: Type` annotation and the entire script block never executes.

**Fix:** Strip ALL type annotations from inline `<script>` blocks in HTML files.
```javascript
// WRONG — breaks browsers (TypeScript annotation)
const preemptTimes: Record<string, number> = { easy: 1500, medium: 1000 };

// RIGHT — pure JavaScript
const preemptTimes = { easy: 1500, medium: 1000 };
```

**Detection:** If buttons do nothing AND the bundle.js loads correctly, suspect TypeScript annotations in inline scripts. Open browser console — there may be no error message because the script never starts executing.

### 4. Browser Cache
**Bug:** After pushing updates, users saw stale code because browsers cache `.js` files aggressively.

**Fix:**
- Add version query parameter: `import { Game } from './dist/bundle.js?v=3'`
- Add cache-control meta tag: `<meta http-equiv="cache-control" content="no-cache, no-store, must-revalidate">`

### 5. Premature Render Loop Start
**Bug:** `feedbackLayer.start()` called on page load, starting animation loops before game state existed. Null reference errors.

**Fix:** Don't call `start()` until game begins:
```javascript
// Page load — create but don't start
const renderer = new FeedbackLayer({ container, width, height });
// renderer.start();  // DON'T

// Game start — now start
renderer.start();  // DO
```

### 6. Orphaned Events Between Games (CRITICAL)
**Bug:** After a game ends, the old judge/bus keep firing events. Keypresses during the transition window reach the old judge, which logs MISS events. Console shows:
```
Game Over — Max Combo: 14   ← first game ends
MISS pressed="t" expected="t" ← OLD judge still firing
MISS pressed="e" expected="e" ← OLD judge still firing
PERFECT "s" combo=1           ← new game starts
```

**Root cause:** `endGame()` sets `gameActive = false` but doesn't stop the raw bus or null the judge until the *next* `startGame()`. That window is where orphaned events leak through.

**Fix 1 — Proper teardown sequence in `endGame()`:**
```javascript
function endGame() {
  // Capture results BEFORE tearing down
  const finalCombo = judge ? judge.state.maxCombo : 0;

  // Stop bus FIRST to prevent any keypresses from reaching the judge
  if (rawBus) rawBus.stop();
  if (normBus) normBus.stop();
  if (tickHandle) clearInterval(tickHandle);

  // Null out old judge so any queued events are ignored
  judge = null;
  normBus = null;
  rawBus = null;

  // Stop feedback and reset state
  feedbackLayer.stop();
  feedbackLayer.reset();
  gameActive = false;
}
```

**Fix 2 — Null out references in `startGame()` too:**
```javascript
// Clean up previous
if (judge) judge.detach();
if (normBus) normBus.stop();
if (rawBus) rawBus.stop();
if (tickHandle) clearInterval(tickHandle);
// Null out references to prevent orphaned events from old game
judge = null;
normBus = null;
rawBus = null;
```

**Fix 3 — Fresh DebugPlugin per game:**
```javascript
// In startGame():
debugPlugin = new DebugPlugin();
debugPlugin.setFeedbackLayer(feedbackLayer);
```

### 7. Keypresses During Lead-In (CRITICAL)
**Bug:** With a 3-second lead-in before the first note, keypresses during that window registered as MISS. The delta would be something like `500 - 3000 = -2500ms` — far outside the ±500ms window.

**Symptom:** User presses keys right after starting, before any note arrives. Every press = MISS.

**Fix:** Ignore keypresses that happen before the note's window opens:
```javascript
onChar(evt: NormalizedEvent): void {
  // ... get expected note ...

  const songTime = evt.raw.timestamp - this._startTime;
  const delta = songTime - expected.time;

  // Ignore keypresses that happen before the note's window opens
  if (delta < -this.windows.good) {
    return; // Too early — don't register as wrong
  }

  // ... rest of judging logic ...
}
```

### 8. "Two Keyboards" Visual Layering (NOT A BUG)
**User report:** "There are two overlapping keyboards — one working, one with a red circle on 7."

**Reality:** There is only ONE SVG keyboard. The "second keyboard" is visual layering of:
- 1 SVG keyboard (bottom layer, z-index 1)
- 1 canvas for particles (middle, z-index 2, transparent)
- 1 canvas for approach rings (middle, z-index 3, transparent)

**Diagnostic:** Run in console: `document.querySelectorAll('svg.{CLIENT}').length` — returns 1.

**The red circle on "7":** A stuck nudge highlight from a previous game that wasn't cleared. Fix: `stop()` must call `keyboard.reset()` which clears all visual highlights.

### 9. Debug Overlays Must Not Ship (CRITICAL — user-facing)
**User report:** "There's a double readout on the left side overlaid on top of each other making it look like a blur of symbols." The keyboard and effects looked great, but the dev HUD ruined it.

**Root cause:** The DebugPlugin (built to validate the plugin contract) renders a visible HUD — combo circle, progress bar, judgment log feed, and judgment counts — into the game container. This was development scaffolding, but it shipped as the game UI. Over multiple games the DOM accumulated and text stacked into a blur.

**Fix:** Gate ALL debug UI behind a flag, default OFF. This means three things, not one:
1. Don't create the DOM elements (no overlay)
2. Don't run the render loop (no per-frame work)
3. Don't `console.log` judgment lines (keeps dev console clean too — the user pasted the console feed into bug reports; muting it cuts noise)

```typescript
private showDebugUI = false; // dev-only overlay

private createUI(): void {
  if (!this.showDebugUI) return; // skip DOM creation entirely
  ...
}
private startRenderLoop(): void {
  if (!this.showDebugUI) return; // skip rAF loop
  ...
}
private log(msg: string): void {
  ...
  if (this.showDebugUI) {
    console.log(`[${this.name}] ${msg}`); // mute console noise
  }
}
```

**Rule:** any dev/diagnostic UI (debug feeds, hit-box visualizers, judgment counters) belongs behind a flag that defaults to false in shipped builds. If a user can see it, it's product UI — design it or hide it.

## Architecture Lessons

### Event Bus Pattern
```
Raw Input → Normalized Bus → Judge → Plugin Hooks → Feedback Layer
```

Each layer transforms events and passes to next:
- **RawBus:** captures DOM events, stamps `performance.now()`
- **NormalizedBus:** handles shift/caps/lock, filters repeats
- **Judge:** computes timing delta, classifies perfect/great/good/miss
- **PluginHooks:** fans out to DebugPlugin, ScorePlugin, etc.
- **FeedbackLayer:** renders particles, rings, combo display

### Approach Ring System (Rhythm Game DNA)
Rings shrink toward target key, matching size at hit moment:

```javascript
const progress = 1 - (timeUntilHit / preemptTime);
const scale = maxScale + (1 - maxScale) * progress;
const radius = keyRadius * scale;
```

**Preempt time scales with difficulty:**
- Easy: 1500ms
- Medium: 1000ms
- Hard: 600ms
- Expert: 350ms

### Spring-Physics Animation
CSS animation with overshoot creates mechanical switch feel:

```css
@keyframes {CLIENT} {
  0% { transform: translateY(0) scale(1); }
  30% { transform: translateY(4px) scale(0.95); }  /* Overshoot */
  60% { transform: translateY(2px) scale(0.97); }  /* Bounce back */
  100% { transform: translateY(2px) scale(0.96); }  /* Settle */
}
```

To re-trigger: remove class → force reflow → add class.

## Animation Enhancements

1. **Ripple Emanation** — Concentric expanding circles from keystroke position
2. **Specular Highlight Sweep** — Diagonal streak of white light on perfect hits
3. **Confetti Burst** — Colored rectangles burst with sparks on perfect hits
4. **Multi-note approach rings** — Multiple simultaneous rings on different keys at different shrink stages

## User Feedback Patterns

- **"Nothing happens" / "buttons don't work"** → Check for TypeScript annotations in inline scripts first, then timing bugs
- **"Can't get past intro screen"** → Bundle not rebuilt after changes, or onboarding button not wired to start game
- **"Way too fast for kids"** → BPM range was 40-180; lowered to 20-120 with default 40
- **"Two overlapping keyboards"** → Visual layering of 1 SVG + 2 transparent canvases, not two keyboards
- **"MISS between games"** → Orphaned judge/bus not torn down properly
- **"MISS during lead-in"** → Keypresses before first note's window opens

## Build & Deploy

```bash
# Build bundle
npx esbuild src/index.ts --bundle --outfile=dist/bundle.js --format=esm

# Serve locally
python3 -m http.server 8000

# Commit and push
git add -A && git commit -m "Description" && git push
```

## Key Insight

The difference between "flash card with a ring" and "rhythm game" is **multiple simultaneous notes at different distances**. osu! and Stepmania show 3-4 approach circles at once, creating the "reading" skill — scanning ahead, planning finger movements.
