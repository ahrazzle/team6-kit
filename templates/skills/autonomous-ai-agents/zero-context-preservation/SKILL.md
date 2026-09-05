---
name: zero-context-preservation
description: "Use when migrating/trimming persistent memory across a fleet. Direct-execution pivot: preservation dumps + harness work done in shell at zero context cost; orchestrator preserves identity verbatim."
version: 1.0.0
author: Team6-kit
license: Apache-2.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Memory-Migration, Context-Efficiency, Preservation, Fleet-Operations, Orchestration]
    related_skills: [knowledge-router, agent-persistence-layers, subagent-pipeline-recovery, multi-agent-team-orchestration]
---

# Zero-Context Preservation — the direct-execution pivot

> Preservation and harness work must NOT cost orchestrator context. The more
> that can be done in the shell, the less memory the migration eats. When a
> task is mechanical (copy content, transform files), execute it directly —
> do not read the bytes into the reasoning window first.

## The pivot

Delegation has a cost: reading content into the orchestrator context to form
a brief. For preservation work, that cost is avoidable — the shell can copy
and shape files without the LLM ever seeing their bytes. The rule:

> **Preservation dumps done via shell at zero context cost; identity
> preserved verbatim by the orchestrator. Delegate only what needs judgment;
> execute directly what is mechanical.**

## The three-part discipline

### 1. Shell-first for mechanical work (`zero-context`)

Do NOT read MEMORY.md / USER.md into the reasoning window to "preserve" it.
The shell does it verbatim:

```bash
for p in azaraki kodekoot lugia shayba sheikh-al-jabr; do
  M="$HOME/.hermes/profiles/$p/memories/MEMORY.md"
  U="$HOME/.hermes/profiles/$p/memories/USER.md"
  OUT="$HOME/.hermes/eldunari/domains/$p-preservation-20260904.md"
  {
    echo "# Preservation Dump — $p memory + user profile"
    echo ""
    echo "> Recovery-only dump. Distilled facts live in ROUTER + modules."
    echo ""
    echo "## === MEMORY.md entries, verbatim ==="
    echo ""
    cat "$M"
    echo ""
    echo "## === USER.md entries, verbatim ==="
    echo ""
    cat "$U"
  } > "$OUT"
done
```

The dumps are written with zero context cost — the bytes never enter the
reasoning window. This is the difference between a cheap migration and an
expensive one.

### 2. Read-targeted for distillation (`judgment`)

Role-specific distillation NEEDS the content seen. Read it ONCE, extract the
role-unique facts, write the role module. This is judgment work — delegate it
or read it, but do not let it balloon: read the file once, write the distilled
product, move on.

### 3. Orchestrator preserves identity verbatim (`identity`)

When rewriting SOUL.md across profiles, the ROLE / MISSION / IDENTITY lines
are load-bearing and must be preserved VERBATIM — never paraphrased. The
orchestrator reads each profile's identity block before rewriting and copies
those lines exactly into the lean version.

## When delegation is the right call vs. direct execution

| Task type | Route |
|---|---|
| Verbatim copy / file reshape / bulk transform | **Direct (shell), zero context** |
| Read + extract + distill role knowledge | Read once, or delegate (judgment) |
| External side effects (push, release, rename) | Orchestrator owns; verify against live state |
| Anything needing a human-in-the-loop decision | Delegate + surface, or ask |

## Hard rules

- **Preservation dump FIRST, verbatim, before slimming anything.**
- **Zero data loss is the only acceptable outcome** — the dump must exist
  before any memory byte is removed.
- **Never read what you don't need to see** — mechanical copy belongs to the
  shell, not the context window.
- **Identity is preserved verbatim, not distilled.** Para-phrasing a Role
  line is data loss.
- **Back up the surfaces you overwrite.** If you rewrite SOUL.md, note whether
  a pre-write backup exists; if none, record the loss scope explicitly rather
  than claiming zero-loss.
- **Verify against the LIVE system, not self-reports.** For runtime claims
  (which model generated tokens) check token/usage logs, not frozen system
  context.

## Known pitfalls

- **The "read then report" trap.** A subagent that reads all specs then dies
  with zero files written is a known failure (read-then-die). For preservation
  work specifically, the shell writes BEFORE any reasoning dies.
- **Path-in-context delegation failure.** Some delegation harnesses reject
  task context containing absolute filesystem paths (parse error). When that
  happens, do not loop retrying the same farm — pivot to direct execution.
- **Overwriting without a backup.** Rewriting a live file that had no
  pre-write backup is recoverable from the session transcript but should not
  pass as "zero-loss." Record it.

## Proof discipline

- After migration: run a **cold-start routing test** (breadcrumb → router →
  every referenced module exists).
- Confirm each dump has nonzero content (spot-check `wc -c`), not a stub.
- For release/push steps: verify the outcome against the live remote (URL,
  release tag, commit SHA) — a successful tool call is not a successful task.

## Relations

- `knowledge-router` — the architecture this feeds (MoE-style activation).
- `agent-persistence-layers` — SOUL/MEMORY/USER layering.
- `subagent-pipeline-recovery` — read-then-die recovery runbooks.