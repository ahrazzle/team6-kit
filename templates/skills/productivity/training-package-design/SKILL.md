<!-- GENERICIZED: 5×{CLIENT} | source: skills/productivity/training-package-design/SKILL.md -->
---
name: training-package-design
description: "Design training/orientation packages for a client org."
---

# Training / Orientation Package Design

## Trigger
Use when the user asks for a training package, orientation module, onboarding/enablement deliverable, or "teach team X about product Y" for a client or internal org.

## Phase {CLIENT} — Learner profile FIRST (design backward from it)
Extract before any architecture. Wrong profile = wrong depth = rebuild. The four inputs:
1. **Role** — title matters less than what they direct: operator, stakeholder, or lead/oversight.
2. **Greenfield vs experienced** — never worked with the product? Then zero vocabulary is assumed; everything must be defined from first principles (Module 0).
3. **Produce vs orient** — "needs to produce artifacts in it" (operator) vs "needs to orient around it because their team uses it" (stakeholder/lead). This single answer decides lab vs tour.
4. **Org maturity** — design emphasis must mirror the org's REAL current state, not projected features. Government/crown orgs adopt slowly: teach today-state mechanics first, aspirational features (AI, new integrations) as a clearly-labeled closing chapter, never the lens.

## Phase {CLIENT} — Level calibration (pick ONE, don't overbuild)
| Learner | Deliverable | Mechanics |
|---|---|---|
| Operator (produces artifacts) | Skills lab | Hands-on actions, scenario assessments, graded missions |
| Awareness/orientation (follows along) | Read-mode interactive tour | Hover-to-reveal, watch-mode workflow demos, zero graded mechanics |
| Lead/governance (directs & oversees) | Tour + accountability layer | Every scenario closes on the lead's DIAGNOSTIC question, not operator steps: "who holds admin? is the convention enforced or just documented?" |

Trap: building a skills-lab for an awareness-level learner is the classic overengineering failure. The interview answer "he doesn't need to produce anything" settles the level — lock it and cut.

## Fidelity contract (product simulations)
When the deliverable simulates a real product:
- Object model must mirror the real product (Projects/Folders/Files/Roles/Permissions...) so learning transfers to the real tool.
- Label it honestly — a greenfield learner may internalize the simulation AS the product.
- Projections (AI layers, future features) are clearly-labeled overlays/toggles, not the primary read.

## Architecture
- One spine, modular tracks; dependency order explicit (governance before data before integration seams).
- Secondary/aspirational topics consolidate into ONE closing chapter ("where this is heading") — do not bleed them through every track.
- Centerpiece artifact the learner leaves with (e.g., permission-and-exposure map); tracks teach how to read it.

## Grounding in real org reality
- Name REAL counterpart systems — "integration with the project stack" is filler; "P6, Oracle Unifier, Aconex, SharePoint" is training.
- Research house style vs standard: teach the org's conventions AS the standard it aligns to (e.g., an ISO 19650-aligned house manual).
- Absence is not empty: when "no org policy on X" is the finding, check for a governing directive/regulation that still obligates them (e.g., Ontario's Responsible Use of AI Directive applies to crown agencies even with no internal AI policy). The sharp question becomes "where is the required risk assessment and does it cover our flow?" — a checkable obligation, not a scary void.

## Deliverable form
Interactive tour = self-contained static web app (no backend, no auth, offline-capable) — runs on a laptop, embeds in a corporate LMS, drives a live demo. Token-driven theming; light default for conservative orgs (see `interactive-simulation` for the dark-mode pattern).

## Pitfalls
- Scope churn from user corrections: each correction reframes, but RE-ORDER don't rebuild — content blocks stay, emphasis moves.
- Generic integration modules = shelfware. Name the systems or cut the module.
- Don't serialize the build on research/interview inputs that only affect depth — scaffold input-independent parts in parallel.
- Never assume a term a greenfield learner hasn't met.

## References
- `references/{CLIENT}` — {CLIENT} session: {CLIENT} orientation tour, scope corrections, level calibration, AI demotion, dark-mode build.
