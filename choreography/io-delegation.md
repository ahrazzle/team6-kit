# Vendor-neutral I/O delegation contract

> A bounded, opt-in routing pattern that *may* offload predictable, read-heavy
> summarization or pattern-conforming scaffolding to a cheaper worker while the
> frontier agent keeps edits, debugging, architecture, and final acceptance.
> This is a **contract and an example config**, not a runtime, hook, or
> dependency. The public kit documents the pattern; it does not bundle an
> implementation.

## What this is (and is not)

- **Is:** a bounded routing pattern for two narrow work classes — predictable
  read-heavy summarization and pattern-conforming scaffolding. It is opt-in and
  is **never automatic merely because a file is large**.
- **Is not:** a runtime, a network client, an executable hook, a new provider,
  a change to the routing/llama layer, or a mechanism for editing, debugging,
  architecture, or high-stakes judgment. It adds no model dependencies and no
  profile-specific settings.

## Why it exists

A generated team already sends approved work outward. For large, predictable
reads, delegating the bulk-read summary to a cheaper worker can reduce token
use on the frontier model and keep the frontier context for the work that
actually needs reasoning. The value is that the pattern is *explicit and
bounded*, so it never silently offloads the work that must stay with the
frontier agent.

## What is always delegated to the frontier agent

The following are **non-delegable** and must be handled by the frontier agent
itself:

- Edits, writes, and any change to the codebase or documents.
- Debugging and root-cause analysis.
- Architecture, design, and decision-making.
- Security- and safety-critical work.
- Ambiguous requirements and anything where the input contract is unclear.
- Final acceptance of any result.

Worker output is **advisory, ephemeral, and not a source of truth**. Before
editing or accepting anything, the frontier agent must independently read the
targeted sections itself. The worker may narrow the search; it never replaces
the frontier agent's own read of the relevant content.

## Explicit route fields

Every route entry records these fields so the delegation is bounded and
auditable:

- `worker model` / `provider` / `api_host` — the exact identity of the worker.
- `purpose` — why this route exists (the predictable work class it serves).
- `max_input_bytes` — hard cap on input size for this route.
- `max_latency_seconds` — hard bound on wait time; the route fails safely
  rather than blocking indefinitely.
- `output_contract` — the shape the worker must return (format + required
  fields).
- `fallback: frontier-targeted-read` — if the worker fails, is rejected, or
  cannot satisfy the output contract, the frontier agent falls back to reading
  the targeted sections itself.

## Modes and quotas

- **Default mode is `observe`**: record what happens but never act on it as a
  standing claim.
- **No invented quotas.** The kit never guesses a limit or a savings figure.
- Route policy resolves using the **existing** provider/model/API-host identity
  rules in `model-policy.md` — a route is a separate concern from rate-limit
  policy and never re-implements it.

## Privacy and approval

Input must pass the local privacy/redaction policy **first** (see
`local-preprocessing.md`). Never transmit secrets, credentials, private
identifiers, or unreviewed client data to a worker.

- **External/third-party workers require explicit operator approval.**
- First-party workers still obey the redaction and no-sensitive-content rules.
- Any delegation that would expose uncertain or sensitive content is held for
  operator review before transmission.

## Telemetry

Every delegation records, without any raw sensitive content:

- the route used (its identity fields),
- input and output byte counts,
- latency,
- status (success / rejected / fallback / failure),
- the fallback outcome, and
- the verification result (how the frontier agent re-read the targeted
  sections).

Record the **routing event and its metadata**, never the sensitive payload.

## Thresholds are recommendations, not claims

This contract defines *bounded routing*, not a measured outcome. No specific
savings percentage is claimed as Team6 evidence. The source vendor's published
figure is treated as a **self-reported vendor claim**, not a universal result:

> Spotify reports a roughly 90% mean bulk-read saving in a four-scenario Java
> monorepo test; Team6 adopts only the routing principle and does not claim
> this result.

## Compatibility

- This contract is **compatible with** `model-policy.md`: route resolution
  reuses the canonical provider/model/API-host identity rules and never invents
  quota domains.
- This contract is **compatible with** `local-preprocessing.md`: every
  delegation sits behind the local privacy/redaction policy and its
  hold-for-review rule.
- **Non-delegation exclusions** are explicit above and mirror the high-stakes
  judgment exclusions in the local-preprocessing contract — anything security-,
  safety-, architecture-, or correctness-critical stays on the frontier agent.

## Example config

A concrete, vendor-neutral example schema is in
`registry/io-delegation.yaml.example`. It is a config **example only** — copy
it into your own deployment settings and fill in verified worker identities and
bounds; nothing in the Team6 open-core build enables this pattern by default or
edits a user's Hermes profile to do so.
