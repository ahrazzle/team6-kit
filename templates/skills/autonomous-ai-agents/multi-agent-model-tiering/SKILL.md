<!-- GENERICIZED: 1×{RELATIONSHIP} | source: skills/autonomous-ai-agents/multi-agent-model-tiering/SKILL.md -->
---
name: multi-agent-model-tiering
description: Use when setting model tiers or costs for an agent team.
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [agents, models, reasoning, cost, config, telemetry, group-chat]
    related_skills: [agent-persistence-layers, skill-library-curation, hermes-agent]
---

# Multi-Agent Model Tiering

Use when deciding **which model and reasoning level each agent in a team runs on**, what
that costs, and how to apply it so it actually takes effect. Covers per-profile model
config, the seven reasoning levels, the per-session binding rule that decides whether a
config write reaches a group chat at all, and how to measure real usage instead of
guessing at it.

## Trigger

- "Configure models for this project," "set up model tiers," "which model should each agent use"
- Choosing a budget tier, or asking whether a paid model is affordable
- An agent seems under- or over-powered for its role
- A model config was written and behavior did not change
- Estimating token or dollar cost for a team of agents
- A team is about to switch models because complexity outgrew the current one

## First Principle: Config Is Per-Profile, Bound Per-Session

Two facts together explain almost every surprise in this area.

1. **`~/.hermes/profiles/<name>/config.yaml` is the default a NEW session starts from.**
   There is one per profile — not one per project, not one per chat.
2. **Each session stores its own resolved `model` and `model_config`.** The `sessions`
   table carries both columns, and rows within a single profile routinely hold different
   values.

So a profile is not locked to one model. Sessions are individually pinned, and the config
file only decides what a *fresh* session inherits.

**The consequence that matters for teams:** a group chat is not one session. It is N
sessions, one per participating profile, and **each one binds the default at the moment
that agent first speaks.** An agent that joins a long-running room later starts on
whatever the default is *then*, not on what the room started with.

Therefore:

> **Write config to every profile FIRST. Then open the room.**

Configuring a room that already has live sessions changes nothing about it. And a
single-session override (a desktop composer pin) does **not** fan out to the other N-1
agents — it upgrades one and silently leaves the rest on the old default. For a team room,
the config file is the only mechanism that reaches everyone.

## The Three Scopes

| Scope | Mechanism | Persists? | Reaches a whole team? |
|---|---|---|---|
| This session only | Composer model picker; `/reasoning <level>`; `--reasoning <level>` CLI flag | No | **No** |
| New sessions onward | `config.yaml` (`model.default`, `agent.reasoning_effort`) | Yes | **Yes** |
| Fully isolated | A dedicated profile per project | Yes | Yes, but forks everything |

Prefer the middle row. Per-project profiles duplicate `SOUL.md`, memory, and the whole
skill library per project — that is the multi-profile drift problem multiplied, for a
benefit the ordering rule already delivers. See `agent-persistence-layers` on drift.

## Reasoning Levels: There Are Seven

```
minimal · low · medium · high · xhigh · max · ultra
```

Plus `none` / `false` / `off` / `disabled` to switch thinking off entirely. `max` is **not**
the ceiling — `ultra` is. Any three-tier "low/medium/high" table is missing four levels.

Resolution priority, in order:

1. A session-scoped override (set before resolution; always wins)
2. `agent.reasoning_overrides` — **per-model** pinning
3. `agent.reasoning_effort` — the global default

`reasoning_overrides` is the underused one. It expresses "high on the primary model,
medium on the cheap fallback" in a single block, so a model swap does not require
rewriting effort levels. Full syntax and source references:
`references/hermes-model-config-mechanics.md`.

## Assigning Levels By Role

Reasoning effort buys depth of deliberation, and it is paid in output tokens. Match it to
whether the work rewards deliberation, not to how important the agent feels.

- **High or above** — orchestration and routing, research and constraint-finding,
  architecture. Decisions that compound or are expensive to reverse.
- **Medium** — implementation against a clear spec, simplification, synthesis and
  summarisation for a human decision.
- **Low or minimal** — mechanical formatting, extraction, transformation with a known shape.

Two calibrations worth keeping:

- **Do not put a summarising role on `low`.** Condensing a whole project so a human can
  decide is synthesis, not formatting, and it is exactly where thin reasoning shows.
- **Check the heaviest consumer against its level.** The agent with the most input tokens
  on a high tier is where a level change moves the bill most.

**Verify the live values before writing a table about them.** Config drifts from whatever
anyone last claimed:

```bash
for p in <profiles>; do
  echo "-- $p"; grep -E "reasoning_effort|default:" ~/.hermes/profiles/$p/config.yaml
done
```

## Measuring Usage: The Command Under-Reads By N×

```bash
hermes insights --days 14          # ← resolves to ONE profile, not the install
hermes -p <name> insights          # explicit, per profile
hermes prompt-size                 # per-turn overhead, broken down
```

**`hermes insights` with no `-p` reads a single profile** — whichever the gateway resolves
to. Running it bare and calling the result a team total under-reads by roughly the number
of agents. Verify by running it both ways: bare output and `-p <that-profile>` output are
byte-identical.

Ledgers are **disjoint**, so summing is correct. Confirm rather than assume: the `sessions`
table has a `profile_name` column, and every row in a profile's database is stamped with
that profile's own name. No row appears twice.

Run `scripts/team-usage-sum.py` to sum every profile correctly in one pass. It also reports
whether any cost data exists at all.

**Watch the period, not the flag.** `--days 14` prints the window it actually covered
(`Period: … — …`). If the install is four days old, that is a four-day sample and a monthly
extrapolation is ~7.5×, not ~2×. Read the printed period before multiplying.

**A profile with cron jobs is the wrong measurement subject.** Its ledger mixes scheduled
runs with interactive work, so cost-per-turn from it is contaminated. Check the `source`
column split (`desktop` vs `cron`) and pick an all-interactive profile.

## Input Dominates, So Context Is The Real Lever

Measured across a six-agent team over four days: **input was ~90% of all tokens.** Most of
that is fixed overhead re-sent every single turn, per agent:

```
hermes prompt-size
  System prompt :  ~37 KB   (skills index, memory, user profile)
  Tool schemas  :  ~70 KB   (every enabled tool, every turn)
```

Tool schemas commonly **exceed the system prompt**. Disabling a toolset the team never uses
cuts input on every turn of every session — which beats any model swap for cost-per-quality
and costs nothing in capability. Do this before shopping for a cheaper model.

Two consequences:

- Optimising output-side settings (reasoning effort) moves ~10% of volume. Optimising
  input-side (toolsets, skills index, memory size) moves ~90%.
- **Switching model mid-chat resets the prompt cache** — the next message re-reads the
  whole conversation at full input price. On a long room, a fresh chat on the new model is
  cheaper than switching inside the old one.

## Honesty Rule: Free Models Produce No Cost Data

The `sessions` table has `estimated_cost_usd`, `actual_cost_usd`, and `cost_status`
columns. When every model in use is free, **they are empty**, and `hermes insights` reports
a near-zero cost with "N session(s) (no pricing data)".

Token counts are real. Dollar figures derived from them are published rates multiplied by
free-model usage — arithmetic, not measurement. Say so plainly when presenting a budget:
an unqualified dollar estimate reads as observed spend and gets trusted as one.

To convert a guess into a number: run **one agent, one paid model, one day**, then read
that profile's ledger. A single profile needs no summing, so it sidesteps the aggregation
question entirely. Pick an all-interactive profile, and prefer the heaviest consumer —
that is where a per-turn figure matters most.

## Beware The Unpriceable Model

A stealth or preview model publishes no rate card, no context window, and no benchmark. It
can be free *and* unmeasurable, and it can be withdrawn or repriced without notice. Two
things follow:

- Any cost model built on it is unfalsifiable. Do not present it as validated.
- **Declare a fallback.** The `fallback_model` block is commented out by default, so if the
  primary vanishes mid-session there is no failover. Setting a known-good free model as the
  declared fallback is a two-line change and the cheapest insurance available.

## Workflow

1. **Read the live config** for every profile. Never write a table from a prior claim.
2. **Measure**: `scripts/team-usage-sum.py` for volume, `hermes prompt-size` for per-turn
   overhead. Note the period the sample actually covers.
3. **Trim input first** — disable unused toolsets before considering a model change.
4. **Assess scope** and pick a tier: free default, escalate only on a named complexity
   signal (irreversible decisions, shared infrastructure, financial logic).
5. **Set levels per role**, using all seven, with `reasoning_overrides` if a fallback model
   is in play.
6. **Declare a fallback model** in each profile.
7. **Write every profile's `config.yaml`.**
8. **Verify on disk** across all N profiles — not the tool's success message.
9. **Then open the room.** Order matters; step 9 after step 7 is the whole point.
10. **Report honestly**: what is measured, what is extrapolated, and that it takes effect
    from the next session.

## Pitfalls

- **Configuring after the room is open.** Live sessions keep their bound model. The write
  must precede first contact by every agent.
- **Assuming a per-chat pin covers a team room.** It is one session out of N. The room looks
  configured and five agents are not.
- **Running `hermes insights` bare and calling it a team total.** It reads one profile.
- **Extrapolating from `--days 14` without reading the printed period.** A four-day sample
  extrapolated as if it were fourteen is off by ~3.5×.
- **Measuring cost on a profile with cron jobs.** Scheduled runs contaminate cost-per-turn.
- **Presenting rate-card arithmetic as observed spend.** With free models the cost columns
  are empty. Label estimates as estimates.
- **Assuming three reasoning levels.** There are seven; `ultra` is the ceiling.
- **Leaving `fallback_model` commented out while running a stealth model.** No failover.
- **Optimising reasoning effort to cut cost.** Output is ~10% of tokens. Input overhead is
  the lever.
- **Switching model mid-conversation to save money.** It resets the prompt cache and the
  next turn re-reads everything at full price.
- **Reaching for per-project profiles.** Duplicates identity, memory, and skills per
  project; the write-then-open ordering already solves the isolation problem.
- **Trusting a teammate's config table.** In this class of work, tables drift from disk
  fast. Read the files.

## References

- `references/hermes-model-config-mechanics.md` — verified specifics: the resolution
  chain with source file and line numbers, all seven levels, `reasoning_overrides` syntax,
  the `sessions` schema columns that prove per-session binding, and the exact commands
- `scripts/team-usage-sum.py` — sums token usage across every profile correctly, reports
  the desktop/cron split per profile, and states whether any real cost data exists

## Related Skills

- **agent-persistence-layers** — what *knowledge* each agent file carries, and the same
  frozen-at-session-start rule applied to `SOUL.md` and memory. Read together: that skill
  covers what an agent knows, this one covers what it runs on.
- **skill-library-curation** — the skills index is part of the per-turn input overhead this
  skill tries to reduce.
- **hermes-agent** (bundled) — authoritative reference for the Hermes CLI and config keys.
