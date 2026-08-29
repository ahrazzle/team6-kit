<!-- GENERICIZED: 7×{AMOUNT}, 12×{CLIENT}, 3×{RELATIONSHIP} | source: skills/research/project-takeover-recon/references/{CLIENT}-{CLIENT} -->
# Worked example: {CLIENT} / {CLIENT} takeover ({CLIENT})

Workspace: `/Users/{RELATIONSHIP}/{CLIENT}{CLIENT}/wrk/3ft6/previousclaude/{CLIENT}/`

- `3rdF.html` — single-file landing page (dark/amber, Jul 25). Substantially built, never deployed/reviewed.
- `skill_activity_outcome_loop.png/.svg` — the loop diagram.
- `{CLIENT}` — the product engine. 16 UI iterations (webapp v2–v13, v14–v16 freeflow), then a `rebuild/` handoff prepared by Claude CoWork (Aug 5). Work stopped exactly at the handoff line.

## The handoff package (`{CLIENT}`)

- `01-DATA-CONTRACT.md`, `02-DESIGN-BRIEF.md`, `03-BUILD-BRIEF.md`, `README.md`, `design/` — **EMPTY** (design step never started).
- **Locked:** 28 authored JSON files (158 skills, 12 branches, 72 activities), `engine/`, `validate.py`, `SPEC-v0.4.md`, `ui/src/lib/walk.js` (port verbatim).
- **Open:** `ui/src/{CLIENT}` (35 KB engineer's sketch), `index.css`, `tailwind.config.js` (empty theme).
- Build order per brief: skill detail → daily loop → orientation → guarded paths.
- Product reframe (the point of the product): a stuck skill must read as an INSTRUCTION — remedy beside the number.

## Verified baseline (ran {CLIENT}, Node v22.17.1)

| Gate | Command | Result |
|---|---|---|
| verify | `npm run verify` (engine/verify-contract.ts) | round-trip byte-identical {AMOUNT} B · walk parity 25/27 (known drifts athlete/Recovery 20v19, athlete/Nutrition 10v9 — KEEP) · 6/6 shape invariants |
| validate | `npm run validate` | PASSED — 158 skills, 99 stubs, 72 activities; 158 gates, 151 band gates, 876 targeted + 121 broadcast + 83 negative edges |
| personas | `npm run personas` (engine/run.ts) | 5 lives: Ada 12, Ravi 34, Marta 58, Jonah 41, Kit 28 (adversarial) + senescence and decay scenarios |
| build | `npm run build` | Vite 5.4.21 OK; base "./" → dist/index.html opens from filesystem |

## Doc-vs-execution discrepancies (handoff claims were stale)

1. **Cashed SP: brief §4 says untriggered → WRONG.** Jonah's live run shows `cashed 180` on Conflict Resolution. UI must render the cashed state.
2. **Worst-case degenerate: brief says Marta {AMOUNT} frozen no-remedy → WRONG.** Kit (adversarial) has {AMOUNT} / {AMOUNT} / {AMOUNT} stranded SP. The "frozen with no remedy" component must survive seven-digit numbers.
3. **`inadmissible`:** claim holds — genuinely zero across all fixtures.
4. All other §4 fixture states reproduced (Marta CEILING 17, Ravi Writing {AMOUNT}, Ada provisional 2, locked 59/716/{AMOUNT}, escrow pending, senescence, age caps).

## Infra facts

- **NO git repo anywhere** — brief's step-1 `git init` never ran. Redesign deletes `ui/src/{CLIENT}`, so the tree was a one-way door. `git init` + baseline commit is the first build action.
- `.gitignore` covers node_modules/dist/.DS_Store but NOT `ui/build/` (stale Jul-29) nor `vite.config.js.timestamp-*.mjs` temp files — add before baseline commit.
- Stack: React 18 + Vite 5 + Tailwind 3 + tsx/esbuild — all MIT, commercial-safe.
- Single absolute path to old `/Users/{RELATIONSHIP}/Documents/{RELATIONSHIP}/...` lives in `handoff/03-BUILD-BRIEF.md` (doc, not code) — portability clean.
- `npm run validate` passes even though `../{CLIENT}*` dirs do not exist — the validator tolerates missing optional inputs; slices never mattered.
- Engine also ships `snapshot.json`, `loop.json`, `orient.json` (export artifacts) and `smoke.ts`, `FINDINGS-raw.txt`.
- Sacred constraints (from handoff README): seven bands · four channels never merged · no progress bar to a maximum · application/consequence require provenance · provisional ≠ verified · decay is rust not loss · frozen SP travels with its remedy · `liftable: false` means no override exists.
