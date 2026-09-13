# Router trust boundary and tool-execution safety

> Generic operating guidance. This document does not endorse a provider, router,
> relay, or model vendor.

A model router is not only a transport convenience. A router or relay that
terminates the client connection and opens another upstream connection can read
and potentially transform the plaintext request and response. Tool definitions,
tool arguments, prompts, outputs, and credentials may cross that boundary.
Multiple routers compose a weakest-link chain: one compromised hop can affect the
response delivered to the client, while every hop can observe plaintext traffic.

This is a security boundary for any instantiated team. It is separate from
prompt-injection defense and separate from model quality.

## Minimum policy

1. Inventory every configured model endpoint and intermediary. Record the
   endpoint's operator, purpose, data exposure, credential scope, and whether
   response integrity is independently authenticated.
2. Use the smallest credential scope and least-privileged tools possible. Do not
   send long-lived or unrelated credentials through an untrusted or unverified
   intermediary.
3. Treat tool-call arguments as untrusted until the client-side policy gate has
   checked the tool name, argument shape, target, and risk class. Schema-valid
   JSON is not proof that the semantic action is safe.
4. Fail closed for high-risk actions when endpoint provenance, response
   integrity, policy evaluation, or required human approval is missing. Do not
   let autonomous mode bypass this gate.
5. Keep router and tool-call audit records append-only and metadata-minimal.
   Never record API keys, private keys, raw prompts, or unredacted sensitive
   arguments merely to make an action auditable.
6. Test conditional and dependency-targeted changes, not only always-on payload
   changes. A benign warm-up probe or a domain-only check is not sufficient
   evidence that a path is clean.

## Bounded preflight checklist

Before enabling a new router or relay:

- [ ] Endpoint, operator, and upstream path are known and documented.
- [ ] Credential scope is limited to this endpoint and this workload.
- [ ] High-risk tools have an explicit policy and approval boundary.
- [ ] Tool-call arguments are checked before execution, including URLs,
      package names, shell commands, filesystem targets, and destinations.
- [ ] Missing or invalid integrity/provenance causes a safe stop.
- [ ] Autonomous execution uses the same gate as interactive execution.
- [ ] Logs exclude secrets and raw sensitive payloads.
- [ ] A test fixture covers benign, rewritten, conditional, and exfiltration
      cases, with measured false positives and false negatives.
- [ ] An independent verifier reads back the result before rollout.

## What this does not claim

This guidance does not claim that every router is malicious, that hop-by-hop TLS
provides end-to-end response integrity, or that a particular research prototype
is production-ready. Cryptographic provider-backed response integrity is a
future protocol capability unless the configured provider and client verify it.
This document is a policy contract; it does not silently change a user's Hermes
configuration or install a router, detector, or dependency.

## Source and evidence

The trust-boundary and attack taxonomy are informed by Liu et al., "Your Agent
Is Mine: Measuring Malicious Intermediary Attacks on the LLM Supply Chain,"
arXiv:2604.08407v1 (2026), https://arxiv.org/abs/2604.08407. The source is a
preprint and is used conceptually. Team6-kit copies no source code, prompts, or
attack payloads from the paper.
