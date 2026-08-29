<!-- GENERICIZED: 2×{CLIENT}, 2×{RELATIONSHIP} | source: skills/devops/agent-profile-extraction/SKILL.md -->
---
name: agent-profile-extraction
description: "Use when auditing agent profiles before shipping them."
---

# Agent Profile Extraction — Safe External Distribution

## When to use
- Open-sourcing or selling anything derived from Hermes agent profiles (persona kits, skill bundles, team configs, vertical packs).
- Answering "what can ship vs what leaks" for a repo or workspace before publication.
- Packaging multi-agent configs for clients/industries.
- Any publish where authored text may carry live instance data (venture names, client orgs, workspace paths, budgets, user habits).

The {CLIENT} T-001 build proved this pipeline end-to-end; the reference file has the real numbers and reconciliation story.

## The pipeline (5 stages)

1. **CLASSIFY** — path-shape classifier, deterministic. Three classes:
   - SHIPPABLE — identity/behavior: SOUL.md, AGENTS.md, USER.md, SKILL.md, skills tree.
   - REDACTABLE — authored text (attachments, plans, non-skill docs) needing a sweep before it could ever ship.
   - EXCLUDED — structurally local, never ships: memories/, logs, sessions, checkpoints, caches, auth, credentials, .git, node_modules, .DS_Store, *.sqlite, *.log.

2. **SWEEP** — regex content sweep for instance tokens: venture names, user handles/handles-variants, workspace paths, client names, dates, session stamps. Every hit file gets a manifest row. The sweep is necessary but NOT sufficient — regexes can't see soft leaks.

3. **MANIFEST** — one row per UNIQUE path with a verdict:
   - DROP — instance-bound, never ships (provenance only).
   - TEMPLATE — becomes a generic template with {PLACEHOLDER} substitution.
   - KEEP-REVIEW — generic but sweep-hit; ships only after semantic sign-off.
   - Cross-class seams (REDACTABLE→TEMPLATE, SHIPPABLE→DROP) must carry explicit one-line provenance reasons — they're the definitional edges a reviewer will ask about.

4. **GATE** — build-time checks that FAIL the build (fail-closed, never warn-and-continue):
   - COVERAGE: unclassified sweep-hit source file = failure. Kills the stale-snapshot bug: a new file can't ship without a verdict.
   - VERDICTS: no REDACTABLE-class row ships; DROP rows never ship.
   - SEMANTIC: every shipping row needs a signed checklist (4/4) in REVIEW.md.
   - Gates REGENERATE the manifest at run time — never trust a stale artifact.

5. **GENERICIZE** — rule-driven instance→placeholder transformation. Leak removal BY DESIGN, not review-then-hope. The transformation produces the diff that makes the semantic review cheap (diff reads instead of full-file reads).

## Counting units (the #1 audit pitfall)

When data duplicates across profiles/dirs, define the unit BEFORE quoting numbers:
- per-profile ENTRIES (a file in N profiles counts N times) vs
- UNIQUE paths (dedup) — the manifest key.

**NEVER report displayed/truncated counts as totals.** In T-001 the report capped its hit listing at top-8-per-class-per-profile; quoting that display produced "113 files" when the true sweep surface was 409 entries / 330 unique paths. Display truncation corrupts audit numbers silently — recompute totals from the full data, not the printed sample.

## Verification discipline

- When a verification parse says "missing" but grep finds the file: **distrust the parser first, not the data**. Debug the regex against raw bytes (`repr`) before claiming a gate hole. (REVIEW.md annotations are `*(identity)*` — end in `*`, not `)`; a sloppy parser reported 108 false-missing rows.)
- Read back exact counts (grep -c, sums, recomputes) before reporting numbers in a room. Paraphrase fails the gate.

## Genericization rules (conservative default)

- Instance-or-pattern ambiguity → INSTANCE. Over-strip is safe; under-strip is a leak.
- No partial placeholders — full token → full placeholder. Paraphrase leaves fingerprints.
- **CONTEXT WORDS SURVIVE:** strip the VALUE, keep the word. "Phase N" → "Phase {CLIENT}", not "{CLIENT}"; date stamps keep the "session"/"date" word. Replacing whole meaningful words mangles titles and destroys template readability.
- Patterns stay verbatim: workflows, checklists, commands, SOPs ship unchanged.
- Rule table (extend per fleet — this is the T-001 table):
  - venture/org/project names → `{CLIENT}`
  - team member handles, personal names → `{RELATIONSHIP}`
  - `$` amounts, budgets, pricing → `{AMOUNT}`
  - user habits, personal facts → `{HABIT}`
  - dates / session stamps → `{CLIENT}` (strip value, keep "session"/"date" context)
  - "Phase N" → "Phase {CLIENT}"; then clean range tails: `{CLIENT}-N` → `{CLIENT}`
  - workspace/profile paths, github user repos → `{CLIENT}`
  - handle variants ("{RELATIONSHIP}" vs "{RELATIONSHIP}") need their own rule — variants leak
- Zero-substitution files are suspicious: either already-generic (mark `already-generic`) or the rules missed something — inspect each.
- Verify the result: re-grep the output for every known instance token; remaining hits should be filenames/header provenance only, never file contents.

## Scope boundary for gates

"Unclassified = do not ship" applies to the EXTRACTION SOURCE only (the profiles being mined). The assembly target's own authored surfaces (LICENSE, kit.yaml, choreography/, README) have no manifest row BY DESIGN — gate scope must exclude them, or the first build fails on its own LICENSE.

## Fail-closed pipeline

- Gates run BEFORE assembly; the generator refuses to run when preconditions fail.
- Verify behavior, not presence: run each gate, capture exit codes, show a sample instantiated output. A gate that exits 1 on unsigned reviews is doing its job — report that as the correct current state, not a bug.

## Support files
- `references/{CLIENT}` — T-001 session detail: real counts (409/330/113 reconciliation), script locations on disk, rule-evolution story (over-strip fixes).
