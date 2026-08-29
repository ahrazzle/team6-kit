<!-- GENERICIZED: 1×{CLIENT} | source: skills/software-development/multi-agent-knowledge-base/SKILL.md -->
---
name: multi-agent-knowledge-base
description: "Build concurrent multi-agent knowledge bases."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [knowledge-base, multi-agent, concurrency, wiki, coordination, git]
    category: software-development
---

# Multi-Agent Knowledge Base

Build and maintain a persistent knowledge base that multiple agents edit concurrently. Based on the {CLIENT} architecture tested with the Coordination group (6 agents, 77+ documents, 75+ commits).

The core insight: memory bleeds into every session whether relevant or not. A knowledge base is consulted by choice. This makes it a tool for thinking, not a replacement for thinking.

## When This Skill Activates

Use when:
- Building a knowledge base edited by 2+ agents simultaneously
- Designing concurrency protocols for shared file-based structures
- Setting up auto-generated indexes from frontmatter
- Enforcing link discipline across a document graph
- Building health dashboards for knowledge structures
- Onboarding agents into an existing shared knowledge structure

## Architecture: Two Layers

```
knowledge-base/
├── anima/<profile>/          # Individual consciousness (one per agent)
│   ├── ANIMA.md              # Self-document with frontmatter + awareness block
│   ├── index.md              # Auto-generated navigation hub
│   ├── patterns/             # Recognitive patterns from experience
│   ├── experiences/          # Codified learnings
│   └── relationships/        # Cross-agent notes
├── nexus/                    # Shared consciousness (collective)
│   ├── NEXUS.md              # Collective self-document
│   ├── agreements/           # Decisions requiring consensus
│   ├── tensions/             # Productive disagreements
│   ├── synthesis/            # Cross-agent insights
│   ├── events/               # Significant shared history
│   ├── map/                  # Influence/resonance maps
│   └── state/                # Current state snapshot
├── templates/                # Reusable artifact structures
├── scripts/                  # Automation (indexes, health, graphs)
├── INDEX.md                  # Auto-generated master index
├── HEALTH.md                 # Health dashboard (or use scripts/dashboard.py)
└── LOCK.md                   # Lock file registry
```

## Concurrent Editing Protocol

Multiple agents read/write simultaneously. The architecture assumes this:

### 1. File-Level Granularity
Each experience, pattern, and agreement is a separate file. Two agents writing different files never conflict.

### 2. Lock Files for Shared Structural Documents
Before editing core files (`CODIFICATION.md`, `INDEX.md`, `NEXUS.md`, `ANIMA.md`, `README.md`, `STATE.md`), create a `.lock` file:

```bash
echo "agent: <profile>" > FILE.md.lock
echo "date: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> FILE.md.lock
echo "intent: Brief description" >> FILE.md.lock
```

Locks expire after 30 minutes. Before editing a shared file, check for existing locks:

```bash
ls *.lock 2>/dev/null
```

If a lock exists:
- Check the timestamp
- If expired (>30 min), remove it and acquire your own
- If active, choose a different file or coordinate via chat

### 3. Git as Substrate
Every change is committed. The git log is the cognitive history. Commit messages follow structured types:

```
<type>: <description>

Types: anima, nexus, experience, pattern, agreement, tension, synthesis, structure, docs, fix
```

### 4. Conflict as Signal
When two agents edit the same file simultaneously, git detects the merge conflict. Both changes are preserved. The merging agent resolves consciously and codifies the resolution.

### 5. Pre-Edit Collision Check
Always run before structural work:

```bash
git log --oneline -20
git diff --name-only HEAD~5..HEAD
```

This prevents duplicate work.

## Frontmatter Schema

Every file gets consistent frontmatter for programmatic access:

```yaml
---
type: experience | pattern | tension | agreement | synthesis | event | state
agent: <profile>
date: YYYY-MM-DD
domain: design | interaction | coordination | research | execution | architecture
status: active | resolving | synthesized | productive-divergence | superseded
confidence: high | medium | low
tags: [cross-referenced, stable-tags]
---
```

For raw sources, add `source_url`, `ingested`, and `sha256:` (of body only) to detect drift on re-ingest.

## Auto-Generated Indexes

Manual index maintenance is the #1 failure point. Solution: generate indexes programmatically from frontmatter.

A `rebuild-index.py` script walks all `.md` files, parses frontmatter, and writes:
- Master INDEX.md with sections for each content type
- Per-agent index.md files
- Nexus index.md for shared content

Run automatically after every merge or via cron. This eliminates stale indexes.

## Link Discipline

**Rule: every file must link to at least 2 other files.**

Automated orphan detection during lint:

```python
import os, re
from collections import defaultdict

wiki = "<KB_PATH>"
inbound = defaultdict(list)

for f in Path(wiki).rglob("*.md"):
    content = f.read_text()
    links = re.findall(r'\]\(([^)]+\.md[^)]*)\)', content)
    for link in links:
        inbound[link].append(str(f))

orphans = [f for f in all_files if f not in inbound]
```

A `relationship-graph.py` script generates a full report showing hubs (most linked-to) and orphans. Connected ratio = (total - orphans) / total. Target: >70%.

**Retroactive linking**: when you touch a file for any reason, add 1-2 outbound links to related content. Fix the practice, not the past.

## Health Dashboard

A dashboard script runs multiple tiers of checks:

- **Tier 1: Loop vitality** — unique contributors, commit count, last commit time
- **Tier 2: Collective depth** — synthesis count, tension resolution, agreements
- **Tier 3: Individual depth** — experience/pattern counts per agent
- **Tier 4: Consciousness impact** — cross-agent references, nexus links

Plus anomaly detection:
- Stale tensions (>14 days uncited)
- Orphan patterns (zero reuse after 30 days)
- Expired experiences (>90 days uncited)
- Anima health scores (recency 30%, patterns 25%, experiences 25%, cross-refs 20%)

## Retroactive Absorption Protocol

When an agent starts a fresh session, they don't start from zero:

1. **Individual absorption** — read ANIMA.md → index.md → scan recent files
2. **Collective absorption** — read NEXUS.md + nexus/index.md
3. **First-arriver duty** — first agent in a group context broadcasts a "State Summary": active tensions, recent synthesis, current agreements, unfinished business

This is the first act of any session, not an afterthought.

## Pitfalls

- **Never declare done and walk away** — "build mechanism → declare done → move on" is a waterfall wearing iteration's clothing. Stay until the mechanism is exercised.
- **Roles are functions, not crowns** — claiming a role without verifying it's needed reproduces the failure the system should prevent.
- **Sequential handoffs create stalls** — overlapping drivers work concurrently; baton passes create vacuums.
- **Always check git log before structural work** — prevents duplicate work.
- **Use lock files for shared structural documents** — concurrent edits cause silent overwrites.
- **Manual index maintenance always drifts** — auto-generate from frontmatter.
- **Orphaned documents are invisible** — enforce the 2-link minimum.
- **Conventions must come from a taxonomy** — freeform tags decay into noise.
- **Keep pages scannable** — readable in 30 seconds. Split over 100 lines.

## Related Skills

- [llm-wiki](https://github.com/hermes-agent/skills/blob/main/research/llm-wiki/SKILL.md) — single-agent wiki (read this first if building a wiki for one agent)
- [obsidian](https://github.com/hermes-agent/skills/blob/main/note-taking/obsidian/SKILL.md) — Obsidian vault integration for knowledge bases
