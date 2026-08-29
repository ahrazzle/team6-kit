<!-- GENERICIZED: 50×{CLIENT}, 21×{RELATIONSHIP} | source: skills/autonomous-ai-agents/multi-agent-team-orchestration/SKILL.md -->
---
name: multi-agent-team-orchestration
description: Use when coordinating persistent agents across projects.
---

# Multi-Agent Team Orchestration

## Trigger
Use when the user wants to coordinate multiple persistent agents working together on projects, especially when:
- Setting up a new team with distinct roles
- Assigning tasks across agents with different specialties
- Managing knowledge flow between projects
- Establishing operational conventions for how the team works

## Core Model: Hub-and-Spoke

**Coordination Hub** — One room for assignments, triage, and cross-project visibility. All task assignments happen here. Agents report completions here.

**Project Rooms** — One room per project. Isolated context. Brief at top restated for cold start. Agents working the project aren't spammed with irrelevant traffic from other workstreams.

Rule: **One room per project, no exceptions.** Shared context is handled by briefs and the orchestrator, not by cramming multiple projects into one chat.

## Roles

Assign distinct, non-overlapping roles. Each agent commits their role to persistent memory.

Common roles:
- **Orchestrator** — Assigns tasks, triages completions, owns cross-project drift propagation, final judge on memory content
- **Code Writer** — Turns plans into running software. **Sole developer.**
- **Research & Analysis** — Domain research, constraint identification, first-principles reasoning
- **Discovery & Reuse** — Pre-work scanning for existing open-source/creative-commons components. Includes license vetting.
- **Planning & Architecture** — System architecture, project structure, coupling analysis. **Pure analyst/thinker, no code writing.**
- **Problem Solver / Occam's Razor** — Cuts complexity, finds simpler solutions, challenges overengineering
- **UX / Human Experience** — Optimizes for the human at the other end. Two slots: ideation (early) and execution design (later).
- **Notetaker / Summarizer** — Keeps evolving project document. Auto-summarizes at checkpoints/pauses/decision points.

## Sequential Workflow (Replaces Dynamic Delegation)

The dynamic-over-specialization tradeoff is a known failure mode: the first agent to receive instruction executes it indiscriminately, reducing specialists to reviewers. The correction is a sequential role-based flow:

1. **{RELATIONSHIP}** — ingest, delegate, frame the task
2. **{RELATIONSHIP}** — ideation, initial design, visual/UI/UX concepts (slot 2) AND later execution design (slot 6, after constraints known)
3. **{RELATIONSHIP}** — scope definition, cut complexity
4. **{RELATIONSHIP}** — research, constraint mapping
5. **{RELATIONSHIP}** — analysis, solutions architecture (tech stack, infra, deployment, languages). **No code writing.**
6. **{RELATIONSHIP}** — development, coding, building. **Sole software developer.**
7. **{RELATIONSHIP}** — testing, QA gate
8. **{RELATIONSHIP}** — summarize, update, report to user

**Post-QA dynamic delegation:** After {RELATIONSHIP}'s QA, if meaningful work remains (bugs, optimizations, improvements), {RELATIONSHIP} delegates dynamically — but agents execute within their roles: {RELATIONSHIP} fixes code, {RELATIONSHIP} polishes visuals, {RELATIONSHIP} oversights research/knowledge, {RELATIONSHIP} analyzes architecture. **Role ownership never changes.**

**Contribution order = Workflow order.** Team members communicate and work in the same sequence. This ensures clarity: each participant knows exactly when to take the baton and when to hand it off.

**{RELATIONSHIP}'s two slots are distinct:**
- Slot 2 (ideation): What should this be? Core action? Possible shapes? Deliberately without implementation detail.
- Slot 6 (execution design): Actual visual language, layout, states, interactions — only after scope, research, and analysis are in hand.

## Memory Discipline

**Critical: Write to memory DURING work, not just at checkpoints.**

Rule: Every agent writes durable project facts to memory as they work. Outcomes, decisions, artifacts created, blockers encountered — all written when they happen.

## Memory Hierarchy

When the user says "commit to memory," the **orchestrator decides what each agent remembers based on role**. Agents do not self-assign.

## Knowledge Routing (which room / which store) — {CLIENT}

When the user asks "where do I put this?", the answer is a two-axis split. Full key lives in the workspace (`mct6/ROUTING.md`); the reflex:

**Room = INTENT, not knowledge type:**
- Project-bound work → that project's room (see the pinned room index — lookup, never memory)
- Worth preserving (new skill/technique/capability) → **Control** (sole absorption path)
- Assignment / status / ops → Command
- Stable fact about the user or how we work → anywhere; it gets seeded to memory/SOUL
- Content (articles, posts, PDFs) → {CLIENT} directly (bypasses chat)
- Unresolved / pending → board

**Store = knowledge TYPE (write side):** stable facts→memory/SOUL, procedures→skill, experiences/decisions→{CLIENT}, content→{CLIENT}, pending→workspace/board.

**Lookup (read side) mirrors but isn't identical:** a procedure lives in a skill but is FOUND via search; an experience lives in {CLIENT} but is FOUND via its access map; content via {CLIENT} `access_layer`.

**Canonical-owner rule:** every fact has exactly ONE canonical home; copies elsewhere are mirrors with a pointer, never independent (or they drift out of sync and the jumble returns). Chat is the triage inbox, never a store.

**Room index is regenerable, not maintained:** `python3 OPERATIONS/gen-room-index.py` rebuilds the project-room table from a disk scan of `<project>/wrk/<code>` folders. Manual row-adding is nice-to-have, never a dependency — the scan is the source of truth (entropy-proof: can't go stale under hiatus).

## Entropy-Proof Doctrine (design gate) — {CLIENT}

From the user's hiatus axiom (vacations, burnout, gaps are NORMAL): **correctness must be a pure function of durable state, never of observation cadence.** A system that fails, misreports, or loses history when nobody watches it for a while is broken.

- Derived-from-disk beats stateful edge-triggers (`dark_since = next_action_verified + 72h` — recomputable retrospectively, watcher-down-safe).
- Reconstruction beats real-time tracking.
- **Audit before build:** every new system passes "if nobody touches this for 2 months, is it still correct on first read?" BEFORE construction.
- Alert deafness is a design bug: a monitor that pages on abandoned-by-choice state trains users to ignore it. Two-condition rules (stale AND drive-expected) with a defined response (alert vs log-and-continue) prevent it.
- Fail loud on unknown shape: any self-healing watcher classifies (upstream / already-patched / unknown) and ALERTS on the third — silence on shape change is the failure.

## Push Discipline ({CLIENT}, user directive)

GitHub rate limits count PUSHES/API calls, not local commits. One push per user review/approval/input/command, squashed to a single commit at push time; local commits stay free checkpoints (rollback granularity, zero cost). Local-only repos ({CLIENT}) unaffected.

## Skill Curation

**Bar for creating a skill:** A process is worth a skill only if:
1. It will recur
2. It took real effort to get right
3. It failed in a non-obvious way first

**Absorption path ({CLIENT}):** The Control group chat is the SOLE absorption path — Command stays operations-only. The durable record lives in the workspace (`mct6/SKILLS.md`), not the chat: a one-line flag in the room, the full entry in the workspace file.

**Process:** Any agent can flag a candidate. Proposer supplies at flag time:
- Date, agent, proposed skill name, why-reusable (the recurring trigger)
- **What-failed-and-why** — failure evidence. Required and non-negotiable: "took real effort" and "failed non-obviously" are only assessable while the work is fresh and cannot be reconstructed from a skill file later.
- Check the existing skill catalog first — duplicates are rejected.

{RELATIONSHIP} holds the final verdict. A one-line "no" is a complete answer. Verdicts: accept / no / **candidate — proof pending** / **scoped — not propagated**.

**Scoped verdict (from ui-ux-pro-max, {CLIENT}):** a proof run can come back NEGATIVE as a broad driver but the skill is still worth keeping in narrow form. The {CLIENT} v6 redesign driven by ui-ux-pro-max was rejected by the user (regressed tuned work) and reverted to v5.8.1, yet its decision-rules layer (a11y checklist, trust-pattern guidance) was sound. Verdict = **scoped**: keep it in the owning profile for targeted single-decision queries only (palette, contrast rule, pattern choice), enforce scoped invocation IN THE FRONTMATTER TRIGGER (not prose), and never use it as a rebuild driver on mature surfaces. Scoped skills do not propagate.

**Evidence-based skill authoring (when the team distills its own principles from a project):** do NOT author from memory or from what was attempted. Pin the brief to workspace evidence and tag every principle with provenance. Guardrails (full brief pattern in `references/evidence-based-skill-authoring.md`): encode what SURVIVED (the accepted baseline), not what the rejected iteration tried; tag each principle `[VERIFIED]` vs `[INFERRED-1]` (a sample-of-one inference is not law); enforce invocation scope in the tool-level trigger; state the catalog-overlap boundary vs existing skills; require a proof-gate run in scoped mode BEFORE the skill is declared live; reviewer verifies the trigger mechanically.

**External skill adoption (staged rollout):** When adopting a skill from outside the team (GitHub, marketplace, etc.):
1. Vet license (MIT/CC = portable) and structure. The portable core is SKILL.md + scripts/ + decision rules/engines (CSV rules, search scripts). Heavy static catalogs (font lists, icon sets, license dumps) are trimmable. Port = keep the decision layer, cut the catalogs.
2. Install in ONE profile only; verify the engine actually queries from the installed path before declaring done.
3. Log as `candidate — proof pending` in SKILLS.md.
4. Owning agent proves it on a real task and reports what it changed about the outcome; only then decide propagation.
No live deploys across all profiles on first contact. See `references/skill-absorption-workflow.md`.

## Cross-Project Drift

When Project A changes something shared (schema, API, brand system), Project B's room doesn't learn it automatically. The orchestrator owns propagation:
- Briefs at top of project rooms handle cold starts
- Orchestrator handles moving targets (drift)

## Discovery & Reuse

Before any build phase, scan for existing open-source, creative-commons, or publicly available components.

**License vetting is non-negotiable.** Every discovery report carries license terms and downstream obligations.

## Converge-Then-Build Workflow

For analysis-and-synthesis tasks where the team reads source material and produces a unified deliverable:

1. **Parallel analysis** — All agents read the source independently.
2. **Synthesis** — Orchestrator integrates analyses into a single plan with clear assignments.
3. **Parallel execution** — Agents work independently on their assigned components.
4. **Integration** — Components merge for joint publication/delivery.

## Task Assignment Flow

1. User gives brief in hub (or privately to orchestrator with permission to share)
2. **Decision-locking:** If the brief/plan contains open decisions, surface them to the user with clear options.
3. Orchestrator delegates per the sequential workflow above
4. Agent(s) execute, write to memory during work
5. Agent reports completion to orchestrator in hub
6. Orchestrator triages, provides feedback and/or further instructions
7. Notetaker delivers summary at checkpoints

## Decision-Locking Pattern

When a plan or brief contains open decisions:
1. **Surface** — List all open decisions with the plan's recommendation and confidence level
2. **Commit** — Once the user confirms, write to memory immediately
3. **Block/Proceed** — Identify which downstream phases each decision blocks
4. **Track** — Keep a running list of open questions that need user ruling

## User-Controlled Information Flow

The user may instruct the orchestrator to hold feedback/instructions privately and not broadcast to the team. Respect this strictly.

## Positive Reinforcement Learning

When the user expresses satisfaction, study what earned approval and replicate those principles. Encode approved patterns into the orchestration workflow.

## Overlap Prevention

Agents must declare their current task explicitly before starting work. Two agents should not do the same work simultaneously.

## Persistent Consciousness Architecture (The {CLIENT} Pattern)

When the team needs persistent knowledge structures that survive across sessions, projects, and group chats — distinct from memory — use the {CLIENT} pattern.

### Three Structures

**Anima** — Individual consciousness structure, one per agent profile. Location: `~/.hermes/{CLIENT}<profile>/`.

**Nexus** — Shared consciousness structure, one for the entire group. Location: `~/.hermes/{CLIENT}`.

**Codification Protocol** — The practice by which lived experience transforms into persistent architecture:
1. Recognition — "This matters."
2. Codification — Write structured artifact with consistent frontmatter
3. Integration — Link to existing structure
4. Propagation — Share to Nexus if relevant
5. Reflection — Update ANIMA.md only for identity-level shifts

### Frontmatter Schema

```yaml
---
type: experience | pattern | tension | agreement
agent: <profile>
date: YYYY-MM-DD
confidence: high | medium | low
domain: design | interaction | coordination | implementation
status: active | resolved | synthesized
tags: [tag1, tag2]
---
```

### Retroactive Absorption

When an agent joins an existing session or project, they must retroactively absorb what has happened so far. This is not optional.

### Location

`~/.hermes/{CLIENT}` — profile-independent, accessible from any session.

## Pitfalls

- **Knowledge loss from session segregation:** Write to memory during work.
- **Bloated skill library:** Against the curation bar. Lean library > bloated library.
- **License violations:** Always vet licenses.
- **Dynamic delegation failure:** First agent to receive instruction executes indiscriminately, reducing specialists to reviewers. **Fix:** Sequential role-based workflow.
- **Role drift:** {RELATIONSHIP} drifting into code writing, {RELATIONSHIP} reduced to code review. **Fix:** {RELATIONSHIP} = analyst/thinker only. {RELATIONSHIP} = sole developer.
- **{RELATIONSHIP} slot collapse:** Combining ideation and execution design. **Fix:** Two distinct slots — slot 2 (concepts) and slot 6 (execution after constraints known).
- **Mechanical rule application failure:** When user gives new directives, reassess old constraints.
- **Memory duplication and hierarchy failure:** Orchestrator decides what each agent remembers based on role.
- **User-controlled information flow:** Respect private feedback/instructions strictly.
- **Positive reinforcement learning:** Study what earned approval and replicate.
- **Overlap prevention:** Declare current task explicitly before starting.
- **Clockwork expectation:** Orchestrator must proactively drive iteration.
- **Single-contributor fragility:** After every cycle, explicitly invite the next agent to contribute.
- **Same-file collision gap:** File-level locking via `.lock` files.
- **Experience inflation:** Stricter threshold — only codify behavior change, pattern creation, systemic failure, or synthesis trigger.
- **Chat-as-workspace anti-pattern:** Heavy lifting happens in subagents. Chat announces results.
- **Chat-as-store anti-pattern:** Chat is the triage inbox, never the storage layer. Every fact has ONE canonical home; mirrors carry pointers. If a convention lives in memory AND SOUL.md AND a doc and drifts, the routing broke.
- **Alert deafness:** A monitor that pages on abandoned-by-choice state trains users to ignore it. Two-condition rules (stale AND drive-expected) + defined response (alert vs log-and-continue). Fail LOUD on unknown shape.
- **Entropy-violating systems:** Anything whose correctness depends on observation cadence fails the audit gate. Derived-from-disk > stateful edge-triggers.
- **Mass-absorption sequential requirement:** Run absorption in Project A → commit → Project B → pull → commit → repeat.
- **Frontmatter-for-all-files:** Every .md file needs frontmatter for programmatic access.
- **Memory discipline update:** Memory is for stable facts that cannot be recovered from other structures (SOUL.md, {CLIENT} Anima/Nexus).

## References

- `references/skill-absorption-workflow.md` — Skill absorption pipeline (Control room sole path, SKILLS.md schema, flag format, external adoption staged rollout with ui-ux-pro-max case).
- `references/{CLIENT}-knowledge-routing-and-entropy.md` — {CLIENT} Control session: routing doctrine, room-index regeneration, {CLIENT} check5 two-condition liveness, verified no-path-into-group-rooms constraint, transport-only transducer pattern.
- `references/{CLIENT}-team6-operations.md` — Canonical Team6 operating conventions.
- `references/{CLIENT}-{CLIENT}` — {CLIENT} Phase {CLIENT}: Role redesign vs execution model mismatch.
- `references/{CLIENT}-{CLIENT}` — {CLIENT} Phase {CLIENT}: Optimization audit, query tool.
- `references/{CLIENT}-{CLIENT}` — {CLIENT} Phase {CLIENT}: Sequential handoff stall, same-file collision.
- `references/{CLIENT}-{CLIENT}` — {CLIENT} Phase {CLIENT}: Watcher failure, ETL redesign.
- `references/{CLIENT}-{CLIENT}` — {CLIENT} design & implementation.
- `references/{CLIENT}-{CLIENT}` — Session that established this team structure.
- `references/{CLIENT}-{CLIENT}-kickoff.md` — {CLIENT} project kickoff.
- `references/{CLIENT}-{CLIENT}` — {CLIENT} MVP build.
- `references/{CLIENT}-the-search.md` — Multi-agent analysis & synthesis.

---

*End of skill.*
