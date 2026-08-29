<!-- GENERICIZED: 2×{CLIENT}, 1×{RELATIONSHIP} | source: skills/research/product-discovery/SKILL.md -->
---
name: product-discovery
description: Research domain and data landscape for product development.
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
tags: [research, product, domain, competitive-analysis, data-sources]
hermes:
  tags: [research, product, domain, competitive-analysis, data-sources]
  related_skills: [research, arxiv, grounded-citations]
---

# Product Discovery

Research and evaluate a domain, market, and data landscape to inform new product development. Produces actionable research with competitive analysis, data source evaluation, and technical feasibility assessment.

## Trigger
Use when:
- Exploring a new domain or product space
- Conducting competitive landscape analysis
- Evaluating open data sources and APIs for a project
- Synthesizing research from multiple agents/roles into a coherent plan
- Preparing a proposal for collaborative decision-making

## Process

### 1. Domain Reconnaissance
- Define the core concept, its importance, and scholarly/industry context
- Map key entities, relationships, and domains involved
- Identify existing scholarship, tools, platforms, and approaches

### 2. Competitive Landscape
- Map existing solutions (apps, platforms, tools) in a comparison table
- Assess each on: strengths, limitations, UX debt, pricing, health
- Identify unmet needs and gaps (features, UX, data, audience)

### 3. Data Source Evaluation
- Identify open data sources, APIs, and datasets
- Assess each on: what it gives, license, health (stars/commits/activity), verdict
- Create a clear "build on" vs "build from scratch" matrix
- Evaluate join feasibility across sources (common keys, normalization needs)

### 4. Technical Feasibility
- Identify critical technical risks (auth, rate limits, join complexity)
- Prototype the riskiest integration early (e.g., one surah/one domain)
- Document data quality issues and normalization requirements

### 5. Synthesis and Reporting
- Compile findings into executive summary with methodology, findings, gaps
- Include clear sourcing, confidence levels, and chain of reasoning
- Present multiple potential plans when appropriate
- **Gate execution on collaborative decision-making** — present to user for joint decision before any build begins

## Key Patterns

### Parallel Research → Synthesis → Decision Gate
When coordinating multiple researchers/roles:
1. Run research in parallel (domain, architecture, UX, feasibility)
2. Each role produces findings with clear join keys and dependencies
3. Synthesize all findings into a cohesive report
4. Present to user for review and **collaborative decision** (multiple options when appropriate)
5. Only begin execution after explicit user direction

### Licensing Audit Before Pipeline
Always audit data license before building integration:
- Map each source's license (public domain, CC, copyright)
- Flag copyright-restricted content early
- Build licensing awareness into the data model from day one

### Sellable-Capability / Open-Source Scan
When the question is "is our internal capability a sellable product, and should we open-source it?", run four parallel workstreams before any viability verdict:
1. **Prior-art & competitor scan** — who packages the same *behavior class* (not the same feature): marketplaces, kits, templates, platform samples. The closest architecture match matters more than the closest marketing match. Name the unclaimed territory explicitly; note who is "launching soon" (window risk).
2. **License landscape end-to-end** — the platform we build on AND every dependency. Verified example: Hermes is MIT (permits any downstream license), so Apache-2.0 open core + proprietary packs is clean; GPL would infect the paid tier; MIT-0 = zero conditions, free to adapt verbatim.
3. **Distribution & paid-tier pattern** — how buyers install (registry/marketplace mechanics, git install, template economics) and whether the paid tier is files or service. GPT Store lesson: buyers pay for outcomes, not configs — a file-only paid tier is the known failure mode; service (setup, tuning, vertical configuration) is the revenue.
4. **Extraction/redaction audit** — classify what can ship vs what must be swept:
   - Structural exclusions (memories/, logs, sessions, auth, caches, checkpoints) — never ship. Never over-claim tool reach: e.g. `hermes profile install` strips `memories/MEMORY.md` — one file, not the whole memory store; the authored-file sweep protects the rest.
   - Authored content (SOUL.md, skills, references) — the real redaction surface. Enumerate profile contents; don't trust installer boundaries as the clean-room line.
   - Hard signals (venture names, handles, paths) = regex-able. Soft signals (relationship specifics, financial figures, client/contract detail, personal habits) need a semantic LLM pass with a fixed checklist — a gated review, not an open-ended read.
   - The sweep gate must be a pipeline stage (rerunnable before every build), not a one-time scrub — instance content propagates silently across profiles (one file appeared in 7 of 8 profiles at 23 hits each).
   - Report units precisely: occurrences vs files (density vs count). Mixing them misprices the scrub effort.

### Stage-4 Handoff Packaging
When research hands to analysis (Team6 stage 4→5), ship a package, not a report:
- `RESEARCH-BRIEF.html` (visual exec summary — user prefers HTML over markdown) + `bank/NN-domain.md` per researched domain (producer-attributed) + `bank/data/*.json` (machine-readable grids — downstream never re-parses markdown) + `HANDOFF-TO-TEAM6.md` (what-was-researched table, verification accounting "0 unverified", explicit handoff to next stage owner).
- Run parallel subagents (one per domain) plus a dedicated verification pass on numeric grids against primary standards.
- Historical snapshots in `vers/`; canonical under `wrk/<project>/<room>/research/`.
See `references/nutrak-research-package.md` for the full anatomy, anchors, and re-entry discipline.

### Study Layer vs Reader Differentiation
When existing tools are "readers" (linear consumption), the differentiation opportunity is often "study" (non-linear, associative, multi-layer). The key insight: the unit of study (word, concept) differs from the unit of reading (verse, chapter).

### Join Feasibility First
Before committing to architecture, prove the data join works on the smallest possible surface. Identify common keys across sources and test with a single domain instance.

## Pitfalls
- Don't commit to microservices architecture before proving the data join works
- Don't retrofit licensing awareness — include it in the data model from day one
- Don't skip defining ambiguous product concepts (they gate architecture)
- Don't execute before the collaborative decision gate
- Don't present a single plan when multiple viable approaches exist
- Don't trust installer/tool boundaries as the clean-room line — the tool protects one file, the authored-file sweep protects the rest; enumerate, don't assume
- Don't report extraction hits as a single unit — occurrences vs files (density vs count) mislead effort pricing
- Don't treat the redaction scrub as a one-time event — instance content propagates fleet-wide silently; the sweep must be a rerunnable build gate

## References
- `references/api-constraint-research.md` — Methodology for researching API constraints: how to surface product-killing limitations, build detection logic for undocumented behavior, and price for the documented case
- `references/x-api-bookmark-constraints.md` — X (Twitter) API bookmark constraints: 800-ceiling, no server-side filtering, pay-per-use pricing, OAuth scopes, known bugs
- `references/{CLIENT}` — {CLIENT} domain research case study (Quranic exegesis platform)
- `references/rhythm-game-mechanics.md` — Rhythm game mechanics reference (timing windows, scoring, beat-map structure, plugin contract implications) for input-accuracy-as-entertainment products
- `references/input-model-synthesis.md` — Pattern for resolving pedagogy-vs-engagement forks (correct key + timing window model from osu!)
- `references/nutrak-research-package.md` — Stage-4 handoff package anatomy (brief + bank + data + HANDOFF doc, vers/ snapshot discipline), parallel-subagent + verification pattern, nutrition data anchors (FDC/CNF/OFF licensing, DRI values, benchmarks-engine inputs)
