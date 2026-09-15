# Declarative reward catalogue

> A reward catalogue is a **declared inventory**, not an executor. It names
> reward identities, their declared behaviour, and the samples they may later
> consume — and it is validated before use, so a typo or an unsafe field fails
> loudly. It never imports, evaluates, or runs the implementation it names.
>
> **Scope:** metadata and a local validator only. Team6-kit does not ship a
> reward loader, a decorator factory, a plugin, or any runtime that executes a
> named reward. A future adapter must be a separate architecture decision.
>
> **Provenance:** the reward-registry qualities adopted here — stable
> identifiers, explicit registration metadata, and validation before use —
> were adopted as a *conceptual source* from the archived `NousResearch/atropos`
> project (MIT). **No Atropos source, dependency, decorator, or code is
> copied.** See `LICENSING.md`.

## Why

Naming a reward in code (a decorator, an import path, a registry factory)
creates an execution and import boundary. Team6-kit does not own that boundary
yet, and a runtime loader would make the catalogue a code surface instead of a
review surface. A declarative catalogue keeps the useful part — a stable name
and an explicit declaration a reviewer can check — and defers the executable
part to a real Team6 trajectory task with an owner and a runtime boundary.

The catalogue also makes the boundary explicit: it records score ranges but
does **not** define aggregation, weighting, calibration, or reward-hacking
defenses, and it does **not** promise that a named reward is implemented.
`source: pending-verification` means the catalogue is not evidence that an
implementation exists.

## Format

The catalogue uses a restricted, dependency-free, YAML-like, line-oriented
shape read by the shipped checker's own minimal parser. No third-party YAML
library is imported. Copy `registry/reward-functions.yaml.example` as the
starting shape.

```yaml
version: 1
rewards:
  - id: exact_match
    description: compare a scored answer with an expected answer
    input: scored_rollout_sample
    output: scalar
    min_score: 0
    max_score: 1
    deterministic: true
    modes: train,eval
    implementation_ref: project-local
    source: operator-documentation
```

## Entry fields

Every reward entry must contain exactly these fields:

| Field | Rule |
|---|---|
| `id` | unique lower snake case identifier matching `^[a-z][a-z0-9_]{1,63}$` |
| `description` | non-empty generic description; must not contain a prompt, credential, or local path |
| `input` | required literal `scored_rollout_sample` |
| `output` | required literal `scalar` |
| `min_score`, `max_score` | finite numbers with `min_score <= max_score` |
| `deterministic` | required `true` or `false` |
| `modes` | non-empty comma-separated set containing only `train` and/or `eval` |
| `implementation_ref` | non-empty opaque reference; documentation, not an import path and not executable |
| `source` | non-empty provenance reference or `pending-verification` |

The top level must contain `version: 1` and at least one `rewards` entry.

## Validation rules (what the checker enforces)

1. Unknown top-level and entry fields fail.
2. Duplicate IDs and duplicate keys fail.
3. Missing required fields fail.
4. Identifiers must match the lower-snake-case shape.
5. Malformed booleans (`true`/`false` only) or numbers fail.
6. Empty descriptions fail; a description carrying a credential-like value or a
   local path fails.
7. Invalid modes fail.
8. Reversed score ranges fail.
9. **Executable hook fields fail** — `callable`, `entrypoint`, `python`, and
   `command` are never valid, and an `implementation_ref` shaped like an import
   path (`module.attr`, a file path, or a `.py` name) fails.
10. Raw credential-like values fail.

## Using it

```
python3 build/check-reward-registry.py registry/reward-functions.yaml   # validate one file
python3 build/check-reward-registry.py --self-test                     # repo pass/fail tests
python3 build/check-reward-registry.py --example-check                 # repo examples
```

Exit `0` = valid, `1` = invalid (each violation printed with its location and
field). The checker is dependency-free (Python 3 stdlib only, no network).

The catalogue is a kit-level registry example, not per-agent persona content.
It stays at `registry/reward-functions.yaml.example` in the source repository;
the kit does **not** copy it into generated kits (the kit ships no executable
reward registration code). The neutral examples are
`examples/reward-functions.valid.yaml` and `examples/reward-functions.invalid.yaml`.
