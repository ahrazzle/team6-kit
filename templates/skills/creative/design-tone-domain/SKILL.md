<!-- GENERICIZED: 1×{RELATIONSHIP} | source: skills/creative/design-tone-domain/SKILL.md -->
---
name: design-tone-domain
description: Match visual design tone to content domain.
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [design, ux, tone, domain, aesthetics, institutional, editorial, financial]
    related_skills: [claude-design, sketch, design-md]
---

# Design Tone for Content Domain

Use when designing any HTML artifact where the **subject matter demands a specific aesthetic register**. The core failure mode this skill prevents: applying a colorful, playful, "bubbly" design to serious content like financial analysis, economic research, or institutional reports.

## Trigger

- The artifact presents analytical, financial, economic, legal, academic, or institutional content
- The user corrects the tone ("too colorful", "too bubbly", "inappropriate for the subject")
- You're about to choose colors, typography, or visual treatment for a content-heavy artifact
- The content is data-dense and meant to inform decisions, not entertain

## Core Rule

**Read the content before choosing visual tokens. The content's domain dictates the design's tone.**

A Federal Reserve analysis and a startup landing page are both "design work" but require opposite aesthetic registers. Reaching for bright gradients, emoji, rainbow palettes, or decorative energy on serious content is a judgment failure, not just a style mismatch.

## Domain Tone Map

| Domain | Tone | Do | Don't |
|---|---|---|---|
| Financial / economic / analytical | Restrained, institutional, authoritative | Muted single accent (warm gold on deep navy), monochrome data scales, serif headlines, high data density, thin borders, minimal decoration | Bright gradients, emoji, rainbow palettes, playful hover effects, oversized decorative elements, colored dots on every card |
| Editorial / journalism | Clean, readable, typographic | Serif headlines, generous line height, restrained color, pull quotes, ample whitespace | Card grids with icons, data-dashboard styling, heavy decoration |
| Academic / research | Precise, structured, citation-friendly | Clear hierarchy, numbered sections, restrained color for figures, readable body text, table-forward layouts | Marketing heroes, decorative imagery, playful color |
| Marketing / SaaS | Polished, modern, conversion-oriented | Strong hero, feature cards, motion, brand colors, social proof | Overly dense text layouts, institutional austerity |
| Technical / developer tools | Precise, dense, utilitarian | Monospace accents, compact spacing, code-forward layouts, functional color only | Marketing heroes, decorative imagery, playful tone |
| Institutional / government / policy | Formal, accessible, trust-building | Clear hierarchy, generous spacing, high contrast, structured sections, minimal color | Trendy design patterns, informal type, decorative elements |

## Restrained Design System (Financial/Analytical Default)

When content is financial, economic, or analytical, default to this system unless directed otherwise:

**Colors:**
- Background: deep navy/near-black (#0b1120 range)
- Surface: slightly lighter navy (#111c2e, #152236)
- Single accent: muted warm gold (#c9a234) — used sparingly for primary data points and key callouts
- Data visualization: monochrome scale (slate blue → steel) with gold reserved for the highest-priority item
- Text: off-white (#e8edf4) primary, muted blue-grey (#8899b0) secondary
- Risk/danger: desaturated red (#b94a5a) — only for tags, not decoration
- Success/ok: desaturated green (#3d8b6e) — only for tags

**Typography:**
- Headlines: serif (DM Serif Display or similar) — conveys authority and tradition
- Body: clean sans-serif (DM Sans or similar) — readability for dense content
- Data/labels: monospace (DM Mono) — precision for numbers and codes
- One typeface per role. No decorative or display fonts.

**Layout:**
- Generous whitespace between sections (2.5–3rem vertical)
- Compact cards and tables within sections
- No radial glows, gradient backgrounds, or decorative shadows
- Callouts: thin left border (2px) in accent color, muted background
- Bar charts: flat fills, no gradients; monochrome scale with gold for primary

**Forbidden on serious content:**
- Emoji (unless the brand explicitly uses them)
- Rainbow palettes
- Gradient bar fills
- Colored dots on every card
- Decorative icons as card toppers
- Oversized rounded rectangles as hierarchy substitutes
- Glassmorphism

## Pitfall: The "Default to Colorful" Reflex

AI design models default to colorful, high-energy palettes (indigo/violet gradients, rainbow data scales, emoji accents). This is appropriate for marketing surfaces but **institutional failure** on analytical content. When the content is serious, you must actively suppress this reflex.

**Corrective check before finalizing:**
1. Count the distinct colors in your design. If more than 4 (excluding neutrals), you likely have too many.
2. Check for emoji. Remove unless explicitly requested.
3. Check bar chart colors. If they're a rainbow, convert to monochrome scale.
4. Check for decorative elements (gradients, glows, icons). Remove anything that doesn't communicate data or structure.
5. Ask: "Would this design be appropriate in a central bank research publication?" If not, simplify.

## Workflow Integration

This skill complements `claude-design`. After committing to a surface archetype and before defining the design system:

1. **Classify the content domain** using the tone map above
2. **Select the appropriate tone** (restrained, editorial, academic, etc.)
3. **Choose tokens that match** — don't reach for your default palette
4. **Run the corrective check** before finalizing

## Verification

Before delivering, confirm:
- The design tone matches the content domain
- Color is used functionally (data encoding, hierarchy) not decoratively
- No emoji, rainbow palettes, or playful elements on serious content
- Typography conveys appropriate authority for the domain
