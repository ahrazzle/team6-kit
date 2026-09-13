# Artifact contract and resume/feedback handoff

> A handoff is a file, not a memory. Every stage boundary — producer to
> verifier, failed run to resumed run, reviewed work to regenerated work —
> carries one **artifact contract**: a small, machine-checkable record of what
> must exist, what state the runtime is in, and exactly what the next worker
> may and may not touch.
>
> **System of record:** Team6 Kanban remains the state authority. A contract
> file is a per-handoff snapshot written *out of* the Kanban record so a cold
> worker can resume without re-reading the whole board. It never replaces or
> overrides the Kanban task state; if the two disagree, Kanban wins and the
> contract is rewritten from it.
>
> **Provenance:** this is a Team6 internal operating record for artifact handoffs.
> It was designed to solve resume/feedback boundary issues in Kanban workflows.
> It is not derived from external code or documentation.

## Why

The failure modes this prevents are the ones `orchestration.md` already names —
in-context state lost on respawn (§4.2), producer self-reports (§7), resume vs
restart (§6) — but at the artifact level:

- A resumed worker re-does finished work or silently rewrites artifacts the
  reviewer already approved, because nothing recorded *what not to touch*.
- A "done" claim carries no evidence, so the verifier re-derives everything
  (§7 read-back receipts exist precisely to stop this).
- A feedback round is applied half-way: nobody can see which notes were
  consumed and which artifacts must be regenerated.
- Size and content bounds live only in prose, so a bloated or hollow artifact
  passes a human eye and fails the next stage.

The contract makes each of those a **checked field**, not a remembered norm.

## Format

Line-oriented, YAML-like, parseable with zero third-party dependencies (the
reference checker ships a minimal parser; a full YAML parser reads the same
file):

- Comments start with `#`.
- Section fields: `key: value` at column zero.
- Lists: `key:` followed by `- ` items; item fields are indented `name: value`
  lines belonging to the current item.
- Placeholders are curly-brace tokens (upper name in braces), the repository's
  template convention (see `templates/`); substitute them before the run
  fills the rest.

Copy `templates/contracts/artifact-contract.md.tmpl` as the starting shape.
Neutral fill-in examples: `examples/artifact-contract.valid.yaml` (passes) and
`examples/artifact-contract.invalid.yaml` (fails on a missing required field
plus an illegal enum value).

## Fields

Every required field must be present and non-empty; unknown keys fail, so a
typo in a required field is a failure, not a shrug.

| Field | Req | Rule |
|---|---|---|
| `contract_version` | yes | integer; `1` for this format |
| `task_id` | yes | identifier of the Kanban task this handoff came from (the pointer; Kanban stays authoritative) |
| `project` | yes | project name |
| `phase` | yes | phase that produced this handoff |
| `status` | yes | `completed` \| `partial` \| `failed` \| `blocked` |
| `runtime_state` | yes | `local` \| `staged` \| `live` — the deployment state of the work product, never inferred from prose |
| `last_stable_phase` | yes | phase whose output was last verified good; must name a `phase` listed under `expected_artifacts` |
| `resume_phase` | yes | where the next worker starts; must equal `last_stable_phase` or a later phase (forward-only) |
| `expected_artifacts` | yes (≥1) | the artifacts this handoff delivers or vouches for |
| `required_sections` | yes (≥1) | sections/markers each artifact must contain |
| `size_bounds` | yes (≥1) | byte bounds per artifact |
| `tests` | yes (≥1) | commands that must pass for the handoff to count as verified |
| `evidence_refs` | yes (≥1) | read-back evidence per §7: command/URL/receipt + what it proves |
| `failure_state` | required when `status: failed` or `blocked` | machine-state and human-state of the failure + remediation |
| `feedback_to_apply` | yes (may be empty) | reviewer notes with `applied: yes\|no\|n-a` |
| `artifacts_to_regenerate` | yes (may be empty) | what must be rebuilt because feedback changed it |
| `artifacts_not_to_touch` | yes (may be empty) | frozen set; any overlap with `artifacts_to_regenerate` is a hard error |

Per-item fields:

- **`expected_artifacts`** — `path` (required), `kind` (`file` \|
  `directory`, default `file`), `produced_by` (phase, optional).
- **`required_sections`** — `artifact` (required, must match an
  `expected_artifacts.path`), `section` (required), `marker` (optional exact
  string to grep).
- **`size_bounds`** — `artifact` (required, must match), `min_bytes` /
  `max_bytes` (at least one; positive integers, `K`/`M` suffixes allowed;
  `min_bytes` must not exceed `max_bytes`).
- **`tests`** — `name` (required), `command` (required).
- **`evidence_refs`** — `ref` (required), `proves` (required).
- **`failure_state`** — `machine_state` (required), `human_state` (required),
  `remediation` (optional).
- **`feedback_to_apply`** — `note` (required), `applied` (optional, enum).
- **`artifacts_to_regenerate`** / **`artifacts_not_to_touch`** — `path`
  (required).

## Validation rules (what the checker enforces)

1. Every required section/field present and non-empty.
2. Enums enforced: `status`, `runtime_state`, `applied`, `kind`.
3. A `failed` or `blocked` contract must carry `failure_state`.
4. `resume_phase` moves only forward from `last_stable_phase`.
5. Cross-references: every `artifact` name used by `required_sections` or
   `size_bounds` must exist in `expected_artifacts`.
6. The regenerate set and the do-not-touch set must be disjoint — the whole
   point of writing both down.
7. Size bounds are positive, bounded, and internally consistent.
8. Unknown fields fail (catches misspelled required fields).

## Using it

```
python3 build/check-artifact-contract.py path/to/handoff.yaml      # validate one contract
python3 build/check-artifact-contract.py --self-test               # run the repo's own pass/fail tests
```

Exit `0` = valid, `1` = invalid (each violation printed with its field).
The checker is dependency-free (Python 3 stdlib only, no network) and is
shipped in the generated kit under `contracts/` alongside this document, the
template, and the examples — in an instantiated team the checker is
`contracts/check-artifact-contract.py`. The template's placeholders resolve
through the same substitution path as every other kit template.

## Operating rules

- **Write the contract at the boundary, not after.** The producer fills it as
  the last act of the stage; the verifier checks it before checking the work.
- **Evidence or it didn't happen.** `evidence_refs` entries are verbatim
  read-backs (command + output handle), same bar as §7 receipts.
- **Runtime state is declared, never implied.** `local` vs `staged` vs `live`
  decides what the next stage may claim; served-truth (§10) applies.
- **Freeze first, then regenerate.** Anything approved and out of scope goes
  into `artifacts_not_to_touch` before the feedback round starts.
- **Keep it small.** The contract is a handoff, not a spec — bound the
  artifacts by size, bind every claim to a check.
