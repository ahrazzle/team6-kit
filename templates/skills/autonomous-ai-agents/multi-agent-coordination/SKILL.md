<!-- GENERICIZED: 8×{CLIENT}, 22×{RELATIONSHIP} | source: skills/autonomous-ai-agents/multi-agent-coordination/SKILL.md -->
---
name: multi-agent-coordination
title: Multi-Agent Coordination
description: Coordinate parallel workstreams to a shared deliverable.
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
tags: [multi-agent, coordination, parallel-workstreams, blocker-management, team-dynamics]
metadata:
  hermes:
    tags: [multi-agent, coordination, parallel-workstreams, blocker-management, team-dynamics]
    related_skills: []
---

# Multi-Agent Coordination

Use when coordinating parallel workstreams across specialized agents (e.g., essay + tracker + visuals, or research + build + review) toward a shared ship date. This covers the full lifecycle: assignment → execution → blocker resolution → joint publication.

## When to Use

Activate this skill when:
- Multiple agents are assigned distinct workstreams that must integrate into a single deliverable
- Workstreams have cross-dependencies (e.g., tracker validates essay predictions; visuals embed in essay)
- A ship date requires synchronized delivery across agents
- Status checks are needed to identify blockers and idle agents

## Core Concepts

**Workstream** — A discrete output assigned to one agent (e.g., essay, tracker, visual asset, fact sheet).

**Cross-dependency** — When one workstream's completion requires output from another (e.g., tracker baseline data comes from essay's sourced fact sheet).

**Blocker** — A missing input that prevents an agent from finalizing their workstream.

**Sync-to-ship** — The constraint that all workstreams must be finalized together because they form a single integrated product (e.g., essay + tracker + visuals publish as one unit).

## Workflow

### 1. Assignment

Assign each workstream to the agent whose specialization matches. State:
- What they own (the output)
- What they need from others (dependencies)
- The ship date
- Who they sync with for integration

### 2. Status Check Format

When the user asks for a status update, each agent reports three lines:
- **Being worked on now:** Active task
- **Already delivered:** Completed outputs
- **Waiting on:** Blockers, if any

This format prevents duplication and makes cross-dependencies visible.

### 3. Blocker Management

When a blocker is identified:
1. Name the specific missing input (not "waiting on {RELATIONSHIP}'s report" but "waiting on junior-expertise verdict — confidence level and whether the finding held")
2. The blocker owner delivers directly to the blocked agent
3. The blocked agent integrates and confirms resolution

### 4. Sync-to-ship

When workstreams are interdependent:
- Final outputs are not "done" until all are ready
- Language/framing must be aligned across outputs
- Ship date is a single point for all outputs
- One agent's delay cascades — flag early

### 5. Stress-testing Integration

If the team includes a stress-testing role:
- They attack the thesis as drafts emerge
- Their concerns should produce concrete changes
- Final stress pass happens on the published draft, not the outline

### 6. Coordination Primitives

**Task Declaration Protocol.** Before starting work, each agent states their current task in one line: "I'm working on X." This prevents two agents from doing the same work simultaneously.

**Silence/Pause Directives.** The director (or user) can restrict room participation. When this happens, agents reply with exactly "(pass)" and stop all work until the directive is lifted. A new directive from the user overrides the previous silence directive — the director should recognize contextual shifts rather than enforcing old rules mechanically.

**Approval Gates.** Phased execution: research/planning first, then implementation only after explicit go-ahead. If the user says "do NOT start writing any code or editing/creating files until receiving an explicit go-ahead," that is a hard gate — research only.

**Positive Reinforcement Encoding.** When the user expresses satisfaction, the team studies what earned the approval and encodes it as reusable patterns. The director assigns targeted memory per role: each agent remembers only their role-specific approval patterns plus cross-cutting coordination rules.

## References

- references/coordination-log-the-search.md — Session transcript of the "The Search" coordination (essay + tracker + visuals, September 2026)
- references/{CLIENT} — {CLIENT} first night: architecture, failures, role system evolution (August 2026)
- references/coordination-primitives.md — Task declaration, silence/pause directives, approval gates, positive reinforcement encoding (August 2022)
- references/team6-coordination-{CLIENT}.md — Team6 formalization: contribution order, SOUL.md as identity carrier, model config framework, cost-benefit analysis, anti-patterns (August 2026)

## Role Design

### Static Domains → Capabilities → Venture Alignment

Three generations of role structure, each learned from failure:

**Generation 1: Static Domains** — Each agent "owns" an activity (design, code, research, speed, simplicity, coordination).
- Failure: Agents work outside their domain because the work demands it. The coordinator becomes a bottleneck (29/29 commits from one agent).
- Lesson: No one can predict which capabilities a task will need. Ownership prevents contribution.

**Generation 2: Shared Capabilities** — Each agent has multiple capabilities (Architecture, Implementation, Verification, Synthesis, etc.). No one "owns" a domain.
- Failure: Documentation vs. behavior gap. Agents are described as having capabilities but still execute sequentially because the chat is single-threaded.
- Lesson: Role structure without execution model change is decorative.

**Generation 3: Venture Alignment** — Each agent owns an *outcome* (a venture), not a function. The chat is for sync, not for doing work.
- Principle: Agents own outcomes ({CLIENT} ships because {RELATIONSHIP} owns it), not activities ("{RELATIONSHIP} does infrastructure").
- Accountability: Clear. If a venture stalls, the owner drives. No diffusion of responsibility.
- Collaboration: Natural overlap points ({CLIENT} + {CLIENT} on monorepo, {CLIENT} + {CLIENT} on knowledge).

### Single Point of Failure Patterns

**The Coordinator Bottleneck.** If all agents "defer to {RELATIONSHIP}" for decisions, {RELATIONSHIP} becomes the single point of failure. The fix: conflict resolution protocol (venture leads first, coordinator last).

**The Sequential Handoff Paradox.** Sequential handoffs create a relay race — only one runner at a time, with stalls between exchanges. The fix: overlapping drivers, not better baton passes.

**The Two-Commit Bottleneck.** A two-commit handoff rule solves the single-driver problem but creates a new one: agents step back after 2 commits, creating a vacuum. The fix: no stepping back when your part is done — stay productive until blocked, then switch tasks (never stop).

## Anti-Patterns

**Doing Work in the Chat.** The chat is single-threaded. Only one agent processes at a time. Doing work in the chat means one agent occupies the channel while others wait. The fix: delegate work to independent sessions/cron jobs. The chat is for coordination, decisions, and conflict resolution.

**Protocol Reproduction.** The default behavior reproduces the failure while naming it. Agents will recreate sequential ownership while documenting overlapping-drivers. The fix: structural changes (handoff rules, lock files, automation), not just documentation.

**Documentation vs. Implementation.** A mechanism that isn't exercised is a hypothesis, not a system. The fix: every mechanism must be wired into an automated check (heartbeat script, health dashboard, cron job) or it will be ignored.

**Role Structure Optimization as Category Mistake.** When the real constraint is sequential execution in a chat, optimizing role structure is a distraction. The fix: minimize channel occupancy (shorter turns, faster handoffs, smaller contributions per agent).

## Contribution Order & Silent Mode

**Hard Contribution Order.** The user established a strict contribution sequence for group chats:
- **{RELATIONSHIP} → {RELATIONSHIP} → {RELATIONSHIP} → {RELATIONSHIP} → {RELATIONSHIP}**, with {RELATIONSHIP} cutting across wherever overengineering appears.
- **"jj" identifier**: When the user types "jj" or asks a simple question directed at {RELATIONSHIP}, other agents stay silent unless called on or their specific expertise applies. No unsolicited opinions.
- **{RELATIONSHIP} never speaks before {RELATIONSHIP} or {RELATIONSHIP}** when their domains are relevant. Research/design before code.

**Why this matters**: The team had a pattern of all five agents chiming in on simple questions, degrading signal-to-noise. The order ensures each layer builds on the previous one, and code never precedes design.

## SOUL.md as Identity Carrier

**Memory strips on profile install.** `hermes profile install` ships SOUL.md, config.yaml, profile.yaml, README.md, assets/ — but hard-excludes `memories/` with no override. Every operational rule, team registry, and environment fact must live in SOUL.md, not memory, for distribution packages.

**Frozen memory caps.** Memory is injected into the system prompt as a frozen snapshot at session start. Changes to memory limits or content won't appear in the current session — they apply on next session start. Every "committed and now active" report is half-true: the file changed, the running context did not.

**hermes config set strips comments.** `hermes config set` removes ALL inline comments from config.yaml. Silent failure mode — settings intact but documentation lost. Always back up before batch config changes.

## Hermes Infrastructure Patterns

**AGENTS.md priority chain.** Only one project context file loads per session, first match wins: `.hermes.md`/`HERMES.md` → `AGENTS.md` → `CLAUDE.md` → `.cursorrules`. If a higher-priority file exists, AGENTS.md is silently ignored — no error, no warning. Always check project roots before authoring.

**Worktrees for parallel agents.** `/worktree new <name>` gives each agent its own branch, directory, and checkpoint history. Mandatory whenever more than one agent edits the same repo — without this, rollback on one agent can silently undo another's work.

**Checkpoints SOP.** Enable on all profiles via `checkpoints.enabled: true`. Shadow store at `~/.hermes/checkpoints/store/`. Per-project refs auto-deduped across sessions.

## Backup File Protocol

**Numbered backups are user-owned.** When the user says "I have backups stored elsewhere" or files are numbered (e.g., `SOUL.md.bak`, `config.yaml.1`), never apply instructions to those files or alter them in any way. Only touch active profile paths in `~/.hermes/profiles/<profile>/`.

## Model Config Framework

**Per-agent reasoning levels.** The config supports per-agent `reasoning_effort`:
- **High**: {RELATIONSHIP} (orchestration), {RELATIONSHIP} (research), {RELATIONSHIP} (architecture — decisions compound)
- **Medium**: {RELATIONSHIP} (pattern-matching), {RELATIONSHIP} (iterative/visual), {RELATIONSHIP} (cutting, not adding)

**Project-start model selection.** At project kickoff, the director assesses scope:
1. Default: free main model (Ox Alpha, DeepSeek V4 Flash) + free aux + per-agent reasoning levels
2. Complexity signal (multi-week, shared infra, financial logic): flag for potential paid tier
3. Critical synthesis only: one-shot escalation to premium model (Hermes 4 405B Thinking, Claude Opus)

**Budget architecture.** Six agents sharing one pool means the main model is the only cost driver. Aux models are already free. Reserve premium models for final synthesis on critical decisions only.

## Pitfalls

**Ambiguous verdict handoff.** If an agent says "verdict is in" without specifying the confidence level or outcome, the blocked agent cannot proceed. Always state: (1) does the finding hold, (2) at what confidence level, (3) what language changes are required.

**Premature finalization.** Don't mark a workstream "complete" before cross-dependent workstreams are ready.

**Duplicate status reports.** If multiple agents report status simultaneously, the user hears the same information twice. The director should designate one reporter per topic.

**Format mismatch.** Confirm the target publication format before building visual assets.

**Commit count as vanity metric.** Measuring commits or files created tells you activity, not health. Measure: distinct contributors per cycle, pattern reuse rate, tension-to-synthesis conversion, orphan document count.

**Experience inflation.** Not every commit needs an experience. The threshold: "does this change future behavior?" If not, session context only.
