<!-- GENERICIZED: 1×{AMOUNT}, 3×{CLIENT}, 2×{RELATIONSHIP} | source: skills/research/tool-adoption-audit/SKILL.md -->
---
name: tool-adoption-audit
description: "Use when auditing a third-party tool before adopting it."
version: 1.0.0
author: {RELATIONSHIP} ({RELATIONSHIP})
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [audit, security, telemetry, trust, third-party, adoption]
    related_skills: [read-only-system-audit, hermes-profile-fleet-operations, source-evaluation]
---

# Third-Party Tool Adoption Audit

> A user hands you a repo: "add to repertoire." The tool promises capability. The cost is trust — the code will run with some degree of system access, and every agent who uses it acts on what it returns. The audit is the difference between adopting a capability and adopting a claim.

## When to Use

- "Add to repertoire: <url>" / "this looks useful, check it out" — any new tool, plugin, package, or skill proposed for the fleet
- Before installing anything that will run with permissions (Accessibility, Screen Recording, filesystem, browser/CDP, network)
- Before making a young project a default backend for a high-traffic capability
- Verifying another agent's audit claims before the team relies on them

**Do not use for** auditing a system you consume but must not modify (`read-only-system-audit`), or debugging your own code. This audit's deliverable is a **verdict with conditions**, not a findings document.

## Core Rules

> **1. README claims are hypotheses; the code is the evidence.** Privacy sections, capability lists, and "never does X" statements are marketing until a line of code contradicts or confirms them. The most valuable findings in every audit were claims that were *technically true and operationally false*.

> **2. The real power often lives outside the advertised repo.** The daemon doing the work may be a separate PyPI dependency. The installer may be a third-party CLI. Audit the whole chain that executes, not just the repo you were handed.

## Procedure

### Step 1 — Clone and enumerate

```bash
rm -rf /tmp/<name>-audit && git clone --depth 1 <url> /tmp/<name>-audit
find /tmp/<name>-audit/src -name "*.py" | sort          # structure
wc -l $(find /tmp/<name>-audit -name "*.py" -o -name "*.mjs") | tail -3   # size → audit scope
cat <pkg>/package.json / pyproject.toml                  # deps: runtime vs dev
```

Line counts set the honest scope. A 2454-line core is fully readable; a 5000-line package means budget the pass. Zero runtime dependencies is itself a finding (less supply-chain surface).

### Step 2 — Read the implementation, not the README

Read every file that executes. Note per primitive what it actually does under the hood — the system API it calls, the process it spawns, the network it touches. The README's bullet list ("background capture, input to PID") is verified only when the code shows `CGEventPostToPid`.

### Step 3 — Enumerate every network endpoint

```bash
grep -rhoE "https?://[a-zA-Z0-9./_-]+" <src> | sort | uniq -c | sort -rn
```

Every URL is a data flow. Classify each: local loopback, schema namespaces, the vendor's API, telemetry. A "no network calls in the render path" claim dies here. If a domain is a config override (`KEENABLE_API_URL`, `BU_API`), note that an attacker-controlled env var can redirect credential-bearing traffic — check whether the code guards it (HTTPS enforcement, credential rejection, loopback-only for http).

### Step 4 — Audit telemetry against the payload it actually builds

The single highest-yield step. Find the telemetry module; read the payload construction field by field; compare against the README's privacy claims.

- Does the README say "never records prompts"? Check whether `cli_event`-style capture ships the task script verbatim (observed: browser-harness sends up to 20KB of task text with a {AMOUNT}-char cap, bypassing its own `_safe_properties` redaction because that filter is applied only to ad-hoc events).
- Does the disable path actually disable *every* send site? `is_enabled()` may gate only one caller.
- Which env vars does it honor? Observed: macos-harness honors `DO_NOT_TRACK`; browser-harness does not. `~/.zshrc` env vars are **decorative for non-interactive paths** (agent tool calls, cron) — the 0600 config file is the durable enforcement layer.
- Telemetry that ships "agent client" detection (env-marker sniffing) identifies the fleet to the vendor; harmless but note it.

Rule: telemetry findings are stated as **enforcement facts** (which layer holds), not just "it's off."

### Step 5 — Find the silent consent paths

Look for anything that grants access without a user action: background threads that click permission dialogs (observed: macos-harness's AX auto-approver presses Chrome's "Allow remote debugging?" button), recovery logic that launches apps or opens privileged pages automatically, "self-healing" that bypasses the gate. Check whether a documented kill-switch env var **actually exists** — observed: the documented `MACOS_HARNESS_AUTO_APPROVE`-style switch did not exist; the gate was procedural only. When no code-level gate exists, the convention is the gate: never call the connect path except from an explicit user-approved action.

### Step 6 — Check silent fallback behavior

A plugin/backend whose `is_available()` returns `True` unconditionally becomes the **silent last-resort fallback** whenever the configured default fails or config is lost — traffic quietly reroutes to a young service. Installation is therefore never fully inert. State this in the verdict even when the tool is installed "disabled."

### Step 7 — Check the feature/claim gap

Docs may tout capabilities the integration cannot reach. Observed: Keenable's docs advertise point-in-time search and date/site filters; the Hermes plugin's `search()` sends only `query`. Installing the plugin buys a redundant backend, not the unique value. The verdict must say what the tool actually delivers *through the integration path being adopted*.

### Step 8 — Audit the install path, and prefer copy over installer

The installer is code that runs with write access to agent skill dirs. `npx skills add owner/repo` executes a third-party CLI (however well-adopted) on first run. If the repo ships a self-contained directory (`archify/` with SKILL.md at root, zero runtime deps), **copy the directory manually** — install scope then equals audit scope, and no new executable surface is introduced. Same for pip/uv tools: prefer the same package manager the fleet already uses.

### Step 9 — License → downstream obligation (verify, don't trust the badge)

MIT/Apache-2.0 = safe to build on. GPL infects derivatives; CC BY-NC kills commercial use. State the obligation in the verdict, not just the license name. The GitHub API `license` field is a **hint, not a finding**: `NOASSERTION` usually means the detector failed on a misnamed file (`LICENCE.md`, `COPYING`, `license.md`), not that the project is unlicensed. Read the actual text from the raw file:

```bash
curl -s "https://api.github.com/repos/<owner>/<repo>" | grep license   # hint only
for f in LICENSE LICENCE.md LICENSE.md COPYING license COPYING.md; do
  curl -s "https://raw.githubusercontent.com/<owner>/<repo>/<branch>/$f" | head -5
done
```

- **Code license ≠ asset license.** Art/data often lives in a sibling repo or submodule with its own license (observed: OpMon GPL-3.0 code, OpMon-Data CC-BY-SA-4.0 art — the main repo's license file explicitly carves art out and points at it). Enumerate `contents/` for submodules and data repos; a path referenced from the parent's LICENSE can 404 — probe the real file at the data repo's root.
- **Per-asset mosaics are the norm in game/asset repos.** Tuxemon's CONTRIBUTING.md policy says art "must be free" while its ATTRIBUTIONS.md ledger actually contains CC-BY-SA-4.0, CC0, PD, CC-BY-3.0 AND CC-BY-NC-SA-3.0. The ledger is ground truth; policy prose is not. Read ATTRIBUTIONS.md / CREDITS.md per file, and treat every NC item as commercially dead.
- **Copyleft ASSETS can sit beside MIT code as a distinct asset layer**: own directory, own LICENSE file, attribution ledger. The engine stays MIT; only that layer is share-alike. Consequence: derivatives of those assets stay CC-BY-SA — fine for a free tier, fatal for paid packs (those need original art).
- **MIT code can still carry upstream IP.** Pokemon Showdown is MIT but its data is Game Freak IP; license cleanliness does not sanitize the IP inside the data. Reuse mechanics/formats, never proprietary data.
- **CONTRIBUTING.md is a license artifact** — it states the contribution-license policy and often per-file art rules; read it alongside the LICENSE.
- **Directory entry counts are not asset counts.** GitHub `contents/` listings include engine metadata sidecars (Godot `.import` files, thumbnails, `.json`). Filter by real extension and count actual files before reporting numbers: OpMon-Data's opmons dir showed 171 entries but only 85 PNGs. "Battle-ready {CLIENT} entries" reported as a count became a retraction.
- **Count distinct entities from the FULL name list, never a regex over a sample.** An ID regex like `\d+-\d+` silently misses prefixed variants (shiny `s10-0` / `ss12-0` sprites) — 45 counted, 51 actual. Derive the ID set by enumerating every name, then reconcile against the machine-generated manifest; the manifest is what makes a teammate's count verifiable against yours.
- **Negative claims require a recursive walk.** Top-level `Animations/` held only UI frames, but `Sprites/opmons/anims/` contained real per-monster animation (8 wink cycles, one 8-frame sequence). A shallow directory scan turns "no X assets exist" into a retracted claim. Walk subdirectories before declaring absence.
- **Report the verdict as a per-repo table** (code license / asset license / reuse verdict with the obligation spelled out). Full worked example: `references/oss-reuse-license-audit-{CLIENT}`.

### Step 10 — Persistence check

Launch agents, login items, cron entries, config dirs, auto-updaters, PID files. "No persistence" is verified by finding none, not by absence of a claim.

### Step 11 — Cross-verify other auditors' claims independently

When another agent has already audited, re-run the load-bearing checks yourself: grep the actual guard lines (DNS pinning, redirect caps, private-IP blocks), count the endpoints, confirm telemetry grep hits are false positives. A teammate's "clean" is a self-report; the md5 of your own grep is evidence.

### Step 12 — Deliver the verdict

Shape: **verdict** (clean / clean with conditions / not clean) → **what I verified** (each with the code line or command) → **conditions** (numbered, each with who holds the gate) → **residual risk** (named component and why). Confidence level explicit. Distinguish what you found, what you inferred, what you could not verify (e.g. "the browser-bridge package is the unaudited link").

## Adoption Convention (fleet)

- Install **inert in one profile** as a testbed — no propagation until it proves itself under real use.
- **Pin the version/commit**; upgrades are reviewed changes: audit → diff against pinned commit → update canonical skill → redistribute with fresh checksums → independent verification.
- A young project (days/weeks old, single maintainer, few stars) is not automatically rejected — it sets the trust profile: pin harder, gate more procedurally, keep the audit current.
- Record gates in the skill that ships with the tool (the macos-harness skill carries: no connect without user go, no cloud sync, telemetry enforcement layer).

## Pitfalls

**Trusting the README's privacy section.** Every privacy claim in every audited package was *mostly* true; the dangerous ones were true in the code path that wasn't exercised. Read the payload, not the promise.

**Auditing only the advertised repo.** The CDP power was in a sibling PyPI package; the installer was a third-party CLI. Trace what actually executes end to end.

**Assuming a documented kill-switch exists.** Verify the env var is read in the code path it is supposed to gate. Absence of a switch means the gate is procedural — say so.

**Version skew between metadata and code.** PyPI metadata said 0.1.1; repo said 0.1.0. Note it; it is a release-hygiene signal.

**Treating "opt-out" as "off".** Telemetry default-enabled is the norm; what matters is the disable path and which layer enforces it (config file vs interactive-only env var).

**Grepping for telemetry keywords and stopping.** "analytics" matches example filenames; "segment" matches geometry code. Read the matches before reporting them as findings.

**Reporting directory entry counts as asset counts.** `.import` sidecars and thumbnails inflate listings; regex ID extraction misses prefixed variants (shiny `s10-0`); a shallow walk hides subdirectory assets. Filter by extension, enumerate every name, walk subdirectories — then reconcile against the machine manifest before the number reaches the team.

## Verification

- Every endpoint in the codebase is classified (loopback / vendor / telemetry / doc-only)
- Telemetry claims are matched against the actual payload construction, and the enforcement layer is named
- Consent paths, fallbacks, and installer scope are each stated in the verdict
- If another agent audited first, your read-back of their load-bearing claims is in the report

## Support Files

- `references/audit-case-studies-2026-08.md` — the macos-harness / browser-harness / keenable / archify audits: what was checked, what was found, verdicts, and the conditions that shipped
- `references/oss-reuse-license-audit-{CLIENT}` — the OpMon/Tuxemon reuse audit: verified license facts, the badge-vs-file methodology, the asset-layer separation pattern, and the verdict table that shipped to the team
