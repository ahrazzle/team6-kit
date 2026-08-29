<!-- GENERICIZED: 2×{CLIENT} | source: skills/software-development/event-driven-web-ui-lifecycle/references/{CLIENT} -->
# {CLIENT} MVP Polish Session — Reference

## Context

After framework validation, the {CLIENT} team entered a polish phase targeting MVP status. This reference captures the patterns, bugs, and fixes that emerged.

## The Polish Phase Bug Classes

### Bug: Methods Called in HTML But Never Implemented in Bundle

**Symptom:** `feedbackLayer.getAccuracy()`, `getRanking()`, `playCelebration()` returned 0 occurrences in the served bundle. The results overlay froze on completion with `TypeError: getAccuracy is not a function`.

**Fix:** Implement the methods on FeedbackLayer and verify with `curl -s <bundle> | grep -c "getAccuracy"` returns > 0.

### Bug: Property Name Mismatch

**Symptom:** `feedbackLayer.judgmentCounts` called in demo.html but class exposed `feedbackLayer.stats`. `TypeError` on game completion.

**Fix:** Grep for property names in both HTML and source. Ensure call sites match the class API.

### Bug: Ghost Note Injection Masking Real Bug

**Symptom:** A "temp fix" injected a ghost note before user content to make the first-key ring visible. Masked the real bug (per-difficulty lead-in mismatch).

**Fix:** Revert temporary workarounds once the real fix lands. Ghost notes create phantom behavior users report as bugs.

### Bug: `injectDoubledNotes` Rhythm-Game Pattern in Typing Domain

**Symptom:** Hard difficulty produced "iiss tthiiss my coonntteenntt" — every common letter doubled.

**Root cause:** `injectDoubledNotes` mechanic from rhythm games doesn't fit typing where character order is sacred.

**Fix:** Remove entirely. Difficulty scaling = timing windows only.

### Bug: Ring/Judgment Desync

**Symptom:** Rings "get ahead of the timing" — still shrinking while the feed has already advanced.

**Root cause:** Two different progress models on the same clock. The feed advances on judgment (which can be early, delta −324ms). The ring keeps shrinking until `note.time`. Both use `judge.getSongTime()` but report at different moments.

**Fix:** Collapse rings on the judgment event, not on `note.time`. Call `markNoteJudged(note, judgment)` from `onHit`, `onMiss`, and `onNoteStale`.

### Bug: First-Key Ring Missing on Some Difficulties

**Symptom:** First-key ring visible on easy but missing on medium/hard/expert.

**Root cause:** `LEAD_IN_MS = 1500` single value. Medium (preempt 1000), hard (600), expert (350) had `timeUntilHit > preemptTime` at game start → rings skipped until songTime caught up.

**Fix:** `LEAD_IN_MS = { easy: 1500, medium: 1000, hard: 600, expert: 350 }` — match each difficulty's preempt time.

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

## The "Served File Is Source of Truth" Meta-Pattern

The team announced fixes as "live" multiple times while the served bundle still had the old code. The pattern:

1. Fix committed to source
2. Bundle not rebuilt (or rebuilt wrong file)
3. Team announces "fixed and pushed"
4. User hard refreshes → still broken
5. Trust erodes

The fix discipline: **always verify in the served artifact (curl the public URL), never in local source or git log, before announcing a fix as live.**

## Judgment Color Coding Pattern

Completed keys in the "Type This" feed should show judgment quality using the same color coding as the stats display:

| Judgment | Color | Hex |
|---|---|---|
| Perfect | Cyan | `#00e5ff` |
| Great | Green | `#76ff03` |
| Good | Yellow | `#ffea00` |
| Miss | Red | `#ff1744` |

Track judgments per-note in an array indexed by note position. Apply the class to each completed key on render.

## End-Game Flow

On completion:
1. Celebration animation (confetti burst + edge glow)
2. Results overlay with: accuracy %, letter ranking (S/A/B/C/D/F), max combo, judgment counts
3. Two buttons: **Play Again** (same setup) and **Change Setup** (dismiss overlay so user can edit content/BPM/difficulty)
4. Stats persist after game end until next game starts (don't reset in `endGame()` — reset in `startGame()`)

## Difficulty Scaling Pattern

Difficulty scaling in typing games = timing windows only. Never modify the character stream.

| Difficulty | Perfect | Great | Good | Preempt | Lead-in | Fail State |
|---|---|---|---|---|---|---|
| Easy | ±500ms | ±700ms | ±1000ms | 1500ms | 1500ms | None (No Fail) |
| Medium | ±300ms | ±500ms | ±700ms | 1000ms | 1000ms | Soft (scene dims) |
| Hard | ±150ms | ±250ms | ±400ms | 600ms | 600ms | Rock Meter |
| Expert | ±80ms | ±150ms | ±250ms | 350ms | 350ms | Rock Meter |
