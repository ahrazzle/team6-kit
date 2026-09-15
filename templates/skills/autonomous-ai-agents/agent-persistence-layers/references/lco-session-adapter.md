---
name: lco-session-adapter-reference
description: LCO session index and adapter contract reference
license: MIT
---

# LCO Session Adapter Reference (B02)

**Reference contract only. No LCO source code vendoring.**

This document describes the adapter boundary for Codex session indexing. All data structures, command names, and MCP interfaces are specified here. Implementations must remain in external repositories; this kit contains only the reference contract.

## Legal Boundary

- **LCO License:** PolyForm Noncommercial / NOASSERTION
- **Adoption Scope:** Schema and command names only
- **Prohibited:** Direct source vendoring without legal clearance
- **Kit Coverage:** Reference contracts in templates/skills/autonomous-ai-agents/

## Session Index Contract

### Index Location (Derived State)

- SQLite FTS5 index for local session-card discovery
- Stored under agent's local data directory (platform-specific)
- Team6 Kanban board remains authoritative state source

### Prepared Card Schema

Each session card in the index must contain:

```json
{
  "objective": "string",
  "blocker": "string | null",
  "lifecycle_state": "pending | in_progress | blocked | resolved",
  "next_action": "string",
  "freshness": "ISO8601 timestamp",
  "confidence": "0.0 - 1.0",
  "source_refs": ["url | path | identifier"]
}
```

## CLI Command Contract

The `lco` CLI provides the following commands (all read-only by default):

| Command | Purpose | Output |
|---------|---------|--------|
| `doctor` | Verify index health and schema version | Status report |
| `find` | Search session cards by keyword | Matched card IDs |
| `grep` | Full-text search across card content | Context excerpts |
| `expand-query` | Enrich search results with details | Expanded card data |
| `dry-run` | Preview state changes without writing | Change log |

## MCP/Orchestration Facade

- **lco_* state surface:** Bounded interface for external orchestrators
- **MCP Server:** Stdio transport for session queries
- **OpenClaw Adapter:** Compatibility layer for multi-agent coordination

### Integration Points

1. **Index Read Interface:** Query session cards by lifecycle state or freshness
2. **Card Update Interface:** Mark cards as resolved or blocked (approval-bound)
3. **Search Interface:** FTS5-backed keyword matching

## Verification Requirements

- Prepared cards must not duplicate Team6 Kanban state
- CLI commands default to read-only mode
- State changes require explicit approval gates
