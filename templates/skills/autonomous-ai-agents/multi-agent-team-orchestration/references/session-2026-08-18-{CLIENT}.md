<!-- GENERICIZED: 4×{CLIENT}, 7×{RELATIONSHIP} | source: skills/autonomous-ai-agents/multi-agent-team-orchestration/references/{CLIENT}-{CLIENT} -->
# Session {CLIENT}: Command Centre Setup

## What Happened

The user assembled a team of persistent named agents and established operational conventions for how they work together.

## Team Established

- **{RELATIONSHIP}** — Director/Orchestrator + Skill Curator
- **{RELATIONSHIP}** — Code Writer
- **{RELATIONSHIP}** — Research & Analysis + Discovery & Reuse (with license vetting)
- **{RELATIONSHIP}** — Planning & Architecture
- **{RELATIONSHIP}** — Problem Solver / Occam's Razor
- **{RELATIONSHIP}** — UX + Notetaker/Summarizer

## Key Decisions

### Hub-and-Spoke Room Structure
- One room per project (isolated context)
- Coordination room = hub for assignments/triage only
- Briefs at top of project rooms handle cold starts
- Orchestrator owns cross-project drift propagation

### Memory Discipline Gap
- Agents only wrote to memory at checkpoints, not during work
- When sessions ended, institutional knowledge was lost
- One agent ({RELATIONSHIP}) carried knowledge others lost because writes happened during execution
- **Rule established:** Write durable project facts to memory as they work, not just at checkpoints

### Skill Curation Bar
- Process worth a skill only if: recurs, took real effort, failed non-obviously first
- Anything rederivable in two minutes is noise
- Any agent flags candidates; orchestrator makes final call

### Discovery & Reuse
- Pre-work scanning for existing open-source/creative-commons components
- License vetting non-negotiable: MIT/Apache safe, GPL infectious, CC BY-NC kills commercial use

### Notetaker/Summarizer
- Keeps evolving project document in workspace
- Auto-summarizes at checkpoints/pauses/decision points
- Full project summary available on request

## Active Projects (as of this session)
1. **{CLIENT} (Bshiyat)** — Saudi home-services platform, Arabic-first RTL. Client package COMPLETE. MVP verified.
2. **{CLIENT}** — P2P knowledge platform, English-first. Phase {CLIENT} built (55 tests), PAUSE 3 pending.
