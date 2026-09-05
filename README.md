# Team6-kit — Multi-Agent Team Kit (open core)

> **What this is:** the reusable layer that turns a single agent engine into a
> *disciplined multi-agent team* — identity archetypes, orchestration
> choreography, governance rules, knowledge routing, and a generator that
> assembles them.
>
> **Why it's standalone, not a fork:** we build on Hermes (MIT) rather than
> vendoring it. That keeps the kit's boundary honest — the engine stays
> upstream and unmodified; everything this repo adds lives in its own licensed
> zones. You get the same credibility as a fork with none of the tree
> confusion: `Team6-kit` reads as a product, not a clone.

Instantiable multi-agent team: identity archetypes + orchestration choreography
+ governance rules + knowledge routing + a generator. One engine, two products.

```
team6-kit/
├── templates/          # persona archetypes (SOUL.md w/ {PLACEHOLDER}), profile.yaml, generic skills
│   └── MANIFEST.md     # row → template mapping + provenance (locked)
├── choreography/       # THE differentiator: orchestration, governance, funnel SOPs
├── build/              # the ONLY assembly path
│   ├── generate.py         # manifest → instantiated kit
│   ├── sweep-gate.py       # precondition: source clean + fully classified
│   ├── review-gate.py      # semantic sign-off enforcement (4/4)
│   ├── extraction-inventory.py   # classifier + content sweep (source audit)
│   └── build-manifest.py         # manifest generator
├── registry/           # kit.yaml + vertical pack parameter files (NOT forks)
└── LICENSE             # Apache-2.0 core; packs proprietary by contract
```

## The invariant

> Every *source* file ships only when it has a manifest verdict of TEMPLATE or
> KEEP-REVIEW with a signed REVIEW.md entry. Unclassified source = build
> failure. (Scope: extraction source — profiles being mined. The kit's own
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

- **knowledge-router** — MoE-style activation for persistent memory: tiny
  always-on router, compartmentalized knowledge modules loaded on demand.
  Solves the growing always-on memory footprint on bounded-context models.
- **zero-context-preservation** — the direct-execution pivot: preservation
  dumps + mechanical fleet work done in the shell at zero context cost;
  orchestrator preserves agent identity verbatim.

## License

- **Built on Hermes (MIT)** — the engine is Nous Research's, MIT-licensed
  (provenance; engine-derived tooling becomes MIT when it lands here, see
  LICENSING.md). This repo is NOT a git-fork of Hermes; it is a standalone
  product with a generated kits layer.
- **Kits layer: Apache-2.0** (see LICENSE) — our identity archetypes,
  orchestration, governance, knowledge routing, and build tooling.
- **Vertical packs: proprietary by contract** — parameter files + service,
  never committed to this repo, never a fork of the engine.

See `LICENSING.md` for the full four-zone statement.

## Status

1.0.0 — first official release. Efficiency update (knowledge router +
zero-context preservation), renamed from airefea-kit to Team6-kit. Open-core
assembly gated (sweep + review + generate). See demo/ + examples/ for the
instantiation proof-point.