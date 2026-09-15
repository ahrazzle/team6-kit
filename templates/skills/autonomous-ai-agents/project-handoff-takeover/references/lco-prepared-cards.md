---
name: lco-prepared-cards-reference
description: LCO prepared card schema and workflow
license: MIT
---

# Prepared Card Contract Reference (B02)

**Reference schema only. No LCO source code vendoring.**

## Prepared Card Fields

| Field | Type | Description |
|-------|------|-------------|
| objective | string | Primary goal or task description |
| blocker | string \| null | Current obstruction (null if unblocked) |
| lifecycle_state | enum | pending, in_progress, blocked, or resolved |
| next_action | string | Immediate next step |
| freshness | ISO8601 | Last modification timestamp |
| confidence | float | 0.0–1.0 confidence score |
| source_refs | array | URLs, paths, or identifiers for provenance |

## Attention Inbox Workflow

1. **Card Creation:** External system writes card to session index
2. **Review Gate:** Team6 orchestrator reviews card before activation
3. **State Transition:** Lifecycle state updated only after approval
4. **Archival:** Resolved cards moved to read-only archive

## Verification

- Cards must reference Team6 Kanban task IDs
- Freshness timestamps updated on each state change
- Confidence scores validated against historical outcomes
