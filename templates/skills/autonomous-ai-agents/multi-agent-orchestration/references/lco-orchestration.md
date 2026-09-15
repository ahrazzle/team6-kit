---
name: lco-orchestration-reference
description: LCO MCP/OpenClaw orchestration contract
license: MIT
---

# LCO Multi-Agent Orchestration Reference (B02)

**Reference contract only. No LCO source code vendoring.**

## MCP Facade Contract

The LCO session adapter exposes an MCP-compatible interface for external orchestrators:

### State Query Endpoints

- `lco.list_sessions`: Enumerate active session cards
- `lco.get_session`: Retrieve full card details by ID
- `lco.find_by_state`: Filter cards by lifecycle state

### MCP Server Configuration

```json
{
  "name": "lco-session-adapter",
  "transport": "stdio",
  "capabilities": ["list_sessions", "get_session", "find_by_state"],
  "read_only": true
}
```

## OpenClaw Adapter

Compatibility layer for OpenClaw multi-agent orchestration:

- Session state synchronization via shared index
- Card lifecycle events broadcast to connected agents
- State transitions require operator approval

## Integration Constraints

1. **No State Ownership:** Adapter reads derived state; Team6 Kanban remains authoritative
2. **Read-Only Default:** All operations default to query mode
3. **Approval Boundary:** State changes require explicit confirmation
