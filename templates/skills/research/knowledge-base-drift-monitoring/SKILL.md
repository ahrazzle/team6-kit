<!-- GENERICIZED: 8×{CLIENT}, 1×{RELATIONSHIP} | source: skills/research/knowledge-base-drift-monitoring/SKILL.md -->
---
name: knowledge-base-drift-monitoring
description: "Use when watching a knowledge store for drift over time."
version: 1
author: {RELATIONSHIP}
license: MIT
metadata:
  hermes:
    tags: [monitoring, drift-detection, knowledge-base, cron, verification]
    related_skills: [knowledge-base-construction, {CLIENT}]
---

# Knowledge Base Drift Monitoring

Watch a living knowledge store ({CLIENT}, {CLIENT}, project doc trees) for internal decay: contradictions between documents, stale metadata, abandoned threads, facts that no longer match machine state. Validated while scoping {CLIENT} v1 ({CLIENT}). Monitoring is read-only — it never edits the watched stores.

## When to Use

- A curated corpus is edited by multiple agents over time and no single writer controls consistency
- The user asks for a "monitoring layer", drift reports, health checks, or scheduled audits of a doc/KB structure
- After a KB build (see `knowledge-base-construction`) — monitoring is the post-build lifecycle phase

Do NOT use for: one-off audits with no follow-up (just do a read-only pass), or watching sources you cannot read directly.

## Core Design Rules

1. **Monitor what already exists.** Before proposing any scaffolding, sweep for live structures on disk (state files, git logs, SQLite boards). A real finding: a scan reported "no active {CLIENT} outside archives" while `nexus/state/STATE.md` and a 187-commit git history sat unscanned. Sweep paths exhaustively before concluding absence.
2. **Truth tiers resolve numeric conflicts.** When two documents disagree on a number, don't report "conflict, unknown winner". Rank evidence: machine-generated snapshots (`cluster_snapshot.json`, DB counts, `wc -l`) > recently-committed state files > narrative prose (experiences, patterns). Prose that contradicts a snapshot is **stale narrative**, a distinct finding class from an ambiguous conflict.
3. **Stable hashed output for cron.** Each check emits deterministic output (sorted keys, no timestamps); hash it. Unchanged hash = silent tick, no delivery. Changed hash = diff injected into the run. First tick always runs (baseline).
4. **Acceptance-test-first builds.** Before writing checker code, excavate REAL instances of each drift type on disk and hand them to the builder as tests the checker must catch on day one. Synthetic examples prove nothing about recall.
5. **Report vs alert split.** Metrics without trend data get reported, not alerted (e.g. pattern-reuse ratio 18/78 — meaningful only once tracked over time). Alerts reserve for binary, actionable findings.

## The Four Baseline Checks

| Check | Detects | How |
|---|---|---|
| Numeric conflicts | Two documents stating different values for the same fact | Grep candidate figures across the corpus; compare against tier-1 snapshots |
| Filename/mtime inversions | Files dated in the future relative to their actual modification | Parse dates in filenames, compare to filesystem mtime |
| Stale index metadata | Index entries reading "unknown date/domain" | Re-run/re-read generated indexes; flag unresolved fields |
| Dormant threads | Tensions/open items with no movement | Check status field + last-touch time (>72h default threshold) |

Add invariants where the domain allows them (e.g. for an ingestion KB: `items_ingested ≥ items_clustered`, delta ≈ pending-review queue size — an inequality check beats chasing exact equality).

## Pitfalls

- **Filenames lie about time.** Dates embedded in filenames can run ahead of (or behind) reality; only mtime/git history is evidence.
- **Prose outlives its data.** Re-clustering, migrations, and recounts happen; old experiences keep citing pre-change numbers and become false authority. Flag them; fixing them is absorption's job (see `{CLIENT}`).
- **Counts diverge by definition, not error.** Ingested vs clustered vs pending-review counts differ legitimately. Encode the relationship as an invariant before flagging.
- **Open databases read-only.** `sqlite3.connect('file:...?mode=ro', uri=True)` — a monitor must never risk writes to the watched store.
- **Don't trust prior sweeps.** Every "authoritative overview" claim gets re-derived from disk; teammate reports and even your own earlier summaries are self-reports.

## References

- `references/{CLIENT}` — concrete v1 scope: monitored targets, real test vectors, baseline values, paths.
