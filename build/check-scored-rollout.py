#!/usr/bin/env python3
"""
check-scored-rollout.py — validator for the grouped scored-rollout contract
(choreography/scored-rollouts.md).

Dependency-free: Python 3 standard library only, zero network (the same
no-egress rule the build gates enforce). Reads a JSON Lines artifact and
enforces the Team6 scored-rollout contract:

  line 1      a run header (record_type: run)
  then        one group declaration (record_type: group) followed by exactly
              `expected_samples` sample records (record_type: sample)

The checker validates structure, cross-references, numeric/array shapes, the
per-sample token-length cap against the header `max_token_length`, the
evaluation-policy enum combination, the off-policy batch cap, and the
allocation-minima sum. It does NOT decode tokens, infer prompts, compute
advantages, normalise scores, or judge whether a score is good — those are
future adapter responsibilities, not contract responsibilities.

USAGE
  python3 build/check-scored-rollout.py <artifact.jsonl>   # validate a file
  python3 build/check-scored-rollout.py --self-test        # built-in pass/fail
  python3 build/check-scored-rollout.py --example-check    # repo examples

EXIT  0 = valid (or all self-tests/example checks behaved)   1 = invalid
"""

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

RUN_SCHEMA = "team6.scored_rollout/v1"
EVAL_HANDLING = {"STOP_TRAIN", "LIMIT_TRAIN", "NONE"}
MODES = {"train", "eval"}

HEADER_FIELDS = {
    "record_type", "schema", "run_id", "mode", "group_size",
    "max_token_length", "eval_handling", "eval_limit_ratio", "batch_size",
    "max_offpolicy_batches",
}
GROUP_FIELDS = {"record_type", "run_id", "group_id", "expected_samples",
                "min_batch_allocation"}
SAMPLE_FIELDS = {
    "record_type", "run_id", "group_id", "batch_id", "sample_index",
    "input_ref", "is_off_policy", "tokens", "mask", "score", "advantages",
    "inference_logprobs", "reference_logprobs",
}
# An opaque input reference must stay a reference: no transcript, no prompt.
INPUT_REF_MAX = 256


class _DupKey(Exception):
    """Raised by the JSON object hook when a duplicate key is seen."""

    def __init__(self, key):
        self.key = key


def _no_dup_pairs(pairs):
    seen = {}
    for key, value in pairs:
        if key in seen:
            raise _DupKey(key)
        seen[key] = value
    return seen


def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _is_num(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _finite(value):
    return _is_num(value) and math.isfinite(value)


def _parse(text):
    """JSONL text -> (records, violations). records = [(lineno, obj), ...]."""
    records = []
    violations = []
    for lineno, raw in enumerate(text.splitlines(), 1):
        if not raw.strip():
            continue
        try:
            obj = json.loads(raw, object_pairs_hook=_no_dup_pairs)
        except _DupKey as exc:
            violations.append(f"line {lineno}: DUPLICATE KEY '{exc.key}'")
            continue
        except ValueError as exc:
            violations.append(f"line {lineno}: NOT JSON ({exc})")
            continue
        if not isinstance(obj, dict):
            violations.append(f"line {lineno}: record must be a JSON object")
            continue
        records.append((lineno, obj))
    return records, violations


def _validate_header(header, lineno):
    v = []
    for key in sorted(set(header) - HEADER_FIELDS):
        v.append(f"line {lineno}: HEADER unknown field '{key}'")

    if header.get("schema") != RUN_SCHEMA:
        v.append(f"line {lineno}: HEADER schema must be '{RUN_SCHEMA}' "
                 f"(got {header.get('schema')!r})")
    if not (isinstance(header.get("run_id"), str) and header["run_id"]):
        v.append(f"line {lineno}: HEADER run_id must be a non-empty string")
    if header.get("mode") not in MODES:
        v.append(f"line {lineno}: HEADER mode must be one of {sorted(MODES)}")
    if not (_is_int(header.get("group_size")) and header["group_size"] > 0):
        v.append(f"line {lineno}: HEADER group_size must be a positive integer")
    if not (_is_int(header.get("max_token_length"))
            and header["max_token_length"] > 0):
        v.append(f"line {lineno}: HEADER max_token_length must be a positive "
                 f"integer")

    handling = header.get("eval_handling")
    if handling not in EVAL_HANDLING:
        v.append(f"line {lineno}: HEADER eval_handling must be one of "
                 f"{sorted(EVAL_HANDLING)}")
    ratio = header.get("eval_limit_ratio")
    if handling == "LIMIT_TRAIN":
        if not (_finite(ratio) and 0 < ratio <= 1):
            v.append(f"line {lineno}: HEADER eval_limit_ratio must be a finite "
                     f"number in (0, 1] when eval_handling is LIMIT_TRAIN")
    elif ratio is not None:
        v.append(f"line {lineno}: HEADER eval_limit_ratio must be null unless "
                 f"eval_handling is LIMIT_TRAIN")

    batch_size = header.get("batch_size")
    if not ((_is_int(batch_size) and batch_size > 0) or batch_size == "runtime"):
        v.append(f"line {lineno}: HEADER batch_size must be a positive integer "
                 f"or the literal 'runtime'")

    cap = header.get("max_offpolicy_batches")
    if not (_is_int(cap) and cap >= 0):
        v.append(f"line {lineno}: HEADER max_offpolicy_batches must be a "
                 f"non-negative integer")
    return v


def _validate_group(group, lineno):
    v = []
    for key in sorted(set(group) - GROUP_FIELDS):
        v.append(f"line {lineno}: GROUP unknown field '{key}'")
    if not (isinstance(group.get("group_id"), str) and group["group_id"]):
        v.append(f"line {lineno}: GROUP group_id must be a non-empty string")
    alloc = group.get("min_batch_allocation")
    if alloc is not None and not (_finite(alloc) and 0 <= alloc <= 1):
        v.append(f"line {lineno}: GROUP min_batch_allocation must be null or a "
                 f"finite number in [0, 1]")
    return v


def _validate_sample(sample, lineno, max_token_length=None):
    v = []
    for key in sorted(set(sample) - SAMPLE_FIELDS):
        v.append(f"line {lineno}: SAMPLE unknown field '{key}'")

    if not (isinstance(sample.get("batch_id"), str) and sample["batch_id"]):
        v.append(f"line {lineno}: SAMPLE batch_id must be a non-empty string")
    if not _is_int(sample.get("sample_index")):
        v.append(f"line {lineno}: SAMPLE sample_index must be an integer")
    if not isinstance(sample.get("is_off_policy"), bool):
        v.append(f"line {lineno}: SAMPLE is_off_policy must be a boolean")

    ref = sample.get("input_ref")
    if not (isinstance(ref, str) and ref):
        v.append(f"line {lineno}: SAMPLE input_ref must be a non-empty string")
    elif "\n" in ref or len(ref) > INPUT_REF_MAX:
        v.append(f"line {lineno}: SAMPLE input_ref must be an opaque reference, "
                 f"not a raw prompt or transcript")

    tokens = sample.get("tokens")
    token_len = None
    if not (isinstance(tokens, list) and tokens):
        v.append(f"line {lineno}: SAMPLE tokens must be a non-empty array")
    elif not all(_is_int(t) and t >= 0 for t in tokens):
        v.append(f"line {lineno}: SAMPLE tokens must be non-negative integers")
    else:
        token_len = len(tokens)
        if _is_int(max_token_length) and token_len > max_token_length:
            v.append(f"line {lineno}: SAMPLE tokens length {token_len} exceeds "
                     f"header max_token_length {max_token_length}")

    mask = sample.get("mask")
    if not isinstance(mask, list):
        v.append(f"line {lineno}: SAMPLE mask must be an array")
    elif not all(_is_int(m) and m in (0, 1) for m in mask):
        v.append(f"line {lineno}: SAMPLE mask must contain only 0 or 1")
    elif token_len is not None and len(mask) != token_len:
        v.append(f"line {lineno}: SAMPLE mask length must equal tokens length")

    if not _finite(sample.get("score")):
        v.append(f"line {lineno}: SAMPLE score must be a finite number")

    for field in ("advantages", "inference_logprobs", "reference_logprobs"):
        value = sample.get(field)
        if value is None:
            continue
        if not isinstance(value, list):
            v.append(f"line {lineno}: SAMPLE {field} must be null or an array")
        elif not all(_finite(x) for x in value):
            v.append(f"line {lineno}: SAMPLE {field} must contain only finite "
                     f"numbers")
        elif token_len is not None and len(value) != token_len:
            v.append(f"line {lineno}: SAMPLE {field} length must equal tokens "
                     f"length")
    return v


def validate_text(text):
    """Full pipeline: parse then validate -> list of violation strings."""
    records, violations = _parse(text)
    if violations:
        return violations
    if not records:
        return ["MISSING HEADER: the artifact has no records"]

    first_lineno, header = records[0]
    if header.get("record_type") != "run":
        violations.append(f"line {first_lineno}: HEADER: the first record must "
                          f"be a run header (record_type: run)")

    header_run_id = header.get("run_id")
    group_size = header.get("group_size") if _is_int(header.get("group_size")) \
        else None
    cap = header.get("max_offpolicy_batches") \
        if _is_int(header.get("max_offpolicy_batches")) else None
    header_max_tokens = header.get("max_token_length") \
        if _is_int(header.get("max_token_length")) else None

    if header.get("record_type") == "run":
        violations += _validate_header(header, first_lineno)

    groups = {}          # group_id -> {"lineno", "expected", "alloc"}
    group_order = []
    samples_by_group = {}
    off_policy_batches = set()
    current_group = None

    for lineno, obj in records[1:]:
        rtype = obj.get("record_type")
        if rtype == "run":
            violations.append(f"line {lineno}: only one run header is allowed, "
                              f"and it must be the first record")
            continue
        if rtype == "group":
            violations += _validate_group(obj, lineno)
            gid = obj.get("group_id")
            if isinstance(gid, str) and gid:
                if gid in groups:
                    violations.append(f"line {lineno}: GROUP duplicate group_id "
                                      f"'{gid}'")
                else:
                    groups[gid] = {
                        "lineno": lineno,
                        "expected": obj.get("expected_samples"),
                        "alloc": obj.get("min_batch_allocation"),
                    }
                    group_order.append(gid)
            if obj.get("run_id") != header_run_id:
                violations.append(f"line {lineno}: GROUP run_id must match the "
                                  f"header run_id {header_run_id!r}")
            expected = obj.get("expected_samples")
            if group_size is not None and expected != group_size:
                violations.append(f"line {lineno}: GROUP expected_samples must "
                                  f"equal the header group_size {group_size}")
            current_group = gid
            if isinstance(gid, str):
                samples_by_group.setdefault(gid, [])
            continue
        if rtype == "sample":
            violations += _validate_sample(obj, lineno,
                                           header_max_tokens)
            if obj.get("run_id") != header_run_id:
                violations.append(f"line {lineno}: SAMPLE run_id must match the "
                                  f"header run_id {header_run_id!r}")
            gid = obj.get("group_id")
            if gid not in groups:
                violations.append(f"line {lineno}: SAMPLE references undeclared "
                                  f"group {gid!r}")
            else:
                if gid != current_group:
                    violations.append(f"line {lineno}: SAMPLE for group {gid!r} "
                                      f"must follow its group declaration")
                samples_by_group.setdefault(gid, []).append(obj)
                if obj.get("is_off_policy") is True:
                    batch = obj.get("batch_id")
                    if isinstance(batch, str) and batch:
                        off_policy_batches.add(batch)
            continue
        violations.append(f"line {lineno}: unknown record_type {rtype!r}")

    # Per-group cardinality and index coverage.
    for gid in group_order:
        group = groups[gid]
        entries = samples_by_group.get(gid, [])
        expected = group["expected"]
        if _is_int(expected) and len(entries) != expected:
            violations.append(
                f"GROUP '{gid}': cardinality — declared expected_samples="
                f"{expected} but found {len(entries)} sample(s)")
        indexes = [s.get("sample_index") for s in entries
                   if _is_int(s.get("sample_index"))]
        if len(set(indexes)) != len(indexes):
            violations.append(f"GROUP '{gid}': duplicate sample_index values")
        if _is_int(expected) and expected > 0:
            want = set(range(expected))
            got = set(indexes)
            if got != want:
                violations.append(
                    f"GROUP '{gid}': index coverage — expected indexes "
                    f"{sorted(want)}, got {sorted(got)}")

    # Allocation minima must not sum above 1.
    alloc_total = sum(g["alloc"] for g in groups.values()
                      if _finite(g["alloc"]))
    if alloc_total > 1:
        violations.append(f"ALLOCATION: min_batch_allocation sum {alloc_total} "
                          f"exceeds 1")

    # Off-policy cap.
    if cap is not None:
        if any(s.get("is_off_policy") is True
               for entries in samples_by_group.values() for s in entries):
            if cap == 0:
                violations.append("OFF-POLICY: an off-policy sample is present "
                                  "but max_offpolicy_batches is 0")
            elif len(off_policy_batches) > cap:
                violations.append(
                    f"OFF-POLICY: {len(off_policy_batches)} distinct off-policy "
                    f"batch_id value(s) exceed max_offpolicy_batches={cap}")
    return violations


def check_file(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return validate_text(fh.read()), None
    except OSError as exc:
        return [], f"unreadable: {exc}"


# ---------------------------------------------------------------------------
# self-test — built-in pass/fail guarantee (no fixtures required)
# ---------------------------------------------------------------------------
def _hdr(**kw):
    d = {"record_type": "run", "schema": RUN_SCHEMA, "run_id": "r1",
         "mode": "train", "group_size": 2, "max_token_length": 8,
         "eval_handling": "NONE", "eval_limit_ratio": None, "batch_size": 2,
         "max_offpolicy_batches": 1}
    d.update(kw)
    return d


def _grp(gid, expected=2, alloc=0.5, run="r1"):
    return {"record_type": "group", "run_id": run, "group_id": gid,
            "expected_samples": expected, "min_batch_allocation": alloc}


def _smp(gid, index, batch="b1", off=False, run="r1", tokens=None, mask=None,
         score=0.5, adv=None, ilp=None, rlp=None, iref=None):
    return {
        "record_type": "sample", "run_id": run, "group_id": gid,
        "batch_id": batch, "sample_index": index,
        "input_ref": iref or f"inputs/{gid}-{index}", "is_off_policy": off,
        "tokens": [1, 2] if tokens is None else tokens,
        "mask": [1, 1] if mask is None else mask, "score": score,
        "advantages": adv, "inference_logprobs": ilp,
        "reference_logprobs": rlp,
    }


def _jsonl(*objs):
    return "\n".join(json.dumps(o) for o in objs) + "\n"


BASE = _jsonl(_hdr(), _grp("g1"), _smp("g1", 0, batch="b1"),
              _smp("g1", 1, batch="b2", off=True, tokens=[3], mask=[1],
                   score=0.1, adv=[0.2]))


def self_test():
    cases = []

    cases.append(("valid input passes", BASE, True))

    cases.append(("missing header fails",
                  _jsonl(_grp("g1"), _smp("g1", 0), _smp("g1", 1)), False))

    bad_unknown = _smp("g1", 0)
    bad_unknown["extra_field"] = 1
    cases.append(("unknown field fails",
                  _jsonl(_hdr(), _grp("g1"), bad_unknown, _smp("g1", 1)), False))

    cases.append(("duplicate key fails",
                  BASE.replace('"score": 0.5', '"score": 0.5, "score": 0.6', 1),
                  False))

    cases.append(("cardinality fails",
                  _jsonl(_hdr(), _grp("g1"), _smp("g1", 0)), False))

    cases.append(("index coverage fails",
                  _jsonl(_hdr(), _grp("g1"), _smp("g1", 0, batch="b1"),
                         _smp("g1", 0, batch="b2")), False))

    cases.append(("array lengths fail",
                  _jsonl(_hdr(), _grp("g1"),
                         _smp("g1", 0, tokens=[1, 2], mask=[1]),
                         _smp("g1", 1)), False))

    cases.append(("non-finite value fails",
                  BASE.replace('"score": 0.5', '"score": NaN', 1), False))

    cases.append(("eval policy combination fails",
                  _jsonl(_hdr(eval_handling="STOP_TRAIN", eval_limit_ratio=0.5),
                         _grp("g1"), _smp("g1", 0), _smp("g1", 1)), False))

    cases.append(("off-policy cap fails",
                  _jsonl(_hdr(max_offpolicy_batches=0), _grp("g1"),
                         _smp("g1", 0, batch="b1"),
                         _smp("g1", 1, batch="b2", off=True)), False))

    cases.append(("token length exceeds cap fails",
                  _jsonl(_hdr(max_token_length=2), _grp("g1"),
                         _smp("g1", 0, tokens=[1, 2, 3], mask=[1, 1, 1]),
                         _smp("g1", 1)), False))

    cases.append(("allocation sum fails",
                  _jsonl(_hdr(), _grp("g1", alloc=0.6), _smp("g1", 0),
                         _smp("g1", 1), _grp("g2", alloc=0.6), _smp("g2", 0),
                         _smp("g2", 1)), False))

    passed = failed = 0
    print("check-scored-rollout — self-test")
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
    """Validate the repo's valid/invalid fixtures expect their verdicts."""
    roots = [os.path.join(HERE, "examples"),
             os.path.join(HERE, "..", "examples")]
    ex = next((r for r in roots if os.path.isdir(r)), None)
    if ex is None:
        print("  [SKIP] scored-rollout examples are not present")
        return 0
    passed = failed = 0
    print("check-scored-rollout — example-check")
    for fname, want_ok in (("scored-rollout-group.valid.jsonl", True),
                           ("scored-rollout-group.invalid.jsonl", False)):
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
