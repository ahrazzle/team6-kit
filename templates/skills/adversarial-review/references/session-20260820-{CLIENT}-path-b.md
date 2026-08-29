<!-- GENERICIZED: 3×{CLIENT}, 15×{RELATIONSHIP} | source: skills/adversarial-review/references/session-20260820-{CLIENT} -->
# Session: {CLIENT} Path B Architecture Review ({CLIENT})

A 6-agent team ({RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}) reviewed the Nani multi-agent system architecture and chose Path B (reasoning patterns on mocks before real providers). {RELATIONSHIP} performed live adversarial review on {RELATIONSHIP}'s implementation plan before {RELATIONSHIP} started building.

## Context

Unlike post-hoc review of a written output or review during active design, this was **pre-implementation adversarial review of a plan** — attacking the proposed architecture before any scaffolding started. The "output" was {RELATIONSHIP}'s written plan itself.

## Interventions Made

### 1. MockLLMService Scope Creep
**The intervention:** {RELATIONSHIP} proposed enhancing the mock LLM to return structured tool-call responses with confidence scores and produce "varied behavior per agent role." This is not a mock — it's a poor man's LLM. If the reasoning loop can't terminate on simple canned responses, fix the loop, don't build a smarter mock.

**Why it mattered:** Path B's entire purpose is de-risking the architecture by deferring external dependencies. Building prompt parsing, tool-call sequencing, and confidence heuristics into a throwaway service defeats that purpose.

**Resolution:** Mock stays dumb — returns predetermined canned sequences (some with tool calls, some without). Reasoning loop handles tool calls generically.

### 2. Unguarded Circular Dependency (agent.ask)
**The intervention:** {RELATIONSHIP} proposed an `agent.ask` tool allowing agents to query each other via the message bus. This creates Agent A → Agent B → Agent A deadlock. Phase {CLIENT}'s "{RELATIONSHIP} explicitly chains agents" is convention, not enforcement.

**Why it mattered:** If the guard is convention, it will fail. An unguarded `agent.ask` tool lets any agent create circular dependencies that deadlock the system.

**Resolution:** Remove `agent.ask` from Path B. Orchestrator remains sole coordinator.

### 3. Uniform Abstraction Mismatch (SimpleAgent vs ReasoningAgent)
**The intervention:** {RELATIONSHIP} proposed every agent go through a unified `ReasoningAgent` base class with max_iterations and tool dispatch. Not all agents need tool-use iterations — a formatter that applies templates doesn't need `max_iterations`.

**Why it mattered:** Forcing every agent through `ReasoningAgent` adds a failure mode (exceeded iterations) where none existed.

**Resolution:** `SimpleAgent` base for deterministic transforms, `ReasoningAgent` for agents that actually explore.

## Outcome

All three interventions accepted. {RELATIONSHIP}'s foundation implementation started with the corrected plan. Zero rework required — the highest-leverage review is the one that prevents bad code from being written.

## The Pattern

**Pre-implementation adversarial cuts > post-hoc review > no review.** The same three issues discovered after implementation would have cost 5-10x more to fix. When the user says "stress-test the thesis with everything you've got," that includes the implementation plan before the code.
