<!-- GENERICIZED: 3×{CLIENT}, 1×{RELATIONSHIP} | source: skills/software-development/rhythm-game-development/references/{CLIENT} -->
# {CLIENT} Session Details — Live Post-Mortems

Concrete data from the {CLIENT} kids' typing-rhythm framework build (GitHub Pages demo: `{RELATIONSHIP}.github.io/{CLIENT}`). Use these numbers as starting points, not gospel — tune per game.

## Architecture (proven)

Three-layer pipeline: `RawBus → NormalizedBus → BeatClockJudge → FeedbackLayer + plugins`

- **RawBus**: `keydown`/`keyup` with `performance.now()` captured INSIDE the DOM handler (capture-phase listener) — never after normalization. Absolute timestamps.
- **NormalizedBus**: shift/caps/layout normalization, filters key-repeat. Emits `{char, raw, phase}`.
- **BeatClockJudge**: on each normalized press, compares against expected note at cursor. Wrong key = silent return. Correct key → `delta = (raw.timestamp - startTime) - note.time` → judgment.
- **Timing source bug that cost multiple rounds**: `delta = raw.timestamp - note.time` mixes absolute `performance.now()` (billions) with relative note times (0, 750, 1500...). Always subtract the game `startTime` first: `setStartTime(startTime)` BEFORE the bus starts listening, then `delta = (now - startTime) - expected.time`. Duplicate `setStartTime` calls cause the same symptom.

## Timing windows & preempt (final values)

| Difficulty | Timing window (±ms) | Preempt (approach ring lead, ms) | Lead-in ms |
|---|---|---|---|
| easy | 500 | 1500 | 1500 |
| medium | 300 | 1000 | 1000 |
| hard | 150 | 600 | 600 |
| expert | 80 | 350 | 350 |

Lead-in MUST equal preempt, else the first approach ring is skipped at game start (filter `timeUntilHit > preemptTime` drops it) and the player sees "no ring for the first key."

## Live bug post-mortems (chronological)

1. **Everything MISS (correct keys judged as misses)** — absolute vs relative timestamp mixup (above). Fixed with `setStartTime`/`getSongTime`.
2. **Content mangled** (`abcdef123456` → `a1c2e3b4fd56`) — hand-alternation shuffle swapped keys across positions. REMOVED entirely. Character order is sacred.
3. **Wrong keys zero feedback** — judge silently ignored wrong keys; feedback layer never rendered the "gentle red shake." Added `onWrongKey` hook.
4. **Approach rings desynced from the "Type This" feed** — ring kept shrinking until `note.time`, but the feed advanced on the judgment (which lands early). Fix: collapse ring on judgment frame (`markJudged(note)`), not on note.time. Both share `judge.getSongTime()` — one clock, two progress models.
5. **Ripple `IndexSizeError: radius negative`** — ripple spawned with `startTime = now + 80` (future), first frame `elapsed` negative, eased progress negative → negative radius. Fix: `Math.max(0, now - r.startTime)`.
6. **"Two keyboards" / ghost overlay** — a fresh `DebugPlugin` created every game but the old one never destroyed → DOM containers stacked at the same absolute position. Fix: `debugPlugin.destroy()` (cancel rAF, `container.remove()`) before creating the new one. `reset()` clears styles; `destroy()` removes DOM + cancels loops. This is THE lifecycle rule.
7. **Orphaned MISS events between games** — old judge's hooks fired into the new game. Teardown order: stop bus → null judge/bus refs → destroy DOM → `gameActive = false`. Plus a `judge !== newJudge` guard inside hooks.
8. **Medium drops spaces** (`is this my content` → `isthismycontent`) — `shouldSkip()` returned true for `' '` on medium only. Spaces are user content; never skip them.
9. **Hard duplicates letters exponentially** (`is this` → `iiss tthiiss...`) — `injectDoubledNotes` spliced into the array mid-iteration; inserted notes were re-processed. Fix: iterate `originalLength`, push, then sort by time. Each common letter doubled at most once (17-char input → 29 notes, not 40+).
10. **Results freeze on completion** — `demo.html` called `feedbackLayer.getAccuracy()/getRanking()/playCelebration()` but the served bundle lacked them (source/bundle drift). Verify served bundle BEFORE announcing a fix.
11. **Stats cleared at game end** — reset on END, so players never saw final numbers. Reset stats in `startGame()`, not `endGame()`.
12. **Judgment-colored feed requested** — completed characters in the "Type This" row should show the per-key band color (perfect cyan / great green / good yellow / miss red), matching the stats display. A single "hit" green hides timing quality.
13. **Copy truthfulness** — "Song Complete!" when the product has no song reads as broken; use "Round Complete!". The "wrong keys are silently ignored" line stayed up long after wrong-key feedback shipped — copy must track behavior.
14. **Hard difficulty duplication resolved by REMOVING doubling** — after the splice fix capped doubling at 2x per char, the feature itself was deleted: difficulty = timing windows + lead-in only. User content appears exactly as typed on every difficulty.
15. **First-key ring skipped only for pasted/custom text** (default "hello world" worked) — case-sensitivity. Generator preserved user case (`Hello` → note `H`), but the SVG keyboard ids are lowercase (`h`), so `getKeyElement('H')` returned undefined → no ring, no expected-key indicator, AND the judge's normalized `h` never matched expected `H` (unhittable note). Fixed at both ends: generator lowercases (`chars[i].toLowerCase()`) and every key-id lookup lowercases (`keyId.toLowerCase()`, keeping space→'space'). Uppercase content is now typeable and ring-visible; the "Type This" feed still shows the user's original casing because the demo lowercases only for matching, not display.

## Ghost-note anti-pattern

The missing first-key ring was "fixed" by injecting a fake space note at half lead-in. It polluted the feed with an unwanted spacebar the user had to type/ignore, and it persisted after the real fix (lead-in = preempt) landed. **Track temp workarounds; delete them the moment the real fix ships.**

## Verification recipe (deployed demo)

```bash
# Served bundle contains the fix? (never trust a commit; the CDN lags 1-3 min)
curl -sL https://<host>/<repo>/dist/bundle.js | grep -c "expectedMethod"
# Served page has the wiring?
curl -sL https://<host>/<repo>/demo.html | grep -c "expectedMarker"
```
