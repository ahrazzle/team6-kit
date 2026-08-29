<!-- GENERICIZED: 1×{AMOUNT}, 17×{CLIENT}, 2×{RELATIONSHIP} | source: skills/software-development/browser-game-development/SKILL.md -->
---
name: browser-game-development
description: "Build browser games with TypeScript and canvas rendering."
version: 1.0.0
author: {RELATIONSHIP} ({RELATIONSHIP}), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [browser, game, typescript, es-modules, canvas, animation]
    related_skills: [hermes-agent-skill-authoring]
---

# Browser Game Development Skill

> Build browser-based games with TypeScript ES modules, event buses, and canvas/SVG rendering. Covers the full pipeline from source to playable browser game.

## When to Use

- Building a browser-based game or interactive demo
- Working with TypeScript compiled to ES modules for browsers
- Implementing event-driven input handling (keyboard, mouse)
- Rendering with Canvas 2D, SVG, or hybrid approaches
- Dealing with browser caching of bundled JavaScript
- Implementing animation loops and game state management

**Don't use for:** Node.js-only games, WebGL/Three.js projects (different rendering model — see `threejs-webgl-development`), or non-interactive web apps.

## Prerequisites

- TypeScript source files
- esbuild or similar bundler (`npx esbuild src/index.ts --bundle --outfile=dist/bundle.js --format=esm`)
- Local HTTP server for development (`python3 -m http.server 8000`)

## Architecture Pattern

The standard architecture for a browser game framework:

```
src/
  index.ts              # Public API exports
  EventBus.ts           # Input capture → normalization → judgment
  GameJudge.ts          # Timing, scoring, state management
  FeedbackLayer.ts      # Canvas/SVG rendering
  effects/
    ParticleSystem.ts   # Canvas particle effects
    ApproachRingSystem.ts  # Rhythm game anticipation rings
  game/
    BeatMap.ts          # Static note data
    BeatMapGenerator.ts # Convert content → playable notes
    Types.ts            # Shared interfaces
dist/
  bundle.js             # Single-file ES module bundle
demo.html               # Self-contained playable page
```

## Critical Pitfalls

### 0. TypeScript Annotations in Inline Scripts (SILENT DEATH)

**THE #1 CAUSE OF "BUT IT WORKS LOCALLY" FAILURES IN BROWSER GAMES.**

Browsers execute JavaScript — NOT TypeScript. If you copy TypeScript code into an inline `<script>` block in HTML, type annotations cause a syntax error that kills the entire script block:

```javascript
// ❌ BREAKS BROWSERS — TypeScript annotation
const preemptTimes: Record<string, number> = { easy: 1500 };

// ✅ WORKS — Pure JavaScript
const preemptTimes = { easy: 1500 };
```

**The failure mode is silent death:** The browser throws `SyntaxError: Unexpected token ':'`, and the entire `<script>` block fails to parse. No error message, no console output, just dead buttons and unresponsive UI.

**Why it "works locally":** Your local server may be transpiling the HTML (e.g., Vite, webpack dev server). GitHub Pages serves raw files — no transpilation.

**Debug checklist when "nothing happens" on button click:**
1. Open browser console → look for `SyntaxError: Unexpected token ':'`
2. Search inline scripts for `: Record<`, `: Array<`, `: string`, `: number`, `: void`, `: boolean`, `: any`
3. Remove ALL type annotations from inline scripts
4. The bundle.js is fine (esbuild strips types) — only inline scripts are affected

### 1. Bundle Cache Busting (Browser Cache)

Browsers aggressively cache `.js` files. After pushing updates, users see stale code.

**Symptom:** User reports "buttons don't work" but server files are correct.

**Fix:** Add version query parameter to bundle import:
```javascript
import { Game } from './dist/bundle.js?v=3';
```

Add cache-control meta tag to HTML `<head>`:
```html
<meta http-equiv="cache-control" content="no-cache, no-store, must-revalidate">
```

When updating, increment the version number (`?v=4`, `?v=5`, etc.).

### 2. ES Module CORS

Browsers block `file://` URLs from loading ES modules. Must serve via HTTP.

**Fix:** Always use a local HTTP server for development:
```bash
python3 -m http.server 8000
```

### 3. Render Loop Timing

Starting render loops (particles, animation) before game state exists causes null reference errors.

**Fix:** Initialize rendering systems but don't `start()` them until game begins:
```javascript
// Page load — create but don't start
const renderer = new FeedbackLayer({ container, width, height });
// renderer.start();  // DON'T

// Game start — now start
renderer.start();  // DO
```

### 3b. Canvas Negative Radius Crash

When animating expanding circles (ripples, shockwaves), if a ripple's `startTime` is in the future (e.g., staggered animations), the elapsed time can go negative, producing a negative radius:

```
IndexSizeError: Failed to execute 'arc' on 'CanvasRenderingContext2D': The radius provided (-59.77) is negative.
```

**Fix:** Clamp elapsed to non-negative and progress to [0,1]:
```javascript
const elapsed = Math.max(0, now - r.startTime);
const progress = Math.min(1, elapsed / r.duration);
const radius = r.maxRadius * this.easeOutQuad(progress);
```

### 4. Rhythm Game Timing

`performance.now()` returns absolute time (ms since page load). Note times in beat maps are relative (0, 1000, 2000...).

**Fix:** Track song start time and compute relative delta:
```javascript
const delta = (evt.raw.timestamp - startTime) - expected.time;
```

### 5. Character Order Preservation

Don't reorder note sequences for "ergonomic" reasons. In a typing game, the user's text is sacred — shuffling characters destroys the intended input.

### 6. Orphaned Events Between Games

After a game ends, the old judge/bus keep firing events. Keypresses during the transition window reach the old judge, which logs MISS events.

**Fix:** Proper teardown sequence in `endGame()`:
1. Capture results BEFORE tearing down
2. Stop bus FIRST (prevents keypresses reaching judge)
3. Null out judge/bus references
4. Stop feedback layer and reset state
5. THEN set `gameActive = false`

### 7. Keypresses During Lead-In

With a 3-second lead-in, keypresses before the first note register as MISS (delta = 500 - 3000 = -2500ms).

**Fix:** Ignore keypresses where `delta < -windows.good` — too early to judge.

### 8. "Two Keyboards" is Visual Layering

User sees "two overlapping keyboards" — one working, one stuck. Reality: 1 SVG keyboard + 2 transparent canvases (particles + approach rings). The stuck element is a nudge highlight from a previous game.

**Diagnostic:** `document.querySelectorAll('svg.{CLIENT}').length` returns 1.

**Fix:** `stop()` must call `keyboard.reset()` to clear all visual highlights.

### 9. Debug Overlays Must Not Ship

A dev HUD (judgment feed, combo circle, debug counters) rendered into the game shows as a "blur of symbols" overlaying the product — and its console.log spam ends up in user bug reports. Any dev/diagnostic UI belongs behind a flag that defaults to `false`, and the flag must gate THREE things: DOM creation, the render loop, AND console logging. If a user can see it, it's product UI — design it or hide it. See `references/{CLIENT}` §9.

### 10. Never Mangle the User's Input by Difficulty (MEDIUM/HARD BUGS)

Difficulty settings must change *timing*, not *content*. Two real bugs:
- **Medium stripped spaces** — a `shouldSkip` density filter returned `key === ' '` on medium, so "is this my content" became "isthismycontent". User's text is sacred.
- **Hard duplicated letters exponentially** — `injectDoubledNotes` spliced notes into the array *while iterating it*; inserted notes got re-processed, doubling repeatedly. Symptom: "iiss tthiiss my coonntteenntt".

**Fixes:** never filter characters (spaces included) out of the user's content; if you must insert notes, capture `originalLength` before the loop, `push` (not `splice`) during iteration, then `sort` by time — or better, drop the transformation entirely and let difficulty only tighten timing windows.

### 11. Keyboard Key Lookups Are Case-Sensitive (PASTED TEXT BUG)

Keyboard layout stores lowercase key ids (`h`, `a`). If you preserve the user's text case, an uppercase note `H` fails `getKeyElement('H')` → no approach ring, no highlight, and the first key looks "skipped".

**Three coordinated fixes:**
1. **Lookups lowercase**: `const lookupKey = keyId === ' ' ? 'space' : keyId.toLowerCase()` in every `getKeyElement` path (approach rings, expected-key indicator, key bounds).
2. **Judge compares case-insensitively**: `evt.char.toLowerCase() !== expected.key.toLowerCase()` — otherwise a kid with caps lock on (or capitalizing the first letter, as taught) gets a guaranteed miss on every letter.
3. **Generator preserves the user's text case** — don't `toLowerCase()` the content; the feed should show what they typed. Lowercasing is only for the lookup, never for the content or the judgment.

### 17. Audio Timing Must Be Verified, Not Assumed (RHYTHM GAMES)

When the judge's beat-grid derives from a track manifest (canonical BPM + beat-grid per file), verify the audio actually decodes to its declared duration instead of assuming it:

1. **Measure decode precision with ffmpeg exact sample counts**, never browser decode: `ffmpeg -v error -i file.ogg -f s16le -ac 1 -ar 44100 - | wc -c` → samples/44100. Real measured result (OpMon .ogg files): declared 99.6238s / decoded 99.6238s — ±0.2ms over a 90s round. The feared VBR decode drift is often a non-issue; the manifest beat-grid is then safe.
2. **`decodeAudioData` needs a real audio device** — headless Chrome has none, so a decode-on-load probe hangs silently. Don't fight it: use ffmpeg for the deterministic half and keep a user-gesture Run button for the hardware-only half (playback clock vs wall clock over a ~30s loop).
3. **Playback-clock offset is per-device**: `AudioContext.currentTime` vs `performance.now()` differs by a fixed offset measurable only on real audio hardware. Contract fix: anchor session start to the audio clock (or one-time offset calibration at playback start) — one calibration, not a per-note fix.

Details + probe architecture: `references/{CLIENT}` ("Audio determinism — RESOLVED").



### 18. Note Grid Must Be Decoupled From Music BPM (THE "INPUT DEAD" BUG)

When a typing game locks its note grid to the music tempo, natural child-paced typing breaks it: at 120 BPM letters are 500ms apart; a player pausing >1s between letters lets the judge's `tick()` mark every pending note stale → the round auto-completes → the judge detaches into the menu → **input genuinely dies mid-word** ("one key then dead" reported live while every headless sim passed). Music-locked grids are exactly what rhythm games ship and exactly what breaks for variable human pace.

Fix (zero framework surface):
- **Decouple the note grid from the music.** Grid BPM is the *typing* tempo (60 BPM = 1000ms/letter for 7–10yo); music BPM is flavor only. The judge derives notes from the grid, never the audio clock.
- **Reframe the product claim** from "rhythm game" to "typing game with rhythm" — the rhythm that matters is the player's self-consistent pacing (approach rings at ~1000ms/letter), not musical sync. This kills the whole bug class and deletes the audio-clock calibration seam.
- **Single-word rounds with menu-seam pauses:** word = round; the pause between words lives in the menu gate (judge detached), so rest is free. Soft-fail spaces (suppress HP drain/combo break when `note.key === ' '`) as the safety net for trailing-space rests.

### 19. Completion Must Converge in the Tick Loop — With a POST-TICK Fresh Read

The stall bug: the round's last letter pressed late (past the window) → `onMiss` advances the cursor to complete → nothing calls next-round → the tick loop's `!isComplete` guard stops → **game freezes on a finished round**. Checking completion only in onHit/onNoteStale misses the onMiss path.

Fix — one convergence point, inside the tick loop AFTER `session.judge.tick()`:
```js
if (S.phase === "battle" && session.judge.state.isComplete && !S.sessionDone) nextRound();
```
Critical detail: **re-read `state` AFTER tick()** — tick() mutates the cursor, so a pre-tick captured `st.isComplete` is still false when the stale path just completed the map. The fresh read is the difference between the fix working and the same stall.

Testing note: a fixed-cadence autofight sim can't exercise the late-final-letter path — it types every note before the window closes. Make the sim ring-aware (only press when `delta > -200`), or stop it at the last letter and let the window lapse.

### 20. Framework UI Has Its Own Anchors — Wrapper CSS Is Not Enough

`#wrapper{top:0}` moves the wrapper, not the child. {CLIENT}'s `keyboardContainer` is `position:absolute; bottom:0; height:55%` — anchored to the WRAP'S BOTTOM, so the keyboard floats mid-screen no matter how flush the wrapper is. This burned four user asks ("keyboard not against top").

Diagnose: don't assume the child follows the parent — read the framework's layout code (`grep -n 'style.position\|style.bottom\|style.top' vendor.js`) and re-anchor the CHILD:
```css
#{CLIENT} > div[style*="bottom"]{bottom:auto!important; top:0!important;}
```
Same class of trap: the framework's built-in chrome the product doesn't want — `feedback.statsDisplay` (top-left judgment counter) and `feedback.expectedKeyIndicator` (floating orange keycap) — needs `display:none` after EVERY session creation (initial + per-round rebuilds), or the built-ins reappear on the next round. Wrap it in a hide helper and call it at both sites.

- **First ring invisible at game start**: if the note is `LEAD_IN_MS` away and `LEAD_IN_MS > preemptTime`, the spawn filter `if (timeUntilHit > preemptTime) continue` skips it until song time catches up. Fix: set the lead-in *per difficulty* equal to that difficulty's preempt time (easy 1500, medium 1000, hard 600, expert 350) so the first ring is exactly `preemptTime` away at t=0.
- **Rings drift ahead of the feed**: ring shrink is driven by `note.time`, but the character feed advances on judgment (which can be early). Fix: collapse the ring on judgment — call `markJudged(note, judgment)` from `onHit`/`onMiss`/`onNoteStale` so the ring pops the same frame the feed advances.

### 13. End-of-Game Copy Must Match the Product

User corrections when the "framework" got exposed in a game build:
- "Song Complete!" → "Round Complete" (there is no song).
- Title "…Framework Validation" → just the product name.
- Remove now-false copy (e.g., "wrong keys are silently ignored" once wrong keys got feedback).

Rule: no framework/engineering vocabulary in user-facing copy; the end screen names what the user just did (a round), not what the code is.

### 14. One Canonical Bundle Filename (IMPORT-PATH DRIFT)

A recurring stale-deploy cause that "rebuild the bundle" does NOT fix: two bundle filenames in the repo (`dist/bundle.js` and `dist/game.js`), the demo importing one while builds write the other. Rebuilding "correctly" writes to `bundle.js`, but the browser loads `game.js` — the served file stays stale no matter how many times you rebuild and push, and docs pointing at the 404 filename break a forker's first command.

**Prevention:**
1. Pick ONE bundle filename and make it canonical (`dist/game.js` if that's what the demo imports).
2. Before writing any build command or docs, check the demo's actual import: `grep -o "from './dist/[a-z]*\.js" demo.html`.
3. After a rebuild, verify the SERVED file at `raw.githubusercontent.com/<owner>/<repo>/main/<bundle>` contains the fix string — not just that local `dist/` is fresh.
4. Keep every doc import path in sync (README, guides, examples) — grep the whole repo for the stale filename before announcing a handoff.

### 15. Hide Multi-Step Wiring Behind a Facade

Repeated integration failures (`feedback.start()` before `setJudge()`; `setStartTime()` after `rawBus.start()`) all trace to callers assembling a multi-step pipeline in the wrong order — and unit tests pass because they test components in isolation, not the wiring. Once the order is known-good, wrap it:

```typescript
function createSession({ container, content, bpm, difficulty, hooks }) {
  const feedback = new FeedbackLayer({ container });          // constructed, NOT started
  const notes = new BeatMapGenerator().generate(content, { bpm, difficulty });
  const judge = new BeatClockJudge(new StaticBeatMap(notes), { difficulty }, hooks);
  feedback.setJudge(judge);              // 1. wire judge into feedback
  judge.setStartTime(performance.now()); // 2. timing baseline before any key
  feedback.start();                      // 3. animation (safe: judge exists)
  const raw = new RawBus(window), norm = new NormalizedBus(raw);
  norm.start(); judge.attach(norm); raw.start();  // 4. events flow
  return { judge, feedback, destroy() { /* full teardown */ } };
}
```

The safe order is **setJudge → setStartTime → start → attach bus**. Document it, enforce it with the facade, and give callers a `destroy()` so repeated sessions don't stack DOM/listeners.

### 16. Handoff Packages: Trust the Bundle, Not the .d.ts

A shipped plugin/handoff can carry **stale type declarations**. {CLIENT}'s handoff had `dist/types.d.ts` + standalone `dist/BeatClockJudge.js` (Aug 23) older than the canonical `dist/game.js` bundle (Aug 28): the `.d.ts` lacked `onWrongKey`/`onStreakThreshold`/`setStartTime`/`getSongTime` that the bundle actually has, and listed `onGameStart`/`onGameEnd`/`onSongComplete` as live when nothing ever invokes them. Authoring a plugin against the `.d.ts` silently builds against the wrong surface.

**Check before trusting any contract claim about a handoff:**
1. `ls -la dist/` — if artifact mtimes differ, the declarations are suspect.
2. Grep the ACTUAL shipped bundle (`dist/game.js`) for the hooks/methods — that is the surface you get at runtime.
3. Check what actually invokes a hook: `grep -n 'hooks.onX' dist/game.js`. A hook implemented only by a debug plugin (or declared only in types) is dead for plugin consumers.
4. Author with plugin-local types mirroring the bundle surface; regenerating `.d.ts` is the framework owner's job.

## {CLIENT}-Battler Architecture (Pose/Motion)

For turn-based battlers rendered on a canvas overlay, split animation into TWO schemas — fusing them is the trap:

- **Pose** = data layer: frames + palette + license tag (a pure record, replaceable, interchangeable between asset sources).
- **Motion** = engine-owned feel: a recipe of tweens/FX keyed by pose id. A recipe never references the asset — only the pose id — so one engine serves multiple asset layers with zero provenance leakage.

**Recipe-category constraint (the maintenance trap):** motions must be parameterized by a small taxonomy — monster archetype × size class (e.g. blob/quad/biped/serpent × small/medium/large) — NEVER tuned per monster. 45 monsters × N bespoke recipes is a combinatorial explosion; 4 archetypes × 3 sizes = 12 recipes covers all. Prove it in the spike: render two monsters in the same category sharing ONE recipe object instance and assert identity in the page.

**Quality gate:** pixel art at child scale needs a contact sheet vote — all sprites at battle size on the battle background, before any enter the starter pack. Monsters must read as monsters, not noise blobs; the vote also corrects the taxonomy draft (archetype labels are guesses until eyeballed).

**Make the vote objective first.** Measure every {CLIENT}'s geometry at manifest generation (PIL alpha channel): `bbox` → `areaPct` (bbox area / canvas area), `density` (painted pixels / bbox area), `aspect` (w/h). Flag `tiny` when areaPct < 15% (auto-scale with a `scaleHint` ~1.6–2.6× so small sprites read at battle scale), `sparse` when density < 10%. Print the numbers under each cell on the contact sheet and tag the named problem set in red — geometry confirms or kills the eyeball read and corrects the taxonomy draft (a "serpent" bucket full of vertical columns at aspect 0.5–0.8 is a dumping ground, not a shape class). Rule: derive every display label from the SAME function the logic uses (e.g. the category lookup) — labels hardcoded a second time will silently disagree with the table they describe.

See `references/{CLIENT}` for the working spike architecture, recipe player, and {CLIENT} contract surface.

## Third-Party Asset Integration (License Island)

Pulling CC-BY-SA/GPL assets beside an MIT engine (open-source launchpads like OpMon/Tuxemon) works ONLY with a ship-time island:

1. **Own directory + own LICENSE** — e.g. `assets/ccbysa/`, never mixed into engine code.
2. **Manifest is the only provenance point.** A generator script produces (a) a machine manifest (`poses.json`: id → frames → license) that the ENGINE consumes — the renderer never touches paths, so it cannot tangle layers at runtime; (b) a per-file SHA-1 attribution ledger (`ATTRIBUTION.md`) — the ship-time proof of the island.
3. **Build assertion:** paid/original content must resolve to ZERO `ccbysa/` entries — fail the build, not the convention.
4. Exclude `.import`/Godot metadata artifacts at pull time; count ACTUAL PNGs at depth before claiming an inventory (directory entry counts lie — e.g. "171 entries" was really 85 PNGs + metadata).
5. **Audio gets the same island — a per-track manifest.** `tracks.json` carries per file: exact PCM-frame duration (ffmpeg decode, not container read; `-ac 2 -ar 44100` → frames = bytes/4 for 2ch×2B), design BPM, beat count, SHA-1, and **honest vet flags** (`vet: "pending-ears"`, `tempoVerified: false`). Design BPM is game-assigned within the engine's tempo range — never invent musical tempo; the manifest must say it is a design value until a human ear confirms. The flag makes "exclude on doubt" mechanically enforceable: a track is unusable until the vet flips.
6. **Generator ROOT pitfall (hit 3× in one session):** when the generator script lives INSIDE the asset dir it manages, `dirname(__file__)` IS the managed dir — do NOT append the subdir name again (`ROOT/audio`, `ROOT/ccbysa`), or it walks/empty-writes the wrong path and appends the ledger to the wrong file (a stray ATTRIBUTION.md appeared inside audio/ while the island ledger stayed silent). The shared island ledger lives one level up: `os.path.dirname(ROOT)` when the script sits in a sub-layer.

Reusable generators: `scripts/generate-license-manifest.py` ({CLIENT} poses) and `scripts/generate-track-manifest.py` (audio tracks).

## Implementation Workflow

### Step 1: Scaffold

```bash
npm init -y
npm install --save-dev typescript tsx esbuild
```

Create `tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "outDir": "dist"
  },
  "include": ["src"]
}
```

### Step 2: Build Bundle

```bash
npx esbuild src/index.ts --bundle --outfile=dist/bundle.js --format=esm
```

### Step 3: Create Demo Page

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta http-equiv="cache-control" content="no-cache, no-store, must-revalidate">
</head>
<body>
  <div id="stage"></div>
  <script type="module">
    import { Game } from './dist/bundle.js?v=1';
    // Initialize game
  </script>
</body>
</html>
```

### Step 4: Serve and Test

```bash
python3 -m http.server 8000
```

Navigate to `http://localhost:8000/demo.html`. Hard refresh (Cmd+Shift+R) after each update.

## Animation Patterns

### Spring-Physics Key Depression

CSS animation with overshoot creates mechanical switch feel:

```css
@keyframes {CLIENT} {
  0% { transform: translateY(0) scale(1); }
  30% { transform: translateY(4px) scale(0.95); }  /* Overshoot */
  60% { transform: translateY(2px) scale(0.97); }  /* Bounce back */
  100% { transform: translateY(2px) scale(0.96); }  /* Settle */
}
.{CLIENT} {
  animation: {CLIENT} 350ms cubic-bezier(0.34, 1.56, 0.64, 1);
}
```

To re-trigger, remove class → force reflow → add class:
```javascript
element.classList.remove('{CLIENT}');
void element.getBoundingClientRect();  // Force reflow
element.classList.add('{CLIENT}');
```

### Ripple Emanation

Concentric expanding circles from keystroke position:

```javascript
emitRipple(x, y, color) {
  const ripple = { x, y, startTime: performance.now(), duration: 500, maxRadius: 150 };
  this.ripples.push(ripple);
}

renderRipples(ctx) {
  const now = performance.now();
  for (const r of this.ripples) {
    const progress = (now - r.startTime) / r.duration;
    const radius = r.maxRadius * progress;
    const alpha = 1 - progress;
    ctx.beginPath();
    ctx.arc(r.x, r.y, radius, 0, Math.PI * 2);
    ctx.strokeStyle = `rgba({AMOUNT},${alpha})`;
    ctx.stroke();
  }
}
```

### Approach Rings (Rhythm Games)

Rings shrink toward target key, matching size at hit moment:

```javascript
const progress = 1 - (timeUntilHit / preemptTime);
const scale = maxScale + (1 - maxScale) * progress;
const radius = keyRadius * scale;
```

Preempt time scales with difficulty:
- Easy: 1500ms
- Medium: 1000ms
- Hard: 600ms
- Expert: 350ms

## Event Bus Architecture

```
Raw Input → Normalized Bus → Judge → Plugin Hooks → Feedback Layer
```

Each layer transforms events and passes to next:

```javascript
// RawBus: captures DOM events, stamps performance.now()
// NormalizedBus: handles shift/caps/lock, filters repeats
// Judge: computes timing delta, classifies perfect/great/good/miss
// PluginHooks: fans out to DebugPlugin, ScorePlugin, etc.
// FeedbackLayer: renders particles, rings, combo display
```

## Verification

- Bundle loads without CORS errors in browser console
- Hard refresh loads latest bundle version
- Render loops only active during gameplay
- Timing deltas computed relative to song start
- Character sequences match input exactly (no reordering)
- Orphaned events don't leak between games (proper teardown)
- Keypresses during lead-in are ignored (not judged as MISS)
- Only 1 SVG keyboard in DOM (visual layering is transparent canvases)
- Canvas-heavy pages verified headless by **dumping the rendered DOM**, not just HTTP 200: `chrome --headless=new --disable-gpu --no-sandbox --virtual-time-budget=9000 --dump-dom URL`, then parse for the stats the page itself injects (a render-success marker per section: sheet note, tile count, taxonomy rows). One JS error mid-boot aborts every later render, so assert each section's marker, not the page load. Use `--screenshot` for the durable artifact. Note: the browser-use `browser_exec` tool blocks private/localhost addresses — for local dev servers use the headless Chrome CLI instead.
- **Deterministic layout assertions on the SERVED page (the anti-"works headless" gate):** when a layout claim has failed more than once, stop arbitrating with screenshots and put a console assertion in the page: `[{CLIENT}] check: keyboardRect.top=0 → PASS/FAIL`, `keyFeed.bottom=58px → PASS/FAIL`. Run it **rAF-sampled** (every ~15th frame, not a 3s timer — a 3s sample can miss the broken frames a player occupies) and **state-aware** (feed asserted only in the active-battle phase; the keyboard always). Measure `getBoundingClientRect()` on the SERVED URL mid-battle — never the victory screen. Announce "done" only when that console line is green on the URL the user tests. Details: `references/deployment-verification.md`.
- **Headless sims ≠ real browser.** A fixed-cadence sim passed every round while the user's real typing broke — it typed every note before the window closed and never hit the stale path. Repro with a human-pace sim (irregular 600–1200ms gaps dispatched on the real document path) or a ring-aware sim (press only in-window).
- **Screenshot receipts must be fresher than the source they document** — a screenshot older than `index.html` (mtime check) showing the pre-fix state proves nothing. Re-shoot from the live page mid-battle.
