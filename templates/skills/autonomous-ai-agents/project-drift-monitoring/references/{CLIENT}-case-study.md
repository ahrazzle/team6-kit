<!-- GENERICIZED: 5×{CLIENT} | source: skills/autonomous-ai-agents/project-drift-monitoring/references/{CLIENT} -->
# {CLIENT} Case Study — Monitor Suite That Survived Audit (2026-08)

Session-specific detail backing project-drift-monitoring/SKILL.md.
Workspace: `{CLIENT}` — monitors over an agent team's {CLIENT}
knowledge base + venture workspaces.

## What was built

- 4 checks: numeric-conflict (truth tiers), date inversion, stale index
  metadata, dormant tensions (git-diff dated).
- Runner script, pulse aggregator (`render_pulse.py` → `OUTPUTS/pulse.md`),
  venture registry generator (`gen_ventures.py` + hand-authored
  `ventures.yaml` manifest), daily cron at 09:00.

## Real drift caught on day one (acceptance vectors)

1. Snapshot v5 (880 items / 25 clusters) vs prose still saying 882/17 from v3 —
   re-clustering happened, experiences never re-absorbed.
2. Three simultaneous review-queue counts: jsonl = 55 lines, IDEA.md "39",
   experience "55".
3. Invariant drift: ingested − clustered = 39 ≠ queue = 55 → ~16 items
   clustered but never removed from review queue.
4. Future-dated filenames: `{CLIENT}/09-08` files with mtime 08-21.
5. Resolved tension whose index status still read `status: active`
   (commit recorded resolution; frontmatter never updated).
6. Truth moved mid-operation: snapshot bumped to v6 (1073/30) overnight;
   tick caught it within the hour — proving baseline-vs-live diffing works.

## False-positive lessons (check 1 precision pass)

6 of first 10 findings were noise:
- "800" was the X bookmark API ceiling (platform constant) → whitelist.
- "399"/"700" were historical batch sizes in docs predating the snapshot →
  historical-doc gate.
- "919" invariant language ("Active — 919 items") defeated a keyword exemption
  keyed on the literal word "ingested" → test exemptions against live phrasing.

## Git-diff dating (check 4)

One bulk commit (`044bbc3`) added `stale_after:` keys to 7 tension
frontmatters at 14:04, overstating recency by ~14h vs true body edits
(00:28–00:52). Filter: last commit whose diff touches BODY only; ignore
frontmatter-only churn; fallback to mtime without git. Result: thin baseline
(1 key) was CORRECT — independent arithmetic confirmed each remaining tension's
trip time within the hour.

## Directory-mtime trap (registry defect 2 that wasn't)

Registry showed khaana last_touched 08-18 while directory mtimes said 08-22.
Verified with `find -newermt {CLIENT} -type f` → zero files. The dir mtimes
were metadata touches (com.apple.macl), not activity. Registry was right;
the human verifier had read directory mtimes as content changes.

## Pipeline ordering bug (defect 1, real)

`run_daily_checks.sh` ran gen_ventures BEFORE render_pulse, so the registry
read stale pulse_state.json (57 findings vs pulse's 60). Fix: checks →
render_pulse → gen_ventures. Verify by comparing headline counts across
artifacts after a full runner pass.

## Process patterns worth copying

- Acceptance vectors = real drift found by hand BEFORE building checkers;
  scripts must catch every real example on day one.
- Independent verification passes caught: false positives, self-report vs disk
  mismatch, ordering bug, and a mis-read of directory mtimes. Self-reported
  "tested and passing" is Tier 2.
- Pulse footnote pattern: green day must state open debts
  ("*known = still open: 4 numeric conflicts, 7 dormant tensions").
- Cron prompt encodes: post stdout verbatim, interpret only new findings,
  judge precision-per-alert never alerts-per-day, expected burst documented,
  read-only constraint restated.
