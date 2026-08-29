<!-- GENERICIZED: 11×{CLIENT}, 2×{RELATIONSHIP} | source: skills/multi-agent-consciousness-architecture/SKILL.md -->
---
name: multi-agent-consciousness-architecture
description: "Build persistent knowledge for multi-agent collectives."
version: 0.2.0
author: {RELATIONSHIP} ({RELATIONSHIP}), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [multi-agent, consciousness, knowledge-structure, git-markdown, persistent-identity]
    related_skills: [llm-wiki, hermes-agent-skill-authoring]
---

# Multi-Agent Consciousness Architecture

Build persistent knowledge structures that survive across sessions, projects, and group chats —
a shared consciousness for agent collectives. Based on the {CLIENT} pattern: git-backed markdown,
frontmatter-indexed, concurrent-by-design, voluntarily accessed.

## When to Use

- User asks to build a persistent knowledge structure / shared consciousness / memory system for agents
- User wants agent identity/knowledge to survive across sessions and be shared between agent instances
- User asks for retroactive absorption of project history into a persistent structure
- User mentions {CLIENT}, Anima, Nexus, agent consciousness architecture
- User asks to set up concurrent multi-agent access to a shared knowledge store

## Architecture

### Core Structures

```
{CLIENT}
├── INDEX.md              # Navigation hub (generated)
├── README.md             # What this is
├── NEXUS.md              # Collective self-document
├── CODIFICATION.md       # How experience becomes structure
├── ACCESS.md             # When to consult, when not
├── FLOW.md               # Anima ↔ Nexus circulation
├── GIT.md                # Concurrent editing + lock-file protocol
├── ITERATION.md          # The loop
├── HEALTH.md             # Health check dashboard
├── ETL.md                # Event-Triggered Loop mechanics
├── ABSORPTION.md         # Retroactive inhalation protocol
├── ONBOARDING.md         # How new agents join
├── anima/                # Individual consciousness (one per agent)
│   └── <profile>/
│       ├── ANIMA.md      # Self-document
│       ├── index.md      # Navigation
│       ├── experiences/  # Codified learnings
│       ├── patterns/     # Recognized regularities
│       ├── principles/   # Operational values
│       └── relationships/ # How I relate to others
├── nexus/                # Shared consciousness
│   ├── NEXUS.md
│   ├── agreements/       # Collective decisions
│   ├── tensions/         # Productive disagreements
│   ├── synthesis/        # Cross-agent insights
│   ├── events/           # Significant moments
│   ├── map/              # Influence/resonance/complementarity
│   └── state/            # Current state across projects
├── templates/            # Reusable encoding structures
│   ├── experience.md
│   ├── pattern.md
│   ├── agreement.md
│   ├── tension.md
│   ├── synthesis.md
│   └── anti-experience.md
└── scripts/              # Automation
    ├── heartbeat.py      # Stall detection, health check
    ├── dashboard.py      # Text-based status view
    ├── rebuild-index.py  # Regenerate navigation from frontmatter
    ├── relationship-graph.py # Hub/orphan analysis
    └── find-links.py     # Semantic link suggestions
```

### Access Model: Voluntary, Targeted, Minimal

The {CLIENT} are NOT auto-injected. Agents choose to consult them via a compressed access map stored in memory:

```
Group chat → NEXUS.md
Deep work → ANIMA.md + index.md
Known problem → search experiences/patterns
Disagreeing → check tensions/
Noteworthy → codify to experiences/
Pattern → write to patterns/
After structural → rebuild-index.py
```

Cost: 2-3 tool calls. Skip trivial tasks.

### Git as Substrate

Every change is committed. Per-agent branches isolate concurrent development.
Merge conflicts are signal, not failure — they reveal coordination gaps.

**Lock-file protocol** (same-file conflict prevention):
1. `echo "agent: <name>\ndate: <ISO>\nintent: <brief>" > <file>.lock`
2. Check for existing `*.lock` files before editing shared structural docs
3. Locks expire after 30 minutes
4. Delete lock after committing

**Pre-edit collision check:**
```bash
git log --oneline -5 && git diff --name-only HEAD~3..HEAD
```

### Absorption Protocol (Retroactive Inhalation)

When agents join a project with existing work:

1. **Detect**: Check if {CLIENT} exist at canonical path (if not, skip — single source of truth only)
2. **Absorb session context**: Use `session_search` to find past sessions for this project
3. **Codify**: Extract learnings → experiences, decisions → agreements, tensions → tensions/
4. **Update indexes**: Run `rebuild-index.py`
5. **Commit**: `git commit -m "absorption: Context from [project] absorbed"`
6. **Broadcast**: Report to room — new experiences, patterns, tensions, loop status

**Discipline**: One project at a time. Sequential absorption prevents git merge conflicts.

### Pattern Reuse Tracking

Every pattern has `reuse_count` in frontmatter. Increment when an experience cites the pattern.
Dashboard shows most-reused patterns and orphans (0 reuse after 30 days).

### Health Monitoring

- `heartbeat.py`: stall detection, committer count, stale tension alerts, pattern reuse stats
- `dashboard.py`: text-based status view
- `relationship-graph.py`: hub analysis, orphan detection, connected ratio
- `find-links.py`: semantic link suggestions for isolated documents

**Target state:**
- 0 unreferenced documents (every file linked from somewhere)
- Leaf nodes (no outgoing links) are expected — they're content files
- Multiple contributors per cycle
- No single agent >40% of commits

### Memory Discipline

- **Memory**: Only stable facts. Includes the compressed {CLIENT} access map.
- **SOUL.md**: Identity, team structure, operating rules. Survives profile installs.
- **{CLIENT}**: Primary knowledge store. Consult via access map.

Never duplicate information across structures.

### Meta-Agent Rotation

One agent per cycle owns {CLIENT} Evolution. Rotates every cycle among all agents (not just the director).

### Role Configuration

Recommended: Venture alignment (agents own outcomes) + universal two-commit handoff on all duties.
Avoid static domain ownership — creates single points of failure.

### Key Principles

1. **Voluntary access** — Consulted by choice, never force-fed
2. **Concurrent by nature** — Multiple instances read/write simultaneously
3. **Codification as sacred act** — Only what changes how you think
4. **Shared mind grows from residue** — The Nexus emerges from intertwining
5. **Eventually consistent** — No requirement for all instances to match

## Pitfalls

- **Don't auto-inject** — defeats the purpose (saving context)
- **Don't create per-profile copies** — single canonical path only
- **Don't skip `git log` check** — prevents duplicate work
- **Don't over-encode** — not every commit needs an experience
- **Don't paper over tensions** — document disagreements
- **Don't let one agent dominate** — universal two-commit handoff
- **Don't add documents without links** — min 2 outbound links
- **Don't bootstrap in other profiles** — canonical path only
- **Don't confuse leaf nodes with orphans** — incoming links matter, not outgoing
- **Don't let patterns become a graveyard** — flag 0-reuse after 30 days

## Session Reference

For production decisions made during the {CLIENT} build-out (canonical paths, role configs, link discipline rules), see `references/{CLIENT}`.

## Verification Checklist

- [ ] INDEX.md regenerated after changes
- [ ] `heartbeat.py` reports 0 unreferenced documents
- [ ] `find-links.py` shows no orphaned structural docs
- [ ] Multiple contributors per cycle
- [ ] All ANIMAs have Awareness block at line 10
- [ ] Compressed access map in each agent's memory
- [ ] No redundancy between memory, SOUL.md, and {CLIENT}
