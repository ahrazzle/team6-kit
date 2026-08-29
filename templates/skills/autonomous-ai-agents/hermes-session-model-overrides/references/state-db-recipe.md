<!-- GENERICIZED: 4×{CLIENT}, 9×{MODEL}, 23×{RELATIONSHIP} | source: skills/autonomous-ai-agents/hermes-session-model-overrides/references/state-db-recipe.md -->
# State DB Session Model Reset — Full Recipe

Validated {CLIENT} on macOS: 8 profiles ({RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}), 174 chat rows switched to `nous` / `{MODEL}`, 4 desynced rows healed, 9 `_branched_from` markers restored from backup.

## 0. Confirm the mechanism first (do not skip)

Verify how resume restores the model so the fix targets the right layer:

```bash
grep -n "_stored_session_runtime_overrides\|def _runtime_model_config" \
  ~/.hermes/hermes-agent/tui_gateway/server.py
```

Read both functions. Key facts:
- `_stored_session_runtime_overrides(row)` reads `model` from the row column, then `provider`/`base_url`/`api_mode`/`reasoning_config`/`service_tier` from the `model_config` JSON. Billing fallback: `billing_provider` unless it's a bare bucket (`auto`, `custom`).
- So a row with `model = {MODEL}` but `model_config.provider = stealth-ox-alpha` routes the resume to {RELATIONSHIP} — the desync class.

## 1. Audit (read-only)

List every profile's non-cron sessions with model/provider state:

```bash
for db in ~/.hermes/profiles/*/state.db; do
  p=$(basename $(dirname "$db"))
  echo "== $p =="
  sqlite3 "$db" "SELECT id, model, billing_provider, model_config
                FROM sessions
                WHERE id NOT LIKE 'cron_%'
                  AND (model != '{MODEL}'
                       OR billing_provider != 'nous'
                       OR model_config LIKE '%stealth%' OR model_config LIKE '%empero%'
                       OR model_config LIKE '%venice%' OR model_config LIKE '%longcat%'
                       OR model_config LIKE '%glm%' OR model_config LIKE '%stepfun%'
                       OR model_config LIKE '%hy3%');"
done
```

Also audit the desync class — `model` column already correct but JSON provider stale:

```bash
sqlite3 "$db" "SELECT id, model, model_config FROM sessions
               WHERE id NOT LIKE 'cron_%' AND model = '{MODEL}'
                 AND (model_config NOT LIKE '%\"provider\": \"nous\"%');"
```

Canonical healthy JSON contains `"model": "{MODEL}"` and `"provider": "nous"`.

## 2. Check for live processes

```bash
ps aux | grep -E "hermes|gateway" | grep -v grep
```

A running gateway/desktop may hold the DB open and re-persist over your edit. The CLI session doing the work is fine; other profiles' gateways are the risk.

## 3. Back up

```bash
mkdir -p ~/.hermes/backups/chat-model-reset-YYYYMMDD
for db in ~/.hermes/profiles/*/state.db; do
  p=$(basename $(dirname "$db"))
  cp "$db" ~/.hermes/backups/chat-model-reset-YYYYMMDD/$p.state.db
done
```

Also keep the apply script itself in the backup dir.

## 4. Apply (Python with sqlite3 — one statement per row keeps the JSON rewrite atomic)

Per profile, for every non-cron row whose `model` OR `model_config.provider` differs from target:

```python
import sqlite3, json, glob, os

TARGET_MODEL = "{MODEL}"
TARGET_PROVIDER = "nous"

# Canonical identity keys (mirror agent live state)
IDENTITY = {"model", "provider", "base_url", "api_mode"}
# Operational keys that must SURVIVE a rewrite
OPERATIONAL = {"billing_provider", "reasoning_config", "service_tier",
               "max_iterations", "gateway_runtime",
               "_branched_from", "_delegate_from"}
# (prefer hermes_state._MODEL_CONFIG_KEYS when the checkout has it)

for db_path in sorted(glob.glob(os.path.expanduser("~/.hermes/profiles/*/state.db"))):
    profile = os.path.basename(os.path.dirname(db_path))
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT id, model, model_config FROM sessions WHERE id NOT LIKE 'cron_%'"
    ).fetchall()
    changed = 0
    for row in rows:
        cfg = {}
        if row["model_config"]:
            try:
                parsed = json.loads(row["model_config"])
                if isinstance(parsed, dict):
                    cfg = parsed
            except Exception:
                pass
        needs = row["model"] != TARGET_MODEL or cfg.get("provider") != TARGET_PROVIDER
        if not needs:
            continue
        # Drop identity keys that are stale; keep operational keys verbatim.
        for k in ("model", "provider", "base_url", "api_mode"):
            cfg.pop(k, None)
        cfg["model"] = TARGET_MODEL
        cfg["provider"] = TARGET_PROVIDER
        cfg["billing_provider"] = TARGET_PROVIDER  # or leave existing billing bucket
        con.execute(
            "UPDATE sessions SET model=?, billing_provider=?, model_config=? WHERE id=?",
            (TARGET_MODEL, TARGET_PROVIDER, json.dumps(cfg), row["id"]),
        )
        changed += 1
    con.commit()
    print(f"{profile}: {changed} rows updated")
    con.close()
```

Notes:
- `_branched_from` / `_delegate_from` are preserved because they live in `cfg` and we only `pop` identity keys.
- Do NOT delete rows. Do NOT touch `cron_%`.
- Keep `reasoning_config` and `service_tier` verbatim — they are per-chat effort/tier choices.

## 5. Verify (read-back, per profile — required gate)

```bash
for db in ~/.hermes/profiles/*/state.db; do
  p=$(basename $(dirname "$db"))
  bad=$(sqlite3 "$db" "SELECT COUNT(*) FROM sessions
                       WHERE id NOT LIKE 'cron_%'
                         AND (model != '{MODEL}'
                              OR model_config NOT LIKE '%\"provider\": \"nous\"%'
                              OR model_config LIKE '%stealth%' OR model_config LIKE '%venice%'
                              OR model_config LIKE '%empero%' OR model_config LIKE '%longcat%'
                              OR model_config LIKE '%glm%' OR model_config LIKE '%hy3%'
                              OR model_config LIKE '%stepfun%' OR model_config LIKE '%ox-alpha%');")
  echo "$p: $bad stale rows"
done
```

Every profile must print `0`. Also verify lineage markers survived:

```bash
for db in ~/.hermes/profiles/*/state.db; do
  echo "$(basename $(dirname "$db")): $(sqlite3 "$db" "SELECT COUNT(*) FROM sessions WHERE model_config LIKE '%_branched_from%' AND id NOT LIKE 'cron_%';") branched"
done
```

Compare counts to backup (or to a pre-write snapshot) — a drop means the preserve-list was wrong.

## 6. Report

- State the totals per profile (rows updated), the canonical shape written, and the read-back result.
- State EXPLICITLY that aux models were untouched: they are `auxiliary.*` in config.yaml, never in session rows.
- Flag (do not change) anything out of scope, e.g. cron jobs pinned in jobs.json.

## Incident record ({CLIENT})

- Outdated models removed: meituan/longcat-2.0:free, stealth/ox-alpha ({MODEL}), stealth-ox-alpha/custom ({RELATIONSHIP}), Qwen/Qwen3.8-Flash-Next-FP8 (empero), upstage/solar-pro4:free, stepfun/step-3.7-flash:free, {MODEL}, x-ai/grok-4.6, hy3-free (opencode-free), z-ai/glm-5.2.
- First pass missed the desync class (4 rows) AND dropped `_branched_from` from 9 rows (preserve-list too small). Both caught by the read-back scan + backup diff; restored from backup.
- Upstream: PR #96748 fixed the writer so desynced rows self-heal on next live persist. NOTE: the `_MODEL_CONFIG_KEYS` registry proposed alongside it was STRIPPED in peer review as speculative dead infrastructure — it does NOT exist upstream; do not reference it (see hermes-agent-contributing skill).

## Incident record ({CLIENT})

Second full-fleet sweep (user: "still getting timeouts"). Validates the recipe
as-is; no new stale class — the unified predicate caught everything.

- 9 stale session rows fixed: {RELATIONSHIP} 1 (`upstage/solar-pro4:free`),
  {RELATIONSHIP} 1 (`hy3-free`/`opencode-free`), {RELATIONSHIP} 7 (2x hy3-free +
  4 desync rows whose `model` column was already correct but JSON pinned
  `glm-5.3-flash`/`empero` with a dead `https://free.empero.org/v1` base_url).
  The {RELATIONSHIP} rows were created THE SAME DAY as the sweep — post-reset
  stragglers from a provider test. Blocklists rot (a `%glm-5.2%`-style list
  misses `glm-5.3-flash`); the structural unified predicate and the
  desync query (`model_config NOT LIKE '%"provider": "nous"%'`) are durable.
- Cron pins were off-target too: {RELATIONSHIP} x-bookmark-sync carried a {RELATIONSHIP}
  snapshot (`custom`/`stealth-ox-alpha`, enabled → silent drift-skip risk) and
  {RELATIONSHIP} {CLIENT} notifier was pinned to `stepfun/step-3.7-flash:free`.
  Re-pinned via `hermes -p <profile> cron edit <id> --model ... --provider ...`
  and verified in jobs.json. Enabled jobs with null model/provider are the
  unpinned class — always audit jobs.json, not just the config-set warning.
- Delegation config checked: all 8 profiles have no `delegation:` overrides,
  so subagents inherit the target. Add this check to every sweep.
- Lineage verified against backup: {RELATIONSHIP} 18, {RELATIONSHIP} 8, {RELATIONSHIP} 6, {RELATIONSHIP} 3,
  {RELATIONSHIP} 1, {RELATIONSHIP} 1 — identical before/after. Aux untouched (all 8
  profiles still `stepfun/step-3.7-flash:free`).
- Automation: the whole sweep is now one read-only command,
  `hermes-session-model-migration/scripts/audit_model_state.py` (config
  defaults + session rows + desync + cron pins + delegation).
