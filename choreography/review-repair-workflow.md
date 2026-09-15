# Guarded review / repair workflow contract

This contract adds a **proposal-only review report** and a **guarded repair
loop** to the kit's existing review surfaces (`github-pr-audit`,
`adversarial-review`, `code-review-verification`, `web-build-verification`). It
is a documentation and validation contract: the kit defines the report shape and
ships a dependency-free validator, but it runs no bot, opens no pull request, and
holds no merge authority.

It is adapted from two public conceptual sources as principles only — no code,
prompts, workflow YAML, or text is copied:

- **ClawSweeper** (`100yenadmin/clawsweeper`, MIT) — the review/repair contracts:
  a typed proposal-only review output that never dispatches a mutation itself,
  deterministic executor steps owning every GitHub mutation, exact-head
  re-review, and a bounded Codex review/fix loop.
- **gstack** (`100yenadmin/gstack`, MIT) — the workflow patterns: forcing
  questions before a plan, real-browser QA that generates a regression test for
  every fix, and a review-to-ship handoff that carries evidence forward.

## What this contract is not

- **Not a second GitHub control plane.** The report describes proposed
  maintainer actions; it executes none of them. The Team6 Kanban board remains
  the authoritative task record, and the human operator remains the only actor
  that approves a mutation.
- **Not a self-hosted bot.** No scheduler, webhook router, worker, or state
  branch is defined here.
- **Not a rename.** No Team6 or Protean surface is renamed, and no new
  slash-command name is introduced where the kit already has a canonical
  surface (`/review`, `/qa`, `/ship`, `/office-hours`, `/cso` stay unused as new
  names).

## The report

One JSON document records one review pass — a code review, an adversarial pass,
a browser verification, or an artifact verification. The `lane` field names
which. The validator is `build/review-repair/check.py`.

```json
{
  "contract_version": 1,
  "lane": "review",
  "target": {
    "repo": "owner/name",
    "live_head": "<40-hex commit sha>",
    "head_source": "how the live head was read (e.g. gh api ... -> sha)"
  },
  "steps": [
    {
      "id": "review-head",
      "action": "re-review the exact head",
      "head": "<same sha as target.live_head>",
      "evidence": [{"ref": "the command that produced this", "proves": "the claim it supports"}],
      "owner": "profile that owns the step",
      "rollback": "how this step is undone"
    }
  ],
  "review_output": {
    "verdict": "accept",
    "findings": [{"id": "F1", "severity": "high", "summary": "..."}],
    "mutations_performed": []
  },
  "proposed_mutations": [
    {
      "id": "M1",
      "kind": "comment",
      "target": "owner/name#123",
      "requires_approval": true,
      "approved_by": null,
      "rollback": "delete the comment"
    }
  ],
  "repairs": [
    {
      "id": "P1",
      "finding": "F1",
      "owner": "profile that owns the fix",
      "regression_test": {
        "name": "the case the fix pins",
        "command": "the command that runs it",
        "pre_fix_result": "fail",
        "post_fix_result": "pass"
      }
    }
  ]
}
```

## The rules (fail-closed)

| Rule | Rejects |
|---|---|
| R1 | a required field missing, empty, or of the wrong kind |
| R2 | a target head that is not a commit sha, a head source that is not stated, or a step bound to a different head (a stale head) |
| R3 | a step with no evidence ref, or evidence that does not say what it proves |
| R4 | a step or a repair with no owner |
| R5 | a step or a proposed mutation with no rollback path |
| R6 | a review output that reports a mutation as already performed (review is proposal-only) |
| R7 | a proposed mutation that is not explicitly approval-required, or whose kind is `merge`, `rename`, or a command name (no automatic merge authority, no rename, no duplicate slash-command name) |
| R8 | a repair with no regression-test contract, or one whose pre-fix result is not `fail` / post-fix result is not `pass` (a test that passes before the fix pins nothing) |
| R9 | an internal local path or a credential-like value anywhere in the report |
| R10 | an unknown top-level field (a typo'd required field fails loudly) |

## Why each rule exists

**R2 — bind to the live head.** A review of a diff captured earlier is a review
of code that may no longer be in the pull request. Every step names the live
head it was verified against, and every step's head must equal the one target
head. A mismatch is a stale review, not a review.

**R6 / R7 — separate the review from the mutation.** The reviewer proposes; a
deterministic, approval-gated actor disposes. A report that carries a performed
mutation is blending the two roles, which is exactly the "reviewer approved
their own change" failure. `merge` is never a proposal the agent may carry, so
automatic merge authority cannot be smuggled in.

**R8 — the regression-test contract.** Every repair names a test and states its
**pre-fix** and **post-fix** result. A test that passes both before and after is
a guard, not a pin; it does not prove the repair. The contract forces the
distinction the kit already teaches in `code-review-verification` (the
RED-check).

## How to use it

1. Run the review, adversarial pass, browser verification, or artifact check.
2. Write the report; binding every step to the live head.
3. Validate it: `python3 build/review-repair/check.py <report.json>`.
4. Hand the report to the operator. Proposed mutations run only after explicit
   approval.

The validator is standard-library only, requires no network or credentials, and
fails closed. Its self-test and fixture corpus run as part of
`build/verify-all.py`.
