<!-- GENERICIZED: 6×{AMOUNT}, 10×{CLIENT}, 3×{RELATIONSHIP} | source: skills/software-development/nodejs-project-bringup/references/{CLIENT} -->
# Case Study: {CLIENT} / {CLIENT} Baseline Bring-up ({CLIENT})

Inherited project: "{CLIENT}" = {CLIENT} education program. Product engine = {CLIENT}, a
skill-simulation webapp (158 skills, 12 branches, 72 activities; validated against 5 synthetic
lifetimes). Work stopped at a rebuild handoff; the UI redesign never started. Task: P0 baseline —
re-run the documented gates, close the one-way door (git init) once approved.

Workspace: `/Users/{RELATIONSHIP}/{CLIENT}{CLIENT}/wrk/3ft6/previousclaude/{CLIENT}/{CLIENT}`
(active tree; sibling version folders `v1`…`v16 freeflow`, `webapp v1`…`v16` are user backups — untouched).

## Layout (no root package.json)

- `engine/package.json` — scripts: `verify` (tsx verify-contract.ts), `export`, `personas` (tsx run.ts)
- `ui/package.json` — scripts: `dev`, `build` (vite), `data`, `personas`, `validate` (python3 validate.py), `verify` (cd ../engine && tsx verify-contract.ts)
- `validate.py` at repo root; run `python3 validate.py .` (14 rules, must end PASSED)

Running `npm run verify` from the repo root fails ENOENT (no root package.json). Run from `engine/`.

## Failure 1 — ESM URL pathname bug (percent-encoded space)

`npm run verify` → `Error: ENOENT: no such file or directory, open '.../ai%20work/.../ui/src/app.json'`.

Root cause: `verify-contract.ts` used `new URL("../ui/src/app.json", import.meta.url).pathname`.
`.pathname` returns a URL-encoded path — the space in `ai work` became `%20`, and `fs.readFileSync`
failed. Original author's path `/Users/{RELATIONSHIP}/Documents/{RELATIONSHIP}/...` had no space, so it never
surfaced. This is a genuine code bug, not an environment quirk.

Files carrying the same bug (found by `grep -rn "\.pathname" --include="*.ts" engine/`):
- `engine/verify-contract.ts` (APP_JSON, EXPORT_OUT, execFileSync arg for export-app.ts)
- `engine/graph.ts` (DIR via `path.resolve(new URL(".", import.meta.url).pathname, "..")` — broke `readdirSync` as an ENOENT inside the child process)
- `engine/export-app.ts` (writeFileSync target)
- `engine/export.ts`, `engine/export-loop.ts`, `engine/export-orient.ts`, `engine/run.ts` (writeFileSync targets; these break `npm run personas` and the other exporters)

Fix: `fileURLToPath(new URL(...))` + `import { fileURLToPath } from "node:url";`.
Mechanical sweep: `perl -0pi -e 's/new URL\("([^"]+)", import\.meta\.url\)\.pathname/fileURLToPath(new URL("{AMOUNT}", import.meta.url))/g' <files>`,
import insert: `sed -i '' '1s/^import /import { fileURLToPath } from "node:url";\nimport /' <file>` (guard with grep -q first).

## Failure 2 — wrong-platform native binaries in committed node_modules

- `engine` esbuild error: "The package @esbuild/linux-arm64 could not be found" — node_modules shipped linux binaries, host is macOS arm64. Fix: `npm install` in `engine/` (changed 26 packages, platform refresh).
- `ui` build: rollup `MODULE_NOT_FOUND` for its native binding — same cause. Fix: `npm install` in `ui/`, then `npm run build` works.
- `.gitignore` already excludes `node_modules/` and `dist/` — platform refresh never enters the commit.

## Failure 3 — script-runner location

`npm run verify` from repo root → ENOENT package.json. The gate lives in `engine/` (or `ui/` per the
brief). Read the brief's "Correctness gates" section for the exact run locations.

## Proof that semantics were untouched

After the mechanical fixes, all gates green:
- `npm run verify` (engine/): round-trip **byte-identical ({AMOUNT} bytes)**; walk parity 25/27 + both
  documented drifts unchanged (athlete/Recovery 20 vs 19, athlete/Nutrition 10 vs 9); all 6 shape guards pass.
- `python3 validate.py .` → PASSED
- `npm run personas` → runs (5 synthetic lives)
- `npm run build` → dist/index.html produced

The byte-identical round-trip is the load-bearing proof: the exporter re-ran against unchanged inputs
and reproduced the committed app.json exactly, so the graph/model was not altered by the fixes.

## Remaining knowns for the follow-up

- `git init` + baseline commit (build brief §2a) was held for approval — one-way door still open.
- DEPLOY.md quotes {AMOUNT} / FINDINGS-phase1.md {AMOUNT} for Ravi/Writing frozen SP; the shipped app.json
  actually produces {AMOUNT} — update the docs, not the number.
- `package-lock.json` will carry the platform refresh in the baseline commit.
- All 15 UI states (§4 of the build brief) including two degenerate frozen-SP cases (Marta {AMOUNT} with
  no remedy; Ada all-four) must render deliberately in the rebuild; no localStorage; no node graph.
