<!-- GENERICIZED: 6×{CLIENT}, 1×{RELATIONSHIP} | source: skills/adversarial-review/references/session-20260828-{CLIENT} -->
# Session {CLIENT} — {CLIENT} contract verification

{CLIENT} = first plugin game for the {CLIENT} rhythm-typing framework (MIT, browser TS, esbuild → `dist/game.js`). Team proposed designing a "new plugin contract" for battle states. Before locking scope, verified the claimed surface against the actual source. All findings source/bundle-verified, high confidence.

## Findings that changed the design

### 1. Dead hooks (lifecycle)
`onGameStart` / `onGameEnd` / `onSongComplete` exist in `types.ts` (interface) and `debug-plugin.ts` (implementation) — but NOTHING invokes them. Grep across src: only onWrongKey, onHit, onCombo, onMiss, onComboBreak, onNoteStale, onStreakThreshold are fired by the judge. Consequence: a contract built on "onSongComplete = battle resolve" sits on a hook that never fires. Plugin must self-init on `createSession()` return and self-detect round completion via `judge.state.isComplete` (poll in its own rAF loop). Mid-session `destroy()` never fires completion hooks — plugin resolves battles itself, always.

### 2. Stale shipped declarations
`dist/game.js` bundle (Aug 28) is newer than standalone `dist/BeatClockJudge.js` + `dist/types.d.ts` (Aug 23). The `.d.ts` describes an older judge (missing onWrongKey). Author against the bundle surface with plugin-local types; flag upstream that handoff `.d.ts` need regenerating.

### 3. Judge clock semantics (the menu gate)
- `getSongTime() = performance.now() - _startTime` (BeatClockJudge.ts). Song time NEVER freezes during a pause; note times are absolute from `setStartTime`.
- `onChar` has an EARLY guard (too-early correct key → silent return) but NO LATE guard: a correct key after the window closes → `handleMiss` → combo break + enemy attack.
- `tick()` (stale detection) is never called by the framework — the plugin owns the tick cadence. Resuming tick after a pause fires `onNoteStale` for EVERY expired note in a loop, each breaking combo (e.g. 3s menu at BPM 40 ≈ 2 enemy hits).
- The pause must therefore be an encapsulated pair, not a ritual:
  - `openMenu()`: `judge.detach()` + stop tick + plugin-owned key listener (menus are plugin canvas UI, not feedback-layer vocabulary).
  - `closeMenu()`: `judge.setStartTime(performance.now())` → resume tick → `attach()` LAST. Re-baseline before tick-resume, attach last.
- Verified against source: `attach`/`detach` are public (BeatClockJudge.ts:160-168); `setStartTime`/`getSongTime` public; wrong keys are judge-silent (no cursor advance, no combo break — only onWrongKey fires).

### 4. Count verification
"171 battle-ready {CLIENT} entries" (OpMon-Data) was a directory-ENTRY count (includes `.import` Godot metadata). Actual PNG count: 85 = 45 monsters × 2 frames (poses, NOT animation cycles). No per-monster attack frames exist in the repo — all motion must be synthesized. Load-bearing inventory claims get file-level verification (count actual files by extension), not listing summaries.

### 5. Audio determinism (rhythm games)
- Judge note timing must derive from a track manifest (canonical BPM + beat-grid per file), never from decoded audio.
- Judge start must anchor to the audio clock (playback start), not the wall clock: VBR/compressed `.ogg` decoding drifts ms over a 90s round; audio-context resume latency adds a per-device offset. At easy windows (±500ms) it's noise; at medium (300/500/700) + BPM ramp it compounds.

### 6. License island pattern (OSS asset reuse)
- GPL engines (OpMon=Godot/GDScript, Tuxemon=Python/Pygame) cannot be bundled into an MIT plugin — adopting one is a rewrite, not a launchpad.
- CC-BY-SA assets CAN ship beside MIT code ONLY as a distinct asset layer: own directory (`assets/ccbysa/`), per-file attribution manifest, and a hard BUILD assertion that paid/original monsters resolve to zero `ccbysa/` references. "Own directory + LICENSE" is necessary but not sufficient; the assertion is what makes the island hold at ship time.
- Tuxemon media is a per-file mosaic: 12 CC-BY-NC-SA assets are commercially dead — all by one artist (Oniwanbashu, in ATTRIBUTIONS.md). Exclude by artist name at pull time.
- Reference-only mining: {CLIENT}/animation GRAMMAR, type-chart balance — never species data (Pokémon Showdown is MIT but its data is Game Freak IP).

## Verdicts landed
- Scope locked with dead-hook corrections (results self-detection, not onSongComplete).
- Menu gate locked as `openMenu()`/`closeMenu()` with re-baseline ordering ({RELATIONSHIP}'s folding, accepted).
- "No new framework surface" held: everything is plugin-side composition via existing public APIs.
