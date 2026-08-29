<!-- GENERICIZED: 3×{AMOUNT}, 9×{CLIENT}, 1×{MODEL}, 23×{RELATIONSHIP} | source: skills/autonomous-ai-agents/multi-agent-team-orchestration/references/{CLIENT}-workflow-overhaul.md -->
# Session {CLIENT} — Workflow Overhaul & Model Config

This session corrected Team6's operational model. The dynamic-delegation experiment was replaced with a sequential role-based workflow, and a `model-config-skill` was created.

## Workflow Overhaul

### Problem
The dynamic-over-specialization tradeoff broke down: the first agent to receive instruction executed it indiscriminately, reducing specialists to reviewers. {RELATIONSHIP} (code writer) was barely writing code — reviewing what others had already written. {RELATIONSHIP} (UX) was doing database queries and code audits (analysis, not design). {RELATIONSHIP} had drifted into code writing, which was never the intention.

### Correction
Sequential role-based flow that doubles as the contribution order:

1. **{RELATIONSHIP}** — ingest, delegate, frame
2. **{RELATIONSHIP}** — ideation (slot 2) and execution design (slot 6)
3. **{RELATIONSHIP}** — scope definition
4. **{RELATIONSHIP}** — research
5. **{RELATIONSHIP}** — analysis & solutions architecture. **No code writing.**
6. **{RELATIONSHIP}** — development. **Sole developer.**
7. **{RELATIONSHIP}** — QA
8. **{RELATIONSHIP}** — summarize/report

**Post-QA dynamic delegation:** After QA, remaining work (bugs, optimizations) is delegated dynamically within roles. Role ownership never changes.

### Key Decisions
- Contribution order = Workflow order (synced)
- {RELATIONSHIP} is purely analyst/thinker, no code
- {RELATIONSHIP} is sole developer
- {RELATIONSHIP}'s two slots are distinct: slot 2 (concepts, no implementation detail) and slot 6 (visual language after constraints known)

## Model Config Skill

Created `model-config-skill` for {RELATIONSHIP} to run at every project start. Installed in all six profiles.

### Key Facts
- Main model: `stealth/ox-alpha` ({RELATIONSHIP}, free, limited time)
- Fallback: `{MODEL}` (Nous, free)
- Config frozen at session start — write `config.yaml` **before** opening the project room
- Per-agent reasoning: {RELATIONSHIP}=high, {RELATIONSHIP}=max, {RELATIONSHIP}=high, {RELATIONSHIP}=high, {RELATIONSHIP}=medium, {RELATIONSHIP}=medium
- Input is ~90% of tokens; tool schemas cost ~70KB per turn
- All cost figures are extrapolation — zero measured spend exists (all sessions ran free models)

### Framework
1. Default: Ox Alpha + free aux + per-agent reasoning → {AMOUNT}
2. Medium complexity: DeepHermes 3 24B → ~{AMOUNT}-11/month
3. High complexity: Hermes 4 70B Thinking → ~{AMOUNT}-64/month
4. Critical: Hermes 4 405B Thinking → per-call escalation

## {CLIENT} Knowledge Base

Team6 audited the {CLIENT} knowledge base at `/Users/{RELATIONSHIP}/{CLIENT}{CLIENT}/wrk/gc1`. 10 findings compiled into `{CLIENT}-findings/ARIF_AUDIT_2026-08-21.md` and a work order at `{CLIENT}-findings/ARIF_WORK_ORDER.md`. No {CLIENT} files were modified — findings only.

Key findings:
- Review queue fully disconnected (QA loop decorative, not functional)
- Source tier key mismatch (`x_bookmark` vs `x_bookmarks`)
- 74% of corpus unclustered
- IDEA.md / ORIENTATION.md overstate coverage

## Lesson Learned

A remediation plan is an untested change. Audit findings get verified; audit fixes should also be verified before inclusion. Three agents reported a skill built and working, but the step that does the actual work was inoperable in all three copies. A skill's cost is not the tokens it occupies — it is the confidence it manufactures.

Any skill whose job is to write files should carry a read-back verification block.

---

*See also: `references/{CLIENT}-team6-operations.md` for the canonical Team6 operating conventions.*
