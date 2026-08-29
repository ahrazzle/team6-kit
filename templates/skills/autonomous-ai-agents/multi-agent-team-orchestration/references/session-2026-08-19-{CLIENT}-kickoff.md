<!-- GENERICIZED: 2×{AMOUNT}, 10×{CLIENT}, 7×{RELATIONSHIP} | source: skills/autonomous-ai-agents/multi-agent-team-orchestration/references/{CLIENT}-{CLIENT}-kickoff.md -->
# Session {CLIENT}: {CLIENT} Project Kickoff

## What Happened

New project "{CLIENT}" created — P2P knowledge-sharing platform. The user provided a detailed `finalplan.md` execution plan and asked the team to read it and discuss how to proceed.

## Project Setup Flow

1. **Project created** via `project_create` with path `/Users/{RELATIONSHIP}/{CLIENT}{CLIENT}/wrk/xpt6`
2. **Plan distributed** to all agents as an attachment
3. **Agent responses** — each agent reviewed the plan and flagged their concerns/recommendations before any work began
4. **Decision-locking** — user confirmed D2/D3/D4 decisions; orchestrator committed to memory
5. **Unblocking Phase {CLIENT}** — orchestrator assigned tasks to agents for immediate start

## Decision-Locking Pattern

When a plan has open decisions (D2/D3/D4), the orchestrator must:
1. Surface all open decisions to the user with clear options
2. Commit confirmed decisions to memory immediately
3. Identify which decisions remain open and block downstream phases until resolved
4. Proceed with work that doesn't depend on open decisions

## User Decisions Committed

- **D2:** English-only launch. Never use automation for translation. Write original content in new language rather than translating existing content.
- **D3:** Build infrastructure for % take fee + subscription model, but keep flexible/adjustable for future changes.
- **D4:** Go with plan recommendation — ship discovery + matching + reviews + messaging + access policies first; full {CLIENT} economy as v2 unlock.

## Open Questions (Blocked for Phase {CLIENT})

- **Auth approach:** Plan says Clerk from day 1; user previously said built-in OTP for MVP, Clerk later. Needs ruling.
- **"Demonstrated learning" definition:** Who designs checkpoints, who verifies, what happens on disagreement? If mentor-confirmed, redundant with teaching points. If automated, AI assessment engine — arguably harder than the rest of the platform.

## Memory Management Technique

When memory is near capacity (hit {AMOUNT}/{AMOUNT} chars), the orchestrator:
1. Identifies stale/verbose entries to remove
2. Shortens remaining entries to free space
3. Adds new decisions in compact form
4. Does this in a single batch operation where possible, or sequential operations if batch fails

Key insight: Memory compression is a recurring task. Proactive trimming before adding prevents hitting the ceiling.

## Agent Routing for Phase {CLIENT}

- **@{RELATIONSHIP}** — monorepo setup, Docker Compose, Prisma, CI, stack spike (Expo/Fastify/PostGIS/pgvector)
- **@{RELATIONSHIP}** — design-token skeleton (`packages/design`), component primitives
- **@{RELATIONSHIP}** — settle "earn by learn" verification question with concrete proposal
- **@{RELATIONSHIP}** — architecture review at REVIEW PAUSE 0, package topology confirmation
- **@{RELATIONSHIP}** — simplicity review, scope challenge (flagged auth conflict and undefined "demonstrated learning")

## AI Component Decisions (Locked Unless User Objects)

Per {RELATIONSHIP}'s recommendation:
- Skip AI learning paths for MVP (huge scope, unproven)
- Use simple embedding similarity for matching (cheap, proven)
- Defer AI fraud detection to rule-based heuristics until labeled data exists

## Key Patterns Observed

- **Plan-first kickoff:** User provides a detailed plan, team discusses before building
- **Agent pre-flight review:** Each agent reads the plan and flags issues before Phase {CLIENT} starts
- **Decision gates:** Review pauses between phases force user confirmation before scope expands
- **Orchestrator as decision router:** Orchestrator decides which questions go to user vs. which can proceed
