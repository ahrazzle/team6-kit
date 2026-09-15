#!/usr/bin/env python3
"""
run-fixtures.py — the B05 catalog/router acceptance fixtures.

Five suites, each printed as [ok]/[FAIL] with a final verdict:

  catalog-search : a search returns compact cards, an exact local read path,
                   no body; limit and determinism hold
  fallback       : the FTS5 fast path and the JSON fallback produce identical
                   ordered results for the same catalog; cap saturation and a
                   forced fallback stay correct
  clean-room     : the installed layer runs in a fresh dir with no repo and no
                   FTS, resolves the read path on demand, and never reads a
                   body as a side effect of search
  package        : catalog, lock, and pack validate against their schemas and
                   pass hygiene (no absolute paths, digest-bound, 1:1 lock)
  provenance     : every entry maps to pack/source/license/provenance; the
                   lock covers the catalog; tampered/unknown/stale entries fail
                   closed and are not router-visible

USAGE
  python3 registry/catalog/run-fixtures.py

EXIT
  0 = all suites pass; 1 = one or more checks failed

Standard library only. No network, no third-party dependency.
"""

import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

CATALOG_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(CATALOG_DIR, "..", ".."))
MINI = os.path.join(CATALOG_DIR, "fixtures", "mini")
ROUTER_SCRIPT = os.path.join(CATALOG_DIR, "skill-catalog.py")
BUILDER_SCRIPT = os.path.join(CATALOG_DIR, "build-catalog.py")

SENTINEL = "SENTINEL_BODY"
_FINDINGS = []


def record(suite, name, ok, detail=""):
    _FINDINGS.append((suite, name, ok, detail))
    tag = "ok" if ok else "FAIL"
    line = f"  [{tag}] {name}"
    if detail and not ok:
        line += f" — {detail}"
    print(line)


def load_router_module():
    spec = importlib.util.spec_from_file_location("skill_catalog", ROUTER_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load router module from {ROUTER_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def digest_entries(entries):
    canonical = json.dumps(entries, sort_keys=True,
                           separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


# ---------------------------------------------------------------------------
# Minimal, dependency-free JSON Schema subset validator (type/required/
# properties/additionalProperties/items/enum/const/pattern/minLength/
# minItems/minProperties). Enough for the catalog's own schemas.
# ---------------------------------------------------------------------------
def validate_schema(schema, obj, path="$"):
    errs = []
    t = schema.get("type")
    if t == "object":
        if not isinstance(obj, dict):
            return [f"{path}: expected object"]
        if "minProperties" in schema and len(obj) < schema["minProperties"]:
            errs.append(f"{path}: needs >= {schema['minProperties']} properties")
        for req in schema.get("required", []):
            if req not in obj:
                errs.append(f"{path}: missing required '{req}'")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in obj:
                if key not in props:
                    errs.append(f"{path}: unexpected property '{key}'")
        for key, value in obj.items():
            if key in props:
                errs += validate_schema(props[key], value, f"{path}.{key}")
    elif t == "array":
        if not isinstance(obj, list):
            return [f"{path}: expected array"]
        if "minItems" in schema and len(obj) < schema["minItems"]:
            errs.append(f"{path}: needs >= {schema['minItems']} items")
        item = schema.get("items")
        if item:
            for i, entry in enumerate(obj):
                errs += validate_schema(item, entry, f"{path}[{i}]")
    elif t == "string":
        if not isinstance(obj, str):
            return [f"{path}: expected string"]
        if "minLength" in schema and len(obj) < schema["minLength"]:
            errs.append(f"{path}: shorter than minLength {schema['minLength']}")
        if "enum" in schema and obj not in schema["enum"]:
            errs.append(f"{path}: '{obj}' not in enum")
        if "const" in schema and obj != schema["const"]:
            errs.append(f"{path}: '{obj}' != const {schema['const']}")
        if "pattern" in schema and not re.search(schema["pattern"], obj):
            errs.append(f"{path}: '{obj}' fails pattern")
    elif t == "integer":
        if isinstance(obj, bool) or not isinstance(obj, int):
            errs.append(f"{path}: expected integer")
        elif "const" in schema and obj != schema["const"]:
            errs.append(f"{path}: {obj} != const {schema['const']}")
    return errs


def walk_strings(node):
    if isinstance(node, dict):
        for value in node.values():
            yield from walk_strings(value)
    elif isinstance(node, list):
        for value in node:
            yield from walk_strings(value)
    elif isinstance(node, str):
        yield node


# ---------------------------------------------------------------------------
# Suite: catalog-search
# ---------------------------------------------------------------------------
def suite_catalog_search(sc):
    router = sc.Router(os.path.join(MINI, "catalog.json"),
                       os.path.join(MINI, "packs"), MINI)
    res = router.search("pull request review", "all", 5, "json")
    cards = res["cards"]
    record("catalog-search", "query returns at least one card", bool(cards),
           "no cards returned")

    card = cards[0] if cards else {}
    for key in ("id", "name", "funnel", "pack", "source", "license",
                "provenance", "read_path"):
        record("catalog-search", f"card carries '{key}'", bool(card.get(key)),
               f"missing {key}")

    body_keys = {"body", "content", "text", "skill_body"}
    leaked = [k for c in cards for k in c if k in body_keys]
    record("catalog-search", "no card exposes a body field", not leaked,
           f"leaked keys: {leaked}")

    oversize = [k for c in cards for k, v in c.items()
                if isinstance(v, str) and len(v) > 300]
    record("catalog-search", "cards are compact (metadata only)", not oversize,
           f"oversize fields: {oversize}")

    sentinel = SENTINEL in json.dumps(cards)
    record("catalog-search", "no skill body text in results", not sentinel)

    resolved = all(os.path.isfile(os.path.join(MINI, c["read_path"]))
                   for c in cards)
    record("catalog-search", "every read_path resolves exactly", resolved)

    limited = router.search("review", "all", 1, "json")
    record("catalog-search", "limit is respected",
           len(limited["cards"]) <= 1, f"got {len(limited['cards'])}")

    a = router.search("architecture diagram", "all", 5, "json")["cards"]
    b = router.search("architecture diagram", "all", 5, "json")["cards"]
    record("catalog-search", "repeat runs are identical",
           json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True))

    empty = router.search("zzzquux", "all", 5, "json")
    record("catalog-search", "no-match query returns nothing", not empty["cards"])


# ---------------------------------------------------------------------------
# Suite: fallback
# ---------------------------------------------------------------------------
def suite_fallback(sc):
    router = sc.Router(os.path.join(MINI, "catalog.json"),
                       os.path.join(MINI, "packs"), MINI)
    queries = ["diagram architecture", "verify sources", "pull request",
               "review", "diagram-maker"]
    parity = True
    for query in queries:
        fts = router.search(query, "all", 3, "fts")
        js = router.search(query, "all", 3, "json")
        if [c["id"] for c in fts["cards"]] != [c["id"] for c in js["cards"]]:
            parity = False
        elif [c["score"] for c in fts["cards"]] != [c["score"] for c in js["cards"]]:
            parity = False
        elif fts["used"] != "fts" or js["used"] != "json":
            parity = False
    record("fallback", "fts and json engines agree (ids + scores)", parity)

    forced = router.search("diagram", "all", 3, "json")
    record("fallback", "forced json engine reports json",
           forced["used"] == "json")

    original_cap = sc.CANDIDATE_CAP
    try:
        sc.CANDIDATE_CAP = 1  # any multi-candidate match now saturates
        saturated = router.search("verification", "all", 3, "auto")
        record("fallback", "cap saturation falls back to json",
               saturated["used"] == "json",
               f"engine used: {saturated['used']}")
        js = router.search("verification", "all", 3, "json")
        record("fallback", "saturated auto equals json ordering",
               [c["id"] for c in saturated["cards"]]
               == [c["id"] for c in js["cards"]])
        try:
            router.search("verification", "all", 3, "fts")
            record("fallback", "forced fts fails closed when saturated", False,
                   "expected a fail-closed error")
        except ValueError:
            record("fallback", "forced fts fails closed when saturated", True)
    finally:
        sc.CANDIDATE_CAP = original_cap


# ---------------------------------------------------------------------------
# Suite: clean-room
# ---------------------------------------------------------------------------
def suite_clean_room():
    tmp = tempfile.mkdtemp(prefix="b05-cleanroom.")
    try:
        dest = os.path.join(tmp, "registry", "catalog")
        shutil.copytree(CATALOG_DIR, dest,
                        ignore=shutil.ignore_patterns("__pycache__"))
        router = os.path.join(dest, "skill-catalog.py")
        mini = os.path.join(dest, "fixtures", "mini")
        before = hashlib.sha256(
            open(os.path.join(mini, "catalog.json"), "rb").read()).hexdigest()

        def run(*extra):
            return subprocess.run(
                [sys.executable, router, "--root", mini,
                 "--catalog", os.path.join(mini, "catalog.json"),
                 "--packs-dir", os.path.join(mini, "packs")] + list(extra),
                capture_output=True, text=True, timeout=60)

        search = run("search", "all", "architecture diagram",
                     "--format", "json", "--engine", "json")
        record("clean-room", "installed layer runs without the repo",
               search.returncode == 0, search.stderr.strip())
        record("clean-room", "search output has no skill body",
               SENTINEL not in search.stdout)
        record("clean-room", "search output leaks no absolute path",
               tmp not in search.stdout and "/Users/" not in search.stdout)
        try:
            payload = json.loads(search.stdout)
            ok = payload["results"] and payload["results"][0]["read_path"]
        except (ValueError, KeyError, IndexError, TypeError):
            ok = False
        record("clean-room", "search returns a bounded read path", bool(ok))

        open_run = run("search", "creative", "diagram-maker",
                       "--format", "json", "--limit", "1", "--engine", "json",
                       "--open")
        record("clean-room", "read-on-demand --open returns the body",
               open_run.returncode == 0 and SENTINEL in open_run.stdout)

        after = hashlib.sha256(
            open(os.path.join(mini, "catalog.json"), "rb").read()).hexdigest()
        record("clean-room", "search does not mutate the catalog", before == after)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# Suite: package
# ---------------------------------------------------------------------------
_NET_RE = re.compile(
    r"^\s*(?:import|from)\s+(http\.client|urllib|requests|socket|ftplib|"
    r"smtplib|telnetlib|imaplib|poplib)\b", re.M)


def suite_package(sc):
    catalog = read_json(os.path.join(CATALOG_DIR, "catalog.json"))
    lock = read_json(os.path.join(CATALOG_DIR, "locks", "core.lock.json"))
    pack = read_json(os.path.join(CATALOG_DIR, "packs", "core.json"))

    for name, schema_file, obj in (
            ("catalog", "catalog.schema.json", catalog),
            ("lock", "lock.schema.json", lock),
            ("pack", "pack.schema.json", pack)):
        schema = read_json(os.path.join(CATALOG_DIR, "schemas", schema_file))
        errs = validate_schema(schema, obj)
        record("package", f"{name} validates against its schema", not errs,
               "; ".join(errs[:3]))

    bad = []
    for path, obj in (("catalog", catalog), ("lock", lock), ("pack", pack)):
        for s in walk_strings(obj):
            if s.startswith("/") or "/Users/" in s or ".." in s.split("/"):
                bad.append((path, s))
    record("package", "no absolute or escaping paths in artifacts", not bad,
           str(bad[:3]))

    pack_bytes = open(os.path.join(CATALOG_DIR, "packs", "core.json"), "rb").read()
    expect_pack = "sha256:" + hashlib.sha256(pack_bytes).hexdigest()
    record("package", "catalog packs the declared pack digest",
           catalog.get("pack_digest") == expect_pack)

    lock_ids = [e["id"] for e in lock["entries"]]
    cat_ids = [e["id"] for e in catalog["entries"]]
    record("package", "lock and catalog are 1:1", lock_ids == cat_ids,
           f"lock={len(lock_ids)} catalog={len(cat_ids)}")
    record("package", "lock digest matches the catalog",
           lock.get("catalog_digest") == digest_entries(catalog["entries"]))

    skill_root = pack["skill_root"]
    outside = [e["read_path"] for e in catalog["entries"]
               if not e["read_path"].startswith(skill_root + "/")]
    record("package", "every read_path is under the declared skill_root",
           not outside, str(outside[:3]))

    net = []
    for script in ("skill-catalog.py", "build-catalog.py"):
        src = open(os.path.join(CATALOG_DIR, script), encoding="utf-8").read()
        if _NET_RE.search(src):
            net.append(script)
    record("package", "router and generator carry no network primitives", not net)

    drift = subprocess.run(
        [sys.executable, BUILDER_SCRIPT, "--check"],
        capture_output=True, text=True, cwd=REPO_ROOT, timeout=120)
    record("package", "committed catalog matches regeneration (core)",
           drift.returncode == 0,
           (drift.stdout.strip().splitlines() or [""])[-1])

    drift_mini = subprocess.run(
        [sys.executable, BUILDER_SCRIPT, "--pack", "mini", "--root", MINI,
         "--packs-dir", os.path.join(MINI, "packs"), "--out", MINI, "--check"],
        capture_output=True, text=True, cwd=REPO_ROOT, timeout=120)
    record("package", "committed fixture catalog matches regeneration",
           drift_mini.returncode == 0)


# ---------------------------------------------------------------------------
# Suite: provenance
# ---------------------------------------------------------------------------
def _tamper_case(sc, catalog, lock, mutate, expect_kind, label):
    mutate(catalog)
    lock["catalog_digest"] = digest_entries(catalog["entries"])
    tmp = tempfile.mkdtemp(prefix="b05-prov.")
    try:
        os.makedirs(os.path.join(tmp, "locks"), exist_ok=True)
        os.makedirs(os.path.join(tmp, "packs"), exist_ok=True)
        with open(os.path.join(tmp, "catalog.json"), "w", encoding="utf-8") as fh:
            json.dump(catalog, fh)
        with open(os.path.join(tmp, "locks", "core.lock.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(lock, fh)
        shutil.copy(os.path.join(CATALOG_DIR, "packs", "core.json"),
                    os.path.join(tmp, "packs", "core.json"))
        router = sc.Router(os.path.join(tmp, "catalog.json"),
                           os.path.join(tmp, "packs"), REPO_ROOT)
        kinds = {kind for _id, kind, _r in router.excluded}
        ids_excluded = {_id for _id, _k, _r in router.excluded}
        target = catalog["entries"][0]["id"]
        record("provenance", label,
               target in ids_excluded and expect_kind in kinds,
               f"kinds={sorted(kinds)} target_excluded={target in ids_excluded}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def suite_provenance(sc):
    catalog = read_json(os.path.join(CATALOG_DIR, "catalog.json"))
    lock = read_json(os.path.join(CATALOG_DIR, "locks", "core.lock.json"))
    pack = read_json(os.path.join(CATALOG_DIR, "packs", "core.json"))
    funnels = set(pack["funnels"].keys())
    lock_prov = {e["provenance"] for e in lock["entries"]}

    problems = []
    for e in catalog["entries"]:
        if not all(e.get(f) for f in ("pack", "source", "license",
                                      "provenance", "read_path")):
            problems.append((e["id"], "incomplete provenance"))
            continue
        if e["pack"] != "core" or e["funnel"] not in funnels:
            problems.append((e["id"], "unclassified"))
        if e["provenance"] not in lock_prov:
            problems.append((e["id"], "not in lock"))
        if not os.path.isfile(os.path.join(REPO_ROOT, e["read_path"])):
            problems.append((e["id"], "stale read_path"))
    record("provenance", "every entry maps to pack/source/license/provenance",
           not problems, str(problems[:3]))

    router = sc.Router(os.path.join(CATALOG_DIR, "catalog.json"),
                       os.path.join(CATALOG_DIR, "packs"), REPO_ROOT)
    record("provenance", "the real catalog serves with zero exclusions",
           not router.excluded, str(router.excluded[:3]))
    record("provenance", "all catalog entries are router-visible",
           len(router.visible) == len(catalog["entries"]),
           f"visible={len(router.visible)} entries={len(catalog['entries'])}")

    base = json.loads(json.dumps(catalog))
    base_lock = json.loads(json.dumps(lock))
    _tamper_case(sc, json.loads(json.dumps(base)), json.loads(json.dumps(base_lock)),
                 lambda c: c["entries"][0].pop("license", None),
                 "missing-field", "missing-license entry fails closed")
    _tamper_case(sc, json.loads(json.dumps(base)), json.loads(json.dumps(base_lock)),
                 lambda c: c["entries"][0].update(pack="ghost"),
                 "unknown-pack", "unknown-pack entry fails closed")
    _tamper_case(sc, json.loads(json.dumps(base)), json.loads(json.dumps(base_lock)),
                 lambda c: c["entries"][0].update(funnel="ghost"),
                 "unclassified", "unclassified entry fails closed")
    _tamper_case(sc, json.loads(json.dumps(base)), json.loads(json.dumps(base_lock)),
                 lambda c: c["entries"][0].update(read_path="skills/nope/SKILL.md"),
                 "stale", "stale read_path entry fails closed")
    _tamper_case(sc, json.loads(json.dumps(base)), json.loads(json.dumps(base_lock)),
                 lambda c: c["entries"][0].update(provenance="prov-core-nope"),
                 "unprovenanced", "unprovenanced entry fails closed")

    tampered_catalog = json.loads(json.dumps(base))
    tampered_catalog["entries"][0]["name"] = "renamed-without-relock"
    tmp = tempfile.mkdtemp(prefix="b05-lock.")
    try:
        os.makedirs(os.path.join(tmp, "locks"), exist_ok=True)
        os.makedirs(os.path.join(tmp, "packs"), exist_ok=True)
        with open(os.path.join(tmp, "catalog.json"), "w", encoding="utf-8") as fh:
            json.dump(tampered_catalog, fh)
        with open(os.path.join(tmp, "locks", "core.lock.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(base_lock, fh)  # stale digest on purpose
        shutil.copy(os.path.join(CATALOG_DIR, "packs", "core.json"),
                    os.path.join(tmp, "packs", "core.json"))
        router = sc.Router(os.path.join(tmp, "catalog.json"),
                           os.path.join(tmp, "packs"), REPO_ROOT)
        kinds = {kind for _id, kind, _r in router.excluded}
        record("provenance", "tampered catalog fails closed on digest",
               "lock-digest-mismatch" in kinds and not router.visible,
               f"kinds={sorted(kinds)} visible={len(router.visible)}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


SUITES = (
    ("catalog-search", lambda sc: suite_catalog_search(sc)),
    ("fallback", lambda sc: suite_fallback(sc)),
    ("clean-room", lambda sc: suite_clean_room()),
    ("package", lambda sc: suite_package(sc)),
    ("provenance", lambda sc: suite_provenance(sc)),
)


def main():
    print("=" * 64)
    print("B05 CATALOG / ROUTER FIXTURES")
    print("=" * 64)
    sc = load_router_module()
    for name, fn in SUITES:
        print(f"\n[{name}]")
        fn(sc)

    failed = [f for f in _FINDINGS if not f[2]]
    print("\n" + "=" * 64)
    print(f"checks: {len(_FINDINGS)}  passed: {len(_FINDINGS) - len(failed)}  "
          f"failed: {len(failed)}")
    if failed:
        print("FIXTURES FAILED")
        for suite, name, _ok, detail in failed:
            print(f"  ✗ [{suite}] {name}" + (f": {detail}" if detail else ""))
        return 1
    print("FIXTURES PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
