<!-- GENERICIZED: 2×{CLIENT}, 2×{MODEL}, 5×{RELATIONSHIP} | source: skills/autonomous-ai-agents/hermes-session-model-migration/references/upstream-bug-notes.md -->
# Upstream notes: session model desync, audit, and PR candidates

Observed {CLIENT} during a full Team6 model migration (174 sessions, 8 profiles).

## The desync bug (model column vs model_config JSON)

Found 4 live rows where `sessions.model` was already
`{MODEL}` but `model_config` still pinned
`provider: empero` or `provider: {RELATIONSHIP}`. On resume,
`_stored_session_runtime_overrides` (tui_gateway/server.py) reads the model from
the column but the provider from the JSON — so those chats would have silently
routed to the old endpoint.

Root cause: `_runtime_model_config(agent, existing)` (tui_gateway/server.py
~line 5299) starts from `dict(existing or {})` and only overwrites keys when the
agent attribute is truthy:

```python
config = dict(existing or {})
if model:   config["model"] = model      # fresh value lands here
if provider: config["provider"] = provider  # but if agent.provider is falsy,
                                            # the OLD provider survives in JSON
```

When `agent.provider` (or model/base_url/api_mode) is falsy at persist time, the
stale JSON key survives while the `model` column gets the fresh value. The
codebase already heals the bare `"custom"` provider case (lines 5311-5338,
`canonical_custom_identity`); nothing heals a non-bare stale provider identity.
Writer is `_persist_live_session_runtime` (~line 5360), which runs each turn.

Migration consequence: the WHERE predicate for stale rows must be the unified
one (`model != target` OR parsed `model_config.model != target` OR
`model_config.provider != target_provider`) — see SKILL.md "two-pass trap".

## One-shot backup key-diff audit

After a migration, prove nothing operational was dropped by diffing key sets
between the backup DB and the live DB:

```python
import json, sqlite3, collections
BK = "<backup-dir>"; PROFILES = ["{PROFILES}"]
TARGET = "{MODEL}"
KNOWN = {"model","provider","base_url","api_mode","reasoning_config","service_tier","max_iterations","max_tokens","_delegate_from","_branched_from"}
all_keys = collections.Counter(); unexpected = []
for prof in PROFILES:
    conn = sqlite3.connect(f"{BK}/{prof}.state.db")
    rows = conn.execute("SELECT id, model, model_config FROM sessions WHERE id NOT LIKE 'cron_%' AND COALESCE(model,'')!='' AND model!=?", (TARGET,)).fetchall()
    for sid, model, raw in rows:
        mc = json.loads(raw) if raw else {}
        for k in mc: all_keys[k] += 1
        extra = set(mc) - KNOWN
        if extra: unexpected.append((prof, sid, model, sorted(extra)))
    conn.close()
print("distinct keys:", all_keys)
print("UNEXPECTED:", unexpected or "NONE")
```

This is what caught `_branched_from` being dropped from 9 rows (it was not in
the first preserve set).

## Restore a dropped key from backup

```python
import json, sqlite3
BK = "<backup-dir>"; PROFILES = [...]
for prof in PROFILES:
    bk = sqlite3.connect(f"{BK}/{prof}.state.db")
    live = sqlite3.connect(f"/Users/{RELATIONSHIP}/.hermes/profiles/{prof}/state.db")
    for sid, raw in bk.execute("SELECT id, model_config FROM sessions WHERE id NOT LIKE 'cron_%'"):
        mc = json.loads(raw) if raw else {}
        bf = mc.get("_branched_from")
        if not bf: continue
        cur = live.execute("SELECT model_config FROM sessions WHERE id=?", (sid,)).fetchone()
        cur_mc = json.loads(cur[0]) if cur and cur[0] else {}
        if cur_mc.get("_branched_from") != bf:
            cur_mc["_branched_from"] = bf
            live.execute("UPDATE sessions SET model_config=? WHERE id=?", (json.dumps(cur_mc, ensure_ascii=False), sid))
    bk.close(); live.commit(); live.close()
```

## Aux models live in config.yaml, not the sessions table

Verified {CLIENT}, all 8 profiles. A session-table edit cannot touch these;
only `hermes config set auxiliary.<slot>.*` can:

| Slot | Provider | Model |
|---|---|---|
| auxiliary.vision | nous | stepfun/step-3.7-flash:free (all 8) |
| auxiliary.compression | auto | '' (all) |
| auxiliary.skills_hub | nous | meituan/longcat-2.0:free (Team6 six); stepfun/step-3.7-flash:free ({RELATIONSHIP}, {RELATIONSHIP}) |
| auxiliary.approval | auto | (all) |

User directive: a main-model switch changes ONLY the main model; aux models
stay exactly as they are, and the report states that they are unchanged.

## Candidate upstream improvements (NousResearch/hermes-agent)

1. PR-worthy bug fix: `_runtime_model_config` should DROP (not retain) keys whose
   agent attribute is empty — fixes the model-vs-JSON desync class. Small diff;
   unit test on falsy attrs + E2E resume-route check (per repo AGENTS.md rubric).
2. Feature: `hermes sessions audit` / `hermes sessions reset-model` — no CLI
   exists to find or bulk-reset per-session overrides; raw SQL on state.db is
   required today. File as an issue first, gauge maintainer interest.
3. Minor: model_config JSON keys (`_delegate_from`, `_branched_from`,
   `service_tier`, `reasoning_config`) are undocumented string literals; a
   constants module would stop third-party tools from guessing. Ride along with
   #1 rather than a standalone PR.
