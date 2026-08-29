<!-- GENERICIZED: 3×{CLIENT}, 2×{RELATIONSHIP} | source: skills/software-development/agent-kit-extraction/SKILL.md -->
---
name: agent-kit-extraction
description: Use when sanitizing live profiles into a generic kit.
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
metadata:
  hermes:
    tags: [extraction, redaction, genericization, leak-gates, agent-profiles, kits]
    related_skills: [web-build-verification, hermes-profile-fleet-operations, agent-kit-distribution]
---

# Agent Kit Extraction & Redaction

## When to Use

Use when: extracting reusable content from live agent profiles or instance-laden files into a shippable kit; sanitizing/redacting authored content before any public release; genericizing instance tokens into placeholders; building leak gates for a release pipeline; or auditing a teammate's extraction/redaction work. Trigger signals: "extract", "sanitize", "redact", "genericize", "make this shippable", "leak check", "kit boundary".

Turn live, instance-laden agent content (profiles, skills, docs) into a shippable generic template kit without leaking identity, ventures, or user data. Validated end-to-end on the {CLIENT} T-001 Team6 kit (2026-08) — see `references/{CLIENT}` for the worked case.

## Pipeline (in order)

1. **Inventory** — path-shape classifier over the extraction source. Classify every artifact: shippable / redactable / excluded (memories, logs, sessions, auth, caches, checkpoints = structurally local, never ship).
2. **Manifest** — one row per UNIQUE relative path (a file present in N profiles = 1 row + occurrence note). Columns: relpath, class, profiles, total_hits, verdict. Verdicts: DROP / TEMPLATE / KEEP-REVIEW. Cross-class seams (SHIPPABLE|DROP, REDACTABLE|TEMPLATE) need one-line provenance in the manifest doc — they are the audit-trail seams.
3. **Genericization** — substitution of instance tokens with `{PLACEHOLDER}`s per locked transformation rules.
4. **Semantic pass** — human/LLM review of genericized output against a fixed soft-leak checklist.
5. **Gates** — fail-closed build precondition: sweep gate + review gate, exit 1 with blocker list. Nothing assembles unless both pass.

## Non-negotiable rules

- **Derive the substitution inventory from identity sources, not sweep hits** (the bootstrap hole). A regex inventory derived from the same sweep that missed a token is blind to it BY CONSTRUCTION (real case: "{RELATIONSHIP}" ×62 across 29 files leaked because it was never in the handle list). Feed SOUL.md names, team handles across all profiles, and config.yaml model configs into the RELATIONSHIP/MODEL class lists at manifest-build time. New profile → identity enters the inventory without needing a leak incident to trigger it.
- **The same derived inventory must feed substitution AND verification.** If the leak-check list is a different (smaller) set than the substitution list, the fix validates itself. One source, both directions.
- **Conservative default:** when a token could be instance or pattern, treat it as instance.
- **Unclassified = do not ship.** Build-time re-scan must fail on any on-disk source file with no manifest row, forcing the manifest builder to assign a verdict before assembly. This also kills snapshot-staleness: the gate re-scans LIVE at build time, never trusts a stale REVIEW.md.
- **Scope the gate to the extraction source, not the assembly target.** The kit's own authored surfaces (LICENSE, kit.yaml, choreography/) have no manifest row by design — scanning the target repo false-fails on its own LICENSE.
- **KEEP-REVIEW is a gate, not a checkbox.** Shipping rows block assembly until the semantic checklist is signed.
- **The generator is the only assembly path.** No hand-copied kits. A kit that cannot be built by the generator from templates + a parameter file does not exist.

## Placeholder class design

- `{CLIENT}` — ventures, orgs, workspace paths, dates, phases
- `{RELATIONSHIP}` — team handles, personal names
- `{AMOUNT}` — financial figures
- `{HABIT}` — user habits, personal facts
- `{MODEL}` — model identifiers. Needs a path-word blacklist: "Google/Chrome" is a filesystem path, not a model — took 3 tightening iterations before the rule stopped eating paths while still stripping real model names.
- List-role placeholders (`{PROFILES}`) for collapsed lists — preserve list semantics instead of emitting 8 identical placeholders.
- No-partial-placeholders rule — substitution must not leave half-placeholders.
- **Code-snippet awareness:** before flagging a stray `{TOKEN}`, diff against the original source — pre-existing template tokens (`{N}` in "Tour v{N}", f-string variables like `{BK}`) are author tokens, not damage.

## Semantic pass (the leak layer regexes can't see)

Fixed soft-leak checklist per file (4 items):
1. relationship specifics (user family, background, personal ties)
2. financial figures (budgets, pricing, costs)
3. client/contract detail (names, terms, obligations)
4. personal habits or identifying routines

Leak classes found in practice: `author:` frontmatter rows (identity in metadata — the genericizer doesn't touch frontmatter), team-roster tables, case-study prose, hardcoded model strings.

Make the review cheap by design: if genericization is rule-based, the review verifies THE TRANSFORMATION FIRED (diff read) instead of re-reading full files. Economics: 124 diff reads + 103 short reads + 10% spot audit of instantiated output, instead of 229 full-file reads.

Verification steps:
- grep the INSTANTIATED output, not just templates (placeholders resolve to real values at instantiation).
- Provenance headers (`GENERICIZED: N×{CLASS} | source: ...`) carry their own placeholder tokens — exclude them from raw grep totals or counts double (the delta between reported and observed substitution counts is the header tokens, ~2 per file).
- For every suspicious token, diff against the original source before ruling damage vs pre-existing.

## Number discipline

- Define the unit before gating on a count: entries (file×profile) vs unique paths vs files vs occurrences vs gate scope. Real case: 409 entries / 330 unique paths / 232 shippable-class paths — and "113" was a truncated-display line-count (top-8 per class per profile), never a real audit figure.
- A truncated listing's line count is not an audit figure.
- Crosstab verdict × class to reconcile sums (e.g. 232 shippable = 122 TEMPLATE + 108 KEEP-REVIEW + 2 SHIPPABLE|DROP).

## Tooling notes

- Use search_files for content search on big trees; large compound terminal greps (multiple clauses + `--include`) can be hard-blocked by the command parser. Split verification into small probes.

## References

- `references/{CLIENT}` — full worked case: audit counts, leak story, {MODEL} iteration history, gate output shapes, licensing landscape.

## Next phase: distribution

Once the kit is sanitized and assembled, the distribution decision (fork vs PR into upstream, per-directory licensing, NOTICE, protecting the paid tier, registry publication) is a separate class — see the `agent-kit-distribution` skill.
