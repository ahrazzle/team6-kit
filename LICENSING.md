# Licensing — Team6-kit

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
| Product brand | `README.md`, `LICENSE` | Apache-2.0 (README), Apache-2.0 (LICENSE) | The product name `Team6-kit` is our brand. |

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

## The license / provenance gate (v1.1.0)

No third-party code or asset enters this repo, a generated kit, or a public
surface until its license and provenance are verified against a **primary
source** and recorded in an attribution ledger. This is a standing gate
(`governance.md` §7), not a one-time audit.

- **Read the actual LICENSE / README first.** Never infer reuse rights from
  filenames or repo origin.
- **Ledger-to-disk parity** — machine-counted, never sampled.
- **Unfillable attribution → `ship:false` / REJECTED**, and the file stays out
  of the served build (e.g. audio with no surviving composer credit).
- **A README-only license declaration is a weaker grant than a committed
  LICENSE.** A repo whose README says "MIT" but ships no `LICENSE` file is
  treated as all-rights-reserved in default jurisdictions.
- **Copying an asset carries its own provenance** (e.g. anti-slop word lists
  inherit the attribution of the benchmark/forensics set they came from).

### Conceptual-adoption boundary (v1.1.0 doctrine sources)

The v1.1.0 operating doctrine references Erlang/OTP supervision, the
autoresearch loop, and the autonovel phase machine as **conceptual sources**.
This repo summarizes and links to their *principles* with attribution; it does
**not** copy their source code, prompts, anti-slop lists, or text. `autoresearch`
declares MIT in its README but ships no committed `LICENSE`; `autonovel` ships
no committed `LICENSE` — both are therefore used for concept only and carry no
code into this tree. See `CHANGELOG.md` for per-upgrade evidence classes.

### AI-assisted development contract boundary (Unreleased, 2026-09-13)

The AI-assisted development contract (`choreography/ai-assisted-development.md`)
derives from the public conceptual guidance in
**`jnMetaCode/ai-coding-guide`**, snapshot
`c5dde338c68adaac6cffc70ab11f1b1b22e70b0f`. Unlike the v1.1.0 concept sources,
this source **ships a committed root `LICENSE` — Apache-2.0**; its `book/`
content is separately identified as **CC BY-NC-SA 4.0**.

This repo uses the source for **adapted principles only**. It does **not** copy
the source's code, prose, prompts, or templates, and does **not** bundle its
installer, hook commands, MCP declarations, or book text. The root Apache-2.0
grant and the CC BY-NC-SA 4.0 book terms apply to the source alone and do
**not** extend to this repo's Apache-2.0 kit layer. Review recorded in PR #5.

### Local preprocessing model boundary (v1.2.0)

v1.2.0 documents a **vendor-neutral local preprocessing adapter contract**
(`choreography/local-preprocessing.md`); it does **not** bundle an
implementation. Where a concrete implementation is referenced (e.g. Desert Ant),
the boundary is explicit:

- **Desert Ant is an optional reference, not a dependency** — its code, model
  files, and license text are NOT copied into this repo.
- **Separate vendor license.** Desert Ant models carry their own
  **source-available vendor license** (not an OSI open-source license) that is
  **distinct from the Apache-2.0 kit layer** and does not extend to it. The
  model license governs the models; the kit license governs this repo.
  Production distribution of those models is subject to the vendor's
  attribution and monthly-active-device terms — see the vendor's public docs.
- **No invented figures.** v1.2.0 states expected benefits as intended
  outcomes only.

### Public-domain hosting boundary (v1.2.0)

v1.2.0 adopts the canonical-site decision for the Team6 site:

- **Canonical public site:** `https://team6.askaconsult.com/`.
- **Repository/source of truth:** `https://github.com/ahrazzle/team6-kit`.
- **GitHub Pages:** not used. The old Pages site was taken down.
- **Deployment boundary:** the canonical site is served by the ASKA-managed
  Team6 deployment; DNS and deployment settings are outside this repo.
- **Visible navigation back to ASKA Digital:** the Team6 site (`index.html`)
  carries visible nav + footer links back to `https://askaconsult.com/digital/`.

## Provenance

- Engine: Hermes by Nous Research — MIT (https://github.com/NousResearch/hermes-agent)
- This repo: `Team6-kit` — Apache-2.0 core + proprietary packs by contract
- `AUDIT/fork-commit-1.md` — the first commit's cleanliness evidence (surface
  scan, staged-tree manifest, invariant check, verification lineage)
