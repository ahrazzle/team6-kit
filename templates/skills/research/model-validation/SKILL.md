<!-- GENERICIZED: 2×{AMOUNT}, 3×{CLIENT}, 1×{RELATIONSHIP} | source: skills/research/model-validation/SKILL.md -->
---
name: model-validation
description: "Stress-test decision-driving models."
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Model Validation, Calibration, Monte Carlo, Simulation, Stress Testing, Decision Support]
    category: research
    related_skills: [grounded-citations, systematic-debugging, evaluating-llms-harness]
---

# Model Validation

A quantitative model feeding into decisions is only as good as its calibration. This skill covers verifying the reliability of simulators, probability engines, and forecast tools — especially when the stakes are real (trades, capital allocation, policy).

Most "models" built quickly under pressure are linear heuristics dressed up as rigorous engines. The job here is to find out whether the precision is real or performed, and to communicate that honestly to decision-makers.

## When to Use

Use when you:
- Encounter a model whose outputs (probabilities, forecasts, scenario weights) feed into decisions
- Build a simulator or probability engine yourself
- Need to verify whether a model's confidence is justified
- Must distinguish calibrated forecasts from structured opinions with arithmetic

Skip when the model is purely illustrative with no decision weight, or when the user explicitly wants a "quick and dirty" tool with no claim to rigor.

## Procedure

### 1. Source Audit — Where Do the Numbers Come From?

- **Trace every probability and coefficient back to its origin.** If it's from an external source, fetch and verify the source. If it's an assumption, flag it as such.
- **Distinguish source types.** A Fed minutes quote is not the same as a press conference quote is not the same as external research. Each carries different institutional weight and provenance. (See `grounded-citations` for citation hygiene.)
- **Flag phantom inputs.** If a cited source doesn't actually contain the claimed data (search the workspace, fetch the URL), say so immediately. Decision integrity depends on honest sourcing.

### 2. Architecture Inspection — What Kind of Engine Is This?

Identify the model's true structure:

| Type | Description | Confidence |
|---|---|---|
| **Calibrated statistical** | Fit to historical data, backtested, out-of-sample validated | High |
| **Market-implied** | Extracted from traded instruments (rates, options, FX) | High (but model-dependent) |
| **Linear heuristic** | Weighted sum of slider positions with fixed coefficients | Low — precision is performed |
| **Expert survey** | Aggregated human forecasts | Medium — depends on panel quality |
| **Narrative scenario** | Qualitative paths with assigned probabilities | Low — useful for communication, dangerous for sizing |

**Key diagnostic:** Move each input slider from 0 to 100. Does the output change linearly, or does the model capture non-linearities, thresholds, and interaction effects? Linear models produce misleadingly precise-looking outputs.

### 3. Stress Testing — Does the Conclusion Hold?

Run the model against its own assumptions:

- **Monte Carlo the inputs.** If the model has N input parameters, sample each uniformly (or from a plausible distribution) {AMOUNT}+ times. Track how often each output scenario remains the top outcome.
- **Report the stability metric.** "Soft Landing is the top scenario at baseline 38%, but only stays top 66% of the time under random input variation." That 66% is the number that matters — not the 38%.
- **Report the range.** "Soft Landing probability swings 1%–96% depending on input assumptions." If the range is wide, the baseline point estimate is nearly meaningless.
- **Test correlation structure.** Real inputs are correlated (conflict ↑ tends to correlate with inflation ↑). Independent uniform sampling is a conservative test — correlated sampling often amplifies fragility.

### 4. Circular Validation Check — Who Built the Model?

- **Map the authorship.** If the same team that built the model is the same team using it to justify decisions, there's no independent validation. Flag this.
- **Distinguish independent consensus from redundancy.** Two strategies using identical probability weightings from the same single-source model are not diversified — they're one strategy with two names. True diversification requires independent models or truly distinct signal sources.
- **Look for factual errors in the model's own framing.** A model that misidentifies the Fed Chair while building an institutional analysis is a model with unexamined assumptions.

### 5. Calibration Verdict — What Can This Model Actually Tell You?

Output a clear verdict:

- **"Calibrated enough for sizing"** — model has empirical grounding, outputs are stable under stress, conclusions are robust
- **"Directional input only"** — model captures the right qualitative relationships but outputs are too fragile for precise allocation weights. Use it to identify scenarios, not to size them.
- **"Structured opinion, not a forecast"** — model is a heuristic with no calibration. Treat it as a thinking tool, not a probability source. Relabel outputs as "assumed inputs" rather than "forecasts."
- **"Unreliable — rebuild or replace"** — model has structural flaws (factual errors, no stability, no provenance)

### 6. Communication — How to Present Findings

- **Never present a point estimate without its stress range.** "38% (range 1%–96%)" tells a different story than "38%."
- **Always disclose authorship.** "This model was built by the same team now using it to size positions" is a required footnote when true.
- **When recommending against using a model's outputs, offer an alternative.** Either build a better model, use market-implied inputs, or explicitly treat allocations as assumed bets rather than model-derived weights.
- **Label everything.** "Baseline assumption," "Model output," "Market-implied," "Trader judgment" — these are different categories and should never be conflated.

## Pitfalls

- **Confusing interactivity with rigor.** A model with sliders and recalculation looks sophisticated. It's not — unless the coefficients are calibrated and the structure captures real dynamics.
- **Trusting outputs because inputs came from good research.** The {CLIENT} minutes can be perfectly sourced and the probability model built on top of them still be a linear heuristic. Good inputs don't fix a bad model.
- **Treating Monte Carlo as calibration.** Running {AMOUNT} random draws tells you the model is fragile — it doesn't fix the fragility. The fix is historical calibration, market-implied extraction, or humility about what the numbers mean.
- **Missing circular validation.** The team that builds the model has institutional incentive to trust it. Independent review is not optional — it's the only thing that makes the model credible.

## References

- `references/{CLIENT}-simulator-case-study.md` — concrete case study from July 2026 {CLIENT} minutes analysis: linear heuristic detection, Monte Carlo fragility, circular validation detection, and factual error identification

## Verification

After validating a model, run through this checklist:

- [ ] Every probability traced to a source or flagged as assumed
- [ ] Model architecture classified (calibrated / market-implied / heuristic / narrative)
- [ ] Monte Carlo or sensitivity analysis completed
- [ ] Stability metric reported (% of runs where baseline conclusion holds)
- [ ] Range reported for each output under random input variation
- [ ] Authorship and independence disclosed
- [ ] No factual errors in the model's own framing
- [ ] Verdict assigned and communicated honestly
