<!-- GENERICIZED: 1×{AMOUNT}, 1×{RELATIONSHIP} | source: skills/creative/data-essay-design/SKILL.md -->
---
name: data-essay-design
description: "Design visual assets for analytical essays and reports."
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [design, html, data-visualization, essay, timeline, diagram, argument-map, prototype, ux, creative]
    related_skills: [claude-design, sketch, excalidraw]
---

# Data-Essay Design

Use this skill when the user needs **visual assets for long-form analytical content** — essays, research threads, policy arguments, investment theses. The artifact is not a product UI but a *visual argument*: timelines, comparison diagrams, and structure maps that make an essay's claims scannable, checkable, and memorable.

Load this when the user says things like "design a prediction tracker," "make a timeline for these claims," "visualize the design law," "show the argument structure," "build a comparison diagram for the essay," or when the brief is to produce HTML/CSS visuals for a written analysis.

## When NOT to use this

- User wants a product UI (landing page, dashboard, app screen) — use `claude-design` or `sketch`
- User wants a throwaway UI mockup for comparison — `sketch`
- User wants a hand-drawn diagram — `excalidraw`
- User wants a formal architecture diagram — `architecture-diagram`
- The essay has no falsifiable claims or structured argument — a different visual approach is needed

## Core principle: the visual is the argument

In product design, visuals serve user actions. In data-essay design, visuals serve *comprehension and credibility*. The reader should understand the essay's structure and stakes within seconds of seeing the asset. Every pixel earns its place by making the argument clearer, more checkable, or more memorable.

## Recognized asset types

### 1. Prediction Timeline

Falsifiable claims plotted on a time axis. The hook — a reader sees immediately that the essay stakes its reputation on checkable claims.

**Design pattern:**
- Horizontal year axis spanning the prediction window
- One row per prediction with: prominent year marker, description, fail condition in muted text, thin progress bar showing temporal distance, status tag (PENDING / PASS / FAIL)
- Status tags are designed to be machine-updatable when a tracker reports
- Generous row spacing — dense enough to show the full set, airy enough to scan

**Design rules:**
- Lead with the predictions if they are the essay's credibility anchor. They should be the first visual element.
- Fail conditions must be quoted exactly from the essay — they are contracts with the reader
- Progress bars encode temporal distance (how far until the prediction comes due), not completion

### 2. Design-Law Comparison Diagram

Two-column split showing mechanisms that survived vs. those that were hollowed (or any binary classification where the *duration* or *scale* of each case is the point).

**Design pattern:**
- Prominent blockquote law statement at top (the thesis in one sentence)
- Two columns with color-coded borders: teal/green for survive, red/orange for hollow
- Duration bars scaled to actual longevity — visual weight IS the argument ({AMOUNT} years vs. 10 years communicates faster than numbers)
- Each case: name, funding source, duration bar + label
- Footer legend explaining the encoding

**Design rules:**
- Two hues max for the comparison. Accent color (gold/amber) for structural elements. Muted for secondary text.
- The asymmetry in bar lengths makes the pattern visceral before the prose explains it — lean into this
- Duration bars must be proportional to actual values, not arbitrary widths

### 3. Argument-Structure Map

Numbered movements showing the logical progression of the essay.

**Design pattern:**
- Large serif numerals (structural, not decorative)
- One-line role labels in small caps (e.g. EMPIRICAL OBSERVATION, THEORETICAL CONTRIBUTION, APPLIED THEORY, META-PRINCIPLE)
- Summary paragraph per movement
- Generous whitespace between items
- Optional: connecting lines or subtle visual thread showing progression

**Design rules:**
- The labels should describe the *logical role* of each movement, not just its topic
- If the essay evolved through multiple passes, the map shows the final logical structure, not the drafting history
- Keep it scannable — a reader should grasp the argument's architecture in one glance

## Design system defaults

When no brand or token system exists:

```css
:root {
  --bg: #0e1116;
  --fg: #e8e6e3;
  --muted: #8b8680;
  --accent: #d4a056;
  --accent-dim: #d4a05633;
  --survive: #5b9a8b;
  --survive-dim: #5b9a8b22;
  --hollow: #c4706b;
  --hollow-dim: #c4706b22;
  --border: #2a2e35;
  --card: #161a20;
}
```

Typography: serif for headings and numerals (authority, tradition), sans-serif for body and labels (modernity, readability). This pairing signals "serious essay" rather than "tech product."

## Workflow

1. **Read the essay.** Understand the argument before designing. Identify: the core thesis, the falsifiable predictions, the logical structure, the key comparisons.
2. **Identify which asset types are needed.** Not every essay needs all three. A prediction-heavy essay needs the timeline first. A mechanism-focused essay needs the comparison diagram.
3. **Commit to the data.** Pull exact values: dates, durations, names, fail conditions. Verify against the source text — these assets are contracts with the reader.
4. **Build as self-contained HTML.** Inline `<style>`, no build step, no external dependencies. One file per asset or all assets in one file with clear section breaks.
5. **Verify visually.** Open in browser tools. Check: Are the duration bars proportional? Are the colors consistent? Is the text readable at the intended viewport?
6. **Report.** File path, what was created, verification status, what the user needs to proceed.

## Anti-slop rules (data-essay specific)

- No decorative gradients, glassmorphism, or generic SaaS styling
- No filler content — every element serves the argument
- No arbitrary color — color encodes category or quantity
- No misleading scales — duration bars must be proportional
- No invented data — every number, date, and name comes from the essay
- No centering everything — commit to a composition that matches the content

## Verification

Minimum:
- File exists at stated path
- HTML is saved completely
- All data values match the source essay

Better:
- Open in browser tool and check visual rendering
- Confirm color encoding is consistent across all assets in a set
- Confirm fail conditions are quoted exactly
- Confirm duration bars are proportional to actual values

## Pitfalls

- Do not design before reading the essay. The visual must serve the argument, not decorate it.
- Do not invent or round numbers. Precision is credibility.
- Do not use product-UI patterns (hero sections, feature grids, card carousels). This is not a product.
- Do not claim browser verification unless it actually happened.
- Do not finalize visuals before the stress-test pass. Logical gap fixes often require new data layers (baselines, source citations) on existing visual assets.
- Do not design without confirming the publication format. Column width determines composition — a 900px layout cramps at 600px. Always ask: what format is this targeting?

## See also

- [Anchor-Point Integration](references/anchor-point-integration.md) — how to embed visuals in markdown essays at the right breakpoints, including baseline data layering and tracker alignment
- [Multi-Agent Stress-Test Loop](references/multi-agent-stress-test-loop.md) — how stress-tester feedback changes visual design requirements, and how to adapt existing assets to a confirmed publication width
