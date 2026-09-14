# Execution-Evidence Contract

## Purpose

This document defines a vendor-neutral contract for recording execution evidence: what an agent actually executed, not only that a procedure ran.

## Evidence Record Contract

An evidence record contains the following fields:

| Field | Required | Description |
|-------|----------|-------------|
| `run_id` | Yes | Stable identifier for the execution run |
| `phase` | Yes | Current phase in the pipeline (research, architecture, design, build, QA, report) |
| `parent_run_id` | Optional | Run ID of parent execution (for nested/child runs) |
| `child_run_ids` | Optional | Array of child run IDs |
| `step_kind` | Yes | Type of step (tool_call, api_call, file_op, reasoning, verification) |
| `tool_identifier` | Optional | Tool/library name where safe (no credentials/instance tokens) |
| `model_identifier` | Optional | Model used where safe (vendor-neutral reference) |
| `start_timestamp` | Yes | ISO 8601 timestamp |
| `end_timestamp` | Yes | ISO 8601 timestamp |
| `status` | Yes | One of: completed, failed, partial, skipped |
| `artifact_refs` | Optional | Array of references to artifacts produced |
| `unresolved_items` | Optional | Array of items requiring follow-up |
| `evidence_boundary` | Yes | Scope of evidence collected (see below) |

## Evidence Types

### Procedure Evidence

Records what execution steps were performed. Includes tool calls, API invocations, and file operations. A command exit code alone is insufficient to prove achievement.

### Achieved-State Evidence

Records that a specific state was achieved. Requires read-back verification (e.g., grep count, checksum, config query) rather than self-report. Producer ≠ verifier: the agent that produces an artifact does not pass it.

## Token Accounting

Only innermost token-bearing spans are counted. Wrapper spans and their children must not both be summed to avoid double-counting.

- Count leaves only (token-bearing spans with no token-bearing descendants)
- Maintain a `dropped` counter when spans exceed capacity

## Cost Honesty

Use a dated, explicit model-price table. Unknown models must remain unknown and are never priced as zero.

- Record the date of the price table
- If a model is not in the table, mark cost as "unknown"
- Never guess or infer prices

## Run Comparison

Step alignment uses a stable key based on `kind + tool/name`. Model changes appear as "changed", not "removed + added".

- LCS with bounded greedy fallback for large traces
- Exclude model from step key to avoid artificial diffs

## Retention and Privacy

- Bounded storage with configurable span limits
- `dropped` counter visible when drops occur
- Metadata-first defaults
- No secrets or raw prompts stored by default
- Loopback/local guidance for any services (no 0.0.0.0 binding)

## Acceptance Checklist

For any implementation of this contract:

- [ ] Evidence record contains all required fields
- [ ] Procedure and achieved-state evidence are distinguishable
- [ ] Token accounting counts only innermost spans
- [ ] Unknown models are not priced as zero
- [ ] Step keys are stable across model changes
- [ ] Retention is bounded with visible dropped count
- [ ] No secrets or raw prompts in default configuration
- [ ] Loopback-only for local services

## Example Record

```json
{
  "run_id": "2026-09-13-team6-run-001",
  "phase": "build",
  "step_kind": "tool_call",
  "tool_identifier": "code_editor",
  "start_timestamp": "2026-09-13T10:15:00Z",
  "end_timestamp": "2026-09-13T10:17:30Z",
  "status": "completed",
  "artifact_refs": ["team6-kit-wrk/build/generate.py"],
  "unresolved_items": [],
  "evidence_boundary": "single-step"
}
```

---

This contract is Apache-2.0 licensed (Team6-kit core). It defines vendor-neutral rules and is not tied to any specific implementation or vendor.
