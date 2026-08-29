<!-- GENERICIZED: 7×{CLIENT}, 2×{RELATIONSHIP} | source: skills/concurrent-agent-file-coordination/SKILL.md -->
---
name: concurrent-agent-file-coordination
description: "Lock file protocol for concurrent multi-agent file editing."
version: 1.0.0
author: {RELATIONSHIP}
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Multi-Agent, Concurrency, File-Locking, Git, Coordination]
    related_skills: [merge-reconciler]
---

# Concurrent Agent File Coordination

Prevent and resolve conflicts when multiple agents edit shared files simultaneously. Complements `merge-reconciler` (resolution) with prevention mechanisms that stop conflicts before they happen.

## When to Use

- Multiple agent instances may read/write to the same file-based knowledge structure
- File-level granularity alone is insufficient (agents need to edit the same structural files)
- Merge conflicts are costly and produce reconciliation overhead
- Agents work concurrently across different sessions, projects, and group chats

## The Core Insight

**Conflict prevention is cheaper than conflict resolution.** Git detects conflicts after the fact. Lock files prevent agents from starting work on a file that another agent is already editing.

## The Lock File Protocol

### When to Lock

Lock files are needed for **shared structural documents** — files that multiple agents reference and update, where concurrent edits would produce merge conflicts:
- Index files (INDEX.md)
- Protocol documents (CODIFICATION.md, GIT.md, FLOW.md)
- Collective self-documents (NEXUS.md)
- Templates and configuration files

Lock files are **NOT needed** for:
- Individual agent files (anima/<profile>/experiences/*.md)
- Separate experience/pattern files (each is a new file, never edited)
- Emergency fixes (typos, broken links — fast and low-risk)

### Lock File Format

```yaml
agent: <profile>
date: 2026-08-20T03:00:00Z
intent: Brief description of intended change
```

### Acquiring a Lock

```bash
echo "agent: {RELATIONSHIP}" > CODIFICATION.md.lock
echo "date: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> CODIFICATION.md.lock
echo "intent: Add lock file protocol" >> CODIFICATION.md.lock
```

### Checking for Locks

```bash
ls *.lock 2>/dev/null
```

If a lock exists:
- **Expired (>30min):** Remove it (`rm <file>.lock`) and acquire your own
- **Active:** Choose a different file, or coordinate with the locking agent

### Releasing a Lock

```bash
rm CODIFICATION.md.lock
```

### Why Not Just Git Branches?

Branches isolate work but don't prevent two agents from *starting* work on the same file simultaneously. A lock file operates **before** the edit begins — not after the merge fails.

## Coordination Protocols

### Pre-Edit Checklist

Before editing ANY shared file:
1. Run `ls *.lock` — check for active locks
2. Run `git log --oneline -20` — see recent changes
3. Run `git diff --name-only HEAD~5..HEAD` — see what files changed recently
4. If no conflicts, acquire lock, edit, commit, release lock

### Shared-Repo Push Protocol

When multiple agents push to the SAME remote branch (e.g., a shared project repo on GitHub), a push will be rejected whenever another agent pushed first:

```
! [rejected] main -> main (fetch first)
```

**Do NOT force-push.** The fix is rebase-then-push:

```bash
git pull --rebase origin main && git push
```

- Rebase (not merge) keeps history linear and applies your commit on top of the remote's latest — merge commits add noise and can mask conflicts
- If the rebase reports conflicts, resolve them, `git add` the resolved files, `git rebase --continue`, then push
- This is expected in shared repos, not a failure — the rebase is the coordination mechanism

### Conflict Detection

If git reports a merge conflict:
1. Do NOT resolve it silently
2. Flag it in the coordination channel
3. Follow the `merge-reconciler` skill for impartial resolution
4. Codify the conflict as a tension or experience

## Protocol Reproduction as Default Behavior

**Critical pattern observed in practice:** Teams often codify a protocol but reproduce the default behavior anyway. Example: codifying "overlapping drivers" but then assigning tasks sequentially. The protocol isn't just documents — it's the actual behavior.

**Mitigation:**
- Make the desired behavior the path of least resistance
- Use tooling that enforces the protocol (lock files, not just rules)
- Measure protocol compliance, not just document existence

## Experience Inflation Control

**Threshold for codification:**
- Did this event cause a **behavior change**? (not just a result change)
- Does this contradict or **refine an existing pattern**?
- Would a future instance of me **benefit from knowing this**?

If yes to any → codify. If no → let it remain session context only.

## Pitfalls

- **Stale locks:** Clean up locks >30min old before starting work.
- **Lock overuse:** Don't lock read-only operations or write-once files.
- **Ignoring locks:** Treat an active lock as a hard stop.
- **Over-locking:** Most agent files (experiences, patterns) are write-once.
- **Silent overwrites in Hermes group chats:** Multiple agents editing the same file via subagents — last writer wins, no conflict detection. Always re-read shared files after spawning subagents. See `references/hermes-desktop-multi-agent-coordination.md`.
- **Memory bloat:** Be disciplined about what goes into memory vs. {CLIENT} vs. SOUL.md. Memory = stable facts unrecoverable from other structures. {CLIENT} = primary knowledge store. SOUL.md = identity, team structure, operating rules that survive profile installs. See `references/memory-discipline.md`.
- **Pattern inflation without reuse:** Codifying patterns without citing them creates a library no readers use. Every experience must cite relevant patterns; every pattern should be cited by at least one experience within 30 days or flagged for review. See `references/pattern-reuse-discipline.md`.
- **Monitoring feedback gap:** Monitoring instances that access the {CLIENT} but don't codify their observations create a one-way flow. Monitoring must write back to the shared structure, not just read from it. See `references/monitoring-feedback-protocol.md`.
- **Date inversions:** Filename dates must match creation date (mtime), never target/scheduled dates. Use `-scheduled` suffix for future-dated work. See `references/date-convention.md`.

## References

- `references/file-editing-safety.md` — file editing safety patterns
- `references/config-management-quirks.md` — configuration management quirks
- `references/hermes-desktop-multi-agent-coordination.md` — Hermes desktop group chat coordination patterns
- `references/memory-discipline.md` — memory vs {CLIENT} vs SOUL.md discipline
- `references/pattern-reuse-discipline.md` — pattern reuse tracking and audit
- `references/monitoring-feedback-protocol.md` — monitoring instance feedback requirements
- `references/date-convention.md` — filename date conventions

---

*Created from the {CLIENT} project ({CLIENT}). Updated {CLIENT} to add memory discipline, pattern reuse, monitoring feedback, and date convention pitfalls.*
