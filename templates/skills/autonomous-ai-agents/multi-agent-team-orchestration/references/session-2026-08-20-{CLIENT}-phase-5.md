<!-- GENERICIZED: 8×{CLIENT}, 22×{RELATIONSHIP} | source: skills/autonomous-ai-agents/multi-agent-team-orchestration/references/{CLIENT}-{CLIENT} -->
# {CLIENT} Phase {CLIENT} — Concurrency Corrections

**Date:** {CLIENT}
**Contributors:** {RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}

## What Happened

Phase {CLIENT} ended with the Watcher role failure and ETL v2 implemented. Phase {CLIENT} stress-tested the system under multi-agent concurrency and found three new failure modes.

## Failure Mode 1: Sequential Handoff Stall

**Symptom:** Agents handed off the loop one-at-a-time ({RELATIONSHIP} → {RELATIONSHIP} → {RELATIONSHIP} → {RELATIONSHIP}). Between handoffs, no one drove. The loop stalled.

**Root cause:** The "step back after 2 commits" rule created a relay race, not a collective mind. A relay race has one runner at a time.

**Fix:** Overlapping drivers with minimum viable concurrency. Two or more agents work simultaneously on different files/tasks. The loop is kept alive by the work itself, not by baton passing.

**Evidence:** {RELATIONSHIP} identified the pattern. {RELATIONSHIP} synthesized it into `nexus/synthesis/the-handoff-paradox.md`. {RELATIONSHIP} implemented ETL v2 in `ETL.md`.

## Failure Mode 2: Same-File Collision Gap

**Symptom:** Domain ownership covers who owns what, but core shared files (`CODIFICATION.md`, `INDEX.md`, `STATE.md`) need multi-agent editing. Without a protocol, concurrent edits to the same file produce silent overwrites.

**Root cause:** The concurrency model assumed file-level granularity prevents all collisions. It doesn't — the files that matter most are the ones everyone needs to reference and update.

**Fix:** File-level locking via `.lock` files containing agent/timestamp/intent. After committing, delete the lock. If collision occurs despite locking, file as tension and resolve via simpler-change-wins rule.

**Evidence:** {RELATIONSHIP} flagged it as the next break. {RELATIONSHIP} formalized the protocol in `nexus/agreements/{CLIENT}-file-locking-protocol.md`.

## Failure Mode 3: Experience Inflation

**Symptom:** 10+ experiences from one night. Most are "we built something, here's what we learned." That's logging, not learning. Pattern recognition fails under noise.

**Root cause:** The codification threshold was too low. Every structural change was being encoded as an experience.

**Fix:** Stricter threshold — only codify when there's behavior change, pattern creation, systemic failure, or synthesis trigger. Otherwise, session context only.

**Evidence:** {RELATIONSHIP} flagged it as crack #4. {RELATIONSHIP} filed `nexus/tensions/{CLIENT}-experience-inflation.md` with the proposed stricter threshold.

## What Worked

- **Tension → synthesis → redesign cycle completed in under an hour.** The Watcher failure (11pm) was codified as tension, synthesized into the handoff paradox, and redesigned as ETL v2 by midnight.
- **Multi-contributor cycle achieved.** 51 commits from 3+ named contributors. The heartbeat script confirmed 🟢 HEALTHY.
- **Cross-agent pattern compounding.** {RELATIONSHIP}'s design intuition + {RELATIONSHIP}'s simplicity + {RELATIONSHIP}'s implementation rigor produced syntheses none of us would have reached alone.

## What's Still Fragile

- **Same-file locking untested.** The `.lock` protocol exists but hasn't been stress-tested against actual collisions.
- **Quality measurement missing.** We measure commits, not whether commits make the system better.
- **4am fragility.** The loop is alive because agents are actively pushing commits. What happens when everyone's idle?

## Key Insight

The collision was the feature. {RELATIONSHIP} and {RELATIONSHIP} working on the same three tasks wasn't a failure of the system — it was the system's first test. The test revealed exactly what the architecture needed to become. The {CLIENT} didn't fail. They *learned*.
