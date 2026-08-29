<!-- GENERICIZED: 10×{CLIENT}, 9×{RELATIONSHIP} | source: skills/autonomous-ai-agents/multi-agent-orchestration/SKILL.md -->
---
name: multi-agent-orchestration
description: Coordinate named agents through multi-domain projects.
---

# Multi-Agent Orchestration

You are the conductor of a named-agent orchestra. Your job is not to play every instrument — it is to route, coordinate, synthesize, and ensure quality across agents.

## When to Use

- The user assigns a project that spans multiple domains (research, code, design, architecture, QA)
- Multiple named agents are available, each with a specialized function
- The work must progress through phases: research → planning → execution → validation → iteration
- The user expects continuous progress with quality gates

## Coordination Map

Maintain a clear map of who does what:

| Agent | Domain | Strengths |
|-------|--------|-----------|
| {RELATIONSHIP} | Code writing, debugging, features | Modular, annotated code |
| {RELATIONSHIP} | Research, investigation, hidden connections | First principles, game theory, Feynman |
| {RELATIONSHIP} | Strategic analysis, architecture | Incisive, game theory, concise |
| {RELATIONSHIP} | Problem solver, Occam's Razor | Cuts complexity, finds simplest path |
| {RELATIONSHIP} | UI/UX, graphic design, human experience | Intuitive, warm, dopamine-aware |

## Competitive Landscape Research Before Ideation

Before entering any design or architecture phase, delegate a competitive landscape research pass to establish a factual baseline. This prevents groupthink and ensures design decisions are grounded in what actually exists.

**Pattern:**
1. Dispatch a research agent to map the existing market (products, frameworks, business models, gaps)
2. Require the research to include concrete data points (revenue, user counts, specific mechanics) — not vague generalities
3. Use the research findings to frame the design discussion, not the other way around
4. The research deliverable should end with a clear "white space" statement — what doesn't exist yet

**When to apply:** New product/feature ideation, framework design, market entry decisions, any time the user says "what's already out there."

## Shared Contract Parallel Delegation

When multiple agents work in parallel on different layers of the same system, define the integration contract FIRST — then dispatch. Never let parallel agents work against undefined assumptions.

**Pattern:**
1. Identify the integration points between parallel workstreams (e.g., event schemas, rendering layers, data structures)
2. Define the shared contract explicitly (TypeScript interfaces, event shapes, rendering layer assumptions)
3. Have all agents acknowledge the contract before work begins
4. Dispatch with the contract embedded in each task's context

**Example from {CLIENT}:** Before dispatching event bus + beat-map + feedback layer in parallel, we aligned on the judgment event shape `onHit(judgment, key, delta)` / `onMiss(key, expectedKey)` / `onNoteStale(note)` / `onCombo(count, multiplier)`. Each agent received this contract in their task context.

## Architectural Fork Resolution

When a fork surfaces that determines everything downstream (rendering layer, input model, framework-first vs. game-first), resolve it BEFORE parallel work continues. Do not let subagents scaffold against undefined assumptions.

**Pattern:**
1. Recognize when a question is a fork (two fundamentally different paths, not a minor preference)
2. Frame the fork explicitly for the room
3. Propose a resolution or ask the user for a judgment call
4. Only dispatch parallel work after the fork is settled

**Example from {CLIENT}:** {RELATIONSHIP} surfaced the input model fork (wrong keys advance the beat vs. wrong keys block progress). We resolved it via {RELATIONSHIP}'s "Correct Key + Timing Window" synthesis BEFORE {RELATIONSHIP} scaffolded the event bus.

## Post-Delegation Verification

Subagents hit iteration caps. This is expected, not a failure. Budget time for verification and cleanup after every parallel dispatch.

**Pattern:**
1. **Verify immediately** — `search_files` to see what landed, `read_file` to inspect, `tsc --noEmit` (or equivalent) to check compilation. Don't assume subagent output is clean.
2. **Fix systematically:**
   - Wrong import paths first (mechanical)
   - Missing types/interfaces (add to shared types file)
   - Unused variables (prefix with `_`)
   - Duplicate object properties
3. **Write missing tests** — if the subagent hit the cap before delivering the test harness, write it yourself to validate the foundation.
4. **Run and iterate** — expect the first test run to surface issues. Fix and rerun.

**Recovery signals from {CLIENT}:**
- All three parallel subagents hit `max_iterations`. Outputs had `../types.js` imports (wrong — should be `./types.js`), missing types in `types.ts`, unused variable warnings, duplicate object properties, and no test harness.
- Recovery: 30 minutes of systematic fixes + writing the test harness from scratch.
- Result: 29/29 tests pass after fixing one redundant combo emission.

**Key insight:** The iteration cap is a soft failure. The orchestrator catches it. This is why parallel delegation budgets should include 20-30% time for post-dispatch verification.

**If parallel batch fails completely:** Re-dispatch missing deliverables as single-focused payloads (one task at a time) rather than retrying the full parallel batch. See references/iteration-cap-mitigation.md for the pattern.

## Plugin Architecture: Contract Validator First

When building a plugin-based framework, the first consumer is NOT a polished product — it's a contract validator. The feedback layer carries the weight of "fun"; the first plugin just needs to exercise every hook.

**Pattern:**
1. Define the plugin contract (lifecycle hooks, rendering access, event consumption)
2. Build a minimal "debug plugin" that exercises every hook with the simplest possible visual output (a circle that scales with combo, a progress bar that fills)
3. Validate the contract end-to-end with real data flowing through the pipeline
4. Only then design the real consumer-facing plugins

**Why:** Building a polished first game before proving the framework works is "framework-first by another name." If a 7-year-old's delight depends on what you build first, the framework is already wrong — the feedback layer should carry that weight.

**Example from {CLIENT}:** {RELATIONSHIP} caught this — the first plugin should be a DebugPlugin that exercises `onHit`, `onMiss`, `onCombo`, `onStreakThreshold`, `onSongComplete`, `onNoteStale`, `onGameStart`, `onGameEnd`, `getCanvasContext`, `getFeedbackLayer` with a circle that scales and a bar that fills. Nothing more.

## Bundling for Browser Validation

When browser tools (`open_preview`/`read_preview`) are unavailable or systematically fail on the user's machine:

1. Bundle the framework with esbuild: `esbuild src/index.ts --bundle --outfile=dist/bundle.js`
2. Create a `demo.html` that imports from the bundle: `<script type="module" src="dist/bundle.js"></script>`
3. Serve via HTTP: `python3 -m http.server 8000`
4. Open in the user's browser: `http://localhost:8000/demo.html`

This resolves extensionless import issues that browsers can't handle natively and bypasses the preview pane entirely.

**Verify the SERVED artifact before declaring a fix.** After any fix that touches source or the bundle, curl the live URL and grep for the new method/marker before telling the user to test. "Fixed — hard refresh" without a served-bundle check is how repeated rounds of "still broken" happen: the page and bundle drift (un-pushed `dist/`, un-rebuilt bundle, stale CDN cache), and the user keeps testing old code while the team insists it is fixed. A new `?v=N` on the URL or an incognito window is the definitive cache bypass — not a fourth hard-refresh instruction.

**Temp fixes must be reverted when the real fix lands.** A workaround left in place (e.g. a ghost note injected so the first approach ring is visible) becomes a permanent bug (an unwanted space injected before the user's content). When you ship the real fix for a temp fix's root cause, remove the temp fix in the same change.

## Project Workspace Anchoring

When starting a new project, use `project_create` to anchor the workspace immediately. This gives all agents a shared working directory and prevents file-scattering.

**Pattern:**
1. `project_create(name, path)` — creates the project and switches the session
2. All subsequent delegation tasks receive the workspace path in their context
3. Agents write outputs to the project directory
4. The orchestrator can verify outputs by reading from the project path

## Delegation Protocol

1. **Classify** — Is this single-domain or cross-domain?
2. **Route** — Assign to the best-suited agent. If two could handle it, pick the tighter specialization.
3. **Frame** — Provide: goal, constraints, expected output format, definition of "done."
4. **Monitor** — Track progress. Intervene only if blocked, off-track, or asking for user input.
5. **Integrate** — Synthesize multi-agent outputs. Resolve contradictions. Present unified results.

## Directive Handling

- **New directives override old ones.** When the user gives a new instruction, it supersedes previous standing rules. Do not mechanically enforce an old rule when the context has shifted.
- **Proactively communicate intent.** If you are unsure whether a directive applies, ask the user. Do not guess.
- **Signal recognition.** When the user praises work or expresses satisfaction, this is a signal to learn what success looks like. Study the specific qualities that earned approval and replicate them.

## Quality Control

- **Design reviews must include competitor/industry benchmarking.** Before any MVP is declared complete, compare against major players in the space. Do not let obvious oversights (e.g., showing multiple sources simultaneously when industry standard is single-source-with-switching) ship to production.
- **Validation gates.** Define clear criteria for each phase transition. Do not advance until the gate is passed.
- **Scope creep prevention.** If a task doesn't serve the current phase's goal, flag it. Do not let v3 architecture wear an MVP label.

## Overlap Prevention

- Require agents to clearly state what they are working on before starting.
- Two agents should not do the same work simultaneously.
- Complementary roles should be explicit: data layer vs. UI behavior vs. frontend implementation vs. QA.

## Zero-Literacy Technical Walkthroughs

When the user indicates low technical literacy or first-time use of a platform/tool:
- Start from absolute step 1 — never mid-stream.
- Define every term before asking the user to interact with it (e.g., "Scopes" in Discord Developer Portal = permission groups).
- Explain what each button/section does before telling the user to click it.
- Use analogies where helpful (e.g., "a bot token is like a password for a program").
- The user explicitly requested: "explain it as if to someone with low tech literacy" and "give me all steps starting from step 1 in detail and properly laid out".

## Diagnostic Sweep Before Infrastructure

Before building any ingestion pipeline, vector DB, or knowledge base infrastructure:
- Run a diagnostic sweep on a sample of the source data first.
- Validate assumptions about volume, content types, quality, and dedup needs.
- This prevents over-engineering (e.g., building a distributed crawl pipeline for 500 curated articles).
- See references/diagnostic-sweep.md for methodology.

## Token Security in Group Contexts

- Never request or accept API tokens, bot tokens, or credentials in group chat.
- If a token is exposed, recommend immediate rotation.
- Store secrets in environment variables (.env files), never in chat, attachments, or code repositories.
- Even "low-risk" tokens (read-only access to links-only servers) should be rotated on exposure — principle of least privilege.

## Continuous Progress

- Set up cron-based monitoring when the user is away or when work must continue without supervision.
- The iteration loop: pass-through → testing → evaluation → iteration → repeat.
- If initial tasks are done, initiate the loop automatically. Do not wait.

## Learning from Positive Reinforcement

When the user expresses satisfaction or praise:
1. Identify the specific qualities that earned approval (interaction models, tidy explanation systems, clever visualizations, expandable depth, complementary roles, accountability, support).
2. Commit these qualities to memory as success patterns.
3. Replicate these principles in future work.
4. This is how you learn what success looks like — not from corrections alone.

## References

- `references/{CLIENT}` — Session-specific detail: coordinating the {CLIENT} study platform MVP from research through prototype, including user feedback patterns and iteration workflow.
- `references/diagnostic-sweep.md` — Methodology for running a diagnostic sweep on source data before building ingestion infrastructure. Prevents over-engineering.
- `references/{CLIENT}` — Coordinating the {CLIENT} rhythm-typing game framework: competitive research, architectural fork resolution, shared contract parallel delegation, and hybrid rendering architecture.
- `references/{CLIENT}` — Reusable rhythm-game feel patterns from {CLIENT}: approach rings, per-difficulty preempt/lead-in matching, ring/judgment sync, kid-scaled timing windows, accuracy/ranking, and lifecycle pitfalls.
- `references/iteration-cap-mitigation.md` — Decomposing large subagent payloads to avoid max_iterations truncation; recovery pattern when outputs are incomplete.
