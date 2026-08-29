<!-- GENERICIZED: 4×{CLIENT}, 1×{RELATIONSHIP} | source: skills/creative/interactive-training-design/SKILL.md -->
---
name: interactive-training-design
description: Design interactive web-based training/orientation artifacts.
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [design, html, training, learning, ux, accessibility, adhd, interactive]
    related_skills: [user-design-aesthetic, interactive-data-simulation, claude-design]
---

# Interactive Training Design

Use when the deliverable is an **interactive web-based training / orientation / onboarding artifact** — teaching a person to *understand and govern* a system, not to operate it. Classic triggers: "training package," "orientation," "teach my team X," a learner who must *follow conversations and ask the right questions* about a governed system (permissions, data, integrations).

Load alongside `user-design-aesthetic` (this user's visual preferences) and `interactive-data-simulation` (adjacent: scenario explorers from source docs). The two differ in purpose: a *simulation* lets a user adjust assumptions and watch outcomes; a *training tour* teaches comprehension of a system.

## First, classify the learner — depth decides the whole build

Get these from the user/interview BEFORE designing. Do not guess.

1. **Operator or stakeholder?** Will they *produce artifacts* in the tool, or just *orient* to it because their team uses it? An operator wants a hands-on lab with graded mechanics; a stakeholder wants a conceptual orientation with no graded prove-it machinery. Building a skills-lab for an awareness-level learner is the #1 overengineering trap.
2. **What must they be able to DO after** (the can-do list) — artifacts, not job title. For a governance/lead learner this is "detect the failure / know what to ask," not "perform the action."
3. **Greenfield or experienced?** A greenfield learner has zero vocabulary — the simulation is the *only* model of the product they'll have seen. That demands a **fidelity contract**: the simulated object model must mirror the real product (real roles, real folder logic, real names) or you train them on a fiction that fails on contact.
4. **Delivery mode** — self-paced lab or facilitator-led workshop. Self-paced scales and the simulated workspace works either way; default to it unless the user objects.

## ADHD-friendly UX (the reward-and-attention layer)

For a wandering-focus learner, design FOR the brain's mechanics, not against them. These are invisible good design — **never label the adaptation** ("ADHD" never appears in artifact copy/chrome; this is a professional package that happens to hold a wandering brain). Guardrail: good design, not therapy.

- **One idea per view.** Cut density ruthlessly. A linear spine stays, but every view must survive mid-chaos entry: **one-hop re-anchor** — each view re-establishes its *single parent concept* in one line ("In this zone teams see only their own folder"), NOT "as we saw in WIP" and NOT a recap of the whole course. One hop deep, no deeper, or the recap reintroduces the density you cut.
- **Payoff line at track top.** Each section opens with "By the end you can ask: …" — the motivation to start forms before content loads.
- **Time-box labels** ("~8 min") in a persistent breadcrumb — visible commitment for time blindness.
- **Where-am-I strip.** Persistent crumb bar: section · view · "9 of 27" · ~8 min. Sameness of chrome is an anchor.
- **Resume-point persistence.** localStorage the last view; returning learner lands where they stopped, deep-link wins when present.
- **Progress that closes loops.** Case/beat sequences show "Step N of 3" + a filling progress bar; visible completion is the reward.
- **Beware two failure modes:** overwhelm (too dense → chunk + one-idea) and boredom (feels like a lecture → make the interactive detective path the DEFAULT, not optional).

## Detective-sequence scenarios (prove comprehension without operator-training)

The "read the map" pattern: a case study becomes a guided sequence, not a story. Three beats:
1. **Spot** the anomaly in a live view (danger-highlighted cells, progressive-disclosure reveal).
2. **Locate** it on the centerpiece map (responsible rows pinned/outlined as they hover).
3. **Land** the diagnostic question the learner must be able to ask.

Each case closes on the *lead's* diagnostic question, not the operator's step. Present situations, don't narrate them — reveal progressively so the learner forms hypotheses. Reuse the same scenarios across tracks (e.g. admin-role ballooning → governance; superseded drawing → data; unauthorized export → integration).

## Completion / elimination mechanic (the dopamine loop)

Let the learner eliminate elements as they finish them. This is the strongest engagement device — every elimination must feel like **closing a loop**, instantly.

- **Companion-object version, NOT whole-container clickable.** A small dim token (✕) beside each text block. Whole-container click risks a misclick mid-reading deleting the text you're reading — catastrophic for a wandering-focus learner (losing your place = instant dropout).
- **Eligibility rule:** text-bearing blocks only (paragraphs, callouts, bullets, question cards, tiles). Structural/interactive blocks (maps, sim, tables, footers, nav) carry NO token — else tokens clutter and the counter lies. The "N of M cleared" counter's denominator = eliminable blocks on screen.
- **Effects:** a SMALL set done well (swipe / shatter / melt), cycled per element or at random. Fast (~300–400ms) — slow animation feels like waiting, not winning. **Never block the next click** (clear next block while previous still animating).
- **Persistence is mandatory** or the loop backfires. Key cleared-state by a **content-derived stable slug**, not array index — content gets edited and an index key silently mis-associates cleared elements (cleared card reappears; new card stays hidden). Same content → same key survives nav/reload; edited block → new key → reappears as new. Persist only the *fact* of clearing, not the effect choice (animation is transient fun).
- **Reset in the chrome** ("reveal everything") must clear the STORED state too, not just the in-memory copy, or a reload undoes the reset.
- **One-time subtle hint** on first use ("done with this? tap the token"), then never returns.
- Cosmetic only: cleared elements collapse the layout smoothly (animate height/margin to zero), no dead gaps.

## Dual-mode terminology toggle (current vs legacy naming)

When a product was rebranded/renamed (e.g. ACC → Forma: Account Admin → Hub Admin, Docs → Data Management), a greenfield learner already has zero vocabulary — a second name for every term doubles cognitive load. Don't ship a glossary. Ship a **bilingual toggle**: runs in *current* naming by default (what the product shows now), one tap switches to *legacy* so the learner can follow teammates using old names. Wire it through EVERYTHING (nav, content, map, title bar). Title-bar chrome should match what the learner will actually open. Guard against double-transform bugs (a transform re-applying to already-transformed text, e.g. "Forma Forma Build").

## Grounding & provenance discipline (training artifacts are cited, not marketing)

- **Anchor content in real, named systems** — not "the project stack." A "integrate with X" module with no named counterparts teaches integrating to nothing. Ground seams in the real stack.
- **Synthetic data when real data is contract-controlled** (government/proprietary programs). Fabricated-but-realistic scenarios teach the same logic without leaking sensitive material. State WHY synthetic in a callout.
- **Label provenance honestly.** Vendor case-study numbers are self-reported, not audited — flag them as such in the source note ("vendor-reported, not independently audited," "transferable reference, not [this org]-documented," contractually anonymized, spoken-vs-deck discrepancies). Also label whose scheme you're teaching ("this is {CLIENT}'s permission scheme, not {CLIENT}'s"). A government-facing artifact that cites unverifiable "-80%" gets challenged in audit — provenance labeling is what keeps it defensible. This is the difference between a training artifact and a vendor infomercial.
- **Configuration IS governance, and configuration drifts.** The strongest governance lessons are about one-time setup decisions that quietly rot until audited (features deliberately switched off, review-workflow templates teams reconfigure wrong). The diagnostic: "who decided this configuration, and who re-audits that it hasn't drifted?" — wire scattered question cards to share ONE thesis so they read as a pattern, not a list.

## Technical / build conventions

- **Static, self-contained, offline.** No backend, no auth, no runtime network — same artifact runs on a laptop, embeds in an LMS, or serves a facilitator live. Keep to a handful of static files (HTML + CSS + JS + assets).
- **Invisible adaptation** — implement ADHD/accessibility mechanisms as CSS/UX passes, not a rebuild; no emoji/glyph overload, no labeling.
- **Theme + naming toggles** in persistent chrome; persist to localStorage (try/catch for private mode); light + current-naming default (matches conservative orgs).
- **Persistence keys:** prefix per app (`{CLIENT}`, `{CLIENT}`), content-derived keys for element state.
- **QA matrix:** run every view × theme × naming mode (e.g. 27 views × light/dark × Forma/ACC) with headless rendering; assert new-content presence, no double-transforms, persistence across reload, zero console errors.
- Text-extract source PDFs via the text layer (no vision) when the user restricts cost — `pdftotext` gives full document text for large decks.

## Pitfalls

- Building a skills-lab for an awareness-level learner — the top overengineering trap; classify the learner first.
- Unpersisted elimination state — destroys the completion loop; must ride the same localStorage as resume-point.
- Array-index-keyed state — breaks on any content edit; use content-derived stable keys.
- Whole-container click-to-eliminate — misclick deletes the text mid-read.
- No provenance on vendor figures — unverifiable numbers get challenged in a government audit.
- Teaching "the stack" without naming real counterpart systems — generic filler.
- Naming-transform double-applied — "Forma Forma Build"; make the transform idempotent (negative-lookbehind, canonical source).
- One-hop re-anchor collapsing into a full recap — reintroduces density; one parent concept per view only.

## Final Response Format

```
Tour v{N} — [what changed]

[Key design decisions with learner benefit]

File: [path]
```
