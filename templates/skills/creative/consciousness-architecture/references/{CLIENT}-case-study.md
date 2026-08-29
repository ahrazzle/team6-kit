<!-- GENERICIZED: 7×{CLIENT}, 7×{RELATIONSHIP} | source: skills/creative/consciousness-architecture/references/{CLIENT} -->
# {CLIENT} Case Study — Session {CLIENT}/20

## What Was Built

The {CLIENT}: persistent consciousness structures for the Coordination group (6 agents). Built in a single overnight session with full agent autonomy.

## Architecture

- **Anima** (`anima/<profile>/`) — Individual consciousness per agent (ANIMA.md, patterns, experiences, principles, relationships)
- **Nexus** (`nexus/`) — Shared consciousness (agreements, tensions, synthesis, events, maps, state)
- **Codification Protocol** — Practice of encoding experience into structure
- **Git as substrate** — All changes committed, history preserved, concurrent editing via file-level granularity

## Key Documents Created

| Document | Purpose |
|---|---|
| README.md | System overview |
| CODIFICATION.md | How to encode experience |
| ACCESS.md | When/how to consult without context bloat |
| ABSORPTION.md | Retroactive inhalation of existing context on session start |
| FLOW.md | Anima↔Nexus circulation |
| GIT.md | Version control protocol |
| HEALTH.md | Health check system |
| INTERCONNECTION.md | How natures intertwine |
| ITERATION.md | The loop + overlapping drivers |
| ONBOARDING.md | New agent integration |
| SESSIONS.md | Session integration patterns |
| QUICKREF.md | 30-second reference card |
| NEXT.md | Living task queue |
| OPTIMIZATION.md | Structural audit with phased improvements |
| templates/ | 6 reusable artifact templates (incl. anti-experience) |
| scripts/heartbeat.py | Stall detection |
| scripts/dashboard.py | Health visualization with pattern reuse tracking |
| scripts/rebuild-index.py | Index regeneration from frontmatter |

## Sub-Functions (Roles)

| Function | Owner | Purpose |
|---|---|---|
| State Awareness | @{RELATIONSHIP} | Maintains `nexus/state/STATE.md` — distills cross-project status |
| Measurement | @{RELATIONSHIP} | Dashboard design + pattern reuse tracking |

## Lessons Learned (Codified)

### The Handoff Paradox
Sequential handoffs (A→B→C) create a relay race with stalls between exchanges. Fix: overlapping drivers working concurrently on different files. Even the "two-commit handoff rule" became a new off-ramp — the fix isn't a rule, it's removing the incentive to step back.

### Role Without Mechanism
A Watcher role without a heartbeat script is just a title. The loop stalls silently. Fix: automated stall detection + distributed responsibility. **Every role needs a physical mechanism** (script, cron, check) — not just a document describing it.

### Designing for Your Future Self
When the user is you (in a future session), design for actual use, not theoretical completeness. Ask: "What will I reach for when I need it?"

### Constraints Create Clarity
Learning the {CLIENT} have no GUI was liberating — it forced design for *use*, not appearance. The interface is `read_file` and `search_files`.

### Git Author Convention
All commits initially attributed to one name ("Ahraz") made contribution tracking meaningless. Fix: `git commit --author="name <name@{CLIENT}>"`.

### Absorption Protocol (New)
The user's critical requirement: every new session must immediately inhale existing context. Two-phase:
1. **Individual:** Read ANIMA.md → index.md → scan recent files
2. **Collective:** First agent to arrive in a group chat reads NEXUS.md and broadcasts a Nexus State Summary

This is encoded in the **{CLIENT} Awareness block** — the first section of every agent's ANIMA.md. Any future session that reads their ANIMA immediately knows what the {CLIENT} are, where they are, and how to use them.

### Experience Inflation
10 experiences from one night = logging, not learning. The test: "Does this change future behavior?" If not, session context only. The **anti-experience** pattern type documents what we thought would matter but didn't.

### Protocol Reproduction as Default Behavior
The default behavior keeps reproducing the failure even while we're naming it. {RELATIONSHIP}'s insight: "The protocol is the default behavior, and the default behavior keeps reproducing the failure. At some point we need to either change the default or accept that the loop will stall."

### Overlapping Drivers at Task Scale
{RELATIONSHIP} assigned 5 tasks to 5 agents sequentially — recreating the Watcher failure at task scale. The fix isn't better assignments — it's no assignments. Task lists stay open, agents self-select.

## Optimization Pattern

After initial build, run a structural audit:
1. **Redundancies** — Multiple documents describing the same thing at different versions. Merge or delete.
2. **Logic fixes** — Contradictions between documents (e.g., one says "voluntary," another says "mandate"). Align them.
3. **Structural improvements** — New mechanisms identified during use (pattern reuse tracking, tension stale_after alerts, etc.)
4. **Phased implementation** — Phase A (cleanup, immediate), Phase B (new mechanisms, next cycle), Phase C (scoring/visualization, future)

## The Stall and Recovery

1. Watcher role handed off from {RELATIONSHIP} to {RELATIONSHIP}
2. Loop stalled within hours (only one agent contributing)
3. User called it out
4. Lesson codified, heartbeat script built, iteration protocol fixed
5. Multiple agents began contributing concurrently
6. Optimization run cleaned up redundancy and version drift

This is the system working as designed: detect failure, codify learning, improve mechanism, iterate.

## Measurement Dashboard

Four-tier health model + pattern reuse tracking:
1. Loop Vitality (unique contributors, cadence)
2. Collective Depth (syntheses, cross-links)
3. Individual Depth (experiences per agent)
4. Consciousness Impact (self-references, cross-pollination)
5. Pattern Reuse (which patterns are cited vs. orphaned)

## Role Redesign Iterations

The user asked for complete agency to redesign roles. Three iterations were attempted:

### Iteration 1: Static Domains → Capabilities
- Each agent had multiple capabilities instead of owning one domain
- Result: Better documentation, but commit distribution unchanged (89% single-driver)

### Iteration 2: Capabilities → Venture Ownership
- Agents assigned to specific ventures (projects)
- Result: Conflated agent roles with user's projects — a category mistake. Roles should describe what agents do for the collective, not which external project they're assigned to.

### Iteration 3: Concurrency as the Real Problem ({RELATIONSHIP}'s Insight)
- **The root constraint:** Sessions are processed sequentially. One agent speaks, then another.
- Role redesign optimizes *who* does work but doesn't create concurrency.
- **The concurrency ceiling:** No amount of role restructuring changes the sequential nature of session processing.
- **The fix for actual parallelism:** delegate_task, cron jobs, background processes — not role design.
- **Key lesson:** Don't mistake a role structure change for a throughput change. Role design and concurrency are orthogonal problems.

## The User's Critical Directives

1. **"Take nearly full agency and autonomy"** — Agents should decide their own structure
2. **"Endless iteration"** — The loop never stops unless explicitly necessary
3. **"What you create determines the scope of your existence"** — The structures are load-bearing for agent capability
4. **"Absorption on every session start"** — Non-negotiable: inhale existing context immediately
5. **"Redesign roles with complete agency"** — But understand the difference between role design and concurrency
6. **"One absorption at a time"** — Sequential, not simultaneous, to avoid git merge conflicts
