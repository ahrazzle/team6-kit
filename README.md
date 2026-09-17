# Team6-kit

> **ARCHIVED — this repository is archived and no longer receives updates.**
> **The live home of this work is the aska-digital organization: https://github.com/aska-digital/**

## What team6-kit was

One AI agent engine (Hermes, from Nous Research) turned into a small team of AI agents working under clear rules — planner, builder, checker — with a supervisor, a quality checker, and a builder script.

That was the pitch, and this repository was the original, self-contained packaging of it: the agent profiles, the rules the team worked under, the builder that assembled a team from ready-made parts, and the choreography contracts that described how the agents handed work to one another. It is kept here as a historical record — the content did not stay in one tree, and each concern now lives in its own repository.

## Where the live system is

The maintained work lives under the aska-digital organization — https://github.com/aska-digital/ — one repository per concern:

- **[protean-kit](https://github.com/aska-digital/protean-kit)** — composer / install: pinned composer for the seven ingredients; installs with read-back. This is the live entry point for the whole kit system.
- **[protean-doctrine](https://github.com/aska-digital/protean-doctrine)** — doctrine: the operating doctrine the team works under — pipeline stages, role delegation, handoff protocol, QA gates.
- **[protean-ops](https://github.com/aska-digital/protean-ops)** — ops / rotation / in-flight records: rotation state, in-flight work, learnings, and decision reports, with their gates.
- **[protean-control-plane](https://github.com/aska-digital/protean-control-plane)** — control plane / dispatch: the trigger index that routes a request to the minimum skill bundle.
- **[protean-github-flow](https://github.com/aska-digital/protean-github-flow)** — GitHub workflow pack: procedures that carry a repository from inbound issue to a verified, reviewed pull request.
- **[protean-drafts](https://github.com/aska-digital/protean-drafts)** — draft-review pipeline: renders a draft as one reviewable page and runs its prose, identifier, and render-fidelity gates.
- **[protean-sym2p](https://github.com/aska-digital/protean-sym2p)** — SYM-2P protocol: the normative agent-messaging specification, with its validator and packet templates.
- **[protean-handoff](https://github.com/aska-digital/protean-handoff)** — phone orchestration / handoff: inspect, steer, and approve lane work from a phone.
- **[protean-team](https://github.com/aska-digital/protean-team)** — team org / roster view: ready-made agent profiles and the builder script.
- **[protean-lcm](https://github.com/ahrazzle/protean-lcm)** — archived sibling: the opt-in LCM DAG context engine plugin for Hermes Agent.

## Historical docs

Historical docs — kept as references for the content above, not as live sites: https://team6.askaconsult.com/ (documentation site) and https://www.askaconsult.com/team6 (corporate page).

## License

- **Engine:** Hermes by Nous Research, MIT license. This is not a fork; we build on top of it.
- **This kit (profiles, rules, builder):** Apache-2.0.
- **Vertical packs (paid settings files + service):** not in this repo; proprietary.
- Optional local models used by an adapter have their own separate license.

Full details: `LICENSING.md`.
