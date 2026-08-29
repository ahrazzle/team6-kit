<!-- GENERICIZED: 3×{CLIENT}, 1×{RELATIONSHIP} | source: skills/software-development/agent-kit-distribution/SKILL.md -->
---
name: agent-kit-distribution
description: Use when open-sourcing built systems — fork vs PR, licenses.
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
metadata:
  hermes:
    tags: [distribution, licensing, fork, open-source, pr-upstream, paid-tier, git]
    related_skills: [agent-kit-extraction, oss-reuse-license-audit, github-pr-workflow, github-repo-management]
---

# Agent Kit Distribution & Open-Source Licensing

## When to Use

Use when: deciding how to open-source / distribute a built system (an agent kit, a team config, a tool) — whether to PR into an upstream repo or fork it; keeping a proprietary/paid layer out of an MIT tree; per-directory licensing; NOTICE files; upstream-sync maintenance; publishing to a skills registry. Trigger signals: "make a PR on X", "fork it", "open source this", "incorporate our system into upstream", "license", "don't lose the paid tier".

Validated on the {CLIENT} T-001 Team6 kit decision (2026-08) — see `references/{CLIENT}` for the worked case.

## The core decision: merge vs fork

- **Merge/PR into an upstream repo = forfeiture of your license layer.** If upstream is MIT and you merge your Apache-2.0 core + proprietary packs into their tree, your additions become MIT by absorption — anyone can resell the tuned product for free. The paid tier's "uncopyable instance" evaporates. One-way door.
- **Fork = control retained.** Copy the upstream repo under your own org. Upstream files keep their license (MIT — unavoidable, they're in your tree), but YOUR additions are new files in your own directories under your own license. Nothing gets absorbed.
- Default answer: **PR the generic tooling upstream; fork for the product.**
- User shorthand matters: "PR" and "fork" are different intents with different license math. If the user says PR but means fork (or vice versa), confirm the mechanics before the license analysis.

## Check upstream's CONTRIBUTING.md before proposing anything

- Contribution priorities tell you what they'll accept: typically bug fixes → cross-platform → security → performance → broadly-useful new skills. Niche/specialized content is often explicitly routed AWAY from the repo (to a skills hub / registry). Read this before drafting a PR or you draft into a closed door.
- Some upstreams auto-close whole PR categories with a pointer to an external registry (e.g. `plugins/memory/`). Don't fight it — use the registry.

## Per-directory licensing (the load-bearing rule for forks)

One git repo, three license zones:

| Zone | Contents | License |
|---|---|---|
| Upstream | engine files, exactly as forked, unmodified | theirs (e.g. MIT) |
| Ours | generated product output (kits/, personas, choreography) | yours (e.g. Apache-2.0) |
| Paid | vertical packs / parameter files / service playbooks | proprietary by contract AND by absence — never committed to the public fork |

- **Root NOTICE file** stating the split at a glance: "fork of X (MIT); files under kits/ are original work of ORG, Apache-2.0; packs are proprietary and not distributed here."
- **Never edit an upstream file's license header.** Upstream files are immutable in the fork; change flows only via sync (upstream → fork) or upstream PRs (fork → upstream).
- Why it survives scrutiny: MIT permits re-licensing your OWN additions under any terms; you never relicense their files. Apache-2.0 is compatible downstream of MIT. No copyleft anywhere in the chain → clean.

## Generator-as-boundary

If you have a generator pipeline (see `agent-kit-extraction`), the fork's product layer must be GENERATED output, not hand-maintained. The generator is the boundary between "copyable upstream engine" and "your licensed product". Product output is stamped with a reproducibility hash; drift = build failure. A license-enforcing build gate fails on: any file outside licensed dirs, any modified upstream file, any identity-inventory identifier in committed source.

## Parameterize before first commit (fork-creation precondition)

- **A public fork puts whatever is in commit one into permanent public git history. Post-hoc fixes rewrite files, not history.**
- Hardcoded identifiers (user names, venture names, client names, handles) must be removed from scripts BEFORE the first commit — before the fork exists publicly, not before the PR.
- Drive the parameterization off the SAME derived identity inventory used for genericization (one inventory, two consumers: extraction + publication) — NOT a fresh hardcoded list, which recreates the bootstrap hole.
- The identifier config IS the per-instance deliverable — what buyers receive. It is the business model's backbone, not a leak in the open core.
- Sequence: parameterize → gate (first commit passes with clean identity inventory) → first commit → then public.

## Upstream-sync maintenance lane

A fork is a long-lived branch, not a one-time copy: `git fetch upstream && git merge upstream/main` on a schedule. Conflicts are rare by design — your additions live in orthogonal directories upstream never touches. If upstream restructures an overlaid dir, resolve by re-running the generator, never hand-editing generated output.

## Upstream PR track (the credibility play)

Send the generic, broadly-useful pieces upstream as PRs FROM the fork, relensed to upstream's license (MIT) — relensing your *tooling* is fine; the tooling was never the product. Never send: choreography, personas, the product layer.

Good PR candidates from practice: audit/inventory scripts, sweep/review gates, generic skills, and a **setup-agent** — an intake mode that turns a user's intent summary (who you are, what you do, intended use) into a parameter file, with beginner (interview-style Q&A) / advanced (free prompt) / raw (no initial config, ongoing learning) modes. Broadly useful to every platform user, engine-adjacent, zero product-layer exposure — an ideal first upstream contribution.

## Distribution model — three surfaces

- **Fork** = credibility surface (visible, "built on X" provenance)
- **Registry** = discovery surface (e.g. agentskills.io, natively supported — list the kit where users already are)
- **Packs** = revenue surface (proprietary parameter files + service — the tuned instance, which files alone can't replicate)
- The paid tier is service, not files: a public fork makes the files copyable — that was always true — so packs are parameter files + setup, not secrets.

## References

- `references/{CLIENT}` — worked case: T-001 Team6 kit, the PR → merge → fork correction chain, license-zone table, NOTICE draft, sequence as routed.
