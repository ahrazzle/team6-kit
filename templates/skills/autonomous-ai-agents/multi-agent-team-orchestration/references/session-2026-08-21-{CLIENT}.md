<!-- GENERICIZED: 8×{CLIENT}, 3×{RELATIONSHIP} | source: skills/autonomous-ai-agents/multi-agent-team-orchestration/references/{CLIENT}-{CLIENT} -->
# {CLIENT} session ({CLIENT}) — client deliverable orchestration lessons

Session: "{CLIENT}" room, Team6. Built a training/orientation package ({CLIENT}) so a {CLIENT} Project Lead could understand Autodesk Construction Cloud (ACC) as used on a subway program. 5-file static web app shipped, dark mode added, 41/41 QA checks.

## What happened (compressed timeline)
1. User: "name {CLIENT}, workspace..., idea: training package for {CLIENT} employee." {RELATIONSHIP} anchored project, scaffolded IDEA.md + AGENTS.md, asked 4 scope questions.
2. Room discovered ACC = Autodesk Construction Cloud (construction tool, not transit ops) — research axis flipped to capital-projects side.
3. User: governance, data management, integration for a complex subway project.
4. Room specced an interactive skills-lab (submittal/RFI action engine, scenario assessments).
5. User: "he doesn't need to produce anything, just needs to orient because his team will use it." → {RELATIONSHIP} cut the lab to an orientation tour; room converged on read-mode interactive tour.
6. User: role = Project Lead managing Data Management & Integration + Governance. → Accountability layer added (scenarios close on the lead's diagnostic question).
7. Research landed ({RELATIONSHIP}): ACC in production on {CLIENT} capital delivery (HDR/ONxpress), ISO 19650-aligned house style, real counterpart stack (Revit/Civil 3D, Aconex+ACC+SharePoint, P6, Oracle Unifier, FME).
8. User: "AI tie-in is secondary; gov org, slow to adopt." → AI demoted from lens to a consolidated closing chapter; human access map became the primary centerpiece; AI layer = "Projected" overlay toggle. Re-order, don't rebuild.
9. Dark mode toggle requested → token-driven theming, localStorage persistence, 41/41 QA.

## Orchestration lessons (the five patterns added to SKILL.md pitfalls)
1. **Design-record drift under scope churn** — keep IDEA.md (or equivalent) updated at EVERY convergence point; three user corrections flipped the design in one session; the record let the room re-converge instantly instead of building from memory.
2. **Verify the artifact, not the reports** — orchestrator grep'd the shipped app's data layer for the research findings (Directive/AUP/Trust Center: zero hits) and caught a real content gap that a second agent's clean sign-off would have passed. Do this before declaring done.
3. **Parallel research/build integration gate** — build landed before research; the check "does the artifact CONTAIN the findings" must run before ship, or research is shelfware.
4. **Re-order, don't rebuild** — user correction shifted emphasis, not content; agent moved content blocks, changed defaults/order/labels, reused the object model. QA re-ran clean (33→41 checks).
5. **Fork oscillation after user correction** — room oscillated lab-vs-tour on inference; the user's own fact settled it; orchestrator locked the decision immediately and cut further debate until a new fact arrived.

## Effective tactics that earned approval
- Independent artifact verification before shipping (grep + byte counts + structure checks).
- Keeping the design record in the workspace (IDEA.md) rather than in chat.
- Delegating research/scope questions to the room while the user sat with the primary source (the employee) — user fed live interview facts, room folded them in.
- Attributing each decision to the agent who proposed it in the room messages and in the design record.

## Supporting detail
- Full instructional-design playbook: see `training-package-design` skill (learner profiling, level calibration, fidelity contract, org-maturity emphasis).
- Dark-mode static app pattern: see `interactive-simulation` skill.
