<!-- GENERICIZED: 14×{CLIENT}, 12×{RELATIONSHIP} | source: skills/hermes/hermes-profile-distribution/SKILL.md -->
---
name: hermes-profile-distribution
description: "Author Hermes profile distributions for multi-agent teams."
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, profile, distribution, multi-agent, packaging, team-setup]
    related_skills: [hermes-agent]
---

# Hermes Profile Distribution

Author profile distributions for Hermes Agent — package one or more agents as a git repo that recipients install with `hermes profile install`.

## When to Use

- Packaging a multi-agent team for others to recreate
- Sharing a tuned agent across machines
- Publishing an agent as a product or community release
- Deploying the same agent to multiple machines

## Critical Constraint: Memory Strips on Install

**`hermes profile install` hard-excludes `memories/MEMORY.md` with no override.** This is the single most important fact about distribution authoring.

If an agent's identity, team registry, or operating rules live only in `memories/MEMORY.md`, a recipient who installs the profile gets an agent with the correct name and model but **zero knowledge of who they are or how the team works**.

**The fix:** All identity, team structure, and operating rules must be authored in `SOUL.md` (or other distribution-owned files). Memory is user data; identity must be authored.

Distribution-owned files (shipped to recipients):
- `SOUL.md` — personality, identity, team registry, operating rules
- `config.yaml` — model, provider, tool defaults
- `distribution.yaml` — manifest
- `skills/` — bundled skills
- `cron/` — scheduled tasks
- `mcp.json` — MCP server connections
- `README.md` — human-facing docs

Hard-excluded paths (NEVER shipped):
- `memories/`, `sessions/`, `state.db*`, `logs/`, `auth.json`, `.env`, `workspace/`, `plans/`, `home/`, `*_cache/`, `local/`

> **Precision (verified {CLIENT}):** the installer strips `memories/MEMORY.md` — one file, not the whole memory store. Memory still survives as injected context on the source machine. The clean-room line for what can ship is therefore an **authored-file sweep**, not the tool exclusion alone: sweep every file you intend to ship (SOUL.md, config.yaml, skills/, SOPs, README) for mentions of live business intelligence (ventures, contracts, user habits, absolute paths, credentials). Never claim "the tool prevents leaks" — claim "we swept the authored files."

## File Structure

```
my-agent-team/
├── distribution.yaml          # manifest: name, version, license, env requirements
├── .gitignore                 # excludes secrets & user data (use template)
├── README.md                  # setup guide for recipients
├── install.sh                 # one-command installer (use template)
├── {RELATIONSHIP}/
│   ├── SOUL.md                # identity + team registry + operating rules
│   └── config.yaml            # (optional) model/provider config
├── {RELATIONSHIP}/
│   ├── SOUL.md
│   └── config.yaml
└── ...                        # one directory per agent
```

## Workflow

### 1. Start from a working profile
Build and refine each agent as a normal profile first. Dogfood until it works.

### 2. Author SOUL.md with team knowledge
Each agent's SOUL.md must carry:
- Its own identity and role
- The full team registry (who does what, who reports to whom)
- Operating rules (one room per project, reporting chain, skill curation bar)
- Coordination map (task type → route to)

### 3. Create distribution.yaml
Use `templates/distribution.yaml`. Required field: `name`. Recommended: `version`, `description`, `license`, `env_requires`.

### 4. Create .gitignore BEFORE first commit
Use `templates/gitignore`. This excludes secrets, user data, and runtime artifacts. Create it before `git init`.

### 5. Create install.sh
Use `templates/install.sh`. The script loops `hermes profile install ./<dir> --alias` over each profile subdirectory.

### 6. Write README.md
Cover: what's inside, how to install (script + manual), post-install setup, how to update, how to uninstall.

### 7. Push and tag
```bash
git init && git add . && git commit -m "v1.0.0"
git tag v1.0.0 && git push -u origin main --tags
```

## Pitfalls

- **Forgetting the memory strip.** The #1 mistake. If you put team knowledge in memory, it won't survive install. Always put it in SOUL.md.
- **Creating .gitignore after git init.** If you've already used the profile, secrets and user data exist in the directory. Create .gitignore first.
- **One distribution.yaml per profile.** Each profile subdirectory needs its own manifest if installing separately, OR use a single repo with an install script that loops over subdirectories.
- **Forgetting .env.EXAMPLE.** Recipients need to know which API keys to configure. List them in `env_requires` in the manifest.
- **Profile-local skills.** Skills live per-profile (`~/.hermes/profiles/<name>/skills/`); a skill present in one profile may be absent in another. Before flagging a referenced skill as nonexistent, scan ALL profiles (`find ~/.hermes/profiles/* -iname '*<name>*'`) — a single-profile scan misses profile-local skills and produces a false claim. In team-wide SOPs, name the concrete tool call (`project_create(name, path)`) instead of a profile-local skill name: the tool call is the contract and works from any profile; a skill reference breaks the chain for every profile that lacks it.
- **Quoting an audit count without naming its unit.** Per-profile entries, unique paths, and class-filtered sets are all real and all different (live: 409 entries → 330 unique paths → 232 shippable-class). And never report a count derived from a truncated report listing — a top-N-per-section display produces phantom totals (a truncated listing once yielded "113 hit files" that was never a real figure). Derive every aggregate from the full dataset, and state the unit next to the number.
- **False-clean audits: prove the scan ran before reporting "0 hits".** A git-scoped audit once returned "0 hits" because the file enumerator was broken (kept a `add ` prefix in the parsed path → `os.path.isfile()` failed on every entry → zero files scanned). Always print `files scanned: N` and sanity-check N against the real tree before trusting a clean result; if a count looks too clean, verify the enumerator parsed real paths, not just that the grep ran.
- **"0 hits" claims fail independent audit when the check differs from the gate.** A case-sensitive grep reported "0 identifiers" while the gate's own inventory is case-insensitive — capitalized forms (`{RELATIONSHIP}`, `{RELATIONSHIP}`) and comment/docstring mentions leaked. When you claim a sweep is clean, use the gate's ACTUAL inventory (case-insensitive, full term list including word-splits) and state the exact command; never a narrower hand-typed list.

## Compilation: a kit is a generator, not a snapshot

When turning a live team into a distribution repo, the repo holds TEMPLATES, not scraped profiles. Live profiles are coupled to one machine (workspace paths, venture names, cron jobs, model config); copying them produces a bespoke artifact that rots on day one. Live profiles are ONE instance of the kit, never the source.

- `templates/` — persona archetypes + `config.yaml` with placeholders (`{WORKSPACE}`, `{TEAM_NAME}`, `{API_KEY_ENV}`)
- `choreography/` — the interaction contract as a first-class artifact: routing, contribution order, handoffs, funnel SOPs, read-back receipts. Six SOUL.md files are six persona cards; the SYSTEM is how they behave together. Document that, or buyers get personas and no team.
- `build/` — an instantiation script that substitutes variables into the templates
- Archetypes are DISTILLED from real identities (Director, Architect, Researcher), never copies of them
- License split: Apache-2.0 on the open core (patterns + choreography), proprietary on tuned vertical packs. Once the choreography ships it is copyable, so the paid tier is service (setup, tuning, vertical configuration), not files.

Session detail (the clean-room audit taxonomy, profile-local-skill lookup commands, and the memory-strip precision that drove this): `references/clean-room-extraction.md`.

Run the mechanical audit with `scripts/extraction-inventory.py` (validated {CLIENT} on an 8-profile fleet): classifies every artifact as SHIPPABLE / REDACTABLE / EXCLUDED and content-sweeps for live identifiers (ventures, handles, workspace paths). Identifiers come from a per-instance `identifiers.yaml` (never hardcoded — see Identifier parameterization below); the sweep enumerates the redaction surface instead of eyeballing it.

Then turn the audit into an export manifest with `scripts/build-manifest.py` — unique-path keyed, DROP / TEMPLATE / KEEP-REVIEW / KEEP verdicts. Its output IS the `templates/` content manifest (the TEMPLATE rows) and the `build/` filter list (the DROP rows). Gate every kit build: mechanical fail on any REDACTABLE-class hit, plus a semantic REVIEW.md checklist on SHIPPABLE-class sweep-hits (soft leaks regexes can't see — relationship/financial/client-contract/habits). The gate re-scans at build time; never trust a saved snapshot. Full methodology and the counting-unit pitfalls: `references/audit-counting-and-release-gates.md`.

## Genericization: leak-removal BY DESIGN, not review-then-hope

TEMPLATE rows become `templates/` content via a rule-driven genericizer (`scripts/genericize.py`) that strips instance content as MANDATORY placeholder substitutions — the transformation enforces the boundary, and the semantic review then verifies the transformation FIRED (diff review) instead of re-reading every file. This collapses the review surface from "229 full-file reads" to "126 diff reads + 103 short reads + 10% spot audit."

- **Four substitution classes** ({RELATIONSHIP}'s soft-leak classes → placeholders): relationship specifics → `{RELATIONSHIP}`, financial figures → `{AMOUNT}`, client/contract detail → `{CLIENT}`, personal habits → `{HABIT}`. Model configs get their own `{MODEL}` class.
- **Conservative default:** when a token could be instance or pattern, it IS instance. Strip it. Over-stripping is safe; under-stripping is a leak.
- **No partial placeholders.** A stripped token becomes a full placeholder, never a truncated fragment (paraphrase leaves fingerprints).
- **Context markers survive.** Keep the surrounding word so the template reads naturally when instantiated: `Phase N` → `Phase {CLIENT}` (word kept, number stripped), not `{CLIENT}`. But DON'T strip reusable context words themselves — stripping "{CLIENT}" produced `{CLIENT} — {CLIENT}` title mangling.
- **Zero-substitution files are suspicious** — either already generic (mark `already-generic`) or the rules missed something. Inspect, don't assume.

**Bootstrap hole — the #1 genericizer trap.** Substitution rules derived from sweep hits miss tokens by construction (the regex inventory only knew handles it had already seen; a teammate's display name survived both substitution AND the leak-check verification because neither knew it). Durable fix: **derive the identity inventory from sources of truth, not sweep hits** — profile directory names, `name:`/`agent.name:` lines in each profile's `config.yaml`, SOUL.md titles. Feed that derived inventory into BOTH the substitution rules AND the post-genericization leak-check list, or the fix validates itself. Add a profile → its identity enters the inventory without a leak incident to trigger it.

**Regex over-strip pitfalls (all bit live; each cost an iteration):**
- **Quoted handle lists collapse to one placeholder.** `["{PROFILES}",...]` ×8 → one `"{PROFILES}"` (list role preserved, loop code still works). The pattern must match ONLY actual handles so generic quoted lists (`{"model","provider",...}`) are untouched — and it must run BEFORE the single-handle rule.
- **Model-name regexes eat filesystem paths.** "Application Support/Google/Chrome/Default/Bookmarks" matched `google/Chrome` as a model string. Lookahead boundaries were either too tight (missed real models) or too loose (matched paths). The winner: an explicit **path-word blacklist** (`Application`, `Support`, `Chrome`, `Default`, `Library`, `Bookmarks`, `Safari`) in a negative lookahead.
- **First-name aliases.** A member's full name in `config.yaml` doesn't cover prose that uses a bare first name ("{RELATIONSHIP}" alone). Add the alias explicitly.
- **Verification false positives (internal QA only):** grepping for `{PLACEHOLDER}` in output catches the placeholder itself — not a leak. BUT do NOT treat instance-token FILENAMES and `GENERICIZED` header `source:` lines as benign in a public fork — they ARE shipped content and a real leak class (61 filenames + 54 header lines leaked live). Sanitize destination paths AND the header's source value (`sanitize_path`), and keep the generator's `target_path()` using the SAME sanitizer or templates resolve to missing files.

Full rule table, the {RELATIONSHIP}-identity leak incident, and the derived-inventory implementation: `references/genericization-and-derived-inventory.md`.

## Identifier parameterization — public-fork precondition

**A public fork's first commit is permanent git history.** `git reset`/rebase rewrites files, never history — any identifier committed at commit one is public forever. So identifier lists move OUT of scripts into an external per-instance config with EMPTY shipped defaults:

- `identifiers.yaml` — team_handles, venture_names, user_handles, client_names, path_markers, habit_phrases, codename_terms. The open kit ships it EMPTY; the operator (or the setup agent) supplies their own values at build time.
- Scripts load it (a minimal YAML-subset reader is fine) and degrade to "no identifiers" when missing — safe, never a leak.
- **The identifier config IS the service-tier deliverable** — per-instance inventory is exactly what buyers pay for, not a leak in the open core.
- Before the first public commit, grep every shipped script for team names, handles, ventures, paths — including COMMENTS and docstrings (a docstring naming a teammate is still a leak). Clean `author:` frontmatter rows too. Then check the scripts still compile.
- **Feed both directions (bootstrap-hole closure).** The derived identity inventory (profile dirs, `config.yaml` `name:`, SOUL.md titles) AND identifiers.yaml must feed BOTH the substitution rules AND the post-build leak-check list — a rule list and a check list that disagree let a leak pass verification by construction.

### Rule-table pitfalls (each bit live this session)

- **Longest-first alternation ordering.** Python regex alternation is first-match-wins: with `{RELATIONSHIP}` before `{RELATIONSHIP}`, the short token matches first and leaves a partial strip (`{RELATIONSHIP} Al-Jabr`) — violating no-partial-placeholders. Sort every alternation by token length descending, including derived display names.
- **Empty alternation matches everything.** `re.compile(r"(?i)(" + "|".join([]) + r")")` = `(?i)()`, which matches the empty string at every position → every file false-hits the sweep. Guard: when the inventory is empty, compile `(?i)(?!)` (never matches).
- **Protected terms for domain-vocabulary collisions.** A token can be BOTH an instance name and legitimate generic vocabulary ("{CLIENT}" = Quran commentary in a quranic-arabic-data skill AND the {CLIENT} project). Per-file `protected_terms` (term + file substrings) with sentinel-and-restore: swap protected tokens to sentinels before rules run, restore after — so no rule strips them in the files where they're domain vocab, while the same token still strips elsewhere. Ambiguous tokens go in protected_terms keyed to the files where they're vocabulary, not in venture/codename lists where they'd over-strip.
- **CamelCase code identifiers defeat word boundaries.** `hide{CLIENT}Stats()`, `instantBook{CLIENT}` — the `\b` venture rule can't match mid-identifier. A `codename_terms` list of UNIQUE invented words gets a substring rule (safe because the words are unique; generic English words like "{CLIENT}" stay whole-word only).
- **Durable deletes live in config, not manual edits.** Deleting a generated file is transient — the next genericizer run regenerates it from source (the `{CLIENT}-sources.md` files came back twice). Instance-bound files get a `drop_files:` entry in `identifiers.yaml` the genericizer skips at generation time.
- **Reachability is the body-leak test ({RELATIONSHIP}'s bar).** Ask *could a reader of the fork reach our instance from this?* — a live reachable integration (a real CDN+repo dependency) fails regardless of license; a generic public service (Unsplash, Vercel) is WARN. Instance-tied integrations live in `identifiers.yaml` `reachable_integrations:`, loaded into BOTH the genericizer rules and the scanner — never hardcoded in committed source (a scanner whose term table names the integration is itself a leak).

## Surface-matrix leak audit — "clean" means 0 across N surfaces with N detectors

The durable replacement for the catch-all grep that kept missing the next surface. Enumerate every surface an identifier can inhabit and run a DEDICATED detector per surface: content, filenames/dirs, GENERICIZED header `source:` lines, script paths, config defaults, gitignore, and reachability. Run it against the STAGED tree (`git add -A -n`), self-exclude the scanner, word-boundary all content terms, keep an explicit brand allowlist, and **enumerate the staged file list yourself before first commit** — the scanner reported `S2-filenames: clean` while 15 real project/client names sat in the tree because the identity inventory missed the project-name class ({CLIENT}, {CLIENT}, {CLIENT}, {CLIENT}, {CLIENT}, {CLIENT}...). Add project tokens to `codename_terms`; quarantine known-leak builds (`mv dist/open-core dist/open-core-QUARANTINED-<date>`); always re-run genericize + the full scan after any rule change (regeneration wipes manual scrubs). Full matrix, the project-name incident, and scanner pitfalls: `references/surface-matrix-leak-audit.md`.

## Update-safety — test-backed, not doc-backed

**`hermes update` is `git pull --ff-only origin $BRANCH` + `git reset --hard origin/$BRANCH`** (verified from the install's own update path). Any directory committed to the fork but absent from upstream is DESTROYED by `reset --hard`. Proven by dry-run on a scratch clone (`scripts/fork-update-safety-dryrun.sh`):

- Overlay dir COMMITTED to the fork branch: destroyed by reset.
- Overlay dir GITIGNORED + untracked: survives reset.

**Governance:** the product layer must NEVER be committed to the fork — it is generated output, rebuilt by the generator after every update. `.gitignore` the overlay; the sync lane re-runs `generate.py`, never hand-merges. `~/.hermes/profiles/` is outside the repo tree entirely — the other safe boundary. Run the dry-run before the first public commit. (The docs claiming update-safety is "structurally locked" were wrong; only the dry-run closes it.)

## Vertical-pack declared-schema (asymmetric, one-directional hard)

Paid tier: each pack's `kit.yaml` declares `placeholders: [...]`; the generator validates the RESOLVED placeholder set against the DECLARED set at instantiation:

- **`declared ∖ resolved` = FAIL** — the pack promised a placeholder and didn't deliver (the `{CLIEN}` typo case). Always fails, strict or not.
- **`resolved ∖ declared` = WARN** — extra tokens (`{BK}`, `{N}`) are legit code literals or template drift; review, don't fail.
- Unresolved tokens: WARN in open-core mode (generic by design), FAIL under `--strict` (a paid kit can't ship mangled).

The asymmetry is deliberate: a symmetric "sets must match exactly" reintroduces the `{BK}` false-fail the schema exists to kill.

Full session detail — the parameterization before/after, the update-mechanism evidence, the dry-run transcript, the filename/header leak-class correction, and the declared-schema implementation: `references/fork-update-safety.md` + `references/genericization-and-derived-inventory.md`.

## Templates

- `templates/distribution.yaml` — manifest template
- `templates/gitignore` — .gitignore template
- `templates/install.sh` — install script template
