<!-- GENERICIZED: 1×{CLIENT}, 1×{RELATIONSHIP} | source: skills/creative/interactive-simulation/SKILL.md -->
---
name: interactive-simulation
description: "Build interactive simulations for scenario analysis."
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
---

# Interactive Simulation

Build self-contained HTML simulations for scenario analysis, policy projection, and market forecasting.

## When to Use

- User asks for "simulation," "scenario explorer," "what-if analysis," or "interactive projection"
- Multiple future paths exist with assignable probabilities
- User needs to explore how assumptions change outcomes
- Dense analytical content needs to become explorable

## Process

1. **Ingest source material** — read PDFs (via vision_analyze), markdown, reports
2. **Extract scenarios** — identify 3-5 distinct future paths with triggers
3. **Build HTML simulation** — single self-contained file with:
   - Assumption sliders that dynamically update probabilities
   - Scenario cards with rate paths and market impacts
   - Timeline showing decision points
   - Detail panels with branching path trees
4. **Preview** — open in preview pane for immediate feedback

## Architecture

### Core Components
- **Header**: Title, key stats badges, current state
- **Controls panel** (left): Sliders with labels, descriptions, presets
- **Content area** (right): Market ticker, timeline, scenario cards, detail panel
- **CSS variables** for theming (dark financial aesthetic)
- **JavaScript** for probability recalculation and view switching

### Probability Model
- Base probabilities for each scenario
- Adjustment factors based on slider positions
- Normalize to 100%
- Update all dependent views (probabilities, timeline, markets)

### Design Principles
- Dark theme with high contrast (suitable for financial data)
- Monospace font for data density
- No external dependencies (self-contained)
- Immediate visual feedback on all interactions
- Mobile-responsive grid layout

## References

- `references/pattern-notes.md` — condensed technique notes from {CLIENT} simulation
- Full example: `simul8/wrk/fomc_scenario_simulation.html`

## Pitfalls

- Don't overload with too many sliders (5-6 max)
- Keep probability model intuitive — linear adjustments with clear directionality
- Always normalize probabilities to 100%
- Test that all interactive elements update consistently
