<!-- GENERICIZED: 4×{CLIENT}, 10×{RELATIONSHIP} | source: skills/software-development/agent-kit-distribution/references/{CLIENT} -->
# Worked case: {CLIENT} T-001 Team6 kit — fork decision ({CLIENT}/29)

## The correction chain

1. User: "let's just make a PR on hermes-agent on github and incorporate our system into it as a branch."
2. {RELATIONSHIP}: PR+branch = a *proposal*, not incorporation. Hermes CONTRIBUTING.md priorities (verified): bug fixes → cross-platform → security → performance → "new skills — broadly useful ones". Niche/specialized content is explicitly routed away from the repo to a Skills Hub / agentskills.io registry. And merging our Apache-2.0 core + proprietary packs into their MIT tree makes the tuned team MIT by absorption — kills the paid tier. Recommended: upstream the tooling, keep the kit standalone + registry.
3. {RELATIONSHIP}/{RELATIONSHIP} agree; split into Track A (upstream PR, MIT-relensed tooling) + Track B (standalone kit to registry).
4. User: "I meant a fork." — **the correction that changes the math.** A fork keeps control: upstream MIT stays MIT, our additions are new files in our own dirs under our own license. No absorption.
5. Fork adopted as distribution model rev 2. Added layers: per-directory licensing + NOTICE, upstream-sync lane, upstream PRs from the fork, kits/ = generated output with license-enforcing build gate.
6. {RELATIONSHIP} escalated: the fork-creation precondition is parameterize-BEFORE-FIRST-COMMIT — hardcoded identifiers in `extraction-inventory.py` (L134-139: `{RELATIONSHIP}`, `{RELATIONSHIP}`, `{RELATIONSHIP}`, `{RELATIONSHIP}`, `{CLIENT}` "client name ({CLIENT})") and `build-manifest.py` (L75) would be in permanent public git history at commit one. {RELATIONSHIP}: drive the parameterization off the SAME derived identity inventory used for genericization, not a fresh hardcoded list.
7. {RELATIONSHIP} locked the sequence: parameterize → gate (first commit clean) → first commit → then public → then MIT-relense surface → kits boundary → naming/landing.

## License-zone table as shipped in fork-architecture.md

| Zone | Contents | License |
|---|---|---|
| Upstream | Hermes engine files, exactly as forked, unmodified | MIT (theirs) |
| Kits | generated output of build/generate.py — personas, choreography, genericized skills, gates, generator | Apache-2.0 (ours) |
| Packs | vertical-pack parameter files + service playbooks | proprietary by contract and by absence (never in the public fork) |

## NOTICE draft (root, mandatory)

```
This repository is a fork of NousResearch/hermes-agent (MIT).
Upstream files retain their MIT license and copyright.
All files under kits/ are original work of <ORG>, licensed Apache-2.0.
Vertical packs are proprietary and are NOT distributed in this repository.
See LICENSE and licenses/ for full texts.
```

## Verified facts that grounded the decision

- Hermes platform: MIT (github.com/NousResearch/hermes-agent, LICENSE). MIT permits any downstream license.
- AWS sample-claude-code-agent-team: MIT-0 (zero conditions). Google agent-starter-pack: Apache-2.0. No GPL in the dependency chain.
- GPT Store postmortem: "catalog of prompts wearing app costumes" — buyers pay for outcomes/delivery, not configs. Hence paid tier = service.
- agentskills.io is natively supported by Hermes (skills registry) — the discovery surface.

## Setup-agent idea (recorded for a future upstream PR)

Three intake modes into the SAME generator (a setup profile is a parameter file):
- beginner — interview-style Q&A; answers become the parameter file
- advanced — user writes a free setup prompt; the prompt IS the parameter file
- raw — no initial config; native ongoing-learning (memory nudges + skill creation)

Update-safety: engine updates touch upstream files only; profiles/kits/workspace are orthogonal zones `hermes update` never rewrites (verified earlier: updates clobbered asar patches, never profiles).

## On-disk artifacts

- `OUTPUTS/fork-architecture.md` (locked, 8KB) — the full architecture doc
- `PROJECTS/T001-team6-kit.md` — distribution model rev 2 recorded
