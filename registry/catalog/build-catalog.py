#!/usr/bin/env python3
"""
build-catalog.py — generate the compact skill catalog and its provenance lock.

WHAT IT DOES
  Reads one declared pack (registry/catalog/packs/<pack>.json), walks the
  pack's skill root for SKILL.md entries, and emits two deterministic files:

    registry/catalog/catalog.json        compact router-visible entries
    registry/catalog/locks/<pack>.lock.json   one provenance record per entry

  Catalog entries carry metadata and an exact, repo-relative read path ONLY.
  The generator never writes a skill body into the catalog or the lock, and
  never copies upstream content — it indexes the kit's own shipped templates.

FAIL-CLOSED CLASSIFICATION (an entry is excluded, not guessed, when:)
  - its category is not in any funnel declared by the pack (unclassified)
  - its path or id contains an unresolved template placeholder ({...})
  - its frontmatter has no usable name (unnamed)

BOUNDED, DETERMINISTIC
  Entries are sorted by id; JSON is emitted with a fixed key order and a
  trailing newline, so regenerating from the same tree is byte-identical.

USAGE
  python3 registry/catalog/build-catalog.py            # write catalog + lock
  python3 registry/catalog/build-catalog.py --check     # drift check, no write
  python3 registry/catalog/build-catalog.py --pack core --root .

EXIT
  0 = written (or --check found no drift)
  1 = --check found drift, or the pack is invalid/unreadable (fail closed)

Standard library only. No network, no third-party dependency.
"""

import argparse
import hashlib
import json
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
DEFAULT_PACKS_DIR = os.path.join(SCRIPT_DIR, "packs")
DEFAULT_OUT_DIR = SCRIPT_DIR

# An id segment: lowercase letters, digits, dots, underscores, hyphens.
_ID_SEG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
# Frontmatter scalar at low indent:  key: value
_SCALAR = re.compile(r"^[ \t]{0,2}([A-Za-z_][A-Za-z0-9_-]*):[ \t]*(.*)$")
# Inline YAML list: key: [a, b, c]
_INLINE_LIST = re.compile(r"^[ \t]*([A-Za-z_][A-Za-z0-9_-]*):[ \t]*\[(.*)\][ \t]*$")


def sha256_bytes(data):
    return "sha256:" + hashlib.sha256(data).hexdigest()


def read_text(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def load_pack(pack_path):
    with open(pack_path, encoding="utf-8") as fh:
        pack = json.load(fh)
    problems = []
    for field in ("pack", "license", "source", "skill_root", "funnels"):
        if not pack.get(field):
            problems.append(f"pack is missing required field: {field}")
    if not isinstance(pack.get("funnels"), dict):
        problems.append("pack.funnels must be an object")
    if problems:
        raise ValueError("; ".join(problems))
    return pack


def funnel_lookup(pack):
    """category -> funnel name from the pack's declared funnels."""
    lookup = {}
    for funnel, spec in pack["funnels"].items():
        for category in spec.get("categories", []):
            lookup[category] = funnel
    return lookup


def strip_quotes(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def split_inline_list(body):
    items = []
    for part in body.split(","):
        part = strip_quotes(part)
        if part:
            items.append(part)
    return items


def parse_frontmatter(text):
    """Return a dict of the frontmatter scalars/lists we index. No dependencies."""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip() == "---":
            start = i
            break
    if start is None:
        return {}
    fm = {}
    for line in lines[start + 1:]:
        if line.strip() == "---":
            break
        m = _INLINE_LIST.match(line)
        if m:
            key, body = m.group(1), m.group(2)
            if key in ("tags", "aliases", "capabilities"):
                fm.setdefault(key, split_inline_list(body))
            continue
        m = _SCALAR.match(line)
        if m:
            key, value = m.group(1), strip_quotes(m.group(2))
            if key in ("name", "description", "license", "version") and value:
                fm.setdefault(key, value)
    return fm


def placeholder_free(*values):
    return not any("{" in str(v) or "}" in str(v) for v in values)


def discover_entries(root, pack):
    """Yield (entry_or_None, exclusion_or_None) per SKILL.md found."""
    lookup = funnel_lookup(pack)
    skill_root = os.path.join(root, pack["skill_root"])
    hits = []
    for dirpath, dirnames, filenames in os.walk(skill_root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__")]
        if "SKILL.md" in filenames:
            hits.append(os.path.join(dirpath, "SKILL.md"))
    hits.sort()

    for path in hits:
        rel = os.path.relpath(path, root).replace(os.sep, "/")
        rel_to_root = rel[len(pack["skill_root"]):].lstrip("/")
        segments = rel_to_root.split("/")
        category = segments[0] if len(segments) > 1 else ""
        stem = segments[-2] if len(segments) >= 2 else ""

        if not placeholder_free(rel, category, stem):
            yield None, ("placeholder-path", rel,
                         "path contains an unresolved template placeholder")
            continue

        funnel = lookup.get(category)
        if funnel is None:
            yield None, ("unclassified", rel,
                         f"category '{category}' is not in any declared funnel")
            continue

        fm = parse_frontmatter(read_text(path))
        name = fm.get("name") or stem
        if not name:
            yield None, ("unnamed", rel, "no frontmatter name and no directory")
            continue

        entry_id = f"{category}/{stem}"
        if not all(_ID_SEG.match(seg) for seg in entry_id.split("/")):
            yield None, ("bad-id", rel, f"id '{entry_id}' is not id-shaped")
            continue

        license_value = fm.get("license")
        if license_value:
            license_source = "frontmatter"
        else:
            license_value = pack["license"]
            license_source = "pack-default"

        provenance = "prov-" + pack["pack"] + "-" + hashlib.sha1(
            entry_id.encode("utf-8")).hexdigest()[:12]

        tags = fm.get("tags", [])
        caps = fm.get("capabilities") or [t.lower().replace(" ", "-")
                                          for t in tags][:8]

        entry = {
            "id": entry_id,
            "name": name,
            "description": fm.get("description", ""),
            "funnel": funnel,
            "tags": tags,
            "aliases": fm.get("aliases", []),
            "capabilities": caps,
            "pack": pack["pack"],
            "source": pack["source"],
            "license": license_value,
            "license_source": license_source,
            "provenance": provenance,
            "read_path": rel,
        }
        yield entry, None


def build(root, pack, pack_path):
    entries = []
    exclusions = []
    seen = {}
    for entry, exclusion in discover_entries(root, pack):
        if entry is None:
            exclusions.append(exclusion)
            continue
        if entry["id"] in seen:
            exclusions.append(("duplicate-id", entry["read_path"],
                               f"id '{entry['id']}' already used by "
                               f"{seen[entry['id']]}"))
            continue
        seen[entry["id"]] = entry["read_path"]
        entries.append(entry)

    entries.sort(key=lambda e: e["id"])
    funnel_order = list(pack["funnels"].keys())

    catalog = {
        "schema_version": 1,
        "catalog_id": f"team6-kit/{pack['pack']}",
        "generated_from": pack["skill_root"],
        "pack": pack["pack"],
        "pack_digest": sha256_bytes(open(pack_path, "rb").read()),
        "funnel_order": funnel_order,
        "entries": entries,
    }

    entries_canonical = json.dumps(entries, sort_keys=True,
                                   separators=(",", ":")).encode("utf-8")
    lock = {
        "schema_version": 1,
        "lock_id": catalog["catalog_id"],
        "pack": pack["pack"],
        "source": pack["source"],
        "catalog_id": catalog["catalog_id"],
        "catalog_digest": sha256_bytes(entries_canonical),
        "generated_from": pack["skill_root"],
        "entries": [
            {
                "provenance": e["provenance"],
                "id": e["id"],
                "name": e["name"],
                "pack": e["pack"],
                "source": e["source"],
                "license": e["license"],
                "license_source": e["license_source"],
                "read_path": e["read_path"],
            }
            for e in entries
        ],
    }
    return catalog, lock, exclusions


def dump(obj):
    return json.dumps(obj, indent=2, ensure_ascii=True) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack", default="core")
    ap.add_argument("--root", default=DEFAULT_ROOT)
    ap.add_argument("--packs-dir", default=DEFAULT_PACKS_DIR)
    ap.add_argument("--out", default=DEFAULT_OUT_DIR)
    ap.add_argument("--check", action="store_true",
                    help="compare regenerated output with the committed files; "
                         "exit 1 on drift (no write)")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.root)
    pack_path = os.path.join(args.packs_dir, f"{args.pack}.json")
    catalog_path = os.path.join(args.out, "catalog.json")
    lock_path = os.path.join(args.out, "locks", f"{args.pack}.lock.json")

    try:
        pack = load_pack(pack_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL — cannot load pack {pack_path}: {exc}")
        return 1

    catalog, lock, exclusions = build(root, pack, pack_path)
    catalog_text = dump(catalog)
    lock_text = dump(lock)

    print("=" * 64)
    print("CATALOG BUILD — compact skill catalog + provenance lock")
    print("=" * 64)
    print(f"  pack        : {pack['pack']} ({pack_path})")
    print(f"  root        : {root}")
    print(f"  entries     : {len(catalog['entries'])}")
    print(f"  funnels     : {', '.join(catalog['funnel_order'])}")
    print(f"  digest      : {lock['catalog_digest']}")
    if exclusions:
        print(f"  excluded    : {len(exclusions)} (fail-closed, not router-visible)")
        for kind, rel, reason in exclusions:
            print(f"      - [{kind}] {rel}: {reason}")

    if args.check:
        drift = []
        for path, text in ((catalog_path, catalog_text), (lock_path, lock_text)):
            current = read_text(path) if os.path.isfile(path) else None
            if current != text:
                drift.append(path)
        if drift:
            print("FAIL — drift: committed artifact(s) differ from regeneration:")
            for path in drift:
                print(f"  ✗ {path}")
            print("remediation: re-run build-catalog.py and commit the result.")
            return 1
        print("PASS — committed catalog and lock match regeneration (no drift).")
        return 0

    os.makedirs(os.path.dirname(lock_path), exist_ok=True)
    with open(catalog_path, "w", encoding="utf-8") as fh:
        fh.write(catalog_text)
    with open(lock_path, "w", encoding="utf-8") as fh:
        fh.write(lock_text)
    print(f"  wrote       : {catalog_path}")
    print(f"  wrote       : {lock_path}")
    print("PASS — catalog and lock written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
