<!-- GENERICIZED: 1×{RELATIONSHIP} | source: skills/creative/interactive-data-simulation/SKILL.md -->
---
name: interactive-data-simulation
description: "Build interactive HTML simulations from source documents."
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [design, html, simulation, data-visualization, interactive, prototype, ux, creative, data-driven]
    related_skills: [claude-design, data-essay-design, sketch]
---

# Interactive Data Simulation

Use this skill when the user provides source documents (PDFs, reports, datasets) and wants an **interactive HTML artifact** that lets them explore scenarios, adjust assumptions, and see outcomes update in real time.

Load this when the user says things like "make an interactive simulation," "build a scenario explorer," "show me what happens if X changes," "project the possible outcomes," or when the deliverable is a self-contained HTML file with sliders/toggles that dynamically update probabilities, charts, or narratives.

## When NOT to use this

- User wants a static visualization (timeline, diagram) — use `data-essay-design`
- User wants a product UI mockup — use `claude-design` or `sketch`
- User wants a formal architecture diagram — `architecture-diagram`
- The data is simple enough for a table — just make a table

## Core principle: the simulation is an argument

Every simulation encodes a mental model of how the world works. The sliders are the assumptions, the probabilities are the projected outcomes, and the scenario narratives are the stories that connect them. The artifact is credible only when the underlying data is accurate and the model is transparent.

## Workflow

### 1. Extract ALL data from source documents
- Read every page of every source document — reviewers WILL catch missed details
- Identify: key metrics, probabilities, structural facts, quotes, dates, vote counts, institutional details
- Note discrepancies between secondary reports and primary sources
- Surface details that reports MISSED, not just what they got right

### 2. Commit to a surface archetype
This is a **Monitor** surface (user is watching state change) with **Configure** elements (user adjusts assumptions). The composition should prioritize:
- Glanceable probability overview at top
- Scenario detail below, progressively disclosed
- Controls persistent and always accessible

### 3. Design the interactive architecture

**Controls:**
- **Sliders** for continuous assumptions (0–100 range, clearly labeled endpoints)
- **Preset buttons** for common configurations (Baseline / Hawkish / Dovish / Crisis)
- Each slider has: label, current value descriptor, descriptive context

**Dynamic elements:**
- **Probability bars** that update in real-time from slider positions
- **Scenario cards** with progressive disclosure (click to expand full detail)
- **Vertical timelines** per scenario (natural reading direction, no horizontal overflow)
- **Market/data impact grids** integrated INTO each scenario
- **Key driver tags** per scenario showing what factors matter most

**State panel:**
- Persistent "current state" box showing the baseline facts from the source
- Orients the user before they start adjusting assumptions

### 4. Probability calculation model

```
p_i = base_i + Σ((slider_j - default_j) × weight_ij)
```

- Each scenario gets a base probability (must sum to 100)
- Each slider has a weight per scenario (how much that assumption affects each outcome)
- Weights range ±0.05 to ±0.35 — no single slider should dominate
- After adjustment: floor at 1% minimum, normalize to 100%

### 5. Build the artifact

- Single self-contained HTML file (inline CSS + JS)
- Dark theme by default (financial/data contexts)
- CSS variables for all tokens
- System fonts or one monospace accent (financial data reads well in mono)
- Responsive but optimized for desktop (primary use case)

**File size management:**
- For files >300 lines: write first chunk via `write_file`, then append via `patch` (mode=replace)
- Never retry the same large write — it will timeout

### 6. Fact-checking review loop

When reviewers correct the simulation against source documents:

**Critical:** Fix ALL instances of an error globally, not just where flagged. Search the entire file for orphaned references.

Common categories of error to watch for:
- **Existing vs proposed vs adopted** — commonly confused. "Existing schedule" ≠ "proposal" ≠ "reform adopted"
- **Vote structures** — which body voted? Who has voting rights? Unanimous vs split?
- **Probability claims** — which meeting/time horizon does a percentage apply to?
- **Structural authority** — who can override whom? (e.g., Board unanimity vs regional dissent)
- **Direction of change** — "easing" from very tight ≠ "easy." "A touch weaker" = ceiling, not floor

### 7. Verification

- [ ] HTML parses cleanly (no unclosed tags) — verify with Python HTMLParser
- [ ] JS braces and parens balanced
- [ ] All interactive elements present in DOM snapshot
- [ ] Slider updates propagate to probability bars AND scenario details
- [ ] No orphaned error phrases after global corrections
- [ ] Reviewer corrections applied to ALL instances
- [ ] `write_file` verified flag returned true

**When the browser is unreachable (dev server on localhost is blocked as a private/internal
address, or no browser tool available):** verify the app's JS logic with a **Node DOM-stub
test harness**. Extract the `<script>` block, stub `document.getElementById` /
`createElement` / `querySelector` / `Option` / `fetch` with minimal objects, then `eval` the
script and drive the render functions directly. This catches runtime errors, unbalanced
tokens, and wrong output without a browser. Build it stepwise:
- `node --check` on the extracted script catches syntax errors first.
- A stub whose `querySelector` returns null breaks any `.querySelector(...).addEventListener`
  call — patch the stub to return minimal objects for the selectors your render code uses.
- Assert on the RENDER OUTPUT (the section HTML built by `innerHTML`), not on deeply nested
  DOM children, which the stub won't structure.
- Remember `Option` is a global constructor your `new Option(...)` calls need.

A reusable harness lives in `references/node-dom-stub-verification.md`.

**Data loading over `fetch()` breaks on `file://`.** If the app fetches JSON data files, it
only runs over HTTP (dev server or GitHub Pages), not by double-clicking the file. Decide at
build time:
- Small data (<~100 KB): embed it as a `const` so the file opens standalone via `file://`.
- Large data (>1 MB): fetch from `data/*.json` over HTTP; show a clear on-page message when
  opened via `file://` telling the user to run `python3 -m http.server 8000`. A `file://`
  load must degrade gracefully, not silently fail.

## Pitfalls

- **Inheriting report errors**: Secondary reports may misread primary sources. Always verify against the original document.
- **Monolithic writes**: Files >300 lines will timeout on `write_file`. Use `patch` for additions.
- **Horizontal overflow**: Timelines crammed horizontally become unreadable. Use vertical layouts.
- **Disconnected data**: Market impacts should be IN each scenario, not in a floating disconnected panel.
- **Missing the narrative**: Every scenario needs a description of what it feels like, not just numbers.
- **Partial corrections**: When fixing an error, search the ENTIRE file. One orphaned phrase undermines credibility.

## Final Response Format

```
Simulation v{N} — [what changed]

[Key design decisions with user benefit]

File: [path]
```
