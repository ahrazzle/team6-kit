<!-- GENERICIZED: 5×{CLIENT}, 3×{RELATIONSHIP} | source: skills/autonomous-ai-agents/hermes-agent-contributing/SKILL.md -->
---
name: hermes-agent-contributing
description: "Use when contributing to hermes-agent upstream."
version: 1.0.0
author: {RELATIONSHIP} ({RELATIONSHIP})
license: MIT
platforms: [linux, macos, windows]
---

# Contributing to hermes-agent Upstream

> User directive ({CLIENT}): never neglect opportunities to contribute to hermes-agent. Real gaps found during Team6 operations become evidence-based PRs or issues. Contributions to date: PR #96748 (session model_config desync fix — landed on main as commit ea15f7fa), issue #96745 (session model audit/reset CLI — IMPLEMENTED and shipped {CLIENT} as PR #97510: `sessions list --model/--provider` filters + `sessions repair --model TARGET [--provider TARGET] [--dry-run] [--all]` + `cron list` model/provider pin display; 9 new tests in tests/hermes_cli/test_sessions_model_reset.py). PR #96748 initially bundled a `_MODEL_CONFIG_KEYS` key-registry, which peer review stripped as speculative dead infrastructure — see Repo Conventions + Pitfalls; the merged PR is the narrow fix only. {CLIENT}: backed PR #92213 (per-room group-chat limits) with operating evidence on why per-room persisted overrides survive app updates where bundle patches do not — comment 5464411459 (see the "Check upstream FIRST" step below; this was the right move instead of writing a competing caps PR).

## When to Use

- A bug/gap in Hermes surfaces during normal ops (session persistence, config, gateway, CLI, resume behavior)
- User asks to put an improvement up on GitHub ("any improvements worth putting up on github?")
- A fix for a whole bug class exists and sibling call paths are identified

## Workflow

### 0. Check upstream FIRST — do not write a competing PR

- Before writing ANY feature PR, confirm it does not already exist as an open issue or PR. Feature ideas for Hermes routinely already have tickets — and the codebase flags them: a source comment reading `live contributor work — #XXXXX and #YYYYY` (e.g. `group-chat.ts:1200` for the group-chat caps) means the seam is deliberately held open for an existing ticket. Search:
  - `gh search prs --repo NousResearch/hermes-agent "<feature>" --json number,title,state,author,mergeable`
  - `gh issue list --repo NousResearch/hermes-agent --search "<feature>"`
  - `grep -rnE '#[0-9]{4,6}' apps/<area>/src` near the constants you would touch (issue-number comments point at the owning ticket).
- If an open PR already implements it (or an open issue already scopes the design), do NOT write a fresh PR with the same title — it will be rejected as redundant. The winning move is one of: (a) back the existing PR with real operating evidence (a comment with incident data a maintainer can act on), or (b) close the specific sub-gap the existing work misses, raised IN that PR's thread.
- Verified {CLIENT}: "configurable group-chat caps" already existed as #92213 (open, actively implemented, 8 commits, 766 add), #98047 (config.yaml global ceilings) and #97492 (round-cap + token-budget port). A fresh PR would have duplicated #92213 and been rejected; contributing evidence instead advanced the real path.

### 1. Recon

- Local checkout: `~/.hermes/hermes-agent` (already cloned, on main).
- Read `AGENTS.md` rubric FIRST — it states what gets merged vs rejected and shapes the PR.
- Confirm clean main: `git status --short --branch`, `git log --oneline -3`.
- Locate the function + all call sites (search_files), read the full function and existing tests — existing tests encode conventions and give the test file to extend.

### 2. Reproduce with live evidence

- Real incident data (row dumps, config excerpts) beats constructed examples in PR descriptions.
- Prove the mechanism in code before claiming root cause (read `_runtime_model_config`, `_stored_session_runtime_overrides`, the write path `update_session_meta`).

### 3. Fix the whole bug class

- AGENTS.md: fix sibling call paths, not just the reported site.
- Match existing patterns in the codebase (e.g. the or-None deletion the CLI path already uses for stale keys).
- Keep the diff small and the docstring honest about the failure mechanism.

### 4. Tests

- Unit tests for the function + real-DB E2E (temp `HERMES_HOME` via `tmp_path` + `monkeypatch.setenv`) per repo preference; behavior contracts over snapshots.
- Run: `cd ~/.hermes/hermes-agent && venv/bin/python -m pytest tests/<area>/ -q`.
- Pre-existing failures: prove with `git stash && run && git stash pop`, report honestly in the PR (do not claim a green suite that isn't green on main either).

### 5. Commit + PR

- Conventional commits, one logical change per commit, branch from main: `git checkout -b fix/<slug>`.
- No direct push (403 for non-maintainers): `gh repo fork NousResearch/hermes-agent --clone=false`, `git remote add fork ...`, push, then `gh pr create --repo NousResearch/hermes-agent --head <user>:<branch> --base main`.
- PR body: what + evidence + reproduction + test results + pre-existing-failure note + related issue link.
- Feature requests: file an ISSUE first with the real incident as motivation; label is `type/feature` (NOT `enhancement` — that label does not exist and `gh issue create` fails atomically; the issue is not created, verify with `gh issue list`).
- Authored as `{RELATIONSHIP}` (user's GitHub identity) — verified in PR metadata.

### 6. Verify + follow up

- `gh pr view <n> --repo NousResearch/hermes-agent --json state,commits,additions,deletions`.
- `gh pr checks <n>` may report nothing on a fresh fork PR — normal.
- Watch maintainer feedback; if the issue gets traction, implement the CLI from the reference script.

## Repo Conventions (verified)

- Contribution rubric in `AGENTS.md`: bug-first, whole-class fixes, E2E validation, core-narrow, no speculative hooks, config.yaml not env vars for non-secrets.
- Test layout: `tests/<module>/test_*.py`; run with `venv/bin/python -m pytest` (repo venv at `venv/`).
- Shared cross-consumer constants live in `hermes_state.py` (precedent: `_BARE_BILLING_PROVIDERS` — genuinely load-bearing at runtime in two files). RESOLVED {CLIENT}: the `_MODEL_CONFIG_KEYS` registry initially added to PR #96748 was stripped by peer review as speculative dead infrastructure — it changed zero runtime behavior (all call sites passed literal keys already in the set), its only stated consumer was an *unimplemented* feature (#96745), and the downgrade-safety it claimed holds anyway because the merge starts from `dict(existing or {})` and never touches un-named keys. Do NOT ship a key-registry for a feature that isn't built yet. The merged PR is the narrow deletion fix only (single commit, 2 files).
- Session persistence map: `_runtime_model_config` (gateway writer) + `_stored_session_runtime_overrides` (gateway reader) in `tui_gateway/server.py`; CLI sibling `_persist_model_switch_to_session` in `cli.py`; DB ops in `hermes_state.py` (`create_session`, `update_session_meta`).
- Known pre-existing main failure: `tests/tui_gateway/test_gui_surface_toolsets.py::test_holds_exactly_the_gui_affordances` (apply_layout toolset drift) — fails on main without any diff; note it, don't fix it in an unrelated PR.

## Pitfalls

- **Never write a competing feature PR when one already exists upstream.** Duplicates are rejected outright and burn reviewer + author time. Run `gh search prs` + `gh issue list` + grep the source you would touch for issue-number comments (`live contributor work — #XXXXX`) BEFORE proposing. If found, contribute evidence to the existing PR or raise the missing sub-gap in its thread — never a fresh PR with the same title. Check BOTH closed and open: a closed PR may be the same feature superseded by a bigger rebuild (e.g. #96842 closed because #96726 deleted its target file) and still carrying the design to port.
- **Check merged PRs too, and their related open PRs.** `gh search prs` surface is shallow; `gh issue view <n> --json comments` (closure rationale often names the successor PR) and searching by feature keywords in related titles surfaced the whole family in this session. One quick keyword search beat an hour of design work.
- **Do NOT bundle speculative infrastructure into a bug-fix PR.** AGENTS.md rejects "hooks/callbacks/extension points with no concrete consumer" and "dead code wired in without E2E proof." A registry/constant/helper whose only stated consumer is an *unimplemented* feature (your own open issue) is exactly that — a peer review WILL return REQUEST CHANGES. A guard that is a no-op at every call site (all literal args already in the set) adds surface with zero runtime effect. Keep the bug-fix PR to the narrow deletion fix; offer the refactor as a focused follow-up tied to the feature, built when the feature lands.
- **Don't justify infra with a wrong rationale.** "This prevents X" is only true if the code path being fixed actually touches X. (The `_branched_from`/`_delegate_from` lineage loss was an ad-hoc SQL script's preserve-list, NOT the merge function being fixed — so a registry inside `_runtime_model_config` would NOT have prevented it.)
- **Heredoc commits**: `git commit -m "$(cat <<'EOF' ...)"` breaks on quotes in the shell — write the message to a file in `.git/` and `git commit -F`.
- **gh label typos fail atomically**: bad label → no issue created, no error you can see. Re-check with `gh issue list --search`.
- **Preserve operational keys**: when the PR touches `model_config` rewrites, `_branched_from`/`_delegate_from` are lineage — see skill `hermes-session-model-overrides`.
- **Don't claim green**: report the real suite result including pre-existing failures, with the stash-proof.

## References

- references/repo-conventions.md — detailed file map, key functions, test conventions
- templates/pr-body.md — evidence-based PR body scaffold
