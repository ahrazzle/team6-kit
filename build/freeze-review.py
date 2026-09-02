#!/usr/bin/env python3
"""Build build/REVIEW.frozen.md — the scoped, frozen semantic sign-off for
the open-core demo surface.

Only rows in the FROZEN manifest (shipped TEMPLATE surface) get entries.
relpaths are SANITIZED in the frozen manifest, so the frozen review keys on
sanitized relpaths too (sanitize_path maps raw->sanitized deterministically).

Provenance marker per Azaraki/Shayba: this is the OPEN-CORE DEMO sign-off —
the paid/instance path requires a fresh buyer-side REVIEW, never this one.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from genericize import sanitize_path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_FROZEN = os.path.join(ROOT, "build", "manifest.frozen.tsv")
REVIEW_LIVE = os.path.join(ROOT, "build", "REVIEW.md")
REVIEW_FROZEN = os.path.join(ROOT, "build", "REVIEW.frozen.md")


def load_frozen_manifest():
    rows = set()
    with open(MANIFEST_FROZEN, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line or line.startswith("relpath"):
                continue
            rows.add(line.split("\t")[0])
    return rows


def load_review_entries():
    """Live REVIEW -> {sanitized_relpath: [checkbox states]}.
    Keys are sanitized so they match the frozen manifest's relpaths."""
    entries = {}
    cur = None
    with open(REVIEW_LIVE, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            m = re.match(r"^### ([^ ]+?)/(.+?)(?:\s+\*\(.*\)\*)?$", line)
            if m:
                cur = sanitize_path(m.group(2))
                entries[cur] = []
                continue
            cm = re.match(r"^- \[( |x)\] \d+\.", line)
            if cm and cur is not None:
                entries[cur].append(cm.group(1))
    return entries


def main():
    frozen = load_frozen_manifest()
    entries = load_review_entries()

    out = []
    out.append("# Kit Extraction Review — semantic pass gate (FROZEN)")
    out.append("")
    out.append("**PROVENANCE: OPEN-CORE DEMO SIGN-OFF.** This frozen review")
    out.append("is the sign-off for the open-core demo surface (the shipped")
    out.append("TEMPLATE rows). It rides the public repo so a fresh clone is")
    out.append("self-contained. It is NOT a buyer-side sign-off: the paid /")
    out.append("instance path requires a fresh REVIEW generated against the")
    out.append("buyer's own content, and the gate fails if that review")
    out.append("predates the params file.")
    out.append("")
    out.append("Checklist source: T-001 pass (soft leak classes).")
    out.append("")
    out.append("## Files requiring semantic review (frozen surface)")
    out.append("")

    n = 0
    missing = []
    exempt = {"profile.yaml"}  # REVIEW_EXEMPT — config surface, no checklist
    for rel in sorted(frozen):
        if rel in exempt:
            continue  # exempt rows need no review entry
        if rel not in entries:
            missing.append(rel)
            continue
        checks = entries[rel]
        out.append(f"### frozen/{rel}  *(frozen open-core sign-off)*")
        for i, state in enumerate(checks, 1):
            out.append(f"- [{state}] {i}.")
        out.append("")
        n += 1

    out.insert(1, f"**{n} files in scope (frozen open-core demo surface).**")
    with open(REVIEW_FROZEN, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")
    print(f"REVIEW.frozen.md written: {n} entries (from {len(frozen)} frozen rows)")
    print(f"missing: {len(missing)}")
    for m in missing[:5]:
        print(f"  {m}")
    if missing:
        sys.exit(1)


if __name__ == "__main__":
    main()
