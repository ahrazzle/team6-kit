#!/usr/bin/env python3
"""
review-gate.py — Semantic sign-off enforcement (build step 2).

Checks that every shipping row (TEMPLATE / KEEP-REVIEW) in the manifest has a
SIGNED REVIEW.md entry: all 4/4 soft-leak checkboxes ticked. REVIEW_EXEMPT
rows (documented config surfaces) are honored.

Exit: 0 = all shipping rows signed; 1 = unsigned/missing (blocks assembly).

This is the one place a human/LLM eye is load-bearing — implemented as a
BLOCKER, never a checkbox (team standard, spec section 6).
"""

import os
import re
import sys
import importlib.util
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(HERE, "manifest.tsv")
REVIEW = os.path.join(HERE, "REVIEW.md")

# Mirrors sweep-gate.py — config surfaces that ship fully templated.
REVIEW_EXEMPT = {
    "profile.yaml": "config surface, fully templated at instantiation",
}


def load_manifest(path):
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


def parse_review(path):
    """REVIEW.md -> {relpath: (ticked, total)} across all profile copies."""
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


def main():
    manifest = load_manifest(MANIFEST)
    review = parse_review(REVIEW)

    unsigned = []
    missing = []
    for rel, (cls, np_, th, verdict) in manifest.items():
        if verdict not in ("TEMPLATE", "KEEP-REVIEW"):
            continue
        if rel in REVIEW_EXEMPT:
            continue
        if rel not in review:
            missing.append(rel)
            continue
        ticked, total = review[rel]
        if ticked < total:
            unsigned.append((rel, ticked, total))

    print("=" * 60)
    print("REVIEW GATE — semantic sign-off enforcement")
    print("=" * 60)
    print(f"  shipping rows    : {sum(1 for v in manifest.values() if v[3] in ('TEMPLATE','KEEP-REVIEW'))}")
    print(f"  review entries   : {len(review)}")
    print(f"  unsigned         : {len(unsigned)}")
    print(f"  missing entry    : {len(missing)}")
    print()

    if missing:
        print("FAIL — shipping files with NO review entry:")
        for rel in missing[:10]:
            print(f"  ✗ {rel}")
    if unsigned:
        print("FAIL — shipping files with unsigned checklists:")
        for rel, t, tot in unsigned[:10]:
            print(f"  ✗ {rel}  ({t}/{tot})")
    if missing or unsigned:
        print()
        print("remediation: complete the semantic pass (soft-leak classes:")
        print("  relationship specifics, financial figures, client/contract")
        print("  detail, personal habits) and tick 4/4 in REVIEW.md.")
        return 1

    print("PASS — every shipping row is signed (4/4). Safe to generate.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
