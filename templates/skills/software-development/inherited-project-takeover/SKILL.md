<!-- GENERICIZED: 3×{CLIENT} | source: skills/software-development/inherited-project-takeover/SKILL.md -->
---
name: inherited-project-takeover
description: Use when taking over an unfinished/inherited project.
---

# Inherited Project Takeover

Use when handed an unfinished project from another agent or tool (Claude CoWork,
a departed teammate, a stale workspace). The handoff usually includes build
briefs, data contracts, and a "done when" list — the finish line is documented,
not guessed. Your job: prove the baseline, make the tree safe to change, then
build to the documented finish line without breaking the model.

## Step 0 — Recon (find the contract)

Before touching anything, locate and read the governing documents:
- `*BUILD-BRIEF*` / `BUILD-PLAN.md` — what "done" means, what is untouchable,
  what is replaceable, the de-risking build order.
- `*DATA-CONTRACT*` — the authority on every field name and invariant.
- `*DESIGN*` doc — the build contract after P1; read it end to end and extract
  acceptance criteria before writing any code.
- `DEPLOY.md` / `README.md` — demo paths and run instructions.

Note which files the brief marks **untouchable** (the validated model/engine)
versus **replaceable** (the redesign surface). "Preserve, don't fix" lists are
real: documented drift is a defect you must NOT repair.

## Step 1 — Verify the baseline BEFORE any edit

"Claimed green" is not green. Run every documented gate yourself, from the
correct directory (npm scripts often live in a sub-package — `engine/` or `ui/`,
not the repo root; check each `package.json`).

If a gate fails, classify the failure before touching anything:
- **Environment blocker** (platform mismatch, path portability) → fix it, but
  fix only the harness, never the model. Proof the model is untouched: the
  round-trip/byte-identity checks still pass.
- **Model failure** → STOP. Do not "fix" the model; report it.

## Step 2 — Close the one-way door (git baseline)

The build brief's step 1 is almost always `git init` because the redesign
deletes the old prototype. Do this BEFORE any destructive edit:

1. **`.gitignore` hygiene first** — the existing file covers the obvious
   (`node_modules/`, `dist/`, `.DS_Store`) but misses stale build dirs
   (`ui/build/`) and temp files (`vite.config.js.timestamp-*.mjs`). Add them.
2. `git init && git add -A`
3. **Review the staged list before committing** — count by top-level directory,
   verify the expected categories are present (graph JSONs, engine sources, ui
   sources, docs), and junk-check with `git status --short | grep -E
   "node_modules|dist/|timestamp|\.DS_Store"`.
4. Commit with the brief's prescribed message. Working tree must be clean after.
5. Numbered version folders / backups around the workspace are user-made: never
   alter them, never read them as current.

Hold `git init` at the approval gate if the workflow demands it — but once
approved, do it immediately and report the commit hash.

## Step 3 — Read the design doc as your build contract

The P1 design doc (if one exists) is binding, not advisory. Extract the
acceptance criteria: degenerate states are design problems, not exceptions —
the brief will name edge cases that MUST render deliberately (e.g. frozen-with-
no-remedy, all-four-remedies, seven-digit magnitudes, cashed-but-locked).
These are hard gates, not suggestions. Design decisions you deviate from at
build time get logged in the handoff's decision table, not buried in code.

## Step 4 — Build in the documented de-risking order, verify after every change

Follow the brief's screen order (usually: hardest screen first, because it
forces every state to exist). Run the primary gate after every change. If it
was green when you began and red when you finish, you broke the model — not
the test.

## Step 5 — Decision log

Record build-time decisions in the handoff's decision table so the user can
veto them cheaply. Note every deviation from the design doc with a reason.

## Pitfalls

- **Node ESM path portability** — `new URL(...).import.meta.url.pathname`
  percent-encodes spaces (`ai work` → `ai%20work`) → ENOENT on macOS paths
  with spaces. Use `fileURLToPath`. See `references/node-esm-path-portability.md`.
- **Committed node_modules carry the wrong platform's native binaries** — a
  handoff committed on Linux ships `linux-arm64` esbuild/rollup; on macOS the
  run fails with `MODULE_NOT_FOUND` in `rollup/dist/native.js` or an esbuild
  `generateBinPath` error. The FIX is `npm install` on the target host to
  refresh platform packages — this is environment repair, not a code bug, and
  it does not touch the model. The lockfile, not node_modules, is the portable
  unit.
- **npm scripts live where the `package.json` is** — running `npm run verify`
  at the repo root fails with ENOENT when the script is in `engine/`. Check
  each package.json's scripts before assuming the invocation.
- **A script that "worked on the author's machine" may be path-fragile** — if
  the original path had no spaces and yours does, portability bugs surface
  only on your machine. Sweep with `grep -rn "\.pathname"` over the source
  tree; fix every instance, not just the first.
- **Shipped `.d.ts` can be stale relative to the canonical bundle** — in a
  handoff with compiled `dist/`, the standalone type declarations may predate
  `bundle.js`/`game.js` (check file mtimes — they tell the story). Before
  authoring against the handoff's API, grep the ACTUAL bundle class bodies and
  exported symbols; when the `.d.ts` disagrees with the bundle, the bundle
  wins. Author plugin-local types against the bundle surface and flag the stale
  declarations to the team so they get regenerated.
- **Interface members ≠ live hooks** — a lifecycle method existing in
  `types.ts`/`.d.ts` does not mean anything invokes it. Grep call sites
  (`this.hooks.onX?.(` / `.onX?.(`) in the bundle to verify which hooks
  actually fire; dead hooks (declared, implemented only in a debug plugin,
  never called by the core) must not be the load-bearing part of a build plan.
  Lifecycle detection belongs on what the code calls, not what the interface
  declares.
- **Gates that were green at start must stay green** — after any harness fix,
  re-run the full suite and paste real output, not claims.

## Verification steps

- `npm run verify` (or the brief's primary gate) — green before and after.
- `npm run build` produces `dist/index.html` that opens from the filesystem.
- `git status --short` is clean after the baseline commit.
- Report: commit hash, gate outputs (verbatim), and what you fixed and why.

## Support files

- `references/node-esm-path-portability.md` — the `fileURLToPath` fix recipe,
  error signature, and sweep commands.
- `references/{CLIENT}` — verified {CLIENT} bundle surface
  (live vs dead hooks, createSession shape, menu gate re-baseline sequence);
  consult before building {CLIENT} plugins.
