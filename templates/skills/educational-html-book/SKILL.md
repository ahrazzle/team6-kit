<!-- GENERICIZED: 2×{HABIT}, 1×{RELATIONSHIP} | source: skills/educational-html-book/SKILL.md -->
---
name: educational-html-book
description: Build HTML books with real visuals and clickable terms.
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [design, html, book, educational, encyclopedia, recipe, health, interactive, visual]
    related_skills: [claude-design, popular-web-designs, design-md]
---

# Educational HTML Book Builder

Build designed HTML books — recipe collections, study guides, field manuals, remedy compilations — that combine instructional content with deep contextual information, real visual assets, and interactive encyclopedia features.

## When To Use

Use this skill when the user asks for:
- Recipe books with health/scientific context woven between steps
- Educational content with clickable terms that reveal deeper explanations
- Books or guides that need real photographs, diagrams, maps, or process visualizations
- Content with evidence-level markers (High/Moderate/Traditional)
- {HABIT}-accessible instructional design with readability-first principles

## Core Principles

### 1. Real Visuals, Never Placeholders

The user explicitly rejects placeholder boxes. If you cannot source an image or diagram, leave the container empty with a descriptive prompt for the user to generate externally — never ship a dashed-border `div` saying "Botanical illustration of X."

**Photographs**: Use Unsplash API (`api.unsplash.com/search/photos`) with the provided client_id. Always include `loading="lazy"` on images.

**Diagrams**: Create inline SVG with clear viewBox, labeled parts, and caption below. Use the recipe's color palette.

**Maps**: Simple SVG with circles for locations, dashed paths for routes, and text labels.

Structure: Wrap visuals in `<div class="visual-container"><div class="visual-frame">...</div><p class="visual-caption">...</p></div>`

### 2. Interactive Encyclopedia Terms

```html
<span class="clickable-term" data-term="Term Name">
  Term Name
  <span class="term-tooltip">Brief definition shown on hover</span>
</span>
```

Add JavaScript that fetches Wikipedia summaries on click.

### 3. Masculine Aesthetic Mode

- **Typography**: Stronger weights (700-800), tighter letter-spacing, uppercase transforms on headings
- **Language**: Direct, declarative sentences. Active voice exclusively. Short paragraphs (2-3 sentences max).
- **Visual weight**: Heavier borders, stronger shadows, more geometric shapes
- **Color**: Deeper, more saturated tones. **Avoid pastels** (pink, lavender, mint) unless required for contrast/readability
- **Tone**: Authoritative but not clinical. Confident. "This broth extracts" not "This broth may help to possibly extract"

### 4. Content Credibility Markers

- **Evidence badges**: `<span class="evidence-badge evidence-high/moderate/traditional">Label</span>`
- **Safety warnings**: `<div class="safety-warning"><i class="fas fa-exclamation-triangle"></i><span>Warning</span></div>`
- **Honest framing**: Distinguish between clinically proven, traditionally used, and preclinical research

### 5. Context Weaving Pattern

Alternate between:
1. **Action step** (numbered instruction)
2. **Context block** (health mechanism, history, culture, fun fact)
3. **Visual** (image, diagram, or map)

Place context blocks after steps involving waiting (simmering, steeping, soaking).

## Navigation Patterns

- **Skip link**: `<a href="#content" class="skip-link">Skip to first recipe</a>`
- **Fixed top nav**: `<nav class="nav-top">` with Contents and Shopping Guide links
- **Back to TOC**: `<a href="#toc" class="back-to-toc">↑ Back to Contents</a>` after each recipe
- **Smooth scroll JavaScript** for anchor clicks

## Accessibility Minimums

- ARIA labels on landmarks and navigation
- Semantic HTML (article, nav, section, header, footer)
- Focus states on interactive elements
- Minimum 18px body text, 1.6+ line height
- WCAG AA contrast ratios

## {HABIT}-Specific Patterns

- **Recipe meta**: Prep time, cook time, serves, difficulty at a glance
- **Pantry-availability icons**: 🟢 Pantry staples, 🟡 Specialty/health store, 🔴 Compounding required
- **Physical demand warnings**: Flag heavy lifting, long simmering, sharp tools
- **Where to Find section**: Shopping guide with store types

## Pitfalls

- Do not ship placeholder boxes for visuals — source real assets or leave empty with prompts.
- Do not fabricate health claims or overstate evidence — use honest evidence-level labels.
- Do not conflate different species or traditions — be precise about cultural origins.
- Do not use pastel colors (pink, lavender, mint) in the palette — stick to deep, saturated tones.
