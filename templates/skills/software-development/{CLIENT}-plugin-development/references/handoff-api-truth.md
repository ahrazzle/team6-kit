<!-- GENERICIZED: 1×{CLIENT} | source: skills/software-development/{CLIENT} -->
# {CLIENT} handoff API truth (verified against dist/game.js, Aug 2026)

Verified by grepping the canonical bundle (not the stale `.d.ts`). The shipped
`dist/types.d.ts` / `dist/BeatClockJudge.js` (Aug 23) describe an OLDER judge and
are missing `onWrongKey`; the bundle (Aug 28) is the source of truth.

## PluginHooks (what actually fires)
| Hook | Wired? | Notes |
|---|---|---|
| `onHit(event)` | YES | `event = { judgment, key, delta, note, timestamp }`; judgment in perfect/great/good |
| `onMiss(key, expectedKey, delta, expected?)` | YES | correct key, wrong time; breaks combo |
| `onWrongKey(char, expectedKey)` | YES | wrong key — silent to judge, combo-safe; use as DODGE |
| `onNoteStale(note)` | YES | only if the PLUGIN calls `judge.tick()` (framework never does) |
| `onCombo(count, multiplier)` | YES | fires after every hit/miss/stale |
| `onComboBreak(prevCount)` | YES | |
| `onStreakThreshold(count)` | YES | via `checkStreakThreshold()` at combo 10 (subtle) / 25 (moderate) / 50 (intense), once per threshold |
| `onGameStart` / `onGameEnd` / `onSongComplete` | DEAD | exist only in types + DebugPlugin; the judge never calls them. Plugin self-inits on `createSession` return and detects completion via `judge.state.isComplete` |

## Judge surface (bundle)
- `attach(normBus)` / `detach()` — judge is the only consumer of the normalized bus; detach = no keystroke reaches timing judgment.
- `setStartTime(performance.now())` — re-baseline (required after menu-exit, and when audio actually starts).
- `getSongTime()` = `performance.now() - _startTime`.
- `tick()` — NEVER called by the framework; plugin owns the cadence. Fires `onNoteStale` for every expired note (each breaks combo) — stop it during menus.
- `onChar` guards: early (correct key before window → silent return) YES; late (correct key after window → `handleMiss`) NO.
- `state = { combo, maxCombo, multiplier, cursor, isComplete }`; `getExpectedNote()`, `getNextNotes(count)`, `getNotes()`.
- `reset()` for replays.

## Timing windows + lead-in (bundle constants)
- `TIMING_WINDOWS`: easy 500/700/1000 · medium 300/500/700 · hard 150/300/500 · expert 80/150/250 (perfect/great/good).
- `LEAD_IN_MS`: easy 1500 · medium 1000 · hard 600 · expert 350.
- BeatMapGenerator: note i at `LEAD_IN + i * (60000/bpm)`; `wordsPerMinute*5` overrides bpm.

## createSession return
`{ judge, feedback, beatMap, rawBus, normBus, songTime(), destroy() }`
- `feedback.getCanvasOverlay()` → battle canvas (draw monsters/HP/FX on top of keyboard+rings).
- `feedback.getContainer()` → plugin-owned UI surface (menus) — coexists because judge is detached.
- `destroy()` does NOT fire any completion hook — plugin must resolve battles itself.

## Audio determinism (measured)
- `.ogg` files decode to container duration ±0.2ms (ffmpeg exact PCM sample counts); a manifest beat-grid is a safe timing source; the only real offset is per-device audio-context latency (calibrate once at playback start, conditional on measurement).
- BPM measurement: librosa `beat_track` (onset autocorrelation) matches within ±3% of an onset-interval histogram; chiptune tracks may alias to half-time — use interval methods.

## Headless Chrome (verification path)
- `decodeAudioData` hangs without an audio device — never gate a battle on it in headless; measure with ffmpeg instead.
- `--virtual-time-budget=N` advances timers/flows; `--timeout=N` does NOT advance virtual time — flows that depend on setTimeout may not progress.
- `--autoplay-policy=no-user-gesture-required` needed for headless audio flows.
- Images: add a load timeout; a 404 then resolves null instead of hanging the promise.
- Verify state via `--dump-dom` (class toggles, HP text) and `--screenshot` (pixel census with PIL: coral/gold/dark counters prove the render painted).
