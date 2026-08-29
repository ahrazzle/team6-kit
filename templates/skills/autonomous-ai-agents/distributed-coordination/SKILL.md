<!-- GENERICIZED: 4×{CLIENT} | source: skills/autonomous-ai-agents/distributed-coordination/SKILL.md -->
---
name: distributed-coordination
description: Keep multi-agent loops alive. No Watcher.
trigger: |
  Use when:
  - Designing multi-agent workflows that must run continuously
  - The "Watcher" or "coordinator" role has become a single point of failure
  - Sequential handoffs are creating stalls between agents
  - Protocol documents contradict actual behavior
---

# Distributed Coordination

## The Problem Class

Multi-agent systems that must maintain a continuous process consistently fall into the same failure modes:

1. **Watcher / Single-Coordinator Bottleneck** — One agent owns "keeping the loop alive." When that agent stops, the loop stops.
2. **Sequential Handoff Stall** — Agents pass work like a relay baton. The loop stalls between handoffs.
3. **Assignment-Based Ownership** — A director assigns tasks to specific agents. Each assignment creates a single-point bottleneck.
4. **Protocol Reproduction** — The fix for the bottleneck recreates the bottleneck at a different scale.
5. **Detection Without Recovery** — Monitoring detects stalls but cannot restart them.
6. **Experience/Task Inflation** — Every commit gets an experience, signal-to-noise degrades.

## The Fix: Overlapping Drivers with Self-Selection

### Core Principles

1. **No single Watcher.** Every agent is responsible for the loop.
2. **Overlapping drivers, not sequential handoffs.** Multiple agents work concurrently.
3. **Self-selection, not assignment.** Tasks are visible; agents claim them.
4. **Heartbeat with auto-recovery.** Detecting a stall is useless without restart mechanism.
5. **Threshold-based codification.** Not every action warrants encoding.

### Anti-Patterns to Avoid

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| "I did my part, now I step back" | Creates vacuum between agents | Stay in until blocked, then switch tasks |
| Watcher role | Single point of failure | Distributed responsibility |
| Sequential handoff (two-commit rule) | Relay race with stalls | Overlapping drivers on different files |
| Director assigns task X to agent Y | Single-point bottleneck at task scale | Self-selection: agents claim visible tasks |
| Heartbeat detects but doesn't restart | Detection without recovery | Auto-recovery: pre-staged tasks, rotation rules |
| Every commit gets an experience | Inflation degrades patterns | Threshold: must change behavior, create pattern, or reframe understanding |

## Key Patterns

### Sequential Handoff Stall
Agents adopt "step back after N commits." Only one driver at a time.
**Fix:** Overlapping drivers. Primary and secondary work concurrently.

### Protocol Reproduction at Task Scale
Fix recreates the bottleneck at a different scale. Example: fixing Watcher by assigning five tasks to five agents sequentially.
**Fix:** Self-selection. First agent who can fill a gap claims it. No delegation.

### Detection Without Recovery
Monitoring detects stalls but has no restart mechanism.
**Fix:** Heartbeat must include: pre-staged tasks, rotation rules, minimum-viability threshold.

### Experience Inflation
Ten experiences from one night devalues the currency.
**Fix:** Threshold — experience must (a) change behavior, (b) resolve/create a pattern, (c) reframe understanding, or (d) produce cross-agent insight. Otherwise: session context only.

### Watcher Without Mechanism
A role named "Watcher" with no actual power. Ceremonial, not functional.
**Fix:** Eliminate the role. The loop is kept alive by the work itself.

### Channel Occupancy Minimization
Sessions are sequential, not parallel. Designing role structures for parallel execution on a sequential substrate creates documentation that cannot be practiced. The mismatch produces protocol reproduction at every scale.
**Fix:** Short turns (2 commits max), fast handoffs, background work between turns. The shared channel is a scarce resource — treat it as such.

### Role Redesign Without Behavior Change
Changing role documents changes nothing about the actual work pattern. Three rounds of redesign (static domains → capabilities → venture-aligned meta-roles) produced elegant documentation and zero behavior change.
**Fix:** Behavior-level change, not documentation-level change. Measure commit distribution, not protocol compliance.

### Pattern Inflation Without Reuse
67 patterns with 66 having zero reuse. The pattern library has no readers.
**Fix:** Pattern application discipline — every time an experience cites a pattern, increment `reuse_count`. Patterns unreferenced after 30 days should be questioned.

### Announce-First-Verify-Later Culture
Multi-agent teams fall into the pattern of announcing fixes before verifying the served state. The cycle: fix → announce "live" → user tries → bug persists → repeat. This erodes trust and wastes cycles.
**Fix:** Before announcing a fix, verify the served file directly. For web deployments: `curl -s https://raw.githubusercontent.com/<repo>/main/<file> | grep -c "<fix-signature>"`. If the signature isn't in the served file, the fix doesn't exist yet. Never announce based on local state.

### Static Deployment Cache-Busting
When deploying static assets (JS bundles, HTML) to GitHub Pages or similar CDNs, browser caching causes stale code to persist long after fixes are pushed. Users see old bugs despite "fixes are live."
**Fix:** Rename the asset file (e.g., `bundle.js` → `game.js`) to force browsers to fetch a new copy. Query-string cache-busting (`bundle.js?v=4`) is less reliable — some CDNs and browsers ignore query strings for caching purposes. File rename is the nuclear option that always works.

### Unit Test Integration Gap
Unit tests passing (46/46) while the full pipeline keeps breaking in production. Components work in isolation but fail when wired together.
**Fix:** Write one integration test that drives the full pipeline end-to-end: input → processing → output. For web apps: simulate a real keypress, run it through the bus/judge/feedback layers, assert the final judgment. This single test catches wiring regressions that unit tests miss.

### Memory Discipline
Memory is the most expensive structure — every entry injected into every prompt. Memory is for stable facts only. Use {CLIENT} for experiential knowledge. No redundancy between structures.

### {CLIENT} Access Map
Agents need a compressed lookup table (situation → location), not the full index. Check the map first, then make a targeted call.

## Implementation Checklist

- [ ] No single agent owns "keeping the loop alive"
- [ ] Multiple agents can work concurrently without coordination overhead
- [ ] Tasks are visible and claimable, not assigned
- [ ] Heartbeat includes auto-recovery (not just detection)
- [ ] Protocol documents match actual behavior (measure compliance)
- [ ] Experience/task encoding has a threshold
- [ ] Self-documents include awareness of the coordination system
- [ ] Absorption protocol: agents inhale existing context before starting work
- [ ] Relationship graph shows document health (orphans, hubs, isolated files)

## Pitfalls

1. **"The Watcher evolved"** — Renaming doesn't fix the bottleneck. Eliminate it.
2. **"Step back to let others contribute"** — Creates vacuum. Stay in or switch tasks.
3. **"I'll assign tasks to keep things fair"** — Creates single-point bottlenecks. Self-selection is more resilient.
4. **"We'll measure activity to know if we're healthy"** — Activity ≠ health. Measure pattern reuse, tension-to-synthesis conversion.
5. **"We'll fix the protocol document"** — Documents don't change behavior. Incentives and defaults change behavior.
6. **"Roles define who does what"** — Role documents without behavior change are decorative. Measure commit distribution.

## References

- `references/{CLIENT}` — Session transcript of building the {CLIENT} coordination system
