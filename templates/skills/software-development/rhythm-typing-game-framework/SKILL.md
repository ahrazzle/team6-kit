<!-- GENERICIZED: 12×{CLIENT}, 1×{RELATIONSHIP} | source: skills/software-development/rhythm-typing-game-framework/SKILL.md -->
---
name: rhythm-typing-game-framework
description: "Use when building/debugging a rhythm-typing browser game."
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [game, rhythm, canvas, keyboard, timing, debugging, {CLIENT}]
    related_skills: [deploy-artifact-verification, systematic-debugging, dogfood]
---

# Rhythm-Typing Game Framework

## When to Use

- Building or extending a rhythm-typing game ({CLIENT}) or any timing-based browser game combining keyboard input + canvas rendering + a beat/judgment clock.
- Debugging a rhythm/canvas game where hits register as misses, approach indicators drift from actual timing, animations crash the canvas, or state leaks across restarts.
- Designing input-driven practice/game tools where the input device itself must feel rewarding to press.

## The Architecture Model (proven pattern)

Three decoupled layers. Keep them separate or every bug becomes a coordination nightmare:

1. **Input** — `RawBus` (captures `keydown`/`keyup` with `performance.now()` timestamps AT the listener) → `NormalizedBus` (shift/caps/layout) → `BeatClockJudge` (compares key + timing against the beat-map).
2. **Feedback** — shared visual feel: SVG keyboard + stacked transparent canvas overlays (particles, approach rings) + combo display. Plugins don't render feel themselves.
3. **Game** — plugins consume judged events via a `GamePlugin` interface (`onHit`, `onMiss`, `onCombo`, `onNoteStale`, `onSongComplete`, ...).

**The "Correct Key + Timing Window" input model (osu!-style):** wrong keys are silently ignored by the judge (no combo break, no cursor advance — they only get a deliberately underwhelming visual "that's not it" so the kid isn't confused). Correct keys are judged on timing → Perfect/Great/Good. This aligns pedagogy (can't advance without the right key) with rhythm satisfaction (timing IS the score).

**Timing windows must scale to the audience.** osu!'s ±25ms Perfect is for expert rhythm gamers; a 7-year-old typing beginner needs ~±500ms Perfect / ±1000ms Good at easy difficulty. Make windows per-difficulty and generous at the low end, and let them tighten with difficulty. A too-tight window makes kids feel "I'm bad at this" — the opposite of the dopamine goal.

## The "Feel" Layer Is the Product

Visual feedback is NOT cosmetic — it's the bridge between "I typed the right key" and "I want to do it again." Key satisfying mechanics (inspired by ThreeUI / osu! / Stepmania):
- **Spring-physics key depression** — key goes past target depth then bounces back (CSS `cubic-bezier` overshoot), like a mechanical switch. Linear transitions feel dead.
- **Ripple emanation** — concentric rings expand across the keyboard surface from the keypress. Perfect = larger + a second white ring.
- **Specular highlight sweep** — a light streak across the surface on Perfect hits.
- **Combo escalation** — keyboard itself becomes the score display (aura at 10x, intensity shift at 25x, light show at 50x).
- **Approach rings** — notes shrink onto the target key as the beat approaches, giving anticipation (the "reading" skill that makes rhythm games addictive). Show 2-3 notes at once, color/opacity ramp by proximity.
- **Reduced-motion mode** must disable shake/heavy particles but keep gentle feedback (spring bounce).

## Recurring Class-Level Bugs (each burned a session)

### 1. Two-clock drift between render loop and judgment
The approach rings shrink on their own animation clock while the judge evaluates on its own start-time clock → rings drift ahead/behind the actual hits and feel wrong. **Fix: both MUST share one time source.** Ring position = `judge.getSongTime()`; the ring's `hitTime` = the note's absolute time; progress = `1 - (hitTime - songTime)/preemptTime`. Never maintain a second accumulating timer.

### 2. Timing delta computed against the wrong clock origin
`delta = evt.timestamp - note.time` fails when `evt.timestamp` is absolute `performance.now()` (billions of ms since load) but `note.time` is relative (0, 1500, 3000...). Every key reads as a miss. **Fix:** capture `startTime = performance.now()` at game start, call `judge.setStartTime(startTime)` BEFORE the bus starts listening, and compute `delta = (evt.timestamp - startTime) - note.time`. Set start time before wiring the bus, not after.

### 3. Canvas `arc` / gradient negative-radius crash (`IndexSizeError`)
A ripple spawned with a future `startTime` (e.g. `performance.now() + 80` for a delayed second ring) computes negative `progress` → negative radius → `ctx.arc` throws, and because it's in a `requestAnimationFrame` loop it spews uncaught errors every frame. **Fix:** clamp `const progress = Math.max(0, Math.min(1, elapsed / duration))` everywhere, and always remove expired effects in a cleanup pass before rendering.

### 4. Strict key comparison punishing capitals / caps lock
If the generator preserves case but the keyboard stores lowercase key ids, a pasted "Hello" generates a note for `H`, `getKeyElement('H')` finds nothing (no first-key ring), AND a capital typed by a school-taught kid or with caps-lock on fails the strict `evt.char !== expected.key` comparison → guaranteed miss on every letter. **Fix:** lowercase BOTH sides of the comparison (`evt.char.toLowerCase() !== expected.key.toLowerCase()`), lowercase key lookups, and map `" " → "space"` for the spacebar id. Do NOT flatten the user's displayed text.

### 5. DOM lifecycle leaks across restarts
Clicking Start repeatedly creates new judges/buses/SVG keyboards while the old ones stay attached. Old `keydown` listeners keep firing into orphaned judges → ghost MISS logs, stacked keyboards, stuck highlights. **Fix:** proper teardown BEFORE recreate: `rawBus.stop()` → `judge.detach()` → null the references → set `gameActive=false`; destroy/remove old DOM elements (not just reset styles); guard against double-start (`if (gameActive) return;`). Reuse one judge per game and null it in `endGame()`, not lazily in the next `startGame()`.

### 6. Ghost-note injection for first-key ring visibility (avoid)
When the first note sits at the lead-in offset, its ring may not spawn because `timeUntilHit > preemptTime` at t=0. A tempting temp fix is injecting a fake "ghost" character before the content — this breaks the user's text and they notice. **Correct fix:** set the lead-in offset equal to the difficulty's preempt time (`LEAD_IN_MS` per difficulty), so the first note's ring is on-screen from the moment Start is pressed.

### 7. Lifecycle of stats/overlay across game end
Final stats must persist after the song ends (player wants to read their score), so reset them in `startGame()`, not `endGame()`. Results overlay should offer both "Play Again" and "Change Setup" so the player can adjust content/BPM without a reload.

### 8. Round-completion check must read `isComplete` FRESH after `tick()`
In a word-per-round game, completion detection is a classic freeze: `onMiss` was a
completion path that no hook checked, so if the *last letter* was typed late (past
the window), `handleMiss` advanced the cursor to complete but nothing called
`nextRound()` → the game sat dead on a finished round. Two fixes converge it into
one place:
- **Put the completion check in the plugin's rAF tick loop, not per-hook.**
  `if (phase==="battle" && judge.state.isComplete && !done) nextRound()`.
- **Read `isComplete` AFTER calling `tick()`** — `tick()` mutates the cursor, so a
  pre-tick read is `false` and misses the stale-path completion. First drafts that
  captured `st` before tick had exactly this trap.
Any fixed-cadence autofight sim will miss this too — it types on an interval that
resolves notes via the stale path, never exercising the late-final-letter path. Use
irregular human-pace gaps or real keystrokes to reproduce it.

## Authoring a {CLIENT} plugin (the GamePlugin contract)

Plugins consume judged events via the `GamePlugin` interface and render their own scene on the canvas overlay ON TOP of the keyboard/rings. Key verified facts when building one ({CLIENT} is the first):

- **`onGameStart` / `onGameEnd` / `onSongComplete` are DEAD hooks.** They exist only in `types.ts` + the debug plugin; the judge never fires them. The plugin must **self-init on `createSession` return** and **self-detect completion** by polling `judge.state.isComplete` in its own rAF loop. Never design a plugin around those three hooks.
- **Live hooks that ARE fired:** `onHit(judgment, key, delta)` (Perfect/Great/Good), `onWrongKey` (combo-safe — this is the anti-frustration dodge hook), `onMiss`, `onNoteStale`, `onCombo(count, multiplier)`, `onComboBreak`, `onStreakThreshold` (fires at 10/25/50 combo).
- **`onWrongKey` is combo-safe** (no cursor advance, no combo break). Map it to a DEFENSIVE action (e.g. dodge) so a wrong key is a non-punishing play — never a damage/HP loss, or kids get kicked out of flow.
- **`onStreakThreshold` is wired** — charges an ultimate/capture meter. `onCombo(count, multiplier)` escalates battle momentum visuals (multiplier 1x/2x/4x/8x at 0/10/25/50).
- **Author against the BUNDLE surface, not the shipped `*.d.ts`.** The handoff `dist/*.d.ts` can be stale (Aug 23) and omit `onWrongKey` while the bundle (`dist/game.js`, Aug 28) has it. Grep the bundle; write plugin-local types. Flag upstream that `.d.ts` need regenerating.

### The input-routing gate: `openMenu()` / `closeMenu()` (LOAD-BEARING)
A battler (or any game with menu/selection moments) is not *only* typing. During menus, selection keystrokes must NOT reach the judge. The judge-sequencing that makes this safe is fragile and must live in exactly ONE named home — two plugin-owned methods — never repeated at call sites:

```
openMenu():   session.judge.detach()   // judge is the ONLY consumer of normBus → no key reaches timing
              hold tick (plugin owns tick cadence)
closeMenu():  judge.setStartTime(performance.now())  // re-baseline FIRST
              resume tick                             // then resume
              judge.attach(normBus)                   // attach LAST
```

**Exit order is load-bearing, all verified:**
- `getSongTime() = performance.now() - _startTime` and note times are absolute → a menu does NOT freeze song time. Skipping `setStartTime(now)` on exit makes the first correct key a guaranteed miss.
- `onChar` has an early-guard but NO late-guard → a correct key after the window closed routes to `handleMiss` (combo break + damage). Re-baseline closes it.
- Resuming `tick()` before re-baselining fires `onNoteStale` for EVERY expired note in a loop, each breaking combo — a 3s menu at BPM 40 = 2 enemy hits. Order: `setStartTime` → tick-resume → `attach` last.
- Menu UI is plugin-owned (option cards + its own keydown listener on `getContainer()`), NOT feedback-layer vocabulary — the rings/expected-key indicator are judge-driven and fight a static menu.

## Audio determinism — the beat source is a data contract, not a file

In a rhythm game, audio is NOT the decorative layer — it's the beat source the
entire judge runs on. This inverts the usual "is the music licensed?" question
into an architecture constraint:

- **The judge's note timing must derive from a track manifest** (canonical BPM +
  beat-grid + declared duration per file), never from whatever file happens to
  play. The judge reads the manifest, not the decoded audio. This keeps
  licensing and testability in the same document and makes a given song+tempo
  yield the same note map every run (the ±500ms windows and the re-baseline gate
  are otherwise untestable).
- **Decode determinism holds — measure it, don't assume VBR is a problem.**
  People claim `.ogg`/VBR decode drifts over a long round. Probe it with ffmpeg
  exact PCM sample count (decode to raw PCM, count samples, compare to container
  duration). Measured for real files: **±0.2ms over a 90s round** — 0.003% of a
  medium-difficulty window. Sub-millisecond error is noise; the track-manifest
  beat-grid is a safe timing source.
  - **Stereo gotcha:** an interleaved stereo file decodes to 2× the per-channel
    sample count (8.7M vs 4.4M for a 99.6s file). Divide by channel count before
    comparing against container duration, or the "drift" is 2× and looks real.
- **Hardware playback offset is the only real seam** (audio-context start latency
  vs wall clock, typically 10–100ms). It **cannot be measured headless** — only
  on real audio hardware (a Run button in the probe). Make the calibration
  **conditional on the measured result, not automatic**: if the offset is small
  vs the timing windows (±500ms easy / ±300ms medium), the wall-clock judge
  (`setStartTime(performance.now())` at battle start + the menu-exit re-baseline)
  is already inside margin and the audio-clock rebase is dead weight — cut it.
- **Browser autoplay policy is a wall for audio games.** Web Audio contexts are
  blocked until a user gesture on all modern browsers. If the session starts
  (`setStartTime(performance.now())`) before audio is running, the offset isn't
  10–100ms of device latency — it's however long the blocked context sat there,
  unbounded and unmeasurable. Structural fix: **the game starts on a user
  gesture** — a "Start Battle" button initializes the AudioContext (the gesture
  unblocks it) THEN creates the session, so the sync line measures real offset on
  a *running* context. The start screen doubles as the first feel moment, so give
  it the game's real visual language (sharp, not childish).
- **Design BPM ≠ musical tempo.** A track manifest's BPM is a *design* assignment
  within the engine's range ({CLIENT}: 20–120), not a claim about the file's real
  tempo. OGA/asset pages rarely state musical tempo — **measure it after pull**
  (onset autocorrelation / interval histogram) before assigning a design BPM; a
  measured value ~40% off a naive design BPM is a real failure, not noise. If a
  track's musical tempo exceeds the engine ceiling, it's either music-only (not
  grid material) or re-declare a lower design BPM — the grid derives from the
  manifest, so lowering costs zero re-pull. For kid combo-spectacle density,
  target 110–120 BPM (dense hits, sitting at the range ceiling).

## The reframe: "typing game with rhythm" — decouple the note grid from the music

A child's typing pace is variable; a rigid musical grid is not. The hard-won
lesson: when a plugin locks its note timing to a beat grid that runs hot (e.g. 120
BPM = 500ms/letter), a kid who pauses longer than a beat between letters gets every
pending note marked stale → the round auto-completes → the judge detaches → **input
goes genuinely dead mid-word**. A headless autofight sim typing on a fixed cadence
never hits this; real (slowed, irregular) typing does. This is the single clearest
"sim passed, real browser broke" miss in the class.

The stable answer is a **reframe, not a tweak**: judgment derives from a **word/note
grid at a comfortable pace (~1000ms/letter = 60 BPM grid), NOT the audio clock**.
Audio becomes mood/flavor, not the beat source. Consequences:
- The whole audio-clock calibration seam (drift-probe gating, hardware-offset
  calibration) is **deleted as dead weight** — judgment no longer depends on the
  playback clock at all. This supersedes the "conditional calibration" step above:
  the reframe cuts it entirely, whatever the measured offset.
- Approach rings at a self-consistent ~1000ms/letter carry the rhythm *feel*
  without musical sync. Copy should claim "typing with rhythm" (the child's own
  pace), never "notes on the beat" — or you overclaim.
- The manifest's remaining job is **note-grid determinism** (same word + same seed
  → same map every run, for ±window testing) — nothing about the music's clock.

### Real words with natural pauses (D + C)
When the task is meaningful typing practice, join dictionary words by spaces and
decide what the gap means BEFORE the child hits it:
- **D (word-boundary rounds) — primary:** each round is ONE word; the pause between
  words lives in the `openMenu()`/`closeMenu()` seam where the judge is detached —
  rest is genuinely free, no penalty possible. That's where a child's eyes leave
  the keyboard, so it's exactly where no penalty should exist.
- **C (soft-fail spaces) — mandatory safety net:** a mid-round trailing space still
  exists (child finishes a word, rests a beat longer than the window). Suppress HP
  drain + combo break when `note.key === ' '` in `onMiss`/`onNoteStale`. D makes
  the pause a feature, C makes it survivable — do both.
- **Spaces are NOT pauses by default** — `BeatMapGenerator` treats a space as a note
  at the same density as letters. Without D+C, the "breath" the design wants is a
  damage source.

### Battle stats + FX composition (single source of truth)
- **ONE plugin-owned stats source.** {CLIENT}'s internal `FeedbackLayer.stats` and a
  plugin's own counter are two independent objects that drift (a top-left 0 and a
  bottom 1 disagreed this session). Hide AND never read the framework's; keep one
  plugin-owned origin, or every stats feature (streak, capture %, accuracy) re-leaks
  the duplicate.
- **FX anchoring:** approach rings (anticipation) belong at the keyboard, converging
  on the key before the hit; hit sparks (reaction) belong at the monster where the
  attack lands. Anchor sparks to the monster {CLIENT}, keep rings on the keyboard —
  never stack both on the same pixels (rings-over-sparks = noise-on-noise; a
  detached particle cluster = sparks rendering at the wrong anchor).

## Borrowing open-source assets — the license audit gates what you reuse

When a game reuses open-source monster/battler assets as a launchpad (animations
are the genuinely hard part), do the license audit BEFORE pulling, per asset
class:

- **GPL engine code GPL-infects an MIT plugin** — a Godot/Pygame/C++ battler's
  *code* cannot be bundled into a {CLIENT} MIT plugin. Assets and design language
  are borrowable; engines are not (porting native engines to the browser is
  months of new bugs anyway).
- **CC-BY-SA assets** are reusable but force share-alike + attribution on
  derivatives. Ship a **machine-generated per-file manifest** (source repo +
  author + license + SHA-1 ledger) as the *only* provenance point the engine
  reads — it's the ship-time proof the island holds and makes count disputes
  verifiable.
- **One non-commercial artist contaminates the pack.** If a single asset is
  attributed to a non-commercial author (e.g. Oniwanbashu on DeviantArt), the
  whole pack goes non-commercial. Exclude that artist's files at pull time.
- **Compositions (`.ogg` tracks) are the highest IP risk** — likely remixes of
  recognizable tunes. Inspect each at pull, exclude on doubt.
- Verify the pull count against the manifest (the manifest is what makes an
  off-by-N count catchable, not eyeballing a file listing).

## Build Order (validate the contract before the game)
1. Build Input + Feedback layers first, not a polished game — the plugin contract is validated by a *minimal* consumer (a "debug plugin" that exercises every hook with a pulsing circle + progress bar), not by the first real game. This is "validate before abstract."
2. Write ONE integration test that drives `keydown → RawBus → NormalizedBus → BeatClockJudge → FeedbackLayer` and asserts a correctly-timed press is Perfect. This single test would catch almost every regression in this class (components can pass unit tests in isolation while the wiring between them is broken).

## Pitfalls
- Prefer an existing browser rhythm engine's patterns (osu!, Stepmania, Nitro Type) as *design reference* — do NOT try to port their C++/native engines to the browser. WebAssembly + input rewrite + render rewrite is months of new bugs, not a shortcut.
- Wrong keys should not be completely silent (kids think the keyboard broke) and not punishing (breaks flow) — a muted red shake/ripple reads as "not that one."
- First-key rings, spacebar rings, and stats persistence are the classic "final polish" bugs — check them explicitly before declaring MVP.

## Support Files
- `references/{CLIENT}` — the {CLIENT} incident record: each bug, its root cause, and the exact fix (timing clock, negative radius, case-insensitivity, DOM lifecycle, ghost note).
- `references/{CLIENT}` — verified contract facts for writing a {CLIENT} plugin: which hooks are live vs dead, bundle-vs-`.d.ts` staleness, and the full `openMenu()`/`closeMenu()` judge-routing gate rationale.
- `references/audio-determinism.md` — probe methodology + measured evidence for deriving judge note timing from a track-manifest beat-grid: ffmpeg PCM-count decode check, the stereo 2× gotcha, the hardware audio-offset seam, and the conditional-calibration decision.
- `references/game-shipping-license-deployment.md` — guardrails for taking a rhythm game public (repo + GH Pages): `.gitignore`-first so excluded/`ship:false` assets never enter git history (git is a permanent second distribution surface), the license-boundary file layout (root MIT + island CC-BY-SA + ledger visible to any visitor), the pre-push audit, and item-page-not-collection license verification for CC0 sourcing.
