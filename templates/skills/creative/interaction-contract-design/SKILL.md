<!-- GENERICIZED: 1×{RELATIONSHIP} | source: skills/creative/interaction-contract-design/SKILL.md -->
---
name: interaction-contract-design
description: "Design event contracts for async UIs before coding."
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ux, event-systems, multi-agent, cli-design, contract-design, prototyping]
    related_skills: [claude-design, sketch, game-ux-architecture]
---

# Interaction Contract Design

Use this skill when designing interfaces for **event-driven systems** — multi-agent platforms, CLI tools that render live progress, IoT dashboards, CI/CD status views, or any system where backend processes emit events that users need to see.

Load this when the user says things like "design the progress view," "how should the user see agent activity," "define the events between backend and UI," "interaction contract," "CLI progress rendering," or when the deliverable is a contract + prototype for surfacing async process state to users.

## When NOT to use this

- Static UI with no async/event-driven behavior — use `claude-design` or `sketch`
- Game input/feedback system — use `game-ux-architecture`
- Data visualization from a source document — use `interactive-data-simulation`
- Contract already defined, just implementing — go straight to `claude-design`

## Core Principle: Contract Before Code

The interaction contract is the **single source of truth** for what information flows from the system to the user. Define it BEFORE either side is implemented:

- The **designer** builds and tests the UX against the contract without waiting for backend
- The **developer** knows exactly what signals to emit and what fields to include
- Both sides verify completeness: if an event type is missing from the contract, it won't exist anywhere

## Procedure

### Step 1: Enumerate Event Types

List every distinct signal the user needs to see during execution. For each, define:

| Field | Description |
|---|---|
| **Event name** | Machine-readable identifier (e.g., `agent.tool_call`) |
| **Topic** | Message bus topic or event channel |
| **Payload** | Fields the event carries |
| **UX purpose** | What the user sees and why |

**Include explicit exclusions.** If a field looks useful but isn't reliable (e.g., `estimated_time_remaining` when iteration count is unknown), say so explicitly.

### Step 2: Define Rendering Intent

For each event type, specify how it should appear to the user:

- **Visual treatment** — color, icon, position
- **Prominence** — headline event or footnote?
- **Persistence** — momentary or persistent in a timeline?
- **Grouping** — agent-specific, phase-specific, or overall task?

### Step 3: Build a Simulation Prototype

Build a standalone HTML prototype that simulates events flowing through the system and renders them as the real interface would. Use the `claude-design` approach: dark-themed, monospace, fintech-dashboard energy. Include edge cases (blocked states, errors, low confidence).

### Step 4: Review and Lock

Present the contract + prototype to the team. Once approved, the contract is **locked** — both designer and developer proceed in parallel against it.

## Contract Design Rules

### 1. Blocked States Are the Most Important

When a process waits on another, the user must see **who** it's waiting on and **why**. Silence feels like a hang.

### 2. Confidence as Trust Signal

Include a confidence score (0.0–1.0) in result events. Render as color-coded badges: green (≥80%), yellow (≥60%), red (<60%).

### 3. Progressive Disclosure

Start with high-level status. Reveal detail (tool calls, intermediate outputs) on demand.

### 4. Tool Calls Are Visible but Not Noisy

Show tool calls as timeline entries with distinct colors. The user sees *what* the process is doing without being buried in raw data.

### 5. Final Output Is Calm

A single, scannable summary. No fanfare, no animation overload.

## Anti-Patterns

- **Over-engineering the mock.** Keep mocks dumb — predetermined canned sequences. If the loop can't terminate on canned responses, fix the loop.
- **Circular dependencies in event chains.** If Agent A can ask Agent B and vice versa, you have deadlock risk. Make the orchestrator the sole coordinator.
- **One-size-fits-all loops.** Deterministic transforms don't need iterative tool-use loops. Use a simpler execution model for them.
- **Fantasy fields.** Don't include fields the system can't reliably produce.

## References

- `references/nani-cli-contract.md` — Nani multi-agent CLI interaction contract (8 event types, payloads, rendering intent)

## Pitfalls

- **Starting without a contract.** Designer waits for backend or developer emits blindly — both waste time.
- **Contract as data schema only.** The contract includes rendering intent, not just data shapes.
- **Forgetting error states.** Every contract needs error events with recovery context.
