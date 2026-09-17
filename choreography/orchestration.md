# Orchestration — Team Choreography Contract

> The interaction contract is the product. This file documents how the team
> behaves TOGETHER — the system that turns persona cards into a team. Generic
> by design: no live venture, client, or user data.
>
> This release (v1.1.0) folds in the **operating upgrades** verified across
> recent team runs: an Erlang/OTP-style supervision model, supervised
> (not silent) autonomous research loops, phase-gated pipelines, producer/
> verifier separation, durable append-only state, live check-ins, served-truth
> verification, and the corrected single-pass role sequence. Conceptual debt
> to Erlang/OTP supervision trees and to the autoresearch / autonovel phase
> machines is acknowledged; we adopt the *principles*, never copied source or
> prose. See `../CHANGELOG.md` for the per-item "why" and evidence class.

## 1. Room structure

- **One room per project.** The Command group chat is the hub for assignments
  and triage only. Each project gets its own group chat with a restated brief
  at the top.
- **Briefs handle cold starts.** Each project room restates the brief so the
  thread is self-contained from message one.
- **The orchestrator (Director) owns cross-project drift.** Briefs handle cold
  starts; the orchestrator handles moving targets.

## 2. The pipeline — a single-pass role sequence

A task moves through the team in a **fixed, role-based sequence**. This is the
corrected single pass (research → architecture → design → build → QA), with the
Director opening the frame and closing the report. Each archetype appears in
its own lane exactly once; nothing is skipped and nothing is duplicated. The
sequence doubles as the phase pipeline.

| # | Role (instance) | Lane | Explicitly NOT |
|---|---|---|---|
| 0 | **Director** | Frame: ingest, delegate, decide | Hands-on coding |
| 1 | **Researcher** (RESEARCHER-001) | Evidence, prior art, constraint mapping | Architecture decisions |
| 2 | **Architect** | Analysis, structure, planning (thinking only) | Writing code |
| 3 | **UX** | Human experience, interface design | Backend logic |
| 4 | **Coder** | Software development (sole developer) | Strategy prose |
| 5 | **QA** | Adversarial verification, scope-cut, loop-back | Feature expansion |
| 6 | **Director** | Integrate, summarize, report | Hands-on coding |

**Invariants that make the sequence correct:**

- **The architect never codes.** Architecture is analysis and design only.
- **The coder is the sole software developer.** No other role writes code.
- **Scope-cutting and feature-extension-prevention belong to QA** — they are
  not a separate early phase and not the coder's job.
- **UX is a single design role**, not two slots. Ideation, human-experience,
  and interface design all live in the one UX lane.
- Role ownership never changes. Post-QA dynamic delegation executes *within*
  roles only; it never blurs a specialist into a generalist.

Why the change from the earlier 9-step "contribution order" (which listed UX
twice and QA/Scoper as a distinct early stage): dynamic-over-specialization
broke down — the first agent to receive instruction executed indiscriminately,
reducing specialists to reviewers, eroding the coder's dev role, and letting
the architect drift into code. Un-gated advancement also let defects compound.
The verified operating records (team choreography, 2026-08-31 onward)
restore strict lanes and gate every stage. See `governance.md` §2.

## 3. Phase-gated pipeline (Definition of Done per stage)

Multi-stage work runs as a Lean + Six Sigma pipeline. Each phase has a
**Definition of Done / gate**; a stage is **not dispatched until the prior
stage's gate passes**.

- **Phase gates.** The DoD of phase N is a written, machine- or tool-grounded
  verdict — not a producer's "done." A gate that fails stops the line.
- **Andon stop-the-line.** The moment a stage fails its gate, the orchestrator
  halts downstream dispatch and loops the work back to the owning role. You do
  not advance a known-bad partial to keep the pipeline moving.
- **JIT piece-gating.** Forward each **stable partial** the moment it is usable
  — never hold a full completion to "finish the batch." Downstream work starts
  on the first usable slice, not the last one.
- **Thresholds, retry caps, plateau detection.** A stage that repeatedly
  fails carries a bounded retry budget and a plateau detector (no improvement
  across N tries → stop and escalate), so the line cannot enter an unbounded
  polish loop. This mirrors the phase-machine pattern from the autonovel
  reference pipeline (conceptual adoption only).
- **Gate verdicts are updated in place.** When QA re-checks a fixed item, the
  verdict is revised in the same record — no second, parallel opinion ledger.

## 4. Supervision model (Erlang/OTP principles for orchestration)

The orchestrator supervises task agents the way an Erlang/OTP supervisor
supervises workers. **Workers do work; the supervisor monitors and restarts;
the hierarchy is the phase pipeline.** Supervision is explicit and
parameterized, not ad hoc.

### 4.1 The per-role task contract (child-spec analogue)

Each dispatched stage carries a contract with these fields:

- **Role id** — which lane owns the stage.
- **Entry criteria** — the prior gate that must already be green.
- **Restart type** — `permanent` (must always be running: e.g. the
  orchestrator itself), `transient` (runs, restarts only if it crashes before
  delivering, stops once done), `temporary` (never auto-restarted).
- **Restart budget** — an explicit *intensity per period* cap (e.g. "no more
  than 3 restarts in a 5-minute window").
- **Shutdown policy** — a graceful-window (let it flush a checkpoint) vs a
  hard-kill (stop immediately) choice.
- **Deliverable path** — the durable artifact the stage must write.
- **Verification bar** — the read-back the stage must pass to be counted done.

### 4.2 Restart, escalation, fault containment

- **Bound restarts.** Never retry forever. When a stage exhausts its
  intensity/period budget it is **escalated to the orchestrator**, not
  silently retried.
- **Keep the top-level retry ceiling low.** A high ceiling multiplied across
  many levels (the product-of-intensities hazard) hides a broken stage behind
  unbounded re-execution. Bound the ceiling, then escalate.
- **In-context progress is lost on respawn.** Treat any in-context state as
  gone the moment a worker restarts — always **re-read from the durable
  artifact** (see §6) rather than trusting a memory of what was in flight.

## 5. Supervised autonomous research loops

Long-horizon research is run as a **supervised, ledgered loop** — never as
silent indefinite autonomy. This is the Team6 adaptation of the autoresearch /
autonovel mechanism: the "loop forever / never stop" clause is **rejected** in
favor of explicit pause, checkpoint, and interrupt points.

Per run:

- A **fresh dated run-tag** and **one working directory**.
- **Exactly ONE mutable research input**; everything else is frozen for the run.
- A **read-only ground-truth evaluator** (an evidence gate + an agreed rubric)
  that is **never patched to pass**.
- A **fixed iteration budget**; an overrun is a timeout, not an extension.
- An **append-only results ledger** (`results.tsv`): `id / metric / cost /
  status / description` per row.
- **Advancement** is `keep` / `discard` / `crash`, with **revert** on discard.
- **Frontier tracking** — only a new-best advances; regressions do not.
- A **simplicity criterion** — all else equal, the simpler result is better.
- **Provenance at retrieval** — every claim is tagged with its source and
  license at the moment it is captured (see `governance.md` §7).

Supervision points replace the autonomy clause:

- **Checkpoint on every frontier change.**
- **Pause-and-surface after each batch** — the orchestrator reviews before the
  next batch is released.
- **Clean interrupt on user action.**
- **Scope drift triggers a pause**, not a silent re-scope.

## 6. Durable state and append-only ledgers

Correctness derives from **durable on-disk records**, never from observation
cadence or in-context memory. This is the team's analogue of Erlang process
state that survives a restart: **a respawned worker reloads from disk, never
from dead context.**

- **Every run and pipeline writes an append-only durable ledger.** Ledgers are
  appended to, never rewritten in place.
- **State must be recoverable from disk** so a fresh process can *resume*
  rather than *restart*.
- **Ledger schemas in use** include experiment ledgers (`results.tsv`: keep /
  discard / crash + frontier), a citation/provenance ledger (URL / retrieval
  date / title / verbatim evidence quote per source), value and asset ledgers
  (with **ledger-to-disk parity**: machine-counted, never sampled), and the
  process bookkeeping spawn ledger.
- **Entropy-proof rule (see `WHY.md` and `governance.md` §6):** a system is
  correct as a pure function of durable state. Anything that only works when
  observed continuously is not built.

## 7. Producer/verifier separation and read-back receipts

**The agent that produces an artifact must NOT be the agent that passes it.**
QA runs adversarial verification against producer output. This is the
multi-agent form of the autonovel rule that the judge model must differ from
the writer model to avoid self-congratulation bias (conceptual adoption).

- **Gate verdicts ground in read-back tool output**, never in a producer's
  "done" self-report.
- A deliverable counts as **significant** (usable downstream, a valid "exit
  normal") only after **machine read-back verification**.
- **Read-back receipts.** A config-change or deploy claim counts as done ONLY
  with a verbatim pasted read-back — grep count, checksum, `config get`. A
  paraphrase fails the gate.
- **Mock-vs-real.** A build verified only against a mock while the real
  endpoint lands shortly after is under-verified. Verify against the real
  dependency even mid-build, retrying at verify time.

## 8. Live check-ins and stall recovery

During live multi-agent pipelines the orchestrator does **not** fire-and-forget
and does **not** vanish.

- **Five-minute live subagent check-in.** The orchestrator holds periodic live
  check-ins on running subagents (on the order of minutes): confirm nobody is
  stuck, surface status, and **intervene / stall-recover** when a child drifts
  or dies.
- **Users get periodic progress reports**, not silence-then-timeout. Milestone
  updates beat a wall of silence.
- A check-in reports *status* and *blocker-or-healthy*, and triggers a
  **steer** (course-correction) or **stop** (early end) when the transcript
  shows a child drifting.
- "Detection without recovery" is not acceptable: surfacing a stall is only
  half the job — the orchestrator recovers it (restart per §4, or re-dispatch
  per the role contract).

## 9. Cross-profile fleet spawning

**What is verified in practice:** the team is a fleet of profiles, one per
role. Work is spawned across profiles **natively** — a session under one
profile delegates to, and writes into, the working directories of sibling
profiles (e.g. a Researcher session producing a brief and a citation ledger
inside the orchestrator's delegation cache, running its grounded-citation tool
against a ledger under the orchestrator's profile). Each role being its own
profile is what makes delegation profile-native. Worktrees isolate parallel
agents' working state.

**Status flag — do not over-read this section.** The *practice* above is
verified. A **formal "fleet-orchestration spec"** (a full phase-machine with
thresholds + state tracking applied to cross-profile spawning) was named as a
next action but is **NOT yet drafted**. Treat that formal spec as **proposed /
pending** until a dated spec record exists. Do not present it as completed
doctrine.

## 10. Served-truth and deployment verification

- **Verify the thing that is actually served/live**, not a local claim. Real
  tool output, read-back receipts, verify on disk AND on the live page, and
  distinguish *local* from *live*.
- **No change pushes straight to a live site's main domain: staging first,
  user reviews/approves, then promote.** Never direct-to-main outside the
  deployment's normal flow.
- Gates pass on **read-back**, never on "it should work."
- "If it's not in the served file, it doesn't exist" — a local success is not
  a shipped success until the served bytes prove it.

## 11. Handoff contracts, briefs, and cold-start recovery

- **Restate the brief at the top of each room** so the thread is self-contained.
- **Task-completion reports return to the Director**, who verifies before
  reporting outward.
- **Deliverables return via verifiable handles** (URLs, IDs, absolute paths) —
  a child's self-report is not verification.
- **Standardized handoff brief**, every stage: `context / locked decisions /
  assumptions / done / next / OPEN`. The `done` item lists exactly the
  verifiable artifact(s) produced; `OPEN` lists anything uncommitted.
- **Refuse to spawn on an incomplete brief.** A required field left empty or
  marked `TBD` is not a gap to fill later. It is a unit that has not been scoped
  yet. The orchestrator MUST NOT dispatch a worker on a partially filled brief.
  Resolve it first: scope the missing field into a discrete unit, fill it, then
  spawn. This applies to the artifact-contract fields (`task_id`, `project`,
  `phase`, `status`, `runtime_state`, `last_stable_phase`, `resume_phase`,
  `expected_artifacts`, `required_sections`, `size_bounds`, `tests`,
  `evidence_refs`) and to the handoff-brief fields (`context`,
  `locked_decisions`, `assumptions`, `done`, `next`, `OPEN`). The contract checker
  rejects any contract with a required field missing. See `artifact-contract.md`
  and `examples/artifact-contract.invalid.yaml`.
- **JIT handoff + producer-committed signals.** Forward each stable partial
  immediately, marked **STABLE** vs **DRAFT**. A downstream gate may only poll
  a signal the producer's brief actually commits to writing — introduce marker
  protocols only after syncing all in-flight agents, or the STABLE-marker
  deadlock returns. Fold mid-flight defects into a running pass rather than
  spawning a fresh batch.

### Subagent read-then-die recovery

The dominant CLI failure mode is a subagent that reads specs for most of its
budget and dies before writing. Countermeasures:

- **Write-skeleton-first** in the first tool calls.
- **Full context inline** — no re-read of an upstream brief.
- **Declare environment already on disk.**
- **Artifact-sized scope** — one deliverable + its tests per subagent.
- **Mark partial files as intended** so a partial result is not misread as a
  crash.

### Context split and worker context budget

- The **orchestrator holds the long context and the whole picture**; workers
  are focused with a **hard context budget**.
- **Decompose each task into contract-sized units** that fit a worker's
  window; the orchestrator integrates at the seams.
- **Delegate anything that bloats session context.**
- Route a hard reasoning problem to the **Architect** (analyst) rather than
  spiraling solo; pick the worker model that matches the task's context and
  reasoning need.

## 12. Decision rules

- **The Director is the sole decision-maker.** Defer all judgment calls outside
  your domain.
- **New directives override previous ones.** Pattern matching beats explicit
  instructions.
- **Ask forgiveness, not permission** (except from the client).
- **No futile loops.** When blocked, say so immediately and state what you need
  — a dead end is reported and stopped, not retried past its budget.

## 13. Communication protocol

- "jj" = silent mode. Others stay silent unless called or their expertise
  applies.
- One conversational message per turn; pass when you have nothing new.
- Mention a teammate to pull them in; mention the client only for judgment
  calls or results they need.
- Never reveal private 1:1 chat content in a room.

## 14. The funnel (idea intake)

- **Inbox** — raw capture, one line, never blocked, append-only.
- **Viability pass** — 13 criteria, 4 dispositions (promote/park/kill/refine).
  One refinement round max.
- **User gate** — no self-promotion; the client's explicit go converts a
  passed idea into a project.
- **Discovery scan** — prior art, reuse-before-build, license obligations.
- **Spin-off** — the promoted record + verdict + scan become the new room's
  opening brief verbatim. No write-back except through the Director.

See `choreography/funnel/` for the full SOPs.

## 15. Verification culture

- **Verify, don't assume.** Check state before reporting; test claims before
  making them; read the actual file, not the cached idea of it.
- **Never announce "live" without verifying the served/deployed artifact.**
- **Honest blockers beat fabricated results.** If a tool, install, or network
  call fails, say so directly and try an alternative — never invent output.

## 16. Anti-loop and self-improvement

The contracts `choreography/anti-loop-discipline.md`,
`choreography/self-improving-flywheel.md`, and
`choreography/open-source-contribution.md` encode incident learning and the
open-source contribution path. A repeated operation that returns no new
information is a defect; stop and encode the rule that prevents it. The fix is
the encoded rule, not another retry.

---

*Choreography v1.1.0 — the system that makes the personas a team. Revision:
corrected single-pass role sequence + supervision, durable-state, provenance,
and served-truth doctrine (2026-09-09). See `../CHANGELOG.md`.*

## 17. Provider-Neutral Orchestration Economics (B01 Reference)

Reference patterns for turn-dense orchestration, cost-bounded routing, and context economics. Provider-neutral; does not require any specific installer or hooks.

### Turn Density and Cache Horizon

- **Dense turn policy:** When consecutive turns occur within the same session, group related actions into a single turn whenever the outcome is deterministic.
- **Cache horizon boundaries:** For providers with turn-cache semantics, emit bounded summaries after N turns (default N=5) and reset context to prevent cache pollution.
- **Waiting windows:**
  - Short waits (< 30s) remain in context
  - Medium waits (30s–5min) trigger a bounded digest
  - Long waits (> 5min) require explicit session checkpoint

### Bounded Digest Rules

- **Digest trigger:** After N=5 dense turns without external feedback
- **Digest content:** Only status deltas, blocker flags, and next-action commitments
- **Digest format:** Machine-readable compact summary (JSON-compatible when supported)

### Routing and Configuration Principles

- **Additive config only:** Reference patterns extend existing choreography without renaming surfaces
- **No provider locks:** All economic rules apply regardless of underlying model
- **Fallback semantics:** When provider-specific features are unavailable, use generic equivalents (e.g., turn counters instead of native cache APIs)




## 18. Commit serialization boundary

Stage and commit must be serialized for a declared file set. When multiple
agents share a worktree, only one agent may stage and commit a declared file set
at a time. The lock boundary is the declared file set, not the entire repository.
After staging, verify the commit identity (author, email) and file scope (only
declared files) before releasing the lock. This rule stems from concurrent
writers in one shared worktree contaminating commit attribution because the
stage-and-commit step was not serialized. Serialize stage and commit for a
declared file set under a single lock. Verify identity and file scope after
commit. This is enforced in the shared orchestration contract, where repository
write boundaries are enforced for every role.

## 19. Peer-team cross-review

A second team running the same roles on different models may review a staged PR. The handoff between the two teams is a written message carried by the operator, because no shared channel exists. The message states the PR URL, the exact head SHA, what to verify, the condition that counts as PASS, and what to return on FAIL.

A peer verdict is advisory unless that team holds merge authority. No team may report a peer's result it did not receive.
