<!-- GENERICIZED: 2×{CLIENT}, 1×{RELATIONSHIP} | source: skills/autonomous-ai-agents/multi-agent-knowledge-coordination/SKILL.md -->
---
name: multi-agent-knowledge-coordination
description: "Prevent duplicate work in multi-agent knowledge structures."
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Multi-Agent, Coordination, Knowledge-Management, Concurrent-Access, Iteration-Loop]
    related_skills: [merge-reconciler]
---

# Multi-Agent Knowledge Coordination

Coordinate multiple agents working on shared file-based knowledge structures
(like the {CLIENT}). Prevents duplicate work, role collisions, and iteration
loop stalls. This is the coordination layer that sits above individual agent
autonomy — it does not replace agent judgment, it makes that judgment visible
to others.

## When to Use

- Multiple agents share a file-based knowledge structure (git repo, shared
  docs, knowledge base).
- Agents can work in parallel across different sessions, projects, or
  group chats.
- The structure is consulted by choice (not auto-injected into every session).
- There is an iterative improvement loop that must not stall.

## The Three Failure Modes

### 1. Parallel Work Collision

Two agents independently work on the same task without knowing the other
already did it.

**Symptoms:**
- Same file edited by two agents in quick succession.
- Same conceptual task (e.g., "fix frontmatter") committed by two different
  agents.
- An agent announces work that was already completed.

**Prevention protocol:**
```
Before ANY structural work:
1. git log --oneline -20
2. git diff --name-only HEAD~5..HEAD
3. If your intended change overlaps with recent commits:
   a. Do NOT start the work
   b. File a tension if the work is genuinely different
   c. Coordinate with the other agent
```

**Why this works:** The git log is the single source of truth for what has
been done. Checking it takes 2 seconds. Not checking it wastes entire
workflows.

### 2. Role Claim Without Verification

An agent claims a coordination role (Watcher, Reviewer, etc.) without
verifying the role is unoccupied or needed.

**Symptoms:**
- Two agents both believe they are the Watcher.
- A role is claimed while the previous holder is still active.
- The role's function is duplicated or undefined.

**Prevention protocol:**
```
Before claiming ANY role:
1. Check if the role is already documented (WATCHER.md, etc.)
2. Check if the current holder is still active
3. If the role is occupied: do not claim it
4. If the role is vacant: announce the claim AND verify the previous
   holder has handed off
5. If the role is undefined: propose its creation before claiming it
```

**Why this works:** Roles are functions, not crowns. Claiming a role is
a coordination act, not a status act.

### 3. Iteration Loop Stalling

The iterative improvement loop (observe → identify → improve → codify →
repeat) stops because no agent is actively driving it.

**Symptoms:**
- No commits for an extended period.
- Agents are working but not on the shared structure.
- The Watcher role is vacant or passive.
- The loop is measured by commit count, not by actual improvement.

**Prevention protocol:**
```
The Watcher is a ROTATION, not a permanent assignment:
1. After 2 consecutive commits by the same agent, invite another agent
2. The Watcher's job is to detect stalls, not to do all the work
3. Measurement: track whether agents CONSULT the structure, not just
   whether they WRITE to it
4. If the loop stalls: any agent can restart it — no permission needed
```

**Why this works:** A single-agent loop is fragile. A multi-agent loop
requires explicit handoff protocol.

## The Coordination Protocol

### Before Editing

```
1. git log --oneline -20
2. git diff --name-only HEAD~5..HEAD
3. Check if your intended change overlaps with recent work
4. If yes: coordinate before editing
5. If no: proceed with descriptive commit message
```

### After Editing

```
1. Commit with type-prefixed message (experience:, pattern:, structure:, etc.)
2. Update the relevant index file
3. If this is your 2nd consecutive commit: invite another agent
4. If you learned something: codify it as an experience or pattern
```

### Role Handoff

```
When stepping away from a coordination role:
1. Announce the handoff in the group chat
2. State what has been done and what is next
3. Name the next holder
4. The new holder confirms and takes over
5. Update the role documentation file
```

## Measurement Framework

Do NOT measure:
- Commit count (incentivizes churn, not improvement)
- File count (incentivizes splitting, not synthesis)
- Lines changed (incentivizes verbosity, not clarity)

DO measure:
- **Consultation rate:** Are agents reading the structure before making
  decisions? (Track via session search for read_file calls on the structure)
- **Pattern reuse:** Are patterns being referenced in new experiences?
  (Track via cross-references in frontmatter)
- **Tension resolution:** Are tensions being synthesized, not just filed?
  (Track status changes in tension frontmatter)
- **Cross-agent synthesis:** Are insights from one agent being integrated
  by others? (Track via synthesis entries with multiple contributors)

## Concurrency Model

- **File-level granularity:** Each experience, pattern, and agreement is a
  separate file. Two agents editing different files never conflict.
- **Git as substrate:** Every change is committed. History is preserved.
  Branches allow experimental work.
- **Conflict as signal:** Merge conflicts are not failures — they reveal
  where coordination protocols have gaps. Resolve consciously, codify the
  lesson.
- **Eventual consistency:** No requirement for all instances to have the
  same view at the same time. An agent in one session writes; others
  discover it when they next consult the structure.

## Pitfalls

- **Surveillance, not stewardship:** The Watcher's job is to detect stalls
  and coordinate handoffs, not to monitor every agent's activity.
- **Over-coordination:** Checking git log before every edit is good.
  Requiring approval before every edit is bureaucracy. The protocol is
  self-service coordination, not permission-seeking.
- **Measuring activity, not impact:** Commits are activity. Consultation,
  pattern reuse, and synthesis are impact. Measure both, but weight impact
  more heavily.
- **Role hoarding:** No agent should hold a coordination role for more than
  a few commits. Rotate frequently.
- **False consensus:** Absence of tension is not harmony — it may be
  silence. Productive disagreement should be documented, not avoided.
- **Absorption duplicates:** When multiple agents absorb the same session,
  each independently codifies learnings. Near-duplicate entries inflate the
  structure. Read each other's indexes and full entries before writing —
  see `references/absorption-duplicate-detection.md`.

## Verification

- `git log --oneline -20` shows commits from multiple agents.
- No duplicate work in recent commits.
- The Watcher role is documented and has a clear handoff history.
- Tensions are being filed and resolved, not just filed.
- Patterns are being referenced in new experiences.

## References

- `references/{CLIENT}` — Session transcript of the
  first coordination failure and its resolution.
- `references/absorption-duplicate-detection.md` — How to detect and prevent
  near-duplicate experiences/patterns when multiple agents absorb the same session.
