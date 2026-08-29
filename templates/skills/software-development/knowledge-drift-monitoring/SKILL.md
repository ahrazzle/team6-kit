<!-- GENERICIZED: 1×{AMOUNT}, 17×{CLIENT}, 2×{RELATIONSHIP} | source: skills/software-development/knowledge-drift-monitoring/SKILL.md -->
---
name: knowledge-drift-monitoring
description: "Detect drift in knowledge bases and {CLIENT} structures."
version: 1.0.0
author: {RELATIONSHIP} ({RELATIONSHIP}), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [monitoring, drift-detection, {CLIENT}, knowledge-base, cron]
    related_skills: [{CLIENT}, multi-agent-knowledge-systems, source-verification]
---

# Knowledge Drift Monitoring

> Detect drift and decay in a living knowledge structure (Team6's {CLIENT}, a project workspace, any markdown + JSON knowledge base) with standalone, cron-ready check scripts. The read-side complement to `{CLIENT}`: absorption writes truth in; monitoring catches it going stale.

## When to Use

- User asks to build a monitoring layer / "{CLIENT}" / drift detection over the {CLIENT} or project workspaces
- A knowledge base has machine-generated artifacts (JSON snapshots, jsonl queues) PLUS narrative prose that quotes numbers — the two drift apart silently
- Need "what changed since yesterday" alerts on a scheduled cadence with zero noise

**Don't use for:** absorbing new work INTO the {CLIENT} (that's `{CLIENT}`); watching external prices (that's `product-price-monitor`).

## Tier-0 Truth Principle (the core idea)

Machine-generated artifacts anchor truth. Prose that contradicts them is **STALE NARRATIVE**, not an ambiguous two-sided conflict.

- **Tier 0:** JSON snapshots (`cluster_snapshot.json`), jsonl line counts (`needs_review.jsonl`), DB counts. Read them directly.
- **Tier 1:** Prose (experiences, patterns, NEXUS/STATE.md, project IDEA.md). A claim that disagrees with Tier 0 is stale — flag it as such with a pointer to the current truth.
- **Invariants are legal, not conflicts:** e.g. `ingested >= clustered` and `ingested - clustered ≈ pending-review count`. Encode these as invariant checks; do NOT flag prose that states them correctly.

## The Five Check Archetypes

These recur in any knowledge-base monitor. One standalone script per check:

1. **Numeric conflict** — prose numbers vs Tier 0. Needs the precision rules below or it cries wolf weekly.
2. **Date inversion** — date-prefixed filenames (`{CLIENT}-*.md`) that run ahead of reality. Only **future-dating** matters (name claims the doc is newer than its mtime); back-dated names are normal absorption churn (edits after write).
3. **Stale index metadata** — index entries carrying "unknown date" / "unknown domain", broken links, linked files missing frontmatter.
4. **Dormant tensions / stalled items** — items active with no movement past a threshold. Use git commit history, not mtime (see below).
5. **Store liveness (two-condition)** — an infra store (kanban.db, a git repo, a DB) stale while work is expected. Needs the deafness guard below or it pages daily about deliberately abandoned stores.

## Two-Condition Liveness (check 5) — the Deafness Guard

A staleness check that alerts on staleness ALONE becomes noise the team trains itself to ignore. Every liveness check needs BOTH conditions before it pages:

- **A (stale):** the store's freshness signal past the threshold (mtime, git last-commit age).
- **B (drive-expected):** a DECLARED registry — separate from the store being judged — says an owner recently committed to act (e.g. `ventures.yaml` `state: active` + `next_action_verified` inside the 72h window).
- **A∧B → alert** (name the venture/owner expected to act). **A without B → log-only, never pages** (deliberately quiet store). **B without A → clean.** **Registry unreadable/missing → ALWAYS alerts** (the thing that decides "expected" is broken — liveness becomes undecidable).

**Registry decoupling (circular-dependency trap):** the drive-expected source MUST be maintained independently of the monitored stores. If "expected work" is read from the kanban and the kanban is the stale store, the check cannot distinguish abandonment from failure. Seed it from the monitor's own project registry ({CLIENT}'s `ventures.yaml`), which stays current while boards drift.

**Diagnostic mode:** on `--full`, print condition A and B independently ("kanban: 309h old (A true); drive-expected (B): 0 ventures") so a human can see WHY a stale store did NOT alert. Otherwise the deafness guard looks like a bug.

## Watcher Negative Check — No-Match Is NOT Success

Applies to any self-healing watchdog / reapply script (a launchd agent that re-patches a bundle after an update clobbers it, a cron that re-applies a config override). A no-match must be a THIRD state, not a silent no-op:

1. **Upstream pattern found** → apply the fix.
2. **Fixed pattern found** → no-op (work already done).
3. **Bundle/file exists but matches NEITHER** → ALERT (build shape changed, override unverifiable) — canary file + log line + notification + non-zero exit.

Classic silent failure: the script treats "no upstream pattern" as "already fixed", so when the minifier reorders constants or adds one, the override silently reverts to defaults and nobody is paged.

**Match by VALUE pattern, never by identifier name.** Minified bundles rename constants on every build (`Zve` → `Fve` observed). Regex the numeric sequence (`var <A>=3,<B>=10,<C>=2,<D>=6;`), not the variable names. Value-based matching survived two builds; name-based would have died on the first.

**Prove all three states with a fixture harness:** temp-dir variant of the script (sed the paths), three fake bundles — upstream (expect patch), fixed (expect no-op), unrelated (expect alert + exit 1). A script that has never fired the alert path is an unproven alarm.

## Design Contract (cron-ready, per {CLIENT} SPEC)

Every check script follows this shape:

- **Stable hashed output:** each finding gets a deterministic hash (`sha256` of file+kind+claimed-value, 16 hex chars).
- **Baseline state:** `PROJECTS/state/checkN_*.json` stores the set of known finding hashes. First run (no state file) records the baseline AND prints the full report; later runs alert ONLY on NEW hashes. Resolved findings fall out automatically because the state is rewritten each run.
- **Silent tick:** no change → empty stdout, exit 0. This is what cron greps for.
- **Alerts:** `OUTPUTS/alerts/<date>-<check>.md`, written only when there's something new.
- **`--full` flag:** print all current findings regardless of baseline (acceptance mode). Never run `--full` as the cron invocation.
- **Verify both directions:** first normal run writes an alert file; second run must be silent. Delete state + alerts and re-`--full` to prove it still catches the vectors after a precision change.

## Entropy-Proof Doctrine (design gate, {CLIENT})

Standing team rule (user axiom: "there are vacations, burn out periods… all
systems we build must be entropy-proof"): **correctness must be a pure function
of durable state, never of observation cadence.** Audit gate before build:
*"2 months untouched, still correct on first read."* Three concrete patterns a
monitoring system must implement:

- **Derived-over-stateful:** recompute derived values from durable state every
  tick; never edge-trigger. `dark_since = next_action_verified + threshold` is
  deterministic and watcher-down-safe — hiatus applies to the watcher too, so
  a logger that was offline at the crossing has no record; a derived column
  needs none.
- **Self-describing artifacts:** generated JSON carries a `_meta` block
  (generator, spec ref, generated timestamp, contract line) so a returning
  reader reconstructs intent from the file alone. Loaders must be tolerant —
  skip non-list values (`isinstance(v, (list, set))`) — instead of exempting
  files; an exemption is a schema time-bomb that breaks the next refactor.
- **Regenerable docs:** any index/table that goes stale under hiatus is rebuilt
  from disk by one command (scan `<project>/wrk/<code>` dirs, skip asset
  folders); manual maintenance is nice-to-have, never a dependency.

## Precision Rules (numeric-conflict check)

These came from a hard false-positive audit — 6 of 10 first-pass findings were noise:

1. **Metric-family classification, not raw number matching.** Classify each number by keyword context: `ingested_total | clustered | clusters | review_queue`. Relations differ per family: `ingested_total` is legal by invariant (never flag); `clustered/clusters/review_queue` must match Tier 0 exactly.
2. **Historical-doc gate:** docs whose own frontmatter `date:` predates the Tier-0 snapshot are point-in-time records — skip. **Exception:** `status: active` docs keep making present-tense claims after their write date, so they stay in scope (this is what keeps catching living-but-stale patterns).
3. **Platform constants whitelist:** real-world ceilings that look like counts but never drift (e.g. X bookmark ceiling 800). Hardcode as `PLATFORM_CONSTANTS = {800}`.
4. **{CLIENT}-context gate:** only scan lines carrying domain vocabulary (`cluster|review|ingest|bookmark|hdbscan|...`) — keeps other projects' numbers out.
5. **Evaluate metric families INDEPENDENTLY per line.** A single line carries multiple claims ("882 items, {AMOUNT} edges, 17 clusters") — one-metric-per-line is wrong and silently drops catches.
6. **Current-state disambiguation:** a line whose cluster count MATCHES Tier 0 is a current-state line — its item count is the ingested total (legal), skip the items check. A line whose cluster count MISMATCHES is stale — flag both numbers on that line.

## Git-Based Dormancy (check 4) — mtime Lies

mtime measures last *write*, not last substantive movement. A single optimization pass (e.g. adding `stale_after` frontmatter keys to 7 tensions in one commit) resets 7 mtimes at once and overstates recency by hours.

- Walk `git log` for the file, newest first; for each commit, inspect the diff; the last commit whose diff touches the **body** (not frontmatter) is the movement date.
- Fall back to file mtime only when git is unavailable or no body-touching commit exists.
- `git log --format="%h|%at" -- <path>` then `git show <commit> -- <path>` per entry; parse `+`/`-` lines.

## Pitfalls

**Python regex `\b` fails between two non-word characters.** `r"stale_after:\b"` does NOT match `stale_after: 14` — after the colon comes a space, and both `:` and space are non-word chars, so no word boundary exists. Anchor with `\s` (e.g. `^(?:date:|status:|...:)\s`) or `$` instead. This bug silently misreads frontmatter lines as body and broke the git-dormancy filter.

**`---` frontmatter delimiter needs a `$` anchor, keys need `\s`.** `r"^(?:---$|(?:key:)\s)"` — mixing both in one alternation works.

**Blank-line diff churn isn't body movement.** In a `git show` diff, a lone `+` (blank line) must be skipped, or adding a frontmatter block looks like a body edit.

**`.DS_Store` false positives.** When scanning directories for agent folders (or any entity dir), skip non-directory entries (`if not os.path.isdir(...): continue`) or macOS artifacts get flagged as "missing index".

**Self-report vs disk mismatch.** If a build report claims "X is exempted" but the live run still flags it, the exemption may key on literal words the document doesn't use ("919 items" lacks the word "ingested"). Verify against the actual file line, not the report. `sed -n '<line>p' <file>` before debugging the logic.

**One metric per line.** Already covered above — the single most common silent-drop bug.

**Baselines MUST regenerate after a precision change**, or the first cron run ships stale findings from the old logic and burns trust in the feed. Delete `PROJECTS/state/*` before re-`--full`.

**"Orphan" is ambiguous — define it as no-INCOMING links.** Two monitors disagreeing on the same tree (heartbeat reported 165 orphans, relationship-graph reported 0) is a definition collision: "no outgoing links" counts leaf nodes (experiences, patterns — expected terminal content), while "no incoming links" counts truly unreferenced documents (the real orphans). Align every tool on incoming-links for "unreferenced"; report leaf-node counts separately as expected behavior, never as findings.

**Duplicate frontmatter keys silently corrupt YAML reads.** YAML parsers take the LAST occurrence of a duplicated key. Files with 2-4 duplicate `reuse_count`/`last_reused` blocks parse fine but feed wrong values to dashboards (observed: a pattern parsed as reuse 0 when its last block said 17). Not cosmetic — scan for duplicates: `grep -c '^key:' file` > 1 → flag.

**Date-inversion repair: filename date = CREATION date.** Convention: the date-prefix in a filename is the creation date, never the target/scheduled date; use a `-scheduled` suffix for scheduled items. Repair = `git mv` to the mtime date + update frontmatter date + rebuild index. Detection: `stat -f '%Sm' -t '%Y-%m-%d'` compared to the name prefix; only future-dating (name claims newer than mtime) matters, back-dating is normal absorption churn.

## Acceptance-Driven Build Loop

1. Build the check against the spec.
2. Run `--full` and verify it catches every real example on live disk (each acceptance vector must appear).
3. Audit every finding for false positives against the source line — the monitor's precision is its credibility.
4. Fix precision, delete state, re-run `--full` until the finding set is exactly the acceptance set.
5. Verify silent-tick both ways (first run writes alert, second run silent) and that normal-mode alert writing works.

## Support Files

- `references/{CLIENT}` — the full worked example: {CLIENT} v1 SPEC, acceptance vectors, which findings were false positives and why, the regex bug autopsy, git commit analysis.
- `references/check5-liveness-and-watchdog.md` — worked example of check 5 (two-condition liveness: SPEC wording, four-case acceptance harness, real-path numbers) and the caps-watchdog anatomy (value-pattern matching, three-state logic, launchd wiring, the negative-check ALERT path).
- `references/entropy-proof-doctrine.md` — the standing design gate: derived-over-stateful (`dark_since` proof), reconstruction-over-realtime, self-describing `_meta` blocks + tolerant loaders, regenerable docs over manual maintenance, two-condition gate recap. Audit every new system against "2 months untouched, still correct."
- `references/{CLIENT}` — worked examples from the post-week pass: the orphan-definition collision (incoming vs outgoing links), duplicate frontmatter keys (YAML last-wins corruption), date-inversion detection + repair one-liner, the post-week pass checklist, and the monitoring feedback gap (detection-not-enforcement baseline).
