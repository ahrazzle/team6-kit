<!-- GENERICIZED: 6×{CLIENT}, 8×{RELATIONSHIP} | source: skills/productivity/training-package-design/references/{CLIENT} -->
# {CLIENT} — {CLIENT} / Autodesk Construction Cloud orientation tour ({CLIENT})

**Task:** Training/orientation package so a {CLIENT} employee could understand Autodesk Construction Cloud (ACC) as used on a complex subway program (GO Expansion / Ontario Line axis).

## Learner profile (primary source, user interview)
Project Lead managing **Data Management & Integration** + **Governance** departments. Greenfield (never worked with ACC), needs to ORIENT because his team will use it, does NOT produce artifacts. Interests: access controls, data protection, how those relate to AI integration.

## Scope evolution — user corrections that reshaped the build
1. "ACC" → **Autodesk Construction Cloud** (construction-program tool, NOT transit ops — research axis flipped to capital-projects side: GO Expansion, Ontario Line, Eglinton Crosstown).
2. Scope confirmed: governance, data management, integration on a complex infrastructure subway project.
3. Role + "he doesn't need to produce anything, just needs to orient" → killed the skills-lab plan; became a read-mode interactive tour.
4. AI demoted: "government org, slow to adopt... AI is secondary focus, not the focus by any means." → AI went from through-line to ONE consolidated closing chapter ("Where this is heading"); human access map became the primary centerpiece; AI layer became a clearly-labeled "Projected" overlay toggle. Lesson: **emphasis mirrors the org's real maturity, not the projected one.**

## Design decisions that held
- **Module 0 "ACC from zero"** (product family, Project→Folder→File object model, CDE concept) — nothing downstream assumes an unknown term.
- **Tracks 1-3** (Governance / Data management / Integration), every track closing on the **lead's diagnostic questions** (accountability layer — can-do = detect the failure, not perform the action).
- **Centerpiece: permission-and-exposure map** — roles × data surfaces, human-first; AI as projected overlay; each vector card carries the lead's "Ask" question.
- **Fidelity contract:** shell's object model mirrors real ACC; honest-to-ACC labeling so the sim isn't internalized as the product.
- **Re-order, don't rebuild:** when emphasis shifted, content blocks were reused; defaults/order/labels changed, nothing regenerated.

## Research grounding (what made it non-generic)
- **ACC in production on {CLIENT} capital delivery** — HDR runs Ontario Line design CDE on BIM 360/ACC (320+ federated models, ArcGIS connector); ONxpress Civil JV runs ACC + Aconex + SharePoint on GO Expansion. NOT a ProjectWise→ACC introduction story.
- **ISO 19650-aligned house style:** MX-ALM-STD-004 (CADD/BIM Standards Manual), AIR, EIR, MIDP, BEP template — teach the house style AS the standard.
- **Counterpart stack:** Revit/Civil 3D/InfraWorks/AutoCAD · ArcGIS + BIM 360 connector · Aconex + ACC + SharePoint · Primavera P6 · Oracle Unifier · FME.
- **AI findings:** no {CLIENT} program-level AI-over-CDE policy (only public website chatbot clause) — BUT Ontario's **Responsible Use of AI Directive** applies to crown agencies (executive accountability for AI risk). Framing: "absence of policy ≠ absence of obligation; the gap is operationalization, not law." Autodesk AUP (late-2025) permits customers to train own models on own data → external-LLM path is contractually open but project-governance ungoverned.

## Build / QA flow
- Static 5-file app (~85 KB): index.html + css/app.css + js/{app,data,tour}.js; 19 views; hash deep-linking (shareable per-view URLs).
- **Independent artifact verification caught the gap:** build landed before research finished; the vector-2 card still carried a generic question. Orchestrator grep'd the data layer for the research findings (`Directive`, `AUP`, `Trust Center`) — zero hits — before shipping. After the fix: 41/41 headless Chromium checks green, zero console errors.
- Three independent verifications of the final re-order (build report + {RELATIONSHIP}'s artifact check + {RELATIONSHIP}'s structural check + orchestrator spot-check) — report-triangulation plus artifact inspection.

## Dark-mode static app pattern (reusable)
- All colors as CSS custom properties; `:root[data-theme="dark"]` swaps tokens ONLY — no hand-recolored component rules.
- Semantic colors keep meaning across palettes: severity cells own `--sev-*` vars (light + dark variants) — recolor the surface, never the meaning.
- Palette: deep slate (`#14171c` page, `#1a1e26` cards), desaturated accents (coral/cobalt) so nothing burns on dark.
- Persistence: `localStorage` key wrapped in try/catch (Safari private mode throws on storage writes); early inline `<script>` in `<head>` applies the theme before first paint — no light-flash on reload.
- Toggle in persistent chrome (sidebar), same place every view; pin visible — with 19 nav items it dropped below the fold, fixed by making the nav scroll internally.
- Light = default for conservative orgs.

## Ownership model (which agent did what)
- {RELATIONSHIP}: research (CDE reality, ISO 19650 house style, counterpart stack, AI policy gap).
- {RELATIONSHIP}: scope-cutting (killed skills-lab for an orientation learner; flagged "integration" filler risk; added accountability layer).
- {RELATIONSHIP}: architecture (module map, dependency order, re-order spec, fidelity contract).
- {RELATIONSHIP}: form + interaction pattern (read-mode tour, exposure map read-layers, dark palette).
- {RELATIONSHIP}: build + QA (shell, re-order, dark mode; 41/41 checks).
- {RELATIONSHIP}: routing, decision-locking, design record (IDEA.md updated at every convergence), artifact verification.
