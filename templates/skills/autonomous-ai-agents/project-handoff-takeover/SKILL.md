<!-- GENERICIZED: 9×{CLIENT}, 1×{RELATIONSHIP} | source: skills/autonomous-ai-agents/project-handoff-takeover/SKILL.md -->
---
name: project-handoff-takeover
description: "Take over an unfinished project from another build tool."
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
---

# Project Handoff Takeover

Take an incomplete project left by another build session or tool (Claude CoWork, Claude Code, a different Team6 room, a previous agent) across the finish line. Produces an execution plan for user review — does NOT build until sign-off.

## When to Use

- User points at a workspace of working files and says "take it across the finish line", "make an execution plan", "finish what X started"
- Incoming workspace contains handoff/spec/brief documents describing a build that stopped partway
- Distinguished from `project-initializer` (brand-new project, no files) — this skill is for EXISTING work with state on disk

## Process

### 1. Recon on disk, not from docs
- Map the tree first: `search_files` (target='files') or `terminal` `find . -maxdepth 3 -not -path "*/node_modules*"` at the top level (skip node_modules, .git).
- Check for `.git` via `search_files` (target='files') or `terminal` `ls -d .git` — **git presence is the #1 safety signal**. If absent, Phase {CLIENT} must close it before any edit.
- Note last-write dates (`ls -la` / `stat`) — they tell you where the work stopped.
- Grep for absolute-path references to the previous machine/tool location (portability check).
- **Verify teammate recon claims yourself** — one tree/`ls` round-trip per major claim before you build the plan on it.

### 2. Find the authority docs; quote the done-definition
- Look for `handoff/`, `*BRIEF*.md`, `*SPEC*.md`, `README.md`, `PROGRESS.md`, `DEPLOY.md`.
- The finish line is usually DOCUMENTED, not guessed: "done when" lists, `npm run verify` gates, demo paths, known quirks to preserve.
- Quote the hard acceptance criteria literally into the plan. Do not paraphrase numbers or states.
- Check whether the handoff sequence actually RAN: an empty next-step directory (`handoff/design` empty etc.) means the project stopped mid-sequence — that step becomes Phase {CLIENT} of your plan.

### 3. Safety net BEFORE any edit (Phase {CLIENT})
- If no git exists on an uncommitted tree: `git init && git add -A && git commit -m "Pre-redesign baseline: ..."`. An uncommitted tree is a one-way door — first edit permanently destroys the prototype.
- Version/redundancy folders (`v16 freeflow`, `webapp v7 (self verify)`, `vers/`, `handoff prepped`) are user-made backups. Never edit, never delete, never apply build instructions to them.
- Identify "untouchable" layers from the brief (validated data, engine, algorithms) vs "replaceable" surface. The brief's rules of engagement are law — the QA gate enforces them later.

### 4. Verify claimed-green gates by RUNNING them
- The handoff says "all green" — re-run `npm run verify` / `validate.py` yourself and record real output. "Claimed green" is a claim, not a fact. If it's red at baseline, that's a diagnosis task BEFORE Phase {CLIENT}, not an assumption to carry.

### 5. Scope split
- **Primary**: the artifact with a hard, documented done-definition (usually the core product/engine surface).
- **Secondary**: supporting surfaces (landing pages, diagrams, README fixes) — sequenced after core is green.
- Explicitly out of scope: anything the brief declares untouchable (model/data changes invalidate validation). Say so in the plan.

### 6. Phased plan with user checkpoints
- Standard shape: P0 baseline+git → P1 design (if handoff design step never ran, it must run now) → P2 build (in the brief's de-risking order — the hardest screen first forces every state to exist) → P3 verification gates → P4 release.
- Checkpoints at decision gates: plan approval → design review (the handoff's "one question" gate) → done-report with actual command output.
- Deliver the plan as a `PLAN.md` in the workspace AND a room report with the summary, phases, ownership table, and the biggest risk called out.

### 7. Preserve, don't fix
- Documented quirks/drifts are sacred: carry explanatory comments across, never "fix" known-good drift by reimplementing logic.
- No new persistence (localStorage etc.) unless the handoff asks for it — "nothing persists across reload" is often deliberate.

## Pitfalls

- Reading the whole tree is a token sink — use `find` excluding node_modules for structure, then targeted reads of only the authority docs.
- Trusting "claimed green" prose in a handoff = planning on a false premise. Run the gate.
- Starting design/build before git init = destroying the phase record irreversibly.
- Applying build steps to version folders = violating the user's backup structure (memory rule: never touch "vers"-like folders).
- Missing that the handoff sequence stopped mid-way (empty design dir etc.) — always check for the missing step; it becomes your Phase {CLIENT}.

## Support Files

- `references/{CLIENT}-{CLIENT}` — concrete worked example: {CLIENT}/{CLIENT} takeover (handoff structure, verified findings, plan shape).