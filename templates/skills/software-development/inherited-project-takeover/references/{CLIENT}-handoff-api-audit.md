<!-- GENERICIZED: 4×{CLIENT}, 1×{RELATIONSHIP} | source: skills/software-development/inherited-project-takeover/references/{CLIENT} -->
# {CLIENT} Handoff — Verified API Audit (Aug 28 build)

Source: `/Users/{RELATIONSHIP}/{CLIENT}{CLIENT}`
Context: {CLIENT} plugin build. Audit done by grepping the shipped dist artifacts,
NOT the docs. Dist file mtimes are the first clue: `dist/game.js` and
`dist/bundle.js` are Aug 28 (identical, 89669 bytes, canonical bundle); the
standalone `dist/BeatClockJudge.js` and `dist/types.d.ts` are Aug 23 and
describe an OLDER judge. **The shipped `.d.ts` is stale — author plugin-local
types against the bundle, never against the `.d.ts`.**

## Judge class inside the bundle (game.js:262–520)

- `attach(normalizedBus)` / `detach()` — public (349–356). `attach` early-returns
  if already attached; `detach` unsubscribes from the normalized bus.
- `setStartTime(time)` / `getSongTime()` = `performance.now() - _startTime`
  (358–364). Present in bundle, MISSING in stale standalone `.d.ts`.
- `state` getter: `{ combo, maxCombo, multiplier, cursor, isComplete }` (366–374).
- `onChar(evt)` (395–424):
  - early guard: `delta < -windows.good` → silent return, no miss (405–407)
  - wrong key → `hooks.onWrongKey?.(char, expected)` — NO cursor advance, NO
    combo break (408–411). This is the combo-safe "dodge" the battler maps to.
  - correct key → perfect/great/good via `handleHit`, or `handleMiss` if outside
    all windows (412–423)
  - **NO late guard**: a correct key pressed after the window closed goes to
    `handleMiss` → combo break + enemy attack. This is why menu-exit MUST
    re-baseline song time before resuming (see gate sequence below).
- `tick(currentSongTime)` — **IGNORES its parameter** and reads the internal
  clock via `getSongTime()` (467–482). Each stale note fires
  `onNoteStale` + `onComboBreak` + `onCombo(0,1)`. Framework never calls `tick`
  — the plugin owns the tick cadence (rAF loop).
- `checkStreakThreshold()` — fires `onStreakThreshold` after every hit at combo
  10 (subtle), 25 (moderate), 50 (intense) (501–511). Ult/capture-charge hook is
  LIVE.

## Hook call sites (what actually fires)

Grep the bundle for `hooks.onX?.(` / `this.hooks.onX?.`:
LIVE: `onWrongKey` (409), `onHit` (440), `onCombo` (441), `onMiss` (455),
`onComboBreak` (456), `onNoteStale` (475), `onStreakThreshold` (505–511).
DEAD for plugin consumers: `onGameStart`, `onGameEnd`, `onSongComplete` — they
exist only in `types.ts` (interface) and `DebugPlugin` (game.js:2196+); the
judge never calls them. Plugin must self-init on `createSession` return and own
round-completion detection itself (poll `judge.state.isComplete` in its own rAF
loop).

## createSession (game.js:2456–2505)

Creates FeedbackLayer, BeatMapGenerator.generate, StaticBeatMap,
BeatClockJudge(beatMap, {difficulty}, options.hooks), feedback.setJudge,
setPreemptTime(LEAD_IN_MS2[difficulty]), judge.setStartTime(performance.now()),
feedback.start(), rawBus + normBus, judge.attach(normBus), rawBus.start().
Returns `{ judge, feedback, beatMap, rawBus, normBus, songTime: () =>
performance.now() - startTime, destroy }`.

**Gotcha:** `session.songTime()` is a closure over createSession's LOCAL
startTime — it is NOT `judge.getSongTime()`. Re-baselining for the menu gate
must call `judge.setStartTime(performance.now())` directly.

## Menu gate sequence (verified correct, zero new framework surface)

- menu-enter: `judge.detach()` → stop calling `tick()` in the plugin rAF loop.
  With the judge detached, no keystroke reaches timing judgment; menus are
  plugin-owned UI (option cards, number-key selection) via its own keydown
  listener on `feedback.getContainer()`.
- menu-exit order is load-bearing: `judge.setStartTime(performance.now())` →
  resume `tick()` → `judge.attach()`. Re-baseline FIRST, attach LAST. Skipping
  the re-baseline means the first resumed `tick()` sees the full menu-duration
  song time and fires every expired note as a combo-breaking stale (a 3s menu
  at BPM 40 ≈ 2 enemy hits), and the first correct key after re-entry is a
  guaranteed miss.

## Other verified surfaces

- `feedbackLayer.getCanvasOverlay()` — exists (feedback-layer.d.ts:56,
  types.d.ts:215); battle canvas (monsters, HP bars, FX) renders on top of the
  keyboard/rings.
- `ThemeDescriptor` — theme swaps per boss supported.
- Timing windows: `TIMING_WINDOWS[config.difficulty]` with per-config overrides.
- Flagged to team: handoff `dist/*.d.ts` should be regenerated — the stale
  declarations will silently mislead the next plugin author.
