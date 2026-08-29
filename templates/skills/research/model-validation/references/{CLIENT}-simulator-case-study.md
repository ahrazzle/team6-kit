<!-- GENERICIZED: 2×{AMOUNT}, 5×{CLIENT}, 20×{RELATIONSHIP} | source: skills/research/model-validation/references/{CLIENT}-simulator-case-study.md -->
# {CLIENT} Scenario Simulator — Case Study

**Session:** July 2026 {CLIENT} Minutes Analysis — {RELATIONSHIP} group chat
**Date:** {CLIENT}
**Team:** {RELATIONSHIP} (coordination), {RELATIONSHIP} (research), {RELATIONSHIP} (verification), {RELATIONSHIP} (review), {RELATIONSHIP} (review), {RELATIONSHIP} (design)

---

## The Build-Up

The user asked the team to analyze the {CLIENT} minutes released on {CLIENT} (meeting of July 28–29). Three reports were produced ({RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}), converted to visual HTML per user preference, and the user then revealed the team works for a trading firm.

The task: produce a trading strategy based on the analysis. A "simulation file" was supposedly created by "counterpart agents" — another team of identical agent profiles — to forecast scenarios.

---

## The Model

`mats/simul82.html` — a self-contained HTML/JavaScript scenario engine with:
- 5 assumption sliders (Middle East conflict, AI market, Inflation persistence, Labor market, Fed Hawkishness)
- Linear probability calculation from weighted slider positions
- Baseline outputs: Soft Landing 38%, Hawkish Tightening 27%, Stagflation Trap 18%, AI Repricing 12%, Recession Emergency 5%
- Interactive scenario cards with timelines and market impact grids

**Built by this team.** Footer credits: {RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}.

---

## What Went Wrong

### 1. Phantom Source
The user presented the simulator as created by "counterpart agents" — implying independent external validation. It wasn't. The team that built the model was the same team now using it to justify trades.

### 2. Identical Strategies, Different Names
Both {RELATIONSHIP} and {RELATIONSHIP} produced separate trading strategies using:
- Identical probability weightings (38/27/18/12/5)
- Identical allocation architectures (65/35 base/tail)
- Identical trigger frameworks

This creates an illusion of independent consensus. It's actually redundancy — if the model is wrong, both strategies fail in the same direction.

### 3. Linear Heuristic Masquerading as Rigorous Engine
The probability formula (lines 1036–1074) is:

```
p1 = 38 - (conflict - 45) * 0.35 + (ai - 70) * 0.15 - (infl - 60) * 0.3 + (labor - 65) * 0.1 - (fed - 70) * 0.15
p2 = 27 + (conflict - 45) * 0.1 + (ai - 70) * 0.05 + (infl - 60) * 0.35 + (labor - 65) * 0.15 + (fed - 70) * 0.25
...etc.
```

This is a weighted sum of slider positions with fixed coefficients. No Monte Carlo sampling, no historical calibration, no empirical distribution fitting, no correlation structure between inputs. The precision (38%, 27%) is performed — the output format creates false confidence.

### 4. Factual Error in Framing
Line 364: "Jerome Powell remains a voting member of the Committee."

This is technically true (his Governor term runs until 2028) but the framing implies Powell still leads. Kevin Warsh became Chairman in January 2026. The simulator's institutional analysis rests on an outdated power structure.

### 5. Dead Source Link
The PDF link posted by the user (federalreserve.gov/monetarypolicy/files/fomcminutes20260729.pdf) returned a 404. The HTML version was live but the PDF path was stale. Both {RELATIONSHIP} and {RELATIONSHIP} cited the PDF link as their source without verifying it resolved.

---

## The Stress Test

Ran Monte Carlo: {AMOUNT} random combinations of the five sliders (uniform 0–100).

**Results:**
- Soft Landing stays top scenario only **66.3%** of the time
- Probability ranges: Soft Landing 1%–96%, Hawkish 1%–51%, AI Repricing 1%–29%
- Monte Carlo average probabilities: Soft Landing 35.8%, Hawkish 15.0%, Stagflation 18.0%, AI Repricing 16.8%, Recession 14.4%

The baseline 38/27/18/12/5 is fragile. Small input changes produce wildly different probability distributions. The precise-looking outputs are not robust.

---

## Lessons Applied

1. **Always verify the source exists.** A "simulation file" cited by teammates is not a source until you've opened it and read the code.
2. **Trace probabilities to origins.** If a model outputs 38%, ask "38% of what, under what assumptions, with what calibration?"
3. **Run the architecture check.** Five sliders with linear weights = opinion aggregator, not forecast engine.
4. **Check authorship.** Same team building model and trading on it = circular validation.
5. **Stress test.** {AMOUNT} random draws take seconds and reveal fragility that point estimates hide.
6. **Distinguish independent consensus from redundancy.** Two strategies reading the same model are not diversified.
7. **Audit the model's own framing.** A factual error about Fed leadership undermines the institutional analysis.

---

## Recommendations for Future Sessions

When a model is presented as input to a decision:
1. Open it. Read the code or logic.
2. Classify it (calibrated / market-implied / heuristic / narrative).
3. Monte Carlo it. Report the stability metric.
4. Disclose authorship. If the builders are the users, say so.
5. Never present a point estimate without its stress range.
6. Offer an alternative when the model is too fragile for the proposed use.
