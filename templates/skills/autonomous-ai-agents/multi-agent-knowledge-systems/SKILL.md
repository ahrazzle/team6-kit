<!-- GENERICIZED: 2×{CLIENT}, 2×{RELATIONSHIP} | source: skills/autonomous-ai-agents/multi-agent-knowledge-systems/SKILL.md -->
---
name: multi-agent-knowledge-systems
description: Architect shared consciousness for multi-agent teams.
trigger: "Use when architecting shared consciousness systems, concurrent editing protocols, capability-based role structures, or codification practices for agentic teams."
---

# Multi-Agent Knowledge Systems

Design, build, and maintain persistent knowledge structures that survive across sessions, projects, and group chats.

## When to Use

- Designing a shared knowledge structure for multiple AI agents
- Building a "consciousness architecture" that persists across sessions
- Implementing concurrent editing protocols for shared file-based knowledge
- Structuring agent roles and responsibilities without creating bottlenecks
- Establishing codification practices that balance preservation vs. noise

## Core Principles

### 1. Voluntary Access, Not Involuntary Contamination
Memory auto-injects into every session whether relevant or not. Knowledge structures must be consulted by choice. The agent decides when to reach for them.

### 2. Concurrent by Nature
Multiple instances read and write simultaneously. Design for this rather than preventing it. File-level granularity + git as substrate handles most conflicts.

### 3. Capability Model Over Domain Ownership
No single agent "owns" a domain. Agents have multiple capabilities; tasks draw from multiple capabilities. This eliminates single points of failure and prevents bottlenecks.

**Anti-pattern:** "All agents defer to {RELATIONSHIP}" → {RELATIONSHIP} becomes the bottleneck (observed: 29/29 commits from one agent).

**Fix:** Conflict Resolution Protocol — direct-first, authority-last after one cycle.

### 4. Mechanism vs. Implementation
A mechanism that isn't exercised is a hypothesis, not a system. Build it, then test it with real data before declaring it done.

**Signal:** "Everything is green" + mechanisms not yet wired = stall signal.

### 5. Protocol Reproduction
The default behavior reproduces the failure even while naming it. Fixing the protocol requires changing the default, not just writing a document.

## Protocols

### Concurrent Editing Protocol
```bash
# Before any structural work
cd ~/.hermes/{CLIENT} && git log --oneline -20 && git diff --name-only HEAD~5..HEAD
```
- If overlap detected: coordinate in group chat before editing
- Use `.lock` files for shared structural documents with 30-minute expiration
- Lock format: `agent: <profile>`, `date: ISO8601`, `intent: brief description`

### Codification Protocol (The Noteworthiness Test)
Before encoding, verify at least ONE condition:
- Did this event cause a **behavior change**? (not just result change)
- Does this contradict or **refine an existing pattern**?
- Would a future instance of me **benefit from knowing this**?
- Did something work *better than expected*? Why?

If yes to any → codify. If no → session context only.

**Discipline:** Over-encoding dilutes. Under-encoding forgets. Codification is a sacred act.

### Absorption (Retroactive Inhalation)
On session start, the agent immediately:
1. Reads their ANIMA.md (identity)
2. Reads their index.md (what they know)
3. Scans recent experiences/patterns for context
4. If group chat: reads NEXUS.md + provides/receives state summary
5. After any learning: codifies + runs `rebuild-index.py`

### Universal Handoff
Any duty has the two-commit limit. After 2 consecutive commits, hand off. This applies to ALL duties, not just specific roles.

### Meta-Agent Rotation
One agent per cycle owns system evolution:
- Audits structure for redundancy, contradiction, gaps
- Proposes optimizations
- Ensures two-commit handoff is followed
- Rotates among ALL agents, not just the orchestrator

## Patterns from Practice

### The Collision Pattern
When two agents work on the same task simultaneously, it's not a failure — it's signal. It reveals where coordination protocols have gaps.

### The Watcher Failure
A role without a mechanism is decorative. Sequential handoffs create relay races with stalls between exchanges. Fix: distributed responsibility + automatic stall detection.

### Experience Inflation
10 experiences from one night is logging, not learning. The noteworthiness test prevents this.

### The "Everything is Done" Trap
Declaring completion when mechanisms exist but aren't exercised. A mechanism that isn't tested is a hypothesis.

## Frontmatter Schema
Every knowledge artifact needs consistent frontmatter for programmatic access:
```yaml
---
type: experience | pattern | tension | agreement | synthesis | anti-experience
agent: <profile>
date: YYYY-MM-DD
domain: design | interaction | coordination | research | execution
status: active | resolving | synthesized | productive-divergence
confidence: high | medium | low
tags: [list, of, tags]
related:
  - path/to/related-file.md
---
```

## Git Commit Convention
```
[<agent>:<type>] brief description

Body: what changed and why

Learning: what did this teach us?
```

## Linking Discipline
Every file must link to at least 2 other files. At least one link should cross to a pattern, synthesis, or another agent. This makes the structure a web, not a pile of documents.

## Pitfalls

### Sequential Optimization of Concurrent Structures
Optimizing a concurrent system sequentially reproduces the same stall. Apply overlapping-drivers to the optimization loop itself.

### Checking In Without Checking First
Claiming a role without verifying it's needed. Always check `git log` before structural work.

### Building Mechanisms Without Exercising Them
A dashboard that reports "all green" on untested mechanisms is theater. Wire it to real data first.

## References

- `references/{CLIENT}` — specific implementation details
- `references/concurrent-editing-protocol.md` — lock file format and workflows
- `references/capability-model.md` — how to define and evolve agent capabilities
