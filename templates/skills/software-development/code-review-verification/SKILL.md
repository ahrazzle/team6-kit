<!-- GENERICIZED: 1×{RELATIONSHIP} | source: skills/software-development/code-review-verification/SKILL.md -->
---
name: code-review-verification
description: "Ground code reviews: stale briefs, RED-check, write path."
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Code-Review, Verification, Testing, Git]
---

# Code Review Verification

Rigor layer for reviewing a contribution described in a brief. The
bundled `github-code-review` skill covers the mechanics (gh commands,
diff reading, review formats). This skill covers the verification
discipline that separates a real audit from a rubber stamp: does the
brief match the live PR, do the added tests actually pin the regression,
and does the fix actually change behavior end-to-end?

## When to use

- Reviewing a PR/commit described by another agent's brief or chat message.
- The diff or commit list does not match what the brief describes.
- A bug-fix PR adds tests and you need to know which ones matter.
- The fix is a merge / delete-on-falsy / persist change and you need to
  know whether it is effective through the full write → read chain.

## 1. Stale-brief guard (verify premises before finding defects)

A brief written by another agent describes the PR at the time the brief
was written. PRs get force-pushed after review feedback; the brief does
not update. A "missing commit" or "missing file" is often a STALE BRIEF,
not a PR defect.

1. Get live truth first — never trust the brief for commit/file counts:
   ```bash
   gh pr view $PR_NUMBER --repo $OWNER/$REPO --json commits,files,additions,deletions,title \
     --jq '{commits: (.commits|length), files: [.files[].path], additions, deletions}'
   ```
2. Check local git ground truth:
   ```bash
   git reflog --date=iso $BRANCH | head -15
   ```
   A commit present in reflog but absent from the branch was deliberately
   dropped (soft-reset + recommit after a prior review). That is usually
   the RESOLUTION of earlier feedback, not lost work. Re-raising it as
   "Critical: missing work" is a false positive.
3. If the brief still claims the dropped work, reconstruct the decision
   from the authoring session before calling it a defect: Hermes chat
   transcripts live in each profile's `state.db` (`sessions` + `messages`
   tables; `timestamp` is a REAL unix epoch). Query by session id —
   the user will often have the id ("the chat where we discussed X").
   The session shows which reviews ran, what they concluded, and what was
   deliberately removed.
4. Only after 1–3, if the mismatch is real, report it — and say it is a
   brief defect, not a PR defect.

Worked example with exact commands: `references/stale-brief-archaeology.md`.

## 2. RED-check regression tests (which tests actually pin the bug)

When a fix PR adds tests, run them against the PRE-FIX code. Tests that
FAIL on old code are real pins; tests that pass on both old and new code
are guards (or tautologies) — report them as such instead of counting
them as regression coverage.

```bash
cp tui_gateway/server.py /tmp/server_fixed.py          # or whatever file changed
git show origin/main:path/to/changed.py > path/to/changed.py
venv/bin/python -m pytest tests/... -q                  # pinning tests FAIL here
cp /tmp/server_fixed.py path/to/changed.py              # restore!
git diff --stat path/to/changed.py                      # verify clean restore
```

Pitfalls:
- Restore the file immediately and confirm with `git diff --stat`
  (empty output = clean). A dirty working tree after a RED-check can
  poison the next test run or get committed by accident.
- The count in the brief ("7 new tests") may be wrong; count
  `def test_` in the diff yourself.
- A test that passes pre-fix is not worthless — it can be a guard for a
  property that already held — but it does not pin THIS regression.

## 3. Write-path effectiveness (delete-on-falsy and merge fixes)

A delete-on-falsy / merge fix is only real if the WRITE path actually
persists the deletion AND no READ path resurrects the old value. Trace
the full chain, not just the merge function:

- Check the DB write for `COALESCE(?, column)`: passing `None` keeps the
  old column value. A JSON key popped from `model_config` is INERT if the
  caller writes `value or None` and the column is authoritative.
- Check the resume/read path for preference order: `row.get("col") or
  json.get("key")` means the column wins — a popped JSON key never changes
  resume behavior.
- Column-vs-JSON asymmetry is a real finding class: the fix is fully
  effective for keys with NO separate column (e.g. `provider` when only a
  `billing_provider` fallback exists) but inert for keys WITH one (e.g.
  `model`). Verify the incident's actual key, not the symmetric-looking
  pair.
- When a fix is inert, the test docstring often overclaims ("an empty X
  cannot keep the row's old Y" — but the row does keep it). Flag the
  docstring, and decide whether the code should also clear the column.

## 4. Re-check after revision

If the session history shows the PR was revised mid-review (registry
stripped, tests removed, force-push), re-verify what survived:
- A property you cared about may have lost its only test when a
  registry-dependent test was deleted. Unknown-key preservation in a
  copy-then-pop-known-keys merge is a property that is trivially true by
  construction but worth a 3-line pin.
- Run the full target suite on the final commit and report the real
  pass count, not the brief's number.
