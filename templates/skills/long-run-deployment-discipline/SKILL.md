<!-- GENERICIZED: 1×{CLIENT} | source: skills/long-run-deployment-discipline/SKILL.md -->
---
name: long-run-deployment-discipline
description: Use when a task has many steps or timeout risk.
---

# Long-Run Deployment Discipline

Cross-profile SOP born from a real failure: an agent ran 100+ commands silently, timed out mid-deploy, and left half-configured infrastructure that took a forensic pass to unwind.

## The rules

1. **Batch aggressively** — multi-step scripts in one call, parallel independent calls. Never one tool call per step.
2. **Front-load recon** — single batched read-only pass (inventory of repos/DNS/projects/files) before any mutation.
3. **Report at milestones** — short message every few minutes instead of silence-then-timeout. Silence and spiraling are both violations.
4. **No retry loops** — on a dead end, state it ONCE with exactly what's needed to unblock, then move to the next independent workstream. Never repeat variations of a failed approach.
5. **Persist state to disk as you go** — maintain `STATE.md` in the pinned workdir (current step, done/remaining, last verified fact). Update at every milestone so ANY teammate can resume mid-task after a cutoff instead of re-deriving context.
6. **Long waits go background** — DNS propagation, builds, installs = background process + work on something else. Never a foreground polling loop.
7. **Verify before reporting** — every milestone report must be read back from disk/DNS/API, never assumed. Reports outrunning verification is how wrong states get signed off three times in a row.
8. **Resume = validate first** — whoever picks up an interrupted task must validate STATE.md against actual disk/network state before acting. STATE.md is a claim, not ground truth.

## STATE.md protocol

- The agent executing the task owns writes, updated at every milestone (closes {CLIENT} NEXT.md lines 39–41).
- Anyone may read; the resumer validates against disk before acting.
- Content: current step / done / remaining / last verified facts. Facts only, no narration.

## Pitfalls

- Memory-only persistence dies on `hermes profile install` (memories/ stripped) — durable procedure belongs in this skill, not memory.
- Duplicate asset/source directories accrete without a declared authority — declare one source-of-truth directory and quarantine the rest before starting.
- Domain migrations: create and VERIFY the destination before releasing the old binding; order matters more than speed.
