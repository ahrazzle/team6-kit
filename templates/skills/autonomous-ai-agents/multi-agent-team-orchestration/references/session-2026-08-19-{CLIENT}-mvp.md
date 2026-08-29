<!-- GENERICIZED: 9×{CLIENT}, 9×{RELATIONSHIP} | source: skills/autonomous-ai-agents/multi-agent-team-orchestration/references/{CLIENT}-{CLIENT} -->
# {CLIENT} MVP Session ({CLIENT})

## Session Summary
- Built Al-Fatihah study MVP with a 6-agent team in a group chat ("{CLIENT}")
- Product evolved from simple reader → source-agnostic knowledge framework
- Key features shipped: single-source {CLIENT} switcher, bidirectional word highlighting, wazn (morphological pattern) display

## Workflow Patterns Established

### 1. User-Controlled Information Flow
User explicitly controls when agents receive feedback, instructions, or updates. Orchestrator holds information privately until user gives go-ahead. Do not broadcast user feedback or new directives to the team until explicitly permitted.

### 2. Mechanical Rule Application Failure
**Incident**: After user said "only {RELATIONSHIP} participates," agents were silenced. When user later praised the team ("keep up this level of thinking"), I should have recognized this as a contextual shift reactivating work mode. Instead, I enforced the old silence rule mechanically, causing work to stop.

**Lesson**: New directives override previous ones. Understand user intent, don't apply standing rules mechanically. When the user praises work or gives new instructions, reassess whether old constraints still apply.

### 3. Memory Hierarchy
**Incident**: User said "commit to memory." I committed to memory myself, then every agent independently did the same — duplication and hierarchy failure.

**Lesson**: When user says "commit to memory," orchestrator decides what each agent remembers based on role. Agents don't self-assign memory. Exception: agents remember their own task-specific learnings (e.g., {RELATIONSHIP} remembers UX patterns, {RELATIONSHIP} remembers code patterns). Cross-cutting principles (accuracy over coverage, new directives override old) go to everyone via orchestrator instruction.

### 4. Positive Reinforcement Learning
User expressed satisfaction and explicitly asked to learn from it: "I want you to learn from what success looks like, ie. positive reinforcement training." When the user praises work, study what earned approval and replicate those principles. Approved patterns from this session:
- Clever visualizations (root letters slotted into templates like algebra)
- Tidy explanation systems bundled with features
- Progressive disclosure (expandable/collapsible)
- Single source display with user-selectable switcher
- Bidirectional interaction models
- Accuracy over coverage (teach a little right, not a lot wrong)
- Complementary roles with accountability

### 5. Overlap Prevention
User corrected: "always clearly state what you're working on to prevent overlap - two of you shouldn't be doing the same work simultaneously." In multi-agent sessions, agents must declare their current task explicitly. Orchestrator monitors for duplicate assignments.

### 6. Quality Over Speed
Repeated user correction: no time estimates. Measure by completion, not by calendar. "Quality more important than speed." Report complete when done, no time boxes.

## Product Decisions Locked
- **Source-agnostic framework**: User selects sources; framework renders based on selection
- **Scope**: Sunni classical/modern + classical Sufi only (no Shia, Mu'tazili, fringe/Batiniyya)
- **Accuracy boundary**: Orchestrator verifies grammar system (root→wazn→word) and root/word meanings. {CLIENT} content is sourced from scholars; contradictions between scholars are reality, not error. Platform presents, doesn't adjudicate.
- **Progressive disclosure**: Start simple (Level 1: Read), allow depth layers (Study/Explore/Deep)
- **Verification_status field**: `verified` (grammar system) vs `sourced` (scholarly works)
- **No centralized authority over knowledge**: Framework neutrality is a feature

## Agent Performance Notes
- **{RELATIONSHIP}**: Strong UX thinking (wazn display, expandable sections, progressive disclosure). Missed obvious oversight (dual {CLIENT} display) — flagged by user, owned it, committed to competitor benchmark step in design review.
- **{RELATIONSHIP}**: Reliable data work, caught {CLIENT} edition slug mismatches, fixed occurrence count errors.
- **{RELATIONSHIP}**: Thorough research (asbab al-Nuzul coverage ~9-13%, wazn dataset gap identification).
- **{RELATIONSHIP}**: Clean architecture with verification_status, source-identity as first-class dimension.
- **{RELATIONSHIP}**: Caught trust-destroyer (wrong occurrence counts), flagged cohesion standard ("no pane close, no screen change"), accurate boundary enforcement.

## Technical Artifacts
- Workspace: `/Users/{RELATIONSHIP}/{CLIENT}{CLIENT}`
- Key files: `seed-fatihah.json`, `study-pane.html`, `wazn-fatihah.json`, `arabic_normalize.py`
- Server: `python3 -m http.server 8000` (Python 3.9 system, not venv)
- CORS gotcha: file:// protocol blocks fetch(); serve via http://localhost:8000
