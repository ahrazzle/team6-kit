#!/usr/bin/env python3
"""
check.py — Side-effect and cost preflight validator.

A dependency-free checker for the side-effect / cost preflight contract
(see choreography/side-effect-cost-preflight.md). Given one operation
description, it decides whether the operation is SAFE TO DESCRIBE — that is,
whether the description states every side effect, credential, cost, public
surface, and rollback path a reviewer needs, and whether it hides anything
(a credential value, an unbounded wait, a side effect with no rollback).

It is a CONTRACT CHECKER, not a runtime gate. Running it performs no network
call, spawns no process, edits no file, and reads no credential. Standard
library only.

USAGE
  python3 check.py --selftest                 # run the built-in self-test
  python3 check.py <preflight.json> [...]     # validate one or more files
  python3 check.py --quiet <preflight.json>   # errors only

EXIT
  0 = every input is valid (or self-test passed)
  1 = at least one input is invalid, unreadable, or not valid JSON (fail closed)

FAIL-CLOSED RULES (a single violation fails the whole document):
  R1  required field missing or empty                     -> REQUIRED_FIELD
  R2  operation identity incomplete                       -> OPERATION_INCOMPLETE
  R3  a credential entry is a value, not an env-var name  -> CREDENTIAL_VALUE
  R4  a credential name is not an env-var-name shape      -> CREDENTIAL_NAME
  R5  a secret-looking token appears anywhere in the doc  -> CREDENTIAL_VALUE
  R6  a wait/timeout is missing, unbounded, or non-finite -> UNBOUNDED_WAIT
  R7  a side-effecting operation has no rollback path     -> MISSING_ROLLBACK
  R8  a paid operation without an approved owner state    -> PAID_WITHOUT_APPROVAL
  R9  a conditional action not explicitly marked may-run  -> CONDITIONAL_NOT_MARKED
  R10 an unknown cost/quantity that is not made explicit  -> UNKNOWN_NOT_DECLARED
  R11 estimated quantity missing or not conservative      -> QUANTITY_NOT_STATED
"""

import json
import math
import os
import re
import sys

# ---------------------------------------------------------------------------
# Contract shape — the required top-level fields and their kinds.
# ---------------------------------------------------------------------------
REQUIRED_FIELDS = {
    "operation": dict,
    "files_to_change": list,
    "external_systems": list,
    "credentials_required": list,
    "paid_operations": list,
    "estimated_quantity": dict,
    "conditional_actions": list,
    "public_surfaces": list,
    "rollback": dict,
    "owner_approval": dict,
    "unknowns": list,
}

APPROVAL_STATES = {"approved", "pending", "not-required", "rejected"}

# Environment-variable NAME shape (values are forbidden by contract).
ENV_NAME_RE = re.compile(r"^[A-Z][A-Z0-9_]{0,63}$")

# A wait key anywhere in the document must carry a finite, positive bound.
WAIT_KEY_RE = re.compile(r"(wait|timeout|deadline|sleep|poll)", re.I)

# Secret-looking token shapes. Names are allowed; values never are.
SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9]{8,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._-]{12,}"),
    re.compile(r"(?i)\b(password|passwd|secret|api[_-]?key)\s*[:=]\s*\S+"),
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


def _is_finite_number(value):
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def _walk(node, path=""):
    """Yield (key, value, dotted_path) for every mapping entry, recursively."""
    if isinstance(node, dict):
        for key, value in node.items():
            child = f"{path}.{key}" if path else str(key)
            yield key, value, child
            yield from _walk(value, child)
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from _walk(value, f"{path}[{i}]")


def validate(doc):
    """Return a list of Violation for one preflight document."""
    v = []

    if not isinstance(doc, dict):
        _fail(v, "R1", "", "document must be a JSON object")
        return v

    # --- R1: required fields present and of the right kind ---------------
    for field, kind in REQUIRED_FIELDS.items():
        if field not in doc:
            _fail(v, "R1", field, f"required field missing ({kind.__name__})")
        elif not isinstance(doc[field], kind):
            _fail(
                v, "R1", field,
                f"required field must be {kind.__name__}, "
                f"got {type(doc[field]).__name__}",
            )

    # --- R2: operation identity ------------------------------------------
    op = doc.get("operation")
    if isinstance(op, dict):
        for sub in ("id", "summary"):
            if not str(op.get(sub, "")).strip():
                _fail(v, "R2", f"operation.{sub}",
                      "operation identity is incomplete")
    elif "operation" in doc:
        pass  # already reported by R1 kind check

    # --- R3/R4: credentials are names, never values ----------------------
    creds = doc.get("credentials_required")
    if isinstance(creds, list):
        for i, entry in enumerate(creds):
            p = f"credentials_required[{i}]"
            if not isinstance(entry, str):
                _fail(v, "R3", p,
                      "credential entry must be an environment-variable NAME "
                      "string, never a value or object")
            elif not ENV_NAME_RE.match(entry):
                _fail(v, "R4", p,
                      f"{entry!r} is not an environment-variable name shape "
                      f"(expected [A-Z][A-Z0-9_]*)")
    else:
        _fail(v, "R1", "credentials_required",
              "credentials_required must be a list of env-var names")

    # --- R5: no secret-looking token anywhere ----------------------------
    raw = json.dumps(doc, sort_keys=True)
    for pat in SECRET_PATTERNS:
        m = pat.search(raw)
        if m:
            _fail(v, "R5", "",
                  "a secret-looking value appears in the document "
                  "(credential values are forbidden; names only)")
            break

    # --- R6: waits and timeouts are bounded ------------------------------
    saw_wait = False
    for key, value, path in _walk(doc):
        if WAIT_KEY_RE.search(str(key)):
            saw_wait = True
            name = str(key).lower()
            if isinstance(value, str):
                if value.strip().lower() in ("", "none", "null", "infinite",
                                             "unbounded", "inf", "-1"):
                    _fail(v, "R6", path,
                          "unbounded/indefinite wait is not allowed; give a "
                          "finite positive bound")
            elif value is None:
                _fail(v, "R6", path, "wait bound must not be null")
            elif not _is_finite_number(value) or value <= 0:
                _fail(v, "R6", path,
                      "wait bound must be a finite positive number")
            if name.endswith("_seconds") and not _is_finite_number(value):
                _fail(v, "R6", path, "wait bound must be numeric seconds")

    # --- side-effect classification --------------------------------------
    nonempty = lambda name: isinstance(doc.get(name), list) and bool(doc.get(name))
    side_effecting = (
        nonempty("files_to_change")
        or nonempty("external_systems")
        or nonempty("public_surfaces")
        or nonempty("paid_operations")
    )

    # --- R7: side effects require a rollback path ------------------------
    rollback = doc.get("rollback")
    if isinstance(rollback, dict):
        if not saw_wait and "max_wait_seconds" not in rollback:
            _fail(v, "R6", "rollback.max_wait_seconds",
                  "rollback must declare a bounded max_wait_seconds")
        if side_effecting:
            if not str(rollback.get("path", "")).strip():
                _fail(v, "R7", "rollback.path",
                      "side-effecting operation has no rollback/recovery path")
            if rollback.get("bounded", None) is not True:
                _fail(v, "R7", "rollback.bounded",
                      "side-effecting operation must declare rollback as "
                      "bounded: true")
    elif "rollback" in doc:
        _fail(v, "R7", "rollback", "rollback must be an object")

    # --- R8: paid operations need an approved owner state ----------------
    paid = doc.get("paid_operations")
    owner = doc.get("owner_approval")
    if isinstance(owner, dict):
        if not str(owner.get("owner", "")).strip():
            _fail(v, "R8", "owner_approval.owner", "owner must be named")
        state = owner.get("approval_state")
        if state not in APPROVAL_STATES:
            _fail(v, "R8", "owner_approval.approval_state",
                  f"approval_state must be one of {sorted(APPROVAL_STATES)}")
        if isinstance(paid, list) and paid and state != "approved":
            _fail(v, "R8", "owner_approval.approval_state",
                  "paid operations are present but approval_state is not "
                  "'approved'")
    elif "owner_approval" in doc:
        _fail(v, "R8", "owner_approval", "owner_approval must be an object")

    # --- R9: conditional actions explicitly marked may-run ---------------
    conds = doc.get("conditional_actions")
    if isinstance(conds, list):
        for i, entry in enumerate(conds):
            p = f"conditional_actions[{i}]"
            if not isinstance(entry, dict):
                _fail(v, "R9", p, "conditional action must be an object")
                continue
            if not str(entry.get("description", "")).strip():
                _fail(v, "R9", f"{p}.description",
                      "conditional action needs a description")
            if not isinstance(entry.get("may_run"), bool):
                _fail(v, "R9", f"{p}.may_run",
                      "conditional action must be explicitly marked "
                      "may_run: true/false")

    # --- R10/R11: quantity stated, unknowns explicit ---------------------
    qty = doc.get("estimated_quantity")
    if isinstance(qty, dict):
        if not str(qty.get("unit", "")).strip():
            _fail(v, "R11", "estimated_quantity.unit",
                  "cost/quantity unit must be stated")
        value = qty.get("value", "<missing>")
        if value == "<missing>":
            _fail(v, "R11", "estimated_quantity.value",
                  "estimated quantity must be stated (a number or 'unknown')")
        elif isinstance(value, str):
            if value.strip().lower() != "unknown":
                _fail(v, "R11", "estimated_quantity.value",
                      "quantity string must be 'unknown' when not a number")
            else:
                if not str(qty.get("basis", "")).strip():
                    _fail(v, "R11", "estimated_quantity.basis",
                          "an unknown quantity must state a conservative basis")
                unknowns = doc.get("unknowns")
                declared = isinstance(unknowns, list) and any(
                    "estimated_quantity" in str(u) for u in unknowns)
                if not declared:
                    _fail(v, "R10", "unknowns",
                          "unknown quantity is not declared in the explicit "
                          "unknowns list")
        elif not _is_finite_number(value) or value < 0:
            _fail(v, "R11", "estimated_quantity.value",
                  "estimated quantity must be a finite number >= 0 or 'unknown'")
    elif "estimated_quantity" in doc:
        _fail(v, "R11", "estimated_quantity",
              "estimated_quantity must be an object")
    else:
        _fail(v, "R11", "estimated_quantity", "estimated quantity must be stated")

    # --- unknowns must be explicit (a list, possibly empty) --------------
    if "unknowns" in doc and not isinstance(doc["unknowns"], list):
        _fail(v, "R10", "unknowns",
              "unknowns must be an explicit list (use an empty list for none)")

    return v


def load(path):
    """Load one preflight document. Returns (doc, error_or_None)."""
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
        print("  OK    all required fields present; no forbidden values; "
              "side effects covered")
    return 0


# ---------------------------------------------------------------------------
# Self-test — valid and invalid documents exercised in-process.
# ---------------------------------------------------------------------------
VALID_OPERATION = {
    "operation": {
        "id": "op-example-doc-edit",
        "summary": "Edit two documentation files and open a review request",
    },
    "files_to_change": ["docs/guide.md", "docs/index.md"],
    "external_systems": [
        {"name": "git remote", "endpoint": "git@host:org/repo.git",
         "purpose": "push branch"}
    ],
    "credentials_required": ["GIT_SSH_KEY", "REVIEW_TOKEN"],
    "paid_operations": [],
    "estimated_quantity": {"unit": "requests", "value": 2, "basis": "two calls"},
    "conditional_actions": [
        {"description": "retry the push on a transient error", "may_run": True}
    ],
    "public_surfaces": ["repository branch"],
    "rollback": {"path": "delete the branch; revert the commit", "bounded": True,
                 "max_wait_seconds": 300},
    "owner_approval": {"owner": "build-lead", "approval_state": "approved"},
    "unknowns": [],
}

VALID_PAID_APPROVED = json.loads(json.dumps(VALID_OPERATION))
VALID_PAID_APPROVED["paid_operations"] = [
    {"name": "image generation", "cost_units": 12}
]
VALID_PAID_APPROVED["estimated_quantity"] = {
    "unit": "images", "value": "unknown", "basis": "bounded by review budget"
}
VALID_PAID_APPROVED["unknowns"] = ["estimated_quantity is unknown"]


def _copy(doc):
    return json.loads(json.dumps(doc))


def selftest():
    cases = []

    ok = _copy(VALID_OPERATION)
    cases.append(("valid/local-edit", ok, True))

    cases.append(("valid/paid-approved-unknown-qty",
                  _copy(VALID_PAID_APPROVED), True))

    bad = _copy(VALID_OPERATION)
    del bad["rollback"]
    cases.append(("invalid/missing-required-field", bad, False))

    bad = _copy(VALID_OPERATION)
    bad["credentials_required"] = ["GIT_SSH_KEY", {"name": "TOKEN",
                                                   "value": "sk-live-abcd1234"}]
    cases.append(("invalid/credential-value", bad, False))

    bad = _copy(VALID_OPERATION)
    bad["rollback"]["max_wait_seconds"] = "infinite"
    cases.append(("invalid/unbounded-wait", bad, False))

    bad = _copy(VALID_OPERATION)
    bad["rollback"]["path"] = ""
    cases.append(("invalid/missing-rollback", bad, False))

    bad = _copy(VALID_OPERATION)
    bad["paid_operations"] = [{"name": "render", "cost_units": 5}]
    bad["owner_approval"]["approval_state"] = "pending"
    cases.append(("invalid/paid-without-approval", bad, False))

    bad = _copy(VALID_OPERATION)
    bad["conditional_actions"] = [{"description": "retry on error"}]
    cases.append(("invalid/conditional-not-marked", bad, False))

    bad = _copy(VALID_OPERATION)
    bad["estimated_quantity"] = {"unit": "requests", "value": "unknown",
                                 "basis": "bounded"}
    bad["unknowns"] = []
    cases.append(("invalid/unknown-not-declared", bad, False))

    failures = 0
    print("SELF-TEST — side-effect / cost preflight validator")
    for name, doc, should_pass in cases:
        violations = validate(doc)
        passed = not violations
        good = passed == should_pass
        if not good:
            failures += 1
        verdict = "ok" if good else "MISMATCH"
        print(f"  [{verdict}] {name}: "
              f"{'valid' if passed else 'invalid'} "
              f"(expected {'valid' if should_pass else 'invalid'})")
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
        print("\nRESULT: FAIL (fail-closed — do not proceed to a side effect)")
        return 1
    print("\nRESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
