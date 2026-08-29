<!-- GENERICIZED: 3×{CLIENT}, 1×{MODEL}, 15×{RELATIONSHIP} | source: skills/hermes/custom-openai-endpoint-registration/SKILL.md -->
---
name: custom-openai-endpoint-registration
description: "Use when adding, reverting, or removing a custom API endpoint as a Hermes provider."
version: 1.0.0
author: {RELATIONSHIP} ({RELATIONSHIP})
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, providers, models, config, multi-agent]
    related_skills: [hermes-agent, model-config-skill]
---

# Register a Custom OpenAI-Compatible Endpoint in Hermes

## When to Use
- User gives an OpenAI-compatible base URL and wants it as a named provider selectable via `/model` in CLI or the desktop app.
- User asks to propagate a provider/model config across multiple Hermes profiles (Team6 fan-out).
- A free community endpoint, self-hosted vLLM/Ollama gateway, or proxy needs registration.

Class: adding an arbitrary OpenAI-compatible base URL as a named Hermes provider,
optionally across all Team6 profiles, with verified end-to-end proof.

Complements the bundled `hermes-agent` skill (whose own references/ dir lists
built-in providers; this covers user-defined `providers:<slug>` entries)
and `model-config-skill` (that one is owned by @{RELATIONSHIP} — do not edit it).

## Recipe (verified {CLIENT} against https://free.empero.org/v1)

### Step 1 — Probe the endpoint before writing any config

```bash
curl -s -m 30 <BASE_URL>/models -H "Authorization: Bearer <KEY>"
curl -s -m 60 <BASE_URL>/chat/completions -H "Authorization: Bearer <KEY>" \
  -H "Content-Type: application/json" \
  -d '{"model":"<MODEL_ID>","messages":[{"role":"user","content":"Say OK"}],"max_tokens":50}'
```

A completion proves the key format, model id, and that the endpoint speaks
OpenAI schema. Note if it returns `reasoning_content` (reasoning model).

### Step 2 — Write the provider via `hermes config set` (never hand-edit)

```bash
hermes [-p <profile>] config set providers.<slug>.name "<Display Name>"
hermes [-p <profile>] config set providers.<slug>.base_url "<BASE_URL>"
hermes [-p <profile>] config set providers.<slug>.model "<MODEL_ID>"
hermes [-p <profile>] config set providers.<slug>.api_key "***"
hermes [-p <profile>] config set model.aliases.<slug> "<slug>/<MODEL_ID>"
```

- Provider entries live in the `providers:` **dict** (not the `custom_providers`
  list used by the picker); they carry their own `base_url` + `api_key`/`key_env`.
- `--provider <slug>` and `-m <slug>` both resolve user-defined slugs.
- For the **default** profile from a profile shell: `env -u HERMES_HOME hermes config set ...`
  (otherwise writes land in the active profile's config).

### Step 3 — End-to-end proof, not just read-back

```bash
hermes [-p <profile>] chat -q "Reply with exactly: TEST OK" -m <slug> -Q --max-turns 1
```

`-Q --max-turns 1` gives a clean one-shot: only the final response + session_id.
The literal reply is the proof. (Config read-back alone proves the file changed,
not that the route works.)

### Step 4 — Multi-profile propagation

Back up first, loop with `-p`, then verify ALL profiles in one batched read-back:

```bash
cp ~/.hermes/profiles/<p>/config.yaml /tmp/<p>.config.$(date +%Y%m%d_%H%M%S).bak
for p in <profiles>; do hermes -p $p config set providers.<slug>.base_url "<BASE_URL>"; done
```

## Pitfalls

**Secret masking round-trip (cost real rework).** Tool results mask secret-looking
values as `***`. If you copy a masked value from an earlier result echo into a
later command, the literal `***` is written to disk. Detection/verification must
never rely on printing the secret: verify by hash instead —
`hashlib.sha256(key.encode()).hexdigest()[:12]` compared against a known-good
profile's copy. When a repair command needs the secret and you only have a masked
copy, assemble it in-process (e.g. python `"fr"+"ee"`) and assert its hash against
the known-good before writing.

**`hermes config set` strips YAML comments** on some profiles (verified 36→0 on
some, kept 36 on others — behavior varies by config, so always check):
`grep -c "^#"` before/after, keep timestamped backups.

**Frozen snapshot.** Profiles load config at session start. Propagated providers
are live only in fresh sessions; running rooms keep their model until restart.
In-chat `/model <alias>` does switch the current session.

**Free community endpoints log everything.** Check the provider's terms page for
logging/training disclosures; tell the user before routing confidential client
material through it.

**Reasoning models** burn tokens on `reasoning_content`; fine for chat, budget
it on high-volume aux slots.

**Top-level `model.base_url` + `model.api_key` hijack the whole profile (verified {CLIENT}).**
They form a profile-wide routing override, not a scoped provider registration. With
`provider: nous` and `default: {MODEL}` set, a leftover
`model.base_url: https://free.empero.org/v1` + `model.api_key: free` silently sent ALL
default-model traffic to the empero endpoint on 5 of 6 Team6 profiles. The config block
LOOKED uniform and correct — only reading `base_url` exposed it. Never fan out a custom
endpoint via the top-level pair; register `providers.<slug>` and switch via alias. To
revert, see the Undo section.

## Undo — revert a custom-endpoint override back to the portal (verified {CLIENT})

The reverse of Step 2/Step 4, used when the user wants the fleet back on Nous Portal
(or any uniform default). `hermes config unset <key>` exists and is the clean way to
remove a key (see `hermes config --help`); `hermes config set model.base_url ''` also
works for blanking a value.

```bash
for p in {RELATIONSHIP} {RELATIONSHIP} {RELATIONSHIP} {RELATIONSHIP} {RELATIONSHIP} {RELATIONSHIP}; do
  cp ~/.hermes/profiles/$p/config.yaml /tmp/$p.config.$(date +%Y%m%d_%H%M%S).bak
  hermes -p $p config set model.base_url ''
  hermes -p $p config unset model.api_key
done
```

- Keep the `providers.<slug>` block and `model.aliases.<slug>` — they stay inert when
  nothing points at them; removing them is optional and saves nothing.
- **Turn caps:** an explicit `agent.max_turns` is the only thing that caps a session —
  the schema default is unlimited (`TURN_LIMIT_UNLIMITED = sys.maxsize` in
  hermes_cli/config.py). "Remove the round cap" = `hermes -p <p> config unset agent.max_turns`.
- **Profile targeting fallback:** `HERMES_HOME=/Users/.../profiles/<p> hermes config get/set/unset ...`
  works when `-p <profile>` isn't available; both edit the same file.
- **Frozen snapshot applies to reverts too** — takes effect next fresh session.

Verify with verbatim read-back of the actual YAML, not the CLI's ✓ lines:

```bash
for p in {RELATIONSHIP} {RELATIONSHIP} {RELATIONSHIP} {RELATIONSHIP} {RELATIONSHIP} {RELATIONSHIP}; do
  f=~/.hermes/profiles/$p/config.yaml
  echo "== $p ($(wc -l < "$f") lines)"
  sed -n '/^model:/,/^providers:/p' "$f" | head -8
  grep -n 'max_turns' "$f" || echo "(max_turns absent — unlimited)"
done
```

## Verification checklist (all four)

1. `hermes config get providers --json` shows the slug on every target profile.
2. api_key verified **by hash**, not by printed literal.
3. `yaml.safe_load` parses every touched config (proves no structural damage).
4. One live `hermes chat -q ... -m <slug> -Q --max-turns 1` returns the expected literal.
