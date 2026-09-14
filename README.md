# Team6-kit

Turn one AI agent engine (Hermes, from Nous Research) into a small team of AI agents that work together under clear rules — with a supervisor, a quality checker, and a builder that assembles your own team from ready-made parts.

Official site: https://team6.askaconsult.com/
Part of ASKA Digital: https://askaconsult.com/digital/

Interactive experience: https://www.askaconsult.com/team6

The official site is the canonical public documentation for Team6-kit. The
interactive experience is served by the Team6 Frontier Vercel project through
ASKA's `/team6` route.

## What problem does it solve?

One AI agent can lose track, skip steps, or claim work is done when it isn't. Team6-kit sets up several agents with separate jobs — planner, builder, checker — and rules so that:

- Work is checked by a different agent than the one that did it.
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

## Execution evidence

The kit defines a vendor-neutral execution-evidence contract that records what
an agent actually executed, not only that a procedure ran. It specifies evidence
record fields, distinguishes procedure evidence from achieved-state evidence,
and establishes rules for token accounting (innermost spans only), cost honesty
(unknown models remain unknown), run comparison with stable step keys, and
bounded retention with no secrets or raw prompts by default.
Read `choreography/run-evidence.md`.

## The main rules

1. **Everything on disk.** Progress is saved to files, so months later you can still pick up where you left off.
2. **Check what is actually live.** Test on a staging copy, get approval, then publish. Never announce "done" from a local test.
3. **The maker never marks their own work.** A different agent checks it and records the result.
4. **Supervised, not autonomous.** Long tasks pause, save progress, and ask for review. Nothing runs forever unattended.

For work performed with an AI coding agent, use the compact
`choreography/ai-assisted-development.md` contract. It adds behavior-first
testing, security checks, scope control, and evidence requirements without
replacing the Team6 ownership and QA gates.

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
