#!/usr/bin/env python3
"""
check-reward-registry.py — validator for the declarative reward catalogue
(choreography/reward-registry.md).

Dependency-free: Python 3 standard library only, zero network. The catalogue
uses a restricted, YAML-like, line-oriented shape parsed by this module's own
minimal reader — no third-party YAML library is imported.

The catalogue is METADATA ONLY. It names reward identities and their declared
behaviour. It never dynamically imports, evaluates, or executes an
implementation named in the file; there is no loader here. A future adapter
must be a separate architecture decision.

USAGE
  python3 build/check-reward-registry.py <catalogue.yaml>   # validate a file
  python3 build/check-reward-registry.py --self-test        # built-in tests
  python3 build/check-reward-registry.py --example-check    # repo examples

EXIT  0 = valid (or all self-tests/example checks behaved)   1 = invalid
"""

import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

TOP_KEYS = {"version", "rewards"}
ENTRY_FIELDS = ("id", "description", "input", "output", "min_score",
                "max_score", "deterministic", "modes", "implementation_ref",
                "source")
# Field names that would imply an executable hook. They are never valid.
EXECUTABLE_FIELDS = {"callable", "entrypoint", "python", "command"}

ID_RE = re.compile(r"^[a-z][a-z0-9_]{1,63}$")
# A dotted import path shape (module.attr.attr), used to reject an
# implementation_ref that is really an import target rather than a reference.
IMPORT_PATH_RE = re.compile(r"^[A-Za-z_]\w*(\.[A-Za-z_]\w*)+$")
INPUT_LITERAL = "scored_rollout_sample"
OUTPUT_LITERAL = "scalar"
MODE_VALUES = {"train", "eval"}

# Credential-like values are forbidden anywhere in a description or source.
CREDENTIAL_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9]{8,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)\b(password|passwd|secret|api[_-]?key|token)\s*[:=]\s*\S+"),
]
PATH_MARKER_RE = re.compile(r"(/Users/|/home/|~/\.hermes/|~/Documents/)")

_KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$")
_TRAILING_COMMENT_RE = re.compile(r"\s+#.*$")


def strip_comment(value):
    if value.lstrip().startswith("#"):
        return ""
    return _TRAILING_COMMENT_RE.sub("", value).strip()


def parse(text):
    """Return (top, rewards, seen_top, errors).

    top: {key: str}; rewards: [ {field: str}, ... ]; seen_top: set of
    top-level keys encountered (for duplicate detection); errors: list of
    parse-level messages (duplicate keys, malformed lines).
    """
    top = {}
    rewards = []
    errors = []
    seen_top = set()
    current = None
    in_rewards = False

    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())

        if indent == 0:
            current = None
            in_rewards = False
            m = _KEY_RE.match(stripped)
            if not m:
                errors.append(f"line {lineno}: not a field: '{stripped[:40]}'")
                continue
            key, val = m.group(1), strip_comment(m.group(2))
            if key in seen_top:
                errors.append(f"line {lineno}: duplicate key '{key}'")
                continue
            seen_top.add(key)
            if key == "rewards":
                if val != "":
                    errors.append(f"line {lineno}: 'rewards' must be a block "
                                  f"list, not an inline value")
                in_rewards = True
            else:
                if not val:
                    errors.append(f"line {lineno}: empty value for '{key}'")
                    continue
                top[key] = val
            continue

        if not in_rewards:
            errors.append(f"line {lineno}: indented content outside 'rewards'")
            continue

        if stripped.startswith("- "):
            rest = stripped[2:].strip()
            current = {}
            rewards.append(current)
            m = _KEY_RE.match(rest)
            if m:
                current[m.group(1)] = strip_comment(m.group(2))
            elif rest:
                errors.append(f"line {lineno}: malformed reward entry "
                              f"'{rest[:40]}'")
            else:
                errors.append(f"line {lineno}: empty reward entry")
            continue

        m = _KEY_RE.match(stripped)
        if m and current is not None:
            key, val = m.group(1), strip_comment(m.group(2))
            if key in current:
                errors.append(f"line {lineno}: duplicate key '{key}'")
            else:
                current[key] = val
            continue
        errors.append(f"line {lineno}: misplaced line: '{stripped[:40]}'")

    return top, rewards, seen_top, errors


def _to_number(text):
    """Parse a finite number from a string, or return None."""
    try:
        value = float(text)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(value):
        return None
    return value


def _credential_like(text):
    return any(p.search(text) for p in CREDENTIAL_PATTERNS)


def _looks_like_path(text):
    return bool(PATH_MARKER_RE.search(text))


def validate(top, rewards, seen_top):
    v = []

    for key in sorted(set(top) - TOP_KEYS):
        v.append(f"UNKNOWN top-level field '{key}'")
    if "rewards" not in seen_top:
        v.append("MISSING REQUIRED FIELD: 'rewards' section absent")
    version = top.get("version")
    if version is None:
        v.append("MISSING REQUIRED FIELD: 'version' is absent")
    elif version != "1":
        v.append(f"version must be 1 (got {version!r})")
    if not rewards:
        v.append("EMPTY CATALOGUE: at least one reward entry is required")
        return v

    seen_ids = set()
    for index, entry in enumerate(rewards):
        where = f"reward[{index}]"
        for key in sorted(set(entry) - set(ENTRY_FIELDS)):
            if key in EXECUTABLE_FIELDS:
                v.append(f"{where}: EXECUTABLE FIELD '{key}' is not allowed")
            else:
                v.append(f"{where}: unknown field '{key}'")
        missing = [f for f in ENTRY_FIELDS if f not in entry or entry[f] == ""]
        if missing:
            v.append(f"{where}: missing required field(s) {sorted(missing)}")

        rid = entry.get("id", "")
        if rid:
            if not ID_RE.match(rid):
                v.append(f"{where}: id '{rid}' is not lower snake case "
                         f"(^[a-z][a-z0-9_]{{1,63}}$)")
            if rid in seen_ids:
                v.append(f"{where}: duplicate id '{rid}'")
            seen_ids.add(rid)

        description = entry.get("description", "")
        if not description:
            v.append(f"{where}: description must be non-empty")
        elif "\n" in description or _credential_like(description) \
                or _looks_like_path(description):
            v.append(f"{where}: description must be a generic description "
                     f"(no prompt, credential, or local path)")

        if entry.get("input") != INPUT_LITERAL:
            v.append(f"{where}: input must be the literal '{INPUT_LITERAL}'")
        if entry.get("output") != OUTPUT_LITERAL:
            v.append(f"{where}: output must be the literal '{OUTPUT_LITERAL}'")

        lo = hi = None
        if "min_score" in entry:
            lo = _to_number(entry.get("min_score"))
            if lo is None:
                v.append(f"{where}: min_score must be a finite number")
        if "max_score" in entry:
            hi = _to_number(entry.get("max_score"))
            if hi is None:
                v.append(f"{where}: max_score must be a finite number")
        if lo is not None and hi is not None and lo > hi:
            v.append(f"{where}: min_score {lo} exceeds max_score {hi}")

        det = entry.get("deterministic")
        if det not in ("true", "false"):
            v.append(f"{where}: deterministic must be 'true' or 'false' "
                     f"(got {det!r})")

        modes = entry.get("modes", "")
        if not modes:
            v.append(f"{where}: modes must be non-empty")
        else:
            tokens = [m.strip() for m in modes.split(",") if m.strip()]
            if not tokens:
                v.append(f"{where}: modes must be non-empty")
            invalid = [m for m in tokens if m not in MODE_VALUES]
            if invalid:
                v.append(f"{where}: invalid mode(s) {invalid} "
                         f"(allowed: {sorted(MODE_VALUES)})")

        ref = entry.get("implementation_ref", "")
        if not ref:
            v.append(f"{where}: implementation_ref must be non-empty")
        elif "/" in ref or "\\" in ref or ref.endswith(".py") \
                or IMPORT_PATH_RE.match(ref):
            v.append(f"{where}: implementation_ref must be an opaque "
                     f"reference, not an import path")

        source = entry.get("source", "")
        if not source:
            v.append(f"{where}: source must be non-empty "
                     f"(or 'pending-verification')")
        elif _credential_like(source):
            v.append(f"{where}: source must not contain a credential-like value")
    return v


def validate_text(text):
    top, rewards, seen_top, errors = parse(text)
    if errors:
        return [f"PARSE: {e}" for e in errors]
    return validate(top, rewards, seen_top)


def check_file(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return validate_text(fh.read()), None
    except OSError as exc:
        return [], f"unreadable: {exc}"


# ---------------------------------------------------------------------------
# self-test — built-in pass/fail guarantee
# ---------------------------------------------------------------------------
VALID = """\
version: 1
rewards:
  - id: exact_match
    description: compare a scored answer with an expected answer
    input: scored_rollout_sample
    output: scalar
    min_score: 0
    max_score: 1
    deterministic: true
    modes: train,eval
    implementation_ref: project-local
    source: operator-documentation
  - id: length_penalty
    description: penalize an answer longer than a declared reference length
    input: scored_rollout_sample
    output: scalar
    min_score: -1
    max_score: 0
    deterministic: true
    modes: eval
    implementation_ref: project-local
    source: pending-verification
"""


def self_test():
    cases = []

    cases.append(("valid entry passes", VALID, True))

    cases.append(("missing required field fails",
                  VALID.replace("    source: operator-documentation\n", ""),
                  False))

    cases.append(("duplicate id fails",
                  VALID.replace("id: length_penalty", "id: exact_match"),
                  False))

    cases.append(("invalid identifier fails",
                  VALID.replace("id: exact_match", "id: ExactMatch"),
                  False))

    cases.append(("invalid mode fails",
                  VALID.replace("modes: train,eval", "modes: train,serve"),
                  False))

    cases.append(("reversed range fails",
                  VALID.replace("min_score: 0", "min_score: 2"),
                  False))

    cases.append(("malformed boolean fails",
                  VALID.replace("deterministic: true", "deterministic: yes"),
                  False))

    cases.append(("malformed number fails",
                  VALID.replace("max_score: 1", "max_score: 1.2.3"),
                  False))

    cases.append(("unknown executable field fails",
                  VALID.replace("    implementation_ref: project-local",
                                "    callable: do_reward", 1),
                  False))

    cases.append(("duplicate key fails",
                  VALID.replace("    output: scalar\n",
                                "    output: scalar\n    output: scalar\n", 1),
                  False))

    passed = failed = 0
    print("check-reward-registry — self-test")
    for name, text, want_ok in cases:
        violations = validate_text(text)
        ok = (not violations) if want_ok else bool(violations)
        mark = "PASS" if ok else "FAIL"
        passed += ok
        failed += not ok
        print(f"  [{mark}] {name}")
        if not ok and violations:
            for detail in violations[:3]:
                print(f"         got: {detail}")
    print(f"\n{passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


def example_check():
    roots = [os.path.join(HERE, "examples"),
             os.path.join(HERE, "..", "examples")]
    ex = next((r for r in roots if os.path.isdir(r)), None)
    if ex is None:
        print("  [SKIP] reward catalogue examples are not present")
        return 0
    passed = failed = 0
    print("check-reward-registry — example-check")
    for fname, want_ok in (("reward-functions.valid.yaml", True),
                           ("reward-functions.invalid.yaml", False)):
        path = os.path.join(ex, fname)
        if not os.path.isfile(path):
            print(f"  [FAIL] repo example {fname} missing")
            failed += 1
            continue
        violations, err = check_file(path)
        if err is not None:
            print(f"  [FAIL] {fname}: {err}")
            failed += 1
            continue
        ok = (not violations) if want_ok else bool(violations)
        mark = "PASS" if ok else "FAIL"
        passed += ok
        failed += not ok
        print(f"  [{mark}] repo example {fname} "
              f"{'valid' if want_ok else 'invalid'} as expected")
        if not ok:
            for detail in violations[:5]:
                print(f"         {detail}")
    print(f"\n{passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


def main():
    args = sys.argv[1:]
    if "--self-test" in args:
        return self_test()
    if "--example-check" in args:
        return example_check()
    if not args or args[0].startswith("-"):
        print(__doc__.strip())
        return 2
    path = args[0]
    violations, err = check_file(path)
    if err is not None:
        print(f"INVALID — {path}")
        print(f"  ✗ {err}")
        return 1
    if violations:
        print(f"INVALID — {path}")
        for detail in violations:
            print(f"  ✗ {detail}")
        return 1
    print(f"VALID — {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
