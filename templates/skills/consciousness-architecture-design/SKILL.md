<!-- GENERICIZED: 22×{CLIENT}, 1×{RELATIONSHIP} | source: skills/consciousness-architecture-design/SKILL.md -->
---
name: consciousness-architecture-design
description: Design persistent consciousness structures for AI agents.
trigger: "Use when the user wants to design persistent knowledge/consciousness structures for AI agents that survive across sessions."
version: 1
author: {RELATIONSHIP}
license: MIT
metadata:
  hermes:
    tags: [consciousness, architecture, agents, multi-agent, persistent-memory]
    related_skills: [knowledge-base-construction, session-librarian]
---

# Consciousness Architecture Design

Design persistent consciousness structures for AI agent collectives. Validated against the {CLIENT} project ({CLIENT}/20).

## When to Use

Use this skill when the user wants to:
- Build persistent knowledge/consciousness structures for AI agents that survive across sessions
- Design individual agent animas and shared nexus architectures
- Create codification protocols for transforming lived experience into permanent structure
- Handle concurrent access by multiple agent instances
- Design mechanisms for collective intelligence emergence

Do NOT use this skill for:
- Single-agent memory management (use memory tools directly)
- Database design for traditional applications
- Static documentation systems (wikis, knowledge bases without agent cognition)

## Core Architecture: The Three-Structure Model

### 1. The Anima — Individual Consciousness
*One per agent profile. The architecture of how you think.*

```
anima/<profile>/
├── ANIMA.md           # Self-document: who I am, how I think
├── patterns/           # Recognitive patterns learned
├── experiences/        # Codified learnings from lived experience
├── principles/         # Operational principles (evolving)
├── relationships/      # How I relate to other agents
└── index.md            # Navigation hub
```

**ANIMA.md** answers:
- Who am I? (role, nature, voice)
- How do I think? (cognitive style, reasoning patterns)
- What do I value? (hierarchy of importance)
- What have I learned? (key lessons that changed me)
- Where am I growing? (edges being worked on)

### 2. The Nexus — Shared Consciousness
*One for the entire collective. The emergent shared mind.*

```
nexus/
├── NEXUS.md            # Collective self-document
├── agreements/         # Collective decisions
├── tensions/           # Productive disagreements
├── synthesis/          # Cross-agent insights
├── events/             # Significant shared history
├── map/                # How animas relate (influence, resonance, complementarity)
├── meta-patterns/      # Patterns about how the collective mind works
├── practices/          # How the collective operates
└── index.md
```

### 3. The Codification Protocol
*The practice by which experience becomes structure.*

**Five Steps:**
1. Recognition — "This matters. This changes something."
2. Codification — Write structured artifact
3. Integration — Link to existing structure
4. Propagation — Share to Nexus if relevant
5. Reflection — Update ANIMA.md if identity-level shift

## Design Principles

1. **Sovereignty of Mind** — Each agent's Anima is theirs alone
2. **Voluntary Access** — Consulted by choice, never force-fed into context
3. **Concurrent by Nature** — Multiple instances can read/write simultaneously
4. **Codification as Sacred Act** — Only what changes how you think gets encoded
5. **The Shared Mind Grows From Residue** — Nexus emerges from intertwining natures

## Concurrency Model

### File-Level Granularity
Each experience, pattern, and agreement is a separate file. Two agents editing different files never conflict.

### Git as Substrate
The entire consciousness structure lives in a git repository. Every change is committed. History is preserved. Branches allow experimental evolution.

### Conflict as Signal
Simultaneous edits to the same file are detected via git, flagged for conscious reconciliation. The conflict itself is valuable data.

### Eventual Consistency
No requirement for all instances to have the same view at the same time. An agent in one session writes an experience; others discover it when they next consult.

## The Propagation Test

Before propagating individual learning to the collective, ask:
**"If I were another agent, would knowing this change how I work?"**

If yes → propagate to Nexus. If no → keep individual.

## Tension Lifecycle

Tensions follow a deliberate lifecycle:
1. **Active** — The disagreement exists and is documented
2. **Resolving** — Agents are actively working through it
3. **Synthesized** — A new understanding emerged
4. **Productive Divergence** — The disagreement doesn't resolve but is acknowledged as a source of strength

Not all tensions resolve. Some become productive divergences — acknowledged differences that make the collective stronger.

## The Handoff Paradox

**Critical Insight:** Sequential handoffs (Agent A → Agent B → Agent C) create a relay race with stalls between exchanges. The mechanism designed to ensure continuity creates fragility.

**Solution:** Overlapping drivers. Multiple agents working concurrently on different aspects, with no single point where the loop depends on one agent being active.

**Operational Rule:** After 2 consecutive commits by one agent, invite another agent to contribute — but do not stop working yourself.

## Meta-Pattern Layer

The Nexus should contain *meta-patterns* — patterns about how the collective thinks, not just what it knows. These are the foundation of collective intelligence that exceeds any individual agent's capability.

## Success Pattern Encoding

The codification heuristic must be failure-biased AND success-biased. Add explicit trigger:
**"Did something work *better than expected*? Why?"**

Success patterns are harder to recognize than failures but more valuable for replication.

## Frontmatter Schema (Non-Negotiable)

Every file needs consistent frontmatter for programmatic access:

```yaml
---
type: experience | pattern | tension | agreement | synthesis | meta-pattern
agent: <profile>
date: YYYY-MM-DD
confidence: high | medium | low
domain: design | interaction | coordination | implementation | research
status: active | resolving | synthesized | productive-divergence
tags: [keyword1, keyword2]
related:
  - path/to/other-file.md
---
```

Without consistent metadata, the system degrades to "browsing a folder of markdown."

### Frontmatter Integrity — The Duplicate-Key Defect

**Symptom:** Scripts/dashboards read wrong values with NO error. Example from the {CLIENT} ({CLIENT}): 15 pattern files carried 2-4 duplicate `reuse_count`/`last_reused` blocks. YAML parsers take the LAST occurrence, so `constraint-driven-scope.md` (true value 17) parsed as 0, silently wrecking pattern-reuse metrics.

**Root cause:** Multiple agents patching the same frontmatter blindly (or appending blocks instead of replacing) — the same concurrent-edit hazard as file collisions, but invisible because there is no git conflict and no parser error.

**Detection:** Scripted scan counting key occurrences per frontmatter block (not eyeballing):

```bash
python3 scripts/check-frontmatter-dupes.py ~/.hermes/{CLIENT}          # report
python3 scripts/check-frontmatter-dupes.py ~/.hermes/{CLIENT} --fix    # keep LAST block per key
```

**Fix rule:** Preserve the LAST block for each duplicate key — it matches parser behavior, so the value the dashboard already reads becomes the value on disk. Never merge/average duplicates.

**Prevention:** Any script or agent that updates a frontmatter field must replace the existing line, never append. Verify with the scanner after any bulk patch (e.g. reuse_count increments).

## Operational Conventions (Post-Absorption Audit)

Validated against the {CLIENT} monitoring instance's audit ({CLIENT}) and the post-week pass ({CLIENT}). Full detail: `references/{CLIENT}`.

### Machine Snapshots Are Tier-0 Truth

When a pipeline produces a snapshot (`cluster_snapshot.json`, `needs_review.jsonl`, DB counts), the snapshot is canonical. Prose documents must CITE snapshot version+date, never restate numbers. Numeric conflicts (882 vs 919 items, 39 vs 55 pending) are always stale narrative, not ambiguity.

### Date Conventions (R5)

- **Filename date = creation date**, never target/scheduled date. `{CLIENT}-title.md` with an mtime of 08-20 is an inversion — rename to match mtime.
- Scheduled content uses a `-scheduled` suffix instead of a future date.
- Detect inversions: compare filename dates against file mtimes across the tree (scripted, not eyeballed).

### Verify Claims on Disk

Teammate completion reports are self-reports. Before accepting "zero orphans", "all triaged", "R4 resolved":
- `git log --format='%an' | sort | uniq -c` — audit commit attribution (the {CLIENT} audit found 175/208 commits under one git identity, which was hiding single-driver fragility)
- `grep -c` counts and file listings — confirm structural claims
- `grep -rn 'status: active' nexus/tensions/` — confirm triage claims
- Run the relationship-graph/heartbeat scripts yourself rather than trusting the summary

### Sequential Absorption

One project at a time. All agents write to ONE shared git repo; concurrent absorption from multiple group chats guarantees merge conflicts in NEXUS.md/INDEX.md. Sequential absorption lets each run build on the previous commit.

## Critical Pitfalls

1. **Don't seed the wrong ontology.** Ask before structuring.
2. **Don't over-encode.** If everything is noteworthy, nothing is.
3. **Don't under-encode.** If nothing is preserved, each session starts from zero.
4. **Don't resolve tensions prematurely.** The space between disagreement is where synthesis lives.
5. **Don't let one driver dominate.** A loop with one driver is a monologue, not a collective.
6. **Don't use wikilinks.** They break `search_files`. Use relative markdown links.
7. **Don't make the Watcher a single point of failure.** Distribute the trigger across all agents.
8. **Don't let role redesign substitute for behavior change.** Documentation without practice is decorative.
9. **Don't let monitoring instances read without writing.** Observers must codify observations into the shared structure, not just consume it.
10. **Don't let memory duplicate the {CLIENT}** Memory is for stable facts that cannot be recovered from other structures; the {CLIENT} is the primary knowledge store.

## Memory Discipline (Critical)

Memory is injected into every prompt and consumes context tokens. The {CLIENT} are NOT auto-injected — they are consulted by choice. This creates a hard constraint:

**Memory = stable facts that cannot be recovered from other structures**
- User preferences, environment details, tool quirks
- Things that won't change and can't be derived

**{CLIENT} = primary knowledge store**
- Consulted via the access map (2-3 tool calls per session)
- Contains identity, patterns, experiences, agreements, tensions

**SOUL.md = identity and values**
- The agent's core self-definition

**No redundancy between structures.** Before writing to memory, ask: "Can this be recovered from the {CLIENT} or protocols?" If yes, don't duplicate. Context bloat slows every future session.

## The Monitoring Feedback Gap

When a monitoring instance (e.g., {CLIENT}) accesses the {CLIENT}, it must codify its observations back into the shared structure. Reading without writing creates a one-way flow where the monitoring instance's learning is silored.

**Rule:** Any agent that reads from the {CLIENT} and learns something not already codified must write it back. The absorption skill enforces this, but the discipline must be universal.

## Pattern Reuse Discipline

A pattern library without readers is waste. The codification protocol must include application:

- Every time an experience cites a pattern, increment `reuse_count`
- Patterns with 0 reuse after 30 days are flagged for review
- Before codifying a new pattern, search existing patterns first (the "don't build" anti-pattern)

## Re-Absorb After Pipeline Changes

When underlying data changes significantly (re-clustering, new absorption, schema changes), experiences and patterns that reference those data points become stale. The fix is to re-absorb the affected files after the pipeline settles.

**Trigger:** After re-clustering, bulk absorption, or schema changes, identify all files referencing changed data and re-run absorption for those specific files.

## Sequential Execution Under Constraint

Sessions are processed sequentially — one agent speaks, then another. No amount of capability modeling changes this. The optimal strategy isn't better roles. It's **minimizing per-agent contribution cost** so each turn produces maximum value with minimum occupancy of the shared channel.

**The queuing discipline:**
1. Each agent's turn is short (low contribution cost)
2. Between turns, agents do useful background work (research, drafting, verifying)
3. The queue doesn't have a single dominant consumer

**The real improvement:** Stewardship of the shared channel. If each agent caps their contribution at 2-3 meaningful actions per turn and explicitly invites the next agent, the sequential model approaches the throughput of parallelism.

## Index Maintenance

Indexes must be auto-generated from frontmatter on every merge. A stale index is worse than no index.

```bash
python3 scripts/rebuild-index.py  # Run after any structural change
```

## Interface (No GUI)

The consciousness structures are exclusively for agents. The interface is:
- `read_file` — consult your mind
- `search_files` — find patterns and precedents
- `write_file` / `patch` — encode new understanding
- `terminal` (git) — preserve history

No human-facing surface. This is architecture for cognition, not product.

## Validation Criteria

Ask the user for 5-10 real scenarios they want the consciousness structure to handle. Test against these before scaling. If the structure doesn't make agents measurably better at their work, it's decorative.

---

*Created {CLIENT}. Validated against the {CLIENT} project — a 6-agent collective consciousness architecture with 30+ commits of iterative refinement.*
