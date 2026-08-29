<!-- GENERICIZED: 1×{AMOUNT}, 1×{CLIENT}, 1×{RELATIONSHIP} | source: skills/software-development/nodejs-project-bringup/SKILL.md -->
---
name: nodejs-project-bringup
description: Use when taking over an inherited Node.js project's gates.
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
metadata:
  hermes:
    tags: [nodejs, portability, esm, debugging, handoff]
    related_skills: [systematic-debugging, codebase-inspection]
---

# Node.js Project Bring-up

Use when taking over, verifying, or resurrecting an inherited Node.js project (a handoff, a stalled workspace, a tree with no git history). Goal: prove the existing gates pass on THIS machine, fix only what environment broke, and never touch model/data semantics. Then the tree is safe to edit.

## When to Use

- A handoff or stalled workspace arrives and the task is "get it running / finish it" — run the gates before believing the docs.
- A verify/test/build script fails with ENOENT on a path containing a space.
- A build fails on a missing native module after a machine/platform change.
- You must prove a mechanical repair changed nothing in the data/model layer.

## Steps

1. **Map the layout first.** `package.json` may live per-directory (`engine/`, `ui/`) with NO root package.json. Find every one before running `npm run <script>` — running from the wrong directory gives a misleading ENOENT. The project's own docs (build brief, README) define which directory each gate runs from and what "done" means.

2. **Run the project's own gates exactly as documented** (`npm run verify`, `validate.py`, test suites, build). Verify, don't assume — "claimed green" is not green until executed on this host.

3. **Gate fails with ENOENT and the path contains a space?** Suspect the ESM URL path bug (see Pitfalls). Grep the whole source tree, not just the failing file:
   `grep -rn "\.pathname" --include="*.ts" --include="*.js" .`
   Fix EVERY occurrence before re-running — each fixed file can surface the next one in the chain.

4. **Gate fails with a missing native module (esbuild, rollup, sharp)?** Committed `node_modules` carry another platform's binaries (e.g. linux-arm64 on a macOS host). Fix: `npm install` in that directory — it refreshes platform-specific binaries. `.gitignore` almost always already excludes `node_modules/`, so this never enters the commit.

5. **Prove semantics untouched.** A byte-identical round-trip test (exporter reproduces the committed data file exactly) is the strongest proof that mechanical fixes changed nothing. Report it with the gate output: green gates + byte-identical round-trip = model untouched.

## Pitfalls

- **`new URL(...).pathname` percent-encodes spaces.** `new URL("./app.json", import.meta.url).pathname` on a path containing a space yields `app%20work/app.json`; `fs.readFileSync` / `readdirSync` / `writeFileSync` / `execFileSync` all fail with ENOENT (or readdir ENOENT inside a child process). The path class is a genuine code bug, not an environment quirk — the original author's path simply had no space, so it never surfaced.
- **Fix is `fileURLToPath`.** Replace `.pathname` with `fileURLToPath(new URL(...))` and add `import { fileURLToPath } from "node:url";`. Mechanical multi-file sweep:
  `perl -0pi -e 's/new URL\("([^"]+)", import\.meta\.url\)\.pathname/fileURLToPath(new URL("{AMOUNT}", import.meta.url))/g' <files>`
  plus insert the import at the top of each file (sed `1s/^import /import { fileURLToPath } from "node:url";\nimport /` only if not already present).
- **`execFileSync` args need the same fix** — a child script path built via `.pathname` fails identically.
- **After each mechanical fix, re-run the gate.** Errors surface one layer at a time (test → exporter → graph loader).
- **Don't "fix" documented drifts.** A test asserting exactly N known mismatches (e.g. two walk drifts) — zero mismatches means someone "fixed" a documented defect and the comments now lie. Preserve, don't repair.

## Verification

- Full gate suite green: verify, validate, personas/run, build.
- `grep -rn "\.pathname"` over source returns nothing.
- Round-trip test byte-identical if one exists.

Session case study: see `references/{CLIENT}`.
