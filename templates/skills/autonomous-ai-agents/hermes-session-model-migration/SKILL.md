<!-- GENERICIZED: 5×{CLIENT}, 2×{MODEL}, 25×{RELATIONSHIP} | source: skills/autonomous-ai-agents/hermes-session-model-migration/SKILL.md -->
---
name: hermes-session-model-migration
description: "Use when existing Hermes chats must switch model/provider."
version: 1.0.0
author: {RELATIONSHIP} ({RELATIONSHIP})
license: MIT
platforms: [linux, macos, windows]
---

# Hermes Session Model Migration

> Re-pin existing Hermes chats (CLI sessions, group rooms, bot chats) to a new
> model/provider. This is the OTHER half of model configuration: `config.yaml`
> governs NEW sessions; per-session overrides in `state.db` govern every EXISTING
> chat on resume. If the user says "old chats are still on longcat/ox-alpha/empero
> even though the profiles moved to nous", this skill is the fix.

## When to Use

- User asks to switch all (or many) existing chats back to a specific model/provider
  (e.g. "switch them all back to Nous Portal, {MODEL}").
- A provider test/rollback leaves rooms pinned to a withdrawn or outdated model.
- Any report that "config.yaml is correct but old chats still use the old model".
- Recurring full-fleet sweeps ("still getting timeouts — run through all Team6
  sessions/projects/group chats again"). Start with `scripts/audit_model_state.py`
  — one read-only command covering config defaults, session rows, the desync
  class, cron pins, and delegation overrides.

**Companion skill:** `model-config-skill` covers the config.yaml side (new-session
defaults, tier selection, `hermes config set`). This skill covers the session-row
side. Run both for a full switch; config.yaml first, then this migration.

## Why config.yaml Is Not Enough

Hermes stores each chat's effective model/provider in the profile session DB
(`~/.hermes/profiles/<profile>/state.db`, table `sessions`, columns `model`,
`billing_provider`, `model_config`). On resume, `_stored_session_runtime_overrides`
in `tui_gateway/server.py` restores those stored values as `model_override` /
`provider_override` — they beat whatever `config.yaml` now says. A chat that ran on
`meituan/longcat-2.0:free` or `stealth/ox-alpha` stays on it forever until the
session row is updated. Root cause of the sneaky desync case (correct `model`
column, stale provider in the JSON): `_runtime_model_config` keeps existing JSON
keys when the agent attribute is falsy at persist time — see
`references/upstream-bug-notes.md`.

## Scope Decisions (what to touch / skip)

- `cron_%` session ids are HISTORICAL RUN RECORDS, not chats — skip them. Future
  cron runs are governed by `cron/jobs.json` model pins, not session rows. Flag
  stale cron pins to the user separately.
- Rows with NULL `model` inherit the profile default — nothing to fix.
- Only rows with an explicit `model` (or `model_config`) pin need updating.
- **Auxiliary models are config.yaml-scoped, never session-scoped.** This
  migration touches only the `sessions` table. Aux slots (`auxiliary.vision`,
  `compression`, `skills_hub`, `approval`, ...) live in each profile's
  `config.yaml` and are global per profile. User directive: a main-model switch
  changes ONLY the main model — leave aux models untouched and state in the
  report that they are unchanged.
- **Delegation overrides** (config.yaml `delegation:` block) — empty means
  subagents inherit the parent model. If present, audit them too; a pinned child
  model survives a parent switch and is a silent straggler.
- Check live processes first (`ps aux | grep -iE "hermes|electron|gateway"`).
  A running desktop/gateway holds the DB open; the CLI session itself is safe to
  write while running (WAL mode).

## Procedure

1. **Back up every target profile's `state.db`** before writing:
   ```bash
   BK=~/.hermes/backups/chat-model-reset-YYYYMMDD; mkdir -p $BK
   for p in {RELATIONSHIP} {RELATIONSHIP} {RELATIONSHIP} {RELATIONSHIP} {RELATIONSHIP} {RELATIONSHIP} {RELATIONSHIP} {RELATIONSHIP}; do
     cp ~/.hermes/profiles/$p/state.db $BK/$p.state.db
   done
   ```
2. **Run the migration script** (edit PROFILES / TARGET_MODEL / TARGET_PROVIDER
   at the top, or pass argv):
   ```bash
   python3 ~/.hermes/profiles/{RELATIONSHIP}/skills/autonomous-ai-agents/hermes-session-model-migration/scripts/switch_session_models.py
   ```
   The script rewrites each stale row:
   - `model` -> target, `billing_provider` -> target provider.
   - `model_config` -> `{"model": ..., "provider": ...}` merged with PRESERVED
     keys: `reasoning_config`, `service_tier`, `max_iterations`, `max_tokens`,
     `_delegate_from` (delegate children keep their marker), `_branched_from`
     (session-branch lineage — dropped once in the wild, restored from backup).
   - DROPS stale endpoint keys when the provider changes: `base_url`, `api_mode`.
3. **Read back per profile** — every non-cron row must show the target:
   ```bash
   for p in {RELATIONSHIP} {RELATIONSHIP} {RELATIONSHIP} {RELATIONSHIP} {RELATIONSHIP} {RELATIONSHIP} {RELATIONSHIP} {RELATIONSHIP}; do
     echo "--- $p ---"
     sqlite3 ~/.hermes/profiles/$p/state.db \
       "SELECT COALESCE(model,'(null)'), COALESCE(billing_provider,'(null)'), count(*)
        FROM sessions WHERE id NOT LIKE 'cron_%' GROUP BY model, billing_provider;"
   done
   ```
4. **Grep model_config for stale strings** (catches rows whose `model` column
   already matches but whose JSON still pins the old provider — the sneaky case):
   ```bash
   sqlite3 <db> "SELECT count(*) FROM sessions WHERE id NOT LIKE 'cron_%'
     AND (model_config LIKE '%longcat%' OR model_config LIKE '%stealth%'
     OR model_config LIKE '%Qwen%' OR model_config LIKE '%empero%'
     OR model_config LIKE '%solar%' OR model_config LIKE '%glm-5.2%'
     OR model_config LIKE '%hy3%' OR model_config LIKE '%grok%'
     OR model_config LIKE '%stepfun%' OR model_config LIKE '%deepseek-v4-pro%'
     OR model_config LIKE '%{RELATIONSHIP}%' OR model_config LIKE '%openrouter%'
     OR model_config LIKE '%opencode%' OR model_config LIKE '%upstage%');"
   ```
   Must return 0 in every profile.

## Pitfalls

**Unpinned cron jobs fail closed SILENTLY after a switch — pin them or they skip for days.** Every enabled cron job stores a `provider_snapshot`/`model_snapshot`; when the global provider/model changes, an unpinned job refuses to run with `RuntimeError: [drift_skip:silent] Skipped to prevent unintended spend: global inference config drifted since this job was created...` — and keeps skipping on every tick, with only a once-sent alert that is easy to miss. Observed {CLIENT}: the {CLIENT} daily monitor skipped 4 days straight (failure_streak: 4) before the pin. The `hermes config set model.provider`/`model.default` output prints the warning: "N enabled unpinned cron job(s) have stored provider_snapshot values that differ..." — that warning IS the to-do list. Fix after ANY model/provider switch:

```bash
hermes -p <profile> cron list                 # find enabled jobs with stored snapshots
hermes -p <profile> cron edit <job_id> --provider <provider> --model <model>
# verify the pin landed in the store:
python3 -c "import json;d=json.load(open('$HOME/.hermes/profiles/<profile>/cron/jobs.json'));[print(j['id'],j['model'],j['provider']) for j in d['jobs']]"
```

Do this in the same pass as the session migration — `hermes config set` prints the drift warning immediately, so the pin step is a follow-on of the config change, not a separate audit.

**Audit jobs.json directly, every sweep — the config-set warning is not the only
path.** The warning fires only at switch time; it misses jobs pinned to a
DIFFERENT off-target model. Observed {CLIENT} (second full sweep, a day after
the first): {RELATIONSHIP}'s x-bookmark-sync was still enabled with a {RELATIONSHIP}
snapshot (`custom`/`stealth-ox-alpha`, silent drift-skip risk) and {RELATIONSHIP}'s
{CLIENT} notifier was pinned to `stepfun/step-3.7-flash:free` — neither was
touched by the first pass. Classification: a job with `model`/`provider` fields
set is pinned (check the values); a job with null pins carries
`provider_snapshot`/`model_snapshot` and drift-skips silently when the snapshot
differs from current global config. The jobs.json python one-liner below (and
`scripts/audit_model_state.py`) covers both classes — run it on every sweep,
not just after a switch.

**The two-pass trap is really one predicate.** A WHERE clause of
`model != target` misses rows whose `model` column already matches but whose
`model_config` still carries a stale `provider` (e.g. `empero`, `{RELATIONSHIP}`) —
that JSON provider override breaks routing on resume even when `model` looks
right. Use the unified predicate: stale = `model != target` OR parsed
`model_config.model != target` OR `model_config.provider != target_provider`.

**Preserve delegate/operational keys.** `_delegate_from` marks subagent children;
`_branched_from` marks session-branch lineage; `max_iterations`/`max_tokens`/
`reasoning_config`/`service_tier` carry real knobs. Blindly replacing
model_config with a bare `{"model", "provider"}` orphans delegates, severs branch
lineage, and drops reasoning effort. Rebuild the JSON, don't clobber it. Full key
set seen in the wild: `model`, `provider`, `base_url`, `api_mode`,
`reasoning_config`, `service_tier`, `max_iterations`, `max_tokens`,
`_delegate_from`, `_branched_from`.

**Audit the backup for dropped keys after the rewrite.** `_branched_from` was
dropped from 9 rows in one real run (missing from the preserve set) and caught
only by diffing key sets between the backup and the live DB. After any
migration: scan the backup JSONs for every distinct key, confirm each is
preserved, deliberately dropped (`base_url`/`api_mode`), or rewritten
(`model`/`provider`), and restore anything unexpected from the backup — one-shot
diff script in `references/upstream-bug-notes.md`.

**Drop base_url/api_mode on provider change.** A stale `base_url` (e.g. a {RELATIONSHIP}
endpoint) left in model_config routes the resumed chat to the old provider even
after `provider` is rewritten.

**Canonical shape** (verified): plain row =
`{"model": "{MODEL}", "provider": "nous"}`; delegate child
adds `"max_iterations": 250, "reasoning_config": null, "max_tokens": null,
"_delegate_from": "<parent-id>"`; reasoning rows add `"reasoning_config":
{"enabled": true, "effort": "max"}, "service_tier": "normal"`.

**Read-back, not report.** Verified on disk per profile: zero stale model strings
in any model_config, every non-cron row on the target. A write returning OK proves
nothing until the audit queries above are run.

## Verification

The two read-back queries in Procedure steps 3-4 ARE the verification. Expected:
every profile prints exactly one line `target|provider|N` and the stale-grep
returns 0. Also spot-check one delegate row keeps `_delegate_from` and one
reasoning row keeps `reasoning_config` after the rewrite.

For full-fleet sweeps, `scripts/audit_model_state.py` is the one-command
read-back gate: it re-checks config defaults, session rows (unified predicate),
the desync class, every enabled cron job's pin/snapshot, and delegation
overrides in a single pass. Pair it with the lineage-count query against the
backup. Live-process nuance (confirmed {CLIENT}): a CLI session running in
another profile does NOT block state.db writes (WAL mode), but that process
keeps its in-memory model until the next resume — state that caveat in the
report rather than claiming instant effect.

## Scripts & References

- `scripts/switch_session_models.py` — parameterized state.db re-pin (backup is
  manual; script does update + second-pass stale scan + per-profile counts).
  Preserves `_branched_from` alongside `_delegate_from`.
- `scripts/audit_model_state.py` — read-only full-fleet sweep: config defaults,
  session rows (unified predicate), desync class, cron pins/snapshots,
  delegation overrides. Run BEFORE a migration as the scope finder and AFTER
  as the verification gate (exit 1 on any issue).
- `references/upstream-bug-notes.md` — root-cause analysis of the model-vs-
  model_config desync (`_runtime_model_config`), the backup key-diff audit
  script, and candidate improvements for NousResearch/hermes-agent.
