<!-- GENERICIZED: 1×{AMOUNT}, 14×{CLIENT}, 7×{RELATIONSHIP} | source: skills/devops/agent-profile-extraction/references/{CLIENT} -->
# T-001 Session Detail — {CLIENT} Kit Extraction ({CLIENT})

Real-world run of the agent-profile-extraction pipeline, built in the {CLIENT}
ideation hub for the "sellable Team6 kit" idea (T-001). Verdict: PROMOTE,
user-gated, skeleton assembled.

## The reconciliation story (counting units)

Three numbers were in play; two were real, one was an artifact:

| Count | Definition | Status |
|---|---|---|
| 113 | Display-truncation artifact: first report capped hit listing at top-8-per-class-per-profile → 6 profiles × 16 + {RELATIONSHIP} 15 + {RELATIONSHIP} 2 = 113. Never a real audit figure. | RETIRED |
| 409 | Per-profile hit ENTRIES (file in N profiles counts N times). = report's sweep-hits column total (72+50+33+91+2+92+31+38). | VERIFIED |
| 330 | UNIQUE relative paths across all profiles (dedup). 29 paths live in >1 profile (finalplan.md ×7, human-evaluation.md ×8, profile.yaml ×6). | MANIFEST KEY |
| 232 | Unique paths with ≥1 SHIPPABLE-class hit — the semantic REVIEW gate scope. | GATE SCOPE |

Cross-class seams that needed provenance lines: 2 SHIPPABLE|DROP + 1
REDACTABLE|TEMPLATE. Redaction effort clusters: {RELATIONSHIP} densest (236 occurrences),
{RELATIONSHIP} near-clean (2 files).

## Scripts on disk ({CLIENT} workspace)

All in `/Users/{RELATIONSHIP}/{CLIENT}{CLIENT}`:
- `OUTPUTS/extraction-inventory.py` — classifier + sweep + `--review` (REVIEW.md emit)
- `OUTPUTS/build-manifest.py` — hit-file → verdict manifest (DROP/TEMPLATE/KEEP-REVIEW)
- `OUTPUTS/sweep-gate.py` — build gate: regenerate → coverage → verdicts → semantic
- `{CLIENT}` — 4/4 checklist enforcement
- `{CLIENT}` — rule-driven genericizer
- `{CLIENT}` — the generator (manifest → kit, fail-closed)
- `OUTPUTS/T-001-viability-pass.md` — the 13-criteria pass, verdict block

## Rule-evolution story (over-strip fixes)

First rule set over-stripped: `{CLIENT}` → `{CLIENT}` and bare `20\d\d-\d\d-\d\d`
mangled titles ("{CLIENT} — Phase {CLIENT}" → "{CLIENT} — {CLIENT}"). Fixes:
1. Keep context words: "Phase N" → "Phase {CLIENT}" (value only).
2. Date rule `(?:session-)?20\d\d-\d\d-\d\d` keeps "session" context.
3. Post-pass cleanup rule `{CLIENT}-\d+` → `{CLIENT}` for range tails.
4. Handle variants leak: "{RELATIONSHIP}" needed its own rule alongside "{RELATIONSHIP}".

Final run: 124 files genericized, {AMOUNT} substitutions (CLIENT 519, RELATIONSHIP
599, AMOUNT 52, HABIT 20), 4 already-generic, 0 instance tokens in contents
(remaining grep hits were filenames + header provenance only).

## Pipeline shape worth reusing

- Gate regenerates the manifest live (staleness bug dead by construction).
- Unclassified sweep-hit source = build failure; assembly target out of scope.
- Semantic pass = diff review over genericized output, not full re-reads.
- 4/4 soft-leak checklist per file: relationship specifics, financial figures,
  client/contract detail, personal habits.
