# Licensing — airefea-kit

This repo is a STANDALONE product built on the Hermes engine. It is not a
git-fork of Hermes: no upstream source or history is copied into this tree.

The two-zone license claim rests on this document + the README, not on a
git-history boundary. Read this before contributing.

## Zones

| Zone | Paths | License | Notes |
|---|---|---|---|
| Engine-derived | `build/` tooling (scanner, gates, generator, manifest), generic skills under `templates/skills/` | **MIT — provenance today, obligation on arrival** | The repo's current content is entirely our own authored work (Apache-2.0). The MIT zone is a FORWARD CONTRACT: MIT attaches when engine-derived code actually lands here (the setup-agent PR, any vendored tooling). Today there are no MIT files in this tree; the zone names what the future upstream surface will be. Nothing here carries instance data. |
| Kit layer | `choreography/`, `templates/personas/`, `registry/kit.yaml`, `AUDIT/` | **Apache-2.0** | Our identity archetypes, orchestration contract, governance, and build evidence. |
| Proprietary | `registry/packs/` parameter files | **Proprietary by contract** | Vertical packs are service deliverables — NEVER committed to this repo. The `packs/README.md` shape is public; the parameter files are not. |
| Product brand | `README.md`, `LICENSE` | Apache-2.0 (README), Apache-2.0 (LICENSE) | The product name `airefea-kit` is our brand. |

## Rules

1. **Never commit instance identifiers** — the surface matrix (`build/surface-scan.py`)
   is the gate; `AUDIT/fork-commit-1.md` is the baseline. Any file failing the
   scan does not land.
2. **Never commit packs** — `registry/packs/` contains only documentation of
   the pack shape (README.md). The parameter files themselves are delivered
   as service, not source.
3. **Engine-adjacent additions go upstream** — new tooling that is broadly
   useful (scanner, gates, setup-agent) is MIT-relensed and PR'd to Hermes;
   it is NOT kept proprietary here.
4. **The setup-agent, when it lands, is MIT** — it is the flagship upstream
   contribution and lives in the engine-derived zone.

## Provenance

- Engine: Hermes by Nous Research — MIT (https://github.com/NousResearch/hermes-agent)
- This repo: `airefea-kit` — Apache-2.0 core + proprietary packs by contract
- `AUDIT/fork-commit-1.md` — the first commit's cleanliness evidence (surface
  scan, staged-tree manifest, invariant check, verification lineage)
