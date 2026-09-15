# Session-recall observer contract

This document defines a read-only way to inspect prior session history and persistent memory views.

## 1. Scope and non-goals

The observer may read existing session history and memory records and derive
recall views from them. It is not a writer, not a memory manager, not a session
manager, and not a replacement for the memory tool. Anything that creates,
edits, deletes, or reorganizes history or memory is outside this contract.

## 2. Terms and trust boundary

- **Observer**: a read path that inspects the history store and persistent
  memory and returns a recall view.
- **History store**: the durable record of prior sessions the observer reads.
- **Memory entry**: one record written by the memory tool into persistent
  memory.
- **Recall view**: the derived, read-only result the observer returns to a
  caller.
- **Missing store**: a history or memory store that is absent when the observer
  attempts to read it.
- **Failure**: an actual error while opening, reading, or parsing an existing
  store.

The observer is an untrusted read path. Its output is observational context,
never an authority to mutate state.

## 3. Read-only history access

Open the history store in read-only mode. Read existing records only. The only
work permitted beyond reading is in-memory aggregation needed to form a recall
view; a read produces no on-disk artifact.

## 4. Missing-store behavior

If the history or memory store is absent, return an empty result in the same
shape as an empty successful view. Never create, initialize, migrate, or repair
the store, and never report a missing store as a failure.

## 5. Failure behavior and opacity

On an actual read, open, or parse failure, log the diagnostic detail inside the
observer boundary and return a stable generic error outside it. Never return
exception text, file paths, SQL, or a traceback to the caller.

## 6. Parse agreement with the memory tool

A recall view parses memory using the same public delimiter, encoding, entry
boundaries, and field interpretation the memory tool uses when it writes
memory. The observer must not introduce a second parser and must not silently
normalize entries.

The implementation handoff must preserve the current public agreement
represented by `ENTRY_DELIMITER` and UTF-8 BOM-tolerant input (`utf-8-sig`),
while resolving the actual runtime symbol from the memory tool rather than
copying a private implementation.

A parser disagreement is a contract failure, not a reason to display a
best-effort reinterpretation as authoritative memory.

## 7. Deterministic subject signals

Subject signals are deterministic, non-normative guidance only. Identical input
records must yield identical candidate signals: no LLM, no randomness, no
wall-clock dependence, and no hidden mutable index.

The allowed signal families are session titles, file paths, tool names, slash
commands, quoted phrases, and identifiers. An implementation may use these to
suggest subjects, but it must not treat a subject as a fact, permission,
policy, or memory entry.

This contract does not mandate a score, ranking, threshold, or user-facing
taxonomy. Any such choice belongs to a later approved design and must not
change the read-only boundary.

## 8. Recall-view shape and empty results

Every successful read — including a missing-store read — must distinguish an
empty view from a failed read without exposing internal storage details. The
consumer can rely on a stable shape: the observed records, whether any record
was observed at all, and whether the read itself succeeded. This contract
describes those dependable fields; it does not prescribe a runtime API.

A view may include derived subjects, session summaries, dates, snippets, or
memory entries only when those values come from the read path and the parse
agreement. It must not invent entries or claim completeness beyond the observed
records.

## 9. Observer write prohibition

The observer must never write session history, persistent memory, derived
history indexes, migrations, repair markers, or user-visible memory changes.
Operational logging is the only permitted side effect, and it must remain
outside the history and memory stores.

## 10. Consumer and compliance rules

Consumers must treat recall output as observational context. A suggested
subject is never normative policy. Consumers must preserve the generic-error
and empty-result distinction defined by this contract rather than collapsing
the two.

## 11. Conceptual provenance

Conceptual source: NousResearch/hermes-memory-wiki (MIT). Original Memory Wiki by @Araja119 (PR #31244); standalone plugin conversion by Teknium/Nous Research (#89940); independent proposal by @scotty87 (#33043). Adopted as a principle only; no source code, prompts, or prose copied.

## 12. Acceptance checklist

A build review must fail unless the implementation demonstrates:

- [ ] Read-only access: the history store is opened read-only and reads
      existing records only.
- [ ] Missing store: an absent store returns an empty view in the successful
      shape, with no create, initialize, migrate, or repair path.
- [ ] Failure opacity: real failures are logged inside the observer boundary
      and surface only a stable generic error outside it.
- [ ] Parse agreement: memory is parsed with the memory tool's public
      `ENTRY_DELIMITER` and `utf-8-sig` handling; no second parser.
- [ ] Deterministic signals: subject suggestions come only from the allowed
      families, are reproducible, and are treated as non-normative guidance.
- [ ] No writes: no history, memory, derived index, migration, or repair
      marker is ever written; operational logs stay outside both stores.
- [ ] Generated-kit ship proof: this document reaches a generated kit
      byte-for-byte verbatim and appears as a generic-ship provenance entry in
      the build audit trail.
