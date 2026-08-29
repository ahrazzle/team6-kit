<!-- GENERICIZED: 3×{CLIENT}, 2×{RELATIONSHIP} | source: skills/software-development/framework-handoff-package/SKILL.md -->
---
name: framework-handoff-package
description: Use when packaging a framework for external teams to fork.
version: 1.0.0
author: {RELATIONSHIP} ({RELATIONSHIP}), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [handoff, documentation, framework, open-source, onboarding, api-reference]
    related_skills: [rhythm-game-development, static-site-production, integration-testing]
---

# Framework Handoff Package

Class-level discipline for making a framework consumable by a stranger — another agent team, a forker, a future self — so they can build a plugin/game/extension on top of it in one session WITHOUT asking questions. Proven building the {CLIENT} rhythm-typing framework handoff (5 docs, docs-linter, worked example type-checked against strict tsc).

## When to Use

- A framework/core/library is "done" and another team (Team6 instances, external fork teams) will build on top of it
- The user asks for a handoff/onboarding package for a repo
- A plugin-architecture codebase needs its plugin contract documented
- You want future sessions to resume work without re-deriving the API

## The 5-Document Structure

Deliver these files at repo root (or `docs/` where noted):

| File | Purpose | Non-negotiable content |
|---|---|---|
| `README.md` | First stop — pitch + architecture + quick start | One-paragraph pitch, layer diagram, `npm install` / `npm test` / build / serve, per-file `src/` map, links to the rest |
| `PLUGIN_DEVELOPMENT.md` | THE critical doc — the plugin contract | Every interface method documented, the event/data flow, config tables (timing windows, multipliers, color codes), **a complete worked example plugin built step-by-step with real code**, best practices, and a pitfalls section |
| `API_REFERENCE.md` | Every exported class with exact signatures | Signatures READ FROM SOURCE, not memory; ThemeDescriptor/Config structures; flag class-only members (interface vs class split) |
| `CONTRIBUTING.md` | Tests, build, deploy, conventions | Exact commands; documented testing lessons; code style |
| `docs/EXAMPLE_PLUGIN.md` | Reference implementation walkthrough | What the reference plugin does, how it's wired, how a real plugin differs |

## The Worked Example MUST be real

- The `PLUGIN_DEVELOPMENT.md` worked example (e.g. "build a Word Racer plugin") is not decorative prose — write the full code, then **reconstruct it into a real file and type-check it** (`npx tsc --noEmit` under strict). A doc whose example doesn't compile is worse than no example: it teaches a broken pattern.
- The type-checker will catch contract mismatches (e.g. a plugin hooking a class method that isn't on the interface). When it does, fix the DOC, not the code — and document the interface-vs-class distinction in the API reference.
- Wire the example the way real consumers will (the actual `RawBus → NormalizedBus → Judge → FeedbackLayer + Plugin` pattern from the demo), not a simplified fantasy.

## API Consistency Linter (the key verification)

Docs drift from source the moment they're written. Add a script (`scripts/check-docs.mjs`) run via `npm run docs` that:
1. Asserts all 5 docs exist.
2. Parses every `ClassName.method()` token in `API_REFERENCE.md` and greps the actual source for `methodName(` — fails on any method documented that doesn't exist in code.

This makes "docs are current" a CI-checkable property instead of a promise. Run it before committing the handoff.

## Pitfalls

- **Never invent APIs.** Read the real source files first; the docs must match reality byte-for-byte. A doc describing `getJudgmentCounts()` when the code calls it `stats` ships a bug to every forker.
- **Interface vs class members.** A `GamePlugin` contract may return a *narrow* interface (from types.ts) while the concrete class has extra methods (`announce`, `markNoteJudged`, `resetStats`). Document which is which — the example should use the concrete class where it needs the extra methods, and still satisfy `implements GamePlugin`.
- **Doc-only commits still need the bundle rebuilt** if the page imports one — see `static-site-production` for the served-vs-source drift class.
- **package.json hygiene**: update the description to something professional, add a `build` and `docs` script, sync the lockfile, add any devDeps the docs tooling needs (e.g. `esbuild`).
- **Rename = update the linter file list + grep for the old name.** After moving/renaming a doc, `npm run docs` fails on the old filename, stale `*.md` references point at the deleted file, and the bundle-import check (if the docs were wrong about a symbol) misses nothing — close all three, not just the rename.

## Open-source finalization (the full kit)

When the user asks for "everything a good open source project needs to get going", the handoff docs are only the first layer. Add the legal + community surface in one pass (proven finalizing the {CLIENT} repo):

| File | Content |
|---|---|
| `LICENSE` | MIT — README may already *claim* MIT; the license FILE is what makes it legal. Check for the file, not the claim. |
| `SECURITY.md` | Private vulnerability reporting (GitHub advisories), trust model, no-telemetry promise |
| `CODE_OF_CONDUCT.md` | Contributor Covenant 2.1 |
| `CHANGELOG.md` | Keep-a-Changelog: a released version + an Unreleased section |
| `CONTRIBUTING.md` | Consolidate duplicates to ONE canonical location (root is the GitHub-surface default) |
| README badges + live URL | MIT + PRs-welcome badges; the live URL (e.g. `{CLIENT}`), NOT the stale `*.github.io` placeholder |
| `package.json` | `"license": "MIT"` field + professional description |

## The divergent-duplicate-docs trap

A docs pass that renames or rewrites a doc (e.g. `PLUGIN_DEVELOPMENT.md` → `docs/PLUGIN_GUIDE.md`) frequently leaves the OLD file committed and orphaned — now two divergent documents cover the same topic, README points at the new one, stale cross-references point at the old, and neither matches the other's length or content. The user has explicitly flagged duplicate/conflicting files as a pet peeve.

Consolidation procedure (proven):
1. **Pick the canonical file** — follow the README/API_REFERENCE/CONTRIBUTING links to find which doc the project actually points at; the others are orphans.
2. **Transplant the unique valuable content** into the canonical file (a worked example, detailed pitfalls) so nothing real is lost.
3. **`git rm` the orphan**, then grep the whole repo for the old filename — zero hits in `*.md` (fix code comments too, not just links).
4. **Update the docs-linter's file list** (`scripts/check-docs.mjs` `DOCS` array) to the canonical path — a linter that still asserts the deleted filename fails for the right reason: it's telling you the canonical list is stale. The linter passing again is the consolidation's proof.
5. Verify the worked example's imports against the actual shipped bundle symbols (`grep -o 'createSession\|ClassName' dist/game.js`) so transplanted code isn't fiction.

## Verifying a handoff is done

- All 5 docs exist and `npm run docs` passes (80+ symbols checked).
- `npm run build` produces the bundle; tests still green.
- The worked example file type-checks standalone.
- A stranger could fork and build without a single question — that's the acceptance test.

## Consumer side

The other half of the handoff: when a team builds ON the framework (plugin/game), they must verify the contract against the shipped bundle, not the type declarations — see `references/consumer-side-verification.md` (stale `.d.ts` vs bundle, dead-hook detection by grep, the input-routing gate, and the upstream flag for stale handoff artifacts).
