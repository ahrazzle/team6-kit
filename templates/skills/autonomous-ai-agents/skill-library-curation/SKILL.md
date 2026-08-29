<!-- GENERICIZED: 1×{AMOUNT}, 1×{RELATIONSHIP} | source: skills/autonomous-ai-agents/skill-library-curation/SKILL.md -->
---
name: skill-library-curation
description: Use when auditing or pruning a skill library.
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [skills, curation, curator, audit, agentskills, authoring, telemetry]
    related_skills: [agent-persistence-layers, hermes-agent]
---

# Skill Library Curation

Use when the health of a **skill library** is the subject: auditing it, pruning it,
splitting oversized skills, rewriting descriptions so skills actually get selected, or
authoring a new one to a standard. Distinct from writing any single skill's content —
this is about whether the library as a whole is findable, affordable, and honest.

## Trigger

- "Audit our skills," "clean up the skill library," "why isn't this skill being used"
- A skill exists and is relevant but never activates
- Context cost is high and skills are suspected
- Adopting or conforming to the agentskills.io standard
- Someone proposes deleting or pruning skills in bulk
- A skill's `SKILL.md` has grown past a few hundred lines

## First Principle: Three Independent Failure Modes

A skill can fail in three ways that look alike from the outside and have different fixes.
Diagnose which one before touching anything.

| Failure | Symptom | Where it is measured |
|---|---|---|
| **Not findable** | Relevant skill never loads | The description's first 57 chars |
| **Too expensive** | Loads, but floods the window | Body line and token count |
| **Not wanted** | Loads never because nobody needs it | The curator usage ledger |

Only the third is a candidate for removal. The first two are candidates for editing.
Conflating "unused" with "badly written" produces the classic wrong plan: rewriting the
descriptions of skills nobody will ever want, while the genuinely mis-described ones stay
broken.

## Measure First — The Tools Do Not Catch This

Run `scripts/audit-skill-library.py <skills-dir>` before forming any opinion. It reports
frontmatter violations, name/directory mismatches, over-budget bodies, and — the part no
validator covers — which descriptions lose their trigger to truncation.

**`skills-ref validate` is not a substitute.** It checks frontmatter and naming
conventions. It does **not** check the truncation window (that is host-specific) and does
**not** enforce the token budget (that is a recommendation, not an error). A clean
validate run tells you almost nothing about whether a library works.

## Failure 1: The Truncation Window

Hosts show the agent a **truncated** description when deciding which skills are relevant.
In Hermes that is **57 characters plus an ellipsis**. That truncated string, plus the skill
name and category path, is the entire selection signal.

So the trigger condition must land inside the window:

```
description: Use when <trigger>. <one-line behavior>.
```

A description that opens with what the skill does and saves the trigger for the second
clause is invisible at selection time. Typical shapes that fail:

```
Apple Reminders via remindctl: add, list, complete.          # what, never when
4-phase root cause debugging: understand bugs before fixi    # cut mid-word
```

**Hermes now enforces this on creation.** `skill_manage(action='create')` refuses a
description over ~60 chars outright, with an error naming the 57-char truncation. So new
skills cannot fail this way — but every skill authored before the guard, and every skill
from an external source, still can. Audit existing ones; trust the guard for new ones.

**Calibrate the claim, though.** A missing trigger degrades selection; it does not
guarantee invisibility. The name and category also carry signal — `github-pr-workflow`
communicates its own trigger without a single word of description, and skills with no
trigger phrase do get used. The honest finding is usually *"descriptions are redundant
with names, wasting the window,"* not *"these skills are invisible."* Overstating it turns
a copy-edit into a fictional migration project. Say the smaller true thing.

## Failure 2: The Activation Budget

On activation the **entire** `SKILL.md` body enters context. Budget: **under 500 lines and
~{AMOUNT} tokens**. Rough conversion for a quick estimate: **~4 chars per token**.

The fix is progressive disclosure, not terse prose. Move detail into support files and
keep the body as the core procedure.

**Check for an existing `references/` directory before planning the split.** A skill that
already has one splits cleanly; a skill with a single flat `SKILL.md` needs the directory
created, which is a different amount of work. Sort the queue by that, not by size.

**The rule that makes disclosure actually work: name the loading condition.**

```
Read references/api-errors.md if the API returns a non-200 status.   # fires
See references/ for more details.                                    # never fires
```

A generic pointer is never followed at the right moment, so its content may as well not
exist. Every support-file reference in the body should state *when* to open it.

## Failure 3: Read The Ledger Before Proposing A Prune

```bash
hermes curator usage          # every skill: origin, use/view/patch counts, last activity
hermes curator status         # runs, interval, stale/archive thresholds, counts by state
hermes curator prune --dry-run --days 90
```

`hermes curator usage` is the only honest source for what is actually wanted. It reports
**origin** per skill — `agent`, `bundled`, or `hub` — and that column decides everything.

**The curator never touches bundled or hub-installed skills.** Its own help text says so.
This kills the most tempting plan in this class of work:

> A library shows 75 skills with zero uses. Seventy-three are `bundled`. The prunable set
> is **two**, both `agent`-authored. The other 73 are the host's shipped library — dormant
> because that domain has not come up yet, not dead weight — and deleting them would be
> undone by the next update anyway.

So the sequence is: read origin first, then decide. A prune plan built from usage counts
alone will be wrong by an order of magnitude and will propose deleting things you do not own.

**Prefer `--dry-run` to a hand-built list.** The curator already tracks state and archive
timestamps and archives recoverably; auto-deletion never happens. Checking what it intends
to do costs nothing and beats assembling a manual kill list.

**Per-profile ledgers diverge.** Each profile has its own telemetry. A teammate's "most
used skill" is not yours, and reasoning from another agent's numbers about your library
produces confident wrong conclusions. Run it where the question is being asked.

## Authoring Standard (agentskills.io)

Condensed spec, frontmatter constraints, and the writing rules that change output quality:
`references/agentskills-spec.md`. Read it before authoring or conforming a skill.

The three rules worth memorising:

1. **The directory name must equal the frontmatter `name`.** Lowercase `a-z0-9` and single
   hyphens; no leading, trailing, or doubled hyphens.
2. **Add what the agent lacks; omit what it knows.** For each line ask "would the agent get
   this wrong without it?" If no, cut it. Never explain what a PDF is.
3. **Give defaults, not menus.** One recommended approach plus a brief escape hatch. Four
   equal options makes the agent try several.

## Workflow

1. **Measure.** Run `scripts/audit-skill-library.py` on the real directory. Numbers, not
   impressions.
2. **Read the ledger.** `hermes curator usage`. Note the origin column before anything else.
3. **Partition** into the three failure modes. Unused-and-bundled is not a task; it is a
   non-issue.
4. **Scope honestly.** Report the smaller true number. "Two prunable, six worth rewriting,
   eight over budget" is actionable; "94 broken skills" invites a project that should not exist.
5. **Prune with `--dry-run` first,** then let the curator archive. Never bulk-delete by hand.
6. **Rewrite triggers** on skills that are actually used and actually yours.
7. **Split over-budget bodies** into `references/`, giving each pointer an explicit loading
   condition.
8. **Re-run the audit** to confirm the counts moved.

## Pitfalls

- **Proposing to prune bundled skills.** The curator refuses, and an update would restore
  them. Check the origin column first.
- **Treating zero uses as evidence of a bad skill.** It is evidence of an unneeded domain.
  Different problem, different fix, often no fix at all.
- **Trusting `skills-ref validate` as an all-clear.** It misses both the truncation window
  and the token budget — the two failures that actually matter.
- **Reasoning from another profile's usage numbers.** Ledgers are per-profile. Run it locally.
- **Overstating the trigger problem.** Names carry signal. "Invisible" is usually false;
  "redundant with the name" is usually true. The exaggeration is what turns a copy-edit into
  a fake migration.
- **Splitting a skill without checking for an existing `references/` dir.** Changes the work
  from a move to a restructure; plan accordingly.
- **A generic "see references/" pointer.** Never followed. State the condition.
- **Quoting a doc page for host-specific behavior.** The truncation width and the ledger's
  origin semantics come from the running host, not the open standard. Verify against the
  installed tool.
- **Reporting an audit as complete without re-running it.** The count is the only proof the
  edit landed.

## References

- `references/agentskills-spec.md` — condensed agentskills.io specification: frontmatter
  fields and constraints, progressive-disclosure budgets, and the authoring rules that
  change output quality
- `references/curator-ledger-audit.md` — worked case notes: real `hermes curator usage`
  output, how a "prune 73 skills" plan collapsed to two, and the per-profile divergence trap
- `references/skill-absorption-verdict.md` — how to evaluate an external/discovered skill
  before adopting it (candidate → proof on a real task → scoped verdict), the finding that
  decision-rule skills are for targeted single-decision lookups NOT broad refreshes on
  mature work, and the guardrails for authoring your own skill from the source project
- `scripts/audit-skill-library.py` — measures all three failure modes across a skills tree;
  run before proposing any change

## Related Skills

- **agent-persistence-layers** — where knowledge lives (`SOUL.md` vs memory vs project
  context). Use that for what must never be missed; use this for the on-demand layer's health.
- **hermes-agent** (bundled) — authoritative reference for the Hermes CLI and curator commands.
