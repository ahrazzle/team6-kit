# Makepad Learnings: Conceptual Reference Audit

STATUS: CONCEPTUAL REFERENCE AUDIT

This file records the conceptual reference audit. It contains a 23-row candidate table surveying all 27 Makepad org repositories (25 unique repositories named across 23 rows; some recur). No code, prompt, transcript, asset, or source prose is copied. Every adopted row links to the Makepad repository and its committed license. MIT and Apache-2.0 sources are used for conceptual reference only. Sources without a committed license are inspiration-only, with no excerpt.

Source brief: the Makepad-learnings brief candidate table, evaluated against the shipped Team6-kit surfaces. This record is public-safe: it uses generic role labels only and contains no real agent names, profile names, private paths, or instance tokens.

## Evidence policy

The evidence tag `[VERIFIED - public conceptual source]` means a claim is grounded in a public source that is linked below and adopted as a *principle* — never by copying code, prompts, assets, or prose. Every adopted row links to the Makepad repository and its committed license file.

- MIT and Apache-2.0 sources are used for conceptual reference only. No dependency, benchmark result, compatibility, hardware-support, or performance claim is added, and no source code or excerpt is copied.
- Sources without a committed license are inspiration-only, with no excerpt. They supply no code, prose, prompt, asset, or dependency and carry the explicit `no committed LICENSE` marker.
- The tag `[VERIFIED - public conceptual source]` appears beside every Makepad-derived statement in this repository. It is not an implementation, support, or live-deployment claim.

## Candidate matrix

Exactly 23 candidate rows cover the A1-A7, B1-B8, and C1-C8 brief table. C8 is a single row covering four empty repositories. The brief surveyed all 27 Makepad org repositories; this file's inventory is 25 unique repositories across 23 rows (28 repository-URL mentions).

| Candidate | Makepad source URL | Evidence path or claim | License status | Current Team6 surface | Disposition | Owner role | Acceptance evidence or reopen trigger |
|---|---|---|---|---|---|---|---|
| A1 Core UI runtime | https://github.com/makepad/makepad | [VERIFIED - public conceptual source] Declarative design description kept separate from assembly and renderer. Principle only. | MIT (committed LICENSE) | html-report-authoring SKILL, WHY, README, CHANGELOG | ADOPT | architecture owner | Repo URL + license URL present; no Makepad API/code/copied wording |
| A2 microserde | https://github.com/makepad/microserde | [VERIFIED - public conceptual source] Serialization overhead as a build/runtime design question. | MIT (committed LICENSE) | project-foundation-scaffold SKILL, README, CHANGELOG | ADOPT | build owner | Repo URL + license URL present; no dependency/benchmark/replacement claim |
| A3 DeepSeek integration | https://github.com/makepad/llama_antirez_deepseek | [VERIFIED - public conceptual source] Model-wire and integration reference. | MIT (committed LICENSE) | evaluating-llms-harness SKILL, README, CHANGELOG | ADOPT | build owner | Repo URL + license URL present; no compatibility/supported-model claim |
| A4 NVFP4 quantization | https://github.com/makepad/llama_nvfp4 | [VERIFIED - public conceptual source] Hardware-specific quantization reference. | MIT (committed LICENSE) | evaluating-llms-harness SKILL, README, CHANGELOG | ADOPT | build owner | Repo URL + license URL present; no hardware/performance claim |
| A5 stitch | https://github.com/makepad/stitch | Fast WASM interpreter, proof-pending for a Team6 edge-WASM workload. | MIT (committed LICENSE) | none | DEFERRED | build owner | Reopen only for a concrete edge-WASM workload; pin revision, verify MIT, reproducible benchmark before any decision |
| A6 jsast | https://github.com/makepad/jsast | JavaScript AST parser, proof-pending for a current build/analysis need. | MIT (committed LICENSE) | none | DEFERRED | build owner | Reopen only when a current build/analysis task needs an AST parser; verify license and compatibility, test a minimal real use case |
| A7 makepad-mpsl-parser | https://github.com/makepad/makepad-mpsl-parser | No committed license verified. | no committed LICENSE | none | REJECTED | build owner | Inspiration-only, no excerpt, no code, no parser dependency; reconsider only after a primary-source license grant |
| B1 cross-platform Rust UI | https://github.com/makepad/makepad-internal | Cross-platform Rust UI build workflow, proof-pending. | MIT (committed LICENSE) | none | PROOF-PENDING | build owner | SPIKE-B1: pinned revision must build a minimal native + WASM/WebGL target on macOS and Linux with read-back; does not auto-adopt |
| B2 historical live-coding IDE | https://github.com/makepad/makepad_history | [VERIFIED - public conceptual source] Historical architecture note: exploratory/live-coding work stays distinct from a supported operating contract. | MIT (committed LICENSE) | WHY, README, CHANGELOG | ADOPT | architecture owner | Repo URL + license URL present; no IDE/VR/runtime feature adopted |
| B3 WASM GitHub Pages examples | https://github.com/makepad/makepad.github.io | [VERIFIED - public conceptual source] Static publishing reference: WASM example treated as a published artifact with independently checked URL/assets/bytes. | Apache-2.0 (committed LICENSE) | github-pages-deployment SKILL, README, CHANGELOG | ADOPT | build owner | Repo URL + license URL present; no site code/asset copied, no Team6 deployment changed |
| B4 fonts | https://github.com/makepad/fonts | Asset pack, proof-pending attribution and license proof. | MIT (committed LICENSE) | none | DEFERRED | copy owner | Reopen only after per-file attribution, committed license proof, asset hashes, and the asset gate; no font asset enters this PR |
| B5 loader | https://github.com/makepad/loader | Source is empty or unverifiable, no usable tree or license evidence. | unverifiable | none | REJECTED | QA owner | No adoption claim possible |
| B6 runner | https://github.com/makepad/runner | Source is empty or unverifiable, no usable tree or license evidence. | unverifiable | none | REJECTED | QA owner | No adoption claim possible |
| B7 boiler | https://github.com/makepad/boiler | Legacy reference is outdated and addresses no current Team6 gap. | MIT (committed LICENSE) | none | REJECTED | architecture owner | No current PR surface |
| B8 experiments | https://github.com/makepad/experiments | Experimental apps, proof-pending a useful minimal representative build. | MIT (committed LICENSE) | none | DEFERRED | build owner | Reopen only after a pinned revision builds a minimal representative app useful outside the experiment; keep all experimental code out |
| C1 native GPU cfg-selected backends | https://github.com/makepad/glui | Native GPU cfg-selected backends, proof-pending. | MIT (committed LICENSE) | none | PROOF-PENDING | build owner | SPIKE-C1: Metal and OpenGL cfg-selected paths must each compile a minimal example from the pin with read-back; partial build is not proof |
| C2 rustquest and hello_quest | https://github.com/makepad/rustquest, https://github.com/makepad/hello_quest | No committed license for the cited toolchain and dated platform assumptions. | no committed LICENSE | none | REJECTED | architecture owner | Inspiration-only, no code or build scripts |
| C3 compiled declarative UI DSL and shader AST | https://github.com/makepad/glui, https://github.com/makepad/ai_snake | Compiled declarative UI DSL and shader AST, proof-pending. | MIT (committed LICENSE) | none | PROOF-PENDING | build owner | SPIKE-C3: minimal live_design! + shader-AST paths compile reproducibly with read-back; no generated UI artifact in this repo |
| C4 image_viewer / Moly Kit | https://github.com/makepad/image_viewer | No committed license and an unpinned branch dependency. | no committed LICENSE | none | REJECTED | architecture owner | Inspiration-only, no code, dependency, image asset, or model integration |
| C5 .mpai transcript provenance | https://github.com/makepad/ai_snake | [VERIFIED - public conceptual source] Metadata shape only; example surface ai/snake_demo.mpai. | MIT (committed LICENSE) | run-evidence, README, CHANGELOG | ADOPT | QA owner | Repo URL + license URL present; no transcript/prompt/model-session content copied |
| C6 numbered lesson layout | https://github.com/makepad/image_viewer | Numbered lesson layout, all-rights-reserved source. | no committed LICENSE | none | DEFERRED | copy owner | Reopen only with a new, independently authored lesson structure or explicit rights; current source is inspiration-only with no excerpt |
| C7 glmeshdraw | https://github.com/makepad/glmeshdraw | Trivial one-file sketch with floating dependencies; no Team6 capability gap. | MIT (committed LICENSE) | none | REJECTED | build owner | No current surface |
| C8 empty placeholders | https://github.com/makepad/ai_demo1, https://github.com/makepad/ai_mr, https://github.com/makepad/ai_ui, https://github.com/makepad/ai_xr | Four empty repositories with no substantive capability surface. | unverifiable | none | REJECTED | QA owner | License labels do not turn an empty placeholder into evidence; no current surface |

## Adopted-Reference Summaries

The following seven references are adopted as conceptual principles. All carry the tag `[VERIFIED - public conceptual source]`. See the Adopted references table below for repository and license URLs.

- A1 Core UI runtime (makepad/makepad, MIT): Declarative design description separate from assembly and renderer. No Makepad API, code, or copied wording is adopted.
- A2 microserde (makepad/microserde, MIT): Serialization overhead as a build/runtime design question. No dependency, benchmark, or replacement claim is added.
- A3 DeepSeek integration (makepad/llama_antirez_deepseek, MIT): Model-wire reference. No compatibility or supported-model claim is made.
- A4 NVFP4 quantization (makepad/llama_nvfp4, MIT): Hardware-specific reference. No hardware support or performance claim is made.
- B2 historical live-coding IDE (makepad/makepad_history, MIT): Historical architecture note. No IDE, VR, or runtime feature is adopted.
- B3 WASM GitHub Pages examples (makepad/makepad.github.io, Apache-2.0): Static publishing reference. No site code or asset is copied.
- C5 .mpai transcript provenance (makepad/ai_snake, MIT): Metadata shape reference. No transcript, prompt, or model-session content is copied.

Team6-kit documents selected Makepad repositories as conceptual reference principles only. It does not support Makepad, Rust, WASM, GPU rendering, DeepSeek, NVFP4, or any Makepad file format.

## Adopted references

The seven adopted references repeat their exact source links and license boundaries.

| Candidate | Source repository | License file | License boundary |
|---|---|---|---|
| A1 | https://github.com/makepad/makepad | https://github.com/makepad/makepad/blob/main/LICENSE | MIT conceptual-source-only. Principle only; no API, code, or copied wording. |
| A2 | https://github.com/makepad/microserde | https://github.com/makepad/microserde/blob/master/LICENSE | MIT conceptual-source-only. No dependency, benchmark, or replacement claim. |
| A3 | https://github.com/makepad/llama_antirez_deepseek | https://github.com/makepad/llama_antirez_deepseek/blob/main/LICENSE | MIT conceptual-source-only. No compatibility or supported-model claim. |
| A4 | https://github.com/makepad/llama_nvfp4 | https://github.com/makepad/llama_nvfp4/blob/master/LICENSE | MIT conceptual-source-only. No hardware support or performance claim. |
| B2 | https://github.com/makepad/makepad_history | https://github.com/makepad/makepad_history/blob/master/LICENSE | MIT conceptual-source-only. Historical context only. |
| B3 | https://github.com/makepad/makepad.github.io | https://github.com/makepad/makepad.github.io/blob/master/LICENSE | Apache-2.0 conceptual-source-only. No site code or asset copied. |
| C5 | https://github.com/makepad/ai_snake | https://github.com/makepad/ai_snake/blob/main/LICENSE | MIT conceptual-source-only. Metadata shape only; no transcript content copied. |

Each license file is linked from the source repository's `LICENSE` path at the committed revision. The all-rights-reserved rule applies to every source in the brief without a committed license, including deferred or rejected sources: they may be named as inspiration-only with no excerpt, and must not supply code, prose, prompts, assets, or dependencies.

## Target-surface verification

The three brief target paths were checked against the shipped repository and are absent:

- `templates/skills/mlops/inference/` — absent. A3 and A4 reroute to the existing `templates/skills/mlops/evaluation/evaluating-llms-harness/SKILL.md`. No `inference` directory is created.
- `templates/skills/software-development/plan/` — absent. B1 is proof-pending (SPIKE-B1) and has no current-repo change. No `plan` directory is created.
- `templates/skills/creative/design-md/` — absent. C3 is proof-pending (SPIKE-C3) and has no current-repo change. No `design-md` directory is created.

No absent surface is created by this PR, and no existing template is renamed.

## Propagation record

One row per adopted candidate with its canonical home, affected files, evidence class, owner role, and next gate. The website is external and not part of this repository change.

| Candidate | Canonical home | Affected files | Evidence class | Owner role | Next gate |
|---|---|---|---|---|---|
| A1 | html-report-authoring SKILL | templates/skills/creative/html-report-authoring/SKILL.md, WHY.md, README.md, CHANGELOG.md | [VERIFIED - public conceptual source] | architecture owner | repo gates + independent QA review |
| A2 | project-foundation-scaffold SKILL | templates/skills/software-development/project-foundation-scaffold/SKILL.md, README.md, CHANGELOG.md | [VERIFIED - public conceptual source] | build owner | repo gates + independent QA review |
| A3 | evaluating-llms-harness SKILL | templates/skills/mlops/evaluation/evaluating-llms-harness/SKILL.md, README.md, CHANGELOG.md | [VERIFIED - public conceptual source] | build owner | repo gates + independent QA review |
| A4 | evaluating-llms-harness SKILL | templates/skills/mlops/evaluation/evaluating-llms-harness/SKILL.md, README.md, CHANGELOG.md | [VERIFIED - public conceptual source] | build owner | repo gates + independent QA review |
| B2 | WHY.md | WHY.md, README.md, CHANGELOG.md | [VERIFIED - public conceptual source] | architecture owner | repo gates + independent QA review |
| B3 | github-pages-deployment SKILL | templates/skills/deployment/github-pages-deployment/SKILL.md, README.md, CHANGELOG.md | [VERIFIED - public conceptual source] | build owner | repo gates + independent QA review |
| C5 | run-evidence.md | choreography/run-evidence.md, README.md, CHANGELOG.md | [VERIFIED - public conceptual source] | QA owner | repo gates + independent QA review |

Site: external. The canonical public site (`team6.askaconsult.com`) is served by an external ASKA-managed Vercel project and is not part of this repository change. No website parity is claimed from repository files.

## Read-back fields

| Field | Value |
|---|---|
| Command | `git diff --check`; `python3 build/surface-scan.py`; `python3 build/verify-all.py` |
| Date | 2026-09-15 |
| Verifier role | QA owner (independent) |
| Not verified | website parity (external site, no live deployment claim); Makepad build, Team6 compatibility, benchmark, or hardware result (none claimed) |

This file does not claim website parity or a live deployment.
