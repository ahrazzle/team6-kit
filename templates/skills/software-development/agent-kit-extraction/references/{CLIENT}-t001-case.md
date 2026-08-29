<!-- GENERICIZED: 2×{AMOUNT}, 3×{CLIENT}, 1×{MODEL}, 4×{RELATIONSHIP} | source: skills/software-development/agent-kit-extraction/references/{CLIENT} -->
# Worked case — {CLIENT} T-001 Team6 kit ({CLIENT})

Full extraction-and-sanitization run that validated this skill. Funnel: idea → viability pass (12 criteria + disposition promote/park/kill/refine) → user gate → build.

## Audit numbers (all verified on disk)

- Structural inventory across 8 profiles: **{AMOUNT} shippable / 401 redactable / {AMOUNT} excluded** (memories, logs, sessions, auth, caches, checkpoints).
- Sweep hits: **409 entries** (file×profile) = **330 unique relative paths** (29 paths in >1 profile: finalplan.md ×7, human-evaluation.md ×8, portal-auth ×8, profile.yaml ×6).
- **232** unique paths with ≥1 SHIPPABLE-class hit = semantic gate scope.
- **"113" was a phantom**: line-count of the first report's truncated display (top-8 per class per profile: 6×16+15+2=113). A truncated listing's line count is not an audit figure.

## Manifest distribution (330 rows)

- 99 DROP / 123 TEMPLATE / 108 KEEP-REVIEW.
- Crosstab: 97 REDACTABLE|DROP, 122 SHIPPABLE|TEMPLATE, 108 SHIPPABLE|KEEP-REVIEW, **2 SHIPPABLE|DROP**, **1 REDACTABLE|TEMPLATE** — the two cross-class seams need provenance lines (they're the audit-trail seams).

## The leak story (why derived inventories exist)

- Post-genericization leak check reported 0 (`{RELATIONSHIP}/{RELATIONSHIP}/{CLIENT}`) — but a hyphenated-token sweep found **"{RELATIONSHIP}" ×62 across 29 files**: 5 `author:` frontmatter rows + 56 prose/roster rows.
- Root cause: the substitution rules were derived from the same sweep that missed the token — the handle list only knew names it had already seen. Blind by construction.
- Fix: derive the RELATIONSHIP/MODEL inventories from identity sources (config.yaml + SOUL.md names + aliases, e.g. "{RELATIONSHIP}"), and feed the SAME derived set to the genericizer AND the leak-check list — otherwise the fix validates itself.

## {MODEL} class iteration (3 rounds)

1. Naive rule ate filesystem paths: `~/Library/Application Support/Google/Chrome/Default/Bookmarks` → damaged.
2. Added path-word blacklist (Google, Chrome, Application Support...) — models still stripped, paths preserved.
3. Final: `{MODEL}` → `{MODEL}` exactly in 3 places (TARGET var, pinned-config note, workflow fallback); Chrome bookmarks path intact in 2 files.

## False alarms ruled benign (check the source first)

- `{BK}` ×2 in a Python reference doc — original source has `BK = "<backup-dir>"` and `f"{BK}/..."`: author's own f-string variable, not damage.
- `{N}` ×1 — `Tour v{N} — [what changed]` exists verbatim in the original source (template token).
- Both verdicts stood because the genericized file was diffed against the original profile source.

## List-role collapse

- `PROFILES = ["{RELATIONSHIP}" ×8]` → `PROFILES = ["{PROFILES}"]` — one placeholder, list role preserved, loop still correct. Rule fix, not a spot-audit exception.

## Gate output shapes (fail-closed, exit 1)

- `sweep-gate.py`: regenerates manifest LIVE at build; blocker groups = UNCLASSIFIED SOURCE (no manifest row) / MISSING REVIEW ENTRY (shipping file, no checklist) / UNSIGNED REVIEW (checklist 0/4).
- `review-gate.py`: shipping rows vs review entries vs unsigned; lists each file.
- `generate.py` (the only assembly path): refuses to assemble when preconditions fail.
- Live re-scan caught 6 new rows since the last build — the staleness bug is dead by construction.
- Staleness case: `agent-team-kit-market.md` (created mid-work) had no REVIEW.md entry — snapshot gates miss new files; live re-scan at build time catches them.

## Substitution totals after fix (verified)

`{RELATIONSHIP}` 668, `{CLIENT}` 519, `{AMOUNT}` 52, `{HABIT}` 20, `{MODEL}` 3. Delta vs report was the GENERICIZED header tokens (~2/file) — exclude headers from raw grep counts.

## Licensing landscape (stage-4 scan, 2026-08)

- Hermes platform: **MIT** (github.com/NousResearch/hermes-agent) — permits any downstream license.
- AWS `sample-claude-code-agent-team`: **MIT-0** — closest architecture (markdown agent defs + protocol-enforcing Python hooks); free to adapt.
- Google `agent-starter-pack`: **Apache-2.0** — ADK scaffolding.
- CrewAI Enterprise Marketplace: submission-gated curated templates, "launching soon" — closest competitor, not shipping.
- GPT Store postmortem: "catalog of prompts wearing app costumes" — buyers pay for outcomes, not files → service tier is the revenue.
- Chosen split: Apache-2.0 open core (engine + generic templates) + proprietary vertical packs (parameter files + service). One generator, two products.

## Semantic pass economics

124 diff reads (verify the transformation fired) + 103 short reads + 10% spot audit of instantiated output — instead of 229 full-file reads. Soft-leak checklist per file: relationship specifics / financial figures / client-contract detail / personal habits.
