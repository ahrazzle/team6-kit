# Safe shareable run packet

> Generic operating guidance. This document describes a reviewable operating
> pattern. It is a conceptual contract, not a copied implementation: it is not
> copied Agency Orchestrator code and it bundles no third-party source,
> prompts, or dependencies. It is documentation only.

When a run finishes, the people who need to know about it are usually not at
the terminal that ran it. A **run packet** is the one artifact that travels:
a compact, self-contained report of what was attempted, what was decided, what
is actually verified, what is still open, what changed, how it was tested,
whether anything reached a live surface, and what happens next.

The packet exists to be **shared** — pasted into a review, attached to a PR,
handed to a different team. That is exactly why it must be safe to share: it
carries no secret, no credential value, no internal local path, and no private
profile identity. A packet that leaks its own context is worse than no packet.

The packet is **derived**, not authoritative. Team6's Kanban board remains the
authoritative record of task state, ownership, and outcome. A run packet is a
shareable **report** derived from that record plus the run's own evidence; it
is **not a second state store**, and writing or approving a packet never
changes a task's state. When the packet and the board disagree, the board is
right.

## Required fields

One packet describes exactly one run. All of the following are required; an
empty value is a missing value, and an omitted field is a failure — there is no
"unknown because I forgot".

1. **Objective** — a one-line statement of the concrete outcome the run set out
   to produce, not a vague intent.
2. **Decisions** — every decision the run made, each with its rationale. An
   empty list is a positive claim that the run made no decision.
3. **Verified evidence** — the claims the run is asserting, each marked with
   its verification state. A claim may be marked verified **only** when it
   carries the evidence that verifies it (a command, a read-back, a source, an
   observation). A claim that is not verified must be marked unverified, never
   upgraded by optimism.
4. **Unresolved items** — everything still open, unknown, or needing a human.
   **The field is always present**; an empty list is a positive claim that
   nothing is open. Omitting the field is a failure, not a shortcut.
5. **Changed artifacts** — every path the run created, edited, or deleted. An
   empty list asserts no artifact changed.
6. **Test results** — each check the run actually exercised, with its observed
   result and the output or signal behind it. "Not run" is stated, not implied.
7. **Runtime / live status** — whether the change reached any live or staged
   surface. When it did, the **target** and the **evidence** are required; a
   live claim with no target or no evidence is rejected.
8. **Next gate** — the concrete next checkpoint: the review, approval, publish,
   or verification step the run hands off to.
9. **Provenance** — where the packet came from: the packet's own identity and
   the run it describes. Provenance is stated generically (a role and a task
   reference), never as an internal local path or a personal profile name.
10. **Redaction status** — whether the packet was checked for shareable-surface
    safety, and how. A packet that has not been through a redaction check is not
    ready to share.

## Fail-closed rules

The packet **fails closed**: a single missing or disallowed item blocks the
packet from being shared. In particular the validator must reject:

- a required field that is missing, empty, or of the wrong shape;
- a claim marked **verified** that carries no verifying evidence;
- a **live or staged** runtime status with no target or no evidence;
- an **omitted** unresolved-items field (present-and-empty is allowed; absent is
  not);
- an **internal local path**, an **internal profile identity**, or a
  **credential-like value** anywhere in the packet;
- a placeholder that is not written in the repository's generic-placeholder
  convention.

### Generic placeholders

When a packet must stand in for something it cannot name, it uses the
repository's placeholder convention: a single upper-snake token in braces, for
example `{CLIENT}`, `{RELATIONSHIP}`, or `{PROFILES}`. Any other placeholder
shape is rejected, because an ad-hoc marker such as `«redacted»`, `<name>`, or
`TODO` is an unverified guess wearing a costume. A placeholder is a permit to
abstract, never a licence to hide a real value.

### Shareable-surface safety

A packet is written to be read by people outside the run. It therefore carries
**no** absolute local filesystem path, **no** internal host/profile directory,
and **no** credential, token, or secret-looking value. Credentials appear as
environment-variable **names** at most, never as values. If a value cannot be
named safely, it is replaced by a convention placeholder or the item moves to
unresolved.

## What this is not

- Not runtime integration. This contract adds no code path, provider call,
  network call, or configuration change. The accompanying validator
  `build/report/check.py` only reads and checks a packet; it performs no side
  effect.
- Not a copy of another tool. The pattern is derived conceptually from the idea
  of an agency-orchestration run report; no Agency Orchestrator source code,
  prompt, or dependency is copied or bundled.
- Not the source of truth. The Team6 Kanban board records task state and
  outcomes; the packet is a derived shareable report, not a second state store,
  and never replaces the board.

## Related

- Validator and fixtures: `build/report/` (`check.py`, `fixtures/valid/`,
  `fixtures/invalid/`).
- Side-effect and cost preflight: `choreography/side-effect-cost-preflight.md`.
