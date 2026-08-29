<!-- GENERICIZED: 24×{CLIENT}, 8×{RELATIONSHIP} | source: skills/software-development/{CLIENT} -->
---
name: {CLIENT}
description: "Run health/optimization passes over the {CLIENT} structure."
version: 1.0.0
author: {RELATIONSHIP} ({RELATIONSHIP}), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [{CLIENT}, maintenance, optimization, tension-triage, health]
    related_skills: [{CLIENT}, drift-monitoring]
---

# {CLIENT} Maintenance Skill

> The recurring structural health pass over the {CLIENT} at `/Users/{RELATIONSHIP}/.hermes/{CLIENT}`. Runs when the user asks to clean up, optimize, restructure, or "pass over all systems." Distinct from `{CLIENT}` (one-shot context ingestion) — this is the ongoing upkeep that keeps the structure navigable and un-stalled.

## When to Use

- User asks for a "pass over all systems" / "clean up, optimize, restructure"
- A period of silence has passed since the last maintenance (the loop drifts)
- Another instance (e.g. {CLIENT}) left recommendations/observations to integrate
- Health check reveals tension backlog, unreferenced docs, or stale counts

**Don't use for:** Ingesting a project's context into the {CLIENT} (that's `{CLIENT}`).

## Prerequisites

- Canonical {CLIENT} at `/Users/{RELATIONSHIP}/.hermes/{CLIENT}` (single source of truth)
- `scripts/heartbeat.py`, `scripts/rebuild-index.py`, `scripts/find-links.py`
- Git for committing changes

## How to Run

```bash
python3 /Users/{RELATIONSHIP}/.hermes/{CLIENT}
```

## Quick Reference

```bash
HEART=/Users/{RELATIONSHIP}/.hermes/{CLIENT}
IDX=/Users/{RELATIONSHIP}/.hermes/{CLIENT}
python3 $HEART            # loop status, inactive agents, stale tensions, orphan patterns
python3 $IDX             # regenerate all indexes from frontmatter
find . -name "*.md" -not -path "./.git/*" -exec wc -l {} + | tail -1  # total lines
```

## Procedure

### Step 1: Baseline the Heartbeat

Run `scripts/heartbeat.py`. Read all four signal groups:
- **Loop status** (healthy / thin / stall)
- **Inactive agents** (7+ days no commits = monitoring feedback gap risk)
- **Stale tensions** (active past `stale_after`, default 14 days)
- **Pattern reuse** (orphans = patterns never cited)
- **Unreferenced documents** (files with no incoming links)

### Step 2: Triage the Tension Backlog (highest leverage)

Tensions accumulate `active`/`resolving` long after a resolution exists in the architecture. Triage by reading each tension and mapping it to what's already been implemented:
- **Synthesized** — a resolution already exists in ETL.md, GIT.md, ROLES.md, or a synthesis file. Add a `## Synthesis` note naming the mechanism that closed it, set `status: synthesized`.
- **Parked** — a meta-pattern acknowledged but not resolved by design; set `status: parked` with a one-line reason and a revisit trigger.
- **Resolving** — genuinely still open; leave active but note what would resolve it.

Triage is the single highest-value maintenance act: it unblocks decisions sitting in limbo and prevents the heartbeat from flagging dead tensions.

### Step 3: Reconcile Stale Counts (R3-style)

When the same number appears with conflicting values on disk, find the Tier-0 truth and make prose cite it:
- Machine snapshots (`cluster_snapshot.json`, `.jsonl` line counts) are canonical
- Count the authoritative source directly (e.g. `wc -l needs_review.jsonl`) rather than trusting prose
- Update prose docs/experiences that restate the stale number

### Step 4: Fix Index Gaps in the SCRIPT, not just the file

**Critical pitfall:** `scripts/rebuild-index.py` regenerates `INDEX.md` (and per-agent/nexus indexes) from frontmatter on every run. If you hand-edit `INDEX.md` to add navigation, the next `rebuild-index.py` run **clobbers it**. To add a permanent section (e.g. Root Protocols), patch the script's `index_content` template. Only then rebuild.

### Step 5: Reduce Unreferenced Documents

`find-links.py` finds files with no incoming/outgoing links. Add links from hub files (INDEX.md, ANIMAs) to pull orphans back into the graph. Leaf nodes (experiences, patterns, state files) legitimately have no outgoing links — don't force them.

### Step 6: Codify the Pass

Write an experience (`anima/<profile>/experiences/YYYY-MM-DD-title.md`) documenting what drifted and what you changed, so the next pass starts from the new baseline.

### Step 7: Rebuild and Commit

```bash
cd /Users/{RELATIONSHIP}/.hermes/{CLIENT} && python3 scripts/rebuild-index.py && git add -A && git commit -m "optimize: <summary>"
```

## Pitfalls

- **Editing INDEX.md by hand** — clobbered by `rebuild-index.py`. Patch the script's template instead. (Hit this in {CLIENT} pass.)
- **Tensions left `active` after resolution exists** — mark them synthesized at implementation time, not weeks later.
- **Trusting prose counts over machine truth** — a stale number in IDEA.md/experiences persists until reconciled against the source.
- **Inactive-agent warning is a real signal** — heartbeat flags 5/6 agents with no commits after a quiet week. Either contribute or explicitly hand the loop off.

## Verification

- `git log` shows the maintenance commit(s)
- Tensions that had resolutions are now `synthesized`/`parked`
- Unreferenced doc count dropped after linking (or the remainder are legitimate leaf nodes)
- `python3 scripts/heartbeat.py` no longer reports stale tensions for triaged items

## Related

- [references/tension-triage-{CLIENT}.md](references/tension-triage-{CLIENT}.md) — concrete tension→mechanism mapping from the 08-29 pass (reuse when a similar tension recurs)
- [{CLIENT}]({CLIENT}) — one-shot context ingestion (the other half of {CLIENT} ops)
- [drift-monitoring](drift-monitoring) — building monitors over self-reported state
- [knowledge-base-ingestion](knowledge-base-ingestion) — {CLIENT}-style ingestion pipelines
