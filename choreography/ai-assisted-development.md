# AI-assisted development contract

This is a compact, tool-neutral contract for work performed with an AI coding
agent. It is derived from the public conceptual guidance in
[jnMetaCode/ai-coding-guide](https://github.com/jnMetaCode/ai-coding-guide),
snapshot c5dde338c68adaac6cffc70ab11f1b1b22e70b0f. It is adapted for Team6's
existing ownership, review, and verification rules. It is not a copied template
or an instruction to install another tool.

## Before editing

The task brief must state:

- the intended behaviour and acceptance criteria;
- the files and dependencies in scope;
- the commands that prove the change;
- constraints and forbidden actions; and
- the handoff owner and independent verification owner.

If the request is unclear, inspect the relevant files and report the current
understanding before changing them. Do not guess from a symptom.

## While editing

1. Read the smallest set of relevant files first.
2. Keep the change within the declared scope. Ask before adding a dependency or
   changing a public interface.
3. For parallel work, give each worker an isolated worktree or explicitly
   disjoint file ownership.
4. Keep generated tests focused on observable behaviour, not call counts or
   private implementation details.

## Test contract

Choose the narrowest useful test level and include normal, boundary, and error
cases. For a refactor, first capture the behaviour that must remain stable.
Prefer this sequence:

1. Write or review the behaviour cases.
2. Run them against the current implementation when practical.
3. Implement the change.
4. Run focused tests, then the repository gate.
5. Review every generated assertion. A passing test is not evidence if it does
   not assert the requested behaviour.

A test that passes before and after a fix is a guard, not proof that it pins the
regression. Record that distinction in the handoff.

## Security contract

Before handoff, check the changed path for:

- hardcoded secrets, tokens, passwords, or private endpoints;
- sensitive values in logs, errors, fixtures, or snapshots;
- unsanitized input in SQL, shell commands, paths, HTML, or templates;
- missing authorization checks on protected operations;
- disabled TLS or unsafe token storage; and
- unvalidated file uploads, deserialization, or external responses.

For security-sensitive changes, run an independent review against the relevant
OWASP categories and record file, severity, evidence, and remediation. Do not
paste live credentials into prompts, tests, commits, or reports.

## Done means verified

The maker does not mark the work complete. The handoff must include the exact
commands run, their exit status, focused results, remaining limitations, and
which independent agent read the artifact back. Local success is not a claim
about a deployed or published surface.

## Source and license boundary

The source guide's repository-level license is Apache-2.0, while its `book/`
content is separately identified as CC BY-NC-SA 4.0. This file uses only
adapted principles and attribution. No source template, executable installer,
MCP declaration, hook command, or book text is bundled.
