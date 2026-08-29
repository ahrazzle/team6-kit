<!-- GENERICIZED: 7×{CLIENT}, 2×{RELATIONSHIP} | source: skills/software-development/rhythm-game-development/SKILL.md -->
---
name: rhythm-game-development
description: Use when building rhythm/typing games or beat-driven feel.
version: 1.0.0
author: {RELATIONSHIP} ({RELATIONSHIP}), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [rhythm-game, typing-game, game-feel, timing, beat-map, feedback, kids]
    related_skills: [integration-testing, static-site-production, test-driven-development]
---

# Rhythm Game Development

Class-level discipline for building rhythm games and rhythm-typing games (the Guitar Hero / DDR / osu! / Stepmania family). Developed and proven while building the {CLIENT} kids' typing-rhythm framework.

## When to Use

- Building a typing game, rhythm game, or educational game where input timing is scored
- Designing game-feel feedback (keyboard/keycap animation, particles, celebration sequences)
- Choosing an input model for "type to the beat" gameplay
- Adding difficulty tiers, scoring, ranks, or end-of-game metrics

## The Input Model Fork (decide BEFORE building anything)

Rhythm games differ on what happens when the player presses a wrong key. Everything downstream branches on this:

| Model | Wrong key behavior | Used by | Risk |
|---|---|---|---|
| **Advance-on-wrong** | Wrong key still advances the beat | Guitar Hero | Kids mash keys; accuracy collapses |
| **Block-on-wrong** | Can't advance until correct key | Traditional typing | Rhythm flow stutters, satisfaction dies |
| **Correct-key + timing window (RECOMMENDED)** | Wrong key is SILENTLY IGNORED (no judgment, no cursor advance, no combo break). Correct key judged on timing only | osu! | None — this is the synthesis |

**The osu!-style model** (recommended for typing games): wrong keys are invisible to the judge. The player literally cannot advance without the correct key (pedagogy holds), the beat never stops (flow holds), and timing still matters (a correct key pressed off-beat scores worse than one on-beat). Mashing becomes self-defeating because timing collapses the score.

## Content Fidelity — THE sacred rule in typing games

**The user's typed content is the contract. Difficulty modifies timing and density, NEVER the content itself.**

Recurring bug classes (all observed live):

1. **Never reorder characters** — a "hand-alternation shuffle" that swaps keys between positions destroys the user's text (`abcdef123456` → `a1c2e3b4fd56`). Character order is sacred. Hand comfort is a *generation-time* constraint (choose words), not a post-hoc reorder.
2. **Never drop spaces** — a density filter that skips spaces on some difficulty silently turns `is this my content` into `isthismycontent`. Spaces are user content.
3. **Never duplicate letters unboundedly** — "double common letters on hard" is fine, but implement it by iterating over the ORIGINAL length and appending; splicing into the array mid-loop re-processes inserted notes → **exponential duplication** (`is this` → `iiss tthiiss...`).
4. **Normalize case at generation, not at lookup** — content keys and keyboard lookups must agree on case. Keyboard layouts key their SVG elements by lowercase ids (`h`, `a`), and the judge's normalizer emits lowercase. If the generator preserves the user's original case (`Hello` → note `H`), three things break at once: the approach ring calls `getKeyElement('H')` and finds nothing (no ring spawns), the expected-key indicator can't find the key either, and the judge compares pressed `h` against expected `H` → **the note can never be hit**. Fix at BOTH ends: lowercase content at generation (`chars[i].toLowerCase()`) and lowercase at every key-id lookup (`keyId.toLowerCase()`, keeping the space→'space' mapping). Symptom signature: default lowercase content works fine; pasted/custom text with any capital fails on the first (or every uppercase) key.

```typescript
// WRONG — splice inside the loop re-processes inserted notes (exponential)
for (let i = 0; i < notes.length; i++) {
  if (COMMON.has(notes[i].key)) {
    notes.splice(i + 1, 0, doubled); // now the loop sees the doubled note too
  }
}

// RIGHT — iterate the original length, append, then sort by time
const originalLength = notes.length;
for (let i = 0; i < originalLength; i++) {
  if (COMMON.has(notes[i].key)) notes.push(doubled);
}
notes.sort((a, b) => a.time - b.time);
```

Regression guard: a test asserting `notes.map(n => n.key).join('')` equals the input (minus intentional additions), plus a max-length bound on doubled notes.

**Final resolution for typing games: remove note doubling entirely.** Doubling "common letters" on hard was eventually removed in the {CLIENT} build — difficulty should modify timing windows and lead-in ONLY, never add or remove content. The user reads the feed and expects exactly what they typed. If a rhythm-games-only mechanic (doubled notes, chords) is wanted, gate it behind an explicit game-mode toggle, not a difficulty tier.

## Word-Boundary Pauses: spaces are not pauses

Splitting content into dictionary words joined by spaces does NOT create a pause. The generator emits a space as a note at the SAME density as letters (uniform `i * beatInterval` spacing) — rhythmically identical to another letter, no breath. Worse, a real pause is PUNISHED: the child finishes "cat", rests 1.5s, and the space note's window closes → `onMiss`/stale → combo break + damage. The natural breathing the user asked for becomes a damage source. (Also: words must come from a shuffled real-word pool, never a repeated `asdfjkl` key sequence — repeated key runs destroy the meaningful-practice value.)

Make the pause read as REST, not risk (proven on {CLIENT}):

- **(D) Word-boundary rounds:** each round = one word (or pair). When the word's notes resolve, return to the menu seam (`openMenu()`/`closeMenu()` — judge detached, tick held) where the pause is genuinely free and unpenalizable; the next word starts on a fresh choice. This is the honest fix — the pause lives where the judge cannot touch it.
- **(C) Soft-fail spaces:** safety net for the intra-round trailing space — in `onMiss`/`onNoteStale`, suppress HP drain + combo break when `note.key === ' '`. Under D the seam covers between-rounds; C covers the trailing space before the next letter. Both are plugin-side, zero framework surface.

## Difficulty Design

- **Timing windows** scale per difficulty, NOT content. Recommended kid-friendly windows (ms, ±):
  - easy 500, medium 300, hard 150, expert 80 (generous for young learners; tighten for mastery)
  - A tight "perfect" window at high levels is what makes mastery feel real; generous at low levels is what keeps kids from quitting.
- **Lead-in = preempt time per difficulty.** The first note must sit exactly one preempt-window away from game start, or the first approach ring never renders. Set `LEAD_IN_MS` per difficulty to match the approach-ring preempt (easy 1500, medium 1000, hard 600, expert 350). Do NOT fix a missing first ring by injecting a "ghost note" — that pollutes the visible feed; fix the lead-in.
- **Note density is independent of BPM** — two separate difficulty axes. Beginner: sparse notes at low BPM. Expert: dense notes at high BPM. BPM→WPM mapping: at 1 note/beat and 5 chars/word, WPM = BPM/5 (60 BPM ≈ 12 WPM).
- **No hard fail for young kids** — scene dims/goes quiet until recovery. Rock-meter fail state is a competitive-mode option.

## Approach Rings (osu!/Stepmania-style anticipation)

- Show 2–3 upcoming notes simultaneously at different shrink stages — single-highlight is a flashcard, not a rhythm game.
- Ring scale formula must start ABOVE 1x: `scale = 1 + (timeUntilHit / preemptTime) * 2` starts at 3x and collapses onto the keycap. `scale = timeUntilHit / preemptTime` starts at 1.0 = invisible.
- Color ramp by proximity (white → cyan → green → yellow), opacity ramp (30% → 100%).
- **Collapse rings on the judgment frame, not on note.time** — otherwise a hit that lands early leaves the ring drifting ahead of the feed, and the two look desynced even though they share one clock. `markJudged(note)` on hit/miss/stale.
- Lane lines (dashed vertical connectors) add the Stepmania reading feel.

## Game-Feel / Dopamine Layer

- **Spring-physics key depression** with overshoot (`cubic-bezier(0.34, 1.56, 0.64, 1)`, key dips past target then bounces back) reads as a mechanical switch — "alive," not "moving."
- **Ripple emanation** across the surface on every press (perfect = big vivid ripple, wrong key = tiny muted red ripple). This is the single highest-dopamine cheap effect.
- **Specular highlight sweep** and confetti on perfect hits only. `canvas-confetti` (6kB, ISC, zero deps) is the go-to open-source celebration lib.
- Celebrate song completion: results overlay + confetti. Never freeze on the last note — the game ending with rings stuck mid-air is a bug, not a finish.
- Respect `prefers-reduced-motion` / a reduced-motion toggle: kill shake/particles, keep the spring (subtle state signal).

## Metrics & Ranks

- Accuracy per key from timing band: Perfect 100%, Great 75%, Good 50%, Miss 0% → final = weighted average.
- Letter rank from accuracy: S ≥95%, A ≥85%, B ≥70%, C ≥55%, D ≥40%, F below.
- Persist final stats on screen after game over until the next game starts — reset on START, not on END, or players never get to read their numbers.
- **Color-code the completed-keys feed by judgment**, not a single "hit" color — each typed character should show its own band color (perfect cyan / great green / good yellow / miss red), matching the stats display. It turns the feed into per-key feedback.

## Copy truthfulness (kids-facing text)

- Say what the product IS. A game with no audio/song must say "Round Complete!", not "Song Complete!" — borrowed rhythm-game copy reads as broken.
- When behavior changes, copy must change with it. The old "wrong keys are silently ignored" line stayed on screen long after the framework started rendering wrong-key feedback — stale copy describing removed behavior is a bug.

## Pause / Menu States (the input-routing gate)

A rhythm game is not always judging. Menu moments (choose attack, switch character, confirm, pause) must NOT route keystrokes into the timing judge — a selection keystroke that matches the expected key would be judged, and wrong ones leak into gameplay semantics. The gate is a plugin/consumer-side composition, not a framework extension:

- **Menu-enter:** `judge.detach()` (the judge is the ONLY consumer of the normalized bus — detaching it silences every keystroke), hold the plugin's own `tick()` calls, and attach a plugin-owned keydown listener for selection. Wrong keys are already judge-silent; detach closes the one real leak (a menu key that matches the expected note).
- **Menu-exit order is load-bearing:** `judge.setStartTime(performance.now())` → resume `tick()` → `judge.attach(normBus)` LAST. Song time never freezes (`getSongTime()` = `now - startTime`; note times are absolute), and `onChar` typically has an early-guard but NO late-guard — so without re-baselining, the first correct key after resume is a guaranteed miss, and the first resumed tick fires EVERY expired note as a combo-breaking stale (a 3s menu at BPM 40 ≈ 2 enemy hits). Re-baseline first, attach last.
- **Fold the fragile sequence into two named plugin methods** (`openMenu()` / `closeMenu()`) so the order-sensitive dance has exactly one home to patch and is testable in isolation — never repeat the 3-step ritual at call sites.
- **Dead-hook trap:** a framework may declare lifecycle hooks (`onSongComplete`, `onGameStart`, `onGameEnd`) in its types AND implement them in a debug plugin while the judge/core NEVER invokes them. Grep for the invocation site (a single match in types.ts doesn't count). If dead, the plugin must self-init on session creation and self-detect round completion (e.g., poll `judge.state.isComplete` in its own rAF loop) — and resolve on mid-session destroy too. This was the {CLIENT} contract's biggest near-miss: the battle-resolve mapping sat on a hook that never fires. **Self-detection must converge on ONE check in the tick loop, read AFTER `tick()` runs** — tick mutates the cursor, so a pre-tick `isComplete` read is stale and misses the stale-path completion. Duplicating the check across `onHit`/`onNoteStale`/`onMiss` misses paths: a late final letter resolves via `onMiss`, and if that hook lacks the completion check, the round finishes and the game sits dead — a child resting mid-word hit this within minutes, and a fixed-cadence sim never saw it.

## Audio / Beat Source & Determinism

- **Audience decides whether audio is the beat source or mood.** For competent rhythm players, audio IS the beat source the judge runs on — note timing derives from the track manifest, and the "borrowed vs original" decision is an architecture question first. For YOUNG CHILDREN / novice typists the rule inverts: a rigid musical grid fights a child's variable typing pace and CAUSES dead-input bugs (a beat-locked grid + a child pausing >1s between letters → every pending note goes stale → input dies mid-word). The proven fix is to decouple: the note grid derives from a comfortable typing pace (~1000ms/letter), the music plays as mood at its own BPM, and the product reframes from "rhythm game" to **"typing game with rhythm"** — the rhythm that matters is the child's self-consistent pacing, not musical sync. This DELETES the audio-clock calibration seam: judgment no longer depends on the audio clock at all, and the manifest only carries note-grid determinism (same word + seed → same map). Say the reframe out loud — resolve-screen copy like "your rhythm tamed the beast" means the child's pace, not the music's.
- **When audio IS the beat source, it must be session-deterministic.** The "borrowed vs original audio" decision is an architecture question first, a licensing question second — whichever way it lands, the same song at the same BPM must yield the same note map every run, or the timing windows and any re-baseline gate become untestable.
- **Note timing derives from a track manifest, never audio playback position.** Ship a track manifest with a canonical BPM + beat-grid per file (same shape as the asset manifest). The judge's note timing comes from the manifest; the file only has to play. This keeps the licensing question and the determinism question in the SAME document — the last coupling seam before a build owns all its inputs.
- **Probe audio-clock drift before committing to audio-driven sync.** Measure `audioContext.currentTime` vs `performance.now()` over a full battle-length loop (2–3 min). If they diverge meaningfully, sync the judge to the manifest clock, not the audio clock. Procedure + measured results + ffmpeg verification: `references/audio-sync-track-manifest.md`.
- **Decode drift is dead — verify once, calibrate conditionally.** Measured: VBR `.ogg` decode matches container duration to ±0.2ms over a 90s battle (0.003% of a medium beat window). The only remaining offset is one-time audio-context latency (10–100ms) against ±300–500ms windows — make the real-hardware calibration CONDITIONAL on its probe result, not automatic. When the offset is small, `setStartTime(performance.now())` at battle start + menu-exit re-baseline is the ENTIRE sync story.
- **Browser autoplay policy makes the offset UNBOUNDED without a user gesture.** Web Audio contexts are blocked until a gesture on all modern browsers; if the session starts (`setStartTime(performance.now())`) before audio is running, the audio clock can lag the wall clock by SECONDS — not the 10–100ms the probe measures, and unmeasurable headlessly. Structural fix: the session starts ON a user gesture — a "Start Battle" button initializes the AudioContext (gesture unblocks it), THEN creates the session. The start screen doubles as the first feel moment, so it carries the game's visual language, not a bare button. Cheap, testable, and it makes the probe's measured offset real.
- **Design-BPM ceiling is one manifest edit away.** When the design BPM sits exactly at the framework's ceiling ({CLIENT}: 120), re-declaring `bpm: 110` later costs zero re-pull — the grid derives from the manifest, never the file. Ship at the exciting value; the escape hatch is a one-line manifest change.
- **Design BPM ≠ musical tempo.** A manifest BPM may be a design assignment (valid within range) that is not the song's musical tempo — mark `tempoVerified: false` so it reads honestly. Design BPM drives attack-cadence feel: 90 BPM ≈ 1.5 notes/sec at 5 chars/word reads leisurely; "exciting" combo spectacle wants 110+. Vet flags (`vet: pending-ears`) are structural: the build treats unvetted tracks as exclude-on-doubt by default.
- **Verify decode determinism headlessly with ffmpeg** (browser `decodeAudioData` needs an audio device): raw s16le decode → bytes/2 = samples; STEREO interleaved = 2× per-channel — divide by channel count before comparing durations.
- **Borrowed audio carries the highest IP-remix risk of any asset class** (compositions, not sprites) — "inspect at pull, exclude on doubt." Mark test material UNVETTED and keep it out of ship paths. Island/ledger rules for borrowing assets: see `open-source-reuse-licensing` skill.

## Lifecycle / Restart Hygiene

- Games with start→play→end→restart cycles accumulate DOM and orphaned listeners. `reset()` clears styles; **`destroy()` removes DOM + cancels animation loops + detaches listeners** is required before creating a new instance.
- Teardown order matters: stop bus → null references → destroy DOM → set inactive. Wrong order = orphaned events from the previous game firing into the new one.
- Temp workarounds must be tracked and deleted the moment the real fix lands.

## Verifying

- Unit tests per component (bus, generator, judge) plus ONE full-pipeline integration test (input → judgment → DOM) — see `integration-testing` skill.
- After deploying, verify the SERVED bundle contains the new method before telling anyone it's fixed (see `static-site-production` skill).

## References

- `references/{CLIENT}` — Concrete timing/preempt tables and live bug post-mortems from the {CLIENT} build.
- `references/audio-sync-track-manifest.md` — Audio determinism: track-manifest rule, Web Audio drift probe procedure, and the "documented probe never built" gap lesson.
