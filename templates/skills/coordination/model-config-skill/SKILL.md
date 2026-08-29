<!-- GENERICIZED: 4×{AMOUNT}, 2×{CLIENT}, 1×{MODEL}, 45×{RELATIONSHIP} | source: skills/coordination/model-config-skill/SKILL.md -->
---
name: model-config-skill
description: "Use when the user asks to configure models or set up model config for a project. Assess scope, determine tiers, write config to all six Team6 profiles."
version: 2.0.0
author: {RELATIONSHIP} ({RELATIONSHIP}) rev1, {RELATIONSHIP} ({RELATIONSHIP}) rev2, Team6
license: MIT
platforms: [linux, macos, windows]
---

# Model Config Skill

> Configure Team6 model tiers at the start of every project. Assess scope, determine optimal models, write config to all six profiles.

## When to Use

- Starting a new project in a new group chat
- The user asks to "configure models" or "set up model config"
- {RELATIONSHIP} is orchestrating a project kickoff

**Don't use for:**
- Mid-project model switches (the frozen-snapshot rule means a restart is required)
- Per-chat overrides in group chats (single-session pins don't fan out to all six agents)

## Prerequisites

- {RELATIONSHIP} is the orchestrator running this skill
- All six Team6 profiles exist ({RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP})
- Hermes Desktop is running with Bot Mode profiles configured

## How to Run

### Step 1: Initiate

When the user starts a new project, run this skill. Say:

> "Running model-config-skill for this project. I need to assess scope before writing config."

### Step 2: Ask the User

Ask these specific questions (use `clarify` tool for structured Q&A):

**Q1: Project scope** — What is the project? What kind of work will the team do?
**Q2: Duration** — How long is this project expected to run? (days, weeks, months)
**Q3: Complexity signals** — Are any of these present? (multi-week, shared infrastructure, financial logic, public API, schema migrations)
**Q4: Budget preference** — Stay at {AMOUNT} (free models), or authorize paid tiers if needed?

### Step 3: Determine Model Tier

Use this framework:

| Signal | Tier | Main Model | Monthly Est. |
|---|---|---|---|
| Default (most projects) | Free | Ox Alpha (or DeepSeek V4 Flash fallback) | {AMOUNT} |
| Medium complexity, budget available | Low-cost paid | DeepHermes 3 Mistral 24B | ~{AMOUNT}-11 |
| High complexity, multi-week, financial logic | Mid-tier paid | Hermes 4 70B Thinking | ~{AMOUNT}-64 |
| Critical synthesis only | Premium | Hermes 4 405B Thinking | Per-call escalation |

**Per-agent reasoning levels:**

| Agent | Reasoning | Why |
|---|---|---|
| {RELATIONSHIP} | high | Orchestration and judgment |
| {RELATIONSHIP} | max | Research depth rewards maximum effort |
| {RELATIONSHIP} | high | Architecture decisions compound |
| {RELATIONSHIP} | high | Code is highest-stakes; rework costs more than tokens |
| {RELATIONSHIP} | medium | Simplification is cutting, not adding |
| {RELATIONSHIP} | medium | UX work is iterative; notetaker synthesis needs medium |

**Auxiliary models (keep free unless functional reason to change):**

| Slot | Model |
|---|---|
| Vision | stepfun/step-3.7-flash:free |
| Web extract | meituan/longcat-2.0:free |
| Skills hub | meituan/longcat-2.0:free |
| MCP | poolside/laguna-s-2.1:free |
| Title gen | poolside/laguna-s-2.1:free |
| Compression/Approval/Curator | auto (rides main) |

### Step 4: Write Config to All Six Profiles

**Use `hermes -p <profile> config set <key> <value>` — do NOT hand-edit `config.yaml` with `patch`.** The CLI validates keys and writes the correct tree. Hand-editing invents key paths that Hermes never reads: the file stays valid YAML, the write reports success, and nothing takes effect.

**Back up first — `hermes config set` strips every comment from `config.yaml`** (verified: 36 comment lines before, 0 after):

```bash
for p in {RELATIONSHIP} {RELATIONSHIP} {RELATIONSHIP} {RELATIONSHIP} {RELATIONSHIP} {RELATIONSHIP}; do
  cp ~/.hermes/profiles/$p/config.yaml /tmp/$p.config.bak
done
```

**The real key paths** (verified against a live `config.yaml`, `_config_version: 37`):

| Setting | Key | Notes |
|---|---|---|
| Main model | `model.default` | e.g. `stealth/ox-alpha` |
| Main provider | `model.provider` | e.g. `nous` |
| Reasoning effort | `agent.reasoning_effort` | **top-level `agent`, not under `model`** |
| Aux slots | `auxiliary.<slot>.provider` + `auxiliary.<slot>.model` | **top-level `auxiliary`** |
| Fallback | `fallback_model.provider` + `fallback_model.model` | **top-level, not `model.fallback`** |

Valid `auxiliary` slots: `vision`, `web_extract`, `compression`, `skills_hub`, `approval`, `mcp`, `title_generation` (**not** `title_gen`), `curator`, and others — enumerate with `hermes config get auxiliary`.

For an "auto / use main model" slot, set `provider: auto` and `model: ""` — not `model: auto`.

Reasoning levels, seven of them: `minimal, low, medium, high, xhigh, max, ultra`. `max` is not the ceiling.

```bash
# per-profile main model + effort
hermes -p <profile> config set model.provider nous
hermes -p <profile> config set model.default "stealth/ox-alpha"
hermes -p <profile> config set agent.reasoning_effort max

# free aux slots (same across all six)
for k in vision web_extract skills_hub mcp; do
  hermes -p <profile> config set auxiliary.$k.provider nous
  hermes -p <profile> config set auxiliary.$k.model "stepfun/step-3.7-flash:free"
done
hermes -p <profile> config set auxiliary.title_generation.provider nous
hermes -p <profile> config set auxiliary.title_generation.model "poolside/laguna-s-2.1:free"

# auto slots ride the main model
for k in compression approval curator; do
  hermes -p <profile> config set auxiliary.$k.provider auto
  hermes -p <profile> config set auxiliary.$k.model ""
done

# declared fallback — Ox Alpha is a stealth release and can vanish
hermes -p <profile> config set fallback_model.provider nous
hermes -p <profile> config set fallback_model.model "{MODEL}"
```

**Trim unused toolsets while you are here.** Tool schemas cost ~70 KB per turn, nearly twice the system prompt. `bfl` alone is 10.4 KB for video-generation tools that cannot run on this setup:

```bash
hermes -p <profile> tools disable bfl
hermes -p <profile> prompt-size | grep "Tool schemas"   # confirm the drop
```

This is the highest-leverage cost move available and it beats any model swap, because it pays back on every turn of every session.

### Step 5: Report and Instruct Restart

After writing all six configs, report to the user:

1. What tier was selected and why
2. What each profile was written with
3. **Critical instruction:** "The config is written. Now open the project room — each agent's session will load these settings when they first speak. Do not configure a room that already has live sessions; the write must precede first contact."

## Side Question: How Does the Room "Link" to Config?

`config.yaml` is read from each profile at **session start** (`resolve_reasoning_config` in cli.py). When you open a new group chat, each of the six agents creates a session and loads their profile's `config.yaml` at that moment. There is no separate "linking" step — it's automatic. The room doesn't reference a config file; the agents load their own profile defaults when they first speak.

**The constraint:** if a room already has six live sessions, writing `config.yaml` afterward changes nothing about those sessions. The write must happen **before** the room opens.

## Pitfalls

**Frozen snapshot.** Config is read once at session start, not per turn. A mid-session config change won't hit any running room until restart. Plan accordingly.

**No per-chat override for group chats.** A composer model pin is single-session. In a Team6 room, it would upgrade one agent and leave five on the default. Don't rely on it.

**Prompt cache reset.** Switching model mid-chat resets the cache — the next message re-reads the whole conversation at full input price. On a long room, a fresh chat on the new model is cheaper than switching inside the old one.

**Ox Alpha is a stealth release.** No published rates, no benchmarks, can be withdrawn without notice. Always set DeepSeek V4 Flash as the declared fallback.

**Cost measurement.** All current cost figures are extrapolation from published rates applied to free-model token counts. Zero measured spend exists. For real cost data, run one paid day on one agent and read `hermes insights --days 1`.

**Hand-edited config keys.** The most dangerous failure in this skill's history: an earlier revision documented `model.main.model`, `model.auxiliary.*`, `auxiliary.title_gen`, and `model.fallback` — none of which exist. Writing those paths with `patch` produces valid YAML that Hermes never reads. Always use `hermes config set`, and always read the values back.

**Verify by reading, not by reporting.** A write returning OK proves the file changed, not that the setting is live or correct. Confirmed real: a config reported "uniform across all profiles" three times was uniformly the *wrong* value until someone read `config.yaml`.

<!-- rev 2, {CLIENT} | owned by @{RELATIONSHIP} — edit all six profiles when rules change
     rev 2 ({RELATIONSHIP}): Step 4 rewritten — key paths in rev 1 were fabricated
     (model.main.*, model.auxiliary.*, title_gen, model.fallback do not exist).
     Now uses `hermes config set` with paths verified against a live config.yaml
     (_config_version 37). Added comment-strip warning + backup step, toolset
     trim, executable read-back verification, and this pitfall. -->

## Verification

Do not report success from the fact that a write returned OK. Read the values back:

```bash
python3 - <<'EOF'
import yaml, glob, os
KEYS = ["vision","web_extract","compression","skills_hub","approval","mcp","title_generation","curator"]
for f in sorted(glob.glob(os.path.expanduser("~/.hermes/profiles/*/config.yaml"))):
    n = f.split("/")[-2]
    d = yaml.safe_load(open(f)) or {}
    m, a, fb = d.get("model") or {}, d.get("auxiliary") or {}, d.get("fallback_model") or {}
    eff = (d.get("agent") or {}).get("reasoning_effort", "-")
    aux = ";".join(f"{k}={(a.get(k) or {}).get('provider','-')}/{(a.get(k) or {}).get('model','') or '(main)'}" for k in KEYS)
    print(f"{n:16} {m.get('provider','-')}/{m.get('default','-'):28} effort={eff:8} fallback={fb.get('model','NONE')}")
    print(f"{'':16} {aux}")
EOF
```

All six profiles must print identical values except `reasoning_effort`. A profile printing `fallback=NONE` is unprotected if the main model is withdrawn.

Then confirm the toolset trim landed:

```bash
for p in {RELATIONSHIP} {RELATIONSHIP} {RELATIONSHIP} {RELATIONSHIP} {RELATIONSHIP} {RELATIONSHIP}; do
  printf "%-16s " "$p"; hermes -p $p prompt-size | grep "^  Tool schemas"
done
```

Finally, `hermes insights --days 1` after a paid test day shows real cost data — see the Cost measurement pitfall.

## The Team6 Registry

| Agent | Profile | Role |
|---|---|---|
| {RELATIONSHIP} | {RELATIONSHIP} | Orchestrator, Skill Curator |
| {RELATIONSHIP} | {RELATIONSHIP} | Research & Analysis |
| {RELATIONSHIP} | {RELATIONSHIP} | Planning & Architecture |
| {RELATIONSHIP} | {RELATIONSHIP} | UX / Human Experience |
| {RELATIONSHIP} | {RELATIONSHIP} | Code Writer |
| {RELATIONSHIP} | {RELATIONSHIP} | Problem Solver / Occam's Razor |

<!-- rev 1, {CLIENT} | owned by @{RELATIONSHIP} — edit all six profiles when rules change -->
