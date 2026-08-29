<!-- GENERICIZED: 7×{CLIENT}, 3×{RELATIONSHIP} | source: skills/github/open-source-project-packaging/references/{CLIENT} -->
# {CLIENT} repo packaging pass ({CLIENT})

Task: "make a final revision to the github project — explanation and instruction docs on what the framework is, how to use it, how to make plugins, how to build on / contribute, everything a good open source project needs to get going."

Repo: `{RELATIONSHIP}/{CLIENT}` (public, fork-target for external teams building wrapper games on the rhythm-typing framework).

## What was added

| File | Purpose |
|---|---|
| `LICENSE` | MIT full text — README claimed MIT but no file existed. Also added `"license": "MIT"` to package.json. |
| `SECURITY.md` | Private reporting (GitHub Security tab), trust model ("plugins are trusted code", "no telemetry / content never leaves the browser"), response SLA. |
| `CODE_OF_CONDUCT.md` | Contributor Covenant 2.1. |
| `CHANGELOG.md` | Keep-a-Changelog; `[Unreleased]` + `[0.1.0]`. |

## What was fixed

- **README live URL** was `{RELATIONSHIP}.github.io/{CLIENT}` → pointed to `https://{CLIENT}` (the custom domain that went live earlier in the session).
- **Badges** added (License MIT, PRs-welcome) + a Community & Governance section.
- **Stale doc links**: `API_REFERENCE.md` had 3 links to `PLUGIN_DEVELOPMENT.md` (renamed to `docs/PLUGIN_GUIDE.md`). Fixed all, including 2 refs inside source code comments (left the code comments as-is — they're `§`-section cross-references, harmless).
- **Duplicate CONTRIBUTING**: root + `docs/CONTRIBUTING.md` had diverged. Root is GitHub-surface canonical; deleted `docs/CONTRIBUTING.md`. Updated root CONTRIBUTING's stale `PLUGIN_DEVELOPMENT.md` → `docs/PLUGIN_GUIDE.md` references.

## Verification run

- `npm run docs` → "Docs check passed — API reference matches source."
- `npm test` → 46/46 green.
- All 4 new files HTTP 200 at `raw.githubusercontent.com/{RELATIONSHIP}/{CLIENT}<file>`.
- README served copy confirmed to contain `https://{CLIENT}`.

Commit: `bbbb19a docs: add LICENSE, SECURITY, CODE_OF_CONDUCT, CHANGELOG; fix stale doc links; consolidate CONTRIBUTING` (9 files, +174/−143).

## Reusable pattern

The "final revision" for a repo going public is a checklist, not a task: LICENSE(+package.json claim) → README(quickstart→architecture→concepts→docs→community + badges + live URL) → single canonical CONTRIBUTING → SECURITY → CODE_OF_CONDUCT → CHANGELOG → docs-consistency check → grep for stale old-filename links → verify all files served at raw URL.
