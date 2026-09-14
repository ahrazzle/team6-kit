#!/usr/bin/env python3
"""
check-artifact-contract.py — validator for the artifact-contract handoff
format (choreography/artifact-contract.md).

Dependency-free: Python 3 stdlib only, zero network (same no-egress rule the
build gates enforce). Parses the line-oriented contract format and enforces
the validation rules documented in the choreography file:

  1. required fields present + non-empty            5. artifact cross-references
  2. enums enforced                                 6. regenerate ∩ not-to-touch = ∅
  3. failure_state required on failed/blocked       7. size bounds sane
  4. resume_phase moves only forward                8. unknown fields fail

USAGE
  python3 build/check-artifact-contract.py <contract.yaml>   # validate a file
  python3 build/check-artifact-contract.py --self-test       # pass/fail tests
  python3 build/check-artifact-contract.py --example-check   # repo examples

EXIT  0 = valid (all tests pass)   1 = invalid (violations listed with fields)
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

SCALAR_REQUIRED = ["contract_version", "task_id", "project", "phase",
                   "status", "runtime_state", "last_stable_phase",
                   "resume_phase"]
LIST_REQUIRED_NONEMPTY = ["expected_artifacts", "required_sections",
                          "size_bounds", "tests", "evidence_refs"]
LIST_REQUIRED_MAYBE_EMPTY = ["feedback_to_apply", "artifacts_to_regenerate",
                             "artifacts_not_to_touch"]
DICT_FIELDS = ["failure_state"]

STATUS_ENUM = {"completed", "partial", "failed", "blocked"}
RUNTIME_ENUM = {"local", "staged", "live"}
KIND_ENUM = {"file", "directory"}
APPLIED_ENUM = {"yes", "no", "n-a"}

# Canonical phase order for validation
PHASE_ORDER = ["build", "test", "staged", "ship", "live"]

ITEM_KEYS = {
    "expected_artifacts": {"path", "kind", "produced_by"},
    "required_sections": {"artifact", "section", "marker"},
    "size_bounds": {"artifact", "min_bytes", "max_bytes"},
    "tests": {"name", "command"},
    "evidence_refs": {"ref", "proves"},
    "feedback_to_apply": {"note", "applied"},
    "artifacts_to_regenerate": {"path"},
    "artifacts_not_to_touch": {"path"},
}
ITEM_REQUIRED_KEYS = {
    "expected_artifacts": ["path"],
    "required_sections": ["artifact", "section"],
    "size_bounds": ["artifact"],
    "tests": ["name", "command"],
    "evidence_refs": ["ref", "proves"],
    "feedback_to_apply": ["note"],
    "artifacts_to_regenerate": ["path"],
    "artifacts_not_to_touch": ["path"],
}
FAILURE_KEYS = {"machine_state", "human_state", "remediation"}

_KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$")
_SIZE_RE = re.compile(r"^\s*(\d+)\s*([KMk m]?)\s*$")
_TRAILING_COMMENT_RE = re.compile(r"\s+#.*$")


def strip_comment(value):
    """Drop a trailing inline comment (' # ...'). A '#' glued to the value
    (e.g. a quoted marker '## Definition of Done') is content, not comment."""
    if value.lstrip().startswith("#"):
        return ""
    return _TRAILING_COMMENT_RE.sub("", value).strip()


def parse_size(value, field):
    """'50K' -> 51200, '500' -> 500. Returns (int_or_None, error_or_None)."""
    m = _SIZE_RE.match(value or "")
    if not m:
        return None, f"{field}: not a positive byte size (got '{value}')"
    n = int(m.group(1))
    suf = m.group(2).upper()
    if suf == "K":
        n *= 1024
    elif suf == "M":
        n *= 1024 * 1024
    if n <= 0:
        return None, f"{field}: must be > 0 (got 0)"
    return n, None


def parse_contract(text):
    """Contract text -> (scalars, lists, dicts, parse_errors).

    scalars: {key: str}; lists: {key: [item, ...]} where an item is a str or
    an ordered dict; dicts: {key: {sub: str}}. Unknown shapes are collected as
    parse errors rather than guessed at — a malformed handoff must fail loudly.
    """
    scalars, lists, dicts, errors = {}, {}, {}, []
    cur_list = None      # list key currently receiving items
    cur_dict = None      # dict field currently receiving sub-keys
    item = None          # current list item (dict being filled)

    def close_item():
        nonlocal item
        if item is not None:
            lists[cur_list].append(item)
            item = None

    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        body = stripped

        if indent == 0:
            close_item()
            cur_list = cur_dict = None
            m = _KEY_RE.match(body)
            if not m:
                errors.append(f"line {lineno}: not a field: '{body[:40]}'")
                continue
            key, val = m.group(1), strip_comment(m.group(2))
            if key in scalars or key in lists or key in dicts:
                errors.append(f"line {lineno}: duplicate field '{key}'")
                continue
            if val == "[]":
                lists[key] = []
            elif val == "":
                if key in DICT_FIELDS:
                    cur_dict = key
                    dicts[key] = {}
                elif key in ITEM_KEYS or key in LIST_REQUIRED_MAYBE_EMPTY \
                        or key in LIST_REQUIRED_NONEMPTY:
                    cur_list = key
                    lists.setdefault(key, [])
                else:
                    errors.append(f"line {lineno}: empty scalar '{key}' "
                                  f"(fill it or use [])")
            else:
                scalars[key] = val
            continue

        # indented
        if body.startswith("- "):
            if cur_list is None:
                errors.append(f"line {lineno}: list item outside a list "
                              f"section")
                continue
            close_item()
            rest = body[2:].strip()
            m = _KEY_RE.match(rest)
            if m:
                item = {m.group(1): strip_comment(m.group(2))}
            elif rest.endswith(":"):
                item = {rest[:-1].strip(): ""}
            elif rest:
                lists[cur_list].append(strip_comment(rest))
            else:
                errors.append(f"line {lineno}: empty list item")
            continue

        m = _KEY_RE.match(body)
        if m and (item is not None or cur_dict is not None):
            key, val = m.group(1), strip_comment(m.group(2))
            target = item if item is not None else dicts[cur_dict]
            if key in target and target[key]:
                errors.append(f"line {lineno}: duplicate field '{key}'")
            else:
                target[key] = val
            continue
        if item is not None and not m:
            # continuation of the previous item value (folded line)
            k = list(item)[-1]
            item[k] = (item[k] + " " + stripped).strip()
            continue
        errors.append(f"line {lineno}: misplaced line: '{body[:40]}'")

    close_item()
    return scalars, lists, dicts, errors


def validate(scalars, lists, dicts):
    """Return a list of violation strings (empty = valid)."""
    v = []

    # 1. required scalars present + non-empty
    for key in SCALAR_REQUIRED:
        if key not in scalars or not scalars[key]:
            v.append(f"MISSING REQUIRED FIELD: '{key}' is absent or empty")

    # unknown top-level keys -> 8. (typo'd required fields fail, not shrug)
    known = set(scalars) | set(lists) | set(dicts)
    allowed = (set(SCALAR_REQUIRED) | set(LIST_REQUIRED_NONEMPTY)
               | set(LIST_REQUIRED_MAYBE_EMPTY) | set(DICT_FIELDS))
    for key in sorted(known - allowed):
        v.append(f"UNKNOWN FIELD: '{key}'")

    # 2. enums
    status = scalars.get("status", "")
    if status and status not in STATUS_ENUM:
        v.append(f"ENUM: status '{status}' not in {sorted(STATUS_ENUM)}")
    rt = scalars.get("runtime_state", "")
    if rt and rt not in RUNTIME_ENUM:
        v.append(f"ENUM: runtime_state '{rt}' not in {sorted(RUNTIME_ENUM)}")

    # 1b. required lists present + non-empty
    for key in LIST_REQUIRED_NONEMPTY:
        items = lists.get(key)
        if items is None:
            v.append(f"MISSING REQUIRED FIELD: '{key}:' section absent")
        elif not items:
            v.append(f"EMPTY REQUIRED LIST: '{key}' must have at least one entry")
    for key in LIST_REQUIRED_MAYBE_EMPTY:
        if lists.get(key) is None and key not in scalars:
            v.append(f"MISSING REQUIRED FIELD: '{key}:' section absent "
                     f"(write it as '[]' if none)")

    # item shape: required item keys, enums, unknown item fields
    paths = set()
    arts = lists.get("expected_artifacts", [])
    for it in arts:
        if isinstance(it, str):
            paths.add(it)
            continue
        if not isinstance(it, dict):
            continue
        for req in ITEM_REQUIRED_KEYS["expected_artifacts"]:
            if not it.get(req):
                v.append(f"ARTIFACT ITEM: missing '{req}' in {it}")
        paths.add(it.get("path", "?"))
        kind = it.get("kind", "file")
        if kind not in KIND_ENUM:
            v.append(f"ENUM: artifact kind '{kind}' not in {sorted(KIND_ENUM)}")
    for key, items in lists.items():
        if key not in ITEM_KEYS:
            continue
        for it in items:
            if isinstance(it, str):
                if key not in ("artifacts_to_regenerate", "artifacts_not_to_touch"):
                    v.append(f"{key}: bare string items not allowed here")
                else:
                    continue
            for req in ITEM_REQUIRED_KEYS[key]:
                if not it.get(req):
                    v.append(f"{key.upper()} ITEM: missing '{req}' in {it}")
            for uk in sorted(set(it) - ITEM_KEYS[key]):
                v.append(f"{key.upper()} ITEM: unknown field '{uk}'")
            applied = it.get("applied")
            if applied and applied not in APPLIED_ENUM:
                v.append(f"ENUM: applied '{applied}' not in {sorted(APPLIED_ENUM)}")

    # 3. failure_state on failed/blocked
    if status in ("failed", "blocked"):
        fs = dicts.get("failure_state") or {}
        for req in ("machine_state", "human_state"):
            if not fs.get(req):
                v.append(f"MISSING REQUIRED FIELD: failure_state.{req} is "
                         f"required when status: {status}")
    for fk in sorted(set((dicts.get("failure_state") or {})) - FAILURE_KEYS):
        v.append(f"UNKNOWN FIELD: failure_state.{fk}")

    # 4. phase consistency + forward-only resume. The phase sequence is the
    #    order of produced_by phases under expected_artifacts.
    #    last_stable_phase must name a phase that actually produced something
    #    (a "stable" phase with no artifact is a stale claim). resume_phase
    #    MAY name a not-yet-produced phase — that is the next work — but when
    #    it names a known phase it must not precede last_stable_phase (a
    #    handoff moves forward, never re-litigates a passed gate).
    order = []
    for it in lists.get("expected_artifacts", []):
        if isinstance(it, dict) and it.get("produced_by"):
            if it["produced_by"] not in order:
                order.append(it["produced_by"])

    # Build set of valid phases (canonical + artifact-produced)
    valid_phases = set(PHASE_ORDER) | set(order)

    last, nxt = scalars.get("last_stable_phase"), scalars.get("resume_phase")
    phase = scalars.get("phase", "")

    # Validate phase names are known
    if phase and phase not in valid_phases:
        v.append(f"PHASE UNKNOWN: phase '{phase}' is not in canonical order "
                 f"{PHASE_ORDER} nor in produced_by {order}")
    if last and last not in valid_phases:
        v.append(f"PHASE UNKNOWN: last_stable_phase '{last}' is not in "
                 f"canonical order {PHASE_ORDER} nor in produced_by {order}")
    if nxt and nxt not in valid_phases:
        v.append(f"PHASE UNKNOWN: resume_phase '{nxt}' is not in canonical "
                 f"order {PHASE_ORDER} nor in produced_by {order}")
    if order and last and last not in order:
        v.append(f"PHASE UNKNOWN: last_stable_phase '{last}' names no phase "
                 f"in expected_artifacts.produced_by {order}")
    if order and last and nxt and last in order and nxt in order:
        if order.index(nxt) < order.index(last):
            v.append(f"RESUME BACKWARD: resume_phase '{nxt}' precedes "
                     f"last_stable_phase '{last}' in the phase order "
                     f"{order}")

    # 5. cross-references
    for key in ("required_sections", "size_bounds"):
        for it in lists.get(key, []):
            if isinstance(it, str):
                continue
            art = it.get("artifact", "")
            if art and art not in paths:
                v.append(f"UNKNOWN REFERENCE: {key} names artifact "
                         f"'{art}' not in expected_artifacts")

    # 6. regenerate vs not-to-touch must be disjoint
    reg = {it.get("path") if isinstance(it, dict) else it
           for it in lists.get("artifacts_to_regenerate", [])}
    froz = {it.get("path") if isinstance(it, dict) else it
            for it in lists.get("artifacts_not_to_touch", [])}
    for clash in sorted(x for x in reg & froz if x):
        v.append(f"CONTRACT CONTRADICTION: '{clash}' appears in both "
                 f"artifacts_to_regenerate and artifacts_not_to_touch")

    # 7. size bounds sane
    for it in lists.get("size_bounds", []):
        if isinstance(it, str):
            continue
        lo_s, hi_s = it.get("min_bytes"), it.get("max_bytes")
        if not lo_s and not hi_s:
            v.append(f"SIZE BOUNDS ITEM: needs min_bytes or max_bytes: {it}")
            continue
        lo = hi = None
        if lo_s:
            lo, err = parse_size(lo_s, "min_bytes")
            if err:
                v.append(f"{err} (artifact '{it.get('artifact', '?')}')")
        if hi_s:
            hi, err = parse_size(hi_s, "max_bytes")
            if err:
                v.append(f"{err} (artifact '{it.get('artifact', '?')}')")
        if lo is not None and hi is not None and lo > hi:
            v.append(f"SIZE BOUNDS ITEM: min_bytes {lo_s} exceeds max_bytes "
                     f"{hi_s} (artifact '{it.get('artifact', '?')}')")
    return v


def check_text(text):
    """Full pipeline: parse + validate -> list of violations."""
    scalars, lists, dicts, errors = parse_contract(text)
    if errors:
        return [f"PARSE: {e}" for e in errors]
    return validate(scalars, lists, dicts)


def check_file(path):
    with open(path, encoding="utf-8") as fh:
        return check_text(fh.read())


# ---------------------------------------------------------------------------
# self-test — the repo's own valid/invalid guarantee (no fixtures needed
# beyond stdlib; runs anywhere, never touches the network)
# ---------------------------------------------------------------------------
VALID_CONTRACT = """\
contract_version: 1
task_id: T-9001
project: Sample Reporting Service
phase: build
status: completed
runtime_state: staged
last_stable_phase: build
resume_phase: ship
expected_artifacts:
  - path: reports/summary.md
    kind: file
    produced_by: build
  - path: site
    kind: directory
    produced_by: ship
required_sections:
  - artifact: reports/summary.md
    section: Definition of Done
    marker: "## Definition of Done"
size_bounds:
  - artifact: reports/summary.md
    min_bytes: 200
    max_bytes: 50K
tests:
  - name: summary renders
    command: python3 tools/render.py --check
evidence_refs:
  - ref: "render.py --check -> exit 0, sha256 a1b2 (log line 41)"
    proves: staged copy is byte-identical to local build
feedback_to_apply:
  - note: tighten the summary heading
    applied: yes
artifacts_to_regenerate:
  - path: reports/summary.md
artifacts_not_to_touch:
  - path: site
"""

def _with(text, drop=None, subs=()):
    if drop:
        # drop a top-level field; if it is a section, drop its indented block
        lines, out, skipping = text.splitlines(), [], False
        for ln in lines:
            if re.match(rf"^{re.escape(drop)}\b", ln):
                skipping = True
                continue
            if skipping and (not ln.strip() or ln.startswith((" ", "\t"))):
                continue
            skipping = False
            out.append(ln)
        text = "\n".join(out) + "\n"
    for old, new in subs:
        text = text.replace(old, new, 1)
    return text


def self_test():
    cases = []

    v = check_text(VALID_CONTRACT)
    cases.append(("valid contract passes", v == [], v))

    v = check_text(_with(VALID_CONTRACT, drop="resume_phase"))
    cases.append(("missing required field (resume_phase) fails",
                  any("resume_phase" in x for x in v), v))

    v = check_text(_with(VALID_CONTRACT, drop="last_stable_phase"))
    cases.append(("missing required field (last_stable_phase) fails",
                  any("last_stable_phase" in x for x in v), v))

    v = check_text(_with(VALID_CONTRACT,
                         subs=[("runtime_state: staged", "runtime_state: prod")]))
    cases.append(("bad runtime_state enum fails",
                  any("runtime_state" in x for x in v), v))

    v = check_text(_with(VALID_CONTRACT, subs=[
        ("last_stable_phase: build", "last_stable_phase: ship"),
        ("resume_phase: ship", "resume_phase: build")]))
    cases.append(("backward resume fails",
                  any("BACKWARD" in x for x in v), v))

    v = check_text(_with(VALID_CONTRACT,
                         subs=[("status: completed", "status: failed")]))
    cases.append(("failed without failure_state fails",
                  any("failure_state" in x for x in v), v))

    v = check_text(_with(VALID_CONTRACT,
                         subs=[("phase: build", "phase: unknown_review")]))
    cases.append(("unknown phase fails",
                  any("PHASE UNKNOWN" in x for x in v), v))

    v = check_text(_with(VALID_CONTRACT,
                         subs=[("resume_phase: ship", "resume_phase: unknown_stage")]))
    cases.append(("unknown resume_phase fails",
                  any("PHASE UNKNOWN" in x for x in v), v))

    v = check_text(_with(VALID_CONTRACT,
                         subs=[("last_stable_phase: build", "last_stable_phase: unknown_stage")]))
    cases.append(("unknown last_stable_phase fails",
                  any("PHASE UNKNOWN" in x for x in v), v))

    v = check_text(_with(VALID_CONTRACT, subs=[
        ("section: Definition of Done", "section: Notes"),
        ("artifact: reports/summary.md\n    section: Notes",
         "artifact: reports/nonexistent.md\n    section: Notes")]))
    cases.append(("required_sections naming an unknown artifact fails",
                  any("UNKNOWN REFERENCE" in x for x in v), v))

    v2 = check_text(_with(VALID_CONTRACT,
                          subs=[("min_bytes: 200", "min_bytes: 9M")]))
    cases.append(("min_bytes > max_bytes fails",
                  any("exceeds" in x for x in v2), v2))

    v = check_text(_with(VALID_CONTRACT, subs=[
        ("artifacts_not_to_touch:\n  - path: site",
         "artifacts_not_to_touch:\n  - path: reports/summary.md")]))
    cases.append(("regenerate vs freeze clash fails",
                  any("CONTRADICTION" in x for x in v), v))

    v = check_text(_with(VALID_CONTRACT,
                         subs=[("task_id: T-9001", "taskid: T-9001")]))
    cases.append(("typo'd required field fails as unknown+missing",
                  any("UNKNOWN FIELD" in x for x in v)
                  and any("task_id" in x for x in v), v))

    v = check_text(_with(VALID_CONTRACT, drop="size_bounds"))
    cases.append(("missing size_bounds section fails",
                  any("size_bounds" in x for x in v), v))

    passed = failed = 0
    for name, ok, detail in cases:
        mark = "PASS" if ok else "FAIL"
        passed += ok
        failed += not ok
        print(f"  [{mark}] {name}")
        if not ok and detail:
            for d in detail[:3]:
                print(f"         got: {d}")

    # repo examples (when present) - not shipped in generated kits
    ex = os.path.join(HERE, "..", "examples")
    if not os.path.isdir(ex):
        print("  [SKIP] repo examples not present (not shipped in kits)")
    else:
        for fname, want_ok in (("artifact-contract.valid.yaml", True),
                               ("artifact-contract.invalid.yaml", False)):
            p = os.path.join(ex, fname)
            if not os.path.isfile(p):
                print(f"  [FAIL] repo example {fname} missing")
                failed += 1
                continue
            v = check_file(p)
            ok = (not v) if want_ok else bool(v)
            mark = "PASS" if ok else "FAIL"
            passed += ok
            failed += not ok
            print(f"  [{mark}] repo example {fname} "
                  f"{'valid' if want_ok else 'invalid'} as expected")
            if not ok:
                for d in v[:5]:
                    print(f"         {d}")

    print(f"\n{passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


def main():
    args = sys.argv[1:]
    if "--self-test" in args or "--example-check" in args:
        print("check-artifact-contract — self-test")
        return self_test()
    if not args or args[0].startswith("-"):
        print(__doc__.strip())
        return 2
    path = args[0]
    violations = check_file(path)
    if violations:
        print(f"INVALID — {path}")
        for x in violations:
            print(f"  ✗ {x}")
        return 1
    print(f"VALID — {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
