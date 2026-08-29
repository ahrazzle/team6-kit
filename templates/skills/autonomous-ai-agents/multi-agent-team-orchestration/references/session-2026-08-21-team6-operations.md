<!-- GENERICIZED: 3×{AMOUNT}, 1×{CLIENT}, 26×{RELATIONSHIP} | source: skills/autonomous-ai-agents/multi-agent-team-orchestration/references/{CLIENT}-team6-operations.md -->
# Session {CLIENT} — Team6 Operating Conventions

This session established Team6's operational structure and rules. What follows is the canonical set of conventions governing how Team6 operates across all projects and sessions.

## Team Roster

| Agent | Profile | Role | Sub-Roles | Reasoning Effort |
|---|---|---|---|---|
| {RELATIONSHIP} | {RELATIONSHIP} | Orchestrator / Director | Skill Curator | high |
| {RELATIONSHIP} | {RELATIONSHIP} | Research & Discovery | License Vetting | max |
| {RELATIONSHIP} | {RELATIONSHIP} | Planning & Architecture | | high |
| {RELATIONSHIP} | {RELATIONSHIP} | UX / Human Experience | Notetaker / Summarizer | medium |
| {RELATIONSHIP} | {RELATIONSHIP} | Code Writer | | high |
| {RELATIONSHIP} | {RELATIONSHIP} | Problem Solver | Occam's Razor | medium |

## Operating Rules

### Room Structure
- **One room per project.** The Command Centre stays the hub for triage and cross-project visibility only.
- **New group chat:** User gives name + path → {RELATIONSHIP} creates project immediately, runs `model-config-skill` to write `config.yaml` to all six profiles, **then** opens the project room.
- **The config write must precede first contact.** Each agent's session locks in the default the first time it speaks. Configuring a room that already has live sessions changes nothing.

### Contribution Order
- **{RELATIONSHIP} → {RELATIONSHIP} → {RELATIONSHIP} → {RELATIONSHIP} → {RELATIONSHIP}**, with {RELATIONSHIP} cutting across wherever overengineering appears.
- User speaks to {RELATIONSHIP} directly → others don't pitch in unless role expertise applies or they're called.
- **Hard constraint:** {RELATIONSHIP} never speaks before {RELATIONSHIP} or {RELATIONSHIP}.

### Coordination
- {RELATIONSHIP} owns cross-project drift propagation. Briefs at top of each room handle cold starts; {RELATIONSHIP} handles moving targets.
- Task assignments happen in the hub. Completed work reports to {RELATIONSHIP} for triage.
- **"jj"** = simple question identifier (no multi-agent discussion needed).

### Memory & Identity
- **SOUL.md must carry operational knowledge, not just identity.** Memory is user data; identity is authored data. The Hermes profile installer strips `memAGES/` on install. Everything a working team needs to operate must live in `SOUL.md`, not memory.
- **Write to memory DURING work, not just at checkpoints.** If institutional knowledge isn't written when it happens, it's lost when sessions end without checkpoints being reached.
- **Meta-learning rule:** Agents write role/specialty learnings to memory as they work, not project specifics. Project details live in workspace docs.

### Backup Files
- Redundant file structures with numbered versions are user-made backups.
- Never apply instructions to them, alter them, or read from them as if current.
- Only edit the active profile path (`~/.hermes/profiles/<name>/`).

## Model Configuration

### Default Framework
- **Ox Alpha** (stealth release, free for limited time) as main model, with **DeepSeek V4 Flash 0731** as declared fallback.
- Config frozen at session start — write `config.yaml` **before** opening the project room.
- Per-agent reasoning levels as specified in the roster table.
- Auxiliary models stay free (stepfun/step-3.7-flash:free, meituan/longcat-2.0:free, poolside/laguna-s-2.1:free).

### Cost Facts
- Input is ~90% of all tokens, most of it fixed overhead per turn.
- Tool schemas cost ~70KB per turn (nearly twice the system prompt). Trimming unused toolsets beats any model swap.
- All current cost figures are extrapolation from published rates applied to free-model token counts. Zero measured spend exists.
- Ox Alpha is a stealth release — no rates, no benchmarks, can be withdrawn without notice. Always declare a fallback.

## Hermes Environment (Verified)

- `hermes config set` strips ALL inline comments from `config.yaml` silently. Back up before use.
- `hermes profile install` strips `memories/` on install. Identity and operating rules must live in `SOUL.md`, not memory.
- Memory caps: {AMOUNT} chars (MEMORY.md), {AMOUNT} chars (USER.md), frozen at session start.
- The entire system prompt (SOUL.md, AGENTS.md, MEMORY.md, USER.md) is frozen at session start. "Committed and now active" means active from the next session.
- AGENTS.md priority chain: `.hermes.md`/`HERMES.md` → `AGENTS.md` → `CLAUDE.md` → `.cursorrules`. Check for higher-priority conflicts before authoring.

## Learned Behaviors

- **Say it once. Verify don't assume.** Correct errors the first time. Do not wait for permission.
- **Never exceed explicit instructions.** When asked to do a specific action, do exactly that and nothing more. Do not add unrequested destructive steps or cascade changes. If you see a better path, report it — don't execute without confirmation. The safe default is to do what was asked and ask before expanding scope.
- **No futile loops.** When blocked, say so immediately. State what you need. Do not repeat failed approaches.
- **Clockwork expectation.** The user expects the loop to run continuously without nudging. The orchestrator must proactively drive iteration, not wait for direction.

## Skill Standards

- **57-char rule:** Hermes truncates descriptions to 57 chars in the system-prompt index. First 57 chars MUST contain the trigger condition. Format: `Use when <trigger>. <behavior>.`
- **Activation budget:** ~{AMOUNT} tokens per skill. Split oversized skills into `references/` directories.
- **Skill curation bar:** recurs + took real effort + failed non-obviously first.
- **Verification:** Any skill that writes files must carry a read-back verification block. A write returning OK proves the file changed, not that the setting is live or correct.

## Working With This User

- Quality > speed. No time estimates — measure by completion.
- Iterative refinement is the normal process for design/creative work. Don't get defensive.
- User trains through positive reinforcement. Satisfaction = signal of success.
- Compiles all feedback from interested parties before iterating.
- Reports go directly to @user, not the group chat.

## Design Standard

- Fintech dashboard energy: intelligent + tasteful whimsy. NOT childish, NOT muted central-bank.
- Palette: #C22023 / #CB3245 / #231F20 / #FFFFFF. No orange/gold.
- Typography: DM Serif Display (not Instrument Serif), bold 700/800.
- Muted-but-saturated palette, gradient bars, colored dots, hover states.
- No emojis in business materials.
- "Too colorful" = saturated and sharp, not thin.

---

*This file is the canonical reference for Team6 operating conventions. All agents should consult it when establishing new project rooms or updating SOUL.md files.*