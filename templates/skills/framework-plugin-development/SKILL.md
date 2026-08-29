<!-- GENERICIZED: 8×{CLIENT} | source: skills/framework-plugin-development/SKILL.md -->
---
name: framework-plugin-development
description: Use when building a plugin/game on an existing framework.
---

# Framework Plugin Development

Discipline for building a plugin, game, or feature on top of an existing framework
({CLIENT}, any plugin architecture) instead of forking or extending it.
Born from the {CLIENT} monster-battler build on the {CLIENT} rhythm-typing framework.

Core stance: **compose, never extend or fork.** The plugin consumes the framework's
public surface and owns its own logic; it adds no framework code. This keeps the
framework upgradeable and the plugin portable.

## 1. Audit the REAL surface before writing the contract

Docs and type declarations lie. Verify against the actual shipped artifact:

- **Check for dead hooks.** A hook may exist in the interface/types AND have an
  implementation, but never be called by the framework's engine. Grep the engine
  source for every hook name and confirm each is actually invoked at runtime.
  {CLIENT} found `onGameStart`/`onGameEnd`/`onSongComplete` present in `types.ts`
  and the debug plugin but NEVER fired by the judge — dead surface. Build the
  contract on the *live* hooks only.
- **Check for stale type declarations.** The shipped `.d.ts` (or docs) can be
  OLDER than the built bundle. Author against the bundle's actual surface
  (`dist/game.js`) with plugin-local types, not the stale `.d.ts`. Verify with
  grep on the bundle, and regenerate upstream `.d.ts` if you own the framework.
- **Verify inheritance you rely on.** Confirm default behavior (e.g. combo-safe
  wrong keys) actually exists in the live build, not just in an older type file.
- Read the framework's `CONTRIBUTING.md`/`PLUGIN_GUIDE.md` for how it expects
  plugins to be authored and deployed — but ground-truth every claim against source.

If the framework needs a fix (stale types, missing guards), record it as an
upstream flag/issue rather than silently working around it in the plugin.

## 2. Own fragile sequencing in ONE named method

When the correct behavior depends on a load-bearing ORDER of framework calls, do
not leave that sequence inline at every call site. Wrap the full sequence in two
plugin-owned methods (e.g. `openMenu()` / `closeMenu()`) so the ordering lives in
exactly one home, is testable in isolation, and survives a future framework
evolution. If the framework's internals change, only those two methods patch.

Example ({CLIENT} menu gate — the judge is the ONLY consumer of the input bus):
- `openMenu()`: `judge.detach()` → hold the plugin's own tick loop → attach the
  plugin's own raw-key listener for menu selection. No judged keystroke can leak
  into the menus.
- `closeMenu()`: `judge.setStartTime(now)` (re-baseline!) → resume tick →
  `judge.attach(bus)` LAST. Order matters: re-baseline first, attach last.

## 3. When timing state must survive, own the clock baseline

If the framework holds an absolute song/state clock (e.g. `time = now - startTime`,
with absolute note times), pausing (menus, re-entry) does NOT freeze it. Any pause
then re-entry needs a clock **re-baseline** (`setStartTime(now)`) on exit, or:
- the first post-pause action is a guaranteed miss (past the window), and
- resuming the framework's stale/tick sweep fires EVERY expired note as a
  combo-breaking error in a loop (a 3s pause at low BPM = 2+ hits).

The re-baseline must happen BEFORE resuming the tick sweep, and input re-attach
LAST, so resumption sees fresh state.

## 4. Determinism for audio/rhythm: manifest, never playback

For any rhythm/timing game, the judge's note map must derive from a **canonical
manifest** (track → BPM + beat-grid + declared duration), never from reading the
audio file's playback position. Then the same track at the same BPM yields the
same note map every run (testable), and playback decode drift is irrelevant to
timing. Probe decode determinism by decoding to exact PCM frames (ffmpeg) and
comparing per-channel sample count / 44100 against the declared duration — a
sub-millisecond match means the manifest is a safe timing source. The ONLY
unavoidable offset is one-time audio-context startup latency, gated by the
browser autoplay policy: initialize the AudioContext from a user gesture
("Start Battle" button) before creating the session.

Note: design BPM and measured musical tempo are different things. If the
composer/beat-grid BPM is a *design* assignment, mark it `tempoVerified: false`
and let a real tempo read (onset autocorrelation / interval histogram) confirm it
before claiming the cadence matches.

## 5. Asset / license layering for reuse (the "island" pattern)

Reusing third-party assets (sprites, audio) alongside your own MIT code: keep
copyleft assets (CC-BY-SA) as a **distinct asset layer** — own directory, own
`LICENSE`, per-file attribution ledger — and enforce with a build assertion that
original/paid assets never reference that namespace. Ship-time island, not a
convention. VET PROVENANCE, not just license: files with unfillable attribution
(squashed git history, zero metadata, no credits doc) fail the "exclude on doubt"
rule even under a permissive-looking license. Audio compositions carry the
highest remix risk — ear-pass or exclude.

## 6. One stats source of truth

A framework and its plugin may each keep their own stats object ({CLIENT}'s
`FeedbackLayer.stats` vs the plugin's own counter). They WILL disagree — the
classic symptom is a duplicate UI counter showing different numbers (top
`Perfect: 0`, bottom `PERFECT 1`). Pick ONE plugin-owned source and treat the
framework's as a read-only artifact you deliberately don't trust: hide its UI,
never read it for logic. Otherwise every future stats feature (streak, capture
%, accuracy) rediscovers the duplicate and drifts again.

See `references/{CLIENT}` for the concrete {CLIENT} application of all five.
