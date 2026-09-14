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
is https://team6.askaconsult.com. The repository is the source of truth at
https://github.com/ahrazzle/team6-kit. GitHub Pages is not used and the old
Pages site was taken down. The canonical site carries visible navigation back to
https://askaconsult.com/digital/. The deployment and DNS boundary is managed
outside this repository.

---

## Unreleased — Release gate verification (2026-09-14)

- **What:** add a deterministic release gate runner at `build/verify-all.py`
  that runs all public gates in documented order: sweep-gate, review-gate,
  surface-scan, check-artifact-contract self-test, preflight/check self-test,
  report/check self-test, and fresh-clone generation test. Also add GitHub
  Actions workflow at `.github/workflows/verify.yml` that runs the gates on
  push and pull requests with Python 3.11 and 3.12, using only checkout and
  setup-python actions (safe for forks, no secrets). Fix a blind spot in
  surface-scan: when `build/identifiers.yaml` is absent or empty, the scanner
  still enforces built-in generic safety terms (paths, credential patterns)
  that must never appear in public code. Add tests for verify-all and the
  empty-identifiers case. Update README.md and index.html to document the
  release gates and CI status.

- **Why it changed:** need a single point of entry for verification that runs
  all gates automatically, with CI integration that catches problems before
  merge. The empty-identifiers fix ensures the scanner remains effective in
  fresh clones and open-kit scenarios.

- **Evidence:** [VERIFIED — internal operating record] gates, checkers, and
  self-tests exist and pass; workflow tested on local execution.

- **Files:** `build/verify-all.py`, `.github/workflows/verify.yml`,
  `build/surface-scan.py`, `tests/test_gates.py`, `README.md`, `index.html`.

---

## Unreleased — Execution-evidence contract (2026-09-13)

- **What:** adds `choreography/run-evidence.md`, defining a vendor-neutral
  contract for recording execution evidence: what an agent actually executed,
  not only that a procedure ran. Evidence record fields include run id, phase,
  parent/child relations, step kind, tool/model identifiers, timestamps, status,
  artifact references, unresolved items, and evidence boundary. Distinguishes
  procedure evidence from achieved-state evidence (exit code alone insufficient).
  Token accounting counts only innermost spans; cost honesty uses dated price
  table (unknown models remain unknown); run comparison uses stable step keys
  (kind + tool/name); retention is bounded with dropped-count visibility; no
  secrets/raw prompts by default; local/loopback guidance. Includes acceptance
  checklist and vendor-neutral example record.
- **Why:** Team6 has read-back receipts and logs but no local, framework-agnostic
  artifact of what the agent actually executed (span tree, tool calls, tokens,
  latency, per-model cost) nor a way to diff two runs step-by-step. This is the
  one genuine capability gap identified in the local-agent-toolkit audit.
- **Evidence:** [VERIFIED — internal operating record] local-agent-toolkit audit
  (2026-09-13) identifies observability as the one real gap. This release
  implements the rules-only adaptation (no external code copied).

- **Files:** `choreography/run-evidence.md`, `README.md`, `index.html`, `CHANGELOG.md`.

---

## Unreleased — OpenShorts route (2026-09-14)

- **What:** docs-only OpenShorts route + non-executable example config; no new dependencies; no bundled code; external tool license and dependency terms apply.
- **Files:** `choreography/openshorts-route.md`, `registry/openshorts-route.yaml.example`, README, CHANGELOG, index.html.

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

## Unreleased — Goal-state evidence guidance (2026-09-13)

- **What:** add one operating rule to `choreography/artifact-contract.md`:
  evidence must prove the achieved target state, not merely that a command or
  procedure ran. A verifier rejects procedure-only evidence.
- **Why it changed:** a passing command does not prove the requested state was
  reached. Adjudicating a handoff on procedure execution alone lets an
  unachieved target state through.
- **Evidence:** [VERIFIED — public conceptual source] the state-versus-procedure
  framing is inspired by Levin, M., "Ingressing Minds: Causal, Non-Physical
  Patterns In-Form Natural, Synthetic, and Hybrid Embodiments," Philosophies
  11(5), 161 (2026), https://doi.org/10.3390/philosophies11050161. Adopted as a
  framing for evidence sufficiency only. The paper's metaphysical and ontology
  claims are not adopted, cited, or relied on.
- **Proof status:** [PROPOSED / PENDING] documentation rule; repository gates
  and independent review required before release.
- **Files:** `choreography/artifact-contract.md`, `CHANGELOG.md`.

## Unreleased — I/O delegation contract (2026-09-13)

- **What:** add a public, vendor-neutral `choreography/io-delegation.md`
  contract and `registry/io-delegation.yaml.example` example config. It
  documents a bounded routing pattern for two narrow work classes — predictable
  read-heavy summarization and pattern-conforming scaffolding — while the
  frontier agent keeps edits, debugging, architecture, security/safety-critical
  work, ambiguous requirements, and final acceptance. Route identity reuses the
  provider/model/API-host rules in `choreography/model-policy.md`; input must
  pass the local privacy/redaction policy in
  `choreography/local-preprocessing.md` first; default mode is `observe` with no
  invented quotas; worker output is advisory and ephemeral; and every delegation
  records route, input/output byte counts, latency, status, fallback, and
  verification result without raw sensitive content. Documentation and an
  example config only — no executable hooks, network clients, model
  dependencies, or profile-specific settings are added.
- **Why it changed:** a large-file offload pattern can reduce frontier-context
  cost, but it carries real risks (sensitive-data leak, context loss, latency,
  shallow summaries). The counterargument is met by making it an **opt-in,
  bounded, audited contract** that is never automatic merely because a file is
  large and never delegates the work that must stay on the frontier agent.
- **Evidence:** [VERIFIED — public conceptual source] Spotify Engineering
  article "Portal by Spotify cut my Claude Code token usage by 90%"
  (engineering.atspotify.com, 2026-09-03) describing a routing principle that
  keeps frontier reasoning for edits/debugging/architecture/safety-critical
  work and routes predictable I/O-heavy work to a cheaper worker. Adopted as a
  principle only — no code, prompts, or source copied; the linked `shunt`
  plugin is Apache-2.0 at `spotify/portal-ai-plugins@main/plugins/shunt` but is
  referenced for the routing principle, not imported. The 90% figure is a
  **self-reported vendor claim**, not Team6 evidence: Team6 adopts only the
  routing principle and does not claim this result.
- **Proof status:** [PROPOSED / PENDING] Team6-kit documentation change;
  fresh-clone gates and independent review required before release.
- **Files:** `choreography/io-delegation.md`, `registry/io-delegation.yaml.example`,
  and the README overview.

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
- **Evidence:** [Internal design] Team6's own conceptual operating pattern for
  side-effect and cost preflight. No external code, prompt, or dependency is
  bundled. The Team6 Kanban board remains the authoritative task record; the
  preflight is a review aid, not a runtime integration, and adds no provider
  call, paid operation, or configuration change.
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

## 1.5.0 — Artifact contract and resume/feedback handoff (2026-09-13)

### Machine-checkable handoff contracts

- **What:** add a generic handoff-contract format and its dependency-free
  validator. One file per stage boundary carries: expected artifacts,
  required sections/markers, size bounds, tests/commands, evidence refs,
  runtime state (`local` / `staged` / `live`), explicit failure state, last
  stable phase, resume phase, feedback to apply, artifacts to regenerate, and
  artifacts **not** to touch. Ships as `choreography/artifact-contract.md`
  (format + rules), `templates/contracts/artifact-contract.md.tmpl` (fill-in
  template), `build/check-artifact-contract.py` (validator + 16-case
  self-test), and valid/invalid examples in `examples/`. The generator ships
  all five under `contracts/` in the instantiated kit. No second orchestration
  runtime is added: the checker validates the *document*, never executes a
  pipeline.
- **Why it changed:** resumed and review-cycle handoffs kept failing at the
  artifact level even though `orchestration.md` §6/§7/§11 already demand
  durable state, read-back receipts, and producer-committed signals —
  finished work got redone, approved artifacts got silently rewritten, and
  "done" claims carried no machine-checkable evidence. The missing piece was
  a *checked* format, not another stated norm.
- **Provenance:** this is a Team6 internal operating record for artifact
  handoffs. The pattern was designed by Team6 to solve resume/feedback
  boundary issues in Kanban workflows; it is not derived from external code
  or documentation, and no external orchestration code, prompts, or prose
  are bundled. The field set, parser, and rules are Team6's own generic
  form. **Team6 Kanban remains the state authority** — the contract is a
  per-handoff snapshot written out of the Kanban record, never a
  replacement for it.
- **Evidence:** [VERIFIED — internal operating record] the fleet's
  resume/handoff failure classes (read-then-die, STABLE-marker deadlock,
  silent rewrites — see the 1.1.0 item 13 record). [VERIFIED] the checker's
  self-test: 16/16 pass, including a missing-required-field case that fails
  and a complete contract that passes, and both repo examples validate to
  their expected verdicts (valid → exit 0, invalid → exit 1 for the
  missing `resume_phase` and the illegal `runtime_state` enum). Public files
  contain generic names only; the full 8-surface leak scan passes.
- **Files:** `choreography/artifact-contract.md`,
  `templates/contracts/artifact-contract.md.tmpl`,
  `build/check-artifact-contract.py`, `build/generate.py` (contracts/ copy
  step), `examples/artifact-contract.{valid,invalid}.yaml`, README, CHANGELOG.

---

## 1.4.1 — Router trust-boundary and tool-execution safety (2026-09-13)

- **What:** add `choreography/router-security.md`, a vendor-neutral preflight
  contract for model routers and relays. It covers endpoint and upstream-path
  trust, credential minimization, high-risk tool gates, autonomous execution,
  metadata-only audit logs, and conditional or dependency-targeted tampering
  tests. It provides a generic checklist for evaluating whether a router or
  relay meets the team's safety requirements before it is enabled.
- **Why it changed:** routers and relays can see plaintext requests and
  responses, and may sit between a model provider and the tools an agent runs.
  Without a trust boundary, there is no shared checklist for endpoint trust,
  credential handling, high-risk tool gates, autonomous execution, audit
  logging, or tampering tests. The new contract provides one.
- **Evidence:** [Internal design] Team6's own conceptual operating pattern for
  router trust boundaries. No external code, prompt, or dependency is
  bundled. The Team6 Kanban board remains the authoritative task record; the
  contract is a review aid, not a runtime integration, and adds no provider
  call, paid operation, or configuration change.
- **Proof status:** [PROPOSED / PENDING] documentation contract plus local
  validator; independent review required before treating it as release policy.
- **Files:** `choreography/router-security.md` and the README overview.

## 1.4.0 — Dynamic model-policy catalogue (2026-09-13)

### Route-based rate-limit protection

- **What:** add a route-based model-policy catalogue (registry/model-rate-limits.yaml.example
  and choreography/model-policy.md) for tracking provider limits per model,
  API host, and provider. It supports bounded admission, protected reserves,
  and observe-only mode for unknown limits.
- **Why it changed:** models move between agents, tasks, and workers. Without
  a unified policy, the team risks hitting unknown limits or inventing quotas.
  A route-based policy that follows the model by provider, identifier, and host
  solves this.
- **Evidence:** [Internal design] Team6's own conceptual operating pattern. No
  external code, prompt, or dependency is bundled. The Team6 Kanban board
  remains the authoritative task record.
- **Files:** `registry/model-rate-limits.yaml.example`, `choreography/model-policy.md`,
  and the README overview.

## 1.3.0 — Handover ingestion completeness & propagation loop (2026-09-12)

**Convention note:** The audit artifacts named by the original 1.3.0 record are not present in the current tree. The entries below preserve the conceptual history of that release; no current path is asserted for those historical files.

### 1. A handed-over source is not reference-only until it is audited

- **What:** a source handed over from another team or external party must go
  through a structured audit: ownership review, capability matrix, disposition
  classification, surface validation, and propagation through each surface's
  own gate.
- **Why:** without a structured audit, handed-over sources accumulate
  unclassified references, duplicate content, or orphan surfaces that never
  propagate to the full surface set.
- **Evidence:** [Internal design] Team6's own operating procedure from real
  handovers (the original 1.3.0 audit trail is not carried in this tree; see the convention note above).

### 2. The audit inspects surfaces, not the README

- **What:** the audit inspects the full surface set (README, CHANGELOG, registry,
  templates, choreography) and validates each against the candidate. It does
  not rely on README references alone.
- **Why:** references in the README do not guarantee the full surface set is
  complete or correct.
- **Evidence:** [Internal design] Team6's own operating procedure.

### 3. Capability matrix, owner, and disposition

- **What:** each handed-over candidate gets a capability matrix (what it covers,
  what it omits), an owner (who is responsible for it), and a disposition
  (adopt, adopt with caveats, or discard).
- **Why:** without these, candidates accumulate without clear ownership or
  disposition.
- **Evidence:** [Internal design] Team6's own operating procedure.

### 4. Separate the five phases

- **What:** handover audits follow five phases: intake, capability matrix,
  disposition, surface validation, and propagation. Each phase is recorded
  in the handover audit file.
- **Why:** separating phases makes handovers auditable and reproducible.
- **Evidence:** [Internal design] Team6's own operating procedure.

### 5. Bounded proof, receipts, and read-back

- **What:** each phase produces bounded proof (audit artifacts, surface
  inventory, propagation receipts) and requires a read-back to validate
  that the candidate is understood and correctly applied.
- **Why:** without proof and read-back, handovers are opaque and error-prone.
- **Evidence:** [Internal design] Team6's own operating procedure.

### 6. Preserve unresolved, dead, and blocked

- **What:** the audit preserves unresolved items, dead candidates, and blocked
  work in the handover record, with disposition and owner for each.
- **Why:** without preservation, candidates lose context and accumulate without
  resolution.
- **Evidence:** [Internal design] Team6's own operating procedure.

### 7. Propagation through each surface's own gate

- **What:** validated content propagates through each surface's own gate (README,
  CHANGELOG, registry, templates, choreography) and each gate is recorded in
  the handover audit.
- **Why:** without gate-by-gate propagation, content accumulates without
  consistency across surfaces.
- **Evidence:** [Internal design] Team6's own operating procedure.

### 8. One capability delta per candidate, routed by impact class

- **What:** each candidate produces one capability delta (what changes) routed
  by impact class (documentation, configuration, or code). Each delta is
  reviewed and signed off separately.
- **Why:** without routing by impact class, deltas accumulate without
  consistent review.
- **Evidence:** [Internal design] Team6's own operating procedure.

---

## 1.2.0 — Desert Ant local preprocessing (2026-09-11)

- **What:** add `choreography/local-preprocessing.md` (Desert Ant reference
  architecture for local privacy/redaction). This is guidance only.
- **Why:** agent inputs can leak sensitive content or cost-inefficient data.
  Local preprocessing (redaction, cost filters, content pruning) protects
  privacy and cost before they reach an external provider.
- **Evidence:** [VERIFIED — public conceptual source] Desert Ant reference
  architecture (desert-ant/desert-ant repo, Apache-2.0). Used for concept only;
  no code, prompt, or dependency is bundled.
- **Files:** `choreography/local-preprocessing.md`.

## 1.1.0 — Local privacy/redaction policy (2026-09-10)

- **What:** add `choreography/local-preprocessing.md` (local privacy/redaction
  policy). This is guidance only — no runtime or dependency is added.
- **Why:** agent inputs can leak sensitive content or cost-inefficient data.
  Local preprocessing (redaction, cost filters, content pruning) protects
  privacy and cost before they reach an external provider.
- **Evidence:** [Internal design] Team6's own conceptual operating pattern.
- **Files:** `choreography/local-preprocessing.md`.

---

## 1.0.0 — Initial release (2026-09-01)

- **What:** initial release of Team6-kit, a framework for turning a single AI
  agent engine into a multi-agent team with clear rules and responsibilities.
- **Why:** to provide a reference implementation for multi-agent team
  orchestration with clear contracts, QA gates, and provenance tracking.
- **Evidence:** [Internal design] Team6's own conceptual operating pattern.
- **Files:** Initial commit.
