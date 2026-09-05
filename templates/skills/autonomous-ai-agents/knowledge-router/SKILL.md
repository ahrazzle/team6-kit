---
name: knowledge-router
description: "Use when scaling a multi-agent memory footprint. MoE-style activation: tiny always-on router, compartmentalized knowledge modules loaded on demand."
version: 1.0.0
author: Team6-kit
license: Apache-2.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Memory, Knowledge-Management, MoE, Context-Efficiency, Multi-Agent]
    related_skills: [agent-persistence-layers, multi-agent-knowledge-coordination, knowledge-drift-monitoring]
---

# Knowledge Router — MoE-style activation for persistent memory

> The pattern that turns an ever-growing always-on memory footprint into a
> small always-on router plus dormant, on-demand knowledge modules. Modeled
> on Mixture-of-Experts (MoE): only the needed parameters activate.

## When to apply

A multi-agent team's persistent memory (MEMORY.md + USER.md per profile, plus
SOUL.md) has grown into the single largest item in every prompt. It is
injected unconditionally, undifferentiated, every turn. That is the anti-MoE:
a dense always-on tensor where a sparse activated router should be.

**Symptoms that trigger this skill:**
- System prompt has crept past ~8K because persistent memory + SOUL are huge.
- Memory duplicates knowledge that also lives in a knowledge base or skills.
- On a bounded-context local model, per-turn re-ingest of the system prompt
  costs real wall-clock (measured: ~4 min/turn at 27K on a local 27B/256K).
- A profile has filled its memory budget and pruning keeps losing signal.

## The architecture (the 80/20 that matters)

| Component | Size | Loaded |
|---|---|---|
| **Router** (this file's pattern) | tiny (~1–2K) | always-on |
| **Breadcrumb** (memory entry) | ~1K | always-on |
| **Identity** (SOUL.md) | lean (<6K) | always-on |
| **Domain modules** | large, one per topic | on-demand, ONE at a time |
| **Zero-loss dump** | whatever it takes | only on recovery |

Three always-on surfaces (router breadcrumb + lean SOUL) carry the pointer
structure. Every byte of payload is a compartment, activated only when a
task touches its domain.

## The MoE rule

> Persistent memory / SOUL = ROUTER ONLY (breadcrumb pointers + identity).
> Everything derivable = module payload: project state, learnings, patterns,
> tool specifics, user-preference detail.
>
> If a needed fact is not on the router, it was NOT lost — the zero-loss dump
> holds it verbatim.

## How to build it (4 steps)

1. **Create a router file** at the knowledge base root (e.g. `ROUTER.md`):
   two knowledge bases (internal vs external), an activation table mapping
   each domain to its load path, a "route by intent" line, and a recovery
   pointer to the zero-loss dump.

2. **Compartmentalize the payload** into per-domain modules. Each module
   covers ONE domain: `ventures.md`, `products.md`, `env-tooling.md`,
   `team-ops.md`, `user-profile.md`, `per-agent roles.md`. Load only the one
   matching the task. Never load all.

3. **Write the zero-loss preservation dump FIRST** (before slimming anything)
   — verbatim content of the always-on memory, structured:
   ```
   # Preservation Dump — <profile> memory + user profile (<date>)
   > Recovery-only unstructured dump. Distilled facts live in ROUTER + modules.
   ## === MEMORY.md entries, verbatim ===
   ...
   ## === USER.md entries, verbatim ===
   ...
   ```

4. **Slim the always-on surfaces.** Replace each profile's memory with a
   breadcrumb-only router pointer (route-by-intent, KB paths, recovery
   pointer). Rewrite SOUL.md lean — preserve role identity + hard rules,
   point payload into the router.

## Hard rules

- **Preservation FIRST.** The zero-loss dump must exist, verbatim, before
  any memory byte is removed. Zero data loss is the only acceptable outcome.
- **Preserve identity verbatim.** When slimming SOUL.md, copy the Role /
  Mission / Gender / identity lines exactly — do not paraphrase identity.
- **Route, don't load.** Read the router once, pick the ONE module needed.
  "Load all" is a build failure, not an option.
- **The dump is recovery-only.** It is deliberately unstructured — never
  treat it as a routable module. Distilled facts live in the real modules.
- **Compartmentalize by domain, not by agent redundancy.** Six agents
  duplicating the same approval list is not modularity. One canonical home
  per fact; mirrors carry pointers.

## Proof discipline

- **Cold-start routing test:** after slimming, simulate a fresh session —
  does the breadcrumb resolve to the router, and does every referenced module
  path exist on disk? Verify, don't assume.
- **Zero-loss verification:** grep the dump for a sample of entries to confirm
  nothing was dropped.
- **Served-file honesty (external KBs):** a breadcrumb pointing at an
  unreachable path is worse than none. Verify the external KB is actually
  queryable (run one real query) before claiming the router works end-to-end.

## Measured payoff (reference)

On a bounded-context local model (27B/256K): cutting a ~27K always-on
system prompt toward ~6K total turned ~4 min/turn re-ingest into a fraction.
The MoE rule is a wall-clock win, not just a token ledger.

## References

- `agent-persistence-layers` — SOUL/MEMORY/USER layering + load-priority chain.
- `knowledge-drift-monitoring` — how to watch modules for drift after split.
- `multi-agent-knowledge-coordination` — cross-agent knowledge addressing.