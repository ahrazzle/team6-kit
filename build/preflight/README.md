# Side-effect and cost preflight — validator

Standard-library-only checker for the side-effect / cost preflight contract in
`choreography/side-effect-cost-preflight.md`. It is documentation tooling: it
performs no network call, spawns no process, edits no file, and reads no
credential. It runs no operation — it checks that an operation's *description*
is complete and safe to review.

## Run it

```bash
python3 build/preflight/check.py --selftest
python3 build/preflight/check.py fixtures/valid/local-doc-edit.json
python3 build/preflight/check.py fixtures/invalid/*.json
```

Exit code `0` means every input is valid; `1` means at least one input is
invalid, unreadable, or not valid JSON. It fails closed.

## Fail-closed rules

| Rule | Rejects |
|---|---|
| R1 | a required field missing, empty, or of the wrong kind |
| R2 | an incomplete operation identity (missing id or summary) |
| R3/R4 | a credential carried as a value or non-env-var-name shape |
| R5 | a secret-looking token anywhere in the document |
| R6 | a wait/timeout that is missing, unbounded, or non-finite |
| R7 | a side-effecting operation with no rollback path (or unbounded rollback) |
| R8 | a paid operation without an approved owner state |
| R9 | a conditional action not explicitly marked `may_run` |
| R10/R11 | an unknown cost/quantity that is not made explicit, or a missing/negative quantity |

## Fixtures

- `fixtures/valid/` — documents a reviewer should accept.
- `fixtures/invalid/` — one document per rule, each of which must fail.

Add a fixture when you add a rule. The self-test (`--selftest`) exercises the
same rules in-process so the checker can be verified without the fixtures.
