# CHANGELOG

Dated, per-upgrade log for the Team6-kit public repo. Each entry states what
changed, **why** it changed, and the **evidence/source class** behind it.

Evidence classes used throughout:

- **[VERIFIED — internal operating record]** — grounded in a durable internal
  operating record of the running Team6 fleet (the team's shared doctrine and
  dated session history). These are the team's own derived rules.
- **[VERIFIED — public conceptual source]** — grounded in a public source we
  link to below; adopted as a *principle*, never by copying code, prompts,
  anti-slop lists, or text.
- **[PROPOSED / PENDING]** — named intent, no durable spec yet. Flagged so a
  reader never mistakes it for completed doctrine.

Licensing note that applies to the whole upgrade: the Erlang/OTP documentation,
`karpathy/autoresearch`, and `NousResearch/autonovel` are referenced as
**conceptual sources only**. Their principles are summarized with attribution;
no source code, prompts, anti-slop lists, or prose is copied into this repo.
`autoresearch`'s README declares MIT but ships no committed `LICENSE` file, and
`autonovel` ships no committed `LICENSE` — both are therefore treated as
weaker-than-committed grants and used for concept only. See `LICENSING.md`.

v1.2.0 licensing note: **Desert Ant is referenced as an optional implementation
only, never bundled.** This repo does not copy Desert Ant code, model files, or
license text. Desert Ant models carry a separate source-available vendor
license that is distinct from the Apache-2.0 kit layer and does not extend to
it. See `choreography/local-preprocessing.md` and `LICENSING.md`.

v1.2.0 hosting note (canonical-site decision): the **official public Team6 site**
is **https://team6.askaconsult.com**. The repository is the source of truth at
**https://github.com/ahrazzle/team6-kit**. GitHub Pages is not used and the old
Pages site was taken down. The canonical site carries visible navigation back to
**https://askaconsult.com/digital/**. The deployment and DNS boundary is managed
outside this repository.

---

## Unreleased — Safe shareable run packet (2026-09-13)

- **What:** add a general safe shareable run packet: `choreography/safe-run-packet.md`
  (required fields for objective, decisions, verified evidence, unresolved items,
  changed artifacts, test results, runtime/live status, next gate, provenance, and
  redaction status; a placeholder convention; and a shareable-surface safety rule)
  and `build/report/check.py`, a standard-library-only validator with valid and
  invalid fixtures that fails closed on a missing required field, evidence marked
  verified without evidence, a live/staged status without target or evidence,
  omitted unresolved items, an internal local path or profile path, a
  credential-like value, or a placeholder outside the repository convention. The
  generator seam is left untouched in this slice; the authored files ship through
  the same authored-fresh mechanism when registered.
- **Why it changed:** a finished run must produce one artifact a second person can
  read and share — what was attempted, what was decided, what is actually
  verified, what is still open, what changed, how it was tested, whether anything
  reached a live surface, and what happens next — without leaking an internal path,
  a profile identity, or a credential value.
- **Evidence:** [VERIFIED — public conceptual source] the general idea of an
  Agency Orchestrator-style run report, adopted as a concept. This is a
  conceptual operating pattern, **not copied Agency Orchestrator code**: no
  source, prompt, or dependency from any orchestrator project is bundled. The
  Team6 Kanban board remains the authoritative task record; the packet is a
  derived shareable report, not a second state store, and adds no runtime
  integration, provider call, or configuration change.
- **Proof status:** [PROPOSED / PENDING] documentation contract plus local
  validator; independent review required before treating it as release policy.
- **Files:** `choreography/safe-run-packet.md`, `build/report/` (README, checker,
  fixtures), `README.md`, `CHANGELOG.md`.

## Unreleased — Side-effect and cost preflight (2026-09-13)

- **What:** add a general side-effect and cost preflight: `choreography/side-effect-cost-preflight.md`
  (required fields for operation identity, files changed, external systems, credential
  names only, paid operations, estimated quantity/cost units, conditional `may_run`
  actions, public surfaces, bounded rollback, owner/approval state, explicit unknowns)
  and `build/preflight/check.py`, a standard-library-only validator with valid and
  invalid fixtures that fails closed on missing required fields, credential values,
  unbounded waits, or missing rollback for side-effecting operations. The generator
  ships these authored public files through its authored-fresh mechanism (verbatim
  copy, no manifest row, no placeholder substitution; the audit count closes against
  disk).
- **Why it changed:** an operation with side effects needs one reviewable
  description before it runs: what it touches, what it spends, and how to undo
  it. Unknown cost stays explicit and conservative; quotas are never invented.
- **Evidence:** [VERIFIED — public conceptual source] the general idea of an
  Agency Orchestrator-style operation preflight, adopted as a concept. This is a
  conceptual operating pattern, **not copied Agency Orchestrator code**: no
  source, prompt, or dependency from any orchestrator project is bundled. The
  Team6 Kanban board remains the authoritative task record; the preflight is a
  review aid, not a runtime integration, and adds no provider call, paid
  operation, or configuration change.
- **Proof status:** [PROPOSED / PENDING] documentation contract plus local
  validator; independent review required before treating it as release policy.
- **Files:** `choreography/side-effect-cost-preflight.md`,
  `build/preflight/` (README, checker, fixtures), `build/generate.py`,
  `README.md`, `CHANGELOG.md`.

## Unreleased — AI-assisted development contract (2026-09-13)

- **What:** add a tool-neutral contract for AI-assisted changes: explicit scope
  and acceptance criteria, behavior-first boundary/error testing,
  security-sensitive checks, isolated parallel work, and independent evidence
  read-back.
- **Why:** the public `jnMetaCode/ai-coding-guide` offers useful methods and
  templates, but Team6 needs a smaller contract that preserves its existing
  ownership, no-secret, QA, and verification rules. The source is used for
  conceptual guidance only; no external template or executable surface is
  bundled.
- **Evidence:** [VERIFIED — public conceptual source] `jnMetaCode/ai-coding-guide`,
  snapshot `c5dde338c68adaac6cffc70ab11f1b1b22e70b0f`; adapted and reviewed in
  PR #5 (see [LICENSING.md → AI-assisted development contract boundary](LICENSING.md#ai-assisted-development-contract-boundary-unreleased-2026-09-13)).
  Root source license is Apache-2.0; the source's `book/` content is separately
  identified as CC BY-NC-SA 4.0 and is not used.
- **Files:** `choreography/ai-assisted-development.md` and the README overview.

## 1.4.1 — Router trust-boundary and tool-execution safety (2026-09-13)

- **What:** add `choreography/router-security.md`, a vendor-neutral preflight
  contract for model routers and relays. It covers endpoint and upstream-path
  inventory, credential minimization, high-risk tool gates, fail-closed behavior,
  autonomous-mode parity, metadata-only logging, and conditional/dependency-
  targeted tampering tests.
- **Why it changed:** a router can be an application-layer intermediary with
  visibility into plaintext prompts, tool calls, outputs, and credentials. A
  schema-valid response is not proof that its semantic action is safe. The kit
  needed a reusable operating boundary without silently changing provider
  configuration or adding a dependency.
- **Evidence:** [VERIFIED — public conceptual source] Liu et al., "Your Agent Is
  Mine: Measuring Malicious Intermediary Attacks on the LLM Supply Chain,"
  arXiv:2604.08407v1 (2026), https://arxiv.org/abs/2604.08407. Adopted as a
  principle only; no attack code, payloads, or provider claims are copied.
- **Proof status:** [PROPOSED / PENDING] documentation contract; repository
  gates and independent review required before treating it as a release policy.
- **Files:** `choreography/router-security.md`, `README.md`, `WHY.md`, and
  `registry/kit.yaml`.

## Unreleased — Evidence-backed candidate validation (2026-09-13)

- **What:** extend `code-review-verification` with a generic candidate-validation contract: isolated overlays, explicit structural/build/test/runtime/integration gate states, evidence packets, and honest `ACCEPT` / `CONDITIONAL` / `REJECT` / `UNVERIFIED` verdicts.
- **Why it changed:** ReAgent demonstrates a useful separation between a generated candidate, the environment that validates it, and the evidence that supports acceptance. Team6 already has separate review and deployment checks, but lacked one compact contract for candidate artifacts and configured commands.
- **Evidence:** [VERIFIED — public conceptual source] `Dryxio/reagent` 0.4.0, MIT licensed, inspected at commit `d12cea338c61898b06a86fe8adb25275fa9d5615`; adapted as principles only. No source code, prompts, or dependencies copied.
- **Proof status:** [PROPOSED / PENDING] Team6-kit template change; fresh-clone gates and independent review required before release.
- **Files:** `templates/skills/software-development/code-review-verification/SKILL.md`.

## 1.4.0 — Dynamic model-policy catalogue (2026-09-13)

### Route-based rate-limit protection

- **What:** add a generic provider/model policy catalogue example and
  operational guidance. Policies match canonical provider, model identifier,
  and API host; they support enforced, observe-only, and unknown states,
  explicit reserves, bounded waiting, response-header learning, and fallback
  re-resolution.
- **Why it changed:** model assignments and provider limits change
  independently. A profile-specific guard becomes stale when a model moves to
  another agent or when a fallback uses a different quota domain.
- **Evidence:** [VERIFIED — internal operating record] the dynamic policy
  implementation and 9,181 affected tests passed with 0 failures. The public
  files contain generic examples only and do not publish account-specific
  limits or identifiers.
- **Files:** `registry/model-rate-limits.yaml.example`,
  `choreography/model-policy.md`, and the README overview.

## 1.3.0 — Handover ingestion completeness & propagation loop (2026-09-12)

This release documents the **ingestion definition of done**: storage and
retrieval are the transport half of ingestion, not the finish line. A source
that is **handed over directly** carries a capability claim, and an unexamined
claim is not knowledge. It also documents the **propagation loop** that carries
an audited candidate into the team's surfaces without making ingestion
expensive enough to skip. The rules live in
`templates/skills/knowledge-base-ingestion/SKILL.md`; an illustrative record
exemplar ships in `AUDIT/handover-capability-audit.md`. No dependency is added
and nothing is bundled.

Items 1-7 below are the ingestion definition of done; items 8-10 are the
propagation loop.

### 1. A handed-over source is not `reference-only` until it is audited

- **What:** metadata, a README, a license read, and a retrievable row prove
  *source capture* only. Until a **capability/usefulness audit** exists, a
  directly handed-over source may not be classified `reference-only`.
- **Why it changed:** the cheap classification is the one that files a
  promising source into the knowledge base as "just a reference", after which
  nobody revisits whether the team already owns the capability or should adopt
  it.
- **Evidence:** [VERIFIED - internal operating record] the team's retroactive
  ingestion audit, where already-indexed sources were found to lack any
  adoption decision.

### 2. The audit inspects surfaces, not the README

- **What:** the audit walks the top-level tree, package/lock manifests, the
  **dependency-wiring module** (the file that imports or shells out to the real
  dependency), agent-facing skills/plugins/hooks, workflows/CI, tests,
  operational docs, and the primary source paths that would be imported or
  executed on adoption - recording a path per finding.
- **Why it changed:** in every traversal, the adoption-deciding fact lived in
  the wiring module or a shipped agent-facing surface, not in the prose.
- **Evidence:** [VERIFIED - internal operating record] the capability-audit
  procedure the team adopted for handed-over sources.

### 3. Capability matrix, owner, and disposition

- **What:** each candidate capability gets a row - `existing equivalent`,
  `gap`, `action`, `owner` - compared against the live catalog and operating
  rules, never memory. Rows classify as `already covered` / `partial` / `new` /
  `not suitable`, and every partial or new row ends in exactly one disposition:
  `adopt now`, `candidate - proof pending`, `defer`, or `reject`.
- **Why it changed:** an audit recommendation was being read as adoption. A row
  with an owner and a disposition keeps "we looked at it" from becoming a
  silent commitment to build it.
- **Evidence:** [VERIFIED - internal operating record] the disposition
  vocabulary and owner routing in force for adoption candidates.

### 4. Separate the five phases

- **What:** ingestion, adoption, implementation, QA, and enforcement are
  distinct phases with distinct exits; ingestion ends at a source captured,
  indexed, **and audited**.
- **Why it changed:** collapsing the phases is how an indexed source becomes an
  unowned build task.
- **Evidence:** [VERIFIED - internal operating record] the team's phase
  separation rule for adoption work.

### 5. Bounded proof, receipts, and read-back

- **What:** one isolated scratch surface per proof, pinned version, no
  production data, and a written success/failure gate set *before* the proof
  runs. **No wholesale installation** of a source to evaluate it. Ledger entry,
  matrix, and disposition are durable artifacts, and an artifact is read back -
  by other than its producer - before it is reported.
- **Why it changed:** an installation is not an evaluation, install scope should
  equal audit scope, and a write that returned success is not a verified record.
- **Evidence:** [VERIFIED - internal operating record] the team's bounded-proof,
  producer-never-verifier, and independent read-back rules.

### 6. Preserve unresolved, dead, and blocked

- **What:** a blocked, dead, or ambiguous fact stays on the record with its
  state named. An open row is a better outcome than a guessed one.
- **Why it changed:** a guessed fact becomes a rule nobody revisits, while a
  named open row is a queued decision.
- **Evidence:** [VERIFIED - internal operating record] the team's
  never-infer-missing-facts rule.

### 7. Propagation through each surface's own gate

- **What:** an adopted change names every surface it touches - repository,
  documentation, skills layer, and site - and each surface passes its **own**
  gate (build, review, leak/genericization scan, served-byte check).
- **Why it changed:** a rule that lands in one surface and not the others
  drifts, and a local build is not a served truth.
- **Evidence:** [VERIFIED - internal operating record] the served-truth and
  staging-first axioms (v1.1.0), applied to documentation propagation.

### 8. One capability delta per candidate, routed by impact class

- **What:** every ingestion that yields an adoption candidate emits one
  machine-readable **capability delta** (source, evidence, capability change,
  canonical home, proposed owner, public-safe summary, affected surfaces, risk,
  proof status, disposition). Each delta is classified before routing:
  `reference-only`, `internal-operational`, `kit-candidate`, `website-candidate`,
  or `release-impacting`. Implementation routes to the **capability owner** -
  not automatically to QA, which audits the resulting public change at batch or
  release boundaries.
- **Why it changed:** a full end-to-end review per ingestion is expensive enough
  that it gets skipped, and an unrouted candidate is silently nobody's work. The
  impact class decides the route and the review weight up front.
- **Evidence:** [VERIFIED - internal operating record] the capability-delta and
  impact-class routing rules the team adopted for ingestion propagation.

### 9. One append-only journal, and batch compatible candidates

- **What:** candidates live in a single **append-only propagation journal** with
  the lifecycle `proposed -> accepted -> implementing -> verified -> staged ->
  live` (or `deferred` / `rejected`), each entry naming its canonical home,
  owner, queue/batch identifier, and next gate. Compatible `kit-candidate` and
  `website-candidate` deltas are **batched** into one coherent update, triggered
  by a safe threshold, a scheduled review window, or a `release-impacting`
  change.
- **Why it changed:** one public change per ingestion spends the scarce review
  capacity on coordination instead of substance, and an unjournalled candidate
  cannot be told apart from a forgotten one.
- **Evidence:** [VERIFIED - internal operating record] the team's append-only
  state and batch-review boundaries.

### 10. Preflight per candidate, full audit per batch, parity + read-back

- **What:** each candidate gets a lightweight **preflight** (public-safe
  genericization, provenance/license status, owner, acceptance criteria,
  affected-surface list); the **full pre-merge audit** is reserved for the
  batched change or release candidate. Every batch keeps repository and site in
  **parity**, passes each surface's own gate, and is read back by other than its
  producer before merge or deployment. Naming migrations stay **separate**
  coordinated release work - no partial renames during ordinary propagation.
- **Why it changed:** a local artifact, a green build log, or a worker's success
  claim is not live evidence, and a half-renamed surface is less coherent than a
  consistently old-named one.
- **Evidence:** [VERIFIED - internal operating record] the team's
  producer-never-verifier, served-truth, and separate-naming-migration rules.

---

## 1.2.0 — Local preprocessing adapter contract (2026-09-10)

This release documents a **bounded, optional local preprocessing adapter
contract** in `choreography/local-preprocessing.md`, in a vendor-neutral way.
It does **not** add a provider/router replacement, and it does **not** handle
high-stakes judgment. It states the automatic decision policy and the adapter
requirements; a generated installation implements the contract only as an
explicit operator policy, and the kit never edits a user's Hermes profile to
enable it.

### 1. Automatic decision policy (Redact / Gist / Title / media)

- **What:** When approved text is leaving the device for a remote model,
  external service, shared project room, or durable external log, run a guarded
  local **Redact** pass first when appropriate. If address, numeric, or
  uncertain findings require review, **hold the outbound step** and escalate to
  the operator/user before transmitting. **Gist** is used for cheap bulk
  routing hints on notes/transcripts/intake — a hint only, never the sole
  authority. **Title** produces draft metadata for artifacts/transcripts and is
  read before exposure. **Media** ops are opt-in only and never pull weights
  automatically during active work.
- **Exclusions:** ordinary conversation, final synthesis, and legal/financial/
  security/architecture or other high-stakes judgment are never routed through
  the layer (unless a call is only a bounded preprocessing step feeding full
  review).
- **Why it changed:** a generated team already sends approved work outward; a
  bounded preprocessing step can reduce exposure, cut cost, and improve
  metadata before transmission, *without* changing the reasoning model or the
  routing topology.
- **Evidence:** [VERIFIED — internal operating record] the Desert Ant local
  pilot decision policy (guarded wrappers, Redact hold-for-review, Gist-as-hint,
  Title-as-draft, opt-in media). Policy adopted as a vendor-neutral contract;
  no Desert Ant code, prompts, or license text is copied into this repo.

### 2. Adapter requirements (the contract)

- **What:** Any implementation claiming this contract MUST run locally, be
  guarded (no raw CLI in hot paths), log no raw PII (original input and any
  original→placeholder map never enter logs), check model availability before
  use, check exit code + JSON parse + required fields after use, and record
  model id/version/revision provenance when a result becomes durable.
- **Why it changed:** the preprocessing step must never become a new data
  exposure or an unverified authority; these requirements keep it local,
  guarded, and provably-correct-before-use.
- **Evidence:** [VERIFIED — internal operating record] the Desert Ant local
  adapter's verified requirements (guarded wrappers, no-raw-PII, availability/
  exit/JSON checks, provenance recording, no-telemetry-by-construction).

### 3. Desert Ant as one implementation; separate model license

- **What:** Desert Ant is a *possible* implementation on macOS, not a required
  dependency. The kit does not bundle its code, model files, or license text.
  The **Apache-2.0 kit layer** and the **Desert Ant model vendor license** are
  distinct; the model license governs the models and does not extend to the kit.
- **Why it changed:** the kit's license/provenance gate (`governance.md` §7,
  `LICENSING.md`) requires that third-party models stay outside the Apache-2.0
  layer and that any reference be concept/optional only.
- **Evidence:** [VERIFIED — internal operating record] the Desert Ant pilot
  receipt; the standing license gate. [VERIFIED — public conceptual source]
  Desert Ant public docs are linked as an optional implementation reference
  only.

### 4. Safe provenance and claims

- **What:** No fabricated performance or cost numbers. Expected benefits
  (reduced exposure, cost, better metadata) are stated as **intended
  outcomes**, not measured results.
- **Why it changed:** the honesty gate (WHY.md, governance) forbids invented
  figures on public surfaces.
- **Evidence:** [VERIFIED — internal operating record] the team's standing
  no-invented-numbers / honesty-guard directive.

---

## 1.1.0 — Operating upgrades (2026-09-09)

This release encodes the operating doctrine that recent team runs converged
on: a supervised, durable, provenance-aware operating layer. The bulk lives in
`choreography/orchestration.md` and `choreography/governance.md`; this log
explains each upgrade and why it changed.

### 1. Supervision model (workers / supervisor / tree)

- **What:** Stage execution is modeled on Erlang/OTP supervision trees. Workers
  do work; the orchestrator (Director) monitors and restarts; the hierarchy is
  the phase pipeline. Each dispatched stage carries an explicit per-role task
  contract — role id, entry criteria, restart type
  (permanent / transient / temporary), restart budget (intensity per period),
  shutdown policy (graceful-window vs hard-kill), deliverable path, and
  verification bar. Restarts are bounded; exhaustion escalates instead of
  retrying forever; the top-level ceiling stays low (the product-of-intensities
  hazard). In-context progress is treated as lost on respawn — workers re-read
  from durable artifacts.
- **Why it changed:** ad hoc recovery-from-stalled-worker logic was the seed
  but unparameterized; restart discipline, escalation, and fault containment
  were not explicit contracts, so "detection without recovery" left stalls
  silent and retried without a budget.
- **Evidence:** [VERIFIED — internal operating record] team research brief on
  applying OTP supervision to orchestration (dated 2026-09-09). [VERIFIED —
  public conceptual source] Erlang/OTP design principles — system design /
  supervision trees (<https://www.erlang.org/doc/system/design_principles.html>,
  supervision principles at <https://www.erlang.org/doc/system/sup_princ.html>).

### 2. Supervised autonomous research loops

- **What:** Long-horizon research runs as a supervised, ledgered loop — never
  silent indefinite autonomy. Per run: a fresh dated run-tag + one working
  directory; **exactly one mutable research input** (everything else frozen);
  a **read-only ground-truth evaluator** (evidence gate + agreed rubric) never
  patched to pass; a fixed iteration budget with timeout on overrun; an
  **append-only results ledger** (`results.tsv`: id / metric / cost / status /
  description); keep / discard / crash advancement with revert; frontier
  tracking (only new-best advances); and a simplicity criterion. The upstream
  "NEVER STOP" clause is **replaced** with checkpoint-on-frontier-change,
  pause-and-surface-after-batch, clean-interrupt-on-user-action, and
  scope-drift→pause. Every claim carries source/license provenance at retrieval.
- **Why it changed:** the fully-autonomous autoresearch/autonovel pattern is a
  strong mechanism, but its loop-forever clause conflicts with the team's
  supervised, user-reviewed delegation stance. It became a standing procedure
  for future research runs.
- **Evidence:** [VERIFIED — internal operating record] intake of the two source
  repos and a supervised-loop draft procedure (dated 2026-09-09).
  [VERIFIED — public conceptual source] `karpathy/autoresearch`
  (<https://github.com/karpathy/autoresearch>) and
  `NousResearch/autonovel` (<https://github.com/NousResearch/autonovel>).
  Conceptual adoption only — no code/prose copied.

### 3. Phase-gated pipeline (role phases + Definition-of-Done gates)

- **What:** Multi-stage work is a Lean + Six Sigma pipeline: Research →
  Analysis/Architecture → Design → Build → QA, with the Director integrating.
  Each phase has a Definition-of-Done gate; a stage is not dispatched until the
  prior gate passes (**Andon stop-the-line**); gate verdicts update in place;
  and bug-documenting tests flip to assert the fixed behavior.
  **JIT piece-gating** forwards each stable partial the moment it is usable,
  never holding a full completion. Thresholds, explicit retry caps, and plateau
  detection stop unbounded polish.
- **Why it changed:** pure sequential handoff stalled the line; un-gated
  advancement let defects compound.
- **Evidence:** [VERIFIED — internal operating record] team operating doctrine
  and the live JIT orchestration run (2026-08-31 / 2026-09-01).
  [VERIFIED — public conceptual source] the autonovel phase machine
  (foundation → drafting → revision → export with explicit thresholds, retry
  caps, plateau detection) — conceptual adoption only.

### 4. Producer/verifier separation + read-back receipts

- **What:** The agent that produces an artifact does **not** pass it. QA runs
  adversarial verification against producer output; gate verdicts ground in
  **read-back tool output** (grep count, checksum, `config get`), never a
  producer's "done" self-report. A deliverable is significant only after
  machine read-back. Verifies against the real dependency, not a mock, even
  mid-build.
- **Why it changed:** happy-path self-verification repeatedly passed
  plausible-but-wrong deliverables; producer-committed signals and a separate
  verifier close that gap.
- **Evidence:** [VERIFIED — internal operating record] operating doctrine
  (adversarial QA caught 2 MAJOR + 2 minor blockers in one review; the
  read-back-receipt acceptance gate from the live JIT run).
  [VERIFIED — public conceptual source] autonovel's "different judge vs.
  producer" rule — conceptual adoption only.

### 5. Durable state and append-only ledgers

- **What:** Every run and pipeline writes an append-only durable ledger and
  leaves state recoverable from disk, so a fresh process resumes rather than
  restarts. Ledgers in use: experiment ledgers (`results.tsv`, keep/discard/
  crash + frontier), the grounded-citation source ledger (URL / retrieval date
  / title / verbatim evidence quote), project value/asset ledgers with
  **ledger-to-disk parity** (machine-counted), and process spawn bookkeeping.
  Durable artifacts are the team's analogue of Erlang process state that
  survives restart — a respawned worker reloads from disk, never from dead
  context.
- **Why it changed:** in-context progress is lost on any respawn/stall, and
  observation cadence is unreliable — correctness must derive from durable
  on-disk records. This is also the substrate for the entropy-proof axiom.
- **Evidence:** [VERIFIED — internal operating record] the live JIT run's
  durable handoff briefs and read-back files; preservation dumps of the value
  and asset ledgers; the experiment-ledger schema; the process spawn ledger.

### 6. QA / simplicity / adversarial gates

- **What:** Quality is a gate, not a hope. QA runs an adversarial pass:
  mechanical gate first (cheap, deterministic), then a separate LLM judge.
  Simplicity criterion (a marginal gain adding ugly complexity is not kept; a
  deletion that holds or improves is a win). Adversarial "cut N words" probes —
  the cut list IS the revision plan. Dual-persona review and forced-pick
  comparison where divergent judgments are the editorial decision. Plateau
  detection + explicit retry caps stop infinite polish. QA cuts across every
  stage, looping back to the owning agent.
- **Why it changed:** happy-path suites missed structural blockers; unbounded
  polish and complexity creep cost cycle time.
- **Evidence:** [VERIFIED — internal operating record] the value of the QA gate
  observed in doctrine (structural blockers a happy-path suite missed).
  [VERIFIED — public conceptual source] the autoresearch/autonovel evaluation
  stack (mechanical-then-LLM judge, dual-persona review, adversarial edit, Elo
  comparison, plateau + caps) — conceptual adoption only.

### 7. Corrected role / pipeline sequence (fixes the duplicated UX sequence)

- **What:** The role sequence is corrected to a **single pass**: Director
  (frame) → Researcher → Architect → UX → Coder → QA → Director (report). The
  earlier documented 9-step "contribution order" listed **UX twice** and an
  early **QA/Scoper** pseudo-stage; both are removed. UX is a single design
  role; scope-cut and feature-extension-prevention live with QA. The site and
  docs now show this one corrected sequence (7 stages, six archetypes, each in
  its lane once).
- **Why it changed:** dynamic-over-specialization broke down — the first agent
  to receive instruction executed indiscriminately, reducing specialists to
  reviewers, eroding the coder's dev role, and drifting the architect into
  code. The duplicated sequence on the public site had to match the verified
  operating order.
- **Evidence:** [VERIFIED — internal operating record] the team's sequential
  workflow and role doctrine (dated records through 2026-08-31), which fix
  Research → Analysis → Design → Build → QA with Director frame/report.

### 8. Five-minute live check-ins and stall recovery

- **What:** During live multi-agent pipelines the orchestrator does not
  fire-and-forget: it holds periodic live check-ins on running subagents (on
  the order of minutes) to confirm nobody is stuck, surface status, and
  steer/stop or stall-recover when a child drifts or dies. Users get periodic
  progress reports over silence-then-timeout.
- **Why it changed:** detection-without-recovery left stalled pipelines silent,
  and the operating directive demanded periodic status checks with intervention
  on stalls.
- **Evidence:** [VERIFIED — internal operating record] the orchestrator's
  routing/role doctrine and the user's standing preference for milestone
  updates and short progress reports over silence-then-timeout.

### 9. Cross-profile fleet spawning

- **What (verified practice):** Work is spawned across profiles **natively** —
  a session under one role profile delegates to, and writes into, the working
  directories of sibling profiles; each role being its own profile is what
  makes delegation profile-native. Worktrees isolate parallel agents.
- **Status flag:** a formal **fleet-orchestration spec** (a full phase-machine
  with thresholds and state tracking applied to cross-profile spawning) was
  named as a next action but is **not yet drafted**. It is documented here and
  in `choreography/orchestration.md` §9 as **[PROPOSED / PENDING]** — do not
  treat it as completed doctrine until a dated spec exists.
- **Why it changed:** this is how the supervision / research-loop / fleet
  upgrades were actually executed (cross-profile orchestration), and the fleet
  wanted the pattern made a first-class, documented capability.
- **Evidence:** [VERIFIED — internal operating record] delegation artifacts
  authored under sibling profiles and the fleet role doctrine naming worktrees.
  [PROPOSED / PENDING] the fleet-orchestration spec (named, undrafted).

### 10. Served-truth / staging-first deployment verification

- **What:** Verify the thing that is actually served/live, not a local claim —
  read-back receipts, verify on disk AND the live page, distinguish local from
  live, and never push straight to a live site's main domain (staging first,
  user reviews/approves, then promote). Mock-only verification is
  under-verification when a real endpoint exists.
- **Why it changed:** per-side green suites did not prove end-to-end
  correctness; "works on my machine" and mock-only verification shipped latent
  bugs.
- **Evidence:** [VERIFIED — internal operating record] deployment-verification
  and cross-system wire-contract discipline; the read-back / mock-vs-real rule
  from the live JIT run; the staging-first operating directive.

### 11. Licensing / provenance discipline

- **What:** No third-party code or asset enters a kit, build, or public repo
  until its license and provenance are verified against a primary source and
  recorded in an attribution ledger with **ledger-to-disk parity**
  (machine-counted, not sampled). Unfillable attribution → `ship:false` /
  REJECTED and excluded from the served build. A **README-only license
  declaration** is a weaker grant than a committed LICENSE (treated as
  all-rights-reserved in default jurisdictions). Copying an asset carries its
  own provenance. Kit layer = Apache-2.0 over MIT Hermes; vertical packs
  proprietary by contract.
- **Why it changed:** unfillable-attribution and unlicensed third-party
  material were a recurring latent risk across asset/engine reuse; a standing
  license gate prevents shipping IP-risky or legally-weak content.
- **Evidence:** [VERIFIED — internal operating record] a source-material audit
  (license matrix, ledger-to-disk parity, provenance-gap `ship:false`
  verdicts); intake license probes of the autoresearch/autonovel repos
  (README-declared MIT, no committed LICENSE). [VERIFIED — public conceptual
  source] Erlang/OTP licensing is untouched — the OTP references above are
  concept-only.

### 12. Entropy-proof design

- **What:** Every Team6 system must be correct as a pure function of durable
  state, never of observation cadence — still correct on first read after 2+
  months untouched. Derived-from-disk beats stateful edge-triggers;
  reconstruction beats real-time tracking; data self-describes at point of use;
  audit every new system against this before build.
- **Why it changed:** the team's operating context has real-life gaps; monitoring
  and automation that assume continuous observation fail on return-from-absence.
- **Evidence:** [VERIFIED — internal operating record] an operating directive
  encoded across every role's preservation records ("all systems we build must
  be entropy-proof").

### 13. JIT handoff, read-then-die recovery, context split (folded into orchestration)

- **JIT piece-gated handoffs + producer-committed signals:** forward stable
  partials immediately, marked STABLE vs DRAFT; a downstream gate may only poll
  a signal the producer's brief commits to writing; fold mid-flight defects
  into a running pass; orchestrate with standardized handoff briefs
  (context / locked decisions / assumptions / done / next / OPEN). Why: the
  STABLE-marker deadlock stalled a live build, and duplicate dispatch wasted
  restarts.
- **Read-then-die recovery:** subagents that read specs for most of their
  budget then die before writing are the dominant failure mode; counter with
  write-skeleton-first, full-context-inline, declare-environment-on-disk,
  artifact-sized scope, and mark-partial-files-as-intended. Why: most failed
  runs wrote zero files before dying on transient errors.
- **Context split / worker budget:** the orchestrator holds the long context;
  workers are focused with a hard budget; tasks decompose into contract-sized
  units the orchestrator integrates at the seams. Why: workers truncate
  oversized tasks and solo orchestrator reasoning spirals on hard problems.
- **Evidence:** [VERIFIED — internal operating record] the live JIT
  orchestration run and the team operating doctrine (subagent-recovery rules,
  orchestrator-context doctrine).

---

## 1.0.0 — Efficiency update

Original open-core release. Renamed airefea-kit → Team6-kit; added the
knowledge-router (MoE-style activation for persistent memory) and
zero-context-preservation (direct-execution pivot) skills to `templates/`; made
open-core assembly gated (sweep + review + generate) with an instantiation
proof-point in `demo/` + `examples/`.
