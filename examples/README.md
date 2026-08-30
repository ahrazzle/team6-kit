# The instantiation proof-point — walkthrough

This directory contains the repo's proof that the kit does what WHY.md
claims: **one parameter file in, a configured team out.** No hand-assembly,
no manual profile setup, no scripting — a single command.

## What you'll get

```
examples/
├── demo-consulting.yaml     # the ONE parameter file you edit
└── README.md                # this walkthrough
```

The parameter file is a plain YAML of 9 declared keys — team name, director,
agent role, model provider. That's the whole input. Everything else the
generator produces (identity, choreography, skills, audit) is derived from
these keys against the kit's `templates/`.

## Run it

```bash
python3 build/generate.py --params examples/demo-consulting.yaml --out /tmp/demo-team
```

Wait for the gates (sweep + review) to pass, then inspect the output:

```
/tmp/demo-team/
├── AUDIT.md          # what was shipped, honestly reconciled to disk
├── personas/         # the configured team's identities
└── skills/           # the skills they run with
```

## What the output demonstrates

Three things, in order of how much they matter:

1. **Instantiation works.** `demo-consulting.yaml` → a team named "Northwind
   Advisory" run by a director "Elena" with a coder role — the placeholder
   substitutions land in the generated SOUL.md and profile.yaml, not as
   un-substituted templates. One file in, a working team out.

2. **The gates are real.** The generator refuses to assemble if the semantic
   pass is unsigned or a new file drifts into scope — it fails closed rather
   than emit an unverified team. This is the governance claim (WHY.md #2)
   *demonstrated*, not asserted.

3. **The audit is honest.** `AUDIT.md` states `rows shipped` equal to the
   files actually on disk, and every KEEP-REVIEW row carries its sign-off
   status. Count == what's written == what passed the gate. No ghost rows.

## Why this matters

The whole kit exists because *designing a multi-agent team from scratch* is
the expensive part — the choreography, the governance, the orchestration
contracts that survive real failures. This demo is the smallest honest proof
that the kit packages that: you write 9 keys, the generator applies the
packaged design, and you get a governed, instantiated team you'd otherwise
have to design yourself.

It's also deliberately *modest*. It proves the contract end-to-end; it does
not yet prove that a team instantiated this way *ships a real product* — that
is the next proof-point, and it arrives with the first vertical pack.
