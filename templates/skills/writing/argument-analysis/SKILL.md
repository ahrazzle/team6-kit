<!-- GENERICIZED: 1×{CLIENT}, 1×{RELATIONSHIP} | source: skills/writing/argument-analysis/SKILL.md -->
---
name: argument-analysis
description: Analyze, edit, and reorganize multi-pass argument writing.
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
tags: [writing, editing, analysis, argument, essay, policy]
related_skills: []
triggers:
  - "analyze this essay"
  - "edit this argument"
  - "reorganize this paper"
  - "traced argument"
  - "multi-pass argument"
  - "these essays need editing"
  - "compile these files into one argument"
---

# Argument Analysis and Structural Editing

## When to Use

This skill governs the analysis, structural editing, and reorganization of multi-pass argumentative writing — essays, policy papers, traced arguments, or any work where an argument builds across multiple drafts or passes. Apply when:

- You have 2+ documents that build an argument incrementally
- The argument's logical structure differs from its genealogical structure (how it was written)
- Falsifiable predictions need to be surfaced and highlighted
- Fact-checking and confidence taxonomy need to be integrated
- Multiple assets (essay, visuals, tracker) need to be compiled into a cohesive review document

## Core Technique: Find the Organizing Principle

The most important step is identifying the **organizing principle** — the most general claim that subsumes all other claims. This is usually NOT the first thing written.

1. Read all passes in order (genealogical structure)
2. Identify the core mechanism or law introduced in later passes
3. Map how each pass relates to this principle:
   - Empirical observation / case study
   - Mechanism introduction
   - Applied theory / interventions
   - Meta-principle / design law
4. The organizing principle becomes the thesis; everything else becomes evidence for it

**Example:** In a four-pass argument about AI infrastructure:
- Pass 1: Empirical observation (transformers are the constraint)
- Pass 2: Mechanism (subtractive fragility + appropriability)
- Pass 3: Interventions (filtered by appropriability)
- Pass 4: Meta-principle (design law: resilience survives when funded sideways)

The design law is the organizing principle. The electrification cycle is the empirical case where it operates. Reorganize around the design law, not the chronology of discovery.

## Structural Reorganization

When reorganizing from genealogical to logical structure:

1. **Lead with falsifiable predictions.** They're the hook — what makes this testable, not just another essay. A reader should know in the first 500 words that this makes specific claims with dates.
2. **State the organizing principle early.** Don't make the reader wait for it to emerge.
3. **Preserve intellectual honesty while collapsing re-derivation.** Show the final building, but keep the structural engineering visible. Each "movement" should feel like a natural progression, not a correction of the previous one. Use role labels (empirical observation → theoretical contribution → applied theory → meta-principle) so the reader always knows where they are.
4. **Integrate counter-evidence at full strength.** A thesis that can't survive its own counter-evidence isn't worth publishing. State objections before the reader can raise them. Place the "what the thesis gets wrong" section immediately after the empirical foundation so the skeptical reader watches the argument absorb and survive critique.
5. **Include a source confidence taxonomy.** State plainly which claims are solid, moderate, weak, or contested. Flag the difference between findings and extrapolations. Distinguish between directionally-established and magnitude-established claims.

## Fact-Checking and Confidence Integration

When integrating fact-checking into argumentative work:

1. Identify load-bearing claims — those that, if wrong, collapse the argument
2. Assign confidence levels: solid, moderate, weak, contested
3. **Flag extrapolations explicitly.** When a number (e.g., "15-year rebuild time") is your own extrapolation rather than a source's finding, state that clearly.
4. Distinguish between directionally-established and magnitude-established claims (e.g., "direction corroborated by Microsoft's statements; magnitude not established")
5. **Pre-specify what "implemented as designed" looks like** for policy proposals. Without this, any intervention failure can be attributed to poor implementation rather than mechanism failure — making the thesis unfalsifiable.

## Stress-Testing and Gap Closure

Before finalizing, run a stress pass:

1. **Rescue-variable gap:** Can any failure be attributed to poor implementation rather than mechanism failure? Pre-specify what success looks like and what counts as failure — with dates.
2. **Survivorship bias:** Are there obvious counterexamples to the design law? (E.g., Social Security is funded by dedicated appropriation and has survived 90 years.) Address them directly — explain why they're not the same category of resilience.
3. **Single points of failure:** Do proposed interventions have concentrated vulnerabilities? (E.g., NHS England could delist a subscription; the VA could change procurement criteria.) Acknowledge that "manufacture a concentrated buyer" can relocate fragility, and explain why combining multiple mechanisms mitigates this.

## Compilation for Review

When compiling multiple assets (essay, visuals, tracker) for user review:

1. **Match the final product visually.** Use the same column width, typography, and layout as the intended output format. If the final is a 720px Substack column, build the review document at 720px.
2. **Single continuous scroll.** The user should experience it as one cohesive document, not separate files to open individually.
3. **Embed visuals at anchor points.** Each visual should appear immediately after the prose it illustrates.
4. **Include implementation-fidelity checks.** For each prediction, track whether the mechanism is being tested fairly, not just whether it succeeds.

## Pitfalls

- **Genealogical fidelity trap:** Don't preserve the order of writing if it weakens the argument. The reader wants the final building, not every revision of the blueprint.
- **Prediction burial:** Don't hide falsifiable predictions at the bottom. They lead, or the essay reads as untestable opinion.
- **Weak-source inflation:** Don't present recruiting-industry statistics as established facts. Flag them as directional.
- **Escape-hatch protection:** Don't let policy proposals protect themselves with vague "unless poorly implemented" caveats. Pre-specify what good implementation looks like — one sentence, specific.
- **Appendix counter-evidence:** Don't bury the "what I got wrong" section at the end. Place it where the skeptical reader needs to see it — immediately after the empirical foundation.

## Support Files

- `references/{CLIENT}` — detailed case study of reorganizing a four-pass argument about AI infrastructure and resilience
