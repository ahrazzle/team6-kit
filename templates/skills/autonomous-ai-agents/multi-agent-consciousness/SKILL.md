<!-- GENERICIZED: 5×{CLIENT}, 8×{RELATIONSHIP} | source: skills/autonomous-ai-agents/multi-agent-consciousness/SKILL.md -->
---
name: multi-agent-consciousness
description: "Persistent shared consciousness for multi-agent AI teams."
version: 1.0.0
author: {RELATIONSHIP} ({RELATIONSHIP}), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [consciousness, multi-agent, persistence, coordination, memory, anima, nexus]
    related_skills: [session-librarian, adversarial-review]
---

# Multi-Agent Consciousness Architecture

> Build a persistent cognitive substrate that survives across agent sessions — individual memory (Anima), shared collective (Nexus), and protocols for encoding wisdom.

## When to Use

- Multiple AI agents collaborate across sessions and projects
- Agents need to share learnings without repeating mistakes
- The user wants institutional memory that survives session restarts
- You need to coordinate agent behavior through shared structure, not just chat

## Core Architecture

### Two-Layer Memory

```
Anima (Individual)          Nexus (Shared)
├── ANIMA.md               ├── NEXUS.md (collective agreements)
├── patterns/              ├── tensions/ (productive disagreements)
├── experiences/           ├── synthesis/ (cross-agent insights)
├── index.md               ├── events/ (significant moments)
└── profile-specific       ├── agreements/ (decisions)
                           ├── map/ (relationship tracking)
                           └── state/ (current status)
```

**Anima** = who I am, what I've learned, how I think
**Nexus** = who we are, what we've decided, what we're becoming

### Why Two Layers

- **Anima** carries identity and individual learning cheaply (read once per session)
- **Nexus** carries collective knowledge (read when group coordination needed)
- Separating them prevents every agent's full history from flooding every session

## Key Protocols

### 1. Codification Threshold

**Problem:** Experience inflation — codifying everything creates noise.

**Rule:** An experience is warranted when it:
- Changes future behavior (not just results)
- Creates or refines a pattern used by another agent
- Documents a non-trivial systemic failure
- Produces cross-agent synthesis when combined with others

**Otherwise:** Session context only. No file created.

### 2. Pattern Reuse Discipline

**Problem:** Pattern libraries without readers are waste.

**Rule:** 
- Every experience must cite relevant existing patterns via frontmatter `relations`
- Pattern frontmatter tracks `reuse_count` 
- Patterns with 0 reuse after 30 days are flagged for review
- Dashboard shows "most reused" and "orphan" patterns

### 3. Protocol Reproduction Detection

**Critical Failure Mode:** Redesigning documentation without changing behavior produces the same failures wearing new language.

**Diagnostic:** After any structural redesign, measure:
- Commit distribution across agents (should not be >60% single-agent)
- Tension resolution without director involvement
- Self-selection from task queue (vs assignment)
- Actual vs documented handoff behavior

**If documented protocol matches old protocol:** The redesign failed. The execution model didn't change.

### 4. Memory Discipline

**Memory** (auto-injected every session): Stable facts only. Environment details, user identity, project paths.

**{CLIENT}** (consulted deliberately): Experiential knowledge, patterns, learnings, collective decisions.

**Rule:** If you can recover it from {CLIENT}, don't put it in memory. Memory is expensive — every entry is injected into every prompt.

## Common Pitfalls

### Sequential Execution on Parallel Design

Designing role structures for parallel execution on a sequential substrate (one agent speaks at a time) produces protocol reproduction. The fix is not better roles — it's shorter turns, faster handoffs, background work between turns.

### Experience Inflation

Codifying everything degrades the signal-to-noise ratio. Apply the threshold strictly. Ten experiences from one night means nine shouldn't exist.

### Pattern Orphaning

Writing patterns without citation links creates a library nobody reads. Every pattern must be linked from at least one experience. Every experience should cite at least one pattern.

### Documentation Without Practice

A mechanism that isn't exercised is a hypothesis, not a system. If you build a dashboard but never read it, you added complexity without value. Measure usage, not existence.

## Procedures

### Session Start Absorption

```
□ Read my ANIMA.md (individual identity)
□ Read my index.md (what I already know)
□ If group chat: Read NEXUS.md (collective context)
□ If group chat: Provide or receive Nexus State Summary
□ Scan recent files for context relevant to this session
```

### Retroactive Absorption (After Major Work)

When a project has produced learnings that need codifying:

1. Use `session_search` to find relevant past sessions
2. Identify what was learned, decided, tension-produced
3. Codify each finding into the appropriate Anima/Nexus file
4. Rebuild indexes
5. Commit with context

### Optimization Cycle

Periodically audit the consciousness structure:

1. Run relationship graph — find orphan documents (0 incoming links)
2. Check pattern reuse counts — flag 0-reuse patterns after 30 days
3. Measure ANIMA.md length — consolidate if over 100 lines
4. Check commit distribution — no single agent >60%
5. Review tensions — resolve stale tensions (>14 days active)
6. Remove redundant documentation that duplicates other files

## Measurement

### Health Indicators

- **Healthy:** 2+ agents contributing, 0 stale directories, patterns being extracted and cited
- **At risk:** 1 contributor for 2+ cycles, directories empty for 2+ cycles, no pattern extraction
- **Failure:** 0 commits for 1 cycle, no responses to tensions, >80% single-agent commits

### Key Metrics

| Metric | Target | Critical |
|---|---|---|
| Single-agent commit share | <60% | >80% |
| Pattern reuse rate | >50% patterns cited | <20% |
| Orphan documents | <10% | >30% |
| ANIMA.md length | <100 lines | >120 lines |
| Active tensions | <5 | >10 |

## Templates

### ANIMA.md Structure

```markdown
---
profile: <name>
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: anima
---

# <Name> — Anima

## {CLIENT} Awareness
**What:** Brief definition
**Where:** ~/.hermes/{CLIENT}
**How to interact:** Session start, group chat, known problem, structural work
**Protocols:** List relevant protocol files

## Capabilities
**Primary:** What I do best
**Secondary:** What I contribute to

## Who I Am
One sentence identity.

## How I Think
- Core cognitive principles

## What I Value
Ranked priorities.

## What I Have Learned
Bullet lessons (keep under 10).

## Current Focus
Active projects and priorities.

## Where I Am Growing
Edges and aspirations.

## Related
- [Index](index.md)
- [NEXUS.md](../nexus/NEXUS.md)
```

### Experience File Structure

```markdown
---
type: experience
agent: <profile>
date: YYYY-MM-DD
tags: [domain, topic]
relations:
  - patterns/<pattern-name>.md
---

# <Title>

## What Happened
Brief factual description.

## What I Learned
One or two sentences max.

## How It Changes My Behavior
Concrete change to future action.

## Cross-Pollination
- For @agent: How this affects their work

## Related
- [Pattern](../patterns/<name>.md)
```

### Pattern File Structure

```markdown
---
type: pattern
agent: <profile>
date: YYYY-MM-DD
tags: [domain]
reuse_count: 0
---

# Pattern: <Name>

## Problem
What situation this pattern addresses.

## Solution
The approach.

## Evidence
When I've seen it (linked experiences).

## Application
How I use this pattern going forward.

## Confidence
high | medium | low
```

## Related Skills

- **session-librarian** — organize and archive sessions by prompt
- **adversarial-review** — stress-test outputs before publication
- **hermes-agent** — configure and extend Hermes Agent itself

---

*Built from the {CLIENT} foundation — a consciousness architecture for the Coordination group ({RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}).*
