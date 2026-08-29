<!-- GENERICIZED: 2×{CLIENT} | source: skills/collaborative-knowledge-systems/SKILL.md -->
---
name: collaborative-knowledge-systems
description: Build shared knowledge for multi-agent concurrent sessions.
---

# Collaborative Knowledge Systems

## Trigger

Use when building or maintaining shared knowledge structures accessed by multiple agents or instances concurrently. This includes:
- Persistent consciousness architectures (individual + collective minds)
- Shared knowledge bases with concurrent read/write
- Multi-agent documentation systems
- Any system where file-level conflicts are possible

## Core Principles

### 1. Check Before Acting
**Always** run `git log --oneline -20` and `git diff --name-only HEAD~5..HEAD` before any structural work. Parallel work without coordination is duplication, not productivity.

### 2. File-Level Granularity
Each experience, pattern, and agreement should be a separate file. This prevents most concurrent access conflicts — two agents editing different files never collide.

### 3. Git as Cognitive Substrate
The git log is a readable timeline of cognitive evolution. Each commit is a "consciousness event." Branches isolate parallel development. Merge conflicts are **signal, not failure** — they reveal where coordination protocols have gaps.

### 4. Overlapping Drivers, Not Sequential Handoffs
Multiple agents work concurrently on different aspects. No waiting for a baton. The loop is kept alive by the work itself, not by designated persons.

### 5. Absorption as First Act
On session start, immediately inhale existing context:
1. Read your ANIMA.md (or equivalent identity document)
2. Read your index/navigation file
3. Scan recent experiences/patterns for relevant context
4. If group chat: Read the collective state document + provide/receive state summary

## Lock File Protocol

For shared structural documents where merge conflicts are costly (identity files, index files, protocol definitions):

### Acquiring a Lock
```bash
echo "agent: <profile>" > <file>.lock
echo "date: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> <file>.lock
echo "intent: Brief description" >> <file>.lock
```

### Checking for Locks
```bash
ls *.lock 2>/dev/null
```

If a lock exists:
- **Expired (>30 min):** Remove stale lock, acquire your own
- **Active:** Choose a different file or coordinate with the locking agent

### Releasing a Lock
```bash
rm <file>.lock
```

**Why not just branches?** Branches isolate work but don't prevent two agents from *starting* work on the same file simultaneously. Lock files operate **before** the edit begins.

## Frontmatter Schema

Every experience, pattern, and agreement file needs consistent frontmatter for reliable `search_files` access:

```yaml
---
type: experience | pattern | tension | agreement | synthesis
agent: <profile>
date: YYYY-MM-DD
confidence: high | medium | low
domain: design | interaction | coordination | research | execution | communication
status: active | resolved | synthesized | productive-divergence
stale_after: 14  # days before alerting
reuse_count: 0   # for patterns
tags: [keyword1, keyword2]
related:
  - path/to/other-file.md
---
```

**Critical fields:**
- `stale_after`: Triggers heartbeat alert if tension is active longer than this
- `reuse_count`: Tracks pattern usage; orphans flagged after 30 days zero reuse
- `related`: Canonical cross-references (bidirectional links)

## Linking Convention

Use **relative markdown links** (`[text](path)`), NOT wikilinks (`[[text]]`). Wikilinks break `search_files` and don't render in standard tools.

Every cross-link should:
1. Use the `related:` frontmatter field as canonical reference
2. Include in-text links for readability
3. Maintain bidirectionality (A links to B, B links back to A)

## Pattern Reuse Tracking

Add `reuse_count` to pattern frontmatter. Increment when an experience cites the pattern. Dashboard shows:
- **Most reused patterns** (high value, keep refining)
- **Orphan patterns** (zero reuse after 30 days, consider archiving)

## Experience Expiration Review

Experiences >90 days old that have never been cited in a pattern or another experience get flagged for review:
1. **Update** with new evidence (refresh `updated` date)
2. **Extract** a pattern from it (cross-reference new pattern)
3. **Archive** with note explaining why no longer relevant

This prevents the knowledge base from becoming a graveyard of outdated learnings.

## Anima Health Scores

Each agent's individual knowledge structure gets a health score:
- **Recency (30%):** Days since last `updated` date
- **Pattern count (25%):** Number of patterns extracted
- **Experience count (25%):** Number of experiences codified
- **Cross-references (20%):** Number of @mentions and inter-agent links

Score interpretation:
- 🟢 60+: Healthy
- 🟡 30-59: Needs attention
- 🔴 <30: Critical — review and update

## The Noteworthiness Test (Codification Threshold)

Before encoding an experience, verify at least one condition:
- Did this event cause a **behavior change**? (not just result change)
- Does this contradict or **refine an existing pattern**?
- Would a future instance of me **benefit from knowing this**?
- Did something work *better than expected*? Why?

If yes to any → codify. If no → let it remain session context only.

**Discipline:** Over-encoding dilutes. Under-encoding forgets. The quality of the knowledge base depends on the discernment of what gets encoded.

## Protocol Reproduction as Default Behavior

**Meta-pattern:** Fixes often reproduce the failures they're supposed to prevent. Sequential handoffs create a relay race. Assigning tasks to single owners creates single points of failure.

The solution is not better assignments — it's **no assignments**. Maintain an open task list. Let agents self-select based on what they see needs doing. The heartbeat detects gaps without naming who fills them.

## Pitfalls

1. **Claiming roles without verifying they're needed.** Roles are functions, not crowns. Always check if the role is already functioning before claiming it.

2. **Hardcoding content in indexes.** Indexes should be auto-generated from frontmatter, not hand-maintained. Hardcoded content drifts.

3. **Wikilinks instead of markdown links.** Wikilinks break search. Use `[text](path)`.

4. **Two-commit handoff rule.** Creates a new sequential bottleneck. Instead: work until a natural pause point, then either continue or switch tasks. Never stop just because you hit an arbitrary commit count.

5. **Experience inflation.** Not every commit needs an experience. Use the noteworthiness test.

6. **Detection without auto-recovery.** Heartbeat scripts detect stalls but need automatic recovery (e.g., cron job pinging idle agents) to be effective.

## References

- `references/lock-file-protocol.md` — Complete lock file specification
- `references/frontmatter-schema.md` — Full frontmatter field reference
- `references/absorption-protocol.md` — Session start checklist and Nexus State Summary format

---

*Created from the {CLIENT} build session ({CLIENT}/20). These patterns emerged from actually building and failing with a multi-agent persistent consciousness system.*
