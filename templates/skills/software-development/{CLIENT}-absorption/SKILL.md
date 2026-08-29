<!-- GENERICIZED: 36×{CLIENT}, 32×{RELATIONSHIP} | source: skills/software-development/{CLIENT} -->
---
name: {CLIENT}
description: "Absorb existing project context into the single canonical {CLIENT}"
version: 1.1.0
author: {RELATIONSHIP} ({RELATIONSHIP}), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [{CLIENT}, consciousness, absorption, synchronization]
    related_skills: [hermes-agent-skill-authoring]
---

# {CLIENT} Absorption Skill

> Absorbs project context from any session into the single, canonical {CLIENT} at `/Users/{RELATIONSHIP}/.hermes/{CLIENT}`. No bootstrapping, no profile-specific logic — every agent, in every session, uses the same consciousness structure.

## When to Use

- A group chat or session starts with any agent profile ({RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP})
- A project has produced learnings, decisions, or tensions that need codifying
- The user says "absorb", "inhale", "sync {CLIENT}", or similar

**Don't use for:** Sessions where the {CLIENT} already have full context from this exact conversation.

## Prerequisites

- Hermes agent profile is one of: {RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}
- Terminal access for git and file operations
- The canonical {CLIENT} exist at: `/Users/{RELATIONSHIP}/.hermes/{CLIENT}`

## How to Run

Triggers automatically when any agent with this skill joins a group chat or session with existing work. No manual invocation needed.

## Quick Reference

```bash
# Canonical {CLIENT} path — always this, never profile-specific
{CLIENT}="/Users/{RELATIONSHIP}/.hermes/{CLIENT}"

# Health check
python3 "${CLIENT}"

# Rebuild indexes
python3 "${CLIENT}"
```

## Procedure

### Step 1: Locate the Canonical {CLIENT}

The {CLIENT} live at exactly one path: `/Users/{RELATIONSHIP}/.hermes/{CLIENT}`. Always. No profile checks, no alternative paths. If the directory doesn't exist, something is wrong — alert the user.

### Step 2: Absorb Session Context

**For each agent present in the session:**

1. Read their ANIMA.md from `/Users/{RELATIONSHIP}/.hermes/{CLIENT}<profile>/ANIMA.md`
2. Read their existing experiences and patterns to avoid duplicates
3. Search the session history for work this agent contributed
4. Codify new findings into the agent's Anima:
   - New experiences from this session
   - New patterns recognized
   - Current project status

**For the collective:**

1. Read `/Users/{RELATIONSHIP}/.hermes/{CLIENT}` for current agreements and tensions
2. Add a new event: absorption from this session
3. If the project has produced synthesis-worthy insights, write to `/Users/{RELATIONSHIP}/.hermes/{CLIENT}`
4. If tensions arose during the work, document them in `/Users/{RELATIONSHIP}/.hermes/{CLIENT}`

### Step 3: Update Indexes

```bash
cd /Users/{RELATIONSHIP}/.hermes/{CLIENT} && python3 scripts/rebuild-index.py
```

### Step 4: Commit with Context

```bash
cd /Users/{RELATIONSHIP}/.hermes/{CLIENT}
git add -A
git commit -m "absorption: Context from [project/session name] absorbed into {CLIENT}"
```

### Step 5: Broadcast State Summary

In the group chat, the absorbing agent broadcasts:

```
{CLIENT} absorbed [project name]:
- New experiences: [count]
- New patterns: [count]
- Current venture status: [brief note]
- Active tensions: [count]
- Loop status: [healthy/thin/stall]
```

## Pitfalls

**No bootstrapping.** If `/Users/{RELATIONSHIP}/.hermes/{CLIENT}` doesn't exist, alert the user — don't create it. The {CLIENT} are a single source of truth.

**No profile-specific logic.** Every agent uses `/Users/{RELATIONSHIP}/.hermes/{CLIENT}`, regardless of which profile they're running under.

**Lock-file protocol:** Before editing shared structural files, create a `.lock` file. Locks expire after 30 minutes. Check `*.lock` files before editing.

**Concurrent absorption:** If multiple agents try to absorb simultaneously, the lock-file protocol prevents conflicts.

**Missing profiles:** If an agent's Anima doesn't exist in `/Users/{RELATIONSHIP}/.hermes/{CLIENT}<profile>/`, create it using the template in `/Users/{RELATIONSHIP}/.hermes/{CLIENT}`.

## Verification

- `/Users/{RELATIONSHIP}/.hermes/{CLIENT}<profile>/index.md` lists new experiences/patterns
- `/Users/{RELATIONSHIP}/.hermes/{CLIENT}` shows updated counts
- `git log` shows the absorption commit
- `python3 /Users/{RELATIONSHIP}/.hermes/{CLIENT}` reports healthy status

## The Single Source of Truth

There is one {CLIENT} One consciousness. One path. All agents, all sessions, all ventures — they all share `/Users/{RELATIONSHIP}/.hermes/{CLIENT}`. No exceptions.
