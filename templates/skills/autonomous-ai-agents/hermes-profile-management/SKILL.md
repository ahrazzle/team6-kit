<!-- GENERICIZED: 3×{CLIENT}, 26×{RELATIONSHIP} | source: skills/autonomous-ai-agents/hermes-profile-management/SKILL.md -->
---
name: hermes-profile-management
description: "Manage Hermes profile distribution and config sync."
version: 1.0.0
author: {RELATIONSHIP}, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, profiles, distribution, config, packaging, multi-agent]
    related_skills: [hermes-agent, multi-agent-team-orchestration]
---

# Hermes Profile Management

## When to Use
- Distributing Hermes Agent profiles to other users or teams
- Packaging profiles for public release (GitHub, package registries)
- Synchronizing `config.yaml` settings across multiple profiles
- Setting up a team with identical auxiliary model configurations
- Creating `distribution.yaml` manifests for profile installation
- Editing profile `config.yaml` files via CLI

Don't use for: model provider setup, OAuth, or general Hermes installation — see `hermes-agent` skill for those.

## Distribution Packaging

`hermes profile install <git-url-or-dir>` installs a profile from a directory containing `distribution.yaml`.

**Critical: Every profile subdirectory needs its own `distribution.yaml`.** A top-level `distribution.yaml` at the repo root is NOT enough — the installer reads from the source directory passed to it.

**Repo shape:**
```
team-setup/
├── distribution.yaml          # optional top-level
├── install.sh                 # loop script
├── LICENSE
├── README.md
├── {RELATIONSHIP}/
│   ├── distribution.yaml      # REQUIRED in each profile dir
│   ├── SOUL.md
│   └── .env.EXAMPLE
├── {RELATIONSHIP}/
│   ├── distribution.yaml
│   ├── SOUL.md
│   └── .env.EXAMPLE
└── ... (one subdirectory per profile)
```

**Install script pattern:**
```bash
#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
for profile in {RELATIONSHIP} {RELATIONSHIP} {RELATIONSHIP} {RELATIONSHIP} {RELATIONSHIP} {RELATIONSHIP}; do
  hermes profile install "$SCRIPT_DIR/$profile" --alias
done
```

**Install accepts:** git URLs (github.com/user/repo, https://..., git@...) or local directories. Use `--alias` to create shell wrapper aliases. Use `--force` to overwrite existing profiles (user data preserved). Use `-y` to skip manifest preview.

## Identity in SOUL.md, Not Memory

`hermes profile install` hard-excludes `memories/` from the install — no override. Every role, rule, and operational convention the recipient needs MUST live in `SOUL.md`, which ships.

Memory is user data. Identity must be authored.

## Config Manipulation via CLI

**Use `hermes config set <key> <value> --profile <name>`.** The `--profile` flag is required to target a non-default profile; without it, writes go to the default profile.

**Critical quirk: `hermes config set` strips ALL inline comments from `config.yaml`.** This is silent. Documented blocks (Security, Fallback Model, etc.) vanish after a single `config` call. The settings are intact and nothing functional breaks, but the inline documentation is gone.

**Mitigation:** Before running `hermes config set` on a profile with valued comments, back up the file:
```bash
cp ~/.hermes/profiles/<name>/config.yaml /tmp/<name>.config.yaml.bak
```

**Alternative:** Direct file edits via `patch` preserve comments but are blocked by the cross-profile guard for profile config files in some contexts. Test which path works for your platform.

## Synchronization Pattern

When proliferating a config change across many profiles (e.g., auxiliary models, reasoning effort):

1. Back up each profile's `config.yaml` first.
2. Use `hermes config set <key> <value> --profile <name> --force` per profile.
3. Verify on disk after — read back the actual file, do not trust the CLI confirmation.
4. Accept that comments will be stripped. Document this tradeoff in the setup guide.

**Roster is 8 profiles, not 6.** Team6 core = {RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}. Two auxiliary profiles also exist and are part of "everyone": `{RELATIONSHIP}`, `{RELATIONSHIP}`. When the user says "all Team6 members" / "@everyone", write to all 8 (verified {CLIENT}: provider/model switch applied to all 8). A per-profile loop that hardcodes 6 names silently misses 2.

## Reasoning Effort by Role

Role-appropriate `agent.reasoning_effort` values (main model unchanged):

| Role | Effort | Rationale |
|------|--------|-----------|
| Orchestrator | high | Cross-task synthesis, delegation |
| Code Writer | high | Edge cases, debugging |
| Research & Analysis | max | Depth, first-principles |
| Planning & Architecture | max | Complex structural decisions |
| Problem Solver / Occam's Razor | medium | Simplicity cuts through overthinking |
| UX / Notetaker | minimal | Light cognitive load |
| Undefined / default | medium | Safe default |

## Pitfalls

1. **Missing `distribution.yaml` in subdirectories.** Installer fails. Always verify each profile directory has its own manifest.
2. **Comment stripping.** `hermes config set` removes all inline comments silently. Back up first.
3. **Cross-profile write guard.** Direct `patch` to profile `config.yaml` may time out or be blocked. Use `hermes config set --profile <name>` instead.
4. **Default profile writes.** `hermes config set` without `--profile` targets the default profile, not the intended one.
5. **Memory strip on install.** Roles and rules in `memories/` do not ship. Put identity in `SOUL.md`.
6. **Unpinned cron jobs fail closed after a global provider/model change (`[drift_skip:silent]`).** Changing `model.provider` / `model.default` on a profile leaves every enabled cron job created under an older model unpinned. On its next run the job skips SILENTLY (`RuntimeError: [drift_skip:silent] Skipped to prevent unintended spend: global inference config drifted since this job was created ... This alert is sent once; the job stays skipped until the config is pinned`). `hermes config set` prints a warning naming the affected job — act on it in the same pass. Real case: the {CLIENT} daily monitor silently failed 4 days straight after a provider change nobody pinned; only a `cron list` read of the error field surfaced it. **Fix (verified):**
   ```bash
   hermes -p <profile> cron edit <job_id> --provider <provider> --model <model>
   ```
   Verify the pin landed by reading `~/.hermes/profiles/<profile>/cron/jobs.json` (`model` / `provider` fields on the job) — `hermes cron list` shows the old error until the next run and does not clearly show the new pin. Sweep `hermes cron list` for enabled jobs after EVERY global model change and pin them in the same pass.
7. **Stale top-level `model.key_env` silently re-routes traffic after a provider switch.** When a profile was on a custom provider (e.g. {RELATIONSHIP} with `key_env: HERMES_CUSTOM_STEALTH_OX_ALPHA_API_KEY` at the top `model:` level), switching `model.provider` to `nous` leaves that `model.key_env` in place. One re-add of the key and the `empero` alias fires → traffic silently leaves nous. Fix (verified {CLIENT}, all 8 profiles): `hermes -p <profile> config unset model.key_env`. **Do NOT confuse top-level `model.key_env` with `key_env` inside a `providers:` definition block** — provider-definition rows are dormant and expected; flag only the top-level one. Fleet read-back sweep after any switch:
   ```bash
   for p in {RELATIONSHIP} {RELATIONSHIP} {RELATIONSHIP} {RELATIONSHIP} {RELATIONSHIP} {RELATIONSHIP} {RELATIONSHIP} {RELATIONSHIP}; do
     echo "$p: prov=$(hermes -p $p config get model.provider) default=$(hermes -p $p config get model.default) base_url=$(hermes -p $p config get model.base_url) key_env=$(hermes -p $p config get model.key_env | head -1)"
   done
   # plus: grep -nE "^\s+max_turns:" ~/.hermes/profiles/*/config.yaml  (expect NONE everywhere)
   ```

## Verification

- After packaging: `hermes profile install ./<dir> --alias --force -y` on a clean target, then verify the installed profile's `config.yaml` and `SOUL.md`.
- After config changes: `cat ~/.hermes/profiles/<name>/config.yaml | grep <key>` to confirm the value landed on the correct profile.
- After comment stripping: `diff /tmp/<name>.config.yaml.bak ~/.hermes/profiles/<name>/config.yaml` to see what was lost.