#!/usr/bin/env python3
"""
sweep-gate.py — Build-time extraction gate for the agent kit.

WHAT IT DOES
  Runs before EVERY kit build. Verifies the extraction source is clean and
  fully classified. Any drift is a build failure, full stop.

SCOPE (the source-scope boundary, formalized)
  The gate inspects the EXTRACTION SOURCE (profiles being mined), never the
  assembly target (the kit repo). The kit's own surfaces — choreography/,
  registry/, LICENSE, kit.yaml — are authored fresh, have no manifest row by
  design, and are OUT of scope here. The rule "unclassified = do not ship"
  applies to source files only.

CONTRACT (the build contract, implemented):
  1. REGENERATE — re-run build-manifest.py so the manifest is live, not stale.
  2. COVERAGE   — every on-disk source file carrying a sweep hit must have a
                 manifest row. Unclassified hit = FAIL (the unclassified edge; also
                 kills the stale-REVIEW.md bug: a new file can't ship without
                 a verdict). Non-hit files are clean by definition and need
                 no row; excluded-class files never ship.
  3. VERDICTS   — no REDACTABLE-class row ships as-is; DROP rows never ship;
                 a row only ships when verdict is TEMPLATE or KEEP-REVIEW.
  4. SEMANTIC   — every shipping row must have a SIGNED REVIEW.md entry
                 (4/4 checkboxes ticked). Missing or unsigned = FAIL.
                 REVIEW_EXEMPT carries documented exceptions (config files
                 that ship fully templated, no authored soft-leak surface).

USAGE
  python3 sweep-gate.py [--no-regenerate] [--source DIR] [--out DIR]

EXIT
  0 = PASS (safe to assemble)
  1 = FAIL (list of blockers + remediation hints)
"""

import os
import re
import sys
import subprocess
import importlib.util
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DEFAULT_SOURCE = os.path.expanduser("~/.hermes/profiles")
MANIFEST_FROZEN = os.path.join(HERE, "manifest.frozen.tsv")
REVIEW_FROZEN = os.path.join(HERE, "REVIEW.frozen.md")

# Files that ship via TEMPLATE but need no soft-leak review: they are
# configuration surfaces fully substituted at instantiation, not authored
# prose. Documented exceptions only — adding to this list is a provenance act.
REVIEW_EXEMPT = {
    "profile.yaml": "config surface, fully templated at instantiation",
}

# Verdicts that may ship. Anything else (DROP, or unclassified) blocks.
SHIPPABLE_VERDICTS = ("TEMPLATE", "KEEP-REVIEW")


def load_engine():
    spec = importlib.util.spec_from_file_location(
        "ei", os.path.join(HERE, "extraction-inventory.py"))
    ei = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ei)
    return ei


def load_manifest(path):
    """manifest.tsv -> {relpath: (cls, n_profiles, total_hits, verdict)}"""
    rows = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line or line.startswith("relpath"):
                continue
            parts = line.split("\t")
            if len(parts) < 5:
                continue
            rel, cls, np_, th, verdict = parts[:5]
            rows[rel] = (cls, int(np_), int(th), verdict)
    return rows


def live_scan(ei, source):
    """Walk source profiles -> {relpath: cls} for every file ON DISK that
    carries a sweep hit. Non-hit files are clean by definition (no venture
    signal) and need no manifest row; excluded-class files never ship."""
    live = {}
    for prof in sorted(os.listdir(source)):
        if prof.startswith("."):
            continue
        root = os.path.join(source, prof)
        if not os.path.isdir(root):
            continue
        for dp, dn, fn in os.walk(root):
            dn[:] = [d for d in dn if d not in ("node_modules", ".git")]
            for f in fn:
                full = os.path.join(dp, f)
                cls = ei.classify(full)
                if cls not in ("SHIPPABLE", "REDACTABLE"):
                    continue
                n, _ = ei.sweep_file(full)
                if n:
                    live[os.path.relpath(full, root)] = cls
    return live


def parse_review(path):
    """REVIEW.md -> {relpath: (n_ticked, n_total)} across all profile copies."""
    signed = {}
    cur = None
    ticked = total = 0
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            m = re.match(r"^### ([^ ]+?)/(.+?)(?:\s+\*\(.*\)\*)?$", line)
            if m:
                if cur is not None:
                    signed[cur] = (ticked, total)
                body = re.sub(r"\s+\*\(.*\)\*$", "", line[4:])
                _, cur = body.split("/", 1)
                ticked = total = 0
                continue
            cm = re.match(r"^- \[( |x)\] \d+\.", line)
            if cm and cur is not None:
                total += 1
                if cm.group(1) == "x":
                    ticked += 1
    if cur is not None:
        signed[cur] = (ticked, total)
    return signed


def regenerate_manifest():
    subprocess.run([sys.executable, os.path.join(HERE, "build-manifest.py")],
                   check=True, capture_output=True)
    return os.path.join(HERE, "manifest.tsv")


def target_exists(rel):
    """True if this manifest row ships — its template target exists under
    templates/. Used by --kit-scope: the gate then checks ONLY the kit's
    shipped surface, not the whole live-fleet manifest (which grows as skills
    are added to profiles long after the kit was authored)."""
    base = os.path.basename(rel)
    t = os.path.join(ROOT, "templates")
    if base == "profile.yaml":
        return os.path.isfile(os.path.join(t, "personas", "profile.yaml.tmpl"))
    if base in ("SOUL.md", "AGENTS.md", "USER.md", "HERMES.md"):
        return os.path.isfile(os.path.join(t, "personas", f"{base}.tmpl"))
    if rel.startswith("skills/"):
        from genericize import sanitize_path
        return os.path.isfile(os.path.join(t, "skills", sanitize_path(rel[len("skills/"):])))
    return os.path.isfile(os.path.join(t, rel))


def main():
    args = sys.argv[1:]
    regenerate = "--no-regenerate" not in args
    kit_scope = "--kit-scope" in args
    frozen = "--frozen" in args
    source = DEFAULT_SOURCE
    out = HERE
    if "--source" in args:
        source = args[args.index("--source") + 1]
    if "--out" in args:
        out = args[args.index("--out") + 1]

    ei = load_engine()
    problems = []
    notes = []

    # 1. REGENERATE — fresh manifest. Skipped in --frozen mode: the frozen
    #    manifest is the committed, self-contained artifact; regeneration
    #    would scan the live fleet, which a fresh clone doesn't have.
    if frozen:
        manifest_path = MANIFEST_FROZEN
        review_path = REVIEW_FROZEN
        notes.append("frozen mode: committed manifest + review (self-contained)")
        regenerate = False
    elif regenerate:
        manifest_path = regenerate_manifest()
        notes.append("manifest regenerated (live)")
        review_path = os.path.join(out, "REVIEW.md")
    else:
        manifest_path = os.path.join(out, "manifest.tsv")
        review_path = os.path.join(out, "REVIEW.md")
        notes.append("manifest used as-is (--no-regenerate)")

    manifest = load_manifest(manifest_path)
    review = parse_review(review_path)

    # SCOPE BOUNDARY (--kit-scope): only rows whose template target exists
    # under templates/ gate the build. The live-fleet manifest grows as
    # skills are added to profiles long after the kit was authored — those
    # rows are NOT the kit's shipped surface and must not veto instantiation.
    if kit_scope:
        manifest = {rel: v for rel, v in manifest.items() if target_exists(rel)}
        notes.append("kit-scope: gate limited to shipped templates/ surface")

    # 2. COVERAGE — every live source file must have a verdict.
    #    Frozen mode: no fleet scan — the frozen manifest IS the shipped
    #    surface, fully classified by construction. A fresh clone has no
    #    local fleet, so scanning it would be both wrong and broken.
    live = {} if frozen else live_scan(ei, source)
    if not frozen and kit_scope:
        live = {rel: cls for rel, cls in live.items() if rel in manifest}
    if not frozen:
        unclassified = sorted(set(live) - set(manifest))
        if unclassified:
            problems.append(
                f"UNCLASSIFIED SOURCE ({len(unclassified)}): "
                f"no manifest row — run build-manifest.py to assign verdicts")
            for rel in unclassified[:10]:
                problems.append(f"    {rel}")

    # 3. VERDICTS — only TEMPLATE/KEEP-REVIEW may ship
    bad_verdicts = []
    for rel, (cls, np_, th, verdict) in manifest.items():
        if verdict == "DROP":
            continue  # dropped by design — never ships
        if cls == "REDACTABLE" and verdict != "TEMPLATE":
            bad_verdicts.append((rel, cls, verdict))
    if bad_verdicts:
        problems.append(
            f"REDACTABLE-CLASS SHIPPING ({len(bad_verdicts)}): "
            f"redactable content must never ship")
        for rel, cls, v in bad_verdicts[:10]:
            problems.append(f"    {rel}  ({cls}|{v})")

    # 4. SEMANTIC — shipping rows need signed review entries
    unsigned = []
    missing_entry = []
    for rel, (cls, np_, th, verdict) in manifest.items():
        if verdict not in SHIPPABLE_VERDICTS:
            continue
        if rel in REVIEW_EXEMPT:
            continue
        if rel not in review:
            missing_entry.append(rel)
            continue
        ticked, total = review[rel]
        if ticked < total:
            unsigned.append((rel, ticked, total))
    if missing_entry:
        problems.append(
            f"MISSING REVIEW ENTRY ({len(missing_entry)}): "
            f"shipping file has no semantic-pass checklist — add to REVIEW.md")
        for rel in missing_entry[:10]:
            problems.append(f"    {rel}")
    if unsigned:
        problems.append(
            f"UNSIGNED REVIEW ({len(unsigned)}): "
            f"checklist not fully ticked — semantic pass incomplete")
        for rel, t, tot in unsigned[:10]:
            problems.append(f"    {rel}  ({t}/{tot})")

    # ---- report ----
    print("=" * 64)
    print("SWEEP GATE — T-001 kit extraction")
    print("=" * 64)
    for n in notes:
        print(f"  note: {n}")
    print(f"  source : {source}")
    print(f"  live   : {len(live) if not frozen else 'n/a (frozen)'} source files")
    print(f"  manifest: {len(manifest)} rows")
    print(f"  review : {len(review)} entries")
    print()
    if problems:
        print(f"FAIL — {len(problems)} blocker group(s):")
        for p in problems:
            print(f"  ✗ {p}")
        print()
        print("remediation:")
        print("  1. run build-manifest.py to assign verdicts to new files")
        print("  2. tick REVIEW.md checkboxes after the semantic pass")
        print("  3. never ship DROP or REDACTABLE content")
        return 1
    print("PASS — extraction source is clean and fully classified.")
    print("Safe to assemble the kit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
