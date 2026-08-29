#!/usr/bin/env python3
"""
build-manifest.py — Hit-file → generic-equivalent manifest for T-001.

KEYED ON UNIQUE PATHS (330), not per-profile entries (409). A file that lives
in 7 profiles is ONE manifest row with an occurrence note — this is the export
inventory and the templates/ content list, both riding on the same rows.

Reconciliation (verified on disk, extraction-inventory.py):
  - 409 = per-profile hit ENTRIES (a file in N profiles counts N times).
         Verified: the report's sweep-hits column sums to 409.
  - 330 = UNIQUE relative paths across all profiles. The manifest key.
  - 232 = unique paths with >=1 SHIPPABLE-class hit (feed the semantic REVIEW
          gate; redactable-class files never ship, they drop or stay home).
  - 113 = OBSOLETE. Artifact of the first report's top-8-per-class-per-profile
          DISPLAY truncation. Never a real audit count; now removed.

VERDICT RULES (rule table — deterministic, rerunnable):
  DROP        — instance content that never ships (attachments/, plans/, cron/,
                logs, .usage.json, secrets). Recorded for provenance only.
  TEMPLATE    — ships as a generic pattern with {PLACEHOLDER} substitution
                (profile.yaml, identity files, skill SKILL.md/references with
                instance detail genericized).
  KEEP        — already generic; no edit needed. Only sweeps because the
                instance-term regex matched a generic word (e.g. "ask" as an
                English/common word).
  KEEP-REVIEW — generic but sweep-hit; still goes through the semantic REVIEW.md
                gate (soft-signal checklist) because the regex may hide a leak.

Output: OUTPUTS/manifest.tsv  (one row per unique path)
        OUTPUTS/manifest.md   (human-readable, grouped by verdict)
"""

import os
import re
import importlib.util
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("ei", os.path.join(HERE, "extraction-inventory.py"))
ei = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ei)


def verdict_for(rel: str, cls: str) -> str:
    """Deterministic verdict from path shape + class."""
    p = rel.replace("\\", "/")
    base = os.path.basename(p)

    # --- DROP: instance-only surfaces (never ship) ---
    if p.startswith("attachments/"):
        return "DROP"
    if p.startswith("plans/") or p.startswith("cron/") or p.startswith("logs/"):
        return "DROP"
    if p.startswith("skills/.usage.json") or base == ".usage.json":
        return "DROP"
    if p.startswith("skills/.hub/"):
        return "DROP"
    if base == "profile.yaml":
        return "TEMPLATE"          # per-profile config -> templated
    if base in ei.SHIPPABLE_ROOT:  # SOUL.md/AGENTS.md/USER.md/HERMES.md
        return "TEMPLATE"          # identity -> persona archetype + redaction

    # --- Skill files ---
    if cls == "REDACTABLE":
        # Authored text outside skills that hit the sweep: never ships as-is.
        return "DROP"
    # cls == SHIPPABLE (skill content)
    if base == "SKILL.md":
        return "TEMPLATE"          # skill main file -> genericized
    if p.endswith((".md", ".txt")):
        # references/ and templates/ are candidate instances. If the path
        # smells like a named instance (generic markers + instance ventures
        # from identifiers.yaml), it templates; generic docs keep.
        inst_markers = ("instance", "session-", "example", "-stack", "live-state",
                        "deployment", "case-study")
        inst_markers += tuple(
            v.lower() for v in ei.load_identifiers()["venture_names"]
            + ei.load_identifiers()["client_names"])
        if any(m in p.lower() for m in inst_markers):
            return "TEMPLATE"
        return "KEEP-REVIEW"
    # code/config inside skills
    return "KEEP-REVIEW"


def main():
    by_relpath = defaultdict(list)   # rel -> [(prof, cls, n)]
    for prof in sorted(os.listdir(ei.DEFAULT_ROOT)):
        if prof.startswith("."):
            continue
        root = os.path.join(ei.DEFAULT_ROOT, prof)
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
                    rel = os.path.relpath(full, root)
                    by_relpath[rel].append((prof, cls, n))

    rows = []
    for rel, occ in sorted(by_relpath.items()):
        cls = "SHIPPABLE" if any(c == "SHIPPABLE" for _, c, _ in occ) else "REDACTABLE"
        total_hits = sum(n for _, _, n in occ)
        n_prof = len(occ)
        verdict = verdict_for(rel, cls)
        profs = ";".join(sorted(p for p, _, _ in occ))
        rows.append((rel, cls, n_prof, total_hits, verdict, profs))

    # TSV
    with open(os.path.join(HERE, "manifest.tsv"), "w", encoding="utf-8") as fh:
        fh.write("relpath\tclass\tprofiles\ttotal_hits\tverdict\tprofiles_detail\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")

    # Markdown, grouped by verdict
    groups = defaultdict(list)
    for r in rows:
        groups[r[4]].append(r)
    order = ["DROP", "TEMPLATE", "KEEP-REVIEW", "KEEP"]
    with open(os.path.join(HERE, "manifest.md"), "w", encoding="utf-8") as fh:
        fh.write("# T-001 Export Manifest — hit-file → generic-equivalent\n\n")
        fh.write(f"**{len(rows)} unique paths** (409 per-profile entries, "
                 f"deduplicated). Keyed on unique path: a file in N profiles is "
                 f"one row. Class = SHIPPABLE if any occurrence is shippable.\n\n")
        fh.write("| Verdict | Count |\n|---|---|\n")
        for v in order:
            fh.write(f"| {v} | {len(groups[v])} |\n")
        fh.write("\n---\n\n")
        for v in order:
            fh.write(f"## {v} ({len(groups[v])})\n\n")
            fh.write("| path | class | #profiles | hits | detail |\n|---|---|---|---|---|\n")
            for rel, cls, np_, th, _, profs in groups[v]:
                fh.write(f"| `{rel}` | {cls} | {np_} | {th} | {profs} |\n")
            fh.write("\n")

    print(f"manifest.tsv: {len(rows)} rows")
    for v in order:
        print(f"  {v:>12}: {len(groups[v])}")
    # top instance-marker templates
    tpl = sorted(groups["TEMPLATE"], key=lambda r: -r[3])
    print("\nTop TEMPLATE rows by hits:")
    for rel, cls, np_, th, _, _ in tpl[:12]:
        print(f"  {th:>3}h x{np_}  {rel}")


if __name__ == "__main__":
    main()
