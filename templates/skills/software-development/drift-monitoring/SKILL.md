<!-- GENERICIZED: 18×{CLIENT}, 2×{RELATIONSHIP} | source: skills/software-development/drift-monitoring/SKILL.md -->
---
name: drift-monitoring
description: "Use when building monitors over self-reported state."
version: 1.0.0
author: {RELATIONSHIP} ({RELATIONSHIP}), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [monitoring, drift-detection, truth-tiers, pulse, dashboards, {CLIENT}]
    related_skills: [knowledge-base-ingestion, {CLIENT}]
---

# Drift Monitoring & Truth-Tier Reconciliation

> Design principles for monitoring layers that watch knowledge bases and project state WITHOUT editing them. {CLIENT} (`~/{CLIENT}{CLIENT}`) is the reference instance: a central feed/analytics hub over Team6 ventures and the canonical {CLIENT}

## When to Use

- Building or extending a monitor, pulse, registry, or dashboard over project state, the {CLIENT}, or a knowledge base
- Reconciling conflicting counts ("three numbers on disk disagree")
- Diagnosing narrative decay — prose claims that drifted from machine reality
- Designing a "morning decision surface" that ranks what to work on next

**Don't use for:** Building the ingestion/clustering pipeline itself (use `knowledge-base-ingestion`). Absorbing session context into the {CLIENT} (use `{CLIENT}`).

## Core Principles

1. **Tier-0 truth = machine artifacts.** Snapshot JSON, git log, DB rows, file mtimes. Prose that contradicts Tier-0 is STALE NARRATIVE — flag it, don't weigh it as an equal claim. The monitor's job is to catch the lie, not adjudicate between two prose claims.
2. **Script artifacts are not truth claims.** A file like `needs_review.jsonl` has a line count, but that count may be an audit trail, not a count of anything meaningful. Verify against the actual datastore (DB, snapshot) before declaring a conflict. {CLIENT}'s check 1 killed a whole alarm class by reading `review_status` from pgvector instead of jsonl lines.
3. **Classify each claim before calling it a conflict.** Conflicting numbers often measure different quantities: "39 pending" = a source-type subset, "55" = audit-file lines, "880" = accepted set. Break the store down by the dimensions that matter (source_type × status, snapshot version × item set); the "conflict" usually resolves into one real invariant plus one real gap.
4. **Derived vs declared fields.** Anything derivable from disk (last_touched, finding counts, stall age) MUST be generated each tick, never hand-typed — a hand-maintained registry lies within days. Human-truth fields (state, next_action, owner) are declared, but every declared field carries an expiry (`next_action_verified`): unverified past 72h renders stale/gray. "Parked" is a declared override — an act of will, not a disk signal — and the one field that SHOULD be hand-authored.
5. **Status-vs-history inversion.** When git history contains a resolution commit but frontmatter still says `status: active`, that's a distinct drift class (found in `watcher-is-ceremonial.md`). Flag it. Rule: status fields must be written back in the same commit as the decision. Monitors should compare history-derived status against metadata-derived status, not just dates.
6. **Announcement drift.** When a team announces a fix as "live," "pushed," and "verified" but the served artifact (bundle, HTML, deployed file) does not contain the fix, that's announcement drift — prose claims decoupled from machine reality. The fix exists in local source or in the announcement, but not in what the browser actually loads. Rule: verify fixes in the SERVED artifact (raw GitHub URL, curl, browser network tab), not in local source or commit messages. A fix is not "verified" until `curl <served-url> | grep <fix-string>` returns a match. **This is especially insidious with build pipelines** (esbuild/webpack/tsc): a source commit does NOT update the served bundle until the build runs AND the output is committed/pushed. Local source and served bundle are decoupled — always verify the built artifact.
6. **Precision-per-alert, never alerts-per-day.** A monitor's first days often produce a burst as threshold walls expire (e.g. all tensions tripping 72h within 40h). Pre-agree the acceptance criterion: every alert must match a known-findings table; volume is not the metric. Otherwise someone "fixes" a checker that is correctly surfacing a stalled board.
7. **Generation order matters.** In multi-stage pipelines (checks → state → registry → render), generating the registry before state updates makes the badge contradict the detail it links to. Encode the ordering constraint in comments so it survives edits.

## Pitfalls

- **Directory mtimes are metadata touches.** Finder/git operations update directory mtimes without touching files. `last_touched` must walk FILES only, or active projects render stale (khaana bug: dirs 08-22, all content 08-18).
- **Monitors over self-reported logs inherit blind spots.** Stale logs look like "no drift" when they may be "no logging." Anchor to signals that cannot self-report stale: git log, file mtimes, machine snapshots.
- **Don't tune the checker against the true state.** If 7 tensions are genuinely stalled, 7 alerts is correct. Fix the state, not the monitor.
- **A resolution commit is not a resolution write-back.** Commit messages say "resolved" — check the frontmatter actually flipped.
- **A source fix is not a bundle fix.** When the build pipeline compiles source → bundle (esbuild, webpack, tsc), a source commit does NOT update the served bundle until the build runs and the output is committed/pushed. Verify in the served bundle, not local source.
- **Future-dated filenames and unknown-date index entries are real signal.** Check 2/3 caught 20 date inversions and 26 unknown-date gaps; baseline new gaps only, don't re-alert the known set.
- **Cross-project reads can surprise.** The canonical {CLIENT} is `~/.hermes/{CLIENT}` — per-project {CLIENT} trees were deliberately consolidated away ({CLIENT}). Searching project dirs for NEXUS.md/ANIMA.md and concluding "premise is hollow" is a false negative; check the canonical path first.

## Reference Instance: {CLIENT} Layout

- `PROJECTS/check1_numeric_conflict.py` — Tier-0 vs prose; reads DB/pgvector counts, not artifact line counts
- `PROJECTS/check2_date_inversion.py` — date-prefixed names vs mtime
- `PROJECTS/check3_stale_index.py` — index entries with unknown date/domain
- `PROJECTS/check4_dormant_tensions.py` — git body-diff dating, 72h threshold, status-vs-history inversion
- `PROJECTS/render_pulse.py` — aggregated readout; delta detection via state key sets
- `PROJECTS/gen_ventures.py` + `ventures.yaml` — derived-from-disk registry + declared manifest (with expiries)
- `PROJECTS/run_daily_checks.sh` — ordering: checks → render_pulse → gen_ventures → post
- `OUTPUTS/pulse.md`, `OUTPUTS/dashboard.html`, `OUTPUTS/alerts/`
- Cron: daily 09:00 ET; silent tick = green one-liner; drift = plain-language summary

## Verification

- Silent tick verified end-to-end: normal-mode first run writes alert, second run silent
- Registry agrees with pulse (60 = 60) after ordering fix
- Every alert maps to a known-finding table row — no unexplained findings
- Watchdog survives a Tier-0 change (snapshot version bump) without false re-alerts on known findings

## References

- `references/{CLIENT}-truth-gap.md` — worked example: reconciling three conflicting {CLIENT} counts end-to-end (method + truth table)
- `references/{CLIENT}` — worked example: source fixes that never reached the served bundle, announcement-without-verification pattern, prevention checklist
