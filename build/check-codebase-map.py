#!/usr/bin/env python3
"""
check-codebase-map.py — structural validator for the codebase-map snapshot
contract (choreography/codebase-map.md).

Dependency-free: Python 3 stdlib only, zero network, no writes. It reads one
JSON snapshot and enforces the rules documented in the contract:

  1. JSON parses to a single object          6. Node/Leaf grammar
  2. required top-level fields present       7. relative, unique path identity
  3. contract token + version == 1           8. included_roots are relative
  4. enums (source_kind, measure, sort,      9. unknown fields fail
     algorithm, leaf color)
  5. sort is declared and matches the actual children order

The declared `sort` policy is compared against the actual `children` order of
every `Node` (contract § Child order): the first out-of-order adjacent pair is
reported once per offending node as an `ORDER:` violation.

USAGE
  python3 build/check-codebase-map.py <snapshot.json>   # validate a snapshot
  python3 build/check-codebase-map.py --self-test       # the repo's own cases

EXIT  0 = valid snapshot (all self-test cases pass)
      1 = invalid snapshot (violations listed)
      2 = usage error (no snapshot path given)
      3 = unreadable input (path missing or not readable)

An unreadable input is reported under a distinct `UNREADABLE` banner and never
as an invalid snapshot: 3 means the input could not be read, so its contents are
unknown; 1 means it was read and rejected by the contract.
"""

import contextlib
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

CONTRACT_TOKEN = "team6-codebase-map"
CONTRACT_VERSION = 1

# Exit codes: callers distinguish operator misuse (2) and unavailable input (3)
# from a snapshot the contract actually rejected (1).
EXIT_VALID = 0
EXIT_INVALID = 1
EXIT_USAGE = 2
EXIT_UNREADABLE = 3

# check_file outcomes.
STATUS_VALID = "valid"
STATUS_INVALID = "invalid"
STATUS_UNREADABLE = "unreadable"

SOURCE_KIND_ENUM = ("synthetic", "repository-snapshot")
MEASURE_ENUM = ("bytes", "lines")
SORT_ENUM = ("lexical", "size-desc", "size-asc")
ALGORITHM_ENUM = ("t6-squarified-v1",)
COLOR_ENUM = ("blue", "green", "amber", "slate", "violet", "red", "unknown")

TOP_KEYS = {
    "contract", "version", "source_kind", "included_roots",
    "excluded_patterns", "measure", "sort", "generated_at", "provenance",
    "rendering", "tree",
}
TOP_REQUIRED = (
    "contract", "version", "source_kind", "included_roots",
    "excluded_patterns", "measure", "sort", "generated_at", "provenance",
    "rendering", "tree",
)
NODE_KEYS = {"kind", "label", "path", "children"}
LEAF_KEYS = {"kind", "label", "path", "size", "color"}
PROVENANCE_KEYS = {"kind", "ref", "note"}
RENDERING_KEYS = {"algorithm"}


# ---------------------------------------------------------------------------
# path identity
# ---------------------------------------------------------------------------

def path_violation(path, where, allow_root_empty=True):
    """Return an error string if `path` is not a normalized relative identity
    (or the root's empty string), else None."""
    if not isinstance(path, str):
        return f"{where}: path must be a string (got {type(path).__name__})"
    if path == "":
        if allow_root_empty and where == "tree":
            return None                  # root's empty path is valid
        elif not allow_root_empty:
            return f"{where}: path must be a non-empty relative path"
    elif where == "tree":
        return f"{where}: root path must be empty string (got '{path}')"
    if path.startswith("/"):
        return f"{where}: absolute path is invalid ('{path}')"
    if path.startswith("\\") or "\\" in path:
        return f"{where}: backslash path is invalid ('{path}')"
    if path.startswith("~"):
        return f"{where}: home-relative path is invalid ('{path}')"
    if "//" in path:
        return f"{where}: path is not normalized ('{path}')"
    if ":" in path:
        return f"{where}: drive-letter path is invalid ('{path}')"
    for seg in path.split("/"):
        if seg in ("", ".", ".."):
            return f"{where}: path is not normalized ('{path}')"
    return None


# ---------------------------------------------------------------------------
# validation
# ---------------------------------------------------------------------------

def validate(doc):
    """Return a list of violation strings (empty = valid)."""
    v = []
    if not isinstance(doc, dict):
        return ["DOCUMENT: top level must be a JSON object"]

    # 2. required top-level fields present + non-empty
    #    (excluded_patterns is required present but MAY be an empty list —
    #     an explicit empty list states "nothing was excluded".)
    for key in TOP_REQUIRED:
        if key not in doc:
            v.append(f"MISSING REQUIRED FIELD: '{key}' is absent")
        elif key == "excluded_patterns":
            if not isinstance(doc[key], list):
                v.append("TYPE: 'excluded_patterns' must be a list "
                         "(use [] when nothing was excluded)")
        elif doc[key] in ("", None, [], {}):
            v.append(f"MISSING REQUIRED FIELD: '{key}' is empty")

    # 9. unknown top-level fields
    for key in sorted(set(doc) - TOP_KEYS):
        v.append(f"UNKNOWN FIELD: '{key}'")

    # 3. contract token + version
    if doc.get("contract") not in (None, "") and doc.get("contract") != CONTRACT_TOKEN:
        v.append(f"CONTRACT: 'contract' must be '{CONTRACT_TOKEN}' "
                 f"(got '{doc.get('contract')}')")
    ver = doc.get("version")
    if ver is not None and ver != "":
        if isinstance(ver, bool) or not isinstance(ver, int):
            v.append(f"VERSION: 'version' must be integer {CONTRACT_VERSION} "
                     f"(got {ver!r})")
        elif ver != CONTRACT_VERSION:
            v.append(f"VERSION: unsupported version {ver} "
                     f"(this checker accepts {CONTRACT_VERSION})")

    # 4. enums
    sk = doc.get("source_kind")
    if sk not in (None, "") and sk not in SOURCE_KIND_ENUM:
        v.append(f"ENUM: source_kind '{sk}' not in {list(SOURCE_KIND_ENUM)}")
    me = doc.get("measure")
    if me not in (None, "") and me not in MEASURE_ENUM:
        v.append(f"ENUM: measure '{me}' not in {list(MEASURE_ENUM)}")
    # 5. ordering policy declared
    so = doc.get("sort")
    if so not in (None, "") and so not in SORT_ENUM:
        v.append(f"ENUM: sort '{so}' not in {list(SORT_ENUM)}")

    # included_roots / excluded_patterns shape (F2: enforce source-bounded)
    inc = doc.get("included_roots")
    if isinstance(inc, list):
        if not inc:
            v.append("MISSING REQUIRED FIELD: 'included_roots' must have >= 1 entry")
        for i, p in enumerate(inc):
            err = path_violation(p, f"included_roots[{i}]")
            if err or p == "":
                v.append(err or f"included_roots[{i}]: root must be a non-empty "
                                f"relative path")
    elif inc is not None and inc != "":
        v.append("TYPE: 'included_roots' must be a list")
    # NOTE: the wrong-type case for 'excluded_patterns' is reported once, in the
    # required-field pass above. Re-checking it here duplicated the message.
    exc = doc.get("excluded_patterns")
    # F2: check each excluded pattern is relative/short
    if isinstance(exc, list):
        for i, p in enumerate(exc):
            if p and (p.startswith("/") or "\\" in p or p.startswith("~")):
                v.append(f"excluded_patterns[{i}]: must be relative/short (got '{p}')")

    # provenance object (F2: enforce source-boundedness)
    prov = doc.get("provenance")
    if isinstance(prov, dict):
        for req in ("kind", "ref"):
            if not prov.get(req):
                v.append(f"MISSING REQUIRED FIELD: provenance.{req} is required")
        # F2: ref must be relative/short, not absolute instance path
        ref = prov.get("ref", "")
        if ref and (ref.startswith("/") or "\\" in ref or ref.startswith("~")):
            v.append(f"PROVENANCE.ref: must be relative/short (got '{ref}')")
        for key in sorted(set(prov) - PROVENANCE_KEYS):
            v.append(f"UNKNOWN FIELD: provenance.{key}")
    elif prov not in (None, ""):
        v.append("TYPE: 'provenance' must be an object")

    # generated_at: must be short string, not absolute path (F2)
    gen = doc.get("generated_at")
    if gen and isinstance(gen, str) and (gen.startswith("/") or "\\" in gen or gen.startswith("~")):
        v.append(f"GENERATED_AT: must be relative/short (got '{gen}')")

    # rendering object + algorithm enum
    rend = doc.get("rendering")
    if isinstance(rend, dict):
        algo = rend.get("algorithm")
        if not algo:
            v.append("MISSING REQUIRED FIELD: rendering.algorithm is required")
        elif algo not in ALGORITHM_ENUM:
            v.append(f"ENUM: rendering.algorithm '{algo}' not in "
                     f"{list(ALGORITHM_ENUM)}")
        for key in sorted(set(rend) - RENDERING_KEYS):
            v.append(f"UNKNOWN FIELD: rendering.{key}")
    elif rend not in (None, ""):
        v.append("TYPE: 'rendering' must be an object")

    # 6/7. tree grammar + path identity
    tree = doc.get("tree")
    if tree is None or tree == "":
        v.append("MISSING REQUIRED FIELD: 'tree' is required")
    else:
        if not isinstance(tree, dict) or tree.get("kind") != "Node":
            v.append("TREE: root entity must be a Node")
        _walk(tree, "tree", 0, v, seen=set())
        # 5/11. the declared policy is compared against the actual order
        if so in SORT_ENUM:
            check_order(tree, so, v)

    return v


def _walk(entity, where, depth, v, seen):
    if not isinstance(entity, dict):
        v.append(f"{where}: entity must be an object")
        return
    kind = entity.get("kind")
    if kind == "Node":
        for key in sorted(set(entity) - NODE_KEYS):
            v.append(f"{where}: unknown field '{key}'")
        for req in ("label", "path", "children"):
            if req not in entity:
                v.append(f"{where}: Node missing required field '{req}'")
        kids = entity.get("children")
        if not isinstance(kids, list):
            v.append(f"{where}: Node 'children' must be a list")
        elif not kids:
            v.append(f"{where}: Node 'children' must be non-empty "
                     f"(empty directories are omitted in v1)")
        else:
            for i, kid in enumerate(kids):
                _walk(kid, f"{where}.children[{i}]", depth + 1, v, seen)
    elif kind == "Leaf":
        for key in sorted(set(entity) - LEAF_KEYS):
            v.append(f"{where}: unknown field '{key}'")
        for req in ("label", "path", "size", "color"):
            if req not in entity:
                v.append(f"{where}: Leaf missing required field '{req}'")
        size = entity.get("size")
        if "size" in entity:
            if isinstance(size, bool) or not isinstance(size, int):
                v.append(f"{where}: size must be a non-negative integer "
                         f"(got {size!r})")
            elif size < 0:
                v.append(f"{where}: size must be non-negative (got {size})")
        color = entity.get("color")
        if "color" in entity and color not in COLOR_ENUM:
            v.append(f"{where}: color '{color}' not in {list(COLOR_ENUM)}")
    else:
        v.append(f"{where}: kind must be 'Node' or 'Leaf' (got {kind!r})")
        return

    # label must be short text (F2: source-bounded)
    label = entity.get("label")
    if "label" in entity and (not isinstance(label, str) or label == ""):
        v.append(f"{where}: label must be a non-empty string")
    elif "label" in entity:
        if label.startswith("/") or "\\" in label or label.startswith("~"):
            v.append(f"{where}: label must be relative/short (got '{label}')")

    # path identity + duplicates
    if "path" in entity:
        path = entity.get("path")
        err = path_violation(path, where)
        if err:
            v.append(err)
        elif path == "":
            if depth != 0:
                v.append(f"{where}: only the root may have an empty path")
        else:
            if path in seen:
                v.append(f"{where}: duplicate identity '{path}' "
                         f"(already declared elsewhere)")
            else:
                seen.add(path)


# ---------------------------------------------------------------------------
# child order — the declared `sort` policy checked against the actual order
# (contract § Child order)
# ---------------------------------------------------------------------------

def effective_size(entity):
    """Subtree size in the declared measure: a `Leaf` contributes its `size`;
    a `Node` contributes the sum of its descendant leaves' `size` values.

    Grammar violations are reported by `_walk`, so an unreadable size counts
    as 0 here rather than adding a second, duplicate complaint.
    """
    if not isinstance(entity, dict):
        return 0
    if entity.get("kind") == "Leaf":
        size = entity.get("size")
        if isinstance(size, bool) or not isinstance(size, int) or size < 0:
            return 0
        return size
    return sum(effective_size(k) for k in (entity.get("children") or []))


def order_key(entity, policy):
    """The comparable key for one child under `policy` (§ Child order)."""
    label = entity.get("label")
    path = entity.get("path")
    if policy == "lexical":
        return (label, path)              # code-point, case-sensitive
    size = effective_size(entity)
    if policy == "size-desc":
        return (-size, label, path)
    return (size, label, path)            # size-asc


def order_key_text(entity, policy):
    """The key as printed in an `ORDER:` violation: the label, or the area."""
    if policy == "lexical":
        return entity.get("label")
    return effective_size(entity)


def check_order(entity, policy, v, where="tree"):
    """Enforce `policy` against the actual `children` order, recursively.

    One violation per non-conforming Node: the node's path and its first
    out-of-order adjacent pair. A Node whose grammar is already broken is
    skipped — `_walk` reports those.
    """
    if not isinstance(entity, dict) or entity.get("kind") != "Node":
        return
    kids = entity.get("children")
    if not isinstance(kids, list):
        return
    comparable = all(
        isinstance(k, dict) and isinstance(k.get("label"), str)
        and isinstance(k.get("path"), str)
        and (k.get("kind") == "Node"
             or (k.get("kind") == "Leaf"
                 and isinstance(k.get("size"), int)
                 and not isinstance(k.get("size"), bool)))
        for k in kids)
    if comparable:
        keys = [order_key(k, policy) for k in kids]
        for i in range(len(keys) - 1):
            if keys[i] > keys[i + 1]:
                a, b = kids[i], kids[i + 1]
                # The root's declared path is the empty string, so the message
                # uses the `tree` designator `_walk` already prints for it.
                node_path = entity.get("path") or where
                v.append(
                    f"ORDER: {node_path}: '{a.get('label')}' "
                    f"({order_key_text(a, policy)}) precedes "
                    f"'{b.get('label')}' ({order_key_text(b, policy)}) "
                    f"under sort '{policy}'")
                break
    for i, kid in enumerate(kids):
        check_order(kid, policy, v, f"{where}.children[{i}]")


def check_file(path):
    """Return (status, violations, doc).

    Only a readable snapshot can be STATUS_INVALID: an unreadable path yields
    STATUS_UNREADABLE with a READ violation, while a file that is readable but
    not valid JSON (or that breaks a contract rule) stays STATUS_INVALID.
    """
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        return STATUS_UNREADABLE, [f"READ: {exc}"], None
    try:
        doc = json.loads(text)
    except json.JSONDecodeError as exc:
        return STATUS_INVALID, [f"PARSE: invalid JSON ({exc})"], None
    violations = validate(doc)
    return (STATUS_VALID if not violations else STATUS_INVALID), violations, doc


def counts(doc):
    """(node_count, leaf_count) for a doc whose tree parsed."""
    nodes = leaves = 0

    def walk(e):
        nonlocal nodes, leaves
        if not isinstance(e, dict):
            return
        if e.get("kind") == "Node":
            nodes += 1
            for k in e.get("children", []) or []:
                walk(k)
        elif e.get("kind") == "Leaf":
            leaves += 1

    walk(doc.get("tree"))
    return nodes, leaves


# ---------------------------------------------------------------------------
# self-test — the repo's own valid/invalid guarantee, stdlib only
# ---------------------------------------------------------------------------

VALID_SNAPSHOT = """\
{
  "contract": "team6-codebase-map",
  "version": 1,
  "source_kind": "synthetic",
  "included_roots": ["src"],
  "excluded_patterns": [],
  "measure": "lines",
  "sort": "lexical",
  "generated_at": "2026-09-15T00:00:00Z",
  "provenance": {"kind": "synthetic-fixture", "ref": "inline:valid"},
  "rendering": {"algorithm": "t6-squarified-v1"},
  "tree": {"kind": "Node", "label": "src", "path": "",
           "children": [
             {"kind": "Leaf", "label": "a.py", "path": "src/a.py",
              "size": 0, "color": "unknown"},
             {"kind": "Node", "label": "pkg", "path": "src/pkg",
              "children": [
                {"kind": "Leaf", "label": "b.py", "path": "src/pkg/b.py",
                 "size": 12, "color": "green"}]}]}
}
"""

ONE_LEAF_SNAPSHOT = """\
{
  "contract": "team6-codebase-map", "version": 1,
  "source_kind": "synthetic", "included_roots": ["solo"],
  "excluded_patterns": [], "measure": "bytes", "sort": "lexical",
  "generated_at": "t",
  "provenance": {"kind": "synthetic-fixture", "ref": "inline:one-leaf"},
  "rendering": {"algorithm": "t6-squarified-v1"},
  "tree": {"kind": "Node", "label": "solo", "path": "",
           "children": [{"kind": "Leaf", "label": "only.txt",
                         "path": "solo/only.txt", "size": 1,
                         "color": "slate"}]}
}
"""


# Child-order fixtures (§ Child order): the same three children (areas 300,
# 100, and a Node summing to 200) emitted in each policy's required order, so a
# policy's passing and failing case differ by nothing but the emitted order.
ORDER_CHILDREN = {
    "a.txt": {"kind": "Leaf", "label": "a.txt", "path": "src/a.txt",
              "size": 300, "color": "blue"},
    "b.txt": {"kind": "Leaf", "label": "b.txt", "path": "src/b.txt",
              "size": 100, "color": "green"},
    "dir": {"kind": "Node", "label": "dir", "path": "src/dir",
            "children": [{"kind": "Leaf", "label": "c.txt",
                          "path": "src/dir/c.txt", "size": 200,
                          "color": "amber"}]},
}
ORDER_EXPECTED = {
    "lexical": ["a.txt", "b.txt", "dir"],
    "size-desc": ["a.txt", "dir", "b.txt"],
    "size-asc": ["b.txt", "dir", "a.txt"],
}


def order_snapshot(policy, names):
    """A snapshot whose root children are `names`, in that order, under
    `policy`."""
    doc = json.loads(VALID_SNAPSHOT)
    doc["sort"] = policy
    doc["tree"]["children"] = [json.loads(json.dumps(ORDER_CHILDREN[n]))
                               for n in names]
    return doc


def _sub(text, old, new):
    return text.replace(old, new, 1)


def self_test():
    cases = []  # (name, ok, detail)

    doc = json.loads(VALID_SNAPSHOT)
    v = validate(doc)
    cases.append(("valid snapshot passes", v == [], v))

    v = validate(json.loads(ONE_LEAF_SNAPSHOT))
    cases.append(("one-leaf snapshot passes", v == [], v))

    # missing required field (sort)
    d = json.loads(_sub(VALID_SNAPSHOT, '"sort": "lexical",\n', ""))
    v = validate(d)
    cases.append(("missing required field (sort) fails",
                  any("'sort'" in x for x in v), v))

    # undeclared ordering policy (sort set to an unknown token)
    d = json.loads(_sub(VALID_SNAPSHOT, '"sort": "lexical"', '"sort": "guess"'))
    v = validate(d)
    cases.append(("undeclared ordering policy fails",
                  any("sort" in x and "ENUM" in x for x in v), v))

    # unknown algorithm enum
    d = json.loads(_sub(VALID_SNAPSHOT, '"t6-squarified-v1"', '"unknown-mode"'))
    v = validate(d)
    cases.append(("unknown algorithm enum fails",
                  any("algorithm" in x and "ENUM" in x for x in v), v))

    # invalid kind
    d = json.loads(_sub(VALID_SNAPSHOT, '"kind": "Node", "label": "pkg"',
                        '"kind": "Directory", "label": "pkg"'))
    v = validate(d)
    cases.append(("invalid kind fails",
                  any("kind must be" in x for x in v), v))

    # negative size
    d = json.loads(_sub(VALID_SNAPSHOT, '"size": 12', '"size": -3'))
    v = validate(d)
    cases.append(("negative size fails",
                  any("size must be non-negative" in x for x in v), v))

    # non-integer size
    d = json.loads(_sub(VALID_SNAPSHOT, '"size": 12', '"size": 3.5'))
    v = validate(d)
    cases.append(("non-integer size fails",
                  any("non-negative integer" in x for x in v), v))

    # absolute path
    d = json.loads(_sub(VALID_SNAPSHOT, '"path": "src/a.py"',
                        '"path": "/opt/synthetic/src/a.py"'))
    v = validate(d)
    cases.append(("absolute path fails",
                  any("absolute path is invalid" in x for x in v), v))

    # duplicate identity
    d = json.loads(_sub(VALID_SNAPSHOT, '"path": "src/pkg/b.py"',
                        '"path": "src/a.py"'))
    v = validate(d)
    cases.append(("duplicate identity fails",
                  any("duplicate identity" in x for x in v), v))

    # unknown color token
    d = json.loads(_sub(VALID_SNAPSHOT, '"color": "green"', '"color": "mustard"'))
    v = validate(d)
    cases.append(("unknown color token fails",
                  any("color" in x and "ENUM" not in x for x in v), v))

    # empty children (empty directory must be omitted, not represented)
    d = json.loads(_sub(
        VALID_SNAPSHOT,
        '"children": [\n                {"kind": "Leaf", "label": "b.py", "path": "src/pkg/b.py",\n                 "size": 12, "color": "green"}]',
        '"children": []'))
    v = validate(d)
    cases.append(("empty children array fails",
                  any("non-empty" in x for x in v), v))

    # malformed JSON
    bad = VALID_SNAPSHOT.replace('"version": 1', '"version": 1,,')
    try:
        json.loads(bad)
        parse_failed = False
    except json.JSONDecodeError:
        parse_failed = True
    cases.append(("malformed JSON fails to parse", parse_failed, []))

    # unknown top-level field
    d = json.loads(_sub(VALID_SNAPSHOT, '"version": 1,',
                        '"version": 1, "extra_thing": true,'))
    v = validate(d)
    cases.append(("unknown top-level field fails",
                  any("UNKNOWN FIELD" in x for x in v), v))

    # child order (§ Child order): one correctly ordered snapshot per policy
    # (passes) and one unordered snapshot per policy (the decided outcome:
    # a hard ORDER failure).
    for policy in SORT_ENUM:
        ordered = ORDER_EXPECTED[policy]
        v = validate(order_snapshot(policy, ordered))
        cases.append((f"{policy}: correctly ordered children pass", v == [], v))
        v = validate(order_snapshot(policy, list(reversed(ordered))))
        cases.append((f"{policy}: unordered children fail",
                      any(x.startswith("ORDER: ") for x in v), v))

    # the violation reaches an operator through the same printer as any other
    # rejection, naming the node and the first out-of-order adjacent pair
    d = order_snapshot("lexical", list(reversed(ORDER_EXPECTED["lexical"])))
    bad = validate(d)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = report("inline:unordered", STATUS_INVALID, bad, d)
    out = buf.getvalue()
    expected_order = ("ORDER: tree: 'dir' (dir) precedes 'b.txt' (b.txt) "
                      "under sort 'lexical'")
    cases.append(("unordered snapshot exits 1 naming the first pair",
                  rc == EXIT_INVALID and expected_order in out,
                  [f"rc={rc}"] + bad))

    # a Node's area is its subtree sum, so a Node is ordered by its leaves
    d = json.loads(json.dumps(ORDER_CHILDREN))
    cases.append(("Node effective area is the subtree leaf sum",
                  effective_size(d["dir"]) == 200, [str(effective_size(d["dir"]))]))

    # no-argument usage: prints the usage text and exits 2
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = main([])
    usage = buf.getvalue()
    codes_documented = all(
        (f"EXIT  {n} =" in usage) or (f"\n      {n} =" in usage)
        for n in (EXIT_VALID, EXIT_INVALID, EXIT_USAGE, EXIT_UNREADABLE))
    cases.append(("no-argument usage exits 2 and documents all four codes",
                  rc == EXIT_USAGE and codes_documented,
                  [f"rc={rc}", f"usage documents codes: {codes_documented}"]))

    # unreadable input: a path that cannot be read exits 3, not 1
    missing = os.path.join(ROOT, "build", "self-test-missing", "snapshot.json")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = main([missing])
    out = buf.getvalue()
    cases.append(("unreadable input exits 3 under the UNREADABLE banner",
                  rc == EXIT_UNREADABLE and "UNREADABLE — " in out
                  and "INVALID" not in out, [f"rc={rc}", out.strip()]))

    status, uv, undoc = check_file(missing)
    cases.append(("unreadable input reports the unreadable status",
                  status == STATUS_UNREADABLE and bool(uv) and undoc is None, uv))

    # wrong-type excluded_patterns: the message is emitted exactly once
    d = json.loads(_sub(VALID_SNAPSHOT, '"excluded_patterns": []',
                        '"excluded_patterns": "oops"'))
    v = validate(d)
    dupes = [x for x in v if "excluded_patterns" in x and "must be a list" in x]
    cases.append(("wrong-type excluded_patterns reported exactly once",
                  len(dupes) == 1, [f"count={len(dupes)}"] + v))

    # exit-code mapping on the repo fixtures: 0 valid, 1 invalid
    ex = os.path.join(ROOT, "examples")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc_valid = main([os.path.join(ex, "codebase-map.valid.json")])
        rc_invalid = main([os.path.join(ex, "codebase-map.invalid.json")])
    cases.append(("repo fixtures map to exit 0 (valid) and 1 (invalid)",
                  rc_valid == EXIT_VALID and rc_invalid == EXIT_INVALID,
                  [f"valid rc={rc_valid}", f"invalid rc={rc_invalid}"]))

    passed = failed = 0
    for name, ok, detail in cases:
        mark = "PASS" if ok else "FAIL"
        passed += bool(ok)
        failed += not ok
        print(f"  [{mark}] {name}")
        if not ok and detail:
            for d in detail[:3]:
                print(f"         got: {d}")

    # repo fixtures
    for fname, want_ok in (("codebase-map.valid.json", True),
                           ("codebase-map.invalid.json", False)):
        p = os.path.join(ex, fname)
        if not os.path.isfile(p):
            print(f"  [FAIL] repo example {fname} missing")
            failed += 1
            continue
        _, v, _ = check_file(p)
        ok = (not v) if want_ok else bool(v)
        mark = "PASS" if ok else "FAIL"
        passed += bool(ok)
        failed += not ok
        print(f"  [{mark}] repo example {fname} "
              f"{'valid' if want_ok else 'invalid'} as expected")
        if not ok:
            for d in v[:5]:
                print(f"         {d}")

    print(f"\n{passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


def report(path, status, violations, doc):
    if status == STATUS_UNREADABLE:
        print(f"UNREADABLE — {path}")
        for x in violations:
            print(f"  x {x}")
        print("  input was not readable; no snapshot was validated")
        return EXIT_UNREADABLE
    if violations:
        print(f"INVALID — {path}")
        for x in violations:
            print(f"  x {x}")
        return EXIT_INVALID
    nodes, leaves = counts(doc)
    print(f"VALID — {path}")
    print(f"  contract: {doc.get('contract')}")
    print(f"  version: {doc.get('version')}")
    print(f"  source_kind: {doc.get('source_kind')}")
    print(f"  measure: {doc.get('measure')}")
    print(f"  sort: {doc.get('sort')}")
    print(f"  algorithm: {(doc.get('rendering') or {}).get('algorithm')}")
    print(f"  nodes: {nodes}  leaves: {leaves}")
    return EXIT_VALID


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if "--self-test" in args:
        print("check-codebase-map — self-test")
        return self_test()
    if not args or args[0].startswith("-"):
        print((__doc__ or "").strip())
        return EXIT_USAGE
    path = args[0]
    status, violations, doc = check_file(path)
    return report(path, status, violations, doc)


if __name__ == "__main__":
    sys.exit(main())
