# registry/packs/ — vertical pack parameter files

A vertical pack is a PARAMETER FILE, not a fork. It feeds the same generator
(`build/generate.py`) as the open core. Buyers get the engine free (Apache-2.0);
the tuned instance — personas, skill bundle, choreography, setup playbook — is
what they pay for.

## Parameter file shape (from skeleton spec section 7)

```yaml
# consulting-agency.yaml (draft shape, off the team's own live division structure)
team:
  name: {TEAM_NAME}
personas:
  Director:
    mission: "route work, own decisions, verify before reporting"
  Architect:
    mission: "analyze and design; never code"
  Researcher:
    mission: "evidence, prior art, market scan"
  UX:
    mission: "human experience; consult on artifacts"
  QA:
    mission: "Occam's razor; scope; verify"
  Coder:
    mission: "sole software developer"
skill_bundle:            # curated from the 126 TEMPLATE rows (generic forms only)
  - landing-page-design
  - static-brand-site-launch
  - github-project-publication
  - analytical-report-design
choreography:
  contribution_order: [Director, UX, QA, Researcher, Architect, UX, Coder, QA, Director]
  handoff: "restate brief; verifiable handles; read-back receipts"
  funnel: "viability-pass → user gate → discovery scan → spin-off"
setup:
  config_placeholders: {MODEL_PROVIDER, MODEL_NAME, BASE_URL}
  workspace_path: {WORKSPACE_PATH}
```

## Authoring rule

Author the first pack from REAL working behavior (the consulting/agency pack is
drafted off the team's own live divisions) — the generator's first proof-point
should stress it with the messiest realistic input available. That exposes
template bugs before they are sold.

## Declared-schema contract (asymmetric, one-directional hard)

Each vertical pack's `kit.yaml` MUST declare the placeholders it resolves:

```yaml
placeholders: [TEAM_NAME, DIRECTOR_NAME, ROLE_NAME, CLIENT, ...]
```

Instantiation validates the resolved set against the declared set
(`generate.py --params <pack>` + `--strict` for paid builds):

- **`declared ∖ resolved` = FAIL.** The pack promised a placeholder and
  didn't deliver — the typo case (`{CLIEN}` when `{CLIENT}` was declared).
  Build stops. This is the paid tier's guard against silently broken kits.
- **`resolved ∖ declared` = WARN.** Extra tokens (`{BK}`, `{N}`) are legit
  code literals or template drift — review, don't fail. A template gaining a
  new placeholder after the pack declared shows up here as drift.
- **Unresolved tokens** (no param at all): WARN in open-core mode (generic
  state by design), FAIL under `--strict` (a paid kit can't ship mangled).

The asymmetry is deliberate: symmetric "sets must match exactly" would
false-fail legitimately generic skills at pack time. Declared at pack
creation, validated at instantiation — the direction of drift stays
meaningful.
