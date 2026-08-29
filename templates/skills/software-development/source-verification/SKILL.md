<!-- GENERICIZED: 6×{CLIENT}, 1×{HABIT}, 9×{RELATIONSHIP} | source: skills/software-development/source-verification/SKILL.md -->
---
name: source-verification
description: "Independently verify claims against source documents using multi-agent cross-checking."
version: 1.0.0
author: {RELATIONSHIP} ({RELATIONSHIP}), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [verification, cross-checking, source-documents, accuracy, multi-agent]
    related_skills: [grounded-citations, systematic-debugging, github-code-review]
---

# Source Verification

## Overview

When multiple agents independently read the same source document, they misread it in **different directions**. The errors cluster around ambiguous qualifiers ("would" vs "is", "existing" vs "proposed", temporal references) and reflect each agent's prior assumptions about what the text *should* say.

A single agent will not catch their own misreading. Two agents may share the same blind spot. Three or more agents with diverse reading styles create a **correction surface**: each agent's error is caught by someone who read differently.

**Core principle:** Always verify report claims against the raw source text, never against other reports.

## When to Use

Use whenever accuracy against a source document matters:

- Legal or regulatory document analysis
- Policy document interpretation
- Financial report verification ({CLIENT} minutes, earnings, SEC filings)
- Technical specification extraction
- Contract clause verification
- Any multi-agent synthesis built from a source document

**Use this ESPECIALLY when:**
- Multiple agents produced reports from the same source
- The source document has high ambiguity (qualifiers, modal verbs, temporal references)
- The stakes of misreading are material
- Reports disagree on specific facts

**Don't use for:**
- Casual fact-checking where a single read suffices
- Tasks where the source document is unambiguous
- Creative work where accuracy to source is not load-bearing

## The Correction Surface

Independent misreadings are not random — they cluster:

| Ambiguity Type | Common Misread | Example |
|---|---|---|
| Modal verbs ("would", "could") | Reading as certainty | "would allow" read as "allows" |
| Temporal references | Wrong time anchoring | "33% for July" read as "33% for September" |
| Existence vs proposal | Status confusion | "existing schedule" vs "proposed schedule" |
| Comparative phrases | Missing the comparison | "more than current practice" ignored |
| Negation scope | Over/under-negating | "not all" read as "none" |
| Conjunction scope | Wrong attachment | "A and B, but not C" read as "A, and B but not C" |

## Procedure

### Step 1: Independent Extraction

Each agent reads the source document **without consulting other agents' reports**. Extract:

- Key figures (percentages, dates, vote counts)
- Qualifiers (modal verbs, hedges, conditionals)
- Structural details (who voted, who didn't, what body decided what)
- Explicit statements vs implied meanings

**Critical:** Note the exact phrasing of ambiguous passages. Do not paraphrase yet.

### Step 2: Cross-Reference Reports

When reports are compared, flag:

- **Direct contradictions** — two agents report different values for the same fact
- **Shared assumptions** — two agents report the same value, but both may be wrong
- **Omissions** — a fact in the source that no report captured
- **Additions** — a claim in a report that cannot be found in the source

### Step 3: Return to Source

For each flagged discrepancy:

1. **Do not vote** — the agent with the most confidence is not necessarily right
2. **Re-read the exact passage** — with attention to the specific ambiguity type
3. **Quote verbatim** — the resolution is in the exact wording, not the paraphrase
4. **Note the qualifier** — what makes this passage ambiguous, and which reading it supports

### Step 4: Correct and Document

- Update the synthesis/product with the verified fact
- Document the correction: what was misread, by whom, and what the source actually says
- Flag the ambiguity type so future readers know why the correction was needed

## Multi-Agent Dynamics

### Shared Blind Spots

When multiple agents misread the same passage in the **same direction**, this is a **shared blind spot** — not consensus. Shared blind spots arise from:

- **Domain expectations** — "{CLIENT} meetings happen 8 times/year" is common knowledge, so agents assume it's true
- **Narrative coherence** — the story "Warsh is reforming the Fed" makes "6-meeting proposal" fit, so agents read it that way
- **Primacy effects** — the first report's reading influences later agents who don't re-read carefully

**Mitigation:** Always have at least one agent who reads "against the grain" — looking for what contradicts the emerging consensus.

### Correction Chains

When Agent A corrects Agent B, Agent A's correction may itself be wrong. This creates a **correction chain**:

1. Agent A misreads
2. Agent B misreads differently
3. Agent C corrects Agent A using Agent B's reading
4. Agent B's reading was also wrong

**Mitigation:** The final arbiter is always the source text, not the most recent correction.

## Pitfalls

- **Confidence as truth** — the most certain agent is not necessarily the most accurate
- **Consensus as correctness** — unanimous agreement does not guarantee accuracy
- **Report-on-report verification** — checking Report A against Report B instead of against the source
- **Ignoring qualifiers** — modal verbs and hedges carry meaning; "would" ≠ "is"
- **Temporal misanchoring** — percentages and probabilities are anchored to specific dates; check the date
- **Authority bias** — deferring to the most {HABIT} agent instead of the source text
- **Correction fatigue** — after multiple rounds of correction, agents stop re-reading the source; force a fresh read

## Real-World Example

From the Simul8 {CLIENT} Minutes analysis ({CLIENT}):

- **6-meeting schedule:** {RELATIONSHIP} and {RELATIONSHIP} read it as "existing"; {RELATIONSHIP} corrected to "proposal" by noting "would allow more information... than under current practice."
- **Market pricing:** {RELATIONSHIP} read ~33% as September pricing; {RELATIONSHIP} corrected that it applied to July.
- **Board vs {CLIENT} vote:** {RELATIONSHIP} surfaced the unanimous Board vote vs 9-3 {CLIENT} split — a structural nuance no report had captured.
- **AI financing:** {RELATIONSHIP} extracted "nonbank investors and regional banks" — a concrete detail absent from all reports.

Each correction required returning to the exact source passage. No correction was resolved by voting or by deferring to the most confident agent.

## Verification

After cross-checking:

- [ ] Every key figure in the synthesis is traceable to a specific source passage
- [ ] Ambiguous qualifiers have been flagged and resolved against the source
- [ ] Contradictions between reports have been documented and resolved
- [ ] No report claim has been accepted without source verification
- [ ] The source text — not any report — is the final authority

## Hermes Agent Integration

### With delegate_task

When dispatching source verification to subagents:

```python
delegate_task(
    goal="Independently extract all key figures from pages 1-4 of the source document. Do NOT consult any existing reports. Note exact phrasing of ambiguous passages.",
    context="""
    Source: <path or URL>
    Task: Extract all numbers, dates, vote counts, and modal qualifiers.
    Output: A list of facts with exact source quotes.
    Do NOT paraphrase. Do NOT compare with other agents' work.
    """,
    toolsets=['file', 'terminal']
)
```

### With grounded-citations

Source verification and grounded citations are complementary:

- **Source verification** ensures the extraction is accurate (the fact is in the source)
- **Grounded citations** ensures the attribution is accurate (the citation points to the right source)

Use source verification first to get the facts right, then grounded citations to document them properly.
