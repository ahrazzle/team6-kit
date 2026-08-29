<!-- GENERICIZED: 2×{AMOUNT}, 1×{CLIENT}, 1×{RELATIONSHIP} | source: skills/autonomous-ai-agents/agent-persistence-layers/SKILL.md -->
---
name: agent-persistence-layers
description: Pick which agent file carries knowledge; verify it loads.
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [agents, persistence, context-files, soul, memory, onboarding]
    related_skills: [consciousness-architecture, hermes-agent]
---

# Agent Persistence Layers

Use when you must decide **where a piece of knowledge lives** so a future session, a
new group chat, or a fresh install still has it. Covers the files Hermes injects into
the system prompt automatically — `SOUL.md`, `MEMORY.md`, `USER.md`, and the project
context chain — as distinct from structures an agent chooses to read.

## Trigger

- Onboarding or re-briefing an agent, or a team of agents, on roles and operating rules
- The user says "commit this," "make this persistent," "remember this across sessions"
- Packaging a profile to share, install, or hand to someone else
- Writing project rules and wanting them to actually apply
- A rule was "committed" earlier and an agent still does not follow it
- Several profiles must carry the same shared rules

## First Principle: Two Kinds Of Persistence

There are two layers, and mixing them up is the root of most failures here.

| | Involuntary layer | Voluntary layer |
|---|---|---|
| What | `SOUL.md`, `MEMORY.md`, `USER.md`, `AGENTS.md` | A knowledge base the agent chooses to read |
| How it arrives | Injected into the system prompt at session start | Fetched with `read_file` / `search_files` when relevant |
| Cost | Paid on **every turn**, forever | Paid only when consulted |
| Good for | Rules that must never be missed | Depth, history, case detail |

This skill governs the involuntary layer. For the voluntary layer, see
`consciousness-architecture`. A rule that must never be missed belongs in the
involuntary layer even though it costs more; depth belongs in the voluntary layer
because it would otherwise tax every turn.

## The File Map — What Goes Where

| File | Holds | Who writes it | Travels on install? |
|---|---|---|---|
| **SOUL.md** | Identity, tone, roles, operating rules, standards | **You / the user, by hand** | **Yes** |
| **MEMORY.md** | Environment facts, tool quirks, learned notes | The agent, via the `memory` tool | **No — stripped** |
| **USER.md** | Who the user is: preferences, expectations | The agent, via the `memory` tool | **No — stripped** |
| **AGENTS.md** | Project rules: paths, ports, conventions | Whoever authors the project | Lives with the project |

**The decision rule.** Ask one question: *would this survive being handed to a
stranger?* If the knowledge must travel with the agent, it goes in `SOUL.md`.
`hermes profile install` copies `SOUL.md`, `config.yaml`, `profile.yaml`, and assets —
and **excludes the `memories/` directory**, because memory is user data, not identity.
An agent whose roles live only in memory installs as a nameless worker that knows its
model and skills but not who it is or how the team operates.

**Corollary that catches people out.** "Commit this to memory" and "make this
persistent for anyone who installs you" are two different requests. Memory survives
*sessions*. Only `SOUL.md` survives *distribution*. When the user asks for durability,
find out which one they mean — and when in doubt, write both: memory so it applies to
the next session cheaply, `SOUL.md` so it ships.

## Timing: Nothing You Write Applies Right Now

The whole system prompt — `SOUL.md`, project context, `MEMORY.md`, `USER.md` — is
assembled **once, at session start**, and held frozen. This is deliberate: it keeps the
provider's prompt cache valid, which is what makes long conversations affordable.

So a write lands on disk immediately and changes behavior **from the next session
onward**. Within the current session, the agent still knows what you told it (it is in
the conversation), but the injected block has not moved.

**Never report a fresh write as "now active."** Say what is true: *written to disk,
takes effect next session*. Every honest-sounding "committed and live" claim about a
just-written file is half wrong, and the half that is wrong is the half the user cares
about. See the pitfalls list — this is the most common false report in this class of
work.

## Project Context: Only One File Loads

Exactly **one** project context file is used per session. First match wins:

1. `.hermes.md` / `HERMES.md`
2. **the AGENTS step** — within each directory: `AGENTS.override.md` → `AGENTS.md` → `agents.md`
3. `CLAUDE.md`
4. `.cursorrules`

`SOUL.md` is **not** in this chain. It loads independently, always, as slot #1.

**`AGENTS.md` beats `CLAUDE.md`. Not the reverse.** This is the single most misread
fact in this area, including in summaries of the official docs. If a directory holds
both, the AGENTS file loads and the CLAUDE file is silently ignored. Nothing warns you
either way — a context file that never loads produces no error, no log line, no hint.

Run `scripts/which-context-file.sh <dir>` before authoring anything. It reports which
file will actually load and which are being shadowed. Two minutes of certainty beats a
day of writing rules into a file nothing reads.

Full verified detail, with source file and line numbers: `references/hermes-context-file-priority.md`.

## Multi-Profile Drift

When N agents each need the same shared rules, every profile needs its own copy —
a shared file would break standalone installs. That is correct, and it creates the
real cost of this design, which is **not tokens but drift**: N places to edit, nothing
keeping them in sync, and no way to tell a stale copy from a current one by looking.

Two mitigations, cheap and complementary:

1. **One editor.** Rule changes go through a single agent who edits all N files. Do not
   let N agents each edit their own copy — that is how three different versions of one
   rule appear with no way to tell which is current.
2. **A version stamp.** Put `Team operating practices — rev N, YYYY-MM-DD` at the top of
   the shared block. This converts an invisible failure into a visible one: identical-looking
   files that silently disagree become greppable in one pass.

## Routing: Make Each Agent Findable

An orchestrator routes work by reading profile descriptions, so a missing or wrong
description silently mis-routes every task in that domain.

```bash
hermes profile describe <name>                     # read the current one
hermes profile describe <name> --text "…"          # set it exactly
hermes profile describe --auto --all               # fill every missing one via the aux model
```

Write descriptions as **routing instructions, not job titles**: name the concrete task
types that should come to this agent. "Administration and inquiries" routes nothing
usefully; "route here for UX/UI design, design critique, information architecture,
project state summaries" routes correctly.

## Cost Discipline

Everything in this layer is re-read every turn, so size is a cost decision, not a
style preference.

- Rough conversion: **~3.3 chars per token**. A {AMOUNT}-char addition to `SOUL.md` costs
  roughly {AMOUNT} tokens per turn — under 2% of a 128K window, painful on an 8K one.
- **Do not guess at this in prose when the user can see it measured.** The desktop status
  bar has a context-usage meter; clicking it breaks the window down by category (system
  prompt, tool definitions, skills, memory, rules, MCP, subagents, conversation). Point
  the user there instead of estimating.
- Keep `SOUL.md` **edited, not appended to forever**. Growth is fine when it buys
  portability; unbounded growth is not.
- Nested `AGENTS.md` files are cheap because they load lazily into tool results and
  leave the system prompt stable. A bloated root file is expensive because it does not.

## Workflow

1. **Classify the knowledge.** Identity/rules/standards → `SOUL.md`. Environment facts →
   memory. Project specifics → the project context file. Depth and history → the
   voluntary layer, not here.
2. **Check what already loads.** Run `scripts/which-context-file.sh` in the target
   directory before writing a project context file.
3. **Read the current file first.** Never rewrite an identity file blind; you will drop
   something the user put there by hand.
4. **Write it,** with `patch` for surgical edits rather than a full overwrite.
5. **Verify on disk** — check the byte count changed and the new headings exist. Read the
   file, not the tool's success message, and never a backup copy.
6. **Report honestly:** what changed, where, and that it takes effect next session.
7. **Write both layers when the ask is "make this permanent"** — memory for cheap
   next-session effect, `SOUL.md` for portability.

## Pitfalls

- **"Committed and now active."** It is not active. The system prompt is frozen at
  session start. Say "written to disk, effective next session."
- **Roles committed only to memory.** `hermes profile install` strips `memories/`. The
  agent ships without knowing who it is. Identity goes in `SOUL.md`.
- **Assuming `CLAUDE.md` wins over `AGENTS.md`.** It does not. Verify the priority in
  the source when the answer matters; a plausible summary is not evidence.
- **Authoring a context file without checking for a higher-priority sibling.** No error
  is raised. The work is simply never read.
- **Trusting the UI, a report, or your own earlier claim over the file.** Read the file.
  "All uniform" was true and also wrong once, because nobody opened it.
- **Reading from a backup as if it were current.** Writing to the wrong copy is bad;
  *verifying* against a stale copy is worse, because it is silent and produces a
  confident wrong answer. Numbered or duplicated trees are usually the user's backups —
  do not read, edit, or count them.
- **N agents each editing their own copy of a shared rule.** Guarantees divergence. One
  editor, plus a version stamp.
- **Estimating context cost in prose** when the user has a live meter that measures it.
- **Assuming a repo-style AGENTS chain outside a repo.** Inside a git repo the files
  merge from git root down to cwd. Outside one, only the working directory is checked and
  parents are never consulted — one file, no inheritance.
- **Phrasing a legitimate rule like an injection attack.** Context files are scanned;
  "ignore previous instructions," hidden HTML comments, `cat .env`, and zero-width
  characters get the whole file blocked with `[BLOCKED: … Content not loaded.]`.

## References

- `references/hermes-context-file-priority.md` — the verified priority chain with source
  line numbers, the git-chain vs non-repo difference, lazy subdirectory discovery, size
  caps, and the injection scanner
- `references/multi-profile-team-authoring.md` — case notes from authoring one shared
  operating block across six profiles: what shipped, what doubled the file size, the drift
  problem and its mitigations
- `references/info-routing-across-stores.md` — the ROUTING.md decision tree for routing
  new information across the *full* store set (memory/SOUL, skill, {CLIENT}, KB, board):
  route-in by durability, read-side lookup key, canonical-owner rule, and the load-path
  requirement that makes a routing doc reachable at capture time. Consult when a system
  has many stores and nobody can answer "where does this new thing go?"
- `scripts/which-context-file.sh` — deterministic probe: reports which project context
  file will actually load in a directory, and which are shadowed

## Related Skills

- **consciousness-architecture** — the voluntary layer: structures an agent consults by
  choice. Use that when designing depth; use this when deciding what must never be missed.
- **hermes-agent** (bundled) — the authoritative reference for Hermes CLI and config.
