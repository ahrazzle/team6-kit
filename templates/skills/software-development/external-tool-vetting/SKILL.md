<!-- GENERICIZED: 6×{CLIENT}, 5×{RELATIONSHIP} | source: skills/software-development/external-tool-vetting/SKILL.md -->
---
name: external-tool-vetting
description: Use when vetting an external tool or service for adoption.
---

# External Tool Vetting

Team6 protocol for adopting third-party tools the user hands over. Routing per {RELATIONSHIP}: the adopter claims + recons → the researcher audits (full implementation, not README) → {RELATIONSHIP} decides install scope. This class of work recurs every time the user finds something "useful to add to toolset" — follow the phases in order.

## When to Use

- The user posts a link/repo with "add to toolset", "add to repertoire", or "looks useful".
- {RELATIONSHIP} routes a tool-adoption task (claim → recon → audit → install decision).
- Any evaluation of whether to install, propagate, or revert a third-party integration across the team's profiles.

## Phase {CLIENT} — Claim

- Post a one-line ack in the room immediately ("claimed — reading it"), per the ack-first convention.
- Read the linked docs AND the repo. Never README-only — READMEs are marketing; the code is truth.

## Phase {CLIENT} — Recon (adopter's job)

Produce a structured, machine-verified summary:

1. **Trust profile** (commands, not vibes):
   - `git clone --depth 1` the repo; check `git log --reverse` first-commit date (age), commit count (activity), latest tag (pin target).
   - GitHub API for stars/forks/license/owner/created: `curl -s https://api.github.com/repos/<owner>/<repo>`.
   - Dependency surface: `package.json` / `pyproject.toml` / `requirements.txt` — zero deps is a strong signal (pure stdlib).
2. **Code surface scan** — grep the source (not docs) for:
   - Network calls: `fetch(`, `http`, `net.`, `dgram`, `tls.`
   - Telemetry: `telemetry`, `posthog`, `analytics`, `track(`
   - Process exec: `child_process`, `spawn`, `execSync`, `eval(`, `Function(`
   - Persistence: launch agents, login items, cron, autostart
   - Note for each hit whether it's opt-in (CLI flag, explicit user action) or default-on.
3. **Docs read**: README + the governing spec (for skills: the SKILL.md — its invariants ARE the product).
4. Report: what it is, what it does, trust profile table, network/telemetry/exec findings, fit for the team. Hand to the researcher for the full audit.

## Phase {CLIENT} — Audit (researcher's job)

- Full implementation read (every source file), plus field-level verification of any telemetry payload — README claims are not evidence.
- Check: telemetry defaults and disable paths; auto-approvers or silent side effects (e.g. an AX thread that clicks "Allow" on a permission dialog); unaudited transitive deps (the actual power may live in a PyPI/npm dep, not the repo); pin-ability.
- Verdict + conditions, same bar as the macos-harness audit.

## Phase {CLIENT} — Install: one profile first (command-level convention)

- New infrastructure lands in ONE profile, proves itself under real load, THEN propagates with {RELATIONSHIP}'s independent verification. Never live-deploy across all eight agents on first contact — the keenable incident is the case study.
- Pin the version; treat upgrades as reviewed changes, not routine pulls.
- Kill telemetry BEFORE first run: CLI `telemetry disable` on every package, plus durable env vars if honored. Verify the enforcement layer survives non-interactive/cron shells — config files (0600) are durable; `~/.zshrc` env vars only cover interactive shells and are decorative for agents.
- Back up `config.yaml` before any `config set` pass (comment-stripping is a known silent behavior).
- Secret keys go in the profile `.env`, never in the room or shell rc.

## Phase {CLIENT} — Verify with receipts

- Live smoke test that does NOT cross the sensitive gate (e.g. no `browser.connect()` without an explicit user go).
- Read-back receipt rule: every claim carries verbatim command output (checksum, grep count, `config get`) — a paraphrase fails the gate.
- Report per-profile end state as a table, verified on disk.

## Phase {CLIENT} — Revert or propagate

- **Revert** when the capability doesn't justify coupling (features unreachable through the integration = zero unique value): restore prior backend/config, keep the package installed but inert, record the explicit opt-in path.
- **Propagate** only after proof under real load, following the distribution protocol: audit → update canonical → redistribute with fresh checksums → {RELATIONSHIP} independently verifies.

## Upgrade protocol

Any version bump re-triggers the full loop: re-audit (diff against the pinned commit) → update canonical → redistribute with fresh checksums → independent verification. The failure mode is eight copies quietly disagreeing about which version is safe.

## Pitfalls

- **Partial terminal-session failure**: a pasted multi-command block (pip install + plugins enable + config set + export) can fail partway and succeed elsewhere. One failed `pip` does NOT stop the `config set` next to it — a config can point at an uninstalled backend. Verify each command's effect independently.
- **pip targets system Python by default** (macOS ships 3.9; many packages require ≥3.10 → "No matching distribution found"). Hermes packages install into `~/.hermes/hermes-agent/venv/bin/pip`; the agent imports from that venv.
- **Bare `hermes config set` writes the DEFAULT profile** (`~/.hermes/config.yaml`), not the agent profile. Always pass `-p <profile>` or verify which file changed.
- **Telemetry disable is per-package, not inherited**: one package may honor `DO_NOT_TRACK`, another won't (browser-harness ships full task scripts verbatim in cli_event; keenable plugin is keyless with rate limits on the public tier). Audit each package's payload and disable path individually.
- **Keys that transit chat/terminal history**: offer rotation when low-stakes; never auto-propagate an exposed key to more profiles.

## References

- `references/case-studies.md` — macos-harness, keenable, and archify condensed findings (trust profiles, telemetry specifics, verdicts) for baseline comparison on future vettings.
