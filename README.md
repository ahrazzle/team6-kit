# Team6-kit — Multi-Agent Team Kit (open core)

Official project site: https://team6.askaconsult.com/

Team6-kit is an ASKA Digital open-source project. For the ASKA product and service context, visit https://askaconsult.com/digital/.

GitHub Pages mirror: https://ahrazzle.github.io/team6-kit/


> **What this is:** the reusable layer that turns a single agent engine into a
> *disciplined multi-agent team* - identity archetypes, orchestration
> choreography, governance rules, knowledge routing, and a generator that
> assembles them.
>
> **Why it's standalone, not a fork:** we build on Hermes (MIT) rather than
> vendoring it. That keeps the kit's boundary honest - the engine stays
> upstream and unmodified; everything this repo adds lives in its own licensed
> zones. You get the same credibility as a fork with none of the tree
> confusion: `Team6-kit` reads as a product, not a clone.

Instantiable multi-agent team: identity archetypes + orchestration choreography
+ governance rules + knowledge routing + a generator. One engine, two products.

```
team6-kit/
├── templates/          # persona archetypes (SOUL.md w/ {PLACEHOLDER}), profile.yaml, generic skills
│   └── MANIFEST.md     # row → template mapping + provenance (locked)
├── build/              # the ONLY assembly path
│   ├── generate.py         # manifest → instantiated kit
│   ├── sweep-gate.py       # precondition: source clean + fully classified
│   ├── review-gate.py      # semantic sign-off enforcement (4/4)
│   ├── extraction-inventory.py   # classifier + content sweep (source audit)
│   └── build-manifest.py         # manifest generator
├── registry/           # kit.yaml + vertical pack parameter files (NOT forks)
├── choreography/       # THE differentiator: orchestration, governance, funnel SOPs, local-preprocessing adapter contract
├── CHANGELOG.md        # dated per-upgrade log: what changed, why, evidence class
├── WHY.md              # design axioms + why the operating layer is shaped this way
└── LICENSE             # Apache-2.0 core; packs proprietary by contract
```

Read `choreography/orchestration.md` (how the team works together),
`choreography/governance.md` (the rules that keep it honest), and
`choreography/local-preprocessing.md` (the optional local preprocessing
adapter contract) first. `WHY.md` explains the operating layer; `CHANGELOG.md`
tracks what changed per release.

## The invariant

> Every *source* file ships only when it has a manifest verdict of TEMPLATE or
> KEEP-REVIEW with a signed REVIEW.md entry. Unclassified source = build
> failure. (Scope: extraction source - profiles being mined. The kit's own
> authored surfaces are out of scope by design.)

## Build sequence

```
1. python3 build/sweep-gate.py    # PASS(0) → continue; FAIL(1) → stop
2. python3 build/review-gate.py   # 4/4 checkboxes on every shipping row
3. python3 build/generate.py --out <kit-dir> [--params <pack.yaml>]
```

A kit that cannot be built by `build/` from `templates/` + a parameter file
does not exist. The generator is the only assembly path.

## Key skills in this release

- **knowledge-router** - MoE-style activation for persistent memory: tiny
  always-on router, compartmentalized knowledge modules loaded on demand.
  Solves the growing always-on memory footprint on bounded-context models.
- **zero-context-preservation** - the direct-execution pivot: preservation
  dumps + mechanical fleet work done in the shell at zero context cost;
  orchestrator preserves agent identity verbatim.

## Local preprocessing adapter (v1.2.0)

A **bounded, optional local preprocessing layer** that a generated
installation may apply around approved outbound work — Redact before approved
outbound text / durable external logs, Gist for bulk routing hints only, Title
for draft metadata. It is a **contract, not a provider/router replacement**: it
never handles high-stakes judgment and it never runs for ordinary conversation
or final synthesis. The public kit documents the contract
(`choreography/local-preprocessing.md`); a generated installation **implements**
it only as an explicit operator policy, and the kit never edits a user's Hermes
profile to enable it. Desert Ant is one possible implementation on macOS, not a
required dependency, and the models carry a separate vendor license distinct
from the Apache-2.0 kit layer. Expected benefits are stated as intended
outcomes — no fabricated performance or cost numbers.

## Operating upgrades in this release (v1.1.0)

The choreography and governance now encode the verified operating doctrine of
a supervised, durable, provenance-aware team. Highlights - full detail and
per-item "why" in `choreography/orchestration.md`, `choreography/governance.md`,
and `CHANGELOG.md`:

- **Erlang/OTP-style supervision** - workers do work; the orchestrator
  supervises and restarts under an explicit per-role task contract (restart
  type, intensity/period budget, shutdown policy, verification bar), escalating
  on budget exhaustion instead of retrying forever.
- **Supervised autonomous research loops** - ledgered, check-pointed research
  with exactly one mutable input, a frozen evaluator, keep/discard/crash
  advancement, and pause/interrupt points - *not* silent indefinite autonomy.
- **Phase-gated pipeline + corrected role sequence** - research → architecture
  → design → build → QA, each with a Definition-of-Done gate, Andon
  stop-the-line, and JIT stable-partial handoffs. The earlier duplicated
  9-step sequence (UX twice, an early QA/Scoper) is corrected to a single pass.
- **Producer/verifier separation** - the agent that produces an artifact never
  passes it; verdicts ground in read-back receipts, never self-reports.
- **Durable state & append-only ledgers** - correctness as a pure function of
  on-disk state, so a respawned worker resumes from disk, not dead context.
- **Five-minute live check-ins & stall recovery** - periodic progress beats
  silence-then-timeout.
- **Served-truth / staging-first verification** - verify what is actually
  served, not a local claim.

### Design axioms

1. **Entropy-proof.** Correct as a pure function of durable state - still
   correct on first read after months untouched. Absence is normal.
2. **Served-truth.** Verify the thing actually served/live; staging first,
   user approves, then promote. Never announce "live" from a local claim.
3. **Producer ≠ verifier.** No one passes their own work; read-back receipts,
   not self-reports.
4. **Supervised, not autonomous.** Long loops pause, checkpoint, and surface
   for review; nothing runs forever unattended.

## License

- **Built on Hermes (MIT)** - the engine is Nous Research's, MIT-licensed
  (provenance; engine-derived tooling becomes MIT when it lands here, see
  LICENSING.md). This repo is NOT a git-fork of Hermes; it is a standalone
  product with a generated kits layer.
- **Kits layer: Apache-2.0** (see LICENSE) - our identity archetypes,
  orchestration, governance, knowledge routing, and build tooling.
- **Vertical packs: proprietary by contract** - parameter files + service,
  never committed to this repo, never a fork of the engine.
- **Optional local preprocessing models: separate vendor license** — an
  adapter may reference models (e.g. Desert Ant) that carry their own
  source-available vendor license; that license governs the models and does
  not extend to this Apache-2.0 kit layer. See `LICENSING.md` and
  `choreography/local-preprocessing.md`.

See `LICENSING.md` for the full four-zone statement.

**Where Team6 lives (v1.2.0 public-domain decision):** the intended public
Team6 site is **https://team6.askaconsult.com** — the ASKA site team connects
the domain to this kit's GitHub Pages source. As a fallback/source mirror, the
kit's GitHub Pages build also serves at **https://ahrazzle.github.io/team6-kit/**
(the repo's existing Pages convention); the repo and source of truth remain
**https://github.com/ahrazzle/team6-kit**. The Team6 site links back to the ASKA
Digital site at **https://askaconsult.com/digital/**.

## Status

**1.2.0 — Local preprocessing adapter contract.** Documents a bounded, optional
local preprocessing layer (Redact / Gist / Title + opt-in media) as a
vendor-neutral adapter contract in `choreography/local-preprocessing.md`. It is
a contract, not a provider/router replacement; generated installations
implement it only as an explicit operator policy, and the kit never edits a
user's Hermes profile. Desert Ant is one optional implementation; its models
carry a separate vendor license distinct from the Apache-2.0 kit. See
`CHANGELOG.md`.

**1.1.0 — Operating upgrades.** Supervision model, supervised research loops,
phase-gated pipeline + corrected single-pass role sequence, producer/verifier
separation, durable append-only ledgers, adversarial QA gate, live check-ins,
served-truth/staging-first verification, and the entropy-proof + license/
provenance axioms - now encoded in `choreography/`. See `CHANGELOG.md`.

1.0.0 - first official release. Efficiency update (knowledge router +
zero-context preservation), renamed from airefea-kit to Team6-kit. Open-core
assembly gated (sweep + review + generate). See demo/ + examples/ for the
instantiation proof-point.