<!-- GENERICIZED: 1×{AMOUNT}, 1×{HABIT}, 1×{RELATIONSHIP} | source: skills/creative/html-report-design/SKILL.md -->
---
name: html-report-design
description: Design HTML reports with domain-appropriate visual energy.
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [design, html, report, dashboard, data-visualization, fintech, institutional]
    related_skills: [claude-design, popular-web-designs]
---

# HTML Report Design

Design self-contained HTML reports and data documents. The core challenge: matching visual energy to content domain. This skill captures the hard-won lesson that **financial/economic/analytical reports need saturated data colors + strong typography + editorial authority** — not monochrome minimalism, and not playful decoration.

## When To Use

Use this skill when the user asks for:
- Analytical reports (financial, economic, policy, research)
- Data dashboards or monitoring surfaces
- Research briefs or institutional documents
- Any HTML page where data encoding and legibility matter more than marketing persuasion

## The Core Lesson: Domain-Aware Visual Energy

A real correction pattern from practice: the user rejected both "too colorful/playful" AND "too monotone/institutional." The sweet spot is the middle:

**Saturated data colors + strong typography + mature type choices + editorial authority.**

This is NOT a compromise — it's the actual target. Premium fintech dashboards (Bloomberg, Koyfin, trading terminals) use exactly this formula: vivid colors for data encoding, strong sans-serif or editorial type for readability, dark backgrounds for long sessions.

## Design System Template (Financial/Analytical)

This template works for most data-heavy reports. Adapt per assignment.

### Color Palette

```
--bg: #060e1a              /* near-black base */
--bg-surface: #0c1829     /* card backgrounds */
--bg-card: #111e35        /* elevated cards */
--gold: #f5c542           /* primary accent — key stats, primary bars */
--cyan: #22d3ee           /* secondary data, positive signals */
--rose: #fb7185           /* danger, risk, negative signals */
--emerald: #34d399        /* success, confirmation, positive tags */
--violet: #a78bfa         /* quaternary data, special highlights */
--text: #f0f4f8           /* primary text */
--text-secondary: #94a3b8 /* body text */
--text-muted: #64748b     /* labels, metadata */
--border: rgba({AMOUNT},0.07)
```

**Key rule:** Color serves data encoding, not decoration. Every colored element should communicate something:
- Stat strip values: color = category (gold = policy, cyan = market, rose = risk, emerald = positive)
- Bar chart fills: gradient bars in distinct hues let the reader distinguish data series at a glance
- Risk tags: elevated (rose), moderate (gold), watch (cyan) — immediate visual triage
- Callout borders: colored left border signals the callout's nature

### Typography

- **Headlines:** Instrument Serif or DM Serif Display — editorial authority, distinguishes section headers from data
- **Body:** Inter or DM Sans — clean, highly legible at small sizes on dark backgrounds
- **Data/labels:** JetBrains Mono or DM Mono — numbers and metadata
- **Weights:** Use 700-800 for stat values, 600 for card headings, 400-500 for body. Bold hierarchy = scannable.

### Layout Patterns

1. **Hero + Stat Strip** — Title, subtitle, metadata row, then a 4-cell stat strip with the most important metrics. The stat strip is the first thing the reader's eyes land on.
2. **Numbered Sections** — `01`, `02`, `03` in monospace beside serif titles. Clear navigation for long documents.
3. **Card Grids** — 3-column for feature cards, 2-column for doctrine/pillar layouts. Consistent padding (1.25-1.5rem), subtle borders, hover states.
4. **Bar Charts** — Horizontal, minimal gridlines, gradient fills in distinct hues, percentage labels inside bars, footnote below.
5. **Data Tables** — Monospace cell text, uppercase muted headers, color-coded risk tags, subtle row hover.
6. **Callouts** — Colored left border (2-3px), tinted background, bold lead-in label. One per section for the key takeaway.
7. **Implication Cards** — Simple cards with bold heading + body text. No emoji, no icons unless they serve scanning.

### Anti-Patterns to Avoid

- **Monochrome minimalism** — stripping all color from a data report reduces legibility and scanability. The user explicitly rejected this.
- **Pastel/bubbly type** — rounded corners, soft colors, playful fonts undermine institutional credibility. The user explicitly rejected this too.
- **Rainbow decoration** — color without data meaning. Every hue should encode something.
- **Emoji as icons** — inappropriate for institutional/financial content.
- **Thin font weights** — 300-400 for body text on dark backgrounds reduces legibility. Use 500+ for body, 700+ for stats.

## Verification

1. File exists at stated path
2. Open in browser via local HTTP server (file:// is blocked by browser tools — use `python3 -m http.server`)
3. Screenshot the primary viewport
4. Check: Can I read all text clearly? Do data colors encode meaning? Does the hierarchy guide my eye? Does it feel appropriate for the content domain?

## Pitfall: The Overcorrection Trap

When the user says "this looks too playful/institutional/wrong," the instinct is to swing hard in the opposite direction. **Do not overcorrect.** If they say "too colorful," the fix is NOT monochrome — it's mature saturated colors with better type choices. If they say "too monotone," the fix is NOT rainbow — it's purposeful data colors with editorial typography.

The correction pattern "rejected A, then rejected the opposite of A" means the target is the nuanced middle: the sophistication to use strong visual tools with restraint and intention.

## File Delivery

- Single self-contained HTML file with embedded CSS/JS
- Exact on-disk path in final response
- Verification screenshot attached

## References

- `references/digital-books.md` — patterns for book-length documents: page navigation, text size controls, content weaving, {HABIT} readability, masculine aesthetics