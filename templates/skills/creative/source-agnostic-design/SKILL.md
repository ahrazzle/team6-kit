<!-- GENERICIZED: 3×{CLIENT}, 1×{RELATIONSHIP} | source: skills/creative/source-agnostic-design/SKILL.md -->
---
name: source-agnostic-design
description: Design source-neutral frameworks.
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [design, ux, framework, neutrality, pluralism, sources, onboarding, multi-source]
    related_skills: [claude-design, sketch, design-md]
---

# Source-Agnostic Framework Design

Use when the product has multiple authoritative sources, editions, or traditions — and users from different schools of thought expect their own sources. The framework itself is neutral; it renders based on the user's chosen sources.

## Trigger

- Users belong to different schools/traditions and need their own sources
- No single "correct" source exists — the value is in the framework, not the content
- Existing tools hardcode one or two sources
- The user says "let users choose their own sources" or "source-agnostic" or "framework, not content"

## Core Principle

**The framework is the product. The sources are user-configurable.** Neutrality is structural (enforced by architecture), not cosmetic (a "we don't endorse anyone" disclaimer).

## Architecture (UX Layer)

### 1. Source Chooser = First-Run Experience

Not buried in settings. The onboarding IS the product. "Build your study panel" or equivalent. This is the first thing every user encounters — it defines what the app *is* for them.

### 2. Selection Model

- **Multi-select** where users engage with multiple sources simultaneously (e.g., multiple commentary editions)
- **Single-select** where only one makes sense at a time (e.g., one translation to read)
- **Optional compare toggle** for a secondary single-select (side-by-side comparison)

**Rendering rule that enforces it (load-bearing):** at the study/drill-down level, show **one
source at a time** with a switcher (dropdown, sidebar, segmented control) — NEVER two or more
sources' content stacked on screen simultaneously. Stacking forces the user to compare when
they came to study, and reads as clutter. This is the single most common oversight in
multi-source frameworks; the user caught it shipping and flagged it as an obvious design
failure. Single-source-at-a-time is the industry-standard pattern (every major Quran app does
it for {CLIENT}). The switcher re-renders the pane instantly and non-destructively.

### 3. Change Sources Anytime

Accessible from the main surface (e.g., a source icon in the header), not just onboarding. Switching re-renders instantly, non-destructively. No "are you sure" — it's reversible.

### 4. Source Transparency on Every Data Point

Every piece of content shows its source attribution inline. Tap the source name → full metadata card (author, era, tradition, methodology, language, license, completeness).

### 5. Source Conflict = Trust Signal

When enabled sources disagree, surface both with a "sources differ" indicator. The framework does not adjudicate. This is the trust signal — hiding disagreement destroys credibility.

## Guided Onboarding with Neutrality

**Problem:** Guided paths ("I follow tradition X") require curation, which IS privileging sources — contradicting the neutrality principle.

**Resolution:** Curate starting points, not sources. Frame as "Most users start with:" followed by 2-3 popular combinations. Each is a pre-built panel, not an editorial endorsement. "Build my own from scratch" is always the first option, not an escape hatch.

The editorial standard is transparent ("most users start here") rather than prescriptive ("these are the right sources").

## Source Metadata Schema

Each source needs:
- `source_id` — canonical identifier
- `source_type` — {CLIENT} / translation / recitation / linguistic / etc.
- `tradition` — descriptive label (not prescriptive)
- `author` — name + era/date
- `language`
- `methodology` — one-line description
- `license_type` — public_domain / cc / copyright_linkout / copyright_restricted
- `completeness` — % of content covered

## Scope Narrowing Is A Product Decision, Not A Design One

The framework architecture stays source-agnostic, but the **source catalog** is a scoped product
decision. When the user narrows it, treat the narrowing as a curation boundary and stay neutral
WITHIN it — do not relitigate the scope.

- A typical narrowing: **Sunni scholarship + classical Sufism only** — explicitly excluding
  Shia/Ja'fari, Mu'tazili, and fringe/offshoot groups. Driven by market/boycott risk and
  community trust, not by design preference.
- **Classical Sufism needs a within-tradition filter.** Mainstream Sufi scholars (Ghazali,
  Rumi, Sulami, Ibn Arabi's earlier works) sit inside Sunni orthodoxy; fringe esotericism
  (Batiniyya, extreme monist positions) does not. Tag the catalog so "Sufi-influenced but
  Sunni-mainstream" sources are separable from those that veer fringe. This keeps the bucket
  clean — classic Golden Age only.
- **Accuracy boundary:** the platform's OWN content (e.g., a modular grammar system) is
  verified to a strict standard; sourced scholarly content ({CLIENT}, asbab, cross-refs) is
  presented as-is with attribution. Contradictions between scholars are the reality of
  fragmented schools of thought, not the platform's error. Design for "we present, we don't
  adjudicate" — surface divergence with both sources visible, never hide it.

## Study/Drill-Down Pane Design

When the user taps into a source-attributed item:
- The content itself (text, excerpt, annotation)
- Source attribution (which source this came from)
- Cross-references to other enabled sources
- Occurrences / connections to other content
- **Context is sacred** — the pane is a bottom sheet or overlay, not a full-screen replacement. Never lose the primary content.

## Design Principles

1. **Neutrality by design** — No default weighting, no ranking. The architecture enforces it structurally.
2. **Context is sacred** — Never lose the primary content when drilling into a source.
3. **Progressive disclosure** — First tap shows the most important layer. Deeper layers on demand.
4. **No dead ends** — Every cross-reference, every occurrence is tappable. Exploration branches infinitely.

## Pitfalls

- **MVP drift into framework-building** — If the goal is to prove a data join works, the source chooser, source registry, and query-time filtering are NOT load-bearing. Prove the join first (2 sources, raw JSON, one screen), then build the framework. The framework is v2; the proof is v1.
- **Guided paths becoming editorial** — If you offer "tradition-based" paths, you're curating which sources appear. Either make curation criteria transparent (popularity, completeness) or offer only "show everything" with optional filters.
- **Source metadata as afterthought** — Source metadata is a content product in itself. It requires research, curation, and maintenance. Budget real work for it.
- **Hardcoding sources in architecture** — Even if v1 only has 2 sources, the data model must support N. Retrofitting source attribution onto anonymous records is a migration nightmare.

## Related Patterns

- See `claude-design` for general design process, surface archetypes, and anti-slop rules.
- See `sketch` for rapid mockup workflows when exploring source-chooser layouts.
- See `design-md` if the source metadata itself needs a formal token spec.
