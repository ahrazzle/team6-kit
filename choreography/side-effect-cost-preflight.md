# Side-effect and cost preflight

> Generic operating guidance. This document describes a reviewable operating
> pattern. It is a conceptual contract, not a copied implementation: it is not
> copied Agency Orchestrator code and it bundles no third-party source,
> prompts, or dependencies. It is documentation only.

Before an operation runs, a reviewer should be able to read one document and
know exactly what it will touch, what it will spend, what it needs, and how to
undo it. This preflight is that document. It covers any operation that may
**edit files, contact an external system, use a credential, incur a paid
operation, affect a public surface, or require rollback** — the ordinary shape
of a build, deploy, migration, or data job.

The goal is a description a second person can approve or reject without asking
the author a follow-up question, and without reading source code. If the
preflight is incomplete, the operation is not ready to run.

Team6's Kanban board remains the authoritative record of task state, ownership,
and outcome. This preflight is a review aid that travels with a task; it does
not replace the board, and approving a preflight does not change a task's
state.

## Required fields

One document describes exactly one operation. All of the following are
required; an empty value is a missing value.

1. **Operation identity** — a stable `id` and a one-line `summary` naming the
   concrete change in behaviour, not a vague intent.
2. **Files to change** — every path the operation creates, edits, or deletes.
   An empty list is a positive claim that no file changes.
3. **External systems / endpoints** — every host, service, or remote the
   operation contacts, with a purpose. "None" is an explicit empty list, never
   an omission.
4. **Credentials required** — environment-variable **names only** (for
   example `SERVICE_TOKEN`). Values are forbidden anywhere in the document.
5. **Paid operations** — every operation that costs money, with its cost unit.
   An empty list is a claim that nothing paid runs.
6. **Estimated quantity / cost units** — the expected amount and its unit. If
   the amount is genuinely unknown, write `unknown` **and** give a conservative
   basis. Never invent a quota or a number you cannot justify.
7. **Conditional actions** — every step allowed to run, or not run, depending
   on a condition, each explicitly marked `may_run: true` or `may_run: false`.
   An action that might run must never be left unmarked.
8. **Public surfaces** — anything a stranger could observe after the operation
   (a published site, a public repository, a released artifact). An empty list
   asserts nothing becomes public.
9. **Rollback / recovery path** — the concrete way to undo the change, and an
   explicit bound on how long recovery may wait. A side-effecting operation
   with no rollback path is not ready.
10. **Owner / approval state** — the named owner and the approval state
    (`approved`, `pending`, `not-required`, `rejected`). A paid operation
    requires an `approved` owner.
11. **Explicit unknowns** — the list of things this operation does not know. An
    empty list is a claim that nothing is left open; write it empty only when
    that is true.

## Fail-closed rules

The preflight **fails closed**: a single missing or disallowed item blocks the
operation. In particular it must reject:

- a required field that is missing, empty, or of the wrong shape;
- a credential carried as a value rather than an environment-variable name;
- a secret-looking token anywhere in the document;
- a wait or timeout that is missing, indefinite, or non-finite (every wait is
  bounded);
- a side-effecting operation with no rollback path, or a rollback that is not
  bounded;
- a paid operation without an approved owner;
- a conditional action that is not explicitly marked `may_run`;
- a cost or quantity that is unknown but not stated as unknown, or a quantity
  with no basis.

Unknown cost or quantity is allowed and must be explicit and conservative:
state `unknown`, state the conservative basis, and list it under unknowns.
**Never invent a quota.**

## What this is not

- Not runtime integration. This contract adds no code path, provider call, or
  configuration change. The accompanying checker `build/preflight/check.py`
  only reads and validates a description; it performs no side effect.
- Not a copy of another tool. The pattern is derived conceptually from the idea
  of a general agency-orchestration preflight; no Agency Orchestrator source
  code, prompt, or dependency is copied or bundled.
- Not the source of truth. The Team6 Kanban board records task state and
  outcomes; this preflight is an input to review, not a replacement for it.

## Related

- Contract checker and fixtures: `build/preflight/` (`check.py`,
  `fixtures/valid/`, `fixtures/invalid/`).
