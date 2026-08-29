<!-- GENERICIZED: 3×{CLIENT}, 1×{RELATIONSHIP} | source: skills/learning-design/training-module-design/SKILL.md -->
---
name: training-module-design
description: "Use when building interactive training/orientation packages."
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Training, Learning-Design, Onboarding, ADHD, Interactive, Static-Web, Orientation]
    category: learning-design
    related_skills: [source-evaluation, org-tech-stack-reconnaissance, visual-report-design, interactive-term-definitions]
---

# Training Module Design

Design interactive training and orientation artifacts that a specific learner can actually use. The deliverable is a working interactive artifact (static web app), not a deck or handbook.

## When to Use

- Onboarding / orientation package for a named role (e.g., a Project Lead at an org adopting a new tool).
- Interactive tours, simulated workspaces, scenario-based training modules.
- Any "person must be able to do/ask X after this" deliverable.

## 0. Scope before design — four gates

Never start building before these are answered by the user:

1. **What does the acronym/product mean in THIS org?** Ambiguity changes everything (e.g., "ACC" = Autodesk Construction Cloud, not Accessibility).
2. **Who is the trainee** — role + department, and what must they be able to DO or ASK after training (the can-do list).
3. **Orientation vs operator level.** A leader who governs (e.g., Project Lead over Data Management/Governance) needs comprehension + an **accountability layer**: "detect the failure and ask the diagnostic question," NOT operator steps. A greenfield operator needs hands-on labs. The user's own words ("he doesn't need to produce anything, just needs to orient") decide — do not infer or flip the design on assumptions.
4. **Delivery form** — self-paced interactive (default; scales, works for a live demo too) vs facilitator-led.

Design backward from the can-do list. For a leadership learner, the output artifact = the exposure/risk map + the diagnostic question set, and the tour is how they learn to read it.

## 1. No theory without mechanics

Governance/data/integration topics become real only when nailed to concrete mechanics:

- Name real roles, real workflows, real systems — never "the project stack." (E.g., Revit/Civil 3D authoring, Aconex + ACC + SharePoint CDEs, P6 schedule, Unifier cost — ground in the org's real stack first, see `org-tech-stack-reconnaissance`.)
- Every track closes on a scenario-based question ("a subcontractor uploaded a superseded drawing — walk the correct action"), never a watched-it.
- Centerpiece for governance learners: a **permission-and-exposure map** — roles × data surfaces, severity-coded, with the diagnostic question per exposure vector; AI/automation layers as clearly-labeled projected overlays, never the lens.
- Each demonstrated scenario ends on the LEAD's question ("who holds Admin today? is the naming convention enforced or just documented?"), not the operator's step.

## 2. Provenance & honesty (client-facing, non-negotiable)

- Real program data is contract-controlled → use **synthetic-but-realistic scenarios**, and say why in the artifact.
- Vendor case-study numbers are marketing, not evidence: label "vendor-reported, not independently audited"; flag AI-drafted markers; cross-check deck vs spoken session; note anonymized-by-contract projects. Full discipline + worked example in `source-evaluation` → `references/{CLIENT}-au2024-provenance-example.md`.
- Teaching a third party's scheme (e.g., a consultant's `COMPANY_DISCIPLINE_ROLE` naming)? Label it "a real scheme to understand, not the client's house style."

## 3. The static offline web shell

- Self-contained static app: no backend, no auth, no runtime network. Runs from file:// on a laptop, embeds in an LMS, serves a live demo unchanged. Keep to ~5-6 files (index.html, css, 2-3 js; content lives in a data.js data layer).
- **Hash deep-linking** for every view (`index.html#t1-questions`) — shareable and resumable.
- **localStorage wrapped in try/catch** (Safari private mode throws on writes); theme applied BEFORE first paint via a tiny inline `<head>` script (no light-flash on reload); light default for conservative orgs.
- **Theme = CSS custom properties only**: `:root[data-theme="dark"]` swaps tokens; semantic/severity colors keep their own variables — recolor the surface, never the meaning.
- **Bilingual terminology toggle** for product rebrands (ACC → Forma): current naming default, one tap to legacy naming. Implement as an idempotent in-place text-node transform (negative-lookbehind rules so it cannot double-apply; `nofn` flag on copy that names both products). Never rebuild via innerHTML — it destroys event listeners (use a text-node walk).
- QA matrix: views × themes × naming modes, zero console errors, interactivity verified in every mode.

## 4. ADHD adaptation — invisible

Good design, not therapy: **no disability labeling anywhere** in a professional artifact; no gimmicks; nothing gamified for its own sake.

- One idea per view; generous whitespace; chunk everything. Progressive disclosure (spot → locate → land) is ADHD-friendly — keep it as the default path, not an optional extra.
- Micro-rewards: short sections that finish, visible progress, "N of M" counters, step indicators. Completion must feel like winning, instantly.
- **Variable-focus design**: every view must survive entry at any point. Persistent "where am I" breadcrumb; resume-point persistence (localStorage; explicit deep-link wins on load); time-box labels ("~8 min"); payoff line at track top ("By the end of this track you can ask…").
- **One-hop re-anchors, not recaps**: each dependent view re-establishes only its single parent concept ("In this zone, teams see only their own folder") — never a summary of the course (recaps reintroduce the density you are cutting).
- **Companion-object elimination** (the completion reward): a small dim token beside each TEXT block (never whole-container clickable — a misclick mid-reading deleting the text is catastrophic for this learner). Clicking kills that element fast (300-400ms), non-blocking (the next click must work while the previous animation runs), effects cycled at random (swipe / shatter / melt). **Persist cleared state keyed by content-derived stable key** (viewId||content-hash), never array index — content edits shift indices and silently mis-associate cleared state (an edited block should reappear as new). "Reveal everything" reset in the chrome clears stored state too. Counter "N of M cleared" (M = eliminable text blocks only; structural/interactive blocks carry no token). One-time hint on first use, then never.
- Arrow-key navigation (←/→ page through tour order); deep-links and resume-point still win on load.

## 5. Verification discipline (multi-agent builds)

Never trust a teammate's "built and verified" — verify on the artifact yourself:

- search_files the data layer for the exact tokens/content claimed.
- Check CSS token structure, keydown handlers, persistence keys, and nav entries (old views removed from nav, not just hidden).
- For factual claims entering the deliverable, verify against primary sources (vendor's own announcements, conference records) and report confidence levels (high/moderate/low/unknown) + method + gaps.

## Pitfalls

- Building before the learner and can-do list are defined — the single biggest waste.
- Flipping the design repeatedly on assumptions: hold the fork — build shells that serve either depth until a fact decides.
- Array-index keys for any persisted per-block state.
- innerHTML rebuilds destroying listeners; non-idempotent text transforms double-applying ("Forma Forma Build").
- Slow (>500ms) animations feel like waiting to an ADHD learner; effects must never block the next action.
- Unlabeled vendor metrics or third-party schemes in a government-facing artifact.
- Unpersisted elimination state quietly destroys the reward loop — build persistence from the start, not retrofitted.

## References

- `source-evaluation` → `references/{CLIENT}-au2024-provenance-example.md` (vendor-claim verification worked example: {CLIENT} AU 2024 class + ACC→Forma rebrand verification).
