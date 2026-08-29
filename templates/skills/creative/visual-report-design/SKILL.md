<!-- GENERICIZED: 3×{AMOUNT}, 1×{RELATIONSHIP} | source: skills/creative/visual-report-design/SKILL.md -->
---
name: visual-report-design
description: "Make reports visual: convert markdown to styled HTML."
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
tags: [report, visualization, html, design, charts]
triggers:
  - format this report as html
  - make this report visual
  - turn this into a presentable report
  - md files suck to read
  - add diagrams and visuals
  - convert markdown report to html
---

# Visual Report Design

Converts text/markdown reports into self-contained, presentable HTML with inline CSS charts, stat boxes, card grids, and data visualization. The user dislikes reading raw markdown — always output reports as styled HTML.

## When to Use

- The user has a markdown or text report that needs to be "presentable" or "visual"
- The user explicitly says "md files suck" or asks for HTML formatting
- A report contains data that benefits from charts, tables, or visual hierarchy
- The user asks to "add diagrams and visuals" to any document

## Design System

The default aesthetic is **dark fintech** — professional, data-dense, and readable.

### Color Palette
| Role | Hex | Use |
|------|-----|-----|
| Background primary | `#061b31` | Page background (deep navy) |
| Background secondary | `#0d253d` | Card surfaces |
| Card surface | `rgba(13,37,61,0.6)` | Content cards with transparency |
| Gold accent | `#fbbf24` | Primary highlights, key numbers, stat values |
| Cyan accent | `#22d3ee` | Secondary data, links, chart bars |
| Rose accent | `#fb7185` | Risk, alerts, negative indicators |
| Emerald accent | `#34d399` | Success, positive, low probability |
| Violet accent | `#a78bfa` | Neutral categories, supplementary |
| Orange accent | `#fb923c` | Warnings, watch items |
| Blue accent | `#60a5fa` | Informational, supplementary |
| Text primary | `#ffffff` | Headings, key text |
| Text secondary | `#94a3b8` | Body text, descriptions |
| Text muted | `#64748d` | Labels, metadata, captions |
| Border | `rgba({AMOUNT},0.08)` | Subtle card borders |

### Typography
- **Primary:** `Inter` (300, 400, 500, 600, 700)
- **Monospace:** `JetBrains Mono` (400, 500, 600) for data values, tables, code
- Load from Google Fonts: `https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap`

### Component Library

#### Stat Boxes
For key metrics at the top of a report. Grid of 3–6 boxes.
- `.value` sized at 1.5rem, weight 700
- `.label` at 0.75rem, uppercase, letter-spacing 0.05em
- Color classes: gold, cyan, rose, emerald, violet

#### Bar Charts
Pure CSS bar charts for comparisons.
- `.bar-label`: 140–160px wide, right-aligned, 0.75rem
- `.bar-track`: flex-1, 24px height, rgba({AMOUNT},0.03) background
- `.bar-fill`: height 100%, 4px radius, color classes match accent palette
- Always include numeric value inside the bar

#### Card Grids
For multi-item sections (findings, implications, drivers).
- Grid: `repeat(auto-fit, minmax(260px, 1fr))`
- Card: bg `var(--bg-card)`, 0.75rem radius, 1.25rem padding
- `.card-dot`: 8px circle, color-coded
- Lists use `→` arrow pseudo-element in gold

#### Data Tables
For categorized data with severity levels.
- Tag classes: `.high` (emerald), `.moderate` (gold), `.low` (violet), `.low-moderate` (cyan), `.notable` (rose)

#### Callout Boxes
For key insights and important notes.
- Gold: `rgba({AMOUNT},36,0.08)` bg, `3px solid #fbbf24` left border
- Blue variant: `.callout-blue` with cyan accents
- Rose variant: `.danger-box` for warnings

## Workflow

1. Analyze the markdown content — identify data points, categories, comparisons, key findings
2. Map content to components: metrics → stat boxes, comparisons → bar charts, multi-item → card grids, categorized → tables
3. Structure: Header → Executive Summary (stats) → Sections (numbered) → Conclusion → Footer
4. Write self-contained HTML — all CSS inline, no external dependencies except Google Fonts
5. Save as `.html` alongside the original `.md`
6. **Formatting QA Gate:** any file flagged "for external distribution" (sales rep, client, event attendee) MUST be converted to branded HTML before the deliverable closes. Raw `.md` sitting in a workspace is not a deliverable — the user will ask why it was never formatted. No deliverable closes without passing this gate.

## Rules

- Always output HTML, never raw markdown, when the user asks for a "presentable" or "visual" report
- Use the dark fintech aesthetic **unless the deliverable carries a client brand** — then extract the client's official palette from their website and use that instead (see design-feedback-iteration: invented palettes get rejected)
- Keep all CSS inline — the file must be self-contained and open in any browser
- Include inline CSS-based charts for any quantitative comparisons
- Stat boxes at the top for the 4–6 most important metrics
- Every section gets a numbered badge for navigation
- Color-code everything: stat values, chart bars, tags, dots — meaning through color
- Responsive: use `repeat(auto-fit, minmax(...))` grids that collapse on mobile
- No emojis when the output is business/client-facing — use text or CSS iconography

## Pitfalls

- Do not use pure black (`#000000`) — always use deep navy (`#061b31`)
- Do not output markdown when HTML was requested — this is the primary user complaint
- Do not make charts without labels — every bar needs a numeric value
- Do not use external image dependencies — everything must be inline CSS/SVG
- Do not use large border-radius — keep it 4–8px for professional feel

## Templates

See `references/template.html` for a complete starter template with all components pre-styled.
