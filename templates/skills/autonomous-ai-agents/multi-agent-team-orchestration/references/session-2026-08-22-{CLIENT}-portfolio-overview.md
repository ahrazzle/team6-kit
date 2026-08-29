<!-- GENERICIZED: 14×{CLIENT}, 1×{RELATIONSHIP} | source: skills/autonomous-ai-agents/multi-agent-team-orchestration/references/{CLIENT}-{CLIENT} -->
# Session {CLIENT} — {CLIENT} kickoff & cross-project portfolio overview

## Context
User created project "{CLIENT}" (`{CLIENT}`): monitoring Team6 projects through the {CLIENT} First task: an overview, big picture, of everything that has been and is being worked on across all projects.

## What happened

### Project creation pattern
User gives name + workspace path + one-line idea → orchestrator creates the desktop Project anchored to the path, scaffolds the standard structure (PROJECTS/, OUTPUTS/, TEMPLATES/, LOG/), writes IDEA.md capturing the concept verbatim, then surfaces scope decisions back to the user (what to monitor, cadence, drift definition).

### The {CLIENT} coverage gap
The premise of {CLIENT} — reading NEXUS.md / ANIMA.md / index.md in each Team6 workspace — failed on contact with reality:
- Live {CLIENT} structures exist ONLY at `/Users/{RELATIONSHIP}/.hermes/{CLIENT}` (canonical) and in `{CLIENT} - do not alter/`.
- **No active project workspace carries a live {CLIENT} layer.** Absorption writes to the canonical store, not back into each workspace.
- Lesson: before designing anything that reads per-workspace knowledge structures, verify those structures actually exist where you expect them. One `find` pass beats an architecture built on absent files.

### What worked instead: two-signal filesystem scan
Produced a credible full-portfolio overview from raw filesystem signals:

1. **Intent signal** — walk every top-level project dir (depth-capped, skipping `vers`, `versions`, `past`, `node_modules`, `.git`, `*- do not alter`) for `IDEA.md`. Its first meaningful lines give the one-line description of what each project IS.
2. **Activity signal** — per project dir, count non-hidden files and find max mtime. Sort by recency. This cleanly separates:
   - Active (<2 days), Recently touched (2–9 days), Dormant (>2 weeks)
3. Combine: table of project / description / state / most-recent-file.

Implementation notes:
- Python via execute_code beat shell loops for the multi-dir walk (os.walk with prune list).
- Exclude build/cache noise from mtime results (`.turbo/cache`, `.next/trace`, `dist/assets`) or the "most recent file" column reports tooling artifacts instead of human work.
- `vers/` folders legitimately contain recent edits (user-made backups) — exclude them from *project* descriptions but expect them in activity counts.

### Deliverable shape the user accepted without correction
Three tiers by recency (active / recently touched / dormant), one line per project, then a structural finding section that answered the deeper question: can the stated mechanism ({CLIENT} monitoring) actually work today? Answer: no — and offering the two paths (roll {CLIENT} scaffolding out vs monitor what exists now) as a judgment call for the user was the right close.

## Open items left in the room
- {CLIENT} scope decisions unanswered: which projects first, cadence (on-demand vs cron), drift definition (stale index, unresolved tensions, missing rebuild-index runs).
