# Demo — Instantiation Proof-Point

This directory holds the demonstration of the core contract:
**one parameter file → a configured team**, via `build/generate.py`.

## The proof-point

```bash
cp demo/demo-consulting.yaml /tmp/demo-consulting.yaml
python3 build/generate.py --params /tmp/demo-consulting.yaml --out /tmp/demo-team
```

Output: a configured team — personas (SOUL.md + profile.yaml templates
instantiated with the params values) + skills + a `keep-review/` surface
(signed KEEP-REVIEW rows) + an honest AUDIT.md (count == what's on disk
== what passed the gate).

The demo params use **fictional, neutral values** (Northwind Advisory,
Elena, nw-coder) — no instance data.

## Why it matters

This is the answer to "what does the kit provide over Hermes?" —
instantiation. `generate.py --params` turns a parameter file into a
configured team in one command, behind the fail-closed gates
(sweep-gate --kit-scope + review-gate + semantic pass + 8-surface matrix).
The audit's provenance invariant means what ships is what's counted and
what's signed — never a promise without an artifact.

## Regenerate

The output is reproducible by construction. Delete `/tmp/demo-team` and
re-run the command above — the same clean tree comes out, or the gates
refuse it and say why.
