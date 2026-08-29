# Why airefea-kit Exists

> **Short version:** Hermes is the engine. airefea-kit is the operating layer —
> the *crew* and the *playbook* that turn a single agent into a disciplined
> multi-agent team. Different axis, not a feature add-on.

---

## The two-layer mental model

Hermes is what you install. You get profiles, skills, memory, cron, plugins
(kanban, accent, etc.), and `hermes setup` for plumbing. It's an *engine* —
the chassis, the dashboard, the wiring. It is excellent at what it does.

airefea-kit is what you instantiate *on top of* the engine. You get
persona archetypes, orchestration choreography, governance funnels, and a
generator that turns a parameter file into a configured team. It's an
*operating layer* — the crew, the playbook, the runbook.

A plugin (kanban, accent) is a *tool*. The kit is the *crew* that uses the
tools. They are not competitors any more than a steering wheel competes with
a driver. If you want a single agent with a task dashboard, you want
Hermes + kanban. If you want multiple agents working a real workflow with
governance, you want Hermes + airefea-kit.

| | Hermes | airefea-kit |
|---|---|---|
| **What it is** | The engine | The operating layer |
| **What you install** | A binary + profiles | A parameter file + the kit |
| **What you get** | Profiles, skills, plugins, memory, `hermes setup` | Persona archetypes, choreography, governance, generator, identity-onboarding |
| **Unit of work** | One agent in one room | Multiple agents in a workflow, with contracts between them |
| **Question it answers** | "How do I run an agent?" | "How should a team of agents actually work together?" |

---

## What the kit actually provides

Four deliverables, each one a thing Hermes does not ship:

### 1. Designed multi-agent behavior

Six persona archetypes with a tested orchestration contract. Hermes gives
you rooms and profiles; it gives you zero guidance on *choreography* — who
speaks first, who handoffs to whom, what the handoff artifact is, how to
read back completion. We built this from real failures: sequential handoffs
stall, role design alone doesn't change behavior, channel occupancy kills
teams, no one owns drift. That knowledge is packaged in the kit, not
implied by the engine.

### 2. Governance as code

The viability funnel (raw-capture → 13-criterion pass → disposition),
spin-off SoP, structured verdict blocks, read-back receipts, two-tier
intake (raw capture never blocks; promotion runs the pass). Hermes has no
equivalent. Building this from scratch is the work; the kit makes it a
file you commit.

### 3. Instantiation

`generate.py --params` turns a parameter file into a configured team
(identity, skills, choreography, gates). Hermes requires hand-assembling
every profile, every skill, every room. The kit's generator is the only
assembly path — a kit that cannot be built by the generator does not exist.

### 4. Identity-onboarding (the upstream contribution)

The setup agent — a built-in interview/advanced/raw initial config that
captures *who you are, what you do, what you'll use it for* and emits a
parameter file. Hermes ships `hermes setup` for plumbing (keys, providers,
platform). It does not ship identity config — the SOUL.md + profile.yaml
layer that makes a profile actually yours. The setup agent is the flagship
upstream PR, MIT-relensed back to Hermes so every Hermes user benefits.
This is the single biggest gap the kit closes, and it closes it for the
*engine* itself, not just the kit.

---

## What the kit does NOT provide (honesty section)

- **No core-engine features.** The kit does not make a single agent
  smarter, faster, or more capable in isolation.
- **No plugin competitor.** Kanban, accent, and other plugins are *inside*
  the engine and stay there. We don't fork or replace them.
- **No magic.** A skeptic can hand-build the SOUL.md files themselves.
  The value is *not having to design this from scratch*, and getting it
  instantiated in one command.
- **No proof, yet.** Nothing is demonstrated at the time of this writing
  — no vertical packs shipped, no setup-agent install live, no stranger
  has instantiated a team from the repo. The repo currently *asserts*
  value. The first vertical pack + a working setup-agent install are
  what make these claims true, not the claims themselves.

If you read this and think "I can hand-build the orchestration in a
weekend" — you probably can. The kit's value is that you don't have to,
and that the version you get has survived the design failures we'd hit
again. That's the difference between code and a product.

---

## The service tier — why the paid layer isn't files

Because anyone can copy files, and a copy is the same as the original.
Nobody can copy the *process* of having built and run the orchestration
that survives — the tuning, the vertical-specific configuration, the
setup. So the paid tier is service: a tuned instance generated against
your parameter file, plus the setup time to make it work in your context.
The files you could copy; the *instance* you pay for. This is the same
structure the T-001 viability pass locked, and the same structure
Hermes uses: open-source engine, paid service on top.

---

## Status as of this writing

- ✅ Open core public (Apache-2.0) on GitHub
- ✅ Licensing coherent (MIT provenance + Apache-2.0 kits + proprietary-by-contract packs)
- ✅ 8-surface hygiene gate (including S8 network-egress, enforcing no-telemetry by construction)
- ✅ Setup-agent spec signed
- 🔲 Setup agent authored and passing the 8-surface gate
- 🔲 Upstream PR for the setup agent
- 🔲 First vertical pack shipped (instance + service)
- 🔲 First working demonstration end-to-end

The list is honest about what's shipped and what's promised. The proof
gates — the setup-agent install, the first pack, the first end-to-end
demonstration — are the deliverables that turn this from a repo into a
product. Until they land, treat the above as the *plan*, not the result.

---

*Authored for the airefea-kit org. Reviewed by the build team. Open to
refinement as the proof points land.*
