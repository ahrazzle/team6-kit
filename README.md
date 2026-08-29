# airefea-kit — Multi-Agent Team Kit (open core)

Instantiable multi-agent team: identity archetypes + orchestration choreography
+ governance rules + a generator. One engine, two products.

```
airefea-kit/
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

## License

- Open core: Apache-2.0 (see LICENSE).
- Vertical packs: proprietary by contract — parameter files + service, never
  a fork of the engine.

## Status

0.1.0 — skeleton assembled against the locked manifest (126 TEMPLATE rows,
111 KEEP-REVIEW, 99 DROP). Gates verified. Semantic pass pending on 229 rows;
nothing assembles until sign-off.
