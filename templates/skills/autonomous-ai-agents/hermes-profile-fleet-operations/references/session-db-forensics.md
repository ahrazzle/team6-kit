<!-- GENERICIZED: 1×{CLIENT} | source: skills/autonomous-ai-agents/hermes-profile-fleet-operations/references/session-db-forensics.md -->
# Agent Turn-Failure Forensics — Reading state.db Directly

When an agent "times out" or dies mid-task in a group chat, the question is never *whether* it died — the session database records the death. This reference is the raw-SQLite layer under `hermes insights` for diagnosing turn-model failures (timeouts, context blowups, delegation verification).

## The Database

`~/.hermes/profiles/<name>/state.db` — SQLite, readable read-only:

```bash
sqlite3 "file:$db?mode=ro" ".tables"
```

Key tables:
- `sessions` — one row per session: `started_at`, `ended_at`, `end_reason`, `message_count`, `tool_call_count`, `model`.
- `session_model_usage` — per-session API accounting: `api_call_count`, `input_tokens`, `cache_read_tokens`, `output_tokens`, `reasoning_tokens`.
- `async_delegations` — subagent activity (the other side of the delegation check).

## Diagnostic Queries

```bash
# How do sessions die? The end_reason distribution is the autopsy table.
sqlite3 "file:$db?mode=ro" \
  "SELECT end_reason, COUNT(*) FROM sessions GROUP BY end_reason;"

# The death row: heavy sessions and how they ended.
sqlite3 -header "file:$db?mode=ro" \
  "SELECT substr(id,1,18) id, datetime(started_at,'unixepoch','localtime') started,
          message_count msgs, tool_call_count tools, end_reason
   FROM sessions ORDER BY started_at DESC LIMIT 10;"

# Token profile of a specific session: total traffic per session.
sqlite3 -header "file:$db?mode=ro" \
  "SELECT substr(m.session_id,1,18) sess, SUM(m.api_call_count) calls,
          printf('%.0fK',SUM(m.input_tokens)/1000.0) in_tot,
          printf('%.0fK',SUM(m.cache_read_tokens)/1000.0) cache_rd,
          printf('%.0fK',SUM(m.output_tokens)/1000.0) out
   FROM session_model_usage m WHERE m.session_id LIKE '20260825%'
   GROUP BY m.session_id ORDER BY m.session_id;"
```

## Interpretation — What the Numbers Mean

**`end_reason = ws_orphan_reap` on every heavy session** = the harness reaped a dead socket; the session died mid-turn, not completed. In the observed case, every heavy session of the day ended that way; light sessions ended clean (empty reason or `cron_complete`).

**Total traffic = the actual failure mechanism.** One session: 632 messages / 306 tool calls, 335 API calls each re-reading a ~100K-token context → ~31M tokens of total traffic for a single task. The per-call breakdown (`session_model_usage` rows) shows the re-read: `cache_read_tokens` dwarfs fresh input because the full conversation is re-sent every call. This is the arithmetic that makes config trims insufficient: only moving the tool-loop into a subagent's own session changes it.

**Verification pair for "delegation works":** after a delegated heavy task,
- the agent's *chat* session row should show small `message_count`/`tool_call_count` (human-conversation sized), and
- `async_delegations` should be heavy (the subagent absorbed the tool turns).

Delegation working = chat light + delegation table heavy + `end_reason` empty-or-clean on both. Trim-only masking shows as a still-massive chat session that happened to survive. This is "measure, not just pass" made mechanical — the same queries work on any profile for future audits.

## The Turn-Model Lesson (why this happens at all)

Long tool work inside one chat turn is a property of the turn model, not of any single agent or role: any role doing multi-minute tool work (research audits, architecture passes) has the same failure surface. The fleet convention that addresses it:

1. **Ack first** — one line in the room before starting ("claimed, running it").
2. **Delegate by default** — heavy tool work runs in a spawned subagent; the chat turn stays light; the subagent's transcript IS the re-entry record.
3. **One delivery** — single substantive message at completion with declared artifacts.
4. **Escalation only** — kanban claim with a self-contained re-entry brief (goal, constraints, current state) fires when work spans sessions or an execution dies mid-run. A bare task title forces archaeology; the brief is what makes the respawn path work.
5. **Task-named background terminals** — `terminal(background=true)` sessions named after the task ("{CLIENT}", not "proc_8f3") so anyone can watch mid-turn.

Config-side load relief (toolset trim — tool schemas ~70KB/turn, measured) is real but is **load relief, not the cure**; the cure is delegation.
