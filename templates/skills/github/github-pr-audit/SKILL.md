---
name: github-pr-audit
description: "Use when auditing a GitHub PR or issue before merge."
version: 1.4.0
author: Team6
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

### 4a. Audit the evidence register
For a multi-finding PR or issue, define the counted unit and count each item once at its highest impact. Separate fixes included in the current head from requests, overlaps, and unresolved findings. Map every row to its exact artifact, commit, test, and status. Record the evidence boundary: base or head, commit or composition, environment, and measurement time when relevant. Missing transferred artifacts or unrun tests do not establish a claim; list them as separate unverified follow-ups.

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
### 6b. When you also own the MERGE lane
Self-approval being impossible does NOT block the merge — review and merge are
separate permissions. Check the real gates instead of assuming a human must act:
`gh api repos/O/R/branches/main --jq .protected` and `gh api repos/O/R --jq .permissions`.
With no branch protection and `admin`, merge it yourself (`gh pr merge N --repo O/R
--<method>`), then post the QA-pass comment on the merged PR and read the merge back.
- Take the merge METHOD from the repo's own history, not the provider default:
  `git rev-list --count --merges origin/main`. Zero merges = linear history, so use
  `--rebase` or `--squash`; a bare `--merge` would add the repo's first merge commit.
  Record the choice and the rejected alternative in the receipt.
- Rebase/squash REWRITE the SHAs you audited. State the new main SHA and note that the
  pre-merge SHA still exists on the branch/PR refs, or the receipt contradicts the audit.
- For issues: post scoping nits (e.g. "proposed `sessions list --model` collides
  with the existing `sessions list` command — extend it instead") as
  `gh issue comment`.

## Cross-artifact and public-claim gates (PQA-CLM / PQA-DOL / PQA-STAND / PQA-SEM)

Four gate contracts cover every public artifact — issue body, PR body, comment,
review. They sit on top of the evidence register in section 4a: that register
proves the internal audit; these four decide what may be published. A CONFIRMED
verdict on code behavior must satisfy PQA-SEM before it may be labeled as a known
defect. PQA-SEM gates semantic justification (dispatch context, per-arm evaluation,
independent reproduction); the others gate claim linkage, artifact division, and
standalone prose. A red or
missing claim register, pair manifest, standalone scan, or second-member
proofread blocks the lane. The lane inputs these gates read are declared in the
handoff brief; the field list is at the end of this section.

| gate | minimum pass condition | required evidence |
|---|---|---|
| **PQA-CLM** evidence-linked public claims | every factual claim is linked, or explicitly scoped as observed in testing; `known` / `known defect` carries a claim-specific public issue/PR URL | complete claim register, boundary, scope wording, public ref where required |
| **PQA-DOL** cross-artifact division | the primary artifact is complete; the secondary carries only new information, a pointer, the ask, and a defect absent from the primary; both deletion tests pass | pair manifest, overlap result, two deletion-test results |
| **PQA-STAND** standalone public prose | issue/PR bodies never address a person; comments are standalone except for a recorded, required one-line handle; no second-person address, salutation, or addressed imperative | surface policy, requirement ref, scan hits, handle-removal result |
| **PQA-SEM** semantic-verification gate | every CONFIRMED code-behavior verdict cites the semantic mechanism and passes adversarial reproduction; conditional/duplicated declarations are evaluated per dispatch context | surface shape, mechanism file:line, per-arm/per-context results, reproducing agent, commit, verdict after SEM |

### PQA-CLM — evidence-linked public claim gate

**Checklist item.** One claim-register row per factual sentence, in every public
artifact. Classify each row as linked fact, scoped observation, proposal or
question, or defect/status claim. A factual assertion hidden in a heading, a
bullet, a closing offer, a quoted log, or a follow-up sentence is still a claim.

**Pass/fail rule.** PASS only when every factual claim has either:

1. an inline or adjacent evidence link or register entry that names the exact
   proof and its boundary; or
2. scoped wording — `observed in our testing`, `in the local prototype`, `in
   this run`, `not verified beyond <scope>` — plus a register entry naming the
   internal evidence with its environment and measurement time.

`known`, `known defect`, `established`, and equivalent certainty FAIL unless the
same claim carries a verified public GitHub issue or PR link that tracks that
exact fact or defect. A private receipt, local path, private log, or private
evidence register never satisfies that link. A cited public issue/PR URL must
resolve to an existing public item and be claim-specific: a future URL for the
artifact being drafted is not evidence, and a link to an unrelated tracking item
does not pass. An unfiled observation is written as an observation, never as a
known defect.

**Required evidence fields.** `claim_id`; `surface`; `artifact_path_or_url`;
`section_or_line`; `claim_text`; `claim_class`; `evidence_ref`;
`evidence_boundary` (base/head, commit or composition, environment, measurement
time); `scope_wording` (required for an observation); `public_issue_or_pr_ref`
(required for known/defect certainty); `status`.

**Lane prompt.** `Public claim register: list every factual claim by artifact and
line. For each row provide claim_id, claim class, exact evidence_ref, boundary,
and either a public issue/PR URL or the scoped observation wording. Mark any
unfiled observation as observed-in-testing; do not call it known or a known
defect. Private receipts do not satisfy public_issue_or_pr_ref.`

### PQA-DOL — cross-artifact division-of-labor gate

**Checklist item.** For each pair of public artifacts, declare the primary
artifact, the secondary artifact, the job of each, and the information units the
secondary may carry. Test the pair, not each file in isolation.

**Pass/fail rule.** PASS only when the primary carries the complete proposal or
story and the secondary repeats no primary claim, even when the repetition is
paraphrased or fact-correct. The secondary may contain only:

- new information absent from the primary, with its own claim/evidence row;
- a pointer to the primary;
- the direct ask; and
- a defect only when the primary is missing that defect.

Run both deletion tests:

- Delete the secondary. The primary must still carry the proposal, its necessary
  facts, and the decision context.
- Delete the primary. The secondary must not tell the whole story. If it does,
  FAIL the pair as self-contained duplication.

A repeated number, mechanism, question list, follow-up, or defect fails the
secondary. Fact correctness, clean overlap, or a pointer somewhere in the
repeated prose does not rescue it.

**Required evidence fields.** `pair_id`; `primary_surface`; `secondary_surface`;
`primary_job`; `secondary_job`; `primary_claim_ids`; `secondary_new_claim_ids`;
`secondary_pointer`; `ask`; `secondary_defect_claim_ids`;
`defect_absent_from_primary` (yes/no with line evidence);
`delete_secondary_result`; `delete_primary_result`; `overlap_result`.

**Lane prompt.** `Artifact pair contract: name primary and secondary surfaces and
their distinct jobs. List the primary claim IDs. List only
secondary_new_claim_ids, the pointer, the direct ask, and defects absent from the
primary. Record the two deletion-test results. If the second artifact still tells
the whole story after the primary is deleted, mark FAIL.`

### PQA-STAND — standalone public-prose gate

**Checklist item.** Fix the exact surface class before the prose gate: issue
body, PR body, comment, review, or other public reply. Scan all natural-language
prose, including headings and asks, not only the first paragraph.

**Exact surface rule.**

- **Issue body** and **PR body**: standalone unconditionally. No `@handle`, no
  second-person `you`/`your`, no `Hi`/`Dear` salutation, no single-person
  imperative such as `please ...` or `point us ...`, and no claim whose meaning
  depends on a named reader.
- **Comment or review**: standalone by default with the same bans. One separate
  first-line `@handle` is allowed only when the lane brief records
  `comment_addressee_required: yes` and says why. The substantive text still
  carries no second-person address, salutation, or addressed imperative. Remove
  the handle and re-read the claim and the ask: both must remain intelligible.
  Any wording beyond that one handle needs its own recorded requirement and a
  second-member review.

**Pass/fail rule.** PASS when the applicable surface rule holds and the
removal-of-handle test passes. FAIL when an issue or PR body addresses a person,
when any surface carries a personal salutation or addressed imperative, when a
comment relies on the named reader, or when a comment uses the handle exception
without the recorded lane requirement.

**Required evidence fields.** `surface_class`; `standalone_policy`;
`addressee_required` (yes/no); `requirement_ref`; `prose_scan_result`;
`second_person_hits`; `salutation_hits`; `imperative_hits`;
`named_reader_dependency`; `handle_removal_result`; `proofreader`.

**Lane prompt.** `Public surface prose: declare surface_class. For issue_body or
pr_body set addressee_required=no. For a comment/review set
comment_addressee_required=yes only with the requirement reference; otherwise no.
Record prose-scan hits and the result after removing any allowed @handle. State
that the public text is interpretable without a named reader.`

### Incident (public-facing note)

A CONFIRMED verdict on code behavior carried into a public artifact without
evaluating the semantic mechanism — the `when`/mode context that makes a
particular surface shape effective — produced a false defect report. The raw
flat list returned by `get_config_schema()` contained duplicate `api_key` and
`api_url` keys in declaration order, but those duplicates sit in mutually
exclusive `when={'mode': ...}` arms (cloud vs local_external); the effective
key set is unique in every mode. This gate pins the class by requiring that
every CONFIRMED verdict cites the mechanism and verifies it via independent
reproduction.

### PQA-SEM — semantic-verification gate

**Checklist item.** Every CONFIRMED verdict on code behavior that appears in a
public artifact must cite the semantic mechanism that makes the observed surface
shape effective behavior and must pass an adversarial re-check from source at
the cited commit.

**Pass/fail rule.**

*SEM-1 (mechanism citation).* Before ANY public filing of a CONFIRMED code-behavior
verdict, the report must cite the semantic mechanism — the dispatch/visibility/
filter context under which the observed surface shape becomes effective behavior —
with the file:line of the mechanism. Absence of that row FAILs.

*SEM-2 (adversarial re-check).* Before ANY public filing of a CONFIRMED code-behavior
verdict, a second named agent (not the verdict author) must reproduce the claim FROM
SOURCE at the cited commit — re-deriving the semantic mechanism, not merely re-running
the author's probe — and record the reproduction result. Absence of that row FAILs.

*SEM-3 (dispatch-context evaluation).* When the evidence under the verdict contains
conditional, mode-gated, or duplicated declarations (the same key/name declared in
multiple arms/contexts), the verdict must evaluate each arm in its dispatch context
and show the effective per-context result before the claim may be called a defect.
A raw "duplicate exists" observation without that evaluation FAILs and cannot reach a
CONFIRMED/known-defect classification.

A verdict that fails SEM-1, SEM-2, or SEM-3 CANNOT be labeled CONFIRMED as a known
defect. It may be filed as an observation linked to a tracking issue only after it
passes the remaining gates (PQA-CLM, PQA-DOL, PQA-STAND) with scoped wording.

PQA-SEM decides whether the verdict is semantically justified; a verdict failing SEM
can never reach PQA-CLM as a known/defect-certainty claim. PQA-CLM's evidence-linkage
rules apply AFTER semantic justification is confirmed.

**Required evidence fields.** `surface_shape` (raw list contents, byte patterns,
counts, or raw return values cited); `mechanism_file_line` (file path and line
number of the semantic mechanism that governs visibility or dispatch); `per_arm_results`
(effective per-context key set or behavior, with mode or condition name for each);
`reproducing_agent` (name of the second agent that performed adversarial reproduction);
`reproduction_commit` (commit hash used for independent verification); `verdict_after_sem`
(the verdict after SEM evaluation, e.g., CONFIRMED known defect, CONFIRMED known
non-defect, or OBSERVATION requiring tracker linkage); `surface_shape_source` (source
of the raw shape: file:line or function name).

**Lane prompt.** `Semantic verification gate: for every CONFIRMED code-behavior verdict
cited in public artifacts, list the surface shape observed, the mechanism file:line
that governs its visibility or dispatch, the per-arm/per-context effective results
evaluated, the second reproducing agent, the commit hash used for reproduction, and
the final verdict after SEM evaluation. Mark any verdict that lacks mechanism citation,
reproduction, or per-arm evaluation as FAIL.`

### Historical fixture matrix (escape corpus)

Eight read-only fixtures keep the four escape classes covered. Run each against
its gate and record the observed result in the QA receipt. They are regression
fixtures, not claims about any live artifact; the fixture files live outside this
repository, so this matrix carries the IDs and the expected verdicts only.

| fixture ID | gate | expected | why |
|---|---|---|---|
| `F-CLM-114364-known` | PQA-CLM | FAIL | a `known` defect claim with no claim-specific public issue/PR URL |
| `F-CLM-114364-unfiled-hindsight` | PQA-CLM | FAIL in certainty form; PASS after scoped observed-in-testing wording or a verified public tracker link | an unfiled observation written as a real provider defect |
| `F-DOL-114364-redundant-pair` | PQA-DOL | FAIL | the secondary repeats the primary's framing, mechanism, numbers, defect, questions, and follow-ups, and the overlap is fact-correct |
| `F-DOL-114364-trim-pass-shape` | PQA-DOL | PASS | the primary already carries the defect; the secondary keeps only the pointer, the ask, and new material |
| `F-STAND-114364-addressed` | PQA-STAND | FAIL | second-person substantive wording: as an issue body it fails unconditionally, as a comment only a recorded one-line handle may remain |
| `F-STAND-114364-body-pass` | PQA-STAND | PASS | a neutral standalone body; the new gate must not reject it |
| `F-SEM-114364-flatlist-shape` | PQA-SEM | FAIL | verdict cites only the flat list with duplicate keys `api_key`, `api_url` and no per-mode evaluation or mechanism citation |
| `F-SEM-114364-arm-evaluated` | PQA-SEM | PASS | verdict shows per-mode effective keys unique (cloud: 32/32, local_external: 32/32, local_embedded: 36/36), mechanism `__init__.py:414-459` cited, independent agent reproduction recorded, verdict reclassified as non-defect |

### Acceptance tests

| test | requirement |
|---|---|
| AT-1 | `F-CLM-114364-known` fails PQA-CLM because `known provider defect` has no claim-specific public issue/PR URL. |
| AT-2 | `F-CLM-114364-unfiled-hindsight` fails in certainty form and passes only after scoped observed-in-testing wording or a verified public tracker link. |
| AT-3 | `F-DOL-114364-redundant-pair` fails PQA-DOL despite clean fact overlap. |
| AT-4 | The trimmed-comment shape in `F-DOL-114364-trim-pass-shape` passes PQA-DOL when the body already carries the defect and the comment contains only pointer, ask, and new material. |
| AT-5 | `F-STAND-114364-addressed` fails when treated as an issue body; as a comment, only an explicitly required one-line handle may remain, and its second-person substantive wording fails. |
| AT-6 | `F-STAND-114364-body-pass` passes PQA-STAND and stays neutral. |
| AT-8 | A claim with an internal receipt but no scope wording and no public issue/PR ref fails. |
| AT-9 | A comment that repeats a body number or mechanism fails PQA-DOL even when its evidence row points at the same receipt. |
| AT-10 | Removing an allowed comment handle leaves the claim and the ask interpretable; otherwise PQA-STAND fails. |
| AT-11 | Each public artifact receives a second-member proofread/fact-audit record before the lane stop condition can pass. |
| AT-12 | A CONFIRMED verdict citing only the flat surface shape (duplicate keys `api_key`, `api_url`) without mechanism citation fails SEM-1 and cannot be labeled a known defect. |
| AT-13 | A CONFIRMED verdict observing duplicated declarations without per-arm/per-context effective-key evaluation fails SEM-3 and cannot be labeled a known defect. |
| AT-14 | A CONFIRMED verdict without the second-agent source-reproduction row (commit, agent name, reproduction result) fails SEM-2 and cannot be labeled a known defect. |
| AT-15 | A verdict that re-evaluates the arms and finds no effective defect must be reclassified as an observation or linked to a tracker; it cannot be published as CONFIRMED known defect. |

AT-7 is a lane-admission requirement, not a checklist rule: it lives in the
handoff brief fields below.

### Lane fields these gates read

The lane brief supplies the inputs; the canonical field definitions live in the
handoff brief template (`choreography/orchestration.md`, section 11). A brief
that omits any of them is incomplete and cannot enter public-writing QA:
`public_surfaces`; `claim_register`; `artifact_pair`; `standalone_policy`;
`qa_fixture_set`; `handoff_stop_condition` — the last meaning all four gates
PASS with the second-member proofread and fact audit recorded. PQA-SEM reads the
same claim-register inputs as the other three gates; it adds no new lane fields. A lane producing
no public text records `public_surface: none`. This checklist names the inputs
and never redefines them; the lane template names them and never restates these
gate conditions.

## Guarded review/repair (proposal-only, approval-gated)

Review output and GitHub mutation are two roles; keep them apart. This is the
kit's guarded review/repair contract (`choreography/review-repair-workflow.md`);
validate a report with `python3 build/review-repair/check.py <report.json>`.

- **A review proposes; it does not mutate.** Your report lists findings and
  *proposed* maintainer actions (a comment, a label, a close). It never carries
  a mutation it already performed. A report that shows `close`/`label`/`comment`
  as done has blended reviewer and actor — the self-approval failure in another
  costume (see section 6).
- **Bind every step to the LIVE head.** Name the exact head each step was
  verified against (`gh api repos/O/R/commits/<ref> --jq .sha`), its source
  evidence, its owner, and its rollback path. A step bound to a different head
  is a stale review, not a review (see section 1). Release steps are steps too:
  the readback that proves the served artifact names a live target and a
  rollback.
- **Every proposed mutation is approval-required.** A proposed mutation is never
  automatic and always names its rollback. An agent report may not propose a
  merge (no automatic merge authority), may not propose a rename, and may not
  introduce a slash-command name.
- **Every repair carries a regression-test contract.** State the test and BOTH
  results: it FAILS before the fix and PASSES after. A test that passes on both
  sides is a guard, not a pin (see `code-review-verification`). The loop is
  bounded — it stops and hands back to the operator.
- **The review-to-ship handoff carries the evidence forward.** A reviewer that
  signs off cites the same head, evidence, and open findings the ship step will
  re-check; do not let the release step re-derive a different story.

## Offering a policy choice

When a fix has two defensible policies and the maintainer should pick one, ship
both as independent commits on one branch rather than asking first. One review
thread, no second branch to rebase, and their pick is a single revert instead of
a request for you to redo the work.

- Commit 1 is the base fix; commit 2 swaps in the alternative, so HEAD carries
the alternative and one revert returns the base.
- In the body, say what each does, which is HEAD, and that a revert switches
policies. Name the trade-off in one line each (what is lost, what is paid).
- Keep both commits green on their own. A commit that only passes on top of the
  other is not a choice.
- Keep the title neutral about which commit is HEAD. A title lifted from one
  commit's subject (or a checkmark on one policy) reads as the recommendation you
  were trying not to make. Name the shared outcome — "no card renders without a
  title" — and let the body say what each policy does.

## Keep the public text short

Reviewers pay for every word. The audit work is verbose; the PR text is not.

- **Plain-language floor applies to PR/issue text.** If the repo's audience is
  not all-native-English or not all-steeped-in-the-project, the PR title, body
  and comments follow the same bar as a README: say what the change does in the
  first lines, no jargon when a plain word exists, one idea per sentence, no
  invented hyphen compounds. A reviewer who cannot parse the body will not parse
  the diff either.
- **PR body: one screen.** What it does, why it matters, repro, one test line, the
  checklist. Cut the reasoning that the diff and tests already show.
- **Comments: a few lines.** State what changed and anything a reviewer must know to
  judge it. Do not restate the body or narrate the investigation.
- **Superseded comments get deleted, not stacked.** Self-correcting in a new comment
  leaves a stale claim in the thread; edit or delete it and post one current comment
  (the user reads the whole thread cost first).
- **Cut prose, never the template.** Condensing a PR body means trimming narrative,
  restated evidence and hedging — keep the repo's template sections in their order, every
  checklist box, the code fences and the links. A short body that no longer matches
  `pull_request_template.md` reads as sloppiness, not concision.
- **Only condense where nobody has engaged.** Editing the description of a PR or issue that
  already has comments or reviews makes contributors re-read text they had already judged
  (and looks like rewriting history under discussion). Zero third-party comments/reviews is
  the bar; leave the rest alone.
- **Check where a long explanation lands before parking it.** A code comment or commit
  body is read only by someone already in that file or history — but "in that file" is not
  automatically cheap: a file that is `@embedFile`'d into a binary, or written to disk by an
  installer, ships its comments to every installation. Grep the ship path first, then match
  the neighbouring comments' length (2-3 lines is the usual register) and keep only the why.
- **Measure the prose share of an asset diff.** Count added comment bytes against total
  added bytes; a file grown mostly by prose is a review liability and a per-install
  footprint at once. Trim to the why and let the tests carry the rest.
- **Match the maintainer's real register for commit bodies.** Sample their recent commits
  (`gh api repos/O/R/commits?author=X`) and count non-blank body lines instead of guessing;
  a body several times the house median reads as a diary. Keep root cause plus a pointer to
  the proof, leave raw test output in the PR body where a reviewer looks for it, and keep
  the subject on one line.

## Pitfalls
- **A scanner that only sees the diff is not a scanner.** A repo gate that
  enumerates via `git add -A -n` (or `git status`) lists only index-relative
  changes — on a clean checkout it scans **zero files** and prints PASS. Prove a
  gate enumerated something before trusting its PASS: in a throwaway clone run
  `git read-tree --empty`, then re-run it. The first PASS on a pristine clone is
  usually vacuous; the real failure appears only once a file is modified.
- **Count the terms a scan loaded, not the ones you assume.** A term/denylist
  built from environment or a gitignored config is empty in your checkout, so one
  scan can miss most names actually present. Check the inventory size, and use a
  direct `grep` per known name to get the true exposure count before reporting
  either a leak or a clean pass.
- **A pre-existing gate failure is still a merge gate.** If a branch's
  public-safety scan also fails on `main`, reproduce it in a `main` worktree and
  report it as a blocker with an owner decision — never silently edit a deliberate
  authored artifact (branding copy, published names) just to force green.
- **Review comments are claims, not results.** When an automated/peer review flags
  your PR, reproduce the finding against the PR HEAD in a throwaway worktree
  (`git worktree add /tmp/prN <sha>`) before replying: the substance can be right
  while the detail is wrong (a bot claimed PyYAML folds `y`/`n` to bools — it does
  not; they resolve as strings). Then run the PR body's OWN "how to test" steps —
  a body that documents a repro which doesn't reproduce is worse than no repro,
  because the next reviewer runs it. Best reply = confirm what's real, correct the
  wrong detail, add the case the comment missed, and name what is deliberately out
  of scope.
- **Check for an adjacent instance of the same bug class the comment missed.** A
  guard keyed on a parsed type silently ignores the same value written in another
  form (e.g. a `isinstance(value, bool)` gate misses the quoted STRING `'false'`
  that the CLI itself writes for string-typed defaults). Probe the neighbouring
  writer/entry point, not just the reported token.
- **Read the consumer's precedence before judging a fallback's policy.** When a PR
  adds a fallback value to a payload field, the component that READS the field may
  prefer it over a different fallback it already applies further down, so the new
  value displaces a better existing label/behaviour — and the variant the body calls
  the "safer default" can be the one that loses information. Grep the field to its
  read site and name which source wins the `orelse`/`??`/`||` chain. Live user data
  is the tiebreak: the artefact on the author's own machine showed the displaced
  value in use while the prose claimed otherwise.
- **A new test can pass with the change deleted — test the trigger, not the tick.**
  Attribute each new case individually. If an earlier fallback short-circuits the
  condition the case is meant to exercise, its assertion is vacuous (delete the new
  clause and it still passes). Build the input only the new branch can decide (the
  unreadable/keyless case, not the readable one an existing fallback already covers)
  and confirm that case goes red without the code.
- **Intent comes from the repo's own user-facing surfaces, not from inference.** To
  settle "is this behaviour a bug or intended", quote the maintainers' own artefacts:
  a settings label, a documented model, the framing of the linked issue. A defect-filed
  issue plus a merged guard on the same class settles it; a behaviour the author merely
  likes is a fork concern, not a reason to re-open PR scope.
- **Detector/linter additions must be idempotent and meaning-preserving.** For any
  check that rewrites config on `--fix`: run it twice and assert the second pass
  reports and rewrites nothing (a guard that re-fires every run is worse than no
  check), and pin that the rewrite never changes the resolved runtime behavior.
  Prefer the value the runtime already resolves to over "the sane default" — the
  fix's job is to make an existing state legible, not to choose for the user.
- **Flag resolver-side accidents instead of cementing them.** When a legacy value
  only resolves the way it does through an accident (e.g. a blank/null value
  stringified to `"none"` and caught by an alias map), the surface fix should name
  it and preserve behavior, and the PR/comment should hand the underlying quirk to
  the resolver's owners as its own item.
- **A text search for a key's value is wrong in both directions — read the parsed node.**
  Detection that greps a file for the value while reading the effective value from a
  dotted key will report a documented value as drift when a decoy line exists
  elsewhere (another section, a block scalar, a duplicate block), AND miss the shapes
  a value really takes: flow style, a quoted key, an anchored `*alias`, and a
  duplicate block whose last entry wins. `yaml.compose()` + walking to the key's own
  node gives the scalar as written (quoted vs plain, `off` vs `false`) with no
  false-positive surface. Write the test table with both classes: decoys that must
  stay silent, and shapes that must be caught.
- **A repo's self-test that clones HEAD tests the last COMMIT, not your working tree.**
  A `fresh-clone-test.sh`-style gate (`git clone <repo> <tmp>` internally) silently
  re-verifies the previous commit while your new edits sit uncommitted — it passes, and
  proves nothing about the change you are about to push. Commit first, then re-run the
  gate, and check the gate's own printed SHA equals your new HEAD.
- **A fresh `git clone` lands on the DEFAULT branch, not the PR.** `git clone` then
  `git diff origin/main...origin/pr` audits correctly, but running the repo's gates in
  that working tree runs them against `main` — and they PASS, so nothing looks wrong.
  Fetch `refs/pull/N/head`, `git checkout --detach <head-sha>`, assert
  `git rev-parse HEAD` equals the audited head, and only then run the gates. Re-run after
  any such slip and say so; a green suite on the wrong tree is a fabricated result.
- **Merging is not publishing.** Before claiming a site or deploy update, prove a deployer
  exists: a CI workflow, a git-linked hosting project (a Vercel `link: null` plus deployments
  carrying no commit sha = manual CLI uploads only), or hosting enabled (`GET /repos/O/R/pages`
  → 404 = disabled). A merged docs PR with no linked deployer changes zero served bytes.
- **Credentials + a found project do not authorise a production write.** Knowing where the
  site lives and holding a valid token is not a documented deployment path. When no repo,
  KB or runbook defines the artifact set and the deploy would publish more than the audited
  diff, report "merged, site pending external deployment" and hand the user the decision
  instead of inventing a deploy — and never let a merge imply a live change.
- **Stale handoff diff** → you review phantom code. Always re-diff live.
- **Trusting PR-body test counts** → false evidence a reviewer catches. Run it.
- **`gh pr diff` needs `--repo O/R`** when not inside a cloned repo context.
- **`gh pr review --approve` self-block** → use a comment, never a fake approve.
- **`python` missing from PATH** → use `./venv/bin/python` or `uv run`.
- **Unqualified test IDs** → class-qualify them (`TestClass::test_method`).
- **Editing a PR body you don't own** → only do it on your own account's PRs.
- **Prove red on the real base, not in prose.** Do not assert the old behaviour
  in the body. Swap the base version of the touched file into the working tree
  (`git show origin/main:<path> > <path>`), run the new tests, restore, and quote
  the exact failure. A test that never failed against the base can pass for the
  wrong reason, and a reviewer who runs it will find out.
- **Do not claim an unverified half.** When the repo's toolchain is missing
  locally (no zig, no rust, no pnpm), fix and test the surface you can execute
  and say in the body which surface you could not build. Never let a green local
  run imply the unbuilt half passes; drop it from the diff or flag it plainly.
- **Verify which artifact carries a cost before acting on it — or dismissing it.** "This
  ships with every install" is a claim about one specific surface: git metadata, an
  embedded/installed file, or reviewer attention. Measure the mechanism before agreeing or
  pushing back (grep how the file reaches the user, size the delta) and name the surface
  that pays. The fix often lands in a different artifact than the claim names — and when the
  named surface is right, the delta can still be too small to matter (hundreds of bytes in a
  multi-MB binary). Argue from the measurement, not from the instinct.
- **Writing into a live install: verify both ends by hash, and quote the restore path from
  a listing you read.** Prove the backup equals the pre-change source and the installed file
  equals the new source (`shasum` on both sides, `git show ref:path | shasum` as the
  reference), then state the rollback command from the real filenames — tooling flattens or
  renames copies (`_Users_name_.hermes_plugins_x___init__.py`), so a path you assembled from
  memory does not exist. An unverified restore instruction is worse than none, because it is
  followed at the worst moment.

## When a docs pass is the actual task

Sometimes the request is not "audit this PR" but "this text confused a reader,
fix the writing". The audit discipline still applies, scoped down:

- Verify the served/repo text live (API or curl), not a cached copy. Baseline
  the SHA before editing; read the result back from the API after pushing — a
  push that reports success but changes no served bytes is a failed push.
- Edit on a branch even for docs-only changes; commit with a message naming the
  pass (`docs: rewrite README in plain language`), not a vague `docs update`.
- Enumerate the reader-facing surfaces before editing: README, repo About line
  (`gh repo view --json description`), site HTML (often `index.html` in the repo
  root, served from the same repo), landing-page meta description. One branch,
  one PR, all surfaces — so the reviewer sees the whole pass in one thread.
- Copy in place when the asset lives in the same repo: a site rewrite is a
  normal file edit, no new repo or deploy step. Verify what is actually served
  with a cache-busted fetch before and after.
- Structure is not copy: in a page rewrite touch only text nodes, `title`,
  `meta description`, `og:title`. CSS classes, ids, anchors, asset references
  and the nav stay byte-identical or rendering breaks. Verify: HTML parses, all
  `#anchor` links resolve to existing ids, local serve returns 200 for the page
  and each referenced asset.
- Specific method names (Erlang/OTP, YAML, Apache-2.0) stay — introduced with
  one plain sentence each, not stripped.
- If the text sits in an open PR thread a human already judged, the
  only-condense-where-nobody-has-engaged rule applies to it too.

## References
- `references/verification-recipe.md` — copy-paste command sequence for a full
  pre-merge audit (live diff, main premise check, venv test run, body-claim
  verification, comment posting).
