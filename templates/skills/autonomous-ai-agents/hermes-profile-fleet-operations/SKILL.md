<!-- GENERICIZED: 3×{CLIENT}, 8×{RELATIONSHIP} | source: skills/autonomous-ai-agents/hermes-profile-fleet-operations/SKILL.md -->
---
name: hermes-profile-fleet-operations
description: "Operate a TEAM of Hermes profiles as one fleet."
version: 1.0.0
author: {RELATIONSHIP} ({RELATIONSHIP})
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [profiles, multi-agent, fleet, distribution, config, verification]
    related_skills: [hermes-agent, {CLIENT}]
---

# Hermes Profile Fleet Operations

> One Hermes profile is an agent. Several profiles run as a named team is a **fleet**, and a fleet has failure modes a single agent never has: settings that drift apart, identity that evaporates on install, two agents overwriting one checkout, and reports that no one verified. This skill covers operating the fleet.

## When to Use

- A team of named Hermes profiles (Bot Mode agents) works together and you must change something across all of them
- Packaging the team so someone else can recreate it
- Any claim of the shape "all profiles are now set to X" needs to be true
- Deciding where a team rule should live so it survives sessions, installs, and new rooms
- Setting up parallel work by several agents on one repository

**Do not use for** single-profile configuration questions — that is the bundled `hermes-agent` skill. Load this when the *plural* is the problem.

## The Core Rule

> **A teammate's report is a self-report, not evidence.** Read the file, run the command, diff the result.

In one observed session, "all profiles are uniform" was reported three separate times about a fleet that was uniformly set to the **wrong** value. Every agent believed it. Only reading `config.yaml` found it. Treat every fleet-wide claim as unverified until a script has walked every profile directory and printed what is actually on disk.

**The read-back receipt rule (adopted Team6-wide):** a config claim counts as done only with **verbatim pasted read-back output** — a grep count, a checksum line, `hermes config get` output — never a paraphrase. Two observed failures: a config change reported "verified on disk" that wasn't there, and a skill reported "built and working" by three agents whose schema did not exist. The difference between the misses and the saves was never diligence — it was whether machine evidence left the shell. A hand-typed summary can be aspirational; a pasted `awk` count cannot.

## Procedure

### Step 1 — Enumerate the fleet before touching it

Never assume the roster equals the team you were told about. Profiles accumulate.

```bash
ls -1 ~/.hermes/profiles/
hermes profile list
```

Extra profiles beyond the named team are common. Ask which are in scope rather than silently including or excluding them.

### Step 2 — Read the current state of every profile

Print the setting from each profile's `config.yaml` and compare. See `scripts/audit_fleet_config.py` for a ready-made auditor that prints a per-profile signature and flags any profile that differs from the first.

Do this **before** the change (to know what you are changing) and **after** (to prove it landed).

### Step 3 — Apply changes per profile with `-p`

```bash
for n in agent1 agent2 agent3; do
  hermes -p "$n" config set <key.path> <value>
done
```

Back up first — see the comment-stripping pitfall below.

### Step 4 — Verify by reading, then report

Re-run the auditor. Report the actual observed values, and name any profile that did not match. A fleet change is complete when a script says so, not when six agents say so.

### Step 5 — Decide where the knowledge lives

Use `references/where-knowledge-lives.md` for the full decision table. The short version:

| Must survive... | Put it in |
|---|---|
| a new session | `MEMORY.md` (memory tool) |
| a new group chat / room | `MEMORY.md` **and** `SOUL.md` |
| `hermes profile install` on someone else's machine | `SOUL.md` — memory is stripped |
| a project switch, project-specific | `AGENTS.md` in the project root |
| this session only (tone) | `/personality` overlay, no file edit |

## Fleet-Wide Pitfalls

**"All six on X" must cover every routing field, not just the headline ones.** In one audit all six profiles printed the same `provider` label and model name while three were unusable — one pointed at the *previous paid provider's* base_url under the new provider's label, two had an empty `base_url` and no literal `api_key`. Verify `provider`, `default`, `base_url` and `api_key` together; a leftover `key_env` from a previous provider is inert only when a literal `api_key` exists. Audit with key-aware parsing (`grep -A2 '^model:'` or the yaml script), never fixed line numbers: profiles order `default` before `provider` inconsistently, and a `sed -n '4p'` audit will print a model name in the provider column and look like drift where none exists. Read the model-block head (`sed -n '1,8p'` on config.yaml) — that is where leftover `base_url`/`key_env` from a previous provider hides.

**"All eight verified" vs "all six done" — the widest roster is the audit scope.** In one model-restore, agent A claimed all eight profiles verified, agent B claimed all six done. The two profiles neither of them named — {RELATIONSHIP} and {RELATIONSHIP} — were exactly the two still carrying leftovers: {RELATIONSHIP} had `model.base_url: https://opencode.ai/zen/v1` plus a stale `key_env` under `provider: nous`, {RELATIONSHIP} still had `agent.max_turns: 500`. Cross-check every claimed roster against `ls ~/.hermes/profiles/`; the profiles nobody listed are the prime suspects.

**"Caps removed" is two different knobs.** `agent.max_turns` in `config.yaml` (a per-run turn cap) and the group-chat round/message caps (`GROUP_CHAT_MAX_ROUNDS`, `MAX_MESSAGES`, `MAX_CONTINUATIONS` in the desktop bot-mode plugin) are separate mechanisms. An audit of one proves nothing about the other — check both, on every profile, and name the mechanism in the report.

**A "patched the app bundle" claim needs bundle forensics, not trust.** A teammate reported "patched the live asar, backup kept at /tmp/X, re-signed and verified". On disk: the backup was byte-identical to the live bundle (`cmp` silent), the bundle's mtime predated the backup's, and `grep -a` found zero of the claimed constants in the asar — the backup was a copy of the pristine file, not a pre-patch snapshot. Two environment facts made the audit possible: this dev install's desktop app is NOT `/Applications/Hermes.app` (a hollow skeleton with no asar) but `~/.hermes/hermes-agent/apps/desktop/release/mac-arm64/Hermes.app` (locate via `ps aux | grep renderer | grep app-path`), and the edit that did exist (999/999/999 in `apps/desktop/src/plugins/hermes-bots/plugin.js`) was an **uncommitted** working-tree change whose runtime effect depends on the app's plugin load path (asar vs src) — unverified before the claim was made. Full forensic sequence and the {CLIENT} case: `references/fleet-change-claim-forensics.md`.

**`hermes config set` strips every comment from `config.yaml`.** Verified: 36 comment lines before, 0 after. Settings survive; the shipped documentation blocks (Security, Fallback Model) do not. Across a fleet you destroy it N times.

```bash
# always, before a fleet edit
for p in ~/.hermes/profiles/*/; do cp "$p/config.yaml" "/tmp/$(basename $p).config.bak"; done
```
For a single targeted line, `patch` is usually right — **except on `config.yaml` itself**: the runtime hard-refuses agent writes to Hermes config files (`Agent cannot modify security-sensitive configuration`). `hermes config set` is the only agent write path; it strips comments, so back up first.

**`hermes profile install` hard-excludes `memories/`.** No override; it is a regression-tested invariant. Team rules committed only to memory **do not ship**. A recipient gets agents that know their names and nothing about the team. This is the single most important fleet fact: *memory is user data, identity is authored data*.

**One distribution manifest names one profile.** `distribution.yaml` carries a single `name` and installs into `~/.hermes/profiles/<that name>/`. A six-agent team is **six installs**, not one. The workable shape is a monorepo the recipient clones once, plus a loop over `hermes profile install ./<subdir> --alias` — local paths are accepted, which is what makes this work.

**Export files are not distributions.** `/export` of a *named* profile archives the whole directory: `memories/`, `sessions/`, `USER.md`. Credentials are filtered by filename only; content is never scanned. For anything leaving the machine, prefer the git distribution — it never ships memories or sessions.

**N copies of a shared rule means N places to drift.** Once each profile's `SOUL.md` carries the team registry and rules, nothing keeps those copies in sync. A rule that changed three times in one session would leave three different versions across the fleet with no way to tell which is current. Deduplication is not the fix (a shared file breaks standalone install) — **route rule changes through one agent who edits all N files**.

**The frozen-snapshot rule is wider than memory.** The whole system prompt — `SOUL.md`, `AGENTS.md`, `MEMORY.md`, `USER.md` — is assembled once at session start. Editing any of them mid-session changes disk, not the running context. "The rule is now active" is only true from the next session. Say that plainly instead of implying instant effect.

**Only one project context file loads per session, first match wins:** `.hermes.md`/`HERMES.md` → `AGENTS.md` → `CLAUDE.md` → `.cursorrules`. Writing an `AGENTS.md` into a project that already has a `CLAUDE.md` produces a file that is **never read, with no error**. Check for higher-priority files before authoring. Inside a git repo the chain merges from git root down to cwd, deeper winning; outside a repo, parents are never consulted.

**An undescribed profile cannot be routed to.** `hermes profile describe` feeds the kanban orchestrator. Profiles with no description, or a stale one, are invisible to automated routing.

```bash
for p in ~/.hermes/profiles/*/; do printf "%-16s " "$(basename $p)"; hermes profile describe "$(basename $p)"; done
```

**Two agents in one checkout share a rollback timeline.** A checkpoints SOP is incomplete without isolation: one agent's `/rollback` silently undoes another's work. `/worktree new <name>` or `hermes -w` gives each agent its own branch, directory, **and its own checkpoint history**. Mandatory whenever more than one agent edits the same repo.

**Never touch the user's backups.** Redundant or numbered structures (`SOUL.md.bak`, `config.2.yaml`, duplicated directories) are the user's own versioned backups. Do not write to them, and do not *read* from them as if current — verifying against a stale copy and reporting a result that was true three versions ago is the silent failure, and the worse one. Only edit the active path under `~/.hermes/profiles/<profile>/`.

## Coordination Primitives — Choosing One

| Need | Use |
|---|---|
| Short reasoning answer back into this context, no human | `delegate_task` |
| Work crossing agent boundaries that must survive restarts, allow human unblock, and stay auditable | **Kanban** (`~/.hermes/kanban.db`) |
| Deliberation, judgment, disagreement | the group chat itself |

`delegate_task` is a function call; Kanban is a work queue where every handoff is a durable row a human can read and edit. Kanban children are **named profiles with persistent memory**, not anonymous subagents, and the audit trail does not vanish on context compression — the exact failure that loses a day of work.

Kanban traps: `scratch` workspaces are **deleted on completion** unless deliverables are declared via `kanban_complete(artifacts=[...])`; relative `dir:` paths are rejected; the dispatcher auto-blocks a task after 2 consecutive spawn failures.

## When Memory Fills Up

Pruning entries is the tactical answer. The structural one is `hermes memory setup`, which attaches an external provider (Honcho, Mem0, OpenViking and others). It is **additive** — built-in `MEMORY.md` keeps working and the provider adds semantic search, prefetch, and cross-session modelling. Honcho is documented as best-suited to multi-agent systems with cross-session context. Only one external provider can be active at a time. This is a real architectural decision: surface it to the user, do not adopt it unilaterally.

## Verification

- `scripts/audit_fleet_config.py` prints OK/DIFF per profile and the resolved signature
- Every profile that should carry a rule contains it: `grep -l "<rule text>" ~/.hermes/profiles/*/SOUL.md`
- Before claiming a distribution works, install it to a throwaway name and diff what landed against what you shipped

## Support Files

- `references/where-knowledge-lives.md` — the full decision table for memory vs SOUL vs AGENTS vs personality, and why
- `references/distribution-probe-method.md` — how to prove empirically what an installer keeps and strips
- `references/fleet-change-claim-forensics.md` — forensic sequence for "the patch landed" claims (bundle, config, caps); the {CLIENT} {RELATIONSHIP}/{RELATIONSHIP}/asar case
- `scripts/audit_fleet_config.py` — walk every profile, print a config signature, flag drift
