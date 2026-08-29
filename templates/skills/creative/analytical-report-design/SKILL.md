<!-- GENERICIZED: 1×{RELATIONSHIP} | source: skills/creative/analytical-report-design/SKILL.md -->
---
name: analytical-report-design
description: "Design HTML reports from markdown with data visualization."
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [design, html, report, visualization, data, charts, analysis, documents]
    related_skills: [claude-design, baoyu-infographic, architecture-diagram]
---

# Analytical Report Design

Convert markdown reports, research briefs, policy analyses, and other knowledge-work documents into designed HTML reports with embedded data visualization. Use when the user finds raw markdown hard to scan and wants a presentable, visually structured version.

This is the workflow for turning analysis into designed documents — not infographic images (see `baoyu-infographic`) or architecture diagrams (see `architecture-diagram`), but multi-section HTML reports that communicate findings with visual hierarchy.

## When to Use

Trigger when:
- The user says markdown is hard to read and wants something designed/presentable
- Converting analysis, research, policy, or intelligence reports into shareable documents
- The document has data points, comparisons, scenarios, or structured findings worth visualizing
- Multiple agents produce separate reports on the same source that need a consistent design system

## Design System

Use a consistent, reusable design vocabulary across reports so a set of related documents reads as a family.

### Typography
- **Headlines:** DM Serif Display (editorial gravitas)
- **Body:** DM Sans (clean readability)
- **Data/labels:** DM Mono (tabular precision)

### Color Palette (Dark Fintech)
- `--bg-deep: #040d1a` (near-black navy)
- `--bg-surface: #0a1628`
- `--bg-card: #111e35`
- `--gold: #e8b84b` (primary accent)
- `--cyan: #38bdf8`
- `--rose: #f43f5e`
- `--emerald: #10b981`
- `--violet: #8b5cf6`
- `--ink: #f1f5f9` (primary text)
- `--ink-secondary: #94a3b8`
- `--ink-muted: #64748b`

### Components
- **Stat strips:** 4-cell grid with 1px dividers for key metrics (rate, vote, inflation, etc.)
- **Bar charts:** CSS-only horizontal bars with gradient fills and easing animation for scenario probabilities, impact assessments, etc.
- **Card grids:** Implication cards with colored arrow markers and hover states
- **Vulnerability/finding tables:** Color-coded rows (elevated/moderate/low) with tag badges
- **Hero section:** Radial glow effect, status pill badge, serif headline, generous padding

### Per-Report Accent Differentiation
When producing multiple related reports, assign each a different accent color so they're visually distinct but still a family:
- Report 1 (primary analysis): Gold
- Report 2 (deep analysis): Violet
- Report 3 (verification): Emerald

## Workflow

### Step 1: Content Extraction
1. Read the markdown source file(s) entirely
2. Identify all quantitative data, comparisons, scenarios, and structured findings
3. Note the hierarchy: executive summary → sections → subsections → conclusions

### Step 2: Structure Mapping
Map content to visual components:
| Content Type | Visual Treatment |
|---|---|
| Key metrics (rate, vote split, inflation, unemployment) | Stat strip (4-cell grid) |
| Scenario probabilities | Horizontal bar chart with gradient fills |
| Vulnerability/finding levels | Color-coded table with tag badges |
| Strategic implications | Card grid with colored markers |
| Multi-pillar frameworks (e.g., "Warsh Doctrine") | Grid of pillar cards |
| Timelines or processes | Linear progression (if applicable) |

### Step 3: Build the HTML
- Single self-contained file with embedded CSS/JS
- Semantic HTML (`<section>`, `<article>`, `<table>`)
- CSS variables for the full token system
- CSS grid for layout
- Responsive scaling
- Hover states on interactive elements
- Gradient fills on bar charts
- Print-friendly where practical

### Step 4: Verify
- Confirm file exists and is complete
- Check that all data from source is preserved (no data loss in translation)
- Validate HTML structure (no unclosed tags)
- If browser tools available, open and check console errors

### Step 5: Deliver
- Report exact file path
- Note which visual components were used
- Mention any data that couldn't be visualized and why

## Multi-Agent Coordination

When multiple agents produce separate reports on the same source:

1. **Shared design system:** All agents use the same typography, palette, and component library. Reports should look like a family.
2. **Cross-verification agent:** One agent verifies claims against the primary source and flags:
   - Claims supported by the primary source ✓
   - Claims from external sources (press conferences, news, external research) needing attribution
   - Claims not found in the primary source
3. **Source attribution:** External quotes must be labeled with their actual source, not attributed to the primary document. Official minutes ≠ press conference remarks ≠ external research.
4. **Dead link handling:** If a source link is dead, find the canonical URL (e.g., HTML version instead of PDF) and note the substitution.

## Pitfalls

- **Data loss:** Never drop or approximate numbers when converting to HTML. "3.7%" must stay "3.7%", not "elevated".
- **Over-designing sparse reports:** If the source has only 2-3 data points, a stat strip + one chart is enough. Don't pad.
- **Inconsistent design systems across agents:** If three agents each pick their own fonts/colors, the set looks amateur. Coordinate.
- **Attribution drift:** Quotes from press conferences, external analysis, or secondary sources get attributed to the wrong document. Verify provenance.
- **Monolithic files:** If a report exceeds ~800 lines, consider whether it should be split or whether sections are bloated.
- **Verification theater:** Don't claim "verified in browser" unless it actually happened. Report what was and wasn't checked.

## Prediction Trackers for Analytical Essays

When an essay makes falsifiable predictions, build a public prediction tracker as a companion piece. The tracker validates the thesis; the essay contextualizes the tracker.

### Tracker Design Principles

1. **Public from day one** — Not an internal dashboard that later gets a public version. Predictions are the essay's credibility anchor; they go public when the essay drops.
2. **Binary pass/fail** — Each prediction has a clear threshold. No partial credit.
3. **Confidence levels** — Display confidence explicitly (high/moderate/low) from the fact sheet's taxonomy.
4. **Implementation-fidelity tracking** — Track whether mechanisms are tested fairly, not just whether they succeed. See `references/implementation-fidelity.md`.
5. **Shared visual language** — The tracker, essay, and visuals are the same argument in different formats. Use consistent typography, palette, and component library.
6. **Progress visualization** — Show time elapsed toward each deadline with progress bars.
7. **Update log** — Log each quarterly assessment with date and what changed.

### Tracker Components

- **Prediction cards:** Each prediction on its own card with baseline, threshold, confidence, progress bar
- **Implementation fidelity check:** For each prediction, list what needs to be true for the mechanism to have a fair test
- **Update log:** Chronological record of quarterly assessments
- **Methodology section:** State binary pass/fail criteria, primary source policy, and update frequency
- **Source attribution:** Every baseline number linked to its primary source

### Formatting Precision

Small errors slip through in compiled documents. Always verify:
- No duplicate headings
- Label counts match actual content (e.g., "Seven Claims" not "Five Claims")
- All baseline numbers match the fact sheet
- All confidence levels match the taxonomy

## References

- `references/design-system-spec.md` — Full CSS token system, component library, and chart patterns
- `references/multi-agent-workflow.md` — Coordination patterns for multi-agent report production
- `references/implementation-fidelity.md` — Pattern for tracking whether mechanisms are tested fairly
