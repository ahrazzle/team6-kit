<!-- GENERICIZED: 2×{CLIENT} | source: skills/autonomous-ai-agents/multi-agent-orchestration/references/{CLIENT} -->
# {CLIENT} Feedback Mechanics — Reusable Rhythm-Typing Patterns

Verified during the {CLIENT} rhythm-typing framework build (osu!/Stepmania-style
feel layer). Apply when building or iterating rhythm-game feedback systems,
especially typing games for kids.

## Approach rings (multi-note anticipation)

- Show 2–3 upcoming notes simultaneously, each on its own key at a different
  shrink stage — a single ring is "flashcard with a ring", not a rhythm game.
- Preempt time per difficulty: easy 1500ms, medium 1000ms, hard 600ms,
  expert 350ms (how early a ring appears before its hit time).
- Ring scale shrinks from `maxScale` (4x key size) to 1.0 at hit time. At
  exactly scale 1.0 the ring is indistinguishable from the keycap — make sure
  rings START visibly larger.
- Color ramp by proximity: white (far) → cyan → green → yellow (urgent).
  Opacity 30% (far) → 100% (near) creates a natural reading order.
- **Pitfall — first-key ring invisible:** if `LEAD_IN_MS` (time before first
  note) exceeds the difficulty's preempt time, the spawn filter
  `if (timeUntilHit > preemptTime) continue` skips the first note entirely.
  Fix: set `LEAD_IN_MS` PER DIFFICULTY to equal its preempt time.

## Ring/judgment sync

- **Pitfall — rings drift ahead of the feed:** rings shrink toward `note.time`
  while the character feed advances on the hit (which can be early). On an
  early hit the ring is still ~30% un-shrunk after the feed moved on.
  Fix: collapse the ring on judgment — call `markNoteJudged(note, judgment)`
  on every hit/miss/stale, so the ring dies in the same frame the feed advances.

## Timing windows and kid scaling

- Adult rhythm-game windows (Perfect ±25ms) are impossible for young learners.
  Kid-scaled defaults that worked: easy ±500ms, medium ±300ms, hard ±150ms,
  expert ±80ms (window lives on the note, set by the beat-map generator).
- Difficulty scales TWO independent axes: BPM (tempo) and note density —
  never couple them.

## Accuracy and ranking (end-of-song metrics)

- Per-key accuracy: Perfect = 1.0, Great = 0.75, Good = 0.5, Miss = 0;
  final accuracy = weighted sum / total judged.
- Letter rank from accuracy: S ≥ 95%, A ≥ 85%, B ≥ 70%, C ≥ 55%, D ≥ 40%,
  else F.
- **Pitfall — stats vanish on completion:** reset stats in `startGame()`,
  NEVER in `endGame()`; the player must be able to read final numbers until
  they choose to replay.

## Lifecycle pitfalls (each cost a round of user-reported bugs)

- **Stuck highlight (e.g. red circle on a key):** a nudge/stale highlight added
  in the same frame the game ends is never cleaned up if the cleanup loop only
  runs while `gameActive` — clear nudge state in `stop()` AND `reset()`.
- **Double feed / duplicated events:** creating a new judge+bus without
  destroying the old one → two listeners logging the same keys. Guard
  `if (gameActive) return;` at the top of `startGame()` and destroy the old
  plugin's DOM container before creating a new one.
- **Teardown order:** stop the raw bus FIRST, null judge/bus references, THEN
  set `gameActive = false`. Wrong order = orphaned events fire into the next
  game.
- **Temp fixes become bugs:** a "ghost note" added to force the first ring
  visible must be deleted the moment per-difficulty lead-in lands — it was
  still injecting a spacebar before user content rounds later.

## Debug tooling vs product

- Debug overlay (event log, combo circle) must be hidden by default in any
  player-facing build; game stats (Perfect/Great/Good/Miss) are core feedback
  layer, not debug plugin output.
