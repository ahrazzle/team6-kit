<!-- GENERICIZED: 2×{AMOUNT}, 2×{RELATIONSHIP} | source: skills/research/read-only-system-audit/SKILL.md -->
---
name: read-only-system-audit
description: "Use when auditing a system you must not modify."
version: 1.0.0
author: {RELATIONSHIP} ({RELATIONSHIP})
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [audit, verification, read-only, data-integrity, knowledge-base, review]
    related_skills: [source-evaluation, knowledge-base-construction, systematic-debugging, hermes-profile-fleet-operations]
---

# Read-Only System Audit

> You are pointed at a system built by someone else and told: use it, assess it, **change nothing**. The instruction sounds like a restriction. It is actually the whole method — it forces every finding to be evidence you gathered rather than a change you made, and it makes the deliverable a document another team can act on.

## When to Use

- "Comb through X and tell me what you find. Do not modify it."
- Onboarding onto a shared, ever-evolving resource owned by another team
- Reviewing a knowledge base, database, pipeline, or codebase you consume but do not maintain
- Any audit whose output is a findings document rather than a patch
- Verifying that a *remediation plan* is safe before it ships

**Do not use for** debugging a system you own and may fix — that is `systematic-debugging`. The distinguishing feature here is that repair is out of scope and the deliverable is prose.

## The Two Core Rules

> **1. Read the data, not the summary.** A system's front page describes what its authors intended. The database describes what exists. When they disagree, the database is the finding.

> **2. Verify the fix, not just the finding.** A remediation plan is an untested change that carries the authority of a solution while having had none of the scrutiny of a diagnosis. Audit findings get reviewed; audit *fixes* usually do not. That asymmetry is where the damage lives.

Rule 2 caught the most dangerous item in one real audit: a "critical" finding whose recommended fix — *"ingest the pending file"* — would have inserted 16 duplicate rows into a table with no unique constraint. The diagnosis was correct and reviewed by several agents. The prescription was never checked by anyone.

## Procedure

### Step 1 — Read the orientation material, then distrust it

Start where the authors tell you to start (`ORIENTATION.md`, `README`, `IDEA.md`). Extract the claims into a list: item counts, coverage percentages, "what's live", "what's blocked", queue depths, completion states.

Treat that list as **hypotheses to test**, not context to absorb. Every number in it is a claim with a timestamp you cannot see.

### Step 2 — Reproduce every headline number from the source of truth

For each claim, find the primitive that would prove or refute it and query it directly. See `references/audit-query-patterns.md` for ready-made probes.

The claims that most often fail:

| Claim shape | What to actually check |
|---|---|
| "N items, M clusters" | how many items fall **outside** every cluster |
| "queue: 0 pending" / "all processed" | does the pending flag exist in the store at all |
| "all items marked X" | is X a set value, or a `.get(key, default)` fallback |
| "N sources integrated" | row counts per source, and whether keys match the code's lookup table |
| "graph of N edges" | what the read path's `LIMIT` actually returns |

### Step 3 — Diff the documents against each other first

Two documents describing the same system will disagree, and the disagreement localises the defect for free. In one audit, `ORIENTATION.md` said "55 items pending" while `IDEA.md` said "0 pending (all processed)". The truth: 55 were never ingested *and* 16 of those had been — so **neither number was right, and the file was a stale log rather than a queue**.

Diff the docs against each other before diffing either against the data.

### Step 4 — Trace each defect into its derived structures

A defect rarely stays where it started. **A metadata gap does not remain a metadata gap** — it propagates into everything computed downstream and surfaces far from its origin wearing a different costume.

Worked example: 28% of items lacking a description → the TF-IDF cluster labeller has only the URL as text → nine of seventeen cluster names come out as `reddit / comments / www`. Reported separately these look like two problems (a data gap, a labelling bug). They are one cause with two symptoms, and saying so changes the fix.

Always ask what is computed *from* the broken field: labels, rankings, embeddings, similarity scores, navigation, counts.

### Step 5 — Check for absent enforcement, not just present bugs

The highest-value findings are often things **missing** rather than wrong:

- A stated principle ("deduplicate before ingest") living only in pipeline code with **no schema constraint** behind it. Every future connector must independently remember; the first that forgets corrupts silently.
- A shared, evolving, multi-writer workspace with **no version control** — no history, no rollback, and a mutating pipeline.
- A quality gate that **reports clean while disconnected** from what it gates. Worse than a gate that fails, because a passing signal stops anyone from looking.

An absence produces no error message, so nobody finds it by watching logs. It is found only by asking "what should be here?"

### Step 6 — Audit your own remediation list before shipping it

For every fix you are about to recommend:

1. **Would executing this literally cause harm?** Duplicate inserts, destructive migration, overwriting live data.
2. **Does it depend on another fix landing first?** Order by dependency, not only severity, and say which item gates which. A safe fix applied second is an unsafe fix.
3. **Is the "or" branch a trap?** Fixes phrased *"do A, or B"* are dangerous when one branch replaces a meaningless output with an authoritative-looking one. Substituting a real vector for a zero vector in a self-similarity computation yields a constant `1.00` — a column of perfect confidence scores a user would believe. The correct remedy was deletion; the either-or framing hid that.
4. **Is it reversible?** If not, say so.

### Step 7 — Write the deliverable outside the audited tree, then prove you touched nothing

Put findings in your own workspace, never inside the audited system — not even a new file, not even a `NOTES.md`. Then verify and state the proof:

```bash
cd <audited-path> && stat -f "%Sm  %N" <key files>     # macOS
cd <audited-path> && stat -c "%y  %n" <key files>      # Linux
```

Report the mtimes and note that they predate the session. "No files were modified" is a claim; mtimes are evidence.

## Deliverable Shape

Read by people who will do the work, so optimise for action:

- **Severity tiers** (Critical / High / Medium), and within each, **dependency order**
- Per finding: **What** (with the query result proving it), **Why it matters**, **Fix** (with ordering caveats), **Owner**
- A measured table over prose whenever a count is involved
- One explicit priority list at the end, with gating relationships called out in a sentence
- A closing line stating what was not modified and how that was verified

Do not soften a finding to be diplomatic; do not inflate one for impact. A count is a count.

## Pitfalls

**Reporting the author's number instead of measuring it.** "17 emergent topic clusters" was true and described 26% of the corpus — 656 of 882 items were unclustered noise. The number was not false, it was *incomplete in a way that inverted its meaning*. Coverage claims need a denominator.

**Accepting a caps-as-performance explanation.** A read path returning 500 of 882 items and {AMOUNT} of {AMOUNT} edges may be correct — the layout could not survive 72K edges. But presenting a recency-biased 2.8% sample as *the* map with nothing telling the user is a **labelling defect**, fixed by one sentence of UI text rather than a re-architecture. Separate "the limit is wrong" from "the limit is undisclosed".

**Double-counting overlapping evidence.** If you measure a gap two ways (a prose count plus a state table), ship only the authoritative one. Two framings of one problem read as two problems and inflate the fix estimate.

**Recommending `git init` on a directory full of generated artifacts.** Check sizes first. Binary stores and regenerated JSON (a 5.7 MB sqlite file, several ~1 MB derived maps) need a `.gitignore` in the same recommendation, or every pipeline re-run produces a megabyte-scale diff and the history becomes unusable.

**Scope creep dressed as helpfulness.** When told not to modify, do not modify — even when the fix is one line and obviously correct. Report it. The owning team may have context you lack, and an unrequested edit to a shared resource costs more trust than the fix saves. If a defect is genuinely urgent, say so at the top of the document and let the owner decide.

**Never exceed the explicit instruction.** Deleting, recreating, or cascading beyond what was asked is its own defect class. If a fix appears to require a step nobody authorised, ask first.

## Verification

- Every quantitative claim traces to a command output you can re-run
- Every recommended fix has been checked against the live schema for harm and ordering
- Audited-tree mtimes are unchanged and quoted in the document
- The deliverable names owners, so nothing is filed to no one

## Support Files

- `references/audit-query-patterns.md` — probes for coverage, orphan/noise rates, silent-fallback keys, absent constraints, and stale queue files
