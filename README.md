# Team6-kit

**Archival.** This repository is no longer the home of the Team6 operating
procedure. The procedure lives in the Protean org repository system. This repo is
kept as a pointer, so links that already exist keep resolving.

No content was deleted: the historical files remain in this tree.

## Where the procedure lives now

| What you are looking for | Where it lives |
|---|---|
| The live composer that assembles a team from parts | [`aska-digital/protean-kit`](https://github.com/aska-digital/protean-kit) |
| GitHub workflow procedures and the PR-audit QA checklist, including the public-claim gate contracts (PQA-CLM, PQA-DOL, PQA-STAND) | [`aska-digital/protean-github-flow`](https://github.com/aska-digital/protean-github-flow) |
| The operating doctrine: the default pipeline, the role delegation map, and the handoff-brief template with its public-surface admission fields | [`aska-digital/protean-doctrine`](https://github.com/aska-digital/protean-doctrine) |

The canonical site for the kit remains https://team6.askaconsult.com/, and the
ASKA corporate page for the service remains https://www.askaconsult.com/team6.

## Provenance of the two SOP additions that landed here

Both additions below were made in this repository and have since been ported to
their org homes. Each org repository keeps its own version numbering; the version
numbers used here do not carry over.

- **Public-claim gate contracts** (PQA-CLM, PQA-DOL, PQA-STAND) were added here as
  pull request #47 (merge commit `4e37686`) and ported to
  `aska-digital/protean-github-flow`.
- **Public-surface admission fields** were added here as pull request #48 (merge
  commit `bc1a38a`) and ported to `aska-digital/protean-doctrine`.
- Both ports landed on 2026-09-17.

## Open follow-up

Pull request #49 adds a semantic-verification gate on top of the contract content
that #47 brought here. While #49 is open, the two files it edits stay untouched in
this repository so the change remains reviewable. When #49 resolves, that gate
ports to the org home as well, and those two files are reduced to redirect stubs.

## Status of this tree

The files under `templates/`, `choreography/`, `build/`, `registry/`, `AUDIT/`,
and `demo/` are historical. They are kept for provenance and are no longer the
source of truth for the operating procedure. Read the org repositories in the
table above for the current procedure.

## License

Unchanged: the engine this kit builds on is Hermes by Nous Research (MIT); the kit
itself (profiles, rules, builder) is Apache-2.0; the vertical packs are not in this
repository. `LICENSING.md` holds the full terms.
