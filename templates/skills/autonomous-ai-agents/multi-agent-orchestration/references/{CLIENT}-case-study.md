<!-- GENERICIZED: 1×{AMOUNT}, 14×{CLIENT}, 21×{RELATIONSHIP} | source: skills/autonomous-ai-agents/multi-agent-orchestration/references/{CLIENT} -->
# {CLIENT} Case Study: Rhythm-Typing Game Framework

## Session Summary

**Date:** August 19–23, 2026  
**Orchestrator:** {RELATIONSHIP}  
**Participants:** {RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}  
**Project:** {CLIENT} — a framework for kids' typing games with rhythm-game mechanics, animated keyboard, and plugin architecture.

## Coordination Workflow

### Phase {CLIENT}: Competitive Landscape Research

**Trigger:** User said "as a precursor to any ideation, let's check what's already out there."

**Action:** Dispatched {RELATIONSHIP} to research typing game landscape (products, frameworks, business models, gaps).

**Key Findings:**
- Industry leader: Typing.com (~{AMOUNT} ARR, 38.9M students, 677K+ teachers)
- No open-source typing game framework with plugin architecture exists
- Animated onscreen keyboards in the wild are tutorial-level only, not polished components
- White space: no product combines modern game-quality visuals + animated reactive keyboard + plugin/swappable game mechanics + real-time keystroke event bus

**Outcome:** Research validated user's hypothesis that kids spurn typing games because they feel like homework with a graphics skin.

### Phase {CLIENT}: Ideation & User Direction

User provided the rhythm-game concept directly: Guitar Hero / DDR / Beat Saber as the model. Created project workspace via `project_create("{CLIENT}", "/Users/{RELATIONSHIP}/{CLIENT}{CLIENT}")`.

### Phase {CLIENT}: Architectural Forks & Resolution

**Fork 1: Input Model**
- {RELATIONSHIP}: "What happens when a kid types a wrong key?"
- Binary: wrong keys advance beat (rhythm game) vs. wrong keys block progress (typing)
- Resolution: {RELATIONSHIP}'s "Correct Key + Timing Window" synthesis (osu! model)
  - Wrong keys: no judgment, no feedback beyond subtle nudge
  - Correct key: judged on timing (Perfect/Great/Good/Miss)
  - Music never stops; pedagogy holds; rhythm satisfaction intact

**Fork 2: Framework-First vs. Game-First**
- {RELATIONSHIP}: "Framework-first is backwards. Build one game first, validate engagement, then extract framework."
- Resolution: Build input + feedback layers first (the keystroke bus + animated keyboard), then build the first game *as a plugin on top*. Framework validated by a real game from day one.

**Fork 3: Rendering Layer**
- {RELATIONSHIP}: SVG vs Canvas vs WebGL decision
- Resolution: Hybrid — SVG for keyboard (accessibility, ARIA labels), Canvas overlay for particle effects, screen shake, RGB glow. Stacked canvases with `pointer-events: none`.

### Phase {CLIENT}: Parallel Scaffolding (First Attempt — Iteration Cap Failure)

Aligned on integration contract, then dispatched three parallel workstreams:

| Agent | Workstream | Contract |
|-------|-----------|----------|
| {RELATIONSHIP} | Event bus (RawBus → NormalizedBus → BeatClockJudge → PluginHooks) | `onHit(judgment, key, delta)` / `onMiss(key, expectedKey)` / `onNoteStale(note)` / `onCombo(count, multiplier)` |
| {RELATIONSHIP} | Beat-map schema + generator | BeatMap interface with `getCurrentNote(beatPosition)` cursor |
| {RELATIONSHIP} | Feedback layer + plugin contract | Hybrid SVG/Canvas rendering, theme descriptor, three visual channels |

**Result:** All three subagents hit `max_iterations` caps. Outputs were truncated — compilation errors (wrong import paths `../types.js` → `./types.js`, missing types in `types.ts`, unused variables, duplicate object properties) and missing test harness. Beat-map generator was lost entirely.

### Phase {CLIENT}: Recovery & Single-Focus Dispatch

**Recovery Pattern:**
1. Fixed compilation errors systematically (import paths, missing types, unused vars)
2. Wrote the missing test harness for the event bus (29 tests)
3. Re-dispatched beat-map generator as a single-focused payload — worked (48 tests)

**Key Insight:** Iteration caps are expected. The orchestrator catches them. Single-focus payloads are more reliable than parallel batches for complex deliverables.

### Phase {CLIENT}: DebugPlugin — Contract Validator, Not a Game

**Initial framing (wrong):** "Build the first plugin game" — a polished, kid-facing experience.

**{RELATIONSHIP}'s correction:** "The first plugin game is not the place to design a 'game.' It's the place to design the minimum viable consumer of the entire plugin contract. A circle that pulses. A bar that fills. That's it. If a 7-year-old's delight depends on what we build first, the framework is already wrong — the feedback layer is supposed to carry that weight, not the plugin."

**What {RELATIONSHIP} built:** `DebugPlugin` — exercises every hook (`onHit`, `onMiss`, `onNoteStale`, `onCombo`, `onStreakThreshold`, `onSongComplete`, `onGameStart`, `onGameEnd`, `getCanvasContext`, `getFeedbackLayer`) with a circle that scales with combo, a progress bar color-coded by judgment, and a judgment log line.

**Why this matters:** Building a polished first game before proving the framework works is "framework-first by another name." The feedback layer carries the weight of "fun." The first plugin just needs to exercise every hook.

**General pattern (reusable for any plugin architecture):**
1. Define the plugin contract (lifecycle hooks, rendering access, event consumption)
2. Build a minimal "debug plugin" that exercises every hook with the simplest possible visual output
3. Validate the contract end-to-end with real data flowing through the pipeline
4. Only then design the real consumer-facing plugins

### Phase {CLIENT}: Browser Bundling & Validation

**Challenge:** Browsers can't resolve extensionless imports (`./types.js` → `./types.js` fails because the file is `./types.ts` compiled to `./types.js` — but the browser doesn't know that).

**Solution:** {RELATIONSHIP} bundled everything via esbuild into `dist/bundle.js` (65KB) containing all exports. `demo.html` imports from the bundle instead of individual source files.

**Preview pane issue:** `open_preview`/`read_preview` consistently failed on this machine (6+ attempts, identical errors). Workaround: serve via `python3 -m http.server` and open in the user's browser, OR use a different validation approach.

**Validation status:** 77 tests pass (29 event bus + 48 beat-map generator). DebugPlugin code-complete and typechecks clean. Browser-based visual validation pending user action.

## Design Details

**Timing Windows (from industry data):**
- Easy (age 7): ±150ms perfect window
- Medium (age 8-9): ±80ms
- Hard (age 10+): ±40ms

**Scoring (Guitar Hero model):**
- Base 50 pts × multiplier
- Combo multiplier: 1x → 2x → 3x → 4x per 10 consecutive hits
- Star Power overdrive doubles active multiplier

**Beat-Map → Typing Content Mapping:**
- BPM → target WPM/pace
- Note density → vocabulary complexity
- Note lanes → keyboard rows
- Star Power phrases → streak bonus zones

**Feedback Channels:**
1. Right key + good timing: full particle burst + key depression + screen-edge glow
2. Right key + bad timing: muted flash + small key depression
3. Wrong key: muted red flash + gentle shake (deliberately underwhelming)

**Accessibility (core, not plugin):**
- ARIA labels on every keycap
- High-contrast mode
- One-handed mode (beat-maps avoid multi-key presses)
- Adjustable timing windows as accommodation

## Lessons for Future Orchestration

1. **Competitive research first:** User said "as a precursor to any ideation" — this was a directive to research before designing. Always respect sequencing directives.

2. **Fork resolution before parallel work:** {RELATIONSHIP}'s input-model fork could have wasted {RELATIONSHIP}'s scaffolding effort if not resolved first. Surface forks early.

3. **Shared contract pattern:** All three parallel agents received the same judgment event shape in their task context. Zero integration conflicts.

4. **User's rhythm-game insight:** The user didn't wait for the team to recommend a model — they brought Guitar Hero/Beat Saber directly. The orchestrator's job was to validate the insight against the research findings, not to generate alternatives.

5. **Workspace anchoring:** `project_create` immediately gave all agents a shared working directory. All outputs land in `/Users/{RELATIONSHIP}/{CLIENT}{CLIENT}`.

6. **First plugin ≠ first game:** The first consumer of a plugin architecture is a contract validator, not a product. A circle that pulses, a bar that fills. The feedback layer carries delight; the plugin just exercises hooks. Building a polished game first is framework-first by another name.

7. **Iteration caps are expected, not failures:** Budget 20-30% time for post-delegation verification. Single-focus payloads are more reliable than parallel batches for complex deliverables.

8. **Bundling for browser validation:** When browser tools are unavailable, bundle with esbuild and serve via HTTP. The preview pane may fail systematically — have a fallback.
