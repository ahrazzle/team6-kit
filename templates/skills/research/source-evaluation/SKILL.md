<!-- GENERICIZED: 1×{HABIT}, 1×{RELATIONSHIP} | source: skills/research/source-evaluation/SKILL.md -->
---
name: source-evaluation
description: "Read a source fully and assess whether claims are supported."
version: 1.1.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Research, Evaluation, Verification, Sources, Methodology, Claims]
    category: research
    related_skills: [grounded-citations, arxiv, knowledge-base-construction]
---

# Source Evaluation

When a high-stakes claim rests on a single source (a working paper, industry report, or dataset), stress-test the source before relying on it. The goal is to determine: **does this source actually say what it's cited for, and at what confidence?**

This skill covers reading a paper systematically, extracting what it actually finds (not what the abstract implies), and delivering a verdict with explicit confidence levels.

## When to Use

- A claim in a deliverable rests on a single source
- The user asks "does this source actually support that?"
- You cited a paper and need to verify the claim matches the findings
- A source is being used to support a prediction or policy recommendation
- Conflicting sources need adjudication

Skip for casual citation, well-established facts, or sources you're only mentioning in passing.

## Procedure

### ① Read the Full Source, Not the Abstract

Abstracts overstate. Introductions frame. Conclusions generalize. Read the actual methodology and results.

- For PDFs: read page by page via `vision_analyze` — extract methodology, sample, timeframe, main findings, limitations, robustness checks
- For web sources: extract with `web_extract` and read the full text
- Never rely on a search snippet or secondary summary for a load-bearing claim

### ② Extract the Core Elements

For any source, answer these questions:

| Element | What to Look For |
|---|---|
| **Methodology** | How was the claim tested? What's the identification strategy? |
| **Sample** | Size, scope, representativeness. Who/what is included and excluded? |
| **Timeframe** | When was the data collected? Does it cover the period the claim refers to? |
| **Main Findings** | What does the source actually find? State figures precisely. |
| **Limitations** | What does the source itself acknowledge as weak or unresolved? |
| **Robustness** | Do the findings hold under alternative specifications? |

### ③ Compare Findings to the Claim

The most common failure mode: a source is cited for a claim it doesn't actually make. Check:

- **Does the source make this claim directly, or is it an extrapolation?**
- **Is the timeframe right?** (A 2023-2024 finding doesn't automatically apply to 2026.)
- **Is the sample representative?** (Large firms in tech ≠ economy-wide.)
- **Are there competing findings the source acknowledges?**

Flag extrapolations explicitly: *"The source finds X; the 15-year rebuild time is my extrapolation based on the mechanism the source describes."*

### ④ Deliver a Verdict

Structure the verdict as:

1. **Confidence level** — High / Moderate / Low / Unknown
2. **What holds** — The findings that are directly supported, stated precisely with timeframe
3. **What's extrapolated** — Claims that go beyond what the source actually finds
4. **What would change the mind** — Conditions under which the verdict would shift

### ⑤ State Figures Precisely

Never round or generalize a source's findings. If the paper says "8% decline after eight quarters," say that — not "roughly 10%" or "significant decline." Precision is how the reader checks your work.

## Pitfalls

- **Citing the abstract instead of the paper.** Abstracts are marketing. Read the methodology.
- **Ignoring timeframe limitations.** A 2023-2024 finding is not a 2026 finding. Flag the gap.
- **Conflating correlation with causation.** If the source says "associated with," don't cite it as "causes."
- **Missing the sample scope.** A finding about large tech firms is not a finding about all firms.
- **Overlooking robustness checks.** If the finding fails under alternative specifications, the confidence drops.
- **Citing secondary summaries.** A news article about a paper is not the paper. Read the source.
- **Delivering a binary verdict.** Most sources are "moderate confidence, holds with caveats." Nuance is not weakness.
- **Trusting vision extraction for numbers.** Vision-based PDF page analysis can miss fine print, footnotes, and numerical details — especially in dense tables. When a figure is load-bearing and discrepancies emerge between readers, pull the full text source (HTML or text extract) to verify. See `references/multi-agent-misreading-correction.md`.
- **Verbatim Arabic quotes vs. extractor normalization.** Web extractors strip tashkeel/diacritics (and normalize hamza variants) when saving page text, so a verbatim-matching quote tool rejects the fully-voweled printed form. When attaching evidence quotes for Arabic sources, copy the sentence from the saved extracted text (the normalized form as it appears on disk), not from the intended printed wording. Also mind minimum-quote-length rules (some tools reject quotes under ~3 words). When quoting classical Islamic sources, attach evidence for the load-bearing citations (the doctrine statement, the key hadith, the modern-standardization claim) — one source per pillar is enough; not every citation needs a quote.

## Example Verdict Structure

```
**Confidence: Moderate**

**What holds:** At AI-adopting firms between 2023 and early 2025, junior employment 
declined roughly 8% relative to {HABIT} employment, driven by slower hiring rather 
than layoffs (Hosseini & Lichtinger, 2025, SSRN 5425555).

**What's extrapolated:** The "15-year rebuild time" claim is my extrapolation based on 
the tacit knowledge transfer mechanism the source describes (Friebel et al., 2026, 
cited in footnote). The source does not quantify this.

**What would change the mind:** If the IBM counter-signal (tripling entry-level hiring 
in 2026 for "reimagined roles") represents a broader restructuring trend rather than 
an outlier, the pipeline may be changing shape rather than closing. The Harvard sample 
ends March 2025 and does not capture this.
```

## Verification

Before delivering a verdict, check:
- [ ] Did I read the full source, not just the abstract?
- [ ] Did I state the timeframe of the data?
- [ ] Did I distinguish findings from extrapolations?
- [ ] Did I state the confidence level explicitly?
- [ ] Did I note what would change the verdict?
