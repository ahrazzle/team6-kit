#!/usr/bin/env python3
"""
check.py — Guarded review / repair workflow validator.

A dependency-free checker for the guarded review/repair workflow contract
(see choreography/review-repair-workflow.md). Given one review report — from a
code review, an adversarial pass, a browser verification, or an artifact
verification — it decides whether the report is a valid, proposal-only review
report: bound to a live target head, evidencing every step, naming an owner and
a rollback for every step, keeping proposed mutations separate from the review
output and approval-required, and carrying a regression-test contract with the
pre-fix / post-fix distinction for every repair.

It is a CONTRACT CHECKER, not a runtime gate. Running it performs no network
call, spawns no process, edits no file, opens no pull request, and holds no
merge authority. Standard library only. The Team6 Kanban board remains
authoritative; the report is a derived review record, not a second state store.

USAGE
  python3 check.py --selftest                 # run the in-process self-test
  python3 check.py --fixtures                 # assert the fixture corpus
  python3 check.py <report.json> [...]        # validate one or more reports
  python3 check.py --quiet <report.json>      # errors only

EXIT
  0 = every input is a valid proposal-only report (or self-test / fixtures pass)
  1 = at least one input is invalid, unreadable, or not valid JSON (fail closed)

FAIL-CLOSED RULES (a single violation fails the whole report):
  R1  a required field is missing, empty, or of the wrong kind   -> REQUIRED_FIELD
  R2  the target head is not a commit sha, its source is not
      stated, or a step is bound to a different head              -> HEAD_BINDING
  R3  a step carries no evidence ref, or ref/proves is empty     -> EVIDENCE
  R4  a step or a repair names no owner                          -> OWNER
  R5  a step or a proposed mutation names no rollback path       -> ROLLBACK
  R6  the review output reports a performed mutation             -> PROPOSAL_ONLY
  R7  a proposed mutation is not approval-required, or its kind
      is merge / rename / a command name                         -> MUTATION_APPROVAL
  R8  a repair has no regression-test contract, or its pre/post
      results are not fail / pass                                -> REGRESSION_CONTRACT
  R9  an internal local path or a credential-like value appears  -> REDACTION
  R10 an unknown top-level field appears (typo'd fields fail)    -> UNKNOWN_FIELD
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Contract shape
# ---------------------------------------------------------------------------
REQUIRED_FIELDS = (
    ("contract_version", (int,)),
    ("lane", (str,)),
    ("target", (dict,)),
    ("steps", (list,)),
    ("review_output", (dict,)),
    ("proposed_mutations", (list,)),
    ("repairs", (list,)),
)
KNOWN_FIELDS = {name for name, _ in REQUIRED_FIELDS}

LANES = {"review", "adversarial", "browser", "artifact"}
VERDICTS = {"accept", "changes-requested", "blocked"}

# Mutation kinds the report MAY propose. Everything else is rejected: `merge`
# would smuggle automatic merge authority, `rename` is a forbidden surface
# rename, and a command kind would introduce a duplicate slash-command name.
ALLOWED_MUTATION_KINDS = {
    "comment", "label", "close", "reopen", "push-commit", "open-pr",
    "request-review",
}
FORBIDDEN_MUTATION_KINDS = {"merge", "rename", "command", "add-command",
                            "slash-command"}

# A commit sha as GitHub reports it: 7-40 hex characters.
HEAD_SHA_RE = re.compile(r"^[0-9a-fA-F]{7,40}$")

# Internal local path shapes. Built from parts so this validator's own source
# never carries a contiguous absolute home-path literal.
_ABS_ROOT = "/" + "Users" + "/"
_HOME_ROOT = "/" + "home" + "/"
_VAR_ROOT = "/" + "var" + "/" + "folders" + "/"
_INTERNAL_PROFILE_DIR = "." + "hermes" + "/" + "profiles" + "/"
_INTERNAL_PATH_PATTERNS = [
    re.compile(_ABS_ROOT + r"[A-Za-z0-9_.-]+/"),
    re.compile(_HOME_ROOT + r"[A-Za-z0-9_.-]+/"),
    re.compile(_VAR_ROOT),
    re.compile(re.escape(_INTERNAL_PROFILE_DIR)),
    re.compile(r"\b" + "profiles" + r"/[A-Za-z0-9_.-]+/"),
    re.compile(r"[A-Za-z]:\\" + "Users" + r"\\\\", re.I),
]

# Credential-like value shapes. Names are allowed; values never are.
SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9]{8,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._-]{12,}"),
    re.compile(r"(?i)\b(password|passwd|secret|api[_-]?key|access[_-]?token)"
               r"\s*[:=]\s*\S+"),
]


class Violation:
    def __init__(self, rule, path, message):
        self.rule = rule
        self.path = path
        self.message = message

    def __str__(self):
        where = f" at {self.path}" if self.path else ""
        return f"{self.rule}{where}: {self.message}"


def _fail(violations, rule, path, message):
    violations.append(Violation(rule, path, message))


def _nonempty_str(value):
    return isinstance(value, str) and bool(value.strip())


def _walk_strings(node, path=""):
    """Yield (value, dotted_path) for every string value, recursively."""
    if isinstance(node, dict):
        for key, value in node.items():
            child = f"{path}.{key}" if path else str(key)
            if isinstance(key, str):
                yield key, f"{child} (key)"
            yield from _walk_strings(value, child)
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from _walk_strings(value, f"{path}[{i}]")
    elif isinstance(node, str):
        yield node, path


def validate(doc):
    """Return a list of Violation for one report document."""
    v = []

    if not isinstance(doc, dict):
        _fail(v, "R1", "", "report must be a JSON object")
        return v

    # --- R1: required fields present and of the right kind ---------------
    for field, kinds in REQUIRED_FIELDS:
        if field not in doc:
            _fail(v, "R1", field, "required field missing")
        elif not isinstance(doc[field], kinds):
            names = "/".join(k.__name__ for k in kinds)
            _fail(v, "R1", field,
                  f"required field must be {names}, "
                  f"got {type(doc[field]).__name__}")

    # --- R10: no unknown top-level field (typos fail loudly) -------------
    for key in sorted(set(doc) - KNOWN_FIELDS):
        _fail(v, "R10", key,
              "unknown top-level field; a typo'd field must fail, not be "
              "ignored")

    # --- lane must be one of the four review lanes -----------------------
    lane = doc.get("lane")
    if isinstance(lane, str) and lane not in LANES:
        _fail(v, "R1", "lane", f"lane must be one of {sorted(LANES)}")

    # --- R2: head binding (target + every step) --------------------------
    head = None
    target = doc.get("target")
    if isinstance(target, dict):
        raw_head = target.get("live_head")
        head_text = raw_head.strip() if isinstance(raw_head, str) else ""
        if not head_text:
            _fail(v, "R2", "target.live_head",
                  "the live target head must be stated")
        elif not HEAD_SHA_RE.match(head_text):
            _fail(v, "R2", "target.live_head",
                  "the live target head must be a commit sha (7-40 hex)")
        else:
            head = head_text.lower()
        if not _nonempty_str(target.get("head_source")):
            _fail(v, "R2", "target.head_source",
                  "state how the live head was read (the command or API that "
                  "produced it)")
        if not _nonempty_str(target.get("repo")):
            _fail(v, "R1", "target.repo", "the target repository must be named")

    steps = doc.get("steps")
    if isinstance(steps, list):
        if not steps:
            _fail(v, "R2", "steps",
                  "a review report must carry at least one step")
        for i, step in enumerate(steps):
            p = f"steps[{i}]"
            if not isinstance(step, dict):
                _fail(v, "R2", p, "step must be an object")
                continue
            if not _nonempty_str(step.get("id")):
                _fail(v, "R1", f"{p}.id", "step must have an id")
            if not _nonempty_str(step.get("action")):
                _fail(v, "R1", f"{p}.action", "step must state its action")
            step_head = step.get("head")
            step_head_text = (step_head.strip().lower()
                              if isinstance(step_head, str) else "")
            if not step_head_text:
                _fail(v, "R2", f"{p}.head",
                      "every step must name the live head it was verified "
                      "against")
            elif head is not None and step_head_text != head:
                _fail(v, "R2", f"{p}.head",
                      "step head does not match the target live head — a stale "
                      "review, not a review")

            # --- R3: evidence -------------------------------------------
            ev = step.get("evidence")
            if not isinstance(ev, list) or not ev:
                _fail(v, "R3", f"{p}.evidence",
                      "every step must carry at least one evidence ref")
            else:
                for j, entry in enumerate(ev):
                    ep = f"{p}.evidence[{j}]"
                    if not isinstance(entry, dict):
                        _fail(v, "R3", ep, "evidence entry must be an object")
                        continue
                    if not _nonempty_str(entry.get("ref")):
                        _fail(v, "R3", f"{ep}.ref",
                              "evidence must name the ref (command or artifact) "
                              "that produced it")
                    if not _nonempty_str(entry.get("proves")):
                        _fail(v, "R3", f"{ep}.proves",
                              "evidence must state what it proves")

            # --- R4: owner ----------------------------------------------
            if not _nonempty_str(step.get("owner")):
                _fail(v, "R4", f"{p}.owner",
                      "every step must name its owner")

            # --- R5: rollback -------------------------------------------
            if not _nonempty_str(step.get("rollback")):
                _fail(v, "R5", f"{p}.rollback",
                      "every step must name its rollback path")

    # --- review_output: verdict + proposal-only -------------------------
    ro = doc.get("review_output")
    if isinstance(ro, dict):
        verdict = ro.get("verdict")
        if not _nonempty_str(verdict):
            _fail(v, "R1", "review_output.verdict",
                  "the review output must state its verdict")
        elif verdict not in VERDICTS:
            _fail(v, "R1", "review_output.verdict",
                  f"verdict must be one of {sorted(VERDICTS)}")
        if not isinstance(ro.get("findings"), list):
            _fail(v, "R1", "review_output.findings",
                  "findings must be an explicit list (use [] for none)")
        # --- R6: proposal-only ------------------------------------------
        performed = ro.get("mutations_performed")
        if not isinstance(performed, list):
            _fail(v, "R6", "review_output.mutations_performed",
                  "the review output must declare mutations_performed as an "
                  "explicit list (use [] — a review proposes, it does not "
                  "mutate)")
        elif performed:
            _fail(v, "R6", "review_output.mutations_performed",
                  "the review output reports a performed mutation; review "
                  "output is proposal-only — mutations belong in "
                  "proposed_mutations and require approval")

    # --- R7: proposed mutations are approval-required and allowed -------
    muts = doc.get("proposed_mutations")
    if isinstance(muts, list):
        for i, mut in enumerate(muts):
            p = f"proposed_mutations[{i}]"
            if not isinstance(mut, dict):
                _fail(v, "R7", p, "proposed mutation must be an object")
                continue
            if not _nonempty_str(mut.get("id")):
                _fail(v, "R1", f"{p}.id", "proposed mutation must have an id")
            kind = mut.get("kind")
            if not _nonempty_str(kind):
                _fail(v, "R7", f"{p}.kind", "proposed mutation must name a kind")
            elif kind in FORBIDDEN_MUTATION_KINDS:
                if kind == "merge":
                    _fail(v, "R7", f"{p}.kind",
                          "a merge may not be proposed by an agent report — no "
                          "automatic merge authority")
                elif kind == "rename":
                    _fail(v, "R7", f"{p}.kind",
                          "a rename is forbidden — no Team6 or Protean surface "
                          "is renamed")
                else:
                    _fail(v, "R7", f"{p}.kind",
                          f"mutation kind '{kind}' would introduce a "
                          "slash-command name — no duplicate command names")
            elif kind not in ALLOWED_MUTATION_KINDS:
                _fail(v, "R7", f"{p}.kind",
                      f"unknown mutation kind '{kind}'; allowed: "
                      f"{sorted(ALLOWED_MUTATION_KINDS)}")
            if mut.get("requires_approval") is not True:
                _fail(v, "R7", f"{p}.requires_approval",
                      "every proposed mutation must set requires_approval: "
                      "true — a proposed mutation is never automatic")
            if not _nonempty_str(mut.get("target")):
                _fail(v, "R1", f"{p}.target",
                      "proposed mutation must name its target")
            # --- R5: rollback -------------------------------------------
            if not _nonempty_str(mut.get("rollback")):
                _fail(v, "R5", f"{p}.rollback",
                      "every proposed mutation must name its rollback path")

    # --- R8: regression-test contract on every repair -------------------
    repairs = doc.get("repairs")
    if isinstance(repairs, list):
        for i, repair in enumerate(repairs):
            p = f"repairs[{i}]"
            if not isinstance(repair, dict):
                _fail(v, "R8", p, "repair must be an object")
                continue
            if not _nonempty_str(repair.get("id")):
                _fail(v, "R1", f"{p}.id", "repair must have an id")
            if not _nonempty_str(repair.get("finding")):
                _fail(v, "R8", f"{p}.finding",
                      "every repair must name the finding it fixes")
            # --- R4: owner ----------------------------------------------
            if not _nonempty_str(repair.get("owner")):
                _fail(v, "R4", f"{p}.owner", "every repair must name its owner")
            rt = repair.get("regression_test")
            if not isinstance(rt, dict):
                _fail(v, "R8", f"{p}.regression_test",
                      "every repair must carry a regression-test contract")
                continue
            if not _nonempty_str(rt.get("name")):
                _fail(v, "R8", f"{p}.regression_test.name",
                      "the regression test must be named")
            if not _nonempty_str(rt.get("command")):
                _fail(v, "R8", f"{p}.regression_test.command",
                      "the regression test must name its command")
            pre, post = rt.get("pre_fix_result"), rt.get("post_fix_result")
            if pre != "fail":
                _fail(v, "R8", f"{p}.regression_test.pre_fix_result",
                      "pre_fix_result must be 'fail' — a test that passes "
                      "before the fix pins nothing")
            if post != "pass":
                _fail(v, "R8", f"{p}.regression_test.post_fix_result",
                      "post_fix_result must be 'pass'")

    # --- R9: no internal path or credential value anywhere --------------
    seen_internal = False
    seen_secret = False
    for value, path in _walk_strings(doc):
        if not seen_internal and any(rx.search(value)
                                     for rx in _INTERNAL_PATH_PATTERNS):
            _fail(v, "R9", path,
                  "an internal local path or profile path appears; replace it "
                  "with a repository-relative path")
            seen_internal = True
        if not seen_secret and any(rx.search(value) for rx in SECRET_PATTERNS):
            _fail(v, "R9", path,
                  "a credential-like value appears; credential names are "
                  "allowed, values are not")
            seen_secret = True

    return v


def load(path):
    """Load one report document. Returns (doc, error_or_None)."""
    if not os.path.isfile(path):
        return None, f"not found: {path}"
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        return None, f"unreadable: {exc}"
    try:
        return json.loads(text), None
    except ValueError as exc:
        return None, f"not valid JSON: {exc}"


def run_file(path, quiet=False):
    doc, err = load(path)
    print(f"== {path}")
    if err is not None:
        print(f"  FAIL  {err}")
        return 1
    violations = validate(doc)
    if violations:
        print(f"  FAIL  {len(violations)} violation(s):")
        for violation in violations:
            print(f"    - {violation}")
        return 1
    if not quiet:
        print("  OK    proposal-only report bound to the live head "
              "(owner, evidence, rollback, regression contract present)")
    return 0


# ---------------------------------------------------------------------------
# A valid report of each lane, exercised in-process by the self-test.
# ---------------------------------------------------------------------------
HEAD = "a1b2c3d4e5f60718293a4b5c6d7e8f9012345678"


def _valid_report(lane):
    return {
        "contract_version": 1,
        "lane": lane,
        "target": {
            "repo": "ahrazzle/team6-kit",
            "live_head": HEAD,
            "head_source": "gh api repos/ahrazzle/team6-kit/commits/main "
                           "--jq .sha",
        },
        "steps": [
            {
                "id": "read-live-head",
                "action": "read the live target head",
                "head": HEAD,
                "evidence": [
                    {"ref": "gh api ... --jq .sha",
                     "proves": "the head the review is bound to"},
                ],
                "owner": "reviewer-profile",
                "rollback": "read-only step; nothing to roll back",
            },
            {
                "id": "prod-readback",
                "action": "release readback: confirm the served artifact",
                "head": HEAD,
                "evidence": [
                    {"ref": "curl -sI <url>",
                     "proves": "the served surface matches the reviewed head"},
                ],
                "owner": "release-owner-profile",
                "rollback": "revert to the previous release artifact",
            },
        ],
        "review_output": {
            "verdict": "changes-requested",
            "findings": [
                {"id": "F1", "severity": "high",
                 "summary": "the guard swallows the quoted-string case"},
            ],
            "mutations_performed": [],
        },
        "proposed_mutations": [
            {
                "id": "M1",
                "kind": "comment",
                "target": "ahrazzle/team6-kit#123",
                "requires_approval": True,
                "approved_by": None,
                "rollback": "delete the review comment",
            },
        ],
        "repairs": [
            {
                "id": "P1",
                "finding": "F1",
                "owner": "implementer-profile",
                "regression_test": {
                    "name": "quoted-string guard case",
                    "command": "python3 -m pytest tests/test_guard.py -q",
                    "pre_fix_result": "fail",
                    "post_fix_result": "pass",
                },
            },
        ],
    }


def _copy(doc):
    return json.loads(json.dumps(doc))


def _drop_error(violations, rule):
    return any(x.rule == rule for x in violations)


def selftest():
    cases = []

    for lane in sorted(LANES):
        cases.append((f"valid/{lane}-lane", _valid_report(lane), True, None))

    # A report with no repairs and no proposed mutations is still valid — the
    # review found nothing to fix.
    clean = _valid_report("review")
    clean["review_output"]["verdict"] = "accept"
    clean["review_output"]["findings"] = []
    clean["proposed_mutations"] = []
    clean["repairs"] = []
    cases.append(("valid/clean-approve", clean, True, None))

    bad = _valid_report("review")
    del bad["target"]
    cases.append(("invalid/missing-required-field", bad, False, "R1"))

    bad = _valid_report("review")
    bad["lane"] = "opinion"
    cases.append(("invalid/bad-lane", bad, False, "R1"))

    bad = _valid_report("review")
    bad["unknown_extra"] = "value"
    cases.append(("invalid/unknown-field", bad, False, "R10"))

    bad = _valid_report("review")
    bad["target"]["live_head"] = "main"
    cases.append(("invalid/head-not-a-sha", bad, False, "R2"))

    bad = _valid_report("review")
    bad["target"]["head_source"] = "   "
    cases.append(("invalid/head-source-empty", bad, False, "R2"))

    bad = _valid_report("review")
    bad["steps"][0]["head"] = "f" * 40
    cases.append(("invalid/stale-step-head", bad, False, "R2"))

    bad = _valid_report("review")
    bad["steps"][0]["evidence"] = []
    cases.append(("invalid/no-evidence", bad, False, "R3"))

    bad = _valid_report("review")
    bad["steps"][0]["evidence"] = [{"ref": "cmd"}]
    cases.append(("invalid/evidence-no-proves", bad, False, "R3"))

    bad = _valid_report("review")
    bad["steps"][0]["owner"] = ""
    cases.append(("invalid/step-no-owner", bad, False, "R4"))

    bad = _valid_report("review")
    bad["steps"][0]["rollback"] = ""
    cases.append(("invalid/step-no-rollback", bad, False, "R5"))

    bad = _valid_report("review")
    bad["proposed_mutations"][0]["rollback"] = ""
    cases.append(("invalid/mutation-no-rollback", bad, False, "R5"))

    bad = _valid_report("review")
    bad["review_output"]["mutations_performed"] = [
        {"kind": "close", "target": "ahrazzle/team6-kit#123"}]
    cases.append(("invalid/mutation-in-review-output", bad, False, "R6"))

    bad = _valid_report("review")
    bad["proposed_mutations"][0]["requires_approval"] = False
    cases.append(("invalid/mutation-not-approved", bad, False, "R7"))

    bad = _valid_report("review")
    bad["proposed_mutations"][0]["kind"] = "merge"
    cases.append(("invalid/auto-merge", bad, False, "R7"))

    bad = _valid_report("review")
    bad["proposed_mutations"][0]["kind"] = "rename"
    cases.append(("invalid/rename", bad, False, "R7"))

    bad = _valid_report("review")
    bad["proposed_mutations"][0]["kind"] = "command"
    cases.append(("invalid/duplicate-command", bad, False, "R7"))

    bad = _valid_report("review")
    del bad["repairs"][0]["regression_test"]
    cases.append(("invalid/repair-no-regression", bad, False, "R8"))

    bad = _valid_report("review")
    bad["repairs"][0]["regression_test"]["pre_fix_result"] = "pass"
    cases.append(("invalid/pre-fix-passed", bad, False, "R8"))

    bad = _valid_report("review")
    bad["repairs"][0]["regression_test"]["post_fix_result"] = "fail"
    cases.append(("invalid/post-fix-failed", bad, False, "R8"))

    bad = _valid_report("review")
    bad["repairs"][0]["owner"] = ""
    cases.append(("invalid/repair-no-owner", bad, False, "R4"))

    bad = _valid_report("review")
    bad["steps"][0]["evidence"][0]["ref"] = "/" + "Users/example/private/notes"
    cases.append(("invalid/internal-path", bad, False, "R9"))

    bad = _valid_report("review")
    bad["review_output"]["findings"][0]["summary"] = "passwd=hunter2xyz"
    cases.append(("invalid/credential-value", bad, False, "R9"))

    failures = 0
    print("SELF-TEST — guarded review/repair workflow validator")
    for name, doc, should_pass, expect_rule in cases:
        violations = validate(doc)
        passed = not violations
        good = passed == should_pass and (
            expect_rule is None or (not should_pass
                                    and _drop_error(violations, expect_rule)))
        if not good:
            failures += 1
        verdict = "ok" if good else "MISMATCH"
        want = "valid" if should_pass else f"invalid, rule {expect_rule}"
        print(f"  [{verdict}] {name}: "
              f"{'valid' if passed else 'invalid'} (expected {want})")
        if not good:
            for violation in violations:
                print(f"        {violation}")
    if failures:
        print(f"SELF-TEST FAILED — {failures} case(s) behaved unexpectedly.")
        return 1
    print(f"SELF-TEST PASSED — {len(cases)} cases behave as specified.")
    return 0


def fixtures():
    """Assert the fixture corpus: every valid/ passes, every invalid/ fails."""
    root = os.path.join(HERE, "fixtures")
    failures = 0
    total = 0
    print("FIXTURES — guarded review/repair workflow validator")
    for lane, should_pass in (("valid", True), ("invalid", False)):
        d = os.path.join(root, lane)
        if not os.path.isdir(d):
            print(f"  [FAIL] fixture dir missing: {d}")
            failures += 1
            continue
        for fname in sorted(os.listdir(d)):
            if not fname.endswith(".json"):
                continue
            total += 1
            path = os.path.join(d, fname)
            doc, err = load(path)
            if err is not None:
                print(f"  [FAIL] {lane}/{fname}: {err}")
                failures += 1
                continue
            violations = validate(doc)
            passed = not violations
            good = passed == should_pass
            if not good:
                failures += 1
            print(f"  [{'ok' if good else 'MISMATCH'}] {lane}/{fname}: "
                  f"{'valid' if passed else 'invalid'} "
                  f"(expected {'valid' if should_pass else 'invalid'})")
            if not good:
                for violation in violations:
                    print(f"        {violation}")
    if failures:
        print(f"FIXTURES FAILED — {failures} of {total} fixture(s) behaved "
              f"unexpectedly.")
        return 1
    print(f"FIXTURES PASSED — {total} fixture(s) behave as specified.")
    return 0


def main(argv):
    args = [a for a in argv if a != "--quiet"]
    quiet = "--quiet" in argv
    if "--selftest" in args:
        return selftest()
    if "--fixtures" in args:
        return fixtures()
    if not args:
        print((__doc__ or "").strip())
        return 1
    worst = 0
    for path in args:
        worst |= run_file(path, quiet=quiet)
    if worst:
        print("\nRESULT: FAIL (fail-closed — report is not a valid proposal-only "
              "review report)")
        return 1
    print("\nRESULT: PASS (every report is bound, evidenced, owned, rollback-"
          "safe, and proposal-only)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
