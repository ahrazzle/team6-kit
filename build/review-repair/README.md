# Guarded review / repair workflow — validator

Standard-library-only checker for the guarded review/repair workflow contract in
`choreography/review-repair-workflow.md`. It is documentation tooling: it
performs no network call, spawns no process, edits no file, opens no pull
request, and holds no merge authority. It runs no operation — it checks that a
review report is a bound, evidenced, owned, rollback-safe, and proposal-only
record.

The Team6 Kanban board remains authoritative. A review report is a derived
record, not a second state store; validating a report never changes a task's
state, and the report executes no mutation.

## Run it

```bash
python3 build/review-repair/check.py --selftest     # in-process cases
python3 build/review-repair/check.py --fixtures     # the fixture corpus
python3 build/review-repair/check.py fixtures/valid/review-report.json
python3 build/review-repair/check.py fixtures/invalid/*.json
```

Exit code `0` means every input is a valid proposal-only report; `1` means at
least one input is invalid, unreadable, or not valid JSON. It fails closed.

## The lanes

One report records one review pass. `lane` names which surface produced it:

- `review` — a code/diff review (`github-pr-audit`, `code-review-verification`)
- `adversarial` — a stress-test / hostile-reading pass (`adversarial-review`)
- `browser` — a real-browser or live-surface verification
  (`web-build-verification`)
- `artifact` — an artifact-contract / deploy-artifact verification

Every lane is validated by the same nine rules; the lane only names the surface.

## Fail-closed rules

| Rule | Rejects |
|---|---|
| R1 | a required field missing, empty, or of the wrong kind |
| R2 | a target head that is not a commit sha, a head source that is not stated, or a step bound to a different head (a stale review) |
| R3 | a step with no evidence ref, or evidence that does not say what it proves |
| R4 | a step or a repair with no owner |
| R5 | a step or a proposed mutation with no rollback path |
| R6 | a review output that reports a mutation as already performed (review is proposal-only) |
| R7 | a proposed mutation that is not explicitly approval-required, or whose kind is `merge`, `rename`, or a command name (no automatic merge authority, no rename, no duplicate slash-command name) |
| R8 | a repair with no regression-test contract, or one whose pre-fix result is not `fail` / post-fix result is not `pass` |
| R9 | an internal local path or a credential-like value anywhere in the report |
| R10 | an unknown top-level field (a typo'd required field fails loudly) |

## Fixtures

- `fixtures/valid/` — one report per lane (review, adversarial, browser,
  artifact) plus a clean-approve report with no findings, each of which must
  pass.
- `fixtures/invalid/` — one report per rule, each of which must fail.

Add a fixture when you add a rule. The self-test (`--selftest`) exercises the
same rules in-process, so the checker can be verified without the fixtures.
