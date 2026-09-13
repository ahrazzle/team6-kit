#!/usr/bin/env python3
"""
check.py — Safe shareable run packet validator.

A dependency-free checker for the safe shareable run packet contract
(see choreography/safe-run-packet.md). Given one run packet, it decides whether
the packet is SAFE TO SHARE — that is, whether it states its objective,
decisions, verified evidence, unresolved items, changed artifacts, test
results, runtime/live status, next gate, provenance, and redaction status, and
whether it hides anything unsafe (an internal local path, a profile identity, a
credential value, or an off-convention placeholder).

It is a CONTRACT CHECKER, not a runtime gate. Running it performs no network
call, spawns no process, edits no file, and reads no credential. Standard
library only.

USAGE
  python3 check.py --selftest                  # run the built-in self-test
  python3 check.py <packet.json> [...]         # validate one or more packets
  python3 check.py --quiet <packet.json>       # errors only

EXIT
  0 = every input is a shareable packet (or self-test passed)
  1 = at least one input is invalid, unreadable, or not valid JSON (fail closed)

FAIL-CLOSED RULES (a single violation fails the whole packet):
  R1  a required field is missing or of the wrong kind   -> REQUIRED_FIELD
  R2  the objective is empty or not stated               -> OBJECTIVE_INCOMPLETE
  R3  a decision lacks its decision or rationale         -> DECISION_INCOMPLETE
  R4  evidence is marked verified without evidence       -> UNVERIFIED_EVIDENCE
  R5  live/staged status has no target or no evidence    -> LIVE_STATUS_INCOMPLETE
  R6  unresolved items omitted (absent or null)           -> UNRESOLVED_OMITTED
  R7  an internal local path or profile path appears      -> INTERNAL_PATH
  R8  a credential-like value appears anywhere            -> CREDENTIAL_VALUE
  R9  a placeholder is not the repository convention      -> PLACEHOLDER_NOT_CONVENTION
  R10 a test result lacks its result or evidence          -> TEST_RESULT_INCOMPLETE
  R11 provenance is incomplete                            -> PROVENANCE_INCOMPLETE
  R12 redaction status is missing or not checked          -> REDACTION_INCOMPLETE

The Team6 Kanban board remains authoritative. This packet is a derived,
shareable report — not a second state store.
"""

import json
import os
import re
import sys

# ---------------------------------------------------------------------------
# Contract shape — the required top-level fields and the kinds each accepts.
# unresolved_items is intentionally handled by R6 (a distinct failure class),
# so it is not repeated here.
# ---------------------------------------------------------------------------
REQUIRED_FIELDS = (
    ("objective", (str,)),
    ("decisions", (list,)),
    ("verified_evidence", (list,)),
    ("changed_artifacts", (list,)),
    ("test_results", (list,)),
    ("runtime_live_status", (dict,)),
    ("next_gate", (str, dict)),
    ("provenance", (dict,)),
    ("redaction_status", (dict,)),
)

# Runtime states. A staged or live claim must name its target and its evidence.
RUNTIME_STATES = {"not-applicable", "local-only", "staged", "live", "not-run"}
LIVE_STATES = {"staged", "live"}

# Redaction states that are ready to share. "not-checked" is not.
REDACTION_READY = {"clean", "redacted"}

# The repository's placeholder convention: a single UPPER_SNAKE token in braces.
PLACEHOLDER_CONVENTION_RE = re.compile(r"^\{[A-Z][A-Z0-9_]*\}$")

# Any brace-delimited run of characters — checked against the convention.
BRACE_RUN_RE = re.compile(r"\{[^{}]*\}")

# Ad-hoc redaction markers that are NOT the convention. Kept deliberately small
# and low-false-positive: guillemets, and bare all-caps marker words.
OFF_CONVENTION_MARKER_RE = re.compile(r"«[^»]*»")
BARE_MARKER_RE = re.compile(r"\b(?:TODO|TBD|FIXME|XXX|PLACEHOLDER)\b")

# Internal local path shapes. These are built from parts so this validator's own
# source never carries a contiguous absolute home-path literal.
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
    """Return a list of Violation for one packet document."""
    v = []

    if not isinstance(doc, dict):
        _fail(v, "R1", "", "packet must be a JSON object")
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

    # --- R2: objective stated --------------------------------------------
    if "objective" in doc and not _nonempty_str(doc.get("objective")):
        _fail(v, "R2", "objective", "objective must be a non-empty statement")

    # --- R3: decisions each carry a decision and a rationale -------------
    decisions = doc.get("decisions")
    if isinstance(decisions, list):
        for i, entry in enumerate(decisions):
            p = f"decisions[{i}]"
            if not isinstance(entry, dict):
                _fail(v, "R3", p, "decision must be an object")
                continue
            if not _nonempty_str(entry.get("decision")):
                _fail(v, "R3", f"{p}.decision", "decision must be stated")
            if not _nonempty_str(entry.get("rationale")):
                _fail(v, "R3", f"{p}.rationale", "decision needs a rationale")

    # --- R4: verified evidence really carries evidence -------------------
    evidence = doc.get("verified_evidence")
    if isinstance(evidence, list):
        for i, entry in enumerate(evidence):
            p = f"verified_evidence[{i}]"
            if not isinstance(entry, dict):
                _fail(v, "R4", p, "evidence entry must be an object")
                continue
            if not _nonempty_str(entry.get("claim")):
                _fail(v, "R4", f"{p}.claim", "evidence needs a claim")
            verified = entry.get("verified")
            if not isinstance(verified, bool):
                _fail(v, "R4", f"{p}.verified",
                      "evidence must be explicitly marked verified: true/false")
            elif verified and not _nonempty_str(entry.get("evidence")):
                _fail(v, "R4", f"{p}.evidence",
                      "evidence marked verified must carry the evidence that "
                      "verifies it")

    # --- R5: live/staged status names a target and evidence --------------
    live = doc.get("runtime_live_status")
    if isinstance(live, dict):
        state = live.get("state")
        if not _nonempty_str(state):
            _fail(v, "R5", "runtime_live_status.state",
                  "runtime/live status must state its state")
        else:
            if state not in RUNTIME_STATES:
                _fail(v, "R5", "runtime_live_status.state",
                      f"state must be one of {sorted(RUNTIME_STATES)}")
            if state in LIVE_STATES:
                if not _nonempty_str(live.get("target")):
                    _fail(v, "R5", "runtime_live_status.target",
                          "a live/staged status must name its target")
                if not _nonempty_str(live.get("evidence")):
                    _fail(v, "R5", "runtime_live_status.evidence",
                          "a live/staged status must carry evidence")

    # --- R6: unresolved items present, never silently omitted ------------
    if "unresolved_items" not in doc or doc.get("unresolved_items") is None:
        _fail(v, "R6", "unresolved_items",
              "unresolved items must be present (use an empty list for none; "
              "omitting the field is a failure)")
    elif not isinstance(doc.get("unresolved_items"), list):
        _fail(v, "R6", "unresolved_items",
              "unresolved items must be an explicit list")
    else:
        for i, entry in enumerate(doc["unresolved_items"]):
            if not _nonempty_str(entry):
                _fail(v, "R6", f"unresolved_items[{i}]",
                      "unresolved item must be a non-empty statement")

    # --- R7/R8: no internal path, profile path, or credential value ------
    seen_internal = False
    seen_secret = False
    for value, path in _walk_strings(doc):
        if not seen_internal and any(rx.search(value)
                                     for rx in _INTERNAL_PATH_PATTERNS):
            _fail(v, "R7", path,
                  "an internal local path or profile path appears; replace it "
                  "with a repository-relative path or a convention placeholder")
            seen_internal = True
        if not seen_secret and any(rx.search(value)
                                   for rx in SECRET_PATTERNS):
            _fail(v, "R8", path,
                  "a credential-like value appears; credential names are "
                  "allowed, values are not")
            seen_secret = True

    # --- R9: placeholders follow the repository convention ---------------
    seen_placeholder = False
    for value, path in _walk_strings(doc):
        if seen_placeholder:
            break
        for run in BRACE_RUN_RE.findall(value):
            if not PLACEHOLDER_CONVENTION_RE.match(run):
                _fail(v, "R9", path,
                      f"placeholder {run!r} is not the repository convention "
                      f"(expected a single UPPER_SNAKE token in braces)")
                seen_placeholder = True
                break
        if seen_placeholder:
            break
        if OFF_CONVENTION_MARKER_RE.search(value) or BARE_MARKER_RE.search(value):
            _fail(v, "R9", path,
                  "an off-convention placeholder marker appears; use the "
                  "repository placeholder convention")
            seen_placeholder = True

    # --- R10: test results carry a result and its evidence ---------------
    tests = doc.get("test_results")
    if isinstance(tests, list):
        for i, entry in enumerate(tests):
            p = f"test_results[{i}]"
            if not isinstance(entry, dict):
                _fail(v, "R10", p, "test result must be an object")
                continue
            if not _nonempty_str(entry.get("name")):
                _fail(v, "R10", f"{p}.name", "test result must name the check")
            if not _nonempty_str(entry.get("result")):
                _fail(v, "R10", f"{p}.result",
                      "test result must state its observed result")
            if not _nonempty_str(entry.get("evidence")):
                _fail(v, "R10", f"{p}.evidence",
                      "test result must carry the output or signal behind it")

    # --- R11: provenance is stated ---------------------------------------
    prov = doc.get("provenance")
    if isinstance(prov, dict):
        if not _nonempty_str(prov.get("produced_by")):
            _fail(v, "R11", "provenance.produced_by",
                  "provenance must name who produced the packet")
        if not _nonempty_str(prov.get("task_ref")):
            _fail(v, "R11", "provenance.task_ref",
                  "provenance must reference the run or task it describes")

    # --- R12: redaction status is stated and the packet is share-ready ---
    red = doc.get("redaction_status")
    if isinstance(red, dict):
        status = red.get("status")
        if not _nonempty_str(status):
            _fail(v, "R12", "redaction_status.status",
                  "redaction status must state its status")
        elif status not in REDACTION_READY:
            _fail(v, "R12", "redaction_status.status",
                  f"a packet is not shareable until redaction status is one of "
                  f"{sorted(REDACTION_READY)}")
        if not _nonempty_str(red.get("method")):
            _fail(v, "R12", "redaction_status.method",
                  "redaction status must state how the packet was checked")

    # --- next_gate must actually name a gate -----------------------------
    ng = doc.get("next_gate")
    if isinstance(ng, dict):
        if not _nonempty_str(ng.get("gate")):
            _fail(v, "R1", "next_gate.gate", "next gate must be named")
    elif "next_gate" in doc and not _nonempty_str(ng):
        _fail(v, "R1", "next_gate", "next gate must be a non-empty statement")

    return v


def load(path):
    """Load one packet document. Returns (doc, error_or_None)."""
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
        print("  OK    packet is complete and safe to share "
              "(no internal path, credential, or off-convention placeholder)")
    return 0


# ---------------------------------------------------------------------------
# Self-test — valid and invalid packets exercised in-process.
# ---------------------------------------------------------------------------
VALID_PACKET = {
    "objective": "Add a documentation-only contract and a dependency-free "
                 "validator for the run packet.",
    "decisions": [
        {"decision": "Keep the validator standard-library only",
         "rationale": "it must run on a bare clone with no install step"},
        {"decision": "Reject ad-hoc redaction markers",
         "rationale": "only the repository placeholder convention is allowed"},
    ],
    "verified_evidence": [
        {"claim": "the validator self-test passes",
         "verified": True, "evidence": "python3 check.py --selftest -> PASS"},
        {"claim": "the new files contain no internal path",
         "verified": True, "evidence": "surface-scan.py -> 0 leaks"},
    ],
    "unresolved_items": [],
    "changed_artifacts": [
        "choreography/safe-run-packet.md",
        "build/report/check.py",
    ],
    "test_results": [
        {"name": "self-test", "result": "pass",
         "evidence": "12 cases behave as specified"},
    ],
    "runtime_live_status": {"state": "not-applicable"},
    "next_gate": "independent review before merge",
    "provenance": {"produced_by": "build agent", "task_ref": "run-packet-contract"},
    "redaction_status": {"status": "clean", "method": "surface-scan + grep sweep"},
}

VALID_WITH_PLACEHOLDER = json.loads(json.dumps(VALID_PACKET))
VALID_WITH_PLACEHOLDER["objective"] = (
    "Document a {CLIENT}-safe handoff artifact for the run.")
VALID_WITH_PLACEHOLDER["unresolved_items"] = [
    "final {RELATIONSHIP} naming is deferred to review"]

VALID_LIVE = json.loads(json.dumps(VALID_PACKET))
VALID_LIVE["runtime_live_status"] = {
    "state": "staged",
    "target": "staging copy of the report surface",
    "evidence": "staging URL rendered the packet without error",
}


def _copy(doc):
    return json.loads(json.dumps(doc))


def selftest():
    cases = []

    cases.append(("valid/basic", _copy(VALID_PACKET), True, None))
    cases.append(("valid/convention-placeholder",
                  _copy(VALID_WITH_PLACEHOLDER), True, None))
    cases.append(("valid/live-with-evidence", _copy(VALID_LIVE), True, None))

    bad = _copy(VALID_PACKET)
    del bad["provenance"]
    cases.append(("invalid/missing-required-field", bad, False, "R1"))

    bad = _copy(VALID_PACKET)
    bad["objective"] = "   "
    cases.append(("invalid/objective-empty", bad, False, "R2"))

    bad = _copy(VALID_PACKET)
    bad["decisions"] = [{"decision": "keep it simple"}]
    cases.append(("invalid/decision-incomplete", bad, False, "R3"))

    bad = _copy(VALID_PACKET)
    bad["verified_evidence"] = [
        {"claim": "the validator works", "verified": True}]
    cases.append(("invalid/evidence-marked-verified", bad, False, "R4"))

    bad = _copy(VALID_PACKET)
    bad["runtime_live_status"] = {"state": "live", "evidence": "seen in UI"}
    cases.append(("invalid/live-without-target", bad, False, "R5"))

    bad = _copy(VALID_PACKET)
    bad["runtime_live_status"] = {"state": "live", "target": "production site"}
    cases.append(("invalid/live-without-evidence", bad, False, "R5"))

    bad = _copy(VALID_PACKET)
    del bad["unresolved_items"]
    cases.append(("invalid/unresolved-omitted", bad, False, "R6"))

    bad = _copy(VALID_PACKET)
    bad["unresolved_items"] = None
    cases.append(("invalid/unresolved-null", bad, False, "R6"))

    bad = _copy(VALID_PACKET)
    bad["changed_artifacts"] = ["/" + "Users/example/private/notes.txt"]
    cases.append(("invalid/internal-path", bad, False, "R7"))

    bad = _copy(VALID_PACKET)
    bad["provenance"]["produced_by"] = (
        "." + "hermes/" + "profiles/" + "example-agent")
    cases.append(("invalid/profile-path", bad, False, "R7"))

    bad = _copy(VALID_PACKET)
    bad["provenance"]["task_ref"] = "api_key=abcdef1234567890"
    cases.append(("invalid/credential-value", bad, False, "R8"))

    bad = _copy(VALID_PACKET)
    bad["objective"] = "Document a «redacted» handoff artifact."
    cases.append(("invalid/placeholder-not-convention", bad, False, "R9"))

    bad = _copy(VALID_PACKET)
    bad["test_results"] = [{"name": "self-test", "result": "pass"}]
    cases.append(("invalid/test-result-incomplete", bad, False, "R10"))

    bad = _copy(VALID_PACKET)
    bad["provenance"] = {"produced_by": "build agent"}
    cases.append(("invalid/provenance-incomplete", bad, False, "R11"))

    bad = _copy(VALID_PACKET)
    bad["redaction_status"] = {"status": "not-checked", "method": "none"}
    cases.append(("invalid/redaction-not-checked", bad, False, "R12"))

    failures = 0
    print("SELF-TEST — safe shareable run packet validator")
    for name, doc, should_pass, expect_rule in cases:
        violations = validate(doc)
        passed = not violations
        rules = {violation.rule for violation in violations}
        good = passed == should_pass and (
            expect_rule is None or (not should_pass and expect_rule in rules))
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


def main(argv):
    args = [a for a in argv if a != "--quiet"]
    quiet = "--quiet" in argv
    if "--selftest" in args:
        return selftest()
    if not args:
        print((__doc__ or "").strip())
        return 1
    worst = 0
    for path in args:
        worst |= run_file(path, quiet=quiet)
    if worst:
        print("\nRESULT: FAIL (fail-closed — packet is not safe to share)")
        return 1
    print("\nRESULT: PASS (every packet is complete and safe to share)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
