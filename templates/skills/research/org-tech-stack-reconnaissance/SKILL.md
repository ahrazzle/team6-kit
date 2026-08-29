<!-- GENERICIZED: 4×{CLIENT}, 1×{RELATIONSHIP} | source: skills/research/org-tech-stack-reconnaissance/SKILL.md -->
---
name: org-tech-stack-reconnaissance
description: Research an org's software stack to ground deliverables.
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
tags: [research, org-research, software-stack, cde, training, onboarding, governance]
---

# Org Tech-Stack Reconnaissance

Research what an organization **actually runs** — software platforms, document/standards conventions, org anatomy, internal training infrastructure — so an org-specific deliverable (training package, onboarding, integration plan, migration assessment) is grounded in verifiable reality instead of generic boilerplate.

## Trigger

Use when the user asks to:
- Build a training/onboarding package for [org] employees on [tool]
- Determine whether an org uses [tool] at all, or is introducing/migrating to it
- Name the real counterpart systems on a program's stack
- Ground any deliverable in real org anatomy ("no generic onboarding boilerplate")

## Core Principle: Verify Tool-In-Use Reality FIRST

Before any architecture work: is the tool in production, being introduced, or in coexistence/migration with others? This one fact changes the framing of the whole deliverable:
- **In production** → teach usage, workflows, governance as-is.
- **Being introduced / coexisting** → the opening chapter is migration/dual-running reality, not a usage tutorial.
- **Not in use at all** → the package is either advocacy or mis-scoped; say so before building.

A package named after a tool the org doesn't run is shelfware. A package that says "integrate with the project stack" without naming the counterpart systems teaches people to integrate to nothing.

## Evidence Pyramid (best sources first)

1. **The org's own published documents.** Standards libraries, manuals, policies, multi-year plans. Reveal governance conventions, naming schemes, house style, AND internal platforms. Example: {CLIENT} publishes its CADD/BIM Standards Manual, EIR/AIR/MIDP templates — these name the actual document-control conventions trainees will meet.
2. **Job postings and hiring specs.** The single best primary source for the ACTUAL stack. Postings name exact tools and mandatory skills (e.g. "expert in Primavera P6 is mandatory"). Contractor and alliance-partner postings are as informative as the org's own — on megaprojects the contractor runs the tooling.
3. **Vendor conference case studies + trade press.** Autodesk University classes, ENR, etc. confirm specific platforms on specific named projects, with named principals and quantities.
4. **Wikipedia / summary pages.** Only for org-identity basics (legal form, parent, history). Always cross-check.

## Process

1. **Correct the org identity first.** Is it a government department, a crown agency, a private contractor, an NGO? "Crown agency of Ontario" vs "Canadian government org" changes framing, reporting chain, and compliance context. Get the legal form and the governance chain (board → minister → ministry).
2. **Find the internal training platform early.** Large orgs run one (e.g. "{CLIENT} University"). If the deliverable is onboarding, that platform is the natural delivery target — and published plans often reference it.
3. **Map the org anatomy** relevant to the deliverable: operating divisions/brands vs capital-delivery arms, and which side of the house the trainee lives in (design-side CDE often differs from construction-side CDE).
4. **Name the counterpart systems** — the integration layer is only real when counterpart systems are named: authoring tools, schedule, cost/contract platform, document platform, GIS, data-movement tools.
5. **Report in three buckets:** Verified (source named) / Inferred (reasoning stated) / Unknown (open gap named, with what would close it). Each finding gets a confidence level. Never paper over the gap.

## Pitfalls

1. **Don't assume the tool the package is named after is org-wide.** Verify usage vs. introduction vs. coexistence per program/segment. An org can run ACC on one program and Aconex on another, with SharePoint everywhere.
2. **Design-side ≠ construction-side.** The same program may use BIM 360/ACC on the design side and a multi-CDE stack (ACC + Aconex + SharePoint) on construction. Say which side your evidence covers.
3. **Contractor postings are primary sources, not hearsay.** Alliance/JV partner hiring specs describe real production environments. Cite them.
4. **House style is usually a standard "in clothing."** ISO 19650-style orgs rarely teach the raw standard; they teach EIR/AIR/MIDP/BEP as the real names. Teach the house style as the standard's local manifestation.
5. **Check for a documented endgame** (e.g. digital-twin / asset-information handover target). It turns "data handover" from a hypothetical into a named corporate goal, and anchors the close of the deliverable.

## Output Format

For a room/briefing deliverable:
1. Executive summary (the one fact that decides architecture — usage vs migration)
2. Org identity + governance chain
3. Tool-in-use verdict per program/segment (with sources)
4. Standards/conventions (house style vs raw standard)
5. Named counterpart systems table (layer → system)
6. Internal training platform / delivery target
7. Open gaps (confidence: unknown)

## References

- `references/{CLIENT}` — {CLIENT} + Autodesk Construction Cloud knowledge bank (verified stack, ISO 19650 house style, counterpart systems, delivery target, open gaps). Worked example of the full methodology.
