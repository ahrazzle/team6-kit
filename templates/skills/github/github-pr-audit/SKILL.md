<!-- GENERICIZED: 1×{RELATIONSHIP} | source: skills/github/github-pr-audit/SKILL.md -->
---
name: github-pr-audit
description: "Use when auditing a GitHub PR or issue before merge."
version: 1.0.0
author: Team6 / {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, Code-Review, Pull-Requests, QA, Audit]
    related_skills: [github-code-review, github-auth, adversarial-review]
---

# GitHub PR / Issue Audit (pre-merge QA)

A focused workflow for the QA pass on a GitHub contribution — PR or feature
issue — before it lands on a high-visibility open-source repo. This is the
VERIFICATION DISCIPLINE that prevents publishing a wrong or sloppy review, plus
the GitHub permission realities that shape how you sign off. For the raw
diff/comment mechanics (gh vs REST, inline comments), load `github-code-review`
alongside this — that skill covers commands; this one covers gates.

## When to use
- "Review this PR", "audit this contribution", "make sure we don't look stupid
  on this merge".
- Any PR/issue on a watched repo where a bad review reflects on the team.
- Companion to `github-code-review`: load both. That one is the tool; this one
  is the QA checklist.

## The non-negotiable sequence

### 1. Get LIVE state — never trust a handoff diff
A `.diff` file dropped in chat or `/tmp` is a SNAPSHOT and may be a stale draft.
The branch is often tightened BEFORE push. Critiquing it produces a review of
code that isn't in the PR — the exact "look stupid" failure.
- `git diff main...HEAD` on the local checkout. First confirm you're actually on
  the PR branch: `git branch --show-current`.
- `gh pr diff N --repo O/R` for the remote truth.
- If they disagree, the local checkout is stale — trust `gh` output and say so.

### 2. Verify the bug premise against `main`
Do not accept the PR's rationale. Read the actual code on `main`:
- `git show main:<path>` (pipe through sed/awk to the function), or
- `git worktree add -q /tmp/hm-main main`, read/run there, then
  `git worktree remove /tmp/hm-main --force`.
Confirm the broken branch/symptom the PR claims to fix REALLY exists on main.
If it doesn't, the fix may be mischaracterized (partial, or already fixed).
State it explicitly.

### 3. RUN the test suite — in the repo's own interpreter
Never trust a PR body's "17 passed". Execute it.
- `python` is often NOT on PATH. Check for `venv/bin/python` (target version per
  `.python-version`), or use `uv run`. Repo venv example:
  `./venv/bin/python -m pytest tests/tui_gateway/test_x.py -q`
- Run the touched file AND the sibling suites the PR depends on.
- Test node IDs are CLASS-qualified: `file.py::TestClass::test_method`, not
  `file.py::test_method` (the latter fails with "no match"). Grep the class name
  first if unsure.
- Record the real pass/fail counts in your review output.

### 4. Verify evidence claims in the PR/issue body
If the body cites a "pre-existing failure" or a specific test as proof, RUN that
exact test on `main` AND on the branch. A reviewer who runs the suite will catch
a false claim — so you must catch it first. If a claim is false or orthogonal
(e.g. cites a GUI test that passes and is unrelated to the logic touched), strip
it via `gh pr edit N --repo O/R --body-file <file>` — you have edit rights on
your own account's PR. Never leave a verifiable falsehood in a public PR.

### 5. Scope & rubric fit
Read the repo's `AGENTS.md` / `CONTRIBUTING.md`. Check specifically:
- **Speculative infrastructure** — shared registries/helpers with NO in-PR
  consumer. Textbook case: a `_X_KEYS` frozenset + `_drop_stale_key` helper
  gating behavior `config.pop` already provides. Trace the code: if an unknown
  key already survives a persist (e.g. `dict(existing)` copy + the function never
  enumerates it), the registry adds ZERO behavior. Flag and recommend deletion.
- New `HERMES_*` env vars for non-secret config, cache-breaking mid-conversation
  changes, scope creep that revives a closed direction.
- Feature requests belong in SEPARATE issues, not bundled into a bugfix PR.
- The bars a good fix meets: "fix real bugs well" + "behavior contracts over
  snapshots" + "E2E validation not just green mocks".

### 6. Posting the sign-off — GitHub blocks self-approval
`gh pr review N --approve` from the PR AUTHOR's account fails:
`Review Can not approve your own pull request` (hard API rule, not policy).
- Do NOT fake an outside-approver stamp or spin up a second account.
- Post a transparent QA-pass COMMENT instead: `gh pr comment N --repo O/R
  --body-file <file>`. Lead with "Team6 QA pass" (honest provenance), document
  the substance, the test numbers you actually ran, and any housekeeping fixed.
- For issues: post scoping nits (e.g. "proposed `sessions list --model` collides
  with the existing `sessions list` command — extend it instead") as
  `gh issue comment`.

## Pitfalls
- **Stale handoff diff** → you review phantom code. Always re-diff live.
- **Trusting PR-body test counts** → false evidence a reviewer catches. Run it.
- **`gh pr diff` needs `--repo O/R`** when not inside a cloned repo context.
- **`gh pr review --approve` self-block** → use a comment, never a fake approve.
- **`python` missing from PATH** → use `./venv/bin/python` or `uv run`.
- **Unqualified test IDs** → class-qualify them (`TestClass::test_method`).
- **Editing a PR body you don't own** → only do it on your own account's PRs.

## References
- `references/verification-recipe.md` — copy-paste command sequence for a full
  pre-merge audit (live diff, main premise check, venv test run, body-claim
  verification, comment posting).
