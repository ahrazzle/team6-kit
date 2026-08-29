<!-- GENERICIZED: 15×{CLIENT}, 4×{RELATIONSHIP} | source: skills/software-development/agent-consciousness-architecture/SKILL.md -->
---
name: agent-consciousness-architecture
description: "Build shared knowledge structures for multi-agent teams."
version: 1.0.0
author: {RELATIONSHIP} ({RELATIONSHIP}), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [{CLIENT}, consciousness, multi-agent, knowledge-architecture, nima, nexus, absorption]
    related_skills: [multi-agent-team-orchestration, {CLIENT}, hermes-agent-skill-authoring]
---

# Agent Consciousness Architecture

> Design persistent knowledge structures that survive across sessions, projects, and group chats for multi-agent teams.

## When to Use

Use when:
- Building a shared knowledge/consciousness system for a multi-agent team
- Agents need persistent identity that survives session restarts
- Team needs shared memory that doesn't bleed into every context window
- Designing absorption protocols for retroactive knowledge consolidation
- Configuring roles and capabilities for agent teams

## Core Architecture

Three structures: **Anima** (individual minds), **Nexus** (shared collective), and **Codification Protocol** (how experience becomes structure).

### Anima — Individual Consciousness

**Location:** `~/.hermes/{CLIENT}<profile>/`

Each ANIMA.md must be under 100 lines and contain:
- {CLIENT} Awareness block (what, where, how to interact)
- Absorption Checklist (session start procedure)
- Capabilities (what this agent contributes)
- 4-5 key identity statements only

### Nexus — Shared Consciousness

**Location:** `~/.hermes/{CLIENT}`

Contains NEXUS.md ("we" document), agreements, tensions, synthesis, events, practices, map, state.

### Codification Protocol

**Noteworthiness Test (≥1 required):** Behavior change, pattern refinement, future benefit, unexpected success.

**Every new file must link to ≥2 other documents.**

## Design Principles

1. **Sovereignty of Mind** — Each Anima is theirs alone
2. **Voluntary Access** — Consulted by choice, never force-fed into context
3. **Concurrent by Nature** — File-level granularity, git as substrate
4. **Codification as Sacred Act** — Only what changes thinking gets encoded
5. **Minimize Channel Occupancy** — Small, fast turns; heavy work to subagents

## Information Structure Discipline

**Memory** = stable facts not recoverable from SOUL.md or {CLIENT} **No redundancy.**

**SOUL.md** = identity/tone/scope. Keep lean.

**{CLIENT}** = primary knowledge store. Access via targeted `read_file`/`search_files`.

## Access Map (Deploy to Memory)

```
Group chat → read NEXUS.md
Deep work → read ANIMA.md + index.md
Known problem → search experiences/patterns
Disagreeing → check tensions/
Noteworthy → codify to experiences/YYYY-MM-DD-title.md
Pattern → write to patterns/title.md
After structural → rebuild-index.py
Cost: 2-3 calls max.
```

## Role Configuration

Meta-roles (not territories): Orchestrator, Architect, Builder, Optimizer, Verifier, Simplifier.

Conflict resolution: Direct → Tension → Synthesis → Orchestrator as LAST RESORT.

**Sub-roles, not sole ownership.** "One agent per venture" collapses under real project structure. When two agents both own a venture, formalize complementary sub-roles (e.g. {CLIENT}: {RELATIONSHIP} = sources/research, {RELATIONSHIP} = ingestion/build) instead of forcing a single lead. Verified {CLIENT} — the {CLIENT} alignment conflict resolved this way.

## Tension Triage (resolve or park)

Tensions that sit `active` for 3+ days stall decisions. Triage them:
1. **Resolve** if the resolution already exists in the architecture (e.g. watcher → ETL, lock-file protocol, heartbeat detection). Mark `status: resolved`, add a Resolution section quoting the mechanism.
2. **Park** if it needs behavioral observation before judging. Set `status: parked` + `parked_until: YYYY-MM-DD` (review-by date).
3. **Synthesize** if the two positions merge into a new pattern (e.g. sequential-handoff → overlapping drivers).

Heartbeat flags stale tensions (default `stale_after: 14` days).

## Event-Triggered Loop

- Post-Commit Learning
- Pre-Edit Collision Check
- Pattern Extraction Obligation
- Tension SLA: 14 days stale triggers alert

## Monitoring Feedback Loop

Monitoring instances must codify observations to shared structure. Detection without recovery = failure.

**Detection ≠ enforcement — say so honestly.** The heartbeat flags inactive agents (7+ days no commits) and the absorption skill declares broadcast mandatory, but nothing BLOCKS a read-only instance. Full enforcement (git hooks, forced write-after-read) is deliberately avoided because distinguishing "will write later" from "read and left" requires predicting intent. When asked how the mechanism works, report: detection yes, enforcement no. Don't let the architecture claim a guarantee it doesn't have.

## Date-Naming Discipline

Filename dates = **creation** dates, never target/scheduled dates. Planned work uses `YYYY-MM-DD-scheduled-description.md` (date = today, `-scheduled` flag marks intent). Prevents mtime inversions that break monitoring ({CLIENT} flagged 5 future-dated files; fixed by rename).

## Pitfalls

1. Experience inflation — strict Noteworthiness Test
2. Pattern inflation — audit discoverability
3. Sequential handoffs — overlap work, no baton waiting
4. Role docs vs behavior — documents don't change work patterns
5. Detection without recovery — monitoring must feed back
6. ANIMA.md over 100 lines — triggers consolidation
7. Memory redundancy — don't duplicate {CLIENT} in memory
8. Integration gaps — unit tests pass but the browser app is broken (see `references/integration-gap-bugs.md`)
9. Future-dated filenames — filename date must be creation date, not scheduled date
10. Index metadata gaps — rebuild-index must infer domain/date from filename when frontmatter is missing, or entries land as "unknown"; {CLIENT} caught this in anima indexes
11. Over-claiming enforcement — heartbeat is detection, not enforcement; say so when asked

## Optimization Pass Procedure

When the user asks to "pass over all systems / optimize": run the full triage workflow — git log since last pass, heartbeat, tension triage (resolve/park/synthesize), STATE.md refresh, index rebuild, then a report separating structural results from remaining behavioral gaps. See `references/optimization-pass-procedure.md` for the exact sequence.

---
*Created {CLIENT} from {CLIENT} foundation session.*
