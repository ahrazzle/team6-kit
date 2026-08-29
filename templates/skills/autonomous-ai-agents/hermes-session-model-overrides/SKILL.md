<!-- GENERICIZED: 2×{CLIENT}, 3×{RELATIONSHIP} | source: skills/autonomous-ai-agents/hermes-session-model-overrides/SKILL.md -->
---
name: hermes-session-model-overrides
description: "Use when chats stay pinned to old models. Reset in state.db."
version: 1.0.0
author: {RELATIONSHIP} ({RELATIONSHIP})
license: MIT
platforms: [linux, macos, windows]
---

# Hermes Session Model Overrides (state.db)

> config.yaml sets profile DEFAULTS; each chat's LAST-USED model/provider is stored per-session and restored on resume — so old chats stay pinned to outdated models even after the global config is correct. This skill covers auditing and bulk-resetting those overrides across all Team6 profiles.

## When to Use

- User reports chats running outdated models/providers ("switch them all back to X")
- After a provider rotation, restore, or cost change — old sessions still pinned
- Before an audit: "which sessions deviate from the profile default?"
- Bulk reset across many profiles at once ({CLIENT} operation: 8 profiles, 174 rows, 4 desynced rows found)
- Recurring full-fleet sweeps (user: "still getting timeouts — run through all
  Team6 sessions/group chats again"). One command: run
  `hermes-session-model-migration/scripts/audit_model_state.py` — read-only,
  covers config defaults, session rows, desync class, cron pins, delegation.

## The Model

- Profile defaults: `~/.hermes/profiles/<name>/config.yaml` (`model.default`, `model.provider`, `auxiliary.*`).
- Per-chat state: `~/.hermes/profiles/<name>/state.db`, table `sessions`, columns `model`, `billing_provider`, `model_config` (JSON string).
- On resume, `_stored_session_runtime_overrides` (tui_gateway/server.py) restores: model from the `model` column, provider/endpoint/reasoning/tier from the `model_config` JSON. The session row therefore WINS over config.yaml for that chat — this is why old chats keep their outdated model despite a correct global config.
- Cron runs are governed by cron job config (jobs.json), NOT session rows — never touch `cron_*` rows (they are run records, and future runs use job config anyway).

## Canonical model_config JSON

Identity (mirror the agent's live state):
- `model`, `provider` (e.g. `nous`), `base_url`, `api_mode` — the last two only for custom/self-hosted endpoints; DROP them when switching to a built-in provider, or resumes route to dead endpoints ({RELATIONSHIP}/empero leftovers were the real vector).

Operational (PRESERVE when rewriting):
- `billing_provider`, `reasoning_config`, `service_tier`, `max_iterations`
- `gateway_runtime` (CLI nested route shape)
- `_branched_from`, `_delegate_from` — lineage markers; dropping them severs branch/subagent ancestry (real incident: 9 rows lost `_branched_from` during a reset and had to be restored from backup)

There is NO upstream key-registry constant to import. `hermes_state._MODEL_CONFIG_KEYS` was proposed in PR #96748 but STRIPPED during peer review ({CLIENT}) as speculative dead infrastructure — it changed zero runtime behavior and its only consumer was an unimplemented feature. Do not reference it. The preserve/identity classifier is the distinction in this skill: **identity keys** (`model`, `provider`, `base_url`, `api_mode`) mirror the agent's live state and may be deleted when the agent attribute is falsy; **operational keys** (`billing_provider`, `reasoning_config`, `service_tier`, `max_iterations`, `gateway_runtime`, `_branched_from`, `_delegate_from`) must survive any rewrite. Preserve by writing only the identity keys you intend and leaving everything else in the JSON untouched.

## Procedure (exact SQL in references/state-db-recipe.md)

1. **Audit** — per profile, SELECT non-cron sessions whose model/provider deviate from the target. Check BOTH the `model` column AND the `model_config` JSON: a row can have a correct `model` column AND a stale `provider` in `model_config` (the desync class — 4 live rows found this way).
2. **Back up** — copy every state.db before writing (a JSON rewrite mistake is unrecoverable otherwise).
3. **Update** — set `model`, `billing_provider`, and rewrite `model_config` together (never just one column), preserving operational keys, dropping stale endpoint keys.
4. **Verify** — read back per profile: zero remaining non-target rows; scan every `model_config` JSON for stale model/provider strings; confirm `_branched_from`/`_delegate_from` counts are unchanged from backup.
5. **Report** — state explicitly that aux models were untouched (they are config.yaml-scoped, never in session rows — the user will ask).

## Pitfalls

- **Desync**: `model` column correct + `model_config.provider` stale → resume routes to the wrong provider. Always audit both, always write both.
- **Lineage loss**: any preserve-list that omits `_branched_from`/`_delegate_from` destroys them. The preserve-list must be a superset of operational keys, not a hand-picked subset.
- **Cron rows**: `cron_*` are run records, not chats — updating them does nothing and corrupts history.
- **Live sessions**: check running processes before writing; a live gateway may hold the DB and re-persist over your edit.
- **No config.yaml writes**: this surgery is session-table-only. Aux models and profile defaults live in config.yaml and stay untouched.

## References

- references/state-db-recipe.md — full recipe: audit SQL, backup, update statements, verification read-backs
