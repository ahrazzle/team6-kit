# Team6-kit

Turn one AI agent engine (Hermes, from Nous Research) into a small team of AI agents that work together under clear rules — with a supervisor, a quality checker, and a builder that assembles your own team from ready-made parts.

Canonical site: https://team6.askaconsult.com/
ASKA corporate page: https://www.askaconsult.com/team6

The canonical site is the public documentation for Team6-kit. The ASKA
corporate page is the service listing for the team that uses it. The
interactive experience is served by the Team6 Frontier Vercel project through
ASKA's `/team6` route.

## What problem does it solve?

One AI agent can lose track, skip steps, or claim work is done when it isn't. Team6-kit sets up several agents with separate jobs — planner, builder, checker — and rules so that:

- Work is checked by a different agent than the one that did it.
- Writing is proofread and fact-audited by a different agent than the one who wrote it.
- Progress is saved on disk, so a crashed agent can resume where it left off.
- Long tasks pause for review instead of running silently forever.
- Knowledge is stored in small files that load only when needed.

## How you use it

1. Pick a ready-made agent profile from `templates/` (each has a role and rules).
2. Add a settings file from `registry/` with your own values.
3. Run the builder, which checks everything and creates your team folder:

```
python3 build/sweep-gate.py      # check the source files are in order
python3 build/review-gate.py     # check every item has been reviewed
python3 build/generate.py --out my-team [--params my-settings.yaml]
```

You get a folder with your team's agents, ready to run.

## What's in the repo

| Folder | What it is |
|---|---|
| `templates/` | Ready-made agent profiles and generic skills |
| `build/` | The builder scripts (the only way to create a team) |
| `registry/` | Settings files you can customize |
| `choreography/` | How the team works together and the rules it follows |
| `AUDIT/` | Records of where content came from |
| `WHY.md` | Why the system is designed this way |
| `CHANGELOG.md` | What changed in each release |

## Anti-loop discipline

The kit includes a contract to prevent thinking loops. It defines four rules:
load once then use, read once then act, plan once then execute, and trust tool
output as the receipt. Published artifacts and live pages still require read-back.

Read `choreography/anti-loop-discipline.md` for the full contract.

## Model rate-limit protection

The kit includes a route-based model-policy catalogue. It follows a model by
provider, model identifier, and API host, so the policy remains correct when a
model moves between agents, tasks, fallback chains, or worker processes. Known
limits can be enforced with bounded waiting and protected request/token
reserves. Unknown limits stay observe-only; the kit never invents a quota.

Start with `registry/model-rate-limits.yaml.example` and read
`choreography/model-policy.md` before adding provider values. Keep the policy
catalogue separate from profile names and account credentials.

## I/O delegation contract

The kit also documents a **vendor-neutral I/O delegation contract**: an opt-in
routing pattern that may offload predictable, read-heavy summarization or
pattern-conforming scaffolding to a cheaper worker, while the frontier agent
keeps edits, debugging, architecture, security/safety-critical work, ambiguous
requirements, and final acceptance. It is never automatic just because a file
is large, never transmits sensitive content, and every delegation is recorded
with route and byte/latency telemetry. It is a contract and an example config
— not a runtime, hook, or dependency.

Start with `registry/io-delegation.yaml.example` and read
`choreography/io-delegation.md`. Route identity follows the same
provider/model/API-host rules as `choreography/model-policy.md`, and input must
pass the local privacy/redaction policy (`choreography/local-preprocessing.md`)
first. Thresholds are recommendations, not universal claims.

## Artifact contracts and resume handoffs

Every stage boundary — producer to verifier, failed run to resumed run —
carries one handoff file: expected artifacts, required sections, size bounds,
tests, evidence refs, runtime state (local/staged/live), failure state, last
stable phase, resume phase, feedback applied, what to regenerate, and what not
to touch. Team6 Kanban remains the state authority; the contract is the
handoff snapshot written out of it. Read
`choreography/artifact-contract.md`, start from
`templates/contracts/artifact-contract.md.tmpl`, and gate with
`python3 build/check-artifact-contract.py <contract>` (or `--self-test`).
The pattern is a conceptual adoption; no external orchestration code is
included or required.

A finished worker stays reachable. When a one-shot run ends, it leaves its
session saved, so a follow-up can be sent to that same session. The worker
answers that single turn, then stops again.

This lets you add one correction or ask one question after a task is done
without starting a new session or losing the thread. Send a follow-up only
after the worker has fully stopped, and only for a turn that reads state.
Never attach a second live writer to a session that is still running.

## Session-recall observer

The session-recall observer reads existing session history and persistent memory to produce recall views.
It is read-only: it does not create a missing store and never writes history or memory.
A missing store appears as an empty view; a real failure is logged internally and returned as a generic error without a traceback.
Memory recall uses the same parse agreement as the memory tool, so the view does not reinterpret saved entries.
Subject signals are deterministic guidance from titles, paths, tool names, slash commands, quoted phrases, and identifiers; read `choreography/session-recall.md` for the full contract.

## Release gate verification

The kit includes a deterministic release gate runner at `build/verify-all.py`.
It runs all public gates in documented order and fails if any check fails.
GitHub Actions runs this automatically on push and pull requests to ensure
the repository stays in a verified state.

Read `choreography/release-gates.md` for the full gate list and order.
**Fresh-clone contract validator gate.** The kit's validators are now exercised
as part of the fresh-clone test. Run `bash scripts/fresh-clone-test.sh` to
clone HEAD to a temp dir and verify (1) frozen artifacts are present, (2) live
artifacts are absent, (3) the demo reproduces, (4) the audit is honest, and
(5) all contract validators pass their self-tests. The aggregator script
`build/check-contracts.py` runs the artifact-contract, preflight, report,
grouped scored-rollout, and declarative reward catalogue validators — each with
its fixtures — in sequence; it is stdlib-only, requires no network or
credentials, and fails closed on errors. The release runner
`build/verify-all.py` runs this aggregate gate before the fresh-clone gate.

Verify a checkout locally (exact commands):

```
python3 -m unittest tests/test_gates.py     # unit tests (stdlib-only)
python3 build/verify-all.py                 # all release gates in order
bash scripts/fresh-clone-test.sh            # clone HEAD and reproduce the demo
python3 build/surface-scan.py               # 8-surface instance-leak scan
python3 build/check-contracts.py            # aggregate contract gate
```

## Router trust-boundary protection

Model routers and relays can see plaintext requests and responses, and may sit
between a model provider and the tools an agent runs. Read
`choreography/router-security.md` before enabling one. It provides a generic
preflight checklist for endpoint trust, credential minimization, high-risk tool
gates, autonomous execution, metadata-only audit logs, and conditional or
dependency-targeted tampering tests. It is guidance only: it does not install a
router, change provider settings, or claim that a route has end-to-end response
integrity.

## Side-effect and cost preflight

Before running an operation that edits files, contacts external systems, uses
credentials, incurs paid operations, affects public surfaces, or needs
rollback, write one preflight document: what changes, what it contacts, which
credential *names* (never values) it needs, what it may cost, which actions
are conditional, what becomes public, how to recover, who approves, and what
is still unknown. `choreography/side-effect-cost-preflight.md` defines the
contract; `build/preflight/check.py` is a dependency-free validator that fails
closed on missing fields, credential values, unbounded waits, or missing
rollback. It is a Team6 internal operating pattern for side-effect and cost
preflight. The Team6 Kanban board remains the authoritative task record.

## OpenShorts route (external, docs only)

Finished short-video production requests — where you explicitly ask for a rendered
short — route to OpenShorts, an external local-first tool Team6 has studied as a
reference. This is a documentation route only: Team6-kit does not bundle or run
OpenShorts, does not render video by itself, and does not post, publish, or schedule
anything on your behalf. Transcript, summary, and media-research requests stay on the
existing media skills. You install OpenShorts separately and check its current license
and dependency terms before use; the route ends at a local export you review.

Start with `registry/openshorts-route.yaml.example` and read
`choreography/openshorts-route.md`.

## Safe shareable run packet

When a run finishes, the people who need to know about it are usually not at the
terminal that ran it. A run packet is the one artifact that travels: objective,
decisions, verified evidence, unresolved items, changed artifacts, test results,
runtime/live status, next gate, provenance, and redaction status.
`choreography/safe-run-packet.md` defines the contract; `build/report/check.py`
is a dependency-free validator that fails closed on a missing required field,
evidence marked verified without evidence, a live status without target or
evidence, omitted unresolved items, an internal path or profile identity, a
credential-like value, or an off-convention placeholder. It is a conceptual
operating pattern adapted from the general idea of an agency-orchestration run
report — no Agency Orchestrator code is copied — and the Team6 Kanban board
remains authoritative: the packet is a derived shareable report, not a second
state store.

## Guarded review and repair

A review that quietly mutates — closing, labeling, or merging as it reports — is
the self-approval failure in another costume. The kit's guarded review/repair
contract separates the two roles. One report records a review, an adversarial
pass, a browser verification, or an artifact verification; it binds every step to
the live target head with its source evidence, owner, and rollback path; it keeps
proposed mutations separate from the review output and approval-required; and it
gives every repair a regression-test contract with the pre-fix / post-fix
distinction. An agent report may not propose a merge, a rename, or a
slash-command name. `choreography/review-repair-workflow.md` defines the
contract; `build/review-repair/check.py` is a dependency-free validator that
fails closed, with a fixture corpus for the review, adversarial, browser, and
artifact lanes. It is adapted from public review/repair contracts and workflow
patterns as principles only — no bot, workflow YAML, or source is bundled — and
the Team6 Kanban board remains authoritative: the report is a derived record, not
a second state store.

## Execution evidence

The kit defines a vendor-neutral execution-evidence contract that records what
an agent actually executed, not only that a procedure ran. It specifies evidence
record fields, distinguishes procedure evidence from achieved-state evidence,
and establishes rules for token accounting (innermost spans only), cost honesty
(unknown models remain unknown), run comparison with stable step keys, and
bounded retention with no secrets or raw prompts by default.
Read `choreography/run-evidence.md`.

## Makepad references

The kit records selected Makepad work as conceptual references only.

[VERIFIED - public conceptual source]
- **Core UI runtime** (makepad/makepad, MIT): Declarative design separate from renderer.
- **Serialization tooling** (makepad/microserde, MIT): Build/runtime design question.
- **Model-wire reference** (makepad/llama_antirez_deepseek, MIT): Integration pattern only.
- **Quantization reference** (makepad/llama_nvfp4, MIT): Hardware-specific pattern only.
- **Historical live-coding** (makepad/makepad_history, MIT): Historical context only.
- **Static WASM publishing** (makepad/makepad.github.io, Apache-2.0): Artifact checking reference.
- **Transcript provenance** (makepad/ai_snake, MIT): Metadata shape reference.

No Makepad code, dependency, runtime, model, asset, transcript, or deployment is included or required.

B1 (cross-platform Rust UI), C1 (native GPU backends), and C3 (declarative UI DSL) remain proof-pending follow-up spikes. They do not affect the current build.

Full source table: [AUDIT/makepad-learnings.md](AUDIT/makepad-learnings.md)

## Codebase-map snapshot contract

This documents a portable snapshot format for spatial codebase evidence. A versioned JSON contract preserves hierarchy, size, ordering, and provenance while failing closed on malformed or leaky inputs.

Includes:
- `choreography/codebase-map.md` — contract
- `build/check-codebase-map.py` — stdlib-only validator
- `demo/codebase-map/index.html` — static treemap proof

To run the validator:

```
python3 build/check-codebase-map.py examples/codebase-map.valid.json
```

To run the local viewer proof:

```
python3 -m http.server
```

Then open `demo/codebase-map/index.html` in your browser. The viewer is zero-dependency and runs from a synthetic fixture. It is local-only. Area represents a declared measure (size); it does not mean importance.

Attribution: This slice uses Codemap as a conceptual source only. The implementation is a clean reimplementation from scratch in zero-dependency static HTML/JavaScript (viewer) and Python-stdlib (validator); no source code, comments, fixtures, or UI text from Codemap were copied.

## Scored rollout contract

The kit provides a local JSONL contract and validator for **grouped scored
samples**: a run header, one declaration per group, and scored samples with
explicit token/mask/log-probability length and finite-value rules. Evaluation
handling, off-policy caps, and per-group allocation minima are recorded and
validated as metadata. It does **not** ship a trainer, an inference server, or
an RL runtime — it gives a future evaluation or post-training adapter one
stable, inspectable artifact boundary.

Read `choreography/scored-rollouts.md`, start from
`templates/contracts/scored-rollout-group.jsonl.tmpl`, and gate with
`python3 build/check-scored-rollout.py <artifact.jsonl>` (or `--self-test`).
Neutral examples: `examples/scored-rollout-group.valid.jsonl` and
`examples/scored-rollout-group.invalid.jsonl`. The grouped-scoring,
evaluation-handling, off-policy, and allocation semantics are a conceptual
adoption; no external rollout, trainer, or server code is included or required.

## Reward catalogue

The kit also provides a **declarative reward catalogue** with a local
validator: a registry example that names reward identities and their declared
behaviour, so a reviewer can check a reward's input, output, score range,
determinism, modes, and provenance before use. It is metadata only — it is
**not** a dynamic loader and it does **not** execute a named reward. Executable
hook fields are rejected, and the catalogue never imports or evaluates an
implementation.

Read `choreography/reward-registry.md`, start from
`registry/reward-functions.yaml.example`, and gate with
`python3 build/check-reward-registry.py <catalogue.yaml>` (or `--self-test`).
Neutral examples: `examples/reward-functions.valid.yaml` and
`examples/reward-functions.invalid.yaml`. The catalogue is a source-repo
registry example; the kit ships no executable reward registration code. The
identifier-and-validation registry qualities are a conceptual adoption; no
external registry code or decorator is included.

## The main rules

1. **Everything on disk.** Progress is saved to files, so months later you can still pick up where you left off.
2. **Check what is actually live.** Test on a staging copy, get approval, then publish. Never announce "done" from a local test.
3. **The maker never marks their own work.** A different agent checks it and records the result.
4. **Supervised, not autonomous.** Long tasks pause, save progress, and ask for review. Nothing runs forever unattended.

For work performed with an AI coding agent, use the compact
`choreography/ai-assisted-development.md` contract. It adds behavior-first
testing, security checks, scope control, and evidence requirements without
replacing the Team6 ownership and QA gates.

## What's new in this release (1.7.0)

This release adds two documentation-first contracts with dependency-free local
validators. **Grouped scored-rollout contract:** a JSONL interchange shape for a
run of scored samples grouped for comparison — a run header, group
declarations, and samples with explicit token, mask, and log-probability
length/finite rules; evaluation handling, off-policy caps, and allocation
minima are recorded and validated as metadata. **Declarative reward
catalogue:** a registry example that names reward identities and declared
behaviour and is validated before use, with executable hook fields rejected.
Neither adds a trainer, rollout service, inference server, reward executor, or
dependency. See `choreography/scored-rollouts.md`,
`choreography/reward-registry.md`, `build/check-scored-rollout.py`, and
`build/check-reward-registry.py`; `CHANGELOG.md` records the full entry.

## What's new in this release (1.5.0)

Every stage boundary can now carry one machine-checkable handoff contract: expected artifacts, required sections, size bounds, tests, evidence refs, runtime state (local/staged/live), failure state, resume phase, feedback applied, artifacts to regenerate, and artifacts not to touch. See `choreography/artifact-contract.md` and `build/check-artifact-contract.py`; Team6 Kanban remains the state authority. The previous release added the route-based model-policy catalogue (`choreography/model-policy.md`). See `CHANGELOG.md`.

## What's new in this release (1.4.1)

The kit now includes a route-based model-policy catalogue for changing provider limits, plus a generic router trust-boundary and tool-execution safety contract. Unknown limits remain observe-only, while verified limits can use bounded admission and protected reserves. See `CHANGELOG.md`, `choreography/model-policy.md`, and `choreography/router-security.md`.

## License

- **Engine:** Hermes by Nous Research, MIT license. This is not a fork; we build on top of it.
- **This kit (profiles, rules, builder):** Apache-2.0.
- **Vertical packs (paid settings files + service):** not in this repo; proprietary.
- Optional local models used by an adapter have their own separate license.

Full details: `LICENSING.md`.
