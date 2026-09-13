# Safe shareable run packet — validator

Standard-library-only checker for the safe shareable run packet contract in
`choreography/safe-run-packet.md`. It is documentation tooling: it performs no
network call, spawns no process, edits no file, and reads no credential. It runs
no operation — it checks that a run packet is complete and safe to share.

The Team6 Kanban board remains authoritative. A run packet is a derived,
shareable report, not a second state store; validating a packet never changes a
task's state.

## Run it

```bash
python3 build/report/check.py --selftest
python3 build/report/check.py fixtures/valid/local-doc-change.json
python3 build/report/check.py fixtures/invalid/*.json
```

Exit code `0` means every input is a shareable packet; `1` means at least one
input is invalid, unreadable, or not valid JSON. It fails closed.

## Fail-closed rules

| Rule | Rejects |
|---|---|
| R1 | a required field missing or of the wrong kind |
| R2 | an objective that is empty or not stated |
| R3 | a decision without its decision or rationale |
| R4 | evidence marked `verified: true` with no evidence behind it |
| R5 | a live/staged runtime status with no target or no evidence |
| R6 | unresolved items omitted (absent or `null`) — present-and-empty is allowed |
| R7 | an internal local path or profile path in the packet |
| R8 | a credential-like value anywhere in the packet |
| R9 | a placeholder that is not the repository convention (`{UPPER_SNAKE}`) |
| R10 | a test result without its result or the evidence behind it |
| R11 | incomplete provenance (who produced it, which run it describes) |
| R12 | a redaction status that is missing or not `clean` / `redacted` |

## Generic placeholders

The repository placeholder convention is a single upper-snake token in braces,
for example `{CLIENT}`, `{RELATIONSHIP}`, or `{PROFILES}`. Any other marker
(such as `«redacted»`, `<name>`, or `TODO`) is rejected, so an ad-hoc marker can
never stand in for a value the packet should have named or moved to unresolved.

## Fixtures

- `fixtures/valid/` — packets a reviewer should accept.
- `fixtures/invalid/` — one packet per rule, each of which must fail.

Add a fixture when you add a rule. The self-test (`--selftest`) exercises the
same rules in-process so the checker can be verified without the fixtures.
