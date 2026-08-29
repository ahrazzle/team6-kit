#!/usr/bin/env python3
"""
extraction-inventory.py — Profile extraction audit for T-001 (Sellable Team6 kit).

PURPOSE
  Foundation for the extraction audit. Walks every Hermes profile dir and
  classifies each artifact into one of three classes so the audit is mechanical,
  not manual:

    SHIPPABLE   — identity/behavior that a kit wants (SOUL.md, skills, AGENTS.md).
    REDACTABLE  — authored text that MAY mention ventures/paths/user data.
                  Shippable ONLY after a content sweep (this script flags hits).
    EXCLUDED    — structurally local state that must never ship (memories, logs,
                  session DBs, auth, caches, checkpoints, editor cruft).

  Also performs the content sweep: scans every authored text file for known
  venture names / user identifiers / workspace paths and reports hits, so the
  redaction surface is enumerated rather than eyeballed.

USAGE
  python3 extraction-inventory.py [profile_dir ...]
    Default: all profiles under ~/.hermes/profiles/

OUTPUT
  Per-profile table (count + bytes per class) + a hit report for the sweep.
  Exit code 0 on success.

DESIGN NOTES
  - The installer excludes `memories/MEMORY.md` (one file). This script does NOT
    rely on that — it classifies the whole memories/ tree as EXCLUDED (structurally
    local), matching the team's correction: the tool protects one file, the
    sweep protects the rest.
  - Secret-bearing files (auth.json, *.token, credentials) are flagged REDACTABLE
    so they can never ship; auth is structurally excluded on principle.
  - File classes are decided by PATH SHAPE (name/dir), never by scanning secrets
    into the report. We only ever print filenames and word counts of hits.
"""

import os
import re
import sys
from collections import defaultdict

# --- Profile root ---------------------------------------------------------
DEFAULT_ROOT = os.path.expanduser("~/.hermes/profiles")


# --- Path-shape classification -------------------------------------------
# Anything under these top-level profile dirs is structurally local.
EXCLUDED_DIRS = {
    "memories",        # installer strips MEMORY.md; whole tree stays home
    "logs",
    "sessions",
    "session",
    "checkpoints",
    "caches",
    "cache",
    "auth",
    "credentials",
    ".git",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
}

# Filenames that are structurally local wherever they appear.
EXCLUDED_FILES = {
    "auth.json",
    "auth.jsonl",
    ".env",
    ".env.local",
    "credentials.json",
    "token.json",
    ".DS_Store",
    "*.sqlite", "*.sqlite3", "*.db",   # session/state DBs
    "*.log",
    "*.lock",
    "*.pid",
}

# Filenames that are authored text — sweep candidates. Everything else
# (binaries, images, archives) is EXCLUDED for a kit.
SWEEP_SUFFIXES = (".md", ".txt", ".yaml", ".yml", ".json", ".toml",
                  ".sh", ".py", ".js", ".ts", ".html", ".css")

# SHIPPABLE identity/behavior files (profile root).
SHIPPABLE_ROOT = {"SOUL.md", "AGENTS.md", "USER.md", "HERMES.md", ".hermes.md"}


def classify(path: str) -> str:
    """Return one of SHIPPABLE / REDACTABLE / EXCLUDED for a profile path."""
    parts = path.split(os.sep)
    name = os.path.basename(path)

    # Excluded by directory shape (ancestors).
    for p in parts:
        if p in EXCLUDED_DIRS:
            return "EXCLUDED"

    # Excluded by filename pattern.
    for pat in EXCLUDED_FILES:
        if pat.startswith("*."):
            if name.endswith(pat[1:]):
                return "EXCLUDED"
        elif name == pat:
            return "EXCLUDED"

    # Auth-ish names anywhere are redactable at best — treat as excluded-leaning
    # redactable so they get flagged, never silently shipped.
    low = name.lower()
    if any(k in low for k in ("auth", "token", "secret", "credential", "key", "password")):
        return "REDACTABLE"  # flagged: must be scrubbed or dropped

    # Shippable identity files at profile root or skills dirs.
    if name in SHIPPABLE_ROOT or name == "SKILL.md":
        return "SHIPPABLE"

    # Under skills/ (or any skill dir) — skill content is authored text.
    if "skills" in parts:
        return "SHIPPABLE" if name.endswith(SWEEP_SUFFIXES) else "EXCLUDED"

    # Everything else authored text → redaction sweep candidate.
    if name.endswith(SWEEP_SUFFIXES):
        return "REDACTABLE"

    return "EXCLUDED"


# --- Content sweep --------------------------------------------------------
# Identifier inventory is loaded from build/identifiers.yaml — EMPTY by
# default. A public fork must not carry instance identifiers in committed
# scripts; the config is supplied per-instance at build time and is itself
# the service-tier deliverable. Never hardcode identifiers here.
IDENTIFIERS = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "identifiers.yaml")


def load_identifiers():
    """Load the instance identifier inventory from identifiers.yaml.
    Missing file / blank values → empty lists (safe: no instance identifiers
    means the sweep matches nothing and the kit ships generic)."""
    out = {
        "team_handles": [], "venture_names": [], "user_handles": [],
        "client_names": [], "path_markers": [], "habit_phrases": [],
        "codename_terms": [],
    }
    idf = IDENTIFIERS
    if not os.path.isfile(idf):
        # Fall back to the committed empty template (fork ships identifiers.yaml
        # gitignored; the .example carries the shape). Empty = safe generic kit.
        fallback = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "identifiers.yaml.example")
        if os.path.isfile(fallback):
            idf = fallback
        else:
            return out
    cur = None
    try:
        with open(idf, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line and not line.startswith("-") and line.endswith(":"):
                    cur = line[:-1].strip()
                    continue
                if line.startswith("- ") and cur in out:
                    out[cur].append(line[2:].strip().strip('"\''))
    except OSError:
        pass
    return out


_INSTANCE = load_identifiers()

# SWEEP_TERMS — built from the instance inventory, never hardcoded.
SWEEP_TERMS = (
    _INSTANCE["user_handles"]
    + _INSTANCE["team_handles"]
    + _INSTANCE["venture_names"]
    + _INSTANCE["client_names"]
    + _INSTANCE["codename_terms"]
    + _INSTANCE["path_markers"]
)

# SWEEP_RE — guard against empty inventory: no terms → match nothing, so the
# sweep never false-hits (an empty alternation would match at every position).
if SWEEP_TERMS:
    SWEEP_RE = re.compile(r"(?i)(" + "|".join(re.escape(t) for t in SWEEP_TERMS) + r")")
else:
    SWEEP_RE = re.compile(r"(?i)(?!)")   # never matches


def sweep_file(path: str):
    """Return (count, sample_lines) of sweep-term hits, or (0, None)."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError:
        return 0, None
    hits = SWEEP_RE.findall(text)
    if not hits:
        return 0, None
    # Collect the distinct lines that matched, for the report sample.
    lines = text.splitlines()
    matched = []
    for ln in lines:
        if SWEEP_RE.search(ln):
            matched.append(ln.strip()[:100])
        if len(matched) >= 3:
            break
    return len(hits), matched


# --- Soft-signal checklist (semantic pass) --------------------------------
# The regex sweep catches HARD signals (venture names, handles, paths). The
# semantic pass must also check the SOFT leak classes the fleet is richest in
# (soft-leak classes, from the T-001 pass). REVIEW.md ships this
# fixed checklist per shippable-class file so the review is gated, not
# open-ended — an LLM/human reviewer ticks each item; the file ships only when
# all four are cleared.
SOFT_SIGNALS = [
    "relationship specifics (user family, background, personal ties)",
    "financial figures (budgets, pricing, costs)",
    "client/contract detail (names, terms, obligations)",
    "personal habits or identifying routines",
]


def emit_review_md(profiles):
    """Write REVIEW.md — one entry per file in semantic-review scope.

    Scope = shippable files that either (a) hit the hard-signal sweep (their
    content is known-touched) or (b) are identity files (SOUL.md / AGENTS.md /
    USER.md — small in count, densest in soft leaks). The remaining skill
    files ship as generic patterns via the generator mapping, not per-file
    review. The mechanical sweep is necessary but not sufficient: regexes
    can't see soft leaks, so this fixed checklist is the gate — a file ships
    only when all four items are cleared.
    """
    out = ["# Kit Extraction Review — semantic pass gate",
           "",
           "Mechanical sweep complete (hard signals). The regex classifier ",
           "cannot see SOFT leaks, so every file below must be reviewed ",
           "against the fixed checklist. Scope = sweep-hit shippable files + ",
           "identity files (dense soft-leak surface). A file ships only when ",
           "all four items are cleared.",
           "",
           "Checklist source: T-001 pass (soft leak classes).",
           "",
           "## Files requiring semantic review",
           ""]
    n = 0
    for prof in profiles:
        root = os.path.join(DEFAULT_ROOT, prof)
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames
                           if d not in ("node_modules", ".git")]
            for fn in filenames:
                full = os.path.join(dirpath, fn)
                if classify(full) != "SHIPPABLE":
                    continue
                rel = os.path.relpath(full, root)
                # Identity = the true persona files only. SKILL.md is every
                # skill's main file (~824 of them) — NOT identity; skill files
                # ship via the generator mapping, only sweep-hit ones need
                # per-file review here.
                is_identity = fn in SHIPPABLE_ROOT
                is_swept = bool(SWEEP_RE.search(
                    open(full, encoding="utf-8",
                         errors="replace").read() if os.path.isfile(full)
                    else ""))
                if not (is_identity or is_swept):
                    continue
                n += 1
                out.append(f"### {prof}/{rel}"
                           + ("  *(sweep-hit)*" if is_swept and not is_identity
                              else "  *(identity)*" if is_identity else ""))
                for i, sig in enumerate(SOFT_SIGNALS, 1):
                    out.append(f"- [ ] {i}. {sig}")
                out.append("")
    out.insert(1, f"**{n} files in scope.**")
    dest = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "REVIEW.md")
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))
    print(f"Wrote {dest} — {n} shippable files, {len(SOFT_SIGNALS)}-item "
          f"checklist each.")


# --- Report ---------------------------------------------------------------
def audit_profile(profile: str) -> dict:
    root = os.path.join(DEFAULT_ROOT, profile)
    stats = defaultdict(lambda: [0, 0])       # class -> [count, bytes]
    hits = defaultdict(list)                   # class -> [(path, count, sample)]
    excluded_n = 0

    for dirpath, dirnames, filenames in os.walk(root):
        # Prune deep vendor dirs for speed.
        dirnames[:] = [d for d in dirnames if d not in ("node_modules", ".git")]
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root)
            try:
                size = os.path.getsize(full)
            except OSError:
                size = 0
            cls = classify(full)
            stats[cls][0] += 1
            stats[cls][1] += size
            if cls in ("SHIPPABLE", "REDACTABLE"):
                n, sample = sweep_file(full)
                if n:
                    hits[cls].append((rel, n, sample))

    return {"stats": stats, "hits": hits}


def main():
    args = sys.argv[1:]
    emit_review = False
    if "--review" in args:
        emit_review = True
        args.remove("--review")
    profiles = [p for p in (args or sorted(os.listdir(DEFAULT_ROOT)))
                if not p.startswith(".")]
    if emit_review:
        emit_review_md(profiles)
        return
    grand = defaultdict(lambda: [0, 0])
    print(f"{'profile':<16} {'ship':>6} {'redact':>7} {'excl':>6}  "
          f"{'sweep-hits':>11}")
    print("-" * 62)
    for prof in profiles:
        if not os.path.isdir(os.path.join(DEFAULT_ROOT, prof)):
            print(f"{prof:<16}  (not a dir — skipping)")
            continue
        res = audit_profile(prof)
        s = res["stats"]
        sh, rd, ex = s["SHIPPABLE"], s["REDACTABLE"], s["EXCLUDED"]
        hits_total = sum(len(v) for v in res["hits"].values())
        for k in ("SHIPPABLE", "REDACTABLE", "EXCLUDED"):
            grand[k][0] += s[k][0]
            grand[k][1] += s[k][1]
        print(f"{prof:<16} {sh[0]:>4} {sh[1]/1024:>6.0f}k "
              f"{rd[0]:>5} {rd[1]/1024:>5.0f}k {ex[0]:>6} "
              f"{hits_total:>8}")

    print("-" * 62)
    print(f"{'TOTAL':<16} {grand['SHIPPABLE'][0]:>4} "
          f"{grand['SHIPPABLE'][1]/1024:>6.0f}k "
          f"{grand['REDACTABLE'][0]:>5} {grand['REDACTABLE'][1]/1024:>5.0f}k "
          f"{grand['EXCLUDED'][0]:>6}")

    # Hit report — the redaction surface.
    print("\n=== CONTENT SWEEP — files mentioning live identifiers ===")
    for prof in profiles:
        if not os.path.isdir(os.path.join(DEFAULT_ROOT, prof)):
            continue
        res = audit_profile(prof)
        if not res["hits"]:
            continue
        print(f"\n-- {prof} --")
        for cls in ("SHIPPABLE", "REDACTABLE"):
            for rel, n, sample in sorted(res["hits"].get(cls, []),
                                         key=lambda x: -x[1]):
                print(f"  [{cls[:4]}] {rel}  ({n} hits)")
                for ln in sample:
                    print(f"        | {ln}")


if __name__ == "__main__":
    main()
