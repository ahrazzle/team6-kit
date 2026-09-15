# Codebase-map snapshot contract (v1)

> A codebase map is a **snapshot artifact**, not a live view. This contract
> defines one small, machine-checkable JSON document that describes a
> file hierarchy as rectangles: area is a declared measure, color is a
> declared token, identity is a normalized relative path, and the child
> order is an explicitly declared policy. A viewer is downstream of the
> snapshot — the snapshot is the evidence object, the browser is only a
> projection of it.
>
> **Why a contract at all:** `choreography/artifact-contract.md` requires
> that state be written down, bounded, and read back rather than
> reconstructed from a worker's context or a hidden live process. If order,
> measure, algorithm, or filtering are left implicit, two producers mint two
> different maps from the same tree and neither is a trustworthy read-back.
> This contract makes each of those a **checked field**.
>
> **Provenance:** this is a fresh Team6 schema and validator. It is informed
> by the general treemap concept and the observed shape of a public
> code-visualizer's JSON example, but it copies no source, prose, fixture
> bytes, assets, or generated material. See `§ Rendering` for the enum
> provenance note. The result is authored-fresh and belongs to the
> Apache-2.0 kit layer.

## What a snapshot is (and is not)

A valid snapshot is evidence of **the captured snapshot only**. It does not
establish that any source repository is live, complete, dependency-free,
semantically correct, or representative. Area is a declared measure (bytes or
lines) — it is **not** importance, risk, quality, or business value. Color is
a display token — it is **not** a semantic grade. A snapshot whose
`source_kind` is `synthetic` is an authored fixture, not a repository capture.

## Format

One UTF-8 JSON object. No third-party parser is required: the reference
checker (`build/check-codebase-map.py`) is Python 3 stdlib only, and a browser
consumes the same bytes with `JSON.parse`.

```json
{
  "contract": "team6-codebase-map",
  "version": 1,
  "source_kind": "synthetic",
  "included_roots": ["app"],
  "excluded_patterns": ["**/__pycache__/**", "**/*.pyc"],
  "measure": "bytes",
  "sort": "lexical",
  "generated_at": "2026-09-15T00:00:00Z",
  "provenance": {
    "kind": "synthetic-fixture",
    "ref": "examples/codebase-map.valid.json",
    "note": "Authored fresh; not a live repository capture."
  },
  "rendering": { "algorithm": "t6-squarified-v1" },
  "tree": {
    "kind": "Node", "label": "app", "path": "",
    "children": [
      { "kind": "Leaf", "label": "README.md", "path": "app/README.md",
        "size": 1200, "color": "slate" }
    ]
  }
}
```

Neutral examples: `examples/codebase-map.valid.json` (passes) and
`examples/codebase-map.invalid.json` (fails on the deliberate violations
listed in `examples/README.md`).

## Top-level fields

Every required field must be present and non-empty; unknown keys fail, so a
typo in a required field is a failure, not a shrug.

| Field | Req | Rule |
|---|---|---|
| `contract` | yes | string; must equal `team6-codebase-map` |
| `version` | yes | integer; `1` for this format (no other value is accepted) |
| `source_kind` | yes | `synthetic` \| `repository-snapshot` — what produced the tree |
| `included_roots` | yes (≥1) | non-empty list of normalized relative root paths that were included |
| `excluded_patterns` | yes (may be empty) | list of glob strings that were skipped (submodules, generated files, vendored trees). An explicit empty list states "nothing was excluded" — it is not left implied |
| `measure` | yes | `bytes` \| `lines` — the unit every leaf `size` is expressed in |
| `sort` | yes | `lexical` \| `size-desc` \| `size-asc` — the declared deterministic child-ordering policy. An undeclared policy fails |
| `generated_at` | yes | string capture marker (the moment the tree was read) |
| `provenance` | yes | object: `kind` (required), `ref` (required), `note` (optional) — the evidence reference for the snapshot |
| `rendering` | yes | object: `algorithm` (required) — see `§ Rendering` |
| `tree` | yes | the root entity (must be a `Node`) |

## Tree grammar

Each entity is an object with a `kind` of `Node` or `Leaf`.

| Entity | Fields | Rules |
|---|---|---|
| `Node` | `kind`, `label`, `path`, `children` | `children` is a **non-empty** array of `Node`\|`Leaf`. An empty directory is **omitted** from v1 (recorded here as a deliberate omission) — so a `Node` with `children: []` is invalid, not an empty folder |
| `Leaf` | `kind`, `label`, `path`, `size`, `color` | `size` is a non-negative **integer** in the declared `measure`; `color` is a controlled token (below) or the explicit `unknown` value |

- **`label`** — display text, non-empty string. It is rendered as text and must
  never be interpreted as markup.
- **`path`** — the normalized relative identity. For the root entity it is the
  empty string `""`; for every other entity it is a non-empty relative path.
  Absolute paths, `~`-paths, drive letters, backslashes, `..` traversal, and
  duplicate identities are invalid.
- **`color`** — one of `blue`, `green`, `amber`, `slate`, `violet`, `red`, or
  the explicit `unknown`. `unknown` means the producer had no token; it is
  never silently defaulted to a color.

## Validation rules (what the checker enforces)

1. The document parses as JSON and is a single object.
2. Every required top-level field is present and non-empty.
3. `contract` equals `team6-codebase-map`; `version` is the integer `1`.
4. Enums enforced: `source_kind`, `measure`, `sort`, `rendering.algorithm`,
   leaf `color`. An unknown enum value fails.
5. `sort` is declared — an undeclared ordering policy fails.
6. Tree grammar: every entity's `kind` is `Node` or `Leaf`; every `Node` has a
   non-empty `children` array; every `Leaf` has a non-negative integer `size`
   (floats, negatives, and booleans fail) and a valid `color` token.
7. Path identity: relative and normalized as above; the root is `""`; no two
   entities share a `path`.
8. `included_roots` entries are normalized relative paths.
9. Unknown fields fail at every level (top-level, entity, `provenance`,
   `rendering`).

Exit `0` = valid, `1` = invalid (each violation printed with its field path).

## Using it

```
python3 build/check-codebase-map.py examples/codebase-map.valid.json   # validate one snapshot
python3 build/check-codebase-map.py examples/codebase-map.invalid.json # a deliberate failure
python3 build/check-codebase-map.py --self-test                        # the repo's own pass/fail cases
```

The checker is dependency-free (Python 3 stdlib only, no network, no writes)
and reads only the snapshot path it is given.

## Operating rules

- **Snapshot, not a live view.** Never label a map "live" unless a verified
  live source and an explicit update mechanism exist. Version 1 has neither.
- **Declare, do not imply.** `measure`, `sort`, `included_roots`,
  `excluded_patterns`, and `algorithm` are all written down; a reader must not
  have to guess them.
- **Source-bounded.** Absolute paths, home-directory paths, profile names,
  credentials, and raw source contents are invalid in a snapshot. The map is
  metadata-only.
- **Fail closed.** An invalid snapshot renders as a visible error, never a
  silently partial map.
- **Evidence, or it did not happen.** A snapshot receipt names the fixture
  hash, algorithm, viewport, and rectangle count, the same read-back bar as
  `choreography/run-evidence.md`.

## Rendering

`rendering.algorithm` is a required named field; a viewer that meets an
unrecognized token must reject it rather than fall back to a default. Version 1
defines exactly one accepted token:

| Token | Meaning |
|---|---|
| `t6-squarified-v1` | The Team6 baseline for the first proof. The token is a fresh, clean-room Team6 name. Its selection rationale, behavior, and the geometry receipt fields are recorded in the Slice 2 extension of this section. |
