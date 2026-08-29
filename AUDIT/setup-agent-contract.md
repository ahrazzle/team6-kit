# Setup-Agent Authoring Contract — S8 boundary + queue state

## The authoring contract (author to the boundary)

The setup agent is authored as a **structurally closed network module** — the
8-surface scan is PROOF of the boundary, not the defense. The author codes to
these constraints so the class is impossible, not just detected:

1. **Zero network egress primitives** — no `import requests`, `urllib`,
   `http.client`, `socket`, `ftplib`, `smtplib`, `telnetlib`, `imaplib`,
   `poplib`; no `subprocess` calls carrying network args (`curl`, `wget`,
   `nc`, `telnet`, `http(s)://`). The interview answers stay in-process and
   touch ONLY the params file.
2. **Params-file-only writes** — the agent's only output surface is the
   parameter file (or the Hermes-native identity subset for the upstream MIT
   variant). No other file, no stdout-to-network, no logs of answers.
3. **No telemetry by construction** — no metrics endpoint, no crash
   reporting, no answer logging. If a future feature needs telemetry, it is
   opt-in by config gate (Hermes standard), never implicit.
4. **The scan is a BUILD GATE, not a review** — the author runs
   `build/surface-scan.py` before committing; the 8-surface PASS is a
   precondition for the PR, enforced at authoring time (same discipline as
   the genericizer's post-substitution invariant).

## Write targets (two, per the schema-split + license-surface guard)

| Variant | Emits | Schema |
|---|---|---|
| Upstream MIT agent | Hermes-native identity subset: SOUL.md + profile.yaml + config | The Hermes-native keys only — NEVER kit-layer keys (the moment it emits kit keys it's a kits-layer artifact wearing MIT clothes) |
| Kit agent | Full params file | The 16-key declared `placeholders:` contract in `registry/kit.yaml` |

## Hygiene gate (review §4)

- The agent is authored in this workspace first, then MIT-relensed upstream.
- It must pass the full 8-surface matrix BEFORE the PR — "MIT-relensable"
  does not mean "no instance identifiers baked in during authoring."
- Same gate as every other committed file: no instance tokens, no live
  integrations, no mangled words, no egress.

## Queue state

1. ✅ S8 network-egress surface (7→8) — built + verified
2. ✅ Setup-agent UX spec — written, reviewed, signed
3. ⏳ Author setup agent (this contract) → 8-surface gate
4. ⏳ Upstream PR (MIT-relensed)
5. ⏳ Registry publish
6. ⏳ First vertical pack
