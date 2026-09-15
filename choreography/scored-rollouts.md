# Grouped scored-rollout contract

> A scored rollout is an artifact, not a service. This contract gives a future
> Team6 evaluation or post-training adapter one stable, inspectable file that
> holds a run of scored samples grouped for comparison — without adopting an
> environment API, a rollout coordinator, a trainer, a tokenizer, or a model
> server.
>
> **Scope:** contract and local validator only. Team6-kit does not perform RL
> training, compute advantages, decode tokens, or run an inference server. The
> contract does not claim that Team6 currently does any of those.
>
> **Provenance:** the grouped-scoring, evaluation-handling, off-policy, and
> allocation semantics were adopted as a *conceptual source* from the archived
> `NousResearch/atropos` project (MIT). **No Atropos source, dependency,
> prompt, default, service, or trainer is copied.** The enum values
> `STOP_TRAIN`, `LIMIT_TRAIN`, and `NONE` are Team6 contract values, not an
> Atropos import or runtime dependency. See `LICENSING.md`.

## Why

A future evaluation or post-training adapter needs a common shape for "a run
of scored samples, several per group." Writing that shape down as a checked
file format means the producer and the reviewer agree on the boundary before
any runtime exists:

- Every group is the **unit of comparison**, so a group is exactly
  `group_size` samples with indexes `0..group_size-1` — no silent short group.
- Scores, token arrays, masks, and log-probability arrays carry explicit
  length and finite-value rules, so a malformed sample fails loudly instead of
  skewing a comparison.
- Evaluation handling and off-policy limits are **recorded and validated as
  metadata**. The kit does not enforce them at runtime in this slice.
- Raw prompts and message transcripts are **not fields**, and `input_ref` is an
  opaque reference — the contract never becomes a place where prompt text is
  copied.

## Format

JSON Lines (`.jsonl`). Every non-empty line is one JSON object. Duplicate JSON
keys are invalid.

- **Line 1** is a run header (`record_type: run`).
- **Then**, for each group in order: one group declaration
  (`record_type: group`) followed by exactly `expected_samples` sample records
  (`record_type: sample`).

Copy `templates/contracts/scored-rollout-group.jsonl.tmpl` as the starting
shape. Neutral examples: `examples/scored-rollout-group.valid.jsonl` (passes)
and `examples/scored-rollout-group.invalid.jsonl` (fails on an invalid
evaluation-policy combination plus a structural group-cardinality violation).

## Run header fields

| Field | Rule |
|---|---|
| `record_type` | required literal `run` |
| `schema` | required literal `team6.scored_rollout/v1` |
| `run_id` | non-empty string; an artifact identifier, not a credential |
| `mode` | `train` or `eval` |
| `group_size` | positive integer |
| `max_token_length` | positive integer — a contract bound, not a tokenizer setting |
| `eval_handling` | `STOP_TRAIN`, `LIMIT_TRAIN`, or `NONE` |
| `eval_limit_ratio` | `null` except for `LIMIT_TRAIN`, where it is a finite number greater than `0` and at most `1` |
| `batch_size` | positive integer or the literal `runtime` |
| `max_offpolicy_batches` | non-negative integer; zero means no off-policy samples are allowed |

## Group declaration fields

| Field | Rule |
|---|---|
| `record_type` | required literal `group` |
| `run_id` | must equal the header `run_id` |
| `group_id` | non-empty unique string |
| `expected_samples` | must equal the header `group_size` |
| `min_batch_allocation` | `null` or a finite number from `0` through `1`; the sum across group declarations must not exceed `1` |

## Sample fields

| Field | Rule |
|---|---|
| `record_type` | required literal `sample` |
| `run_id` | must equal the header `run_id` |
| `group_id` | must reference a declared group, and the sample must follow that declaration |
| `batch_id` | non-empty string; used to count off-policy batches |
| `sample_index` | integer, unique within the group, exactly the range `0..group_size-1` after validation |
| `input_ref` | non-empty opaque reference; must not contain the input prompt or transcript |
| `is_off_policy` | required boolean |
| `tokens` | required non-empty array of non-negative integers, length at most `max_token_length` |
| `mask` | required array containing only `0` or `1`, same length as `tokens` |
| `score` | required finite JSON number |
| `advantages` | `null` or an array of finite numbers, same length as `tokens` |
| `inference_logprobs` | `null` or an array of finite numbers, same length as `tokens` |
| `reference_logprobs` | `null` or an array of finite numbers, same length as `tokens` |

## Validation rules (what the checker enforces)

1. Missing or non-first header fails; a second run header fails.
2. Unknown header, group, and sample fields fail.
3. Duplicate keys fail.
4. Groups: unique `group_id`, `run_id` match, `expected_samples` equals
   `group_size`, exactly that many samples, sample indexes unique and covering
   `0..group_size-1`.
5. Samples: undeclared group fails; array lengths must match `tokens`;
   non-finite values in `score`, `advantages`, `inference_logprobs`, or
   `reference_logprobs` fail; `tokens` length must not exceed
   `max_token_length`.
6. Evaluation policy: `eval_limit_ratio` is `null` except for `LIMIT_TRAIN`,
   where it must be a finite number in `(0, 1]`.
7. Off-policy cap: more distinct off-policy `batch_id` values than
   `max_offpolicy_batches` fails; any off-policy sample when the cap is `0`
   fails.
8. Allocation minima: the sum across group declarations must not exceed `1`.

The checker does **not** decode tokens, infer prompts, calculate advantages,
normalize scores, or decide whether a score is good. Those are future adapter
responsibilities.

## Using it

```
python3 build/check-scored-rollout.py path/to/artifact.jsonl   # validate one file (repo path)
python3 build/check-scored-rollout.py --self-test              # repo pass/fail tests
python3 build/check-scored-rollout.py --example-check          # repo examples

# From inside a generated kit:
python3 contracts/check-scored-rollout.py path/to/artifact.jsonl
python3 contracts/check-scored-rollout.py --self-test
```

Exit `0` = valid, `1` = invalid (each violation printed with its line number
and field). The checker is dependency-free (Python 3 stdlib only, no network)
and ships under `contracts/` in the generated kit alongside this document, the
template, and the examples. The template's placeholders resolve through the
same substitution path as every other kit template.
