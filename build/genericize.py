#!/usr/bin/env python3
"""
genericize.py — Rule-driven genericizer for the 126 TEMPLATE skill rows.

Implements `genericization-spec.md` (locked): leak-removal BY DESIGN.

For each TEMPLATE row in manifest.tsv:
  1. Copy the source skill file from the profile tree (generic form is the
     skill's reusable body).
  2. Apply rule-driven substitutions: instance tokens (team names, ventures,
     client orgs, workspace paths, budgets, user habits) → {PLACEHOLDER}.
  3. Emit into templates/skills/<relpath> with a header transformation
     manifest (# N×{CLASS} ...).

Rules (from spec section 2):
  - Conservative default: instance-or-pattern → INSTANCE. Strip it.
  - No partial placeholders: full token → full placeholder, never truncation.
  - Context markers survive: the sentence structure around the placeholder
    stays, so templates read naturally when instantiated.
  - Patterns stay verbatim: workflows, checklists, commands, SOPs ship
    unchanged.

OUTPUT
  templates/skills/...  — genericized skill files, header manifests included
  templates/genericization-report.md — per-file substitution counts + classes

USAGE
  python3 build/genericize.py [--rows TEMPLATE] [--source ~/.hermes/profiles]
                              [--out ../templates/skills]
"""

import os
import re
import sys
import shutil
import importlib.util
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DEFAULT_SOURCE = os.path.expanduser("~/.hermes/profiles")
DEFAULT_OUT = os.path.join(ROOT, "templates", "skills")
MANIFEST = os.path.join(HERE, "manifest.tsv")

# ---------------------------------------------------------------------------
# Identity inventory — DERIVED from sources of truth + external config.
# (bootstrap-hole fix: the substitution rules and the leak-check
# list must both come from identity SOURCES so a new member's identity enters
# the inventory by construction, not after a leak incident.)
# Sources:
#   - profile directory names under ~/.hermes/profiles/  (handles)
#   - `name:` / `agent.name:` lines in each profile's config.yaml  (display names)
#   - SOUL.md first-line titles where they carry an identity name  (best-effort)
#   - build/identifiers.yaml — instance identifiers (EMPTY in the open kit;
#     supplied per-instance at build time, never committed with values)
# ---------------------------------------------------------------------------
def derive_identity_inventory(source=DEFAULT_SOURCE):
    handles = set()
    names = set()
    for prof in sorted(os.listdir(source)):
        if prof.startswith("."):
            continue
        root = os.path.join(source, prof)
        if not os.path.isdir(root):
            continue
        handles.add(prof)
        # config.yaml -> name / agent.name
        cfg = os.path.join(root, "config.yaml")
        if os.path.isfile(cfg):
            try:
                for line in open(cfg, encoding="utf-8", errors="replace"):
                    m = re.match(r"\s*(?:agent\.)?name\s*:\s*[\"']?([^\"'#\n]+)", line)
                    if m:
                        v = m.group(1).strip()
                        if v and v != prof:
                            names.add(v)
            except OSError:
                pass
        # SOUL.md first identity line (best-effort; handles profile names)
        soul = os.path.join(root, "SOUL.md")
        if os.path.isfile(soul):
            try:
                for line in open(soul, encoding="utf-8", errors="replace"):
                    if re.match(r"^#\s+", line):
                        title = line.lstrip("# ").strip()
                        if len(title) > 3 and not title.lower().startswith((prof,)):
                            names.add(title.split("—")[0].strip())
                        break
            except OSError:
                pass
    return sorted(handles), sorted(names)


# Derived identity tokens feed the rule table (handles + display names).
_DERIVED_HANDLES, _DERIVED_NAMES = derive_identity_inventory()
_ALL_HANDLES = sorted(set(_DERIVED_HANDLES))
_ALL_NAMES = sorted(set(_DERIVED_NAMES))


# --- Instance identifiers from build/identifiers.yaml (EMPTY in open kit) ---
def load_instance_identifiers():
    """Read build/identifiers.yaml. Missing/blank → empty (safe generic kit).
    Returns (out, protected) where protected = {term_lower: [file_substrings]}."""
    out = {
        "team_handles": [], "venture_names": [], "user_handles": [],
        "client_names": [], "path_markers": [], "habit_phrases": [],
        "codename_terms": [], "drop_files": [], "reachable_integrations": [],
        "ambiguous_terms": [],
    }
    protected = {}
    p = os.path.join(HERE, "identifiers.yaml")
    if not os.path.isfile(p):
        # Fall back to the committed empty template (fork ships identifiers.yaml
        # gitignored; the .example carries the shape). Empty = safe generic kit.
        p = os.path.join(HERE, "identifiers.yaml.example")
    if not os.path.isfile(p):
        return out, protected
    cur = None
    protect_term = None
    try:
        with open(p, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line and not line.startswith("-") and line.endswith(":"):
                    cur = line[:-1].strip()
                    continue
                if line.startswith("- "):
                    val = line[2:].strip()
                    if cur in out:
                        out[cur].append(val.strip('"\''))
                    elif cur == "protected_terms":
                        # "- term: <token>" — a key: value map entry
                        if ":" in val:
                            k, v = val.split(":", 1)
                            if k.strip() == "term":
                                protect_term = v.strip().strip('"\'')
                        else:
                            protect_term = val.strip('"\'')
                    continue
                # Indented sub-key with a list value: "files: [a, b]"
                if ":" in line and line.endswith("]"):
                    k, v = line.split(":", 1)
                    if k.strip() == "files" and protect_term:
                        inner = v.strip().strip("[]").strip('"\'')
                        protected.setdefault(protect_term.lower(), []).extend(
                            x.strip().strip('"\'') for x in inner.split(",") if x.strip())
                    continue
    except OSError:
        pass
    return out, protected


_INST, _PROTECTED = load_instance_identifiers()
_DROP_FILES = set(_INST.get("drop_files", []))
_REACH = sorted(set(_INST.get("reachable_integrations", [])))
_AMBIGUOUS = set(_INST.get("ambiguous_terms", []))
_VENTURES = sorted(set(_INST["venture_names"] + _INST["client_names"] +
                       _INST["codename_terms"]))
_HANDLES_CFG = sorted(set(_INST["team_handles"] + _INST["user_handles"]))
_PATH_MARKERS = sorted(_INST["path_markers"])
_HABITS = sorted(_INST["habit_phrases"])
_CODENAMES = sorted(_INST["codename_terms"])

# ---------------------------------------------------------------------------
# Rule tables — the transformation engine.
# Each entry: (regex, placeholder, class). Ordered; first match wins.
# Conservative: when ambiguous, match (strip). Patterns stay verbatim — only
# these specific instance shapes are stripped.
# Handle lists below are DERIVED (_ALL_HANDLES) so identity coverage is by
# construction, not by hardcode.
# ---------------------------------------------------------------------------
_HANDLE_ALT = "|".join(re.escape(h) for h in _ALL_HANDLES)
_NAME_ALT = "|".join(
    re.escape(n) for n in sorted((x for x in _ALL_NAMES if len(x) > 2),
                                 key=len, reverse=True))
# Longest-first ordering is CRITICAL: regex alternation is first-match-wins,
# so a short token ("short") must never shadow a longer one ("short-name"
# / "a longer team-handle") — that would leave partial-stripped fragments
# ("{RELATIONSHIP} Short-Name"), violating the spec's no-partial-placeholders rule.
_CFG_HANDLE_ALT = "|".join(
    re.escape(h) for h in sorted(_HANDLES_CFG, key=len, reverse=True))
_CFG_VENTURE_ALT = "|".join(
    re.escape(v) for v in sorted(_VENTURES, key=len, reverse=True))
_CFG_PATH_ALT = "|".join(
    re.escape(m) for m in sorted(_PATH_MARKERS, key=len, reverse=True))
_CFG_HABIT_ALT = "|".join(
    re.escape(h) for h in sorted(_HABITS, key=len, reverse=True))
_CFG_CODENAME_ALT = "|".join(
    re.escape(c) for c in sorted(_CODENAMES, key=len, reverse=True))

# Precompute venture/codename rule tuples: UNIQUE tokens get the greedy tail
# (compound forms), AMBIGUOUS tokens (English substrings: a client name in
# "registry", a project name in "explore") get word-boundary only. None
# entries are filtered below.
_V_UNIQ = sorted([v for v in _VENTURES if v not in _AMBIGUOUS],
                 key=len, reverse=True)
_V_AMB = sorted([v for v in _VENTURES if v in _AMBIGUOUS],
                key=len, reverse=True)
_C_UNIQ = sorted([v for v in _CODENAMES if v not in _AMBIGUOUS],
                 key=len, reverse=True)
_C_AMB = sorted([v for v in _CODENAMES if v in _AMBIGUOUS],
                key=len, reverse=True)

RULES = [
    # List of team handles in a quoted list — collapse the whole run to ONE
    # {PROFILES} placeholder, preserving the list role (spec §2: context
    # markers survive). MUST run BEFORE any handle rule so the run is caught
    # whole — otherwise individual handles become {RELATIONSHIP} and the
    # quoted-run pattern can no longer match.
    (re.compile(r'(?i)["\'](?:%s)["\'](?:\s*,\s*["\'](?:%s)["\'])+' % (_HANDLE_ALT, _HANDLE_ALT)),
     '"{PROFILES}"', "RELATIONSHIP"),
    # --- Relationship specifics → {RELATIONSHIP} ---
    # Personal names from identifiers.yaml (EMPTY in the open kit; supplied
    # per-instance). When config is blank, no pattern matches — safe.
    (re.compile(r"\b(?:%s)\b" % _CFG_HANDLE_ALT, re.I),
     "{RELATIONSHIP}", "RELATIONSHIP"),

    # --- Financial figures → {AMOUNT} ---
    # The space before currency must NOT be consumed unless currency follows
    # ("59,680 INFO" -> "{AMOUNT} INFO", never "{AMOUNT}INFO"). Use a
    # lookahead so the optional space only matches when a currency unit
    # actually follows it.
    (re.compile(r"\$\s?\d[\d,\.]*(?:\s?(?:k|K|m|M|bn|B))?|\b\d{1,3}(?:,\d{3})+\.?\d*(?:\s(?=USD|EUR|GBP))?(?:USD|EUR|GBP)?\b",
     re.I), "{AMOUNT}", "AMOUNT"),

    # --- Client/contract detail → {CLIENT} ---
    # Venture / org / project names from identifiers.yaml.
    # AMBIGUOUS tokens (English substrings: a client name in "registry",
    # a project name in "explore") match word-boundary ONLY — never a greedy
    # tail (register must not become "client"+"ter"). UNIQUE invented tokens
    # keep the greedy tail for compound forms (vendor-plugin).
    *([(re.compile(r"\b(?:%s)[A-Za-z0-9_\-\./]*" % "|".join(
        re.escape(v) for v in _V_UNIQ), re.I), "{CLIENT}", "CLIENT")]
      if _V_UNIQ else []),
    *([(re.compile(r"\b(?:%s)\b" % "|".join(
        re.escape(v) for v in _V_AMB), re.I), "{CLIENT}", "CLIENT")]
      if _V_AMB else []),
    # Workspace / path markers from identifiers.yaml
    (re.compile(r"(?:%s)[A-Za-z0-9_\-/ ]*" % _CFG_PATH_ALT, re.I),
     "{CLIENT}", "CLIENT"),
    # Codenames — SUBSTRING match inside camelCase code identifiers
    # (hideProjectStats, instantBookFeature) where \b boundaries don't fire.
    # Safe ONLY for unique invented words — ambiguous tokens (a client name
    # in "registry") get word-boundary matching instead, or they clobber
    # ordinary words (register -> "client"+"ter", explore -> "e"+"plor"+"e").
    *([(re.compile(r"(?:%s)" % "|".join(
        re.escape(v) for v in _C_UNIQ), re.I), "{CLIENT}", "CLIENT")]
      if _C_UNIQ else []),
    *([(re.compile(r"\b(?:%s)\b" % "|".join(
        re.escape(v) for v in _C_AMB), re.I), "{CLIENT}", "CLIENT")]
      if _C_AMB else []),
    # Team member handles — DERIVED inventory (profile dirs)
    (re.compile(r"\b(?:%s)\b" % _HANDLE_ALT, re.I),
     "{RELATIONSHIP}", "RELATIONSHIP"),
    # Team member display names — DERIVED inventory (config.yaml / SOUL.md)
    (re.compile(r"\b(?:%s)\b" % _NAME_ALT, re.I),
     "{RELATIONSHIP}", "RELATIONSHIP"),
    # Session-date stamps — strip ONLY the date value, keep the "session"/"date" context word
    (re.compile(r"\b(?:session-)?20\d\d-\d\d-\d\d\b", re.I),
     "{CLIENT}", "CLIENT"),
    (re.compile(r"\bAugust \d{1,2}, 20\d\d\b", re.I), "{CLIENT}", "CLIENT"),
    # "Phase N" — keep the word, strip only the number. Note: "Phase 2-4" is
    # a range; the number after the hyphen is already consumed by the date
    # rule's session- prefix when present, so strip the leading number only.
    (re.compile(r"\bPhase\s+(\d+)\b", re.I), "Phase {CLIENT}", "CLIENT"),
    # "N-N" ranges following a placeholder ("Phase {CLIENT}-4") — the -N tail
    # is an instance range suffix, strip it.
    (re.compile(r"\{CLIENT\}-\d+", re.I), "{CLIENT}", "CLIENT"),

    # --- Model config → {MODEL} (instance-content finding) ---
    # Tight: KNOWN provider prefixes + a MODEL-NAME shape, with an explicit
    # blacklist of filesystem path words (Chrome, Default, Application,
    # Support, Library, Bookmarks, Safari, etc.) so paths like
    # "~/Library/Application Support/Google/Chrome/Default/Bookmarks" are
    # never mistaken for model strings. Real models (deepseek-v4-flash-0731,
    # gpt-4o, claude-3) are not on the blacklist and still strip.
    (re.compile(r"\b(?:nous|openai|anthropic|google|mistral|meta-llama|deepseek)/(?!Application\b|Support\b|Chrome\b|Default\b|Library\b|Bookmarks\b|Safari\b|Google\b)[A-Za-z0-9][A-Za-z0-9_\-\.]*", re.I),
     "{MODEL}", "MODEL"),

    # --- Instance-specific reachable integrations → {CLIENT} (reachability
    # --- bar: a stranger reaching these reaches our stack). Loaded from
    # --- identifiers.yaml (reachable_integrations) — never hardcoded here.
    # --- Substring match: covers compound forms (vendor_slug) and URL hosts
    # --- (cdn.host.tld).
    # --- This is a single rule with one placeholder per match; we use a
    # --- closure over a Counter to count per-term, or just one {CLIENT}.
    (re.compile(r"(?:%s)[A-Za-z0-9_.\-]*" % "|".join(
        re.escape(r) for r in sorted(_REACH, key=len, reverse=True)),
        re.I), "{CLIENT}", "CLIENT"),

    # --- Personal habits → {HABIT} — from identifiers.yaml (EMPTY in open kit)
    (re.compile(r"\b(?:%s)\b" % _CFG_HABIT_ALT, re.I),
     "{HABIT}", "HABIT"),
]


def apply_rules(text: str, protect: frozenset = frozenset()):
    """Apply the rule table. Returns (new_text, Counter by class).

    protect: set of lowercased tokens to leave untouched (protected terms —
    ambiguous domain vocabulary in specific files). Implemented as
    sentinel-and-restore so no rule can strip them.

    INVARIANT (team): after substitution, no {PLACEHOLDER} token may be
    adjacent to a word character — a placeholder mid-word is always wrong by
    definition (w{CLIENT}rd is a mangled template, not a leak class). Any
    violation raises, failing the build: substitution is never allowed to
    corrupt words, and a boundary tweak alone cannot guarantee this against
    the next word shape."""
    c = Counter()
    # Sentinel-guard protected terms (case-preserving restore)
    sentinels = {}
    if protect:
        for i, tok in enumerate(protect):
            def repl_sentinel(m, _i=i):
                sentinels.setdefault(_i, []).append(m.group(0))
                return f"\x00PROT{_i}\x00"
            text = re.sub(re.escape(tok), repl_sentinel, text, flags=re.I)
    for rx, placeholder, cls in RULES:
        def repl(m, _p=placeholder, _c=cls):
            c[_c] += 1
            return _p
        text = rx.sub(repl, text)
    # Restore protected terms (pattern must use REAL null bytes, matching the
    # sentinel insert — a raw-string \x00 would be a literal backslash-x)
    for i, toks in sentinels.items():
        it = iter(toks)
        text = re.sub(f"\x00PROT{i}\x00", lambda m: next(it), text)
    # INVARIANT: no placeholder may split an ordinary lowercase word — i.e.
    # a placeholder followed by a lowercase word char (w{CLIENT}rd, e{CLIENT}a)
    # means substitution clobbered English. EXCEPTIONS:
    #   - pre-existing template tokens ({N}, {BK}) — legit code literals
    #   - camelCase compounds (hide{CLIENT}Stats) — placeholder followed by
    #     UPPERCASE: the intended sanitization of code identifiers, not a clobber.
    #   - placeholder preceded by a word char is fine when followed by
    #     uppercase or boundary (compound identifiers, spacing).
    _SUBST_PLACEHOLDERS = re.compile(
        r"(\{(?:CLIENT|RELATIONSHIP|AMOUNT|MODEL|HABIT|PROFILES|"
        r"PROFILE_NAME|ROLE_[A-Z_]+|TEAM_NAME|DIRECTOR_NAME|AGENT_NAME|"
        r"BASE_URL|MODEL_PROVIDER|MODEL_NAME|WORKSPACE|PLACEHOLDER|TOKEN|"
        r"API_KEY_ENV|CLASS)\})[a-z]")
    midword = _SUBST_PLACEHOLDERS.findall(text)
    if midword:
        raise ValueError(
            f"PLACEHOLDER MID-WORD INVARIANT VIOLATED: {midword[:5]} "
            f"— substitution clobbered ordinary words; fix the rule, don't "
            f"patch the output")
    return text, c


def file_protections(rel: str):
    """Return frozenset of lowercased protected terms for this file, or empty."""
    if not _PROTECTED:
        return frozenset()
    hits = frozenset(
        term for term, files in _PROTECTED.items()
        if any(fs in rel for fs in files))
    return hits


def sanitize_path(rel: str) -> str:
    """Sanitize a source RELATIVE PATH so no instance token ships in the
    committed tree's filenames/dirs. Instance tokens (handles, ventures,
    codenames, user handles) become {CLIENT}/{RELATIONSHIP} placeholders;
    date/phase/structural tokens stay (they are not instance identity).
    Consecutive placeholders collapse ({CLIENT}-{CLIENT} -> {CLIENT}).

    AMBIGUOUS tokens (substrings of English: a client name in "registry", a
    project name in "explore") match word-boundary only — substring matching
    would clobber "registration" -> w{CLIENT}rd. Unique invented tokens
    match as substrings to catch compound filenames (vendor-plugin)."""
    tokens = sorted(
        set(_HANDLES_CFG) | set(_VENTURES) | set(_CODENAMES)
        | set(_INST.get("user_handles", [])),
        key=len, reverse=True)
    if not tokens:
        return rel
    # Only single-token identifiers (no spaces/slashes) are safe in paths.
    # Multi-word phrases and path markers never appear as path components.
    tokens = [t for t in tokens
              if t and " " not in t and "/" not in t and len(t) >= 2]
    if not tokens:
        return rel
    _AMB = _AMBIGUOUS
    out = rel
    for t in tokens:
        t = t.strip().strip('"\'')
        if not t or len(t) < 2:
            continue
        cls = "CLIENT" if any(
            t.lower() in v.lower() for v in _VENTURES + _PATH_MARKERS
            + _INST.get("codename_terms", [])) else "RELATIONSHIP"
        ph = "{" + cls + "}"
        if t in _AMB:
            # Word-boundary only — never clobber English words mid-path.
            pat = re.compile(r"\b" + re.escape(t) + r"\b", re.I)
        else:
            # Substring for unique invented tokens (compound filenames).
            pat = re.compile(re.escape(t), re.I)
        out = pat.sub(ph, out)
    # Collapse consecutive/repeated placeholders: {A}-{B} -> {A}
    while re.search(r"\{[A-Z]+\}-\{[A-Z]+\}", out):
        out = re.sub(r"\{([A-Z]+)\}-\{[A-Z]+\}", r"{\1}", out)
    return out


def load_manifest():
    rows = {}
    with open(MANIFEST, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line or line.startswith("relpath"):
                continue
            parts = line.split("\t")
            if len(parts) < 5:
                continue
            rows[parts[0]] = (parts[1], parts[4])
    return rows


def find_source(rel, source):
    """Locate the first on-disk copy of a source relpath across profiles."""
    for prof in sorted(os.listdir(source)):
        if prof.startswith("."):
            continue
        full = os.path.join(source, prof, rel)
        if os.path.isfile(full):
            return full
    return None


def main():
    args = sys.argv[1:]
    source = DEFAULT_SOURCE
    out = DEFAULT_OUT
    if "--source" in args:
        source = args[args.index("--source") + 1]
    if "--out" in args:
        out = args[args.index("--out") + 1]

    manifest = load_manifest()
    templ_rows = [rel for rel, (cls, v) in manifest.items()
                  if v == "TEMPLATE" and rel.startswith("skills/")]
    print(f"TEMPLATE skill rows: {len(templ_rows)}")

    os.makedirs(out, exist_ok=True)
    report = []
    zero_sub = []
    total_subs = Counter()

    for rel in sorted(templ_rows):
        if rel in _DROP_FILES:
            report.append(f"| `{rel}` | DROP (drop_files) | 0 | 0 | - |")
            continue
        src = find_source(rel, source)
        if src is None:
            report.append(f"| {rel} | MISSING SOURCE | 0 | 0 | - |")
            continue
        with open(src, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        generic, c = apply_rules(text, protect=file_protections(rel))
        # header transformation manifest (spec section 3)
        sub_desc = ", ".join(f"{n}×{{{k}}}" for k, n in sorted(c.items()))
        if not c:
            sub_desc = "already-generic"
            zero_sub.append(rel)
        # The source path in the header must ALSO be sanitized: instance tokens
        # live in filenames (instance-plugin-dev, client-metrolinx.md), and the
        # header carries the original rel path. Strip them the same way the body
        # is stripped so the provenance line leaks nothing.
        sanitized_rel, _ = apply_rules(rel)
        header = (f"<!-- GENERICIZED: {sub_desc} "
                  f"| source: {sanitized_rel} -->\n")
        generic = header + generic
        # Dest path must ALSO be sanitized: instance tokens live in source
        # directory/file names and would ship in the committed tree otherwise.
        dst_rel = sanitize_path(rel[len("skills/"):])
        dst = os.path.join(out, dst_rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "w", encoding="utf-8") as fh:
            fh.write(generic)
        total_subs.update(c)
        report.append(f"| `{rel}` | {len(c)} classes | "
                      f"{sum(c.values())} subs | {sub_desc} | `{dst_rel}` |")

    # report
    with open(os.path.join(ROOT, "templates", "genericization-report.md"),
              "w", encoding="utf-8") as fh:
        fh.write("# Genericization Report — templates/skills/\n\n")
        fh.write(f"Rows processed: {len(templ_rows)}\n\n")
        fh.write("| source | classes | subs | detail | output |\n|---|---|---|---|---|\n")
        fh.write("\n".join(report) + "\n")
        fh.write("\n## Totals\n\n")
        fh.write(f"- files with ZERO substitutions: {len(zero_sub)}\n")
        for k, v in sorted(total_subs.items()):
            fh.write(f"- {k}: {v} substitutions\n")

    print(f"Wrote {len(templ_rows)} genericized files to {out}")
    print(f"Zero-substitution files: {len(zero_sub)}")
    for z in zero_sub[:10]:
        print(f"  ZERO: {z}")
    print("Substitution totals:", dict(total_subs))
    print("Report: templates/genericization-report.md")


if __name__ == "__main__":
    main()
