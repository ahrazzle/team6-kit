<!-- GENERICIZED: 24×{CLIENT}, 3×{RELATIONSHIP} | source: skills/software-development/{CLIENT} -->
---
name: {CLIENT}
description: "Use when building or QA-testing {CLIENT} game plugins."
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [{CLIENT}, plugin, rhythm-game, game-dev, typescript, contract, qa]
---

# {CLIENT} Plugin Development

{CLIENT} is a browser TypeScript rhythm-typing framework (MIT): the player types text in time with a beat; the framework owns keyboard input, timing judgment, approach rings, particles, and stats. Games are built as plugins that consume judged events and render their own scene. Repo: `/Users/{RELATIONSHIP}/{CLIENT}{CLIENT}` (handoff docs in `docs/`: PLUGIN_GUIDE.md, API_REFERENCE.md, EXAMPLE_PLUGIN.md).

## When to Use

- Building or extending a {CLIENT} plugin game (current: {CLIENT}, workspace `/Users/{RELATIONSHIP}/{CLIENT}{CLIENT}`, IDEA.md is canonical scope).
- QA-testing a {CLIENT} plugin: the verified hook/clock facts below are the acceptance criteria — a plugin built on dead hooks fails review regardless of how it plays.
- Reviewing any claim about the {CLIENT} contract surface (verify against the bundle, see the pitfalls).
- Designing a rhythm-game feature that touches timing, menus, or audio.

## Entry point

```typescript
const session = createSession({
  container: stage,
  content: 'hello world',   // each char = one note; frozen at creation
  bpm: 60,                  // framework range 20–120 (user directive)
  difficulty: 'easy',       // easy | medium | hard | expert
  hooks: myPlugin,          // Partial<GamePlugin>
});
session.destroy();          // full teardown; safe between rounds
```

One `createSession` = one typing round. Game state that spans rounds (HP, XP, progression) lives OUTSIDE the session, in plugin-owned state.

## VERIFIED contract facts (source-verified {CLIENT}, high confidence)

### Live hooks (fired by the judge)
`onWrongKey(key, expectedKey)` — combo-safe dodge, no cursor advance
`onHit(judgment, key, delta)` — judgment ∈ perfect|great|good
`onMiss(key, expectedKey, delta)` — correct key, wrong time; breaks combo
`onNoteStale(note)` — note expired; breaks combo (fires ONLY if plugin calls `judge.tick()` — the framework never does)
`onCombo(count, multiplier)`, `onComboBreak(previousCount)`, `onStreakThreshold(count)` — combo thresholds default 10/25/50

### DEAD hooks (declared, never invoked — verified by grep)
`onGameStart`, `onGameEnd`, `onSongComplete` — exist in types + debug-plugin only; nothing calls them.
→ Plugin self-inits on `createSession()` return; self-detects completion by polling `judge.state.isComplete` in its own rAF loop. Mid-session `destroy()` never fires completion hooks.

### Author against the bundle, not the .d.ts
Shipped `dist/*.d.ts` were stale (Aug 23) vs `dist/game.js` bundle (Aug 28). Verify symbols by grepping the built bundle; keep plugin-local types.

## Judge clock semantics (critical)

- `getSongTime() = performance.now() - _startTime` — song time NEVER freezes during a pause.
- Early guard exists (too-early correct key → silent return); NO late guard (correct key after window → miss + combo break).
- Wrong keys are judge-silent: no cursor advance, no combo break, only onWrongKey fires.
- `tick()` is plugin-owned; resuming it after a pause fires onNoteStale for every expired note in a loop (each breaks combo).

### Menu gate pattern (encapsulate as named methods)
- `openMenu()`: `judge.detach()` + stop tick + own keydown listener on the canvas container (menus are plugin UI — the feedback layer's rings are judge-driven and die on detach).
- `closeMenu()`: `judge.setStartTime(performance.now())` → resume tick → `attach()` LAST. Re-baseline first, attach last.

## Word content & pacing (kids)

- **Spaces are judged notes, not pauses.** `BeatMapGenerator` never skips spaces (source-line 120), and every note including the space lands at uniform `LEAD_IN + i*beatInterval` spacing — rhythmically identical to a letter. A word boundary does NOT produce a longer rest, and a child's natural rest (>1s) at a boundary turns the space note stale/missed → combo break + damage. The "breathe between words" the user wants is a damage source unless designed around.
  - Pattern D (primary): one word per round; the pause lives in the `openMenu()`/`closeMenu()` seam where the judge is detached — genuinely free rest, next word starts on a fresh choice.
  - Pattern C (safety net): soft-fail spaces in `onMiss`/`onNoteStale` — `if (note.key === ' ') return;` — no HP drain, no combo break.
- **Beat grid must fit child typing pace, not the music.** At 120 BPM (500ms/letter), any pause >1s makes `tick()` stale every pending note → the round auto-completes → the judge detaches into the menu → **input genuinely dies mid-word**. Comfortable child grid ≈ 60 BPM (1000ms/letter), decoupled from the music BPM (music-as-mood). If notes stop landing on musical beats, reframe the product claim honestly: "typing game with rhythm" (self-consistent pacing) is not "rhythm game" (musical sync) — and the reframe deletes the audio-clock calibration machinery for free.
- Randomize per-battle word order with a seed (deterministic per session, varied across battles). Meaningful typing needs real words, not keyboard-row gibberish — keep a curated grade-school word list (3–6 letters).

## Round completion (the stall-bug class)

Completion fires in NO hook — poll `judge.state.isComplete` in YOUR rAF loop, and read it FRESH **after** calling `tick()` (tick mutates the cursor, so a pre-tick `isComplete` is false and the stale-path completion is invisible). Converge completion in that one loop; do NOT scatter `isComplete → nextRound()` checks across hooks. The failure mode proven this session: completion checked in `onHit` and `onNoteStale` but not `onMiss` — a late final letter (past the easy ±1000ms window) still advances the cursor to complete via `handleMiss`, and with no check in `onMiss` and the tick-loop guard now false, the game freezes on a finished round. A 7–10yo resting mid-word is the natural trigger, not a corner case.

## Framework defaults (verified from source)

- Timing windows (ms): easy 500/700/1000, medium 300/500/700, hard 150/300/500, expert 80/150/250 (perfect/great/good).
- Lead-in: easy 1500ms → expert 350ms (matched to ring preempt).
- Combo multiplier: 0–9 →1x, 10–24 →2x, 25–49 →4x, 50+ →8x.
- Ranking: S≥95%, A≥85%, B≥70%, C≥55%, D≥40%, else F.
- `FeedbackLayer` surface: getCanvasOverlay() (plugin draws battle scene ON TOP of keyboard/rings), getContainer(), setHighContrast, setReducedMotion, announce(), resetStats(), getRanking().
- Case-insensitive judging; spaces are valid notes (spacebar).

## Audio ({CLIENT} state: music-as-mood)

{CLIENT} decoupled the note grid from the music clock after the input-dead bug (see Word content & pacing). When judgment derives from the word grid and NOT the playback clock, the whole audio-clock-calibration seam is dead weight — drop it. Do not resurrect the "anchor judge to audio clock" pattern; it was built, measured, and deleted.

- Decode drift does NOT exist for the tested files: ffmpeg decode vs container duration matched ±0.2ms over a 90s round. Do not block on it.
- The track manifest still matters, for two independent reasons: (a) note-grid determinism — same word + same seed → same map, which is what keeps the ±window tests stable; (b) licensing/provenance.
- Music provenance is the real risk class, not timing. Prefer CC0 with a named author (OpenGameArt, Tuxemon's clean CC0 sets). The OpMon `.ogg` trio was killed for unfillable CC-BY-SA attribution: composer identity died in a git squash, zero metadata tags, and files named like Pokémon tracks. Rule: exclude-on-doubt; never ship a track whose author you cannot name.
- Autoplay policy is the load-bearing sync gate: an `AudioContext` is blocked until a user gesture. If the session starts while audio is blocked, the start-offset is unbounded and unmeasurable. Start the game ON a user gesture (a Start button that initializes the context) so the context is running before `setStartTime`. This also gives the game its first feel moment.

Only if a future game re-anchors notes to the music clock does the old advice return: derive the beat-grid from a manifest, probe drift per file, and calibrate on real devices with a running context.

## Asset licensing ({CLIENT} policy)

- Engine stays MIT. CC-BY-SA assets (OpMon-Data: 45 monsters × 2 frames + 18 type icons) ship ONLY as a distinct island: `assets/ccbysa/` + per-file attribution manifest + build-time assertion that paid/original monsters never reference that namespace.
- GPL engines (OpMon/Godot, Tuxemon/Pygame) do NOT transfer to a TS plugin — reuse is reference-only (grammar, archetypes, balance), never code.
- Tuxemon media: exclude everything by artist Oniwanbashu (CC-BY-NC-SA traps) at pull time.
- Motion is synthesized, not borrowed: upstream ships poses, not animation frames.

## {CLIENT} QA gate ({CLIENT} taxonomy vote — pending)

Monster readability vote is grounded in pixel data, not vibes: opaque ratio + alpha bbox from a minimal PNG parse (struct+zlib, no PIL). Thresholds at battle scale (100×100): <5% opaque = exclude/rescale, 5–8% = suspect noise, dark-but-dense = contrast-boost not exclusion; bbox geometry refutes archetype labels (serpent bucket was a dumping ground); the demo page must agree with itself before the vote runs. Full technique + measured table: `adversarial-review` skill, attack vector 7, `references/session-20260828-{CLIENT}-qa.md`. Note: `vision_analyze` 404s on paths with spaces — copy to /tmp first.

## Testing

Pure-TS state machine is unit-testable via `RawBus.inject(key, code, type, timestamp?)`; judge logic runs headless. Never test plugin timing logic against real timers.

Headless autofight sims are NOT acceptance: a fixed-cadence sim resolves rounds via the stale path (it types through note windows) and never exercises a late-final-letter miss or real slowed child typing. It passed while a real browser froze (twice this project). When you sim: model irregular human gaps (700–1200ms), and treat the served page with real keystrokes as the acceptance gate — a sim pass is a hint, not a result. Report honestly when verification was sim-only.

## Pitfalls

- Don't build "new framework surface" — verify first what already exists (see `adversarial-review` skill, attack vector 6).
- Don't call `feedback.start()` before `setJudge()` — the facade exists to prevent this; use createSession.
- Don't forget `session.destroy()` between rounds — keyboard DOM and listeners stack.
- Don't let menus leak keystrokes into the judge — detach is required, not optional.
- {CLIENT} renders its OWN top-left stats overlay from `FeedbackLayer.stats`. Adding a plugin judgment counter without hiding the built-in produces a desynced duplicate (0 vs N Perfect). Hide the built-in (`hide{CLIENT}Stats()` after each session); keep one stats source of truth.
- There are TWO timing-window tables: `beatmap-generator.ts`'s internal one (the per-note `window` field, easy 500 across all tiers is NOT the judge's) and `types.ts` `TIMING_WINDOWS` (the judge's real windows: easy 500/700/1000). Judge uses the types.ts table.
- Enemy assets: distinctness from the player is only half the gate — verify legibility crispness at battle scale too. Pick the enemy by silhouette contrast with the player (tall biped column vs small round reads as "big foe"; same-size blue-vs-purple humanoids do not), and re-check the swapped {CLIENT} renders crisp, not blurry.
- GH Pages / subpath demos: an absolute fetch (`fetch("/x.json")` or `src="/"+{CLIENT}`) works on the local dev server and 404s on `<user>.github.io/<repo>/` — keep every asset path relative to the page. Verify the LIVE-served fetch, not just the local page.
