<!-- GENERICIZED: 3×{CLIENT} | source: skills/software-development/verify-deployed-artifacts/references/{CLIENT} -->
# {CLIENT} Phase {CLIENT} — Polish & Domain Patterns

## Context

After the initial deployment-verification crisis (documented in `{CLIENT}`), the framework entered a polish phase with 5 more source/artifact divergence bugs and several domain-specific design insights.

## New Divergence Points

### 5. `judgmentCounts` vs `stats` property mismatch

`demo.html` called `feedbackLayer.judgmentCounts` but the served bundle exposed `feedbackLayer.stats`. The mismatch caused a `TypeError: judgmentCounts is not a function` that crashed the results overlay on game completion, freezing the UI with rings stuck on screen.

**Fix:** grep for property names in both the demo and the bundle. `grep -n "judgmentCounts\|stats" demo.html src/feedback-layer.ts` — ensure the property called in HTML matches what the class exposes.

### 6. Methods called in HTML but never implemented in bundle

`demo.html` called `feedbackLayer.getAccuracy()`, `feedbackLayer.getRanking()`, `feedbackLayer.playCelebration()` — all returned 0 occurrences in the served bundle. The calls existed in HTML/CSS but the TypeScript methods on FeedbackLayer were never bundled (or never existed).

**Pattern:** HTML/CSS skeletons with `display:none` can reference JS methods that don't exist. The browser doesn't error until the method is actually invoked (e.g., when `showResultsOverlay()` runs). Verify not just that the bundle loads, but that every method called from HTML exists in the bundle.

### 7. Ghost note injection masking a different bug

A "temp fix" injected a ghost note before user content to make the first-key ring visible. This masked the real bug (per-difficulty lead-in mismatch). When the ghost note was removed, user content started where typed. **Rule:** temporary workarounds that modify content/data should be reverted once the real fix lands — they create phantom behavior users will report as bugs.

## Domain-Specific Design Patterns (Typing Games)

### Character Order is Sacred

Typing games have one invariant rhythm games don't: **the user's content must appear in exactly the order typed.** No shuffling, no note-doubling, no post-hoc reordering.

The `injectDoubledNotes` mechanic (double common letters at half-beat offset for hard difficulty) was a rhythm-game pattern that turned "is this my content" into "iiss tthiiss my coonntteenntt." Wrong domain. Removed entirely.

**Rule:** difficulty scaling in typing games = timing windows only. Tighter windows for harder difficulties. Never modify the character stream.

### Ring/Judgment Sync

Approach rings must collapse on the **judgment event**, not on `note.time`. When a user hits a key early (delta = -324ms), the character advances immediately, but the ring keeps shrinking until `note.time` passes → visual desync.

**Fix:** `markNoteJudged(note, judgment)` called from `onHit`, `onMiss`, and `onNoteStale` hooks. Ring collapses in the same frame the character advances.

### Per-Difficulty Lead-In

First-key ring visibility requires `LEAD_IN_MS[difficulty]` to equal `preemptTime[difficulty]` for each difficulty tier. Easy: 1500ms, Medium: 1000ms, Hard: 600ms, Expert: 350ms.

When lead-in was a single global value (3000ms), easy's first ring was visible but medium/hard/expert had `timeUntilHit > preemptTime` at game start → rings skipped entirely.

### Judgment Color Coding in "Type This" Feed

Completed keys should show judgment quality using the same color coding as the stats display:
- Perfect: cyan `#00e5ff`
- Great: green `#76ff03`
- Good: yellow `#ffea00`
- Miss: red `#ff1744`

This gives per-key feedback matching aggregate metrics. Track judgments per-note in an array indexed by note position.

### End-Game Flow

On completion:
1. Celebration animation (confetti burst + edge glow)
2. Results overlay with: accuracy %, letter ranking (S/A/B/C/D/F), max combo, judgment counts
3. Two buttons: **Play Again** (same setup) and **Change Setup** (dismiss overlay so user can edit content/BPM/difficulty)
4. Stats persist after game end until next game starts (don't reset in `endGame()` — reset in `startGame()`)

### Wrong Keys Get Feedback

"Wrong keys are silently ignored" was the osu!-style input model, but the user explicitly wanted feedback. Wrong keys now trigger `renderMiss()` with red shake + ripple — visible feedback that the press was wrong, without advancing the cursor.

## Verification Checklist for Future Sessions

When fixing a bug in a bundled web app:

1. [ ] Read the import path in the served HTML (`grep "import.*dist" demo.html`)
2. [ ] Rebuild exactly that file (`npx esbuild ... --outfile=dist/<file>`)
3. [ ] Verify fix at commit SHA URL (`curl .../<sha>/dist/<file> | grep fix`)
4. [ ] Verify fix at `main` URL after propagation
5. [ ] Verify fix at live Pages URL (what user loads)
6. [ ] Check for property/method name mismatches between HTML and bundle
7. [ ] Check for temp workarounds that should be reverted
8. [ ] Bump cache-buster on import (`?v=N+1`)
