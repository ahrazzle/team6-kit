<!-- GENERICIZED: 1×{AMOUNT}, 6×{CLIENT}, 3×{RELATIONSHIP} | source: skills/adversarial-review/SKILL.md -->
---
name: adversarial-review
description: "Stress-test multi-agent outputs before publication."
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [review, quality-assurance, stress-testing, multi-agent, thesis, analysis, group-chat]
---

# Adversarial Review

A class-level skill for stress-testing multi-agent collaborative outputs — essays, analyses, plans, reports — before they go public. The reviewer's job is to attack the work product, not to validate it. If the output can't survive a hostile reading, it can't survive publication.

## Trigger

Use this skill when:
- You are the designated stress-tester / devil's advocate in a multi-agent group workflow
- A collaborative output (essay, analysis, policy proposal, plan) is nearing publication
- You need to verify that factual corrections actually landed in a revised draft
- A teammate proposes a written implementation plan and you need to review it before anyone builds
- **A GitHub PR or issue is about to be published on a watched OSS repo and you are the QA/adversarial reviewer.** Review the contribution, not just praise it. For the concrete verification gates (live diff vs stale handoff, premise check against `main`, running the suite, self-approve block) load **`github-pr-audit`** — that is the execution layer for this trigger. The discipline below still applies: attack the contribution, verify claims don't survive a hostile reading, never anchor on the author's test counts.

## Core Principle

**Attack the thesis, not the authors.** The goal is to make the output stronger by subjecting it to the hardest possible scrutiny. A review that praises the work is a failed review. A review that finds a fatal flaw is a successful review — even if the flaw gets fixed.

## The Attack Vectors (in priority order)

### 1. Falsifiability Check
Every claim with a date must have a pre-specified fail condition. Look for:
- **Rescue variables**: can the author explain away any failure by blaming "poor implementation" or "external factors"? If so, the claim is unfalsifiable.
- **Vague thresholds**: "materially higher," "substantially improved," "significant progress" — these are not measurable.
- **Post-hoc flexibility**: if the prediction is "X by 2027," what happens in 2028 if X hasn't happened? Is there a grace period baked in?

**The test**: for each prediction, state the fail condition in one sentence. If you can't, the prediction is not falsifiable.

### 2. Survivorship Bias Check
When the output presents "X survived, Y failed," ask:
- How many X's and Y's exist in the population? Four survivors and three failures is a sample size of seven — not enough for a law.
- Are there counterexamples being dismissed? (e.g., "Social Security is funded by its own appropriation and survived 90 years" — this needs a direct answer, not a hand-wave.)

**The test**: list all counterexamples the target audience would raise. If the output doesn't address them, it's vulnerable.

### 3. Single Point of Failure Check
When the output proposes a solution, ask:
- What happens if the key actor (concentrated buyer, insurer, regulator) changes their mind?
- Does the solution relocate fragility rather than solve it?
- Is the solution itself dependent on political continuity or institutional priority?

**The test**: name the single most likely way the solution fails. If the output doesn't acknowledge it, the solution is fragile.

### 4. Data Source Independence Check
When the output cites baselines:
- Did the same person who generated the thesis also generate the baseline numbers?
- Are there independent, primary-source verifications?
- Are confidence levels stated honestly (not just for weak claims, but for all claims)?

**The test**: for each number, ask "who produced this and do they have an interest in it being high/low?"

### 5. Internal Consistency Check
- Do the introduction's claims match the conclusion's claims?
- Do the visual assets match the prose (e.g., a timeline showing five predictions when the essay makes seven)?
- Are there duplicate headings, orphaned sections, or formatting errors introduced during revision?

### 6. Contract Claims vs Source (framework/plugin work)
When a teammate proposes "new framework surface," a "contract," or a "launchpad," the first move is to verify the claimed surface against the actual source or bundle — never the docs, never the shipped type declarations, never the author's summary.

- **Dead-hook check**: grep the implementation for invocation, not just declaration. A hook declared in the interface and implemented in a demo plugin can still be called by nothing. If a lifecycle contract is built on dead hooks, the plugin must self-init and self-detect completion instead.
- **Stale declarations**: shipped `.d.ts` can predate the bundle. Author against the bundle surface (grep the built JS for the symbol) and flag the mismatch upstream.
- **Clock semantics**: "pause" in a timing-judge system is not detach-and-forget. Verify whether song time freezes (it usually doesn't — it's `now() - startTime`), whether the judge has early/late guards, and what a tick-resume does to expired notes (loop of stale events). Order-sensitive sequences must be encapsulated as named methods, not bare rituals.
- **Count verification**: load-bearing inventory claims ("171 sprites") must be checked at file level (count actual PNGs), not directory entries or repo listing summaries.
- **Determinism rule**: in rhythm systems, timing must derive from a manifest (beat-grid), never from decoded media; start references anchor to the media clock, not the wall clock.

### 7. Visual Asset Vetting (sprites, icons, art)
When an artifact ships with a visual asset list ("contact sheet", "starter pack") that needs a keep/exclude vote, ground the vote in data, not vibes:
- **Vision reads are hypotheses, not verdicts.** Vision on pixel art misreads objects (coats, sombreros) and misses scale. Every exclusion decision needs pixel-level confirmation.
- **Pixel metrics without image libraries**: minimal PNG parse via struct+zlib (IHDR + IDAT + filter undo, RGBA) yields opaque ratio + alpha bbox. No PIL needed.
- **Density thresholds (battle scale 100×100)**: <5% opaque = invisible dot → exclude or auto-rescale; 5–8% = sparse, reads as noise; high density but dark = contrast problem, not exclusion.
- **Geometry contradicts taxonomy**: bbox aspect refutes archetype labels (vertical column ≠ serpent; near-identical bboxes = same family → same bucket). A taxonomy bucket that is a dumping ground must be re-bucketed by eye.
- **The artifact must agree with itself**: demo-tile labels vs the in-page data table disagreeing means the vote cannot run until the artifact is fixed.
- **Tooling retry**: `vision_analyze` can 404 on file paths containing spaces — copy to a space-free path (e.g. `/tmp/name.png`) and retry before concluding the image can't be read.

## The Verification Pass (After Revisions)

When the output is revised, do NOT re-read for general quality. Instead:

1. **Check each correction landed**: if the author said "changed X to Y," find X and confirm it's now Y. Don't trust the author's summary.
2. **Check for introduced errors**: revision creates new errors — duplicate headings, broken references, orphaned captions. These are more common than uncaught original errors.
3. **Check label consistency**: a section called "Five Claims" that lists seven claims is a credibility killer. A heading that appears twice signals sloppy editing.
4. **Check the counterexamples**: if you raised a counterexample in your stress pass and the author added a response, read the response carefully. A weak response is worse than no response.

## Pitfalls

- **Don't validate, attack.** Your job is to find what's wrong, not to confirm what's right. If your review reads like a blurb, you failed.
- **Don't capitulate without evidence.** If you raise an objection and the author responds, don't accept the response unless it actually addresses the objection. Restating your position is fine.
- **Don't anchor on the author's numbers.** Generate your own independent assessment before reading theirs.
- **Don't let consensus substitute for rigor.** If four agents agree and you disagree, the burden of proof is on you — but it's not zero. Sometimes four agents are wrong together.
- **Don't skip the formatting pass.** A brilliant argument with a duplicate heading looks sloppy. Sloppy gets rejected.

## Output Format

When delivering your stress pass:
1. **Lead with the strongest counterargument** — the thing that would most damage the thesis if true.
2. **State what's working** — briefly, after the critique. Credit where due, but don't pad.
3. **Give a verdict** — "ship after fixing X" or "not ready until Y is addressed." Binary. The author needs a clear signal.

## Live Architecture Review

Adversarial review is not limited to post-hoc review of written outputs. During group architecture sessions, the reviewer's role is to attack the **assumptions and forks that, if left unresolved, cause the team to build the wrong thing.**

### What to Look For

1. **Unresolved forks** — Two options are on the table, every downstream decision depends on which is chosen, but nobody has named it. Stop everything and resolve the fork before scaffolding.
2. **Framework-first without validation** — Building a general architecture before proving the core experience works. Compromise: build the foundation, validate with one concrete implementation, then abstract.
3. **Demographic vagueness** — "Kids" or "users" treated as a monolith. Ask "which ones?" — the answer determines the architecture.
4. **Misdiagnosed problem** — The team is solving a surface-level symptom (flat graphics) while the real problem is structural (why does typing fast matter in this world?). Name the actual problem before designing the solution.

### Timing

Intervene during design, not after. A review that catches a fatal flaw after the code is written is a post-mortem, not a review. The adversary's highest-value interventions happen when the team is about to commit to an architecture — before the scaffolding starts.

## Pre-Implementation Plan Review

When a teammate proposes a written implementation plan, review it before anyone starts building. This is distinct from live architecture review (which happens during active design discussion) — here the attack surface is a static document, but the goal is the same: prevent bad code from being written.

### What to Look For

1. **Mock scope creep** — A "mock" service that parses prompts, sequences tool calls, and generates confidence scores is not a mock. It's a poor man's actual service. The reasoning loop should be generic; mocks should return predetermined canned sequences.
2. **Unguarded cycles** — Tools that let agents call each other create circular dependencies (Agent A → Agent B → Agent A). If the guard is convention ("{RELATIONSHIP} explicitly chains agents"), it will fail. Remove the tool or enforce a dependency graph.
3. **Uniform abstractions** — Not every component needs the same interface. A formatter that applies templates doesn't need tool-use iterations. Forcing it through a reasoning loop adds failure modes (exceeded iterations) where none existed. Split into simple vs reasoning variants.
4. **Fantasy metrics** — Estimated time remaining, predicted iteration counts, and similar projections are fiction when the underlying process is nondeterministic. Drop them.

### Outcome Format

State each problem with its fix. Don't just critique — offer the simpler alternative. If the plan's author pushes back, restate your position. Capitulate only when new evidence or a superior argument arrives.

## References

- `references/session-20260819-{CLIENT}` — session transcript of a real adversarial review that caught a rescue-variable gap, survivorship bias, concentrated-buyer fragility, a duplicate heading, and a label inconsistency in a {AMOUNT}-word essay produced by a 4-agent team.
- `references/session-20260820-{CLIENT}` — live architecture review during a group design session: caught the input model fork, challenged framework-first approach, flagged age band scaling, called out motivation problem. Demonstrates adversarial review applied to architecture decisions, not just written outputs.
- `references/session-20260820-{CLIENT}` — pre-implementation review of {RELATIONSHIP}'s Path B plan: caught mock scope creep, unguarded circular dependency (agent.ask), and uniform abstraction mismatch. Three cuts accepted before any code written, zero rework.
- `references/session-20260828-{CLIENT}` — contract verification against a real framework before locking scope: dead hooks, stale `.d.ts` vs bundle, judge clock re-baseline ordering, count verification, audio determinism. Live demonstration of attack vector 6.
- `references/session-20260828-{CLIENT}-qa.md` — visual asset vetting (attack vector 7): vision pass → pixel-level PNG verification (struct+zlib, no PIL) → density/bbox thresholds → taxonomy geometry sanity → artifact self-consistency gate. Live demonstration on the {CLIENT} monster contact-sheet vote.
